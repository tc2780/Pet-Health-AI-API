#!/usr/bin/env python3
"""
Direct Ollama API connectivity and response test
Quick validation script to ensure Ollama is running correctly
"""
import asyncio
import aiohttp
import json
import os
import sys


async def test_ollama_connectivity(model="llama3.2:1b"):
    """Test basic Ollama API connectivity and response parsing"""
    print(f"🧪 Testing Ollama AI Integration with {model}...")
    print("=" * 60)
    
    # Simple test prompt for veterinary analysis
    test_prompt = """You are Dr. VetAI, a professional veterinary consultation assistant. Analyze the following case:

PET INFORMATION:
- Species: dog
- Breed: Golden Retriever
- Age: 5 years
- Weight: 65 lbs

REPORTED SYMPTOMS:
- Lethargy (severity: moderate)
- Loss of appetite (severity: mild)

Provide a JSON response with exactly these fields:
{
  "urgency_level": "emergency|high|medium|low",
  "analysis": "detailed analysis of symptoms and possible causes",
  "recommendations": "specific care recommendations"
}

Respond only with the JSON object, no other text."""

    payload = {
        "model": model,
        "prompt": test_prompt,
        "stream": False,
        "options": {
            "temperature": 0.3,
            "top_p": 0.9,
            "num_predict": 500
        }
    }
    
    # Get Ollama URL from environment variable (for Docker) or use localhost
    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    
    try:
        async with aiohttp.ClientSession() as session:
            print(f"📡 Calling Ollama API at {ollama_url}...")
            
            async with session.post(
                f"{ollama_url}/api/generate", 
                json=payload, 
                timeout=30
            ) as response:
                
                if response.status != 200:
                    print(f"❌ API call failed with status: {response.status}")
                    error_text = await response.text()
                    print(f"Error: {error_text}")
                    return False
                
                result = await response.json()
                ai_response = result.get("response", "")
                
                print("\n✅ Raw AI Response:")
                print("-" * 60)
                print(ai_response)
                print("-" * 60)
                
                # Parse and validate JSON response
                try:
                    clean_response = ai_response.strip()
                    if clean_response.startswith("```json"):
                        clean_response = clean_response[7:]
                    if clean_response.endswith("```"):
                        clean_response = clean_response[:-3]
                    
                    parsed = json.loads(clean_response.strip())
                    
                    print("\n✅ Parsed JSON Response:")
                    print(json.dumps(parsed, indent=2))
                    
                    # Validate required fields
                    required_fields = ["urgency_level", "analysis", "recommendations"]
                    missing_fields = [field for field in required_fields if field not in parsed]
                    
                    if missing_fields:
                        print(f"\n⚠️  Missing required fields: {missing_fields}")
                        return False
                    
                    print("\n✅ All required fields present!")
                    
                    # Validate urgency level
                    valid_urgency = ["emergency", "high", "medium", "low"]
                    if parsed["urgency_level"] not in valid_urgency:
                        print(f"⚠️  Invalid urgency level: {parsed['urgency_level']}")
                        return False
                    
                    print(f"✅ Valid urgency level: {parsed['urgency_level']}")
                    
                    print("\n" + "=" * 60)
                    print("🎉 Ollama Integration Test: PASSED")
                    print("=" * 60)
                    return True
                    
                except json.JSONDecodeError as e:
                    print(f"\n❌ Failed to parse JSON: {e}")
                    print("🔄 Response would use fallback parsing in production")
                    return False
                    
    except asyncio.TimeoutError:
        print("⏰ Request timed out - Ollama might be slow or busy")
        print("💡 Try: docker compose restart ollama")
        return False
    except aiohttp.ClientError as e:
        print(f"❌ Connection error: {e}")
        print("💡 Ensure Ollama is running: docker compose ps")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


if __name__ == "__main__":
    # Parse command line arguments for model selection
    model = "llama3.2:3b"  # Default to more accurate model
    if len(sys.argv) > 1:
        if sys.argv[1] in ["1b", "llama3.2:1b"]:
            model = "llama3.2:1b"
        elif sys.argv[1] in ["3b", "llama3.2:3b"]:
            model = "llama3.2:3b"
        else:
            print(f"Usage: {sys.argv[0]} [1b|3b|llama3.2:1b|llama3.2:3b]")
            print(f"Defaulting to {model}")
    
    success = asyncio.run(test_ollama_connectivity(model))
    exit(0 if success else 1)
