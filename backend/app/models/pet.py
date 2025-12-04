"""
Pet model for storing pet information
"""
from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base, uuid_column, uuid_foreign_key_column


class Pet(Base):
    __tablename__ = "pets"
    
    id = uuid_column()
    user_id = uuid_foreign_key_column("users.id")
    name = Column(String(100), nullable=False)
    species = Column(String(50), nullable=False)
    breed = Column(String(100))
    age_years = Column(Integer)
    weight_kg = Column(Numeric(5, 2))
    sex = Column(String(20))  # 'male', 'female', 'unknown'
    neutered = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    owner = relationship("User", back_populates="pets")
    symptoms = relationship("Symptom", back_populates="pet", cascade="all, delete-orphan")
    assessments = relationship("SymptomAssessment", back_populates="pet", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Pet(id='{self.id}', name='{self.name}', species='{self.species}')>"