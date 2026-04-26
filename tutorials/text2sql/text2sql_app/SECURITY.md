# WardOps Dashboard — text2sql Tutorial App

> 🏥 Natural language query interface for hospital operations, powered by agentic text-to-SQL (text2sql SDK + LangChain Deep Agents + Claude Sonnet).

## Quick Start

```bash
cd text2sql_app
pip install -r requirements.txt
export ANTHROPIC_API_KEY=<YOUR_ANTHROPIC_KEY>
streamlit run streamlit_app.py
```

## Features

- **💬 Query tab** — ask NL questions, get SQL + results
- **🛠️ Admin tab** — schema monitor, view browser, SQL translation verifier, DB health, scenarios seed

## Based On

- [text2sql-framework](https://github.com/Text2SqlAgent/text2sql-framework)
- WardOps BRD+PRD (`../wardops-brd-prd.md`)

## License

MIT
