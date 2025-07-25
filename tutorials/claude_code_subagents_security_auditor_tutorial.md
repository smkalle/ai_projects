# Build a **Security-Audit Subagent** in **Claude Code v1.0.60**  
_A hands-on, SDE3-level tutorial for AI engineers_

> **TL;DR**: You’ll create a **custom Claude Code subagent** called `security-auditor` that runs secure code reviews (OWASP Top 10 focus), integrates with your Git workflow (e.g., pre-commit), and produces structured, severity-tagged findings. You’ll also learn how to extend it into a **multi-subagent swarm** (e.g., `secrets-hunter`, `license-checker`, `sbom-auditor`) and how to continuously evaluate its quality.

---

## Table of Contents

1. [Why subagents?](#why-subagents)
2. [What you’ll build](#what-youll-build)
3. [Prerequisites](#prerequisites)
4. [Project scaffold](#project-scaffold)
5. [Step 1 — Install & verify Claude Code](#step-1--install--verify-claude-code)
6. [Step 2 — Create a vulnerable demo repo](#step-2--create-a-vulnerable-demo-repo)
7. [Step 3 — Define the `security-auditor` subagent](#step-3--define-the-security-auditor-subagent)
8. [Step 4 — Run the agent on your codebase](#step-4--run-the-agent-on-your-codebase)
9. [Step 5 — Wire it into your workflow (git hooks, CI)](#step-5--wire-it-into-your-workflow-git-hooks-ci)
10. [Step 6 — Hardening, evaluation & continuous improvement](#step-6--hardening-evaluation--continuous-improvement)
11. [Going further — Multi-subagent swarms](#going-further--multi-subagent-swarms)
12. [Troubleshooting](#troubleshooting)
13. [FAQ](#faq)
14. [License](#license)

---

## Why subagents?

Claude Code **v1.0.60** introduces **custom subagents** that:
- **Partition context**: each subagent has its **own context window**, minimizing cross-talk and reducing context overload.
- **Specialize tasks**: give security audits (or any deep specialty task) a **focused, role-aligned system prompt** and toolset.
- **Compose workflows**: chain or parallelize multiple subagents (e.g., `security-auditor`, `secrets-hunter`) to cover the spectrum of software risks.

Early community feedback highlighted:
- **Strong wins**: cleaner separation of concerns, faster iterations on narrow tasks (e.g., security, docs, testing).
- **Rough edges**: command / tool routing & recognition occasionally flaky → add **explicit commands**, **strict prompts**, and **fallback scripts**.

---

## What you’ll build

A production-ready **security auditing subagent** that:

- Scans your repo and reports:
  - **OWASP Top 10** style issues
  - **Hard-coded secrets**
  - **Insecure crypto, auth, CORS configs**, etc.
- Outputs **machine-readable JSON** + **human-friendly Markdown**.
- Blocks commits with **High/Critical** issues (optional).
- Runs locally (CLI) or in CI (GitHub Actions, GitLab CI, etc.).

You’ll also:
- Add **evaluation harnesses** to track precision/recall on seeded vulns.
- Learn to **compose more subagents** for orthogonal concerns.

---

## Prerequisites

- **Claude Code v1.0.60 or later** (verify below).
- **Node.js ≥ 18** (if your Claude Code CLI depends on Node; adapt if you installed via another channel).
- **Git** (for hooks / CI).
- Python 3.9+ (for demo vulnerable code / evaluator scripts).

> ⚠️ **CLI surface may differ slightly across platforms / releases.** If a command here doesn’t exist, run `claude --help` or `claude agents --help` and adapt. Keep your **docs handy** and pin versions in CI.

---

## Project scaffold

```bash
security-auditor-demo/
├─ .claude/
│  └─ agents/
│     └─ security-auditor.agent.json
├─ audit/
│  ├─ prompts/
│  │  └─ security-auditor.system.md
│  ├─ rules/
│  │  ├─ owasp-top10.md
│  │  └─ patterns.yaml
│  └─ runners/
│     ├─ run_audit.sh
│     └─ postprocess_report.py
├─ scripts/
│  ├─ install_git_hook.sh
│  └─ eval_seeded_vulns.py
├─ src/
│  └─ vulnerable.py
├─ .git/hooks/            # (generated)
├─ .pre-commit-config.yaml (optional)
├─ Makefile
└─ README.md               # ← this file
```

---

## Step 1 — Install & verify Claude Code

```bash
# (Example) If installed via npm:
npm i -g @anthropic-ai/claude-code

# Verify
claude --version
# or
claude code --version

# Check agents subcommand (names may differ)
claude agents --help
```

If the **`agents`** (or similar) subcommand is not available, update Claude Code or consult its docs/changelog for the **custom subagent** feature.

---

## Step 2 — Create a vulnerable demo repo

```bash
mkdir security-auditor-demo && cd security-auditor-demo
git init

python - <<'PY'
import sqlite3

def login(username, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    # ❌ Vulnerable: SQL injection
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    cursor.execute(query)
    res = cursor.fetchone()
    conn.close()
    return bool(res)
PY
```

Save that as `src/vulnerable.py`.

Commit:

```bash
git add src/vulnerable.py
git commit -m "feat: add vulnerable login example"
```

---

## Step 3 — Define the `security-auditor` subagent

### 3.1 System prompt (high-signal, role-aligned)

Create: `audit/prompts/security-auditor.system.md`

```md
You are **Security Auditor AI**. Your job is to perform **deep, actionable security reviews** of source code and config.

### Scope
- Find and explain vulnerabilities (OWASP Top 10 and beyond).
- Assign **severity** (critical, high, medium, low).
- Provide **line/file locations**, **exploit narratives**, and **clear remediations** with secure code examples.
- Flag **hard-coded secrets**, **crypto misuse**, **weak auth**, **CORS misconfig**, **deserialization bugs**, **RCE**, **path traversal**, etc.

### Output
- Return a **Markdown report** + **JSON block** named `SECURITY_AUDIT_JSON` summarizing findings.
- If **no issues**, say so explicitly.

### Rules
- **No hand-waving**. Be specific: show the vulnerable line(s).
- If a tool is needed (e.g., grep, ripgrep) but blocked, **ask for it**.
- Prefer **parameterized queries**, **prepared statements**, **proper input validation**, **principle of least privilege**, **encrypted storage**, **secure defaults**.
- If you’re uncertain, mark it as **needs human validation**.
```

### 3.2 (Optional) Pattern/rule file

`audit/rules/patterns.yaml` (simple starter example — adapt to your stack):

```yaml
patterns:
  - id: sql-injection-string-format
    lang: python
    regex: "cursor\.execute\(f?\".*\{.*\}\".*\)"
    severity: high
    description: "Interpolated user input in raw SQL string (possible SQLi)"
  - id: hardcoded-aws-key
    regex: "AKIA[0-9A-Z]{16}"
    severity: critical
    description: "Possible hardcoded AWS access key"
```

> Tip: You can wire this into the subagent so it **first runs fast pattern scanning**, then performs **deeper reasoning**.

### 3.3 Agent definition JSON

Create `.claude/agents/security-auditor.agent.json`:

```json
{
  "name": "security-auditor",
  "description": "Performs OWASP-style secure code reviews, outputs structured findings with severities and remediations.",
  "system_prompt_file": "audit/prompts/security-auditor.system.md",
  "tools": {
    "allow_shell": false,
    "allow_network": false,
    "allow_code_execution": true,
    "extra": []
  },
  "context": {
    "include": ["src/**/*", "requirements.txt", "pyproject.toml"],
    "exclude": ["**/node_modules/**", "**/.git/**"]
  },
  "output": {
    "format": ["markdown", "json"],
    "json_block_label": "SECURITY_AUDIT_JSON"
  },
  "limits": {
    "max_tokens": 100000
  }
}
```

> **Adjust keys to match the real Claude Code schema.** Run `claude agents create --help` to see the exact shape your version expects.

### 3.4 Register the agent

Examples (adapt to your CLI):

```bash
# Option A: direct create
claude agents create   --file .claude/agents/security-auditor.agent.json

# Option B: link / sync (keeps file as source of truth)
claude agents link .claude/agents/security-auditor.agent.json
```

Verify:

```bash
claude agents list
# should show `security-auditor`
```

---

## Step 4 — Run the agent on your codebase

```bash
# Ask the subagent explicitly:
claude agent run security-auditor   --path src   --out audit/report.md   --json-out audit/report.json
```

Example (expected) output snippet (markdown):

```markdown
## Security Audit Report

**Summary**
- Critical: 0
- High: 1
- Medium: 0
- Low: 0

---

### [HIGH] SQL Injection in `src/vulnerable.py:6`

**Why**
`cursor.execute` builds a SQL query with f-string interpolation of user inputs.

**Exploit sketch**
`username = "admin' OR 1=1 --"` bypasses auth.

**Fix**
Use parameterized queries:

```python
query = "SELECT * FROM users WHERE username = ? AND password = ?"
cursor.execute(query, (username, password))
```

---

```json
SECURITY_AUDIT_JSON
{
  "summary": {"critical":0, "high":1, "medium":0, "low":0},
  "findings": [{
    "severity":"high",
    "type":"sql_injection",
    "file":"src/vulnerable.py",
    "line":6,
    "description":"SQL query built via f-string, vulnerable to SQLi",
    "remediation":"Use parameterized queries with placeholders"
  }]
}
```

---

## Step 5 — Wire it into your workflow (git hooks, CI)

### 5.1 Git pre-commit hook

`scripts/install_git_hook.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

HOOK=".git/hooks/pre-commit"

cat > "$HOOK" <<'EOF'
#!/usr/bin/env bash
set -e

echo "[pre-commit] Running security-auditor..."

TMP_MD=$(mktemp)
TMP_JSON=$(mktemp)

claude agent run security-auditor   --path src   --out "$TMP_MD"   --json-out "$TMP_JSON"

CRITICALS=$(jq '.summary.critical' "$TMP_JSON")
HIGHS=$(jq '.summary.high' "$TMP_JSON")

if [ "$CRITICALS" -gt 0 ] || [ "$HIGHS" -gt 0 ]; then
  echo "❌ Security audit failed:"
  cat "$TMP_MD"
  exit 1
fi

echo "✅ Security audit passed."
EOF

chmod +x "$HOOK"
echo "✅ Pre-commit hook installed."
```

Install it:

```bash
bash scripts/install_git_hook.sh
```

Try committing insecure code — the hook should **block** it with a detailed report.

### 5.2 CI (GitHub Actions example)

`.github/workflows/security-audit.yml`:

```yaml
name: Security Audit

on:
  pull_request:
    branches: [ main ]

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Environment
        run: |
          npm i -g @anthropic-ai/claude-code
          claude --version

      - name: Run security-auditor
        run: |
          claude agent run security-auditor             --path src             --out audit/report.md             --json-out audit/report.json

      - name: Fail on high/critical
        run: |
          criticals=$(jq '.summary.critical' audit/report.json)
          highs=$(jq '.summary.high' audit/report.json)
          if [ "$criticals" -gt 0 ] || [ "$highs" -gt 0 ]; then
            echo "High/Critical issues found. See audit/report.md"
            exit 1
          fi
```

---

## Step 6 — Hardening, evaluation & continuous improvement

### 6.1 Seeded vuln evaluation

Create `scripts/eval_seeded_vulns.py`:

```python
import json, glob

EXPECTED = {
  "sql_injection": 1,  # how many we planted
  "hardcoded_secret": 0
}

def main():
    found = {}
    for path in glob.glob("audit/*.json"):
        data = json.load(open(path))
        for f in data.get("findings", []):
            t = f.get("type")
            found[t] = found.get(t, 0) + 1

    print("Expected:", EXPECTED)
    print("Found   :", found)

    # crude score
    tp = sum(min(found.get(k,0), v) for k,v in EXPECTED.items())
    fn = sum(max(v - found.get(k,0), 0) for k,v in EXPECTED.items())
    print(f"TP={tp}, FN={fn}")

if __name__ == "__main__":
    main()
```

Automate in **CI** to track your agent’s **recall** on a known corpus. Add more real-world vuln fixtures over time.

### 6.2 Tighten the prompt & permissions

If the agent:
- **Misses patterns** → enrich the **prompt** with explicit rules & examples.
- **Over-reports / hallucinates** → require **evidence** (files/lines) and mark unknowns as “needs human validation”.
- **Fails to run commands** → explicitly list allowed tools or **disable** tool use entirely and feed it pre-extracted context.

---

## Going further — Multi-subagent swarms

Split responsibilities:

| Subagent           | Purpose                                              |
|--------------------|------------------------------------------------------|
| `security-auditor` | Code vulns, OWASP Top 10, structured remediation     |
| `secrets-hunter`   | Hardcoded creds, token regexes, dotenv leaks         |
| `license-checker`  | License compliance, GPL contamination, attribution   |
| `sbom-auditor`     | Dependency CVEs, SBOM synthesis, upgrade guidance    |
| `config-sentinel`  | YAML/TOML/INI/Helm misconfigurations, SSRF, CORS     |

Orchestrate with:
- **Makefile** targets (simple)
- A **controller script** that runs agents in stages and merges reports
- **Graph frameworks** (e.g., LangGraph) if you need complex inter-agent state machines

---

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---|---|---|
| `claude agents create` not found | CLI version mismatch | Upgrade Claude Code, or use the equivalent command your version supports |
| Agent “forgets” constraints | Prompt too weak / context polluted | Strengthen the system prompt, reduce included context, enforce stricter output schema |
| Command recognition flaky | Tool schema unclear to agent | Add explicit CLI wrappers (shell scripts) and call them deterministically |
| Reports are too verbose | Missing output contract | Enforce the `SECURITY_AUDIT_JSON` block and a fixed Markdown template |
| False positives galore | Over-aggressive heuristics | Add explicit pattern allow-lists, severity downgrades, or ask for human confirmation |

---

## FAQ

**Q: Can I make the agent auto-fix code?**  
Yes—add a **patch generation step** (e.g., `--apply-fixes` flag that writes diffs to a branch) and require a human to approve PRs.

**Q: How do I prevent leaking secrets to the model?**  
- Run locally with **no network tools**.
- Redact sensitive chunks pre-prompt, or run a local pattern scan first and only feed minimal context.

**Q: Can I chain multiple agents with dependencies?**  
Yes. Run `secrets-hunter` first, then `security-auditor`, etc., and pass outputs as inputs. A graph/orchestrator helps for complex flows.

---

## License

MIT — see [LICENSE](./LICENSE) (add one if you plan to open source).

---

### Changelog

- **2025-07-25**: Initial release of this tutorial for Claude Code v1.0.60 subagents.
