# Plan-Mode Interview Template

## How to Use
After completing the 10-question interview, fill this template and present it to the user for confirmation before writing a single line of SKILL.md.

---

## SKILL DESIGN BRIEF

**Skill name (proposed):** `[kebab-case-name]`

**Category:** [1] Document & Asset Creation | [2] Workflow Automation | [3] MCP Enhancement

**One-line purpose:**  
[What this skill helps Claude do, in plain language]

---

### Trigger Conditions
*When should this skill activate?*

| Trigger type | Example phrase |
|-------------|----------------|
| Direct | "[user says exactly this]" |
| Paraphrased | "[same intent, different words]" |
| Implicit | "[problem description that implies this skill]" |
| Domain-specific | "[jargon that signals this context]" |
| Terse | "[minimal phrase]" |

**Should NOT trigger when:** [describe 2–3 adjacent cases that are out of scope]

---

### Inputs
| Input | Type | Required? | Notes |
|-------|------|-----------|-------|
| [Input 1] | [file/text/URL/context] | Yes/No | [how it's used] |
| [Input 2] | [file/text/URL/context] | Yes/No | [how it's used] |

---

### Output
**Format:** [file type, structured text, MCP calls, etc.]  
**Delivered as:** [attachment / inline response / tool calls / combination]  
**Quality criteria:** [what makes the output "done" and good]

---

### Workflow Steps (high-level)
1. [Step 1 — what happens first]
2. [Step 2]
3. [Step 3]
4. [...continue...]
N. [Final step — delivery]

---

### MCP Dependencies
| MCP Server | Tools Used | Purpose |
|-----------|-----------|---------|
| [server name] | [tool1, tool2] | [what it does in this workflow] |
| *(none if standalone)* | | |

---

### Domain Knowledge to Embed
- [Key rule or standard 1]
- [Key rule or standard 2]
- [Style guide, compliance requirement, or best practice 3]

---

### Edge Cases & Error Handling
| Situation | How skill should handle it |
|-----------|---------------------------|
| [Edge case 1] | [response/fallback] |
| [Edge case 2] | [response/fallback] |
| [Error case] | [error message + fix suggestion] |

---

### Proposed Folder Structure
```
[skill-name]/
├── SKILL.md
├── scripts/
│   └── [script-name].py
├── references/
│   ├── domain-notes.md
│   └── [other-ref].md
└── assets/
    └── [template-name].md
```
*(Remove directories that won't be needed)*

---

### Pattern Selection
**Primary pattern:** [Pattern 1/2/3/4/5 — name]  
**Secondary pattern (if applicable):** [Pattern name or "none"]

---

### Success Definition
*How will we know the skill is working perfectly?*

**Quantitative:** [e.g., "produces 5-task sprint plan in under 30 seconds"]  
**Qualitative:** [e.g., "user doesn't need to re-prompt; result is immediately usable"]

---

### Test Coverage Plan
| Test type | Count | What they cover |
|-----------|-------|----------------|
| Trigger=true | 5 | [obvious, paraphrased, implicit, domain, terse] |
| Trigger=false | 3 | [unrelated, adjacent-but-out-of-scope, generic] |
| Functional | 3+ | [happy path, edge case, error case] |

---

*Confirm this design brief before proceeding to build.*  
*Ask: "Does this match your intent? Any corrections before I write the skill?"*
