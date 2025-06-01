#!/usr/bin/env python3
"""Simple test script to verify web interface functionality."""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_web_pages():
    """Test that all web pages load correctly."""
    pages = [
        "/",
        "/assess", 
        "/dosage",
        "/cases"
    ]
    
    print("🌐 Testing Web Pages...")
    for page in pages:
        try:
            response = requests.get(f"{BASE_URL}{page}")
            if response.status_code == 200:
                print(f"✅ {page} - OK")
            else:
                print(f"❌ {page} - Error {response.status_code}")
        except Exception as e:
            print(f"❌ {page} - Exception: {e}")

def test_api_endpoints():
    """Test API endpoints."""
    print("\n🔌 Testing API Endpoints...")
    
    # Health check
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        if response.status_code == 200:
            print("✅ Health endpoint - OK")
        else:
            print(f"❌ Health endpoint - Error {response.status_code}")
    except Exception as e:
        print(f"❌ Health endpoint - Exception: {e}")
    
    # Assessment endpoint
    try:
        data = {
            "symptoms": "test symptoms",
            "age": 25,
            "severity": "medium"
        }
        response = requests.post(
            f"{BASE_URL}/api/v2/cases/assess",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            print("✅ Assessment endpoint - OK")
        else:
            print(f"❌ Assessment endpoint - Error {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Assessment endpoint - Exception: {e}")
    
    # Cases endpoint
    try:
        response = requests.get(f"{BASE_URL}/api/cases")
        if response.status_code == 200:
            data = response.json()
            cases_count = len(data.get('cases', []))
            print(f"✅ Cases endpoint - OK ({cases_count} cases)")
        else:
            print(f"❌ Cases endpoint - Error {response.status_code}")
    except Exception as e:
        print(f"❌ Cases endpoint - Exception: {e}")

def test_form_submission():
    """Test form submission simulation."""
    print("\n📝 Testing Form Submission...")
    
    # Test assessment form data
    assessment_data = {
        "symptoms": "Diarrhea with bloated stomach",
        "age": 10,
        "severity": "medium"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v2/cases/assess",
            json=assessment_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            urgency = result.get('assessment', {}).get('urgency', 'unknown')
            ai_used = result.get('ai_used', False)
            print(f"✅ Assessment form simulation - OK")
            print(f"   Urgency: {urgency}, AI Used: {ai_used}")
        else:
            print(f"❌ Assessment form simulation - Error {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Assessment form simulation - Exception: {e}")

if __name__ == "__main__":
    print("🏥 Medical AI Assistant - Web Interface Test")
    print("=" * 50)
    
    test_web_pages()
    test_api_endpoints()
    test_form_submission()
    
    print("\n✨ Test completed!") 