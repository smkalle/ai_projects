import io
import unittest
from contextlib import redirect_stdout

from memory_bridge_agent.console import print_user_testing_steps, show_latest_kit


class MemoryBridgeConsoleTest(unittest.TestCase):
    def test_user_testing_steps_print_expected_script(self):
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            print_user_testing_steps()
        output = buffer.getvalue()
        self.assertIn("support aid, not medical advice", output)
        self.assertIn("Run option 1", output)
        self.assertIn("safety blocks", output)

    def test_show_latest_kit_does_not_crash(self):
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            show_latest_kit()
        self.assertTrue(buffer.getvalue())


if __name__ == "__main__":
    unittest.main()
