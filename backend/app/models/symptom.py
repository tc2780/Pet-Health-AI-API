"""
Symptom models for tracking pet symptoms and AI assessments
"""
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class Symptom(Base):
    __tablename__ = "symptoms"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    pet_id = Column(UUID(as_uuid=True), ForeignKey("pets.id", ondelete="CASCADE"), nullable=False)
    symptom_name = Column(String(100), nullable=False)
    severity = Column(String(20), nullable=False)  # 'mild', 'moderate', 'severe'
    description = Column(Text)
    observed_at = Column(DateTime(timezone=True), nullable=False)
    duration_hours = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    pet = relationship("Pet", back_populates="symptoms")
    
    def __repr__(self):
        return f"<Symptom(id='{self.id}', name='{self.symptom_name}', severity='{self.severity}')>"


class SymptomAssessment(Base):
    __tablename__ = "symptom_assessments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    pet_id = Column(UUID(as_uuid=True), ForeignKey("pets.id", ondelete="CASCADE"), nullable=False)
    symptoms_json = Column(JSONB, nullable=False)  # Store symptom data as JSON
    ai_analysis = Column(Text)
    urgency_level = Column(String(20), nullable=False)  # 'low', 'medium', 'high', 'emergency'
    recommendations = Column(Text)
    ai_provider = Column(String(50))  # Track which AI provider was used
    processing_time_ms = Column(Integer)  # Track response times
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    pet = relationship("Pet", back_populates="assessments")
    
    def __repr__(self):
        return f"<SymptomAssessment(id='{self.id}', urgency='{self.urgency_level}')>"