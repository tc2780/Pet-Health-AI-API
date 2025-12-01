"""
Tests for authentication endpoints
"""
import pytest
from httpx import AsyncClient


class TestAuthEndpoints:
    """Test authentication endpoints"""
    
    async def test_register_user_success(self, client: AsyncClient, sample_user_data):
        """Test successful user registration"""
        response = await client.post("/api/v1/auth/register", json=sample_user_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["email"] == sample_user_data["email"]
        assert data["is_active"] is True
        assert data["is_verified"] is False
        assert "created_at" in data
        assert "updated_at" in data
        # Password should not be in response
        assert "password" not in data
    
    async def test_register_user_duplicate_email(self, client: AsyncClient, sample_user_data):
        """Test registration with duplicate email fails"""
        # Register first user
        response1 = await client.post("/api/v1/auth/register", json=sample_user_data)
        assert response1.status_code == 200
        
        # Try to register with same email
        response2 = await client.post("/api/v1/auth/register", json=sample_user_data)
        assert response2.status_code == 400
        data = response2.json()
        assert "already registered" in data["detail"].lower()
    
    async def test_register_user_invalid_email(self, client: AsyncClient):
        """Test registration with invalid email fails"""
        invalid_user_data = {
            "username": "testuser",
            "email": "invalid-email",
            "password": "testpassword123"
        }
        response = await client.post("/api/v1/auth/register", json=invalid_user_data)
        assert response.status_code == 422  # Validation error
    
    async def test_register_user_missing_fields(self, client: AsyncClient):
        """Test registration with missing required fields fails"""
        incomplete_data = {
            "username": "testuser"
            # Missing email and password
        }
        response = await client.post("/api/v1/auth/register", json=incomplete_data)
        assert response.status_code == 422
    
    async def test_login_success(self, client: AsyncClient, sample_user_data):
        """Test successful user login"""
        # First register a user
        register_response = await client.post("/api/v1/auth/register", json=sample_user_data)
        assert register_response.status_code == 200
        
        # Then login
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
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0
    
    async def test_login_invalid_credentials(self, client: AsyncClient, sample_user_data):
        """Test login with invalid credentials fails"""
        # Register a user first
        await client.post("/api/v1/auth/register", json=sample_user_data)
        
        # Try login with wrong password
        login_data = {
            "username": sample_user_data["email"],
            "password": "wrongpassword"
        }
        response = await client.post(
            "/api/v1/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == 401
        data = response.json()
        assert "incorrect" in data["detail"].lower()
    
    async def test_login_nonexistent_user(self, client: AsyncClient):
        """Test login with nonexistent user fails"""
        login_data = {
            "username": "nonexistent@example.com",
            "password": "somepassword"
        }
        response = await client.post(
            "/api/v1/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == 401
        data = response.json()
        assert "incorrect" in data["detail"].lower()
    
    async def test_login_missing_fields(self, client: AsyncClient):
        """Test login with missing fields fails"""
        login_data = {
            "username": "test@example.com"
            # Missing password
        }
        response = await client.post(
            "/api/v1/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == 422
    
    async def test_protected_endpoint_without_token(self, client: AsyncClient):
        """Test that protected endpoints require authentication"""
        response = await client.get("/api/v1/pets/")
        assert response.status_code == 401
    
    async def test_protected_endpoint_with_invalid_token(self, client: AsyncClient):
        """Test that protected endpoints reject invalid tokens"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = await client.get("/api/v1/pets/", headers=headers)
        assert response.status_code == 401
    
    async def test_protected_endpoint_with_valid_token(self, client: AsyncClient, authenticated_user):
        """Test that protected endpoints work with valid tokens"""
        response = await client.get("/api/v1/pets/", headers=authenticated_user["headers"])
        assert response.status_code == 200
        assert isinstance(response.json(), list)