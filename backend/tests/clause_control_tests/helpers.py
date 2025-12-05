"""
Shared Helper Functions for Clause Control Tests

This module contains common helper functions used across all clause control tests
to avoid duplication and ensure consistency in test setup and execution.
"""

import pytest
from httpx import AsyncClient
from unittest import mock
from datetime import datetime
import json
from uuid import uuid4


async def get_auth_headers(client: AsyncClient, user_email="test@example.com"):
    """Get authentication headers for test user"""
    import uuid
    # Use unique email to avoid conflicts
    unique_email = f"test_{uuid.uuid4().hex[:8]}@example.com" if user_email == "test@example.com" else user_email
    
    # Register user
    register_response = await client.post("/api/v1/auth/register", json={
        "email": unique_email,
        "password": "TestPass123!"
    })
    
    # Login (whether registration succeeded or user already exists)
    login_response = await client.post("/api/v1/auth/login", data={
        "username": unique_email,
        "password": "TestPass123!"
    })
    
    if login_response.status_code != 200:
        raise Exception(f"Login failed: {login_response.status_code} - {login_response.text}")
    
    response_data = login_response.json()
    # Handle different possible token field names
    token = response_data.get("access_token") or response_data.get("token") or response_data.get("access-token")
    
    if not token:
        raise Exception(f"No token found in response: {response_data}")
    
    return {"Authorization": f"Bearer {token}"}


async def create_test_pet(client: AsyncClient, auth_headers=None):
    """Create a test pet and return its ID"""
    if auth_headers is None:
        auth_headers = await get_auth_headers(client)
    
    pet_data = {
        "name": "TestPet",
        "species": "dog",
        "age_years": 5
    }
    
    response = await client.post("/api/v1/pets/", json=pet_data, headers=auth_headers)
    return response.json()["id"]


async def create_test_pet_with_data(client: AsyncClient, pet_data, auth_headers=None):
    """Create a test pet with specific data"""
    if auth_headers is None:
        auth_headers = await get_auth_headers(client)
    
    response = await client.post("/api/v1/pets/", json=pet_data, headers=auth_headers)
    return response.json()["id"]


async def create_user_and_get_headers(client: AsyncClient, email):
    """Create a new user and return auth headers"""
    return await get_auth_headers(client, email)


async def create_test_symptom(client: AsyncClient, pet_id, auth_headers=None):
    """Create a test symptom for a pet and return its ID"""
    if auth_headers is None:
        auth_headers = await get_auth_headers(client)
    
    from datetime import datetime
    # Ensure pet_id is a string (UUID will be handled by API)
    pet_id_str = str(pet_id) if not isinstance(pet_id, str) else pet_id
    
    symptom_data = {
        "pet_id": pet_id_str,
        "symptom_name": "coughing",
        "severity": "mild",
        "observed_at": datetime.now().isoformat(),
        "duration_hours": 48
    }
    
    response = await client.post("/api/v1/symptoms/", json=symptom_data, headers=auth_headers)
    if response.status_code == 200:
        return response.json()["id"]
    return None


def format_symptoms_for_assessment(symptom_list, pet_id):
    """Format symptoms with required fields for assessment endpoint"""
    from datetime import datetime
    formatted = []
    for symptom in symptom_list:
        formatted_symptom = {
            "pet_id": str(pet_id),  # Required for each symptom
            "symptom_name": symptom.get("name", symptom.get("symptom_name", "unknown")),
            "severity": symptom.get("severity", "mild"),
            "observed_at": symptom.get("observed_at", datetime.now().isoformat()),
            "duration_hours": symptom.get("duration_hours", 24)
        }
        formatted.append(formatted_symptom)
    return formatted