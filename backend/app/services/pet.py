"""
Pet service for database operations
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.pet import Pet
from app.schemas.pet import PetCreate, PetUpdate


class PetService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_pet_by_id(self, pet_id: str) -> Optional[Pet]:
        """Get pet by ID"""
        result = await self.db.execute(select(Pet).where(Pet.id == pet_id))
        return result.scalar_one_or_none()
    
    async def get_pet_with_symptoms(self, pet_id: str) -> Optional[Pet]:
        """Get pet with its symptoms and assessments"""
        result = await self.db.execute(
            select(Pet)
            .options(
                selectinload(Pet.symptoms),
                selectinload(Pet.assessments)
            )
            .where(Pet.id == pet_id)
        )
        return result.scalar_one_or_none()
    
    async def get_user_pets(self, user_id: str) -> List[Pet]:
        """Get all pets for a user"""
        result = await self.db.execute(select(Pet).where(Pet.user_id == user_id))
        return list(result.scalars().all())
    
    async def create_pet(self, user_id: str, pet_data: PetCreate) -> Pet:
        """Create a new pet"""
        pet = Pet(
            user_id=user_id,
            name=pet_data.name,
            species=pet_data.species,
            breed=pet_data.breed,
            age_years=pet_data.age_years,
            weight_kg=pet_data.weight_kg,
            sex=pet_data.sex,
            neutered=pet_data.neutered
        )
        
        self.db.add(pet)
        await self.db.commit()
        await self.db.refresh(pet)
        return pet
    
    async def update_pet(self, pet_id: str, pet_data: PetUpdate) -> Optional[Pet]:
        """Update pet information"""
        pet = await self.get_pet_by_id(pet_id)
        if not pet:
            return None
        
        update_data = pet_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(pet, field, value)
        
        await self.db.commit()
        await self.db.refresh(pet)
        return pet
    
    async def delete_pet(self, pet_id: str) -> bool:
        """Delete a pet"""
        pet = await self.get_pet_by_id(pet_id)
        if not pet:
            return False
        
        await self.db.delete(pet)
        await self.db.commit()
        return True