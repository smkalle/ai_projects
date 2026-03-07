# SecOps Skill — How-To Guide

A step-by-step guide to installing, using, and extending the SecOps skill for Claude Code.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Your First Scan](#your-first-scan)
4. [Understanding the Output](#understanding-the-output)
5. [Scan Modes](#scan-modes)
6. [Real-World Workflow](#real-world-workflow)
7. [Customizing the Skill](#customizing-the-skill)
8. [CI/CD Integration](#cicd-integration)
9. [Methodology Deep Dive](#methodology-deep-dive)
10. [Troubleshooting](#troubleshooting)

---

## Prerequisites

- [Claude Code CLI](https://claude.com/claude-code) v1.0.60+
- A codebase to audit (or use the included samples)

```bash
# Verify Claude Code is installed
claude --version
```

---

## Installation

### Option A: Copy the skill

```bash
cp -r skill/secops ~/.claude/skills/secops
```

### Option B: Symlink (for development)

```bash
ln -s "$(pwd)/skill/secops" ~/.claude/skills/secops
```

### Option C: One-liner from this repo

```bash
mkdir -p ~/.claude/skills && \
cp -r tutorials/secops-skill-demo/skill/secops ~/.claude/skills/
```

Verify installation:

```bash
ls ~/.claude/skills/secops/SKILL.md
```

---

## Your First Scan

### Step 1: Open Claude Code in a project

```bash
cd your-project
claude
```

### Step 2: Run a scan

```
/secops scan src/
```

Claude will:
1. Read all source files in `src/`
2. Analyze each for vulnerability patterns
3. Verify findings aren't false positives
4. Produce a structured report

### Step 3: Review the output

Each finding includes severity, CWE ID, location, description, reproducer, and fix.

### Example Session

```
You: /secops scan samples/vulnerable/web_app.py

Claude: ## Security Audit Report

**Target:** samples/vulnerable/web_app.py
**Findings:** 6 (Critical: 2, High: 2, Medium: 1, Low: 1)

### Finding 1: SQL Injection in user_login()
- **Severity:** Critical
- **CWE:** CWE-89
- **Location:** `web_app.py:28`
...
```

---

## Understanding the Output

### Severity Levels

| Level | Meaning | Action |
|-------|---------|--------|
| **Critical** | Exploitable with high impact (RCE, auth bypass, data breach) | Fix immediately |
| **High** | Exploitable or high impact, one of the two | Fix within days |
| **Medium** | Requires specific conditions to exploit | Fix within sprint |
| **Low** | Minor risk or defense-in-depth | Fix when convenient |
| **Info** | Best practice recommendation | Consider adopting |

### CWE Classifications

Each finding maps to a [Common Weakness Enumeration](https://cwe.mitre.org/) ID:

| CWE | Name | Example |
|-----|------|---------|
| CWE-78 | OS Command Injection | `os.system(user_input)` |
| CWE-89 | SQL Injection | `f"SELECT * WHERE id = '{user_id}'"` |
| CWE-79 | Cross-Site Scripting | `innerHTML = user_input` |
| CWE-22 | Path Traversal | `open(os.path.join(base, user_filename))` |
| CWE-502 | Deserialization of Untrusted Data | `pickle.loads(request.data)` |
| CWE-798 | Hardcoded Credentials | `API_KEY = "sk-live-..."` |
| CWE-327 | Use of Broken Crypto | `hashlib.md5(password)` |
| CWE-306 | Missing Authentication | Routes without `@login_required` |
| CWE-942 | CORS Misconfiguration | `Access-Control-Allow-Origin: *` |
| CWE-416 | Use After Free | Dangling pointer access (C/C++) |

---

## Scan Modes

### Full scan — all vulnerability classes

```
/secops scan src/
```

### Focused scan — single vulnerability class

```
/secops audit --class injection src/
/secops audit --class auth src/
/secops audit --class crypto src/
```

### PR review — check only changed files

```
/secops review
```

This checks staged and unstaged git changes against the secure code review checklist.

### Dependency audit

```
/secops deps
```

Checks `requirements.txt`, `package.json`, `pyproject.toml`, etc. for known vulnerable versions.

### Full report — comprehensive output

```
/secops report src/
```

Produces a complete report with executive summary, findings table, remediation priorities, and positive observations.

---

## Real-World Workflow

### Scenario: Auditing a FastAPI application

```
# 1. Scan the entire app
/secops scan src/

# 2. Focus on the most common web vulnerabilities
/secops audit --class injection src/api/
/secops audit --class auth src/middleware/

# 3. Check dependencies
/secops deps

# 4. Review your fixes before committing
/secops review
```

### Scenario: Pre-PR security check

```
# Before opening a PR, review your changes
git add -A
/secops review

# Fix any issues found, then commit
```

### Scenario: Incident response

```
# Scan a specific file flagged in a security alert
/secops scan src/auth/login.py

# Deep dive into the vulnerability class
/secops audit --class auth src/auth/
```

---

## Customizing the Skill

The skill is just a Markdown file. Edit it to fit your needs.

### Add custom rules

Edit `~/.claude/skills/secops/SKILL.md` and add patterns specific to your stack:

```markdown
### Custom Rules for Django

When scanning Django projects, additionally check:
- [ ] `DEBUG = True` not in production settings
- [ ] `ALLOWED_HOSTS` is not `['*']`
- [ ] `SECRET_KEY` is loaded from environment
- [ ] CSRF middleware is enabled
- [ ] `@login_required` on all views handling sensitive data
```

### Adjust severity thresholds

Modify the severity definitions to match your organization's risk tolerance.

### Add language-specific patterns

Add sections for languages your team uses:

```markdown
### Go-Specific Checks
- [ ] No `fmt.Sprintf` in SQL queries
- [ ] `crypto/rand` used instead of `math/rand` for security
- [ ] HTTP handlers check `r.Method` before processing
```

---

## CI/CD Integration

### GitHub Actions

```yaml
name: Security Audit
on: [pull_request]

jobs:
  secops:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install Claude Code
        run: npm i -g @anthropic-ai/claude-code

      - name: Install SecOps skill
        run: |
          mkdir -p ~/.claude/skills
          cp -r .secops-skill/secops ~/.claude/skills/

      - name: Run security audit
        run: |
          claude -p "/secops report src/" > security-report.md
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}

      - name: Upload report
        uses: actions/upload-artifact@v4
        with:
          name: security-report
          path: security-report.md
```

### Git Pre-Commit Hook

```bash
#!/usr/bin/env bash
# .git/hooks/pre-commit
echo "Running SecOps review on staged changes..."
RESULT=$(claude -p "/secops review" 2>&1)

if echo "$RESULT" | grep -qi "critical"; then
    echo "BLOCKED: Critical security issues found."
    echo "$RESULT"
    exit 1
fi

echo "Security check passed."
```

### Shell Script

Use the included helper:

```bash
bash scripts/run_audit.sh /path/to/your/project
```

---

## Methodology Deep Dive

### The Task Verifier Pattern

The core methodology comes from Anthropic's Mozilla audit. The key insight: **Claude works best when it can check its own work.**

```
FIND vulnerability
  → PROPOSE fix
    → VERIFY fix removes the vulnerability
      → VERIFY fix doesn't break functionality
        → REPORT with confidence
```

This loop reduces false positives dramatically. Instead of just pattern-matching (which catches `eval` in comments), the verifier step asks: "Could this actually be exploited? Does the fix actually work?"

### Why Minimal Reproducers Matter

Mozilla valued three things in every report:
1. **Minimal test case** — smallest input that triggers the bug
2. **Proof-of-concept** — demonstration of impact
3. **Candidate patch** — proposed fix

The skill instructs Claude to produce all three. A vulnerability report without a reproducer is just a theory.

### Scoping Strategy

Start narrow, expand outward:
1. **High-impact isolated components** — auth, payment, data access
2. **System boundaries** — where untrusted input enters
3. **Error handling paths** — less tested, more likely to have bugs
4. **Shared utilities** — bugs here affect everything

---

## Troubleshooting

### Skill not appearing

```bash
# Verify the file exists
ls ~/.claude/skills/secops/SKILL.md

# Check file format — must have YAML frontmatter
head -5 ~/.claude/skills/secops/SKILL.md
```

### Too many false positives

The skill may flag educational/demo code as vulnerable. Tell Claude:

```
/secops scan src/ — ignore files in tests/ and examples/
```

### Scan takes too long

For large codebases, scope the scan:

```
# Scan only changed files
/secops review

# Scan one directory at a time
/secops scan src/api/
/secops scan src/auth/
```

### Claude doesn't follow the report format

Re-invoke the skill explicitly:

```
/secops report src/ — use the exact output format from the skill
```

---

## Next Steps

- Read the [skill source](skill/secops/SKILL.md) to understand exactly what Claude is told
- Try it on your own projects
- Customize it for your stack and security policies
- Share improvements back via pull requests
