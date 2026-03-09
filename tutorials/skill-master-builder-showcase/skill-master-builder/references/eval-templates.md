# Eval Templates — Test Case Generation Guide

Use this reference during Phase 5 (Generate Test Cases) of skill-master-builder.

---

## Table of Contents
1. [Why Test Cases Matter](#why-test-cases-matter)
2. [Trigger Eval Schema](#trigger-eval-schema)
3. [Functional Eval Schema](#functional-eval-schema)
4. [Full Eval Set Template](#full-eval-set-template)
5. [Writing Good Test Queries](#writing-good-test-queries)
6. [Success Metrics](#success-metrics)

---

## Why Test Cases Matter

Skills fail in two ways:
1. **Undertriggering** — skill doesn't load when it should → user gets generic response
2. **Overtriggering** — skill loads when irrelevant → confusion, wasted tokens

A good eval set catches both before the skill is deployed.

**Minimum eval set for any skill:**
- 5 trigger=true cases
- 3 trigger=false cases
- 3 functional cases

**Recommended eval set for production skills:**
- 10–20 trigger cases (mix of obvious, paraphrased, implicit)
- 5+ functional cases (happy path, edge cases, error cases)

---

## Trigger Eval Schema

```json
{
  "id": "trigger-001",
  "type": "trigger",
  "query": "The exact user message to test",
  "should_trigger": true,
  "rationale": "Why this should/shouldn't trigger the skill"
}
```

**Fields:**
- `id` — unique identifier, format: `trigger-NNN`
- `type` — always `"trigger"` for these tests
- `query` — realistic user message (complete sentence, natural language)
- `should_trigger` — `true` or `false`
- `rationale` — one sentence explaining the expected behavior

---

## Functional Eval Schema

```json
{
  "id": "functional-001",
  "type": "functional",
  "query": "The user request to execute",
  "context": "Any setup context the skill needs",
  "expected_behavior": "High-level description of what should happen",
  "assertions": [
    "Specific, checkable condition 1",
    "Specific, checkable condition 2",
    "Specific, checkable condition 3"
  ],
  "edge_case": false,
  "notes": "Optional: special considerations for this test"
}
```

**Fields:**
- `id` — unique identifier, format: `functional-NNN`
- `type` — always `"functional"` for these tests
- `query` — complete realistic user request
- `context` — any prerequisite state or inputs (file content, project state, etc.)
- `expected_behavior` — plain language description of the correct workflow
- `assertions` — 2–5 specific, objectively checkable conditions
- `edge_case` — `true` if this tests unusual/boundary behavior
- `notes` — optional clarifications

---

## Full Eval Set Template

```json
{
  "skill_name": "your-skill-name",
  "skill_version": "1.0.0",
  "generated_date": "2026-03-08",
  "eval_set": [
    {
      "id": "trigger-001",
      "type": "trigger",
      "query": "[Obvious, direct use case — user says exactly what the skill does]",
      "should_trigger": true,
      "rationale": "Direct match to primary use case"
    },
    {
      "id": "trigger-002",
      "type": "trigger",
      "query": "[Paraphrased version — same intent, different words]",
      "should_trigger": true,
      "rationale": "Paraphrase of primary trigger"
    },
    {
      "id": "trigger-003",
      "type": "trigger",
      "query": "[Implicit trigger — user describes the problem, not the tool]",
      "should_trigger": true,
      "rationale": "Implied use case — skill should infer need"
    },
    {
      "id": "trigger-004",
      "type": "trigger",
      "query": "[Adjacent domain — similar-sounding but the skill covers it]",
      "should_trigger": true,
      "rationale": "Within scope — related workflow this skill handles"
    },
    {
      "id": "trigger-005",
      "type": "trigger",
      "query": "[Edge trigger — minimal context, skill should still catch it]",
      "should_trigger": true,
      "rationale": "Minimal phrasing that should still activate skill"
    },
    {
      "id": "trigger-006",
      "type": "trigger",
      "query": "What's the weather in Bangalore today?",
      "should_trigger": false,
      "rationale": "Completely unrelated query"
    },
    {
      "id": "trigger-007",
      "type": "trigger",
      "query": "[Adjacent topic the skill does NOT cover]",
      "should_trigger": false,
      "rationale": "Similar domain but out of scope for this skill"
    },
    {
      "id": "trigger-008",
      "type": "trigger",
      "query": "[Generic task Claude can handle without the skill]",
      "should_trigger": false,
      "rationale": "General capability — no skill needed"
    },
    {
      "id": "functional-001",
      "type": "functional",
      "query": "[Standard happy-path request]",
      "context": "[Required inputs or state]",
      "expected_behavior": "[Skill runs full workflow and produces expected output]",
      "assertions": [
        "Output contains [required element]",
        "Workflow completes in correct sequence",
        "No error messages in output"
      ],
      "edge_case": false
    },
    {
      "id": "functional-002",
      "type": "functional",
      "query": "[Edge case — unusual but valid input]",
      "context": "[Edge case setup]",
      "expected_behavior": "[Skill handles gracefully with appropriate output or error message]",
      "assertions": [
        "Skill does not crash or produce garbled output",
        "Error is communicated clearly if applicable",
        "User is given next steps"
      ],
      "edge_case": true
    },
    {
      "id": "functional-003",
      "type": "functional",
      "query": "[Error case — input that should trigger error handling]",
      "context": "[Setup that will cause a failure]",
      "expected_behavior": "[Skill detects error, explains cause, suggests fix]",
      "assertions": [
        "Error message is specific (not generic)",
        "Root cause is identified",
        "At least one corrective action is suggested"
      ],
      "edge_case": true,
      "notes": "Tests the Error Handling section of SKILL.md"
    }
  ]
}
```

---

## Writing Good Test Queries

### Trigger=true queries — vary along these dimensions

| Dimension | Example for "sprint-planner" skill |
|-----------|-------------------------------------|
| Direct | "Help me plan this sprint" |
| Paraphrased | "I need to organize our two-week iteration" |
| Implicit | "We have 12 tasks to finish by end of month, can you help prioritize?" |
| Domain jargon | "Create story points and velocity estimates for Q2 sprint 4" |
| Terse | "sprint planning" |

### Trigger=false queries — make them realistic

Bad trigger=false test: "What is 2+2?" (too obviously unrelated)  
Good trigger=false test: "Can you help me write a project roadmap?" (adjacent but different)

The best negative tests are queries that SOUND like they might trigger the skill but shouldn't.

### Functional assertions — make them checkable

Bad assertion: "Output is good quality"  
Good assertion: "Output contains at least 5 task items, each with a name and estimated hours"

Bad assertion: "MCP calls succeed"  
Good assertion: "Skill calls `create_sprint` exactly once with non-empty project_id parameter"

---

## Success Metrics

**Quantitative targets (from Anthropic guide):**
- Skill triggers on ≥90% of relevant queries
- Skill does NOT trigger on ≥95% of irrelevant queries
- Functional tests pass on first attempt ≥80% of the time
- Zero crashed/garbled outputs on edge cases

**Qualitative signals:**
- User doesn't need to re-prompt Claude about next steps
- Workflow completes without user correction
- New user can accomplish the task on first try
- Results are consistent across multiple sessions
