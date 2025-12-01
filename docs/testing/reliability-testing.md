# Reliability & Testing Strategy

## Testing Pyramid

### **Unit Tests (70%)**
Fast, isolated tests for individual components

#### **Model Tests**
```python
# tests/test_models.py
def test_pet_creation():
    pet = Pet(
        name="Buddy",
        species="dog", 
        breed="Golden Retriever",
        age_years=5
    )
    assert pet.name == "Buddy"
    assert pet.species == "dog"

def test_symptom_validation():
    with pytest.raises(ValidationError):
        Symptom(
            pet_id="123",
            symptom_name="",  # Invalid empty name
            severity="invalid"  # Invalid severity
        )
```

#### **Service Layer Tests**
```python
# tests/test_services.py
@pytest.mark.asyncio
async def test_symptom_service_create():
    mock_db = Mock()
    service = SymptomService(mock_db)
    
    symptom_data = SymptomCreate(
        symptom_name="lethargy",
        severity="moderate",
        observed_at=datetime.utcnow()
    )
    
    result = await service.create_symptom("pet-123", symptom_data)
    assert result.symptom_name == "lethargy"
    mock_db.add.assert_called_once()
```

### **Integration Tests (20%)**
Test component interactions and external dependencies

#### **API Integration Tests**
```python
# tests/test_api_integration.py
@pytest.mark.asyncio
async def test_symptom_tracking_workflow():
    # Create user and pet
    user = await create_test_user()
    pet = await create_test_pet(user.id)
    
    # Log symptom
    symptom_data = {
        "symptom_name": "vomiting",
        "severity": "moderate",
        "observed_at": "2025-11-30T10:00:00Z"
    }
    
    response = await client.post(
        f"/symptoms/{pet.id}/symptoms",
        json=symptom_data,
        headers=get_auth_headers(user.id)
    )
    
    assert response.status_code == 201
    symptom = response.json()
    
    # Retrieve symptoms
    get_response = await client.get(
        f"/symptoms/{pet.id}/symptoms",
        headers=get_auth_headers(user.id)
    )
    
    assert get_response.status_code == 200
    symptoms = get_response.json()["symptoms"]
    assert len(symptoms) == 1
    assert symptoms[0]["id"] == symptom["id"]
```

#### **Database Integration Tests**
```python
# tests/test_database.py
@pytest.mark.asyncio
async def test_database_connection_resilience():
    """Test database reconnection after connection loss"""
    
    # Simulate connection loss
    await db.execute("SELECT pg_terminate_backend(pg_backend_pid())")
    
    # Should automatically reconnect
    result = await symptom_service.get_symptoms("pet-123")
    assert result is not None
    
@pytest.mark.asyncio
async def test_transaction_rollback():
    """Test transaction rollback on error"""
    async with db.transaction():
        pet = await create_test_pet()
        
        # Simulate error
        with pytest.raises(IntegrityError):
            await create_duplicate_pet(pet.id)  # Should fail
    
    # Pet should not exist due to rollback
    assert await get_pet(pet.id) is None
```

### **End-to-End Tests (10%)**
Full system integration tests

#### **User Journey Tests**
```python
# tests/test_e2e.py
@pytest.mark.asyncio
async def test_complete_pet_health_journey():
    """Test full user journey from registration to AI assessment"""
    
    # 1. User registration
    user_data = {
        "email": "test@example.com",
        "password": "secure123"
    }
    auth_response = await client.post("/auth/register", json=user_data)
    assert auth_response.status_code == 201
    tokens = auth_response.json()
    
    # 2. Create pet
    pet_data = {
        "name": "Buddy",
        "species": "dog",
        "age_years": 5
    }
    pet_response = await client.post(
        "/pets",
        json=pet_data,
        headers={"Authorization": f"Bearer {tokens['access_token']}"}
    )
    assert pet_response.status_code == 201
    pet = pet_response.json()
    
    # 3. Log symptoms
    symptoms = [
        {"symptom_name": "lethargy", "severity": "moderate"},
        {"symptom_name": "loss_of_appetite", "severity": "mild"}
    ]
    
    for symptom in symptoms:
        symptom_response = await client.post(
            f"/symptoms/{pet['id']}/symptoms",
            json=symptom,
            headers={"Authorization": f"Bearer {tokens['access_token']}"}
        )
        assert symptom_response.status_code == 201
    
    # 4. Get AI assessment
    assessment_response = await client.post(
        f"/ai-vet/{pet['id']}/assess",
        json={"include_recent_symptoms": True},
        headers={"Authorization": f"Bearer {tokens['access_token']}"}
    )
    assert assessment_response.status_code == 200
    assessment = assessment_response.json()
    
    # Verify AI response structure
    assert "urgency_level" in assessment
    assert "possible_causes" in assessment
    assert "recommendations" in assessment
    assert "disclaimer" in assessment
```

## Load & Chaos Testing

### **Load Testing Strategy**
```python
# tests/load_test.py
from locust import HttpUser, task, between

class PetHealthUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """Setup user session"""
        self.login()
        self.pet_id = self.create_test_pet()
    
    def login(self):
        response = self.client.post("/auth/login", json={
            "email": "loadtest@example.com",
            "password": "test123"
        })
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    @task(3)
    def log_symptom(self):
        """Most common operation - log symptoms"""
        self.client.post(
            f"/symptoms/{self.pet_id}/symptoms",
            json={
                "symptom_name": "lethargy",
                "severity": "mild",
                "observed_at": datetime.utcnow().isoformat()
            },
            headers=self.headers
        )
    
    @task(2)
    def get_symptoms(self):
        """Second most common - view symptoms"""
        self.client.get(
            f"/symptoms/{self.pet_id}/symptoms?days_back=7",
            headers=self.headers
        )
    
    @task(1)
    def ai_assessment(self):
        """Less frequent but resource intensive"""
        self.client.post(
            f"/ai-vet/{self.pet_id}/assess",
            json={"include_recent_symptoms": True},
            headers=self.headers
        )

# Load test scenarios
class LoadTestScenarios:
    @staticmethod
    async def normal_load():
        """Normal usage: 100 concurrent users"""
        return await run_load_test(
            users=100,
            spawn_rate=10,
            duration="10m"
        )
    
    @staticmethod
    async def peak_load():
        """Peak usage: 500 concurrent users"""
        return await run_load_test(
            users=500,
            spawn_rate=25,
            duration="15m"
        )
    
    @staticmethod
    async def stress_test():
        """Stress test: 1000+ users until failure"""
        return await run_load_test(
            users=1000,
            spawn_rate=50,
            duration="30m"
        )
```

### **Chaos Engineering**
```python
# tests/chaos_test.py
class ChaosTests:
    
    @pytest.mark.chaos
    async def test_database_failure_recovery():
        """Test system behavior when database fails"""
        
        # Start normal operations
        await start_background_requests()
        
        # Kill database
        await docker.kill_container("postgres")
        
        # System should gracefully degrade
        response = await client.get("/health")
        assert response.json()["status"] == "degraded"
        
        # Restart database
        await docker.start_container("postgres")
        
        # System should recover
        await wait_for_recovery(timeout=30)
        response = await client.get("/health")
        assert response.json()["status"] == "healthy"
    
    @pytest.mark.chaos
    async def test_ai_service_failure():
        """Test fallback when AI service fails"""
        
        # Kill AI service
        await docker.kill_container("ollama")
        
        # AI requests should fail gracefully
        response = await client.post("/ai-vet/pet-123/assess", json={})
        assert response.status_code == 503
        assert "AI service temporarily unavailable" in response.json()["error"]["message"]
        
        # Other services should continue working
        response = await client.get("/pets")
        assert response.status_code == 200
    
    @pytest.mark.chaos
    async def test_redis_failure_degradation():
        """Test system with cache failure"""
        
        # Kill Redis
        await docker.kill_container("redis")
        
        # System should work but slower
        start_time = time.time()
        response = await client.get("/symptoms/pet-123/symptoms")
        end_time = time.time()
        
        assert response.status_code == 200
        # Should be slower without cache but still functional
        assert (end_time - start_time) > 0.5  # Slower response expected
```

## Observability & Monitoring

### **Health Checks**
```python
# app/api/health.py
class HealthCheck:
    
    async def comprehensive_health_check(self) -> Dict[str, Any]:
        """Multi-level health assessment"""
        
        checks = {
            "database": await self._check_database(),
            "redis": await self._check_redis(), 
            "ai_service": await self._check_ai_service(),
            "disk_space": await self._check_disk_space(),
            "memory_usage": await self._check_memory()
        }
        
        overall_status = self._calculate_overall_status(checks)
        
        return {
            "status": overall_status,
            "timestamp": datetime.utcnow().isoformat(),
            "checks": checks,
            "version": settings.VERSION
        }
    
    async def _check_database(self) -> Dict[str, Any]:
        try:
            start_time = time.time()
            await db.execute("SELECT 1")
            response_time = (time.time() - start_time) * 1000
            
            return {
                "status": "healthy",
                "response_time_ms": response_time,
                "details": "Database connection successful"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "details": "Database connection failed"
            }
    
    async def _check_ai_service(self) -> Dict[str, Any]:
        try:
            # Quick AI connectivity test
            test_response = await ai_service.health_check()
            
            return {
                "status": "healthy",
                "model": test_response.get("model", "unknown"),
                "details": "AI service responding"
            }
        except Exception as e:
            return {
                "status": "unhealthy", 
                "error": str(e),
                "details": "AI service unavailable"
            }
```

### **Metrics Collection**
```python
# app/core/metrics.py
from prometheus_client import Counter, Histogram, Gauge

# Business metrics
SYMPTOM_LOGS = Counter('pet_symptoms_logged_total', 'Total symptoms logged', ['species', 'severity'])
AI_ASSESSMENTS = Counter('ai_assessments_total', 'Total AI assessments', ['urgency_level'])
USER_REGISTRATIONS = Counter('user_registrations_total', 'Total user registrations')

# Performance metrics  
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'Request duration', ['method', 'endpoint'])
AI_RESPONSE_TIME = Histogram('ai_response_duration_seconds', 'AI response time')
DATABASE_QUERY_TIME = Histogram('database_query_duration_seconds', 'Database query time')

# System metrics
ACTIVE_USERS = Gauge('active_users_count', 'Number of active users')
DATABASE_CONNECTIONS = Gauge('database_connections_active', 'Active database connections')
MEMORY_USAGE = Gauge('memory_usage_bytes', 'Memory usage in bytes')

class MetricsCollector:
    
    @staticmethod
    def record_symptom_logged(species: str, severity: str):
        SYMPTOM_LOGS.labels(species=species, severity=severity).inc()
    
    @staticmethod
    def record_ai_assessment(urgency_level: str, duration: float):
        AI_ASSESSMENTS.labels(urgency_level=urgency_level).inc()
        AI_RESPONSE_TIME.observe(duration)
    
    @staticmethod
    def record_request_duration(method: str, endpoint: str, duration: float):
        REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)
```

### **Alerting Rules**
```yaml
# monitoring/alerts.yml
groups:
  - name: pet-health-api.rules
    rules:
    
    # High-priority alerts
    - alert: APIHighErrorRate
      expr: rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) > 0.05
      for: 5m
      labels:
        severity: critical
      annotations:
        summary: "High error rate detected"
        description: "API error rate is {{ $value | humanizePercentage }} over 5 minutes"
    
    - alert: DatabaseConnectionFailure  
      expr: up{job="postgres"} == 0
      for: 1m
      labels:
        severity: critical
      annotations:
        summary: "Database is down"
        description: "PostgreSQL database is not responding"
    
    - alert: AIServiceUnresponsive
      expr: ai_service_health_check_success == 0
      for: 2m
      labels:
        severity: high
      annotations:
        summary: "AI service not responding"
        description: "Local LLM service is not responding to health checks"
    
    # Medium-priority alerts
    - alert: HighResponseTime
      expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 2
      for: 10m
      labels:
        severity: warning
      annotations:
        summary: "High API response times"
        description: "95th percentile response time is {{ $value }}s"
    
    - alert: LowDiskSpace
      expr: node_filesystem_avail_bytes / node_filesystem_size_bytes < 0.1
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: "Low disk space"
        description: "Disk usage is above 90%"
```

## Failure Handling

### **Idempotency Implementation**
```python
# app/core/idempotency.py
class IdempotencyManager:
    
    async def ensure_idempotent_operation(
        self, 
        operation_id: str, 
        operation_func: Callable,
        ttl: int = 3600
    ):
        """Ensure operation is idempotent using Redis"""
        
        cache_key = f"idempotency:{operation_id}"
        
        # Check if operation already completed
        cached_result = await redis.get(cache_key)
        if cached_result:
            return json.loads(cached_result)
        
        # Execute operation
        result = await operation_func()
        
        # Cache result
        await redis.setex(cache_key, ttl, json.dumps(result, default=str))
        
        return result

# Usage in API endpoints
@router.post("/symptoms/{pet_id}/symptoms")
async def create_symptom(
    pet_id: str,
    symptom_data: SymptomCreate,
    idempotency_key: str = Header(None),
    db: Session = Depends(get_db)
):
    if idempotency_key:
        idempotency_manager = IdempotencyManager()
        return await idempotency_manager.ensure_idempotent_operation(
            idempotency_key,
            lambda: symptom_service.create_symptom(pet_id, symptom_data)
        )
    else:
        return await symptom_service.create_symptom(pet_id, symptom_data)
```

### **Circuit Breaker Pattern**
```python
# app/core/circuit_breaker.py
class CircuitBreaker:
    def __init__(self, failure_threshold=5, recovery_timeout=60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    async def call(self, func, *args, **kwargs):
        if self.state == "OPEN":
            if self._should_attempt_reset():
                self.state = "HALF_OPEN"
            else:
                raise CircuitBreakerOpenException("Circuit breaker is open")
        
        try:
            result = await func(*args, **kwargs)
            self._record_success()
            return result
        except Exception as e:
            self._record_failure()
            raise e
    
    def _record_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
    
    def _record_success(self):
        self.failure_count = 0
        self.state = "CLOSED"
    
    def _should_attempt_reset(self):
        return (time.time() - self.last_failure_time) >= self.recovery_timeout

# Usage with AI service
ai_circuit_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=30)

async def get_ai_assessment_with_fallback(pet_data, symptoms):
    try:
        return await ai_circuit_breaker.call(ai_service.analyze_symptoms, pet_data, symptoms)
    except CircuitBreakerOpenException:
        # Fallback to basic rule-based assessment
        return basic_symptom_assessment(pet_data, symptoms)
```

## Service Level Objectives (SLOs)

### **Availability SLOs**
```yaml
API Availability:
  Target: 99.9% (8.77 hours downtime/year)
  Measurement: Successful HTTP responses / Total HTTP requests
  Window: 30-day rolling window

Database Availability:
  Target: 99.95% (4.38 hours downtime/year)
  Measurement: Successful database connections
  Window: 30-day rolling window

AI Service Availability:
  Target: 99.5% (3.65 days downtime/year)
  Measurement: Successful AI assessments / Total AI requests
  Window: 30-day rolling window
```

### **Performance SLOs**
```yaml
API Response Time:
  Target: 95% of requests < 500ms
  Target: 99% of requests < 2s
  Measurement: HTTP request duration
  Exclusions: AI assessment endpoint (separate SLO)

AI Assessment Response Time:
  Target: 95% of assessments < 5s
  Target: 99% of assessments < 15s
  Measurement: End-to-end AI processing time

Database Query Performance:
  Target: 95% of queries < 100ms
  Target: 99% of queries < 500ms
  Measurement: Database query execution time
```

This comprehensive testing strategy ensures system reliability through automated testing, proactive monitoring, and graceful failure handling.