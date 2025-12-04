# Pet Health API - Unit Tests

This directory contains comprehensive unit tests for all API endpoints and functionality.

## Test Organization

### Test Files
- **`conftest.py`** - Test configuration, fixtures, and setup
- **`test_auth.py`** - Authentication endpoint tests
- **`test_pets.py`** - Pet management endpoint tests  
- **`test_users.py`** - User management endpoint tests
- **`test_health_and_general.py`** - Health checks and general API tests

### Test Coverage
- ✅ **Authentication Flow** - Registration, login, token validation
- ✅ **Pet CRUD Operations** - Create, read, update, delete pets
- ✅ **Vet Sync Integration** - Mock veterinary clinic data sync
- ✅ **User Management** - User profile operations
- ✅ **Authorization** - Access control and security
- ✅ **Data Validation** - Input validation and error handling
- ✅ **API Health** - Health checks and documentation
- ✅ **Error Scenarios** - 400, 401, 404, 422 responses
- ✅ **Concurrent Access** - Multi-user data isolation

## Running Tests

### Prerequisites
```bash
# Start the Docker containers
docker compose up -d
```

### Basic Test Run
```bash
# From the project root directory
docker compose exec api python run_tests.py
```

### With Coverage Report
```bash
# Generate HTML coverage report
docker compose exec api python run_tests.py --coverage
```

### Manual pytest Commands
```bash
# Run all tests (note: some integration tests may fail due to external dependencies)
docker compose exec api pytest tests/ -v

# Run specific test categories that work reliably
docker compose exec api pytest tests/unit/ -v

# Run AI tests (requires Ollama service to be running)
docker compose exec api pytest tests/ai/ -v

# Run specific test file
docker compose exec api pytest tests/unit/test_core_utilities.py -v

# Run specific test
docker compose exec api pytest tests/unit/test_core_utilities.py::TestSecurityFunctions::test_jwt_token_creation_and_validation -v

# Run with coverage
docker compose exec api pytest tests/unit/ --cov=app --cov-report=html

# Run integration tests
docker compose exec api pytest tests/integration/ -v
```

## AI Testing Setup

The AI tests require the Ollama service and models to be properly set up:

```bash
# Start Ollama service
docker compose up -d ollama

# Install a small model for testing (1-2GB download)
docker compose exec ollama ollama pull llama3.2:1b

# Now run AI tests
docker compose exec api pytest tests/ai/ -v
```

**AI Test Categories:**
- **Ollama Integration**: Direct API connectivity and response parsing
- **Performance**: Response time, concurrency, and memory usage benchmarks  
- **Symptom Analysis**: End-to-end AI analysis functionality

**Note**: AI tests may be skipped if Ollama is unavailable or models aren't installed.

## Test Database

Tests use an in-memory SQLite database that is:
- **Isolated** - Each test gets a clean database
- **Fast** - No external dependencies
- **Temporary** - Automatically cleaned up after tests

## Test Fixtures

### Key Fixtures (from `conftest.py`)
- **`client`** - Async HTTP client for API testing
- **`db_session`** - Database session for tests
- **`authenticated_user`** - User with valid JWT token
- **`test_pet`** - Sample pet for testing
- **`sample_*_data`** - Sample data for various entities

### Using Fixtures
```python
async def test_create_pet(client, authenticated_user, sample_pet_data):
    response = await client.post(
        "/api/v1/pets/",
        json=sample_pet_data,
        headers=authenticated_user["headers"]
    )
    assert response.status_code == 200
```

## Running Tests in Docker

All test commands should be run using the Docker container to ensure consistency with the production environment:

```bash
# Start containers first
docker compose up -d

# Run tests using the container
docker compose exec api pytest tests/ -v

# Check logs if needed
docker compose logs api
```

## Test Categories

### 🔐 Authentication Tests (`test_auth.py`)
- User registration validation
- Login with JWT token generation
- Password security
- Duplicate email handling
- Invalid credentials
- Token-based authorization

### 🐕 Pet Management Tests (`test_pets.py`)
- Pet creation with full validation
- Retrieving user's pets
- Pet details with symptoms/assessments
- Pet updates and modifications
- Pet deletion and cleanup
- **Vet clinic sync integration** - Single pet and bulk sync operations
- **Sync authorization** - Ownership validation and access control
- Multi-user data isolation
- Authorization and ownership

### 👤 User Tests (`test_users.py`)
- User profile retrieval
- User information updates
- Account deletion
- Data integrity and isolation
- Cascade deletion of user data

### 🏥 Health & General Tests (`test_health_and_general.py`)
- API health endpoints
- OpenAPI documentation
- Error handling (404, 405, 422)
- CORS and compression
- Concurrent request handling
- Large request processing

## Sample Test Output

```bash
🧪 Running Pet Health API Unit Tests
==================================================

tests/test_auth.py::TestAuthEndpoints::test_register_user_success PASSED
tests/test_auth.py::TestAuthEndpoints::test_register_user_duplicate_email PASSED
tests/test_auth.py::TestAuthEndpoints::test_login_success PASSED
tests/test_pets.py::TestPetEndpoints::test_create_pet_success PASSED
tests/test_pets.py::TestPetEndpoints::test_get_user_pets_success PASSED
tests/test_users.py::TestUserEndpoints::test_get_current_user PASSED
tests/test_health_and_general.py::TestHealthEndpoints::test_health_check PASSED

========== 25 passed in 3.45s ==========

==================================================
✅ All tests passed!
```

## Docker Test Commands Reference

```bash
# Quick test runs
docker compose exec api pytest tests/integration/ -v
docker compose exec api pytest tests/unit/ -v
docker compose exec api pytest tests/ai/ -v

# Specific test categories
docker compose exec api pytest tests/integration/test_pets.py -v
docker compose exec api pytest tests/integration/test_auth.py -v
docker compose exec api pytest tests/unit/test_auth_service.py -v
docker compose exec api pytest tests/ai/test_performance.py -v

# AI-specific tests (requires Ollama setup)
docker compose exec api pytest tests/ai/test_ollama_integration.py -v
docker compose exec api pytest tests/ai/test_symptom_analysis.py -v

# Coverage and reporting
docker compose exec api pytest tests/ --cov=app --cov-report=html --cov-report=term
docker compose exec api pytest tests/ --tb=short -q
```

## Writing New Tests

### Test Structure
```python
class TestNewEndpoint:
    """Test new endpoint functionality"""
    
    async def test_success_case(self, client, authenticated_user):
        """Test successful operation"""
        response = await client.get("/api/v1/new", headers=authenticated_user["headers"])
        assert response.status_code == 200
        assert "expected_field" in response.json()
    
    async def test_error_case(self, client):
        """Test error handling"""
        response = await client.get("/api/v1/new")
        assert response.status_code == 401
```

### Best Practices
- **Test both success and error cases**
- **Use descriptive test names**
- **Include authorization tests**
- **Validate response structure**
- **Test edge cases and validation**
- **Keep tests focused and independent**

## Troubleshooting

### Common Issues
1. **Container Not Running**: Start containers with `docker compose up -d`
2. **Import Errors**: Dependencies are pre-installed in the Docker image
3. **Database Errors**: Tests use in-memory database, no external setup needed
4. **Async Errors**: `pytest-asyncio` is pre-configured in the container
5. **Token Errors**: Use the `authenticated_user` fixture for protected endpoints
6. **Permission Errors**: Ensure Docker has proper permissions

### Docker-Specific Troubleshooting
```bash
# Check container status
docker compose ps

# View logs
docker compose logs api
docker compose logs ollama

# Restart containers if needed
docker compose restart

# Rebuild if dependencies changed
docker compose build api

# Setup Ollama for AI tests
docker compose up -d ollama
docker compose exec ollama ollama pull llama3.2:1b
```

### Getting Help
- Check test output for specific error messages
- Run individual test files to isolate issues: `docker compose exec api pytest tests/test_auth.py -v`
- Use `-v` flag for verbose output
- Check `conftest.py` for fixture definitions
- Ensure containers are running before executing tests