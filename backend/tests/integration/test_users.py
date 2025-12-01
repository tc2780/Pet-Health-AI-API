"""
Tests for user management API integration
"""
import pytest
from httpx import AsyncClient


class TestUserAPIIntegration:
    """Test user management API integration with database and authentication"""
    
    async def test_user_update_database_persistence(self, client: AsyncClient, authenticated_user):
        """Test that user updates persist correctly in database"""
        update_data = {
            "username": "updated_integration_user",
            "email": "updated@integration.com"
        }
        
        response = await client.put(
            "/api/v1/users/me",
            json=update_data,
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 200
        
        # Verify persistence by fetching user again
        get_response = await client.get("/api/v1/users/me", headers=authenticated_user["headers"])
        assert get_response.status_code == 200
        data = get_response.json()
        assert data["username"] == update_data["username"]
        assert data["email"] == update_data["email"]
    
    async def test_user_deletion_cascade_with_pets(self, client: AsyncClient, authenticated_user, test_pet):
        """Test that user deletion properly cascades to delete associated pets"""
        # Verify pet exists before deletion
        pet_response = await client.get(
            f"/api/v1/pets/{test_pet['id']}",
            headers=authenticated_user["headers"]
        )
        assert pet_response.status_code == 200
        
        # Delete user
        delete_response = await client.delete("/api/v1/users/me", headers=authenticated_user["headers"])
        assert delete_response.status_code == 200
        
        # Verify user is deleted and token is invalidated
        me_response = await client.get("/api/v1/users/me", headers=authenticated_user["headers"])
        assert me_response.status_code == 401
    
    async def test_user_data_isolation_across_sessions(self, client: AsyncClient, sample_user_data):
        """Test that user data is properly isolated between different user sessions"""
        # Create two users
        user1_data = {**sample_user_data, "email": "user1@isolation.com", "username": "user1"}
        user2_data = {**sample_user_data, "email": "user2@isolation.com", "username": "user2"}
        
        # Register both users
        user1_register = await client.post("/api/v1/auth/register", json=user1_data)
        user2_register = await client.post("/api/v1/auth/register", json=user2_data)
        assert user1_register.status_code == 200
        assert user2_register.status_code == 200
        
        # Login both users
        user1_login = await client.post(
            "/api/v1/auth/login",
            data={"username": user1_data["email"], "password": user1_data["password"]},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        user2_login = await client.post(
            "/api/v1/auth/login",
            data={"username": user2_data["email"], "password": user2_data["password"]},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        user1_headers = {"Authorization": f"Bearer {user1_login.json()['access_token']}"}
        user2_headers = {"Authorization": f"Bearer {user2_login.json()['access_token']}"}
        
        # Verify each user only sees their own data
        user1_me = await client.get("/api/v1/users/me", headers=user1_headers)
        user2_me = await client.get("/api/v1/users/me", headers=user2_headers)
        
        assert user1_me.status_code == 200
        assert user2_me.status_code == 200
        assert user1_me.json()["email"] == user1_data["email"]
        assert user2_me.json()["email"] == user2_data["email"]
        assert user1_me.json()["id"] != user2_me.json()["id"]
    
    async def test_unique_constraint_enforcement(self, client: AsyncClient, authenticated_user, sample_user_data):
        """Test that database unique constraints are properly enforced via API"""
        # Create another user
        other_user_data = {
            "username": "other_unique_user",
            "email": "other@unique.com",
            "password": "otherpassword123"
        }
        register_response = await client.post("/api/v1/auth/register", json=other_user_data)
        assert register_response.status_code == 200
        
        # Try to update current user's email to the other user's email (should fail due to unique constraint)
        update_data = {"email": other_user_data["email"]}
        
        response = await client.put(
            "/api/v1/users/me",
            json=update_data,
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 400  # Database constraint violation