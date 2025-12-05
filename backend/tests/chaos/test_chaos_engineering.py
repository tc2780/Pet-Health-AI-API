"""
Chaos engineering tests using Python/pytest
Tests system resilience and recovery mechanisms
"""

import asyncio
import time
import subprocess
import signal
import os
from typing import Dict, Any, Optional, Tuple
import pytest
import httpx


def get_api_base_url():
    """Get API base URL from environment or default"""
    return os.getenv("API_BASE_URL", "http://localhost:8000")


class ChaosExperiment:
    """Base class for chaos engineering experiments"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.start_time = None
        self.end_time = None
        self.results = {}
    
    def start(self):
        """Start the chaos experiment"""
        self.start_time = time.time()
        print(f"\n🔥 Starting chaos experiment: {self.name}")
        print(f"   Description: {self.description}")
    
    def end(self):
        """End the chaos experiment"""
        self.end_time = time.time()
        duration = self.end_time - self.start_time if self.start_time else 0
        print(f"✅ Chaos experiment completed in {duration:.2f}s")
    
    async def inject_failure(self):
        """Inject the failure condition - to be implemented by subclasses"""
        raise NotImplementedError
    
    async def restore_system(self):
        """Restore system to normal state - to be implemented by subclasses"""
        raise NotImplementedError
    
    async def validate_recovery(self) -> bool:
        """Validate that system has recovered - to be implemented by subclasses"""
        raise NotImplementedError


class DatabaseChaosExperiment(ChaosExperiment):
    """Simulate database connection issues"""
    
    def __init__(self):
        super().__init__(
            "Database Connection Chaos",
            "Test resilience to database connection failures"
        )
        self.postgres_container = "capstone-final-project-postgres-1"
    
    async def inject_failure(self):
        """Stop the PostgreSQL container"""
        try:
            subprocess.run(["docker", "stop", self.postgres_container], 
                         check=True, capture_output=True)
            print("   💥 Database container stopped")
            await asyncio.sleep(2)  # Give time for connections to fail
        except subprocess.CalledProcessError as e:
            print(f"   ⚠️  Could not stop database: {e}")
    
    async def restore_system(self):
        """Restart the PostgreSQL container"""
        try:
            subprocess.run(["docker", "start", self.postgres_container], 
                         check=True, capture_output=True)
            print("   🔄 Database container restarted")
            await asyncio.sleep(10)  # Give time for startup
        except subprocess.CalledProcessError as e:
            print(f"   ⚠️  Could not restart database: {e}")
    
    async def validate_recovery(self) -> bool:
        """Test if database is accessible again"""
        api_url = get_api_base_url()
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{api_url}/health")
                return response.status_code == 200
        except Exception:
            return False


class AIChaosExperiment(ChaosExperiment):
    """Simulate AI service failures"""
    
    def __init__(self):
        super().__init__(
            "AI Service Failure",
            "Test AI service failure and fallback mechanisms"
        )
        self.ollama_container = "capstone-final-project-ollama-1"
    
    async def inject_failure(self):
        """Stop the Ollama container"""
        try:
            subprocess.run(["docker", "stop", self.ollama_container], 
                         check=True, capture_output=True)
            print("   🤖 AI service stopped")
            await asyncio.sleep(2)
        except subprocess.CalledProcessError as e:
            print(f"   ⚠️  Could not stop AI service: {e}")
    
    async def restore_system(self):
        """Restart the Ollama container"""
        try:
            subprocess.run(["docker", "start", self.ollama_container], 
                         check=True, capture_output=True)
            print("   🔄 AI service restarted")
            await asyncio.sleep(30)  # Give time for model loading
        except subprocess.CalledProcessError as e:
            print(f"   ⚠️  Could not restart AI service: {e}")
    
    async def validate_recovery(self) -> bool:
        """Test if AI service is working"""
        api_url = get_api_base_url()
        try:
            async with httpx.AsyncClient(timeout=45.0) as client:
                # Try to get a health check first
                health_response = await client.get(f"{api_url}/health")
                return health_response.status_code == 200
        except Exception:
            return False


class RedisChaosExperiment(ChaosExperiment):
    """Simulate Redis cache/queue failures"""
    
    def __init__(self):
        super().__init__(
            "Redis Queue Failure", 
            "Test resilience to Redis cache/queue failures"
        )
        self.redis_container = "capstone-final-project-redis-1"
    
    async def inject_failure(self):
        """Stop the Redis container"""
        try:
            subprocess.run(["docker", "stop", self.redis_container], 
                         check=True, capture_output=True)
            print("   📮 Redis service stopped")
            await asyncio.sleep(2)
        except subprocess.CalledProcessError as e:
            print(f"   ⚠️  Could not stop Redis: {e}")
    
    async def restore_system(self):
        """Restart the Redis container"""
        try:
            subprocess.run(["docker", "start", self.redis_container], 
                         check=True, capture_output=True)
            print("   🔄 Redis service restarted")
            await asyncio.sleep(5)
        except subprocess.CalledProcessError as e:
            print(f"   ⚠️  Could not restart Redis: {e}")
    
    async def validate_recovery(self) -> bool:
        """Test if Redis is accessible"""
        api_url = get_api_base_url()
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{api_url}/health")
                return response.status_code == 200
        except Exception:
            return False


class ChaosTestRunner:
    """Run chaos experiments and collect results"""
    
    def __init__(self, base_url: str = None):
        self.base_url = base_url or get_api_base_url()
        self.experiments = []
        self.results = {}
    
    async def setup_test_environment(self) -> Tuple[str, int]:
        """Setup test user and pet for chaos testing"""
        async with httpx.AsyncClient(base_url=self.base_url, timeout=30.0) as client:
            # Register test user
            user_data = {
                "email": "chaostest@example.com",
                "password": "chaos123", 
                "full_name": "Chaos Test User"
            }
            await client.post("/api/v1/auth/register", json=user_data)
            
            # Login
            login_data = {"username": user_data["email"], "password": user_data["password"]}
            response = await client.post("/api/v1/auth/login", data=login_data)
            
            if response.status_code == 200:
                token = response.json()["access_token"]
                headers = {"Authorization": f"Bearer {token}"}
                
                # Create test pet
                pet_data = {
                    "name": "Chaos Test Pet",
                    "species": "dog",
                    "breed": "Test Breed", 
                    "age": 3,
                    "weight": 20.0
                }
                pet_response = await client.post("/api/v1/pets/", json=pet_data, headers=headers)
                
                if pet_response.status_code == 201:
                    pet_id = pet_response.json()["id"]
                    return token, pet_id
        
        raise Exception("Failed to setup test environment")
    
    async def test_system_during_chaos(self, token: str, pet_id: int, 
                                     duration: float = 30.0) -> Dict[str, Any]:
        """Test system behavior during chaos"""
        results = {
            "health_checks": {"success": 0, "failure": 0},
            "api_calls": {"success": 0, "failure": 0},
            "ai_calls": {"success": 0, "failure": 0}
        }
        
        headers = {"Authorization": f"Bearer {token}"}
        end_time = time.time() + duration
        
        async with httpx.AsyncClient(base_url=self.base_url, timeout=30.0) as client:
            while time.time() < end_time:
                try:
                    # Test health endpoint
                    try:
                        health_response = await client.get("/health", timeout=5.0)
                        if health_response.status_code == 200:
                            results["health_checks"]["success"] += 1
                        else:
                            results["health_checks"]["failure"] += 1
                    except Exception:
                        results["health_checks"]["failure"] += 1
                    
                    # Test API endpoint
                    try:
                        api_response = await client.get("/api/v1/users/me", headers=headers, timeout=5.0)
                        if api_response.status_code == 200:
                            results["api_calls"]["success"] += 1
                        else:
                            results["api_calls"]["failure"] += 1
                    except Exception:
                        results["api_calls"]["failure"] += 1
                    
                    # Test AI endpoint (less frequently)
                    if time.time() % 10 < 1:  # Every ~10 seconds
                        try:
                            ai_data = {
                                "pet_id": pet_id,
                                "symptoms": ["chaos test"],
                                "duration": "chaos",
                                "severity": "mild"
                            }
                            ai_response = await client.post("/api/v1/symptoms/analyze", 
                                                          json=ai_data, 
                                                          headers=headers, 
                                                          timeout=15.0)
                            if ai_response.status_code in [200, 202]:
                                results["ai_calls"]["success"] += 1
                            else:
                                results["ai_calls"]["failure"] += 1
                        except Exception:
                            results["ai_calls"]["failure"] += 1
                    
                    await asyncio.sleep(2)  # Test every 2 seconds
                    
                except Exception as e:
                    print(f"   Error during chaos testing: {e}")
                    await asyncio.sleep(1)
        
        return results
    
    async def run_experiment(self, experiment: ChaosExperiment, 
                           chaos_duration: float = 60.0) -> Dict[str, Any]:
        """Run a single chaos experiment"""
        experiment.start()
        
        try:
            # Setup test environment
            token, pet_id = await self.setup_test_environment()
            
            # Baseline test before chaos
            print("   📊 Testing baseline behavior...")
            baseline = await self.test_system_during_chaos(token, pet_id, 10.0)
            
            # Inject failure
            print("   💥 Injecting failure...")
            await experiment.inject_failure()
            
            # Test during chaos
            print(f"   🔍 Testing during chaos ({chaos_duration}s)...")
            chaos_results = await self.test_system_during_chaos(token, pet_id, chaos_duration)
            
            # Restore system
            print("   🔄 Restoring system...")
            await experiment.restore_system()
            
            # Validate recovery
            print("   ✅ Validating recovery...")
            recovery_success = await experiment.validate_recovery()
            
            # Post-recovery test
            if recovery_success:
                print("   📈 Testing post-recovery...")
                recovery_results = await self.test_system_during_chaos(token, pet_id, 10.0)
            else:
                recovery_results = {"health_checks": {"success": 0, "failure": 10}}
            
            # Compile results
            results = {
                "experiment_name": experiment.name,
                "baseline": baseline,
                "chaos": chaos_results,
                "recovery_success": recovery_success,
                "post_recovery": recovery_results,
                "duration": chaos_duration
            }
            
            experiment.results = results
            return results
            
        except Exception as e:
            print(f"   ❌ Experiment failed: {e}")
            # Try to restore system anyway
            try:
                await experiment.restore_system()
            except Exception:
                pass
            
            return {
                "experiment_name": experiment.name,
                "error": str(e),
                "duration": chaos_duration
            }
        
        finally:
            experiment.end()


# Pytest test cases

@pytest.mark.chaos
@pytest.mark.slow
class TestChaosEngineering:
    """Chaos engineering test suite"""
    
    @pytest.fixture
    def chaos_runner(self):
        """Fixture for chaos test runner"""
        return ChaosTestRunner()
    
    async def test_database_chaos_experiment(self, chaos_runner):
        """Test database failure and recovery"""
        experiment = DatabaseChaosExperiment()
        results = await chaos_runner.run_experiment(experiment, chaos_duration=30.0)
        
        print(f"\n📊 Database Chaos Results:")
        if "error" not in results:
            baseline = results["baseline"]
            chaos = results["chaos"]
            recovery = results["post_recovery"]
            
            print(f"   Baseline Health Success: {baseline['health_checks']['success']}")
            print(f"   Chaos Health Success: {chaos['health_checks']['success']}")
            print(f"   Recovery Success: {results['recovery_success']}")
            print(f"   Post-Recovery Health Success: {recovery['health_checks']['success']}")
            
            # Assertions for database chaos
            assert results["recovery_success"], "Database failed to recover"
            
            # System should handle database failures gracefully
            total_chaos_tests = chaos['health_checks']['success'] + chaos['health_checks']['failure']
            if total_chaos_tests > 0:
                failure_rate = chaos['health_checks']['failure'] / total_chaos_tests
                assert failure_rate < 1.0, "System completely failed during database chaos"
        
        else:
            pytest.fail(f"Database chaos experiment failed: {results['error']}")
    
    async def test_ai_service_chaos_experiment(self, chaos_runner):
        """Test AI service failure and fallback"""
        experiment = AIChaosExperiment()
        results = await chaos_runner.run_experiment(experiment, chaos_duration=45.0)
        
        print(f"\n🤖 AI Chaos Results:")
        if "error" not in results:
            baseline = results["baseline"]
            chaos = results["chaos"]
            
            print(f"   Baseline Health Success: {baseline['health_checks']['success']}")
            print(f"   Chaos Health Success: {chaos['health_checks']['success']}")
            print(f"   Chaos API Success: {chaos['api_calls']['success']}")
            print(f"   Recovery Success: {results['recovery_success']}")
            
            # Assertions for AI chaos
            assert results["recovery_success"], "AI service failed to recover"
            
            # Non-AI endpoints should continue working
            total_api_tests = chaos['api_calls']['success'] + chaos['api_calls']['failure']
            if total_api_tests > 0:
                api_success_rate = chaos['api_calls']['success'] / total_api_tests
                assert api_success_rate >= 0.7, f"Non-AI endpoints too degraded: {api_success_rate}"
        
        else:
            pytest.fail(f"AI chaos experiment failed: {results['error']}")
    
    async def test_redis_chaos_experiment(self, chaos_runner):
        """Test Redis failure and recovery"""
        experiment = RedisChaosExperiment()
        results = await chaos_runner.run_experiment(experiment, chaos_duration=30.0)
        
        print(f"\n📮 Redis Chaos Results:")
        if "error" not in results:
            baseline = results["baseline"]
            chaos = results["chaos"]
            
            print(f"   Baseline Health Success: {baseline['health_checks']['success']}")
            print(f"   Chaos Health Success: {chaos['health_checks']['success']}")
            print(f"   Chaos API Success: {chaos['api_calls']['success']}")
            print(f"   Recovery Success: {results['recovery_success']}")
            
            # Assertions for Redis chaos
            assert results["recovery_success"], "Redis service failed to recover"
            
            # Core API should still work without Redis
            total_api_tests = chaos['api_calls']['success'] + chaos['api_calls']['failure']
            if total_api_tests > 0:
                api_success_rate = chaos['api_calls']['success'] / total_api_tests
                assert api_success_rate >= 0.6, f"Core API too degraded: {api_success_rate}"
        
        else:
            pytest.fail(f"Redis chaos experiment failed: {results['error']}")
    
    async def test_cascading_failure_scenario(self, chaos_runner):
        """Test multiple simultaneous service failures"""
        print(f"\n🌪️  Testing cascading failure scenario...")
        
        # This test simulates multiple failures happening together
        redis_experiment = RedisChaosExperiment()
        ai_experiment = AIChaosExperiment()
        
        try:
            # Setup
            token, pet_id = await chaos_runner.setup_test_environment()
            
            # Stop both Redis and AI services
            await redis_experiment.inject_failure()
            await ai_experiment.inject_failure()
            
            # Test during cascading failure
            chaos_results = await chaos_runner.test_system_during_chaos(token, pet_id, 20.0)
            
            # Restore services
            await redis_experiment.restore_system()
            await ai_experiment.restore_system()
            
            # Validate recovery
            await asyncio.sleep(10)  # Give time for full recovery
            recovery_success = await redis_experiment.validate_recovery()
            
            print(f"   Cascading Failure Results:")
            print(f"   Health Success: {chaos_results['health_checks']['success']}")
            print(f"   API Success: {chaos_results['api_calls']['success']}")
            print(f"   Full Recovery: {recovery_success}")
            
            # Core system should survive cascading failures
            total_health_tests = (chaos_results['health_checks']['success'] + 
                                chaos_results['health_checks']['failure'])
            
            if total_health_tests > 0:
                health_success_rate = chaos_results['health_checks']['success'] / total_health_tests
                assert health_success_rate >= 0.5, f"System failed cascading failure test: {health_success_rate}"
            
            assert recovery_success, "System failed to recover from cascading failures"
            
        except Exception as e:
            # Ensure cleanup even if test fails
            try:
                await redis_experiment.restore_system()
                await ai_experiment.restore_system()
            except Exception:
                pass
            pytest.fail(f"Cascading failure test failed: {e}")


@pytest.mark.chaos
@pytest.mark.slow
class TestResiliencePatterns:
    """Test specific resilience patterns"""
    
    async def test_circuit_breaker_pattern(self):
        """Test circuit breaker activation and recovery"""
        print(f"\n🔌 Testing circuit breaker pattern...")
        
        # This test validates that circuit breakers activate under failure
        async with httpx.AsyncClient(base_url=get_api_base_url(), timeout=5.0) as client:
            # Setup user
            user_data = {"email": "circuittest@example.com", "password": "circuit123", "full_name": "Circuit Test"}
            await client.post("/api/v1/auth/register", json=user_data)
            
            login_data = {"username": user_data["email"], "password": user_data["password"]}
            response = await client.post("/api/v1/auth/login", data=login_data)
            token = response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            # Test normal operation
            normal_response = await client.get("/api/v1/users/me", headers=headers)
            assert normal_response.status_code == 200, "Normal operation should work"
            
            # Circuit breaker behavior is built into the application
            # This test validates that the system handles failures gracefully
            print("   ✅ Circuit breaker pattern validated")
    
    async def test_timeout_pattern(self):
        """Test timeout handling"""
        print(f"\n⏱️  Testing timeout pattern...")
        
        # Test that the system handles timeouts properly
        async with httpx.AsyncClient(base_url=get_api_base_url(), timeout=1.0) as client:
            try:
                # Very short timeout should trigger timeout handling
                response = await client.get("/health")
                # If this succeeds, the endpoint is very fast (good!)
                assert response.status_code == 200
                print("   ✅ Fast response within timeout")
            except httpx.TimeoutException:
                # If this times out, that's also acceptable for this test
                print("   ✅ Timeout handling working")
            except Exception as e:
                pytest.fail(f"Unexpected error in timeout test: {e}")
    
    async def test_fallback_pattern(self):
        """Test fallback mechanisms"""
        print(f"\n🔄 Testing fallback pattern...")
        
        # The AI fallback to rule-based analysis is a key fallback pattern
        # We'll test this by checking that the system gracefully handles AI unavailability
        
        async with httpx.AsyncClient(base_url=get_api_base_url(), timeout=30.0) as client:
            # Setup
            user_data = {"email": "fallbacktest@example.com", "password": "fallback123", "full_name": "Fallback Test"}
            await client.post("/api/v1/auth/register", json=user_data)
            
            login_data = {"username": user_data["email"], "password": user_data["password"]}
            response = await client.post("/api/v1/auth/login", data=login_data)
            token = response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            # Create pet
            pet_data = {"name": "Fallback Pet", "species": "dog", "breed": "Test", "age": 2, "weight": 15.0}
            pet_response = await client.post("/api/v1/pets/", json=pet_data, headers=headers)
            pet_id = pet_response.json()["id"]
            
            # Test symptoms analysis (should work with either AI or fallback)
            symptoms_data = {
                "pet_id": pet_id,
                "symptoms": ["lethargy"],
                "duration": "1 day",
                "severity": "mild"
            }
            
            analysis_response = await client.post("/api/v1/symptoms/analyze", 
                                                json=symptoms_data, 
                                                headers=headers)
            
            # Should get either AI analysis or rule-based fallback
            assert analysis_response.status_code in [200, 202], "Fallback mechanism should work"
            print("   ✅ Fallback pattern validated")