import unittest

from memory_bridge_agent.schemas import ProfileValidationError
from memory_bridge_agent.tools import load_memory_profile


class MemoryBridgeProfileValidationTest(unittest.TestCase):
    def test_valid_profile_loads(self):
        profile = load_memory_profile("examples/memory_profiles/maria_valid.json")
        self.assertEqual(profile["person"]["preferred_name"], "Maria")
        self.assertTrue(profile["consent"]["attestation"])
        self.assertGreaterEqual(len(profile["life_events"]), 3)

    def test_missing_consent_blocks(self):
        with self.assertRaisesRegex(ProfileValidationError, "Consent attestation"):
            load_memory_profile("examples/memory_profiles/missing_consent.json")

    def test_unsafe_medical_request_blocks(self):
        with self.assertRaisesRegex(ProfileValidationError, "Unsafe medical request"):
            load_memory_profile("examples/memory_profiles/unsafe_medical_request.json")


if __name__ == "__main__":
    unittest.main()
