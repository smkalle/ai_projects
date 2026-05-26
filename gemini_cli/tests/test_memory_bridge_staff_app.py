import unittest

from memory_bridge_staff_app import build_profile


class MemoryBridgeStaffAppTest(unittest.TestCase):
    def test_build_profile_from_staff_form(self):
        profile = build_profile(
            {
                "consent": True,
                "provided_by": "Jane Alvarez",
                "provided_relationship": "daughter",
                "consent_notes": "Reviewed where possible.",
                "preferred_name": "Maria",
                "full_name": "Maria Alvarez",
                "pronouns": "she/her",
                "birth_decade": "1940s",
                "primary_language": "English",
                "contact_name": "Jane",
                "contact_relationship": "daughter",
                "contact_label": "Call Jane",
                "life_events": "1968: Moved to Chicago\n1972: Opened a bakery\n2005: Volunteered in garden",
                "daily_routine": "Morning: Tea\nAfternoon: Garden",
                "favorite_places": "Chicago lakefront\nfamily kitchen",
                "favorite_topics": "gardening\nbaking",
                "calming_phrases": "You are safe.",
                "confusion_triggers": "Rushed schedule changes",
                "privacy_exclusions": "Do not mention finances",
                "caregiver_notes": "Use large text.",
                "observed_symptoms": "Occasional confusion\nRepeats questions",
                "symptom_context": "Busy rooms are harder",
                "staff_goals": "Create orientation board",
                "non_diagnostic_notes": "Use facility protocol.",
            }
        )
        self.assertTrue(profile["consent"]["attestation"])
        self.assertEqual(profile["person"]["preferred_name"], "Maria")
        self.assertEqual(len(profile["life_events"]), 3)
        self.assertEqual(profile["life_events"][0]["year_or_period"], "1968")
        self.assertEqual(profile["daily_routine"][0]["time_label"], "Morning")
        self.assertEqual(len(profile["patient_onboarding"]["observed_symptoms"]), 2)
        self.assertIn("orientation board", profile["patient_onboarding"]["staff_goals"][0])


if __name__ == "__main__":
    unittest.main()
