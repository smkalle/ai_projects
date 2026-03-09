# How skill-master-builder Works

## The Meta-Skill Concept

Most Claude skills encode domain expertise — they know how to do *one thing* well.

`skill-master-builder` is different: it knows how to *build* skills. Its output is not a document, a plan, or a piece of code — it's another Claude skill.

This is what makes it a **meta-skill**.

```
Ordinary skill:    User input → [domain expertise] → output artifact
Meta-skill:        User input → [skill-building expertise] → new skill
```

The new skill then becomes reusable, shareable, and installable — a permanent capability addition for any Claude user.

---

## Architecture

skill-master-builder runs a structured 6-phase pipeline every time it builds a skill.

### Phase 0: Plan-Mode Interview

Before writing a single line, skill-master-builder asks 10 structured questions:

| # | Question | Purpose |
|---|----------|---------|
| 1 | WHAT | Define the task in plain language |
| 2 | CATEGORY | Route to correct pattern (Doc / Workflow / MCP) |
| 3 | TRIGGER | Define activation phrases for the description field |
| 4 | INPUTS | Understand what the user provides |
| 5 | OUTPUT | Clarify the success artifact |
| 6 | MCP | Identify external tool dependencies |
| 7 | DOMAIN KNOWLEDGE | Surface expertise to embed |
| 8 | EDGE CASES | Anticipate failure modes |
| 9 | SUCCESS | Define what "perfect" looks like |
| 10 | SCOPE | Single-step vs multi-step |

The answers become a **SKILL DESIGN BRIEF** — a written summary confirmed by the user before any building begins.

**Why this matters:** Skills built without a plan tend to have vague descriptions (undertriggering), missing error handling, and no test coverage. The interview forces specificity before commitment.

### Phase 1: Research & Domain Enrichment

Once the plan is confirmed, skill-master-builder researches the domain:

- If MCP is involved → looks up tool names, parameters, error codes
- If compliance is involved → surfaces specific rules (I-9 deadlines, state forms)
- If patterns exist → consults `references/patterns-catalog.md`
- Web search for best practices, failure modes, example inputs/outputs

Research is captured in `references/domain-notes.md` inside the new skill.

**Why this matters:** A skill without domain knowledge is just a template. The research phase is what makes the output genuinely useful — it bakes in expertise the user shouldn't need to specify on every use.

### Phase 2: Skill Architecture Design

Three folder structures based on complexity:

```
Minimal (no MCP, no scripts):
  your-skill/
  └── SKILL.md

Standard (with reference docs):
  your-skill/
  ├── SKILL.md
  └── references/domain-notes.md

Full (MCP, scripts, templates):
  your-skill/
  ├── SKILL.md
  ├── scripts/validate_output.py
  ├── references/
  │   ├── domain-notes.md
  │   └── api-patterns.md
  └── assets/output-template.md
```

Pattern selection from `references/patterns-catalog.md`:

| Pattern | Best for |
|---------|---------|
| Sequential Workflow | Ordered multi-step processes |
| Multi-MCP Coordination | Spanning multiple services |
| Iterative Refinement | Quality-improving review loops |
| Context-Aware Tool Selection | Adaptive approach by context |
| Domain-Specific Intelligence | Compliance-heavy or standards-driven |

Patterns can be combined. Common combos:
- Pattern 1 + Pattern 5 = Compliance workflow (e.g., hr-onboarding-manager)
- Pattern 2 + Pattern 3 = Design-to-dev with review cycles

### Phase 3: Write SKILL.md

The core instruction file. skill-master-builder enforces:

- **Frontmatter:** `name` (kebab-case, ≤64 chars), `description` (≤1024 chars, 4–6 trigger phrases, no XML)
- **Body structure:** Prerequisites → numbered steps → examples → error handling → quality checklist
- **Writing rules:**
  - Instructions specific and actionable (never "process the data")
  - Critical instructions at the top with `CRITICAL:` prefix
  - Bundled files referenced explicitly by path
  - Under 500 lines — detail moved to `references/`
- **Progressive disclosure:** SKILL.md is loaded when relevant; bundled files loaded only as needed

**The description field is the most critical part.** It's how Claude decides whether to load the skill. skill-master-builder writes it to be "slightly pushy" — avoiding undertriggering by including paraphrased and implicit trigger phrases.

### Phase 4: Build Supporting Files

**scripts/** — Python or Bash scripts for deterministic checks. Prefer scripts over language instructions for format validation, required field checks, and file structure assertions. Scripts must be self-contained with clear pass/fail output.

**references/** — Domain knowledge loaded on demand. Files over 300 lines get a table of contents. Typical files:
- `domain-notes.md` — from Phase 1 research
- `compliance-requirements.md` — legal/regulatory rules
- `api-patterns.md` — MCP tool call conventions

**assets/** — Output templates, schemas, style guides. Pre-built templates reduce variance in generated output.

### Phase 5: Generate Test Cases

Minimum test set saved to `evals/trigger-eval.json`:

| Type | Minimum | Purpose |
|------|---------|---------|
| `trigger: true` | 5 | Obvious + paraphrased + implicit activations |
| `trigger: false` | 3 | Adjacent topics that must NOT activate the skill |
| `functional` | 3 | Happy path + edge case + error case |

Assertions are specific and checkable — not "output is good" but "output contains at least 5 tasks with owners."

### Phase 6: Validate + Package

```bash
# Validate structure and compliance
python scripts/validate_skill.py /path/to/skill

# Package as .skill ZIP
python scripts/package_skill.py /path/to/skill /output/
```

`validate_skill.py` checks 30+ items across:
- YAML frontmatter correctness
- Description quality and trigger coverage
- SKILL.md line count and structure
- Security rules (no XML, no "claude"/"anthropic" in name)
- Progressive disclosure compliance
- Eval coverage

Zero errors required before packaging.

---

## Progressive Disclosure

Skills use a 3-level loading system:

| Level | Content | When loaded | Token cost |
|-------|---------|-------------|------------|
| 1 | YAML frontmatter only | Every conversation | ~100 tokens |
| 2 | SKILL.md body | When Claude determines relevance | ~2,000 tokens |
| 3 | `references/`, `assets/`, `scripts/` | On demand, as cited | Unlimited |

This means:
- The description must be self-sufficient for Claude to decide when to trigger
- SKILL.md should contain the workflow, not all the detail
- Heavy domain knowledge lives in `references/` and is pulled only when needed

---

## The hr-onboarding-manager Example

`hr-onboarding-manager` was built by `skill-master-builder` to demonstrate all of this concretely.

**Interview answers that shaped the skill:**
- Category: [B] Workflow Automation
- Trigger phrases: "onboard a new employee", "new hire starting", "30-60-90 day plan", "new hire checklist"
- Domain knowledge: SHRM 4 C's, I-9 compliance (Day 3 deadline, $272+ fine), state-specific forms
- Edge cases: compressed timeline (<5 days), unknown state, manager unavailable Day 1
- Patterns used: Pattern 1 (Sequential) + Pattern 5 (Domain-Specific Intelligence)

**What was built:**
- 6-phase SKILL.md (280 lines)
- `references/domain-notes.md` — SHRM framework, role-specific TTP, failure modes
- `references/compliance-requirements.md` — federal + state compliance rules, I-9 deep dive
- `assets/` — 3 ready-to-use HR templates
- `scripts/validate_onboarding_plan.py` — checks generated plans for compliance completeness
- `evals/trigger-eval.json` — 11 test cases

**Validation result:** ✅ All checks passed on first run.

The skill was then used as the intelligence layer for a Streamlit + SQLite workbench that HR teams can use as an MVP dashboard — demonstrating the full chain from meta-skill → domain skill → production application.

---

## Relationship to the Official Anthropic Spec

skill-master-builder implements the rules and patterns from Anthropic's official guide: [*The Complete Guide to Building Skills for Claude*](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf) (January 2026).

The spec defines the skill format (folder structure, YAML frontmatter, progressive disclosure), three skill categories (Document & Asset Creation, Workflow Automation, MCP Enhancement), five workflow patterns, testing methodology, and distribution model.

skill-master-builder encodes these as enforceable rules rather than suggestions:
- The plan-mode interview maps directly to the spec's "Start with use cases" and "Define success criteria" sections
- Phase 3 writing rules enforce the spec's frontmatter requirements, description structure, and instruction best practices
- Phase 5 eval generation follows the spec's three testing areas (triggering, functional, performance)
- Phase 6 validation catches every structural and security violation the spec prohibits

For a complete summary of the spec, see [anthropic-skill-spec-summary.md](anthropic-skill-spec-summary.md).

---

## Building Your Own Skill

See [building-your-own-skill.md](building-your-own-skill.md).
