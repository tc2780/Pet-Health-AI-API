"""
Tests for authentication API endpoints integration
"""
import pytest
from httpx import AsyncClient


class TestAuthAPIIntegration:
    """Test authentication API endpoint integration with database and security"""
    
    async def test_register_login_flow_integration(self, client: AsyncClient, sample_user_data):
        """Test the complete register-login flow integration"""
        # Register user
        response = await client.post("/api/v1/auth/register", json=sample_user_data)
        assert response.status_code == 200
        
        # Login with registered user
        login_data = {
            "username": sample_user_data["email"],
            "password": sample_user_data["password"]
        }
        response = await client.post(
            "/api/v1/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    async def test_duplicate_user_database_constraint(self, client: AsyncClient, sample_user_data):
        """Test that database constraints prevent duplicate registrations"""
        # Register first user
        response1 = await client.post("/api/v1/auth/register", json=sample_user_data)
        assert response1.status_code == 200
        
        # Try to register with same email - should hit database constraint
        response2 = await client.post("/api/v1/auth/register", json=sample_user_data)
        assert response2.status_code == 400
    
    async def test_authentication_middleware_integration(self, client: AsyncClient):
        """Test that authentication middleware properly integrates with endpoints"""
        # Test unauthorized access
        response = await client.get("/api/v1/pets/")
        assert response.status_code == 401
        
        # Test with invalid token
        headers = {"Authorization": "Bearer invalid_token"}
        response = await client.get("/api/v1/pets/", headers=headers)
        assert response.status_code == 401
    
    async def test_token_validation_across_services(self, client: AsyncClient, authenticated_user):
        """Test that valid tokens work across different API services"""
        headers = authenticated_user["headers"]
        
        # Test multiple endpoints with same token
        endpoints = ["/api/v1/pets/", "/api/v1/users/me"]
        
        for endpoint in endpoints:
            response = await client.get(endpoint, headers=headers)
            assert response.status_code == 200