# Anthropic Skill Recipe — Complete Reference

Distilled from **"The Complete Guide to Building Skills for Claude"** (Anthropic, 2026).
Use this as the authoritative source of truth when writing any SKILL.md.

> **Source:** [The Complete Guide to Building Skills for Claude (PDF)](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf)
> skill-master-builder automates and systematizes the best practices from this guide —
> enforcing the recipe at every phase so every built skill is compliant by default.

---

## Table of Contents
1. [What is a Skill](#what-is-a-skill)
2. [Folder Structure Rules](#folder-structure-rules)
3. [YAML Frontmatter Spec](#yaml-frontmatter-spec)
4. [Progressive Disclosure System](#progressive-disclosure-system)
5. [Writing Effective Instructions](#writing-effective-instructions)
6. [Description Field Guide](#description-field-guide)
7. [Common Mistakes](#common-mistakes)
8. [Security Rules](#security-rules)

---

## What is a Skill

A skill is a folder containing instructions that teach Claude how to handle a specific task or workflow. Skills eliminate the need to re-explain preferences, processes, and domain expertise in every conversation.

**Skill components:**
- `SKILL.md` (required) — instructions in Markdown with YAML frontmatter
- `scripts/` (optional) — executable Python or Bash code
- `references/` (optional) — documentation loaded as needed
- `assets/` (optional) — templates, fonts, icons used in output

**Three design principles:**
1. **Progressive Disclosure** — load content in 3 layers (see below)
2. **Composability** — skills work alongside other skills; never assume yours is the only one
3. **Portability** — works identically on Claude.ai, Claude Code, and API

---

## Folder Structure Rules

```
your-skill-name/           ← kebab-case, lowercase only
├── SKILL.md               ← MUST be exactly this name (case-sensitive)
├── scripts/               ← optional
│   ├── process_data.py
│   └── validate.sh
├── references/            ← optional
│   ├── api-guide.md
│   └── examples/
└── assets/                ← optional
    └── report-template.md
```

**Critical naming rules:**
- Folder: `kebab-case` only — `notion-project-setup` ✅ | `Notion Project Setup` ❌ | `notion_project_setup` ❌
- File: must be `SKILL.md` — `SKILL.MD` ❌ | `skill.md` ❌ | `Skill.md` ❌
- NO `README.md` inside skill folder — all docs go in `SKILL.md` or `references/`
- Skill `name` must match folder name

---

## YAML Frontmatter Spec

### Minimal required format
```yaml
---
name: your-skill-name
description: What it does and when to use it.
---
```

### Full format with all optional fields
```yaml
---
name: your-skill-name                          # required, kebab-case
description: What it does and when to trigger. # required, <1024 chars, no XML
license: MIT                                   # optional: MIT, Apache-2.0, etc.
compatibility: Claude.ai, Claude Code          # optional, <500 chars
allowed-tools: "Bash(python:*) WebFetch"       # optional: restrict tool access
metadata:                                      # optional: any key-value pairs
  author: Your Name
  version: 1.0.0
  mcp-server: your-server-name
  category: workflow-automation
  tags: [automation, project-management]
  documentation: https://example.com/docs
  support: support@example.com
---
```

### Field validation rules

| Field | Required | Max length | Rules |
|-------|----------|------------|-------|
| `name` | YES | 64 chars | kebab-case, `[a-z0-9-]+`, no leading/trailing/double hyphens |
| `description` | YES | 1024 chars | Must include WHAT and WHEN; no XML (`< >`) |
| `license` | no | — | SPDX identifier |
| `compatibility` | no | 500 chars | Plain text only |
| `allowed-tools` | no | — | Space-separated tool specs |
| `metadata` | no | — | Any YAML key-value pairs |

---

## Progressive Disclosure System

Skills use a three-level loading system to minimize token usage:

| Level | Content | When loaded | Size target |
|-------|---------|-------------|-------------|
| 1 | YAML frontmatter (`name` + `description`) | Always — in every system prompt | ~100 words |
| 2 | `SKILL.md` body | When Claude determines skill is relevant | <500 lines |
| 3 | Bundled files (`scripts/`, `references/`, `assets/`) | Only as needed, on demand | Unlimited |

**Implications for writing:**
- Description must be self-sufficient for Claude to decide when to load the skill
- SKILL.md body should focus on core workflow; push detail to `references/`
- Reference linked files explicitly: "See `references/api-patterns.md` for rate limits"
- Large reference files (>300 lines) need a table of contents

---

## Writing Effective Instructions

### Be specific and actionable

✅ Good:
```
Run `python scripts/validate.py --input {filename}` to check data format.
If validation fails, common issues:
- Missing required fields → add them to the CSV
- Invalid date formats → use YYYY-MM-DD
```

❌ Bad:
```
Validate the data before proceeding.
```

### Include error handling
```markdown
## Common Issues

### MCP Connection Failed
If you see "Connection refused":
1. Verify MCP server is running: Settings > Extensions
2. Confirm API key is valid and not expired
3. Reconnect: Settings > Extensions > [Service] > Reconnect
```

### Use progressive disclosure for detail
Keep SKILL.md focused on workflow. Move:
- API reference → `references/api-guide.md`
- Examples → `references/examples/`
- Large schemas → `references/schemas.md`

### Add performance notes for quality-critical skills
```markdown
## Performance Notes
- Take time to do this thoroughly; quality matters more than speed
- Do not skip validation steps
- Review output before finalizing
```

### Prefer scripts over language for critical validations
Code is deterministic; language instructions are interpreted. For must-not-fail checks, write a validation script.

---

## Description Field Guide

The description is the **most important part** of a skill. It's how Claude decides whether to load your skill. Get this wrong and the skill never fires.

### Structure
```
[What it does] + [When to use it — trigger phrases] + [Key capabilities]
```

### Good examples

```
# Good — specific, includes trigger phrases, clear value
description: Analyzes Figma design files and generates developer handoff docs. 
Use when user uploads .fig files, asks for "design specs", "component docs", 
or "design-to-code handoff". Produces annotated specs with asset manifest.
```

```
# Good — outcome-oriented, real trigger phrases
description: End-to-end customer onboarding for PayFlow. Handles account creation, 
payment setup, and subscription management. Use when user says "onboard new customer", 
"set up subscription", or "create PayFlow account". Requires PayFlow MCP connected.
```

### Bad examples

```
# Too vague — no triggers, no specifics
description: Helps with projects.

# Missing triggers — tells Claude what but not when
description: Creates sophisticated multi-page documentation systems.

# Too technical — no user-facing trigger phrases
description: Implements Project entity model with hierarchical relationships.
```

### Anti-undertriggering
Claude tends to undertrigger skills. Make descriptions slightly "pushy":

Instead of:
> "Use for data visualization tasks."

Write:
> "Use whenever the user mentions dashboards, charts, data visualization, metrics, 
> or wants to display any kind of data — even if they don't say 'visualization' explicitly."

---

## Common Mistakes

| Mistake | Symptom | Fix |
|---------|---------|-----|
| `SKILL.MD` (wrong case) | Upload error: "Could not find SKILL.md" | Rename to exactly `SKILL.md` |
| Missing `---` delimiters | Upload error: "Invalid frontmatter" | Add `---` before and after YAML block |
| Unclosed quotes in YAML | Parse error | Use `|` for multiline or escape quotes |
| Spaces in skill name | Upload error: "Invalid skill name" | Use `kebab-case` only |
| No trigger phrases in description | Skill never fires | Add 4–6 real user phrases to description |
| Description too vague | Undertriggering | Add specific tasks, file types, domain terms |
| Description too broad | Overtriggering | Add negative triggers, narrow scope |
| Instructions too verbose | Instructions ignored | Use bullets, keep SKILL.md under 500 lines |
| Critical instructions buried | Missed steps | Put critical items at top with `CRITICAL:` prefix |
| Skill name has "claude" or "anthropic" | Rejected | Reserved prefixes — choose another name |

---

## Security Rules

**Forbidden in frontmatter:**
- XML angle brackets `< >` — security restriction, injected into system prompt
- Skill names containing "claude" or "anthropic" — reserved by Anthropic

**Safe YAML parsing** is used — no code execution possible in frontmatter. Stick to standard YAML types (strings, numbers, booleans, lists, objects).
