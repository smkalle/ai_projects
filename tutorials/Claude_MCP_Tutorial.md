
# 🔌 Claude + MCP: Build Looping AI Agents that Outsmart 99.9% of Users

This tutorial is for AI engineers who want to integrate Claude with the **Model Context Protocol (MCP)** to build tool-using, loop-capable agents. Based on Riley Brown’s demo from Greg Isenberg’s post, this practical guide walks you through setup, agent logic, deployment, and advanced orchestration.

---

## 🧠 1. Why MCP + Claude?

MCP is an open standard from Anthropic that connects LLMs to external data and tools without custom glue code. Think of it as a “USB-C for LLMs”. It powers early adopters like:

- **Block**
- **Apollo**
- **Zed**
- **Replit**
- **Codeium**
- **Sourcegraph**

Claude can call MCP servers to *Plan → Act → Reflect* in loops that make it truly autonomous.

---

## 🛠️ 2. Prerequisites

| Tool | Purpose |
|------|---------|
| Claude API / Claude Desktop | Main LLM agent |
| `@anthropic-ai/mcp` CLI | Scaffolding & testing |
| Docker + Compose | Containerization |
| GitHub | Hosting server code |
| Postgres or your DB | Sample data source |

Install CLI:

```bash
npm install -g @anthropic-ai/mcp
export ANTHROPIC_API_KEY=sk-...
```

---

## ⚙️ 3. Setup MCP Server

### 3.1 Clone a reference

```bash
git clone https://github.com/modelcontextprotocol/servers mcp-lab
cd mcp-lab/skeleton-python
```

### 3.2 Define resource

Edit `resources.py`:

```python
from mcp import Resource, Field

class Ticket(Resource):
    id = Field(int, primary=True)
    text = Field(str)

    def list_open(limit: int = 20):
        return db.query("SELECT id, text FROM tickets WHERE status='OPEN' LIMIT %s", limit)
```

### 3.3 Run & expose

```bash
docker compose up
mcp dev proxy
```

Expose via Claude Desktop → Add Tool → Custom URL.

---

## 🤖 4. Connect Claude to Server

Create a manifest:

```json
{
  "schema_version": "v1",
  "name_for_model": "support_db",
  "description_for_model": "Query open support tickets",
  "auth": { "type": "none" },
  "api": { "type": "mcp", "url": "https://<your-tunnel>.mcp.dev" }
}
```

---

## 🔁 5. Agent Loop: Plan → Act → Reflect

Claude can loop intelligently using tools:

```python
system = '''
You are an autonomous troubleshooting agent.
Use support_db and aws_docs tools.
Loop: PLAN → ACT → REFLECT.
'''
```

---

## 🧬 6. Orchestration Patterns

| Pattern | Example Tools | Use-Case |
|--------|----------------|----------|
| Fan-out | GitHub + Jira + Slack | Code → Ticket → Notify |
| Chain | Notion → Glyph | Content → Thumbnail |
| Mesh | DB + Vector DB | Augmented RAG |

---

## 🔐 7. Security

Use HMAC auth headers to secure JSON-RPC calls:

```http
Authorization: MCP-HMAC <timestamp>:<sig>
```

---

## 🚀 8. Production Tips

- Use **distroless** containers
- Kubernetes ingress with MCP routing
- Add **token + latency metrics**
- Feature-flag manifests

---

## 🎥 9. Case Study: Riley Brown

| Step | MCP Tool | Action |
|------|----------|--------|
| 1 | Notion | Find high-performing hooks |
| 2 | Glyph | Auto-generate thumbnails |
| 3 | YouTube | Upload & schedule |
| 4 | Analytics | Optimize from CTR data |

---

## 📚 10. Resources

- [Anthropic MCP Docs](https://docs.anthropic.com)
- [GitHub MCP Server](https://github.com/modelcontextprotocol/servers)
- [Awesome MCP Servers](https://github.com/modelcontextprotocol/awesome-mcp)
- [Greg Isenberg + Riley Demo](https://x.com/gregisenberg)

---

> 🚧 You now have a full MCP-powered Claude agent loop connected, deployed, and ready to automate real workflows.

