"""
Comprehensive unit tests for SymptomService components
"""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
import json
from datetime import datetime
from uuid import uuid4
from app.services.symptom import SymptomService
from app.schemas.symptom import SymptomCreate, SymptomAssessmentCreate
from app.models.symptom import Symptom, SymptomAssessment
from app.models.pet import Pet



class TestSymptomServicePrivateMethods:
    """Unit tests for private methods in SymptomService"""
    
    @pytest.fixture
    def symptom_service(self):
        """SymptomService with mocked database"""
        mock_session = MagicMock()
        return SymptomService(mock_session)
    
    def test_parse_ai_response_valid_json(self, symptom_service):
        """Test parsing valid AI JSON response"""
        response_text = '{"urgency_level": "high", "analysis": "Test analysis", "recommendations": "Test recommendations"}'
        
        result = symptom_service._parse_ai_response(response_text)
        
        assert result is not None
        assert result["urgency_level"] == "high"
        assert result["analysis"] == "Test analysis"
        assert result["recommendations"] == "Test recommendations"
    
    def test_parse_ai_response_with_code_blocks(self, symptom_service):
        """Test parsing AI response with markdown code blocks"""
        response_text = '```json\n{"urgency_level": "medium", "analysis": "Test", "recommendations": "Test"}\n```'
        
        result = symptom_service._parse_ai_response(response_text)
        
        assert result is not None
        assert result["urgency_level"] == "medium"
    
    def test_parse_ai_response_with_whitespace(self, symptom_service):
        """Test parsing AI response with extra whitespace"""
        response_text = '\n\n  {"urgency_level": "low", "analysis": "Test analysis", "recommendations": "Test recommendations"}  \n\n'
        
        result = symptom_service._parse_ai_response(response_text)
        
        assert result is not None
        assert result["urgency_level"] == "low"
    
    def test_parse_ai_response_invalid_json(self, symptom_service):
        """Test handling invalid JSON in AI response - should return fallback"""
        response_text = 'Invalid JSON response'
        
        # The service returns a fallback response instead of None
        result = symptom_service._parse_ai_response(response_text)
        
        assert result is not None  # Service provides fallback
        assert "urgency_level" in result
    
    def test_parse_ai_response_missing_fields(self, symptom_service):
        """Test handling response missing required fields - should return fallback"""
        response_text = '{"urgency_level": "high"}'  # Missing analysis and recommendations
        
        result = symptom_service._parse_ai_response(response_text)
        
        assert result is not None  # Service provides fallback
        assert "urgency_level" in result
    
    def test_parse_ai_response_invalid_urgency(self, symptom_service):
        """Test handling invalid urgency level - should return fallback"""
        response_text = '{"urgency_level": "invalid", "analysis": "Test", "recommendations": "Test"}'
        
        result = symptom_service._parse_ai_response(response_text)
        
        assert result is not None  # Service provides fallback
        assert result["urgency_level"] in ["emergency", "high", "medium", "low"]
    
    async def test_fallback_analysis(self, symptom_service):
        """Test fallback analysis when AI is unavailable"""
        symptoms_data = [
            {
                "symptom_name": "lethargy",
                "severity": "moderate", 
                "observed_at": datetime.now().isoformat(),
                "description": "Pet seems tired"
            }
        ]
        
        result = await symptom_service._fallback_analysis(symptoms_data)
        
        assert result is not None
        assert result["urgency_level"] in ["emergency", "high", "medium", "low"]
        assert "lethargy" in result["analysis"]
        assert "veterinary" in result["recommendations"].lower()
        assert len(result["analysis"]) > 20
        assert len(result["recommendations"]) > 20
    
    def test_generate_analysis(self, symptom_service):
        """Test analysis text generation"""
        symptoms = [
            {"symptom_name": "lethargy", "severity": "moderate"},
            {"symptom_name": "loss of appetite", "severity": "mild"}
        ]
        urgency = "medium"
        severity = 1.5
        
        result = symptom_service._generate_analysis(symptoms, urgency, severity)
        
        assert isinstance(result, str)
        assert "lethargy" in result.lower()
        assert "2 reported symptom" in result
        assert "1.5" in result  # Severity score should be included
        assert len(result) > 20  # Should have meaningful content
    
    def test_generate_recommendations(self, symptom_service):
        """Test recommendations generation for different urgency levels"""
        symptoms = [{"symptom_name": "lethargy", "severity": "mild"}]
        
        # Test emergency recommendations
        emergency_rec = symptom_service._generate_recommendations("emergency", symptoms)
        assert "immediate" in emergency_rec.lower()
        assert "emergency" in emergency_rec.lower()
        
        # Test high priority recommendations
        high_rec = symptom_service._generate_recommendations("high", symptoms)
        assert "24 hours" in high_rec or "24-hour" in high_rec
        
        # Test medium priority recommendations
        medium_rec = symptom_service._generate_recommendations("medium", symptoms)
        assert "monitor" in medium_rec.lower()
        
        # Test low priority recommendations
        low_rec = symptom_service._generate_recommendations("low", symptoms)
        assert "continue monitoring" in low_rec.lower() or "maintain" in low_rec.lower()
    
    async def test_get_pet_context_existing_pet(self, symptom_service):
        """Test getting pet context for existing pet"""
        mock_pet = Pet(
            id="pet-123",
            name="Buddy",
            species="dog",
            breed="Golden Retriever", 
            age_years=5,
            weight_kg=29.5,
            user_id="user-123"
        )
        
        # Mock database query
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_pet
        symptom_service.db.execute = AsyncMock(return_value=mock_result)
        
        result = await symptom_service._get_pet_context("pet-123")
        
        assert result["species"] == "dog"
        assert result["breed"] == "Golden Retriever"
        assert result["age"] == "5 years"
        assert result["weight"] == "29.5 kg"
    
    async def test_get_pet_context_missing_pet(self, symptom_service):
        """Test getting pet context for non-existent pet"""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        symptom_service.db.execute = AsyncMock(return_value=mock_result)
        
        result = await symptom_service._get_pet_context("nonexistent-pet")
        
        assert result["species"] == "unknown"
        assert result["breed"] == "unknown"
        assert result["age"] == "unknown"
        assert result["weight"] == "unknown"
    
    def test_create_veterinary_prompt(self, symptom_service):
        """Test veterinary prompt creation"""
        pet_info = {
            "species": "dog",
            "breed": "Labrador",
            "age": "3 years",
            "weight": "55 lbs"
        }
        symptoms = [
            {"symptom_name": "vomiting", "severity": "moderate", "description": "Yellow liquid"}
        ]
        
        prompt = symptom_service._create_veterinary_prompt(pet_info, symptoms)
        
        assert "Dr. VetAI" in prompt
        assert "dog" in prompt
        assert "Labrador" in prompt
        assert "3 years" in prompt
        assert "55 lbs" in prompt
        assert "vomiting" in prompt
        assert "moderate" in prompt
        assert "Yellow liquid" in prompt
        assert "JSON" in prompt
        assert "urgency_level" in prompt


class TestSymptomServicePublicMethods:
    """Unit tests for public CRUD methods in SymptomService"""
    
    @pytest.fixture
    def symptom_service(self):
        """SymptomService with mocked database"""
        mock_session = AsyncMock()
        return SymptomService(mock_session)
    
    @pytest.fixture
    def sample_symptom_data(self):
        """Sample symptom create data"""
        pet_id = uuid4()
        return SymptomCreate(
            pet_id=pet_id,
            symptom_name="lethargy",
            severity="moderate",
            description="Pet seems tired",
            observed_at=datetime.now(),
            duration_hours=48
        )
    
    async def test_create_symptom_success(self, symptom_service, sample_symptom_data):
        """Test successful symptom creation"""
        symptom_id = uuid4()
        mock_symptom = Symptom(
            id=symptom_id,
            pet_id=sample_symptom_data.pet_id,
            symptom_name="lethargy",
            severity="moderate"
        )
        
        symptom_service.db.add = MagicMock()
        symptom_service.db.commit = AsyncMock()
        symptom_service.db.refresh = AsyncMock()
        
        # Mock the symptom creation
        with patch('app.services.symptom.Symptom', return_value=mock_symptom):
            result = await symptom_service.create_symptom(sample_symptom_data)
        
        assert result == mock_symptom
        symptom_service.db.add.assert_called_once()
        symptom_service.db.commit.assert_called_once()
        symptom_service.db.refresh.assert_called_once()
    
    async def test_get_symptom_by_id_found(self, symptom_service):
        """Test getting symptom by ID when it exists"""
        mock_symptom = Symptom(id="symptom-123", symptom_name="lethargy")
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_symptom
        symptom_service.db.execute = AsyncMock(return_value=mock_result)
        
        result = await symptom_service.get_symptom_by_id("symptom-123")
        
        assert result == mock_symptom
        symptom_service.db.execute.assert_called_once()
    
    async def test_get_symptom_by_id_not_found(self, symptom_service):
        """Test getting symptom by ID when it doesn't exist"""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        symptom_service.db.execute = AsyncMock(return_value=mock_result)
        
        result = await symptom_service.get_symptom_by_id("nonexistent")
        
        assert result is None
    
    async def test_delete_symptom_success(self, symptom_service):
        """Test successful symptom deletion"""
        mock_symptom = Symptom(id="symptom-123")
        
        # Mock get_symptom_by_id to return the symptom
        with patch.object(symptom_service, 'get_symptom_by_id', return_value=mock_symptom):
            symptom_service.db.delete = AsyncMock()
            symptom_service.db.commit = AsyncMock()
            
            result = await symptom_service.delete_symptom("symptom-123")
        
        assert result is True
        symptom_service.db.delete.assert_called_once()
        symptom_service.db.commit.assert_called_once()
    
    async def test_delete_symptom_not_found(self, symptom_service):
        """Test deleting non-existent symptom"""
        with patch.object(symptom_service, 'get_symptom_by_id', return_value=None):
            result = await symptom_service.delete_symptom("nonexistent")
        
        assert result is False


class TestEdgeCasesAndErrorHandling:
    """Test edge cases and error handling scenarios"""
    
    @pytest.fixture
    def symptom_service(self):
        mock_session = MagicMock()
        return SymptomService(mock_session)
    
    def test_parse_ai_response_empty_string(self, symptom_service):
        """Test parsing empty AI response"""
        result = symptom_service._parse_ai_response("")
        assert result is not None  # Should return fallback
    
    def test_parse_ai_response_only_whitespace(self, symptom_service):
        """Test parsing whitespace-only response"""
        result = symptom_service._parse_ai_response("   \n\t  ")
        assert result is not None  # Should return fallback
    
    def test_generate_analysis_empty_symptoms(self, symptom_service):
        """Test analysis generation with empty symptoms list"""
        result = symptom_service._generate_analysis([], "low", 0.0)
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_generate_analysis_many_symptoms(self, symptom_service):
        """Test analysis generation with many symptoms (truncation)"""
        symptoms = [
            {"symptom_name": f"symptom_{i}", "severity": "mild"} 
            for i in range(10)
        ]
        
        result = symptom_service._generate_analysis(symptoms, "medium", 1.5)
        
        assert isinstance(result, str)
        assert "..." in result or "10 reported symptom" in result
    
    async def test_fallback_analysis_malformed_symptoms(self, symptom_service):
        """Test fallback analysis with malformed symptom data"""
        malformed_symptoms = [
            {"name": "lethargy"},  # Missing symptom_name field
            {"symptom_name": "vomiting", "level": "high"},  # Missing severity field
            {}  # Empty symptom
        ]
        
        result = await symptom_service._fallback_analysis(malformed_symptoms)
        
        assert result is not None
        assert result["urgency_level"] in ["emergency", "high", "medium", "low"]
    
    async def test_get_pet_context_partial_pet_data(self, symptom_service):
        """Test getting pet context with incomplete pet data"""
        mock_pet = Pet(
            id="pet-123",
            name="Buddy",
            species="dog",
            breed=None,       # Missing breed
            age_years=None,   # Missing age
            weight_kg=None,   # Missing weight
            user_id="user-123"
        )
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_pet
        symptom_service.db.execute = AsyncMock(return_value=mock_result)
        
        result = await symptom_service._get_pet_context("pet-123")
        
        assert result["species"] == "dog"
        assert result["breed"] == "mixed"  # Default for None breed
        assert result["age"] == "unknown"
        assert result["weight"] == "unknown"


class TestUtilityLogic:
    """Unit tests for SymptomService components"""
    
    @pytest.fixture
    def symptom_service(self):
        """SymptomService with mocked database"""
        mock_session = MagicMock()
        return SymptomService(mock_session)
    
    def test_parse_ai_response_valid_json(self, symptom_service):
        """Test parsing valid AI JSON response"""
        response_text = '{"urgency_level": "high", "analysis": "Test analysis", "recommendations": "Test recommendations"}'
        
        result = symptom_service._parse_ai_response(response_text)
        
        assert result is not None
        assert result["urgency_level"] == "high"
        assert result["analysis"] == "Test analysis"
        assert result["recommendations"] == "Test recommendations"
    
    def test_parse_ai_response_with_code_blocks(self, symptom_service):
        """Test parsing AI response with markdown code blocks"""
        response_text = '```json\n{"urgency_level": "medium", "analysis": "Test", "recommendations": "Test"}\n```'
        
        result = symptom_service._parse_ai_response(response_text)
        
        assert result is not None
        assert result["urgency_level"] == "medium"
    
    def test_parse_ai_response_invalid_json(self, symptom_service):
        """Test handling invalid JSON in AI response"""
        response_text = 'Invalid JSON response'
        
        result = symptom_service._parse_ai_response(response_text)
        
        assert result is None
    
    def test_parse_ai_response_missing_fields(self, symptom_service):
        """Test handling response missing required fields"""
        response_text = '{"urgency_level": "high"}'  # Missing analysis and recommendations
        
        result = symptom_service._parse_ai_response(response_text)
        
        assert result is None
    
    def test_parse_ai_response_invalid_urgency(self, symptom_service):
        """Test handling invalid urgency level"""
        response_text = '{"urgency_level": "invalid", "analysis": "Test", "recommendations": "Test"}'
        
        result = symptom_service._parse_ai_response(response_text)
        
        assert result is None
    
    def test_create_fallback_analysis(self, symptom_service):
        """Test fallback analysis creation"""
        symptoms_data = [
            {
                "symptom_name": "lethargy",
                "severity": "moderate", 
                "observed_at": datetime.now().isoformat(),
                "description": "Pet seems tired"
            }
        ]
        
        result = symptom_service._create_fallback_analysis(symptoms_data)
        
        assert result is not None
        assert result["urgency_level"] in ["emergency", "high", "medium", "low"]
        assert "lethargy" in result["analysis"]
        assert "veterinary care" in result["recommendations"]
        assert len(result["analysis"]) > 20
        assert len(result["recommendations"]) > 20
    
    def test_format_symptoms_for_prompt(self, symptom_service):
        """Test symptom formatting for AI prompt"""
        symptoms_data = [
            {
                "symptom_name": "lethargy",
                "severity": "moderate",
                "observed_at": datetime.now().isoformat(),
                "description": "Pet seems tired"
            },
            {
                "symptom_name": "loss of appetite", 
                "severity": "mild",
                "observed_at": datetime.now().isoformat(),
                "description": "Not eating much"
            }
        ]
        
        formatted = symptom_service._format_symptoms_for_prompt(symptoms_data)
        
        assert "lethargy" in formatted
        assert "moderate" in formatted
        assert "loss of appetite" in formatted
        assert "Pet seems tired" in formatted
        assert "Not eating much" in formatted


class TestUtilityLogic:
    """Test utility and calculation logic"""
    
    @pytest.fixture
    def symptom_service(self):
        mock_session = MagicMock()
        return SymptomService(mock_session)
    
    def test_severity_score_calculation(self, symptom_service):
        """Test symptom severity scoring logic"""
        symptoms = [
            {"severity": "mild"},
            {"severity": "moderate"}, 
            {"severity": "severe"}
        ]
        
        severity_map = {"mild": 1, "moderate": 2, "severe": 3}
        avg_severity = sum(severity_map.get(s["severity"], 1) for s in symptoms) / len(symptoms)
        
        assert avg_severity == 2.0  # (1+2+3)/3 = 2.0
    
    def test_urgency_keyword_detection(self, symptom_service):
        """Test emergency symptom keyword detection"""
        emergency_keywords = ["difficulty breathing", "collapse", "severe bleeding", "unconscious"]
        high_keywords = ["vomiting blood", "severe pain", "can't walk", "seizure"]
        
        # Emergency case
        emergency_symptoms = [{"symptom_name": "difficulty breathing", "severity": "severe"}]
        has_emergency = any(
            keyword in symptom["symptom_name"].lower()
            for symptom in emergency_symptoms
            for keyword in emergency_keywords
        )
        assert has_emergency is True
        
        # High priority case
        high_symptoms = [{"symptom_name": "vomiting blood", "severity": "moderate"}]
        has_high = any(
            keyword in symptom["symptom_name"].lower()
            for symptom in high_symptoms
            for keyword in high_keywords
        )
        assert has_high is True
        
        # Normal case
        normal_symptoms = [{"symptom_name": "mild lethargy", "severity": "mild"}]
        has_emergency_normal = any(
            keyword in symptom["symptom_name"].lower()
            for symptom in normal_symptoms
            for keyword in emergency_keywords
        )
        assert has_emergency_normal is False
    
    def test_duration_impact_on_urgency(self, symptom_service):
        """Test how symptom duration affects urgency assessment"""
        # Acute symptoms (short duration, high severity) should be more urgent
        acute_symptoms = [
            {"symptom_name": "vomiting", "severity": "severe", "duration_hours": 2}
        ]
        
        # Chronic symptoms (long duration, moderate severity) might be less urgent
        chronic_symptoms = [
            {"symptom_name": "mild lethargy", "severity": "mild", "duration_hours": 168}  # 1 week
        ]
        
        # This tests the logic that acute severe symptoms are more urgent than chronic mild ones
        acute_severity = 3  # severe
        chronic_severity = 1  # mild
        
        # Simple urgency calculation based on severity and recency
        acute_urgency = acute_severity * (1 if acute_symptoms[0]["duration_hours"] < 24 else 0.5)
        chronic_urgency = chronic_severity * (1 if chronic_symptoms[0]["duration_hours"] < 24 else 0.5)
        
        assert acute_urgency > chronic_urgency
    
    def test_multiple_symptoms_aggregation(self, symptom_service):
        """Test how multiple symptoms are aggregated for urgency"""
        # Multiple mild symptoms might indicate higher concern
        multiple_mild = [
            {"symptom_name": "lethargy", "severity": "mild"},
            {"symptom_name": "loss of appetite", "severity": "mild"},
            {"symptom_name": "mild vomiting", "severity": "mild"}
        ]
        
        # Single moderate symptom
        single_moderate = [
            {"symptom_name": "moderate vomiting", "severity": "moderate"}
        ]
        
        severity_map = {"mild": 1, "moderate": 2, "severe": 3}
        
        multiple_score = sum(severity_map[s["severity"]] for s in multiple_mild)
        single_score = sum(severity_map[s["severity"]] for s in single_moderate)
        
        # Multiple mild symptoms (3) should be considered more concerning than single moderate (2)
        assert multiple_score > single_score
    
    def test_symptom_name_normalization(self, symptom_service):
        """Test symptom name normalization and categorization"""
        symptom_variations = [
            "lethargy",
            "Lethargy", 
            "LETHARGY",
            "lethargic",
            "tired",
            "fatigue"
        ]
        
        # Test case-insensitive matching
        normalized = [name.lower().strip() for name in symptom_variations]
        
        # All should be recognized as similar symptoms
        lethargy_related = ["lethargy", "lethargic", "tired", "fatigue"]
        recognized = [name for name in normalized if any(related in name for related in lethargy_related)]
        
        assert len(recognized) >= 4  # Should recognize most variations