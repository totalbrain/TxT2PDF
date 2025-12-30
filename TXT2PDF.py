from __future__ import annotations

import os
import sys
import logging
from typing import List
from typing_extensions import Final
import re
from pdf_core import (
    estimate_chunk_count,
    process_text_to_pdf,
)

# ===================== Config =====================
FONT_PATH: Final[str] = "Vazirmatn-Regular.ttf"
INPUT_DIR: Final[str] = "input_txt"
OUTPUT_DIR: Final[str] = "output_pdf"
MAX_PDF_MB: Final[int] = 10
# ================================================
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ===================== Logging ====================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("TXT2PDF")
# ===================== Progress Bar ===============
def render_progress(current: int, total: int, width: int = 30) -> None:
    ratio = current / total if total else 1
    filled = int(ratio * width)
    bar = "█" * filled + "─" * (width - filled)
    percent = int(ratio * 100)
    print(f"\r[{bar}] {percent:3d}% ({current}/{total})", end="", flush=True)
    if current == total:
        print()
# ===================== Text Processing ===========
def check_unclosed_tags(text: str) -> str:
    # یافتن تمامی تگ‌های باز نشده
    unclosed_tags = re.findall(r'<([^/][^>]+)>', text)
    for tag in unclosed_tags:
        if not text.endswith(f"</{tag}>"):
            text += f"</{tag}>"
    # اصلاح تگ‌های پارا برای اطمینان از بسته شدن آنها
    text = re.sub(r'<para[^>]*>', '<para>', text)  # اصلاح تگ‌های پارا
    text = re.sub(r'</para>', '</para>', text)    # اطمینان از تگ بسته
    # trunk-ignore(git-diff-check/error)
    # همچنین، بسته کردن تگ‌های HTML
    text = re.sub(r'<head[^>]*>', '<head>', text)
    text = re.sub(r'</head>', '</head>', text)
    text = re.sub(r'<body[^>]*>', '<body>', text)
    text = re.sub(r'</body>', '</body>', text)
    text = re.sub(r'<html[^>]*>', '<html>', text)
    text = re.sub(r'</html>', '</html>', text)
    # بررسی و بستن سایر تگ‌های احتمالی
    text = re.sub(r'<p[^>]*>', '<p>', text)
    text = re.sub(r'</p>', '</p>', text)

    return text

# تابع برای پاکسازی تگ‌های غیر ضروری (HTML)
def clean_html_tags(text: str) -> str:
    # حذف تمام تگ‌های HTML اگر نیاز نباشد
    clean_text = re.sub(r'<[^>]*>', '', text)  # حذف تمام تگ‌های HTML
    return clean_text

# تابع برای لاگ کردن زمانی که خطا رخ می‌دهد
def log_error_text_part(text: str, part_number: int) -> None:
    part_preview = text[:500]  # ذخیره 500 کاراکتر اول برای بررسی
    logger.error(f"Error in part {part_number} of file: Text causing the issue - {part_preview}")

# تابع برای پاکسازی تگ‌های نامعتبر
def clean_invalid_attributes(text: str) -> str:
    text = re.sub(r'class="[^"]+"', '', text)
    text = re.sub(r'id="[^"]+"', '', text)
    return text

# ===================== Main =======================
def main() -> None:
    logger.info("Starting TXT to PDF conversion...")

    if not os.path.exists(FONT_PATH):
        logger.critical("Vazir font file not found: %s", FONT_PATH)
        return

    try:
        files: List[str] = [
            f for f in os.listdir(INPUT_DIR)
            if f.lower().endswith(".txt")
        ]
    except OSError as exc:
        logger.critical("Error accessing directory '%s': %s", INPUT_DIR, exc)
        logger.critical("Please check that the directory exists and update access permissions.")
        return

    if not files:
        logger.warning("No .txt files found in the input directory: %s", INPUT_DIR)
        return

    for file in files:
        logger.info("Processing file: %s", file)
        input_path = os.path.join(INPUT_DIR, file)

        try:
            with open(input_path, "r", encoding="utf-8") as f:
                full_text = f.read()

            # فراخوانی برای بستن تگ‌های باز
            full_text = check_unclosed_tags(full_text)

            # پاکسازی تگ‌های نامعتبر
            full_text = clean_invalid_attributes(full_text)

            # پاکسازی تگ‌های HTML اگر لازم باشد
            full_text = clean_html_tags(full_text)

        except OSError as exc:
            logger.error("Error reading file %s: ", file, exc)
            continue

        chunk_count = estimate_chunk_count(full_text, MAX_PDF_MB)
        chunk_size = len(full_text) // chunk_count

        for i in range(chunk_count):
            render_progress(i + 1, chunk_count)

            part_text = full_text[
                i * chunk_size : (i + 1) * chunk_size
            ]

            try:
                process_text_to_pdf(
                    text=part_text,
                    output_path=os.path.join(OUTPUT_DIR, f"{os.path.splitext(file)[0]}_part{i+1}.pdf"),
                    font_path=FONT_PATH,
                )
            except Exception as exc:
                log_error_text_part(part_text, i + 1)  # لاگ کردن متن مشکل‌دار
                logger.error(
                    "Error in part %d of file %s: %s",
                    i + 1,
                    file,
                    exc,
                )

        logger.info("Finished processing file: %s", file)

    logger.info("All files have been processed.")

if __name__ == "__main__":
    main()
