#!/usr/bin/env python3
"""
Performance Benchmark Script for TXT2PDF

- Generates test text files (Persian/Arabic + table samples).
- Runs TXT->PDF conversion.
- Logs timing and throughput results.

Usage examples:
  python benchmark.py
  python benchmark.py --sizes 1 10 50 --workers 4
  python benchmark.py --repeat 3 --cleanup
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import logging

# Ensure the project directory is importable BEFORE importing project modules.
PROJECT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_DIR))

from app_logging import LoggingConfig, setup_logging  # noqa: E402
from TXT2PDF import process_file  # noqa: E402


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class BenchmarkResult:
    size_mb: float
    elapsed_sec: float
    throughput_mb_s: float
    status: str


def _sample_lines() -> list[str]:
    # Includes normal RTL text + a simple markdown-like table to exercise parse_table().
    return [
        "این یک متن تستی است برای بررسی عملکرد برنامه تبدیل متن به PDF.",
        "سیستم باید بتواند فایل‌های بزرگ را با سرعت بالا پردازش کند.",
        "این خط شامل متن طولانی‌تری است که برای تست شکل‌دهی متن RTL استفاده می‌شود.",
        "| ستون 1 | ستون 2 | ستون 3 |",
        "| --- | --- | --- |",
        "| داده 1 | داده 2 | داده 3 |",
        "| ردیف بعدی | اطلاعات | مقادیر |",
        "",
        "پاراگراف جدید پس از جدول با محتوای بیشتر برای تست.",
    ]


def generate_test_file(input_dir: Path, size_mb: float, filename: str) -> Path:
    """
    Generate a UTF-8 test file with approximately `size_mb` megabytes of content.
    """
    input_dir.mkdir(parents=True, exist_ok=True)
    filepath = input_dir / filename

    target_bytes = int(size_mb * 1024 * 1024)
    written_bytes = 0
    lines = _sample_lines()

    logger.info("Generating test file: %s (target=%.2fMB)", filepath.name, size_mb)

    with filepath.open("w", encoding="utf-8", newline="\n") as f:
        while written_bytes < target_bytes:
            for line in lines:
                f.write(line + "\n")
                written_bytes += len((line + "\n").encode("utf-8"))
                if written_bytes >= target_bytes:
                    break

    actual_size = filepath.stat().st_size / (1024 * 1024)
    logger.info("Generated: %s (actual=%.2fMB)", filepath.name, actual_size)
    return filepath


def _iter_generated_pdfs(output_dir: Path, base_name: str) -> Iterable[Path]:
    # Matches TXT2PDF naming: <stem>_part<idx>.pdf
    return output_dir.glob(f"{base_name}_part*.pdf")


def run_benchmark(
    input_dir: Path,
    output_dir: Path,
    sizes: list[float],
    *,
    workers: int,
    repeat: int,
    cleanup: bool,
) -> list[BenchmarkResult]:
    """
    Run the benchmark across multiple file sizes.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    results: list[BenchmarkResult] = []

    logger.info("=" * 70)
    logger.info("TXT2PDF Benchmark")
    logger.info("Input dir:  %s", input_dir)
    logger.info("Output dir: %s", output_dir)
    logger.info("Sizes (MB): %s", sizes)
    logger.info("Repeat:     %d", repeat)
    logger.info("Workers:    %d", workers)
    logger.info("=" * 70)

    for size_mb in sizes:
        filename = f"test_{int(size_mb)}mb.txt"
        input_path = generate_test_file(input_dir, size_mb, filename)
        base_name = input_path.stem

        # Optional: remove old PDFs for a clean run
        for old_pdf in _iter_generated_pdfs(output_dir, base_name):
            try:
                old_pdf.unlink()
            except OSError:
                logger.warning("Could not delete old pdf: %s", old_pdf.name)

        logger.info("-" * 70)
        logger.info("Test case: %s (%.2fMB)", input_path.name, size_mb)
        logger.info("-" * 70)

        for run_idx in range(1, repeat + 1):
            start = time.perf_counter()
            try:
                # process_file signature is (input_path: Path, output_dir: Path, ...)
                process_file(
                    input_path,
                    output_dir,
                    max_workers=workers,
                )
                elapsed = time.perf_counter() - start
                throughput = (size_mb / elapsed) if elapsed > 0 else 0.0

                results.append(
                    BenchmarkResult(
                        size_mb=size_mb,
                        elapsed_sec=elapsed,
                        throughput_mb_s=throughput,
                        status=f"SUCCESS (run {run_idx}/{repeat})",
                    )
                )

                logger.info(
                    "Run %d/%d: %.2fs | %.2f MB/s",
                    run_idx,
                    repeat,
                    elapsed,
                    throughput,
                )
            except Exception as exc:
                elapsed = time.perf_counter() - start
                results.append(
                    BenchmarkResult(
                        size_mb=size_mb,
                        elapsed_sec=elapsed,
                        throughput_mb_s=0.0,
                        status=f"FAILED (run {run_idx}/{repeat}): {exc}",
                    )
                )
                logger.exception("Benchmark failed: %s", input_path.name)

    logger.info("=" * 70)
    logger.info("Summary")
    logger.info("=" * 70)
    logger.info("%-10s %-12s %-16s %s", "Size", "Time", "Throughput", "Status")
    logger.info("-" * 70)

    for r in results:
        size_label = f"{int(r.size_mb)}MB"
        time_label = f"{r.elapsed_sec:.2f}s"
        thr_label = f"{r.throughput_mb_s:.2f} MB/s" if r.throughput_mb_s > 0 else "N/A"
        logger.info("%-10s %-12s %-16s %s", size_label, time_label, thr_label, r.status)

    logger.info("=" * 70)

    if cleanup:
        logger.info("Cleanup enabled: deleting generated test files and PDFs...")
        for size_mb in sizes:
            filename = f"test_{int(size_mb)}mb.txt"
            input_path = input_dir / filename
            base_name = input_path.stem

            try:
                if input_path.exists():
                    input_path.unlink()
            except OSError:
                logger.warning("Could not delete test file: %s", input_path.name)

            for pdf_file in _iter_generated_pdfs(output_dir, base_name):
                try:
                    pdf_file.unlink()
                except OSError:
                    logger.warning("Could not delete pdf: %s", pdf_file.name)

    return results


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="TXT2PDF performance benchmark")
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=Path("input_txt"),
        help="Directory to write generated test .txt files",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("output_pdf"),
        help="Directory where PDFs are written",
    )
    parser.add_argument(
        "--sizes",
        type=float,
        nargs="*",
        default=[1, 10, 50],
        help="List of test sizes in MB (e.g., --sizes 1 10 50)",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=4,
        help="Max worker threads for chunk rendering per file",
    )
    parser.add_argument(
        "--repeat",
        type=int,
        default=1,
        help="Repeat each test case N times",
    )
    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="Delete generated test files and PDFs after benchmark",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default=os.getenv("LOG_LEVEL", "INFO"),
        help="Logging level (default: env LOG_LEVEL or INFO)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    # Central logging configuration (compatible with app_logging.py)
    setup_logging(
        LoggingConfig(
            level=str(args.log_level).upper(),
            log_file="benchmark.log",
            # Benchmark is often run standalone; forcing avoids surprises if re-run in same process.
            force_reconfigure=True,
        )
    )

    run_benchmark(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        sizes=list(args.sizes),
        workers=args.workers,
        repeat=args.repeat,
        cleanup=args.cleanup,
    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Benchmark interrupted by user.")
    except Exception:
        logger.exception("Benchmark failed unexpectedly.")
        raise
