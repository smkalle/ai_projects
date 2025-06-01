#!/usr/bin/env python3
"""Demo script for Medical AI Assistant MVP."""

import asyncio
import json
from datetime import datetime

from src.agents import MVPMedicalTools, MVPTriageAgent


async def demo_triage_agent():
    """Demonstrate the triage agent functionality."""
    print("🏥 Medical AI Assistant MVP - Triage Agent Demo")
    print("=" * 50)

    agent = MVPTriageAgent()

    # Test cases
    test_cases = [
        {
            "symptoms": "high fever and chills",
            "age": 8,
            "severity": "high",
            "description": "Child with high fever",
        },
        {
            "symptoms": "severe bleeding from cut",
            "age": 25,
            "severity": "emergency",
            "description": "Adult with severe bleeding",
        },
        {
            "symptoms": "mild headache",
            "age": 30,
            "severity": "low",
            "description": "Adult with mild headache",
        },
        {
            "symptoms": "difficulty breathing",
            "age": 65,
            "severity": "high",
            "description": "Elderly with breathing issues",
        },
        {
            "symptoms": "mild fever",
            "age": 1,
            "severity": "medium",
            "description": "Infant with fever (should escalate)",
        },
    ]

    for i, case in enumerate(test_cases, 1):
        print(f"\n📋 Test Case {i}: {case['description']}")
        print(f"   Symptoms: {case['symptoms']}")
        print(f"   Age: {case['age']} years")
        print(f"   Severity: {case['severity']}")

        assessment = await agent.assess_symptoms(
            symptoms=case["symptoms"], age=case["age"], severity=case["severity"]
        )

        print(f"   🤖 AI Assessment:")
        print(f"      Urgency: {assessment.urgency}")
        print(f"      Escalate: {'Yes' if assessment.escalate else 'No'}")
        print(f"      Confidence: {assessment.confidence:.1%}")
        print(f"      Actions: {', '.join(assessment.actions)}")
        if assessment.red_flags:
            print(f"      🚩 Red Flags: {', '.join(assessment.red_flags)}")


def demo_medical_tools():
    """Demonstrate the medical tools functionality."""
    print("\n\n💊 Medical Tools Demo")
    print("=" * 30)

    tools = MVPMedicalTools()

    # Test medication dosage calculations
    test_medications = [
        {
            "medication": "acetaminophen",
            "weight_kg": 25.0,
            "age_years": 8,
            "description": "Child acetaminophen dose",
        },
        {
            "medication": "ibuprofen",
            "weight_kg": 70.0,
            "age_years": 25,
            "description": "Adult ibuprofen dose",
        },
        {
            "medication": "paracetamol",
            "weight_kg": 15.0,
            "age_years": 5,
            "description": "Child paracetamol dose",
        },
        {
            "medication": "unknown_med",
            "weight_kg": 25.0,
            "age_years": 8,
            "description": "Unknown medication (should show error)",
        },
    ]

    for i, case in enumerate(test_medications, 1):
        print(f"\n💊 Medication {i}: {case['description']}")
        print(f"   Medication: {case['medication']}")
        print(f"   Weight: {case['weight_kg']} kg")
        print(f"   Age: {case['age_years']} years")

        result = tools.calculate_dose(
            medication=case["medication"],
            weight_kg=case["weight_kg"],
            age_years=case["age_years"],
        )

        if "error" in result:
            print(f"   ❌ Error: {result['error']}")
            print(f"   Available: {', '.join(result['available_medications'])}")
        else:
            print(f"   ✅ Dose: {result['dose_mg']} mg ({result['dose_type']})")
            print(f"   Frequency: {result['frequency']}")
            print(f"   Max daily: {result['max_daily_mg']} mg")
            print(f"   ⚠️  {result['warning']}")


def demo_summary():
    """Show demo summary and next steps."""
    print("\n\n🎯 MVP Demo Summary")
    print("=" * 25)
    print("✅ Triage Agent: Basic symptom assessment with decision trees")
    print("✅ Medical Tools: Medication dosage calculations")
    print("✅ Age-based adjustments: Infant and elderly considerations")
    print("✅ Severity overrides: Emergency escalation")
    print("✅ Safety features: Red flags and escalation logic")

    print("\n🚀 Next Steps for Full MVP:")
    print("1. Start FastAPI server: python -m src.main")
    print("2. Test API endpoints:")
    print("   - Health check: GET /api/health")
    print("   - Create case: POST /api/cases")
    print("   - List cases: GET /api/cases")
    print("   - Upload photos: POST /api/cases/{id}/photos")
    print("   - Doctor review: POST /api/cases/{id}/review")

    print("\n📊 Test Coverage:")
    print("   - Run tests: python -m pytest tests/ -v")
    print("   - Code quality: black src/ tests/ && ruff check src/ tests/")

    print(f"\n⏰ Demo completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


async def main():
    """Run the complete demo."""
    await demo_triage_agent()
    demo_medical_tools()
    demo_summary()


if __name__ == "__main__":
    asyncio.run(main()) 