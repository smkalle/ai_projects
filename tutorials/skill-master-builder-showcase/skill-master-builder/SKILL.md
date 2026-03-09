---
name: skill-master-builder
description: Builds production-ready Claude skills from scratch following the official Anthropic recipe. Use when anyone says "build me a skill", "create a skill for", "I want a skill that", "make a Claude skill", "help me design a skill", or "turn this workflow into a skill". Runs a structured plan-mode interview first, researches the domain, then generates a full skill package (SKILL.md + scripts/ + references/ + assets/) with auto-generated test cases. Always use this skill when the goal is producing a new deployable Claude skill — even if the user just describes a workflow they want automated.
metadata:
  author: skill-master-builder
  version: 1.0.0
  category: workflow-automation
---

# Skill Master Builder

Builds complete, Anthropic-compliant Claude skills from scratch using the official recipe:  
**Plan → Research → Design → Build → Validate → Package**

Before reading anything else: always run the **Plan-Mode Interview** first. Do not write SKILL.md until the interview is complete and confirmed.

---

## Phase 0: Plan-Mode Interview

Run this before writing a single line of skill content. Ask all questions in one go to minimize back-and-forth. Present them as a numbered list so the user can answer all at once.

```
PLAN-MODE INTERVIEW — answer all before we proceed:

1. WHAT: What should this skill help Claude do? (describe the task/workflow in plain language)
2. CATEGORY: Which best fits?
   [A] Document & Asset Creation (reports, decks, docs, designs, code)
   [B] Workflow Automation (multi-step processes, pipelines, coordination)
   [C] MCP Enhancement (adds workflow smarts on top of an MCP server)
3. TRIGGER: When should this skill activate? What would a user say to need it?
   Give 3–5 real example phrases.
4. INPUTS: What does the user provide? (files, text, URLs, project context...)
5. OUTPUT: What should Claude produce? (file type, format, structure)
6. MCP: Does this skill coordinate any external tools or MCP servers? If so, which ones?
7. DOMAIN KNOWLEDGE: What expertise should be baked in?
   (brand guidelines, compliance rules, style conventions, API patterns...)
8. EDGE CASES: What are 2–3 things that could go wrong or need special handling?
9. SUCCESS: How would you know it worked perfectly? Describe the ideal output.
10. SCOPE: Single-step or multi-step workflow?
```

After collecting answers:
- Summarize the plan in a brief **SKILL DESIGN BRIEF** (see `assets/plan-interview-template.md`)
- Ask for confirmation: "Does this match your intent? Any corrections before I build?"
- Only proceed after user confirms

---

## Phase 1: Research & Domain Enrichment

Once the plan is confirmed, research the domain before writing any instructions.

### What to research
- If an MCP server is involved → look up its tool names, parameters, error codes
- If a file format is involved (DOCX, PPTX, PDF) → check relevant skill docs in `/mnt/skills/`
- If a domain has specific standards (legal, finance, compliance, bioinformatics) → surface key rules
- If a workflow pattern exists in `references/patterns-catalog.md` → select the best-fit pattern

### Research outputs
Capture findings in a `references/domain-notes.md` file inside the new skill being built. Include:
- Key concepts users of this skill must know
- API tool names / MCP endpoint names (if applicable)
- Common failure modes and how to handle them
- Example inputs/outputs from research

---

## Phase 2: Skill Architecture Design

Choose the folder structure based on complexity:

**Minimal (Category 1 — no MCP, no scripts):**
```
your-skill-name/
└── SKILL.md
```

**Standard (Category 1–2):**
```
your-skill-name/
├── SKILL.md
└── references/
    └── domain-notes.md
```

**Full (Category 2–3 with MCP, scripts, or templates):**
```
your-skill-name/
├── SKILL.md
├── scripts/
│   └── validate_output.py        # deterministic checks
├── references/
│   ├── domain-notes.md           # from Phase 1 research
│   └── api-patterns.md           # MCP tool call patterns
└── assets/
    └── output-template.md        # template for generated artifacts
```

Decide structure before writing. State it explicitly to the user.

For pattern selection, consult → `references/patterns-catalog.md`

---

## Phase 3: Write SKILL.md

Follow the Anthropic recipe exactly. For full rules see → `references/anthropic-recipe.md`

### Frontmatter template
```yaml
---
name: skill-name-in-kebab-case
description: [What it does] + [When to trigger — include real user phrases] + [Key capabilities]. 
             Be specific. Include 4–6 trigger phrases. Under 1024 chars. No XML brackets.
license: MIT                         # if open source
compatibility: Claude.ai, Claude Code  # optional
metadata:
  author: your-name
  version: 1.0.0
  category: document-creation | workflow-automation | mcp-enhancement
  mcp-server: server-name            # if applicable
---
```

### SKILL.md body structure
```markdown
# [Skill Name]

One-line summary of what this skill does and for whom.

## Prerequisites
List any tools, MCP connections, or files the user needs to have set up.
(Skip if none)

## Step 1: [First Major Action]
Clear, actionable instruction. Use imperative voice.
- Sub-step with specifics
- Expected result: [describe what success looks like here]

## Step 2: [Next Action]
...repeat for each step...

## Examples
### Example 1: [Common scenario title]
**User says:** "..."
**What Claude does:**
1. ...
2. ...
**Result:** [describe output]

## Error Handling
### [Error Name]
**Cause:** why it happens  
**Fix:** how to resolve it

## Quality Checklist
Before finalizing output, verify:
- [ ] [Check 1]
- [ ] [Check 2]
- [ ] [Check 3]
```

### Writing rules (enforce strictly)
- Instructions must be **specific and actionable** — no vague "process the data"
- Put critical instructions **at the top**, not buried
- Use `CRITICAL:` prefix for must-not-skip steps
- Reference bundled files explicitly: "Read `references/api-patterns.md` before calling tools"
- Add `## Performance Notes` with "Take time to do this thoroughly" for quality-critical skills
- Keep SKILL.md under **500 lines** — move detail to `references/`

---

## Phase 4: Build Supporting Files

### Scripts (scripts/)
Write Python or Bash scripts for deterministic checks. Prefer scripts over language instructions for:
- Format validation
- Required field checks
- File structure assertions

Scripts must be self-contained, handle errors gracefully, and print clear pass/fail messages.

### References (references/)
- `domain-notes.md` — captured in Phase 1
- `api-patterns.md` — for MCP tool call conventions
- Any guide over 300 lines should have a **table of contents** at the top

### Assets (assets/)
- Output templates (Markdown, HTML, YAML structures)
- Style guides
- Data schemas

---

## Phase 5: Generate Test Cases

After building the skill, generate a test suite. Save to `evals/trigger-eval.json`.

For each test, use this format (see `references/eval-templates.md` for full schema):

```json
{
  "eval_set": [
    {
      "id": "trigger-001",
      "type": "trigger",
      "query": "Help me set up a new Linear sprint",
      "should_trigger": true,
      "rationale": "Direct use case match"
    },
    {
      "id": "trigger-002",
      "type": "trigger", 
      "query": "What's the weather today?",
      "should_trigger": false,
      "rationale": "Unrelated topic — should not load skill"
    },
    {
      "id": "functional-001",
      "type": "functional",
      "query": "Create a project workspace with 5 tasks for Q4 planning",
      "expected_behavior": "Skill runs Steps 1–4 in sequence, produces task list",
      "assertions": [
        "Output contains at least 5 tasks",
        "Each task has a name and assignee",
        "No API errors reported"
      ]
    }
  ]
}
```

Minimum test set:
- **5 trigger=true** cases (obvious, paraphrased, implicit)
- **3 trigger=false** cases (unrelated, adjacent topics)
- **3 functional** cases (happy path, edge case, error case)

---

## Phase 6: Validate & Package

### Validate
Run validation script before packaging:
```bash
python scripts/validate_skill.py /path/to/your-new-skill
```

Fix all errors before proceeding.

### Compliance checklist
Before delivering, mentally walk through `references/compliance-checklist.md`.
All items must be checked.

### Package
```bash
python scripts/package_skill.py /path/to/your-new-skill /mnt/user-data/outputs/
```

This creates a `.skill` file the user can upload directly to Claude.ai Settings > Capabilities > Skills.

---

## Delivery

When handing off to the user, present:
1. The `.skill` file (via `present_files`)
2. A summary card with:
   - Skill name and category
   - Trigger phrases (the 4–6 that activate it)
   - Package contents (what files were built and why)
   - Test coverage (how many trigger + functional tests)
   - Installation instructions (2–3 steps)
3. Offer to iterate: "Want to adjust any behavior, add edge cases, or refine the triggers?"

---

## Quick Reference

| Phase | Key action | Reference |
|-------|-----------|-----------|
| 0 | Run plan-mode interview | `assets/plan-interview-template.md` |
| 1 | Research domain | web search + MCP docs + `/mnt/skills/` |
| 2 | Choose architecture | `references/patterns-catalog.md` |
| 3 | Write SKILL.md | `references/anthropic-recipe.md` |
| 4 | Build scripts/refs/assets | Phase 4 guidance above |
| 5 | Generate evals | `references/eval-templates.md` |
| 6 | Validate + package | `scripts/validate_skill.py` + `scripts/package_skill.py` |
