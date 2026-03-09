#!/usr/bin/env python3
"""
validate_onboarding_plan.py

Validates a generated HR onboarding plan document to ensure all required
sections, compliance items, and phase deliverables are present.

Usage:
    python scripts/validate_onboarding_plan.py <path-to-onboarding-plan.md>

Exit codes:
    0 = all checks passed
    1 = validation errors found
"""

import sys
import re
from pathlib import Path


# Required sections that must appear in a generated onboarding plan
REQUIRED_SECTIONS = [
    "New Hire Card",
    "Pre-Boarding",
    "Day 1",
    "Week 1",
    "30-Day",
    "60-Day",
    "90-Day",
]

# Required compliance items that must be mentioned
REQUIRED_COMPLIANCE_ITEMS = [
    "I-9",
    "W-4",
    "state new hire report",
]

# Required fields in the New Hire Card block
REQUIRED_HIRE_CARD_FIELDS = [
    "Name",
    "Role",
    "Start Date",
    "Work Type",
    "State",
]

# Owner keywords — every action item should have an owner assigned
OWNER_KEYWORDS = ["HR", "Manager", "IT", "Buddy", "New Hire"]


def load_file(path: str) -> str:
    try:
        return Path(path).read_text(encoding="utf-8")
    except FileNotFoundError:
        print(f"FAIL: File not found: {path}")
        sys.exit(1)
    except Exception as e:
        print(f"FAIL: Could not read file: {e}")
        sys.exit(1)


def check_required_sections(content: str) -> list[str]:
    errors = []
    for section in REQUIRED_SECTIONS:
        pattern = re.compile(re.escape(section), re.IGNORECASE)
        if not pattern.search(content):
            errors.append(f"Missing required section: '{section}'")
    return errors


def check_compliance_items(content: str) -> list[str]:
    errors = []
    for item in REQUIRED_COMPLIANCE_ITEMS:
        pattern = re.compile(re.escape(item), re.IGNORECASE)
        if not pattern.search(content):
            errors.append(f"Missing compliance item: '{item}' not mentioned")
    return errors


def check_i9_deadline(content: str) -> list[str]:
    errors = []
    # I-9 deadline (Day 3) must be explicitly stated
    if not re.search(r"I-9.{0,100}(day\s*3|3\s*business\s*days|third\s*business\s*day)", content, re.IGNORECASE):
        errors.append(
            "I-9 Day 3 deadline not explicitly stated — this is a legal requirement"
        )
    return errors


def check_new_hire_card(content: str) -> list[str]:
    errors = []
    if "NEW HIRE CARD" not in content.upper():
        errors.append("New Hire Card not found — intake summary required before plan")
        return errors
    # Check for required fields within the card section
    card_match = re.search(
        r"NEW HIRE CARD.*?(?=##|\Z)", content, re.IGNORECASE | re.DOTALL
    )
    if card_match:
        card_block = card_match.group(0)
        for field in REQUIRED_HIRE_CARD_FIELDS:
            if field.lower() not in card_block.lower():
                errors.append(f"New Hire Card missing field: '{field}'")
    return errors


def check_owner_assignments(content: str) -> list[str]:
    """Warn if action items appear without any owner assignment."""
    errors = []
    # Find checklist items (lines with - [ ] or numbered items with ":")
    checklist_lines = re.findall(r"^[-*]\s+\[[ x]\].+$", content, re.MULTILINE)
    if checklist_lines:
        unowned = [
            line for line in checklist_lines
            if not any(owner.lower() in line.lower() for owner in OWNER_KEYWORDS)
        ]
        if len(unowned) > 5:
            errors.append(
                f"Warning: {len(unowned)} action items found with no obvious owner "
                f"(HR/Manager/IT/Buddy). Assign owners to all items."
            )
    return errors


def check_all_phases_present(content: str) -> list[str]:
    """Verify all 6 phases are present and in order."""
    errors = []
    phases = [
        ("Phase 1", "Pre-Boarding"),
        ("Phase 2", "Day 1"),
        ("Phase 3", "Week 1"),
        ("Phase 4", "30-Day"),
        ("Phase 5", "60-Day"),
        ("Phase 6", "90-Day"),
    ]
    for phase_label, phase_name in phases:
        has_phase = (
            re.search(re.escape(phase_label), content, re.IGNORECASE)
            or re.search(re.escape(phase_name), content, re.IGNORECASE)
        )
        if not has_phase:
            errors.append(f"Missing phase: {phase_label} ({phase_name})")
    return errors


def check_closure_checklist(content: str) -> list[str]:
    """90-day close must include a closure checklist."""
    errors = []
    if "90" in content:
        # Look for a checklist near the 90-day section
        ninety_day_section = re.search(
            r"90.{0,200}?(\[[ x]\])", content, re.IGNORECASE | re.DOTALL
        )
        if not ninety_day_section:
            errors.append(
                "No closure checklist found near 90-day section — required for legal compliance"
            )
    return errors


def run_validation(filepath: str) -> None:
    print(f"\nValidating onboarding plan: {filepath}")
    print("=" * 60)

    content = load_file(filepath)
    all_errors = []

    checks = [
        ("Required sections", check_required_sections(content)),
        ("Compliance items", check_compliance_items(content)),
        ("I-9 deadline", check_i9_deadline(content)),
        ("New Hire Card", check_new_hire_card(content)),
        ("Owner assignments", check_owner_assignments(content)),
        ("All phases present", check_all_phases_present(content)),
        ("Closure checklist", check_closure_checklist(content)),
    ]

    for check_name, errors in checks:
        if errors:
            print(f"\nFAIL: {check_name}")
            for err in errors:
                print(f"  - {err}")
            all_errors.extend(errors)
        else:
            print(f"PASS: {check_name}")

    print("\n" + "=" * 60)
    if all_errors:
        print(f"RESULT: {len(all_errors)} issue(s) found. Fix before delivering.")
        sys.exit(1)
    else:
        print("RESULT: All checks passed. Onboarding plan is valid.")
        sys.exit(0)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/validate_onboarding_plan.py <path-to-plan.md>")
        sys.exit(1)
    run_validation(sys.argv[1])
