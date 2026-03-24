#!/usr/bin/env bash
# verify.sh — Run the test suite and verify everything passes

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================"
echo "Code Eval Workbench — Test Suite"
echo "========================================"
echo ""

# Run pytest with verbose output and fail-fast on first error
uv run pytest tests/ -v --tb=short

echo ""
echo "========================================"
echo "All tests passed!"
echo "========================================"
