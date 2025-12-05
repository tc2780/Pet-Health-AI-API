"""
Performance testing module for Pet Health API using Python/pytest
Integrates with existing test infrastructure and follows pytest conventions
"""

import asyncio
import time
import statistics
import os
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any, Tuple
import pytest
import httpx
from sqlalchemy.orm import Session

from app.core.database import get_db_session
from app.models.user import User
from app.models.pet import Pet
from app.schemas.user import UserCreate
from app.schemas.pet import PetCreate


def get_api_base_url():
    """Get API base URL from environment or default"""
    return os.getenv("API_BASE_URL", "http://localhost:8000")


class PerformanceMetrics:
    """Collect and analyze performance metrics"""
    
    def __init__(self):
        self.response_times = []
        self.error_count = 0
        self.success_count = 0
        self.start_time = None
        self.end_time = None
    
    def add_result(self, response_time: float, success: bool):
        """Add a test result"""
        self.response_times.append(response_time)
        if success:
            self.success_count += 1
        else:
            self.error_count += 1
    
    def start_timer(self):
        """Start timing the test"""
        self.start_time = time.time()
    
    def stop_timer(self):
        """Stop timing the test"""
        self.end_time = time.time()
    
    @property
    def total_requests(self) -> int:
        """Total number of requests made"""
        return self.success_count + self.error_count
    
    @property
    def error_rate(self) -> float:
        """Error rate as percentage"""
        if self.total_requests == 0:
            return 0.0
        return (self.error_count / self.total_requests) * 100
    
    @property
    def success_rate(self) -> float:
        """Success rate as percentage"""
        return 100.0 - self.error_rate
    
    @property
    def avg_response_time(self) -> float:
        """Average response time in seconds"""
        if not self.response_times:
            return 0.0
        return statistics.mean(self.response_times)
    
    @property
    def p95_response_time(self) -> float:
        """95th percentile response time"""
        if not self.response_times:
            return 0.0
        return statistics.quantiles(self.response_times, n=20)[18]  # 95th percentile
    
    @property
    def max_response_time(self) -> float:
        """Maximum response time"""
        if not self.response_times:
            return 0.0
        return max(self.response_times)
    
    @property
    def min_response_time(self) -> float:
        """Minimum response time"""
        if not self.response_times:
            return 0.0
        return min(self.response_times)
    
    @property
    def requests_per_second(self) -> float:
        """Calculate requests per second"""
        if not self.start_time or not self.end_time or self.end_time <= self.start_time:
            return 0.0
        duration = self.end_time - self.start_time
        return self.total_requests / duration
    
    def summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        return {
            "total_requests": self.total_requests,
            "success_count": self.success_count,
            "error_count": self.error_count,
            "error_rate_percent": round(self.error_rate, 2),
            "success_rate_percent": round(self.success_rate, 2),
            "avg_response_time_ms": round(self.avg_response_time * 1000, 2),
            "p95_response_time_ms": round(self.p95_response_time * 1000, 2),
            "max_response_time_ms": round(self.max_response_time * 1000, 2),
            "min_response_time_ms": round(self.min_response_time * 1000, 2),
            "requests_per_second": round(self.requests_per_second, 2),
            "test_duration_seconds": round((self.end_time or 0) - (self.start_time or 0), 2)
        }


class LoadTestClient:
    """HTTP client for load testing with authentication"""
    
    def __init__(self, base_url: str = None):
        self.base_url = base_url or get_api_base_url()
        self.session = httpx.Client(base_url=self.base_url, timeout=30.0)
        self.auth_token = None
    
    def authenticate(self, email: str = "loadtest@example.com", password: str = "loadtest123") -> bool:
        """Authenticate and store token (synchronous version)"""
        try:
            # Try to register first (ignore if user exists)
            self.register_user("Load Test User", email, password)
            
            # Login to get token
            login_data = {
                "username": email,
                "password": password
            }
            
            response = self.session.post("/api/v1/auth/login", data=login_data)
            if response.status_code == 200:
                token_data = response.json()
                self.auth_token = token_data["access_token"]
                return True
            else:
                print(f"Login failed: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Authentication failed: {e}")
        return False
    
    def register_user(self, full_name: str, email: str, password: str) -> bool:
        """Register a new user (synchronous version)"""
        try:
            user_data = {
                "email": email,
                "password": password,
                "full_name": full_name
            }
            response = self.session.post("/api/v1/auth/register", json=user_data)
            return response.status_code in [201, 409]  # 409 = user already exists
        except Exception as e:
            print(f"Registration failed: {e}")
            return False
    
    @property
    def auth_headers(self) -> Dict[str, str]:
        """Get authentication headers"""
        if self.auth_token:
            return {"Authorization": f"Bearer {self.auth_token}"}
        return {}
    
    def get_health(self) -> Tuple[float, bool]:
        """Test health endpoint"""
        start_time = time.time()
        try:
            response = self.session.get("/health")
            response_time = time.time() - start_time
            return response_time, response.status_code == 200
        except Exception:
            return time.time() - start_time, False
    
    def get_user_profile(self) -> Tuple[float, bool]:
        """Test user profile endpoint"""
        start_time = time.time()
        try:
            response = self.session.get("/api/v1/users/me", headers=self.auth_headers)
            response_time = time.time() - start_time
            return response_time, response.status_code == 200
        except Exception:
            return time.time() - start_time, False
    
    def list_pets(self) -> Tuple[float, bool, List[Dict]]:
        """Test list pets endpoint"""
        start_time = time.time()
        try:
            response = self.session.get("/api/v1/pets/", headers=self.auth_headers)
            response_time = time.time() - start_time
            if response.status_code == 200:
                return response_time, True, response.json()
            else:
                print(f"List pets failed: {response.status_code} - {response.text}")
                return response_time, False, []
        except Exception as e:
            print(f"List pets exception: {e}")
            return time.time() - start_time, False, []
    
    def create_pet(self, pet_data: Dict) -> Tuple[float, bool, Dict]:
        """Test create pet endpoint"""
        start_time = time.time()
        try:
            response = self.session.post("/api/v1/pets/", json=pet_data, headers=self.auth_headers)
            response_time = time.time() - start_time
            if response.status_code in [200, 201]:  # Accept both 200 and 201
                return response_time, True, response.json()
            else:
                print(f"Create pet failed: {response.status_code} - {response.text}")
                return response_time, False, {}
        except Exception as e:
            print(f"Create pet exception: {e}")
            return time.time() - start_time, False, {}
    
    def analyze_symptoms(self, symptoms_data: Dict) -> Tuple[float, bool]:
        """Test AI symptom analysis endpoint"""
        start_time = time.time()
        try:
            response = self.session.post("/api/v1/symptoms/analyze", 
                                       json=symptoms_data, 
                                       headers=self.auth_headers,
                                       timeout=45.0)  # Longer timeout for AI
            response_time = time.time() - start_time
            return response_time, response.status_code in [200, 202]
        except Exception:
            return time.time() - start_time, False
    
    def close(self):
        """Close the HTTP session"""
        self.session.close()


async def simulate_user_workflow(client: LoadTestClient, user_id: int, metrics: PerformanceMetrics):
    """Simulate a realistic user workflow"""
    
    # 1. Check health (quick operation)
    response_time, success = client.get_health()
    metrics.add_result(response_time, success)
    
    await asyncio.sleep(0.5)  # Think time
    
    # 2. Get user profile
    response_time, success = client.get_user_profile()
    metrics.add_result(response_time, success)
    
    await asyncio.sleep(1.0)
    
    # 3. List pets
    response_time, success, pets = client.list_pets()
    metrics.add_result(response_time, success)
    
    await asyncio.sleep(1.5)
    
    # 4. Create pet if user has less than 2 pets
    if success and len(pets) < 2:
        pet_data = {
            "name": f"LoadTestPet{user_id}",
            "species": "dog",
            "breed": "Test Breed",
            "age": 3,
            "weight": 20.5
        }
        response_time, success, pet = client.create_pet(pet_data)
        metrics.add_result(response_time, success)
        
        if success:
            pets.append(pet)
    
    await asyncio.sleep(2.0)
    
    # 5. AI analysis (occasionally)
    if pets and len(pets) > 0 and user_id % 3 == 0:  # Every 3rd user
        pet = pets[0]
        symptoms_data = {
            "pet_id": pet["id"],
            "symptoms": ["lethargy", "loss of appetite"],
            "duration": "2 days",
            "severity": "mild"
        }
        response_time, success = client.analyze_symptoms(symptoms_data)
        metrics.add_result(response_time, success)


def run_concurrent_users(num_users: int, duration_seconds: int = 60) -> PerformanceMetrics:
    """Run load test with concurrent users"""
    metrics = PerformanceMetrics()
    metrics.start_timer()
    
    async def worker(user_id: int):
        client = LoadTestClient()
        try:
            # Authenticate (synchronous call)
            auth_success = client.authenticate(
                email=f"loadtest{user_id}@example.com",
                password="loadtest123"
            )
            
            if not auth_success:
                print(f"Authentication failed for user {user_id}")
                return
            
            # Run user workflow for specified duration
            end_time = time.time() + duration_seconds
            while time.time() < end_time:
                await simulate_user_workflow(client, user_id, metrics)
                await asyncio.sleep(2.0)  # Pause between workflows
                
        except Exception as e:
            print(f"Worker {user_id} error: {e}")
        finally:
            client.close()
    
    async def run_all_workers():
        tasks = [worker(i) for i in range(num_users)]
        await asyncio.gather(*tasks, return_exceptions=True)
    
    # Run the load test
    asyncio.run(run_all_workers())
    
    metrics.stop_timer()
    return metrics


# Pytest fixtures and test cases

@pytest.fixture
def load_test_client():
    """Fixture for load test client"""
    client = LoadTestClient()
    yield client
    client.close()


@pytest.mark.performance
@pytest.mark.slow
class TestPerformanceBaseline:
    """Baseline performance tests"""
    
    async def test_health_endpoint_baseline(self, load_test_client):
        """Test health endpoint baseline performance"""
        metrics = PerformanceMetrics()
        
        # Run 100 requests to health endpoint
        for _ in range(100):
            response_time, success = load_test_client.get_health()
            metrics.add_result(response_time, success)
        
        # Performance assertions
        assert metrics.success_rate >= 99.0, f"Success rate {metrics.success_rate}% below 99%"
        assert metrics.avg_response_time < 0.1, f"Avg response time {metrics.avg_response_time}s above 100ms"
        assert metrics.p95_response_time < 0.2, f"P95 response time {metrics.p95_response_time}s above 200ms"
        
        print(f"\n🎯 Health Endpoint Baseline: {metrics.summary()}")
    
    async def test_authenticated_endpoints_baseline(self, load_test_client):
        """Test authenticated endpoints baseline performance"""
        # Authenticate first
        auth_success = load_test_client.authenticate()
        assert auth_success, "Authentication failed"
        
        metrics = PerformanceMetrics()
        
        # Test user profile endpoint
        for _ in range(50):
            response_time, success = load_test_client.get_user_profile()
            metrics.add_result(response_time, success)
        
        # Performance assertions (adjusted for Docker)
        assert metrics.success_rate >= 95.0, f"Success rate {metrics.success_rate}% below 95%"
        assert metrics.avg_response_time < 0.5, f"Avg response time {metrics.avg_response_time}s above 500ms"
        
        print(f"\n🔐 Auth Endpoints Baseline: {metrics.summary()}")
    
    async def test_pet_operations_baseline(self, load_test_client):
        """Test pet CRUD operations baseline performance"""
        auth_success = load_test_client.authenticate()
        assert auth_success, "Authentication failed"
        
        metrics = PerformanceMetrics()
        
        # Test list pets
        for _ in range(30):
            response_time, success, _ = load_test_client.list_pets()
            metrics.add_result(response_time, success)
        
        # Test create pet
        for i in range(10):
            pet_data = {
                "name": f"BaselinePet{i}",
                "species": "dog",
                "breed": "Baseline Breed",
                "age": 2,
                "weight": 15.0
            }
            response_time, success, _ = load_test_client.create_pet(pet_data)
            metrics.add_result(response_time, success)
        
        # Performance assertions (more lenient for Docker environment)
        assert metrics.success_rate >= 80.0, f"Success rate {metrics.success_rate}% below 80%"
        assert metrics.avg_response_time < 1.0, f"Avg response time {metrics.avg_response_time}s above 1s"
        
        print(f"\n🐕 Pet Operations Baseline: {metrics.summary()}")


@pytest.mark.performance
@pytest.mark.slow
class TestLoadTesting:
    """Load testing with concurrent users"""
    
    @pytest.mark.parametrize("num_users,duration", [(5, 30), (10, 60), (25, 120)])
    def test_concurrent_users_load(self, num_users, duration):
        """Test API under concurrent user load"""
        print(f"\n🚀 Starting load test: {num_users} users for {duration}s")
        
        metrics = run_concurrent_users(num_users, duration)
        summary = metrics.summary()
        
        print(f"\n📊 Load Test Results ({num_users} users):")
        print(f"   Total Requests: {summary['total_requests']}")
        print(f"   Success Rate: {summary['success_rate_percent']}%")
        print(f"   Error Rate: {summary['error_rate_percent']}%")
        print(f"   Avg Response Time: {summary['avg_response_time_ms']}ms")
        print(f"   P95 Response Time: {summary['p95_response_time_ms']}ms")
        print(f"   Requests/Second: {summary['requests_per_second']}")
        
        # Load test assertions (adjusted for Docker environment)
        if num_users <= 10:
            # For smaller loads, expect better performance
            assert summary['success_rate_percent'] >= 80.0, \
                f"Success rate {summary['success_rate_percent']}% below 80%"
        else:
            # For higher loads, be more lenient  
            assert summary['success_rate_percent'] >= 70.0, \
                f"Success rate {summary['success_rate_percent']}% below 70%"
        
        assert summary['p95_response_time_ms'] < 10000, \
            f"P95 response time {summary['p95_response_time_ms']}ms above 10s"
        
        assert summary['error_rate_percent'] < 30.0, \
            f"Error rate {summary['error_rate_percent']}% above 30%"


@pytest.mark.performance
@pytest.mark.slow  
class TestStressTesting:
    """Stress testing to find breaking points"""
    
    def test_stress_50_users(self):
        """Stress test with 50 concurrent users"""
        print(f"\n🔥 Stress test: 50 users for 3 minutes")
        
        metrics = run_concurrent_users(50, 180)  # 3 minutes
        summary = metrics.summary()
        
        print(f"\n⚡ Stress Test Results (50 users):")
        print(f"   Total Requests: {summary['total_requests']}")
        print(f"   Success Rate: {summary['success_rate_percent']}%")
        print(f"   Error Rate: {summary['error_rate_percent']}%")
        print(f"   Avg Response Time: {summary['avg_response_time_ms']}ms")
        print(f"   P95 Response Time: {summary['p95_response_time_ms']}ms")
        print(f"   Requests/Second: {summary['requests_per_second']}")
        
        # Stress test assertions (focus on graceful degradation)
        assert summary['success_rate_percent'] >= 75.0, \
            f"Success rate {summary['success_rate_percent']}% below 75% - system failure"
        
        assert summary['error_rate_percent'] < 25.0, \
            f"Error rate {summary['error_rate_percent']}% above 25% - system breakdown"
        
        # Log warning if performance is degraded but not failing
        if summary['p95_response_time_ms'] > 10000:
            print("⚠️  Warning: High response times detected under stress")
        if summary['error_rate_percent'] > 15.0:
            print("⚠️  Warning: Elevated error rate under stress")


# AI-specific performance tests
@pytest.mark.performance
@pytest.mark.slow
@pytest.mark.ai
class TestAIPerformance:
    """AI-specific performance testing"""
    
    async def test_ai_processing_baseline(self, load_test_client):
        """Test AI processing performance baseline"""
        auth_success = load_test_client.authenticate()
        assert auth_success, "Authentication failed"
        
        # Create a test pet first
        pet_data = {
            "name": "AI Test Pet",
            "species": "dog", 
            "breed": "AI Test Breed",
            "age": 3,
            "weight": 20.0
        }
        _, success, pet = load_test_client.create_pet(pet_data)
        assert success, "Failed to create test pet"
        
        metrics = PerformanceMetrics()
        
        # Test AI analysis with various symptoms
        test_cases = [
            {
                "pet_id": pet["id"],
                "symptoms": ["lethargy"],
                "duration": "1 day",
                "severity": "mild"
            },
            {
                "pet_id": pet["id"], 
                "symptoms": ["vomiting", "diarrhea"],
                "duration": "2 days",
                "severity": "moderate"
            },
            {
                "pet_id": pet["id"],
                "symptoms": ["difficulty breathing"],
                "duration": "6 hours", 
                "severity": "severe"
            }
        ]
        
        for symptoms_data in test_cases:
            response_time, success = load_test_client.analyze_symptoms(symptoms_data)
            metrics.add_result(response_time, success)
            
            # Wait between AI requests to avoid overloading
            await asyncio.sleep(5.0)
        
        # AI performance assertions
        assert metrics.success_rate >= 80.0, f"AI success rate {metrics.success_rate}% below 80%"
        assert metrics.avg_response_time < 30.0, f"AI avg response time {metrics.avg_response_time}s above 30s"
        assert metrics.max_response_time < 60.0, f"AI max response time {metrics.max_response_time}s above 60s"
        
        print(f"\n🤖 AI Performance Baseline: {metrics.summary()}")
    
    def test_concurrent_ai_requests(self):
        """Test multiple concurrent AI analysis requests"""
        print(f"\n🤖 Testing concurrent AI requests")
        
        async def ai_worker(worker_id: int, results: List):
            client = LoadTestClient()
            try:
                auth_success = client.authenticate(
                    email=f"aitest{worker_id}@example.com",
                    password="aitest123"
                )
                
                if not auth_success:
                    results.append({"worker_id": worker_id, "success": False, "error": "Auth failed"})
                    return
                
                # Create test pet
                pet_data = {
                    "name": f"ConcurrentAIPet{worker_id}",
                    "species": "cat",
                    "breed": "Test",
                    "age": 2,
                    "weight": 8.0
                }
                _, success, pet = client.create_pet(pet_data)
                
                if not success:
                    results.append({"worker_id": worker_id, "success": False, "error": "Pet creation failed"})
                    return
                
                # Submit AI analysis
                symptoms_data = {
                    "pet_id": pet["id"],
                    "symptoms": ["excessive grooming"],
                    "duration": "3 days",
                    "severity": "mild"
                }
                
                start_time = time.time()
                response_time, success = client.analyze_symptoms(symptoms_data)
                
                results.append({
                    "worker_id": worker_id,
                    "success": success,
                    "response_time": response_time,
                    "timestamp": start_time
                })
                
            finally:
                client.close()
        
        async def run_concurrent_ai():
            results = []
            tasks = [ai_worker(i, results) for i in range(5)]  # 5 concurrent AI requests
            await asyncio.gather(*tasks)
            return results
        
        results = asyncio.run(run_concurrent_ai())
        
        # Analyze results
        successful_results = [r for r in results if r.get("success", False)]
        total_requests = len(results)
        successful_requests = len(successful_results)
        
        print(f"   Total AI Requests: {total_requests}")
        print(f"   Successful: {successful_requests}")
        print(f"   Success Rate: {(successful_requests/total_requests)*100:.1f}%")
        
        if successful_results:
            avg_time = statistics.mean([r["response_time"] for r in successful_results])
            max_time = max([r["response_time"] for r in successful_results])
            print(f"   Avg Response Time: {avg_time:.2f}s")
            print(f"   Max Response Time: {max_time:.2f}s")
        
        # Assertions for concurrent AI processing
        assert successful_requests >= 3, f"Only {successful_requests}/5 AI requests succeeded"
        
        if successful_results:
            avg_time = statistics.mean([r["response_time"] for r in successful_results])
            assert avg_time < 45.0, f"Concurrent AI avg time {avg_time}s above 45s"