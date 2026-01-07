# TxT2PDF (Dev Branch)

## Low-Level Technical & Programming Documentation

---

## 1. Purpose of This Document

This document describes **the internal software design and implementation details** of the **TxT2PDF Dev Branch**.

It focuses on:

* Code structure and responsibilities
* Execution flow at runtime
* Threading and concurrency behavior
* Chunking logic and memory model
* PDF rendering pipeline
* Logging, observability, and benchmarking
* Known technical constraints in the code

### Explicitly Excluded

The following are **intentionally excluded** from both implementation and documentation:

* HTML cleaning or stripping
* Text normalization or transformation
* Markdown parsing
* Semantic interpretation of text
* Any preprocessing beyond raw file reading

**TxT2PDF treats input text as immutable raw data.**

---

## 2. Codebase Overview (Dev Branch)

### 2.1 Main Modules

```text
TxT2PDF (Dev)
├── TXT2PDF.py        # CLI entry point & orchestration
├── pdf_core.py       # Core PDF rendering & text shaping
├── app_logging.py    # Centralized logging & progress reporting
├── benchmark.py      # Performance benchmark utility
└── doc/
    └── Programming Documentation.md
```

Each module has **clear, non-overlapping responsibilities**.

---

## 3. TXT2PDF.py — CLI & Orchestration Layer

### 3.1 Role of This Module

`TXT2PDF.py` is responsible for:

* CLI argument handling
* Input/output directory management
* File discovery and batching
* Chunk calculation
* Parallel execution of rendering jobs
* High-level progress reporting

This module **does not render PDFs directly**.

---

### 3.2 Execution Flow (High-Level)

```text
Program Start
   ↓
Configure logging (app_logging)
   ↓
Resolve input directory
   ↓
Discover .txt files
   ↓
For each file (parallel):
   ├── Read full text (UTF-8)
   ├── Estimate chunk count
   ├── Split text into chunks
   ├── Dispatch chunk rendering tasks
   └── Track progress via completed futures
   ↓
Program Exit
```

---

### 3.3 File Discovery

* The input directory defaults to a predefined path
* Files are filtered strictly by `.txt` extension
* No recursive traversal (by design)

This keeps file discovery **predictable and fast**.

---

### 3.4 Chunk Estimation Logic

Chunking is based on **approximate output PDF size**, not semantic boundaries.

Key properties:

* File size is estimated using UTF-8 byte length
* A maximum PDF size target (MB) is used as a heuristic
* Chunk count is derived dynamically
* Each chunk is capped to a safe maximum size

This strategy avoids:

* Loading very large buffers into memory
* Excessive PDF page counts in a single render task

---

### 3.5 Chunk Splitting Strategy

* Text is sliced using character indices
* No awareness of:

  * Paragraph boundaries
  * Line boundaries
  * Semantic structure

This is a **deliberate simplification** to keep chunking deterministic and fast.

---

### 3.6 Parallel Task Execution

* Chunk rendering uses `ThreadPoolExecutor`
* Worker count is bounded by chunk count and configuration
* Each chunk is rendered independently
* Failures are isolated per chunk

This design prioritizes **fault isolation and stability** over strict ordering.

---

### 3.7 Progress Reporting

* Progress is tied to **completed futures**, not submitted tasks
* Implemented via `render_progress()` from `app_logging.py`
* Logging is **throttled** by:

  * Percentage change
  * Minimum time interval

**Important:** Progress reaching 100% does not mean the process has exited; final I/O may still be running.

---

## 4. app_logging.py — Centralized Logging & Progress

### 4.1 Design Goals

* Single, centralized logging configuration
* No `basicConfig()` outside the entrypoint
* Thread-safe progress logging
* Linter- and security-compliant implementation

---

### 4.2 Logging Configuration

```python
from app_logging import setup_logging, LoggingConfig

setup_logging(
    LoggingConfig(
        level="INFO",
        log_file="txt2pdf.log",
    )
)
```

---

## 5. pdf_core.py — Core Rendering Engine

### 5.1 Responsibilities

* Font registration (thread-safe)
* RTL shaping and bidi reordering
* Line-to-flowable conversion
* Table detection and rendering
* PDF document construction

---

## 6. Benchmarking

`benchmark.py` provides a repeatable performance test harness.

Example:

```bash
python benchmark.py --sizes 1 10 50 --workers 4
```

---

## 7. Known Technical Limitations

* Chunk boundaries may split lines
* Output order is not guaranteed
* Each chunk produces an independent PDF
* UTF-8 encoding is assumed
* RTL layout is partial (ReportLab limitation)

---

## 8. Final Summary

TxT2PDF (Dev Branch) is a stability-oriented, CLI-first system for converting raw text into PDF with predictable performance and clear failure boundaries.
