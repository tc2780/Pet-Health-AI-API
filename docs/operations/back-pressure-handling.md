# Back-pressure and Rate Limiting Guide

*Last Updated: December 5, 2025*

**Related Documents:**
- [SLA/SLO Definitions](./sla-slo-definitions.md) - Service level requirements
- [Incident Response Playbook](./incident-response-playbook.md) - Emergency procedures
- [Architecture Diagram](../system-design/architecture/architecture_diagram.md) - System design

## Back-pressure Handling Overview

Back-pressure occurs when downstream services cannot process requests as fast as they receive them, potentially leading to resource exhaustion, timeouts, and service degradation.

### Current Implementation Status

```yaml
Implemented:
  - FastAPI built-in request limiting via async/await
  - PostgreSQL connection pooling with SQLAlchemy
  - Redis connection pooling
  - Docker container resource limits
  - Graceful shutdown handling

Planned Enhancements:
  - Rate limiting middleware
  - Circuit breaker patterns
  - Request queuing with priority
  - AI inference queue management
```

## Rate Limiting Implementation

### API-Level Rate Limiting

#### FastAPI Rate Limiting Middleware
```python
# backend/app/middleware/rate_limiter.py
import time
import asyncio
from typing import Dict, Optional
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import redis.asyncio as redis

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, redis_url: str = "redis://localhost:6379"):
        super().__init__(app)
        self.redis = redis.from_url(redis_url)
        
        # Rate limits by endpoint type
        self.rate_limits = {
            "auth": {"requests": 10, "window": 60},      # 10 requests per minute for auth
            "api": {"requests": 100, "window": 60},       # 100 requests per minute for API
            "ai": {"requests": 5, "window": 60},          # 5 AI assessments per minute
            "default": {"requests": 50, "window": 60}     # Default rate limit
        }

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        endpoint_type = self._get_endpoint_type(request.url.path)
        
        # Check rate limit
        allowed = await self._check_rate_limit(client_ip, endpoint_type)
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "Rate limit exceeded",
                    "retry_after": self.rate_limits[endpoint_type]["window"]
                }
            )
        
        # Add rate limit headers
        response = await call_next(request)
        await self._add_rate_limit_headers(response, client_ip, endpoint_type)
        return response

    def _get_endpoint_type(self, path: str) -> str:
        if "/auth/" in path:
            return "auth"
        elif "/symptoms/assess" in path:
            return "ai"
        elif "/api/v1/" in path:
            return "api"
        return "default"

    async def _check_rate_limit(self, client_ip: str, endpoint_type: str) -> bool:
        key = f"rate_limit:{endpoint_type}:{client_ip}"
        limit = self.rate_limits[endpoint_type]
        
        # Sliding window implementation
        current_time = int(time.time())
        pipe = self.redis.pipeline()
        
        # Remove old entries
        pipe.zremrangebyscore(key, 0, current_time - limit["window"])
        # Add current request
        pipe.zadd(key, {str(current_time): current_time})
        # Count current requests
        pipe.zcard(key)
        # Set expiry
        pipe.expire(key, limit["window"])
        
        results = await pipe.execute()
        request_count = results[2]
        
        return request_count <= limit["requests"]

    async def _add_rate_limit_headers(self, response: Response, client_ip: str, endpoint_type: str):
        key = f"rate_limit:{endpoint_type}:{client_ip}"
        limit = self.rate_limits[endpoint_type]
        
        current_count = await self.redis.zcard(key)
        remaining = max(0, limit["requests"] - current_count)
        
        response.headers["X-RateLimit-Limit"] = str(limit["requests"])
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(time.time()) + limit["window"])
```

#### Integration with FastAPI App
```python
# backend/app/main.py
from app.middleware.rate_limiter import RateLimitMiddleware

app = FastAPI(title="Pet Health AI API")

# Add rate limiting middleware
app.add_middleware(RateLimitMiddleware)
```

### User-Specific Rate Limiting

#### Authenticated User Rate Limiting
```python
# backend/app/services/rate_limit.py
from functools import wraps
from fastapi import HTTPException, Depends, status
from app.services.auth import get_current_user
import redis.asyncio as redis

class UserRateLimiter:
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis = redis.from_url(redis_url)
        
        # User-specific limits (higher than IP-based)
        self.user_limits = {
            "ai_assessments": {"requests": 20, "window": 3600},    # 20 AI assessments per hour
            "api_calls": {"requests": 1000, "window": 3600},       # 1000 API calls per hour
            "pet_operations": {"requests": 100, "window": 3600}    # 100 pet operations per hour
        }

    async def check_user_rate_limit(self, user_id: str, operation: str) -> bool:
        if operation not in self.user_limits:
            return True
            
        key = f"user_rate_limit:{operation}:{user_id}"
        limit = self.user_limits[operation]
        
        current_time = int(time.time())
        pipe = self.redis.pipeline()
        
        # Sliding window implementation
        pipe.zremrangebyscore(key, 0, current_time - limit["window"])
        pipe.zadd(key, {str(current_time): current_time})
        pipe.zcard(key)
        pipe.expire(key, limit["window"])
        
        results = await pipe.execute()
        request_count = results[2]
        
        return request_count <= limit["requests"]

def rate_limit(operation: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract user from dependencies
            user = None
            for arg in args:
                if hasattr(arg, 'id'):  # User object
                    user = arg
                    break
            
            if user:
                rate_limiter = UserRateLimiter()
                allowed = await rate_limiter.check_user_rate_limit(str(user.id), operation)
                if not allowed:
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail=f"Rate limit exceeded for {operation}"
                    )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

# Usage example
@rate_limit("ai_assessments")
async def create_symptom_assessment(
    request: AssessmentRequest,
    user: User = Depends(get_current_user)
):
    # AI assessment logic
    pass
```

## AI Service Back-pressure Management

### Ollama Request Queue Management

#### AI Inference Queue
```python
# backend/app/services/ai_queue.py
import asyncio
from typing import Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime
import json

class AIRequestQueue:
    def __init__(self, max_concurrent: int = 3, max_queue_size: int = 100):
        self.max_concurrent = max_concurrent
        self.max_queue_size = max_queue_size
        self.active_requests = {}
        self.queue = asyncio.Queue(maxsize=max_queue_size)
        self.semaphore = asyncio.Semaphore(max_concurrent)
        
    async def enqueue_request(self, user_id: UUID, pet_id: UUID, symptoms: list) -> str:
        """Enqueue AI assessment request"""
        if self.queue.qsize() >= self.max_queue_size:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="AI service is currently overloaded. Please try again later."
            )
        
        request_id = str(uuid4())
        request_data = {
            "id": request_id,
            "user_id": str(user_id),
            "pet_id": str(pet_id),
            "symptoms": symptoms,
            "created_at": datetime.utcnow().isoformat(),
            "status": "queued"
        }
        
        await self.queue.put(request_data)
        return request_id
    
    async def process_queue(self):
        """Background task to process AI requests"""
        while True:
            try:
                # Wait for semaphore and request
                await self.semaphore.acquire()
                request_data = await self.queue.get()
                
                # Process request
                asyncio.create_task(self._process_request(request_data))
                
            except Exception as e:
                logger.error(f"Error in AI queue processing: {e}")
                await asyncio.sleep(1)
    
    async def _process_request(self, request_data: Dict[str, Any]):
        """Process individual AI request"""
        try:
            request_id = request_data["id"]
            self.active_requests[request_id] = {
                **request_data,
                "status": "processing",
                "started_at": datetime.utcnow().isoformat()
            }
            
            # Call Ollama service
            ollama_service = OllamaService()
            assessment = await ollama_service.analyze_symptoms(
                request_data["pet_id"],
                request_data["symptoms"]
            )
            
            # Store result
            self.active_requests[request_id].update({
                "status": "completed",
                "result": assessment,
                "completed_at": datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            # Mark as failed
            self.active_requests[request_id] = {
                **request_data,
                "status": "failed",
                "error": str(e),
                "failed_at": datetime.utcnow().isoformat()
            }
            
        finally:
            self.semaphore.release()
    
    async def get_request_status(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Get status of AI request"""
        return self.active_requests.get(request_id)
```

#### Async AI Assessment Endpoint
```python
# backend/app/api/v1/symptoms.py
from app.services.ai_queue import AIRequestQueue

ai_queue = AIRequestQueue()

@router.post("/assess-async")
async def create_symptom_assessment_async(
    request: AssessmentRequest,
    user: User = Depends(get_current_user)
):
    """Async AI assessment with queue management"""
    
    # Get pet and symptoms
    pet = await pet_service.get_pet(request.pet_id, user.id)
    symptoms = await symptom_service.get_symptoms_by_pet(request.pet_id)
    
    # Enqueue request
    try:
        request_id = await ai_queue.enqueue_request(
            user.id, request.pet_id, symptoms
        )
        
        return {
            "request_id": request_id,
            "status": "queued",
            "estimated_wait_time": ai_queue.queue.qsize() * 15,  # 15 seconds per request
            "position_in_queue": ai_queue.queue.qsize()
        }
        
    except HTTPException:
        # Queue is full, provide fallback
        return {
            "error": "AI service temporarily unavailable",
            "fallback_available": True,
            "retry_after": 300  # 5 minutes
        }

@router.get("/assess-status/{request_id}")
async def get_assessment_status(
    request_id: str,
    user: User = Depends(get_current_user)
):
    """Check status of async AI assessment"""
    status = await ai_queue.get_request_status(request_id)
    
    if not status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment request not found"
        )
    
    # Verify user owns the request
    if status["user_id"] != str(user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return status
```

## Circuit Breaker Implementation

### AI Service Circuit Breaker
```python
# backend/app/services/circuit_breaker.py
import asyncio
import time
from enum import Enum
from typing import Callable, Any
from functools import wraps

class CircuitState(Enum):
    CLOSED = "closed"       # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open" # Testing if service recovered

class CircuitBreaker:
    def __init__(self, 
                 failure_threshold: int = 5,
                 timeout: int = 60,
                 expected_exception: type = Exception):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
        
    def call(self, func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if self.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self.state = CircuitState.HALF_OPEN
                else:
                    raise Exception("Circuit breaker is OPEN - AI service unavailable")
            
            try:
                result = await func(*args, **kwargs)
                self._on_success()
                return result
                
            except self.expected_exception as e:
                self._on_failure()
                raise e
                
        return wrapper
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to try again"""
        return (time.time() - self.last_failure_time) >= self.timeout
    
    def _on_success(self):
        """Reset circuit breaker on successful call"""
        self.failure_count = 0
        self.state = CircuitState.CLOSED
    
    def _on_failure(self):
        """Handle failure and potentially open circuit"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN

# Usage with AI service
ai_circuit_breaker = CircuitBreaker(
    failure_threshold=3,  # Open after 3 failures
    timeout=120,          # Try again after 2 minutes
    expected_exception=Exception
)

class OllamaService:
    @ai_circuit_breaker.call
    async def analyze_symptoms(self, pet_id: str, symptoms: list) -> dict:
        """AI analysis with circuit breaker protection"""
        # Ollama API call logic
        pass
```

## Database Connection Pool Management

### SQLAlchemy Pool Configuration
```python
# backend/app/core/database.py
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

# Enhanced connection pool configuration
DATABASE_URL = "postgresql://postgres:password@localhost:5432/pettech_db"

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,                    # Base number of connections
    max_overflow=20,                 # Additional connections when needed
    pool_recycle=3600,               # Recycle connections every hour
    pool_pre_ping=True,              # Validate connections before use
    pool_timeout=30,                 # Timeout when getting connection
    echo=False                       # Set to True for SQL logging
)

# Connection health monitoring
async def check_database_health():
    """Check database connection pool status"""
    pool = engine.pool
    return {
        "size": pool.size(),
        "checked_in": pool.checkedin(),
        "checked_out": pool.checkedout(),
        "overflow": pool.overflow(),
        "invalid": pool.invalid()
    }
```

## Resource Limits and Kill Switches

### Docker Resource Limits
```yaml
# docker-compose.yml - Enhanced resource limits
version: '3.8'
services:
  api:
    build: ./backend
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
        reservations:
          memory: 512M
          cpus: '0.25'
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  postgres:
    image: postgres:15
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
        reservations:
          memory: 1G
          cpus: '0.5'
    command: |
      postgres 
      -c max_connections=100
      -c shared_buffers=256MB
      -c effective_cache_size=1GB
      -c work_mem=4MB

  ollama:
    image: ollama/ollama
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: '2.0'
        reservations:
          memory: 2G
          cpus: '1.0'

  redis:
    image: redis:7-alpine
    deploy:
      resources:
        limits:
          memory: 256M
          cpus: '0.25'
        reservations:
          memory: 128M
          cpus: '0.125'
    command: redis-server --maxmemory 200mb --maxmemory-policy allkeys-lru
```

### Application Kill Switches
```python
# backend/app/core/kill_switch.py
import os
from typing import Dict, Any
from fastapi import HTTPException, status

class KillSwitch:
    def __init__(self):
        self.switches = {
            "ai_service": os.getenv("DISABLE_AI_SERVICE", "false").lower() == "true",
            "new_registrations": os.getenv("DISABLE_NEW_USERS", "false").lower() == "true",
            "ai_assessments": os.getenv("DISABLE_AI_ASSESSMENTS", "false").lower() == "true",
            "data_exports": os.getenv("DISABLE_DATA_EXPORTS", "false").lower() == "true"
        }
    
    def check_switch(self, feature: str):
        """Check if a feature is disabled"""
        if self.switches.get(feature, False):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"{feature} is temporarily disabled for maintenance"
            )
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of all kill switches"""
        return {
            "kill_switches": self.switches,
            "healthy_services": [k for k, v in self.switches.items() if not v],
            "disabled_services": [k for k, v in self.switches.items() if v]
        }

# Usage in endpoints
kill_switch = KillSwitch()

@router.post("/assess")
async def create_assessment(...):
    kill_switch.check_switch("ai_assessments")
    # Assessment logic
```

## Monitoring and Alerting

### Prometheus Metrics for Back-pressure
```python
# backend/app/monitoring/metrics.py
from prometheus_client import Counter, Histogram, Gauge

# Rate limiting metrics
rate_limit_exceeded = Counter('rate_limit_exceeded_total', 
                             'Number of rate limit violations', 
                             ['endpoint', 'limit_type'])

# Queue metrics
ai_queue_size = Gauge('ai_queue_size', 'Current AI request queue size')
ai_processing_time = Histogram('ai_processing_seconds', 
                              'AI request processing time')

# Circuit breaker metrics
circuit_breaker_state = Gauge('circuit_breaker_state', 
                             'Circuit breaker state (0=closed, 1=half-open, 2=open)',
                             ['service'])

# Connection pool metrics
db_pool_connections = Gauge('db_pool_connections', 
                           'Database connection pool status',
                           ['state'])  # checked_in, checked_out, overflow
```

### Alert Rules
```yaml
# monitoring/alert_rules.yml
groups:
  - name: back_pressure
    rules:
      - alert: HighRateLimitRejection
        expr: rate(rate_limit_exceeded_total[5m]) > 10
        for: 2m
        annotations:
          summary: "High rate of rate limit rejections"
          
      - alert: AIQueueBacklog
        expr: ai_queue_size > 50
        for: 5m
        annotations:
          summary: "AI request queue is backing up"
          
      - alert: CircuitBreakerOpen
        expr: circuit_breaker_state == 2
        for: 1m
        annotations:
          summary: "Circuit breaker is open for {{ $labels.service }}"
          
      - alert: DatabasePoolExhaustion
        expr: db_pool_connections{state="checked_out"} / (db_pool_connections{state="checked_out"} + db_pool_connections{state="checked_in"}) > 0.9
        for: 2m
        annotations:
          summary: "Database connection pool nearly exhausted"
```

This comprehensive back-pressure handling documentation provides the operational procedures needed to manage load and prevent service degradation in your Pet Health AI system.