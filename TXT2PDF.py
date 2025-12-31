from __future__ import annotations

import os
import sys
import logging
from typing import List
from typing_extensions import Final
import re
import math
from pdf_core import (
    estimate_chunk_count,
    process_text_to_pdf,
)

# ===================== Config =====================
FONT_PATH: Final[str] = "Vazirmatn-Regular.ttf"
INPUT_DIR: Final[str] = "input_txt"
OUTPUT_DIR: Final[str] = "output_pdf"
MAX_PDF_MB: Final[int] = 1
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
    # بررسی اینکه آیا ورودی دایرکتوری به درستی مشخص شده است
    if len(sys.argv) < 2:
        input_dir = INPUT_DIR
    else:
        input_dir = sys.argv[1]

    if not os.path.isdir(input_dir):
        logger.error(f"Input directory {input_dir} does not exist.")
        sys.exit(1)

    # پیدا کردن تمامی فایل‌های متنی در دایرکتوری ورودی
    text_files: List[str] = [
        f for f in os.listdir(input_dir) if f.endswith(".txt")
    ]
    if not text_files:
        logger.error("No text files found in the input directory.")
        sys.exit(1)

    logger.info(f"Found {len(text_files)} text files to process.")

    # پردازش هر فایل متنی به صورت جداگانه
    for idx, text_file in enumerate(text_files):
        input_path = os.path.join(input_dir, text_file)
        output_path = os.path.join(OUTPUT_DIR, f"{os.path.splitext(text_file)[0]}.pdf")
        logger.info(f"Processing file {text_file} ({idx+1}/{len(text_files)})")
        try:
            with open(input_path, encoding="utf-8") as f:
                text = f.read()

            # پاکسازی متن (حذف تگ‌های HTML، بررسی تگ‌های باز نشده و اصلاحات)
            text = clean_invalid_attributes(text)
            text = check_unclosed_tags(text)
            text = clean_html_tags(text)

            # محاسبه تعداد بخش‌های ممکن بر اساس اندازه فایل PDF
            chunk_count = estimate_chunk_count(text, MAX_PDF_MB)
            chunk_size = math.ceil(len(text) / chunk_count)

            # پردازش هر بخش به صورت جداگانه
            for i in range(chunk_count):
                start_idx = i * chunk_size
                end_idx = min((i + 1) * chunk_size, len(text))

                chunk_text = text[start_idx:end_idx]
                try:
                    process_text_to_pdf(chunk_text, f"{output_path}_{i+1}.pdf", FONT_PATH)
                    render_progress(i + 1, chunk_count)
                except Exception as e:
                    logger.error(f"Error processing file {text_file}: {str(e)}")
                    log_error_text_part(text, idx + 1)

            logger.info("Processing complete!")

if __name__ == "__main__":
    main()
