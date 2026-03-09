# Building Your Own Skill with skill-master-builder

## Prerequisites

1. Install skill-master-builder on Claude.ai:
   - Settings → Capabilities → Skills → Upload skill
   - Upload `skill-master-builder.skill` from [Releases](../../releases)

2. Optionally install any MCP servers your skill will coordinate

## Step 1: Trigger skill-master-builder

Say any of these in a new Claude conversation:

```
"Build me a skill that [describes what you want]"
"Create a skill for [your use case]"
"Turn this workflow into a Claude skill: [describe it]"
"I want a skill that handles [domain]"
```

## Step 2: Answer the Interview

skill-master-builder will ask 10 questions. Answer them all at once for fastest results.

**Tips for good answers:**

- **TRIGGER phrases:** Think about what someone would literally type when they need this. Include obvious, paraphrased, and implicit versions. Bad: "data processing". Good: "analyze my sales data", "show me trends in this CSV", "what's in this spreadsheet"

- **DOMAIN KNOWLEDGE:** Be specific about rules and constraints. "HR compliance" is vague. "I-9 must be completed by Day 3, W-4 before first paycheck, state new hire report within 20 days" is useful.

- **EDGE CASES:** What breaks the happy path? Name 2–3 real failure modes you've seen.

- **SUCCESS:** Describe the ideal output in concrete terms. "A markdown checklist with owner and deadline per item" is better than "a helpful plan."

## Step 3: Confirm the Design Brief

skill-master-builder will summarize your answers as a SKILL DESIGN BRIEF and ask for confirmation.

Read it carefully — corrections here are free. Corrections after building cost iteration cycles.

## Step 4: Wait for the Build

The full pipeline runs automatically:
1. Domain research (web search + pattern matching)
2. Architecture selection
3. SKILL.md authoring
4. Supporting file generation
5. Test case creation
6. Validation + packaging

You'll receive a `.skill` file and a summary card with trigger phrases, package contents, and install instructions.

## Step 5: Install and Test

Upload the `.skill` file to Claude.ai Settings → Capabilities → Skills.

Test with the trigger phrases from the summary card. Run the eval set if you want automated coverage metrics:

```bash
# After downloading the skill package:
python validate_skill.py /path/to/your-skill   # structural check
```

## Step 6: Iterate

skill-master-builder will offer to adjust behavior, add edge cases, or refine triggers. Common iterations:

- "Add handling for [edge case]"
- "The trigger is too narrow — it should also fire when someone says [phrase]"
- "Add a section for [scenario I forgot to mention]"
- "The instructions for Phase 3 need more specificity about [detail]"

## Packaging for Distribution

```bash
# Validate before packaging
python skill-master-builder/scripts/validate_skill.py /path/to/your-skill

# Package
python skill-master-builder/scripts/package_skill.py /path/to/your-skill ./output/
```

## Contributing to This Repo

Built a skill with skill-master-builder? Submit it as an example:

1. Fork this repo
2. Add your skill to `examples/your-domain/skill/`
3. Optionally add a demo app to `examples/your-domain/demo/`
4. Add a brief `examples/your-domain/README.md`
5. Open a pull request

See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.
