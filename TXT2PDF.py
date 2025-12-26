from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

# ========= تنظیمات =========
INPUT_DIR = r"input_txt"
OUTPUT_DIR = r"output_pdf"
FONT_PATH = r"Vazirmatn-Regular.ttf"  # فونت فارسی
MAX_LINES_PER_PDF = 100000  # اگر خواستی فایل‌ها split شوند
# ==========================

os.makedirs(OUTPUT_DIR, exist_ok=True)

pdfmetrics.registerFont(TTFont("Vazir", FONT_PATH))
styles = getSampleStyleSheet()
styles["Normal"].fontName = "Vazir"

def txt_to_pdf(txt_path):
    base = os.path.splitext(os.path.basename(txt_path))[0]

    with open(txt_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    chunks = [
        lines[i:i + MAX_LINES_PER_PDF]
        for i in range(0, len(lines), MAX_LINES_PER_PDF)
    ]

    for idx, chunk in enumerate(chunks, start=1):
        pdf_name = f"{base}_part_{idx}.pdf" if len(chunks) > 1 else f"{base}.pdf"
        pdf_path = os.path.join(OUTPUT_DIR, pdf_name)

        doc = SimpleDocTemplate(pdf_path, pagesize=A4)
        story = []

        for line in chunk:
            story.append(Paragraph(line.replace("&", "&amp;")
                                         .replace("<", "&lt;")
                                         .replace(">", "&gt;"),
                                     styles["Normal"]))

        doc.build(story)
        print(f"✔ ساخته شد: {pdf_name}")

def main():
    for file in os.listdir(INPUT_DIR):
        if file.lower().endswith(".txt"):
            print(f"▶ پردازش: {file}")
            txt_to_pdf(os.path.join(INPUT_DIR, file))

if __name__ == "__main__":
    main()
# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

