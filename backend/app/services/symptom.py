"""
Symptom service for database operations and AI analysis
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
import time
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from app.models.symptom import Symptom, SymptomAssessment
from app.schemas.symptom import SymptomCreate, SymptomUpdate, SymptomAssessmentCreate


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
    async def create_assessment(self, assessment_data: SymptomAssessmentCreate) -> SymptomAssessment:
        """Create a new symptom assessment with AI analysis"""
        start_time = time.time()
        
        # Prepare symptoms data for AI analysis
        symptoms_json = [symptom.model_dump() for symptom in assessment_data.symptoms]
        
        # Mock AI analysis (replace with actual AI service call)
        ai_analysis_result = await self._analyze_symptoms_with_ai(
            assessment_data.pet_id, 
            symptoms_json
        )
        
        processing_time = int((time.time() - start_time) * 1000)
        
        assessment = SymptomAssessment(
            pet_id=assessment_data.pet_id,
            symptoms_json=symptoms_json,
            ai_analysis=ai_analysis_result["analysis"],
            urgency_level=ai_analysis_result["urgency_level"],
            recommendations=ai_analysis_result["recommendations"],
            ai_provider="mock_ai_v1",
            processing_time_ms=processing_time
        )
        
        self.db.add(assessment)
        await self.db.commit()
        await self.db.refresh(assessment)
        
        # Also create individual symptom records
        for symptom_data in assessment_data.symptoms:
            await self.create_symptom(symptom_data)
        
        return assessment
    
    async def get_assessment_by_id(self, assessment_id: str) -> Optional[SymptomAssessment]:
        """Get assessment by ID"""
        result = await self.db.execute(
            select(SymptomAssessment).where(SymptomAssessment.id == assessment_id)
        )
        return result.scalar_one_or_none()
    
    async def get_assessments_by_pet(self, pet_id: str) -> List[SymptomAssessment]:
        """Get all assessments for a specific pet"""
        result = await self.db.execute(
            select(SymptomAssessment)
            .where(SymptomAssessment.pet_id == pet_id)
            .order_by(SymptomAssessment.created_at.desc())
        )
        return result.scalars().all()
    
    async def get_assessments_by_user(self, user_id: str) -> List[SymptomAssessment]:
        """Get all assessments for all pets owned by a user"""
        from app.models.pet import Pet
        result = await self.db.execute(
            select(SymptomAssessment)
            .join(Pet, SymptomAssessment.pet_id == Pet.id)
            .where(Pet.user_id == user_id)
            .order_by(SymptomAssessment.created_at.desc())
        )
        return result.scalars().all()
    
    async def _analyze_symptoms_with_ai(self, pet_id: str, symptoms: List[Dict]) -> Dict[str, Any]:
        """
        Mock AI analysis of symptoms
        In production, this would call the actual AI service (Ollama, OpenAI, etc.)
        """
        # Simple rule-based mock analysis
        urgency_keywords = {
            'emergency': ['bleeding', 'unconscious', 'seizure', 'difficulty breathing', 'choking'],
            'high': ['vomiting', 'diarrhea', 'fever', 'pain', 'limping severely'],
            'medium': ['lethargy', 'loss of appetite', 'coughing', 'sneezing'],
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
                    elif level == 'medium' and urgency_level not in ['emergency', 'high']:
                        urgency_level = 'medium'
            
            # Factor in severity
            severity_score = {'mild': 1, 'moderate': 2, 'severe': 3}.get(severity, 1)
            severity_scores.append(severity_score)
        
        # Adjust urgency based on severity
        avg_severity = sum(severity_scores) / len(severity_scores) if severity_scores else 1
        if avg_severity >= 2.5 and urgency_level == 'low':
            urgency_level = 'medium'
        elif avg_severity >= 3 and urgency_level in ['low', 'medium']:
            urgency_level = 'high'
        
        # Generate analysis and recommendations
        analysis = self._generate_analysis(symptoms, urgency_level, avg_severity)
        recommendations = self._generate_recommendations(urgency_level, symptoms)
        
        return {
            "analysis": analysis,
            "urgency_level": urgency_level,
            "recommendations": recommendations
        }
    
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
        elif urgency == 'medium':
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