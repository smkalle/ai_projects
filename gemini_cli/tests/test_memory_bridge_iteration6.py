import unittest
from pathlib import Path


class MemoryBridgeUserTestReadinessTest(unittest.TestCase):
    def test_user_test_guide_exists_with_required_sections(self):
        path = Path("docs/USER_TEST_GUIDE.md")
        self.assertTrue(path.exists())
        text = path.read_text(encoding="utf-8")
        for phrase in [
            "not a diagnostic tool",
            "Test Command",
            "Caregiver Review Checklist",
            "Interview Questions",
            "Stop Conditions",
            "Feedback Capture",
        ]:
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
