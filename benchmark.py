#!/usr/bin/env python3
"""
Performance Testing Script for TXT2PDF

Generates test files and measures conversion performance.
"""

from TXT2PDF import process_file, INPUT_DIR, OUTPUT_DIR
import os
import time
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))


def generate_test_file(size_mb: float, filename: str) -> str:
    """Generate a test text file of specified size."""

    # Sample Persian/Arabic text
    sample_lines = [
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

    os.makedirs(INPUT_DIR, exist_ok=True)
    filepath = os.path.join(INPUT_DIR, filename)

    target_bytes = int(size_mb * 1024 * 1024)
    current_bytes = 0

    with open(filepath, 'w', encoding='utf-8') as f:
        while current_bytes < target_bytes:
            for line in sample_lines:
                f.write(line + '\n')
                current_bytes += len(line.encode('utf-8')) + 1
                if current_bytes >= target_bytes:
                    break

    actual_size = os.path.getsize(filepath) / (1024 * 1024)
    print(f"✓ Generated {filename}: {actual_size:.2f}MB")
    return filepath


def run_performance_test():
    """Run performance tests on different file sizes."""

    print("=" * 60)
    print("TXT2PDF Performance Test")
    print("=" * 60)

    test_cases = [
        (1, "test_1mb.txt"),
        (10, "test_10mb.txt"),
        (50, "test_50mb.txt"),
    ]

    results = []

    for size_mb, filename in test_cases:
        print(f"\n{'─' * 60}")
        print(f"Test: {filename} ({size_mb}MB)")
        print(f"{'─' * 60}")

        # Generate test file
        filepath = generate_test_file(size_mb, filename)

        # Measure conversion time
        start_time = time.time()

        try:
            process_file(filename)
            elapsed = time.time() - start_time

            # Calculate throughput
            throughput = size_mb / elapsed if elapsed > 0 else 0

            results.append({
                'size': size_mb,
                'time': elapsed,
                'throughput': throughput,
                'status': 'SUCCESS'
            })

            print(f"\n✓ Completed in {elapsed:.2f}s ({throughput:.2f} MB/s)")

        except Exception as e:
            elapsed = time.time() - start_time
            results.append({
                'size': size_mb,
                'time': elapsed,
                'throughput': 0,
                'status': f'FAILED: {e}'
            })
            print(f"\n✗ Failed after {elapsed:.2f}s: {e}")

    # Print summary
    print(f"\n{'=' * 60}")
    print("Summary")
    print(f"{'=' * 60}")
    print(f"{'Size':<10} {'Time':<12} {'Throughput':<15} {'Status'}")
    print(f"{'─' * 60}")

    for r in results:
        status = r['status']
        if status == 'SUCCESS':
            print(f"{r['size']:>4}MB    {r['time']:>6.2f}s      "
                  f"{r['throughput']:>6.2f} MB/s    {status}")
        else:
            print(f"{r['size']:>4}MB    {r['time']:>6.2f}s      "
                  f"{'N/A':<13}  {status}")

    print(f"{'=' * 60}\n")

    # Cleanup
    if input("Delete test files? (y/n): ").lower() == 'y':
        for _, filename in test_cases:
            try:
                os.remove(os.path.join(INPUT_DIR, filename))
                # Also remove generated PDFs
                base_name = os.path.splitext(filename)[0]
                for pdf_file in Path(OUTPUT_DIR).glob(f"{base_name}_part*.pdf"):
                    pdf_file.unlink()
                print(f"✓ Deleted {filename} and its PDFs")
            except Exception as e:
                print(f"✗ Error deleting {filename}: {e}")


if __name__ == "__main__":
    try:
        run_performance_test()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
    except Exception as e:
        print(f"\n\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()
