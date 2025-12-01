"""
Tests for user management endpoints
"""
import pytest
from httpx import AsyncClient


class TestUserEndpoints:
    """Test user management endpoints"""
    
    async def test_get_current_user(self, client: AsyncClient, authenticated_user):
        """Test getting current user information"""
        response = await client.get("/api/v1/users/me", headers=authenticated_user["headers"])
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == authenticated_user["user"]["id"]
        assert data["email"] == authenticated_user["user"]["email"]
        assert data["is_active"] == authenticated_user["user"]["is_active"]
        # Password should not be included
        assert "password" not in data
    
    async def test_get_current_user_unauthorized(self, client: AsyncClient):
        """Test getting current user without authentication fails"""
        response = await client.get("/api/v1/users/me")
        assert response.status_code == 401
    
    async def test_get_current_user_invalid_token(self, client: AsyncClient):
        """Test getting current user with invalid token fails"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = await client.get("/api/v1/users/me", headers=headers)
        assert response.status_code == 401
    
    async def test_update_current_user(self, client: AsyncClient, authenticated_user):
        """Test updating current user information"""
        update_data = {
            "username": "updateduser",
            "email": "updated@example.com"
        }
        
        response = await client.put(
            "/api/v1/users/me",
            json=update_data,
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == update_data["username"]
        assert data["email"] == update_data["email"]
        assert data["id"] == authenticated_user["user"]["id"]
    
    async def test_update_current_user_partial(self, client: AsyncClient, authenticated_user):
        """Test partial update of current user"""
        update_data = {
            "username": "partiallydated"
            # Only updating username, not email
        }
        
        response = await client.put(
            "/api/v1/users/me",
            json=update_data,
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == update_data["username"]
        # Email should remain unchanged
        assert data["email"] == authenticated_user["user"]["email"]
    
    async def test_update_current_user_invalid_email(self, client: AsyncClient, authenticated_user):
        """Test updating user with invalid email fails"""
        update_data = {
            "email": "invalid-email-format"
        }
        
        response = await client.put(
            "/api/v1/users/me",
            json=update_data,
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 422  # Validation error
    
    async def test_update_current_user_unauthorized(self, client: AsyncClient):
        """Test updating user without authentication fails"""
        update_data = {
            "username": "shouldnotwork"
        }
        
        response = await client.put("/api/v1/users/me", json=update_data)
        assert response.status_code == 401
    
    async def test_update_current_user_duplicate_email(self, client: AsyncClient, authenticated_user, sample_user_data):
        """Test updating user to existing email fails"""
        # Create another user
        other_user_data = {
            "username": "otheruser",
            "email": "other@example.com",
            "password": "otherpassword123"
        }
        register_response = await client.post("/api/v1/auth/register", json=other_user_data)
        assert register_response.status_code == 200
        
        # Try to update current user's email to the other user's email
        update_data = {
            "email": other_user_data["email"]
        }
        
        response = await client.put(
            "/api/v1/users/me",
            json=update_data,
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "already" in data["detail"].lower()
    
    async def test_delete_current_user(self, client: AsyncClient, authenticated_user):
        """Test deleting current user account"""
        response = await client.delete("/api/v1/users/me", headers=authenticated_user["headers"])
        
        assert response.status_code == 200
        data = response.json()
        assert "deleted" in data["message"].lower()
        
        # Verify user can no longer access protected endpoints
        protected_response = await client.get("/api/v1/users/me", headers=authenticated_user["headers"])
        assert protected_response.status_code == 401
    
    async def test_delete_current_user_unauthorized(self, client: AsyncClient):
        """Test deleting user without authentication fails"""
        response = await client.delete("/api/v1/users/me")
        assert response.status_code == 401
    
    async def test_user_cascade_delete_pets(self, client: AsyncClient, authenticated_user, test_pet):
        """Test that deleting user also deletes their pets"""
        # Verify pet exists
        pet_response = await client.get(
            f"/api/v1/pets/{test_pet['id']}",
            headers=authenticated_user["headers"]
        )
        assert pet_response.status_code == 200
        
        # Delete user
        delete_response = await client.delete("/api/v1/users/me", headers=authenticated_user["headers"])
        assert delete_response.status_code == 200
        
        # Create a new user to check if the pet still exists
        new_user_data = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "newpassword123"
        }
        register_response = await client.post("/api/v1/auth/register", json=new_user_data)
        assert register_response.status_code == 200
        
        # Login as new user
        login_data = {
            "username": new_user_data["email"],
            "password": new_user_data["password"]
        }
        login_response = await client.post(
            "/api/v1/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert login_response.status_code == 200
        new_token = login_response.json()["access_token"]
        new_headers = {"Authorization": f"Bearer {new_token}"}
        
        # Try to access the deleted user's pet (should fail)
        old_pet_response = await client.get(
            f"/api/v1/pets/{test_pet['id']}",
            headers=new_headers
        )
        assert old_pet_response.status_code == 404


class TestUserDataIntegrity:
    """Test user data integrity and security"""
    
    async def test_user_data_isolation(self, client: AsyncClient, sample_user_data):
        """Test that users can only see their own data"""
        # Create two users
        user1_data = {**sample_user_data, "email": "user1@example.com", "username": "user1"}
        user2_data = {**sample_user_data, "email": "user2@example.com", "username": "user2"}
        
        # Register both users
        user1_register = await client.post("/api/v1/auth/register", json=user1_data)
        user2_register = await client.post("/api/v1/auth/register", json=user2_data)
        assert user1_register.status_code == 200
        assert user2_register.status_code == 200
        
        user1_id = user1_register.json()["id"]
        user2_id = user2_register.json()["id"]
        
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
        
        user1_token = user1_login.json()["access_token"]
        user2_token = user2_login.json()["access_token"]
        user1_headers = {"Authorization": f"Bearer {user1_token}"}
        user2_headers = {"Authorization": f"Bearer {user2_token}"}
        
        # Each user should only see their own data
        user1_me = await client.get("/api/v1/users/me", headers=user1_headers)
        user2_me = await client.get("/api/v1/users/me", headers=user2_headers)
        
        assert user1_me.status_code == 200
        assert user2_me.status_code == 200
        assert user1_me.json()["id"] == user1_id
        assert user2_me.json()["id"] == user2_id
        assert user1_me.json()["id"] != user2_me.json()["id"]