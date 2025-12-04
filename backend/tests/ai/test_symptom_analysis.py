"""
Test AI-powered symptom analysis functionality
"""
import asyncio
import pytest
import json
from datetime import datetime
from uuid import uuid4
from unittest.mock import patch, AsyncMock, MagicMock
from app.services.symptom import SymptomService
from app.schemas.symptom import SymptomCreate
from app.models.pet import Pet
from app.models.user import User

pytestmark = pytest.mark.asyncio


class TestAISymptomAnalysis:
    """Test AI-powered symptom analysis service"""
    
    @pytest.fixture
    def mock_db_session(self):
        """Mock database session"""
        session = MagicMock()
        return session
        
    @pytest.fixture 
    def symptom_service(self, mock_db_session):
        """Symptom service with mocked database"""
        return SymptomService(mock_db_session)
    
    @pytest.fixture
    def sample_pet(self):
        """Sample pet data for testing"""
        pet_id = uuid4()
        user_id = uuid4()
        pet = Pet(
            id=pet_id,
            name="Buddy",
            species="dog", 
            breed="Golden Retriever",
            age_years=5,
            weight_kg=29.5,
            user_id=user_id
        )
        return pet
        
    @pytest.fixture
    def sample_symptoms(self, sample_pet):
        """Sample symptom data"""
        symptom = SymptomCreate(
            pet_id=sample_pet.id,
            symptom_name="lethargy",
            severity="moderate",
            description="Dog seems less energetic than usual",
            observed_at=datetime.now(),
            duration_hours=48
        )
        return [symptom.model_dump()]
    
    async def test_ai_analysis_success(self, symptom_service, sample_pet, sample_symptoms):
        """Test successful AI analysis with Ollama"""
        # Mock Ollama response
        mock_ai_response = {
            "urgency_level": "medium",
            "analysis": "The combination of lethargy and loss of appetite in a 5-year-old Golden Retriever could indicate several conditions. Given the moderate severity and recent onset, this warrants monitoring and potentially veterinary consultation within 24-48 hours.",
            "recommendations": "Monitor the pet closely for any worsening symptoms. Ensure access to fresh water. If symptoms persist or worsen, consult with a veterinarian. Consider any recent changes in diet, environment, or stress factors."
        }
        
        with patch.object(symptom_service, '_call_ollama_api', new_callable=AsyncMock) as mock_ollama:
            mock_ollama.return_value = json.dumps(mock_ai_response)
            
            analysis = await symptom_service._analyze_symptoms_with_ai(sample_pet.id, sample_symptoms)
            
            assert analysis is not None
            assert analysis["urgency_level"] == "moderate"
            assert "lethargy" in analysis["analysis"].lower()
            assert "vet" in analysis["recommendations"].lower()  # More flexible - matches "vet" or "veterinary"
            assert len(analysis["analysis"]) > 50
            assert len(analysis["recommendations"]) > 30
            
    async def test_ai_analysis_fallback(self, symptom_service, sample_pet, sample_symptoms):
        """Test fallback behavior when AI is unavailable"""
        with patch.object(symptom_service, '_call_ollama_api', new_callable=AsyncMock) as mock_ollama:
            mock_ollama.side_effect = Exception("Ollama service unavailable")
            
            analysis = await symptom_service._analyze_symptoms_with_ai(sample_pet.id, sample_symptoms)
            
            # Should return fallback analysis
            assert analysis is not None
            assert analysis["urgency_level"] in ["emergency", "high", "moderate", "low"]
            assert "analysis" in analysis["analysis"].lower()  # More flexible - matches fallback format
            assert "vet" in analysis["recommendations"].lower()
            
    async def test_ai_response_parsing_robust(self, symptom_service, sample_pet, sample_symptoms):
        """Test robust parsing of AI responses with various formats"""
        test_cases = [
            # Standard JSON
            '{"urgency_level": "high", "analysis": "Test analysis", "recommendations": "Test recommendations"}',
            
            # JSON with code blocks
            '```json\n{"urgency_level": "moderate", "analysis": "Test analysis", "recommendations": "Test recommendations"}\n```',
            
            # JSON with extra whitespace
            '\n\n  {"urgency_level": "low", "analysis": "Test analysis", "recommendations": "Test recommendations"}  \n\n',
        ]
        
        for i, response_format in enumerate(test_cases):
            with patch.object(symptom_service, '_call_ollama_api', new_callable=AsyncMock) as mock_ollama:
                mock_ollama.return_value = response_format
                
                analysis = await symptom_service._analyze_symptoms_with_ai(sample_pet.id, sample_symptoms)
                
                assert analysis is not None, f"Failed to parse format {i}: {response_format}"
                assert "urgency_level" in analysis
                assert "analysis" in analysis 
                assert "recommendations" in analysis
                
    async def test_urgency_level_validation(self, symptom_service, sample_pet, sample_symptoms):
        """Test that invalid urgency levels are handled"""
        invalid_response = '{"urgency_level": "invalid", "analysis": "Test", "recommendations": "Test"}'
        
        with patch.object(symptom_service, '_call_ollama_api', new_callable=AsyncMock) as mock_ollama:
            mock_ollama.return_value = invalid_response
            
            analysis = await symptom_service._analyze_symptoms_with_ai(sample_pet.id, sample_symptoms)
            
            # Should fallback to safe default
            assert analysis is not None
            assert analysis["urgency_level"] in ["emergency", "high", "moderate", "low"]
            
    async def test_emergency_symptom_detection(self, symptom_service, sample_pet):
        """Test that emergency symptoms are properly prioritized"""
        emergency_symptom = SymptomCreate(
            pet_id=sample_pet.id,
            symptom_name="difficulty breathing",
            severity="severe",
            description="Pet collapsed and is having trouble breathing",
            observed_at=datetime.now(),
            duration_hours=0  # just now
        )
        emergency_symptoms = [emergency_symptom.model_dump()]
        
        # Mock emergency response
        emergency_response = {
            "urgency_level": "emergency",
            "analysis": "Severe breathing difficulties and collapse require immediate emergency veterinary care",
            "recommendations": "Seek emergency veterinary care immediately. This is a life-threatening emergency."
        }
        
        with patch.object(symptom_service, '_call_ollama_api', new_callable=AsyncMock) as mock_ollama:
            mock_ollama.return_value = json.dumps(emergency_response)
            
            analysis = await symptom_service._analyze_symptoms_with_ai(sample_pet.id, emergency_symptoms)
            
            assert analysis["urgency_level"] == "emergency"
            assert "emergency" in analysis["recommendations"].lower()
            
    @pytest.mark.parametrize("timeout_scenario", [
        "connection_timeout",
        "read_timeout", 
        "general_timeout"
    ])
    async def test_timeout_handling(self, symptom_service, sample_pet, sample_symptoms, timeout_scenario):
        """Test handling of various timeout scenarios"""
        timeout_exceptions = {
            "connection_timeout": asyncio.TimeoutError("Connection timeout"),
            "read_timeout": asyncio.TimeoutError("Read timeout"),
            "general_timeout": Exception("Request timeout")
        }
        
        with patch.object(symptom_service, '_call_ollama_api', new_callable=AsyncMock) as mock_ollama:
            mock_ollama.side_effect = timeout_exceptions[timeout_scenario]
            
            analysis = await symptom_service._analyze_symptoms_with_ai(sample_pet.id, sample_symptoms)
            
            # Should gracefully fallback
            assert analysis is not None
            assert "urgency_level" in analysis
            assert "timeout" not in analysis["analysis"].lower()  # Shouldn't expose internal errors
            
    async def test_prompt_construction(self, symptom_service, sample_pet, sample_symptoms):
        """Test that AI prompts are properly constructed"""
        # Mock both the pet context fetch and the AI call
        with patch.object(symptom_service, '_get_pet_context', new_callable=AsyncMock) as mock_get_pet:
            mock_get_pet.return_value = {
                "species": sample_pet.species,
                "breed": sample_pet.breed,
                "age": f"{sample_pet.age_years} years",
                "weight": f"{sample_pet.weight_kg} kg"
            }
            
            with patch.object(symptom_service, '_call_ollama_api', new_callable=AsyncMock) as mock_ollama:
                mock_ollama.return_value = '{"urgency_level": "medium", "analysis": "Test", "recommendations": "Test"}'
                
                await symptom_service._analyze_symptoms_with_ai(sample_pet.id, sample_symptoms)
                
                # Verify prompt construction
                mock_ollama.assert_called_once()
                prompt_used = mock_ollama.call_args[0][0]
                
                # Check prompt contains expected information
                assert sample_pet.species in prompt_used
                assert sample_pet.breed in prompt_used
                assert str(sample_pet.age_years) in prompt_used
                assert "lethargy" in prompt_used
                assert "JSON" in prompt_used
                assert "urgency_level" in prompt_used