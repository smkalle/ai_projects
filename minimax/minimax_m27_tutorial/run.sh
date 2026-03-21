#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════════════
#  run.sh — MiniMax M2.7 Tutorial Suite — Module Runner
# ═══════════════════════════════════════════════════════════════════════════════
#
#  Usage:
#    ./run.sh                          # interactive module picker
#    ./run.sh --loop                   # interactive picker, re-runs after each module
#    ./run.sh --list                   # list all modules and exit
#    ./run.sh --module 01              # run a specific module (01–08)
#    ./run.sh --module 04              # tool use demo
#    ./run.sh --all                    # run all 8 modules in sequence
#    ./run.sh --all --from 03          # run modules 03 through 08
#    ./run.sh --all --to 05            # run modules 01 through 05
#    ./run.sh --all --from 03 --to 06  # run modules 03 through 06
#
#  Model / endpoint overrides (override .env values):
#    ./run.sh --module 02 --highspeed         # force MiniMax-M2.7-highspeed
#    ./run.sh --module 02 --model standard    # force MiniMax-M2.7 (standard)
#    ./run.sh --module 01 --endpoint cn       # force China endpoint
#    ./run.sh --module 01 --endpoint global   # force global endpoint
#
#  Output:
#    ./run.sh --module 04 --log           # tee output to logs/module-04-<ts>.log
#    ./run.sh --all --log                 # log all modules to logs/run-all-<ts>.log
#    ./run.sh --module 03 --quiet         # suppress dividers, show only content
#
#  Environment:
#    ./run.sh --env .env.staging          # use a different .env file
#    ./run.sh --venv myenv                # activate a specific venv before running
#
#  Diagnostics:
#    ./run.sh --check                     # verify .env, venv, imports; do not run
#    ./run.sh --dry-run --module 04       # print what would run without running
#
# ═══════════════════════════════════════════════════════════════════════════════

set -euo pipefail

# ── Colours ────────────────────────────────────────────────────────────────────
RED='\033[0;31m'; YELLOW='\033[0;33m'; GREEN='\033[0;32m'
CYAN='\033[0;36m'; BOLD='\033[1m'; DIM='\033[2m'; RESET='\033[0m'

log()    { echo -e "${CYAN}[ run  ]${RESET} $*"; }
ok()     { echo -e "${GREEN}[  ok  ]${RESET} $*"; }
warn()   { echo -e "${YELLOW}[ warn ]${RESET} $*"; }
err()    { echo -e "${RED}[error ]${RESET} $*" >&2; }
header() { echo -e "\n${BOLD}$*${RESET}"; echo -e "${DIM}$(printf '─%.0s' {1..60})${RESET}"; }
dry()    { echo -e "${DIM}[dry-run] $*${RESET}"; }

# ── Defaults ───────────────────────────────────────────────────────────────────
MODULE=""
RUN_ALL=false
RUN_LOOP=false
FROM_MOD="01"
TO_MOD="08"
HIGHSPEED_OVERRIDE=""   # empty = use .env value
ENDPOINT_OVERRIDE=""    # empty = use .env value
DO_LOG=false
QUIET=false
ENV_FILE=".env"
VENV_DIR=""
DO_CHECK=false
DRY_RUN=false
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ── Module registry (must match config.py) ─────────────────────────────────────
declare -A MOD_NAMES=(
  [01]="Hello World"
  [02]="Streaming"
  [03]="Multi-Turn Chat"
  [04]="Tool Use"
  [05]="Extended Thinking"
  [06]="System Prompting"
  [07]="Cost Tracking"
  [08]="Agent ReAct Loop"
)
declare -A MOD_TAGS=(
  [01]="basic"       [02]="streaming"  [03]="conversation" [04]="agentic"
  [05]="reasoning"   [06]="prompting"  [07]="production"   [08]="agentic"
)
ALL_MODS=(01 02 03 04 05 06 07 08)

# ── Arg parsing ────────────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
  case "$1" in
    --module|-m)    MODULE=$(printf "%02d" "$2"); shift 2 ;;
    --all|-a)       RUN_ALL=true; shift ;;
    --loop)         RUN_LOOP=true; shift ;;
    --from)         FROM_MOD=$(printf "%02d" "$2"); shift 2 ;;
    --to)           TO_MOD=$(printf "%02d" "$2"); shift 2 ;;
    --highspeed)    HIGHSPEED_OVERRIDE="true"; shift ;;
    --model)
      case "$2" in
        standard|std)  HIGHSPEED_OVERRIDE="false" ;;
        highspeed|hs)  HIGHSPEED_OVERRIDE="true"  ;;
        *)  err "Unknown --model '$2'. Use 'standard' or 'highspeed'."; exit 1 ;;
      esac
      shift 2 ;;
    --endpoint)
      case "$2" in
        global)  ENDPOINT_OVERRIDE="https://api.minimax.io/anthropic" ;;
        cn)      ENDPOINT_OVERRIDE="https://api.minimaxi.com/anthropic" ;;
        *)       err "Unknown --endpoint '$2'. Use 'global' or 'cn'."; exit 1 ;;
      esac
      shift 2 ;;
    --log)          DO_LOG=true; shift ;;
    --quiet|-q)     QUIET=true; shift ;;
    --env)          ENV_FILE="$2"; shift 2 ;;
    --venv)         VENV_DIR="$2"; shift 2 ;;
    --check)        DO_CHECK=true; shift ;;
    --dry-run)      DRY_RUN=true; shift ;;
    --list|-l)
      echo ""
      echo -e "${BOLD}  MiniMax M2.7 Tutorial Suite — Modules${RESET}"
      echo ""
      TAG_COLOURS=(
        "basic:\033[36m" "streaming:\033[33m" "conversation:\033[34m"
        "agentic:\033[35m" "reasoning:\033[90m" "prompting:\033[32m"
        "production:\033[31m"
      )
      for mod in "${ALL_MODS[@]}"; do
        tag="${MOD_TAGS[$mod]}"
        echo -e "  ${BOLD}${mod}${RESET}  ${MOD_NAMES[$mod]:-?}  ${DIM}[${tag}]${RESET}"
      done
      echo ""
      exit 0 ;;
    --help|-h)
      sed -n '3,35p' "$0" | sed 's/^#//'
      exit 0 ;;
    *)
      err "Unknown flag: $1  (use --help for usage)"
      exit 1 ;;
  esac
done

# ── Banner ─────────────────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}  MiniMax M2.7 Tutorial Suite — Runner${RESET}"
echo -e "${DIM}  $(date '+%Y-%m-%d %H:%M:%S')${RESET}"
echo ""

$DRY_RUN && warn "DRY-RUN mode — modules will not execute"

# ── Activate venv if requested ─────────────────────────────────────────────────
if [[ -n "$VENV_DIR" ]]; then
  ACTIVATE="$SCRIPT_DIR/$VENV_DIR/bin/activate"
  if [[ -f "$ACTIVATE" ]]; then
    log "Activating venv: $VENV_DIR"
    # shellcheck disable=SC1090
    source "$ACTIVATE"
    ok "Activated $($PYTHON_CMD --version 2>&1)"
  else
    err "Venv activate script not found: $ACTIVATE"
    exit 1
  fi
elif [[ -f "$SCRIPT_DIR/.venv/bin/activate" ]]; then
  # Auto-detect default venv
  # shellcheck disable=SC1091
  source "$SCRIPT_DIR/.venv/bin/activate" 2>/dev/null || true
fi

# ── Resolve python command (Termux may only have python3) ──────────────────────
PYTHON_CMD=""
for cmd in python python3; do
  if command -v "$cmd" &>/dev/null; then
    PYTHON_CMD="$cmd"
    break
  fi
done
if [[ -z "$PYTHON_CMD" ]]; then
  err "No python or python3 found in PATH."
  err "In Termux: pkg install python"
  exit 1
fi

# ── Resolve env file ───────────────────────────────────────────────────────────
ENV_PATH="$SCRIPT_DIR/$ENV_FILE"
if [[ "$ENV_FILE" == /* ]]; then ENV_PATH="$ENV_FILE"; fi

if [[ ! -f "$ENV_PATH" ]]; then
  err ".env file not found: $ENV_PATH"
  err "Run ./setup.sh first."
  exit 1
fi

# ── Apply overrides into the environment ───────────────────────────────────────
# Load .env first, then apply flag overrides on top
set -a
# shellcheck disable=SC1090
source "$ENV_PATH"
set +a

[[ -n "$HIGHSPEED_OVERRIDE" ]] && export MINIMAX_USE_HIGHSPEED="$HIGHSPEED_OVERRIDE"
[[ -n "$ENDPOINT_OVERRIDE"  ]] && export ANTHROPIC_BASE_URL="$ENDPOINT_OVERRIDE"

# ── --check mode ───────────────────────────────────────────────────────────────
if $DO_CHECK; then
  header "Diagnostics"

  # Python
  PY_VER=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
  ok "Python $PY_VER"

  # Packages
  for pkg in anthropic dotenv; do
    if $PYTHON_CMD -c "import $pkg" 2>/dev/null; then
      VER=$($PYTHON_CMD -c "import importlib.metadata; print(importlib.metadata.version('$pkg' | tr _ -))" 2>/dev/null || echo "?")
      ok "import $pkg  ✓"
    else
      err "Cannot import '$pkg'"
    fi
  done

  # .env values
  KEY="${ANTHROPIC_API_KEY:-}"
  URL="${ANTHROPIC_BASE_URL:-}"
  HS="${MINIMAX_USE_HIGHSPEED:-false}"

  [[ -z "$KEY" ]] && err "ANTHROPIC_API_KEY is not set" || ok "API key   : ${KEY:0:6}...${KEY: -4}"
  [[ -z "$URL" ]] && warn "ANTHROPIC_BASE_URL is not set (will use default)" || ok "Base URL  : $URL"
  ok "Highspeed : $HS"
  ok "Model     : $( [[ $HS == true ]] && echo 'MiniMax-M2.7-highspeed' || echo 'MiniMax-M2.7' )"

  # Module files
  echo ""
  log "Module files:"
  ALL_PRESENT=true
  for mod in "${ALL_MODS[@]}"; do
    f="$SCRIPT_DIR/modules/${mod}_*.py"
    # Use glob expansion
    files=($f)
    if [[ -f "${files[0]:-}" ]]; then
      ok "  ${files[0]##*/}"
    else
      err "  modules/${mod}_*.py — NOT FOUND"
      ALL_PRESENT=false
    fi
  done
  $ALL_PRESENT && ok "All module files present" || warn "Some module files missing"
  echo ""
  exit 0
fi

# ── Print effective config ─────────────────────────────────────────────────────
KEY="${ANTHROPIC_API_KEY:-}"
if [[ -z "$KEY" ]]; then
  err "ANTHROPIC_API_KEY is not set in $ENV_PATH"
  err "Run ./setup.sh to configure."
  exit 1
fi
MASKED_KEY="${KEY:0:6}...${KEY: -4}"
MODEL_NAME="$( [[ "${MINIMAX_USE_HIGHSPEED:-false}" == true ]] \
  && echo 'MiniMax-M2.7-highspeed' || echo 'MiniMax-M2.7' )"

log "API key  : $MASKED_KEY"
log "Endpoint : ${ANTHROPIC_BASE_URL:-https://api.minimax.io/anthropic}"
log "Model    : $MODEL_NAME"

# ── Logging setup ──────────────────────────────────────────────────────────────
LOG_FILE=""
if $DO_LOG; then
  mkdir -p "$SCRIPT_DIR/logs"
  TS=$(date '+%Y%m%d-%H%M%S')
  if [[ -n "$MODULE" ]]; then
    LOG_FILE="$SCRIPT_DIR/logs/module-${MODULE}-${TS}.log"
  else
    LOG_FILE="$SCRIPT_DIR/logs/run-all-${TS}.log"
  fi
  log "Logging to $LOG_FILE"
fi

# ── Run function ───────────────────────────────────────────────────────────────
run_module() {
  local mod="$1"

  # Validate
  if [[ -z "${MOD_NAMES[$mod]:-}" ]]; then
    err "Module '$mod' not found. Use --list to see valid IDs."
    exit 1
  fi

  # Find the module file
  local pattern="$SCRIPT_DIR/modules/${mod}_*.py"
  local files=($pattern)
  local mod_file="${files[0]:-}"

  if [[ ! -f "$mod_file" ]]; then
    err "Module file not found: modules/${mod}_*.py"
    exit 1
  fi

  header "Module ${mod} · ${MOD_NAMES[$mod]}  [${MOD_TAGS[$mod]}]"

  if $DRY_RUN; then
    dry "$PYTHON_CMD $mod_file"
    return
  fi

  local start_ts=$SECONDS

  if $DO_LOG && [[ -n "$LOG_FILE" ]]; then
    $PYTHON_CMD "$mod_file" 2>&1 | tee -a "$LOG_FILE"
  else
    $PYTHON_CMD "$mod_file"
  fi

  local elapsed=$(( SECONDS - start_ts ))
  echo ""
  ok "Module ${mod} finished in ${elapsed}s"
}

# ── Determine run target ───────────────────────────────────────────────────────
cd "$SCRIPT_DIR"

if [[ -n "$MODULE" ]]; then
  # ── Single module ──────────────────────────────────────────────────────────
  if [[ -n "${MOD_NAMES[$MODULE]:-}" ]]; then
    run_module "$MODULE"
  else
    err "Module '$MODULE' not found."
    echo ""
    echo "Valid IDs: ${ALL_MODS[*]}"
    exit 1
  fi

elif $RUN_ALL; then
  # ── Range of modules ───────────────────────────────────────────────────────
  RUN_LIST=()
  for mod in "${ALL_MODS[@]}"; do
    if [[ "$mod" -ge "$FROM_MOD" && "$mod" -le "$TO_MOD" ]]; then
      RUN_LIST+=("$mod")
    fi
  done

  if [[ ${#RUN_LIST[@]} -eq 0 ]]; then
    err "No modules in range ${FROM_MOD}–${TO_MOD}"
    exit 1
  fi

  log "Running ${#RUN_LIST[@]} module(s): ${RUN_LIST[*]}"

  PASS=0; FAIL=0; FAIL_LIST=()

  for mod in "${RUN_LIST[@]}"; do
    if run_module "$mod"; then
      (( PASS++ ))
    else
      (( FAIL++ ))
      FAIL_LIST+=("$mod")
      warn "Module $mod exited with error — continuing"
    fi
    echo ""
  done

  # ── Summary ────────────────────────────────────────────────────────────────
  echo ""
  echo -e "${BOLD}  ═══ Run Summary ═══${RESET}"
  echo ""
  printf "  %-20s %s\n" "Modules run:"    "${#RUN_LIST[@]}"
  printf "  %-20s ${GREEN}%s${RESET}\n" "Passed:"  "$PASS"
  [[ $FAIL -gt 0 ]] && \
    printf "  %-20s ${RED}%s${RESET} (${FAIL_LIST[*]})\n" "Failed:" "$FAIL"
  $DO_LOG && printf "  %-20s %s\n" "Log file:" "$LOG_FILE"
  echo ""

else
  # ── Interactive picker ─────────────────────────────────────────────────────
  while true; do
    echo ""
    echo -e "${BOLD}  Available Modules${RESET}"
    echo ""
    for mod in "${ALL_MODS[@]}"; do
      printf "  ${BOLD}%s${RESET}  %-22s ${DIM}[%s]${RESET}\n" \
        "$mod" "${MOD_NAMES[$mod]}" "${MOD_TAGS[$mod]}"
    done
    echo ""

    read -rp "  Enter module ID (01–08), 'all', or 'q' to quit: " CHOICE
    CHOICE="${CHOICE// /}"
    if [[ "$CHOICE" == "q" || "$CHOICE" == "quit" ]]; then
      echo ""
      ok "Goodbye!"
      break
    elif [[ "$CHOICE" == "all" ]]; then
      RUN_ALL=true
      for mod in "${ALL_MODS[@]}"; do run_module "$mod"; done
      if $RUN_LOOP; then
        echo ""
        warn "Looping — press Ctrl+C to stop or 'q' to quit"
        echo ""
      else
        break
      fi
    elif [[ -n "${MOD_NAMES[$( printf "%02d" "$CHOICE" 2>/dev/null || echo XX )]:-}" ]]; then
      run_module "$(printf "%02d" "$CHOICE")"
      if $RUN_LOOP; then
        echo ""
        warn "Looping — press Ctrl+C to stop or 'q' to quit"
        echo ""
      else
        break
      fi
    else
      warn "Invalid choice '$CHOICE'. Enter a number 1–8, 'all', or 'q'."
    fi
  done
fi

echo -e "${GREEN}${BOLD}  Done.${RESET}"
echo ""
