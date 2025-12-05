"""
Performance test fixtures and utilities
"""

import pytest
import asyncio
import os
from typing import Generator
import httpx

from app.core.database import get_db_session
from app.models.user import User
from app.models.pet import Pet


def get_api_base_url():
    """Get API base URL from environment or default"""
    return os.getenv("API_BASE_URL", "http://localhost:8000")


@pytest.fixture
def performance_client():
    """HTTP client for performance testing"""
    base_url = get_api_base_url()
    client = httpx.Client(base_url=base_url, timeout=30.0)
    yield client
    client.close()


@pytest.fixture  
def async_performance_client():
    """Async HTTP client for performance testing"""
    base_url = get_api_base_url()
    
    async def _client():
        async with httpx.AsyncClient(base_url=base_url, timeout=30.0) as client:
            yield client
    
    return _client


@pytest.fixture
def api_base_url():
    """Get the base URL for API calls"""
    return get_api_base_url()


@pytest.fixture
def performance_user_data():
    """Standard user data for performance tests"""
    return {
        "email": "perftest@example.com",
        "password": "perftest123",
        "full_name": "Performance Test User"
    }


@pytest.fixture
def performance_pet_data():
    """Standard pet data for performance tests"""
    return {
        "name": "Performance Test Pet",
        "species": "dog",
        "breed": "Golden Retriever", 
        "age": 3,
        "weight": 25.5
    }


@pytest.fixture
def performance_symptoms_data():
    """Standard symptoms data for AI performance tests"""
    return {
        "symptoms": ["lethargy", "loss of appetite"],
        "duration": "2 days",
        "severity": "moderate"
    }