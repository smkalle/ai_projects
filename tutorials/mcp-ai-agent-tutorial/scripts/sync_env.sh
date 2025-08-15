#!/usr/bin/env bash
# Sync selected environment variables from ~/.bashrc into .env
set -euo pipefail

VARS=(
  API_BASE_URL
  API_PORT
  UI_PORT
  OPENAI_API_KEY
  ANTHROPIC_API_KEY
  FRONTEND_URL
  LANGCHAIN_API_KEY
  LANGSMITH_API_KEY
  ALLOWED_ORIGINS
  MCP_CONFIG_PATH
  TAVILY_API_KEY
  SEARCH_PROVIDER
  SEARCH_PORT
  START_SEARCH_SERVER
  SEARCH_SERVER_URL
)

SRC_BASHRC="$HOME/.bashrc"
DEST_ENV=".env"

if [ ! -f "$SRC_BASHRC" ]; then
  echo "No ~/.bashrc found; nothing to sync." >&2
  exit 0
fi

# Ensure .env exists
if [ ! -f "$DEST_ENV" ]; then
  cp .env.example "$DEST_ENV" 2>/dev/null || touch "$DEST_ENV"
fi

update_env_var() {
  local key="$1" value="$2"
  # Escape slashes for sed
  local esc_value
  esc_value=$(printf '%s' "$value" | sed 's/[\&/]/\\&/g')
  if grep -qE "^${key}=" "$DEST_ENV"; then
    sed -i "s/^${key}=.*/${key}=${esc_value}/" "$DEST_ENV"
  else
    echo "${key}=${value}" >> "$DEST_ENV"
  fi
}

echo "Syncing variables from $SRC_BASHRC to $DEST_ENV"
for key in "${VARS[@]}"; do
  # Look for lines like: export KEY=..., KEY=... or export KEY="..."
  line=$(grep -E "(^|[[:space:]])(export[[:space:]]+)?${key}=" "$SRC_BASHRC" | tail -n 1 || true)
  if [ -n "$line" ]; then
    # Extract after first '=' and strip quotes
    value=${line#*=}
    value=${value%\r}
    value=${value%\n}
    value=$(printf '%s' "$value" | sed 's/^"\(.*\)"$/\1/' | sed "s/^'\(.*\)'$/\1/")
    if [ -n "$value" ]; then
      update_env_var "$key" "$value"
      echo "- $key synced"
    fi
  fi
done

echo "Done. Review $DEST_ENV for accuracy."
