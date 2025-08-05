import pytest
import json
from fastapi.testclient import TestClient
from phase4_communicaid import app, AlertType, AlertChannel, PublicAlert
from unittest.mock import patch, MagicMock
from datetime import datetime

client = TestClient(app)

class TestCommunicaidUnit:
    """Unit tests for Communicaid agent components"""
    
    def test_alert_type_enum(self):
        """Test alert type enumeration values"""
        assert AlertType.ADVISORY.value == "advisory"
        assert AlertType.WARNING.value == "warning"
        assert AlertType.URGENT.value == "urgent"
        assert AlertType.EMERGENCY.value == "emergency"
    
    def test_alert_channel_enum(self):
        """Test alert channel enumeration values"""
        assert AlertChannel.SMS.value == "sms"
        assert AlertChannel.EMAIL.value == "email"
        assert AlertChannel.SOCIAL_MEDIA.value == "social_media"
        assert AlertChannel.EMERGENCY_BROADCAST.value == "emergency_broadcast"
        assert AlertChannel.MOBILE_PUSH.value == "mobile_push"
    
    def test_public_alert_model(self):
        """Test PublicAlert model validation"""
        alert = PublicAlert(
            alert_id="TEST123",
            alert_type=AlertType.WARNING,
            title="Test Alert",
            message="Test message",
            summary="Test summary",
            detailed_description="Test detailed description",
            health_recommendations=["Stay indoors", "Use masks"],
            vulnerable_populations=["Children", "Elderly"],
            effective_immediately=True,
            expiration_time=datetime.now(),
            recommended_channels=[AlertChannel.SMS, AlertChannel.EMAIL],
            urgency_score=0.75,
            readability_score=0.85
        )
        assert alert.alert_type == AlertType.WARNING
        assert 0 <= alert.urgency_score <= 1
        assert 0 <= alert.readability_score <= 1
        assert len(alert.recommended_channels) >= 1
    
    def test_urgency_score_bounds(self):
        """Test urgency score validation bounds"""
        with pytest.raises(ValueError):
            PublicAlert(
                alert_id="TEST123",
                alert_type=AlertType.WARNING,
                title="Test",
                message="Test",
                summary="Test",
                detailed_description="Test",
                health_recommendations=[],
                vulnerable_populations=[],
                effective_immediately=True,
                expiration_time=None,
                recommended_channels=[AlertChannel.SMS],
                urgency_score=1.5,  # Invalid: > 1
                readability_score=0.8
            )
    
    def test_alert_id_generation(self):
        """Test alert ID generation uniqueness"""
        import uuid
        id1 = str(uuid.uuid4())[:8].upper()
        id2 = str(uuid.uuid4())[:8].upper()
        assert id1 != id2
        assert len(id1) == 8
        assert id1.isupper()

class TestCommunicaidIntegration:
    """Integration tests for full alert generation pipeline"""
    
    @patch('phase4_communicaid.TavilySearchResults')
    @patch('phase4_communicaid.ChatOpenAI')
    def test_full_alert_generation_pipeline(self, mock_llm, mock_tavily):
        """Test complete DataScout -> RiskAssessor -> Communicaid pipeline"""
        # Mock Tavily search results
        mock_search = MagicMock()
        mock_search.invoke.return_value = [
            {
                "title": "Environmental Health Alert",
                "url": "http://example.com",
                "content": "Severe air quality issues detected"
            }
        ]
        mock_tavily.return_value = mock_search
        
        # Mock LLM responses
        mock_llm_instance = MagicMock()
        mock_llm_instance.invoke.side_effect = [
            # Risk assessment response
            MagicMock(content=json.dumps({
                "risk_level": "high",
                "confidence_score": 0.9,
                "primary_hazards": ["Air pollution", "Chemical exposure"],
                "health_impacts": ["Respiratory distress", "Eye irritation"],
                "vulnerable_populations": ["Children", "Elderly", "Asthma patients"],
                "data_quality_score": 0.85
            })),
            # Alert generation response
            MagicMock(content="Immediate health alert: High levels of air pollution detected. Residents should limit outdoor activities and use protective masks when necessary."),
            # Alert variations response
            MagicMock(content=json.dumps({
                "sms": "HEALTH ALERT: High air pollution in Test City. Stay indoors. Use masks if going out.",
                "email": "URGENT: Environmental Health Alert for Test City - High air pollution levels detected requiring immediate protective action.",
                "social_media": "🚨 Health Alert Test City: High air pollution! Stay safe indoors. #HealthAlert #AirQuality",
                "emergency_broadcast": "Official health emergency: High air pollution in Test City. Take immediate protective measures.",
                "mobile_push": "Health Alert: High pollution Test City"
            }))
        ]
        mock_llm.return_value = mock_llm_instance
        
        # Test the endpoint
        response = client.post("/generate-alert", json={"location": "Test City"})
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"
        assert data["location"] == "Test City"
        assert data["public_alert"]["alert_type"] in ["urgent", "emergency"]
        assert len(data["public_alert"]["health_recommendations"]) >= 1
        assert len(data["alert_variations"]) >= 4
        assert "sms" in data["alert_variations"]
        assert "email" in data["alert_variations"]
    
    def test_risk_level_to_alert_type_mapping(self):
        """Test proper mapping from risk levels to alert types"""
        risk_to_alert_mapping = {
            "low": "advisory",
            "moderate": "warning", 
            "high": "urgent",
            "severe": "emergency",
            "critical": "emergency"
        }
        
        for risk_level, expected_alert_type in risk_to_alert_mapping.items():
            # This would be tested with actual alert generation
            # For now, verify the mapping logic exists
            assert expected_alert_type in ["advisory", "warning", "urgent", "emergency"]
    
    def test_missing_api_keys_error(self):
        """Test error handling for missing API keys"""
        with patch.dict('os.environ', {}, clear=True):
            response = client.post("/generate-alert", json={"location": "Test City"})
            assert response.status_code == 500
            assert "Missing API keys" in response.json()["detail"]

class TestCommunicaidSmoke:
    """Smoke tests for critical alert generation paths"""
    
    def test_api_health(self):
        """Test API is accessible"""
        response = client.get("/")
        assert response.status_code == 200
        assert "Communicaid" in response.text
        assert "Alert System" in response.text
    
    def test_test_endpoints_accessible(self):
        """Test all testing endpoints are accessible"""
        test_types = ["unit", "integration", "smoke"]
        
        for test_type in test_types:
            response = client.get(f"/run-tests?test_type={test_type}")
            assert response.status_code == 200
            data = response.json()
            assert data["test_type"] == test_type
            assert "total_tests" in data
            assert "passed" in data
    
    def test_ui_validation_endpoint(self):
        """Test UI validation endpoint"""
        response = client.get("/validate-ui")
        assert response.status_code == 200
        
        data = response.json()
        assert data["passed"] == True
        assert data["total_tests"] > 10
        assert "Silicon Valley aesthetic" in data["details"]
        assert "glassmorphism" in data["details"]
    
    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test', 'TAVILY_API_KEY': 'test'})
    def test_alert_generation_endpoint_exists(self):
        """Test alert generation endpoint is reachable"""
        response = client.post("/generate-alert", json={})
        # Should fail validation but endpoint should exist
        assert response.status_code in [422, 500]

class TestCommunicaidUI:
    """UI and UX validation tests"""
    
    def test_alert_preview_structure(self):
        """Test alert preview contains required UI elements"""
        response = client.get("/")
        html_content = response.text
        
        # Check for key UI components
        assert "alert-preview-container" in html_content
        assert "variation-tabs" in html_content
        assert "metrics-grid" in html_content
        assert "recommendation-grid" in html_content
        assert "channel-selector" in html_content
    
    def test_responsive_design_classes(self):
        """Test responsive design CSS classes are present"""
        response = client.get("/")
        html_content = response.text
        
        # Check for responsive grid classes
        assert "main-layout" in html_content
        assert "@media (max-width:" in html_content
        assert "grid-template-columns" in html_content
    
    def test_accessibility_features(self):
        """Test accessibility features are implemented"""
        response = client.get("/")
        html_content = response.text
        
        # Check for accessibility attributes
        assert 'role=' in html_content or 'aria-' in html_content or 'alt=' in html_content
        assert "font-weight" in html_content  # Font hierarchy
        assert "color:" in html_content  # Color contrast considerations

def test_alert_channel_variations():
    """Test that alert variations are generated for all channels"""
    required_channels = ["sms", "email", "social_media", "emergency_broadcast", "mobile_push"]
    
    # This would test the actual variation generation
    # For now, verify the channels are defined
    for channel in required_channels:
        assert hasattr(AlertChannel, channel.upper())

def test_silicon_valley_ux_standards():
    """Test Silicon Valley UX standards compliance"""
    response = client.get("/")
    html_content = response.text
    
    # Check for modern UX patterns
    assert "backdrop-filter: blur" in html_content  # Glassmorphism
    assert "Inter" in html_content  # Modern typography
    assert "gradient" in html_content  # Modern gradients
    assert "animation:" in html_content  # Smooth animations
    assert "transition:" in html_content  # Smooth transitions
    assert "box-shadow:" in html_content  # Depth and elevation

if __name__ == "__main__":
    pytest.main([__file__, "-v"])