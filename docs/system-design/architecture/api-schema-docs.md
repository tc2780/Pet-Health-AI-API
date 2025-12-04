# Pet Health API - OpenAPI Specification

## Overview
RESTful API for pet health management with AI-powered symptom analysis using local Ollama LLM processing.

**Base URL**: `http://localhost:8000/api/v1` (development)  
**Authentication**: Bearer JWT tokens  
**OpenAPI Docs**: `http://localhost:8000/docs`  
**Current Version**: 1.0.0

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
  "pet_id": "456e7890-e89b-12d3-a456-426614174001",
  "symptoms": [
    {
      "pet_id": "456e7890-e89b-12d3-a456-426614174001",
      "symptom_name": "lethargy",
      "severity": "moderate",
      "description": "Pet seems unusually tired",
      "observed_at": "2025-12-04T14:30:00Z",
      "duration_hours": 6
    },
    {
      "pet_id": "456e7890-e89b-12d3-a456-426614174001",
      "symptom_name": "loss of appetite",
      "severity": "mild",
      "description": "Eating less than usual",
      "observed_at": "2025-12-04T14:00:00Z",
      "duration_hours": 12
    }
  ]
}

Response (200):
{
  "id": "abc0123-e89b-12d3-a456-426614174003",
  "pet_id": "456e7890-e89b-12d3-a456-426614174001",
  "symptoms_json": [...],
  "urgency_level": "moderate",
  "analysis": "Based on the symptoms of lethargy and loss of appetite, your Golden Retriever may be experiencing a mild illness or stress. These symptoms can indicate various conditions ranging from minor digestive upset to more serious health issues.",
  "recommendations": "Monitor your pet closely for the next 24-48 hours. Ensure they have access to fresh water. If symptoms worsen or persist beyond 48 hours, consult with your veterinarian. Watch for additional symptoms like vomiting, diarrhea, or unusual behavior.",
  "possible_causes": ["dietary indiscretion", "stress", "minor viral infection", "change in routine"],
  "ai_provider": "ollama",
  "processing_time_ms": 2450,
  "created_at": "2025-12-04T15:00:00Z"
}
```

### Get Pet Assessments
```yaml
GET /api/v1/symptoms/assessments/pet/{pet_id}
Authorization: Bearer {access_token}

Response (200):
[
  {
    "id": "abc0123-e89b-12d3-a456-426614174003",
    "pet_id": "456e7890-e89b-12d3-a456-426614174001",
    "urgency_level": "moderate",
    "analysis": "Based on the symptoms...",
    "recommendations": "Monitor your pet closely...",
    "possible_causes": ["dietary indiscretion", "stress"],
    "ai_provider": "ollama",
    "created_at": "2025-12-04T15:00:00Z"
  }
]
```

### Get All User Pet Assessments
```yaml
GET /api/v1/symptoms/assessments/my-pets
Authorization: Bearer {access_token}

Response (200):
[
  {
    "id": "abc0123-e89b-12d3-a456-426614174003",
    "pet_id": "456e7890-e89b-12d3-a456-426614174001",
    "urgency_level": "moderate",
    "analysis": "Based on the symptoms...",
    "recommendations": "Monitor your pet closely...",
    "possible_causes": ["dietary indiscretion", "stress"],
    "ai_provider": "ollama",
    "created_at": "2025-12-04T15:00:00Z"
  }
]
```

### Get Specific Assessment
```yaml
GET /api/v1/symptoms/assessments/{assessment_id}
Authorization: Bearer {access_token}

Response (200):
{
  "id": "abc0123-e89b-12d3-a456-426614174003",
  "pet_id": "456e7890-e89b-12d3-a456-426614174001",
  "symptoms_json": [...],
  "urgency_level": "moderate",
  "analysis": "Based on the symptoms of lethargy and loss of appetite...",
  "recommendations": "Monitor your pet closely for the next 24-48 hours...",
  "possible_causes": ["dietary indiscretion", "stress", "minor viral infection"],
  "ai_provider": "ollama",
  "processing_time_ms": 2450,
  "created_at": "2025-12-04T15:00:00Z"
}
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

### Urgency Levels
- **`emergency`**: Life-threatening symptoms requiring immediate veterinary attention
- **`high`**: Serious symptoms requiring veterinary consultation within 24 hours  
- **`moderate`**: Concerning symptoms that should be monitored closely, veterinary consultation recommended
- **`low`**: Mild symptoms that can be monitored at home with routine veterinary care

### AI Provider Integration
- **Local Processing**: Ollama with Llama 3.2:3b model for privacy-first analysis
- **Fallback Handling**: Graceful degradation when AI service unavailable
- **Response Structure**: Standardized JSON format with medical disclaimers
- **Conservative Approach**: Always errs on the side of caution with veterinary referrals

### Medical Ethics & Disclaimers
All AI responses include appropriate medical disclaimers and emphasize the importance of professional veterinary care for accurate diagnosis and treatment.

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

**Last Updated**: December 4, 2025  
**API Version**: 1.0.0  
**OpenAPI Spec**: Available at `/docs` endpoint