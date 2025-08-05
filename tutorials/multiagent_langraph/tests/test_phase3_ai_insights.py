"""
Phase 3 Tests - AI Insights Q&A Feature
Tests for the AI-powered environmental insights system
"""

import pytest
from fastapi.testclient import TestClient
from greenguard.main import app

client = TestClient(app)

def test_ai_insights_safety_query():
    """Test AI insights for safety-related queries"""
    response = client.post("/api/ai-insights", json={
        "query": "Is it safe to exercise outside?",
        "location": "Tokyo, Japan"
    })
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["query_type"] == "safety"
    assert 0.8 <= data["confidence"] <= 1.0
    assert "Tokyo, Japan" in data["insight"]
    assert "safe" in data["insight"].lower()
    assert len(data["recommendations"]) >= 3
    assert len(data["data_sources"]) >= 1

def test_ai_insights_activity_query():
    """Test AI insights for activity-related queries"""
    response = client.post("/api/ai-insights", json={
        "query": "Can I go running today?",
        "location": "London, UK"
    })
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["query_type"] == "activity"
    assert data["location"] == "London, UK"
    assert "running" in data["insight"].lower() or "exercise" in data["insight"].lower()
    assert isinstance(data["recommendations"], list)

def test_ai_insights_air_quality_query():
    """Test AI insights for air quality queries"""
    response = client.post("/api/ai-insights", json={
        "query": "How is the air quality today?",
        "location": "Singapore"
    })
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["query_type"] == "air_quality"
    assert "air quality" in data["insight"].lower()
    assert "aqi" in data["insight"].lower()
    assert data["confidence"] >= 0.9  # Air quality queries should be high confidence

def test_ai_insights_water_quality_query():
    """Test AI insights for water quality queries"""
    response = client.post("/api/ai-insights", json={
        "query": "Is the water safe to drink?",
        "location": "New York, NY"
    })
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["query_type"] == "water_quality"
    assert "water" in data["insight"].lower()

def test_ai_insights_weather_query():
    """Test AI insights for weather-related queries"""
    response = client.post("/api/ai-insights", json={
        "query": "What's the temperature like?",
        "location": "Dubai, UAE"
    })
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["query_type"] == "weather"
    assert "Dubai, UAE" in data["insight"]

def test_ai_insights_comparison_query():
    """Test AI insights for comparison queries"""
    response = client.post("/api/ai-insights", json={
        "query": "Compare air quality with yesterday",
        "location": "Mumbai, India"
    })
    
    assert response.status_code == 200 
    data = response.json()
    
    assert data["query_type"] == "comparison"
    assert "comparison" in data["insight"].lower() or "compare" in data["insight"].lower()

def test_ai_insights_forecast_query():
    """Test AI insights for forecast queries"""
    response = client.post("/api/ai-insights", json={
        "query": "What will air quality be like tomorrow?",
        "location": "Cairo, Egypt"
    })
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["query_type"] == "forecast"
    assert "forecast" in data["insight"].lower() or "tomorrow" in data["insight"].lower()

def test_ai_insights_general_query():
    """Test AI insights for general queries"""
    response = client.post("/api/ai-insights", json={
        "query": "Tell me about environmental conditions",
        "location": "São Paulo, Brazil"
    })
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["query_type"] == "general"
    assert "São Paulo, Brazil" in data["insight"]
    assert len(data["recommendations"]) >= 2

def test_ai_insights_different_locations():
    """Test AI insights work with different world cities"""
    test_cities = [
        "New York, NY",
        "London, UK", 
        "Tokyo, Japan",
        "Sydney, Australia",
        "Paris, France"
    ]
    
    for city in test_cities:
        response = client.post("/api/ai-insights", json={
            "query": "Is it safe outside?",
            "location": city
        })
        
        assert response.status_code == 200
        data = response.json()
        assert city in data["insight"]
        assert data["query_type"] == "safety"

def test_ai_insights_confidence_levels():
    """Test that confidence levels are appropriate for different query types"""
    queries = [
        {"query": "What's the AQI?", "min_confidence": 0.9},  # High confidence for specific data
        {"query": "Is it safe?", "min_confidence": 0.8},      # High confidence for safety
        {"query": "Compare with Tokyo", "min_confidence": 0.6}, # Lower for comparisons
        {"query": "What about tomorrow?", "min_confidence": 0.5} # Lower for forecasts
    ]
    
    for test_case in queries:
        response = client.post("/api/ai-insights", json={
            "query": test_case["query"],
            "location": "Paris, France"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["confidence"] >= test_case["min_confidence"]

def test_ai_insights_response_structure():
    """Test that AI insights response has correct structure"""
    response = client.post("/api/ai-insights", json={
        "query": "How's the air?",
        "location": "Singapore"
    })
    
    assert response.status_code == 200
    data = response.json()
    
    # Check all required fields are present
    required_fields = ["insight", "confidence", "location", "query_type", 
                      "recommendations", "data_sources"]
    for field in required_fields:
        assert field in data
    
    # Check data types
    assert isinstance(data["insight"], str)
    assert isinstance(data["confidence"], float)
    assert isinstance(data["location"], str)
    assert isinstance(data["query_type"], str)
    assert isinstance(data["recommendations"], list)
    assert isinstance(data["data_sources"], list)
    
    # Check reasonable lengths
    assert len(data["insight"]) > 20
    assert 0.0 <= data["confidence"] <= 1.0
    assert len(data["recommendations"]) >= 1
    assert len(data["data_sources"]) >= 1

def test_ai_insights_emoji_usage():
    """Test that AI insights use appropriate emojis for visual appeal"""
    queries = [
        {"query": "Safe to exercise?", "expected_emojis": ["✅", "⚠️", "🚨", "🏃"]},
        {"query": "Air quality?", "expected_emojis": ["🌫️"]},
        {"query": "General conditions?", "expected_emojis": ["🌍"]}
    ]
    
    for test_case in queries:
        response = client.post("/api/ai-insights", json={
            "query": test_case["query"],
            "location": "Tokyo, Japan"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Check that at least one expected emoji is present
        insight = data["insight"]
        has_emoji = any(emoji in insight for emoji in test_case["expected_emojis"])
        assert has_emoji, f"No expected emoji found in: {insight}"

def test_ai_insights_integration_with_template_cities():
    """Test AI insights work with all template cities"""
    # Get template cities
    cities_response = client.get("/api/template-cities")
    assert cities_response.status_code == 200
    
    cities = cities_response.json()["cities"]
    
    # Test AI insights with each template city
    for city in cities[:3]:  # Test first 3 to keep test time reasonable
        response = client.post("/api/ai-insights", json={
            "query": "Safe for outdoor activities?",
            "location": city["name"]
        })
        
        assert response.status_code == 200
        data = response.json()
        assert city["name"] in data["location"]
        assert data["query_type"] == "safety"