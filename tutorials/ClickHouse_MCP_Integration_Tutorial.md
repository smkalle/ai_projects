# ClickHouse + MCP Integration with Grok Pattern Support 🚀

This repository demonstrates a complete, production-grade integration between **ClickHouse**, a real-time analytical columnar database, and the **Model Context Protocol (MCP)**—the emerging standard for allowing Large Language Models (LLMs) to connect with third-party tools.

You will:
- Run and test ClickHouse queries from **Cursor**, **ChatGPT**, or **Claude** using natural language
- Enable **Grok-style pattern recognition** for structured log analysis
- Deploy a fully MCP-compatible server using **PydanticAI** and **uv**

---

## 🧱 Project Structure

```
clickhouse-mcp-demo/
├── clickhouse_mcp.py         # Main integration script
├── grok_patterns.sql         # Create & insert log data
├── requirements.txt          # Python dependencies
├── .env.example              # Environment template
├── README.md                 # This tutorial
```

---

## 🛠 Prerequisites

- Python ≥ 3.13
- Docker (for local ClickHouse)
- `uv` (https://astral.sh/uv)
- Anthropic Claude API key (for LLM)
- MCP-compatible client (e.g., Cursor)

Install `uv`:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

---

## ⚙️ Setup

### Clone & Configure
```bash
git clone https://github.com/yourname/clickhouse-mcp-demo.git
cd clickhouse-mcp-demo
cp .env.example .env
```
Edit `.env` with your configuration and API key.

### Install Python Dependencies
```bash
pip install -r requirements.txt
```

`requirements.txt`:
```
pydantic-ai
python-dotenv
tenacity
```

---

## 🐳 Local ClickHouse Setup

Run ClickHouse with Docker:
```bash
docker run -d --name clickhouse-server \
  -p 8123:8123 \
  clickhouse/clickhouse-server
```
Verify:
```bash
curl http://localhost:8123
# → Should return "Ok."
```

---

## 🔎 Create Sample Data

Load `grok_patterns.sql`:
```sql
CREATE TABLE log_events (
  raw_log String,
  timestamp DateTime
) ENGINE = MergeTree()
ORDER BY timestamp;

INSERT INTO log_events VALUES
('[INFO] 2025-06-01T12:00:00 Login succeeded user=alice', '2025-06-01 12:00:00'),
('[ERROR] 2025-06-01T12:05:00 Login failed user=bob', '2025-06-01 12:05:00');
```

Load via CLI:
```bash
curl -G 'http://localhost:8123' --data-urlencode "query=$(< grok_patterns.sql)"
```

---

## 🤖 MCP Integration

### clickhouse_mcp.py
```python
import asyncio, os
from dotenv import load_dotenv
from pydantic_ai import Agent, MCPServerStdio
from tenacity import retry, stop_after_attempt, wait_fixed

load_dotenv()

server = MCPServerStdio(
    command="uv",
    args=["run", "--with", "mcp-clickhouse", "--python", "3.13", "mcp-clickhouse"],
    env={**os.environ}
)

agent = Agent(
    model="anthropic:claude-sonnet-4-0",
    mcp_servers=[server],
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
async def run_query(q: str):
    return await agent.run(q)

async def main():
    async with server:
        response = await run_query("Find all ERROR logs on June 1, 2025")
        print("\nResponse:\n", response)

if __name__ == "__main__":
    asyncio.run(main())
```

Run:
```bash
python clickhouse_mcp.py
```

---

## 🧪 Sample Prompts for Grok Search

| Natural Language Prompt                    | Translated SQL |
|-------------------------------------------|----------------|
| What logs contain login errors?           | `SELECT ... WHERE raw_log LIKE '%Login failed%'` |
| List all ERROR-level logs for June 1      | `extract(raw_log, '[\\[](\\w+)[\\]]') = 'ERROR'` |
| What users logged in successfully?        | `extract(raw_log, 'user=([a-zA-Z]+)')` |

Test variations like:
```python
response = await run_query("List all users who failed login between 12:00 and 12:10")
```

---

## 🧠 MCP via Cursor

1. Launch **Cursor** editor
2. Go to: Settings → Integrations → MCP
3. Register MCP tool: `clickhouse_mcp.py`
4. Try:
```text
What were the most starred GitHub repos in 2025?
```

---

## 🛡️ Production Ready Tips

- 🔐 Use HTTPS + secure users (readonly)
- 📦 Deploy MCP server as microservice w/ `uv`
- 📈 Monitor via `system.query_log`
- 🧠 Add OpenTelemetry or Logfire for tracing

---

## 📚 References
- [ClickHouse Docs](https://clickhouse.com/docs/en/)
- [PydanticAI](https://github.com/pydantic/pydantic-ai)
- [uv](https://astral.sh/uv)
- [Cursor](https://cursor.sh)
- [MCP Protocol](https://github.com/mutabletools/mcp)

---

## 🧑‍💻 Contributing
PRs welcome! Fork the repo, test, and submit fixes, docs, or extensions.

```bash
git checkout -b my-feature
# make changes
git commit -am 'Add new example'
git push origin my-feature
```

---

## 📜 License
MIT License. Use freely, modify responsibly.

---

## ❤️ Acknowledgments

Inspired by ClickHouse, PydanticAI, and the MCP open tooling movement.
Let’s bring natural language to structured data—for everyone.

> _If you found this helpful, star 🌟 the repo and spread the word!_
