
---

# TxT2PDF Project Documentation

## 1. Introduction

### Scope of this Document

This document provides detailed information about the **TxT2PDF** project, which is a utility designed to convert plain text (TXT) files into PDF format. The focus of this document is on the technical aspects, architecture, features, limitations, and installation process of the TxT2PDF tool. This tool operates as a command-line interface (CLI) that ensures simple, reliable, and efficient conversion of text files into PDFs.

---

### TxT2PDF Overview

The **TxT2PDF** project was created to convert plain text files (TXT) into PDF format. The tool is designed with simplicity, stability, and efficiency in mind. It is ideal for converting raw text files, logs, script outputs, and other unformatted text into well-structured PDFs.

Key Features:

* Convert single or multiple TXT files to PDF
* Retain line structure and spacing
* Customize font, page size, and margins
* Ideal for large files (using chunk-based processing)

---

## 2. Architecture of TxT2PDF

### Architecture Objective

The architecture of TxT2PDF has been designed with the following core goals:

1. **Stability in processing large text files**
2. **Simplicity and ease of maintenance**
3. **Usability in automated scripts and pipelines**

### Overall Processing Flow

The process is broken down as follows:

```
TXT File
  ↓
Safe Reader (encoding-aware)
  ↓
Chunk Processor (20MB)
  ↓
Line Layout Engine
  ↓
PDF Builder (reportlab)
  ↓
Output PDF
```

### Main Components

1. **File Reader**: Safely reads the input file with proper encoding handling.
2. **Chunk Manager**: Breaks large files into manageable chunks (20MB).
3. **Layout Engine**: Handles line breaks and page breaks.
4. **PDF Renderer**: Uses `reportlab` to create the final PDF output.

---

### Directory Structure

```
project-root/
├── src/
│   ├── converter.py       # Main entry point for the CLI
│   ├── text_processor.py  # Responsible for processing raw text
│   ├── pdf_builder.py     # Builds the PDF using reportlab
│   └── utils.py           # Utility functions for encoding, path, chunking
├── inputs/                # Directory for input TXT files
├── outputs/               # Directory for output PDF files
├── requirements.txt       # Lists the necessary Python dependencies
└── README.md              # Project documentation
```

### Module Descriptions

* **converter.py**: The entry point of the program. It manages CLI arguments and controls the execution flow of the conversion process.
* **text_processor.py**: Handles the conversion of raw text files into PDF-ready content, including safe encoding handling and text processing.
* **pdf_builder.py**: Uses the `reportlab` library to generate the PDF from processed text.
* **utils.py**: Contains utility functions such as encoding handling, path management, and chunk splitting.

---

## 3. Installation and Setup

### Prerequisites

To run **TxT2PDF**, ensure you have the following:

* Python 3.9 or higher
* `reportlab` library for PDF generation
* A font file for rendering (e.g., `Vazir` for Persian text support)

### Installation Steps

1. Install the necessary dependencies:

```
pip install reportlab
```

Or use the provided `requirements.txt` file:

```
pip install -r requirements.txt
```

2. Ensure you have a compatible font file (e.g., `Vazir-Regular.ttf`) for rendering text correctly.

### Running the Program

To convert a single TXT file:

```
python converter.py input.txt
```

To convert multiple TXT files (batch processing):

```
python converter.py inputs/
```

### Output

The resulting PDFs will be stored in the `outputs/` directory by default.

---

## 4. Core Logic and Implementation

### Design Principles

* **No complete file loading into memory**: Only chunks of the file are processed to ensure memory efficiency.
* **Sequential and predictable processing**: Processing happens in a controlled, step-by-step manner.
* **Minimal external dependencies**: Apart from the required libraries, the project aims to be lightweight and simple.

### Processing Steps

1. **Detecting encoding**: The file encoding is detected safely, with fallbacks if necessary.
2. **Chunk processing**: Large files are divided into manageable chunks of 20MB.
3. **Line-by-line processing**: Each chunk is processed line by line to generate the final output.
4. **Page breaks**: Pages are divided based on length, ensuring each chunk fits into a single PDF page.
5. **PDF Generation**: The processed text is sent to the `pdf_builder` to generate the final PDF output.

### Key Functions

* `process_text_to_pdf()`: The main function that converts text into a PDF.
* `estimate_chunk_count()`: Estimates the number of chunks needed for large files, ensuring efficient processing.

---

## 5. Performance Considerations

### Memory Efficiency

* **Fixed memory usage**: By processing the file in chunks of 20MB, the program keeps memory usage predictable and stable.
* **Efficient for large files**: The chunk-based processing approach ensures that even very large files (several gigabytes) can be processed without causing excessive memory usage.

### Optimization

* **Chunk size tuning**: The 20MB chunk size was chosen based on practical experience and can be adjusted in the future if necessary.
* **Page break management**: Careful management of page breaks ensures that the resulting PDF has a consistent and clean layout, with no content spilling over or overlapping.

---

## 6. Limitations and Known Issues

### RTL Support

TxT2PDF does **not** fully support right-to-left (RTL) languages like Persian or Arabic. Some of the known issues are:

* Word order disruption in RTL text.
* Incorrect display of parentheses and punctuation.

### Formatting Limitations

* **Bold/Italic/Heading support**: The current version does not support advanced formatting like bold, italic, or heading styles.
* **Structure retention**: Only basic line and paragraph structure are preserved.

### Large File Handling

* **Progress bar freeze**: When processing large files, the progress bar may appear frozen at 100%. This is due to I/O processing completing after the main iteration has finished.
* **Memory usage**: While chunk-based processing ensures memory efficiency, there may still be issues with very large files that approach the system's memory limits.

---

## 7. Conclusion

**TxT2PDF** is a simple, stable, and reliable tool for converting plain text files into PDF format. By focusing on raw text processing, it avoids the complexity of dealing with advanced formatting or multi-language support. This makes it highly suitable for converting large text files and logs into structured PDF documents for documentation or reporting purposes.

---

## 8. Future Proposals

The following improvements are planned for future releases of **TxT2PDF**:

* **Full RTL support**: Incorporating support for right-to-left text rendering, especially for Persian and Arabic languages.
* **Advanced formatting support**: Adding support for bold, italic, headings, and other styles.
* **Error handling and logging improvements**: Enhancing error messages and adding more detailed logging for debugging.
* **PDF output configuration**: Allowing users to customize PDF output settings, such as font size, margins, and page layout.
* **Library version**: Refactoring the tool to offer a library version alongside the CLI, enabling easier integration into other projects.

---

**This document is a living document and will be updated as the project evolves.**

---

This version of the documentation covers **only the TxT2PDF project**, ensuring clarity and completeness while leaving the **TXTandMD2PDF** project out of scope.
