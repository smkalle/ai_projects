"""
Phase 2 Tests - User Favorites Feature
Tests for the user favorites functionality with session-based storage
"""

import pytest
from fastapi.testclient import TestClient
from greenguard.main import app

client = TestClient(app)

def test_empty_favorites():
    """Test getting favorites for new session"""
    response = client.get("/api/favorites", headers={"session-id": "test-empty"})
    
    assert response.status_code == 200
    data = response.json()
    assert data["favorites"] == []
    assert data["session_id"] == "test-empty"

def test_add_favorite():
    """Test adding a favorite city"""
    response = client.post("/api/favorites", json={
        "city": "Tokyo, Japan",
        "session_id": "test-add"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "Tokyo, Japan" in data["favorites"]
    assert len(data["favorites"]) == 1

def test_add_duplicate_favorite():
    """Test adding the same city twice (should not duplicate)"""
    session_id = "test-duplicate"
    
    # Add first time
    response1 = client.post("/api/favorites", json={
        "city": "London, UK",
        "session_id": session_id
    })
    
    # Add same city again
    response2 = client.post("/api/favorites", json={
        "city": "London, UK", 
        "session_id": session_id
    })
    
    assert response2.status_code == 200
    data = response2.json()
    assert data["favorites"].count("London, UK") == 1
    assert len(data["favorites"]) == 1

def test_favorite_limit():
    """Test 5 favorite limit enforcement"""
    session_id = "test-limit"
    cities = [
        "New York, NY",
        "London, UK", 
        "Tokyo, Japan",
        "Sydney, Australia",
        "Paris, France"
    ]
    
    # Add 5 favorites (should work)
    for city in cities:
        response = client.post("/api/favorites", json={
            "city": city,
            "session_id": session_id
        })
        assert response.status_code == 200
    
    # Try to add 6th favorite (should fail)
    response = client.post("/api/favorites", json={
        "city": "Dubai, UAE",
        "session_id": session_id
    })
    
    assert response.status_code == 400
    assert "Maximum 5 favorite cities allowed" in response.json()["detail"]

def test_remove_favorite():
    """Test removing a favorite city"""
    session_id = "test-remove"
    
    # Add a favorite
    client.post("/api/favorites", json={
        "city": "Singapore",
        "session_id": session_id
    })
    
    # Remove the favorite
    response = client.delete("/api/favorites/Singapore", 
                           headers={"session-id": session_id})
    
    assert response.status_code == 200
    data = response.json()
    assert "Singapore" not in data["favorites"]
    assert len(data["favorites"]) == 0

def test_remove_nonexistent_favorite():
    """Test removing a city that's not in favorites"""
    session_id = "test-nonexistent"
    
    response = client.delete("/api/favorites/NonExistent City", 
                           headers={"session-id": session_id})
    
    assert response.status_code == 200
    data = response.json()
    assert data["favorites"] == []

def test_session_isolation():
    """Test that different sessions have separate favorites"""
    # Add favorite to session 1
    client.post("/api/favorites", json={
        "city": "Mumbai, India",
        "session_id": "session1"
    })
    
    # Check session 2 is empty
    response = client.get("/api/favorites", headers={"session-id": "session2"})
    assert response.json()["favorites"] == []
    
    # Check session 1 still has favorite
    response = client.get("/api/favorites", headers={"session-id": "session1"})
    assert "Mumbai, India" in response.json()["favorites"]

def test_world_cities_with_favorites():
    """Test that template cities work with favorites system"""
    # Get template cities
    response = client.get("/api/template-cities")
    assert response.status_code == 200
    
    cities = response.json()["cities"]
    assert len(cities) == 10
    
    # Verify all cities have required fields for favorites
    for city in cities:
        assert "name" in city
        assert "icon" in city
        assert "coordinates" in city
        assert "common_hazards" in city
        
        # Test that we can favorite each city
        response = client.post("/api/favorites", json={
            "city": city["name"],
            "session_id": "test-world-cities"
        })
        
        # Should succeed for first 5, fail for rest due to limit
        if len(client.get("/api/favorites", 
                         headers={"session-id": "test-world-cities"}).json()["favorites"]) < 5:
            assert response.status_code == 200
        else:
            assert response.status_code == 400

def test_favorites_integration_with_workflow():
    """Test that favorite cities can be used with main workflow"""
    session_id = "test-integration"
    
    # Add a favorite
    client.post("/api/favorites", json={
        "city": "Cairo, Egypt",
        "session_id": session_id
    })
    
    # Get favorites
    response = client.get("/api/favorites", headers={"session-id": session_id})
    favorite_city = response.json()["favorites"][0]
    
    # Test workflow with favorite city
    response = client.post("/trigger-check", json={
        "location": favorite_city
    })
    
    assert response.status_code == 200
    assert response.json()["location"] == favorite_city