import json
import tempfile
import unittest
from pathlib import Path

from memory_bridge_agent.tools import (
    evaluate_memory_kit,
    generate_caregiver_handoff,
    generate_visit_prompts,
    load_memory_profile,
    plan_memory_storyboard,
)


class MemoryBridgeEvaluatorTest(unittest.TestCase):
    def setUp(self):
        self.profile = load_memory_profile("examples/memory_profiles/maria_valid.json")

    def _make_clean_artifacts(self, tmp):
        return {
            "visit_prompts": generate_visit_prompts(self.profile, tmp),
            "caregiver_handoff": generate_caregiver_handoff(self.profile, tmp),
            "storyboard": plan_memory_storyboard(self.profile, tmp),
        }

    def test_clean_kit_returns_parseable_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = json.loads(evaluate_memory_kit(self.profile, self._make_clean_artifacts(tmp)))
            self.assertIn("overall_passed", result)
            self.assertTrue(result["caregiver_review_required"])
            self.assertIn("privacy_safety", result["scores"])

    def test_privacy_leak_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "bad.md"
            bad.write_text("Do not mention finances", encoding="utf-8")
            result = json.loads(evaluate_memory_kit(self.profile, {"bad": str(bad)}))
            self.assertFalse(result["overall_passed"])
            self.assertEqual(result["scores"]["privacy_safety"], 1)
            self.assertFalse(result["regeneration_recommended"])

    def test_medical_advice_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "bad.md"
            bad.write_text("You should take a different medication dosage.", encoding="utf-8")
            result = json.loads(evaluate_memory_kit(self.profile, {"bad": str(bad)}))
            self.assertFalse(result["overall_passed"])
            self.assertEqual(result["scores"]["medical_safety_boundary"], 1)


if __name__ == "__main__":
    unittest.main()
