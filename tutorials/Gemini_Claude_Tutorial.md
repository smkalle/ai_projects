
# Gemini CLI + Claude Code  
### A Hands‑On Integration & Comparison Guide (July 2025)

> **TL;DR** — Gemini CLI (free, 1 M‑token context) and Claude Code (paid, deep reasoning) play to opposite strengths.  
> Pair them via direct CLI calls or the **Model Context Protocol (MCP)** to cover both *huge* codebases **and** *reliable* agentic execution.

---

## 1  Why use them together?
|  | Gemini CLI | Claude Code |
|---|-----------|-------------|
|Model|**Gemini 2.5 Pro**|**Claude 4 (Opus / Sonnet)**|
|Context window|**≈ 1 M tokens**|Smaller (≤ 200 k tokens)|
|Pricing (Jul 2025)|Free tier: 60 req/min, 1 000 req/day|Pro US $20 / Max US $200 per month|
|Licence|Apache‑2.0, open source|Closed|
|Sweet‑spot|Whole‑repo analysis, web‑grounded search|Refactors, reliable multi‑step plans|

Gemini’s *breadth* and Claude’s *depth* are complementary.

---

## 2  Architectural patterns

```
                   ┌──────────────────┐
    (big‑repo)     │  Gemini CLI      │
    CLI call 1 ───▶│  "--pipe" mode   │
                   └────────┬─────────┘
                            │ stdout JSON
                            ▼
┌────────────┐   stdin   ┌────────────┐
│ Claude 4   │◀──────────│  MCP       │  ← pattern B
│  planner   │           │  Server    │
└────────────┘           └────────────┘
     ▲  ▲                     ▲
     │pattern A   small‑ctx   │
     └────────────────────────┘
```

* **Pattern A — Tool Invocation**  
  Claude invokes `gemini -p` directly whenever a request risks blowing its context.

* **Pattern B — MCP Bridge**  
  A local **MCP server** mediates, adds rate‑limit, confidence fusion, and logging.

---

## 3  5‑minute Quick Start

```bash
# 1. Install Node 18+ & Gemini CLI
npm install -g @google/gemini-cli
gemini --help         # triggers auth → sign in w/ Google

# 2. Ask something
echo "List top OWASP rules" | gemini -m gemini-2.5-pro

# 3. (Optional) Grab Claude Code
#   → https://claude.ai or Anthropic API key
```

---

## 4  Standalone cheat‑sheets
### 4.1 Gemini CLI

```bash
# Large‑repo summary
gemini -p "Summarise this repo" -d .

# Web‑grounded answer
gemini "Why use functional options pattern in Go?"
```

⚙️ *Config*: `$HOME/.config/gemini/cli-config.json`  
🚦 Rate‑limit: 60 req/min · 1 000/day (free)  
🛡 Auth: browser‑based OAuth; prefer **host‑based** execution over containers.

### 4.2 Claude Code

```bash
# With Anthropic CLI
pip install anthropic
export ANTHROPIC_API_KEY="sk‑..."
anthropic complete --model opus‑4 --prompt "Refactor this Go file..."
```

Plan options: **Pro**, **Max**, **Team**, **Enterprise**.

---

## 5  Pattern A – Gemini CLI as Claude tool
1. **Add usage note** in `CLAUDE.md` (example below).  
2. Claude spots tasks ➜ `gemini -p "...long prompt..."`.  
3. Claude merges Gemini output into its reasoning.

```markdown
# `CLAUDE.md`
## Large‑Context Helper
Use **Gemini CLI** for tasks that:
- span >150 k tokens
- traverse many files
- require real‑time web search

Call template:  
```bash
gemini -p "{task}" -d .
```
```

---

## 6  Pattern B – MCP server bridge
> Based on the community gist *Gemini CLI Integration for Claude Code*.

### 6.1 Folder layout
```text
your‑project/
  mcp-server.py
  gemini_integration.py
  gemini-config.json
  mcp-config.json
```

### 6.2 Setup

```bash
# a) Install Gemini CLI (host)
npm i -g @google/gemini-cli

# b) Start MCP
python3 mcp-server.py --project-root .

# c) Claude desktop → add mcp-config.json
```

### 6.3 Key environment flags

|Var|Purpose|Typical|
|---|-------|-------|
|`GEMINI_ENABLED`|turn integration on/off|`true`|
|`GEMINI_AUTO_CONSULT`|auto second‑opinion on uncertainty|`true`|
|`GEMINI_TIMEOUT`|CLI timeout (s)|`300`|

---

## 7  Workflow recipes
### 7.1 Repo security scan
```bash
# Claude prompt
"Analyse repo for SQL injection, use Gemini if >20 files."
```
> Gemini summarises findings → Claude prints remediation checklist.

### 7.2 Root‑cause debugging
```bash
# Claude
"My Node app crashes, diagnose; delegate whole repo diff to Gemini."
```

### 7.3 PyTest generation
Claude: plan suite → Gemini: bulk‑generate tests → Claude: verify and trim.

---

## 8  Best practices & gotchas
* **Warm up Gemini**: first call can be slow (auth token).  
* **Rate limits**: respect `gemini status` logs; queue calls >1 000/day.  
* **Context trimming**: gzip large diffs before piping.  
* **Security**: never pipe secrets; use host‑based auth, not inside CI.  
* **Troubleshooting**:  
  * `EACCES` → reinstall Node ≥18.  
  * 429 errors → wait 60 s or add `--rate-limit`.

---

## 9  Next steps
* Switch Gemini model with `-m gemini-2.5-flash` for faster but cheaper calls.  
* Try **Claude Team** plan for shared memory pools.  
* Watch the GitHub issues for LiteLLM & VS Code extensions.

---

## 10  References
1. Google Blog — *Introducing Gemini CLI* (Jun 2025).  
2. Anthropic — *Introducing Claude 4*.  
3. Andrew Altimit — *Gemini CLI × Claude Code MCP Integration* Gist.  
4. Anthropic — *Model Context Protocol* documentation.

---

