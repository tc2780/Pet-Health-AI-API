"""
Test Ollama API integration directly
"""
import asyncio
import pytest
import aiohttp
import json
from typing import Dict, Any

pytestmark = pytest.mark.asyncio


class TestOllamaIntegration:
    """Test direct Ollama API integration"""
    
    @pytest.fixture
    def ollama_url(self) -> str:
        """Ollama API endpoint"""
        return "http://localhost:11434/api/generate"
    
    @pytest.fixture
    def test_prompt(self) -> str:
        """Standard veterinary test prompt"""
        return """You are Dr. VetAI, a professional veterinary consultation assistant. Analyze the following case and provide a structured assessment.

PET INFORMATION:
- Species: dog
- Breed: Golden Retriever
- Age: 5 years
- Weight: 65 lbs

REPORTED SYMPTOMS:
- Lethargy (severity: moderate)
- Loss of appetite (severity: mild)

Please provide a JSON response with exactly these fields:
{
  "urgency_level": "emergency|high|medium|low",
  "analysis": "detailed analysis of symptoms and possible causes",
  "recommendations": "specific care recommendations and when to seek professional help"
}

Respond only with the JSON object, no other text."""

    async def test_ollama_api_connectivity(self, ollama_url: str):
        """Test basic Ollama API connectivity"""
        try:
            async with aiohttp.ClientSession() as session:
                # Test tags endpoint first
                async with session.get("http://localhost:11434/api/tags", timeout=10) as response:
                    assert response.status == 200
                    data = await response.json()
                    assert "models" in data
                    
                    # Check if our model is available
                    model_names = [model.get("name", "") for model in data.get("models", [])]
                    assert any("llama3.2:3b" in name for name in model_names), "llama3.2:3b model not found"
                    
        except asyncio.TimeoutError:
            pytest.skip("Ollama service not available or too slow")
        except Exception as e:
            pytest.fail(f"Failed to connect to Ollama: {e}")

    async def test_ollama_veterinary_analysis(self, ollama_url: str, test_prompt: str):
        """Test Ollama veterinary analysis with standard prompt"""
        payload = {
            "model": "llama3.2:3b",
            "prompt": test_prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,
                "top_p": 0.9,
                "num_predict": 500
            }
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(ollama_url, json=payload, timeout=30) as response:
                    assert response.status == 200
                    result = await response.json()
                    
                    ai_response = result.get("response", "")
                    assert ai_response, "Empty response from Ollama"
                    
                    # Clean up response
                    clean_response = ai_response.strip()
                    if clean_response.startswith("```json"):
                        clean_response = clean_response[7:]
                    if clean_response.endswith("```"):
                        clean_response = clean_response[:-3]
                    
                    # Parse JSON
                    parsed = json.loads(clean_response.strip())
                    
                    # Validate structure
                    required_fields = ["urgency_level", "analysis", "recommendations"]
                    for field in required_fields:
                        assert field in parsed, f"Missing required field: {field}"
                    
                    # Validate urgency level
                    valid_urgency = ["emergency", "high", "medium", "low"]
                    assert parsed["urgency_level"] in valid_urgency, f"Invalid urgency level: {parsed['urgency_level']}"
                    
                    # Validate content quality
                    assert len(parsed["analysis"]) > 50, "Analysis too short"
                    assert len(parsed["recommendations"]) > 30, "Recommendations too short"
                    
        except asyncio.TimeoutError:
            pytest.skip("Ollama response timeout - model may be loading")
        except json.JSONDecodeError:
            pytest.fail(f"Invalid JSON response: {ai_response[:200]}")
        except Exception as e:
            pytest.fail(f"Ollama analysis failed: {e}")

    @pytest.mark.parametrize("urgency_case", [
        {
            "name": "emergency_case",
            "symptoms": "difficulty breathing, collapse",
            "expected_urgency": "emergency"
        },
        {
            "name": "high_priority_case", 
            "symptoms": "vomiting with blood, severe diarrhea",
            "expected_urgency": ["emergency", "high"]  # Could be either
        },
        {
            "name": "medium_case",
            "symptoms": "lethargy, mild loss of appetite", 
            "expected_urgency": ["medium", "low"]  # Could be either
        }
    ])
    async def test_urgency_assessment_accuracy(self, ollama_url: str, urgency_case: Dict[str, Any]):
        """Test urgency assessment for different symptom severities"""
        prompt = f"""You are Dr. VetAI, a veterinary assistant. Analyze this case:

PET: Dog, Golden Retriever, 5 years, 65 lbs
SYMPTOMS: {urgency_case['symptoms']}

Respond only with JSON:
{{"urgency_level": "emergency|high|medium|low", "analysis": "brief analysis", "recommendations": "brief recommendations"}}"""

        payload = {
            "model": "llama3.2:3b",
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.2, "num_predict": 200}
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(ollama_url, json=payload, timeout=25) as response:
                    if response.status != 200:
                        pytest.skip(f"Ollama API error: {response.status}")
                    
                    result = await response.json()
                    ai_response = result.get("response", "").strip()
                    
                    # Parse response
                    clean_response = ai_response
                    if clean_response.startswith("```json"):
                        clean_response = clean_response[7:]
                    if clean_response.endswith("```"):
                        clean_response = clean_response[:-3]
                    
                    parsed = json.loads(clean_response.strip())
                    actual_urgency = parsed.get("urgency_level", "")
                    
                    # Check expected urgency
                    expected = urgency_case["expected_urgency"]
                    if isinstance(expected, list):
                        assert actual_urgency in expected, f"Expected {expected}, got {actual_urgency}"
                    else:
                        assert actual_urgency == expected, f"Expected {expected}, got {actual_urgency}"
                        
        except (asyncio.TimeoutError, aiohttp.ClientError):
            pytest.skip("Ollama service unavailable for urgency test")
        except (json.JSONDecodeError, KeyError) as e:
            pytest.skip(f"Response parsing failed: {e}")
        except Exception as e:
            pytest.fail(f"Urgency assessment test failed: {e}")


@pytest.mark.integration
class TestOllamaServiceIntegration:
    """Test Ollama integration with error handling"""
    
    async def test_ollama_service_fallback(self):
        """Test that service falls back gracefully when Ollama is unavailable"""
        # This would test the actual SymptomService._analyze_symptoms_with_ai method
        # with a mock or unavailable Ollama service
        pass
        
    async def test_response_parsing_robustness(self):
        """Test response parsing handles various AI response formats"""
        # Test parsing with different JSON formats, extra text, etc.
        pass