# Pet Health AI API

**Team Members**: aria231, tc2780  
**Project**: AI-powered pet health monitoring and symptom assessment system

## 🌟 Overview

Many pet owners struggle to assess their pet's health symptoms and determine when veterinary care is needed, often leading to delayed treatment or unnecessary emergency visits. This system bridges that gap by providing instant, privacy-preserving AI-powered health assessments.

A comprehensive pet health management system featuring local AI-powered symptom analysis, user management, and veterinary integration. Built with privacy-first design using FastAPI, PostgreSQL, Redis, and local Ollama LLM processing to deliver immediate health insights without compromising pet owner privacy.

### Key Features
- 🤖 **Privacy-First AI**: Local llama3.2:3b model for pet health assessments
- 🔒 **Secure Authentication**: JWT-based user management with GDPR compliance
- 🐾 **Pet Management**: Complete pet profile and symptom tracking
- 📊 **Comprehensive Monitoring**: Prometheus and Grafana observability stack
- 🧪 **Extensive Testing**: 187 automated tests with 97% success rate
- 📋 **Compliance Framework**: 31 privacy and ethics compliance tests  

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose V2 installed
- 8GB RAM (recommended for optimal AI performance)
- 10GB free disk space (5GB for AI model)

### Method 1: One-Command Start (Recommended)

```bash
# Quick start script handles everything
./start.sh
```

### Method 2: Manual Setup

1. **Start all services**:
   ```bash
   docker compose up -d
   ```

2. **Download the AI model** (first time only):
   ```bash
   # Production model (recommended - 3GB download)
   docker compose exec ollama ollama pull llama3.2:3b
   
   # Alternative: Smaller model (if resources are limited)
   docker compose exec ollama ollama pull llama3.2:1b
   ```

3. **Verify everything is running**:
   ```bash
   docker compose ps
   ```

4. **Access the application**:
   - 📖 **API Documentation**: http://localhost:8000/docs (interactive Swagger UI)
   - ❤️ **Health Check**: http://localhost:8000/health
   - 🌐 **API Base URL**: http://localhost:8000/api/v1/

### Frontend Setup (Demonstration in Action)

The project includes a React-based frontend for interactive pet health management:

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   pnpm install
   ```

3. **Start development server**:
   ```bash
   pnpm dev
   ```

4. **Access the frontend**:
   - 🌐 **Frontend Application**: http://localhost:8080
   - The frontend automatically connects to the backend API at http://localhost:8000
        - Please make sure the backend is running before using the frontend.
   - Use the interactive UI to register, add pets, log symptoms, and get AI assessments.

### 🎮 Simple Interactive Demo

Run comprehensive demo scripts to test all functionality:

```bash
# Interactive demo menu with 4 options
docker compose exec api python demo_scripts/run_demo.py
# 1. 🔌 Ollama Connectivity Test (~5 seconds)
# 2. 🏥 AI Veterinary Analysis Demo (~30-60 seconds)
# 3. 🔧 Service Integration Test (~20-40 seconds)
# 4. 🔄 End-to-End Workflow Test (~10-20 seconds)

# Individual demo scripts
docker compose exec api python demo_scripts/ai_veterinary_demo.py
docker compose exec api python demo_scripts/end_to_end_workflow_test.py
docker compose exec api python demo_scripts/ollama_direct_test.py
```

**Model Selection**: Add model argument for testing (`3b` for accuracy, `1b` for speed):
```bash
docker compose exec api python demo_scripts/ai_veterinary_demo.py 3b
```

### 🧪 Testing

Comprehensive test suite with Docker-based infrastructure:

```bash
# Run all tests with detailed reporting
./run-docker-tests.sh all

# Run specific test categories
./run-docker-tests.sh standard      # Unit, integration, AI, compliance (166/171 passing)
./run-docker-tests.sh performance   # Load and stress testing (7/9 passing)  
./run-docker-tests.sh chaos         # Chaos engineering tests

# Manual test execution
docker compose up -d
docker compose exec api python -m pytest tests/ -v

# Individual test suites
docker compose exec api python -m pytest tests/unit/ -v           # Unit tests
docker compose exec api python -m pytest tests/integration/ -v    # Integration tests
docker compose exec api python -m pytest tests/ai/ -v             # AI functionality
docker compose exec api python -m pytest tests/clause_control_tests/ -v  # Compliance
```

**Test Coverage Summary:**
- ✅ **Total Tests**: 187 automated tests
- ✅ **Success Rate**: 97% (181/187 passing)
- ✅ **Unit Tests**: Core business logic validation
- ✅ **Integration Tests**: End-to-end API workflows
- ✅ **AI Tests**: LLM integration and assessment quality
- ✅ **Compliance Tests**: 31 privacy and ethics validations
- ✅ **Performance Tests**: Load testing and stress scenarios

### 🛑 Stop Services

```bash
# Stop all services
docker compose down

# Stop and remove all data (complete reset)
docker compose down -v
```

## 🏗️ System Architecture

### Core Services
- **🌐 FastAPI Application**: Async Python web framework (http://localhost:8000)
- **🗄️ PostgreSQL Database**: Primary data store (localhost:5432)
- **⚡ Redis Cache**: Session and data caching (localhost:6379)  
- **🤖 Ollama AI Service**: Local LLM processing (http://localhost:11434)

### Monitoring & Observability (Optional)
- **📊 Prometheus**: Metrics collection (http://localhost:9090)
- **📈 Grafana Dashboard**: Data visualization (http://localhost:3000, admin/admin)

### Start Monitoring Stack
```bash
# Start monitoring services
docker compose up -d prometheus grafana

# Access dashboards
open http://localhost:3000  # Grafana (admin/admin)
open http://localhost:9090  # Prometheus
```

## 📋 API Reference

### 🔐 Authentication & User Management
- **User Registration**: `POST /api/v1/auth/register`
- **User Login**: `POST /api/v1/auth/login`
- **Get Current User**: `GET /api/v1/auth/me`
- **Update Profile**: `PUT /api/v1/users/me`
- **Delete Account**: `DELETE /api/v1/users/me`
- **Export User Data**: `GET /api/v1/users/me/export` (GDPR compliance)

### 🐾 Pet Management
- **Create Pet**: `POST /api/v1/pets/`
- **List User's Pets**: `GET /api/v1/pets/`
- **Get Pet Details**: `GET /api/v1/pets/{pet_id}`
- **Update Pet Info**: `PUT /api/v1/pets/{pet_id}`
- **Delete Pet**: `DELETE /api/v1/pets/{pet_id}`

### 🩺 Symptom Tracking & AI Analysis
- **Record Symptoms**: `POST /api/v1/symptoms/`
- **Get Pet Symptoms**: `GET /api/v1/symptoms/pet/{pet_id}`
- **Get All User Pet Symptoms**: `GET /api/v1/symptoms/my-pets`
- **Update Symptom**: `PUT /api/v1/symptoms/{symptom_id}`
- **Delete Symptom**: `DELETE /api/v1/symptoms/{symptom_id}`

### 🤖 AI-Powered Health Assessment
- **Create AI Assessment**: `POST /api/v1/symptoms/assess` (analyzes all symptoms for a pet)
- **Get Pet Assessments**: `GET /api/v1/symptoms/assessments/pet/{pet_id}`
- **Get All User Assessments**: `GET /api/v1/symptoms/assessments/my-pets`
- **Get Specific Assessment**: `GET /api/v1/symptoms/assessments/{assessment_id}`

### 🏥 Veterinary Integration (Mock)
- **Sync Single Pet**: `POST /api/v1/pets/{pet_id}/sync`
- **Sync All User Pets**: `POST /api/v1/pets/sync-all`

### ❤️ System Health
- **Health Check**: `GET /health`
- **API Root**: `GET /`

## 🔧 AI Assessment Features

### Model Specifications
- **Model**: Meta Llama 3.2 3B Instruct
- **Local Processing**: Complete privacy - no data leaves your system
- **Response Time**: 15-45 seconds for full assessment
- **Medical Disclaimers**: Automatic inclusion in all AI responses

### Assessment Input
```json
{
  "pet_id": "uuid-string"
}
```

### Assessment Output  
```json
{
  "assessment_id": "uuid-string",
  "urgency_level": "low|moderate|high|emergency",
  "analysis": "Detailed AI assessment with medical disclaimer",
  "recommendations": ["action1", "action2"],
  "possible_causes": ["cause1", "cause2"],
  "ai_provider": "ollama",
  "ai_model": "llama3.2:3b",
  "processing_time_ms": 24500,
  "created_at": "2025-12-05T15:00:00Z"
}
```

## 🎭 Live Demo Experience

### Interactive Features

1. **Immediate AI Response**: The application uses a local AI model that provides instant feedback
2. **Real-Time Symptom Tracking**: Add multiple symptoms and see how AI assessment updates
3. **Progressive Disclosure**: Start with basic pet info, add symptoms, get detailed AI analysis
4. **Privacy First**: All AI processing happens locally - no data sent to external services

### Demo Workflow

1. **User Registration** → Create account with email/password
2. **Pet Profile Creation** → Add pet details (name, species, breed, age)
3. **Symptom Documentation** → Record observed symptoms with descriptions
4. **AI Assessment** → Get instant analysis with urgency levels and recommendations
5. **Historical Tracking** → View past assessments and symptom progression

### Expected AI Response Format

```json
{
  "urgency_level": "moderate",
  "analysis": "Based on the reported symptoms of lethargy and decreased appetite in a 3-year-old Golden Retriever, several potential causes should be considered...",
  "recommendations": [
    "Monitor temperature and hydration",
    "Provide easily digestible food",
    "Consult veterinarian if symptoms persist beyond 24 hours"
  ],
  "possible_causes": [
    "Minor gastrointestinal upset",
    "Stress or environmental changes",
    "Early signs of infection"
  ],
  "medical_disclaimer": "This assessment is for informational purposes only and does not replace professional veterinary care."
}
```

## 🏥 Veterinary Integration (Mock)

This project includes a mock vet clinic sync service and API endpoints to demonstrate how pet data can be synchronized with external veterinary partners:

- `POST /api/v1/pets/{pet_id}/sync` — sync a single pet's data (mock)
- `POST /api/v1/pets/sync-all` — sync all pets for the authenticated user (mock)

When running with `docker compose`, the `api` service exposes `VET_SYNC_MOCK=true` to enable the mock sync behavior by default. Replace the mock implementation in `backend/app/services/vet_sync.py` with a real integration when ready.

## 📚 Documentation & Compliance

### Architecture Documentation
- **[Architecture Overview](docs/system-design/architecture/architecture_diagram.md)**: Complete system architecture with service interactions
- **[API Schema Documentation](docs/system-design/architecture/api-schema-docs.md)**: Detailed API specifications and data models
- **[ADR 001](docs/system-design/adrs/ADR-001-fastapi-framework.md)**: FastAPI framework selection rationale
- **[ADR 002](docs/system-design/adrs/ADR-002-local-llm-choice.md)**: Local LLM implementation decision
- **[ADR 003](docs/system-design/adrs/ADR-003-postgresql-database.md)**: PostgreSQL database choice

### Compliance & Ethics Framework
- **[Ethics Framework](docs/compliance/ethics-framework.md)**: AI ethics guidelines and implementation
- **[Trust Model](docs/compliance/trust-model.md)**: Security architecture and data protection
- **[Clause Control Testing](docs/compliance/clause-control-test.md)**: Compliance verification procedures
- **[Ethics Debt Ledger](docs/compliance/ethics_debt_ledger.md)**: AI ethics tracking and technical debt

### Operations & Deployment
- **[Deployment Instructions](docs/operations/deployment-instructions.md)**: Production deployment guidelines
- **[Cost & Operability Analysis](docs/operations/cost-operability.md)**: Resource planning and monitoring
- **[Testing & Reliability](docs/testing/reliability-testing.md)**: Comprehensive testing strategy

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make changes with appropriate tests
4. Ensure all tests pass: `./run-docker-tests.sh all`
5. Submit a pull request

### Code Standards
- **Python**: Follow PEP 8, use type hints
- **API**: RESTful design principles
- **Testing**: Minimum 90% coverage
- **Documentation**: Update relevant docs with changes

## 📄 License

This project is part of academic coursework (CPSC 436C) and is available for educational use.
