#!/usr/bin/env python3
"""
End-to-End Backend Workflow Test
Complete test of the Pet Health API from registration to pet management
"""
import requests
import json
import time
import sys
from datetime import datetime
from typing import Optional, Dict, Any


class BackendWorkflowTester:
    """Complete end-to-end test of backend functionality"""
    
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
            "details": details
        })
        
    def make_request(self, method: str, endpoint: str, data: Dict = None, 
                    headers: Dict = None, is_form: bool = False) -> tuple[bool, Dict]:
        """Make HTTP request with error handling"""
        try:
            url = f"{self.base_url}{endpoint}"
            
            if headers is None:
                headers = {}
            
            if self.access_token and "Authorization" not in headers:
                headers["Authorization"] = f"Bearer {self.access_token}"
            
            print(f"    📡 {method} {endpoint}")
            
            if method == "GET":
                response = requests.get(url, headers=headers)
            elif method == "POST":
                if is_form:
                    headers["Content-Type"] = "application/x-www-form-urlencoded"
                    response = requests.post(url, data=data, headers=headers)
                else:
                    headers["Content-Type"] = "application/json"
                    response = requests.post(url, json=data, headers=headers)
            elif method == "PUT":
                headers["Content-Type"] = "application/json"
                response = requests.put(url, json=data, headers=headers)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers)
            else:
                return False, {"error": f"Unsupported method: {method}"}
            
            print(f"    📥 Status: {response.status_code}")
            
            response_data = {}
            if response.content:
                try:
                    response_data = response.json()
                except json.JSONDecodeError:
                    response_data = {"raw_response": response.text}
                
            return response.status_code < 400, response_data
                
        except requests.exceptions.ConnectionError:
            return False, {"error": "Connection failed - is the API running?"}
        except Exception as e:
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
            response = requests.get(f"{self.base_url}/docs")
            if response.status_code == 200 and "swagger" in response.text.lower():
                self.log_test("API Documentation", True, "Swagger docs available")
            else:
                self.log_test("API Documentation", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("API Documentation", False, str(e))
    
    def test_user_registration(self):
        """Test user registration"""
        timestamp = int(time.time())
        test_user = {
            "email": f"test_{timestamp}@example.com",
            "password": "SecurePassword123!"
        }
        
        success, data = self.make_request("POST", "/api/v1/auth/register", test_user)
        if success and "id" in data:
            self.user_id = data["id"]
            self.test_email = test_user["email"]
            self.test_password = test_user["password"]
            self.log_test("User Registration", True, f"User ID: {self.user_id[:8]}...")
        else:
            self.log_test("User Registration", False, f"Error: {data.get('detail', data)}")
            
    def test_user_login(self):
        """Test user login and token generation"""
        if not hasattr(self, 'test_email'):
            self.log_test("User Login", False, "No registered user to test login")
            return
            
        login_data = f"username={self.test_email}&password={self.test_password}"
        
        success, data = self.make_request(
            "POST", 
            "/api/v1/auth/login", 
            login_data,
            is_form=True
        )
        
        if success and "access_token" in data:
            self.access_token = data["access_token"]
            self.log_test("User Login", True, "JWT token received")
        else:
            self.log_test("User Login", False, f"Error: {data}")
    
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
            "weight_kg": 20.5
        }
        
        success, data = self.make_request("POST", "/api/v1/pets/", pet_data)
        if success and "id" in data:
            self.pet_id = data["id"]
            self.log_test("Create Pet", True, f"Pet '{data['name']}' created")
        else:
            self.log_test("Create Pet", False, f"Error: {data}")
    
    def test_get_pets(self):
        """Test retrieving user's pets"""
        if not self.access_token:
            self.log_test("Get Pets", False, "No access token available")
            return
            
        success, data = self.make_request("GET", "/api/v1/pets/")
        if success and isinstance(data, list):
            self.log_test("Get Pets", True, f"Retrieved {len(data)} pet(s)")
        else:
            self.log_test("Get Pets", False, f"Error: {data}")
    
    def test_get_specific_pet(self):
        """Test retrieving a specific pet"""
        if not self.access_token or not self.pet_id:
            self.log_test("Get Specific Pet", False, "No access token or pet ID")
            return
            
        success, data = self.make_request("GET", f"/api/v1/pets/{self.pet_id}")
        if success and "name" in data:
            self.log_test("Get Specific Pet", True, f"Retrieved: {data['name']}")
        else:
            self.log_test("Get Specific Pet", False, f"Error: {data}")
    
    def test_update_pet(self):
        """Test updating pet information"""
        if not self.access_token or not self.pet_id:
            self.log_test("Update Pet", False, "No access token or pet ID")
            return
            
        update_data = {"age_years": 4, "weight_kg": 21.0}
        
        success, data = self.make_request("PUT", f"/api/v1/pets/{self.pet_id}", update_data)
        if success and data.get("age_years") == 4:
            self.log_test("Update Pet", True, f"Age updated to {data['age_years']}")
        else:
            self.log_test("Update Pet", False, f"Error: {data}")
    
    def test_authentication_protection(self):
        """Test that protected endpoints require authentication"""
        current_token = self.access_token
        self.access_token = None
        
        success, data = self.make_request("GET", "/api/v1/pets/")
        self.access_token = current_token
        
        if not success:
            self.log_test("Authentication Protection", True, "Endpoints properly secured")
        else:
            self.log_test("Authentication Protection", False, "Auth not enforced")
    
    def cleanup_test_data(self):
        """Clean up test data"""
        if self.access_token and self.pet_id:
            success, _ = self.make_request("DELETE", f"/api/v1/pets/{self.pet_id}")
            if success:
                print(f"\n🧹 Cleaned up test pet")
    
    def run_all_tests(self):
        """Run complete test suite"""
        print("🚀 PET HEALTH API - END-TO-END WORKFLOW TEST")
        print("=" * 60)
        print(f"Testing: {self.base_url}")
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Basic tests
        print("📊 INFRASTRUCTURE TESTS")
        print("-" * 30)
        self.test_health_check()
        self.test_api_docs()
        
        # Auth tests
        print("\n🔐 AUTHENTICATION TESTS")
        print("-" * 30)
        self.test_user_registration()
        self.test_user_login()
        self.test_authentication_protection()
        
        # Pet management tests
        print("\n🐕 PET MANAGEMENT TESTS")
        print("-" * 30)
        self.test_create_pet()
        self.test_get_pets()
        self.test_get_specific_pet()
        self.test_update_pet()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for r in self.test_results if r["success"])
        total = len(self.test_results)
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"Tests Passed: {passed}/{total} ({success_rate:.1f}%)")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED! Backend fully operational.")
        else:
            print("⚠️  Some tests failed. Check details above.")
            for r in self.test_results:
                if not r["success"]:
                    print(f"  ❌ {r['test']}")
        
        self.cleanup_test_data()
        print("\n✅ Test execution completed")
        
        return success_rate == 100.0


def check_prerequisites():
    """Check if prerequisites are met"""
    try:
        import requests
    except ImportError:
        print("❌ Error: 'requests' library not found.")
        print("Install: pip install requests")
        return False
    
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code != 200:
            print("❌ API health check failed.")
            print("Start backend: docker compose up -d")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API at http://localhost:8000")
        print("Start backend: docker compose up -d")
        return False
    
    return True


def main():
    """Main entry point"""
    if not check_prerequisites():
        sys.exit(1)
    
    tester = BackendWorkflowTester()
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
