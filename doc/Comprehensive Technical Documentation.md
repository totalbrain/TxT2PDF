

This document reflects **the current Dev reality + intentional constraints**, and is suitable as a **technical spec, internal reference, or basis for stabilization and release**.

---

# TxT2PDF (Dev Branch)

## Comprehensive Technical Documentation

---

## 1. Introduction

### 1.1 Scope of This Document

This document provides **complete and up-to-date technical documentation** for the **TxT2PDF project (Dev Branch)**.

The scope is intentionally limited to:

* Architectural design and rationale
* Internal processing logic
* CLI execution model
* Known limitations and edge cases
* Explicit design trade-offs and non-goals

> **Out of scope by design**:
>
> * Markdown support
> * HTML cleaning or sanitization
> * Any form of text preprocessing or transformation
> * Content normalization, rewriting, or filtering

TxT2PDF treats the input text as **opaque raw content** and focuses solely on **rendering it faithfully into PDF form**.

---

## 2. Project Overview

### 2.1 What Is TxT2PDF?

**TxT2PDF** is a **CLI-first utility** for converting **plain text (TXT)** files into **PDF** documents.

The project is optimized for:

* Stability over long-running jobs
* Predictable memory consumption
* Batch and automated execution
* Large, unformatted text files

Typical use cases include:

* System logs
* Script outputs
* Generated reports
* Large raw text archives

---

### 2.2 Core Characteristics

* **Input:** Plain text files (TXT)
* **Output:** One or more PDF files
* **Execution model:** CLI / batch-oriented
* **Processing strategy:** Chunk-based, parallel-capable
* **Text handling:** No modification of content

TxT2PDF does **not** attempt to interpret, clean, or restructure text.
Its responsibility begins and ends with **layout-safe rendering**.

---

## 3. Architectural Goals

The architecture of TxT2PDF is guided by the following goals:

1. **Stability when processing large files**
2. **Predictable and bounded memory usage**
3. **Low architectural complexity**
4. **Reliability in automated environments**
5. **Clear separation of concerns**

Feature richness is explicitly deprioritized in favor of robustness.

---

## 4. High-Level Architecture

### 4.1 Conceptual Processing Pipeline

```
Input TXT File
   ↓
Safe File Reader (encoding-aware)
   ↓
Chunk Size Estimation
   ↓
Chunk Splitting
   ↓
Line-by-Line Rendering
   ↓
PDF Builder (ReportLab)
   ↓
Output PDF File(s)
```

---

### 4.2 Important Behavioral Note (Dev Branch)

In the current Dev implementation:

* Large input files are **split into multiple chunks**
* **Each chunk produces an independent PDF file**
* There is **no shared document state** between chunks

This is a deliberate design choice to ensure stability and parallelism.

---

## 5. Internal Design & Processing Logic

### 5.1 Design Principles

* Input text is treated as **read-only**
* No semantic interpretation of content
* No transformation or preprocessing
* Fail-fast behavior on critical errors
* Explicit control over resource usage

---

### 5.2 Chunk-Based Processing Strategy

#### Rationale

Processing very large text files as a single unit introduces risks:

* Excessive RAM usage
* Unpredictable performance
* Increased likelihood of crashes

To mitigate this, TxT2PDF uses **adaptive chunking**.

---

#### Current Dev Behavior

* File size is estimated using character count and byte size
* A chunk count is calculated dynamically
* Each chunk is capped to a safe upper size
* Chunks are rendered **independently**

Each chunk results in a separate PDF file named using a numeric suffix.

---

#### Trade-offs

| Advantage                | Cost                     |
| ------------------------ | ------------------------ |
| Predictable memory usage | Multiple output PDFs     |
| Parallel processing      | No document continuity   |
| Simple failure recovery  | No shared page numbering |

This trade-off is **intentional and accepted**.

---

## 6. Concurrency Model

### 6.1 Parallel Execution

TxT2PDF supports **controlled multithreading**:

* Multiple chunks may be rendered in parallel
* Thread count is bounded to avoid oversubscription
* Each chunk is isolated from others

Concurrency is applied at the **task level**, not at the document layout level.

---

### 6.2 Implications

* Improves throughput on multi-core systems
* Simplifies error isolation
* Requires careful logging for observability

Parallelism is a **performance optimization**, not a functional requirement.

---

## 7. PDF Rendering Behavior

### 7.1 Text Rendering Rules

* Text is processed **line by line**
* Line breaks are preserved exactly
* Empty lines are rendered as vertical spacing
* No attempt is made to reflow or wrap text semantically

---

### 7.2 Right-to-Left (RTL) Support

#### Current Capabilities (Dev Branch)

* Arabic / Persian text shaping
* Bidirectional reordering
* Right-aligned paragraph rendering
* Unicode-safe text handling

RTL support is implemented **at the paragraph level**.

---

#### Known Limitations

* Tables and complex layouts are **not fully RTL-aware**
* Punctuation and mixed-direction text may render incorrectly
* ReportLab is not natively bidi-aware

RTL support should be considered **partial and experimental**.

---

## 8. CLI Usage

### 8.1 Requirements

* Python 3.9+
* Dependencies:

  * reportlab
  * arabic_reshaper
  * python-bidi

---

### 8.2 Installation

```bash
pip install -r requirements.txt
```

---

### 8.3 Execution

Convert files from the default input directory:

```bash
python TXT2PDF.py
```

Specify a custom input directory:

```bash
python TXT2PDF.py /path/to/txt/files
```

---

### 8.4 Output

* Output PDFs are written to `output_pdf/`
* Large files generate multiple PDFs
* File naming follows a deterministic pattern

---

## 9. Known Issues & Edge Cases

### 9.1 Large File Edge Cases (High Priority)

* Chunk boundary alignment issues
* Trailing newline handling
* Last chunk processing requires careful validation

---

### 9.2 Progress Bar Perception

**Symptom:**
Progress reaches 100% but process does not exit immediately.

**Cause:**
Final PDF rendering and I/O flushing occur after progress completion.

This is expected behavior but requires clearer logging.

---

### 9.3 Encoding Sensitivity

* UTF-8 is assumed
* Mixed or legacy encodings may fail
* Manual encoding override is not yet supported

---

### 9.4 RTL Rendering Issues

* Word order issues in certain contexts
* Incorrect punctuation direction
* Table rendering limitations

---

## 10. Design Trade-offs & Non-Goals

### 10.1 No Text Preprocessing

**Decision:**
TxT2PDF does not clean, normalize, or modify text.

**Reason:**
Text preprocessing introduces ambiguity and hidden behavior.

---

### 10.2 No Full RTL Layout Engine

**Decision:**
Full RTL layout is out of scope.

**Reason:**
Requires a fundamentally different rendering pipeline.

---

### 10.3 CLI-First Design

**Decision:**
TxT2PDF is CLI-first, not a library.

**Roadmap:**
Extraction of a reusable core library is planned but not yet implemented.

---

### 10.4 No Single-PDF Streaming (Dev Branch)

**Decision:**
Each chunk produces an independent PDF.

**Trade-off:**
Stability and predictability over document continuity.

---

## 11. Future Directions (Non-Binding)

* Optional single-PDF streaming mode
* Configurable chunk size
* Improved logging and observability
* Encoding detection and override
* Formal unit and stress tests
* Clearer RTL boundaries and documentation

---

## 12. Conclusion

**TxT2PDF (Dev Branch)** is a **pragmatic, stability-oriented tool** designed for converting raw text into PDF under real-world constraints.

The project deliberately avoids:

* Content interpretation
* Text modification
* Feature-heavy document semantics

In doing so, it provides a **reliable and maintainable foundation** for large-scale, automated text-to-PDF conversion workflows.

---

**This document is a living technical reference and should evolve alongside the codebase.**
