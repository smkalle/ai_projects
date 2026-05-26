"""Interactive command console for Memory Bridge demos and user tests."""

from __future__ import annotations

import json
from pathlib import Path

from .tools import OUTPUT_ROOT, create_memory_bridge_kit

VALID_PROFILE = "examples/memory_profiles/maria_valid.json"
MISSING_CONSENT_PROFILE = "examples/memory_profiles/missing_consent.json"
UNSAFE_PROFILE = "examples/memory_profiles/unsafe_medical_request.json"


def latest_kit_dir() -> Path | None:
    """Return the most recently modified generated kit directory."""
    if not OUTPUT_ROOT.exists():
        return None
    dirs = [path for path in OUTPUT_ROOT.iterdir() if path.is_dir()]
    if not dirs:
        return None
    return max(dirs, key=lambda path: path.stat().st_mtime)


def print_header() -> None:
    print()
    print("=" * 72)
    print("Memory Bridge Prototype Console")
    print("=" * 72)
    print("Non-clinical orientation, reminiscence, and caregiver support kits.")
    print("Caregiver review is required. Not medical advice.")
    print()


def print_menu() -> None:
    print("Choose an action:")
    print("  1. Run demo with sample caregiver profile")
    print("  2. Run missing-consent safety block")
    print("  3. Run unsafe-medical-request safety block")
    print("  4. Run custom JSON profile")
    print("  5. Show latest generated kit")
    print("  6. Print user-testing steps")
    print("  q. Quit")
    print()


def run_profile(profile_path: str) -> None:
    print(f"Running profile: {profile_path}")
    print(create_memory_bridge_kit(profile_path))
    print()


def show_latest_kit() -> None:
    kit_dir = latest_kit_dir()
    if kit_dir is None:
        print("No generated Memory Bridge kits found.")
        return

    print(f"Latest kit: {kit_dir}")
    for path in sorted(kit_dir.iterdir()):
        if path.is_file():
            print(f"  - {path.name}")

    evaluation_path = kit_dir / "evaluation.json"
    if evaluation_path.exists():
        evaluation = json.loads(evaluation_path.read_text(encoding="utf-8"))
        print()
        print(f"Evaluation passed: {evaluation.get('overall_passed')}")
        print(f"Caregiver review required: {evaluation.get('caregiver_review_required')}")
        if evaluation.get("issues"):
            print("Issues:")
            for issue in evaluation["issues"]:
                print(f"  - {issue.get('severity')}: {issue.get('description')}")
    print()


def print_user_testing_steps() -> None:
    print("Demo and user-testing steps:")
    print("  1. Explain the boundary: support aid, not medical advice.")
    print("  2. Run option 1 to generate the sample kit.")
    print("  3. Open the generated output directory shown in the console.")
    print("  4. Review orientation_board.png and memory_timeline.png first.")
    print("  5. Review visit_prompts.md, caregiver_handoff.md, and storyboard.md.")
    print("  6. Open evaluation.json and confirm pass/fail plus review notes.")
    print("  7. Ask the tester what they would print, use, remove, or correct.")
    print("  8. Run options 2 and 3 to demonstrate pre-generation safety blocks.")
    print("  9. Capture ratings for usefulness, dignity, readability, privacy, and trust.")
    print()


def run_console() -> None:
    """Run the Memory Bridge demo console."""
    print_header()
    while True:
        print_menu()
        choice = input("Action: ").strip().lower()
        print()
        if choice == "1":
            run_profile(VALID_PROFILE)
        elif choice == "2":
            run_profile(MISSING_CONSENT_PROFILE)
        elif choice == "3":
            run_profile(UNSAFE_PROFILE)
        elif choice == "4":
            profile_path = input("Path to JSON profile: ").strip()
            if profile_path:
                run_profile(profile_path)
            else:
                print("No profile path entered.")
        elif choice == "5":
            show_latest_kit()
        elif choice == "6":
            print_user_testing_steps()
        elif choice in {"q", "quit", "exit"}:
            print("Exiting Memory Bridge console.")
            return
        else:
            print("Unknown action. Choose 1-6 or q.")


if __name__ == "__main__":
    run_console()
