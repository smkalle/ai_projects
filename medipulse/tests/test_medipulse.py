"""
Unit tests for MediPulse

Run tests with: python -m pytest tests/
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch
import json

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from medipulse import MediPulse, MediPulseConfig, DocumentType, ExtractedData, ValidationResult

class TestMediPulseConfig:
    """Test MediPulseConfig class"""

    def test_config_initialization(self):
        """Test config initialization"""
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'}):
            config = MediPulseConfig()
            assert config.openai_api_key == 'test_key'
            assert config.model == 'gpt-4o'

    def test_config_missing_api_key(self):
        """Test config with missing API key"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="OPENAI_API_KEY not found"):
                MediPulseConfig()

class TestDocumentType:
    """Test DocumentType model"""

    def test_valid_document_type(self):
        """Test valid document type creation"""
        doc_type = DocumentType(
            doc_type="lab_report",
            confidence=0.95,
            reasoning="Contains lab results"
        )
        assert doc_type.doc_type == "lab_report"
        assert doc_type.confidence == 0.95
        assert doc_type.reasoning == "Contains lab results"

    def test_invalid_confidence(self):
        """Test invalid confidence values"""
        with pytest.raises(ValueError):
            DocumentType(
                doc_type="lab_report",
                confidence=1.5,  # Invalid: > 1.0
                reasoning="Test"
            )

class TestExtractedData:
    """Test ExtractedData model"""

    def test_extracted_data_creation(self):
        """Test extracted data model"""
        data = ExtractedData(
            patient_name="John Doe",
            date_of_service="2025-08-16",
            lab_results={"glucose": "95 mg/dL"}
        )
        assert data.patient_name == "John Doe"
        assert data.date_of_service == "2025-08-16"
        assert data.lab_results == {"glucose": "95 mg/dL"}

class TestValidationResult:
    """Test ValidationResult model"""

    def test_validation_result(self):
        """Test validation result model"""
        result = ValidationResult(
            is_valid=True,
            errors=[],
            warnings=["Minor warning"],
            completeness_score=0.85
        )
        assert result.is_valid is True
        assert result.errors == []
        assert result.warnings == ["Minor warning"]
        assert result.completeness_score == 0.85

class TestMediPulse:
    """Test main MediPulse class"""

    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'})
    def test_medipulse_initialization(self):
        """Test MediPulse initialization"""
        with patch('medipulse.ChatOpenAI'):
            medipulse = MediPulse()
            assert medipulse is not None
            assert medipulse.config is not None
            assert medipulse.workflow is not None

    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'})
    def test_route_extraction(self):
        """Test routing logic"""
        with patch('medipulse.ChatOpenAI'):
            medipulse = MediPulse()

            # Test supported document type
            state = {"doc_type": "lab_report"}
            result = medipulse._route_extraction(state)
            assert result == "extract"

            # Test unsupported document type
            state = {"doc_type": "other"}
            result = medipulse._route_extraction(state)
            assert result == "other"

    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'})
    def test_handle_unsupported(self):
        """Test handling unsupported document types"""
        with patch('medipulse.ChatOpenAI'):
            medipulse = MediPulse()

            state = {
                "doc_type": "unsupported_type",
                "processing_steps": []
            }

            result = medipulse._handle_unsupported(state)

            assert "error" in result["extracted_data"]
            assert "Document type not supported" in result["processing_steps"]

    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'})
    def test_process_document_error_handling(self):
        """Test error handling in document processing"""
        with patch('medipulse.ChatOpenAI'):
            medipulse = MediPulse()

            # Mock the workflow to raise an exception
            with patch.object(medipulse, 'workflow') as mock_workflow:
                mock_workflow.invoke.side_effect = Exception("Test error")

                result = medipulse.process_document("test_base64")

                assert result["success"] is False
                assert "Test error" in result["error_message"]

class TestIntegration:
    """Integration tests"""

    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'})
    @patch('medipulse.ChatOpenAI')
    def test_full_workflow_mock(self, mock_llm):
        """Test full workflow with mocked responses"""
        # Mock LLM responses
        mock_llm_instance = Mock()
        mock_llm.return_value = mock_llm_instance

        # Mock classification response
        mock_classification = DocumentType(
            doc_type="lab_report",
            confidence=0.95,
            reasoning="Contains lab test results"
        )

        # Mock extraction response
        mock_extraction = {
            "patient_name": "John Doe",
            "date_of_service": "2025-08-16",
            "lab_results": {"glucose": "95 mg/dL"}
        }

        # Mock validation response
        mock_validation = ValidationResult(
            is_valid=True,
            errors=[],
            warnings=[],
            completeness_score=0.85
        )

        # Configure the mock to return structured outputs
        mock_llm_instance.with_structured_output.return_value.invoke.side_effect = [
            mock_classification,
            mock_validation
        ]
        mock_llm_instance.invoke.return_value = mock_extraction

        medipulse = MediPulse()

        # This would require more complex mocking of the LangGraph workflow
        # For now, we test that the MediPulse object is created successfully
        assert medipulse is not None

@pytest.fixture
def sample_base64():
    """Fixture providing a sample base64 image"""
    # 1x1 pixel PNG
    return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="

def test_sample_base64_fixture(sample_base64):
    """Test that the fixture works"""
    assert sample_base64 is not None
    assert isinstance(sample_base64, str)
    assert len(sample_base64) > 0
