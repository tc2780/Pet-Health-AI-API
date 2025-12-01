"""
Mock Vet Clinic sync service

This service provides a best-effort mock implementation for syncing pet data
with external veterinary clinic systems. Replace the mock implementations with
real HTTP client logic when integrating with partner APIs.
"""
from datetime import datetime
from typing import Any, Dict, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.pet import PetService


class VetSyncService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.pet_service = PetService(db)

    async def sync_pet(self, pet_id: UUID) -> Dict[str, Any]:
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

    async def sync_all_user_pets(self, user_id: UUID) -> List[Dict[str, Any]]:
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
