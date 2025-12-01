"""
Performance tests for AI symptom analysis
"""
import asyncio
import time
import pytest
from datetime import datetime
from uuid import uuid4
from unittest.mock import patch, AsyncMock, MagicMock
from app.services.symptom import SymptomService
from app.schemas.symptom import SymptomCreate
from app.models.pet import Pet

pytestmark = pytest.mark.asyncio


class TestAIPerformance:
    """Performance benchmarks for AI symptom analysis"""
    
    @pytest.fixture
    def symptom_service(self):
        """Symptom service with mocked database"""
        mock_session = MagicMock()
        return SymptomService(mock_session)
    
    @pytest.fixture
    def sample_pet(self):
        """Sample pet for benchmarking"""
        pet_id = uuid4()
        user_id = uuid4()
        return Pet(
            id=pet_id,
            name="TestPet",
            species="dog",
            breed="Labrador",
            age_years=3,
            weight_kg=22.7,
            user_id=user_id
        )
    
    @pytest.fixture
    def sample_symptoms(self, sample_pet):
        """Sample symptoms for benchmarking"""
        return [SymptomCreate(
            pet_id=sample_pet.id,
            symptom_name="lethargy",
            severity="moderate",
            description="Pet seems tired and less active than usual",
            observed_at=datetime.now(),
            duration_hours=48
        ).model_dump()]
    
    async def test_ai_response_time_benchmark(self, symptom_service, sample_pet, sample_symptoms):
        """Benchmark AI analysis response time"""
        response_times = []
        num_tests = 5
        
        # Mock fast AI response
        with patch.object(symptom_service, '_call_ollama_api', new_callable=AsyncMock) as mock_ollama:
            mock_ollama.return_value = '{"urgency_level": "medium", "analysis": "Test analysis", "recommendations": "Test recommendations"}'
            
            for _ in range(num_tests):
                start_time = time.time()
                
                analysis = await symptom_service._analyze_symptoms_with_ai(sample_pet.id, sample_symptoms)
                
                end_time = time.time()
                response_time = end_time - start_time
                response_times.append(response_time)
                
                assert analysis is not None
        
        avg_response_time = sum(response_times) / len(response_times)
        max_response_time = max(response_times)
        
        # Performance assertions
        assert avg_response_time < 0.1, f"Average response time too slow: {avg_response_time:.3f}s"
        assert max_response_time < 0.2, f"Max response time too slow: {max_response_time:.3f}s"
        
        print(f"AI Analysis Performance:")
        print(f"  Average: {avg_response_time:.3f}s")
        print(f"  Max: {max_response_time:.3f}s")
        print(f"  Min: {min(response_times):.3f}s")
    
    async def test_concurrent_analysis_performance(self, symptom_service, sample_pet, sample_symptoms):
        """Test performance under concurrent analysis load"""
        concurrent_requests = 10
        
        with patch.object(symptom_service, '_call_ollama_api', new_callable=AsyncMock) as mock_ollama:
            mock_ollama.return_value = '{"urgency_level": "medium", "analysis": "Test analysis", "recommendations": "Test recommendations"}'
            
            start_time = time.time()
            
            # Run concurrent analyses
            tasks = [
                symptom_service._analyze_symptoms_with_ai(sample_pet.id, sample_symptoms)
                for _ in range(concurrent_requests)
            ]
            
            results = await asyncio.gather(*tasks)
            
            end_time = time.time()
            total_time = end_time - start_time
            
            # Verify all requests completed successfully
            assert len(results) == concurrent_requests
            assert all(result is not None for result in results)
            
            # Performance check
            avg_time_per_request = total_time / concurrent_requests
            assert avg_time_per_request < 0.5, f"Concurrent performance degraded: {avg_time_per_request:.3f}s per request"
            
            print(f"Concurrent Analysis Performance ({concurrent_requests} requests):")
            print(f"  Total time: {total_time:.3f}s")
            print(f"  Average per request: {avg_time_per_request:.3f}s")
            
    async def test_memory_usage_stability(self, symptom_service, sample_pet, sample_symptoms):
        """Test that memory usage remains stable during analysis"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        with patch.object(symptom_service, '_call_ollama_api', new_callable=AsyncMock) as mock_ollama:
            mock_ollama.return_value = '{"urgency_level": "medium", "analysis": "Test analysis", "recommendations": "Test recommendations"}'
            
            # Run multiple analyses
            for _ in range(20):
                analysis = await symptom_service._analyze_symptoms_with_ai(sample_pet.id, sample_symptoms)
                assert analysis is not None
        
        final_memory = process.memory_info().rss
        memory_increase = (final_memory - initial_memory) / 1024 / 1024  # MB
        
        # Memory shouldn't increase significantly
        assert memory_increase < 10, f"Memory usage increased by {memory_increase:.2f}MB"
        
        print(f"Memory Usage:")
        print(f"  Initial: {initial_memory / 1024 / 1024:.2f}MB")
        print(f"  Final: {final_memory / 1024 / 1024:.2f}MB")
        print(f"  Increase: {memory_increase:.2f}MB")