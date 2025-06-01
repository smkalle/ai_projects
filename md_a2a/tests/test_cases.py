"""Tests for cases API endpoints."""

import io
import json
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient


class TestCasesAPI:
    """Test cases API endpoints."""

    def test_create_case(self, client: TestClient, sample_case_data: dict) -> None:
        """Test creating a new case."""
        response = client.post("/api/cases", json=sample_case_data)

        assert response.status_code == 200
        data = response.json()

        assert "case_id" in data
        assert data["symptoms"] == sample_case_data["symptoms"]
        assert data["patient"]["age_years"] == sample_case_data["patient"]["age_years"]
        assert data["ai_assessment"] is not None
        assert data["status"] == "new"

        # Check AI assessment structure
        assessment = data["ai_assessment"]
        assert "urgency" in assessment
        assert "actions" in assessment
        assert "escalate" in assessment
        assert isinstance(assessment["actions"], list)

    def test_create_case_fever_high_urgency(
        self, client: TestClient, sample_patient_data: dict
    ) -> None:
        """Test creating a case with high fever results in high urgency."""
        case_data = {
            "patient": sample_patient_data,
            "symptoms": "high fever and chills",
            "severity": "high",
        }

        response = client.post("/api/cases", json=case_data)

        assert response.status_code == 200
        data = response.json()

        assessment = data["ai_assessment"]
        assert assessment["urgency"] == "high"
        assert assessment["escalate"] is True
        assert "high_fever" in assessment["red_flags"]

    def test_create_case_emergency_severity(
        self, client: TestClient, sample_patient_data: dict
    ) -> None:
        """Test creating a case with emergency severity."""
        case_data = {
            "patient": sample_patient_data,
            "symptoms": "mild headache",
            "severity": "emergency",
        }

        response = client.post("/api/cases", json=case_data)

        assert response.status_code == 200
        data = response.json()

        assessment = data["ai_assessment"]
        assert assessment["urgency"] == "emergency"
        assert assessment["escalate"] is True
        assert "reported_as_emergency" in assessment["red_flags"]

    def test_get_case(self, client: TestClient, sample_case_data: dict) -> None:
        """Test retrieving a specific case."""
        # First create a case
        create_response = client.post("/api/cases", json=sample_case_data)
        case_id = create_response.json()["case_id"]

        # Then retrieve it
        response = client.get(f"/api/cases/{case_id}")

        assert response.status_code == 200
        data = response.json()

        assert data["case_id"] == case_id
        assert data["symptoms"] == sample_case_data["symptoms"]
        assert data["ai_assessment"] is not None

    def test_get_case_not_found(self, client: TestClient) -> None:
        """Test retrieving a non-existent case."""
        response = client.get("/api/cases/non-existent-id")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_get_cases_list(self, client: TestClient, sample_case_data: dict) -> None:
        """Test retrieving list of cases."""
        # Create a few cases
        case_ids = []
        for i in range(3):
            case_data = sample_case_data.copy()
            case_data["symptoms"] = f"symptoms {i}"
            response = client.post("/api/cases", json=case_data)
            case_ids.append(response.json()["case_id"])

        # Get all cases
        response = client.get("/api/cases")

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)
        assert len(data) >= 3

        # Check that our cases are in the list
        retrieved_ids = [case["case_id"] for case in data]
        for case_id in case_ids:
            assert case_id in retrieved_ids

    def test_get_cases_with_status_filter(
        self, client: TestClient, sample_case_data: dict
    ) -> None:
        """Test retrieving cases with status filter."""
        # Create a case
        response = client.post("/api/cases", json=sample_case_data)
        case_id = response.json()["case_id"]

        # Get cases with 'new' status
        response = client.get("/api/cases?status=new")

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)
        assert len(data) >= 1

        # All cases should have 'new' status
        for case in data:
            assert case["status"] == "new"

    def test_review_case(
        self, client: TestClient, sample_case_data: dict, sample_doctor_review: dict
    ) -> None:
        """Test doctor reviewing a case."""
        # First create a case
        create_response = client.post("/api/cases", json=sample_case_data)
        case_id = create_response.json()["case_id"]

        # Review the case
        response = client.post(
            f"/api/cases/{case_id}/review", json=sample_doctor_review
        )

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "reviewed"
        assert data["case_id"] == case_id

        # Verify the case was updated
        get_response = client.get(f"/api/cases/{case_id}")
        case_data = get_response.json()

        assert case_data["status"] == "reviewed"
        assert case_data["doctor_review"] == sample_doctor_review["review"]
        assert case_data["doctor_id"] == sample_doctor_review["doctor_id"]

    def test_review_case_not_found(
        self, client: TestClient, sample_doctor_review: dict
    ) -> None:
        """Test reviewing a non-existent case."""
        response = client.post(
            "/api/cases/non-existent-id/review", json=sample_doctor_review
        )

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_upload_photo(self, client: TestClient, sample_case_data: dict) -> None:
        """Test uploading a photo to a case."""
        # First create a case
        create_response = client.post("/api/cases", json=sample_case_data)
        case_id = create_response.json()["case_id"]

        # Create a fake image file
        image_content = b"fake image content"
        files = {"file": ("test_image.jpg", io.BytesIO(image_content), "image/jpeg")}

        # Upload the photo
        response = client.post(f"/api/cases/{case_id}/photos", files=files)

        assert response.status_code == 200
        data = response.json()

        assert "photo_url" in data
        assert data["case_id"] == case_id
        assert "uploaded_at" in data
        assert "/static/photos/" in data["photo_url"]

        # Verify the case was updated with photo
        get_response = client.get(f"/api/cases/{case_id}")
        case_data = get_response.json()

        assert len(case_data["photos"]) == 1
        assert case_data["photos"][0]["url"] == data["photo_url"]

    def test_upload_photo_invalid_file(
        self, client: TestClient, sample_case_data: dict
    ) -> None:
        """Test uploading an invalid file type."""
        # First create a case
        create_response = client.post("/api/cases", json=sample_case_data)
        case_id = create_response.json()["case_id"]

        # Try to upload a text file
        files = {"file": ("test.txt", io.BytesIO(b"text content"), "text/plain")}

        response = client.post(f"/api/cases/{case_id}/photos", files=files)

        assert response.status_code == 400
        assert "Invalid file type" in response.json()["detail"]

    def test_upload_photo_case_not_found(self, client: TestClient) -> None:
        """Test uploading photo to non-existent case."""
        files = {"file": ("test.jpg", io.BytesIO(b"image"), "image/jpeg")}

        response = client.post("/api/cases/non-existent-id/photos", files=files)

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_create_case_invalid_data(self, client: TestClient) -> None:
        """Test creating a case with invalid data."""
        invalid_data = {
            "patient": {"name": "Test"},  # Missing required fields
            "symptoms": "",  # Empty symptoms
        }

        response = client.post("/api/cases", json=invalid_data)

        assert response.status_code == 422  # Validation error

    def test_infant_case_escalation(self, client: TestClient) -> None:
        """Test that infant cases are automatically escalated."""
        case_data = {
            "patient": {
                "name": "Baby Test",
                "age_years": 1,
                "gender": "female",
                "weight_kg": 10.0,
            },
            "symptoms": "mild fever",
            "severity": "low",
        }

        response = client.post("/api/cases", json=case_data)

        assert response.status_code == 200
        data = response.json()

        assessment = data["ai_assessment"]
        assert assessment["escalate"] is True  # Should be escalated due to age
        assert assessment["urgency"] in ["medium", "high"]  # Should be upgraded


class TestAIEnhancedEndpoints:
    """Test the new AI-enhanced endpoints."""

    def test_ai_assessment_endpoint(self, client: TestClient) -> None:
        """Test the direct AI assessment endpoint."""
        assessment_data = {
            "symptoms": "high fever and headache",
            "age": 8,
            "severity": "medium"
        }

        response = client.post("/api/v2/cases/assess", json=assessment_data)

        assert response.status_code == 200
        data = response.json()

        # Check top-level structure
        assert "assessment" in data
        assert "ai_used" in data
        assert "timestamp" in data

        # Check AI assessment structure
        assessment = data["assessment"]
        assert "urgency" in assessment
        assert "actions" in assessment
        assert "escalate" in assessment
        assert "confidence" in assessment

        # Verify AI-specific fields
        assert isinstance(data["ai_used"], bool)
        assert isinstance(assessment["confidence"], float)
        assert 0.0 <= assessment["confidence"] <= 1.0

    def test_ai_dosage_endpoint(self, client: TestClient) -> None:
        """Test the AI dosage calculation endpoint."""
        dosage_data = {
            "medication": "acetaminophen",
            "weight_kg": 25.0,
            "age_years": 8
        }

        response = client.post("/api/v2/cases/dosage", json=dosage_data)

        assert response.status_code == 200
        data = response.json()

        # Check top-level structure
        assert "dosage" in data
        assert "ai_used" in data
        assert "timestamp" in data

        # Check dosage calculation structure
        dosage = data["dosage"]
        assert "medication" in dosage
        assert "dose_mg" in dosage
        assert "frequency" in dosage
        assert "warnings" in dosage

        # Verify dosage values
        assert dosage["medication"] == "acetaminophen"
        assert isinstance(dosage["dose_mg"], (int, float))
        assert dosage["dose_mg"] > 0

    def test_case_reassessment_endpoint(self, client: TestClient, sample_case_data: dict) -> None:
        """Test the case reassessment endpoint."""
        # First create a case
        create_response = client.post("/api/cases", json=sample_case_data)
        case_id = create_response.json()["case_id"]

        # Reassess the case
        response = client.post(f"/api/cases/{case_id}/reassess")

        assert response.status_code == 200
        data = response.json()

        assert "case_id" in data
        assert "new_assessment" in data
        assert "previous_assessment" in data
        assert data["case_id"] == case_id

        # Check that new assessment has AI fields
        new_assessment = data["new_assessment"]
        assert "confidence_score" in new_assessment
        assert "reasoning" in new_assessment
        assert "ai_used" in new_assessment

    @patch('src.agents.openai_client')
    def test_ai_assessment_with_mock(self, mock_client, client: TestClient) -> None:
        """Test AI assessment with mocked OpenAI response."""
        # Mock successful AI response
        mock_response = {
            "urgency": "medium",
            "escalate_to_doctor": True,
            "confidence_score": 0.85,
            "reasoning": "Child with fever requires evaluation",
            "first_aid_steps": ["Monitor temperature", "Ensure hydration"],
            "red_flags": ["high_fever"],
            "follow_up_needed": True
        }

        mock_completion = AsyncMock()
        mock_completion.choices = [MagicMock()]
        mock_completion.choices[0].message.content = json.dumps(mock_response)
        mock_client.chat.completions.create.return_value = mock_completion

        assessment_data = {
            "symptoms": "high fever and headache",
            "age": 8,
            "severity": "medium"
        }

        response = client.post("/api/v2/cases/assess", json=assessment_data)

        assert response.status_code == 200
        data = response.json()

        assert data["urgency"] == "medium"
        assert data["escalate_to_doctor"] is True
        assert data["confidence_score"] == 0.85
        assert data["ai_used"] is True
        assert "Monitor temperature" in data["first_aid_steps"]

    @patch('src.agents.openai_client')
    def test_ai_fallback_on_failure(self, mock_client, client: TestClient) -> None:
        """Test fallback to local processing when AI fails."""
        # Mock AI failure
        mock_client.chat.completions.create.side_effect = Exception("API Error")

        assessment_data = {
            "symptoms": "high fever",
            "age": 8,
            "severity": "medium"
        }

        response = client.post("/api/v2/cases/assess", json=assessment_data)

        assert response.status_code == 200
        data = response.json()

        # Should fallback to local processing
        assert data["ai_used"] is False
        assert data["urgency"] in ["low", "medium", "high", "emergency"]
        assert isinstance(data["escalate_to_doctor"], bool)

    def test_ai_assessment_validation(self, client: TestClient) -> None:
        """Test validation of AI assessment request."""
        # Missing required fields
        invalid_data = {
            "symptoms": "",  # Empty symptoms
            "age": -1,  # Invalid age
        }

        response = client.post("/api/v2/cases/assess", json=invalid_data)

        assert response.status_code == 422  # Validation error

    def test_ai_dosage_validation(self, client: TestClient) -> None:
        """Test validation of AI dosage request."""
        # Invalid data
        invalid_data = {
            "medication": "",  # Empty medication
            "weight_kg": -5.0,  # Invalid weight
            "age_years": 0  # Invalid age
        }

        response = client.post("/api/v2/cases/dosage", json=invalid_data)

        assert response.status_code == 422  # Validation error

    def test_unknown_medication_dosage(self, client: TestClient) -> None:
        """Test dosage calculation for unknown medication."""
        dosage_data = {
            "medication": "unknown_medication",
            "weight_kg": 25.0,
            "age_years": 8
        }

        response = client.post("/api/v2/cases/dosage", json=dosage_data)

        assert response.status_code == 200
        data = response.json()

        # Should return error information
        assert "error" in data
        assert "not found" in data["error"] or "unknown" in data["error"]

    def test_cost_optimization_routing(self, client: TestClient) -> None:
        """Test that cost optimization routes simple cases appropriately."""
        # Simple case that should use local processing
        simple_data = {
            "symptoms": "mild headache",
            "age": 25,
            "severity": "low"
        }

        response = client.post("/api/v2/cases/assess", json=simple_data)

        assert response.status_code == 200
        data = response.json()

        # Should work regardless of AI or local processing
        assert "urgency" in data
        assert "escalate_to_doctor" in data
        assert "ai_used" in data

    def test_infant_safety_mode(self, client: TestClient) -> None:
        """Test safety mode for infant cases."""
        infant_data = {
            "symptoms": "mild fever",
            "age": 1,
            "severity": "low"
        }

        response = client.post("/api/v2/cases/assess", json=infant_data)

        assert response.status_code == 200
        data = response.json()

        # Safety mode should escalate infant cases
        assert data["escalate_to_doctor"] is True
        assert data["urgency"] in ["medium", "high", "emergency"]

    def test_elderly_safety_mode(self, client: TestClient) -> None:
        """Test safety mode for elderly cases."""
        elderly_data = {
            "symptoms": "chest pain",
            "age": 75,
            "severity": "medium"
        }

        response = client.post("/api/v2/cases/assess", json=elderly_data)

        assert response.status_code == 200
        data = response.json()

        # Should handle elderly cases appropriately
        assert "urgency" in data
        assert "escalate_to_doctor" in data
        # Elderly cases with chest pain should typically be escalated
        assert data["escalate_to_doctor"] is True
