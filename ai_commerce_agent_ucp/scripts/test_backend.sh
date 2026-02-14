#!/usr/bin/env bash
# =============================================================================
# test_backend.sh — Run backend tests for the AI Commerce Agent
#
# Runs pytest against all backend test suites:
#   - Merchant server (UCP endpoints, cart, checkout)
#   - Agent API (session management, web UI)
#   - Agent graph (LangGraph workflow, mocked LLM/RAG)
#   - RAG module (keyword search, vector store fallback)
#   - Pydantic models
#
# Usage:
#   ./scripts/test_backend.sh                  # Run all tests
#   ./scripts/test_backend.sh --verbose        # Verbose output
#   ./scripts/test_backend.sh --coverage       # With coverage report
#   ./scripts/test_backend.sh --fast           # Skip slow tests (if any)
#   ./scripts/test_backend.sh -k "test_cart"   # Run specific tests by pattern
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

# Activate venv if it exists
if [ -f "$PROJECT_DIR/.venv/bin/activate" ]; then
    # shellcheck disable=SC1091
    source "$PROJECT_DIR/.venv/bin/activate"
fi

PYTEST_ARGS=()
VERBOSE=false
COVERAGE=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --verbose|-v)
            VERBOSE=true; shift ;;
        --coverage)
            COVERAGE=true; shift ;;
        --fast)
            PYTEST_ARGS+=("-m" "not slow"); shift ;;
        -h|--help)
            echo "Usage: $0 [--verbose] [--coverage] [--fast] [-k PATTERN] [PYTEST_ARGS...]"
            echo ""
            echo "Options:"
            echo "  --verbose, -v       Verbose test output"
            echo "  --coverage          Generate coverage report (requires pytest-cov)"
            echo "  --fast              Skip tests marked as slow"
            echo "  -k PATTERN          Run tests matching pattern"
            echo "  Any extra args are passed directly to pytest"
            echo ""
            echo "Test suites:"
            echo "  tests/test_merchant_server.py  Merchant UCP endpoints"
            echo "  tests/test_agent_api.py        Agent API endpoints"
            echo "  tests/test_agent_graph.py      LangGraph workflow (mocked)"
            echo "  tests/test_rag.py              RAG / keyword search"
            echo "  tests/test_models.py           Pydantic models"
            exit 0
            ;;
        *)
            PYTEST_ARGS+=("$1"); shift ;;
    esac
done

echo "======================================"
echo "  AI Commerce Agent — Backend Tests"
echo "======================================"
echo ""

# Build pytest command
CMD=(python3 -m pytest tests/)

if $VERBOSE; then
    CMD+=(-v --tb=short)
else
    CMD+=(-v)
fi

if $COVERAGE; then
    CMD+=(--cov=. --cov-report=term-missing --cov-report=html:htmlcov)
    echo "  Coverage report will be written to htmlcov/"
fi

if [ ${#PYTEST_ARGS[@]} -gt 0 ]; then
    CMD+=("${PYTEST_ARGS[@]}")
fi

echo "  Command: ${CMD[*]}"
echo ""

# Run tests
"${CMD[@]}"
EXIT_CODE=$?

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo "All backend tests passed!"
else
    echo "Some tests failed (exit code: $EXIT_CODE)"
fi

exit $EXIT_CODE
