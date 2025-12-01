"""
User schemas for request/response validation
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict


# Base user schema
class UserBase(BaseModel):
    email: EmailStr
    username: Optional[str] = None


# User creation schema
class UserCreate(UserBase):
    password: str


# User update schema
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: Optional[str] = None


# User response schema
class User(UserBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime


# User with pets schema
class UserWithPets(User):
    pets: list["Pet"] = []


# Login schemas
class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    email: Optional[str] = None