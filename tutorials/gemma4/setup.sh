#!/usr/bin/env bash
# =============================================================================
#  setup.sh  —  Gemma 4 CLI  ·  One-time environment bootstrap
#  Usage:
#    chmod +x setup.sh && ./setup.sh [OPTIONS]
#
#  Options:
#    --model  <key>      Default model to pull: e2b|e4b|26b|31b  (default: e4b)
#    --all-models        Pull all four Gemma 4 variants
#    --skip-ollama       Don't install/check Ollama
#    --skip-pull         Don't pull any models
#    --skip-venv         Use system Python (not recommended)
#    --python  <bin>     Python binary to use         (default: auto-detect)
#    --venv    <dir>     Virtualenv directory          (default: .venv)
#    --ollama-url <url>  Ollama base URL               (default: http://localhost:11434)
#    --ollama-home <dir> Ollama models directory      (default: ~/.ollama)
#    --log-dir <dir>     Log directory                 (default: ./logs)
#    --force             Re-run even if already set up
#    --dry-run           Print actions without executing
#    --help  -h          Show this message
#
#  What it does:
#    1.  Detect OS / arch / shell
#    2.  Verify Python >= 3.10
#    3.  Create isolated virtualenv
#    4.  Install / upgrade Python dependencies
#    5.  Install Ollama (macOS/Linux — skipped on Windows, manual step printed)
#    6.  Start Ollama server transiently to verify it works
#    7.  Pull requested Gemma 4 model(s)
#    8.  Write .env config file
#    9.  Create logs/ and sessions/ directories
#   10.  Run self-test (import check + Ollama ping)
#   11.  Print next-step summary
# =============================================================================

set -euo pipefail

# ─── Colour palette ───────────────────────────────────────────────────────────
_R='\033[0;31m'  _G='\033[0;32m'  _Y='\033[0;33m'
_B='\033[0;34m'  _C='\033[0;36m'  _W='\033[1;37m'  _D='\033[2m'
_BOLD='\033[1m'  _RESET='\033[0m'

log_hdr()   { echo -e "\n${_BOLD}${_C}══ $* ${_RESET}"; }
log_info()  { echo -e "  ${_B}▸${_RESET} $*"; }
log_ok()    { echo -e "  ${_G}✓${_RESET} $*"; }
log_warn()  { echo -e "  ${_Y}⚠${_RESET}  $*"; }
log_err()   { echo -e "  ${_R}✗${_RESET}  $*" >&2; }
log_step()  { echo -e "\n${_BOLD}${_B}[ STEP ]${_RESET} $*"; }
log_dry()   { echo -e "  ${_D}[dry-run]${_RESET} $*"; }

die() { log_err "$*"; exit 1; }

banner() {
  echo -e "${_BOLD}${_C}"
  echo "  ╔══════════════════════════════════════════════════════╗"
  echo "  ║         GEMMA 4 CLI  ·  Environment Setup            ║"
  echo "  ║         Apache 2.0  ·  AI Engineers Edition          ║"
  echo "  ╚══════════════════════════════════════════════════════╝${_RESET}"
  echo ""
}

# ─── Defaults ─────────────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEFAULT_MODEL="e4b"
PULL_ALL=false
SKIP_OLLAMA=false
SKIP_PULL=false
SKIP_VENV=false
PYTHON_BIN=""
VENV_DIR="${SCRIPT_DIR}/.venv"
OLLAMA_URL="http://localhost:11434"
OLLAMA_HOME="${HOME}/.ollama"
LOG_DIR="${SCRIPT_DIR}/logs"
SESSIONS_DIR="${SCRIPT_DIR}/sessions"
FORCE=false
DRY_RUN=false
MARKER="${SCRIPT_DIR}/.setup_done"

# Model tag lookup
declare -A MODEL_TAGS=(
  [e2b]="gemma4:e2b"
  [e4b]="gemma4:e4b"
  [26b]="gemma4:26b"
  [31b]="gemma4:31b"
)

declare -A MODEL_VRAM=(
  [e2b]="~3.2 GB"  [e4b]="~5 GB"
  [26b]="~15.6 GB" [31b]="~17.4 GB"
)

MIN_PYTHON_MINOR=10

# ─── Argument parsing ─────────────────────────────────────────────────────────
parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --model)        DEFAULT_MODEL="$2"; shift 2 ;;
      --all-models)   PULL_ALL=true; shift ;;
      --skip-ollama)  SKIP_OLLAMA=true; shift ;;
      --skip-pull)    SKIP_PULL=true; shift ;;
      --skip-venv)    SKIP_VENV=true; shift ;;
      --python)       PYTHON_BIN="$2"; shift 2 ;;
      --venv)         VENV_DIR="$2"; shift 2 ;;
      --ollama-url)   OLLAMA_URL="$2"; shift 2 ;;
      --ollama-home)  OLLAMA_HOME="$2"; shift 2 ;;
      --log-dir)      LOG_DIR="$2"; shift 2 ;;
      --force)        FORCE=true; shift ;;
      --dry-run)      DRY_RUN=true; shift ;;
      -h|--help)      usage; exit 0 ;;
      *)              die "Unknown option: $1" ;;
    esac
  done

  # Validate model key
  if [[ -z "${MODEL_TAGS[$DEFAULT_MODEL]+_}" ]]; then
    die "Invalid --model '$DEFAULT_MODEL'. Choose: ${!MODEL_TAGS[*]}"
  fi
}

usage() {
  sed -n '3,17p' "${BASH_SOURCE[0]}" | sed 's/^#  \{0,2\}//'
}

# ─── Dry-run wrapper ──────────────────────────────────────────────────────────
run() {
  if [[ "$DRY_RUN" == true ]]; then
    log_dry "$*"
  else
    "$@"
  fi
}

# ─── OS / arch detection ──────────────────────────────────────────────────────
detect_platform() {
  log_step "Detecting platform"

  OS_TYPE="$(uname -s)"
  ARCH="$(uname -m)"
  IS_WSL=false
  IS_MACOS=false
  IS_LINUX=false

  case "$OS_TYPE" in
    Darwin) IS_MACOS=true ;;
    Linux)
      IS_LINUX=true
      if grep -qi microsoft /proc/version 2>/dev/null; then IS_WSL=true; fi
      ;;
    MINGW*|MSYS*|CYGWIN*) die "Use WSL2 or Git Bash on Windows. See README." ;;
    *) die "Unsupported OS: $OS_TYPE" ;;
  esac

  log_ok "OS: $OS_TYPE ($ARCH)$(${IS_WSL} && echo ' [WSL]' || true)"

  # Warn about VRAM for larger models
  if [[ "$DEFAULT_MODEL" == "26b" || "$DEFAULT_MODEL" == "31b" ]]; then
    log_warn "Model ${MODEL_TAGS[$DEFAULT_MODEL]} needs ${MODEL_VRAM[$DEFAULT_MODEL]} VRAM."
    log_warn "Ensure you have a compatible GPU or enough unified memory."
  fi
}

# ─── Python detection ─────────────────────────────────────────────────────────
detect_python() {
  log_step "Checking Python"

  if [[ -n "$PYTHON_BIN" ]]; then
    PYTHON="$PYTHON_BIN"
  else
    # Prefer explicit versioned binaries first
    for candidate in python3.13 python3.12 python3.11 python3.10 python3 python; do
      if command -v "$candidate" &>/dev/null; then
        PYTHON="$(command -v "$candidate")"
        break
      fi
    done
  fi

  [[ -z "${PYTHON:-}" ]] && die "Python not found. Install Python 3.10+ from https://python.org"

  PY_VERSION="$("$PYTHON" -c 'import sys; print(sys.version_info.minor)')"
  PY_MAJOR="$(  "$PYTHON" -c 'import sys; print(sys.version_info.major)')"
  PY_FULL="$(   "$PYTHON" --version 2>&1)"

  if [[ "$PY_MAJOR" -lt 3 || ( "$PY_MAJOR" -eq 3 && "$PY_VERSION" -lt "$MIN_PYTHON_MINOR" ) ]]; then
    die "Python 3.$MIN_PYTHON_MINOR+ required. Found: $PY_FULL"
  fi

  log_ok "Python: $PY_FULL  ($(which "$PYTHON"))"
}

# ─── Virtualenv setup ─────────────────────────────────────────────────────────
setup_venv() {
  if [[ "$SKIP_VENV" == true ]]; then
    log_warn "--skip-venv: using system Python. Dependency isolation disabled."
    VENV_PYTHON="$PYTHON"
    VENV_PIP="$PYTHON -m pip"
    return
  fi

  log_step "Setting up virtualenv → $VENV_DIR"

  if [[ -d "$VENV_DIR" && "$FORCE" != true ]]; then
    log_ok "Virtualenv already exists. Reusing. (--force to rebuild)"
  else
    [[ -d "$VENV_DIR" ]] && run rm -rf "$VENV_DIR"
    run "$PYTHON" -m venv "$VENV_DIR" --upgrade-deps
    log_ok "Created: $VENV_DIR"
  fi

  VENV_PYTHON="${VENV_DIR}/bin/python"
  VENV_PIP="${VENV_DIR}/bin/pip"

  # Upgrade packaging toolchain
  log_info "Upgrading pip / wheel / setuptools …"
  run "$VENV_PIP" install --quiet --upgrade pip wheel setuptools
  log_ok "pip: $("$VENV_PIP" --version | awk '{print $2}')"
}

# ─── Python dependencies ──────────────────────────────────────────────────────
install_deps() {
  log_step "Installing Python dependencies"

  REQS="${SCRIPT_DIR}/requirements.txt"
  [[ ! -f "$REQS" ]] && die "requirements.txt not found at $REQS"

  log_info "$(cat "$REQS" | grep -v '^#' | grep -v '^$' | tr '\n' ' ')"
  run "$VENV_PIP" install --quiet -r "$REQS"

  # Verify critical imports
  log_info "Verifying imports …"
  run "$VENV_PYTHON" -c "
import rich, requests
print(f'  rich={rich.__version__}  requests={requests.__version__}')
"
  log_ok "All Python dependencies installed"
}

# ─── Ollama installation ──────────────────────────────────────────────────────
install_ollama() {
  if [[ "$SKIP_OLLAMA" == true ]]; then
    log_warn "--skip-ollama: skipping Ollama install check."
    return
  fi

  log_step "Checking Ollama"

  if command -v ollama &>/dev/null; then
    OLLAMA_VERSION="$(ollama --version 2>&1 | head -1)"
    log_ok "Ollama already installed: $OLLAMA_VERSION"
    return
  fi

  log_info "Ollama not found. Installing …"

  if [[ "$IS_MACOS" == true ]]; then
    if command -v brew &>/dev/null; then
      log_info "Using Homebrew …"
      run brew install ollama
    else
      log_warn "Homebrew not found. Downloading Ollama installer …"
      run curl -fsSL https://ollama.com/install.sh | run sh
    fi
  elif [[ "$IS_LINUX" == true ]]; then
    run curl -fsSL https://ollama.com/install.sh | run sh
  fi

  if ! command -v ollama &>/dev/null; then
    log_warn "Ollama binary not in PATH after install."
    log_warn "On macOS: add /usr/local/bin to PATH"
    log_warn "Download manually: https://ollama.com/download"
    log_warn "Windows users: install from https://ollama.com/download"
  else
    log_ok "Ollama installed: $(ollama --version 2>&1 | head -1)"
  fi
}

# ─── Ollama server lifecycle ──────────────────────────────────────────────────
ollama_ping() {
  curl -sf "${OLLAMA_URL}/" > /dev/null 2>&1
}

ensure_ollama_running() {
  if [[ "$SKIP_OLLAMA" == true ]]; then return; fi

  log_step "Verifying Ollama server"

  OLLAMA_STARTED_BY_SETUP=false

  if ollama_ping; then
    log_ok "Ollama is running at $OLLAMA_URL"
    return
  fi

  log_info "Ollama not responding. Starting server …"

  if [[ "$DRY_RUN" == true ]]; then
    log_dry "ollama serve  (OLLAMA_MODELS=${OLLAMA_HOME})"
    return
  fi

  mkdir -p "$LOG_DIR"
  export OLLAMA_MODELS="${OLLAMA_HOME}"
  ollama serve > "${LOG_DIR}/ollama_setup.log" 2>&1 &
  OLLAMA_PID=$!
  OLLAMA_STARTED_BY_SETUP=true

  # Wait up to 15 seconds
  for i in {1..15}; do
    sleep 1
    if ollama_ping; then
      log_ok "Ollama server ready (PID $OLLAMA_PID)"
      return
    fi
    printf "  ${_D}waiting for Ollama%${i}d\r${_RESET}" 0
  done

  die "Ollama did not start within 15 s. Check ${LOG_DIR}/ollama_setup.log"
}

stop_setup_ollama() {
  if [[ "${OLLAMA_STARTED_BY_SETUP:-false}" == true && -n "${OLLAMA_PID:-}" ]]; then
    log_info "Stopping Ollama server started by setup (PID $OLLAMA_PID) …"
    kill "$OLLAMA_PID" 2>/dev/null || true
    log_ok "Ollama server stopped."
  fi
}

# ─── Model pull ───────────────────────────────────────────────────────────────
pull_models() {
  if [[ "$SKIP_PULL" == true || "$SKIP_OLLAMA" == true ]]; then
    log_warn "Skipping model pull."
    return
  fi

  log_step "Pulling Gemma 4 model(s)"

  if [[ "$PULL_ALL" == true ]]; then
    MODELS_TO_PULL=("${!MODEL_TAGS[@]}")
  else
    MODELS_TO_PULL=("$DEFAULT_MODEL")
  fi

  for key in "${MODELS_TO_PULL[@]}"; do
    tag="${MODEL_TAGS[$key]}"
    vram="${MODEL_VRAM[$key]}"
    log_info "Pulling $tag  (VRAM: $vram) …"
    if [[ "$DRY_RUN" == true ]]; then
      log_dry "ollama pull $tag"
    else
      ollama pull "$tag" || log_warn "Pull failed for $tag — model may already be cached or unavailable."
    fi
    log_ok "Ready: $tag"
  done
}

# ─── Directories ──────────────────────────────────────────────────────────────
create_dirs() {
  log_step "Creating runtime directories"
  for dir in "$LOG_DIR" "$SESSIONS_DIR"; do
    run mkdir -p "$dir"
    log_ok "$dir"
  done

  # .gitignore for runtime artifacts (only create if not present)
  if [[ "$DRY_RUN" != true && ! -f "${SCRIPT_DIR}/.gitignore" ]]; then
    cat > "${SCRIPT_DIR}/.gitignore" << 'GITIGNORE'
# Gemma 4 CLI — Runtime artifacts
.venv/
logs/
sessions/
*.env
.setup_done

# Python
__pycache__/
*.py[cod]
*.pyo
*.pyd
.Python
*.so
*.egg-info/
dist/
build/

# Environment / IDE
.env.local
.env.*.local
*.log
.idea/
.vscode/
*.swp
*.swo
*~
.DS_Store
Thumbs.db

# Ollama model blobs (large, not versioned)
~/.ollama/

# Claude Code session
.claude/
GITIGNORE
    log_ok ".gitignore written"
  fi
}

# ─── Write .env config ────────────────────────────────────────────────────────
write_env() {
  log_step "Writing .env configuration"

  ENV_FILE="${SCRIPT_DIR}/.env"

  if [[ -f "$ENV_FILE" && "$FORCE" != true ]]; then
    log_ok ".env already exists. Skipping. (--force to overwrite)"
    return
  fi

  if [[ "$DRY_RUN" == true ]]; then
    log_dry "Writing $ENV_FILE"
    return
  fi

  cat > "$ENV_FILE" << ENV
# Gemma 4 CLI — Runtime Configuration
# Generated by setup.sh on $(date -u +"%Y-%m-%dT%H:%M:%SZ")
# Edit this file to change defaults. run.sh reads it automatically.

# ── Model ──────────────────────────────────────────────────────────────────────
GEMMA4_DEFAULT_MODEL="${DEFAULT_MODEL}"         # e2b | e4b | 26b | 31b

# ── Ollama ─────────────────────────────────────────────────────────────────────
OLLAMA_HOST="${OLLAMA_URL}"                     # Override if using remote Ollama
OLLAMA_MODELS="${OLLAMA_HOME}"                  # Model blobs storage directory

# ── Generation defaults ────────────────────────────────────────────────────────
GEMMA4_TEMPERATURE="0.7"                        # 0.0 (deterministic) – 2.0 (creative)
GEMMA4_CTX_SIZE="32768"                         # Context tokens (32K default)
                                                # Use 131072 for 128K (e2b/e4b max)
                                                # Use 262144 for 256K (26b/31b max)

# ── Feature flags ──────────────────────────────────────────────────────────────
GEMMA4_TOOLS_ENABLED="false"                    # "true" to start with function calling on
GEMMA4_SYSTEM_PROMPT=""                         # Override default engineer system prompt

# ── Paths ──────────────────────────────────────────────────────────────────────
GEMMA4_SESSIONS_DIR="${SESSIONS_DIR}"           # Where /save writes JSON files
GEMMA4_LOG_DIR="${LOG_DIR}"                     # Log output directory
GEMMA4_VENV_DIR="${VENV_DIR}"                   # Python virtualenv path
ENV

  chmod 600 "$ENV_FILE"   # protect system prompt / URL from world-read
  log_ok ".env written: $ENV_FILE  (chmod 600)"
}

# ─── Self-test ────────────────────────────────────────────────────────────────
self_test() {
  log_step "Running self-test"

  # 1. Python import test
  log_info "Importing CLI module …"
  if [[ "$DRY_RUN" == true ]]; then
    log_dry "${VENV_PYTHON} -c 'import ast; ast.parse(open(\"gemma4_cli.py\").read())'"
  else
    "$VENV_PYTHON" - << 'PYTEST'
import sys, ast, pathlib
src = pathlib.Path("gemma4_cli.py").read_text()
ast.parse(src)
import importlib.util, types
# Check all external deps are importable
for mod in ("rich", "requests"):
    spec = importlib.util.find_spec(mod)
    assert spec is not None, f"Missing: {mod}"
print("  ✓ gemma4_cli.py syntax OK")
print("  ✓ rich and requests importable")
PYTEST
  fi

  # 2. Ollama ping
  if [[ "$SKIP_OLLAMA" != true ]]; then
    log_info "Pinging Ollama at $OLLAMA_URL …"
    if [[ "$DRY_RUN" == true ]]; then
      log_dry "curl -sf ${OLLAMA_URL}/"
    elif ollama_ping; then
      log_ok "Ollama responding"
    else
      log_warn "Ollama not reachable now — start it before running the CLI"
    fi
  fi

  log_ok "Self-test passed"
}

# ─── Write setup marker ───────────────────────────────────────────────────────
write_marker() {
  if [[ "$DRY_RUN" != true ]]; then
    date -u +"%Y-%m-%dT%H:%M:%SZ" > "$MARKER"
  fi
}

# ─── Summary ─────────────────────────────────────────────────────────────────
print_summary() {
  echo ""
  echo -e "${_BOLD}${_G}  ╔═══════════════════════════════════════════════════════╗${_RESET}"
  echo -e "${_BOLD}${_G}  ║          Setup complete!  Ready to launch.            ║${_RESET}"
  echo -e "${_BOLD}${_G}  ╚═══════════════════════════════════════════════════════╝${_RESET}"
  echo ""
  echo -e "${_BOLD}  Next steps:${_RESET}"
  echo ""
  echo -e "  ${_C}# Start chatting (default model from .env)${_RESET}"
  echo -e "  ${_W}./run.sh${_RESET}"
  echo ""
  echo -e "  ${_C}# Specific model + agent mode${_RESET}"
  echo -e "  ${_W}./run.sh --model 31b --tools${_RESET}"
  echo ""
  echo -e "  ${_C}# 256K context mode (31B/26B only)${_RESET}"
  echo -e "  ${_W}./run.sh --model 31b --ctx 262144${_RESET}"
  echo ""
  echo -e "  ${_C}# Multimodal — attach an image in the chat session${_RESET}"
  echo -e "  ${_W}./run.sh --model e4b${_RESET}"
  echo -e "  ${_D}  (inside chat: /image /path/to/photo.png)${_RESET}"
  echo ""
  echo -e "  ${_C}# Offline code generation mode${_RESET}"
  echo -e "  ${_W}./run.sh --code-mode${_RESET}"
  echo ""
  echo -e "  ${_C}# Multilingual${_RESET}"
  echo -e "  ${_W}./run.sh --system \"Reply only in Kannada\"${_RESET}"
  echo ""
  echo -e "  ${_C}# See all run.sh options${_RESET}"
  echo -e "  ${_W}./run.sh --help${_RESET}"
  echo ""

  if [[ -n "${OLLAMA_STARTED_BY_SETUP:-}" && "$OLLAMA_STARTED_BY_SETUP" == true ]]; then
    echo -e "  ${_Y}Note: The Ollama server started by setup was stopped.${_RESET}"
    echo -e "  ${_Y}Start it before using the CLI: ${_W}ollama serve${_RESET}"
    echo ""
  fi
}

# ─── Early exit if already set up ─────────────────────────────────────────────
check_already_done() {
  if [[ -f "$MARKER" && "$FORCE" != true ]]; then
    echo -e "${_G}Setup already completed on $(cat "$MARKER").${_RESET}"
    echo -e "Run ${_W}./run.sh --help${_RESET} to launch.  Use ${_W}--force${_RESET} to re-run setup."
    exit 0
  fi
}

# ─── Trap cleanup ─────────────────────────────────────────────────────────────
cleanup() {
  local exit_code=$?
  stop_setup_ollama
  if [[ $exit_code -ne 0 ]]; then
    log_err "Setup failed (exit $exit_code). Check output above."
  fi
  exit $exit_code
}
trap cleanup EXIT

# ─── Main ─────────────────────────────────────────────────────────────────────
main() {
  banner
  parse_args "$@"
  check_already_done
  detect_platform
  detect_python
  setup_venv
  install_deps
  install_ollama
  ensure_ollama_running
  pull_models
  create_dirs
  write_env
  self_test
  write_marker
  print_summary
}

main "$@"
