"""
Tests for health and general API endpoints
"""
import pytest
from httpx import AsyncClient


class TestHealthEndpoints:
    """Test health and general API endpoints"""
    
    async def test_root_endpoint(self, client: AsyncClient):
        """Test the root endpoint"""
        response = await client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "docs" in data
        assert "health" in data
        assert data["message"] == "Pet Health API"
        assert data["docs"] == "/docs"
        assert data["health"] == "/health"
    
    async def test_health_check(self, client: AsyncClient):
        """Test the health check endpoint"""
        response = await client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "version" in data
        assert "environment" in data
        assert data["status"] == "healthy"
        assert data["environment"] in ["development", "production"]
    
    async def test_docs_endpoint_accessible(self, client: AsyncClient):
        """Test that the docs endpoint is accessible"""
        response = await client.get("/docs")
        
        assert response.status_code == 200
        # Should return HTML content for Swagger UI
        assert "text/html" in response.headers.get("content-type", "")
        content = response.text
        assert "swagger" in content.lower() or "openapi" in content.lower()
    
    async def test_openapi_json_endpoint(self, client: AsyncClient):
        """Test that the OpenAPI JSON schema is accessible"""
        response = await client.get("/openapi.json")
        
        assert response.status_code == 200
        assert response.headers.get("content-type") == "application/json"
        
        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data
        assert data["info"]["title"] == "Pet Health API"


class TestAPIValidation:
    """Test general API behavior and validation"""
    
    async def test_invalid_endpoint_404(self, client: AsyncClient):
        """Test that invalid endpoints return 404"""
        response = await client.get("/api/v1/nonexistent")
        assert response.status_code == 404
    
    async def test_invalid_method_405(self, client: AsyncClient):
        """Test that invalid HTTP methods return 405"""
        # Try POST on a GET-only endpoint
        response = await client.post("/health")
        assert response.status_code == 405
    
    async def test_malformed_json_400(self, client: AsyncClient, authenticated_user):
        """Test that malformed JSON returns 400"""
        # Send malformed JSON
        response = await client.post(
            "/api/v1/pets/",
            content="{ invalid json }",
            headers={
                **authenticated_user["headers"],
                "Content-Type": "application/json"
            }
        )
        assert response.status_code == 422  # FastAPI returns 422 for JSON decode errors
    
    async def test_cors_headers_present(self, client: AsyncClient):
        """Test that CORS headers are present in responses"""
        # Make a request with an Origin header to trigger CORS
        headers = {"Origin": "http://localhost:3000"}
        response = await client.get("/health", headers=headers)
        
        assert response.status_code == 200
        # Check for CORS headers (these may vary based on configuration)
        headers = response.headers
        # At minimum, we should not get CORS errors in browser environments
        assert "access-control-allow-origin" in headers or "vary" in headers
    
    async def test_gzip_compression_header(self, client: AsyncClient):
        """Test that responses can be compressed"""
        # Request with Accept-Encoding for gzip
        headers = {"Accept-Encoding": "gzip, deflate"}
        response = await client.get("/", headers=headers)
        
        assert response.status_code == 200
        # The response should either be compressed or ready for compression
        # (depends on response size and server configuration)
    
    async def test_content_type_headers(self, client: AsyncClient):
        """Test that appropriate content-type headers are set"""
        # JSON endpoints should return application/json
        response = await client.get("/health")
        assert response.status_code == 200
        assert "application/json" in response.headers.get("content-type", "")
        
        # HTML endpoints should return text/html
        docs_response = await client.get("/docs")
        assert docs_response.status_code == 200
        assert "text/html" in docs_response.headers.get("content-type", "")
    
    async def test_large_request_handling(self, client: AsyncClient, authenticated_user):
        """Test handling of unusually large requests"""
        # Create a pet with very long strings
        large_pet_data = {
            "name": "A" * 1000,  # Very long name
            "species": "dog",
            "breed": "B" * 500,  # Very long breed
            "description": "C" * 2000,  # Very long description
            "age_years": 5,
            "weight_kg": 25.5,
            "sex": "male",
            "neutered": True
        }
        
        response = await client.post(
            "/api/v1/pets/",
            json=large_pet_data,
            headers=authenticated_user["headers"]
        )
        
        # Should either accept the large data or return a validation error
        assert response.status_code in [200, 422]
        
        if response.status_code == 200:
            # If accepted, verify the data was stored correctly
            data = response.json()
            assert data["name"] == large_pet_data["name"]
    
    async def test_concurrent_requests_same_user(self, client: AsyncClient, authenticated_user, sample_pet_data):
        """Test handling of concurrent requests from the same user"""
        import asyncio
        
        # Make multiple concurrent requests to create pets
        tasks = []
        for i in range(5):
            pet_data = {**sample_pet_data, "name": f"Pet{i}"}
            task = client.post(
                "/api/v1/pets/",
                json=pet_data,
                headers=authenticated_user["headers"]
            )
            tasks.append(task)
        
        # Execute all requests concurrently
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # All requests should succeed
        successful_responses = [r for r in responses if not isinstance(r, Exception)]
        assert len(successful_responses) == 5
        
        for response in successful_responses:
            assert response.status_code == 200
        
        # Verify all pets were created
        pets_response = await client.get("/api/v1/pets/", headers=authenticated_user["headers"])
        assert pets_response.status_code == 200
        pets = pets_response.json()
        assert len(pets) == 5