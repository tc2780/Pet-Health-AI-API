"""
Symptom schemas for request/response validation
"""
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict


# Base symptom schema
class SymptomBase(BaseModel):
    symptom_name: str
    severity: str  # 'mild', 'moderate', 'severe'
    description: Optional[str] = None
    observed_at: datetime
    duration_hours: Optional[int] = None


# Symptom creation schema
class SymptomCreate(SymptomBase):
    pet_id: UUID


# Symptom update schema
class SymptomUpdate(BaseModel):
    symptom_name: Optional[str] = None
    severity: Optional[str] = None
    description: Optional[str] = None
    observed_at: Optional[datetime] = None
    duration_hours: Optional[int] = None


# Symptom response schema
class Symptom(SymptomBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    pet_id: UUID
    created_at: datetime


# Symptom assessment schemas
class SymptomAssessmentBase(BaseModel):
    symptoms_json: Dict[str, Any]
    ai_analysis: Optional[str] = None
    urgency_level: str  # 'low', 'medium', 'high', 'emergency'
    recommendations: Optional[str] = None
    possible_causes: Optional[list[str]] = None


class SymptomAssessmentCreate(BaseModel):
    pet_id: UUID
    symptoms: list[SymptomCreate]


class SymptomAssessment(SymptomAssessmentBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    pet_id: UUID
    ai_provider: Optional[str] = None
    processing_time_ms: Optional[int] = None
    created_at: datetime
    medical_disclaimer: Optional[str] = None


# AI Analysis Request/Response
class AIAnalysisRequest(BaseModel):
    pet_info: Dict[str, Any]
    symptoms: list[Dict[str, Any]]


class AIAnalysisResponse(BaseModel):
    urgency_level: str
    analysis: str
    recommendations: list[str]
    confidence_score: Optional[float] = None
    processing_time_ms: int