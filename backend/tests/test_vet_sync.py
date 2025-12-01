import uuid
import datetime
import pytest
from types import SimpleNamespace

from httpx import AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_sync_single_pet(monkeypatch):
    # Prepare fake user and override auth dependency
    user_id = uuid.uuid4()
    pet_id = uuid.uuid4()

    fake_user = SimpleNamespace(
        id=user_id,
        email="tester@example.com",
        is_active=True,
        is_verified=True,
        created_at=datetime.datetime.utcnow(),
        updated_at=datetime.datetime.utcnow(),
    )

    # Override get_current_user dependency in pets endpoints
    from app.api.v1.endpoints.pets import get_current_user

    app.dependency_overrides[get_current_user] = lambda: fake_user

    # Mock PetService.get_pet_by_id to return a pet owned by fake_user
    async def fake_get_pet_by_id(self, pet_id_arg):
        return SimpleNamespace(
            id=pet_id_arg,
            user_id=user_id,
            name="Fido",
            species="dog",
            age_years=4,
            symptoms=[],
        )

    # Mock VetSyncService.sync_pet to return a deterministic payload
    async def fake_sync_pet(self, pet_id_arg):
        return {"success": True, "pet_id": str(pet_id_arg), "clinic_id": "mock-clinic-001"}

    monkeypatch.setattr("app.services.pet.PetService.get_pet_by_id", fake_get_pet_by_id)
    monkeypatch.setattr("app.services.vet_sync.VetSyncService.sync_pet", fake_sync_pet)

    async with AsyncClient(app=app, base_url="http://test") as ac:
        resp = await ac.post(f"/api/v1/pets/{pet_id}/sync")
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["clinic_id"] == "mock-clinic-001"

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_sync_all_user_pets(monkeypatch):
    user_id = uuid.uuid4()

    fake_user = SimpleNamespace(
        id=user_id,
        email="tester2@example.com",
        is_active=True,
        is_verified=True,
        created_at=datetime.datetime.utcnow(),
        updated_at=datetime.datetime.utcnow(),
    )

    from app.api.v1.endpoints.pets import get_current_user
    app.dependency_overrides[get_current_user] = lambda: fake_user

    # Mock VetSyncService.sync_all_user_pets
    async def fake_sync_all(self, user_id_arg):
        return [
            {"pet_id": str(uuid.uuid4()), "synced": True, "synced_at": datetime.datetime.utcnow().isoformat() + "Z"}
        ]

    monkeypatch.setattr("app.services.vet_sync.VetSyncService.sync_all_user_pets", fake_sync_all)

    async with AsyncClient(app=app, base_url="http://test") as ac:
        resp = await ac.post(f"/api/v1/pets/sync-all")
        assert resp.status_code == 200
        data = resp.json()
        assert "results" in data
        assert isinstance(data["results"], list)

    app.dependency_overrides.clear()
