import tempfile
import unittest
from pathlib import Path

from memory_bridge_agent.tools import (
    create_output_dir,
    generate_caregiver_handoff,
    generate_visit_prompts,
    load_memory_profile,
    plan_memory_storyboard,
)


class MemoryBridgeTextKitTest(unittest.TestCase):
    def setUp(self):
        self.profile = load_memory_profile("examples/memory_profiles/maria_valid.json")

    def test_text_artifacts_are_created_and_source_bounded(self):
        with tempfile.TemporaryDirectory() as tmp:
            visit_path = Path(generate_visit_prompts(self.profile, tmp))
            handoff_path = Path(generate_caregiver_handoff(self.profile, tmp))
            storyboard_path = Path(plan_memory_storyboard(self.profile, tmp))

            for path in (visit_path, handoff_path, storyboard_path):
                self.assertTrue(path.exists(), path)
                text = path.read_text(encoding="utf-8")
                self.assertIn("Maria", text)
                self.assertNotIn("diagnosis", text.lower())

            combined = "\n".join(
                path.read_text(encoding="utf-8") for path in (visit_path, handoff_path, storyboard_path)
            )
            self.assertIn("Chicago", combined)
            self.assertIn("Caregiver", combined)

    def test_output_dir_writes_normalized_profile(self):
        path = Path(create_output_dir(self.profile))
        try:
            self.assertTrue((path / "profile_normalized.json").exists())
            self.assertTrue((path / "run_log.txt").exists())
        finally:
            for child in path.iterdir():
                child.unlink()
            path.rmdir()


if __name__ == "__main__":
    unittest.main()
