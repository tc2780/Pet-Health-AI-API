"""
Symptom models for tracking pet symptoms and AI assessments
"""
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base, uuid_column, uuid_foreign_key_column


class Symptom(Base):
    __tablename__ = "symptoms"
    
    id = uuid_column()
    pet_id = uuid_foreign_key_column("pets.id")
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
    
    id = uuid_column()
    pet_id = uuid_foreign_key_column("pets.id")
    symptoms_json = Column(JSON, nullable=False)  # Store symptom data as JSON
    ai_analysis = Column(Text)
    urgency_level = Column(String(20), nullable=False)  # 'low', 'medium', 'high', 'emergency'
    recommendations = Column(Text)
    possible_causes = Column(JSON)  # Store possible causes as JSON array
    ai_provider = Column(String(50))  # Track which AI provider was used
    processing_time_ms = Column(Integer)  # Track response times
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    pet = relationship("Pet", back_populates="assessments")
    
    def __repr__(self):
        return f"<SymptomAssessment(id='{self.id}', urgency='{self.urgency_level}')>"