from __future__ import annotations

import os
import sys
import logging
import math
import re
from typing import List
from typing_extensions import Final
from concurrent.futures import ThreadPoolExecutor, as_completed

from pdf_core import estimate_chunk_count, process_text_to_pdf

# ===================== Config =====================
FONT_PATH: Final[str] = r".\font\Vazirmatn-Regular.ttf"
INPUT_DIR: Final[str] = "input_txt"
OUTPUT_DIR: Final[str] = "output_pdf"
MAX_PDF_MB: Final[int] = 10

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


def clean_html(text: str) -> str:
    text = re.sub(r'class="[^"]+"', '', text)
    text = re.sub(r'id="[^"]+"', '', text)
    text = re.sub(r'<[^>]+>', '', text)
    return text


# ===================== Processing =================
def process_file(filename: str) -> None:
    input_path = os.path.join(INPUT_DIR, filename)
    base_name = os.path.splitext(filename)[0]

    with open(input_path, encoding="utf-8") as f:
        text = clean_html(f.read())

    chunk_count = estimate_chunk_count(text, MAX_PDF_MB)

    # Calculate appropriate chunk size
    text_bytes = len(text.encode("utf-8"))
    chunk_size_bytes = math.ceil(text_bytes / chunk_count)

    # Convert back to character count (approximate)
    chunk_size = math.ceil(len(text) / chunk_count)

    logger.info(
        f"Processing {filename}: {text_bytes/1024/1024:.2f}MB in {chunk_count} chunk(s)")

    futures = []
    with ThreadPoolExecutor(max_workers=min(4, chunk_count)) as executor:
        for i in range(chunk_count):
            start = i * chunk_size
            end = min(start + chunk_size, len(text))
            chunk_text = text[start:end]

            output_pdf = os.path.join(
                OUTPUT_DIR,
                f"{base_name}_part{i + 1}.pdf",
            )

            # Submit chunk processing tasks
            futures.append(executor.submit(process_text_to_pdf,
                           chunk_text, output_pdf, FONT_PATH))

        # Monitor processing progress
        for i, future in enumerate(as_completed(futures), 1):
            try:
                future.result()
                render_progress(i, chunk_count)
            except Exception as exc:
                logger.error(f"Failed on {filename} part {i}: {exc}")

    logger.info(f"{filename} completed.")


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

    with ThreadPoolExecutor() as executor:
        executor.map(process_file, text_files)

    logger.info("All files processed successfully.")


if __name__ == "__main__":
    main()
