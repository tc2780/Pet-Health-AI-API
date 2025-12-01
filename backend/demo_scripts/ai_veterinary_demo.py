#!/usr/bin/env python3
"""
Comprehensive AI Veterinary Analysis Demonstration
Showcases different urgency levels with realistic pet health cases
"""
import asyncio
import aiohttp
import json
from typing import Dict, List, Any


class VeterinaryDemo:
    """Demonstration of AI-powered veterinary analysis"""
    
    def __init__(self, ollama_url: str = "http://localhost:11434/api/generate"):
        self.ollama_url = ollama_url
        self.model = "llama3.2:3b"
        
    def get_test_cases(self) -> List[Dict[str, Any]]:
        """Define realistic test cases for different urgency levels"""
        return [
            {
                "case_name": "🚨 EMERGENCY: Severe Respiratory Distress",
                "pet_info": {
                    "species": "dog",
                    "breed": "Golden Retriever",
                    "age": "7 years",
                    "weight": "70 lbs"
                },
                "symptoms": [
                    {
                        "name": "difficulty breathing",
                        "severity": "severe",
                        "description": "Gasping for air, blue gums"
                    },
                    {
                        "name": "collapse",
                        "severity": "severe",
                        "description": "Unable to stand, weak pulse"
                    }
                ]
            },
            {
                "case_name": "⚠️  HIGH PRIORITY: Gastrointestinal Issues",
                "pet_info": {
                    "species": "cat",
                    "breed": "Persian",
                    "age": "4 years",
                    "weight": "12 lbs"
                },
                "symptoms": [
                    {
                        "name": "vomiting",
                        "severity": "moderate",
                        "description": "Vomiting every few hours"
                    },
                    {
                        "name": "diarrhea",
                        "severity": "moderate",
                        "description": "Loose stools with blood"
                    }
                ]
            },
            {
                "case_name": "🟡 MEDIUM: Behavioral Changes",
                "pet_info": {
                    "species": "dog",
                    "breed": "Labrador",
                    "age": "3 years",
                    "weight": "65 lbs"
                },
                "symptoms": [
                    {
                        "name": "lethargy",
                        "severity": "mild",
                        "description": "Less playful than usual"
                    },
                    {
                        "name": "loss of appetite",
                        "severity": "mild",
                        "description": "Eating 50% of normal food"
                    }
                ]
            }
        ]
    
    def create_prompt(self, pet_info: Dict, symptoms: List[Dict]) -> str:
        """Create a structured veterinary consultation prompt"""
        symptoms_text = [
            f"- {s['name']} (severity: {s['severity']}) - {s['description']}"
            for s in symptoms
        ]
        
        return f"""You are Dr. VetAI, a professional veterinary consultation assistant. Analyze this case:

PET INFORMATION:
- Species: {pet_info['species']}
- Breed: {pet_info['breed']}
- Age: {pet_info['age']}
- Weight: {pet_info['weight']}

REPORTED SYMPTOMS:
{chr(10).join(symptoms_text)}

Provide a JSON response with exactly these fields:
{{
  "urgency_level": "emergency|high|medium|low",
  "analysis": "detailed analysis of symptoms and possible causes",
  "recommendations": "specific care recommendations and when to seek professional help"
}}

Respond only with the JSON object, no other text."""
    
    async def analyze_case(self, test_case: Dict) -> Dict:
        """Call Ollama API to analyze a single case"""
        prompt = self.create_prompt(
            test_case['pet_info'],
            test_case['symptoms']
        )
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.3, "num_predict": 500}
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.ollama_url,
                json=payload,
                timeout=30
            ) as response:
                
                if response.status != 200:
                    raise Exception(f"API call failed: {response.status}")
                
                result = await response.json()
                ai_response = result.get("response", "").strip()
                
                # Clean and parse JSON
                if ai_response.startswith("```json"):
                    ai_response = ai_response[7:]
                if ai_response.endswith("```"):
                    ai_response = ai_response[:-3]
                
                return json.loads(ai_response.strip())
    
    def display_result(self, case_name: str, result: Dict):
        """Display formatted analysis results"""
        urgency = result.get('urgency_level', 'unknown')
        urgency_emoji = {
            'emergency': '🚨',
            'high': '⚠️',
            'medium': '🟡',
            'low': '🟢'
        }.get(urgency, '❓')
        
        print(f"\n{case_name}")
        print("-" * 60)
        print(f"🎯 AI ASSESSMENT: {urgency_emoji} {urgency.upper()} URGENCY")
        print(f"\n📋 Analysis:")
        print(f"   {result.get('analysis', 'N/A')}")
        print(f"\n💊 Recommendations:")
        print(f"   {result.get('recommendations', 'N/A')}")
        print("\n✅ AI analysis successful")
    
    async def run_demo(self):
        """Run the complete demonstration"""
        print("🏥 PET HEALTH AI ASSISTANT - DEMONSTRATION")
        print("=" * 60)
        print("This demo showcases AI-powered veterinary symptom analysis")
        print("using local LLM (Ollama with llama3.2:3b)")
        print("=" * 60)
        
        test_cases = self.get_test_cases()
        
        for i, test_case in enumerate(test_cases, 1):
            try:
                result = await self.analyze_case(test_case)
                self.display_result(test_case['case_name'], result)
                
                if i < len(test_cases):
                    print("\n" + "." * 20 + " Next Case " + "." * 20)
                    await asyncio.sleep(1)
                    
            except Exception as e:
                print(f"\n❌ Error analyzing case: {e}")
                print("🔄 Would fall back to rule-based analysis in production")
        
        print("\n" + "=" * 60)
        print("🎉 DEMONSTRATION COMPLETE!")
        print("=" * 60)
        print("\n🏥 Pet Health API Features:")
        print("   ✅ Local LLM integration (llama3.2:3b)")
        print("   ✅ Professional veterinary analysis")
        print("   ✅ Intelligent urgency assessment")
        print("   ✅ Privacy-preserving (no external APIs)")
        print("   ✅ Fallback to rule-based analysis")
        print("=" * 60)


async def main():
    """Main entry point"""
    demo = VeterinaryDemo()
    await demo.run_demo()


if __name__ == "__main__":
    asyncio.run(main())
