# Pet Health API - OpenAPI Specification

## Overview
RESTful API for pet health management with AI-powered symptom analysis using local Ollama llama3.2:3b model processing.

**Base URL**: `http://localhost:8000/api/v1` (development)  
**Authentication**: Bearer JWT tokens  
**OpenAPI Docs**: `http://localhost:8000/docs`  
**Current Version**: 1.0.0  
**AI Model**: Ollama llama3.2:3b (local processing)  
**Docker Environment**: Docker Compose with FastAPI, PostgreSQL, Redis, Ollama

## Architecture Overview
- **FastAPI**: Async Python web framework
- **PostgreSQL**: Primary database with persistent volumes
- **Redis**: Caching and session management
- **Ollama**: Local LLM processing with llama3.2:3b model
- **Docker Compose**: Containerized development and deployment

## Authentication Endpoints

### Register User
```yaml
POST /api/v1/auth/register
Content-Type: application/json

Request:
{
  "email": "user@example.com",
  "password": "securePassword123"
}

Response (200):
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "user@example.com",
  "username": null,
  "is_active": true,
  "is_verified": false,
  "created_at": "2025-12-04T10:30:00Z",
  "updated_at": "2025-12-04T10:30:00Z"
}
```

### Login
```yaml
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded

Request:
username=user@example.com&password=securePassword123

Response (200):
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Get Current User
```yaml
GET /api/v1/auth/me
Authorization: Bearer {access_token}

Response (200):
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "user@example.com",
  "username": "petlover123",
  "is_active": true,
  "is_verified": false,
  "created_at": "2025-12-04T10:30:00Z",
  "updated_at": "2025-12-04T10:30:00Z"
}
```

## User Management Endpoints

### Get User Profile
```yaml
GET /api/v1/users/me
Authorization: Bearer {access_token}

Response (200):
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "user@example.com",
  "username": "petlover123",
  "is_active": true,
  "is_verified": false,
  "created_at": "2025-12-04T10:30:00Z",
  "updated_at": "2025-12-04T10:30:00Z"
}
```

### Update User Profile
```yaml
PUT /api/v1/users/me
Authorization: Bearer {access_token}
Content-Type: application/json

Request:
{
  "username": "newusername",
  "email": "newemail@example.com",
  "password": "newPassword123"  // optional
}

Response (200):
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "newemail@example.com",
  "username": "newusername",
  "is_active": true,
  "is_verified": false,
  "created_at": "2025-12-04T10:30:00Z",
  "updated_at": "2025-12-04T11:00:00Z"
}
```

### Delete User Account
```yaml
DELETE /api/v1/users/me
Authorization: Bearer {access_token}

Response (200):
{
  "message": "User account successfully deleted"
}
```

### Export User Data (GDPR Compliance)
```yaml
GET /api/v1/users/me/export
Authorization: Bearer {access_token}

Response (200):
{
  "export_timestamp": "2025-12-04T11:00:00Z",
  "user_profile": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "user@example.com",
    "username": "petlover123",
    "created_at": "2025-12-04T10:30:00Z",
    "is_active": true,
    "is_verified": false
  },
  "pets": [...],
  "symptoms": [...],
  "assessments": [...],
  "data_summary": {
    "total_pets": 2,
    "total_symptoms": 5,
    "total_assessments": 3
  }
}
```

## Pet Management Endpoints

### Create Pet
```yaml
POST /api/v1/pets/
Authorization: Bearer {access_token}
Content-Type: application/json

Request:
{
  "name": "Buddy",
  "species": "dog",
  "breed": "Golden Retriever",
  "age_years": 5,
  "weight_kg": 30.5,
  "sex": "male",
  "neutered": true
}

Response (200):
{
  "id": "456e7890-e89b-12d3-a456-426614174001",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "name": "Buddy",
  "species": "dog",
  "breed": "Golden Retriever",
  "age_years": 5,
  "weight_kg": 30.5,
  "sex": "male",
  "neutered": true,
  "created_at": "2025-12-04T10:30:00Z",
  "updated_at": "2025-12-04T10:30:00Z"
}
```

### Get User's Pets
```yaml
GET /api/v1/pets/
Authorization: Bearer {access_token}

Response (200):
[
  {
    "id": "456e7890-e89b-12d3-a456-426614174001",
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "name": "Buddy",
    "species": "dog",
    "breed": "Golden Retriever",
    "age_years": 5,
    "weight_kg": 30.5,
    "sex": "male",
    "neutered": true,
    "created_at": "2025-12-04T10:30:00Z",
    "updated_at": "2025-12-04T10:30:00Z"
  }
]
```

### Get Pet Details
```yaml
GET /api/v1/pets/{pet_id}
Authorization: Bearer {access_token}

Response (200):
{
  "id": "456e7890-e89b-12d3-a456-426614174001",
  "name": "Buddy",
  "species": "dog",
  "breed": "Golden Retriever",
  "age_years": 5,
  "weight_kg": 30.5,
  "sex": "male",
  "neutered": true,
  "created_at": "2025-12-04T10:30:00Z",
  "updated_at": "2025-12-04T10:30:00Z",
  "symptoms": [...],
  "assessments": [...]
}
```

### Update Pet
```yaml
PUT /api/v1/pets/{pet_id}
Authorization: Bearer {access_token}
Content-Type: application/json

Request:
{
  "weight_kg": 32.0,
  "age_years": 6
}

Response (200):
{
  "id": "456e7890-e89b-12d3-a456-426614174001",
  "name": "Buddy",
  "species": "dog",
  "breed": "Golden Retriever",
  "age_years": 6,
  "weight_kg": 32.0,
  "sex": "male",
  "neutered": true,
  "created_at": "2025-12-04T10:30:00Z",
  "updated_at": "2025-12-04T11:00:00Z"
}
```

### Delete Pet
```yaml
DELETE /api/v1/pets/{pet_id}
Authorization: Bearer {access_token}

Response (200):
{
  "message": "Pet deleted successfully"
}
```

## Veterinary Sync Endpoints (Mock)

### Sync Single Pet
```yaml
POST /api/v1/pets/{pet_id}/sync
Authorization: Bearer {access_token}
Content-Type: application/json

Request:
{
  "vet_clinic_id": "clinic_001",
  "include_assessments": true
}

Response (200):
{
  "success": true,
  "clinic_id": "mock-clinic-001",
  "synced_at": "2025-12-04T11:00:00Z",
  "payload_summary": {
    "pet_id": "456e7890-e89b-12d3-a456-426614174001",
    "name": "Buddy",
    "species": "dog",
    "age_years": 5,
    "symptoms_count": 2
  }
}
```

### Sync All User Pets
```yaml
POST /api/v1/pets/sync-all
Authorization: Bearer {access_token}

Response (200):
[
  {
    "pet_id": "456e7890-e89b-12d3-a456-426614174001",
    "synced": true,
    "synced_at": "2025-12-04T11:00:00Z"
  }
]
```

## Symptom Management Endpoints

### Create Symptom
```yaml
POST /api/v1/symptoms/
Authorization: Bearer {access_token}
Content-Type: application/json

Request:
{
  "pet_id": "456e7890-e89b-12d3-a456-426614174001",
  "symptom_name": "lethargy",
  "severity": "moderate",
  "description": "Pet seems unusually tired and less active than normal",
  "observed_at": "2025-12-04T14:30:00Z",
  "duration_hours": 6
}

Response (200):
{
  "id": "789e0123-e89b-12d3-a456-426614174002",
  "pet_id": "456e7890-e89b-12d3-a456-426614174001",
  "symptom_name": "lethargy",
  "severity": "moderate",
  "description": "Pet seems unusually tired and less active than normal",
  "observed_at": "2025-12-04T14:30:00Z",
  "duration_hours": 6,
  "created_at": "2025-12-04T14:30:00Z"
}
```

### Get Pet Symptoms
```yaml
GET /api/v1/symptoms/pet/{pet_id}
Authorization: Bearer {access_token}

Response (200):
[
  {
    "id": "789e0123-e89b-12d3-a456-426614174002",
    "pet_id": "456e7890-e89b-12d3-a456-426614174001",
    "symptom_name": "lethargy",
    "severity": "moderate",
    "description": "Pet seems unusually tired and less active than normal",
    "observed_at": "2025-12-04T14:30:00Z",
    "duration_hours": 6,
    "created_at": "2025-12-04T14:30:00Z"
  }
]
```

### Get All User Pet Symptoms
```yaml
GET /api/v1/symptoms/my-pets
Authorization: Bearer {access_token}

Response (200):
[
  {
    "id": "789e0123-e89b-12d3-a456-426614174002",
    "pet_id": "456e7890-e89b-12d3-a456-426614174001",
    "symptom_name": "lethargy",
    "severity": "moderate",
    "description": "Pet seems unusually tired and less active than normal",
    "observed_at": "2025-12-04T14:30:00Z",
    "duration_hours": 6,
    "created_at": "2025-12-04T14:30:00Z"
  }
]
```

### Update Symptom
```yaml
PUT /api/v1/symptoms/{symptom_id}
Authorization: Bearer {access_token}
Content-Type: application/json

Request:
{
  "severity": "severe",
  "description": "Pet is now completely inactive"
}

Response (200):
{
  "id": "789e0123-e89b-12d3-a456-426614174002",
  "pet_id": "456e7890-e89b-12d3-a456-426614174001",
  "symptom_name": "lethargy",
  "severity": "severe",
  "description": "Pet is now completely inactive",
  "observed_at": "2025-12-04T14:30:00Z",
  "duration_hours": 6,
  "created_at": "2025-12-04T14:30:00Z"
}
```

### Delete Symptom
```yaml
DELETE /api/v1/symptoms/{symptom_id}
Authorization: Bearer {access_token}

Response (200):
{
  "message": "Symptom deleted successfully"
}
```

## AI-Powered Symptom Assessment Endpoints

### Create AI Assessment
```yaml
POST /api/v1/symptoms/assess
Authorization: Bearer {access_token}
Content-Type: application/json

Request:
{
  "pet_id": "456e7890-e89b-12d3-a456-426614174001"
}

Response (200):
{
  "assessment_id": "abc0123-e89b-12d3-a456-426614174003",
  "pet_id": "456e7890-e89b-12d3-a456-426614174001", 
  "urgency_level": "moderate",
  "analysis": "Based on your Golden Retriever's symptoms, I recommend monitoring closely for changes. Here's my assessment: [Detailed AI analysis follows...] **Medical Disclaimer**: This assessment is not a substitute for professional veterinary care. Please consult with a licensed veterinarian for accurate diagnosis and treatment.",
  "recommendations": [
    "Monitor pet closely for next 24-48 hours",
    "Ensure access to fresh water",
    "Consult veterinarian if symptoms worsen"
  ],
  "possible_causes": ["dietary indiscretion", "stress", "minor viral infection"],
  "confidence_score": 0.78,
  "ai_provider": "ollama",
  "ai_model": "llama3.2:3b", 
  "processing_time_ms": 18500,
  "medical_disclaimer": "This AI assessment is for informational purposes only and should not replace professional veterinary advice.",
  "created_at": "2025-12-05T15:00:00Z"
}
```

```

### Get Specific Assessment
```yaml
GET /api/v1/symptoms/assessments/{assessment_id}
Authorization: Bearer {access_token}

Response (200):
{
  "assessment_id": "abc0123-e89b-12d3-a456-426614174003",
  "pet_id": "456e7890-e89b-12d3-a456-426614174001",
  "urgency_level": "moderate",
  "analysis": "Based on your Golden Retriever's symptoms, detailed analysis...",
  "recommendations": [
    "Monitor pet closely for next 24-48 hours",
    "Ensure access to fresh water"
  ],
  "possible_causes": ["dietary indiscretion", "stress", "minor viral infection"],
  "ai_provider": "ollama",
  "ai_model": "llama3.2:3b",
  "processing_time_ms": 18500,
  "created_at": "2025-12-05T15:00:00Z"
}
```
```

## Health & Utility Endpoints

### Root Endpoint
```yaml
GET /
Response (200):
{
  "message": "Pet Health API v1.0.0",
  "docs": "/docs",
  "health": "/health"
}
```

### Health Check
```yaml
GET /health
Response (200):
{
  "status": "healthy",
  "timestamp": "2025-12-04T15:00:00Z",
  "version": "1.0.0"
}
```

## Data Models

### User Model
```json
{
  "id": "uuid-string",
  "email": "string",
  "username": "string | null",
  "is_active": "boolean",
  "is_verified": "boolean", 
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### Pet Model
```json
{
  "id": "uuid-string",
  "user_id": "uuid-string",
  "name": "string",
  "species": "string",
  "breed": "string | null",
  "age_years": "integer | null",
  "weight_kg": "decimal | null", 
  "sex": "string | null",
  "neutered": "boolean",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### Symptom Model
```json
{
  "id": "uuid-string",
  "pet_id": "uuid-string",
  "symptom_name": "string",
  "severity": "mild | moderate | severe",
  "description": "string | null",
  "observed_at": "datetime",
  "duration_hours": "integer | null",
  "created_at": "datetime"
}
```

### Assessment Model
```json
{
  "id": "uuid-string",
  "pet_id": "uuid-string",
  "symptoms_json": "object",
  "urgency_level": "emergency | high | moderate | low",
  "analysis": "string",
  "recommendations": "string",
  "possible_causes": "array[string] | null",
  "ai_provider": "string | null",
  "processing_time_ms": "integer | null",
  "created_at": "datetime"
}
```

## AI Processing Features

### AI Service Integration
- **Primary Model**: Ollama llama3.2:3b (3GB model size)
- **Local Processing**: All AI inference runs locally via Docker Compose  
- **Privacy-First**: Pet health data never leaves your infrastructure
- **Response Time**: Typically 10-30 seconds for complete assessment
- **Fallback Handling**: Graceful degradation when Ollama service unavailable

### Model Specifications  
- **Model**: Meta Llama 3.2 3B Instruct
- **Quantization**: Optimized for consumer hardware
- **Context Length**: 128k tokens
- **Specialization**: Medical and veterinary domain knowledge

### Urgency Levels
- **`emergency`**: Life-threatening symptoms requiring immediate veterinary attention
- **`high`**: Serious symptoms requiring veterinary consultation within 24 hours  
- **`moderate`**: Concerning symptoms that should be monitored closely, veterinary consultation recommended
- **`low`**: Mild symptoms that can be monitored at home with routine veterinary care

### Conservative Medical Approach
- **Veterinary Referrals**: Always errs on the side of caution
- **Medical Disclaimers**: Automatic inclusion in all AI responses
- **Professional Emphasis**: Consistently recommends veterinary consultation
- **Liability Protection**: Clear limitations of AI assessment capabilities

### Docker Compose Integration
- **Service Discovery**: AI service accessible via `http://ollama:11434`
- **Health Checks**: Automatic model availability monitoring
- **Resource Allocation**: 8GB RAM recommended for optimal performance
- **Network Isolation**: AI processing contained within Docker network

## System Architecture Integration

### Development Environment
```bash
# Start all services
docker compose up -d

# Service URLs
API: http://localhost:8000
Docs: http://localhost:8000/docs  
PostgreSQL: localhost:5432
Redis: localhost:6379
Ollama: localhost:11434

# Health checks
curl http://localhost:8000/health
curl http://localhost:11434/api/tags
```

### Testing Endpoints
```bash
# AI functionality test with actual assessment
curl -X POST http://localhost:8000/api/v1/symptoms/assess \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"pet_id": "your-pet-id"}'

# Health check
curl http://localhost:8000/health

# API documentation
curl http://localhost:8000/docs

# Database connectivity
docker compose exec postgres pg_isready -U petuser

# Redis connectivity  
docker compose exec redis redis-cli ping

# Ollama service check
curl http://localhost:11434/api/tags
```

## Error Responses

### Authentication Errors
```json
// 401 Unauthorized
{
  "detail": "Could not validate credentials"
}

// 403 Forbidden  
{
  "detail": "Not enough permissions"
}
```

### Validation Errors
```json
// 422 Unprocessable Entity
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "email"],
      "msg": "String should have at least 1 character",
      "input": ""
    }
  ]
}
```

### Resource Errors
```json
// 404 Not Found
{
  "detail": "Pet not found"
}

// 400 Bad Request
{
  "detail": "Invalid request parameters"
}
```

## Rate Limiting
- **Default**: 100 requests per minute per user
- **AI Endpoints**: 10 assessments per minute per user  
- **Headers**: `X-RateLimit-Limit`, `X-RateLimit-Remaining`

## CORS Policy
- **Allowed Origins**: Configurable for development/production
- **Allowed Methods**: GET, POST, PUT, DELETE, OPTIONS
- **Allowed Headers**: Authorization, Content-Type, Accept

---

**Last Updated**: December 5, 2025  
**API Version**: 1.0.0  
**Docker Environment**: Docker Compose V2  
**AI Model**: Ollama llama3.2:3b  
**OpenAPI Spec**: Available at `/docs` endpoint