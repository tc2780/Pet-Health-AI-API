# Capstone Project

**Group members**: aria231, tc2780  

## Quick Start - Backend Development

### Prerequisites
- Docker and Docker Compose installed
- Python 3.11+ (for testing)

### Start the Backend Locally

1. **Start all services**:
   ```bash
   docker compose up -d
   ```

2. **Download the AI model** (first time only):
   ```bash
   # Default: More accurate model (recommended)
   docker compose exec ollama ollama pull llama3.2:3b
   
   # Alternative: Faster model (if resources are limited)
   docker compose exec ollama ollama pull llama3.2:1b
   ```

3. **Verify everything is running**:
   ```bash
   docker compose ps
   ```

4. **Access the API**:
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health
   - API Base: http://localhost:8000/api/v1/

### Run Demo Scripts

All demo scripts run inside the Docker container (no local Python setup needed):

```bash
# Run the main demo
docker compose exec api python demo_scripts/run_demo.py

# Run AI veterinary demo
docker compose exec api python demo_scripts/ai_veterinary_demo.py

# Run end-to-end workflow test
docker compose exec api python demo_scripts/end_to_end_workflow_test.py

# Test Ollama integration directly
docker compose exec api python demo_scripts/ollama_direct_test.py
```

Note: You can specify the model to use by adding an argument (`1b` for faster, `3b` for more accurate). Example:

```bash
docker compose exec api python demo_scripts/ai_veterinary_demo.py 1b
```

### Run Tests

Run the test suite inside the Docker container:

```bash
# Run all tests
docker compose exec api pytest

# Run specific test categories
docker compose exec api pytest tests/unit/
docker compose exec api pytest tests/integration/
docker compose exec api pytest tests/ai/

# Run with coverage
docker compose exec api pytest --cov=app --cov-report=html
```

### Test the Backend

Run the comprehensive test suite:
```bash
cd backend/happy_path_test
pip install requests  # if not already installed
python test_backend_workflow.py
```

### Stop the Backend

```bash
docker compose down
```

### Services Running Locally
- **FastAPI Backend**: http://localhost:8000
- **PostgreSQL Database**: localhost:5432
- **Redis Cache**: localhost:6379
- **Ollama AI Service**: localhost:11434
- **Prometheus Monitoring**: http://localhost:9090
- **Grafana Dashboard**: http://localhost:3000

## Key Features & API Endpoints

### Authentication & User Management
- **User Registration**: `POST /api/v1/auth/register`
- **User Login**: `POST /api/v1/auth/login`
- **Get Profile**: `GET /api/v1/auth/me`
- **Update Profile**: `PUT /api/v1/users/me`
- **Delete Account**: `DELETE /api/v1/users/me`
- **Export Data**: `GET /api/v1/users/me/export` (GDPR compliance)

### Pet Management
- **Create Pet**: `POST /api/v1/pets/`
- **List User's Pets**: `GET /api/v1/pets/`
- **Get Pet Details**: `GET /api/v1/pets/{pet_id}`
- **Update Pet**: `PUT /api/v1/pets/{pet_id}`
- **Delete Pet**: `DELETE /api/v1/pets/{pet_id}`

### AI-Powered Symptom Analysis
- **Record Symptoms**: `POST /api/v1/symptoms/`
- **Get Pet Symptoms**: `GET /api/v1/symptoms/pet/{pet_id}`
- **Get User's Pet Symptoms**: `GET /api/v1/symptoms/my-pets`
- **AI Symptom Assessment**: `POST /api/v1/symptoms/assess` (with Ollama LLM)
- **Get Assessments**: `GET /api/v1/symptoms/assessments/pet/{pet_id}`
- **Get All User Assessments**: `GET /api/v1/symptoms/assessments/my-pets`

### Veterinary Integration (Mock)
- **Sync Single Pet**: `POST /api/v1/pets/{id}/sync`
- **Sync All Pets**: `POST /api/v1/pets/sync-all`

## Vet Clinic Sync

This project includes a mock vet clinic sync service and API endpoints to demonstrate how pet data can be synchronized with external veterinary partners. The endpoints are:

- `POST /api/v1/pets/{id}/sync` — sync a single pet's data (mock)
- `POST /api/v1/pets/sync-all` — sync all pets for the authenticated user (mock)

When running with `docker compose`, the `api` service exposes `VET_SYNC_MOCK=true` to enable the mock sync behavior by default. Replace the mock implementation in `backend/app/services/vet_sync.py` with a real integration when ready.
