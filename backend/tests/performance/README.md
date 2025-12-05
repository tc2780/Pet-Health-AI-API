# Performance Testing Module

This module provides Python-based performance testing that integrates with the existing pytest framework.

## Overview

- **test_load_testing.py**: Main performance test suite with baseline, load, and stress tests
- **Integrates with existing pytest**: Uses same test runner and conventions as current tests
- **Python-based**: Consistent with existing test infrastructure
- **Realistic scenarios**: Tests actual user workflows including AI analysis

## Test Categories

### Baseline Performance Tests
- Single-user optimal performance validation
- Health endpoint response time testing
- Authenticated endpoint performance
- Pet CRUD operation baselines

### Load Testing
- Concurrent user simulation (5, 10, 25 users)
- Realistic user workflow patterns
- Performance under normal operating conditions

### Stress Testing  
- High concurrent user loads (50+ users)
- System breaking point identification
- Graceful degradation validation

### AI Performance Testing
- AI processing baseline performance
- Concurrent AI request handling
- Queue management under load

## Usage

### Docker Testing (Recommended)

Run performance tests in Docker environment for production-like conditions:

```bash
# Run all performance tests in Docker
./run-docker-tests.sh performance

# Or manually with Docker Compose
docker compose up -d
docker compose exec api python docker_run_tests.py performance
```

### Manual Docker Commands

```bash
# Start services
docker compose up -d

# Run all performance tests
docker compose exec api python -m pytest tests/performance/ -v --tb=short

# Run specific test categories
docker compose exec api python -m pytest tests/performance/ -m "performance and not slow" -v

# Load testing only
docker compose exec api python -m pytest tests/performance/test_load_testing.py::TestLoadTesting -v

# AI performance tests
docker compose exec api python -m pytest tests/performance/ -m "ai" -v
```

### Local Development Testing

For quick development testing (requires local setup):

```bash
cd backend

# Run all performance tests
python -m pytest tests/performance/ -v --tb=short

# Run specific test categories
python -m pytest tests/performance/ -m "performance and not slow" -v

# Load tests
python -m pytest tests/performance/test_load_testing.py::TestLoadTesting -v

# AI performance tests
python -m pytest tests/performance/ -m "ai" -v
```

### Performance Test Markers

```bash
# All performance tests (including slow ones)
docker compose exec api python -m pytest -m "performance" -v

# Skip slow tests
docker compose exec api python -m pytest -m "performance and not slow" -v

# AI-specific performance tests
docker compose exec api python -m pytest -m "performance and ai" -v
```

## Performance Thresholds

### Baseline Performance (Single User)
- Health endpoint: <100ms
- Authentication: <300ms
- Pet operations: <500ms  
- AI processing: <30s

### Load Testing (Concurrent Users)
- Success rate: >90%
- P95 response time: <5s
- Error rate: <10%

### Stress Testing (High Load)
- Success rate: >75% (graceful degradation)
- Error rate: <25%
- System remains responsive

## Dependencies

The performance tests use the same dependencies as existing tests:
- `pytest` (already installed)
- `httpx` (for HTTP client - already used in integration tests)
- `asyncio` (built-in Python)
- Existing app modules and fixtures