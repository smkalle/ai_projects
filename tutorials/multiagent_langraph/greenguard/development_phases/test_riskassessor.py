import pytest
import json
from fastapi.testclient import TestClient
from phase3_riskassessor import app, RiskLevel, RiskAssessment
from unittest.mock import patch, MagicMock

client = TestClient(app)

class TestRiskAssessorUnit:
    """Unit tests for RiskAssessor components"""
    
    def test_risk_level_enum(self):
        """Test risk level enumeration values"""
        assert RiskLevel.LOW.value == "low"
        assert RiskLevel.MODERATE.value == "moderate"
        assert RiskLevel.HIGH.value == "high"
        assert RiskLevel.SEVERE.value == "severe"
        assert RiskLevel.CRITICAL.value == "critical"
    
    def test_risk_assessment_model(self):
        """Test RiskAssessment model validation"""
        assessment = RiskAssessment(
            risk_level=RiskLevel.HIGH,
            confidence_score=0.85,
            primary_hazards=["Air pollution", "Water contamination"],
            health_impacts=["Respiratory issues"],
            vulnerable_populations=["Children", "Elderly"],
            recommendations=["Use air purifiers"],
            data_quality_score=0.9
        )
        assert assessment.risk_level == RiskLevel.HIGH
        assert 0 <= assessment.confidence_score <= 1
        assert 0 <= assessment.data_quality_score <= 1
    
    def test_confidence_score_bounds(self):
        """Test confidence score validation"""
        with pytest.raises(ValueError):
            RiskAssessment(
                risk_level=RiskLevel.LOW,
                confidence_score=1.5,  # Invalid: > 1
                primary_hazards=[],
                health_impacts=[],
                vulnerable_populations=[],
                recommendations=[],
                data_quality_score=0.5
            )

class TestRiskAssessorIntegration:
    """Integration tests for DataScout -> RiskAssessor flow"""
    
    @patch('phase3_riskassessor.TavilySearchResults')
    @patch('phase3_riskassessor.ChatOpenAI')
    def test_full_risk_assessment_flow(self, mock_llm, mock_tavily):
        """Test complete risk assessment pipeline"""
        # Mock Tavily search results
        mock_search = MagicMock()
        mock_search.invoke.return_value = [
            {
                "title": "Air Quality Alert",
                "url": "http://example.com",
                "content": "High pollution levels detected"
            }
        ]
        mock_tavily.return_value = mock_search
        
        # Mock LLM responses
        mock_llm_instance = MagicMock()
        mock_llm_instance.invoke.side_effect = [
            MagicMock(content=json.dumps({
                "risk_level": "high",
                "confidence_score": 0.85,
                "primary_hazards": ["Air pollution"],
                "health_impacts": ["Respiratory issues"],
                "vulnerable_populations": ["Children"],
                "recommendations": ["Stay indoors"],
                "data_quality_score": 0.9
            })),
            MagicMock(content="Detailed analysis of environmental risks...")
        ]
        mock_llm.return_value = mock_llm_instance
        
        # Test the endpoint
        response = client.post("/assess-risk", json={"location": "Test City"})
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"
        assert data["location"] == "Test City"
        assert data["risk_assessment"]["risk_level"] == "high"
        assert data["risk_assessment"]["confidence_score"] == 0.85
    
    def test_missing_api_keys(self):
        """Test error handling for missing API keys"""
        with patch.dict('os.environ', {}, clear=True):
            response = client.post("/assess-risk", json={"location": "Test City"})
            assert response.status_code == 500
            assert "Missing API keys" in response.json()["detail"]

class TestRiskAssessorSmoke:
    """Smoke tests for critical paths"""
    
    def test_api_health(self):
        """Test API is accessible"""
        response = client.get("/")
        assert response.status_code == 200
        assert "GreenGuard" in response.text
    
    def test_test_endpoints(self):
        """Test that test endpoints are accessible"""
        response = client.get("/run-tests?test_type=unit")
        assert response.status_code == 200
        assert response.json()["test_type"] == "unit"
        
        response = client.get("/validate-ui")
        assert response.status_code == 200
        assert response.json()["passed"] == True
    
    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test', 'TAVILY_API_KEY': 'test'})
    def test_risk_assessment_endpoint_exists(self):
        """Test risk assessment endpoint is reachable"""
        response = client.post("/assess-risk", json={})
        # Should fail validation but endpoint should exist
        assert response.status_code in [422, 500]  # Validation or execution error

def test_ui_validation_checklist():
    """Test UI validation returns expected structure"""
    response = client.get("/validate-ui")
    assert response.status_code == 200
    
    data = response.json()
    assert data["passed"] == True
    assert data["total_tests"] > 0
    assert "Silicon Valley aesthetic" in data["details"]
    assert "Risk meter animates" in data["details"]

if __name__ == "__main__":
    pytest.main([__file__, "-v"])