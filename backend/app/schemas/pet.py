"""
Pet schemas for request/response validation
"""
from __future__ import annotations
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, ConfigDict


# Base pet schema
class PetBase(BaseModel):
    name: str
    species: str
    breed: Optional[str] = None
    age_years: Optional[int] = None
    weight_kg: Optional[Decimal] = None
    sex: Optional[str] = None  # 'male', 'female', 'unknown'
    neutered: Optional[bool] = False


# Pet creation schema
class PetCreate(PetBase):
    pass


# Pet update schema
class PetUpdate(BaseModel):
    name: Optional[str] = None
    species: Optional[str] = None
    breed: Optional[str] = None
    age_years: Optional[int] = None
    weight_kg: Optional[Decimal] = None
    sex: Optional[str] = None
    neutered: Optional[bool] = None


# Pet response schema
class Pet(PetBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime


# Pet with symptoms
class PetWithSymptoms(Pet):
    symptoms: List['Symptom'] = []
    assessments: List['SymptomAssessment'] = []


# Import at the end to resolve circular dependencies
from app.schemas.symptom import Symptom, SymptomAssessment
PetWithSymptoms.model_rebuild()