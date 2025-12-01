#!/usr/bin/env python3
"""
SymptomService Integration Test
Tests the service layer with real AI integration (without full database)
"""
import asyncio
import sys
import os
from uuid import uuid4

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from app.services.symptom import SymptomService
from app.schemas.symptom import SymptomCreate


class ServiceIntegrationTest:
    """Test symptom analysis through the service layer"""
    
    def __init__(self):
        # Use in-memory SQLite for testing
        engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        self.session_maker = sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        # Generate consistent test pet IDs
        self.test_pet_1 = uuid4()
        self.test_pet_2 = uuid4()
        self.test_pet_3 = uuid4()
    
    def get_test_cases(self):
        """Define test cases with different severity levels"""
        return [
            {
                "name": "🚨 Emergency: Severe Symptoms",
                "pet_id": self.test_pet_1,
                "symptoms": [
                    SymptomCreate(
                        pet_id=self.test_pet_1,
                        symptom_name="vomiting blood",
                        severity="severe",
                        description="Dog has vomited blood multiple times",
                        observed_at=datetime.now()
                    ),
                    SymptomCreate(
                        pet_id=self.test_pet_1,
                        symptom_name="difficulty breathing",
                        severity="severe",
                        description="Labored breathing, gasping",
                        observed_at=datetime.now()
                    )
                ]
            },
            {
                "name": "🟡 Moderate: Common Symptoms",
                "pet_id": self.test_pet_2,
                "symptoms": [
                    SymptomCreate(
                        pet_id=self.test_pet_2,
                        symptom_name="lethargy",
                        severity="moderate",
                        description="Dog seems tired and less active",
                        observed_at=datetime.now()
                    ),
                    SymptomCreate(
                        pet_id=self.test_pet_2,
                        symptom_name="loss of appetite",
                        severity="mild",
                        description="Eating less than normal",
                        observed_at=datetime.now()
                    )
                ]
            },
            {
                "name": "🟢 Mild: Minor Issue",
                "pet_id": self.test_pet_3,
                "symptoms": [
                    SymptomCreate(
                        pet_id=self.test_pet_3,
                        symptom_name="scratching",
                        severity="mild",
                        description="Scratching occasionally behind ears",
                        observed_at=datetime.now()
                    )
                ]
            }
        ]
    
    async def test_case(self, service: SymptomService, test_case: dict):
        """Test a single case through the service"""
        print(f"\n{'=' * 60}")
        print(f"TEST: {test_case['name']}")
        print('=' * 60)
        
        try:
            # Convert symptoms to dict format for AI analysis
            symptoms_json = [symptom.model_dump() for symptom in test_case['symptoms']]
            
            # Call the AI analysis method
            result = await service._analyze_symptoms_with_ai(
                test_case['pet_id'],
                symptoms_json
            )
            
            print("\n✅ AI ANALYSIS RESULTS:")
            print(f"   📊 Urgency Level: {result.get('urgency_level', 'Unknown')}")
            print(f"   🔍 Analysis: {result.get('analysis', 'N/A')[:100]}...")
            print(f"   💡 Recommendations: {result.get('recommendations', 'N/A')[:100]}...")
            
            # Validate response structure
            required_fields = ['urgency_level', 'analysis', 'recommendations']
            if all(key in result for key in required_fields):
                print("\n✅ Response structure is valid")
            else:
                print("\n⚠️  Response structure is missing required fields")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Test failed: {e}")
            print("🔄 Service would fall back to rule-based analysis")
            return False
    
    async def run_tests(self):
        """Run all integration tests"""
        print("🧪 SYMPTOM SERVICE INTEGRATION TEST")
        print("=" * 60)
        print("Testing SymptomService with AI-powered analysis")
        print("=" * 60)
        
        async with self.session_maker() as session:
            service = SymptomService(session)
            test_cases = self.get_test_cases()
            
            results = []
            for test_case in test_cases:
                success = await self.test_case(service, test_case)
                results.append((test_case['name'], success))
                await asyncio.sleep(0.5)  # Brief pause between tests
            
            # Summary
            print(f"\n{'=' * 60}")
            print("📊 TEST SUMMARY")
            print('=' * 60)
            
            passed = sum(1 for _, success in results if success)
            total = len(results)
            
            for name, success in results:
                status = "✅ PASS" if success else "❌ FAIL"
                print(f"{status}: {name}")
            
            print(f"\nTotal: {passed}/{total} tests passed")
            print('=' * 60)
            
            if passed == total:
                print("🎉 All integration tests passed!")
            else:
                print("⚠️  Some tests failed - check output above")
            
            return passed == total


async def main():
    """Main entry point"""
    tester = ServiceIntegrationTest()
    success = await tester.run_tests()
    exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
