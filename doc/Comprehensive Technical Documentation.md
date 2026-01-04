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
* Logging, observability, and concurrency behavior
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

```text
Input TXT File
   ↓
Safe File Reader (UTF-8)
   ↓
Chunk Size Estimation
   ↓
Chunk Splitting
   ↓
Parallel Chunk Rendering
   ↓
PDF Builder (ReportLab)
   ↓
Output PDF File(s)
```

---

### 4.2 Behavioral Characteristics (Dev Branch)

In the current Dev implementation:

* Large input files are **split into multiple chunks**
* **Each chunk produces an independent PDF file**
* There is **no shared document state** between chunks

This is a deliberate design choice to ensure stability, bounded memory usage, and safe parallelism.

---

## 5. Internal Design & Processing Logic

### 5.1 Design Principles

* Input text is treated as **read-only**
* No semantic interpretation of content
* No transformation or preprocessing
* Fail-fast behavior on critical errors
* Explicit control over concurrency and resources

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

* File size is estimated using UTF-8 byte length
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

## 6. Concurrency & Logging Model

### 6.1 Concurrency Model

* File-level parallelism in `TXT2PDF.py`
* Chunk-level parallelism per file via `ThreadPoolExecutor`
* Rendering logic itself avoids nested executors
* No shared mutable state across threads

This minimizes race conditions and oversubscription.

---

### 6.2 Logging & Observability

* Centralized logging via `app_logging.py`
* Root logger configured once at application entrypoint
* Console + rotating file handlers
* Progress logging is **throttled** (time + percentage based)

Progress reporting is based on **completed futures**, not task submission.

---

## 7. PDF Rendering Behavior

### 7.1 Text Rendering Rules

* Text is processed **line by line**
* Line breaks are preserved exactly
* Empty lines are rendered as vertical spacing
* No attempt is made to reflow or wrap text semantically

---

### 7.2 Right-to-Left (RTL) Support

#### Current Capabilities

* Arabic / Persian text shaping
* Bidirectional reordering
* Right-aligned paragraph rendering
* Unicode-safe escaping for ReportLab

RTL support is implemented **at the paragraph level**.

---

#### Known Limitations

* Tables and complex layouts are **not fully RTL-aware**
* Punctuation and mixed-direction text may render incorrectly
* ReportLab is not natively bidi-aware

RTL behavior should be considered **partial and experimental**.

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

Default execution:

```bash
python TXT2PDF.py
```

Custom input/output directories:

```bash
python TXT2PDF.py /path/to/input /path/to/output
```

---

## 9. Known Issues & Edge Cases

### 9.1 Large File Edge Cases

* Chunk boundaries may split lines
* Trailing newline handling is sensitive
* Final chunk must be validated carefully

---

### 9.2 Progress Bar Perception

**Symptom:**
Progress reaches 100% but the process does not exit immediately.

**Cause:**
Final PDF rendering and I/O flushing occur after progress completion.

This is expected behavior and is logged explicitly.

---

### 9.3 Encoding Sensitivity

* UTF-8 is assumed
* Mixed or legacy encodings may fail early
* Manual encoding override is not yet supported

---

## 10. Design Trade-offs & Non-Goals

### 10.1 No Text Preprocessing

**Decision:** No cleaning, normalization, or transformation.

**Reason:** Avoid hidden behavior and ambiguity.

---

### 10.2 No Full RTL Layout Engine

**Decision:** Full RTL layout is out of scope.

**Reason:** Requires a fundamentally different rendering pipeline.

---

### 10.3 CLI-First Architecture

**Decision:** CLI-first, not library-first.

**Roadmap:** Core extraction is possible but not yet planned.

---

### 10.4 No Single-PDF Streaming (Dev Branch)

**Decision:** Each chunk produces an independent PDF.

**Trade-off:** Stability and predictability over document continuity.

---

## 11. Future Directions (Non-Binding)

* Optional single-PDF streaming mode
* Configurable chunk size
* Improved structured logging
* Encoding detection and override
* Formal unit and stress tests
* Clearer RTL documentation and guarantees

---

## 12. Conclusion

**TxT2PDF (Dev Branch)** is a pragmatic, stability-oriented system for converting raw text into PDF under real-world constraints.

By deliberately avoiding content interpretation and text mutation, the project delivers:

* Predictable behavior
* Bounded resource usage
* Clear failure modes
* Maintainable and auditable code

This document reflects the **current Dev reality** and should evolve alongside the codebase.
