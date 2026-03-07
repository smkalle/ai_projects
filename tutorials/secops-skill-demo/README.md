# SecOps Skill for Claude Code

An open-source Claude Code skill for AI-assisted security operations — vulnerability discovery, code auditing, and secure development practices.

Inspired by [Anthropic's collaboration with Mozilla](https://www.anthropic.com/news/mozilla-firefox-security) where Claude discovered **22 vulnerabilities (14 high-severity)** in Firefox by scanning ~6,000 C++ files in two weeks.

## What Is a Claude Code Skill?

A **skill** is a reusable prompt module that extends Claude Code with domain expertise. When you type `/secops` in Claude Code, it loads the SecOps skill — giving Claude structured methodology for security auditing, vulnerability classification, and patch generation.

Skills are just Markdown files with frontmatter. No plugins, no compilation, no API keys required.

## Quick Start

### 1. Install the skill

```bash
# Copy the skill into your Claude Code skills directory
cp -r skill/secops ~/.claude/skills/secops
```

Or symlink it:
```bash
ln -s "$(pwd)/skill/secops" ~/.claude/skills/secops
```

### 2. Use it

Open Claude Code in any project and run:

```
/secops scan src/
```

Claude will read your source files, analyze them for vulnerabilities, and produce a structured report with CWE classifications, severity ratings, reproducers, and candidate patches.

### 3. Try the demo

```bash
# Run Claude Code in this directory to audit the sample vulnerable code
cd tutorials/secops-skill-demo
claude

# Then type:
/secops scan samples/vulnerable/
```

## Commands

| Command | Description |
|---------|-------------|
| `/secops scan <path>` | Scan files for vulnerabilities |
| `/secops audit --class <category> <path>` | Focus on one vulnerability class |
| `/secops report <path>` | Generate a full security report |
| `/secops review` | Review staged git changes for security issues |
| `/secops deps` | Audit dependencies for known CVEs |

### Vulnerability Classes

Use with `--class`:
- `memory-safety` — UAF, double-free, buffer overflow, dangling pointers
- `injection` — SQLi, command injection, XSS, template injection
- `auth` — broken access control, privilege escalation
- `crypto` — weak algorithms, hardcoded secrets, key management
- `concurrency` — race conditions, TOCTOU, deadlocks
- `input-validation` — bounds checks, integer overflow, format strings

## How It Works

The skill follows the **Task Verifier Pattern** from the Mozilla audit:

```
1. SCOPE    → Identify target files and attack surface
2. SCAN     → Read and analyze code for vulnerability patterns
3. VERIFY   → Confirm findings aren't false positives
4. REPORT   → Classify by CWE, severity, and impact
5. PATCH    → Propose minimal, correct fixes
6. VALIDATE → Confirm patches resolve issues without regressions
```

### Output Format

Each finding includes:

```markdown
### Finding 1: SQL Injection in login()

- **Severity:** Critical
- **CWE:** CWE-89 Improper Neutralization of Special Elements in SQL
- **Location:** `app.py:42`
- **Description:** User input interpolated directly into SQL query
- **Reproducer:** `username = "' OR '1'='1' --"`
- **Fix:** Use parameterized queries with `cursor.execute("SELECT ... WHERE username = ?", (username,))`
- **Impact:** Authentication bypass, data exfiltration
```

## Project Structure

```
secops-skill-demo/
├── skill/
│   └── secops/
│       └── SKILL.md            # The skill file (copy to ~/.claude/skills/)
├── samples/
│   ├── vulnerable/             # Intentionally vulnerable code for testing
│   │   ├── web_app.py          # Flask app with OWASP Top 10 vulns
│   │   ├── auth_service.py     # Broken authentication patterns
│   │   ├── data_handler.py     # Injection and deserialization flaws
│   │   ├── file_server.py      # Path traversal and SSRF
│   │   └── crypto_utils.py     # Weak cryptography examples
│   └── secure/                 # Fixed versions showing remediation
│       ├── web_app.py
│       ├── auth_service.py
│       ├── data_handler.py
│       ├── file_server.py
│       └── crypto_utils.py
├── reports/
│   └── sample_report.md        # Example audit output
├── scripts/
│   └── run_audit.sh            # Helper to run audit via CLI
├── GUIDE.md                    # Detailed how-to guide
└── README.md                   # This file
```

## Sample Audit Results

Running `/secops scan samples/vulnerable/` on the included samples produces:

| Severity | Count | Examples |
|----------|-------|---------|
| Critical | 4 | SQL injection, command injection, pickle deserialization, hardcoded secrets |
| High | 5 | Path traversal, eval(), weak CORS, missing auth, broken session mgmt |
| Medium | 4 | MD5 hashing, verbose errors, debug mode, missing rate limits |
| Low | 2 | Missing security headers, broad exception handling |

See `reports/sample_report.md` for the full output.

## Writing Your Own Skills

A skill is a directory containing `SKILL.md` with YAML frontmatter:

```yaml
---
name: my-skill
version: 1.0.0
description: "What it does in one line."
---

# My Skill

Instructions for Claude when this skill is invoked...
```

Place it in `~/.claude/skills/my-skill/SKILL.md` and it becomes available as `/my-skill` in Claude Code.

### Tips for Effective Skills

1. **Be specific** — Give Claude clear steps, not vague guidance
2. **Include output formats** — Show exactly what the output should look like
3. **Use checklists** — Structured lists prevent Claude from skipping steps
4. **Add examples** — Concrete examples beat abstract descriptions
5. **Define scope** — Tell Claude what NOT to do as well as what to do

## Responsible Disclosure

This skill follows coordinated vulnerability disclosure principles:

- Report findings to maintainers before public disclosure
- Allow reasonable remediation time (typically 90 days)
- Provide actionable information: reproducer, patch, impact
- Do not develop weaponized exploits beyond proof-of-concept
- Follow your organization's security policies

## Contributing

1. Fork this repository
2. Add new vulnerability samples to `samples/vulnerable/`
3. Add corresponding fixes to `samples/secure/`
4. Update the sample report
5. Submit a pull request

## License

MIT

---

Built for [Claude Code](https://claude.com/claude-code). Inspired by [Anthropic x Mozilla Firefox Security Audit](https://www.anthropic.com/news/mozilla-firefox-security).
