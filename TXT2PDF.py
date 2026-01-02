from __future__ import annotations

import os
import sys
import logging
import math
import re
from typing import List
from typing_extensions import Final

from pdf_core import estimate_chunk_count, process_text_to_pdf

# ===================== Config =====================
FONT_PATH: Final[str] = r".\font\Vazirmatn-Regular.ttf"
INPUT_DIR: Final[str] = "input_txt"
OUTPUT_DIR: Final[str] = "output_pdf"
MAX_PDF_MB: Final[int] = 1

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ===================== Logging ====================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("TXT2PDF")


# ===================== Utils ======================
def render_progress(current: int, total: int, width: int = 30) -> None:
    ratio = current / total if total else 1
    filled = int(ratio * width)
    bar = "█" * filled + "─" * (width - filled)
    percent = int(ratio * 100)
    print(f"\r[{bar}] {percent:3d}% ({current}/{total})", end="", flush=True)
    if current == total:
        print()




# ===================== Main =======================
def main() -> None:
    input_dir = sys.argv[1] if len(sys.argv) > 1 else INPUT_DIR

    if not os.path.isdir(input_dir):
        logger.error(f"Input directory not found: {input_dir}")
        sys.exit(1)

    text_files: List[str] = [
        f for f in os.listdir(input_dir) if f.lower().endswith(".txt")
    ]

    if not text_files:
        logger.error("No .txt files found.")
        sys.exit(1)

    logger.info(f"{len(text_files)} file(s) found.")

    for file_index, filename in enumerate(text_files, start=1):
        logger.info(f"Processing {filename} ({file_index}/{len(text_files)})")

        input_path = os.path.join(input_dir, filename)
        base_name = os.path.splitext(filename)[0]

        with open(input_path, encoding="utf-8") as f:
            text = f.read()

        chunk_count = estimate_chunk_count(text, MAX_PDF_MB)
        chunk_size = math.ceil(len(text) / chunk_count)

        for i in range(chunk_count):
            start = i * chunk_size
            end = min(start + chunk_size, len(text))
            chunk_text = text[start:end]

            output_pdf = os.path.join(
                OUTPUT_DIR,
                f"{base_name}_part{i + 1}.pdf",
            )

            try:
                process_text_to_pdf(chunk_text, output_pdf, FONT_PATH)
                render_progress(i + 1, chunk_count)
            except Exception as exc:
                logger.error(f"Failed on {filename} part {i + 1}: {exc}")

        logger.info(f"{filename} completed.")

    logger.info("All files processed successfully.")


if __name__ == "__main__":
    main()
