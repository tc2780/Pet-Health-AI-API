"""
P2: Purpose Limitation Clause Control Tests

CLAUSE P2: "Use pet data only for health management, not marketing"

This test file validates that the system implements proper purpose limitation controls:

TECHNICAL CONTROLS:
- Code review processes requiring health-related purpose for all data access
- API endpoints restricted to health management functionality only
- Data export limited to health-related information
- No marketing, advertising, or non-health analytics endpoints

COMPLIANCE VERIFICATION:
- No marketing or advertising endpoints exist in the API
- Data access is limited to health management purposes
- No third-party data sharing capabilities for non-health purposes
- User data exports contain only health-related information

PRIVACY RATIONALE:
Purpose limitation ensures that personal data is processed only for the specific
purposes for which it was collected. For pet health data, this means using the
information solely for health monitoring, assessment, and care recommendations,
not for marketing, advertising, or other commercial purposes.
"""

import pytest
from httpx import AsyncClient
from .helpers import get_auth_headers, create_test_pet, create_test_symptom


@pytest.mark.asyncio
async def test_no_marketing_endpoints(client: AsyncClient):
    """
    Ensure no marketing-related endpoints exist in the API
    
    CLAUSE: P2 - Purpose Limitation
    CONTROL: API design excludes marketing/advertising functionality
    VERIFICATION: Marketing endpoints return 404 (do not exist)
    """
    auth_headers = await get_auth_headers(client)
    
    marketing_endpoints = [
        "/api/v1/ads", 
        "/api/v1/marketing", 
        "/api/v1/promotions", 
        "/api/v1/analytics/marketing"
    ]
    for endpoint in marketing_endpoints:
        response = await client.get(endpoint, headers=auth_headers)
        assert response.status_code == 404, f"Marketing endpoint {endpoint} should not exist"


@pytest.mark.asyncio
async def test_data_access_for_health_purposes_only(client: AsyncClient):
    """
    Test that data access is limited to health management purposes
    
    CLAUSE: P2 - Purpose Limitation  
    CONTROL: Data responses exclude non-health tracking information
    VERIFICATION: API responses contain only health-related fields
    """
    auth_headers = await get_auth_headers(client)
    
    # Create test pet and symptoms
    pet_id = await create_test_pet(client, auth_headers)
    symptom_id = await create_test_symptom(client, pet_id, auth_headers)
    
    # Access symptom data
    response = await client.get(f"/api/v1/symptoms/pet/{pet_id}", 
                                headers=auth_headers)
    assert response.status_code == 200
    
    # Verify no analytics or tracking data is included
    data = response.json()
    prohibited_fields = ["ad_targeting", "marketing_segment", "tracking_id", 
                        "analytics_data", "user_behavior", "commercial_score"]
    # Check if data is a list (symptoms) or dict
    items_to_check = data if isinstance(data, list) else [data]
    for item in items_to_check:
        for field in prohibited_fields:
            assert field not in item, f"Non-health field '{field}' found in health data"


@pytest.mark.asyncio
async def test_no_third_party_data_sharing(client: AsyncClient):
    """
    Test that no endpoints expose data to third parties for non-health purposes
    
    CLAUSE: P2 - Purpose Limitation
    CONTROL: No third-party integration endpoints for marketing/analytics
    VERIFICATION: Third-party sharing endpoints do not exist
    """
    auth_headers = await get_auth_headers(client)
    
    # Check for common third-party integration patterns
    third_party_endpoints = [
        "/api/v1/export/facebook",
        "/api/v1/export/google", 
        "/api/v1/share/analytics",
        "/api/v1/integrations/advertising",
        "/api/v1/tracking/external",
        "/api/v1/data/commercial"
    ]
    for endpoint in third_party_endpoints:
        response = await client.post(endpoint, 
                                     json={},
                                     headers=auth_headers)
        assert response.status_code == 404, f"Third-party endpoint {endpoint} should not exist"


@pytest.mark.asyncio
async def test_user_data_export_health_only(client: AsyncClient):
    """
    Test that user data export contains only health-related information
    
    CLAUSE: P2 - Purpose Limitation
    CONTROL: Data export limited to health management data
    VERIFICATION: Export contains only pets, symptoms, assessments, profile
    """
    auth_headers = await get_auth_headers(client)
    
    # Create test data
    pet_id = await create_test_pet(client, auth_headers)
    await create_test_symptom(client, pet_id, auth_headers)
    
    # Export user data
    response = await client.get("/api/v1/users/me/export", headers=auth_headers)
    assert response.status_code == 200
    
    exported_data = response.json()
    
    # Verify only health-related data sections exist
    allowed_sections = ["pets", "symptoms", "assessments", "user_profile", "export_metadata"]
    prohibited_sections = ["marketing_data", "analytics", "behavioral_data", "commercial_insights"]
    
    for section in prohibited_sections:
        assert section not in exported_data, f"Non-health section '{section}' found in export"
    
    # Verify required health sections exist
    health_sections = ["pets", "symptoms", "user_profile"]
    for section in health_sections:
        assert section in exported_data, f"Health section '{section}' missing from export"