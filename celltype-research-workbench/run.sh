#!/usr/bin/env bash
# ============================================================================
# CellType Research Workbench — Run Script
# Uses uv for fast, reliable execution.
#
# Usage:
#   ./run.sh                    # Launch the Streamlit workbench (default)
#   ./run.sh app                # Same as above
#   ./run.sh test               # Run tests
#   ./run.sh lint               # Lint with ruff
#   ./run.sh fmt                # Format with ruff
#   ./run.sh check              # Verify installation & health
#   ./run.sh doctor             # Run ct doctor (requires celltype-cli)
#   ./run.sh help               # Show this help
# ============================================================================

set -euo pipefail

# ---------------------------------------------------------------------------
# Colors & helpers
# ---------------------------------------------------------------------------
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

info()  { echo -e "${BLUE}[INFO]${NC}  $*"; }
ok()    { echo -e "${GREEN}[OK]${NC}    $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
fail()  { echo -e "${RED}[FAIL]${NC}  $*"; exit 1; }

# ---------------------------------------------------------------------------
# Project directory
# ---------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# ---------------------------------------------------------------------------
# Ensure uv is available
# ---------------------------------------------------------------------------
if ! command -v uv &>/dev/null; then
    fail "uv is not installed. Run ./setup.sh first, or install uv: https://docs.astral.sh/uv/"
fi

# ---------------------------------------------------------------------------
# Ensure virtual environment exists
# ---------------------------------------------------------------------------
if [ ! -d ".venv" ]; then
    warn "No .venv found. Running setup first..."
    bash setup.sh
fi

# Activate venv if not already active
if [ -z "${VIRTUAL_ENV:-}" ]; then
    source .venv/bin/activate 2>/dev/null || true
fi

# ---------------------------------------------------------------------------
# Command routing
# ---------------------------------------------------------------------------
COMMAND="${1:-app}"
shift 2>/dev/null || true

case "$COMMAND" in
    # ------------------------------------------------------------------
    # Launch the Streamlit workbench
    # ------------------------------------------------------------------
    app|start|serve|"")
        echo ""
        echo -e "${CYAN}╔══════════════════════════════════════════════════╗${NC}"
        echo -e "${CYAN}║   🧬 CellType Research Workbench                ║${NC}"
        echo -e "${CYAN}║   Launching Streamlit server...                  ║${NC}"
        echo -e "${CYAN}╚══════════════════════════════════════════════════╝${NC}"
        echo ""

        # Check for API key
        if [ -z "${ANTHROPIC_API_KEY:-}" ]; then
            warn "ANTHROPIC_API_KEY not set — running in demo mode."
            echo -e "  Set it: ${CYAN}export ANTHROPIC_API_KEY=\"sk-ant-...\"${NC}"
            echo ""
        fi

        info "Starting workbench at http://localhost:8501"
        uv run streamlit run app.py \
            --server.headless true \
            --server.port 8501 \
            --browser.gatherUsageStats false \
            "$@"
        ;;

    # ------------------------------------------------------------------
    # Run tests
    # ------------------------------------------------------------------
    test|tests)
        info "Running tests..."
        uv run python -m pytest tests/ -v "$@"
        ;;

    # ------------------------------------------------------------------
    # Lint code
    # ------------------------------------------------------------------
    lint)
        info "Linting with ruff..."
        uv run python -m ruff check . "$@"
        ;;

    # ------------------------------------------------------------------
    # Format code
    # ------------------------------------------------------------------
    fmt|format)
        info "Formatting with ruff..."
        uv run python -m ruff format . "$@"
        ok "Formatting complete."
        ;;

    # ------------------------------------------------------------------
    # Verify installation & system health
    # ------------------------------------------------------------------
    check|verify)
        echo ""
        info "Verifying workbench installation..."
        echo ""

        uv run python -c "
import sys

print('=== Python Environment ===')
print(f'Python: {sys.version}')
print(f'Executable: {sys.executable}')
print()

print('=== Core Packages ===')
packages = {
    'streamlit': 'streamlit',
    'plotly': 'plotly',
    'pandas': 'pandas',
    'numpy': 'numpy',
    'anthropic': 'anthropic',
    'Bio': 'biopython',
    'requests': 'requests',
    'dotenv': 'python-dotenv',
}
all_ok = True
for module, name in packages.items():
    try:
        mod = __import__(module)
        ver = getattr(mod, '__version__', 'ok')
        print(f'  ✓ {name:20s} {ver}')
    except ImportError:
        print(f'  ✗ {name:20s} MISSING')
        all_ok = False

print()
print('=== Optional Packages ===')
optional = {
    'streamlit_option_menu': 'streamlit-option-menu',
    'st_aggrid': 'streamlit-aggrid',
    'scipy': 'scipy',
    'sklearn': 'scikit-learn',
    'gseapy': 'gseapy',
}
for module, name in optional.items():
    try:
        mod = __import__(module)
        ver = getattr(mod, '__version__', 'ok')
        print(f'  ✓ {name:20s} {ver}')
    except ImportError:
        print(f'  · {name:20s} not installed (optional)')

print()
print('=== API Configuration ===')
import os
api_key = os.environ.get('ANTHROPIC_API_KEY', '')
if api_key:
    masked = api_key[:10] + '...' + api_key[-4:]
    print(f'  ✓ ANTHROPIC_API_KEY: {masked}')
else:
    print('  ✗ ANTHROPIC_API_KEY: not set')

print()
print('=== celltype-cli ===')
import shutil
ct = shutil.which('ct')
if ct:
    print(f'  ✓ celltype-cli found: {ct}')
else:
    print('  · celltype-cli not installed (optional)')

print()
if all_ok:
    print('✅ All core dependencies verified!')
else:
    print('❌ Some core dependencies are missing. Run: ./setup.sh')
    sys.exit(1)
"
        ;;

    # ------------------------------------------------------------------
    # Run celltype-cli doctor
    # ------------------------------------------------------------------
    doctor)
        info "Running ct doctor..."
        if command -v ct &>/dev/null; then
            ct doctor
        else
            warn "celltype-cli not installed."
            echo -e "  Install: ${CYAN}pip install celltype-cli${NC}"
        fi
        ;;

    # ------------------------------------------------------------------
    # Help
    # ------------------------------------------------------------------
    help|-h|--help)
        echo ""
        echo -e "${CYAN}CellType Research Workbench — Run Script${NC}"
        echo ""
        echo "Usage: ./run.sh [command] [options]"
        echo ""
        echo "Commands:"
        echo "  app, start, serve    Launch the Streamlit workbench (default)"
        echo "  test, tests          Run pytest test suite"
        echo "  lint                 Lint code with ruff"
        echo "  fmt, format          Format code with ruff"
        echo "  check, verify        Verify installation and system health"
        echo "  doctor               Run ct doctor (requires celltype-cli)"
        echo "  help                 Show this help message"
        echo ""
        echo "Examples:"
        echo "  ./run.sh                             # Launch workbench"
        echo "  ./run.sh app --server.port 8080      # Custom port"
        echo "  ./run.sh test -k 'test_config'       # Run specific tests"
        echo "  ./run.sh check                       # Verify setup"
        echo ""
        echo "Environment:"
        echo "  ANTHROPIC_API_KEY    Anthropic API key (required for agent)"
        echo "  NCBI_API_KEY         NCBI API key (optional, for PubMed)"
        echo ""
        ;;

    # ------------------------------------------------------------------
    # Unknown command
    # ------------------------------------------------------------------
    *)
        warn "Unknown command: $COMMAND"
        echo "Run ./run.sh help for usage."
        exit 1
        ;;
esac
