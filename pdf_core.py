from __future__ import annotations

import math
import os
from typing import List, Sequence, Union
from typing_extensions import TypeAlias, Final, TypeGuard
from defusedxml import defuse_stdlib
from xml.sax.saxutils import escape
defuse_stdlib()

from reportlab.platypus import (
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    SimpleDocTemplate,
)
from reportlab.platypus.flowables import Flowable
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

import arabic_reshaper
from bidi.algorithm import get_display
from concurrent.futures import ThreadPoolExecutor, as_completed

# ===================== Types =====================
TextLike: TypeAlias = Union[str, bytes, bytearray, memoryview]

# ===================== Constants =================
AVG_CHARS_PER_MB: Final[int] = 500_000
FONT_NAME: Final[str] = "Vazir"


# ===================== Helpers ===================
def safe_paragraph_text(text: str) -> str:
    return escape(text, {"'": "&apos;", '"': "&quot;"})


def _is_memoryview(value: TextLike) -> TypeGuard[memoryview]:
    return isinstance(value, memoryview)


def shape_text(text: str) -> str:
    reshaped = arabic_reshaper.reshape(text)
    visual = get_display(reshaped)

    if isinstance(visual, str):
        return visual
    if isinstance(visual, (bytes, bytearray)):
        return visual.decode("utf-8")
    if _is_memoryview(visual):
        return visual.tobytes().decode("utf-8")

    raise TypeError("Unsupported RTL text type")


# ===================== Table =====================
def parse_table(lines: Sequence[str]) -> List[List[str]]:
    rows: List[List[str]] = []
    for line in lines:
        if not line.strip().startswith("|"):
            continue

        cells = [
            shape_text(cell.strip())
            for cell in line.strip().split("|")[1:-1]
            if cell.strip()
        ]
        if cells:
            rows.append(cells)

    return rows


# ===================== PDF Builder ===============
def build_pdf(
    output_path: str,
    flowables: Sequence[Flowable],
) -> None:
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )
    doc.build(list(flowables))


# ===================== Core ======================
def process_text_to_pdf(
    text: str,
    output_path: str,
    font_path: str,
) -> None:
    if not os.path.isfile(font_path):
        print(f"Font file not found: {font_path}")
        return
    else:
        print(f"Font file found: {font_path}")
        try:
            pdfmetrics.getFont(FONT_NAME)
        except KeyError:
            pdfmetrics.registerFont(TTFont(FONT_NAME, font_path))

    style = ParagraphStyle(
        name="RTL",
        fontName=FONT_NAME,
        fontSize=11,
        leading=16,
        alignment=TA_RIGHT,
    )

    elements: List[Flowable] = []
    lines = text.splitlines()

    table_buffer: List[str] = []
    in_table = False

    # استفاده از ThreadPoolExecutor برای موازی‌سازی پردازش خطوط
    with ThreadPoolExecutor() as executor:
        futures = []
        for line in lines:
            stripped = line.strip()

            if stripped.startswith("|"):
                in_table = True
                table_buffer.append(line)
                continue

            if in_table:
                futures.append(executor.submit(parse_table, table_buffer))
                table_buffer.clear()
                in_table = False

            if stripped:
                shaped = shape_text(line)
                safe = safe_paragraph_text(shaped)
                elements.append(Paragraph(safe, style))
            else:
                elements.append(Spacer(1, 8))

        # پردازش نتیجه‌های جدول‌ها به صورت موازی
        for future in as_completed(futures):
            table_data = future.result()
            if table_data:
                table = Table(table_data, hAlign="RIGHT")
                table.setStyle(
                    TableStyle(
                        [
                            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                            ("FONT", (0, 0), (-1, -1), FONT_NAME),
                            ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
                        ]
                    )
                )
                elements.append(table)
                elements.append(Spacer(1, 8))

    build_pdf(output_path, elements)


# ===================== Chunk Estimator ===========
def estimate_chunk_count(text: str, max_mb: int) -> int:
    approx_chars = AVG_CHARS_PER_MB * max_mb
    if approx_chars <= 0:
        return 1
    return max(1, math.ceil(len(text) / approx_chars))
