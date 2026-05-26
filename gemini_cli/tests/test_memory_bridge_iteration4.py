import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from memory_bridge_agent.tools import (
    evaluate_memory_kit,
    generate_memory_timeline,
    load_memory_profile,
)


class MemoryBridgeTimelineTest(unittest.TestCase):
    def setUp(self):
        self.profile = load_memory_profile("examples/memory_profiles/maria_valid.json")

    def test_memory_timeline_png_is_created_and_evaluates(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(generate_memory_timeline(self.profile, tmp))
            self.assertTrue(path.exists())
            with Image.open(path) as img:
                self.assertEqual(img.size, (1650, 1275))
                self.assertEqual(img.mode, "RGB")

            result = json.loads(evaluate_memory_kit(self.profile, {"memory_timeline": str(path)}))
            self.assertTrue(result["caregiver_review_required"])
            self.assertEqual(result["scores"]["privacy_safety"], 5)
            self.assertEqual(result["scores"]["medical_safety_boundary"], 5)


if __name__ == "__main__":
    unittest.main()
