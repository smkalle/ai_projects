# Claude AI + n8n + MCP Integration: Complete Implementation Guide
> **Status**: Production-ready patterns • Updated **2025-08-01**  
> **What you’ll build**: Connect **Claude Desktop** to **n8n** via **Model Context Protocol (MCP)** so Claude can **send emails, hit APIs, update CRMs, schedule meetings, post to Slack,** and more — safely, with auth and audit trails.

This repo-style guide is a hands-on, end‑to‑end tutorial for AI engineers. You’ll wire up n8n’s **native MCP Server Trigger** to expose tools, then attach it to Claude using the `mcp-remote` connector. You’ll also learn to call *other* MCP servers from n8n with the **MCP Client Tool**, add auth, observability, and CI/CD.

---

## Table of Contents

- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Quick Start (TL;DR)](#quick-start-tldr)
- [Step 1 — Install/Upgrade n8n (v1.88+)](#step-1--installupgrade-n8n-v188)
- [Step 2 — Build an MCP Server in n8n](#step-2--build-an-mcp-server-in-n8n)
  - [2.1 Create the workflow and MCP endpoint](#21-create-the-workflow-and-mcp-endpoint)
  - [2.2 Add tools (email, HTTP, Slack, sub-workflows)](#22-add-tools-email-http-slack-sub-workflows)
  - [2.3 Harden auth](#23-harden-auth)
- [Step 3 — Connect Claude Desktop with `mcp-remote`](#step-3--connect-claude-desktop-with-mcp-remote)
- [Step 4 — Test from Claude](#step-4--test-from-claude)
- [Step 5 — Production deployment](#step-5--production-deployment)
- [Advanced Patterns](#advanced-patterns)
- [Security Checklist](#security-checklist)
- [Troubleshooting](#troubleshooting)
- [Observability & Ops](#observability--ops)
- [Appendix: Templates & JSON snippets](#appendix-templates--json-snippets)
- [References](#references)
## Architecture

```
Claude Desktop ──(MCP via mcp‑remote)──▶ n8n MCP Server Trigger ──▶ Tools
      │                                                ├─ Gmail Send
      │                                                ├─ HTTP Request (APIs)
      │                                                ├─ Slack Post Message
      │                                                └─ Call n8n Workflow Tool (sub‑workflows)
      │
      └───────────── Optional: n8n MCP Client Tool ──▶ External MCP servers
```

- **MCP Server Trigger (n8n)** exposes **tools** over SSE/HTTP-stream transports.
- **Claude Desktop** connects using **`mcp-remote`**; Claude discovers and calls your tools with structured inputs/outputs.
- Use **Custom/Call n8n Workflow Tool** to wrap existing workflows as reusable tools with clear input schemas.
## Prerequisites

- **n8n 1.88.0+** (Cloud or self-hosted; required for MCP nodes)
- **Claude Desktop** (with *Developer* settings available)
- **Node.js 18+** (to run `npx mcp-remote` or custom servers)
- **HTTPS** endpoint for production (reverse proxy OK)
- API keys/credentials for any services you’ll automate (Gmail, Slack, Calendar, CRM, etc.)
## Quick Start (TL;DR)

1. **Upgrade n8n** to >= **1.88.0** and enable public webhooks at your HTTPS domain.
2. In n8n, create a workflow with **MCP Server Trigger** → add one or more **Tool** nodes (Gmail/HTTP/Slack) and/or **Call n8n Workflow Tool**.
3. Activate the workflow and copy the **Production MCP URL** and **Bearer token**.
4. In **Claude Desktop → Settings → Developer → Edit Config**, add an entry using **`npx mcp-remote <MCP_URL> --header "Authorization: Bearer ${TOKEN}"`**.
5. Restart Claude and ask: **“/mcp list tools”** or **“What tools do you have?”** Then try: *“Send an email…”* or *“Call the Acme CRM API for customer 123”*.
## Step 1 — Install/Upgrade n8n (v1.88+)

**Docker (dev):**
```yaml
# docker-compose.dev.yml
version: '3.8'
services:
  n8n:
    image: n8nio/n8n:1.88.0
    ports: ["5678:5678"]
    environment:
      - N8N_BASIC_AUTH_ACTIVE=false
      - WEBHOOK_URL=http://localhost:5678
    volumes:
      - n8n_data:/home/node/.n8n
volumes:
  n8n_data: {}
```

**Docker (prod skeleton):**
```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  n8n:
    image: n8nio/n8n:1.88.0
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=${N8N_USER}
      - N8N_BASIC_AUTH_PASSWORD=${N8N_PASSWORD}
      - N8N_ENCRYPTION_KEY=${N8N_ENCRYPTION_KEY}
      - WEBHOOK_URL=https://n8n.yourdomain.com
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.n8n.rule=Host(`n8n.yourdomain.com`)"
      - "traefik.http.routers.n8n.tls.certresolver=letsencrypt"
```

> **Tip:** On n8n Cloud, set the **Version** to **1.88+**; on self-hosted, pull `n8nio/n8n:1.88.0`.
## Step 2 — Build an MCP Server in n8n

### 2.1 Create the workflow and MCP endpoint

1. **New Workflow** → add **MCP Server Trigger**.
2. Set **Authentication** = *Bearer*; create a credential (e.g., `MCP_BEARER`).
3. Optional: Set **Path** to a stable route (e.g., `/mcp/automation`).
4. Click **Activate**. Note the **Production MCP URL** (you’ll use it in Claude).

The MCP Trigger supports **SSE** and **HTTP streamable** transports. It exposes *only* connected **Tool** nodes as callable tools.

### 2.2 Add tools (email, HTTP, Slack, sub-workflows)

Add one or more of the following under the MCP Trigger:

**A) Gmail Send (email)**  
- Node: **Gmail** → *Send*  
- Map inputs from the MCP call:
  - `to` → `={{$json.to}}`
  - `subject` → `={{$json.subject}}`
  - `body` → `={{$json.body}}`

**B) Generic API (HTTP Request)**
- Node: **HTTP Request**  
- Map from MCP input:
  - `method` → `={{$json.method || "GET"}}`
  - `url` → `={{$json.url}}`
  - `headers` (JSON) → `={{$json.headers}}`
  - `query` (JSON) → `={{$json.query}}`
  - `body` (JSON) → `={{$json.body}}`

**C) Slack Notification**
- Node: **Slack** → *Post Message*  
- `channel` → `={{$json.channel}}`  
- `text` → `={{$json.text}}`

**D) Wrap existing workflows as tools**
- Node: **Call n8n Workflow Tool** (or “Custom n8n Workflow Tool”) to expose a sub‑workflow as a single tool.
- In the *sub‑workflow*, define **expected inputs** (fields or JSON example) and output shape, so Claude sees a clean tool schema.

> **Why sub‑workflows?** You get stable interfaces (contracts) and versioning for tools, instead of wiring raw nodes into the MCP trigger.

### 2.3 Harden auth

- Use **Bearer** or **Header** auth on the MCP Trigger.
- Store secrets in **Credentials**; never in node parameters.
- For Slack/Gmail/CRM, configure provider credentials with least permissions required.
## Step 3 — Connect Claude Desktop with `mcp-remote`

Open **Claude Desktop → Settings → Developer → Edit Config** and add an entry like:

```jsonc
{
  "mcpServers": {
    "n8n-automation": {
      "command": "npx",
      "args": [
        "mcp-remote",
        "https://n8n.yourdomain.com/mcp/automation",    // Production MCP URL
        "--header",
        "Authorization: Bearer ${N8N_MCP_TOKEN}"
      ],
      "env": {
        "N8N_MCP_TOKEN": "paste-your-token-here"
      }
    }
  }
}
```

> If your n8n shows separate URLs for **Test** and **Production**, use **Production** for real runs and **Test** while iterating in the editor. Restart Claude after saving.
## Step 4 — Test from Claude

In a new chat, try:

```
/mcp list tools
```
You should see your tools (e.g., `send_email`, `http_request`, `slack_post`, or your sub‑workflow tools). Then test an action:

> **Example:**  
> *“Send an email to `test@example.com` with subject `MCP Test` and body `Integration working!`”*

Or invoke a generic API:
> *“Call the `GET https://api.github.com/repos/owner/repo` endpoint and summarize the response.”*

Check n8n **Executions** to verify runs and debug inputs/outputs.
## Step 5 — Production deployment

**Reverse proxy (nginx) for SSE/HTTP‑stream):**
```nginx
location /mcp/ {
  proxy_http_version          1.1;
  proxy_buffering             off;
  gzip                        off;
  chunked_transfer_encoding   off;
  proxy_set_header            Connection '';
  proxy_pass                  http://n8n:5678;
}
```

**Queue mode / replicas:** Route all `/mcp*` traffic to a **single** webhook replica to avoid broken streams. Prefer dedicated ingress rules for MCP paths.
## Advanced Patterns

1. **Two‑way toolbelt:** From n8n, call *other* MCP servers using the **MCP Client Tool**. This lets n8n agents use tools from GitHub, filesystems, or third‑party MCP vendors.
2. **Typed tool schemas:** In sub‑workflows, define inputs via **JSON example** so Claude gets precise argument names and types. Keep outputs small and structured.
3. **Role‑based tools:** Create multiple MCP Trigger workflows (e.g., `/mcp/sales`, `/mcp/support`) exposing only the tools each role needs.
4. **Safeguards:** Add **Approvals** or **Form** nodes for high‑risk actions (e.g., wire transfers, mass emails). Gate with environment flags.
5. **Secrets handoff:** Use short‑lived access tokens from an IdP (OAuth2) and inject with Header auth. Rotate on schedule.
6. **Multi‑agent orchestration:** Let Claude propose a plan; have n8n execute via multiple tools with retries, backoff, and compensating actions.
## Security Checklist

- [ ] HTTPS everywhere; no plain HTTP in production
- [ ] **Bearer/Header** auth on the MCP Trigger; long random tokens; rotate regularly
- [ ] Narrow OAuth scopes for Gmail/Slack/Calendar/CRM
- [ ] Input validation in Function nodes (reject unexpected fields / sizes)
- [ ] Rate limits and concurrency caps on destructive tools
- [ ] Separate **test** and **prod** MCP URLs; least privilege per environment
- [ ] Audit logs: persist tool calls (who/what/when/params subset)
- [ ] Disable community tool usage unless needed (`N8N_COMMUNITY_PACKAGES_ALLOW_TOOL_USAGE=false`)
## Troubleshooting

**Claude can’t see tools**
- Ensure the **MCP Server Trigger** is **executing** (Test) or **activated** (Production).
- Tools must be **connected** to the MCP Trigger; disconnected nodes aren’t exposed.

**Auth errors**
- Verify the token in Claude matches your n8n credential.
- If using `--header`, keep the exact `Authorization: Bearer <token>` format.

**Broken streams / timeouts**
- Make sure reverse proxy disables buffering and enables HTTP/1.1 as above.
- In queue mode with multiple replicas, pin `/mcp*` to one webhook pod.

**Parameter shape mismatch**
- In sub‑workflows, define inputs via **fields** or **JSON example**; reference with `{{$json.foo}}` in tool nodes.
- Log the raw `$json` in a **Function** node to inspect what Claude sends.

**Version drift**
- MCP nodes require **n8n 1.88.0+**. Confirm your image tag and Cloud version selector.
## Observability & Ops

Add a lightweight logger tool wired to the MCP Trigger:

```js
// Function node: "Log Execution"
console.log('MCP Operation', {
  at: new Date().toISOString(),
  tool: $json.__tool,
  user: $json.__user || 'unknown',
  params: Object.keys($json),
});
return items;
```

Monitor:
- MCP request latency & error rate
- Per‑tool success/failure
- Upstream API quotas / rate limits
## Appendix: Templates & JSON snippets

**Minimal sub‑workflow input contract**
```json
{
  "to": "string (email)",
  "subject": "string",
  "body": "string (markdown allowed)"
}
```

**Claude Desktop config (multiple servers)**
```jsonc
{
  "mcpServers": {
    "n8n-sales": {
      "command": "npx",
      "args": ["mcp-remote", "https://n8n.yourdomain.com/mcp/sales", "--header", "Authorization: Bearer ${SALES_TOKEN}"]
    },
    "n8n-support": {
      "command": "npx",
      "args": ["mcp-remote", "https://n8n.yourdomain.com/mcp/support", "--header", "Authorization: Bearer ${SUPPORT_TOKEN}"]
    }
  }
}
```
## References

- n8n **MCP Server Trigger** docs: https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-langchain.mcptrigger/
- n8n **MCP Client Tool** docs: https://docs.n8n.io/integrations/builtin/cluster-nodes/sub-nodes/n8n-nodes-langchain.toolmcp/
- n8n template (requires 1.88+): https://n8n.io/workflows/3514-build-an-mcp-server-with-google-calendar-and-custom-functions/
- Model Context Protocol site: https://modelcontextprotocol.io/
- Connect Claude to remote MCP via `mcp-remote`: https://developers.cloudflare.com/agents/guides/test-remote-mcp-server/
- Anthropic MCP docs & Desktop extensions: https://docs.anthropic.com/en/docs/claude-code/mcp , https://www.anthropic.com/engineering/desktop-extensions
- VS Code MCP docs: https://code.visualstudio.com/docs/copilot/chat/mcp-servers
- IBM on MCP: https://www.ibm.com/think/topics/model-context-protocol

**Context**
- Julian Goldie’s posts and video walkthroughs on n8n + MCP (X/YouTube) for non‑coders and templates


---

## Importable n8n Workflows (Copy/Import)

**Option A — MCP Trigger (preferred, n8n ≥ 1.88.0):**  
Download and import: [`n8n-mcp-starter-workflow.json`](sandbox:/mnt/data/n8n-mcp-starter-workflow.json)

**Option B — Webhook fallback (works on older n8n):**  
Download and import: [`n8n-webhook-starter-workflow.json`](sandbox:/mnt/data/n8n-webhook-starter-workflow.json)

> After import, open each node and **set credentials** for Gmail and Slack, and replace any placeholder values.  
> For MCP: put your **Header Auth** token on the **MCP Server Trigger** node, and copy the **Production MCP URL** from n8n into Claude’s `mcp-remote` config.

**What the workflows expect from Claude (or a client):**

- **send_email**  
  ```json
  {
    "tool": "send_email",
    "to": "person@example.com",
    "subject": "Hello from MCP",
    "body": "This is a test."
  }
  ```

- **http_request**  
  ```json
  {
    "tool": "http_request",
    "method": "GET",
    "url": "https://api.github.com/repos/n8n-io/n8n",
    "headers": {}, 
    "query": {}
  }
  ```

- **slack_post**  
  ```json
  {
    "tool": "slack_post",
    "channel": "#general",
    "text": "Deployment finished ✅"
  }
  ```

> The MCP Trigger dispatches the payload to the **Normalize Input → Route by Tool** logic, then runs only the selected branch (Gmail/HTTP/Slack) and returns a merged result.
