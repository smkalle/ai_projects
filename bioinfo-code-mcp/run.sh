#!/usr/bin/env bash
# run.sh — Run the playground, examples, tests, or MCP server
#
# Usage:
#   ./run.sh playground          # Start interactive web playground
#   ./run.sh examples            # Run all example scripts
#   ./run.sh example <name>      # Run a specific example
#   ./run.sh test                # Run full test suite
#   ./run.sh test --quick        # Run fast tests only (no network)
#   ./run.sh server              # Start the MCP server (stdio)
#   ./run.sh search <query>      # Search available operations
#   ./run.sh --help              # Show this help

set -euo pipefail

# ── Colors ─────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

info()  { echo -e "${BLUE}>>>${NC} $*"; }
ok()    { echo -e "${GREEN}>>>${NC} $*"; }
warn()  { echo -e "${YELLOW}>>>${NC} $*"; }
fail()  { echo -e "${RED}>>>${NC} $*"; exit 1; }

# ── Navigate to project root ──────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# ── Activate venv if available ────────────────────────────────────────
if [ -z "${VIRTUAL_ENV:-}" ] && [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# ── Detect Python ─────────────────────────────────────────────────────
PYTHON="${PYTHON:-python3}"
if ! command -v "$PYTHON" &>/dev/null; then
    PYTHON="python"
fi

# ── Commands ──────────────────────────────────────────────────────────

show_help() {
    echo ""
    echo -e "${BOLD}Bioinformatics Code MCP — Runner${NC}"
    echo ""
    echo "Usage: ./run.sh <command> [options]"
    echo ""
    echo "Commands:"
    echo "  playground              Start the interactive web playground (http://localhost:8765)"
    echo "  examples                Run all example scripts sequentially"
    echo "  example <name>          Run a specific example (agent_demo, sequence_analysis, protein_lookup)"
    echo "  test                    Run the full test suite (144 tests)"
    echo "  test --quick            Run tests without network calls"
    echo "  test --coverage         Run tests with coverage report"
    echo "  server                  Start the MCP server (stdio transport)"
    echo "  search <query>          Search available bioinformatics operations"
    echo "  info                    Show project info and available modules"
    echo "  lint                    Run linter (ruff)"
    echo "  fmt                     Auto-format code (ruff)"
    echo ""
    echo "Environment variables:"
    echo "  NCBI_EMAIL              Email for NCBI API access (required for API calls)"
    echo "  NCBI_API_KEY            NCBI API key (optional, increases rate limit)"
    echo "  EXEC_TIMEOUT            Code execution timeout in seconds (default: 30)"
    echo "  PLAYGROUND_PORT         Playground port (default: 8765)"
    echo ""
    echo "Examples:"
    echo "  ./run.sh playground                           # Start the playground"
    echo "  NCBI_EMAIL=me@uni.edu ./run.sh examples       # Run all examples"
    echo "  ./run.sh example sequence_analysis            # Run one example"
    echo "  ./run.sh search 'protein structure'           # Search operations"
    echo "  ./run.sh test --quick                         # Fast test run"
    echo ""
}

run_playground() {
    local port="${PLAYGROUND_PORT:-8765}"
    info "Starting Bioinformatics Playground on http://localhost:${port}"
    echo ""
    echo -e "  ${CYAN}Open your browser to:${NC} ${BOLD}http://localhost:${port}${NC}"
    echo -e "  Press Ctrl+C to stop"
    echo ""
    $PYTHON playground/app.py
}

run_examples() {
    echo ""
    echo -e "${CYAN}========================================${NC}"
    echo -e "${CYAN}  Running All Examples${NC}"
    echo -e "${CYAN}========================================${NC}"

    local examples=(
        "examples/sequence_analysis.py"
        "examples/agent_demo.py"
        "examples/protein_lookup.py"
    )

    local passed=0
    local failed=0

    for script in "${examples[@]}"; do
        local name
        name="$(basename "$script" .py)"
        echo ""
        echo -e "${BOLD}--- $name ---${NC}"

        if $PYTHON "$script" 2>&1; then
            ok "$name completed"
            ((passed++))
        else
            warn "$name failed (may need NCBI_EMAIL or network access)"
            ((failed++))
        fi
    done

    echo ""
    echo -e "${CYAN}========================================${NC}"
    echo -e "  Results: ${GREEN}$passed passed${NC}, ${RED}$failed failed${NC}"
    echo -e "${CYAN}========================================${NC}"
    echo ""
}

run_example() {
    local name="$1"
    local script=""

    # Find the script
    if [ -f "examples/${name}.py" ]; then
        script="examples/${name}.py"
    elif [ -f "examples/${name}" ]; then
        script="examples/${name}"
    else
        fail "Example not found: $name"
        echo ""
        echo "Available examples:"
        for f in examples/*.py; do
            [ "$(basename "$f")" = "__init__.py" ] && continue
            echo "  $(basename "$f" .py)"
        done
        exit 1
    fi

    info "Running $script"
    echo ""
    $PYTHON "$script"
}

run_tests() {
    local args=("-v" "--tb=short")

    for arg in "$@"; do
        case "$arg" in
            --quick)    args+=("-m" "not network") ;;
            --coverage) args+=("--cov=bioinfo_code_mcp" "--cov-report=term-missing") ;;
            *)          args+=("$arg") ;;
        esac
    done

    info "Running tests..."
    echo ""
    $PYTHON -m pytest tests/ "${args[@]}"
}

run_server() {
    info "Starting MCP server (stdio transport)..."
    echo "  The server communicates via stdin/stdout."
    echo "  Configure your MCP client to connect to: bioinfo-mcp"
    echo ""
    $PYTHON -m bioinfo_code_mcp.server
}

run_search() {
    local query="$*"
    if [ -z "$query" ]; then
        fail "Usage: ./run.sh search <query>"
    fi

    $PYTHON -c "
from bioinfo_code_mcp.registry import Registry
import json

r = Registry()
results = r.search(query='$query', limit=15)

if not results:
    print('No operations found for: $query')
    print('Try: gene, protein, sequence, blast, fasta, variant, structure')
else:
    print(f'Found {len(results)} operation(s) for \"$query\":\n')
    for op in results:
        print(f'  {op[\"name\"]}')
        print(f'    {op[\"description\"]}')
        print(f'    Method: {op[\"method\"]}')
        if op.get('example'):
            print(f'    Example: {op[\"example\"]}')
        print()
"
}

run_info() {
    $PYTHON -c "
from bioinfo_code_mcp.registry import Registry
import bioinfo_code_mcp

r = Registry()
modules = r.list_modules()
tags = r.list_tags()
total = sum(m['operation_count'] for m in modules)

print()
print('Bioinformatics Code MCP v' + bioinfo_code_mcp.__version__)
print('=' * 50)
print()
print(f'Total operations: {total}')
print()
print('Modules:')
for m in modules:
    print(f'  {m[\"module\"]:<20} {m[\"operation_count\"]:>3} operations')
print()
print(f'Tags ({len(tags)}):')
# Print tags in rows of 8
row = []
for t in tags:
    row.append(t)
    if len(row) == 8:
        print('  ' + ', '.join(row))
        row = []
if row:
    print('  ' + ', '.join(row))
print()
"
}

run_lint() {
    info "Running linter..."
    ruff check src/ tests/ playground/
    ok "Lint passed"
}

run_fmt() {
    info "Formatting code..."
    ruff format src/ tests/ playground/
    ok "Formatting complete"
}

# ── Main ──────────────────────────────────────────────────────────────

if [ $# -eq 0 ]; then
    show_help
    exit 0
fi

COMMAND="$1"
shift

case "$COMMAND" in
    playground) run_playground ;;
    examples)   run_examples ;;
    example)
        if [ $# -eq 0 ]; then
            fail "Usage: ./run.sh example <name>"
        fi
        run_example "$1"
        ;;
    test)       run_tests "$@" ;;
    server)     run_server ;;
    search)     run_search "$@" ;;
    info)       run_info ;;
    lint)       run_lint ;;
    fmt)        run_fmt ;;
    help|--help|-h)  show_help ;;
    *)
        fail "Unknown command: $COMMAND"
        echo ""
        show_help
        ;;
esac
