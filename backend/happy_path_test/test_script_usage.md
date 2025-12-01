# Backend Workflow Test Script

## Quick Start

1. **Install the requests library** (if not already installed):
   ```bash
   pip install requests
   ```

2. **Make sure your backend is running**:
   ```bash
   docker compose up -d
   ```

3. **Install the LLM model for AI functionality**:
   ```bash
   # Wait for Ollama service to start (may take 1-2 minutes)
   docker compose logs ollama
   
   # Download the Llama 3.1 model (this will take several minutes - ~4.9GB download)
   docker compose exec ollama ollama pull llama3.1:latest
   
   # Verify the model is installed
   docker compose exec ollama ollama list
   ```

4. **Run the complete test suite**:
   ```bash
   python test_backend_workflow.py
   ```

## What This Script Tests

### ✅ Core Infrastructure
- **Health Check** - API responsiveness and version
- **API Documentation** - Swagger/OpenAPI docs availability
- **Database Connectivity** - PostgreSQL operations

### ✅ Authentication Flow
- **User Registration** - Create new user account
- **User Login** - JWT token generation
- **Authentication Protection** - Verify endpoints are secured

### ✅ Pet Management (CRUD)
- **Create Pet** - Add new pet with full details
- **Read Pets** - Get all pets for user
- **Read Specific Pet** - Get individual pet details
- **Update Pet** - Modify pet information
- **Delete Pet** - Remove pet (optional cleanup)

### ✅ Security & Data Persistence
- **JWT Token Validation** - Ensure tokens work correctly
- **Data Persistence** - Verify database stores data properly
- **Authorization** - Check user can only access their own data

## Sample Output

```
🚀 Pet Health API - Complete Backend Test Suite
=======================================================
Testing API at: http://localhost:8000
Started at: 2025-11-30 18:45:32

✅ PASS Health Check
    API version: 1.0.0
✅ PASS API Documentation
    Swagger docs available

🔐 Authentication Tests
-------------------------
✅ PASS User Registration
    User ID: e2d3b837-b98c-4b38-b219-16a7466cf589
✅ PASS User Login
    JWT token received
✅ PASS Authentication Protection
    Protected endpoints properly secured

🐕 Pet Management Tests
-------------------------
✅ PASS Create Pet
    Pet 'Max' created with ID: 695ff762-54d7-4716-8ca3-55a7740cd536
✅ PASS Get Pets
    Retrieved 1 pet(s)
    Sample pet: Max (dog)
✅ PASS Get Specific Pet
    Retrieved pet: Max
✅ PASS Update Pet
    Pet updated - new age: 4

💾 Database & Infrastructure Tests
-----------------------------------
✅ PASS Database Connectivity
    Database operations working - 1 pets stored

📊 Test Results Summary
=========================
Tests Passed: 10/10 (100.0%)
🎉 ALL TESTS PASSED! Backend is fully operational.

Clean up test data? (y/N):
```

## Troubleshooting

If tests fail:

1. **Connection Error**: Make sure the backend is running with `docker compose up -d`
2. **Authentication Errors**: Check that JWT tokens are being generated properly
3. **Database Errors**: Verify PostgreSQL container is healthy with `docker compose ps`
4. **Port Conflicts**: Ensure port 8000 is available
5. **LLM/AI Errors**: 
   - Check Ollama service status: `docker compose logs ollama`
   - Verify model is installed: `docker compose exec ollama ollama list`
   - Re-download model if needed: `docker compose exec ollama ollama pull llama3.1:latest`

Check service status: `docker compose ps`
View logs: `docker compose logs api`
View Ollama logs: `docker compose logs ollama`

## LLM Model Information

- **Model**: Llama 3.1:latest
- **Size**: ~4.9GB download
- **Purpose**: AI-powered pet symptom analysis and recommendations
- **Download time**: 5-15 minutes depending on internet connection
- **Storage**: Persisted in Docker volume `ollama_data`

### LLM Installation Commands Reference:

```bash
# Start all services
docker compose up -d

# Check Ollama service status
docker compose logs ollama --tail=20

# Download the AI model (run this once)
docker compose exec ollama ollama pull llama3.1:latest

# List installed models
docker compose exec ollama ollama list

# Test the model directly (optional)
docker compose exec ollama ollama run llama3.1:latest "Hello, how are you?"

# Remove a model if needed
docker compose exec ollama ollama rm llama3.1:latest
```