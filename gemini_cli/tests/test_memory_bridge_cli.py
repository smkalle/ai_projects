import subprocess
import unittest


class MemoryBridgeCliTest(unittest.TestCase):
    def test_module_cli_runs_valid_profile(self):
        result = subprocess.run(
            ["python3", "-m", "memory_bridge_agent", "examples/memory_profiles/maria_valid.json"],
            check=True,
            text=True,
            capture_output=True,
        )
        self.assertIn("Memory Bridge kit completed", result.stdout)
        self.assertIn("Caregiver review is required", result.stdout)


if __name__ == "__main__":
    unittest.main()
