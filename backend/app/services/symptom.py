"""
Symptom service for database operations and AI analysis
"""
import json
import aiohttp
from typing import List, Optional, Dict, Any
from datetime import datetime
import time
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.models.symptom import Symptom, SymptomAssessment as SymptomAssessmentModel
from app.schemas.symptom import SymptomCreate, SymptomUpdate, SymptomAssessmentCreate, SymptomAssessment as SymptomAssessmentSchema


class SymptomService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # Symptom CRUD operations
    async def create_symptom(self, symptom_data: SymptomCreate) -> Symptom:
        """Create a new symptom record"""
        symptom = Symptom(**symptom_data.model_dump())
        self.db.add(symptom)
        await self.db.commit()
        await self.db.refresh(symptom)
        return symptom
    
    async def get_symptom_by_id(self, symptom_id: str) -> Optional[Symptom]:
        """Get symptom by ID"""
        result = await self.db.execute(
            select(Symptom).where(Symptom.id == symptom_id)
        )
        return result.scalar_one_or_none()
    
    async def get_symptoms_by_pet(self, pet_id: str) -> List[Symptom]:
        """Get all symptoms for a specific pet"""
        result = await self.db.execute(
            select(Symptom)
            .where(Symptom.pet_id == pet_id)
            .order_by(Symptom.observed_at.desc())
        )
        return result.scalars().all()
    
    async def get_symptoms_by_user(self, user_id: str) -> List[Symptom]:
        """Get all symptoms for all pets owned by a user"""
        from app.models.pet import Pet
        result = await self.db.execute(
            select(Symptom)
            .join(Pet, Symptom.pet_id == Pet.id)
            .where(Pet.user_id == user_id)
            .order_by(Symptom.observed_at.desc())
        )
        return result.scalars().all()
    
    async def update_symptom(self, symptom_id: str, symptom_data: SymptomUpdate) -> Optional[Symptom]:
        """Update symptom information"""
        symptom = await self.get_symptom_by_id(symptom_id)
        if not symptom:
            return None
        
        update_data = symptom_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(symptom, field, value)
        
        await self.db.commit()
        await self.db.refresh(symptom)
        return symptom
    
    async def delete_symptom(self, symptom_id: str) -> bool:
        """Delete a symptom record"""
        symptom = await self.get_symptom_by_id(symptom_id)
        if not symptom:
            return False
        
        await self.db.delete(symptom)
        await self.db.commit()
        return True
    
    # Assessment operations
    async def create_assessment(self, assessment_data: SymptomAssessmentCreate) -> SymptomAssessmentSchema:
        """Create a new symptom assessment with AI analysis based on existing symptoms"""
        start_time = time.time()
        
        # Get existing symptoms for the pet
        existing_symptoms = await self.get_symptoms_by_pet(assessment_data.pet_id)
        
        if not existing_symptoms:
            raise ValueError("No symptoms found for this pet. Please record symptoms before requesting an assessment.")
        
        # Convert existing symptoms to the format expected by AI analysis
        symptoms_list = []
        for symptom in existing_symptoms:
            symptom_dict = {
                'symptom_name': symptom.symptom_name,
                'severity': symptom.severity,
                'description': symptom.description,
                'observed_at': symptom.observed_at.isoformat(),
                'duration_hours': symptom.duration_hours,
                'pet_id': str(symptom.pet_id)
            }
            symptoms_list.append(symptom_dict)
        
        # Wrap symptoms in a dictionary as expected by schema
        symptoms_json = {
            "symptoms": symptoms_list,
            "assessment_timestamp": datetime.now().isoformat(),
            "pet_id": str(assessment_data.pet_id),
            "total_symptoms_analyzed": len(symptoms_list)
        }
        
        # AI analysis using existing symptoms
        ai_analysis_result = await self._analyze_symptoms_with_ai(
            assessment_data.pet_id, 
            symptoms_list
        )
        
        processing_time = int((time.time() - start_time) * 1000)
        
        # Create the SQLAlchemy model instance
        assessment = SymptomAssessmentModel(
            pet_id=assessment_data.pet_id,
            symptoms_json=symptoms_json,
            ai_analysis=ai_analysis_result["analysis"],
            urgency_level=ai_analysis_result["urgency_level"],
            recommendations=ai_analysis_result["recommendations"],
            possible_causes=ai_analysis_result.get("possible_causes", []),
            ai_provider=f"ollama_{settings.ollama_model}" if "Fallback" not in ai_analysis_result["analysis"] else "fallback_rules",
            processing_time_ms=processing_time
        )
        
        self.db.add(assessment)
        await self.db.commit()
        await self.db.refresh(assessment)
        
        # Access all attributes while session is active to avoid detached instance errors
        assessment_dict = {
            'id': assessment.id,
            'pet_id': assessment.pet_id,
            'symptoms_json': assessment.symptoms_json,
            'ai_analysis': assessment.ai_analysis,
            'urgency_level': assessment.urgency_level,
            'recommendations': assessment.recommendations,
            'possible_causes': assessment.possible_causes,
            'ai_provider': assessment.ai_provider,
            'processing_time_ms': assessment.processing_time_ms,
            'created_at': assessment.created_at,
            'medical_disclaimer': ai_analysis_result.get("medical_disclaimer", 
                "This assessment is for educational purposes only and is not professional veterinary advice. Please consult a licensed veterinarian for proper diagnosis and treatment.")
        }

        # Convert to Pydantic schema for response using dict
        return SymptomAssessmentSchema(**assessment_dict)
    
    async def get_assessment_by_id(self, assessment_id: str) -> Optional[SymptomAssessmentModel]:
        """Get assessment by ID"""
        result = await self.db.execute(
            select(SymptomAssessmentModel).where(SymptomAssessmentModel.id == assessment_id)
        )
        return result.scalar_one_or_none()
    
    async def get_assessments_by_pet(self, pet_id: str) -> List[SymptomAssessmentModel]:
        """Get all assessments for a specific pet"""
        result = await self.db.execute(
            select(SymptomAssessmentModel)
            .where(SymptomAssessmentModel.pet_id == pet_id)
            .order_by(SymptomAssessmentModel.created_at.desc())
        )
        return result.scalars().all()
    
    async def get_assessments_by_user(self, user_id: str) -> List[SymptomAssessmentModel]:
        """Get all assessments for all pets owned by a user"""
        from app.models.pet import Pet
        result = await self.db.execute(
            select(SymptomAssessmentModel)
            .join(Pet, SymptomAssessmentModel.pet_id == Pet.id)
            .where(Pet.user_id == user_id)
            .order_by(SymptomAssessmentModel.created_at.desc())
        )
        return result.scalars().all()
    
    async def _analyze_symptoms_with_ai(self, pet_id: str, symptoms: List[Dict]) -> Dict[str, Any]:
        """
        AI analysis of symptoms using local Ollama LLM
        """
        try:
            # Get pet information for context
            pet_info = await self._get_pet_context(pet_id)
            
            # Create structured prompt
            prompt = self._create_veterinary_prompt(pet_info, symptoms)
            
            # Call Ollama API
            ai_response = await self._call_ollama_api(prompt)
            
            # Parse and validate response
            parsed_response = self._parse_ai_response(ai_response)
            
            return parsed_response
            
        except Exception as e:
            # Fallback to rule-based analysis if AI fails
            print(f"AI analysis failed, using fallback: {str(e)}")
            return await self._fallback_analysis(symptoms)
    
    def _generate_analysis(self, symptoms: List[Dict], urgency: str, severity: float) -> str:
        """Generate mock AI analysis text"""
        symptom_count = len(symptoms)
        symptom_names = [s.get('symptom_name', '') for s in symptoms]
        
        analysis = f"Based on the analysis of {symptom_count} reported symptom(s): {', '.join(symptom_names[:3])}{'...' if len(symptom_names) > 3 else ''}. "
        
        if urgency == 'emergency':
            analysis += "This appears to be an emergency situation requiring immediate veterinary attention. "
        elif urgency == 'high':
            analysis += "These symptoms indicate a condition that should be evaluated by a veterinarian within 24 hours. "
        elif urgency == 'medium':
            analysis += "These symptoms suggest a condition that should be monitored and may require veterinary consultation. "
        else:
            analysis += "These symptoms appear to be mild and may resolve with monitoring and basic care. "
        
        analysis += f"Average severity assessment: {severity:.1f}/3.0. "
        
        return analysis
    
    def _generate_recommendations(self, urgency: str, symptoms: List[Dict]) -> str:
        """Generate mock recommendations based on urgency and symptoms"""
        recommendations = []
        
        if urgency == 'emergency':
            recommendations = [
                "Seek immediate emergency veterinary care",
                "Do not wait - contact the nearest emergency vet clinic",
                "Keep pet calm and comfortable during transport",
                "Bring any relevant medical history"
            ]
        elif urgency == 'high':
            recommendations = [
                "Schedule veterinary appointment within 24 hours",
                "Monitor symptoms closely for any worsening",
                "Keep detailed log of symptom progression",
                "Ensure pet has access to fresh water",
                "Consider temporary dietary restrictions if gastrointestinal symptoms present"
            ]
        elif urgency in ['moderate', 'medium']:  # Handle both for backward compatibility
            recommendations = [
                "Monitor symptoms for 24-48 hours",
                "Schedule routine veterinary appointment if symptoms persist",
                "Ensure pet is comfortable and well-hydrated",
                "Take note of any changes in behavior or appetite",
                "Consider contacting vet if condition worsens"
            ]
        else:
            recommendations = [
                "Continue monitoring pet's condition",
                "Maintain regular feeding and exercise routine",
                "Note any changes in symptoms",
                "Contact veterinarian if symptoms persist beyond 2-3 days",
                "Ensure pet is getting adequate rest"
            ]
        
        return "; ".join(recommendations)
    
    async def _get_pet_context(self, pet_id: str) -> Dict[str, Any]:
        """Get pet information for AI context"""
        from app.models.pet import Pet
        result = await self.db.execute(
            select(Pet).where(Pet.id == pet_id)
        )
        pet = result.scalar_one_or_none()
        
        if not pet:
            return {
                "species": "unknown",
                "breed": "unknown", 
                "age": "unknown",
                "weight": "unknown"
            }
        
        return {
            "species": pet.species,
            "breed": pet.breed or "mixed",
            "age": f"{pet.age_years} years" if pet.age_years else "unknown",
            "weight": f"{pet.weight_kg} kg" if pet.weight_kg else "unknown"
        }
    
    def _create_veterinary_prompt(self, pet_info: Dict, symptoms: List[Dict]) -> str:
        """Create structured prompt for veterinary AI analysis"""
        symptoms_text = []
        for symptom in symptoms:
            symptom_desc = f"- {symptom.get('symptom_name', 'Unknown symptom')}"
            if symptom.get('severity'):
                symptom_desc += f" (severity: {symptom.get('severity')})"
            if symptom.get('description'):
                symptom_desc += f" - {symptom.get('description')}"
            symptoms_text.append(symptom_desc)
        
        prompt = f"""You are Dr. VetAI, a professional veterinary consultation assistant with extensive experience in animal health. Analyze the following case and provide a structured assessment.

PET INFORMATION:
- Species: {pet_info.get('species', 'unknown')}
- Breed: {pet_info.get('breed', 'unknown')}
- Age: {pet_info.get('age', 'unknown')}
- Weight: {pet_info.get('weight', 'unknown')}

REPORTED SYMPTOMS:
{chr(10).join(symptoms_text)}

IMPORTANT GUIDELINES:
- Always emphasize that this is preliminary guidance, not a diagnosis
- Recommend professional veterinary care for concerning symptoms
- Focus on urgency assessment and immediate care steps
- Be conservative in recommendations - when in doubt, recommend vet visit
- MANDATORY: Include medical disclaimer in all responses

Please provide a JSON response with exactly these fields:
{{
  "urgency_level": "emergency|high|medium|low",
  "analysis": "detailed analysis of symptoms and possible causes",
  "recommendations": "specific care recommendations and when to seek professional help",
  "possible_causes": ["list", "of", "possible", "causes"],
  "medical_disclaimer": "This assessment is for educational purposes only and is not professional veterinary advice. Please consult a licensed veterinarian for proper diagnosis and treatment."
}}

Respond only with the JSON object, no other text."""

        return prompt
    
    async def _call_ollama_api(self, prompt: str) -> str:
        """Call local Ollama API"""
        ollama_url = f"{settings.ollama_base_url}/api/generate"
        
        payload = {
            "model": settings.ollama_model,  # Configurable: llama3.2:1b or llama3.2:3b
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,  # Lower temperature for more consistent medical advice
                "top_p": 0.9,
                "num_predict": 500   # Limit response length
            }
        }
        
        async with aiohttp.ClientSession() as session:
            # Set timeout to 60 seconds for AI model processing
            timeout = aiohttp.ClientTimeout(total=60)
            async with session.post(ollama_url, json=payload, timeout=timeout) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get("response", "")
                else:
                    raise Exception(f"Ollama API error: {response.status}")
    
    def _parse_ai_response(self, ai_response: str) -> Dict[str, Any]:
        """Parse and validate AI response"""
        try:
            # Try to extract JSON from response
            ai_response = ai_response.strip()
            if ai_response.startswith("```json"):
                ai_response = ai_response[7:]
            if ai_response.endswith("```"):
                ai_response = ai_response[:-3]
            
            parsed = json.loads(ai_response.strip())
            
            # Validate required fields
            required_fields = ["urgency_level", "analysis", "recommendations"]
            for field in required_fields:
                if field not in parsed:
                    raise ValueError(f"Missing required field: {field}")
            
            # Add medical disclaimer if not present
            if "medical_disclaimer" not in parsed or not parsed["medical_disclaimer"]:
                parsed["medical_disclaimer"] = "This assessment is for educational purposes only and is not professional veterinary advice. Please consult a licensed veterinarian for proper diagnosis and treatment."
            
            # Add possible_causes if not present
            if "possible_causes" not in parsed or not parsed["possible_causes"]:
                parsed["possible_causes"] = ["general health concerns", "environmental factors", "age-related conditions"]
            
            # Ensure recommendations is a string (convert list to string if needed)
            if isinstance(parsed.get("recommendations"), list):
                parsed["recommendations"] = "; ".join(parsed["recommendations"])
            
            # Ensure analysis is a string
            if isinstance(parsed.get("analysis"), list):
                parsed["analysis"] = " ".join(parsed["analysis"])
            
            # Validate urgency level and normalize to standard values
            valid_urgency_map = {
                "emergency": "emergency",
                "high": "high", 
                "medium": "moderate",  # Map AI's "medium" to our standard "moderate"
                "moderate": "moderate",
                "low": "low"
            }
            
            urgency_level = parsed.get("urgency_level", "moderate").lower()
            parsed["urgency_level"] = valid_urgency_map.get(urgency_level, "moderate")  # Default to moderate if invalid
            
            return parsed
            
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Failed to parse AI response: {e}")
            # Return structured response from raw text
            return {
                "urgency_level": "medium",
                "analysis": f"AI Analysis: {ai_response[:200]}..." if len(ai_response) > 200 else ai_response,
                "recommendations": "Please monitor your pet and consult with a veterinarian if symptoms persist or worsen.",
                "possible_causes": ["general health concerns", "environmental factors"],
                "medical_disclaimer": "This assessment is for educational purposes only and is not professional veterinary advice. Please consult a licensed veterinarian for proper diagnosis and treatment."
            }
    
    async def _fallback_analysis(self, symptoms: List[Dict]) -> Dict[str, Any]:
        """Fallback rule-based analysis when AI is unavailable"""
        # Simple rule-based analysis (original mock logic)
        urgency_keywords = {
            'emergency': ['bleeding', 'unconscious', 'seizure', 'difficulty breathing', 'choking'],
            'high': ['vomiting', 'diarrhea', 'fever', 'pain', 'limping severely'],
            'moderate': ['lethargy', 'loss of appetite', 'coughing', 'sneezing'],
            'low': ['minor scratching', 'slight behavior change']
        }
        
        urgency_level = 'low'
        severity_scores = []
        
        for symptom in symptoms:
            symptom_name = symptom.get('symptom_name', '').lower()
            severity = symptom.get('severity', 'mild')
            
            # Check for emergency keywords
            for level, keywords in urgency_keywords.items():
                if any(keyword in symptom_name for keyword in keywords):
                    if level == 'emergency':
                        urgency_level = 'emergency'
                        break
                    elif level == 'high' and urgency_level not in ['emergency']:
                        urgency_level = 'high'
                    elif level == 'moderate' and urgency_level not in ['emergency', 'high']:
                        urgency_level = 'moderate'
            
            # Factor in severity
            severity_score = {'mild': 1, 'moderate': 2, 'severe': 3}.get(severity, 1)
            severity_scores.append(severity_score)
        
        # Adjust urgency based on severity
        avg_severity = sum(severity_scores) / len(severity_scores) if severity_scores else 1
        if avg_severity >= 2.5 and urgency_level == 'low':
            urgency_level = 'moderate'
        elif avg_severity >= 3 and urgency_level in ['low', 'moderate']:
            urgency_level = 'high'
        
        # Generate analysis and recommendations
        analysis = self._generate_analysis(symptoms, urgency_level, avg_severity)
        recommendations = self._generate_recommendations(urgency_level, symptoms)
        
        # Add medical disclaimer
        disclaimer = "IMPORTANT: This is not professional veterinary advice. This analysis is for educational purposes only. Please consult a licensed veterinarian for proper medical evaluation and diagnosis."
        analysis_with_disclaimer = f"{analysis} {disclaimer}"
        
        # Generate possible causes based on symptoms
        possible_causes = self._generate_possible_causes(symptoms)
        
        return {
            "analysis": f"Fallback Analysis: {analysis_with_disclaimer}",
            "urgency_level": urgency_level,
            "recommendations": recommendations,
            "possible_causes": possible_causes,
            "medical_disclaimer": "This assessment is for educational purposes only and is not professional veterinary advice. Please consult a licensed veterinarian for proper diagnosis and treatment."
        }

    def _generate_possible_causes(self, symptoms: List[Dict]) -> List[str]:
        """Generate possible causes based on symptoms"""
        causes = []
        symptom_names = [s.get('symptom_name', '').lower() for s in symptoms]
        
        # Map symptoms to possible causes
        cause_mapping = {
            'vomiting': ['dietary indiscretion', 'gastrointestinal upset', 'stress', 'food sensitivity'],
            'diarrhea': ['dietary change', 'food intolerance', 'stress', 'gastrointestinal infection'],
            'lethargy': ['mild illness', 'overexertion', 'weather changes', 'routine changes'],
            'loss of appetite': ['stress', 'minor illness', 'food preferences', 'environmental changes'],
            'not eating': ['stress', 'minor illness', 'food preferences', 'environmental changes'],
            'coughing': ['mild respiratory irritation', 'environmental allergens', 'dry air'],
            'sneezing': ['environmental allergens', 'dust', 'mild respiratory irritation']
        }
        
        # Add causes based on symptoms
        for symptom in symptom_names:
            for key, possible_causes_list in cause_mapping.items():
                if key in symptom:
                    causes.extend(possible_causes_list)
        
        # Remove duplicates and return unique causes
        unique_causes = list(set(causes))
        
        # If no specific causes found, provide general ones
        if not unique_causes:
            unique_causes = ['minor illness', 'environmental factors', 'stress', 'routine changes']
        
        return unique_causes[:4]  # Limit to 4 causes