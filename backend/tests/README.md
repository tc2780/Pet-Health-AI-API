# Pet Health API - Unit Tests

This directory contains comprehensive unit tests for all API endpoints and functionality.

## Test Organization

### Test Structure
```
tests/
├── conftest.py                    # Test configuration and fixtures
├── test_clause_control_fixed.py  # Privacy & compliance validation tests
├── unit/                          # Unit tests for services and core functionality  
│   ├── test_auth_service.py      # Authentication service tests
│   ├── test_core_utilities.py    # Core utility function tests
│   ├── test_pet_service.py       # Pet service layer tests
│   ├── test_symptom_service.py   # Symptom and AI analysis service tests
│   └── test_user_service.py      # User service layer tests
├── integration/                   # API integration tests
│   ├── test_auth.py              # Authentication endpoints
│   ├── test_health_and_general.py # Health checks and general API
│   ├── test_pets.py              # Pet management endpoints
│   └── test_users.py             # User management endpoints
└── ai/                           # AI and ML integration tests
    ├── test_ollama_integration.py # Direct Ollama API tests
    ├── test_performance.py        # AI performance and benchmarks
    └── test_symptom_analysis.py   # End-to-end AI symptom analysis
```

### Test Coverage (164 Total Tests)
- ✅ **Unit Tests (103 tests)** - Service layer, core utilities, business logic
- ✅ **Integration Tests (18 tests)** - API endpoints, database persistence
- ✅ **AI Tests (19 tests)** - Ollama integration, symptom analysis, performance
- ✅ **Compliance Tests (24 tests)** - Privacy controls, ethics validation, data export

## Running Tests

### Prerequisites
```bash
# Start the Docker containers
docker compose up -d
```

### Basic Test Run
```bash
# Run all tests (164 tests)
docker compose exec api pytest tests/ -v

# Quick comprehensive test
docker compose exec api pytest tests/ --tb=short -q

# Run by category
docker compose exec api pytest tests/unit/ -v           # Service layer tests
docker compose exec api pytest tests/integration/ -v    # API endpoint tests  
docker compose exec api pytest tests/ai/ -v            # AI functionality tests
docker compose exec api pytest tests/test_clause_control_fixed.py -v  # Compliance tests
```

### With Coverage Report
```bash
# Generate HTML coverage report
docker compose exec api pytest tests/unit/ --cov=app --cov-report=html

# Coverage with terminal output
docker compose exec api pytest tests/ --cov=app --cov-report=term-missing
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
docker compose exec ollama ollama pull llama3.2:3b

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

### 🔐 Authentication Tests (`integration/test_auth.py`)
- User registration validation
- Login with JWT token generation
- Password security and hashing
- Duplicate email handling
- Invalid credentials
- Token-based authorization
- Cross-session authentication

### 🐕 Pet Management Tests (`integration/test_pets.py`)
- Pet creation with full validation
- Retrieving user's pets with data relationships
- Pet details with symptoms/assessments
- Pet updates and modifications
- Pet deletion and cascade cleanup
- **Vet clinic sync integration** - Single pet and bulk sync operations
- Multi-user data isolation
- Authorization and ownership validation

### 👤 User Tests (`integration/test_users.py`)
- User profile retrieval
- User information updates
- Account deletion with cascade effects
- **Data export functionality** - GDPR-compliant complete data export
- Data integrity and isolation
- Username/email uniqueness validation

### 🩺 Symptom & AI Analysis Tests (`unit/test_symptom_service.py`, `ai/test_symptom_analysis.py`)
- Symptom recording and tracking
- **AI-powered symptom analysis** with Ollama integration
- Urgency level assessment (emergency/high/moderate/low)
- **Fallback analysis** when AI unavailable
- Response parsing and validation
- Context-aware recommendations
- Medical disclaimer inclusion

### 🏥 Health & General Tests (`integration/test_health_and_general.py`)
- API health endpoints
- OpenAPI documentation
- Error handling (404, 405, 422)
- CORS and compression
- Concurrent request handling

### 🛡️ Privacy & Compliance Tests (`test_clause_control_fixed.py`)
- **Data minimization** - No excessive data collection
- **User control** - Data modification and deletion rights
- **Privacy controls** - No third-party data sharing
- **AI ethics** - Conservative medical advice, disclaimers
- **Data portability** - Complete user data export
- **Red bar compliance** - Critical security and privacy controls

## Sample Test Output

```bash
🧪 Running Pet Health API Unit Tests
==================================================

tests/unit/test_auth_service.py::TestAuthService::test_get_current_user_success PASSED
tests/unit/test_pet_service.py::TestPetServiceQueries::test_get_pet_by_id_found PASSED  
tests/unit/test_symptom_service.py::TestSymptomServicePrivateMethods::test_parse_ai_response_valid_json PASSED
tests/integration/test_auth.py::TestAuthAPIIntegration::test_register_login_flow_integration PASSED
tests/integration/test_pets.py::TestPetAPIIntegration::test_pet_crud_database_persistence PASSED
tests/integration/test_users.py::TestUserAPIIntegration::test_user_update_database_persistence PASSED
tests/ai/test_ollama_integration.py::TestOllamaIntegration::test_ollama_api_connectivity PASSED
tests/ai/test_symptom_analysis.py::TestAISymptomAnalysis::test_ai_analysis_success PASSED
tests/test_clause_control_fixed.py::test_complete_data_export PASSED
tests/test_clause_control_fixed.py::TestRedBarCompliance::test_no_external_ai_calls_RED_BAR PASSED

========== 161 passed, 3 skipped in 52.74s ==========

==================================================
✅ 98.2% test success rate! (161/164 passed, 3 skipped)
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
docker compose exec ollama ollama pull llama3.2:3b
```

### Getting Help
- Check test output for specific error messages
- Run individual test files to isolate issues: `docker compose exec api pytest tests/test_auth.py -v`
- Use `-v` flag for verbose output
- Check `conftest.py` for fixture definitions
- Ensure containers are running before executing tests