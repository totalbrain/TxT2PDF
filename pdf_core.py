from __future__ import annotations

import math
import os
import arabic_reshaper
from functools import lru_cache
from typing import List, Sequence, Union
from typing_extensions import TypeAlias, Final, TypeGuard
from defusedxml import defuse_stdlib
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, SimpleDocTemplate
from reportlab.platypus.flowables import Flowable
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from bidi.algorithm import get_display
from concurrent.futures import ThreadPoolExecutor, as_completed
from xml.sax.saxutils import escape
defuse_stdlib()
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


@lru_cache(maxsize=2048)
def shape_text(text: str) -> str:
    """
    Shape RTL text with caching for repeated content.
    Cache size of 2048 handles common repeated lines efficiently.
    """
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
def shape_text_batch(lines: List[str]) -> List[str]:
    """Shape multiple lines at once for better performance."""
    return [shape_text(line) for line in lines]


def process_text_to_pdf(
    text: str,
    output_path: str,
    font_path: str,
) -> None:
    if not os.path.isfile(font_path):
        print(f"Font file not found: {font_path}")
        return
    else:
        try:
            # Check if the font is already registered
            if FONT_NAME not in pdfmetrics.getRegisteredFontNames():
                pdfmetrics.registerFont(TTFont(FONT_NAME, font_path))
            else:
                print(f"Font {FONT_NAME} already registered.")
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
    text_batch: List[str] = []
    in_table = False

    # Process lines in batches for better performance
    BATCH_SIZE = 100

    def flush_text_batch():
        """Process accumulated text lines in batch."""
        if not text_batch:
            return

        # Shape all text lines at once (much faster than one-by-one)
        with ThreadPoolExecutor(max_workers=4) as executor:
            # Split batch into sub-batches for parallel processing
            sub_batch_size = max(1, len(text_batch) // 4)
            futures = []

            for i in range(0, len(text_batch), sub_batch_size):
                sub_batch = text_batch[i:i + sub_batch_size]
                futures.append(executor.submit(shape_text_batch, sub_batch))

            # Collect results in order
            shaped_results = []
            for future in futures:
                shaped_results.extend(future.result())

        # Create paragraph elements
        for shaped in shaped_results:
            safe = safe_paragraph_text(shaped)
            elements.append(Paragraph(safe, style))

        text_batch.clear()

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("|"):
            # Flush any pending text before starting table
            flush_text_batch()
            in_table = True
            table_buffer.append(line)
            continue

        if in_table:
            # Process table immediately (maintain document order)
            table_data = parse_table(table_buffer)
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
            table_buffer.clear()
            in_table = False

        if stripped:
            text_batch.append(line)
            # Process batch when it reaches size limit
            if len(text_batch) >= BATCH_SIZE:
                flush_text_batch()
        else:
            # Flush text before spacer to maintain order
            flush_text_batch()
            elements.append(Spacer(1, 8))

    # Process any remaining text and table
    flush_text_batch()
    if table_buffer:
        table_data = parse_table(table_buffer)
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

    build_pdf(output_path, elements)


# ===================== Chunk Estimator ===========
def estimate_chunk_count(text: str, max_mb: int) -> int:
    """
    Calculate number of chunks based on target size in MB.
    Each chunk should be approximately max_mb in size.
    """
    file_size_bytes = len(text.encode("utf-8"))
    target_chunk_bytes = max_mb * 1024 * 1024  # Convert MB to bytes
    return max(1, math.ceil(file_size_bytes / target_chunk_bytes))
