"""
Full Integration Tests - All Phases Working Together
Tests for the complete GreenGuard v2 system with all features integrated
"""

import pytest
from fastapi.testclient import TestClient
from greenguard.main import app

client = TestClient(app)

def test_complete_user_journey():
    """Test a complete user journey through all features"""
    session_id = "integration_test_session"
    
    # 1. Get template cities
    cities_response = client.get("/api/template-cities")
    assert cities_response.status_code == 200
    cities = cities_response.json()["cities"]
    assert len(cities) == 10
    
    # 2. Select a city and add to favorites
    selected_city = cities[0]["name"]  # New York, NY
    favorite_response = client.post("/api/favorites", json={
        "city": selected_city,
        "session_id": session_id
    })
    assert favorite_response.status_code == 200
    assert selected_city in favorite_response.json()["favorites"]
    
    # 3. Ask AI question about the city
    ai_response = client.post("/api/ai-insights", json={
        "query": "Is it safe to exercise outside?",
        "location": selected_city
    })
    assert ai_response.status_code == 200
    ai_data = ai_response.json()
    assert selected_city in ai_data["insight"]
    assert ai_data["query_type"] == "safety"
    
    # 4. Trigger full workflow for the city
    workflow_response = client.post("/trigger-check", json={
        "location": selected_city
    })
    assert workflow_response.status_code == 200
    assert workflow_response.json()["location"] == selected_city

def test_all_template_cities_functionality():
    """Test that all template cities work with all features"""
    session_id = "full_cities_test"
    
    # Get all template cities
    cities_response = client.get("/api/template-cities")
    cities = cities_response.json()["cities"]
    
    # Test first 5 cities (favorites limit)
    for i, city in enumerate(cities[:5]):
        city_name = city["name"]
        
        # Add to favorites
        fav_response = client.post("/api/favorites", json={
            "city": city_name,
            "session_id": session_id
        })
        assert fav_response.status_code == 200
        
        # Test AI insights
        ai_response = client.post("/api/ai-insights", json={
            "query": f"How's the air quality in {city_name}?",
            "location": city_name
        })
        assert ai_response.status_code == 200
        
        # Test workflow
        workflow_response = client.post("/trigger-check", json={
            "location": city_name
        })
        assert workflow_response.status_code == 200
    
    # Verify all favorites were added
    final_favorites = client.get("/api/favorites", headers={"session-id": session_id})
    assert len(final_favorites.json()["favorites"]) == 5

def test_ai_query_types_coverage():
    """Test that all AI query types work correctly"""
    test_location = "London, UK"
    
    query_tests = [
        {"query": "Is it safe outside?", "expected_type": "safety"},
        {"query": "Can I go running?", "expected_type": "activity"},
        {"query": "What's the AQI?", "expected_type": "air_quality"},
        {"query": "Is water safe to drink?", "expected_type": "water_quality"},
        {"query": "How's the weather?", "expected_type": "weather"},
        {"query": "Compare with yesterday", "expected_type": "comparison"},
        {"query": "What about tomorrow?", "expected_type": "forecast"},
        {"query": "Tell me about conditions", "expected_type": "general"}
    ]
    
    for test in query_tests:
        response = client.post("/api/ai-insights", json={
            "query": test["query"],
            "location": test_location
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["query_type"] == test["expected_type"]
        assert test_location in data["insight"]

def test_system_performance():
    """Test that system performs well with multiple requests"""
    import time
    
    # Test template cities load speed
    start_time = time.time()
    response = client.get("/api/template-cities")
    cities_time = time.time() - start_time
    
    assert response.status_code == 200
    assert cities_time < 1.0  # Should load in under 1 second
    
    # Test AI insights response time
    start_time = time.time()
    response = client.post("/api/ai-insights", json={
        "query": "Is it safe outside?",
        "location": "Tokyo, Japan"
    })
    ai_time = time.time() - start_time
    
    assert response.status_code == 200
    assert ai_time < 3.0  # Should respond in under 3 seconds

def test_error_handling():
    """Test system handles errors gracefully"""
    
    # Test empty AI query
    response = client.post("/api/ai-insights", json={
        "query": "",
        "location": "Paris, France"
    })
    # Should still work with empty query (defaults to general)
    assert response.status_code == 200
    
    # Test invalid location (should still work with fallback data)
    response = client.post("/api/ai-insights", json={
        "query": "Is it safe?",
        "location": "Nonexistent City, Nowhere"
    })
    assert response.status_code == 200

def test_data_consistency():
    """Test that data remains consistent across different endpoints"""
    session_id = "consistency_test"
    test_city = "Singapore"
    
    # Add city to favorites
    client.post("/api/favorites", json={
        "city": test_city,
        "session_id": session_id
    })
    
    # Verify in favorites
    favorites = client.get("/api/favorites", headers={"session-id": session_id})
    assert test_city in favorites.json()["favorites"]
    
    # Use same city in AI insights
    ai_response = client.post("/api/ai-insights", json={
        "query": "Environmental conditions?",
        "location": test_city
    })
    
    # Verify city name consistency
    assert test_city in ai_response.json()["insight"]
    assert ai_response.json()["location"] == test_city

def test_ui_component_compatibility():
    """Test that API responses are compatible with UI requirements"""
    
    # Template cities should have UI-required fields
    cities_response = client.get("/api/template-cities")
    cities = cities_response.json()["cities"]
    
    for city in cities:
        # UI requires these fields
        assert "name" in city
        assert "icon" in city
        assert "coordinates" in city
        assert "common_hazards" in city
        
        # Icons should be single emoji characters
        assert len(city["icon"]) <= 2  # Single emoji or emoji with modifier
    
    # AI insights should have UI-displayable format
    ai_response = client.post("/api/ai-insights", json={
        "query": "Test query",
        "location": "Test Location"
    })
    ai_data = ai_response.json()
    
    # UI requires formatted text
    assert len(ai_data["insight"]) > 10  # Meaningful insight text
    assert 0.0 <= ai_data["confidence"] <= 1.0  # Valid confidence range
    assert len(ai_data["recommendations"]) >= 1  # At least one recommendation
    
    # Recommendations should be displayable as list items
    for rec in ai_data["recommendations"]:
        assert isinstance(rec, str)
        assert len(rec) > 5  # Meaningful recommendation text

def test_session_management():
    """Test session-based features work correctly"""
    session1 = "session_alpha"
    session2 = "session_beta"
    
    # Add different favorites to different sessions
    client.post("/api/favorites", json={
        "city": "Tokyo, Japan",
        "session_id": session1
    })
    
    client.post("/api/favorites", json={
        "city": "London, UK", 
        "session_id": session2
    })
    
    # Verify session isolation
    fav1 = client.get("/api/favorites", headers={"session-id": session1})
    fav2 = client.get("/api/favorites", headers={"session-id": session2})
    
    assert "Tokyo, Japan" in fav1.json()["favorites"]
    assert "Tokyo, Japan" not in fav2.json()["favorites"]
    assert "London, UK" in fav2.json()["favorites"]
    assert "London, UK" not in fav1.json()["favorites"]

def test_world_cities_coverage():
    """Test that world cities provide good geographic coverage"""
    cities_response = client.get("/api/template-cities")
    cities = cities_response.json()["cities"]
    
    # Should have cities from different continents
    continents_represented = set()
    
    city_continent_map = {
        "New York, NY": "North America",
        "London, UK": "Europe", 
        "Tokyo, Japan": "Asia",
        "Sydney, Australia": "Australia",
        "Paris, France": "Europe",
        "Singapore": "Asia",
        "Dubai, UAE": "Asia",
        "Mumbai, India": "Asia",
        "São Paulo, Brazil": "South America",
        "Cairo, Egypt": "Africa"
    }
    
    for city in cities:
        continent = city_continent_map.get(city["name"])
        if continent:
            continents_represented.add(continent)
    
    # Should represent at least 5 different regions
    assert len(continents_represented) >= 5