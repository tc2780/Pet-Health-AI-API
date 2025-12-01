"""
Main API v1 router
"""
from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, pets, symptoms

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(pets.router, prefix="/pets", tags=["pets"])
api_router.include_router(symptoms.router, prefix="/symptoms", tags=["symptoms"])