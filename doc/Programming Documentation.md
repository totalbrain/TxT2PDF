

This document is written as a **developer reference**, suitable for:

* onboarding a new engineer
* refactoring / stabilization work
* future library extraction
* architecture review

---

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

```
TxT2PDF (Dev)
├── TXT2PDF.py      # CLI entry point & orchestration
└── pdf_core.py     # Core PDF rendering & text shaping
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
* Progress reporting and logging

This module **does not render PDFs directly**.

---

### 3.2 Execution Flow (High-Level)

```
Program Start
   ↓
Resolve input directory
   ↓
Discover .txt files
   ↓
For each file:
   ├── Read full text (UTF-8)
   ├── Estimate chunk count
   ├── Split text into chunks
   ├── Dispatch chunk rendering tasks
   └── Monitor progress
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

* File size is estimated using character count and byte size
* A maximum PDF size target is used as a heuristic
* Chunk count is derived dynamically
* Each chunk is capped to a safe maximum character length

This strategy avoids:

* Loading very large buffers into memory
* Excessive PDF page counts in a single render task

---

### 3.5 Chunk Splitting Strategy

* Text is sliced using character indices
* No awareness of:

  * Paragraph boundaries
  * Line boundaries
  * Encoding boundaries beyond UTF-8 correctness

This is a **deliberate simplification** to keep chunking deterministic.

---

### 3.6 Parallel Task Execution

Chunk rendering is executed using `ThreadPoolExecutor`.

Characteristics:

* Fixed upper bound on worker threads
* Each chunk is rendered independently
* Failures are isolated per chunk
* Errors do not crash the entire batch

This design prioritizes **fault isolation over strict ordering**.

---

### 3.7 Progress Reporting

* Progress is tied to **completed futures**
* Rendering completion ≠ process termination
* Final I/O and PDF build steps may continue after progress reaches 100%

This explains the perceived “freeze” at completion.

---

## 4. pdf_core.py — Core Rendering Engine

### 4.1 Role of This Module

`pdf_core.py` is the **rendering backend**.

Its responsibilities:

* Font registration
* RTL shaping (paragraph-level)
* Line-to-flowable conversion
* PDF document construction
* Layout configuration

This module is **purely functional** with respect to rendering.

---

## 5. Font Management

### 5.1 Font Registration Strategy

* A specific TrueType font is required (e.g., Vazir)
* Fonts are registered once per process
* Duplicate registration attempts are guarded

Font handling is centralized to prevent inconsistent rendering.

---

## 6. Text Handling Model

### 6.1 Immutable Text Contract

* Input text is assumed to be final
* No cleaning, filtering, or transformation is applied
* Lines are rendered exactly as provided

This ensures **lossless rendering**.

---

### 6.2 Line Processing

* Text is split using `splitlines()`
* Each line is processed independently
* Empty lines generate vertical spacing
* Non-empty lines generate paragraph flowables

No reflow or word-wrapping logic is applied beyond ReportLab defaults.

---

## 7. RTL (Right-to-Left) Rendering Pipeline

### 7.1 RTL Processing Steps

For each line:

1. Arabic shaping using `arabic_reshaper`
2. Visual reordering using `python-bidi`
3. Right-aligned paragraph rendering
4. Unicode-safe escaping for ReportLab

This pipeline is applied **only at the paragraph level**.

---

### 7.2 RTL Design Constraints

* ReportLab is not bidi-aware
* Tables and mixed-direction layouts are limited
* Punctuation direction may be incorrect in edge cases

RTL support is **functional but not layout-complete**.

---

## 8. PDF Construction

### 8.1 Flowables Model

* Each rendered element is a ReportLab `Flowable`
* Paragraphs and spacers are appended sequentially
* The ordering of flowables defines final layout

This model is simple and predictable.

---

### 8.2 Document Building

* A `SimpleDocTemplate` is used
* Page size, margins, and layout are fixed
* Each chunk produces **one independent PDF**

There is **no shared canvas or cross-chunk state**.

---

## 9. Concurrency at the Rendering Layer

### 9.1 Internal Parallelism

* Rendering tasks are parallelized at the chunk level
* Rendering logic itself is mostly synchronous
* No shared mutable state between threads

This avoids race conditions at the cost of document continuity.

---

## 10. Memory Model

### 10.1 Memory Characteristics

* Full file text is read once per input file
* Each chunk is processed independently
* Memory usage scales linearly with:

  * Chunk size
  * Number of concurrent workers

This model is predictable and bounded.

---

## 11. Error Handling Strategy

### 11.1 Philosophy

* Fail fast on critical errors
* Isolate failures per chunk
* Log errors with sufficient context
* Do not silently skip failures

This is designed for **batch reliability**.

---

## 12. Known Technical Limitations (Dev Branch)

### 12.1 Chunk Boundary Issues

* Chunks may split mid-line
* No semantic continuity between chunks
* Page numbering resets per chunk

---

### 12.2 Ordering Guarantees

* Parallel execution means output order is not guaranteed
* Output filenames enforce deterministic identification

---

### 12.3 Encoding Assumptions

* UTF-8 is assumed
* No encoding detection or override exists
* Invalid encodings fail early

---

## 13. Design Decisions & Rationale

### 13.1 No Preprocessing

**Decision:** No text preprocessing of any kind.

**Rationale:**
Preprocessing introduces ambiguity, hidden behavior, and maintenance burden.

---

### 13.2 Chunk-Based PDFs

**Decision:** Multiple PDFs instead of a single streamed PDF.

**Rationale:**

* Predictable memory usage
* Simplified concurrency
* Easier failure recovery

---

### 13.3 CLI-First Architecture

**Decision:** CLI-first, not library-first.

**Rationale:**
Most use cases involve automation and batch processing.

---

## 14. Refactoring Readiness

The Dev Branch code is **well-positioned for future refactors**:

* Core rendering is already isolated
* CLI orchestration is explicit
* State management is minimal

Low-risk future steps include:

* Extracting `pdf_core` as a reusable library
* Adding optional single-PDF streaming mode
* Making chunk size configurable
* Improving structured logging

---

## 15. Final Summary

**TxT2PDF (Dev Branch)** is a **deliberately minimal, stability-oriented system** designed to convert raw text into PDF under constrained and predictable conditions.

It avoids:

* Semantic interpretation
* Text mutation
* Feature-heavy document models

In exchange, it delivers:

* Reliability
* Scalability
* Clear failure boundaries
* Maintainable code

This makes TxT2PDF a strong foundation for **production-grade, automated text-to-PDF workflows**.

---

**This document is a developer-level reference and should evolve alongside the Dev Branch codebase.**
