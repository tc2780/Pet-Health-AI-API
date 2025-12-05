"""
Pytest Configuration for Clause Control Tests

This file sets up test fixtures and configuration for the clause control test suite.
It provides the AsyncClient fixture and other test dependencies needed across
all clause control test modules.

These tests run against the actual application database (not an isolated test database)
to verify compliance controls in a real environment.
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient
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
    
    NOTE: These clause control tests run against the actual application database
    to verify compliance controls in the real environment.
    """
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac