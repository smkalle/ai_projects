#!/usr/bin/env bash
# ============================================================================
# CellType Research Workbench — Setup Script
# Uses uv for fast, reliable Python package management.
#
# Usage:
#   ./setup.sh              # Core + widgets (default)
#   ./setup.sh --core       # Core dependencies only
#   ./setup.sh --science    # Core + scientific computing stack
#   ./setup.sh --dev        # Everything including dev tools
#   ./setup.sh --all        # All optional dependencies
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
# Parse arguments
# ---------------------------------------------------------------------------
INSTALL_MODE="widgets"  # default

while [[ $# -gt 0 ]]; do
    case "$1" in
        --core)     INSTALL_MODE="core";    shift ;;
        --widgets)  INSTALL_MODE="widgets"; shift ;;
        --science)  INSTALL_MODE="science"; shift ;;
        --dev)      INSTALL_MODE="dev";     shift ;;
        --all)      INSTALL_MODE="all";     shift ;;
        -h|--help)
            echo "Usage: ./setup.sh [--core|--widgets|--science|--dev|--all]"
            echo ""
            echo "Install modes:"
            echo "  --core      Core dependencies only (streamlit, plotly, anthropic, etc.)"
            echo "  --widgets   Core + Streamlit widget extensions (default)"
            echo "  --science   Core + scientific computing (scipy, scikit-learn, gseapy)"
            echo "  --dev       Everything + dev tools (pytest, ruff)"
            echo "  --all       All optional dependencies"
            exit 0
            ;;
        *) warn "Unknown option: $1"; shift ;;
    esac
done

# ---------------------------------------------------------------------------
# Project directory
# ---------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo ""
echo -e "${CYAN}╔══════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║   🧬 CellType Research Workbench — Setup        ║${NC}"
echo -e "${CYAN}║   Install mode: ${YELLOW}${INSTALL_MODE}${CYAN}                             ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════╝${NC}"
echo ""

# ---------------------------------------------------------------------------
# Step 1: Ensure uv is installed
# ---------------------------------------------------------------------------
info "Checking for uv..."

if command -v uv &>/dev/null; then
    ok "uv found: $(uv --version)"
else
    info "uv not found. Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh

    # Add to PATH for this session
    export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"

    if command -v uv &>/dev/null; then
        ok "uv installed: $(uv --version)"
    else
        fail "Failed to install uv. Install manually: https://docs.astral.sh/uv/getting-started/installation/"
    fi
fi

# ---------------------------------------------------------------------------
# Step 2: Create virtual environment
# ---------------------------------------------------------------------------
info "Creating virtual environment with Python >=3.10..."

if [ -d ".venv" ]; then
    warn "Existing .venv found — reusing it."
else
    uv venv --python ">=3.10"
    ok "Virtual environment created at .venv/"
fi

# ---------------------------------------------------------------------------
# Step 3: Install dependencies
# ---------------------------------------------------------------------------
info "Installing dependencies (mode: ${INSTALL_MODE})..."

case "$INSTALL_MODE" in
    core)
        uv pip install -e .
        ;;
    widgets)
        uv pip install -e ".[widgets]"
        ;;
    science)
        uv pip install -e ".[widgets,science]"
        ;;
    dev)
        uv pip install -e ".[dev]"
        ;;
    all)
        uv pip install -e ".[all]"
        ;;
esac

ok "Dependencies installed."

# ---------------------------------------------------------------------------
# Step 4: Verify installation
# ---------------------------------------------------------------------------
info "Verifying installation..."

VERIFY_SCRIPT='
import sys
errors = []

checks = [
    ("streamlit", "streamlit"),
    ("plotly", "plotly"),
    ("pandas", "pandas"),
    ("numpy", "numpy"),
    ("anthropic", "anthropic"),
    ("Bio", "biopython"),
    ("requests", "requests"),
    ("dotenv", "python-dotenv"),
]

for module, name in checks:
    try:
        __import__(module)
        print(f"  ✓ {name}")
    except ImportError:
        errors.append(name)
        print(f"  ✗ {name} — MISSING")

if errors:
    print(f"\n{len(errors)} package(s) failed to import: {", ".join(errors)}")
    sys.exit(1)
else:
    print("\nAll core packages verified!")
'

uv run python -c "$VERIFY_SCRIPT" || fail "Verification failed. Check errors above."
ok "All core packages verified."

# ---------------------------------------------------------------------------
# Step 5: Check for Anthropic API key
# ---------------------------------------------------------------------------
if [ -n "${ANTHROPIC_API_KEY:-}" ]; then
    ok "ANTHROPIC_API_KEY is set."
else
    warn "ANTHROPIC_API_KEY is not set."
    echo ""
    echo -e "  Set it with:  ${CYAN}export ANTHROPIC_API_KEY=\"sk-ant-...\"${NC}"
    echo -e "  Get a key at: ${CYAN}https://console.anthropic.com/${NC}"
    echo ""
    echo "  The workbench will run in demo mode without an API key."
fi

# ---------------------------------------------------------------------------
# Step 6: Check for celltype-cli (optional)
# ---------------------------------------------------------------------------
info "Checking for celltype-cli (optional)..."

if uv run python -c "import shutil; print(shutil.which('ct'))" 2>/dev/null | grep -q "/"; then
    ok "celltype-cli found."
else
    info "celltype-cli not installed (optional)."
    echo ""
    echo -e "  Install with:  ${CYAN}pip install celltype-cli${NC}"
    echo -e "  Or full stack: ${CYAN}pip install \"celltype-cli[all]\"${NC}"
    echo ""
    echo "  Without it, the workbench uses the Anthropic API directly."
fi

# ---------------------------------------------------------------------------
# Step 7: Create local directories
# ---------------------------------------------------------------------------
info "Ensuring local directories exist..."
mkdir -p "$HOME/.celltype-workbench/sessions"
mkdir -p "$HOME/.celltype-workbench/reports"
ok "Directories ready."

# ---------------------------------------------------------------------------
# Done
# ---------------------------------------------------------------------------
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   ✅ Setup complete!                             ║${NC}"
echo -e "${GREEN}║                                                  ║${NC}"
echo -e "${GREEN}║   Launch the workbench:                          ║${NC}"
echo -e "${GREEN}║     ./run.sh                                     ║${NC}"
echo -e "${GREEN}║                                                  ║${NC}"
echo -e "${GREEN}║   Or directly:                                   ║${NC}"
echo -e "${GREEN}║     uv run streamlit run app.py                  ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════╝${NC}"
echo ""
