# TxT2PDF

A simple, reliable command-line tool to convert plain text files (.txt) into PDF documents. Designed for batch conversions, customizable layout options, and seamless integration into scripts and workflows.

## Features

- Single-file and batch TXT → PDF conversion
- Customizable page size, margins, font, and encoding
- Preserve simple formatting (line breaks, blank lines)
- Cross-platform CLI usage
- Lightweight and script-friendly

## Requirements

- Python 3.8+ (or relevant runtime if implemented in another language)
- Typical Python build tools if installing from source (pip, venv)

## Installation

Clone the repository and install dependencies (example for Python-based implementation):

```bash
git clone https://github.com/totalbrain/TxT2PDF.git
cd TxT2PDF
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Or install via pip (if packaged):

```bash
pip install txt2pdf
```

## Usage (CLI)

Basic:

```bash
txt2pdf input.txt
# Creates input.pdf in the same directory
```

Specify output file:

```bash
txt2pdf input.txt -o output.pdf
```

Batch convert multiple files:

```bash
txt2pdf *.txt -d ./pdf-output
```

Common options:

```
--output, -o     Output PDF path
--dir, -d        Output directory for batch
--pagesize       Page size (A4, Letter)
--font           Font family (e.g., "DejaVu Sans")
--fontsize       Font size (e.g., 12)
--margins        Margins in mm (top,right,bottom,left)
--encoding       Text encoding (utf-8, latin-1)
--help, -h       Show help
```

Windows example:

```powershell
txt2pdf "C:\Users\Me\Notes.txt" -o "C:\Users\Me\Notes.pdf" --pagesize A4 --font "Consolas" --fontsize 11
```

## Examples

Convert and set page layout:

```bash
txt2pdf report.txt -o report.pdf --pagesize Letter --font "Times New Roman" --fontsize 12 --margins 20,20,20,20
```

Convert all text files in a folder:

```bash
txt2pdf ./texts/*.txt -d ./pdfs
```

## Integration

Use the CLI within scripts or call the library API (if provided) to programmatically convert files, set options, and handle outputs.

## Contributing

- Open an issue for bugs or feature requests.
- Fork, create a feature branch, add tests, and submit a pull request.
- Follow repository code style and include changelog entries for notable changes.

## License

Specify a license (e.g., MIT). Replace this line with the chosen license file and SPDX identifier.

## Contact

For questions or enterprise support, open an issue in this repository.
