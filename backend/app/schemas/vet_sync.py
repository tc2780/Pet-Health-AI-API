"""
Schemas for vet clinic sync responses
"""
from __future__ import annotations
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class SyncPayloadSummary(BaseModel):
    pet_id: str
    name: Optional[str]
    species: Optional[str]
    age_years: Optional[int]
    symptoms_count: int


class SyncResult(BaseModel):
    success: bool
    clinic_id: Optional[str] = None
    synced_at: Optional[datetime] = None
    payload_summary: Optional[SyncPayloadSummary] = None
    reason: Optional[str] = None


class SyncAllResponse(BaseModel):
    results: List[SyncResult]
