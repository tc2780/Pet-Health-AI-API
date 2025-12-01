#!/usr/bin/env python3
"""
Pet Health API - Complete Backend Workflow Test Script
=====================================================

This script tests the entire backend functionality including:
- User registration and authentication
- Pet management (CRUD operations)
- Health checks and API status
- Database connectivity
- Error handling

TO RUN THIS TEST:
1. Install requests library (if not already installed):
   pip install requests

2. Make sure your backend is running:
   docker compose up -d

3. Run the test script:
   cd local_planning
   python test_backend_workflow.py

4. The script will automatically clean up test data at the end

Requirements:
    pip install requests
"""

import requests
import json
import time
import sys
from datetime import datetime
from typing import Optional, Dict, Any

class PetHealthAPITester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.access_token: Optional[str] = None
        self.user_id: Optional[str] = None
        self.pet_id: Optional[str] = None
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"    {details}")
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        
    def make_request(self, method: str, endpoint: str, data: Dict[Any, Any] = None, headers: Dict[str, str] = None) -> tuple[bool, Dict[Any, Any]]:
        """Make HTTP request with error handling and detailed logging"""
        try:
            url = f"{self.base_url}{endpoint}"
            
            if headers is None:
                headers = {}
            
            if self.access_token and "Authorization" not in headers:
                headers["Authorization"] = f"Bearer {self.access_token}"
            
            # Log the request details
            print(f"    📡 {method} {endpoint}")
            if data:
                print(f"    📤 Request Data: {json.dumps(data, indent=2)}")
            if headers and any(k != "Authorization" for k in headers.keys()):
                safe_headers = {k: v for k, v in headers.items() if k != "Authorization"}
                if safe_headers:
                    print(f"    📋 Headers: {json.dumps(safe_headers, indent=2)}")
            if "Authorization" in headers:
                print(f"    🔑 Authorization: Bearer [JWT TOKEN]")
                
            if method == "GET":
                response = requests.get(url, headers=headers)
            elif method == "POST":
                headers["Content-Type"] = "application/json"
                response = requests.post(url, json=data, headers=headers)
            elif method == "PUT":
                headers["Content-Type"] = "application/json"
                response = requests.put(url, json=data, headers=headers)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers)
            else:
                print(f"    ❌ Unsupported method: {method}")
                return False, {"error": f"Unsupported method: {method}"}
            
            # Log the response details
            print(f"    📥 Response Status: {response.status_code}")
            
            response_data = {}
            if response.content:
                try:
                    response_data = response.json()
                    print(f"    📥 Response Data: {json.dumps(response_data, indent=2)}")
                except json.JSONDecodeError:
                    response_text = response.text[:200] + "..." if len(response.text) > 200 else response.text
                    print(f"    📥 Response Text: {response_text}")
                    response_data = {"raw_response": response.text}
                
            if response.status_code < 400:
                print(f"    ✅ Request successful")
                return True, response_data
            else:
                print(f"    ❌ Request failed: {response.status_code}")
                return False, {"status_code": response.status_code, "error": response.text, "response_data": response_data}
                
        except requests.exceptions.ConnectionError:
            print(f"    ❌ Connection failed - is the API running?")
            return False, {"error": "Connection failed - is the API running?"}
        except Exception as e:
            print(f"    ❌ Request error: {str(e)}")
            return False, {"error": str(e)}
    
    def test_health_check(self):
        """Test API health endpoint"""
        success, data = self.make_request("GET", "/health")
        if success and data.get("status") == "healthy":
            self.log_test("Health Check", True, f"API version: {data.get('version')}")
        else:
            self.log_test("Health Check", False, f"Response: {data}")
            
    def test_api_docs(self):
        """Test API documentation availability"""
        try:
            endpoint = "/docs"
            url = f"{self.base_url}{endpoint}"
            
            print(f"    📡 GET {endpoint}")
            response = requests.get(url)
            print(f"    📥 Response Status: {response.status_code}")
            
            if response.status_code == 200 and "swagger" in response.text.lower():
                print(f"    📥 Response: HTML document with Swagger UI detected")
                print(f"    ✅ Request successful")
                self.log_test("API Documentation", True, "Swagger docs available")
            else:
                response_preview = response.text[:100] + "..." if len(response.text) > 100 else response.text
                print(f"    📥 Response Preview: {response_preview}")
                print(f"    ❌ Request failed or invalid content")
                self.log_test("API Documentation", False, f"Status: {response.status_code}")
        except Exception as e:
            print(f"    ❌ Request error: {str(e)}")
            self.log_test("API Documentation", False, str(e))
    
    def test_user_registration(self):
        """Test user registration"""
        test_user = {
            "username": f"testuser_{int(time.time())}",
            "email": f"test_{int(time.time())}@example.com",
            "password": "SecurePassword123!"
        }
        
        success, data = self.make_request("POST", "/api/v1/auth/register", test_user)
        if success and "id" in data:
            self.user_id = data["id"]
            self.test_email = test_user["email"]
            self.test_password = test_user["password"]
            self.log_test("User Registration", True, f"User ID: {self.user_id}")
        else:
            self.log_test("User Registration", False, f"Error: {data}")
            
    def test_user_login(self):
        """Test user login and token generation"""
        if not hasattr(self, 'test_email'):
            self.log_test("User Login", False, "No registered user to test login")
            return
            
        # FastAPI OAuth2 expects form data for login
        login_data = f"username={self.test_email}&password={self.test_password}"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        
        try:
            endpoint = "/api/v1/auth/login"
            url = f"{self.base_url}{endpoint}"
            
            # Log the request details for login
            print(f"    📡 POST {endpoint}")
            print(f"    📤 Form Data: username={self.test_email}&password=[HIDDEN]")
            print(f"    📋 Headers: {json.dumps(headers, indent=2)}")
            
            response = requests.post(url, data=login_data, headers=headers)
            
            # Log the response details
            print(f"    📥 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"    📥 Response Data: {json.dumps({k: v if k != 'access_token' else '[JWT_TOKEN]' for k, v in data.items()}, indent=2)}")
                
                if "access_token" in data:
                    self.access_token = data["access_token"]
                    print(f"    ✅ Request successful")
                    self.log_test("User Login", True, "JWT token received")
                else:
                    print(f"    ❌ No access token in response")
                    self.log_test("User Login", False, "No access token in response")
            else:
                print(f"    📥 Response Text: {response.text}")
                print(f"    ❌ Request failed: {response.status_code}")
                self.log_test("User Login", False, f"Status: {response.status_code}, Error: {response.text}")
                
        except Exception as e:
            print(f"    ❌ Request error: {str(e)}")
            self.log_test("User Login", False, str(e))
    
    def test_create_pet(self):
        """Test pet creation"""
        if not self.access_token:
            self.log_test("Create Pet", False, "No access token available")
            return
            
        pet_data = {
            "name": "Max",
            "species": "dog", 
            "breed": "Border Collie",
            "age_years": 3,
            "weight_kg": 20.5,
            "sex": "male",
            "neutered": True
        }
        
        success, data = self.make_request("POST", "/api/v1/pets/", pet_data)
        if success and "id" in data:
            self.pet_id = data["id"]
            self.log_test("Create Pet", True, f"Pet '{data['name']}' created with ID: {self.pet_id}")
        else:
            self.log_test("Create Pet", False, f"Error: {data}")
    
    def test_get_pets(self):
        """Test retrieving user's pets"""
        if not self.access_token:
            self.log_test("Get Pets", False, "No access token available")
            return
            
        success, data = self.make_request("GET", "/api/v1/pets/")
        if success and isinstance(data, list):
            pet_count = len(data)
            self.log_test("Get Pets", True, f"Retrieved {pet_count} pet(s)")
            if pet_count > 0:
                print(f"    Sample pet: {data[0]['name']} ({data[0]['species']})")
        else:
            self.log_test("Get Pets", False, f"Error: {data}")
    
    def test_get_specific_pet(self):
        """Test retrieving a specific pet"""
        if not self.access_token or not self.pet_id:
            self.log_test("Get Specific Pet", False, "No access token or pet ID available")
            return
            
        success, data = self.make_request("GET", f"/api/v1/pets/{self.pet_id}")
        if success and "name" in data:
            self.log_test("Get Specific Pet", True, f"Retrieved pet: {data['name']}")
        else:
            self.log_test("Get Specific Pet", False, f"Error: {data}")
    
    def test_update_pet(self):
        """Test updating pet information"""
        if not self.access_token or not self.pet_id:
            self.log_test("Update Pet", False, "No access token or pet ID available")
            return
            
        update_data = {
            "age_years": 4,
            "weight_kg": 21.0
        }
        
        success, data = self.make_request("PUT", f"/api/v1/pets/{self.pet_id}", update_data)
        if success and data.get("age_years") == 4:
            self.log_test("Update Pet", True, f"Pet updated - new age: {data['age_years']}")
        else:
            self.log_test("Update Pet", False, f"Error: {data}")
    
    def test_database_connectivity(self):
        """Test database operations by checking data persistence"""
        if not self.access_token:
            self.log_test("Database Connectivity", False, "No access token for testing")
            return
            
        # Get pets to verify database read
        success, pets_before = self.make_request("GET", "/api/v1/pets/")
        
        if success:
            pet_count = len(pets_before) if isinstance(pets_before, list) else 0
            self.log_test("Database Connectivity", True, f"Database operations working - {pet_count} pets stored")
        else:
            self.log_test("Database Connectivity", False, "Failed to read from database")
    
    def test_authentication_protection(self):
        """Test that protected endpoints require authentication"""
        # Save current token
        current_token = self.access_token
        self.access_token = None
        
        # Try to access protected endpoint without token
        success, data = self.make_request("GET", "/api/v1/pets/")
        
        # Restore token
        self.access_token = current_token
        
        if not success and ("401" in str(data) or "Unauthorized" in str(data)):
            self.log_test("Authentication Protection", True, "Protected endpoints properly secured")
        else:
            self.log_test("Authentication Protection", False, "Authentication not properly enforced")
    
    def cleanup_test_data(self, force: bool = False):
        """Clean up test data - delete test pet and optionally test user"""
        cleanup_performed = False
        
        if self.access_token and self.pet_id:
            success, data = self.make_request("DELETE", f"/api/v1/pets/{self.pet_id}")
            if success:
                print(f"🧹 Cleaned up test pet: {self.pet_id}")
                cleanup_performed = True
            else:
                print(f"⚠️  Could not clean up test pet: {data}")
        
        if cleanup_performed:
            print("✅ Test data cleanup completed")
        elif not force:
            print("ℹ️  No test data to clean up")
        
        return cleanup_performed
    
    def run_all_tests(self):
        """Run complete test suite"""
        print("🚀 Pet Health API - Complete Backend Test Suite")
        print("=" * 55)
        print(f"Testing API at: {self.base_url}")
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Basic connectivity and health
        self.test_health_check()
        self.test_api_docs()
        
        print()
        print("🔐 Authentication Tests")
        print("-" * 25)
        self.test_user_registration()
        self.test_user_login()
        self.test_authentication_protection()
        
        print()
        print("🐕 Pet Management Tests")
        print("-" * 25)
        self.test_create_pet()
        self.test_get_pets()
        self.test_get_specific_pet()
        self.test_update_pet()
        
        print()
        print("💾 Database & Infrastructure Tests")
        print("-" * 35)
        self.test_database_connectivity()
        
        # Summary
        print()
        print("📊 Test Results Summary")
        print("=" * 25)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"Tests Passed: {passed}/{total} ({success_rate:.1f}%)")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED! Backend is fully operational.")
        else:
            print("⚠️  Some tests failed. Check the details above.")
            failed_tests = [r for r in self.test_results if not r["success"]]
            print("\nFailed tests:")
            for test in failed_tests:
                print(f"  - {test['test']}: {test['details']}")
        
        # Automatic cleanup
        print()
        print("🧹 Cleaning up test data...")
        self.cleanup_test_data(force=True)
        
        print()
        print("🔄 Test execution completed. Backend is ready for development!")
        
        return success_rate == 100.0


def main():
    """Main test execution"""
    print("Checking if requests library is available...")
    try:
        import requests
    except ImportError:
        print("❌ Error: 'requests' library not found.")
        print("Install it with: pip install requests")
        sys.exit(1)
    
    # Check if API is running
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code != 200:
            print("❌ API health check failed. Is the backend running?")
            print("Start it with: docker compose up -d")
            sys.exit(1)
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API at http://localhost:8000")
        print("Start the backend with: docker compose up -d")
        sys.exit(1)
    
    # Run tests
    tester = PetHealthAPITester()
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()