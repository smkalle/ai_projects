#!/usr/bin/env python3
"""
Test the live server at localhost:8000
"""

import asyncio
import json
import time
import random
from httpx import AsyncClient

async def test_live_server():
    """Test the actual running server"""
    base_url = "http://localhost:8000"
    unique_id = int(time.time() * 1000) % 1000000 + random.randint(1000, 9999)
    mobile_suffix = f"{unique_id % 100000:05d}"
    
    print("🌐 Testing Live Server at localhost:8000")
    print("=" * 50)
    
    try:
        async with AsyncClient(base_url=base_url, timeout=10.0) as client:
            # Test patient registration
            patient_data = {
                "first_name": "LiveTest",
                "last_name": "User",
                "date_of_birth": "1995-05-15",
                "mobile_number": f"91234{mobile_suffix}",
                "gender": "Female",
                "village": "Live Village",
                "district": "Live District", 
                "city": "Live City"
            }
            
            print("📝 Testing Patient Registration...")
            response = await client.post("/api/v2/patients/register", json=patient_data)
            if response.status_code == 200:
                data = response.json()
                patient_id = data["patient_id"]
                print(f"✅ SUCCESS - Patient registered: {patient_id}")
                
                # Test patient details
                print("👤 Testing Patient Details...")
                response = await client.get(f"/api/v2/patients/{patient_id}")
                if response.status_code == 200:
                    print("✅ SUCCESS - Patient details retrieved")
                else:
                    print(f"❌ FAILED - Status: {response.status_code}")
                
                # Test AI Assessment
                print("🤖 Testing AI Assessment...")
                assessment_data = {
                    "symptoms": "Fever and cough",
                    "age": 25,
                    "duration": "2 days",
                    "severity": "moderate"
                }
                response = await client.post(f"/api/v2/patients/{patient_id}/assess", json=assessment_data)
                if response.status_code == 200:
                    print("✅ SUCCESS - AI Assessment completed")
                else:
                    print(f"❌ FAILED - AI Assessment Status: {response.status_code}")
                
                # Test case creation
                print("📋 Testing Case Creation...")
                case_data = {
                    "healthcare_worker_id": "HW001",
                    "case_type": "Assessment", 
                    "chief_complaint": "Fever",
                    "symptoms": "High fever and body ache",
                    "urgency_level": "Medium"
                }
                response = await client.post(f"/api/v2/patients/{patient_id}/cases", json=case_data)
                if response.status_code == 200:
                    case_data = response.json()
                    print(f"✅ SUCCESS - Case created: {case_data['case_id']}")
                else:
                    print(f"❌ FAILED - Case Creation Status: {response.status_code}: {response.text}")
                    
            else:
                print(f"❌ FAILED - Registration Status: {response.status_code}: {response.text}")
                
    except Exception as e:
        print(f"❌ CONNECTION ERROR: {e}")
        print("Make sure the server is running on localhost:8000")

if __name__ == "__main__":
    asyncio.run(test_live_server()) 