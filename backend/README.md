# Pet Health API Backend

AI-powered pet health symptom tracking and analysis API built with FastAPI.

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.11+ (optional, only if running outside Docker)

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
# Default: More accurate model (recommended)
docker compose exec ollama ollama pull llama3.2:3b

# Alternative: Faster model (if resources are limited)
docker compose exec ollama ollama pull llama3.2:1b
```

## 🧪 Testing

The API includes comprehensive testing with Docker-based execution for production-like conditions.

### Quick Test Execution

```bash
# Run all tests in Docker environment (recommended)
./run-docker-tests.sh

# Run specific test types
./run-docker-tests.sh standard      # Unit, integration, AI tests (2-5 min)
./run-docker-tests.sh performance   # Load and stress tests (5-10 min) 
./run-docker-tests.sh chaos         # Resilience testing (10-15 min)

# Local testing (requires setup)
cd backend && python run_tests.py
```

### Test Categories

| Test Type | Coverage | Duration | Purpose |
|-----------|----------|----------|---------|
| **Standard** | Unit, Integration, AI | 2-5 min | Core functionality validation |
| **Performance** | Load, Stress, Throughput | 5-10 min | Performance benchmarking |
| **Chaos** | Failure simulation | 10-15 min | Resilience and recovery testing |

## 📊 **Services Overview**

| Service | Port | Description |
|---------|------|-------------|
| **API** | 8000 | FastAPI backend with automatic docs |
| **PostgreSQL** | 5432 | Primary database with pet/symptom data |
| **Redis** | 6379 | Caching and session storage |
| **Ollama** | 11434 | Local AI processing (privacy-first) |
| **Prometheus** | 9090 | Metrics collection |
| **Grafana** | 3000 | Monitoring dashboards |

## 🔗 **Complete API Reference**

### 🔐 **Authentication Endpoints**
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/api/v1/auth/register` | Register new user account | ❌ |
| `POST` | `/api/v1/auth/login` | Login and get access token | ❌ |
| `GET` | `/api/v1/auth/me` | Get current user profile | ✅ |

### 👤 **User Management Endpoints**  
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/api/v1/users/me` | Get current user profile | ✅ |
| `PUT` | `/api/v1/users/me` | Update user profile (email, username, password) | ✅ |
| `DELETE` | `/api/v1/users/me` | Delete user account and all data | ✅ |
| `GET` | `/api/v1/users/me/export` | Export all user data (GDPR compliance) | ✅ |

### 🐕 **Pet Management Endpoints**
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/api/v1/pets/` | Create new pet | ✅ |
| `GET` | `/api/v1/pets/` | List user's pets | ✅ |
| `GET` | `/api/v1/pets/{pet_id}` | Get specific pet with symptoms & assessments | ✅ |
| `PUT` | `/api/v1/pets/{pet_id}` | Update pet information | ✅ |
| `DELETE` | `/api/v1/pets/{pet_id}` | Delete pet and all associated data | ✅ |

### 🔄 **Veterinary Sync Endpoints**
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/api/v1/pets/{pet_id}/sync` | Sync single pet with external vet system (mock) | ✅ |
| `POST` | `/api/v1/pets/sync-all` | Sync all user's pets with vet system (mock) | ✅ |

### 🩺 **Symptom Tracking Endpoints**
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/api/v1/symptoms/` | Create new symptom record | ✅ |
| `GET` | `/api/v1/symptoms/pet/{pet_id}` | Get all symptoms for specific pet | ✅ |
| `GET` | `/api/v1/symptoms/my-pets` | Get all symptoms for user's pets | ✅ |
| `GET` | `/api/v1/symptoms/{symptom_id}` | Get specific symptom details | ✅ |
| `PUT` | `/api/v1/symptoms/{symptom_id}` | Update symptom information | ✅ |
| `DELETE` | `/api/v1/symptoms/{symptom_id}` | Delete symptom record | ✅ |

### 🤖 **AI Assessment Endpoints**
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/api/v1/symptoms/assess` | Create AI-powered symptom assessment | ✅ |
| `GET` | `/api/v1/symptoms/assessments/pet/{pet_id}` | Get all AI assessments for pet | ✅ |
| `GET` | `/api/v1/symptoms/assessments/my-pets` | Get all assessments for user's pets | ✅ |
| `GET` | `/api/v1/symptoms/assessments/{assessment_id}` | Get specific AI assessment | ✅ |

### 🏥 **Health & Utility Endpoints**
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/` | Root endpoint | ❌ |
| `GET` | `/health` | System health check | ❌ |
| `GET` | `/docs` | Interactive API documentation | ❌ |
| `GET` | `/openapi.json` | OpenAPI specification | ❌ |

## 🧪 **API Usage Examples**

### 1. **User Registration & Authentication**
```bash
# Register a new user
curl -X POST "http://localhost:8000/api/v1/auth/register" \
     -H "Content-Type: application/json" \
     -d '{"email": "test@example.com", "password": "securepassword"}'

# Login to get access token
curl -X POST "http://localhost:8000/api/v1/auth/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=test@example.com&password=securepassword"

# Update user profile
curl -X PUT "http://localhost:8000/api/v1/users/me" \
     -H "Authorization: Bearer YOUR_TOKEN_HERE" \
     -H "Content-Type: application/json" \
     -d '{"username": "petlover", "email": "newemail@example.com"}'

# Export all user data (GDPR compliance)
curl -X GET "http://localhost:8000/api/v1/users/me/export" \
     -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 2. **Pet Management**
```bash
# Create a new pet
curl -X POST "http://localhost:8000/api/v1/pets/" \
     -H "Authorization: Bearer YOUR_TOKEN_HERE" \
     -H "Content-Type: application/json" \
     -d '{"name": "Buddy", "species": "dog", "breed": "Golden Retriever", "age_years": 3}'

# Get pet with symptoms and assessments
curl -X GET "http://localhost:8000/api/v1/pets/PET_ID_HERE" \
     -H "Authorization: Bearer YOUR_TOKEN_HERE"

# Update pet information
curl -X PUT "http://localhost:8000/api/v1/pets/PET_ID_HERE" \
     -H "Authorization: Bearer YOUR_TOKEN_HERE" \
     -H "Content-Type: application/json" \
     -d '{"weight_kg": 25.5, "age_years": 4}'
```

### 3. **Symptom Tracking**
```bash
# Log a new symptom
curl -X POST "http://localhost:8000/api/v1/symptoms/" \
     -H "Authorization: Bearer YOUR_TOKEN_HERE" \
     -H "Content-Type: application/json" \
     -d '{
       "pet_id": "PET_ID_HERE",
       "symptom_name": "vomiting", 
       "severity": "moderate",
       "description": "Threw up twice this morning",
       "observed_at": "2025-11-30T08:30:00Z",
       "duration_hours": 2
     }'

# Get all symptoms for a pet
curl -X GET "http://localhost:8000/api/v1/symptoms/pet/PET_ID_HERE" \
     -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 4. **AI-Powered Symptom Assessment**
```bash
# Create comprehensive AI assessment (analyzes all existing symptoms for pet)
curl -X POST "http://localhost:8000/api/v1/symptoms/assess" \
     -H "Authorization: Bearer YOUR_TOKEN_HERE" \
     -H "Content-Type: application/json" \
     -d '{
       "pet_id": "PET_ID_HERE"
     }'

# Get AI assessment results
curl -X GET "http://localhost:8000/api/v1/symptoms/assessments/pet/PET_ID_HERE" \
     -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 5. **Veterinary Clinic Integration**
```bash
# Sync single pet with external vet system
curl -X POST "http://localhost:8000/api/v1/pets/PET_ID_HERE/sync" \
     -H "Authorization: Bearer YOUR_TOKEN_HERE" \
     -H "Content-Type: application/json" \
     -d '{"vet_clinic_id": "clinic_123", "include_assessments": true}'

# Sync all pets with vet system  
curl -X POST "http://localhost:8000/api/v1/pets/sync-all" \
     -H "Authorization: Bearer YOUR_TOKEN_HERE" \
     -H "Content-Type: application/json" \
     -d '{"vet_clinic_id": "clinic_123"}'
```

## � **Data Models & Response Formats**

### **User Model**
```json
{
  "id": "uuid-string",
  "email": "user@example.com", 
  "username": "optional-username",
  "is_active": true,
  "is_verified": false,
  "created_at": "2025-11-30T12:00:00Z",
  "updated_at": "2025-11-30T12:00:00Z"
}
```

### **Pet Model** 
```json
{
  "id": "uuid-string",
  "user_id": "user-uuid",
  "name": "Buddy",
  "species": "dog", 
  "breed": "Golden Retriever",
  "age_years": 3,
  "weight_kg": 25.5,
  "sex": "male",
  "neutered": true,
  "created_at": "2025-11-30T12:00:00Z",
  "updated_at": "2025-11-30T12:00:00Z"
}
```

### **Pet with Symptoms & Assessments**
```json
{
  "id": "uuid-string",
  "name": "Buddy",
  "species": "dog",
  "breed": "Golden Retriever", 
  "symptoms": [
    {
      "id": "symptom-uuid",
      "symptom_name": "vomiting",
      "severity": "moderate",
      "observed_at": "2025-11-30T08:30:00Z",
      "duration_hours": 2
    }
  ],
  "assessments": [
    {
      "id": "assessment-uuid", 
      "urgency_level": "medium",
      "ai_analysis": "Based on symptoms...",
      "recommendations": "Monitor closely; contact vet if worsens",
      "created_at": "2025-11-30T09:00:00Z"
    }
  ]
}
```

### **AI Assessment Response**
```json
{
  "id": "assessment-uuid",
  "pet_id": "pet-uuid", 
  "symptoms_json": [...],
  "ai_analysis": "Based on the analysis of 2 reported symptoms: lethargy, loss of appetite. These symptoms suggest a condition that should be monitored and may require veterinary consultation.",
  "urgency_level": "moderate",
  "recommendations": "Monitor symptoms for 24-48 hours; Schedule routine veterinary appointment if symptoms persist; Ensure pet is comfortable and well-hydrated",
  "possible_causes": ["dietary indiscretion", "stress", "minor illness"],
  "ai_provider": "ollama",
  "processing_time_ms": 24500,
  "created_at": "2025-11-30T09:00:00Z"
}
```

### **Urgency Levels**
- **`emergency`**: Immediate veterinary attention required
- **`high`**: Veterinary consultation within 24 hours
- **`moderate`**: Monitor closely, vet consultation recommended
- **`low`**: Continue monitoring, routine care sufficient

## �🔧 **Development**

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

- **Local LLM**: Ollama with Llama 3.2 (1b or 3b variants) for symptom analysis
- **Privacy-First**: All AI processing happens locally
- **Conservative Approach**: Provides cautious recommendations with disclaimers
- **Fallback Support**: Graceful degradation when AI service unavailable
- **Data Export**: Full GDPR-compliant user data export functionality

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
   docker compose exec ollama ollama pull llama3.2:3b  # or llama3.2:1b
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
AI_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b  # Options: llama3.2:3b (more accurate) or llama3.2:1b (faster)

# Features
DEBUG=true
RATE_LIMIT_ENABLED=true
```