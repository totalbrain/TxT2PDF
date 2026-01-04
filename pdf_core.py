from __future__ import annotations

import logging
import math
import os
import threading
from dataclasses import dataclass
from functools import lru_cache
from typing import List, Optional, Sequence

import arabic_reshaper
from bidi.algorithm import get_display
from defusedxml import defuse_stdlib
from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from reportlab.platypus.flowables import Flowable
from xml.sax.saxutils import escape

# Secure xml usage (monkey-patches stdlib xml parsers)
defuse_stdlib()

logger = logging.getLogger(__name__)

FONT_NAME = "Vazir"
BATCH_SIZE = 100

# Font registration is global in reportlab; protect it in multithread usage
_font_lock = threading.Lock()


@dataclass(frozen=True)
class RenderContext:
    """Optional context for better logs (without changing call sites)."""
    source_file: Optional[str] = None
    chunk_id: Optional[int] = None

    def prefix(self) -> str:
        parts: List[str] = []
        if self.source_file:
            parts.append(f"file={self.source_file}")
        if self.chunk_id is not None:
            parts.append(f"chunk={self.chunk_id}")
        return (" | " + " ".join(parts)) if parts else ""


def safe_paragraph_text(text: str) -> str:
    # Prevent ReportLab Paragraph markup injection / broken XML-like markup
    return escape(text, {"'": "&apos;", '"': "&quot;"})


@lru_cache(maxsize=4096)
def shape_text(text: str) -> str:
    """
    RTL shaping (hot-path).
    IMPORTANT: no INFO logging here to avoid log spam and huge overhead.
    """
    # Lazy debug (only if enabled) + no text content (PII/huge logs)
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("shape_text called (len=%d)", len(text))

    reshaped = arabic_reshaper.reshape(text)
    visual = get_display(reshaped)
    # In practice, get_display returns str; keep it strict/simple.
    if not isinstance(visual, str):
        visual = str(visual)
        return visual


# ===================== Table =====================
def parse_table(lines: Sequence[str]) -> List[List[str]]:
    """
    Parse markdown-like tables:
    | col1 | col2 |
    Returns rows of shaped cells.
    """
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("parse_table lines=%d", len(lines))

    rows: List[List[str]] = []
    for line in lines:
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue

        cells = [
            shape_text(cell.strip())
            for cell in stripped.split("|")[1:-1]
            if cell.strip()
        ]
        if cells:
            rows.append(cells)

    return rows


def _ensure_font_registered(font_path: str, ctx: RenderContext) -> None:
    if not os.path.isfile(font_path):
        raise FileNotFoundError(f"Font file not found: {font_path}")

    # reportlab font registry is global; race possible without lock
    with _font_lock:
        if FONT_NAME not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont(FONT_NAME, font_path))
            logger.info("Font registered: %s%s", FONT_NAME, ctx.prefix())
        else:
            # Keep this debug to reduce noise
            logger.debug("Font already registered: %s%s", FONT_NAME, ctx.prefix())


def build_pdf(output_path: str, flowables: Sequence[Flowable], ctx: RenderContext) -> None:
    logger.info("Building PDF: %s%s", output_path, ctx.prefix())

    out_dir = os.path.dirname(output_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )
    doc.build(list(flowables))

    logger.info("PDF built: %s%s", output_path, ctx.prefix())


def process_text_to_pdf(
    text: str,
    output_path: str,
    font_path: str,
    *,
    source_file: Optional[str] = None,
    chunk_id: Optional[int] = None,
) -> None:
    """
    Convert text to PDF.
    - No basicConfig here (logging must be configured in app entrypoint).
    - Avoid nested thread pools (caller already parallelizes).
    """
    ctx = RenderContext(source_file=source_file, chunk_id=chunk_id)

    logger.info("Render start: out=%s text_len=%d%s", output_path, len(text), ctx.prefix())

    try:
        _ensure_font_registered(font_path, ctx)

        style = ParagraphStyle(
            name="RTL",
            fontName=FONT_NAME,
            fontSize=11,
            leading=16,
            alignment=TA_RIGHT,
        )

        elements: List[Flowable] = []
        table_buffer: List[str] = []
        text_batch: List[str] = []
        in_table = False

        def flush_text_batch() -> None:
            if not text_batch:
                return

            # No internal ThreadPoolExecutor:
            # This module is called inside the app-level ThreadPool; nesting causes oversubscription.
            for line in text_batch:
                shaped = shape_text(line)
                elements.append(Paragraph(safe_paragraph_text(shaped), style))

            text_batch.clear()

        def flush_table_buffer() -> None:
            nonlocal in_table
            if not table_buffer:
                in_table = False
                return

            table_data = parse_table(table_buffer)
            table_buffer.clear()
            in_table = False

            if not table_data:
                return

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

        for line in text.splitlines():
            stripped = line.strip()

            if stripped.startswith("|"):
                # entering/continuing a table
                flush_text_batch()
                in_table = True
                table_buffer.append(line)
                continue

            if in_table:
                # leaving table: flush it before normal content
                flush_table_buffer()

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
        if in_table:
            flush_table_buffer()

        build_pdf(output_path, elements, ctx)

        logger.info("Render complete%s", ctx.prefix())

    except Exception:
        logger.exception("Render failed: out=%s%s", output_path, ctx.prefix())
        raise


# ===================== Chunk Estimator ===========
def estimate_chunk_count(text: str, max_mb: int) -> int:
    """
    Calculate chunk count based on target max size (MB).
    """
    if max_mb <= 0:
        raise ValueError("max_mb must be > 0")

    file_size_bytes = len(text.encode("utf-8"))
    target_chunk_bytes = max_mb * 1024 * 1024
    return max(1, math.ceil(file_size_bytes / target_chunk_bytes))
