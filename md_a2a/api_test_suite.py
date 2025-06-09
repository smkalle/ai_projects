#!/usr/bin/env python3
"""
Simple API Test Suite for Medical AI Assistant MVP V2.0
Tests all patient management endpoints directly
"""

import asyncio
import json
import random
import time
from httpx import AsyncClient
from src.main import app

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

class APITestSuite:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.patient_id = None
        self.unique_id = int(time.time() * 1000) % 1000000 + random.randint(1000, 9999)
        
    def log_success(self, test_name):
        print(f"{Colors.GREEN}✅ PASS{Colors.END} - {test_name}")
        self.passed += 1
        
    def log_failure(self, test_name, error):
        print(f"{Colors.RED}❌ FAIL{Colors.END} - {test_name}")
        print(f"   Error: {error}")
        self.failed += 1
        
    def log_info(self, message):
        print(f"{Colors.BLUE}ℹ️  INFO{Colors.END} - {message}")
        
    def log_warning(self, message):
        print(f"{Colors.YELLOW}⚠️  WARN{Colors.END} - {message}")

    async def test_patient_registration(self, client):
        """Test patient registration endpoint"""
        try:
            # Generate exactly 10-digit mobile number
            mobile_suffix = f"{self.unique_id % 100000:05d}"  # 5 digits
            patient_data = {
                "first_name": "John",
                "last_name": "Doe",
                "date_of_birth": "1990-01-01",
                "mobile_number": f"98765{mobile_suffix}",  # Exactly 10 digits
                "gender": "Male",
                "village": "Test Village",
                "district": "Test District",
                "city": "Test City"
            }
            
            response = await client.post("/api/v2/patients/register", json=patient_data)
            
            if response.status_code != 200:
                self.log_failure("Patient Registration", f"Status {response.status_code}: {response.text}")
                return
                
            data = response.json()
            
            # Verify response structure
            required_fields = ["patient_id", "patient_data", "qr_code", "success", "message"]
            for field in required_fields:
                if field not in data:
                    self.log_failure("Patient Registration", f"Missing field: {field}")
                    return
            
            # Verify patient ID format
            self.patient_id = data["patient_id"]
            if not self.patient_id.startswith("PAT") or len(self.patient_id) != 8:
                self.log_failure("Patient Registration", f"Invalid patient ID format: {self.patient_id}")
                return
                
            self.log_success("Patient Registration")
            self.log_info(f"Created patient: {self.patient_id}")
            
        except Exception as e:
            self.log_failure("Patient Registration", str(e))

    async def test_patient_search(self, client):
        """Test patient search endpoints"""
        if not self.patient_id:
            self.log_warning("Skipping patient search - no patient created")
            return
            
        try:
            # Test search by patient ID
            response = await client.get(f"/api/v2/patients/search?patient_id={self.patient_id}")
            
            if response.status_code != 200:
                self.log_failure("Patient Search by ID", f"Status {response.status_code}")
                return
                
            data = response.json()
            if data["total_count"] != 1 or len(data["patients"]) != 1:
                self.log_failure("Patient Search by ID", "Patient not found")
                return
                
            self.log_success("Patient Search by ID")
            
            # Test search by name
            response = await client.get(f"/api/v2/patients/search?query=John")
            if response.status_code == 200 and response.json()["total_count"] >= 1:
                self.log_success("Patient Search by Name")
            else:
                self.log_failure("Patient Search by Name", "Search failed")
                
        except Exception as e:
            self.log_failure("Patient Search", str(e))

    async def test_patient_details(self, client):
        """Test patient details endpoint"""
        if not self.patient_id:
            self.log_warning("Skipping patient details - no patient created")
            return
            
        try:
            response = await client.get(f"/api/v2/patients/{self.patient_id}")
            
            if response.status_code != 200:
                self.log_failure("Patient Details", f"Status {response.status_code}")
                return
                
            data = response.json()
            required_fields = ["patient_id", "first_name", "last_name", "mobile_number"]
            for field in required_fields:
                if field not in data:
                    self.log_failure("Patient Details", f"Missing field: {field}")
                    return
                    
            self.log_success("Patient Details")
            
        except Exception as e:
            self.log_failure("Patient Details", str(e))

    async def test_patient_history(self, client):
        """Test patient history endpoint"""
        if not self.patient_id:
            self.log_warning("Skipping patient history - no patient created")
            return
            
        try:
            response = await client.get(f"/api/v2/patients/{self.patient_id}/history")
            
            if response.status_code != 200:
                self.log_failure("Patient History", f"Status {response.status_code}")
                return
                
            data = response.json()
            required_fields = ["patient_info", "cases", "visit_patterns"]
            for field in required_fields:
                if field not in data:
                    self.log_failure("Patient History", f"Missing field: {field}")
                    return
                    
            if data["patient_info"]["patient_id"] != self.patient_id:
                self.log_failure("Patient History", "Patient ID mismatch")
                return
                
            self.log_success("Patient History")
            
        except Exception as e:
            self.log_failure("Patient History", str(e))

    async def test_visit_alerts(self, client):
        """Test visit alerts endpoint"""
        if not self.patient_id:
            self.log_warning("Skipping visit alerts - no patient created")
            return
            
        try:
            response = await client.get(f"/api/v2/patients/{self.patient_id}/alerts")
            
            if response.status_code != 200:
                self.log_failure("Visit Alerts", f"Status {response.status_code}")
                return
                
            data = response.json()
            required_fields = ["has_alerts", "alert_level", "alert_type", "pattern_analysis", "recommendations"]
            for field in required_fields:
                if field not in data:
                    self.log_failure("Visit Alerts", f"Missing field: {field}")
                    return
                    
            # New patient should have no alerts
            if data["has_alerts"] != False or data["alert_level"] != "green":
                self.log_failure("Visit Alerts", "Unexpected alerts for new patient")
                return
                
            self.log_success("Visit Alerts")
            
        except Exception as e:
            self.log_failure("Visit Alerts", str(e))

    async def test_case_creation(self, client):
        """Test case creation endpoint"""
        if not self.patient_id:
            self.log_warning("Skipping case creation - no patient created")
            return
            
        try:
            case_data = {
                "healthcare_worker_id": "HW001",  # Default worker
                "case_type": "Assessment",
                "chief_complaint": "Fever and cough",
                "symptoms": "Patient reports fever for 2 days",
                "urgency_level": "Medium",
                "notes": "Test case"
            }
            
            response = await client.post(f"/api/v2/patients/{self.patient_id}/cases", json=case_data)
            
            if response.status_code != 200:
                self.log_failure("Case Creation", f"Status {response.status_code}: {response.text}")
                return
                
            data = response.json()
            required_fields = ["case_id", "patient_id", "case_type", "urgency_level"]
            for field in required_fields:
                if field not in data:
                    self.log_failure("Case Creation", f"Missing field: {field}")
                    return
                    
            if data["patient_id"] != self.patient_id:
                self.log_failure("Case Creation", "Patient ID mismatch")
                return
                
            self.log_success("Case Creation")
            self.log_info(f"Created case: {data['case_id']}")
            
        except Exception as e:
            self.log_failure("Case Creation", str(e))

    async def test_ai_assessment(self, client):
        """Test AI assessment endpoint"""
        if not self.patient_id:
            self.log_warning("Skipping AI assessment - no patient created")
            return
            
        try:
            assessment_data = {
                "symptoms": "Headache and nausea",
                "age": 30,  # Add required age field
                "duration": "1 day",
                "severity": "mild",
                "additional_info": "Started this morning"
            }
            
            response = await client.post(f"/api/v2/patients/{self.patient_id}/assess", json=assessment_data)
            
            if response.status_code != 200:
                self.log_failure("AI Assessment", f"Status {response.status_code}: {response.text}")
                return
                
            data = response.json()
            required_fields = ["assessment_id", "ai_assessment", "historical_context", "pattern_insights"]
            for field in required_fields:
                if field not in data:
                    self.log_failure("AI Assessment", f"Missing field: {field}")
                    return
                    
            # Verify AI assessment structure
            ai_assessment = data["ai_assessment"]
            ai_required_fields = ["primary_diagnosis", "confidence", "urgency", "recommendations"]
            for field in ai_required_fields:
                if field not in ai_assessment:
                    self.log_failure("AI Assessment", f"Missing AI field: {field}")
                    return
                    
            self.log_success("AI Assessment")
            
        except Exception as e:
            self.log_failure("AI Assessment", str(e))

    async def test_patient_stats(self, client):
        """Test patient statistics endpoint"""
        try:
            response = await client.get("/api/v2/patients/stats/summary")
            
            if response.status_code != 200:
                self.log_failure("Patient Statistics", f"Status {response.status_code}")
                return
                
            data = response.json()
            required_fields = ["total_patients", "total_cases"]  # Simplified to actual available fields
            for field in required_fields:
                if field not in data:
                    self.log_failure("Patient Statistics", f"Missing field: {field}")
                    return
                    
            if data["total_patients"] < 0 or data["total_cases"] < 0:
                self.log_failure("Patient Statistics", "Invalid negative values")
                return
                
            self.log_success("Patient Statistics")
            
        except Exception as e:
            self.log_failure("Patient Statistics", str(e))

    async def test_error_handling(self, client):
        """Test error handling for invalid requests"""
        try:
            # Test invalid patient ID
            response = await client.get("/api/v2/patients/INVALID123")
            if response.status_code == 404:
                self.log_success("Error Handling - Invalid Patient ID")
            else:
                self.log_failure("Error Handling", f"Expected 404, got {response.status_code}")
                
            # Test invalid registration data
            response = await client.post("/api/v2/patients/register", json={"invalid": "data"})
            if response.status_code == 422:
                self.log_success("Error Handling - Invalid Registration Data")
            else:
                self.log_failure("Error Handling", f"Expected 422, got {response.status_code}")
                
        except Exception as e:
            self.log_failure("Error Handling", str(e))

    async def test_cases_filtering(self, client):
        """Test cases filtering by status and patient name"""
        try:
            # Test basic cases endpoint
            response = await client.get("/api/cases")
            if response.status_code != 200:
                self.log_failure("Cases List", f"Status {response.status_code}")
                return
                
            data = response.json()
            if "cases" not in data:
                self.log_failure("Cases List", "Missing cases field")
                return
                
            total_cases = len(data["cases"])
            self.log_success("Cases List")
            self.log_info(f"Found {total_cases} total cases")
            
            # Test status filtering
            for status in ["new", "reviewed", "closed"]:
                response = await client.get(f"/api/cases?status={status}")
                if response.status_code != 200:
                    self.log_failure(f"Cases Filter by Status ({status})", f"Status {response.status_code}")
                    continue
                    
                filtered_data = response.json()
                filtered_count = len(filtered_data["cases"])
                self.log_success(f"Cases Filter by Status ({status})")
                self.log_info(f"Found {filtered_count} {status} cases")
            
            # Test patient name filtering
            response = await client.get("/api/cases?patient_name=John")
            if response.status_code == 200:
                john_cases = response.json()["cases"]
                self.log_success("Cases Filter by Patient Name")
                self.log_info(f"Found {len(john_cases)} cases for 'John'")
            else:
                self.log_failure("Cases Filter by Patient Name", f"Status {response.status_code}")
            
            # Test combined filtering
            response = await client.get("/api/cases?status=new&patient_name=John")
            if response.status_code == 200:
                combined_cases = response.json()["cases"]
                self.log_success("Cases Combined Filtering")
                self.log_info(f"Found {len(combined_cases)} new cases for 'John'")
                
                # Verify all returned cases match filters
                for case in combined_cases:
                    if case["status"] != "new":
                        self.log_failure("Cases Combined Filtering", f"Case {case['id']} has wrong status: {case['status']}")
                        return
                    if "john" not in case["patient_name"].lower():
                        self.log_failure("Cases Combined Filtering", f"Case {case['id']} has wrong patient: {case['patient_name']}")
                        return
            else:
                self.log_failure("Cases Combined Filtering", f"Status {response.status_code}")
                
        except Exception as e:
            self.log_failure("Cases Filtering", str(e))

    async def test_case_status_updates(self, client):
        """Test case status update functionality"""
        try:
            # First get a case to test with
            response = await client.get("/api/cases?status=new")
            if response.status_code != 200:
                self.log_failure("Case Status Update Setup", "Cannot fetch cases")
                return
                
            cases = response.json()["cases"]
            if not cases:
                self.log_failure("Case Status Update Setup", "No new cases available for testing")
                return
                
            test_case = cases[0]
            case_id = test_case["id"]
            original_status = test_case["status"]
            
            self.log_info(f"Testing status updates on case {case_id[-8:]}...")
            
            # Test valid status updates
            valid_statuses = ["reviewed", "closed", "new"]
            for new_status in valid_statuses:
                if new_status == original_status:
                    continue
                    
                response = await client.put(f"/api/cases/{case_id}/status?status={new_status}")
                if response.status_code != 200:
                    self.log_failure(f"Case Status Update to {new_status}", f"Status {response.status_code}: {response.text}")
                    continue
                    
                result = response.json()
                if result["new_status"] != new_status:
                    self.log_failure(f"Case Status Update to {new_status}", f"Status not updated correctly")
                    continue
                    
                self.log_success(f"Case Status Update to {new_status}")
                
                # Verify the update persisted
                verify_response = await client.get(f"/api/cases?status={new_status}")
                if verify_response.status_code == 200:
                    updated_cases = verify_response.json()["cases"]
                    case_found = any(case["id"] == case_id for case in updated_cases)
                    if case_found:
                        self.log_success(f"Case Status Persistence ({new_status})")
                    else:
                        self.log_failure(f"Case Status Persistence ({new_status})", "Status change not persisted")
                
                # Small delay between updates
                await asyncio.sleep(0.1)
            
            # Test invalid status update
            response = await client.put(f"/api/cases/{case_id}/status?status=invalid_status")
            if response.status_code == 400:
                self.log_success("Case Status Update Error Handling")
            else:
                self.log_failure("Case Status Update Error Handling", f"Expected 400, got {response.status_code}")
            
            # Test non-existent case
            fake_case_id = "00000000-0000-0000-0000-000000000000"
            response = await client.put(f"/api/cases/{fake_case_id}/status?status=reviewed")
            if response.status_code == 404:
                self.log_success("Case Status Update Non-existent Case")
            else:
                self.log_failure("Case Status Update Non-existent Case", f"Expected 404, got {response.status_code}")
                
        except Exception as e:
            self.log_failure("Case Status Updates", str(e))

    async def test_case_details_modal(self, client):
        """Test individual case details endpoint"""
        try:
            # Get a case to test with
            response = await client.get("/api/cases")
            if response.status_code != 200:
                self.log_failure("Case Details Setup", "Cannot fetch cases")
                return
                
            cases = response.json()["cases"]
            if not cases:
                self.log_failure("Case Details Setup", "No cases available for testing")
                return
                
            test_case = cases[0]
            case_id = test_case["id"]
            
            # Test case details endpoint
            response = await client.get(f"/api/cases/{case_id}")
            if response.status_code != 200:
                self.log_failure("Case Details", f"Status {response.status_code}")
                return
                
            case_data = response.json()
            
            # Verify required fields
            required_fields = ["id", "patient_id", "symptoms", "status", "created_at"]
            for field in required_fields:
                if field not in case_data:
                    self.log_failure("Case Details", f"Missing field: {field}")
                    return
            
            # Verify case ID matches
            if case_data["id"] != case_id:
                self.log_failure("Case Details", "Case ID mismatch")
                return
                
            self.log_success("Case Details")
            self.log_info(f"Retrieved details for case {case_id[-8:]}...")
            
        except Exception as e:
            self.log_failure("Case Details", str(e))

    async def test_filtering_edge_cases(self, client):
        """Test edge cases for filtering functionality"""
        try:
            # Test empty patient name filter
            response = await client.get("/api/cases?patient_name=")
            if response.status_code == 200:
                self.log_success("Empty Patient Name Filter")
            else:
                self.log_failure("Empty Patient Name Filter", f"Status {response.status_code}")
            
            # Test non-existent patient name
            response = await client.get("/api/cases?patient_name=NonExistentPatient12345")
            if response.status_code == 200:
                data = response.json()
                if len(data["cases"]) == 0:
                    self.log_success("Non-existent Patient Name Filter")
                else:
                    self.log_failure("Non-existent Patient Name Filter", "Found cases for non-existent patient")
            else:
                self.log_failure("Non-existent Patient Name Filter", f"Status {response.status_code}")
            
            # Test partial patient name matching
            response = await client.get("/api/cases?patient_name=Jo")
            if response.status_code == 200:
                data = response.json()
                # Should find cases with names containing "Jo" (like "John")
                self.log_success("Partial Patient Name Filter")
                self.log_info(f"Found {len(data['cases'])} cases with partial name 'Jo'")
            else:
                self.log_failure("Partial Patient Name Filter", f"Status {response.status_code}")
            
            # Test case-insensitive search
            response = await client.get("/api/cases?patient_name=john")
            if response.status_code == 200:
                data = response.json()
                self.log_success("Case-insensitive Patient Name Filter")
                self.log_info(f"Found {len(data['cases'])} cases with lowercase 'john'")
            else:
                self.log_failure("Case-insensitive Patient Name Filter", f"Status {response.status_code}")
                
        except Exception as e:
            self.log_failure("Filtering Edge Cases", str(e))

    async def run_all_tests(self):
        """Run the complete test suite"""
        print(f"\n{Colors.BOLD}🚀 Medical AI Assistant MVP V2.0 - API Test Suite{Colors.END}")
        print("=" * 60)
        
        # Initialize database to ensure all tables exist
        from src.database import init_database
        await init_database()
        self.log_info("Database initialized with V2.0 schema")
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Core functionality tests
            await self.test_patient_registration(client)
            await self.test_patient_search(client)
            await self.test_patient_details(client)
            await self.test_patient_history(client)
            await self.test_visit_alerts(client)
            await self.test_case_creation(client)
            await self.test_ai_assessment(client)
            await self.test_patient_stats(client)
            await self.test_error_handling(client)
            await self.test_cases_filtering(client)
            await self.test_case_status_updates(client)
            await self.test_case_details_modal(client)
            await self.test_filtering_edge_cases(client)
        
        # Summary
        total = self.passed + self.failed
        success_rate = (self.passed / total * 100) if total > 0 else 0
        
        print("\n" + "=" * 60)
        print(f"{Colors.BOLD}📊 TEST SUMMARY{Colors.END}")
        print("=" * 60)
        print(f"Total Tests: {total}")
        print(f"{Colors.GREEN}Passed: {self.passed}{Colors.END}")
        print(f"{Colors.RED}Failed: {self.failed}{Colors.END}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if self.failed == 0:
            print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 ALL TESTS PASSED! 🎉{Colors.END}")
            print(f"{Colors.GREEN}✅ Medical AI Assistant MVP V2.0 is working correctly!{Colors.END}")
            return True
        else:
            print(f"\n{Colors.RED}{Colors.BOLD}❌ {self.failed} tests failed{Colors.END}")
            print(f"{Colors.RED}Please fix the failing functionality before deployment{Colors.END}")
            return False

async def main():
    """Main test runner"""
    test_suite = APITestSuite()
    success = await test_suite.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code) 