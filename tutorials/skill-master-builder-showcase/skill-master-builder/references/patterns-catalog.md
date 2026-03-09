# Skill Patterns Catalog

Five production-proven patterns from the official Anthropic guide + category frameworks.  
Select the right pattern **before** writing SKILL.md.

---

## Table of Contents
1. [Category Quick-Select](#category-quick-select)
2. [Pattern 1: Sequential Workflow Orchestration](#pattern-1-sequential-workflow-orchestration)
3. [Pattern 2: Multi-MCP Coordination](#pattern-2-multi-mcp-coordination)
4. [Pattern 3: Iterative Refinement](#pattern-3-iterative-refinement)
5. [Pattern 4: Context-Aware Tool Selection](#pattern-4-context-aware-tool-selection)
6. [Pattern 5: Domain-Specific Intelligence](#pattern-5-domain-specific-intelligence)
7. [Pattern Combination Guide](#pattern-combination-guide)

---

## Category Quick-Select

### Category 1: Document & Asset Creation
**Use for:** Generating consistent, high-quality outputs — documents, presentations, dashboards, designs, code artifacts.

**Signals:**
- User wants a file or structured document produced
- Style consistency or brand standards matter
- No external tools required — uses Claude's built-in capabilities
- Output is self-contained

**Key techniques:**
- Embedded style guides and quality criteria in `references/`
- Template structures in `assets/`
- Quality checklist before finalizing
- Examples of good vs. bad output

**Real example:** `frontend-design`, `docx`, `pptx`, `visual-explainer`

---

### Category 2: Workflow Automation
**Use for:** Multi-step processes that benefit from consistent methodology. May span multiple tools.

**Signals:**
- Task requires 3+ steps in a specific order
- User would otherwise forget steps or do them inconsistently
- Validation gates matter between steps
- Could involve scripts, file transforms, or MCP calls

**Key techniques:**
- Explicit step ordering with numbered phases
- Validation gates between steps
- Templates for consistent structure
- Iterative refinement loops
- Built-in review and improvement suggestions

**Real example:** `skill-creator`, `sprint-planner`, `onboarding-flow`

---

### Category 3: MCP Enhancement
**Use for:** Adding workflow intelligence on top of an existing MCP server connection.

**Signals:**
- User already has an MCP server (Notion, Linear, Asana, Sentry, etc.)
- They know what to do but not *how* Claude should do it well
- Consistent tool call sequences matter
- Domain best practices need to be embedded

**Key techniques:**
- Coordinate multiple MCP calls in sequence
- Embed domain expertise users shouldn't need to specify
- Provide context that would otherwise require manual prompting
- Error handling for common MCP failure modes

**Real example:** `sentry-code-review`, `linear-sprint-planner`, `notion-workspace-setup`

---

## Pattern 1: Sequential Workflow Orchestration

**Use when:** Users need multi-step processes run in a specific, ordered sequence.

**Best fit:** Category 2, Category 3

```markdown
## Workflow: [Name]

### Step 1: [Action]
Call: `mcp_tool_name` with parameters: name, email, company
Expected result: [describe what success looks like]

CRITICAL: Do not proceed to Step 2 until Step 1 returns a success status.

### Step 2: [Dependent Action]
Requires: output.id from Step 1
Call: `next_mcp_tool` with customer_id={step1.id}

### Step 3: [Final Action]
...

### Rollback (if Step 3 fails)
1. Call `delete_customer` with id={step1.id}
2. Notify user of failure with specific error
```

**Key techniques:**
- Explicit step ordering with gate conditions
- Pass outputs between steps explicitly
- Rollback instructions for failure states
- State confirmation at each stage

---

## Pattern 2: Multi-MCP Coordination

**Use when:** Workflows span multiple services (Figma + Drive + Linear + Slack, etc.)

**Best fit:** Category 3 (advanced)

```markdown
## Phase 1: [Service A — e.g., Figma]
1. Export design assets
2. Generate specifications  
3. Create asset manifest

## Phase 2: [Service B — e.g., Drive]
Requires: asset manifest from Phase 1
1. Create project folder
2. Upload all assets
3. Generate shareable links

## Phase 3: [Service C — e.g., Linear]
Requires: Drive links from Phase 2
1. Create development tasks
2. Attach asset links
3. Assign to team

## Phase 4: [Service D — e.g., Slack]
1. Post handoff summary
2. Include all links from Phases 2–3
```

**Key techniques:**
- Clear phase separation by service
- Explicit data passing between MCPs
- Validate completion before moving phases
- Centralized error handling section

---

## Pattern 3: Iterative Refinement

**Use when:** Output quality improves with multiple review/improve cycles.

**Best fit:** Category 1, Category 2

```markdown
## Step 1: Generate Initial Draft
[Produce first version of output]

## Step 2: Quality Check
Run: `python scripts/validate_output.py`
Check for:
- Missing required sections
- Formatting inconsistencies  
- Data validation errors

## Step 3: Refinement Loop
For each issue found:
1. Address the specific issue
2. Regenerate affected section
3. Re-run validation

Continue until: all checks pass OR 3 iterations complete

## Step 4: Finalize
Apply final formatting → save → present to user
```

**Key techniques:**
- Explicit quality criteria (not vague "check quality")
- Deterministic validation via script when possible
- Clear termination condition for the loop
- Know when to stop and ask user instead

---

## Pattern 4: Context-Aware Tool Selection

**Use when:** The same goal has different optimal approaches depending on context.

**Best fit:** Category 2, Category 3

```markdown
## Decision: Choose Storage Approach

Evaluate the file:
- Size > 10MB → use cloud storage MCP
- Collaborative editing needed → use Notion/Docs MCP  
- Code files → use GitHub MCP
- Temporary/scratch → use local storage

Then:
1. Call appropriate MCP with service-specific parameters
2. Apply service-specific metadata
3. Generate access link
4. Explain to user WHY that storage was chosen
```

**Key techniques:**
- Explicit decision criteria (not ambiguous)
- Fallback options for each path
- Transparency to user about the decision made
- Consistent outcome regardless of path taken

---

## Pattern 5: Domain-Specific Intelligence

**Use when:** The skill embeds specialized knowledge or compliance rules beyond tool access.

**Best fit:** Category 1 (with standards), Category 3 (compliance-heavy)

```markdown
## Pre-Processing: Domain Rules Check

Before performing the main action, apply domain rules:

CRITICAL: Run compliance check before any external calls:
1. Fetch transaction/document details
2. Apply domain rules:
   - Rule A: [specific check]
   - Rule B: [specific check]
   - Rule C: [specific check]
3. Document the compliance decision

## Processing (only if rules passed)

IF compliance_status == "passed":
  - Proceed with main workflow
  - Apply additional domain-specific parameters
ELSE:
  - Flag for human review
  - Create audit case
  - Do NOT proceed

## Audit Trail
Log: all checks performed, decisions made, timestamps
```

**Key techniques:**
- Domain expertise baked into check logic
- Compliance/rules before action (never after)
- Comprehensive documentation of decisions
- Clear governance and escalation paths

---

## Pattern Combination Guide

Patterns can be combined. Common combos:

| Primary | Secondary | Use case |
|---------|-----------|----------|
| Pattern 1 (Sequential) | Pattern 5 (Domain) | Compliance workflow |
| Pattern 2 (Multi-MCP) | Pattern 3 (Iterative) | Design-to-dev with review cycles |
| Pattern 4 (Context-aware) | Pattern 1 (Sequential) | Adaptive onboarding |
| Pattern 3 (Iterative) | Pattern 5 (Domain) | Report generation with standards |

When combining: run Pattern 5 checks first, then orchestrate with Pattern 1 or 2, refine with Pattern 3.
