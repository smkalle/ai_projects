# Improvement Plan: AI Commerce Agent UCP

## Comparison: Other Agent (ChatGPT) vs Our Implementation

### What the Other Agent Built (Minimal)

| File | What it does |
|------|-------------|
| `products.json` | Flat product list (2 items) |
| `merchant_server.py` | Single-file FastAPI with `/.well-known/ucp` + `POST /checkout-sessions` |
| `agent_graph.py` | Naive keyword matching, no real RAG or LangGraph (stubs only) |
| `agent_api.py` | Single `/chat` endpoint wrapping the agent |

**Design philosophy:** Get a working demo fast, acknowledge stubs, defer real integrations.
No tests, no UI, no cart management, no session state, no error handling.

### What We Built (Full-Stack)

| Component | Files | Status |
|-----------|-------|--------|
| Merchant Server | 4 files, 15 endpoints | Complete |
| RAG Engine | `agent/rag.py` with ChromaDB | Real (requires OpenAI key) |
| LangGraph Agent | `agent/graph.py` with 7-node StateGraph | Real conditional workflow |
| UCP Client | `agent/ucp_client.py` | Full CRUD wrapper |
| Agent API | `agent_api.py` with sessions | 7 API endpoints |
| Web UI | HTML + CSS + JS (3 files) | Interactive chat + product catalog |
| Tests | 3 test files, 37 passing | Merchant + models + API |
| Config | `config.py` + `.env.example` | pydantic-settings |

### Gap Analysis: Where the Other Agent's Simplicity Reveals Our Weaknesses

The other agent's minimal approach actually highlights areas where our fuller
implementation introduced complexity without fully solving the underlying problems:

1. **They avoided subprocess management entirely** (single process) - we took on
   subprocess orchestration in `agent_api.py:50-102` but implemented it poorly
   (hardcoded sleeps, no cleanup on error, no monitoring).

2. **They kept state trivial** (stateless per-request) - we added sessions but
   stored them in a volatile dict with no expiration and no persistence.

3. **They used simple keyword matching** as an honest placeholder - we wired up
   real ChromaDB but with no fallback if OpenAI is unreachable, meaning our app
   actually fails harder than theirs does.

---

## Improvement Plan (Priority Order)

### Phase 1: Reliability & Error Handling (Critical)

#### 1.1 Fix Subprocess Lifecycle in `agent_api.py`

**Problem:** `agent_api.py:50-102` - Hardcoded `time.sleep(2)`, no try/finally
cleanup, orphaned processes on crash, blocking sync calls in async lifespan,
`os.chdir()` is process-global and not thread-safe.

**Changes:**
- Replace `time.sleep(2)` + fixed retry loop with async exponential backoff
  using `httpx.AsyncClient` instead of blocking `requests`
- Wrap entire lifespan in try/finally so merchant process is always terminated
- Add SIGKILL fallback after SIGTERM timeout
- Remove `os.chdir()` - use absolute paths everywhere
- Drain stdout/stderr from subprocess to prevent pipe buffer deadlock

**File:** `agent_api.py` (lines 32-102)

#### 1.2 Add Error Recovery Node to LangGraph

**Problem:** `agent/graph.py` - If RAG fails (line 80) or UCP client throws
(line 168), the exception either crashes the pipeline or sets `state["error"]`
which `generate_response` then ignores.

**Changes:**
- Add `handle_error` node that reads `state["error"]` and generates a helpful
  fallback response
- Add conditional edges from `retrieve`, `buy`, `checkout`, `cart` nodes that
  route to `handle_error` when `state["error"]` is set
- Wrap `detect_intent` in try/except with fallback to keyword-based intent
  detection (no LLM needed)

**File:** `agent/graph.py`

#### 1.3 Add Keyword Search Fallback to RAG

**Problem:** `agent/rag.py:105-107` - If ChromaDB or OpenAI embeddings are
unavailable, `search()` throws and the whole pipeline fails. The other agent's
naive keyword approach is actually more resilient.

**Changes:**
- Add `keyword_search(query, products_json_path)` method that does substring
  matching (like the merchant server's `/products/search` does)
- In `search()`, catch exceptions and fall back to keyword search
- Log degraded mode clearly

**File:** `agent/rag.py`

#### 1.4 Add Request Timeouts to UCP Client

**Problem:** `agent/ucp_client.py` - No timeouts on any HTTP calls except
`health_check`. A hung merchant server blocks the agent indefinitely.

**Changes:**
- Add `timeout: float = 10.0` to `__init__` and pass to all requests
- Add retry logic (max 2 retries with 1s backoff) for transient errors

**File:** `agent/ucp_client.py`

---

### Phase 2: Agent Intelligence (High Value)

#### 2.1 Multi-Turn Conversation History

**Problem:** `agent/graph.py:36` - `conversation_history` field exists in
AgentState but is never populated. Each query starts from scratch with no
memory of what the user previously asked.

**Changes:**
- Store conversation history in the session (`agent_api.py:129-133`)
- Pass last N messages (configurable, default 10) into `run_query()`
- In `generate_response()`, include history in the LLM messages list
- In `detect_intent()`, include history for better intent classification
  (e.g., "yes, buy that one" after a search should resolve to "buy")

**Files:** `agent/graph.py`, `agent_api.py`

#### 2.2 Product Selection Instead of First-Match

**Problem:** `agent/graph.py:159` - `handle_buy` always grabs `product_results[0]`.
If user says "buy the USB cable" and headphones ranked first, wrong item purchased.

**Changes:**
- Add `select_product` node between `retrieve_for_buy` and `buy`
- Use the LLM to pick the best matching product from results given the user's
  query (e.g., "The user said 'buy the cable'. Which of these products?")
- Store selected product ID in state as `selected_product_id`
- `handle_buy` uses `selected_product_id` instead of index 0

**File:** `agent/graph.py`

#### 2.3 RAG Quality Improvements

**Problem:** `agent/rag.py:105` - No minimum similarity threshold, no metadata
filtering, no result diversity.

**Changes:**
- Use `search_with_scores()` and filter results below a configurable threshold
  (default 0.7)
- Add `in_stock_only: bool` parameter that filters by quantity > 0 via Chroma
  metadata filter (`where={"quantity": {"$gt": 0}}` - requires adding quantity
  to metadata in `load_products`)
- Add `quantity` to document metadata (line 82-88)

**File:** `agent/rag.py`

---

### Phase 3: UCP Compliance & Merchant Server (Medium)

#### 3.1 Fix UCP Manifest to Match Actual Endpoints

**Problem:** `merchant_server/server.py:67-102` - Manifest declares 4 capabilities
but server has 10+ endpoints. Cart capability says `["GET", "POST"]` on `/cart`
but actual endpoints include `GET /cart/{id}`, `POST /cart/{id}/items`,
`DELETE /cart/{id}/items/{product_id}`.

**Changes:**
- Expand capabilities list to declare all endpoints accurately
- Add `product_list` capability for `GET /products`
- Split cart into `cart_create`, `cart_view`, `cart_add_item`, `cart_remove_item`
- Add `checkout_view` and `checkout_confirm` capabilities
- Add endpoint version prefix support (optional, `/v1/` prefix)

**File:** `merchant_server/server.py`

#### 3.2 Add Cart Quantity Update Endpoint

**Problem:** Can add and remove cart items but cannot update quantity. User
saying "change to 3 headphones" requires remove + re-add.

**Changes:**
- Add `PATCH /cart/{cart_id}/items/{product_id}` with `{"quantity": N}` body
- Add corresponding `update_cart_item()` to `UCPClient`
- Add to UCP manifest

**Files:** `merchant_server/server.py`, `merchant_server/models.py`,
`agent/ucp_client.py`

#### 3.3 Standardize Error Responses

**Problem:** Errors are raw FastAPI HTTPException with unstructured `detail` strings.

**Changes:**
- Create `UCPError` Pydantic model with `code`, `message`, `details` fields
- Add custom exception handler that returns consistent JSON errors
- Use error codes like `PRODUCT_NOT_FOUND`, `INSUFFICIENT_STOCK`,
  `INVALID_CHECKOUT_STATE`

**Files:** `merchant_server/models.py`, `merchant_server/server.py`

---

### Phase 4: Testing (Important)

#### 4.1 Add Agent Workflow Tests with Mocked LLM

**Problem:** Zero test coverage on `agent/graph.py` and `agent/rag.py`.
The LangGraph workflow, intent detection, and RAG are completely untested.

**Changes:**
- Create `tests/test_agent_graph.py`:
  - Mock `ChatOpenAI` to return predetermined intents/responses
  - Mock `get_product_rag()` to return fake Documents
  - Mock `get_ucp_client()` to return fake cart/checkout data
  - Test each intent path: search, buy, cart, checkout, general
  - Test error handling: RAG fails, UCP client fails, invalid intent
- Create `tests/test_rag.py`:
  - Test `keyword_search` fallback (after Phase 1.3)
  - Test `format_results` with various inputs
  - Test empty results handling

**Files:** `tests/test_agent_graph.py` (new), `tests/test_rag.py` (new)

#### 4.2 Add Chat API Integration Test

**Problem:** `/api/chat` endpoint (the main user-facing endpoint) has zero tests.

**Changes:**
- In `tests/test_agent_api.py`, add `TestChat` class
- Mock `run_query` to return predetermined results
- Test session state persistence across multiple calls
- Test error response when agent fails

**File:** `tests/test_agent_api.py`

#### 4.3 Add UCP Client Tests

**Changes:**
- Create `tests/test_ucp_client.py`
- Use `responses` or `httpx` mock to simulate merchant server
- Test timeout handling, retry logic (after Phase 1.4)
- Test all CRUD operations

**File:** `tests/test_ucp_client.py` (new)

---

### Phase 5: Security & Production Readiness (Important)

#### 5.1 Sanitize LLM Output in Frontend

**Problem:** `ui/static/js/app.js:88` - `contentDiv.innerHTML = formatMessage(content)`
renders LLM output as raw HTML. If the LLM returns `<script>` or `<img onerror=...>`,
it executes in the browser.

**Changes:**
- Add DOMPurify (CDN link in index.html) or write a strict allowlist sanitizer
- In `formatMessage()`, sanitize the final HTML before assignment
- Only allow `<p>`, `<strong>`, `<code>`, `<pre>`, `<ul>`, `<li>`, `<br>` tags

**Files:** `ui/static/js/app.js`, `ui/templates/index.html`

#### 5.2 Add Rate Limiting

**Changes:**
- Add `slowapi` dependency
- Rate limit `/api/chat` to 10 requests/minute per session
- Rate limit `/api/products` to 60 requests/minute
- Return 429 with Retry-After header

**Files:** `agent_api.py`, `pyproject.toml`

#### 5.3 Add Session Expiration

**Problem:** `agent_api.py:122-133` - Sessions accumulate forever in memory with
no TTL, no max count.

**Changes:**
- Add `created_at` timestamp to each session
- Add background task that prunes sessions older than 1 hour
- Cap max sessions at 1000, evict oldest when exceeded

**File:** `agent_api.py`

---

### Phase 6: UI Enhancements (Nice to Have)

#### 6.1 Add Product Detail Modal

**Changes:**
- Clicking a product card opens a detail modal with full description, rating,
  stock info, and "Add to Cart" / "Buy Now" buttons
- Wire buttons to send appropriate chat queries

**Files:** `ui/templates/index.html`, `ui/static/js/app.js`, `ui/static/css/style.css`

#### 6.2 Add Cart Sidebar

**Changes:**
- Replace the static info panel with a live cart view when cart is active
- Show items, quantities, totals, and "Checkout" button
- Auto-refresh after buy/cart operations

**Files:** `ui/templates/index.html`, `ui/static/js/app.js`, `ui/static/css/style.css`

#### 6.3 Add Streaming Responses

**Changes:**
- Switch `/api/chat` to use Server-Sent Events (SSE) for streaming LLM output
- Use LangChain's `.stream()` instead of `.invoke()` in `generate_response()`
- Frontend reads SSE and renders tokens incrementally

**Files:** `agent/graph.py`, `agent_api.py`, `ui/static/js/app.js`

---

## Summary: Priority Matrix

| Phase | Effort | Impact | Risk if Skipped |
|-------|--------|--------|-----------------|
| 1. Reliability | Medium | Critical | App crashes in production |
| 2. Intelligence | Medium | High | Agent gives wrong answers, buys wrong items |
| 3. UCP Compliance | Low | Medium | Manifest misleads agent consumers |
| 4. Testing | Medium | High | Regressions undetected |
| 5. Security | Low | High | XSS, DoS, session exhaustion |
| 6. UI | Medium | Low | Functional but basic |

**Recommended execution order:** 1 → 2 → 4 → 5 → 3 → 6
(Fix reliability first, then make the agent smarter, then prove it with tests,
then harden, then polish.)
