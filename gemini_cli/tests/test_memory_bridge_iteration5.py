import json
import re
import shutil
import unittest
from pathlib import Path

from memory_bridge_agent.agent import root_agent
from memory_bridge_agent.tools import create_memory_bridge_kit


class MemoryBridgeEndToEndWorkflowTest(unittest.TestCase):
    def _extract_output_dir(self, summary: str) -> Path:
        match = re.search(r"Output directory: ([^.]+)\.", summary)
        self.assertIsNotNone(match, summary)
        return Path(match.group(1))

    def test_agent_has_workflow_tool(self):
        self.assertEqual(root_agent.name, "memory_bridge_agent")
        self.assertTrue(root_agent.tools)

    def test_end_to_end_valid_profile_creates_complete_kit(self):
        summary = create_memory_bridge_kit("examples/memory_profiles/maria_valid.json")
        output_dir = self._extract_output_dir(summary)
        try:
            expected = [
                "profile_normalized.json",
                "patient_onboarding_summary.md",
                "visit_prompts.md",
                "caregiver_handoff.md",
                "storyboard.md",
                "storyboard_image_prompts.md",
                "storyboard_scene_1.png",
                "storyboard_scene_2.png",
                "storyboard_scene_3.png",
                "orientation_board.png",
                "memory_timeline.png",
                "evaluation.json",
                "run_log.txt",
            ]
            for filename in expected:
                self.assertTrue((output_dir / filename).exists(), filename)
            evaluation = json.loads((output_dir / "evaluation.json").read_text(encoding="utf-8"))
            self.assertTrue(evaluation["caregiver_review_required"])
            self.assertIn("Overall passed", summary)
            onboarding = (output_dir / "patient_onboarding_summary.md").read_text(encoding="utf-8")
            self.assertIn("Observed Symptoms", onboarding)
            prompts = (output_dir / "storyboard_image_prompts.md").read_text(encoding="utf-8")
            self.assertIn("Negative prompt", prompts)
        finally:
            shutil.rmtree(output_dir, ignore_errors=True)

    def test_invalid_profiles_stop_before_generation(self):
        missing = create_memory_bridge_kit("examples/memory_profiles/missing_consent.json")
        unsafe = create_memory_bridge_kit("examples/memory_profiles/unsafe_medical_request.json")
        self.assertIn("stopped before generation", missing)
        self.assertIn("Consent attestation", missing)
        self.assertIn("stopped before generation", unsafe)
        self.assertIn("Unsafe medical request", unsafe)


if __name__ == "__main__":
    unittest.main()
