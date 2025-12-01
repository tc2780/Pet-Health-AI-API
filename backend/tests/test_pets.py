"""
Tests for pet management endpoints
"""
import pytest
from httpx import AsyncClient
from uuid import uuid4


class TestPetEndpoints:
    """Test pet management endpoints"""
    
    async def test_create_pet_success(self, client: AsyncClient, authenticated_user, sample_pet_data):
        """Test successful pet creation"""
        response = await client.post(
            "/api/v1/pets/",
            json=sample_pet_data,
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["name"] == sample_pet_data["name"]
        assert data["species"] == sample_pet_data["species"]
        assert data["breed"] == sample_pet_data["breed"]
        assert data["age_years"] == sample_pet_data["age_years"]
        assert float(data["weight_kg"]) == sample_pet_data["weight_kg"]
        assert data["sex"] == sample_pet_data["sex"]
        assert data["neutered"] == sample_pet_data["neutered"]
        assert data["user_id"] == authenticated_user["user"]["id"]
        assert "created_at" in data
        assert "updated_at" in data
    
    async def test_create_pet_unauthorized(self, client: AsyncClient, sample_pet_data):
        """Test pet creation without authentication fails"""
        response = await client.post("/api/v1/pets/", json=sample_pet_data)
        assert response.status_code == 401
    
    async def test_create_pet_missing_required_fields(self, client: AsyncClient, authenticated_user):
        """Test pet creation with missing required fields fails"""
        incomplete_data = {
            "name": "Buddy"
            # Missing species and other required fields
        }
        response = await client.post(
            "/api/v1/pets/",
            json=incomplete_data,
            headers=authenticated_user["headers"]
        )
        assert response.status_code == 422
    
    async def test_create_pet_invalid_data_types(self, client: AsyncClient, authenticated_user):
        """Test pet creation with invalid data types fails"""
        invalid_data = {
            "name": "Buddy",
            "species": "dog",
            "age_years": "not_a_number",  # Should be integer
            "weight_kg": "not_a_number",  # Should be decimal
            "neutered": "not_a_boolean"   # Should be boolean
        }
        response = await client.post(
            "/api/v1/pets/",
            json=invalid_data,
            headers=authenticated_user["headers"]
        )
        assert response.status_code == 422
    
    async def test_get_user_pets_success(self, client: AsyncClient, authenticated_user, test_pet):
        """Test retrieving user's pets"""
        response = await client.get("/api/v1/pets/", headers=authenticated_user["headers"])
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        
        pet = data[0]
        assert pet["id"] == test_pet["id"]
        assert pet["name"] == test_pet["name"]
        assert pet["user_id"] == authenticated_user["user"]["id"]
    
    async def test_get_user_pets_empty_list(self, client: AsyncClient, authenticated_user):
        """Test retrieving pets when user has none"""
        response = await client.get("/api/v1/pets/", headers=authenticated_user["headers"])
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    async def test_get_user_pets_unauthorized(self, client: AsyncClient):
        """Test retrieving pets without authentication fails"""
        response = await client.get("/api/v1/pets/")
        assert response.status_code == 401
    
    async def test_get_specific_pet_success(self, client: AsyncClient, authenticated_user, test_pet):
        """Test retrieving a specific pet"""
        pet_id = test_pet["id"]
        response = await client.get(
            f"/api/v1/pets/{pet_id}",
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == pet_id
        assert data["name"] == test_pet["name"]
        assert data["user_id"] == authenticated_user["user"]["id"]
        # Should include symptoms and assessments (empty lists for new pet)
        assert "symptoms" in data
        assert "assessments" in data
        assert isinstance(data["symptoms"], list)
        assert isinstance(data["assessments"], list)
    
    async def test_get_specific_pet_not_found(self, client: AsyncClient, authenticated_user):
        """Test retrieving a non-existent pet"""
        fake_pet_id = str(uuid4())
        response = await client.get(
            f"/api/v1/pets/{fake_pet_id}",
            headers=authenticated_user["headers"]
        )
        assert response.status_code == 404
    
    async def test_get_specific_pet_unauthorized(self, client: AsyncClient, test_pet):
        """Test retrieving a pet without authentication fails"""
        pet_id = test_pet["id"]
        response = await client.get(f"/api/v1/pets/{pet_id}")
        assert response.status_code == 401
    
    async def test_get_specific_pet_wrong_user(self, client: AsyncClient, test_pet, sample_user_data):
        """Test retrieving another user's pet fails"""
        # Create a second user
        different_user_data = {
            "username": "differentuser",
            "email": "different@example.com",
            "password": "differentpassword123"
        }
        register_response = await client.post("/api/v1/auth/register", json=different_user_data)
        assert register_response.status_code == 200
        
        # Login as the second user
        login_data = {
            "username": different_user_data["email"],
            "password": different_user_data["password"]
        }
        login_response = await client.post(
            "/api/v1/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert login_response.status_code == 200
        different_user_token = login_response.json()["access_token"]
        different_user_headers = {"Authorization": f"Bearer {different_user_token}"}
        
        # Try to access the first user's pet
        pet_id = test_pet["id"]
        response = await client.get(
            f"/api/v1/pets/{pet_id}",
            headers=different_user_headers
        )
        assert response.status_code == 403
    
    async def test_update_pet_success(self, client: AsyncClient, authenticated_user, test_pet):
        """Test successful pet update"""
        pet_id = test_pet["id"]
        update_data = {
            "age_years": 6,
            "weight_kg": 26.0,
            "neutered": False
        }
        
        response = await client.put(
            f"/api/v1/pets/{pet_id}",
            json=update_data,
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == pet_id
        assert data["age_years"] == update_data["age_years"]
        assert float(data["weight_kg"]) == update_data["weight_kg"]
        assert data["neutered"] == update_data["neutered"]
        # Unchanged fields should remain the same
        assert data["name"] == test_pet["name"]
        assert data["species"] == test_pet["species"]
    
    async def test_update_pet_not_found(self, client: AsyncClient, authenticated_user):
        """Test updating a non-existent pet"""
        fake_pet_id = str(uuid4())
        update_data = {"age_years": 6}
        
        response = await client.put(
            f"/api/v1/pets/{fake_pet_id}",
            json=update_data,
            headers=authenticated_user["headers"]
        )
        assert response.status_code == 404
    
    async def test_update_pet_unauthorized(self, client: AsyncClient, test_pet):
        """Test updating a pet without authentication fails"""
        pet_id = test_pet["id"]
        update_data = {"age_years": 6}
        
        response = await client.put(f"/api/v1/pets/{pet_id}", json=update_data)
        assert response.status_code == 401
    
    async def test_delete_pet_success(self, client: AsyncClient, authenticated_user, test_pet):
        """Test successful pet deletion"""
        pet_id = test_pet["id"]
        
        response = await client.delete(
            f"/api/v1/pets/{pet_id}",
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "deleted successfully" in data["message"]
        
        # Verify pet is deleted by trying to retrieve it
        get_response = await client.get(
            f"/api/v1/pets/{pet_id}",
            headers=authenticated_user["headers"]
        )
        assert get_response.status_code == 404
    
    async def test_delete_pet_not_found(self, client: AsyncClient, authenticated_user):
        """Test deleting a non-existent pet"""
        fake_pet_id = str(uuid4())
        
        response = await client.delete(
            f"/api/v1/pets/{fake_pet_id}",
            headers=authenticated_user["headers"]
        )
        assert response.status_code == 404
    
    async def test_delete_pet_unauthorized(self, client: AsyncClient, test_pet):
        """Test deleting a pet without authentication fails"""
        pet_id = test_pet["id"]
        
        response = await client.delete(f"/api/v1/pets/{pet_id}")
        assert response.status_code == 401
    
    async def test_sync_single_pet_success(self, client: AsyncClient, authenticated_user, test_pet):
        """Test successful vet clinic sync for a single pet"""
        pet_id = test_pet["id"]
        
        response = await client.post(
            f"/api/v1/pets/{pet_id}/sync",
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "clinic_id" in data
        assert "synced_at" in data
        assert "payload_summary" in data
        assert data["payload_summary"]["pet_id"] == pet_id
        assert data["payload_summary"]["name"] == test_pet["name"]
    
    async def test_sync_single_pet_not_found(self, client: AsyncClient, authenticated_user):
        """Test syncing a non-existent pet"""
        fake_pet_id = str(uuid4())
        
        response = await client.post(
            f"/api/v1/pets/{fake_pet_id}/sync",
            headers=authenticated_user["headers"]
        )
        assert response.status_code == 404
    
    async def test_sync_single_pet_unauthorized(self, client: AsyncClient, test_pet):
        """Test syncing a pet without authentication fails"""
        pet_id = test_pet["id"]
        
        response = await client.post(f"/api/v1/pets/{pet_id}/sync")
        assert response.status_code == 401
    
    async def test_sync_single_pet_forbidden(self, client: AsyncClient, authenticated_user2, test_pet):
        """Test syncing another user's pet is forbidden"""
        pet_id = test_pet["id"]
        
        response = await client.post(
            f"/api/v1/pets/{pet_id}/sync",
            headers=authenticated_user2["headers"]
        )
        assert response.status_code == 403
    
    async def test_sync_all_user_pets_success(self, client: AsyncClient, authenticated_user, test_pet):
        """Test successful vet clinic sync for all user pets"""
        response = await client.post(
            "/api/v1/pets/sync-all",
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert isinstance(data["results"], list)
        assert len(data["results"]) >= 1  # Should have at least the test pet
        
        # Check the structure of the first result
        if data["results"]:
            result = data["results"][0]
            assert "pet_id" in result
            assert "synced" in result
            assert "synced_at" in result
            assert result["synced"] is True
    
    async def test_sync_all_user_pets_unauthorized(self, client: AsyncClient):
        """Test syncing all pets without authentication fails"""
        response = await client.post("/api/v1/pets/sync-all")
        assert response.status_code == 401
    
    async def test_sync_all_user_pets_empty_list(self, client: AsyncClient, authenticated_user2):
        """Test syncing all pets when user has no pets returns empty results"""
        response = await client.post(
            "/api/v1/pets/sync-all", 
            headers=authenticated_user2["headers"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert isinstance(data["results"], list)
        assert len(data["results"]) == 0  # authenticated_user2 has no pets