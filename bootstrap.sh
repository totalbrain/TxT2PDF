#!/usr/bin/env bash
set +e  # Disable script termination on error

# Path to the dev-structure folder where the structure should be created
DEV_STRUCTURE_DIR="D:/old user/Documents/My-Work-and-Projects/Software Engineer/Helpful_Scripts/Converter/TxT2PDF/dev-structure"

echo "▶ Bootstrapping repository structure for 'dev-structure' branch..."

# -------------------------
# Create directories
# -------------------------
mkdir -p "$DEV_STRUCTURE_DIR/src/core" || echo "Error creating directory src/core"
mkdir -p "$DEV_STRUCTURE_DIR/tests/unit" || echo "Error creating directory tests/unit"
mkdir -p "$DEV_STRUCTURE_DIR/tests/functional" || echo "Error creating directory tests/functional"
mkdir -p "$DEV_STRUCTURE_DIR/tests/stress" || echo "Error creating directory tests/stress"
mkdir -p "$DEV_STRUCTURE_DIR/tests/bisect" || echo "Error creating directory tests/bisect"
mkdir -p "$DEV_STRUCTURE_DIR/tests/fixtures" || echo "Error creating directory tests/fixtures"
mkdir -p "$DEV_STRUCTURE_DIR/tools/benchmarks" || echo "Error creating directory tools/benchmarks"
mkdir -p "$DEV_STRUCTURE_DIR/tools/scripts" || echo "Error creating directory tools/scripts"
mkdir -p "$DEV_STRUCTURE_DIR/tools/debugging" || echo "Error creating directory tools/debugging"
mkdir -p "$DEV_STRUCTURE_DIR/ci/docs" || echo "Error creating directory ci/docs"
mkdir -p "$DEV_STRUCTURE_DIR/ci/templates" || echo "Error creating directory ci/templates"
mkdir -p "$DEV_STRUCTURE_DIR/.github/workflows" || echo "Error creating directory .github/workflows"
mkdir -p "$DEV_STRUCTURE_DIR/docs/architecture" || echo "Error creating directory docs/architecture"
mkdir -p "$DEV_STRUCTURE_DIR/docs/design" || echo "Error creating directory docs/design"
mkdir -p "$DEV_STRUCTURE_DIR/docs/decisions" || echo "Error creating directory docs/decisions"
mkdir -p "$DEV_STRUCTURE_DIR/input_txt" || echo "Error creating directory input_txt"
mkdir -p "$DEV_STRUCTURE_DIR/output_pdf" || echo "Error creating directory output_pdf"

# -------------------------
# Create placeholder files
# -------------------------
touch "$DEV_STRUCTURE_DIR/src/__init__.py" || echo "Error creating file __init__.py"
touch "$DEV_STRUCTURE_DIR/src/cli.py" || echo "Error creating file cli.py"
touch "$DEV_STRUCTURE_DIR/src/config.py" || echo "Error creating file config.py"
touch "$DEV_STRUCTURE_DIR/src/core/__init__.py" || echo "Error creating file core/__init__.py"
touch "$DEV_STRUCTURE_DIR/src/core/pdf_core.py" || echo "Error creating file pdf_core.py"

# -------------------------
# Rename description files and create new ones
# -------------------------

# Unit Tests
mv "$DEV_STRUCTURE_DIR/tests/unit/unit_tests_description" "$DEV_STRUCTURE_DIR/tests/unit/This-folder-contains-unit-tests-related-to-chunking-text-processing-and-file-splitting" || echo "Error renaming file unit_tests_description"
touch "$DEV_STRUCTURE_DIR/tests/unit/chunking_test.py" || echo "Error creating file chunking_test.py"

# Functional Tests
mv "$DEV_STRUCTURE_DIR/tests/functional/functional_tests_description" "$DEV_STRUCTURE_DIR/tests/functional/This-folder-contains-functional-tests-for-various-input-sizes-and-conversion-checks" || echo "Error renaming file functional_tests_description"
touch "$DEV_STRUCTURE_DIR/tests/functional/small_input_test.py" || echo "Error creating file small_input_test.py"

# Stress Tests
mv "$DEV_STRUCTURE_DIR/tests/stress/stress_tests_description" "$DEV_STRUCTURE_DIR/tests/stress/This-folder-contains-stress-tests-for-large-input-files-and-performance-analysis" || echo "Error renaming file stress_tests_description"
touch "$DEV_STRUCTURE_DIR/tests/stress/large_input_stress.py" || echo "Error creating file large_input_stress.py"

# Bisect Tests
mv "$DEV_STRUCTURE_DIR/tests/bisect/bisect_tests_description" "$DEV_STRUCTURE_DIR/tests/bisect/This-folder-contains-bisect-tests-to-identify-corrupted-input-files-and-trace-errors" || echo "Error renaming file bisect_tests_description"
touch "$DEV_STRUCTURE_DIR/tests/bisect/corruption_bisect.py" || echo "Error creating file corruption_bisect.py"

# Fixtures
mv "$DEV_STRUCTURE_DIR/tests/fixtures/test_fixtures_description" "$DEV_STRUCTURE_DIR/tests/fixtures/This-folder-contains-test-fixtures-that-provide-predefined-data-for-unit-and-functional-tests" || echo "Error renaming file test_fixtures_description"
touch "$DEV_STRUCTURE_DIR/tests/fixtures/sample_fixture.txt" || echo "Error creating file sample_fixture.txt"

# Benchmark Tools
mv "$DEV_STRUCTURE_DIR/tools/benchmarks/benchmark_tools_description" "$DEV_STRUCTURE_DIR/tools/benchmarks/This-folder-contains-benchmarking-scripts-to-test-performance-and-throughput-of-the-conversion" || echo "Error renaming file benchmark_tools_description"
touch "$DEV_STRUCTURE_DIR/tools/benchmarks/performance_benchmark.py" || echo "Error creating file performance_benchmark.py"

# Automation Scripts
mv "$DEV_STRUCTURE_DIR/tools/scripts/automation_scripts_description" "$DEV_STRUCTURE_DIR/tools/scripts/This-folder-contains-scripts-for-automating-various-tasks-related-to-the-project" || echo "Error renaming file automation_scripts_description"
touch "$DEV_STRUCTURE_DIR/tools/scripts/ci_integration_script.py" || echo "Error creating file ci_integration_script.py"

# Debugging Tools
mv "$DEV_STRUCTURE_DIR/tools/debugging/debugging_tools_description" "$DEV_STRUCTURE_DIR/tools/debugging/This-folder-contains-tools-for-debugging-error-tracing-and-log-analysis" || echo "Error renaming file debugging_tools_description"
touch "$DEV_STRUCTURE_DIR/tools/debugging/error_tracing_tool.py" || echo "Error creating file error_tracing_tool.py"

# CI Docs and Templates
mv "$DEV_STRUCTURE_DIR/ci/docs/ci_docs_description" "$DEV_STRUCTURE_DIR/ci/docs/This-folder-contains-CI-documentation-and-templates-for-workflows" || echo "Error renaming file ci_docs_description"
touch "$DEV_STRUCTURE_DIR/ci/docs/ci_workflow_template.yml" || echo "Error creating file ci_workflow_template.yml"
mv "$DEV_STRUCTURE_DIR/ci/templates/ci_templates_description" "$DEV_STRUCTURE_DIR/ci/templates/This-folder-contains-templates-for-CI-configuration-files" || echo "Error renaming file ci_templates_description"
touch "$DEV_STRUCTURE_DIR/ci/templates/ci_config_template.yml" || echo "Error creating file ci_config_template.yml"

# Documentation
mv "$DEV_STRUCTURE_DIR/docs/architecture/architecture_docs_description" "$DEV_STRUCTURE_DIR/docs/architecture/This-folder-contains-architectural-documentation-for-the-TxT2PDF-project" || echo "Error renaming file architecture_docs_description"
touch "$DEV_STRUCTURE_DIR/docs/architecture/system_architecture.md" || echo "Error creating file system_architecture.md"
mv "$DEV_STRUCTURE_DIR/docs/design/design_docs_description" "$DEV_STRUCTURE_DIR/docs/design/This-folder-contains-design-decisions-and-rationale-behind-the-system" || echo "Error renaming file design_docs_description"
touch "$DEV_STRUCTURE_DIR/docs/design/architecture_design.md" || echo "Error creating file architecture_design.md"
mv "$DEV_STRUCTURE_DIR/docs/decisions/decision_docs_description" "$DEV_STRUCTURE_DIR/docs/decisions/This-folder-contains-project-decision-making-documents" || echo "Error renaming file decision_docs_description"
touch "$DEV_STRUCTURE_DIR/docs/decisions/project_decisions.md" || echo "Error creating file project_decisions.md"

# Runtime Directories
mv "$DEV_STRUCTURE_DIR/input_txt/input_files_description" "$DEV_STRUCTURE_DIR/input_txt/This-folder-contains-input-text-files-for-conversion-into-PDF" || echo "Error renaming file input_files_description"
touch "$DEV_STRUCTURE_DIR/input_txt/sample_input_file.txt" || echo "Error creating file sample_input_file.txt"
mv "$DEV_STRUCTURE_DIR/output_pdf/output_files_description" "$DEV_STRUCTURE_DIR/output_pdf/This-folder-contains-output-PDF-files-generated-from-text-files" || echo "Error renaming file output_files_description"
touch "$DEV_STRUCTURE_DIR/output_pdf/converted_output.pdf" || echo "Error creating file converted_output.pdf"

# -------------------------
# CI and Workflow files
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
# Documentation files
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
echo "✅ Repository structure for 'dev-structure' branch created and updated successfully."
echo
echo "Next recommended steps:"
echo "1. Start adding implementation files to the 'src' folder."
echo "2. Fill the test files with real logic."
echo "3. Commit the changes as: 'chore: bootstrap and update dev-structure branch'"
