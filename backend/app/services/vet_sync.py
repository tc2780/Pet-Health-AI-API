"""
Mock Vet Clinic sync service

This service provides a best-effort mock implementation for syncing pet data
with external veterinary clinic systems. Replace the mock implementations with
real HTTP client logic when integrating with partner APIs.
"""
from datetime import datetime
from typing import Any, Dict, List
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.pet import PetService
from app.services.user import UserService


class VetSyncService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.pet_service = PetService(db)
        self.user_service = UserService(db)

    async def sync_pet(self, pet_id: str) -> Dict[str, Any]:
        """Mock-sync a single pet's data to a vet clinic.

        Returns a dict with status and metadata that mirrors what a real
        integration might return.
        """
        pet = await self.pet_service.get_pet_with_symptoms(pet_id)
        if not pet:
            return {"success": False, "reason": "pet_not_found"}

        # Mock payload that would be sent to external API
        payload = {
            "pet_id": str(pet.id),
            "name": pet.name,
            "species": pet.species,
            "age_years": pet.age_years,
            "symptoms_count": len(getattr(pet, "symptoms", [])),
        }

        # Simulate an external sync result
        result = {
            "success": True,
            "clinic_id": "mock-clinic-001",
            "synced_at": datetime.utcnow().isoformat() + "Z",
            "payload_summary": payload,
        }

        return result

    async def sync_all_user_pets(self, user_id: str) -> List[Dict[str, Any]]:
        """Mock-sync all pets belonging to a user and return list of results."""
        pets = await self.pet_service.get_user_pets(user_id)
        results = []
        for p in pets:
            res = {
                "pet_id": str(p.id),
                "synced": True,
                "synced_at": datetime.utcnow().isoformat() + "Z",
            }
            results.append(res)

        return results

    async def export_user_data(self, user_id: str) -> Dict[str, Any]:
        """
        Export all user data including user profile, pets, symptoms, and assessments.
        
        This provides a comprehensive data export for compliance with data portability
        requirements and user data access rights.
        """
        # Get user profile
        user = await self.user_service.get_user_by_id(user_id)
        if not user:
            raise ValueError("User not found")
            
        user_profile = {
            "id": str(user.id),
            "username": user.username,
            "email": user.email,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "is_active": user.is_active,
            "is_verified": getattr(user, 'is_verified', None)
        }
        
        # Get all user's pets with symptoms and assessments
        pets = await self.pet_service.get_user_pets(user_id)
        pets_data = []
        all_symptoms = []
        all_assessments = []
        
        for pet in pets:
            # Get pet with symptoms and assessments for comprehensive export
            pet_with_data = await self.pet_service.get_pet_with_symptoms(str(pet.id))
            
            pet_data = {
                "id": str(pet.id),
                "name": pet.name,
                "species": pet.species,
                "breed": pet.breed,
                "age_years": pet.age_years,
                "weight_kg": float(pet.weight_kg) if pet.weight_kg else None,
                "sex": pet.sex,
                "is_neutered": pet.neutered,
                "created_at": pet.created_at.isoformat() if pet.created_at else None,
                "symptoms_count": len(getattr(pet_with_data, "symptoms", [])) if pet_with_data else 0,
                "assessments_count": len(getattr(pet_with_data, "assessments", [])) if pet_with_data else 0
            }
            pets_data.append(pet_data)
            
            if pet_with_data:
                # Collect symptoms for this pet
                if hasattr(pet_with_data, "symptoms") and pet_with_data.symptoms:
                    for symptom in pet_with_data.symptoms:
                        symptom_data = {
                            "id": str(symptom.id),
                            "pet_id": str(symptom.pet_id),
                            "symptom_name": symptom.symptom_name,
                            "severity": symptom.severity,
                            "description": symptom.description,
                            "observed_at": symptom.observed_at.isoformat() if symptom.observed_at else None,
                            "duration_hours": symptom.duration_hours,
                            "created_at": symptom.created_at.isoformat() if symptom.created_at else None
                        }
                        all_symptoms.append(symptom_data)
                
                # Collect assessments for this pet
                if hasattr(pet_with_data, "assessments") and pet_with_data.assessments:
                    for assessment in pet_with_data.assessments:
                        # Handle the 'analysis' field which might be stored as 'ai_analysis'
                        analysis_field = getattr(assessment, 'analysis', None) or getattr(assessment, 'ai_analysis', None)
                        
                        assessment_data = {
                            "id": str(assessment.id),
                            "pet_id": str(assessment.pet_id),
                            "urgency_level": assessment.urgency_level,
                            "analysis": analysis_field,
                            "recommendations": assessment.recommendations,
                            "possible_causes": assessment.possible_causes,
                            "symptoms_json": assessment.symptoms_json,
                            "ai_provider": getattr(assessment, 'ai_provider', None),
                            "processing_time_ms": getattr(assessment, 'processing_time_ms', None),
                            "created_at": assessment.created_at.isoformat() if assessment.created_at else None
                        }
                        all_assessments.append(assessment_data)
        
        # Compile complete export
        export_data = {
            "export_timestamp": datetime.utcnow().isoformat() + "Z",
            "user_profile": user_profile,
            "pets": pets_data,
            "symptoms": all_symptoms,
            "assessments": all_assessments,
            "data_summary": {
                "total_pets": len(pets_data),
                "total_symptoms": len(all_symptoms),
                "total_assessments": len(all_assessments)
            }
        }
        
        return export_data
