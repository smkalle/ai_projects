#!/usr/bin/env bash
# setup.sh — One-command setup for the Bioinformatics Code MCP project
#
# Usage:
#   ./setup.sh              # Install core + playground + dev dependencies
#   ./setup.sh --core       # Install core only (MCP server, no playground)
#   ./setup.sh --playground # Install core + playground
#   ./setup.sh --dev        # Install everything including test/lint tools
#
# Requirements: Python 3.10+ (uv will be auto-installed if missing)

set -euo pipefail

# ── Colors ─────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

info()  { echo -e "${BLUE}[INFO]${NC}  $*"; }
ok()    { echo -e "${GREEN}[OK]${NC}    $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
fail()  { echo -e "${RED}[ERROR]${NC} $*"; exit 1; }

# ── Navigate to project root ──────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo ""
echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}  Bioinformatics Code MCP — Setup${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

# ── Ensure uv is available ──────────────────────────────────────────
if command -v uv &>/dev/null; then
    ok "Found uv $(uv --version 2>&1 | head -1)"
else
    info "uv not found — installing..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    # Add to PATH for this session
    export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
    if command -v uv &>/dev/null; then
        ok "Installed uv $(uv --version 2>&1 | head -1)"
    else
        fail "Failed to install uv. Install manually: https://docs.astral.sh/uv/getting-started/installation/"
    fi
fi

# ── Parse arguments ───────────────────────────────────────────────────
INSTALL_MODE="dev"  # default: install everything

for arg in "$@"; do
    case "$arg" in
        --core)       INSTALL_MODE="core" ;;
        --playground) INSTALL_MODE="playground" ;;
        --dev)        INSTALL_MODE="dev" ;;
        --help|-h)
            echo "Usage: ./setup.sh [--core|--playground|--dev]"
            echo ""
            echo "  --core        Install core MCP server only"
            echo "  --playground  Install core + interactive playground"
            echo "  --dev         Install everything + test/lint tools (default)"
            exit 0
            ;;
        *) warn "Unknown argument: $arg" ;;
    esac
done

info "Install mode: $INSTALL_MODE"

# ── Create virtual environment with uv ────────────────────────────────
if [ -z "${VIRTUAL_ENV:-}" ]; then
    if [ ! -d ".venv" ]; then
        info "Creating virtual environment with uv..."
        uv venv --python ">=3.10"
        ok "Virtual environment created at .venv/"
    fi
    info "Activating virtual environment..."
    source .venv/bin/activate
    ok "Activated .venv"
else
    ok "Already in virtual environment: $VIRTUAL_ENV"
fi

# ── Install project with uv ─────────────────────────────────────────
case "$INSTALL_MODE" in
    core)
        info "Installing core dependencies..."
        uv pip install -e .
        ;;
    playground)
        info "Installing core + playground dependencies..."
        uv pip install -e ".[playground]"
        ;;
    dev)
        info "Installing all dependencies (core + playground + dev)..."
        uv pip install -e ".[dev]"
        ;;
esac
ok "Dependencies installed"

# ── Verify installation ──────────────────────────────────────────────
info "Verifying installation..."

PYTHON="$(which python)"

$PYTHON -c "import bioinfo_code_mcp; print(f'  bioinfo_code_mcp {bioinfo_code_mcp.__version__}')" || fail "Core package import failed"
$PYTHON -c "import httpx; print(f'  httpx {httpx.__version__}')" || fail "httpx not available"

if [ "$INSTALL_MODE" != "core" ]; then
    $PYTHON -c "import fastapi; print(f'  fastapi {fastapi.__version__}')" || warn "fastapi not available — playground won't work"
    $PYTHON -c "import uvicorn; print(f'  uvicorn {uvicorn.__version__}')" || warn "uvicorn not available — playground won't work"
fi

if [ "$INSTALL_MODE" = "dev" ]; then
    $PYTHON -c "import pytest; print(f'  pytest {pytest.__version__}')" || warn "pytest not available"
fi

ok "All imports verified"

# ── NCBI email configuration ─────────────────────────────────────────
if [ -z "${NCBI_EMAIL:-}" ]; then
    echo ""
    warn "NCBI_EMAIL is not set."
    echo "  NCBI requires an email for API access (usage policy)."
    echo "  Set it with:  export NCBI_EMAIL=\"your-email@institution.edu\""
    echo "  Optional:     export NCBI_API_KEY=\"your-key\"  (increases rate limit)"
    echo ""
fi

# ── Run quick self-test ──────────────────────────────────────────────
info "Running quick self-test..."
uv run python -c "
from bioinfo_code_mcp.registry import Registry
from bioinfo_code_mcp.config import ServerConfig
from bioinfo_code_mcp.sandbox import Sandbox
import asyncio

r = Registry()
modules = r.list_modules()
total = sum(m['operation_count'] for m in modules)
print(f'  Registry: {total} operations across {len(modules)} modules')

config = ServerConfig(execution_timeout_seconds=5)
sb = Sandbox(config)
result = asyncio.run(sb.execute('return seq_utils.gc_content(\"ATGCGC\")'))
assert result.success and abs(result.result - 0.6667) < 0.01
print(f'  Sandbox: execution OK (GC content = {result.result:.4f})')
" || fail "Self-test failed"

ok "Self-test passed"

# ── Done ─────────────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Setup complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "  Next steps:"
echo ""
if [ "$INSTALL_MODE" = "core" ]; then
    echo "    # Start the MCP server"
    echo "    ./run.sh server"
    echo ""
    echo "    # Run examples"
    echo "    ./run.sh examples"
else
    echo "    # Start the interactive playground"
    echo "    ./run.sh playground"
    echo ""
    echo "    # Run examples"
    echo "    ./run.sh examples"
fi
echo ""
echo "    # Run tests"
echo "    ./run.sh test"
echo ""
echo "    # See all commands"
echo "    ./run.sh --help"
echo ""
if [ -z "${NCBI_EMAIL:-}" ]; then
    echo -e "  ${YELLOW}Remember to set NCBI_EMAIL before making API calls!${NC}"
    echo ""
fi
