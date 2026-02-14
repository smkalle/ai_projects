#!/usr/bin/env bash
# =============================================================================
# test_frontend.sh — Run frontend smoke tests for the AI Commerce Agent
#
# Verifies the frontend assets and API endpoints are working correctly.
# Tests can run against a live server or use the FastAPI TestClient.
#
# Usage:
#   ./scripts/test_frontend.sh                 # Offline tests (no server needed)
#   ./scripts/test_frontend.sh --live          # Live tests against running server
#   ./scripts/test_frontend.sh --live --port 9000
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

LIVE=false
PORT=8000
HOST="localhost"
PASSED=0
FAILED=0
TOTAL=0

while [[ $# -gt 0 ]]; do
    case "$1" in
        --live)
            LIVE=true; shift ;;
        --port)
            PORT="$2"; shift 2 ;;
        --host)
            HOST="$2"; shift 2 ;;
        -h|--help)
            echo "Usage: $0 [--live] [--port PORT] [--host HOST]"
            echo ""
            echo "Modes:"
            echo "  (default)   Offline tests using pytest + FastAPI TestClient"
            echo "  --live      Run HTTP tests against a live server"
            echo ""
            echo "Options:"
            echo "  --port PORT   Server port for --live mode (default: 8000)"
            echo "  --host HOST   Server host for --live mode (default: localhost)"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"; exit 1 ;;
    esac
done

cd "$PROJECT_DIR"

# Activate venv if it exists
if [ -f "$PROJECT_DIR/.venv/bin/activate" ]; then
    # shellcheck disable=SC1091
    source "$PROJECT_DIR/.venv/bin/activate"
fi

# --- Test helpers ---
pass_test() {
    TOTAL=$((TOTAL + 1))
    PASSED=$((PASSED + 1))
    echo "  PASS: $1"
}

fail_test() {
    TOTAL=$((TOTAL + 1))
    FAILED=$((FAILED + 1))
    echo "  FAIL: $1"
    if [ -n "${2:-}" ]; then
        echo "        $2"
    fi
}

echo "======================================"
echo "  AI Commerce Agent — Frontend Tests"
echo "======================================"
echo ""

# ==========================================================
# PART 1: Offline tests (always run, no server needed)
# ==========================================================

echo "--- Offline Tests (static analysis) ---"
echo ""

# Test: HTML template exists and has key elements
if [ -f "ui/templates/index.html" ]; then
    pass_test "index.html exists"

    if grep -q "chat-form" "ui/templates/index.html"; then
        pass_test "index.html contains chat form"
    else
        fail_test "index.html missing chat form"
    fi

    if grep -q "product-list" "ui/templates/index.html"; then
        pass_test "index.html contains product list"
    else
        fail_test "index.html missing product list"
    fi

    if grep -q "ucp-modal" "ui/templates/index.html"; then
        pass_test "index.html contains UCP modal"
    else
        fail_test "index.html missing UCP modal"
    fi
else
    fail_test "index.html does not exist"
fi

# Test: CSS file exists and has key styles
if [ -f "ui/static/css/style.css" ]; then
    pass_test "style.css exists"

    if grep -q "chat-messages\|message-content" "ui/static/css/style.css"; then
        pass_test "style.css has chat styles"
    else
        fail_test "style.css missing chat styles"
    fi
else
    fail_test "style.css does not exist"
fi

# Test: JS file exists and has key functions
if [ -f "ui/static/js/app.js" ]; then
    pass_test "app.js exists"

    if grep -q "function escapeHtml" "ui/static/js/app.js"; then
        pass_test "app.js has escapeHtml (XSS protection)"
    else
        fail_test "app.js missing escapeHtml function"
    fi

    if grep -q "function handleChatSubmit" "ui/static/js/app.js"; then
        pass_test "app.js has handleChatSubmit"
    else
        fail_test "app.js missing handleChatSubmit"
    fi

    if grep -q "function formatMessage" "ui/static/js/app.js"; then
        pass_test "app.js has formatMessage"
    else
        fail_test "app.js missing formatMessage"
    fi

    # XSS check: formatMessage should escape HTML before applying markdown
    if grep -q "escapeHtml(text)" "ui/static/js/app.js"; then
        pass_test "app.js escapes HTML in formatMessage (XSS safe)"
    else
        fail_test "app.js does NOT escape HTML in formatMessage (potential XSS)"
    fi

    if grep -q "function loadProducts" "ui/static/js/app.js"; then
        pass_test "app.js has loadProducts"
    else
        fail_test "app.js missing loadProducts"
    fi

    if grep -q "function sendQuickQuery" "ui/static/js/app.js"; then
        pass_test "app.js has sendQuickQuery"
    else
        fail_test "app.js missing sendQuickQuery"
    fi
else
    fail_test "app.js does not exist"
fi

# Test: Pytest-based frontend tests
echo ""
echo "--- Pytest Frontend Tests (TestClient) ---"
echo ""
python3 -m pytest tests/test_agent_api.py -v --tb=short 2>&1
PYTEST_EXIT=$?
if [ $PYTEST_EXIT -eq 0 ]; then
    pass_test "pytest test_agent_api.py (session, web UI, static files)"
else
    fail_test "pytest test_agent_api.py failed"
fi

# ==========================================================
# PART 2: Live tests (only if --live flag)
# ==========================================================

if $LIVE; then
    echo ""
    echo "--- Live Server Tests (http://${HOST}:${PORT}) ---"
    echo ""

    BASE_URL="http://${HOST}:${PORT}"

    # Check server is running
    if ! curl -sf "${BASE_URL}/api/products" > /dev/null 2>&1; then
        fail_test "Server not reachable at ${BASE_URL}"
        echo ""
        echo "Start the server first: ./scripts/run_backend.sh"
    else
        pass_test "Server reachable at ${BASE_URL}"

        # Test: Home page
        HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "${BASE_URL}/")
        if [ "$HTTP_CODE" = "200" ]; then
            pass_test "GET / returns 200"
        else
            fail_test "GET / returned $HTTP_CODE (expected 200)"
        fi

        # Test: Home page contains key HTML
        BODY=$(curl -sf "${BASE_URL}/")
        if echo "$BODY" | grep -q "AI Commerce Agent"; then
            pass_test "Home page contains 'AI Commerce Agent'"
        else
            fail_test "Home page missing 'AI Commerce Agent'"
        fi

        # Test: Static CSS
        HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "${BASE_URL}/static/css/style.css")
        if [ "$HTTP_CODE" = "200" ]; then
            pass_test "GET /static/css/style.css returns 200"
        else
            fail_test "GET /static/css/style.css returned $HTTP_CODE"
        fi

        # Test: Static JS
        HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "${BASE_URL}/static/js/app.js")
        if [ "$HTTP_CODE" = "200" ]; then
            pass_test "GET /static/js/app.js returns 200"
        else
            fail_test "GET /static/js/app.js returned $HTTP_CODE"
        fi

        # Test: Products API
        PRODUCTS=$(curl -sf "${BASE_URL}/api/products" 2>/dev/null || echo "")
        if [ -n "$PRODUCTS" ] && echo "$PRODUCTS" | python3 -c "import sys,json; d=json.load(sys.stdin); assert 'products' in d" 2>/dev/null; then
            pass_test "GET /api/products returns valid JSON with products"
        else
            fail_test "GET /api/products invalid response"
        fi

        # Test: UCP Discovery
        UCP=$(curl -sf "${BASE_URL}/api/ucp/discover" 2>/dev/null || echo "")
        if [ -n "$UCP" ] && echo "$UCP" | python3 -c "import sys,json; d=json.load(sys.stdin); assert d.get('protocol')=='ucp'" 2>/dev/null; then
            pass_test "GET /api/ucp/discover returns UCP manifest"
        else
            fail_test "GET /api/ucp/discover invalid response"
        fi

        # Test: Session API
        SESSION=$(curl -sf "${BASE_URL}/api/session/test-frontend" 2>/dev/null || echo "")
        if [ -n "$SESSION" ] && echo "$SESSION" | python3 -c "import sys,json; d=json.load(sys.stdin); assert d.get('session_id')=='test-frontend'" 2>/dev/null; then
            pass_test "GET /api/session/test-frontend returns session"
        else
            fail_test "GET /api/session/test-frontend invalid response"
        fi

        # Test: Clear session
        CLEAR=$(curl -sf -X DELETE "${BASE_URL}/api/session/test-frontend" 2>/dev/null || echo "")
        if [ -n "$CLEAR" ] && echo "$CLEAR" | python3 -c "import sys,json; d=json.load(sys.stdin); assert d.get('status')=='cleared'" 2>/dev/null; then
            pass_test "DELETE /api/session/test-frontend clears session"
        else
            fail_test "DELETE /api/session/test-frontend invalid response"
        fi

        # Test: Chat API (only if OPENAI_API_KEY is set)
        if [ -n "${OPENAI_API_KEY:-}" ]; then
            CHAT=$(curl -sf -X POST "${BASE_URL}/api/chat" \
                -H "Content-Type: application/json" \
                -d '{"query": "hello", "session_id": "test-frontend"}' 2>/dev/null || echo "")
            if [ -n "$CHAT" ] && echo "$CHAT" | python3 -c "import sys,json; d=json.load(sys.stdin); assert 'response' in d" 2>/dev/null; then
                pass_test "POST /api/chat returns valid response"
            else
                fail_test "POST /api/chat invalid response"
            fi
        else
            echo "  SKIP: POST /api/chat (OPENAI_API_KEY not set)"
        fi
    fi
fi

# ==========================================================
# Summary
# ==========================================================

echo ""
echo "======================================"
echo "  Results: $PASSED/$TOTAL passed, $FAILED failed"
echo "======================================"

if [ $FAILED -gt 0 ]; then
    exit 1
fi
exit 0
