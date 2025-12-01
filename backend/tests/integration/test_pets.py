"""
Tests for pet management API integration
"""
import pytest
from httpx import AsyncClient
from uuid import uuid4


class TestPetAPIIntegration:
    """Test pet management API integration with database and authentication"""
    
    async def test_pet_crud_database_persistence(self, client: AsyncClient, authenticated_user, sample_pet_data):
        """Test full CRUD workflow integration with database persistence"""
        # Create pet
        create_response = await client.post(
            "/api/v1/pets/",
            json=sample_pet_data,
            headers=authenticated_user["headers"]
        )
        assert create_response.status_code == 200
        pet_data = create_response.json()
        pet_id = pet_data["id"]
        
        # Read pet back to verify persistence
        get_response = await client.get(
            f"/api/v1/pets/{pet_id}",
            headers=authenticated_user["headers"]
        )
        assert get_response.status_code == 200
        retrieved_pet = get_response.json()
        assert retrieved_pet["name"] == sample_pet_data["name"]
        assert retrieved_pet["species"] == sample_pet_data["species"]
        
        # Update pet and verify persistence
        update_data = {"age_years": 8, "weight_kg": 28.5}
        update_response = await client.put(
            f"/api/v1/pets/{pet_id}",
            json=update_data,
            headers=authenticated_user["headers"]
        )
        assert update_response.status_code == 200
        
        # Verify updates persisted
        get_updated_response = await client.get(
            f"/api/v1/pets/{pet_id}",
            headers=authenticated_user["headers"]
        )
        updated_pet = get_updated_response.json()
        assert updated_pet["age_years"] == 8
        assert float(updated_pet["weight_kg"]) == 28.5
        
        # Delete and verify removal
        delete_response = await client.delete(
            f"/api/v1/pets/{pet_id}",
            headers=authenticated_user["headers"]
        )
        assert delete_response.status_code == 200
        
        # Verify deletion
        get_deleted_response = await client.get(
            f"/api/v1/pets/{pet_id}",
            headers=authenticated_user["headers"]
        )
        assert get_deleted_response.status_code == 404
    
    async def test_pet_user_ownership_enforcement(self, client: AsyncClient, authenticated_user, test_pet, sample_user_data):
        """Test that pet ownership is properly enforced across user sessions"""
        # Create a different user
        different_user_data = {
            "username": "differentowner",
            "email": "different@owner.com", 
            "password": "differentpassword123"
        }
        register_response = await client.post("/api/v1/auth/register", json=different_user_data)
        assert register_response.status_code == 200
        
        # Login as different user
        login_response = await client.post(
            "/api/v1/auth/login",
            data={"username": different_user_data["email"], "password": different_user_data["password"]},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        different_headers = {"Authorization": f"Bearer {login_response.json()['access_token']}"}
        
        # Different user should not see original user's pet in their list
        pets_response = await client.get("/api/v1/pets/", headers=different_headers)
        assert pets_response.status_code == 200
        assert len(pets_response.json()) == 0
        
        # Different user should not be able to access original user's pet directly
        pet_id = test_pet["id"]
        get_response = await client.get(f"/api/v1/pets/{pet_id}", headers=different_headers)
        assert get_response.status_code == 403
        
        # Different user should not be able to modify original user's pet
        update_response = await client.put(
            f"/api/v1/pets/{pet_id}",
            json={"age_years": 999},
            headers=different_headers
        )
        assert update_response.status_code == 403
    
    async def test_pet_data_relationships_integration(self, client: AsyncClient, authenticated_user, test_pet):
        """Test that pet data properly integrates with related entities (symptoms, assessments)"""
        pet_id = test_pet["id"]
        
        # Get pet details - should include empty relationships for new pet
        response = await client.get(
            f"/api/v1/pets/{pet_id}",
            headers=authenticated_user["headers"]
        )
        assert response.status_code == 200
        data = response.json()
        
        # Should include symptoms and assessments even if empty
        assert "symptoms" in data
        assert "assessments" in data
        assert isinstance(data["symptoms"], list)
        assert isinstance(data["assessments"], list)
        assert data["user_id"] == authenticated_user["user"]["id"]
    
    async def test_pet_sync_vet_clinic_integration(self, client: AsyncClient, authenticated_user, test_pet):
        """Test pet synchronization with vet clinic system integration"""
        pet_id = test_pet["id"]
        
        # Test single pet sync
        sync_response = await client.post(
            f"/api/v1/pets/{pet_id}/sync",
            headers=authenticated_user["headers"]
        )
        
        assert sync_response.status_code == 200
        sync_data = sync_response.json()
        assert sync_data["success"] is True
        assert "clinic_id" in sync_data
        assert "synced_at" in sync_data
        assert sync_data["payload_summary"]["pet_id"] == pet_id
        
        # Test all pets sync
        sync_all_response = await client.post(
            "/api/v1/pets/sync-all",
            headers=authenticated_user["headers"]
        )
        
        assert sync_all_response.status_code == 200
        sync_all_data = sync_all_response.json()
        assert "results" in sync_all_data
        assert len(sync_all_data["results"]) >= 1
        
        # Verify sync result structure - results follow SyncResult schema
        result = sync_all_data["results"][0]
        assert "success" in result
        assert "synced_at" in result
        assert result["success"] is True
        # Check that payload_summary contains pet_id
        assert result["payload_summary"] is not None
        assert result["payload_summary"]["pet_id"] == pet_id