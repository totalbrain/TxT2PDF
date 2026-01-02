# TxT2PDF Technical Details and Code Explanation

## 1. Overview of TxT2PDF Code

The **TxT2PDF** tool is designed to convert plain text (TXT) files into PDF format. The code is structured around reading and processing text files in chunks, and then using the `reportlab` library to generate the final PDF. The main goals of the project are to ensure memory efficiency (by processing files in manageable chunks) and to maintain a simple and predictable structure.

---

## 2. Code Breakdown

### 2.1. Imports and Constants

The TxT2PDF project uses several Python libraries for file handling, text processing, and PDF generation:

```python
from reportlab.platypus import (
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    SimpleDocTemplate,
)
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

import arabic_reshaper
from bidi.algorithm import get_display
```

**Key Libraries:**

* **reportlab**: Used for PDF generation. It handles page layout, fonts, and the structure of the PDF.
* **arabic_reshaper** and **bidi.algorithm**: These libraries are used for handling and rendering right-to-left (RTL) text, specifically for languages like Persian and Arabic.
* **math, os**: These are used for chunk calculations and file management.
* **colors**: Defines color constants for use in tables within the PDF.

---

### 2.2. Helper Functions

#### `safe_paragraph_text(text: str) -> str`

This function ensures that any special characters (like quotation marks) in the text are safely escaped so they don't interfere with HTML/XML rendering or PDF generation.

```python
def safe_paragraph_text(text: str) -> str:
    return escape(text, {"'": "&apos;", '"': "&quot;"})
```

**Purpose:** Prevents issues with special characters that might break XML or HTML-like rendering when converted into a PDF.

#### `shape_text(text: str) -> str`

This function reshapes RTL text (like Arabic or Persian) into its correct visual order using the `arabic_reshaper` and `bidi.algorithm` libraries.

```python
def shape_text(text: str) -> str:
    reshaped = arabic_reshaper.reshape(text)
    visual = get_display(reshaped)
    if isinstance(visual, str):
        return visual
    if isinstance(visual, (bytes, bytearray)):
        return visual.decode("utf-8")
    if _is_memoryview(visual):
        return visual.tobytes().decode("utf-8")

    raise TypeError("Unsupported RTL text type")
```

**Purpose:** Ensures correct rendering of RTL languages in the final PDF. Arabic characters, for example, need to be reshaped and displayed correctly based on their position in the text (e.g., beginning, middle, end).

---

### 2.3. Table Parsing

#### `parse_table(lines: Sequence[str]) -> List[List[str]]`

This function processes table-like structures in the text. It identifies lines that start with `|`, which is commonly used in Markdown or plain-text tables, and processes them into a structured list that can be used to generate a `reportlab` table.

```python
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
```

**Purpose:** Extracts the content of a table from the raw text and converts it into a list of rows and columns, which can then be passed to `reportlab` for PDF rendering.

---

### 2.4. PDF Generation

#### `build_pdf(output_path: str, flowables: Sequence[Flowable]) -> None`

This function takes a list of `Flowable` objects (such as `Paragraph`, `Spacer`, and `Table`) and generates a PDF file using `reportlab`.

```python
def build_pdf(output_path: str, flowables: Sequence[Flowable]) -> None:
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )
    doc.build(list(flowables))
```

**Purpose:** Creates the final PDF document. The flowables are processed and laid out on A4 pages with custom margins.

---

### 2.5. Core Processing Logic

#### `process_text_to_pdf(text: str, output_path: str, font_path: str) -> None`

This is the main function that converts a raw text file into a PDF. It reads the text, processes it line-by-line, handles tables, and generates a PDF.

```python
def process_text_to_pdf(text: str, output_path: str, font_path: str) -> None:
    if not os.path.isfile(font_path):
        print(f"Font file not found: {font_path}")
        return
    else:
        print(f"Font file found: {font_path}")
    
    try:
        pdfmetrics.getFont(FONT_NAME)
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
    in_table = False

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("|"):
            in_table = True
            table_buffer.append(line)
            continue

        if in_table:
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
            shaped = shape_text(line)
            safe = safe_paragraph_text(shaped)
            elements.append(Paragraph(safe, style))
        else:
            elements.append(Spacer(1, 8))

    build_pdf(output_path, elements)
```

**Purpose:** This function processes the text file line by line. It handles plain text as well as tables, reshapes any RTL text, and builds the PDF by adding paragraphs, tables, and spacers. The final PDF is saved at the specified output path.

---

### 2.6. Chunk Estimation

#### `estimate_chunk_count(text: str, max_mb: int) -> int`

This function estimates how many chunks the text should be split into based on the file size, ensuring that each chunk is no larger than a specified size (in megabytes). This is useful for handling very large files.

```python
def estimate_chunk_count(text: str, max_mb: int) -> int:
    approx_chars = AVG_CHARS_PER_MB * max_mb
    if approx_chars <= 0:
        return 1
    return max(1, math.ceil(len(text) / approx_chars))
```

**Purpose:** To ensure that the file is split into manageable parts, preventing memory overload when processing very large files.

---

## 3. Conclusion

### Key Points:

1. **Chunk-based Processing**: To avoid memory overload, the tool processes text in chunks (e.g., 20MB).
2. **RTL Text Handling**: Using `arabic_reshaper` and `bidi.algorithm`, the tool can properly handle right-to-left languages.
3. **Modular Design**: The code is modular, with separate functions for text processing, table parsing, and PDF generation, making it easy to maintain and extend.
4. **Simplicity**: The tool aims to keep things simple by focusing only on plain text and basic formatting, ensuring reliability in automated environments.
