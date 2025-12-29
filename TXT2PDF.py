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

TARGET_PDF_SIZE = 20 * 1024 * 1024   # 20MB
SAFETY_RATIO    = 0.85
# ===========================================================

os.makedirs(OUTPUT_DIR, exist_ok=True)

if not os.path.exists(FONT_PATH):
    raise FileNotFoundError(" Font file must be placed next to the script.❌ ")

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

# فارسی | لاتین | علائم نگارشی
TOKEN_RE = re.compile(
    rf'({PERSIAN_RE}|{LATIN_RE}|[^\w\s])'
)

# ---------- تشخیص خطوط حساس ----------
def is_table_line(line: str) -> bool:
    line = line.strip()
    return (
        '|' in line
        or line.startswith(':---')
        or line.startswith('---')
    )

# ---------- پردازش امن خط ----------
def process_line_safe(line: str) -> str:
    if is_table_line(line):
        # جدول / Markdown را دست نزن
        return line

    tokens = TOKEN_RE.findall(line)
    visual = []

    for tok in tokens:
        if re.search(PERSIAN_RE, tok):
            reshaped = arabic_reshaper.reshape(tok)
            visual.append(get_display(reshaped))
        else:
            visual.append(tok)

    # پاراگراف RTL است
    return "".join(visual[::-1])

# ---------- تقسیم متن بر اساس حجم ----------
def split_by_estimated_size(lines):
    max_bytes = TARGET_PDF_SIZE * SAFETY_RATIO

    chunks = []
    current = []
    size = 0

    for line in lines:
        b = len(line.encode("utf-8"))
        if size + b > max_bytes and current:
            chunks.append(current)
            current = []
            size = 0
        current.append(line)
        size += b

    if current:
        chunks.append(current)

    return chunks

# ---------- تبدیل TXT به PDF ----------
def txt_to_pdf(txt_path):
    base = os.path.splitext(os.path.basename(txt_path))[0]

    with open(txt_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    chunks = split_by_estimated_size(lines)

    for i, chunk in enumerate(chunks, start=1):
        name = f"{base}_part_{i}.pdf" if len(chunks) > 1 else f"{base}.pdf"
        out_path = os.path.join(OUTPUT_DIR, name)

        doc = SimpleDocTemplate(
            out_path,
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
                story.append(
                    Paragraph(process_line_safe(line), styles["RTL"])
                )

        doc.build(story)
        print(f"{name} Is Done! ✔ ")

# ---------- اجرای اصلی ----------
def main():
    files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith(".txt")]
    if not files:
        print(" No TXT files found.⚠️")
        return

    for f in files:
        print(f"Processing : {f} ▶")
        txt_to_pdf(os.path.join(INPUT_DIR, f))

if __name__ == "__main__":
    main()
