#!/usr/bin/env python3
"""
skill-master-builder: Skill Validator
Validates a skill directory against Anthropic's full compliance spec.

Usage:
    python scripts/validate_skill.py <path/to/skill-folder>

Exit codes:
    0 = valid
    1 = invalid (errors found)
    2 = warnings only (skill is valid but improvements suggested)
"""

import sys
import os
import re
import json
from pathlib import Path

try:
    import yaml
except ImportError:
    print("❌ Missing dependency: pyyaml")
    print("   Fix: pip install pyyaml --break-system-packages")
    sys.exit(1)


# ── Constants ──────────────────────────────────────────────────────────────────

ALLOWED_FRONTMATTER_KEYS = {"name", "description", "license", "allowed-tools", "metadata", "compatibility"}
RESERVED_NAME_PREFIXES = {"claude", "anthropic"}
MAX_NAME_LENGTH = 64
MAX_DESCRIPTION_LENGTH = 1024
MAX_COMPATIBILITY_LENGTH = 500
MAX_SKILL_MD_LINES = 500
MIN_TRIGGER_TRUE_TESTS = 5
MIN_TRIGGER_FALSE_TESTS = 3
MIN_FUNCTIONAL_TESTS = 3
GOOD_TRIGGER_PHRASES = ["when", "use", "ask", "say", "mention", "request"]


# ── Helpers ────────────────────────────────────────────────────────────────────

def red(s): return f"\033[91m{s}\033[0m"
def yellow(s): return f"\033[93m{s}\033[0m"
def green(s): return f"\033[92m{s}\033[0m"
def bold(s): return f"\033[1m{s}\033[0m"


# ── Validators ─────────────────────────────────────────────────────────────────

def validate_folder_name(skill_path: Path, errors: list, warnings: list):
    name = skill_path.name
    if not re.match(r'^[a-z0-9-]+$', name):
        errors.append(f"Folder name '{name}' must be kebab-case (lowercase letters, digits, hyphens only)")
    if name.startswith('-') or name.endswith('-') or '--' in name:
        errors.append(f"Folder name '{name}' cannot start/end with hyphen or have consecutive hyphens")
    for prefix in RESERVED_NAME_PREFIXES:
        if name.startswith(prefix):
            errors.append(f"Folder name '{name}' uses reserved prefix '{prefix}'")


def validate_required_files(skill_path: Path, errors: list, warnings: list):
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        errors.append("SKILL.md not found (must be exactly 'SKILL.md', case-sensitive)")
        return False

    # Check for common wrong names
    for bad_name in ["skill.md", "SKILL.MD", "Skill.md", "skill.MD"]:
        if (skill_path / bad_name).exists():
            errors.append(f"Found '{bad_name}' — must be renamed to exactly 'SKILL.md'")

    if (skill_path / "README.md").exists():
        warnings.append("README.md found inside skill folder — move documentation to SKILL.md or references/")

    return True


def validate_frontmatter(skill_path: Path, errors: list, warnings: list):
    skill_md = skill_path / "SKILL.md"
    content = skill_md.read_text(encoding="utf-8")

    if not content.startswith("---"):
        errors.append("SKILL.md must begin with YAML frontmatter (---)")
        return None

    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        errors.append("Frontmatter block not properly closed — add '---' after YAML content")
        return None

    frontmatter_text = match.group(1)

    # Check for XML angle brackets
    if "<" in frontmatter_text or ">" in frontmatter_text:
        errors.append("Frontmatter contains XML angle brackets (< >) — remove them (security restriction)")

    try:
        fm = yaml.safe_load(frontmatter_text)
    except yaml.YAMLError as e:
        errors.append(f"Invalid YAML in frontmatter: {e}")
        return None

    if not isinstance(fm, dict):
        errors.append("Frontmatter must be a YAML dictionary")
        return None

    # Unexpected keys
    unexpected = set(fm.keys()) - ALLOWED_FRONTMATTER_KEYS
    if unexpected:
        errors.append(f"Unexpected frontmatter key(s): {', '.join(sorted(unexpected))} "
                      f"— allowed: {', '.join(sorted(ALLOWED_FRONTMATTER_KEYS))}")

    return fm


def validate_name_field(fm: dict, skill_path: Path, errors: list, warnings: list):
    name = fm.get("name", "")
    if not name:
        errors.append("'name' field is required in frontmatter")
        return

    if not isinstance(name, str):
        errors.append(f"'name' must be a string, got {type(name).__name__}")
        return

    name = name.strip()

    if not re.match(r'^[a-z0-9-]+$', name):
        errors.append(f"'name' field '{name}' must be kebab-case (lowercase, digits, hyphens only)")
    if name.startswith('-') or name.endswith('-') or '--' in name:
        errors.append(f"'name' field '{name}' cannot start/end with hyphen or have consecutive hyphens")
    if len(name) > MAX_NAME_LENGTH:
        errors.append(f"'name' is {len(name)} chars — max is {MAX_NAME_LENGTH}")
    for prefix in RESERVED_NAME_PREFIXES:
        if name.startswith(prefix):
            errors.append(f"'name' uses reserved prefix '{prefix}'")

    # Name should match folder
    folder_name = skill_path.name
    if name != folder_name:
        warnings.append(f"'name' field '{name}' doesn't match folder name '{folder_name}' — they should match")


def validate_description_field(fm: dict, errors: list, warnings: list):
    desc = fm.get("description", "")
    if not desc:
        errors.append("'description' field is required in frontmatter")
        return

    if not isinstance(desc, str):
        errors.append(f"'description' must be a string, got {type(desc).__name__}")
        return

    desc = desc.strip()

    if "<" in desc or ">" in desc:
        errors.append("'description' contains XML angle brackets — remove them")
    if len(desc) > MAX_DESCRIPTION_LENGTH:
        errors.append(f"'description' is {len(desc)} chars — max is {MAX_DESCRIPTION_LENGTH}")
    if len(desc) < 50:
        warnings.append("'description' seems very short — include what the skill does AND when to trigger it")

    # Check for trigger phrases
    has_trigger_hint = any(phrase in desc.lower() for phrase in GOOD_TRIGGER_PHRASES)
    if not has_trigger_hint:
        warnings.append("'description' may be missing trigger conditions — include 'Use when...' or specific user phrases")

    # Check for both what and when
    lower_desc = desc.lower()
    if "use when" not in lower_desc and "trigger" not in lower_desc and "when user" not in lower_desc:
        warnings.append("'description' should explicitly state when to use the skill — add 'Use when...' clause")


def validate_skill_md_body(skill_path: Path, errors: list, warnings: list):
    content = (skill_path / "SKILL.md").read_text(encoding="utf-8")
    lines = content.split("\n")

    # Strip frontmatter from line count
    if content.startswith("---"):
        end_fm = content.find("\n---\n", 3)
        if end_fm != -1:
            body = content[end_fm + 5:]
            body_lines = len(body.split("\n"))
            if body_lines > MAX_SKILL_MD_LINES:
                warnings.append(f"SKILL.md body is {body_lines} lines — consider moving detail to references/ (target: <{MAX_SKILL_MD_LINES})")

    # Check for examples
    if "## Example" not in content and "### Example" not in content:
        warnings.append("No examples found in SKILL.md — add at least 1-2 concrete examples")

    # Check for error handling
    if "error" not in content.lower() and "fail" not in content.lower():
        warnings.append("No error handling found in SKILL.md — add an Error Handling section")


def validate_compatibility_field(fm: dict, errors: list, warnings: list):
    compat = fm.get("compatibility", "")
    if compat and len(str(compat)) > MAX_COMPATIBILITY_LENGTH:
        errors.append(f"'compatibility' is {len(str(compat))} chars — max is {MAX_COMPATIBILITY_LENGTH}")


def validate_eval_set(skill_path: Path, errors: list, warnings: list):
    eval_path = skill_path / "evals" / "trigger-eval.json"
    if not eval_path.exists():
        warnings.append("No eval set found at evals/trigger-eval.json — generate test cases for reliability")
        return

    try:
        with open(eval_path) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        errors.append(f"evals/trigger-eval.json is not valid JSON: {e}")
        return

    eval_set = data.get("eval_set", [])
    trigger_true = [t for t in eval_set if t.get("type") == "trigger" and t.get("should_trigger") is True]
    trigger_false = [t for t in eval_set if t.get("type") == "trigger" and t.get("should_trigger") is False]
    functional = [t for t in eval_set if t.get("type") == "functional"]

    if len(trigger_true) < MIN_TRIGGER_TRUE_TESTS:
        warnings.append(f"Eval set has {len(trigger_true)} trigger=true tests — recommend ≥{MIN_TRIGGER_TRUE_TESTS}")
    if len(trigger_false) < MIN_TRIGGER_FALSE_TESTS:
        warnings.append(f"Eval set has {len(trigger_false)} trigger=false tests — recommend ≥{MIN_TRIGGER_FALSE_TESTS}")
    if len(functional) < MIN_FUNCTIONAL_TESTS:
        warnings.append(f"Eval set has {len(functional)} functional tests — recommend ≥{MIN_FUNCTIONAL_TESTS}")


def validate_references(skill_path: Path, errors: list, warnings: list):
    refs_dir = skill_path / "references"
    skill_content = (skill_path / "SKILL.md").read_text(encoding="utf-8")

    if refs_dir.exists():
        for ref_file in refs_dir.rglob("*.md"):
            rel_path = ref_file.relative_to(skill_path)
            ref_name = rel_path.name
            # Check if reference is cited in SKILL.md
            if ref_name not in skill_content and str(rel_path) not in skill_content:
                warnings.append(f"references/{rel_path} exists but is not linked from SKILL.md — add a reference")

            # Large files should have TOC
            ref_lines = ref_file.read_text(encoding="utf-8").split("\n")
            if len(ref_lines) > 300 and "## Table of Contents" not in ref_file.read_text():
                warnings.append(f"references/{rel_path} is {len(ref_lines)} lines — add a Table of Contents")


# ── Main ───────────────────────────────────────────────────────────────────────

def validate_skill(skill_path_str: str) -> tuple[bool, int, list, list]:
    """
    Validate a skill directory.
    Returns (is_valid, exit_code, errors, warnings)
    """
    skill_path = Path(skill_path_str).resolve()
    errors = []
    warnings = []

    if not skill_path.exists():
        errors.append(f"Skill folder not found: {skill_path}")
        return False, 1, errors, warnings

    if not skill_path.is_dir():
        errors.append(f"Path is not a directory: {skill_path}")
        return False, 1, errors, warnings

    # Run all validators
    validate_folder_name(skill_path, errors, warnings)
    has_skill_md = validate_required_files(skill_path, errors, warnings)

    if not has_skill_md:
        return False, 1, errors, warnings

    fm = validate_frontmatter(skill_path, errors, warnings)
    if fm is not None:
        validate_name_field(fm, skill_path, errors, warnings)
        validate_description_field(fm, errors, warnings)
        validate_compatibility_field(fm, errors, warnings)

    validate_skill_md_body(skill_path, errors, warnings)
    validate_eval_set(skill_path, errors, warnings)
    validate_references(skill_path, errors, warnings)

    is_valid = len(errors) == 0
    exit_code = 0 if is_valid and len(warnings) == 0 else (1 if not is_valid else 2)
    return is_valid, exit_code, errors, warnings


def main():
    if len(sys.argv) != 2:
        print("Usage: python scripts/validate_skill.py <skill-directory>")
        sys.exit(1)

    skill_path = sys.argv[1]
    print(f"\n{bold('skill-master-builder: Skill Validator')}")
    print(f"Checking: {skill_path}\n")

    is_valid, exit_code, errors, warnings = validate_skill(skill_path)

    if errors:
        print(red(f"❌ {len(errors)} error(s) found:\n"))
        for i, err in enumerate(errors, 1):
            print(f"  {i}. {red(err)}")
        print()

    if warnings:
        print(yellow(f"⚠️  {len(warnings)} warning(s):\n"))
        for i, warn in enumerate(warnings, 1):
            print(f"  {i}. {yellow(warn)}")
        print()

    if is_valid:
        if warnings:
            print(yellow("✅ Skill is VALID (with warnings — consider addressing before distribution)"))
        else:
            print(green("✅ Skill is VALID — all checks passed!"))
    else:
        print(red("❌ Skill is INVALID — fix errors before packaging"))

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
