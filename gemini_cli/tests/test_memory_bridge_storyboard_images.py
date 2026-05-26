import tempfile
import unittest
from pathlib import Path

from PIL import Image

from memory_bridge_agent.tools import generate_storyboard_images, load_memory_profile


class MemoryBridgeStoryboardImagesTest(unittest.TestCase):
    def test_storyboard_images_are_generated(self):
        profile = load_memory_profile("examples/memory_profiles/maria_valid.json")
        with tempfile.TemporaryDirectory() as tmp:
            paths = [Path(path) for path in generate_storyboard_images(profile, tmp)]
            self.assertEqual(len(paths), 3)
            for path in paths:
                self.assertTrue(path.exists(), path)
                with Image.open(path) as img:
                    self.assertEqual(img.size, (1280, 720))
                    self.assertEqual(img.mode, "RGB")


if __name__ == "__main__":
    unittest.main()
