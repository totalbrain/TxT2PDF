import os
import re
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

import arabic_reshaper
from bidi.algorithm import get_display

# ========================= تنظیمات =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

INPUT_DIR  = os.path.join(BASE_DIR, "input_txt")
OUTPUT_DIR = os.path.join(BASE_DIR, "output_pdf")
FONT_PATH  = os.path.join(BASE_DIR, "Vazirmatn-Regular.ttf")

TARGET_PDF_SIZE = 20 * 1024 * 1024   # 20 MB
SAFETY_RATIO    = 0.85               # حاشیه امن
# ===========================================================

os.makedirs(OUTPUT_DIR, exist_ok=True)

if not os.path.exists(FONT_PATH):
    raise FileNotFoundError("❌ فونت پیدا نشد. فایل فونت را کنار اسکریپت بگذار.")

# ---------- فونت ----------
pdfmetrics.registerFont(TTFont("Vazir", FONT_PATH))

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(
    name="RTL",
    fontName="Vazir",
    fontSize=10,
    leading=14,
    alignment=2,  # RIGHT
))

# ---------- Regex ----------
PERSIAN_RE = r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]+'
LATIN_RE   = r'[A-Za-z0-9@:/._\-]+'
TOKEN_RE   = re.compile(f'({PERSIAN_RE}|{LATIN_RE})')

# ---------- پردازش خط مخلوط ----------
def process_mixed_line(line: str) -> str:
    tokens = TOKEN_RE.findall(line)
    visual_parts = []

    for tok in tokens:
        if re.search(PERSIAN_RE, tok):
            reshaped = arabic_reshaper.reshape(tok)
            visual_parts.append(get_display(reshaped))
        else:
            visual_parts.append(tok)

    # چون پاراگراف RTL است
    return " ".join(visual_parts[::-1])

# ---------- تقسیم متن بر اساس حجم ----------
def split_by_estimated_size(lines):
    total_bytes = sum(len(l.encode("utf-8")) for l in lines)
    if total_bytes == 0:
        return [lines]

    max_chunk_bytes = TARGET_PDF_SIZE * SAFETY_RATIO

    chunks = []
    current = []
    current_size = 0

    for line in lines:
        line_size = len(line.encode("utf-8"))

        if current_size + line_size > max_chunk_bytes and current:
            chunks.append(current)
            current = []
            current_size = 0

        current.append(line)
        current_size += line_size

    if current:
        chunks.append(current)

    return chunks

# ---------- تبدیل TXT به PDF ----------
def txt_to_pdf(txt_path):
    base_name = os.path.splitext(os.path.basename(txt_path))[0]

    with open(txt_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    chunks = split_by_estimated_size(lines)

    for i, chunk in enumerate(chunks, start=1):
        pdf_name = f"{base_name}_part_{i}.pdf" if len(chunks) > 1 else f"{base_name}.pdf"
        pdf_path = os.path.join(OUTPUT_DIR, pdf_name)

        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=A4,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36,
        )

        story = []
        for line in chunk:
            line = line.rstrip()
            if not line:
                story.append(Paragraph("&nbsp;", styles["RTL"]))
            else:
                processed = process_mixed_line(line)
                story.append(Paragraph(processed, styles["RTL"]))

        doc.build(story)
        print(f"✔ ساخته شد: {pdf_name}")

# ---------- اجرای اصلی ----------
def main():
    files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith(".txt")]

    if not files:
        print("⚠️ هیچ فایل TXT در input_txt پیدا نشد.")
        return

    for file in files:
        print(f"▶ پردازش: {file}")
        txt_to_pdf(os.path.join(INPUT_DIR, file))

if __name__ == "__main__":
    main()
