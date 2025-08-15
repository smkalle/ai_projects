#!/usr/bin/env bash
# Prepare and validate local MCP tool servers
# - Ensures the filesystem server package is available via npx
# - Optionally updates configs/mcp_config.json search URL from env
# - Checks reachability of the search server URL

set -euo pipefail

ROOT_DIR=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT_DIR"

# Load env
if [ -f .env ]; then
  echo "Loading .env"
  set -a; # export all
  # shellcheck disable=SC1091
  source .env
  set +a
fi

# Defaults
SEARCH_SERVER_URL=${SEARCH_SERVER_URL:-http://localhost:8765}
FILESERVER_ROOT=${FILESERVER_ROOT:-.}
FILESERVER_ALLOW=${FILESERVER_ALLOW:-read}
MCP_CONFIG_PATH=${MCP_CONFIG_PATH:-configs/mcp_config.json}

echo "Filesystem root: $FILESERVER_ROOT (allow=$FILESERVER_ALLOW)"
echo "Search server URL: $SEARCH_SERVER_URL"
echo "MCP config: $MCP_CONFIG_PATH"

echo "--- Ensuring filesystem server package is available (npx)"
if ! command -v npx >/dev/null 2>&1; then
  echo "npx not found. Please install Node.js (includes npx)." >&2
  exit 1
fi

# Warm-install/check help (does not start a long-running process)
if ! npx -y @modelcontextprotocol/server-filesystem --help >/dev/null 2>&1; then
  echo "Failed to fetch @modelcontextprotocol/server-filesystem via npx." >&2
  exit 1
fi
echo "Filesystem server package is available. (Client will spawn it via stdio.)"

echo "--- Updating search URL in MCP config (if jq is available)"
if command -v jq >/dev/null 2>&1; then
  if [ -f "$MCP_CONFIG_PATH" ]; then
    tmp=$(mktemp)
    jq --arg url "$SEARCH_SERVER_URL" '.mcpServers.search.url = $url' "$MCP_CONFIG_PATH" > "$tmp" && mv "$tmp" "$MCP_CONFIG_PATH"
    echo "Updated search.url in $MCP_CONFIG_PATH"
  else
    echo "Config file $MCP_CONFIG_PATH not found; skipping update." >&2
  fi
else
  echo "jq not found; skipping automatic JSON update. Update $MCP_CONFIG_PATH manually if needed." >&2
fi

echo "--- Checking search server reachability"
code=$(curl -s -o /dev/null -w "%{http_code}" "$SEARCH_SERVER_URL" || true)
echo "Search server HTTP status: $code"
if [ "$code" = "000" ] || [ "$code" = "404" ] || [ "$code" = "500" ]; then
  echo "Note: MCP HTTP servers may not expose a root docs page; non-200 can be expected. Ensure URL is correct." >&2
fi

# Optionally start Tavily server if requested
if [ "${START_SEARCH_SERVER:-false}" = "true" ] || [ "${START_SEARCH_SERVER:-0}" = "1" ]; then
  echo "--- START_SEARCH_SERVER=true; attempting to start local Tavily search server"
  ./scripts/run_search_server.sh start || true
  echo "Search server status after start:" && ./scripts/run_search_server.sh status || true
fi

echo "Done. Start the backend and UI with ./scripts/run_dev.sh"
