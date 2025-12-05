"""
Pytest Configuration for Clause Control Tests

This file sets up test fixtures and configuration for the clause control test suite.
It provides the AsyncClient fixture and other test dependencies needed across
all clause control test modules.
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient
from fastapi.testclient import TestClient
import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "app"))

from app.main import app


@pytest_asyncio.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def client():
    """
    Create an async HTTP client for testing API endpoints
    """
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """
    Set up test environment variables and configuration
    """
    # Set environment variables for testing
    os.environ["ENVIRONMENT"] = "test"
    os.environ["DATABASE_URL"] = "sqlite:///./test.db"
    os.environ["JWT_SECRET"] = "test-secret-key"
    
    yield
    
    # Cleanup after tests
    pass