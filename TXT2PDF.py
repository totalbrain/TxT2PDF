from __future__ import annotations

import logging
import math
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Iterable

from typing_extensions import Final

from app_logging import LoggingConfig, render_progress, setup_logging
from pdf_core import estimate_chunk_count, process_text_to_pdf


# ===================== Config =====================
FONT_PATH: Final[Path] = Path("./font/Vazirmatn-Regular.ttf")
DEFAULT_INPUT_DIR: Final[Path] = Path("input_txt")
DEFAULT_OUTPUT_DIR: Final[Path] = Path("output_pdf")
MAX_PDF_MB: Final[int] = 10

logger = logging.getLogger(__name__)


def _iter_txt_files(input_dir: Path) -> list[Path]:
    # Design choice: non-recursive scanning (matches legacy behavior).
    return sorted(
        [p for p in input_dir.iterdir() if p.is_file() and p.suffix.lower() == ".txt"]
    )


def _split_text_into_chunks(text: str, chunk_count: int) -> Iterable[str]:
    """
    Chunking is intentionally deterministic and simple:
    we slice the text by character index to create `chunk_count` segments.
    """
    if chunk_count <= 1:
        yield text
        return

    chunk_size = math.ceil(len(text) / chunk_count)
    for i in range(chunk_count):
        start = i * chunk_size
        end = min(start + chunk_size, len(text))
        yield text[start:end]


# ===================== Processing =================
def process_file(
    input_path: Path,
    output_dir: Path,
    *,
    font_path: Path = FONT_PATH,
    max_pdf_mb: int = MAX_PDF_MB,
    max_workers: int = 4,
) -> None:
    filename = input_path.name
    base_name = input_path.stem

    logger.info("Start file: %s", filename)

    try:
        text = input_path.read_text(encoding="utf-8")

        chunk_count = estimate_chunk_count(text, max_pdf_mb)
        text_bytes = len(text.encode("utf-8"))
        logger.info(
            "File size=%.2fMB chunks=%d file=%s",
            text_bytes / 1024 / 1024,
            chunk_count,
            filename,
        )

        output_dir.mkdir(parents=True, exist_ok=True)

        futures = []
        with ThreadPoolExecutor(max_workers=min(max_workers, chunk_count)) as executor:
            for idx, chunk_text in enumerate(
                _split_text_into_chunks(text, chunk_count), start=1
            ):
                output_pdf = output_dir / f"{base_name}_part{idx}.pdf"

                futures.append(
                    executor.submit(
                        process_text_to_pdf,
                        chunk_text,
                        str(output_pdf),
                        str(font_path),
                        # Attach context so logs are traceable per file/chunk.
                        source_file=filename,
                        chunk_id=idx,
                    )
                )

            # Update progress based on completed futures (not submission order).
            for done_count, future in enumerate(as_completed(futures), start=1):
                try:
                    future.result()
                except Exception:
                    # Log full traceback but continue processing remaining chunks.
                    logger.exception(
                        "Chunk failed | file=%s completed=%d/%d",
                        filename,
                        done_count,
                        chunk_count,
                    )

                render_progress(done_count, chunk_count, logger=logger)

        logger.info("Completed file: %s", filename)

    except FileNotFoundError:
        logger.error("Input file not found: %s", input_path)
    except UnicodeDecodeError:
        logger.exception("UTF-8 decode failed: %s", input_path)
    except Exception:
        logger.exception("Fatal error while processing file: %s", filename)


# ===================== Main =======================
def main() -> None:
    # Configure logging only here (entrypoint).
    setup_logging(
        LoggingConfig(
            level=os.getenv("LOG_LEVEL", "INFO"),
            log_file="txt2pdf.log",
        )
    )

    input_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_INPUT_DIR
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_OUTPUT_DIR

    if not input_dir.is_dir():
        logger.error("Input directory not found: %s", input_dir)
        sys.exit(1)

    if not FONT_PATH.is_file():
        logger.error("Font file not found: %s", FONT_PATH)
        sys.exit(1)

    files = _iter_txt_files(input_dir)
    if not files:
        logger.error("No .txt files found in: %s", input_dir)
        sys.exit(1)

    logger.info("Discovered %d file(s) in %s", len(files), input_dir)

    # We have nested executors (file-level and chunk-level). Keep outer pool small.
    outer_workers = min(4, len(files))
    with ThreadPoolExecutor(max_workers=outer_workers) as executor:
        futures = [executor.submit(process_file, p, output_dir) for p in files]
        for f in as_completed(futures):
            # If `process_file` unexpectedly raises, log it here.
            try:
                f.result()
            except Exception:
                logger.exception("Unexpected crash in file worker")

    logger.info("All files processed.")


if __name__ == "__main__":
    main()
