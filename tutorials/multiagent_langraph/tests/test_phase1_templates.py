"""
Phase 1 Tests - Template Cities Feature
Tests for the top 5 US cities quick selection functionality
"""

import pytest
from fastapi.testclient import TestClient
from greenguard.main import app

client = TestClient(app)

def test_template_cities_endpoint():
    """Test that the template cities endpoint returns correct data"""
    response = client.get("/api/template-cities")
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify response structure
    assert "cities" in data
    assert "total" in data
    assert "version" in data
    
    # Verify we have exactly 5 cities
    assert data["total"] == 5
    assert len(data["cities"]) == 5
    
    # Verify each city has required fields
    for city in data["cities"]:
        assert "id" in city
        assert "name" in city
        assert "coordinates" in city
        assert "lat" in city["coordinates"]
        assert "lon" in city["coordinates"]
        assert "icon" in city
        assert "common_hazards" in city
        assert isinstance(city["common_hazards"], list)

def test_template_cities_content():
    """Test that the correct top 5 US cities are included"""
    response = client.get("/api/template-cities")
    data = response.json()
    
    city_names = [city["name"] for city in data["cities"]]
    
    # Verify the top 5 cities are present
    assert "New York, NY" in city_names
    assert "Los Angeles, CA" in city_names
    assert "Chicago, IL" in city_names
    assert "Houston, TX" in city_names
    assert "Phoenix, AZ" in city_names

def test_template_city_trigger_check():
    """Test that template cities can be used with the main workflow"""
    # Get a template city
    response = client.get("/api/template-cities")
    template_city = response.json()["cities"][0]
    
    # Use the template city in a check
    response = client.post("/trigger-check", json={
        "location": template_city["name"]
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "location" in data
    assert data["location"] == template_city["name"]

def test_template_cities_hazards():
    """Test that each city has appropriate hazard types"""
    response = client.get("/api/template-cities")
    cities = response.json()["cities"]
    
    # Verify hazard types are valid
    valid_hazards = [
        "air_quality", "water_quality", "wildfire", 
        "extreme_weather", "chemical", "flooding", "extreme_heat"
    ]
    
    for city in cities:
        assert len(city["common_hazards"]) > 0
        for hazard in city["common_hazards"]:
            assert hazard in valid_hazards

def test_template_cities_coordinates():
    """Test that city coordinates are valid"""
    response = client.get("/api/template-cities")
    cities = response.json()["cities"]
    
    for city in cities:
        coords = city["coordinates"]
        
        # Verify latitude is in valid range
        assert -90 <= coords["lat"] <= 90
        
        # Verify longitude is in valid range  
        assert -180 <= coords["lon"] <= 180
        
        # Verify specific city coordinates (rough check)
        if city["name"] == "New York, NY":
            assert 40 < coords["lat"] < 41
            assert -75 < coords["lon"] < -73

def test_template_cities_icons():
    """Test that each city has a unique emoji icon"""
    response = client.get("/api/template-cities")
    cities = response.json()["cities"]
    
    icons = [city["icon"] for city in cities]
    
    # All cities should have icons
    assert all(icon for icon in icons)
    
    # Icons should be unique
    assert len(icons) == len(set(icons))
    
    # Verify specific icons
    city_dict = {city["name"]: city["icon"] for city in cities}
    assert city_dict["New York, NY"] == "🗽"
    assert city_dict["Los Angeles, CA"] == "🌴"
    assert city_dict["Phoenix, AZ"] == "🌵"