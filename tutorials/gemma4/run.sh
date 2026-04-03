#!/usr/bin/env bash
# =============================================================================
#  run.sh  —  Gemma 4 CLI  ·  Launch script
#  Usage:
#    ./run.sh [OPTIONS]
#
#  Core options (map 1-to-1 to gemma4_cli.py flags):
#    --model   <key>        Model size: e2b|e4b|26b|31b      (default: .env / e4b)
#    --system  <prompt>     System prompt override
#    --tools                Enable function calling from startup
#    --ctx     <tokens>     Context window: 32768|65536|131072|262144
#    --temp    <float>      Temperature: 0.0–2.0              (default: 0.7)
#
#  Preset shortcuts:
#    --code-mode            SDE3 code-generation system prompt + temp 0.2
#    --agent                --tools + --model 26b  (MoE agent preset)
#    --max                  --model 31b + --ctx 262144  (max quality preset)
#    --edge                 --model e2b  (minimum footprint preset)
#    --multilingual <lang>  Set system prompt to "Reply only in <lang>"
#
#  Ollama lifecycle:
#    --no-start-ollama      Don't auto-start Ollama; error if not running
#    --stop-ollama          Kill Ollama server when CLI exits (if we started it)
#    --ollama-url  <url>    Override Ollama base URL
#    --ollama-home <dir>    Ollama models directory
#    --wait-ollama <secs>   Seconds to wait for Ollama to start  (default: 30)
#    --pull-first  [model]  Pull / refresh model before starting
#
#  Session options:
#    --load    <file>       Load a saved conversation (JSON) on startup
#    --log                  Enable session log to logs/session_<timestamp>.log
#    --sessions-dir <dir>   Override sessions directory
#
#  Process / environment:
#    --venv    <dir>        Virtualenv directory             (default: .venv)
#    --env-file <file>      Env file to source              (default: .env)
#    --no-env               Don't source .env file
#    --gpu-layers <n>       OLLAMA_NUM_GPU (0=CPU-only)
#    --dry-run              Print command without running
#    --help  -h             Show this message
#
#  ENV overrides (read from .env or shell environment):
#    GEMMA4_DEFAULT_MODEL   GEMMA4_TEMPERATURE   GEMMA4_CTX_SIZE
#    GEMMA4_TOOLS_ENABLED   GEMMA4_SYSTEM_PROMPT OLLAMA_HOST
#    GEMMA4_SESSIONS_DIR    GEMMA4_LOG_DIR       GEMMA4_VENV_DIR
# =============================================================================

set -euo pipefail

# ─── Colours ──────────────────────────────────────────────────────────────────
_R='\033[0;31m'  _G='\033[0;32m'  _Y='\033[0;33m'
_B='\033[0;34m'  _C='\033[0;36m'  _W='\033[1;37m'  _D='\033[2m'
_BOLD='\033[1m'  _RESET='\033[0m'

log_info() { echo -e "  ${_B}▸${_RESET} $*"; }
log_ok()   { echo -e "  ${_G}✓${_RESET} $*"; }
log_warn() { echo -e "  ${_Y}⚠${_RESET}  $*"; }
log_err()  { echo -e "  ${_R}✗${_RESET}  $*" >&2; }
die()      { log_err "$*"; exit 1; }

# ─── Defaults (overridden by .env then by flags) ──────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Will be filled from .env then args
MODEL=""
SYSTEM_PROMPT=""
TOOLS=false
CTX_SIZE=""
TEMPERATURE=""
CODE_MODE=false
AGENT_MODE=false
MAX_MODE=false
EDGE_MODE=false
MULTILANG=""

# Ollama lifecycle
NO_START_OLLAMA=false
STOP_OLLAMA_ON_EXIT=false
OLLAMA_URL=""
OLLAMA_HOME=""
WAIT_OLLAMA=30
PULL_FIRST=false
PULL_MODEL_TAG=""

# Session / paths
LOAD_FILE=""
ENABLE_LOG=false
SESSIONS_DIR=""
VENV_DIR="${SCRIPT_DIR}/.venv"
ENV_FILE="${SCRIPT_DIR}/.env"
NO_ENV=false
GPU_LAYERS=""
DRY_RUN=false

# Internal
OLLAMA_PID=""
OLLAMA_STARTED=false
SESSION_LOG=""

# ─── Usage ────────────────────────────────────────────────────────────────────
usage() {
  sed -n '3,44p' "${BASH_SOURCE[0]}" | sed 's/^#  \{0,2\}//'
}

# ─── Source .env ──────────────────────────────────────────────────────────────
load_env() {
  if [[ "$NO_ENV" == true ]]; then return; fi
  if [[ ! -f "$ENV_FILE" ]]; then
    log_warn ".env not found at $ENV_FILE — using defaults. Run ./setup.sh first."
    return
  fi
  # shellcheck disable=SC1090
  set -a; source "$ENV_FILE"; set +a
}

# ─── Apply env variables to local vars (env → local, flags override later) ───
apply_env_vars() {
  [[ -z "$MODEL"        ]] && MODEL="${GEMMA4_DEFAULT_MODEL:-e4b}"
  [[ -z "$TEMPERATURE"  ]] && TEMPERATURE="${GEMMA4_TEMPERATURE:-0.7}"
  [[ -z "$CTX_SIZE"     ]] && CTX_SIZE="${GEMMA4_CTX_SIZE:-32768}"
  [[ -z "$OLLAMA_URL"   ]] && OLLAMA_URL="${OLLAMA_HOST:-http://localhost:11434}"
  [[ -z "$OLLAMA_HOME"  ]] && OLLAMA_HOME="${OLLAMA_MODELS:-${HOME}/.ollama}"
  [[ -z "$SESSIONS_DIR" ]] && SESSIONS_DIR="${GEMMA4_SESSIONS_DIR:-${SCRIPT_DIR}/sessions}"
  LOG_DIR="${GEMMA4_LOG_DIR:-${SCRIPT_DIR}/logs}"
  [[ -z "$VENV_DIR"     ]] && VENV_DIR="${GEMMA4_VENV_DIR:-${SCRIPT_DIR}/.venv}"

  # Boolean env flags
  if [[ "${GEMMA4_TOOLS_ENABLED:-false}" == "true" ]]; then TOOLS=true; fi
  if [[ -n "${GEMMA4_SYSTEM_PROMPT:-}" && -z "$SYSTEM_PROMPT" ]]; then
    SYSTEM_PROMPT="$GEMMA4_SYSTEM_PROMPT"
  fi
}

# ─── Parse CLI arguments (override env) ───────────────────────────────────────
parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      # Core model flags
      --model)          MODEL="$2"; shift 2 ;;
      --system)         SYSTEM_PROMPT="$2"; shift 2 ;;
      --tools)          TOOLS=true; shift ;;
      --ctx)            CTX_SIZE="$2"; shift 2 ;;
      --temp)           TEMPERATURE="$2"; shift 2 ;;

      # Presets
      --code-mode)      CODE_MODE=true; shift ;;
      --agent)          AGENT_MODE=true; shift ;;
      --max)            MAX_MODE=true; shift ;;
      --edge)           EDGE_MODE=true; shift ;;
      --multilingual)   MULTILANG="$2"; shift 2 ;;

      # Ollama lifecycle
      --no-start-ollama) NO_START_OLLAMA=true; shift ;;
      --stop-ollama)    STOP_OLLAMA_ON_EXIT=true; shift ;;
      --ollama-url)     OLLAMA_URL="$2"; shift 2 ;;
      --ollama-home)    OLLAMA_HOME="$2"; shift 2 ;;
      --wait-ollama)    WAIT_OLLAMA="$2"; shift 2 ;;
      --pull-first)
        PULL_FIRST=true
        if [[ $# -gt 1 && ! "$2" =~ ^-- ]]; then PULL_MODEL_TAG="$2"; shift; fi
        shift ;;

      # Session
      --load)           LOAD_FILE="$2"; shift 2 ;;
      --log)            ENABLE_LOG=true; shift ;;
      --sessions-dir)   SESSIONS_DIR="$2"; shift 2 ;;

      # Process
      --venv)           VENV_DIR="$2"; shift 2 ;;
      --env-file)       ENV_FILE="$2"; shift 2 ;;
      --no-env)         NO_ENV=true; shift ;;
      --gpu-layers)     GPU_LAYERS="$2"; shift 2 ;;
      --dry-run)        DRY_RUN=true; shift ;;
      -h|--help)        usage; exit 0 ;;
      *)                die "Unknown option: $1  (use --help)" ;;
    esac
  done
}

# ─── Apply presets (expand shortcuts into concrete flags) ─────────────────────
apply_presets() {
  if [[ "$CODE_MODE" == true ]]; then
    SYSTEM_PROMPT="You are an expert SDE3 at Google. Write clean, production-ready, well-documented Python code. Use type hints, pydantic, FastAPI where appropriate. Include tests. Follow PEP8 + Google style guide."
    TEMPERATURE="0.2"
    log_info "Preset: --code-mode  (temp=0.2, SDE3 system prompt)"
  fi

  if [[ "$AGENT_MODE" == true ]]; then
    MODEL="26b"
    TOOLS=true
    log_info "Preset: --agent  (model=26b + tools)"
  fi

  if [[ "$MAX_MODE" == true ]]; then
    MODEL="31b"
    CTX_SIZE="262144"
    log_info "Preset: --max  (model=31b + ctx=262144)"
  fi

  if [[ "$EDGE_MODE" == true ]]; then
    MODEL="e2b"
    [[ -z "$CTX_SIZE" || "$CTX_SIZE" -gt 131072 ]] && CTX_SIZE="131072"
    log_info "Preset: --edge  (model=e2b)"
  fi

  if [[ -n "$MULTILANG" ]]; then
    SYSTEM_PROMPT="You are a helpful assistant. Reply only in ${MULTILANG}. When the user writes in any language, always respond in ${MULTILANG}."
    log_info "Preset: --multilingual ${MULTILANG}"
  fi
}

# ─── Validate inputs ──────────────────────────────────────────────────────────
validate() {
  # Model key
  local valid_models="e2b e4b 26b 31b"
  if [[ ! " $valid_models " =~ " $MODEL " ]]; then
    die "Invalid model '$MODEL'. Choose: $valid_models"
  fi

  # Temperature range
  local temp_ok
  temp_ok="$(python3 -c "print('ok' if 0.0 <= float('${TEMPERATURE}') <= 2.0 else 'fail')" 2>/dev/null || echo fail)"
  [[ "$temp_ok" == "ok" ]] || die "--temp must be between 0.0 and 2.0 (got: $TEMPERATURE)"

  # Context size sanity
  if ! [[ "$CTX_SIZE" =~ ^[0-9]+$ ]]; then
    die "--ctx must be an integer (got: $CTX_SIZE)"
  fi
  if [[ "$CTX_SIZE" -gt 262144 ]]; then
    log_warn "ctx=$CTX_SIZE exceeds Gemma 4 max (262144). Model may cap it."
  fi
  if [[ "$CTX_SIZE" -gt 131072 && ( "$MODEL" == "e2b" || "$MODEL" == "e4b" ) ]]; then
    log_warn "Model $MODEL max context is 128K (131072). Got ctx=$CTX_SIZE — capping to 131072."
    CTX_SIZE="131072"
  fi

  # Load file
  if [[ -n "$LOAD_FILE" && ! -f "$LOAD_FILE" ]]; then
    die "--load: file not found: $LOAD_FILE"
  fi
}

# ─── Virtualenv check ─────────────────────────────────────────────────────────
find_python() {
  if [[ -f "${VENV_DIR}/bin/python" ]]; then
    PYTHON="${VENV_DIR}/bin/python"
    log_ok "Virtualenv: $VENV_DIR"
  elif command -v python3 &>/dev/null; then
    PYTHON="python3"
    log_warn "Virtualenv not found at $VENV_DIR. Using system Python."
    log_warn "Run ./setup.sh to create a proper environment."
  else
    die "No Python found. Run ./setup.sh first."
  fi
}

# ─── Ollama health check & auto-start ─────────────────────────────────────────
ollama_ping() {
  curl -sf "${OLLAMA_URL}/" > /dev/null 2>&1
}

ensure_ollama() {
  if [[ "$NO_START_OLLAMA" == true ]]; then
    if ! ollama_ping; then
      die "Ollama is not running at $OLLAMA_URL and --no-start-ollama is set."
    fi
    log_ok "Ollama running at $OLLAMA_URL"
    return
  fi

  if ollama_ping; then
    log_ok "Ollama already running at $OLLAMA_URL"
    return
  fi

  if ! command -v ollama &>/dev/null; then
    log_warn "Ollama binary not found. Chat will fail until Ollama is installed."
    log_warn "Run ./setup.sh or: curl -fsSL https://ollama.com/install.sh | sh"
    return
  fi

  log_info "Starting Ollama server …"

  mkdir -p "$LOG_DIR"
  local ts; ts="$(date +%Y%m%d_%H%M%S)"
  local logfile="${LOG_DIR}/ollama_${ts}.log"

  # Set GPU layers if specified
  if [[ -n "$GPU_LAYERS" ]]; then
    export OLLAMA_NUM_GPU="$GPU_LAYERS"
    log_info "OLLAMA_NUM_GPU=$GPU_LAYERS"
  fi

  export OLLAMA_HOST="$OLLAMA_URL"
  export OLLAMA_MODELS="$OLLAMA_HOME"
  log_info "OLLAMA_MODELS=$OLLAMA_HOME"

  if [[ "$DRY_RUN" == true ]]; then
    log_info "[dry-run] Would start: ollama serve  > $logfile 2>&1 &"
    return
  fi

  nohup ollama serve > "$logfile" 2>&1 &
  OLLAMA_PID=$!
  OLLAMA_STARTED=true
  log_info "Ollama PID $OLLAMA_PID  (log: $logfile)"

  # Wait up to WAIT_OLLAMA seconds
  local waited=0
  while [[ $waited -lt $WAIT_OLLAMA ]]; do
    sleep 1; (( waited++ ))
    if ollama_ping; then
      log_ok "Ollama server ready  (${waited}s)"
      return
    fi
    printf "  ${_D}Waiting for Ollama … ${waited}s${_RESET}\r"
  done

  die "Ollama did not start in ${WAIT_OLLAMA}s. Check $logfile"
}

stop_ollama() {
  if [[ "$STOP_OLLAMA_ON_EXIT" == true && -n "$OLLAMA_PID" && "$OLLAMA_STARTED" == true ]]; then
    log_info "Stopping Ollama (PID $OLLAMA_PID) …"
    kill "$OLLAMA_PID" 2>/dev/null && log_ok "Ollama stopped." || log_warn "Could not stop Ollama."
  fi
}

# ─── Optional model pull ──────────────────────────────────────────────────────
pull_if_requested() {
  if [[ "$PULL_FIRST" == false ]]; then return; fi
  if [[ "$DRY_RUN"   == true   ]]; then
    log_info "[dry-run] Would: ollama pull ${PULL_MODEL_TAG:-gemma4:${MODEL}}"
    return
  fi

  local tag="${PULL_MODEL_TAG:-gemma4:${MODEL}}"
  log_info "Pulling $tag …"
  ollama pull "$tag" && log_ok "Pulled: $tag" || log_warn "Pull failed for $tag"
}

# ─── Session log setup ────────────────────────────────────────────────────────
setup_log() {
  if [[ "$ENABLE_LOG" == false || "$DRY_RUN" == true ]]; then return; fi
  mkdir -p "$LOG_DIR"
  local ts; ts="$(date +%Y%m%d_%H%M%S)"
  SESSION_LOG="${LOG_DIR}/session_${ts}.log"
  log_info "Session log: $SESSION_LOG"
}

# ─── Build the Python invocation ──────────────────────────────────────────────
build_cmd() {
  CLI_SCRIPT="${SCRIPT_DIR}/gemma4_cli.py"
  [[ ! -f "$CLI_SCRIPT" ]] && die "gemma4_cli.py not found at $CLI_SCRIPT"

  CMD=("$PYTHON" "$CLI_SCRIPT")

  CMD+=(--model      "$MODEL")
  CMD+=(--ctx        "$CTX_SIZE")
  CMD+=(--temp       "$TEMPERATURE")

  [[ "$TOOLS"           == true ]] && CMD+=(--tools)
  [[ -n "$SYSTEM_PROMPT"        ]] && CMD+=(--system "$SYSTEM_PROMPT")
  [[ -n "$OLLAMA_URL"           ]] && CMD+=(--ollama-url "$OLLAMA_URL")

  # --load is handled by the CLI via a /load command, but we can pre-inject it
  # by starting the process and passing the flag if CLI supports it in future;
  # for now we print a reminder
  if [[ -n "$LOAD_FILE" ]]; then
    log_info "Tip: once CLI starts, type:  /load $LOAD_FILE"
  fi
}

# ─── Pre-launch summary ───────────────────────────────────────────────────────
print_launch_info() {
  local tag="gemma4:${MODEL}"
  echo ""
  echo -e "${_BOLD}${_C}  Launching Gemma 4 CLI${_RESET}"
  echo -e "  ${_D}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${_RESET}"
  echo -e "  ${_D}Model${_RESET}        ${_W}$tag${_RESET}"
  echo -e "  ${_D}Context${_RESET}      ${_W}${CTX_SIZE} tokens${_RESET}"
  echo -e "  ${_D}Temperature${_RESET}  ${_W}${TEMPERATURE}${_RESET}"
  echo -e "  ${_D}Tools${_RESET}        ${_W}$(${TOOLS} && echo 'enabled ✅' || echo 'disabled')${_RESET}"
  echo -e "  ${_D}Ollama${_RESET}       ${_W}${OLLAMA_URL}${_RESET}"
  echo -e "  ${_D}Ollama home${_RESET}  ${_W}${OLLAMA_HOME}${_RESET}"
  [[ -n "$SYSTEM_PROMPT" ]] && \
    echo -e "  ${_D}System${_RESET}       ${_W}${SYSTEM_PROMPT:0:60}…${_RESET}"
  [[ -n "$SESSION_LOG"   ]] && \
    echo -e "  ${_D}Log${_RESET}          ${_W}${SESSION_LOG}${_RESET}"
  echo ""
}

# ─── Execute ──────────────────────────────────────────────────────────────────
launch() {
  if [[ "$DRY_RUN" == true ]]; then
    echo ""
    echo -e "${_BOLD}[dry-run]${_RESET} Would execute:"
    echo "  ${CMD[*]}"
    [[ -n "$SESSION_LOG" ]] && echo "  (tee $SESSION_LOG)"
    echo ""
    return
  fi

  # Export OLLAMA_HOST so the Python client picks it up via env
  export OLLAMA_HOST="$OLLAMA_URL"
  export OLLAMA_MODELS="$OLLAMA_HOME"

  # Export sessions dir for any future CLI feature that reads it
  export GEMMA4_SESSIONS_DIR="$SESSIONS_DIR"
  mkdir -p "$SESSIONS_DIR"

  if [[ -n "$SESSION_LOG" ]]; then
    "${CMD[@]}" 2>&1 | tee "$SESSION_LOG"
  else
    "${CMD[@]}"
  fi
}

# ─── Trap: cleanup on exit ────────────────────────────────────────────────────
cleanup() {
  local code=$?
  echo ""                       # clean newline after any partial output
  stop_ollama
  if [[ $code -ne 0 && $code -ne 130 ]]; then
    log_warn "Exited with code $code"
  fi
}
trap cleanup EXIT

# Forward SIGINT/SIGTERM to the Python child so Rich cleans up properly
forward_signal() {
  [[ -n "${CLI_PID:-}" ]] && kill -s "${1}" "$CLI_PID" 2>/dev/null || true
}
trap 'forward_signal INT'  INT
trap 'forward_signal TERM' TERM

# ─── Main ─────────────────────────────────────────────────────────────────────
main() {
  load_env
  apply_env_vars
  parse_args "$@"
  apply_presets
  validate
  find_python
  ensure_ollama
  pull_if_requested
  setup_log
  build_cmd
  print_launch_info
  launch
}

main "$@"
