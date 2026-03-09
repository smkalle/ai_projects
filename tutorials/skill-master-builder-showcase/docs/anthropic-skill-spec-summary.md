# The Complete Guide to Building Skills for Claude — Summary

> **Source:** Anthropic, *The Complete Guide to Building Skills for Claude* (January 2026)
> **PDF:** [resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf)
>
> This document summarizes the official Anthropic specification that `skill-master-builder` automates.
> Every skill produced by this tool is designed to comply with this spec by default.

---

## What is a Skill?

A skill is a set of instructions — packaged as a simple folder — that teaches Claude how to handle specific tasks or workflows. Instead of re-explaining preferences, processes, and domain expertise in every conversation, skills let you teach Claude once and benefit every time.

Skills work well with Claude's built-in capabilities (code execution, document creation) and with MCP integrations, where they turn raw tool access into reliable, optimized workflows.

---

## Core Design Principles

### Progressive Disclosure

Skills use a three-level loading system to minimize token usage while maintaining specialized expertise:

| Level | Content | When Loaded |
|-------|---------|-------------|
| **1st** | YAML frontmatter (`name` + `description`) | Always — in Claude's system prompt |
| **2nd** | SKILL.md body | When Claude determines the skill is relevant |
| **3rd** | Linked files (`references/`, `scripts/`, `assets/`) | On demand, as needed |

### Composability

Claude can load multiple skills simultaneously. Skills should work well alongside others and never assume they are the only capability available.

### Portability

Skills work identically across Claude.ai, Claude Code, and the API. Create once, use everywhere — provided the environment supports any dependencies the skill requires.

---

## Skill Categories

Anthropic identifies three common use case categories:

### Category 1: Document & Asset Creation

Creating consistent, high-quality output — documents, presentations, apps, designs, code.

**Key techniques:** Embedded style guides, template structures, quality checklists. No external tools required.

### Category 2: Workflow Automation

Multi-step processes that benefit from consistent methodology, including coordination across multiple MCP servers.

**Key techniques:** Step-by-step workflows with validation gates, templates for common structures, iterative refinement loops.

### Category 3: MCP Enhancement

Workflow guidance that enhances the tool access an MCP server provides.

**Key techniques:** Coordinating multiple MCP calls in sequence, embedding domain expertise, providing context users would otherwise need to specify, error handling for common MCP issues.

---

## Technical Requirements

### File Structure

```
your-skill-name/
├── SKILL.md               # Required — main skill file
├── scripts/               # Optional — executable code (Python, Bash)
├── references/            # Optional — documentation loaded as needed
└── assets/                # Optional — templates, fonts, icons
```

### Critical Naming Rules

- **SKILL.md:** Must be exactly `SKILL.md` (case-sensitive). No variations (`SKILL.MD`, `skill.md`).
- **Folder name:** kebab-case only (`notion-project-setup`). No spaces, underscores, or capitals.
- **No README.md** inside the skill folder — all documentation goes in SKILL.md or `references/`.
- Skill `name` field must match the folder name.

### YAML Frontmatter

The frontmatter is how Claude decides whether to load your skill.

**Required fields:**

```yaml
---
name: your-skill-name
description: What it does. Use when user asks to [specific phrases].
---
```

**Optional fields:**

| Field | Max Length | Purpose |
|-------|-----------|---------|
| `license` | — | SPDX identifier (MIT, Apache-2.0) |
| `compatibility` | 500 chars | Environment requirements |
| `allowed-tools` | — | Restrict tool access (e.g., `"Bash(python:*) WebFetch"`) |
| `metadata` | — | Custom key-value pairs (author, version, mcp-server, etc.) |

**Security restrictions:**
- No XML angle brackets (`< >`) — frontmatter appears in Claude's system prompt
- No skill names starting with "claude" or "anthropic" (reserved)

### The Description Field

The most important part of a skill. Structure: `[What it does] + [When to use it] + [Key capabilities]`

**Good descriptions** include 4–6 specific trigger phrases users would actually say, mention relevant file types, and stay under 1024 characters.

**Bad descriptions** are vague ("Helps with projects"), lack trigger conditions, or are too technical without user-facing language.

---

## Writing Effective Instructions

- **Be specific and actionable** — never "validate the data"; instead, show the exact command and expected output.
- **Put critical instructions at the top** — use `CRITICAL:` prefix for must-not-skip steps.
- **Reference bundled resources clearly** — `"Before writing queries, consult references/api-patterns.md"`.
- **Use progressive disclosure** — keep SKILL.md focused on core instructions; move detailed docs to `references/`.
- **Prefer scripts over language for critical validations** — code is deterministic; language interpretation isn't.
- **Add Performance Notes** for quality-critical skills — `"Take your time to do this thoroughly"`.

---

## Testing

Anthropic recommends three levels of testing rigor:

1. **Manual testing in Claude.ai** — run queries directly, fast iteration.
2. **Scripted testing in Claude Code** — automate test cases for repeatable validation.
3. **Programmatic testing via skills API** — systematic evaluation suites.

### Recommended Test Areas

**1. Triggering tests** — Ensure the skill loads at the right times:
- Triggers on obvious tasks
- Triggers on paraphrased requests
- Does NOT trigger on unrelated topics

**2. Functional tests** — Verify correct outputs:
- Valid outputs generated
- API calls succeed
- Error handling works
- Edge cases covered

**3. Performance comparison** — Prove the skill improves results vs. baseline (fewer messages, fewer errors, lower token consumption).

### Success Criteria (Aspirational Benchmarks)

- Skill triggers on ~90% of relevant queries
- Workflows complete in target number of tool calls
- 0 failed API calls per workflow
- Users don't need to prompt Claude about next steps
- Consistent results across sessions

---

## Five Workflow Patterns

These patterns emerged from skills created by early adopters and internal Anthropic teams.

### Pattern 1: Sequential Workflow Orchestration

**Use when:** Multi-step processes in a specific order.
**Key techniques:** Explicit step ordering, dependencies between steps, validation at each stage, rollback instructions for failures.

### Pattern 2: Multi-MCP Coordination

**Use when:** Workflows span multiple services (e.g., Figma + Drive + Linear + Slack).
**Key techniques:** Clear phase separation, data passing between MCPs, validation before moving to next phase, centralized error handling.

### Pattern 3: Iterative Refinement

**Use when:** Output quality improves with iteration (e.g., report generation).
**Key techniques:** Explicit quality criteria, validation scripts, know when to stop iterating.

### Pattern 4: Context-Aware Tool Selection

**Use when:** Same outcome, different tools depending on context (e.g., file storage routing).
**Key techniques:** Clear decision criteria, fallback options, transparency about choices.

### Pattern 5: Domain-Specific Intelligence

**Use when:** Your skill adds specialized knowledge beyond tool access (e.g., compliance checks).
**Key techniques:** Domain expertise embedded in logic, compliance before action, comprehensive audit trails.

---

## Distribution

### Current Model (January 2026)

**Individual users:**
1. Download the skill folder
2. Zip the folder
3. Upload to Claude.ai via Settings > Capabilities > Skills
4. Or place in Claude Code skills directory

**Organizations:** Admins can deploy skills workspace-wide with automatic updates and centralized management (shipped December 2025).

**API:** Skills can be used programmatically via the `/v1/skills` endpoint and `container.skills` parameter in the Messages API. Requires Code Execution Tool beta.

### Open Standard

Anthropic published Agent Skills as an open standard. Like MCP, skills are designed to be portable across tools and platforms.

---

## Troubleshooting Quick Reference

| Problem | Cause | Fix |
|---------|-------|-----|
| "Could not find SKILL.md" | Wrong filename case | Rename to exactly `SKILL.md` |
| "Invalid frontmatter" | Missing `---` delimiters or YAML error | Add proper delimiters, fix YAML |
| "Invalid skill name" | Spaces or capitals in name | Use kebab-case |
| Skill never triggers | Description too vague | Add specific trigger phrases |
| Skill triggers too often | Description too broad | Add negative triggers, narrow scope |
| MCP calls fail | Server not connected or wrong tool names | Test MCP independently first |
| Instructions not followed | Too verbose or buried | Put critical items at top, use scripts |
| Slow/degraded responses | Skill too large | Move detail to `references/`, keep SKILL.md under 5,000 words |

---

## Quick Checklist (from Appendix A)

**Before you start:**
- [ ] 2–3 concrete use cases identified
- [ ] Tools identified (built-in or MCP)
- [ ] Folder structure planned

**During development:**
- [ ] Folder named in kebab-case
- [ ] `SKILL.md` exists (exact spelling)
- [ ] YAML frontmatter with `---` delimiters
- [ ] `name`: kebab-case, no spaces, no capitals
- [ ] `description`: includes WHAT and WHEN
- [ ] No XML tags (`< >`) anywhere
- [ ] Instructions clear and actionable
- [ ] Error handling included
- [ ] Examples provided
- [ ] References clearly linked

**Before upload:**
- [ ] Tested triggering (obvious + paraphrased)
- [ ] Verified no false triggers on unrelated topics
- [ ] Functional tests pass
- [ ] Compressed as .zip

**After upload:**
- [ ] Test in real conversations
- [ ] Monitor for under/over-triggering
- [ ] Iterate on description and instructions
