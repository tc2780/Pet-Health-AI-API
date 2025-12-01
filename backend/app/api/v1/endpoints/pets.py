"""
Pet management endpoints
"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.schemas.pet import Pet, PetCreate, PetUpdate, PetWithSymptoms
from app.schemas.user import User
from app.services.auth import get_current_user_from_token
from app.services.pet import PetService
from app.api.v1.endpoints.auth import oauth2_scheme

router = APIRouter()


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db_session)
) -> User:
    """Get current user from token"""
    return await get_current_user_from_token(token, db)


@router.post("/", response_model=Pet)
async def create_pet(
    pet_data: PetCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Create a new pet for the current user
    """
    pet_service = PetService(db)
    pet = await pet_service.create_pet(current_user.id, pet_data)
    return pet


@router.get("/", response_model=List[Pet])
async def get_user_pets(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get all pets for the current user
    """
    pet_service = PetService(db)
    pets = await pet_service.get_user_pets(current_user.id)
    return pets


@router.get("/{pet_id}", response_model=PetWithSymptoms)
async def get_pet(
    pet_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get a specific pet with its symptoms and assessments
    """
    pet_service = PetService(db)
    pet = await pet_service.get_pet_with_symptoms(pet_id)
    
    if not pet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pet not found"
        )
    
    # Verify ownership
    if pet.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this pet"
        )
    
    return pet


@router.put("/{pet_id}", response_model=Pet)
async def update_pet(
    pet_id: UUID,
    pet_data: PetUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Update a pet's information
    """
    pet_service = PetService(db)
    
    # Verify ownership first
    pet = await pet_service.get_pet_by_id(pet_id)
    if not pet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pet not found"
        )
    
    if pet.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this pet"
        )
    
    updated_pet = await pet_service.update_pet(pet_id, pet_data)
    return updated_pet


@router.delete("/{pet_id}")
async def delete_pet(
    pet_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Delete a pet
    """
    pet_service = PetService(db)
    
    # Verify ownership first
    pet = await pet_service.get_pet_by_id(pet_id)
    if not pet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pet not found"
        )
    
    if pet.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this pet"
        )
    
    success = await pet_service.delete_pet(pet_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete pet"
        )
    
    return {"message": "Pet deleted successfully"}