"""
Tests for health and essential API integration behavior
"""
import pytest
from httpx import AsyncClient


class TestHealthEndpoints:
    """Test health and essential API endpoints"""
    
    async def test_root_endpoint(self, client: AsyncClient):
        """Test the root endpoint returns proper API information"""
        response = await client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "docs" in data
        assert "health" in data
        assert data["message"] == "Pet Health API"
    
    async def test_health_check(self, client: AsyncClient):
        """Test the health check endpoint"""
        response = await client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
        assert "environment" in data
    
    async def test_openapi_integration(self, client: AsyncClient):
        """Test that OpenAPI schema is properly integrated"""
        response = await client.get("/openapi.json")
        
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data
        assert data["info"]["title"] == "Pet Health API"


class TestAPIIntegration:
    """Test essential API integration behavior"""
    
    async def test_invalid_endpoint_404(self, client: AsyncClient):
        """Test that invalid endpoints return 404"""
        response = await client.get("/api/v1/nonexistent")
        assert response.status_code == 404
    
    async def test_cors_and_headers_integration(self, client: AsyncClient):
        """Test that API properly handles headers and CORS in integration"""
        headers = {"Origin": "http://localhost:3000"}
        response = await client.get("/health", headers=headers)
        
        assert response.status_code == 200
        assert "application/json" in response.headers.get("content-type", "")
        # CORS headers should be present or handled gracefully
        response_headers = response.headers
        assert "access-control-allow-origin" in response_headers or "vary" in response_headers
    
    async def test_concurrent_authenticated_requests(self, client: AsyncClient, authenticated_user):
        """Test handling of concurrent authenticated requests"""
        import asyncio
        
        async def make_request():
            return await client.get("/api/v1/users/me", headers=authenticated_user["headers"])
        
        # Make 3 concurrent requests to test session handling
        tasks = [make_request() for _ in range(3)]
        responses = await asyncio.gather(*tasks)
        
        # All requests should succeed with consistent data
        for response in responses:
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == authenticated_user["user"]["id"]
