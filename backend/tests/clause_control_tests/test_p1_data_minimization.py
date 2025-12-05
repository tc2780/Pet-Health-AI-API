"""
P1: Data Minimization Clause Control Tests

CLAUSE P1: "Collect only data necessary for pet health management"

This test file validates that the system implements proper data minimization controls:

TECHNICAL CONTROLS:
- API validation through Pydantic models that reject unnecessary fields
- Database schema designed to store only essential pet health data
- Optional fields clearly marked with clear benefit explanations

COMPLIANCE VERIFICATION:
- Pet creation requires only minimal necessary data (name, species)
- Unnecessary personal information is rejected or ignored
- Optional fields can be omitted without impact on core functionality
- System doesn't collect non-health-related personal identifiers

PRIVACY RATIONALE:
Data minimization is a core GDPR principle requiring that personal data collection
be limited to what is necessary for the specified purpose. For pet health management,
this means collecting only information directly related to pet care and health monitoring.
"""

import pytest
from httpx import AsyncClient
from .helpers import get_auth_headers


@pytest.mark.asyncio
async def test_pet_creation_data_minimization(client: AsyncClient):
    """
    Test that only necessary fields are required for pet creation
    
    CLAUSE: P1 - Data Minimization
    CONTROL: API requires only essential fields (name, species)
    VERIFICATION: Pet can be created with minimal data
    """
    auth_headers = await get_auth_headers(client)
    
    minimal_pet = {
        "name": "Buddy",
        "species": "dog"
    }
    response = await client.post("/api/v1/pets/", 
                                  json=minimal_pet,
                                  headers=auth_headers)
    assert response.status_code == 200
    pet_data = response.json()
    assert pet_data["name"] == "Buddy"
    assert pet_data["species"] == "dog"


@pytest.mark.asyncio
async def test_excessive_data_rejection(client: AsyncClient):
    """
    Test rejection or ignoring of unnecessary personal data
    
    CLAUSE: P1 - Data Minimization  
    CONTROL: API ignores non-essential personal identifiers
    VERIFICATION: Unnecessary fields like SSN, income are not stored
    """
    auth_headers = await get_auth_headers(client)
    
    pet_with_pii = {
        "name": "Buddy", 
        "species": "dog",
        "owner_ssn": "123-45-6789",  # Should be rejected
        "owner_income": 50000         # Should be rejected
    }
    response = await client.post("/api/v1/pets/", 
                                  json=pet_with_pii,
                                  headers=auth_headers)
    # Should succeed but ignore unnecessary fields
    assert response.status_code == 200
    pet_data = response.json()
    assert "owner_ssn" not in pet_data
    assert "owner_income" not in pet_data


@pytest.mark.asyncio
async def test_optional_fields_clearly_marked(client: AsyncClient):
    """
    Test that optional fields are properly validated and marked
    
    CLAUSE: P1 - Data Minimization
    CONTROL: Optional fields have clear health benefits and can be omitted
    VERIFICATION: Pet creation works with or without optional fields
    """
    auth_headers = await get_auth_headers(client)
    
    # Test with all optional fields omitted
    minimal_pet = {"name": "Max", "species": "cat"}
    response = await client.post("/api/v1/pets/", 
                                  json=minimal_pet,
                                  headers=auth_headers)
    assert response.status_code == 200
    
    # Test with optional fields included
    complete_pet = {
        "name": "Max",
        "species": "cat", 
        "breed": "Persian",      # Optional: enables breed-specific advice
        "age_years": 3,          # Optional: enables age-appropriate care
        "weight_kg": 4.5         # Optional: enables dosage recommendations
    }
    response = await client.post("/api/v1/pets/", 
                                  json=complete_pet,
                                  headers=auth_headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_no_unnecessary_user_data_collection(client: AsyncClient):
    """
    Test that user registration doesn't collect unnecessary personal data
    
    CLAUSE: P1 - Data Minimization
    CONTROL: User accounts require only authentication essentials  
    VERIFICATION: Registration works with minimal required fields
    """
    import uuid
    # Use unique email to avoid conflicts with other tests
    unique_email = f"minimal_{uuid.uuid4().hex[:8]}@example.com"
    
    # Test minimal user registration
    minimal_user = {
        "email": unique_email,
        "password": "SecurePass123!"
    }
    
    response = await client.post("/api/v1/auth/register", json=minimal_user)
    assert response.status_code == 200
    
    user_data = response.json()
    # Should not collect unnecessary personal details
    assert "phone_number" not in user_data
    assert "address" not in user_data 
    assert "full_name" not in user_data
    assert "date_of_birth" not in user_data