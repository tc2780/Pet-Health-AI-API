# Pet Health API Backend

AI-powered pet health symptom tracking and analysis API built with FastAPI.

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.11+ (for local development)

### Development Setup

1. **Clone and navigate to project**:
```bash
git clone <repository-url>
cd capstone-final-project
```

2. **Start all services**:
```bash
docker compose up -d
```

3. **Verify services are running**:
```bash
# Check API health
curl http://localhost:8000/health

# Check API documentation
open http://localhost:8000/docs
```

4. **Set up AI model (first time only)**:
```bash
# Pull the Llama model for local AI processing
docker compose exec ollama ollama pull llama3.1:latest
```

## 📊 **Services Overview**

| Service | Port | Description |
|---------|------|-------------|
| **API** | 8000 | FastAPI backend with automatic docs |
| **PostgreSQL** | 5432 | Primary database with pet/symptom data |
| **Redis** | 6379 | Caching and session storage |
| **Ollama** | 11434 | Local AI processing (privacy-first) |
| **Prometheus** | 9090 | Metrics collection |
| **Grafana** | 3000 | Monitoring dashboards |

## 🔗 **API Endpoints**

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - User login
- `GET /api/v1/auth/me` - Get current user

### Pet Management  
- `POST /api/v1/pets/` - Create new pet
- `GET /api/v1/pets/` - List user's pets
- `GET /api/v1/pets/{id}` - Get pet with symptoms
- `PUT /api/v1/pets/{id}` - Update pet information
- `DELETE /api/v1/pets/{id}` - Delete pet

### Vet Clinic Sync (Integration)
- `POST /api/v1/pets/{id}/sync` - Sync a single pet's data with a vet clinic (mock).
- `POST /api/v1/pets/sync-all` - Sync all pets belonging to the authenticated user (mock).

These endpoints currently perform a mock sync and return a `SyncResult` or `SyncAllResponse`. In production replace the mock service with real HTTP clients and secure authentication with partner clinics.

### Symptoms & AI Analysis
- `POST /api/v1/symptoms/` - Log new symptom
- `GET /api/v1/symptoms/pet/{id}` - Get pet's symptom history
- `POST /api/v1/symptoms/analyze` - AI symptom analysis

## 🧪 **Testing the API**

### Register a new user:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
     -H "Content-Type: application/json" \
     -d '{"email": "test@example.com", "password": "securepassword"}'
```

### Login and get token:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=test@example.com&password=securepassword"
```

### Create a pet (use token from login):
```bash
curl -X POST "http://localhost:8000/api/v1/pets/" \
     -H "Authorization: Bearer YOUR_TOKEN_HERE" \
     -H "Content-Type: application/json" \
     -d '{"name": "Buddy", "species": "dog", "breed": "Golden Retriever", "age_years": 3}'
```

### Vet Sync examples

Sync a single pet (replace PET_ID):

```bash
curl -X POST "http://localhost:8000/api/v1/pets/PET_ID/sync" \
   -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

Sync all user's pets:

```bash
curl -X POST "http://localhost:8000/api/v1/pets/sync-all" \
   -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

Note: When running via `docker-compose`, the `api` service sets `VET_SYNC_MOCK=true` to enable mock behaviour by default.

## 🔧 **Development**

### Local Development Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Run locally (with external services)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Database Migrations
```bash
# Generate migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head
```

## 📊 **Monitoring**

- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Prometheus Metrics**: http://localhost:9090
- **Grafana Dashboards**: http://localhost:3000 (admin/admin)

## 🛡️ **Security Features**

- JWT-based authentication
- Password hashing with bcrypt
- Input validation with Pydantic
- SQL injection prevention with SQLAlchemy
- CORS protection
- Rate limiting (configurable)

## 🤖 **AI Integration**

The API uses local AI processing for privacy-first veterinary guidance:

- **Local LLM**: Ollama with Llama 3.1 for symptom analysis
- **Privacy-First**: All AI processing happens locally
- **Conservative Approach**: Provides cautious recommendations with disclaimers
- **Fallback Support**: Optional OpenAI integration for enhanced features

## 🐳 **Docker Commands**

```bash
# Start all services
docker compose up -d

# View logs
docker compose logs -f api

# Restart specific service
docker compose restart api

# Stop all services
docker compose down

# Reset everything (including data)
docker compose down -v
```

## 🔍 **Troubleshooting**

### Common Issues:

1. **Database Connection Failed**:
   ```bash
   docker compose logs postgres
   # Ensure PostgreSQL is healthy before starting API
   ```

2. **AI Service Not Responding**:
   ```bash
   docker compose logs ollama
   # Pull the model if not already downloaded
   docker compose exec ollama ollama pull llama3.1:latest
   ```

3. **Port Conflicts**:
   - Check if ports 8000, 5432, 6379, 11434 are available
   - Modify ports in docker-compose.yml if needed

## 📝 **Environment Variables**

Key configuration options in `.env`:

```bash
# Database
DATABASE_URL=postgresql://petuser:petpass@localhost:5432/petdb

# Security
SECRET_KEY=your-secure-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI Configuration
AI_PROVIDER=ollama  # or "openai"
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:latest

# Features
DEBUG=true
RATE_LIMIT_ENABLED=true
```