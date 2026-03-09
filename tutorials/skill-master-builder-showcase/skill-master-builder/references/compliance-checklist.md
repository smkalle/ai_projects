# Anthropic Skill Compliance Checklist

Run this checklist before packaging and delivering any skill built by skill-master-builder.  
All items must be checked. No exceptions.

---

## Phase 0: Planning ✓

- [ ] Plan-mode interview completed (all 10 questions answered)
- [ ] Skill Design Brief written and confirmed by user
- [ ] Category identified: [1] Doc/Asset | [2] Workflow | [3] MCP Enhancement
- [ ] Pattern(s) selected from patterns-catalog.md
- [ ] Folder structure decided before writing

---

## Phase 1: Research ✓

- [ ] Domain knowledge researched (web search, MCP docs, or existing references)
- [ ] Key domain concepts documented in `references/domain-notes.md`
- [ ] MCP tool names verified (if applicable)
- [ ] Common failure modes identified and documented
- [ ] Any related existing skills checked in `/mnt/skills/`

---

## Phase 2: Folder Structure ✓

- [ ] Folder named in `kebab-case` (lowercase, hyphens only, no spaces, no underscores)
- [ ] `SKILL.md` file exists with exact spelling (case-sensitive)
- [ ] No `README.md` inside the skill folder
- [ ] `scripts/` directory present (if scripts used)
- [ ] `references/` directory present (if reference docs created)
- [ ] `assets/` directory present (if templates/assets created)
- [ ] `evals/trigger-eval.json` created with test cases

---

## Phase 3: YAML Frontmatter ✓

- [ ] `---` delimiters present — opening AND closing
- [ ] `name` field present and in `kebab-case`
- [ ] `name` is ≤64 characters
- [ ] `name` matches the folder name
- [ ] `name` does NOT contain "claude" or "anthropic" (reserved)
- [ ] `description` field present
- [ ] `description` is ≤1024 characters
- [ ] `description` explains WHAT the skill does
- [ ] `description` explains WHEN to use it (trigger conditions)
- [ ] `description` includes 4–6 specific trigger phrases users would actually say
- [ ] `description` contains NO XML angle brackets `< >`
- [ ] `compatibility` field ≤500 characters (if present)
- [ ] No unexpected/undocumented frontmatter fields

---

## Phase 4: SKILL.md Body ✓

- [ ] SKILL.md body is under 500 lines
- [ ] Instructions are specific and actionable (not vague)
- [ ] Critical instructions are at the TOP of the file
- [ ] `CRITICAL:` prefix used for must-not-skip steps
- [ ] Bundled reference files cited explicitly with paths
- [ ] Error handling section included
- [ ] At least 2 concrete examples provided
- [ ] Quality checklist or validation criteria included
- [ ] No README.md content duplicated here

---

## Phase 5: Supporting Files ✓

**Scripts (if present):**
- [ ] Scripts handle errors gracefully (try/except or error codes)
- [ ] Scripts print clear pass/fail messages
- [ ] Scripts are self-contained (no undeclared dependencies)
- [ ] Script paths match references in SKILL.md

**References (if present):**
- [ ] Files are clearly named and purposeful
- [ ] Files >300 lines have a table of contents
- [ ] `domain-notes.md` captures Phase 1 research
- [ ] No orphan files (every reference file is linked from SKILL.md)

**Assets (if present):**
- [ ] Templates are complete and usable
- [ ] Assets are referenced from SKILL.md or scripts

---

## Phase 6: Eval Set ✓

- [ ] `evals/trigger-eval.json` created
- [ ] Minimum 5 trigger=true test cases
- [ ] Minimum 3 trigger=false test cases
- [ ] Minimum 3 functional test cases
- [ ] All assertions are specific and checkable (not "output is good")
- [ ] Negative tests are realistic (not "what is 2+2?")
- [ ] Edge cases covered in functional tests
- [ ] Error cases covered in functional tests

---

## Security ✓

- [ ] No XML angle brackets `< >` anywhere in YAML frontmatter
- [ ] Skill name does not start with "claude" or "anthropic"
- [ ] No external URLs hardcoded into scripts (use parameters or references)
- [ ] No API keys, tokens, or credentials in any file
- [ ] Scripts use safe input handling (no shell injection risk)

---

## Progressive Disclosure ✓

- [ ] Frontmatter description is self-sufficient for triggering decisions (~100 words max)
- [ ] SKILL.md body contains core workflow (not all edge case detail)
- [ ] Detailed domain knowledge pushed to `references/`
- [ ] Large reference files linked explicitly, not inlined

---

## Final Delivery ✓

- [ ] `validate_skill.py` run with zero errors
- [ ] `package_skill.py` produces `.skill` file successfully
- [ ] Delivery summary prepared (trigger phrases, package contents, install steps)
- [ ] User offered opportunity to iterate
