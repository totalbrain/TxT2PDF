from __future__ import annotations
import math
from typing import List, Sequence, Union
from typing_extensions import TypeAlias, Final, TypeGuard

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Table,
    TableStyle,
)
from reportlab.platypus.flowables import Flowable
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

import arabic_reshaper
from bidi.algorithm import get_display


# ===================== Types =====================
TextLike: TypeAlias = Union[str, bytes, bytearray, memoryview]
Flowables: TypeAlias = List[Flowable]

# ===================== Constants =================
AVG_CHARS_PER_MB: Final[int] = 500_000

# ===================== Type Guards ================
def _is_memoryview(value: TextLike) -> TypeGuard[memoryview]:
    return isinstance(value, memoryview)


# ===================== RTL Shaping ================
def shape_text(text: str) -> str:
    reshaped: TextLike = arabic_reshaper.reshape(text)
    visual: TextLike = get_display(reshaped)

    if isinstance(visual, str):
        return visual
    if isinstance(visual, (bytes, bytearray)):
        return visual.decode("utf-8")
    if _is_memoryview(visual):
        return visual.tobytes().decode("utf-8")

    raise TypeError("Unexpected type returned from get_display")


# ===================== Table Parsing ==============
def parse_table(lines: Sequence[str]) -> List[List[str]]:
    rows: List[List[str]] = []

    for line in lines:
        if "|" not in line:
            continue
        cells = [
            shape_text(cell.strip())
            for cell in line.strip().split("|")[1:-1]
        ]
        if cells:
            rows.append(cells)

    return rows


# ===================== Chunk Estimator ============
def estimate_chunk_count(text: str, max_mb: int) -> int:
    approx_chars = AVG_CHARS_PER_MB * max_mb
    count = math.ceil(len(text) / approx_chars)
    return max(1, count)


# ===================== PDF Builder ================
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


# ===================== Core Processor =============


# تابع برای پردازش فایل به PDF
def process_text_to_pdf(
    text: str,
    output_path: str,
    font_path: str
) -> None:
    pdfmetrics.registerFont(TTFont("Vazir", font_path))

    rtl_style = ParagraphStyle(
        name="RTL",
        fontName="Vazir",
        fontSize=11,
        leading=16,
        alignment=TA_RIGHT,
    )

    elements: Flowables = []

    lines = text.splitlines()
    table_buffer: List[str] = []
    in_table = False

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("|"):
            in_table = True
            table_buffer.append(line)
            continue

        if in_table:
            table_data = parse_table(table_buffer)
            if table_data:
                table = Table(table_data, hAlign="RIGHT")
                table.setStyle(
                    TableStyle(
                        [
                            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                            ("FONT", (0, 0), (-1, -1), "Vazir"),
                            ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
                        ]
                    )
                )
                elements.append(table)
                elements.append(Paragraph("<br/>", rtl_style))

            table_buffer.clear()
            in_table = False

        if stripped:
            elements.append(Paragraph(shape_text(line), rtl_style))
        else:
            elements.append(Paragraph("<br/>", rtl_style))

    build_pdf(output_path, elements)
