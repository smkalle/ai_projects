#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════════════
#  setup.sh — MiniMax M2.7 Tutorial Suite — Environment Setup
# ═══════════════════════════════════════════════════════════════════════════════
#
#  Usage:
#    ./setup.sh                        # interactive setup (recommended first run)
#    ./setup.sh --key YOUR_API_KEY     # non-interactive, set key inline
#    ./setup.sh --endpoint cn          # use China endpoint (api.minimaxi.com)
#    ./setup.sh --endpoint global      # use global endpoint (default)
#    ./setup.sh --highspeed            # enable MiniMax-M2.7-highspeed variant
#    ./setup.sh --venv myenv           # custom venv directory name (default: .venv)
#    ./setup.sh --skip-venv            # skip virtual environment creation
#    ./setup.sh --skip-install         # skip pip install (venv already set up)
#    ./setup.sh --force                # overwrite existing .env without prompting
#    ./setup.sh --dry-run              # print actions without executing
#
#  Combinations:
#    ./setup.sh --key sk-xxx --endpoint cn --highspeed
#    ./setup.sh --skip-venv --force
#
# ═══════════════════════════════════════════════════════════════════════════════

set -euo pipefail

# ── Colours ────────────────────────────────────────────────────────────────────
RED='\033[0;31m'; YELLOW='\033[0;33m'; GREEN='\033[0;32m'
CYAN='\033[0;36m'; BOLD='\033[1m'; DIM='\033[2m'; RESET='\033[0m'

log()    { echo -e "${CYAN}[setup]${RESET} $*"; }
ok()     { echo -e "${GREEN}[  ok  ]${RESET} $*"; }
warn()   { echo -e "${YELLOW}[ warn ]${RESET} $*"; }
err()    { echo -e "${RED}[error ]${RESET} $*" >&2; }
header() { echo -e "\n${BOLD}$*${RESET}"; echo -e "${DIM}$(printf '─%.0s' {1..60})${RESET}"; }
dry()    { echo -e "${DIM}[dry-run] $*${RESET}"; }

# ── Defaults ───────────────────────────────────────────────────────────────────
API_KEY=""
ENDPOINT="global"
HIGHSPEED="false"
VENV_DIR=".venv"
SKIP_VENV=false
SKIP_INSTALL=false
FORCE=false
DRY_RUN=false
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ── Arg parsing ────────────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
  case "$1" in
    --key)         API_KEY="$2";    shift 2 ;;
    --endpoint)    ENDPOINT="$2";   shift 2 ;;
    --highspeed)   HIGHSPEED="true";shift ;;
    --venv)        VENV_DIR="$2";   shift 2 ;;
    --skip-venv)   SKIP_VENV=true;  shift ;;
    --skip-install)SKIP_INSTALL=true;shift ;;
    --force)       FORCE=true;      shift ;;
    --dry-run)     DRY_RUN=true;    shift ;;
    --help|-h)
      sed -n '3,30p' "$0" | sed 's/^#//'
      exit 0 ;;
    *)
      err "Unknown flag: $1  (use --help for usage)"
      exit 1 ;;
  esac
done

# ── Validate endpoint ──────────────────────────────────────────────────────────
case "$ENDPOINT" in
  global) BASE_URL="https://api.minimax.io/anthropic" ;;
  cn)     BASE_URL="https://api.minimaxi.com/anthropic" ;;
  *)
    err "Invalid --endpoint '$ENDPOINT'. Use 'global' or 'cn'."
    exit 1 ;;
esac

# ── Banner ─────────────────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}  MiniMax M2.7 Tutorial Suite — Setup${RESET}"
echo -e "${DIM}  $(date '+%Y-%m-%d %H:%M:%S')  ·  $SCRIPT_DIR${RESET}"
echo ""

$DRY_RUN && warn "DRY-RUN mode — no files will be written or commands executed"

# ── 1. Check Python ────────────────────────────────────────────────────────────
header "Step 1 · Python"

PYTHON_CMD=""
for cmd in python3 python; do
  if command -v "$cmd" &>/dev/null; then
    PY_VER=$("$cmd" --version 2>&1 | awk '{print $2}')
    PY_MAJOR=$(echo "$PY_VER" | cut -d. -f1)
    PY_MINOR=$(echo "$PY_VER" | cut -d. -f2)
    if [[ "$PY_MAJOR" -ge 3 && "$PY_MINOR" -ge 10 ]]; then
      PYTHON_CMD="$cmd"
      ok "Found $cmd $PY_VER"
      break
    else
      warn "$cmd $PY_VER is too old (need 3.10+)"
    fi
  fi
done

if [[ -z "$PYTHON_CMD" ]]; then
  err "Python 3.10+ not found. Install from https://python.org and re-run."
  exit 1
fi

# ── 2. Virtual environment ─────────────────────────────────────────────────────
header "Step 2 · Virtual Environment"
VENV_PATH="$SCRIPT_DIR/$VENV_DIR"
ACTIVATE="$VENV_PATH/bin/activate"

if $SKIP_VENV; then
  warn "--skip-venv: using system Python"
  PYTHON_CMD="$PYTHON_CMD"
else
  if [[ -d "$VENV_PATH" ]]; then
    ok "Venv already exists at $VENV_DIR/"
  else
    log "Creating venv at $VENV_DIR/"
    if ! $DRY_RUN; then
      "$PYTHON_CMD" -m venv "$VENV_PATH"
      ok "Venv created"
    else
      dry "$PYTHON_CMD -m venv $VENV_PATH"
    fi
  fi

  if [[ -f "$ACTIVATE" ]]; then
    if ! $DRY_RUN; then
      # shellcheck disable=SC1090
      source "$ACTIVATE"
      PYTHON_CMD="python"
      ok "Activated $VENV_DIR  (python=$(python --version 2>&1 | awk '{print $2}'))"
    else
      dry "source $ACTIVATE"
    fi
  fi
fi

# ── 3. Install dependencies ────────────────────────────────────────────────────
header "Step 3 · Dependencies"
REQ_FILE="$SCRIPT_DIR/requirements.txt"

if $SKIP_INSTALL; then
  warn "--skip-install: skipping pip install"
else
  if [[ ! -f "$REQ_FILE" ]]; then
    err "requirements.txt not found at $REQ_FILE"
    exit 1
  fi

  log "Installing from requirements.txt…"
  if ! $DRY_RUN; then
    pip install --upgrade pip --quiet
    pip install -r "$REQ_FILE" --quiet
    ok "Dependencies installed"
    echo ""
    pip list | grep -E "anthropic|python-dotenv" | \
      awk '{printf "    %-20s %s\n", $1, $2}'
  else
    dry "pip install -r $REQ_FILE"
  fi
fi

# ── 4. .env file ───────────────────────────────────────────────────────────────
header "Step 4 · Environment File (.env)"
ENV_FILE="$SCRIPT_DIR/.env"

write_env() {
  cat > "$ENV_FILE" <<EOF
# .env — MiniMax M2.7 Tutorial Suite
# Generated by setup.sh on $(date '+%Y-%m-%d %H:%M:%S')

# ── Anthropic-compatible endpoint ─────────────────────────────────────────
ANTHROPIC_BASE_URL=${BASE_URL}

# ── API Key (from https://platform.minimax.io) ────────────────────────────
ANTHROPIC_API_KEY=${API_KEY}

# ── Model variant ─────────────────────────────────────────────────────────
# false = MiniMax-M2.7 (standard)
# true  = MiniMax-M2.7-highspeed (same quality, higher TPS)
MINIMAX_USE_HIGHSPEED=${HIGHSPEED}
EOF
}

if [[ -f "$ENV_FILE" ]] && ! $FORCE; then
  warn ".env already exists. Use --force to overwrite."
  log "Showing current .env (key masked):"
  sed 's/\(ANTHROPIC_API_KEY=\).*/\1***/' "$ENV_FILE" | sed 's/^/    /'
else
  # Interactive key entry if not passed via --key
  if [[ -z "$API_KEY" ]]; then
    echo ""
    echo -e "  ${BOLD}MiniMax API key required.${RESET}"
    echo -e "  ${DIM}Get yours at: https://platform.minimax.io${RESET}"
    echo ""
    read -rsp "  Enter API key (input hidden): " API_KEY
    echo ""
    if [[ -z "$API_KEY" ]]; then
      warn "No key provided. .env will be written with a placeholder."
      API_KEY="YOUR_MINIMAX_API_KEY_HERE"
    fi
  fi

  if ! $DRY_RUN; then
    write_env
    ok ".env written"
  else
    dry "Write .env with BASE_URL=$BASE_URL, HIGHSPEED=$HIGHSPEED"
  fi
fi

# ── 5. Validation ──────────────────────────────────────────────────────────────
header "Step 5 · Validation"

check_import() {
  local pkg="$1"
  if ! $DRY_RUN; then
    if $PYTHON_CMD -c "import $pkg" 2>/dev/null; then
      ok "import $pkg  ✓"
    else
      err "Cannot import '$pkg' — install may have failed"
      return 1
    fi
  else
    dry "python -c 'import $pkg'"
  fi
}

check_import "anthropic"
check_import "dotenv"

if ! $DRY_RUN && [[ -f "$ENV_FILE" ]]; then
  KEY_VAL=$(grep 'ANTHROPIC_API_KEY' "$ENV_FILE" | cut -d= -f2)
  if [[ "$KEY_VAL" == "YOUR_MINIMAX_API_KEY_HERE" || -z "$KEY_VAL" ]]; then
    warn "API key is a placeholder — edit .env before running modules"
  else
    MASKED="${KEY_VAL:0:6}...${KEY_VAL: -4}"
    ok "API key present ($MASKED)"
  fi
fi

# ── Summary ────────────────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}  ═══ Setup Complete ═══${RESET}"
echo ""
printf "  %-22s %s\n" "Endpoint:"   "$BASE_URL"
printf "  %-22s %s\n" "Model:"      "$( [[ $HIGHSPEED == true ]] && echo 'MiniMax-M2.7-highspeed' || echo 'MiniMax-M2.7' )"
printf "  %-22s %s\n" "Venv:"       "$( $SKIP_VENV && echo 'skipped (system python)' || echo "$VENV_DIR/" )"
printf "  %-22s %s\n" ".env:"       "$ENV_FILE"
echo ""
echo -e "  ${DIM}Next step:${RESET}"
if ! $SKIP_VENV; then
  echo -e "  ${CYAN}source ${VENV_DIR}/bin/activate${RESET}"
fi
echo -e "  ${CYAN}./run.sh --list${RESET}"
echo -e "  ${CYAN}./run.sh --module 01${RESET}"
echo ""
