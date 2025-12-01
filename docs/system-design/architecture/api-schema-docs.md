# Pet Health API - OpenAPI Specification

## Overview
RESTful API for pet health management with AI-powered symptom analysis.

**Base URL**: `https://api.pethealth.com/v1`
**Authentication**: Bearer JWT tokens

## Authentication

### Register User
```yaml
POST /auth/register
Content-Type: application/json

Request:
{
  "email": "user@example.com",
  "password": "securePassword123",
  "first_name": "John",
  "last_name": "Doe"
}

Response (201):
{
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "user@example.com",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### Login
```yaml
POST /auth/login
Content-Type: application/json

Request:
{
  "email": "user@example.com",
  "password": "securePassword123"
}

Response (200):
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

## Pet Management

### Create Pet
```yaml
POST /pets
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

Response (201):
{
  "id": "456e7890-e89b-12d3-a456-426614174001",
  "name": "Buddy",
  "species": "dog",
  "breed": "Golden Retriever",
  "age_years": 5,
  "weight_kg": 30.5,
  "sex": "male",
  "neutered": true,
  "created_at": "2025-11-30T10:30:00Z"
}
```

### Get User's Pets
```yaml
GET /pets
Authorization: Bearer {access_token}

Response (200):
{
  "pets": [
    {
      "id": "456e7890-e89b-12d3-a456-426614174001",
      "name": "Buddy",
      "species": "dog",
      "breed": "Golden Retriever",
      "age_years": 5,
      "created_at": "2025-11-30T10:30:00Z"
    }
  ],
  "total": 1
}
```

### Get Pet Details
```yaml
GET /pets/{pet_id}
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
  "created_at": "2025-11-30T10:30:00Z",
  "recent_symptoms_count": 3
}
```

## Symptom Tracking

### Log Symptom
```yaml
POST /symptoms/{pet_id}/symptoms
Authorization: Bearer {access_token}
Content-Type: application/json

Request:
{
  "symptom_name": "lethargy",
  "severity": "moderate",
  "description": "Pet seems unusually tired and less active than normal",
  "observed_at": "2025-11-30T14:30:00Z",
  "duration_hours": 6
}

Response (201):
{
  "id": "789e0123-e89b-12d3-a456-426614174002",
  "pet_id": "456e7890-e89b-12d3-a456-426614174001",
  "symptom_name": "lethargy",
  "severity": "moderate",
  "description": "Pet seems unusually tired and less active than normal",
  "observed_at": "2025-11-30T14:30:00Z",
  "duration_hours": 6,
  "created_at": "2025-11-30T15:00:00Z"
}
```

### Get Symptoms by Time Frame
```yaml
GET /symptoms/{pet_id}/symptoms?days_back=7
Authorization: Bearer {access_token}

Query Parameters:
- days_back: integer (optional, default: 30) - Number of days to look back
- start_date: ISO 8601 date (optional) - Start of date range
- end_date: ISO 8601 date (optional) - End of date range

Response (200):
{
  "symptoms": [
    {
      "id": "789e0123-e89b-12d3-a456-426614174002",
      "symptom_name": "lethargy",
      "severity": "moderate",
      "description": "Pet seems unusually tired",
      "observed_at": "2025-11-30T14:30:00Z",
      "duration_hours": 6,
      "created_at": "2025-11-30T15:00:00Z"
    }
  ],
  "total": 1,
  "date_range": {
    "start": "2025-11-30T00:00:00Z",
    "end": "2025-11-30T23:59:59Z"
  }
}
```

### Get Full Symptom History
```yaml
GET /symptoms/{pet_id}/symptoms/history
Authorization: Bearer {access_token}

Response (200):
{
  "symptoms": [
    {
      "id": "789e0123-e89b-12d3-a456-426614174002",
      "symptom_name": "lethargy",
      "severity": "moderate",
      "observed_at": "2025-11-30T14:30:00Z",
      "duration_hours": 6
    }
  ],
  "total": 1,
  "oldest_symptom": "2025-11-30T10:00:00Z",
  "newest_symptom": "2025-11-30T14:30:00Z"
}
```

## AI Veterinary Assessment

### Request AI Assessment
```yaml
POST /ai-vet/{pet_id}/assess
Authorization: Bearer {access_token}
Content-Type: application/json

Request:
{
  "include_recent_symptoms": true,
  "additional_context": "Pet ate new food yesterday",
  "current_symptoms": [
    {
      "symptom_name": "vomiting",
      "severity": "mild",
      "description": "Vomited twice this morning",
      "observed_at": "2025-11-30T08:00:00Z",
      "duration_hours": 2
    }
  ]
}

Response (200):
{
  "assessment_id": "abc12345-e89b-12d3-a456-426614174003",
  "pet_id": "456e7890-e89b-12d3-a456-426614174001",
  "urgency_level": "moderate",
  "possible_causes": [
    "Dietary indiscretion (eating new or inappropriate food)",
    "Gastric upset from stress or environmental changes",
    "Mild food allergy or sensitivity",
    "Early stages of viral gastroenteritis"
  ],
  "recommendations": [
    "Withhold food for 12-24 hours but ensure water access",
    "Monitor for additional symptoms like diarrhea or lethargy",
    "Gradually reintroduce bland diet (rice and boiled chicken)",
    "Keep pet comfortable and watch for dehydration signs"
  ],
  "when_to_see_vet": "If vomiting continues beyond 24 hours, if pet becomes lethargic, refuses water, or shows signs of dehydration",
  "monitoring_instructions": [
    "Track frequency and volume of vomiting episodes",
    "Monitor water intake and urination patterns",
    "Check gum color and skin elasticity for dehydration",
    "Note any changes in behavior or energy levels"
  ],
  "created_at": "2025-11-30T16:00:00Z",
  "disclaimer": "This AI assessment is for educational purposes only. Always consult a licensed veterinarian for medical concerns."
}
```

### Get Assessment History
```yaml
GET /ai-vet/{pet_id}/assessments
Authorization: Bearer {access_token}

Query Parameters:
- limit: integer (optional, default: 10) - Number of assessments to return
- offset: integer (optional, default: 0) - Pagination offset

Response (200):
{
  "assessments": [
    {
      "assessment_id": "abc12345-e89b-12d3-a456-426614174003",
      "urgency_level": "moderate",
      "symptoms_analyzed": ["vomiting", "lethargy"],
      "created_at": "2025-11-30T16:00:00Z"
    }
  ],
  "total": 1,
  "has_more": false
}
```

### Get Specific Assessment
```yaml
GET /ai-vet/assessments/{assessment_id}
Authorization: Bearer {access_token}

Response (200):
{
  "assessment_id": "abc12345-e89b-12d3-a456-426614174003",
  "pet_id": "456e7890-e89b-12d3-a456-426614174001",
  "urgency_level": "moderate",
  "possible_causes": [...],
  "recommendations": [...],
  "when_to_see_vet": "...",
  "monitoring_instructions": [...],
  "symptoms_analyzed": [
    {
      "symptom_name": "vomiting",
      "severity": "mild",
      "observed_at": "2025-11-30T08:00:00Z"
    }
  ],
  "created_at": "2025-11-30T16:00:00Z"
}
```

## System Endpoints

### Health Check
```yaml
GET /health

Response (200):
{
  "status": "healthy",
  "services": {
    "database": "healthy",
    "redis": "healthy",
    "ai_service": "healthy"
  },
  "timestamp": "2025-11-30T16:30:00Z",
  "version": "1.0.0"
}
```

### API Metrics
```yaml
GET /metrics
Authorization: Bearer {access_token}

Response (200):
# Prometheus format metrics
pet_health_api_requests_total{method="GET",endpoint="/pets",status="200"} 1245
pet_health_api_response_time_seconds{endpoint="/ai-vet/{pet_id}/assess"} 2.3
pet_health_ai_assessments_total{urgency="moderate"} 234
```

## Error Responses

### Standard Error Format
```yaml
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": [
      {
        "field": "severity",
        "message": "Must be one of: mild, moderate, severe"
      }
    ],
    "timestamp": "2025-11-30T16:45:00Z",
    "request_id": "req_123456789"
  }
}
```

### Common Error Codes
```yaml
Error Codes:
  400: BAD_REQUEST - Invalid request format or parameters
  401: UNAUTHORIZED - Missing or invalid authentication
  403: FORBIDDEN - Access denied to resource
  404: NOT_FOUND - Resource not found
  422: VALIDATION_ERROR - Request validation failed
  429: RATE_LIMIT_EXCEEDED - Too many requests
  500: INTERNAL_ERROR - Server error
  503: SERVICE_UNAVAILABLE - AI service temporarily unavailable
```

## Rate Limiting

```yaml
Rate Limits:
  - Authentication endpoints: 5 requests/minute per IP
  - Pet management: 60 requests/minute per user
  - Symptom tracking: 30 requests/minute per user
  - AI assessments: 10 requests/minute per user
  
Headers:
  X-RateLimit-Limit: Maximum requests per window
  X-RateLimit-Remaining: Requests remaining in current window
  X-RateLimit-Reset: Unix timestamp when limit resets
```

## Data Models

### Pet Schema
```yaml
Pet:
  id: string (UUID)
  name: string (max: 100)
  species: string (enum: dog, cat, rabbit, bird, other)
  breed: string (optional, max: 100)
  age_years: integer (optional, min: 0, max: 30)
  weight_kg: number (optional, min: 0.1, max: 200)
  sex: string (optional, enum: male, female, unknown)
  neutered: boolean (default: false)
  created_at: datetime
```

### Symptom Schema
```yaml
Symptom:
  id: string (UUID)
  pet_id: string (UUID, foreign key)
  symptom_name: string (max: 100)
  severity: string (enum: mild, moderate, severe)
  description: string (optional, max: 1000)
  observed_at: datetime
  duration_hours: integer (optional, min: 0)
  created_at: datetime
```

This API specification provides a complete interface for pet health management with AI-powered veterinary guidance.