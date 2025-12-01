"""
Test configuration and fixtures for the Pet Health API
"""
import pytest
import asyncio
import os
from typing import AsyncGenerator, Generator
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import get_db_session, Base
from app.core.config import settings

# Test database URL (in-memory SQLite for testing)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    poolclass=StaticPool,
    connect_args={"check_same_thread": False},
)

TestSessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
    class_=AsyncSession
)


async def get_test_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Override database session for testing"""
    async with TestSessionLocal() as session:
        yield session


@pytest.fixture(scope="session")
async def setup_test_db():
    """Set up test database"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Create test client with database override"""
    # Create tables for this test
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async def get_test_db():
        async with TestSessionLocal() as session:
            try:
                yield session
            finally:
                await session.rollback()
    
    app.dependency_overrides[get_db_session] = get_test_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()
    
    # Clean up tables after test
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session for testing"""
    # Create tables for this test
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestSessionLocal() as session:
        try:
            yield session
        finally:
            await session.rollback()
    
    # Clean up tables after test
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
def sample_user_data():
    """Sample user data for testing"""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123"
    }


@pytest.fixture
def sample_pet_data():
    """Sample pet data for testing"""
    return {
        "name": "Buddy",
        "species": "dog",
        "breed": "Golden Retriever",
        "age_years": 5,
        "weight_kg": 25.5,
        "sex": "male",
        "neutered": True
    }


@pytest.fixture
def sample_symptom_data():
    """Sample symptom data for testing"""
    return {
        "symptom_name": "lethargy",
        "severity": "moderate",
        "description": "Pet seems unusually tired and inactive",
        "observed_at": "2025-11-30T10:00:00Z",
        "duration_hours": 24
    }


@pytest.fixture
async def authenticated_user(client: AsyncClient, sample_user_data):
    """Create and authenticate a test user"""
    # Register user
    register_response = await client.post("/api/v1/auth/register", json=sample_user_data)
    assert register_response.status_code == 200
    user_data = register_response.json()
    
    # Login to get token
    login_data = {
        "username": sample_user_data["email"],
        "password": sample_user_data["password"]
    }
    login_response = await client.post(
        "/api/v1/auth/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert login_response.status_code == 200
    token_data = login_response.json()
    
    return {
        "user": user_data,
        "token": token_data["access_token"],
        "headers": {"Authorization": f"Bearer {token_data['access_token']}"}
    }


@pytest.fixture
async def authenticated_user2(client: AsyncClient):
    """Create and authenticate a second test user"""
    # Create different user data for user2
    user2_data = {
        "email": "user2@example.com",
        "password": "testpassword456"
    }
    
    # Register user2
    register_response = await client.post("/api/v1/auth/register", json=user2_data)
    assert register_response.status_code == 200
    user_data = register_response.json()
    
    # Login to get token
    login_data = {
        "username": user2_data["email"],
        "password": user2_data["password"]
    }
    login_response = await client.post(
        "/api/v1/auth/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert login_response.status_code == 200
    token_data = login_response.json()
    
    return {
        "user": user_data,
        "token": token_data["access_token"],
        "headers": {"Authorization": f"Bearer {token_data['access_token']}"}
    }


@pytest.fixture
async def test_pet(client: AsyncClient, authenticated_user, sample_pet_data):
    """Create a test pet"""
    response = await client.post(
        "/api/v1/pets/",
        json=sample_pet_data,
        headers=authenticated_user["headers"]
    )
    assert response.status_code == 200
    return response.json()