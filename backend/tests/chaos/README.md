# Chaos Engineering Module

This module provides Python-based chaos engineering tests that integrate with the existing pytest framework.

## Overview

- **test_chaos_engineering.py**: Main chaos engineering test suite
- **Python-based**: Consistent with existing test infrastructure  
- **Docker integration**: Uses Docker commands to simulate failures
- **Realistic scenarios**: Tests actual failure scenarios and recovery

## Chaos Experiments

### Database Chaos
- PostgreSQL container failure simulation
- Connection exhaustion testing
- Automatic recovery validation

### AI Service Chaos
- Ollama container failure simulation
- AI fallback mechanism testing
- Model loading recovery validation

### Redis Chaos
- Cache/queue service failure
- Non-AI endpoint isolation testing
- Queue recovery validation

### Cascading Failures
- Multiple simultaneous service failures
- System stability under compound stress
- Full system recovery validation

## Usage

### Docker Testing (Recommended)

Run chaos engineering tests in Docker environment for realistic failure simulation:

```bash
# Run all chaos tests in Docker
./run-docker-tests.sh chaos

# Or manually with Docker Compose
docker compose up -d
docker compose exec api python docker_run_tests.py chaos
```

### Manual Docker Commands

```bash
# Start services
docker compose up -d

# Run all chaos tests
docker compose exec api python -m pytest tests/chaos/ -v --tb=short -s

# Run specific chaos experiments
docker compose exec api python -m pytest tests/chaos/test_chaos_engineering.py::TestChaosEngineering::test_database_chaos_experiment -v -s

# AI service chaos
docker compose exec api python -m pytest tests/chaos/test_chaos_engineering.py::TestChaosEngineering::test_ai_service_chaos_experiment -v -s

# Resilience patterns
docker compose exec api python -m pytest tests/chaos/test_chaos_engineering.py::TestResiliencePatterns -v -s
```

### Chaos Test Markers

```bash
# All chaos tests
docker compose exec api python -m pytest -m "chaos" -v -s

# Chaos tests (skip slow ones)
docker compose exec api python -m pytest -m "chaos and not slow" -v -s

# Specific chaos categories
docker compose exec api python -m pytest -m "chaos" -k "database" -v -s
```

### Local Development Testing

For development testing (requires Docker access and local setup):

```bash
cd backend

# Run all chaos tests
python -m pytest tests/chaos/ -v --tb=short -s

# Run specific experiments
python -m pytest tests/chaos/test_chaos_engineering.py::TestChaosEngineering::test_database_chaos_experiment -v -s

# Run with chaos markers
python -m pytest -m "chaos" -v -s
```

**Note**: Chaos tests require Docker socket access to manipulate containers. In Docker environment, this is automatically configured.

## Resilience Patterns Tested

### Circuit Breaker
- Database connection failure handling
- Automatic failure detection
- Recovery after service restoration

### Bulkhead Pattern
- Service isolation verification
- AI service failure doesn't affect core API
- Database failure isolation

### Timeout Pattern
- Request timeout handling
- Graceful degradation under latency
- Proper error responses

### Fallback Pattern  
- AI service fallback to rule-based analysis
- Graceful feature degradation
- User experience continuity

### Retry Pattern
- Automatic retry mechanisms
- Exponential backoff validation
- Transient failure handling

## Test Scenarios

### Single Service Failures
- Database unavailability
- AI service crashes
- Redis cache failures

### Compound Failures
- Multiple services down simultaneously
- Cascading failure scenarios
- Resource exhaustion

### Recovery Validation
- Automatic service recovery
- Health check responsiveness
- Data consistency after failures

## Requirements

The chaos tests use the same dependencies as existing tests plus:
- Docker CLI access for container management
- Proper container naming (follows docker-compose.yml)
- Network connectivity to test containers

## Safety Features

- ✅ Automatic cleanup after tests
- ✅ Service restoration even on test failure
- ✅ Limited blast radius (local containers only)
- ✅ Non-destructive data operations
- ✅ Configurable experiment duration