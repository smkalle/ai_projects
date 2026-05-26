import json
import shutil
import unittest
from pathlib import Path

from memory_bridge_agent.tools import (
    AUDIT_LOG,
    build_analytics_summary,
    create_memory_bridge_kit,
    load_memory_profile,
    read_audit_events,
)


class MemoryBridgeOnboardingAnalyticsTest(unittest.TestCase):
    def setUp(self):
        if AUDIT_LOG.exists():
            self.original_audit = AUDIT_LOG.read_text(encoding="utf-8")
        else:
            self.original_audit = None
        AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
        AUDIT_LOG.write_text("", encoding="utf-8")

    def tearDown(self):
        if self.original_audit is None:
            AUDIT_LOG.unlink(missing_ok=True)
        else:
            AUDIT_LOG.write_text(self.original_audit, encoding="utf-8")

    def test_profile_normalizes_patient_onboarding(self):
        profile = load_memory_profile("examples/memory_profiles/maria_valid.json")
        onboarding = profile["patient_onboarding"]
        self.assertGreaterEqual(len(onboarding["observed_symptoms"]), 1)
        self.assertGreaterEqual(len(onboarding["staff_goals"]), 1)

    def test_workflow_writes_audit_events_and_analytics(self):
        summary = create_memory_bridge_kit("examples/memory_profiles/maria_valid.json")
        output_dir = Path(summary.split("Output directory: ", 1)[1].split(".", 1)[0])
        try:
            events = read_audit_events()
            event_types = {event["event_type"] for event in events}
            self.assertIn("workflow_started", event_types)
            self.assertIn("artifact_generated", event_types)
            self.assertIn("workflow_completed", event_types)
            analytics = build_analytics_summary()
            self.assertEqual(analytics["runs_started"], 1)
            self.assertEqual(analytics["runs_completed"], 1)
            self.assertGreaterEqual(analytics["artifacts_generated"], 7)
            self.assertTrue((output_dir / "patient_onboarding_summary.md").exists())
            self.assertTrue((output_dir / "storyboard_image_prompts.md").exists())
            self.assertTrue((output_dir / "storyboard_scene_1.png").exists())
            self.assertTrue((output_dir / "storyboard_scene_2.png").exists())
            self.assertTrue((output_dir / "storyboard_scene_3.png").exists())
            evaluation = json.loads((output_dir / "evaluation.json").read_text(encoding="utf-8"))
            self.assertTrue(evaluation["caregiver_review_required"])
        finally:
            shutil.rmtree(output_dir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
