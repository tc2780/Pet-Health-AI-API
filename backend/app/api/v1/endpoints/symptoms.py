"""
Symptom tracking and AI analysis endpoints
"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.schemas.symptom import (
    Symptom, SymptomCreate, SymptomUpdate, 
    SymptomAssessment, SymptomAssessmentCreate
)
from app.schemas.user import User
from app.services.auth import get_current_user_from_token
from app.services.symptom import SymptomService
from app.services.pet import PetService
from app.api.v1.endpoints.auth import oauth2_scheme

router = APIRouter()


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db_session)
) -> User:
    """Get the current authenticated user"""
    return await get_current_user_from_token(token, db)


# Symptom CRUD endpoints
@router.post("/", response_model=Symptom)
async def create_symptom(
    symptom_data: SymptomCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Create a new symptom record for a pet
    """
    # Verify pet ownership
    pet_service = PetService(db)
    pet = await pet_service.get_pet_by_id(symptom_data.pet_id)
    
    if not pet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pet not found"
        )
    
    if pet.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to add symptoms for this pet"
        )
    
    symptom_service = SymptomService(db)
    return await symptom_service.create_symptom(symptom_data)


@router.get("/pet/{pet_id}", response_model=List[Symptom])
async def get_pet_symptoms(
    pet_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get all symptoms for a specific pet
    """
    # Verify pet ownership
    pet_service = PetService(db)
    pet = await pet_service.get_pet_by_id(pet_id)
    
    if not pet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pet not found"
        )
    
    if pet.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view symptoms for this pet"
        )
    
    symptom_service = SymptomService(db)
    return await symptom_service.get_symptoms_by_pet(pet_id)


@router.get("/my-pets", response_model=List[Symptom])
async def get_user_symptoms(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get all symptoms for all pets owned by the current user
    """
    symptom_service = SymptomService(db)
    return await symptom_service.get_symptoms_by_user(current_user.id)


@router.get("/{symptom_id}", response_model=Symptom)
async def get_symptom(
    symptom_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get a specific symptom by ID
    """
    symptom_service = SymptomService(db)
    symptom = await symptom_service.get_symptom_by_id(symptom_id)
    
    if not symptom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Symptom not found"
        )
    
    # Verify pet ownership
    pet_service = PetService(db)
    pet = await pet_service.get_pet_by_id(symptom.pet_id)
    
    if not pet or pet.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this symptom"
        )
    
    return symptom


@router.put("/{symptom_id}", response_model=Symptom)
async def update_symptom(
    symptom_id: str,
    symptom_data: SymptomUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Update a symptom record
    """
    symptom_service = SymptomService(db)
    symptom = await symptom_service.get_symptom_by_id(symptom_id)
    
    if not symptom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Symptom not found"
        )
    
    # Verify pet ownership
    pet_service = PetService(db)
    pet = await pet_service.get_pet_by_id(symptom.pet_id)
    
    if not pet or pet.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this symptom"
        )
    
    updated_symptom = await symptom_service.update_symptom(symptom_id, symptom_data)
    return updated_symptom


@router.delete("/{symptom_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_symptom(
    symptom_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Delete a symptom record
    """
    symptom_service = SymptomService(db)
    symptom = await symptom_service.get_symptom_by_id(symptom_id)
    
    if not symptom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Symptom not found"
        )
    
    # Verify pet ownership
    pet_service = PetService(db)
    pet = await pet_service.get_pet_by_id(symptom.pet_id)
    
    if not pet or pet.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this symptom"
        )
    
    await symptom_service.delete_symptom(symptom_id)


# AI Assessment endpoints
@router.post("/assess", response_model=SymptomAssessment)
async def create_symptom_assessment(
    assessment_data: SymptomAssessmentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Create a new symptom assessment with AI analysis
    """
    # Verify pet ownership
    pet_service = PetService(db)
    pet = await pet_service.get_pet_by_id(assessment_data.pet_id)
    
    if not pet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pet not found"
        )
    
    if pet.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create assessment for this pet"
        )
    
    symptom_service = SymptomService(db)
    return await symptom_service.create_assessment(assessment_data)


@router.get("/assessments/pet/{pet_id}", response_model=List[SymptomAssessment])
async def get_pet_assessments(
    pet_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get all AI assessments for a specific pet
    """
    # Verify pet ownership
    pet_service = PetService(db)
    pet = await pet_service.get_pet_by_id(pet_id)
    
    if not pet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pet not found"
        )
    
    if pet.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view assessments for this pet"
        )
    
    symptom_service = SymptomService(db)
    return await symptom_service.get_assessments_by_pet(pet_id)


@router.get("/assessments/my-pets", response_model=List[SymptomAssessment])
async def get_user_assessments(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get all AI assessments for all pets owned by the current user
    """
    symptom_service = SymptomService(db)
    return await symptom_service.get_assessments_by_user(current_user.id)


@router.get("/assessments/{assessment_id}", response_model=SymptomAssessment)
async def get_assessment(
    assessment_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get a specific AI assessment by ID
    """
    symptom_service = SymptomService(db)
    assessment = await symptom_service.get_assessment_by_id(assessment_id)
    
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found"
        )
    
    # Verify pet ownership
    pet_service = PetService(db)
    pet = await pet_service.get_pet_by_id(assessment.pet_id)
    
    if not pet or pet.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this assessment"
        )
    
    return assessment