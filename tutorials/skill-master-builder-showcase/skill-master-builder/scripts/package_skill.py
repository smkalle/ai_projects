#!/usr/bin/env python3
"""
skill-master-builder: Skill Packager

Packages a skill folder into a distributable .skill file (zip format),
running validation first and excluding build artifacts.

Usage:
    python scripts/package_skill.py <path/to/skill-folder> [output-directory]

Example:
    python scripts/package_skill.py ./my-skill
    python scripts/package_skill.py ./my-skill /mnt/user-data/outputs/
"""

import sys
import zipfile
import fnmatch
from pathlib import Path

# Files/dirs to exclude from package
EXCLUDE_DIRS = {"__pycache__", "node_modules", ".git", ".DS_Store"}
EXCLUDE_FILES = {".DS_Store", ".gitignore", ".env"}
EXCLUDE_GLOBS = {"*.pyc", "*.pyo", "*.log", "*.tmp", "*.swp"}
# Dirs excluded only at skill root
ROOT_EXCLUDE_DIRS = {"evals"}  # evals are for dev, not distribution


def should_exclude(rel_path: Path) -> bool:
    parts = rel_path.parts
    if any(part in EXCLUDE_DIRS for part in parts):
        return True
    if len(parts) > 1 and parts[1] in ROOT_EXCLUDE_DIRS:
        return True
    name = rel_path.name
    if name in EXCLUDE_FILES:
        return True
    return any(fnmatch.fnmatch(name, pat) for pat in EXCLUDE_GLOBS)


def package_skill(skill_path_str: str, output_dir_str: str = None) -> Path | None:
    skill_path = Path(skill_path_str).resolve()

    if not skill_path.exists() or not skill_path.is_dir():
        print(f"❌ Skill folder not found: {skill_path}")
        return None

    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        print(f"❌ SKILL.md not found in {skill_path}")
        return None

    # Run validation first
    print("🔍 Running validation...")
    try:
        # Try to import from same scripts directory
        sys.path.insert(0, str(skill_path.parent.parent / "scripts"))
        # Fall back to inline import
        from validate_skill import validate_skill
        is_valid, exit_code, errors, warnings = validate_skill(str(skill_path))
    except ImportError:
        print("⚠️  Could not import validate_skill — skipping validation")
        is_valid = True
        errors = []
        warnings = []

    if errors:
        print(f"❌ Validation failed with {len(errors)} error(s):")
        for err in errors:
            print(f"   • {err}")
        print("\n   Fix errors before packaging.")
        return None

    if warnings:
        print(f"⚠️  {len(warnings)} warning(s) found (packaging anyway):")
        for warn in warnings:
            print(f"   • {warn}")
    else:
        print("✅ Validation passed\n")

    # Determine output path
    skill_name = skill_path.name
    if output_dir_str:
        output_dir = Path(output_dir_str).resolve()
        output_dir.mkdir(parents=True, exist_ok=True)
    else:
        output_dir = Path.cwd()

    output_file = output_dir / f"{skill_name}.skill"

    # Package into .skill (zip)
    print(f"📦 Packaging {skill_name}...")
    try:
        with zipfile.ZipFile(output_file, "w", zipfile.ZIP_DEFLATED) as zf:
            for file_path in skill_path.rglob("*"):
                if not file_path.is_file():
                    continue
                arcname = file_path.relative_to(skill_path.parent)
                if should_exclude(arcname):
                    print(f"   Skipped: {arcname}")
                    continue
                zf.write(file_path, arcname)
                print(f"   Added:   {arcname}")

        size_kb = output_file.stat().st_size / 1024
        print(f"\n✅ Packaged successfully!")
        print(f"   File: {output_file}")
        print(f"   Size: {size_kb:.1f} KB")
        print(f"\n📎 Install: Claude.ai > Settings > Capabilities > Skills > Upload skill")
        return output_file

    except Exception as e:
        print(f"❌ Packaging failed: {e}")
        return None


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/package_skill.py <skill-folder> [output-directory]")
        print("\nExample:")
        print("  python scripts/package_skill.py ./my-skill")
        print("  python scripts/package_skill.py ./my-skill /mnt/user-data/outputs/")
        sys.exit(1)

    skill_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    result = package_skill(skill_path, output_dir)
    sys.exit(0 if result else 1)


if __name__ == "__main__":
    main()
