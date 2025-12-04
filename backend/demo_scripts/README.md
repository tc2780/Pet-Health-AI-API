# Demo Scripts

This folder contains demonstration scripts for testing and showcasing the Pet Health API's AI capabilities.

## 🚀 Quick Start

Run the interactive demo launcher:

```bash
docker compose exec api python demo_scripts/run_demo.py
```

Or run individual scripts directly (see below).

## 📋 Prerequisites

**No local Python setup required** - all demos run inside Docker containers.

Before running demos:

```bash
# 1. Start Docker services
docker compose up -d

# 2. Verify Ollama is running
docker compose ps ollama

# 3. Ensure model is available
docker compose exec ollama ollama list

# 4. If model missing, pull it
# Default: More accurate model (recommended)
docker compose exec ollama ollama pull llama3.2:3b

# Alternative: Faster model (if resources are limited)
docker compose exec ollama ollama pull llama3.2:1b
```

## 🧪 Quick Validation

To quickly verify everything is working:

```bash
# Test Ollama connectivity (fastest)
docker compose exec api python demo_scripts/ollama_direct_test.py

# Run full demo (comprehensive)
docker compose exec api python demo_scripts/ai_veterinary_demo.py
```

## 📁 Scripts

### 1. `run_demo.py` (Interactive Menu)
**Purpose:** Interactive launcher for all demo scripts  
**Use Case:** Convenient way to explore all demos

```bash
# Launch interactive menu
docker compose exec api python demo_scripts/run_demo.py

# Model selection within menu:
# Type '1 3b' or '2 1b' to run with specific model
# Example: '1 1b' runs Ollama test with 1b model
```

### 2. `ollama_direct_test.py`
**Purpose:** Test Ollama API connectivity and response parsing  
**Use Case:** Quick validation that Ollama is running and responding correctly  
**Runtime:** ~5 seconds

```bash
# Use default model (llama3.2:3b)
docker compose exec api python demo_scripts/ollama_direct_test.py

# Or specify model
docker compose exec api python demo_scripts/ollama_direct_test.py 3b
docker compose exec api python demo_scripts/ollama_direct_test.py 1b
```

**Features:**
- ✅ Tests Ollama API connectivity
- ✅ Validates JSON response parsing
- ✅ Checks response structure
- ✅ Returns exit code for CI/CD

### 3. `ai_veterinary_demo.py`
**Purpose:** Comprehensive demonstration of AI-powered veterinary analysis  
**Use Case:** Showcase different urgency levels with realistic pet cases  
**Runtime:** ~30-60 seconds

```bash
# Use default model (llama3.2:3b)
docker compose exec api python demo_scripts/ai_veterinary_demo.py

# Or specify model
docker compose exec api python demo_scripts/ai_veterinary_demo.py 3b
docker compose exec api python demo_scripts/ai_veterinary_demo.py 1b
```

**Test Cases:**
- 🚨 **Emergency:** Severe respiratory distress (dog)
- ⚠️ **High Priority:** Gastrointestinal issues with blood (cat)
- 🟡 **Medium:** Behavioral changes and lethargy (dog)

### 4. `service_integration_test.py`
**Purpose:** Test the SymptomService with real AI integration  
**Use Case:** Validate end-to-end symptom analysis through the service layer  
**Runtime:** ~20-40 seconds

```bash
# Use default model (llama3.2:3b)
docker compose exec api python demo_scripts/service_integration_test.py

# Or specify model
docker compose exec api python demo_scripts/service_integration_test.py 3b
docker compose exec api python demo_scripts/service_integration_test.py 1b
```

**Features:**
- ✅ Tests SymptomService integration
- ✅ Uses in-memory database
- ✅ Validates service-level functionality
- ✅ Comprehensive test summary

### 5. `end_to_end_workflow_test.py`
**Purpose:** Complete backend workflow test (registration → authentication → pet management)  
**Use Case:** Validate entire API flow with real HTTP requests  
**Runtime:** ~10-20 seconds

```bash
docker compose exec api python demo_scripts/end_to_end_workflow_test.py
```

**Test Coverage:**
- ✅ Health check and API docs
- ✅ User registration and login
- ✅ JWT authentication
- ✅ Pet CRUD operations
- ✅ Authorization enforcement
- ✅ Automatic cleanup

## 🔄 What Changed?

Previously scattered test files have been **consolidated** into `demo_scripts/`:

**Removed from `backend/` root:**
- ❌ `test_ai_demo.py`
- ❌ `test_ai_integration.py`
- ❌ `test_ollama.py`

**Removed `happy_path_test/` folder:**
- ❌ `happy_path_test/test_backend_workflow.py`
- ❌ `happy_path_test/test_script_usage.md`

**Improvements:**
- ✅ Removed code redundancy
- ✅ Better organization
- ✅ Cleaner structure
- ✅ Interactive launcher
- ✅ Comprehensive documentation
- ✅ All demos in one place

## 💡 Tips

- Use `ollama_direct_test.py` for quick connectivity checks
- Use `ai_veterinary_demo.py` for presentations and demonstrations
- Use `service_integration_test.py` for development validation
- Use `end_to_end_workflow_test.py` for full API integration testing
- Use `run_demo.py` for exploring all options interactively

## 📊 Script Comparison

| Script | Runtime | Purpose | Use Case |
|--------|---------|---------|----------|
| `ollama_direct_test` | ~5 sec | Ollama connectivity | Quick health check |
| `ai_veterinary_demo` | ~30-60 sec | AI showcase | Presentations/demos |
| `service_integration_test` | ~20-40 sec | Service layer | Development validation |
| `end_to_end_workflow_test` | ~10-20 sec | Full API workflow | Integration testing |
