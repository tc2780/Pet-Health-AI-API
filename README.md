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
   docker compose exec ollama ollama pull llama3.1:latest
   ```

3. **Verify everything is running**:
   ```bash
   docker compose ps
   ```

4. **Access the API**:
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health
   - API Base: http://localhost:8000/api/v1/

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
