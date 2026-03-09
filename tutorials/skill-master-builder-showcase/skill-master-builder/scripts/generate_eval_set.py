#!/usr/bin/env python3
"""
skill-master-builder: Eval Set Generator

Reads a SKILL.md and generates a starter trigger-eval.json
by extracting trigger phrases from the description and producing
both trigger=true and trigger=false test stubs.

Also calls Claude API to enrich the eval set if ANTHROPIC_API_KEY is set,
or operates in "stub mode" for offline use.

Usage:
    python scripts/generate_eval_set.py <path/to/skill-folder> [--stub]

Options:
    --stub    Generate stub test cases only (no API calls)

Output:
    <skill-folder>/evals/trigger-eval.json
"""

import sys
import os
import re
import json
import argparse
from pathlib import Path
from datetime import date

try:
    import yaml
except ImportError:
    print("❌ Missing dependency: pyyaml")
    print("   Fix: pip install pyyaml --break-system-packages")
    sys.exit(1)


# ── Helpers ────────────────────────────────────────────────────────────────────

def extract_frontmatter(skill_md_path: Path) -> dict | None:
    content = skill_md_path.read_text(encoding="utf-8")
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return None
    try:
        return yaml.safe_load(match.group(1))
    except yaml.YAMLError:
        return None


def extract_trigger_phrases(description: str) -> list[str]:
    """Extract quoted trigger phrases and 'Use when' conditions from description."""
    phrases = []
    # Quoted phrases
    quoted = re.findall(r'"([^"]{5,80})"', description)
    phrases.extend(quoted)
    # "user says/mentions/asks" patterns
    patterns = re.findall(r'(?:user (?:says?|asks?|mentions?|requests?|types?)[:\s]+)([^,.]+)', description, re.IGNORECASE)
    phrases.extend([p.strip().strip('"') for p in patterns])
    # "Use when" conditions
    use_when = re.findall(r'[Uu]se when[:\s]+([^.]+)', description)
    for uw in use_when:
        sub = re.split(r',|;| or ', uw)
        phrases.extend([s.strip() for s in sub if len(s.strip()) > 5])
    return list(dict.fromkeys(phrases))  # deduplicate preserving order


def generate_stub_eval(skill_name: str, description: str, trigger_phrases: list[str]) -> dict:
    """Generate a minimal stub eval set from extracted trigger phrases."""
    eval_set = []
    counter = {"trigger": 0, "functional": 0}

    def tid(t): counter[t] += 1; return f"{t}-{counter[t]:03d}"

    # Trigger=true from extracted phrases
    for phrase in trigger_phrases[:5]:
        eval_set.append({
            "id": tid("trigger"),
            "type": "trigger",
            "query": phrase,
            "should_trigger": True,
            "rationale": "Extracted from skill description trigger phrases"
        })

    # Fill to 5 if not enough phrases
    while counter["trigger"] < 5:
        eval_set.append({
            "id": tid("trigger"),
            "type": "trigger",
            "query": f"[TODO: Add trigger=true query #{counter['trigger']} for {skill_name}]",
            "should_trigger": True,
            "rationale": "[TODO: Explain why this should trigger the skill]"
        })

    # Trigger=false stubs
    unrelated_stubs = [
        ("What's the weather in Bangalore today?", "Completely unrelated query"),
        ("Help me write a haiku about coffee", "Creative writing — unrelated domain"),
        ("What is the Pythagorean theorem?", "General knowledge question — no skill needed"),
    ]
    for query, rationale in unrelated_stubs:
        eval_set.append({
            "id": tid("trigger"),
            "type": "trigger",
            "query": query,
            "should_trigger": False,
            "rationale": rationale
        })

    # Functional stubs
    for i in range(1, 4):
        labels = ["happy-path", "edge-case", "error-case"]
        eval_set.append({
            "id": tid("functional"),
            "type": "functional",
            "query": f"[TODO: Add functional test #{i} ({labels[i-1]}) for {skill_name}]",
            "context": "[TODO: Describe the input or setup required]",
            "expected_behavior": "[TODO: Describe what the skill should do]",
            "assertions": [
                "[TODO: Specific, checkable condition 1]",
                "[TODO: Specific, checkable condition 2]"
            ],
            "edge_case": i > 1,
            "notes": f"[TODO: Add notes for {labels[i-1]} scenario]"
        })

    return {
        "skill_name": skill_name,
        "skill_version": "1.0.0",
        "generated_date": str(date.today()),
        "generated_by": "skill-master-builder/generate_eval_set.py",
        "eval_set": eval_set
    }


def generate_api_eval(skill_name: str, description: str, skill_md_content: str) -> dict | None:
    """Use Claude API to generate a rich eval set."""
    try:
        import urllib.request
        import urllib.error
    except ImportError:
        return None

    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        return None

    prompt = f"""You are an expert at writing test cases for Claude skills.

Given this skill:
- Name: {skill_name}
- Description: {description}

Generate a comprehensive eval set with:
- 7 trigger=true test cases (obvious, paraphrased, implicit, domain-jargon, terse, context-heavy, multi-intent)
- 4 trigger=false test cases (unrelated, adjacent-but-out-of-scope, too-generic, different-tool)
- 4 functional test cases (happy-path, complex-input, edge-case, error-case)

Return ONLY valid JSON matching this schema exactly:
{{
  "eval_set": [
    {{
      "id": "trigger-001",
      "type": "trigger",
      "query": "realistic user message",
      "should_trigger": true,
      "rationale": "one sentence explanation"
    }},
    {{
      "id": "functional-001",
      "type": "functional", 
      "query": "realistic user request",
      "context": "any required setup or input context",
      "expected_behavior": "what the skill should do",
      "assertions": ["checkable condition 1", "checkable condition 2"],
      "edge_case": false,
      "notes": "optional notes"
    }}
  ]
}}

Make queries realistic and specific to the skill's domain. Trigger=false cases should be plausibly adjacent but clearly out of scope."""

    payload = json.dumps({
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 2000,
        "messages": [{"role": "user", "content": prompt}]
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01"
        }
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read())
        text = result["content"][0]["text"].strip()
        # Strip markdown fences if present
        text = re.sub(r'^```json\s*', '', text)
        text = re.sub(r'\s*```$', '', text)
        parsed = json.loads(text)
        return {
            "skill_name": skill_name,
            "skill_version": "1.0.0",
            "generated_date": str(date.today()),
            "generated_by": "skill-master-builder/generate_eval_set.py (Claude API)",
            "eval_set": parsed["eval_set"]
        }
    except Exception as e:
        print(f"⚠️  API enrichment failed ({e}) — falling back to stub mode")
        return None


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Generate eval set for a Claude skill")
    parser.add_argument("skill_path", help="Path to skill directory")
    parser.add_argument("--stub", action="store_true", help="Generate stubs only (no API)")
    args = parser.parse_args()

    skill_path = Path(args.skill_path).resolve()
    skill_md = skill_path / "SKILL.md"

    if not skill_md.exists():
        print(f"❌ SKILL.md not found at {skill_md}")
        sys.exit(1)

    fm = extract_frontmatter(skill_md)
    if not fm:
        print("❌ Could not parse SKILL.md frontmatter")
        sys.exit(1)

    skill_name = fm.get("name", skill_path.name)
    description = fm.get("description", "")
    skill_md_content = skill_md.read_text(encoding="utf-8")

    print(f"\n📋 Generating eval set for: {skill_name}")
    print(f"   Description: {description[:80]}{'...' if len(description) > 80 else ''}\n")

    trigger_phrases = extract_trigger_phrases(description)
    print(f"   Found {len(trigger_phrases)} trigger phrase(s) in description")

    # Try API enrichment first (unless --stub)
    eval_data = None
    if not args.stub:
        print("   Attempting API-enriched eval generation...")
        eval_data = generate_api_eval(skill_name, description, skill_md_content)

    if eval_data is None:
        print("   Using stub mode...")
        eval_data = generate_stub_eval(skill_name, description, trigger_phrases)

    # Write output
    evals_dir = skill_path / "evals"
    evals_dir.mkdir(exist_ok=True)
    output_path = evals_dir / "trigger-eval.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(eval_data, f, indent=2)

    total = len(eval_data["eval_set"])
    trigger_true = sum(1 for t in eval_data["eval_set"] if t.get("type") == "trigger" and t.get("should_trigger"))
    trigger_false = sum(1 for t in eval_data["eval_set"] if t.get("type") == "trigger" and not t.get("should_trigger"))
    functional = sum(1 for t in eval_data["eval_set"] if t.get("type") == "functional")

    print(f"\n✅ Eval set written to: {output_path}")
    print(f"   Total test cases: {total}")
    print(f"   - trigger=true:  {trigger_true}")
    print(f"   - trigger=false: {trigger_false}")
    print(f"   - functional:    {functional}")

    stubs_exist = any("[TODO" in json.dumps(t) for t in eval_data["eval_set"])
    if stubs_exist:
        print(f"\n⚠️  Some test cases contain [TODO] placeholders — fill them in before running evals")

    print("\n   Next step: review and customize the eval set, then validate your skill:")
    print(f"   python scripts/validate_skill.py {skill_path}")


if __name__ == "__main__":
    main()
