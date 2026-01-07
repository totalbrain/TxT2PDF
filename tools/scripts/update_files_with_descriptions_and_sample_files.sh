#!/usr/bin/env bash
set -e

# مسیر پوشه dev-structure که ساختار باید در آن ایجاد شود
DEV_STRUCTURE_DIR="D:/old user/Documents/My-Work-and-Projects/Software Engineer/Helpful_Scripts/Converter/TxT2PDF/dev-structure"

echo "▶ Updating files in the 'dev-structure' branch with descriptions and meaningful sample files..."

# -------------------------
# ایجاد فایل توضیحات و فایل‌های نمونه معنادار
# -------------------------

# unit tests
echo "This folder contains unit tests related to chunking, text processing, and file splitting." > "$DEV_STRUCTURE_DIR/tests/unit/unit_tests_description"
touch "$DEV_STRUCTURE_DIR/tests/unit/chunking_test.py"

# functional tests
echo "This folder contains functional tests for various input sizes and conversion checks." > "$DEV_STRUCTURE_DIR/tests/functional/functional_tests_description"
touch "$DEV_STRUCTURE_DIR/tests/functional/small_input_test.py"

# stress tests
echo "This folder contains stress tests for large input files and performance analysis." > "$DEV_STRUCTURE_DIR/tests/stress/stress_tests_description"
touch "$DEV_STRUCTURE_DIR/tests/stress/large_input_stress.py"

# bisect tests
echo "This folder contains bisect tests to identify corrupted input files and trace errors." > "$DEV_STRUCTURE_DIR/tests/bisect/bisect_tests_description"
touch "$DEV_STRUCTURE_DIR/tests/bisect/corruption_bisect.py"

# fixtures
echo "This folder contains test fixtures that provide predefined data for unit and functional tests." > "$DEV_STRUCTURE_DIR/tests/fixtures/test_fixtures_description"
touch "$DEV_STRUCTURE_DIR/tests/fixtures/sample_fixture.txt"

# benchmark tools
echo "This folder contains benchmarking scripts to test performance and throughput of the conversion." > "$DEV_STRUCTURE_DIR/tools/benchmarks/benchmark_tools_description"
touch "$DEV_STRUCTURE_DIR/tools/benchmarks/performance_benchmark.py"

# scripts for automation
echo "This folder contains scripts for automating various tasks related to the project." > "$DEV_STRUCTURE_DIR/tools/scripts/automation_scripts_description"
touch "$DEV_STRUCTURE_DIR/tools/scripts/ci_integration_script.py"

# debugging tools
echo "This folder contains tools for debugging, error tracing, and log analysis." > "$DEV_STRUCTURE_DIR/tools/debugging/debugging_tools_description"
touch "$DEV_STRUCTURE_DIR/tools/debugging/error_tracing_tool.py"

# CI docs and templates
echo "This folder contains CI documentation and templates for workflows." > "$DEV_STRUCTURE_DIR/ci/docs/ci_docs_description"
touch "$DEV_STRUCTURE_DIR/ci/docs/ci_workflow_template.yml"
echo "This folder contains templates for CI configuration files." > "$DEV_STRUCTURE_DIR/ci/templates/ci_templates_description"
touch "$DEV_STRUCTURE_DIR/ci/templates/ci_config_template.yml"

# documentation
echo "This folder contains architectural documentation for the TxT2PDF project." > "$DEV_STRUCTURE_DIR/docs/architecture/architecture_docs_description"
touch "$DEV_STRUCTURE_DIR/docs/architecture/system_architecture.md"
echo "This folder contains design decisions and rationale behind the system." > "$DEV_STRUCTURE_DIR/docs/design/design_docs_description"
touch "$DEV_STRUCTURE_DIR/docs/design/architecture_design.md"
echo "This folder contains project decision-making documents." > "$DEV_STRUCTURE_DIR/docs/decisions/decision_docs_description"
touch "$DEV_STRUCTURE_DIR/docs/decisions/project_decisions.md"

# runtime directories
echo "This folder contains input text files for conversion into PDF." > "$DEV_STRUCTURE_DIR/input_txt/input_files_description"
touch "$DEV_STRUCTURE_DIR/input_txt/sample_input_file.txt"
echo "This folder contains output PDF files generated from text files." > "$DEV_STRUCTURE_DIR/output_pdf/output_files_description"
touch "$DEV_STRUCTURE_DIR/output_pdf/converted_output.pdf"

# -------------------------
# فایل‌های CI و Workflow
# -------------------------
cat > "$DEV_STRUCTURE_DIR/.github/workflows/ci.yml" << 'EOF'
name: CI Workflow

on:
  push:
    branches:
      - dev-structure
  pull_request:
    branches:
      - main

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - name: Check out code
        uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.8'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt

      - name: Run tests
        run: |
          pytest tests/

  lint:
    runs-on: ubuntu-latest

    steps:
      - name: Check out code
        uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.8'

      - name: Install flake8
        run: |
          pip install flake8

      - name: Run flake8
        run: |
          flake8 src/
EOF

# -------------------------
# فایل‌های مستندات
# -------------------------
cat > "$DEV_STRUCTURE_DIR/README.md" << 'EOF'
# TxT2PDF

Repository structure bootstrapped.
TODO: update README after architecture stabilization.
EOF

cat > "$DEV_STRUCTURE_DIR/pytest.ini" << 'EOF'
# TODO:
# pytest configuration will be added later
EOF

cat > "$DEV_STRUCTURE_DIR/pyproject.toml" << 'EOF'
# TODO:
# future packaging & tooling configuration
EOF

echo
echo "✅ Files updated with descriptions and meaningful sample files successfully."
echo
echo "Next recommended steps:"
echo "1. Start adding implementation files to the 'src' folder."
echo "2. Fill the test files with real logic."
echo "3. Commit the changes as: 'chore: add descriptions and sample files to dev-structure'"
