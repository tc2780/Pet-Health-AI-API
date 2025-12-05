# Cost Model & Operability Guide

*Last Updated: December 5, 2025*

**Current Implementation Status:** Docker Compose deployment with Ollama llama3.2:3b local AI processing

**Related Documents:**
- [Trust Model](../compliance/trust-model.md) - Security and deployment considerations
- [Ethics Framework](../compliance/ethics-framework.md) - AI service ethical guidelines
- [Deployment Instructions](./deployment-instructions.md) - Technical deployment guide

## Cost Model Analysis

### **Development Phase Costs**

#### **Zero-Cost Development Setup (Current Implementation)**
```yaml
Local Development (Free - Currently Used):
  - Hardware: Developer laptop with Docker Desktop
  - Software: All open-source (FastAPI, PostgreSQL, Redis, Ollama)
  - Docker Desktop: Free for individual use
  - Ollama + llama3.2:3b: Free forever (2GB model)
  - GitHub: Free tier for public repos
  - IDE: VS Code (free)
  - Testing: 187 automated tests run in containers
  - Total: $0/month

Resource Requirements:
  - RAM: 8GB minimum (4GB for Ollama, 4GB for other services)
  - Storage: 10GB (2GB for model, 8GB for containers and data)
  - CPU: 4 cores recommended for AI processing
```

#### **Free-Tier Cloud Development**
```yaml
Railway Free Tier:
  - $5 free credits monthly
  - PostgreSQL database: Included
  - Redis: 100MB free
  - Container hosting: Included
  - Usage: Perfect for development/testing
  - Total: $0/month (within credits)

Alternative Free Options:
  - Render: 750 hours/month free
  - Heroku: Basic app hosting
  - Fly.io: 3 shared VMs free
  - Total: $0/month
```

### **Production Deployment Costs**

#### **Current Docker Compose Production (Recommended)**
```yaml
Single Server Deployment:
  - Server: $20-40/month (4GB RAM, 2 CPU, 50GB storage)
  - Docker Compose services:
    * FastAPI backend (api)
    * PostgreSQL database (postgres)
    * Redis cache (redis)
    * Ollama AI service (ollama with llama3.2:3b)
  - Domain: $12/year
  - SSL Certificate: Free (Let's Encrypt)
  - Monitoring: Free (built-in Docker stats)
  - Total: $25-45/month

Performance Characteristics:
  - Handles 100-1K concurrent users
  - AI processing: 2-5 seconds per assessment
  - Database: PostgreSQL with proper indexing
  - Caching: Redis for session and response caching
```

#### **Small Scale Production (0-1K users)**
```yaml
DigitalOcean Droplet Setup:
  - App Server: $12/month (Basic Droplet)
  - Database: $15/month (Managed PostgreSQL)  
  - Redis: $5/month (Basic Redis)
  - Load Balancer: $12/month
  - Backup Storage: $2/month
  - Monitoring: Free (Prometheus/Grafana)
  - Total: $46/month

Alternative AWS Setup:
  - EC2 t3.small: $17/month
  - RDS t3.micro: $13/month
  - ElastiCache t3.micro: $11/month
  - ALB: $16/month
  - S3 + CloudWatch: $3/month
  - Total: $60/month
```

#### **Medium Scale Production (1K-10K users)**
```yaml
Kubernetes Cluster Setup:
  - Control Plane: $72/month (3 nodes)
  - Worker Nodes: $144/month (4 nodes) 
  - Managed Database: $45/month
  - Redis Cluster: $25/month
  - Load Balancer: $20/month
  - Monitoring Stack: $15/month
  - Backup/Storage: $8/month
  - Total: $329/month

Cost Per User: $0.03-0.33/month
```

#### **Large Scale Production (10K+ users)**
```yaml
High Availability Setup:
  - Multi-region deployment: $800/month
  - Database cluster: $200/month
  - Redis cluster: $100/month
  - CDN: $50/month
  - Monitoring/Logging: $75/month
  - Security services: $100/month
  - Total: $1,325/month

Cost Per User: $0.13/month (at 10K users)
```

### **AI Processing Costs**

#### **Local LLM (Ollama) - Current Implementation**
```yaml
Infrastructure Costs:
  - Development Server: $0 (laptop with 8GB+ RAM)
  - Production Server: $20-40/month (included in Docker deployment)
  - Model Storage: 2GB for llama3.2:3b (one-time download)
  - Model Alternatives: 1.3GB for llama3.2:1b (faster, less accurate)
  - Processing: No per-request costs
  - Scaling: Linear with server capacity

Current Performance:
  - llama3.2:3b: 2-5 seconds per assessment (higher accuracy)
  - llama3.2:1b: 1-3 seconds per assessment (faster processing)
  - Concurrent requests: 3-5 (limited by model processing)
  - Memory usage: 2-4GB per model instance

Cost per AI Request: $0.00 (after infrastructure)
Monthly at 10K requests: $0.00
Monthly at 100K requests: $0.00 (may need multiple server instances)
```

#### **Cloud AI APIs (for comparison)**
```yaml
OpenAI GPT-3.5 Turbo:
  - Input: $0.0005 per 1K tokens
  - Output: $0.0015 per 1K tokens
  - Average consultation: ~800 tokens
  - Cost per consultation: ~$0.0008

Monthly Costs:
  - 1,000 consultations: $0.80
  - 10,000 consultations: $8.00
  - 100,000 consultations: $80.00

Break-even vs Local LLM:
  - Local LLM pays for itself at ~200K consultations/month
```

### **Cost Optimization Strategies**

#### **Docker Compose Scaling Strategy**
```yaml
Horizontal Scaling with Docker Compose:
  - Load balancer: nginx (free, $5/month for managed)
  - API instances: Scale with `docker compose up --scale api=3`
  - Database: PostgreSQL with read replicas
  - AI service: Multiple Ollama containers on separate ports
  
Cost-Effective Scaling:
  - Single server: 0-1K users ($25-45/month)
  - Multi-server: 1K-5K users ($100-200/month)
  - Container orchestration: 5K+ users ($300+/month)

Docker Resource Optimization:
  - Container resource limits prevent resource hogging
  - Health checks ensure service reliability
  - Volume mounts for data persistence
  - Network isolation for security
```

#### **Current Database Implementation**
```yaml
PostgreSQL in Docker:
  - Development: Single container with persistent volume
  - Production: Container with backup volumes and replication
  - Query optimization: SQLAlchemy ORM with indexes
  - Connection pooling: Built-in asyncpg connection management

Storage Optimization:
  - Hot data (recent symptoms): Primary PostgreSQL storage
  - Warm data (6+ months): Compressed tables with partitioning
  - Cold data (2+ years): Archive to separate volumes or S3
  - Cost reduction: 60-80% for historical data

Current Schema Efficiency:
  - Normalized tables with proper foreign keys
  - Indexes on frequently queried columns
  - UUID primary keys for security and distribution
  - Audit trails for compliance and debugging
```

## Current Operational Status (Dec 2025)

### **Deployment Architecture**
```yaml
Current Tech Stack:
  - Backend: FastAPI with async/await
  - Database: PostgreSQL 15 with asyncpg
  - Cache: Redis 7 for sessions and responses
  - AI Service: Ollama with llama3.2:3b model
  - Orchestration: Docker Compose with custom networks
  - Testing: 187 automated tests (31 compliance-focused)

Service Health Monitoring:
  - Health check endpoints: /health for all services
  - Container status: docker compose ps
  - Resource monitoring: docker stats
  - Log aggregation: docker compose logs
  - AI service status: Ollama API connectivity tests
```

### **Current Cost Breakdown**
```yaml
Development Environment:
  - Infrastructure: $0 (local Docker)
  - AI Processing: $0 (local Ollama)
  - External Services: $0 (no cloud dependencies)
  - Total Monthly: $0

Production Ready Deployment:
  - Single Server (DigitalOcean/Linode): $25-40/month
  - Domain + SSL: $1/month (amortized)
  - Monitoring: $0 (built-in Docker monitoring)
  - Backups: $5/month (automated volume snapshots)
  - Total Monthly: $30-50/month

Cost per User (at 1K users): $0.03-0.05/month
Cost per AI Assessment: $0 (after infrastructure)
```

## Monetization Guardrails

### **Freemium Model Controls (Future Implementation)**
```python
# app/core/usage_limits.py
class UsageLimitService:
    
    async def check_user_limits(self, user_id: str, action: str) -> bool:
        """Check if user can perform action within their tier limits"""
        
        user_tier = await self.get_user_tier(user_id)
        usage = await self.get_current_usage(user_id)
        
        limits = {
            "free": {
                "ai_assessments_per_month": 3,
                "pets_max": 2,
                "symptoms_per_month": 50
            },
            "premium": {
                "ai_assessments_per_month": 100,
                "pets_max": 10,
                "symptoms_per_month": 1000
            },
            "pro": {
                "ai_assessments_per_month": -1,  # Unlimited
                "pets_max": -1,
                "symptoms_per_month": -1
            }
        }
        
        user_limits = limits[user_tier]
        limit_key = f"{action}_per_month"
        
        if user_limits.get(limit_key, -1) == -1:
            return True  # Unlimited
        
        return usage.get(limit_key, 0) < user_limits[limit_key]
    
    async def track_usage(self, user_id: str, action: str):
        """Increment usage counter for user action"""
        month_key = datetime.now().strftime("%Y-%m")
        usage_key = f"usage:{user_id}:{month_key}:{action}"
        
        await redis.incr(usage_key)
        await redis.expire(usage_key, 86400 * 31)  # 31 days
```

### **Cost Monitoring & Alerts**
```python
# app/core/cost_monitoring.py
class CostMonitor:
    
    async def calculate_monthly_costs(self) -> Dict[str, float]:
        """Calculate current month's infrastructure costs"""
        
        costs = {
            "compute": await self.get_compute_costs(),
            "database": await self.get_database_costs(),
            "storage": await self.get_storage_costs(),
            "ai_api": await self.get_ai_api_costs(),
            "monitoring": await self.get_monitoring_costs()
        }
        
        total = sum(costs.values())
        
        # Alert if costs exceed budget
        if total > self.monthly_budget * 0.8:
            await self.send_cost_alert(costs, total)
        
        return costs
    
    async def predict_monthly_costs(self) -> float:
        """Predict end-of-month costs based on current usage"""
        
        current_day = datetime.now().day
        days_in_month = calendar.monthrange(datetime.now().year, datetime.now().month)[1]
        
        current_costs = await self.calculate_monthly_costs()
        total_current = sum(current_costs.values())
        
        # Linear prediction (can be made more sophisticated)
        predicted_total = (total_current / current_day) * days_in_month
        
        return predicted_total
```

## Incident Response Playbook

### **Severity Classifications**
```yaml
SEV1 - Critical (< 15min response):
  - Complete system outage
  - Data breach or security incident
  - AI providing dangerous medical advice
  - Payment system failure
  
SEV2 - High (< 1hr response):
  - Significant feature degradation
  - Database performance issues
  - AI service completely down
  - Authentication system problems

SEV3 - Medium (< 4hr response):
  - Minor feature issues
  - Performance degradation
  - Non-critical service failures
  - Integration problems

SEV4 - Low (< 24hr response):
  - Cosmetic bugs
  - Documentation issues
  - Minor usability problems
```

### **Incident Response Procedures**

#### **Current Docker Compose Incident Response**
```markdown
## Immediate Actions (0-15 minutes)
1. **Service Status Check**
   ```bash
   # Check all services
   docker compose ps
   
   # Check service logs
   docker compose logs --tail=50
   
   # Check resource usage
   docker stats
   ```

2. **Quick Service Recovery**
   ```bash
   # Restart specific service
   docker compose restart api
   
   # Full system restart
   docker compose down && docker compose up -d
   
   # Check AI service specifically
   docker compose exec ollama ollama list
   ```

3. **Health Verification**
   ```bash
   # API health check
   curl http://localhost:8000/health
   
   # Database connectivity
   docker compose exec postgres pg_isready
   
   # Redis connectivity
   docker compose exec redis redis-cli ping
   ```

## Investigation Phase (15-60 minutes)
1. **Container-Specific Debugging**
   ```bash
   # View detailed service logs
   docker compose logs api --since 1h
   
   # Check container resource usage
   docker compose exec api ps aux
   
   # Inspect container configuration
   docker compose config
   ```

2. **AI Service Diagnostics**
   ```bash
   # Test Ollama connectivity
   docker compose exec api python demo_scripts/ollama_direct_test.py
   
   # Check Ollama model status
   docker compose exec ollama ollama show llama3.2:3b
   
   # Monitor AI processing
   docker compose logs ollama -f
   ```
```

#### **AI Service Failure Response (Current Implementation)**
```python
# Current implementation in app/services/symptom.py
class SymptomService:
    
    async def create_assessment(self, assessment_data: SymptomAssessmentCreate):
        """Create assessment with AI fallback for service failures"""
        
        try:
            # Attempt AI analysis with Ollama
            ai_analysis = await self._analyze_symptoms_with_ai(
                str(assessment_data.pet_id), 
                symptoms_data
            )
            
            # Verify AI response contains required fields
            if not self._validate_ai_response(ai_analysis):
                raise ValueError("Invalid AI response format")
                
            return ai_analysis
            
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            # Ollama service failure - use rule-based fallback
            logger.warning(f"AI service failed: {e}. Using fallback rules.")
            
            return self._get_fallback_assessment(symptoms_data)
    
    def _get_fallback_assessment(self, symptoms: List[Dict]) -> Dict[str, Any]:
        """Rule-based fallback when Ollama is unavailable"""
        
        emergency_keywords = [
            "difficulty breathing", "seizure", "unconscious", 
            "severe bleeding", "poisoning", "trauma", "choking"
        ]
        
        high_priority_keywords = [
            "vomiting", "diarrhea", "lethargy", "loss of appetite"
        ]
        
        symptom_text = " ".join([
            s.get("symptom_name", "").lower() + " " + 
            s.get("description", "").lower() 
            for s in symptoms
        ])
        
        if any(keyword in symptom_text for keyword in emergency_keywords):
            urgency = "emergency"
            recommendations = [
                "Seek immediate veterinary care - this is an emergency",
                "Contact your veterinarian or emergency animal hospital now",
                "Do not wait - immediate professional attention required"
            ]
        elif any(keyword in symptom_text for keyword in high_priority_keywords):
            urgency = "high"
            recommendations = [
                "Schedule veterinary appointment within 24 hours",
                "Monitor your pet closely for any changes",
                "Provide comfort and ensure access to water"
            ]
        else:
            urgency = "moderate"
            recommendations = [
                "Monitor symptoms and contact veterinarian if they persist",
                "Ensure your pet is comfortable and hydrated",
                "Keep detailed notes about symptom changes"
            ]
        
        return {
            "urgency_level": urgency,
            "possible_causes": ["Multiple factors could contribute to these symptoms"],
            "recommendations": recommendations,
            "warning_signs": ["Worsening symptoms", "Loss of appetite", "Lethargy"],
            "medical_disclaimer": "This is a fallback assessment. Please consult a veterinarian.",
            "analysis": "Fallback Rules Applied - AI Service Unavailable"
        }
```

## Runbooks

### **Docker Compose Database Maintenance**
```markdown
## Monthly Database Maintenance (Current Implementation)

### Pre-maintenance Checklist
- [ ] Schedule maintenance window (low traffic period)
- [ ] Create database backup via Docker volume snapshot
- [ ] Verify backup integrity with test restore
- [ ] Prepare rollback procedures

### Maintenance Commands
1. **Create Database Backup**
   ```bash
   # Stop services gracefully
   docker compose stop api
   
   # Create PostgreSQL backup
   docker compose exec postgres pg_dump -U petuser -d petdb > backup_$(date +%Y%m%d).sql
   
   # Create volume backup
   docker run --rm -v capstone-final-project_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_volume_backup.tar.gz -C /data .
   ```

2. **Database Maintenance**
   ```bash
   # Access PostgreSQL container
   docker compose exec postgres psql -U petuser -d petdb
   
   # Run maintenance commands
   ANALYZE;
   VACUUM;
   REINDEX;
   ```

3. **Check Performance**
   ```sql
   -- Check table sizes
   SELECT tablename, pg_size_pretty(pg_total_relation_size(tablename::regclass)) 
   FROM pg_tables WHERE schemaname = 'public';
   
   -- Check index usage
   SELECT schemaname, tablename, attname, n_distinct, correlation 
   FROM pg_stats 
   WHERE tablename IN ('pets', 'symptoms', 'symptom_assessments');
   ```

### Post-maintenance Verification
- [ ] Restart all services: `docker compose up -d`
- [ ] Run health checks: `curl http://localhost:8000/health`
- [ ] Run compliance tests: `docker compose exec api python -m pytest tests/clause_control_tests/`
- [ ] Verify AI service: `docker compose exec api python demo_scripts/ollama_direct_test.py`
```

### **Docker Compose Deployment Runbook**
```markdown
## Production Deployment Process (Current Stack)

### Pre-deployment Checklist
- [ ] All 187 tests passing locally
- [ ] Docker images built and tagged
- [ ] Environment variables configured
- [ ] Database migration scripts prepared
- [ ] AI model (llama3.2:3b) available

### Deployment Steps
1. **Backup Current State**
   ```bash
   # Backup database
   docker compose exec postgres pg_dump -U petuser -d petdb > pre_deploy_backup.sql
   
   # Backup volumes
   docker run --rm -v capstone-final-project_postgres_data:/data alpine tar czf postgres_backup.tar.gz -C /data .
   ```

2. **Update Application**
   ```bash
   # Pull latest code
   git pull origin main
   
   # Rebuild containers with new code
   docker compose build
   
   # Apply database migrations (if any)
   docker compose exec postgres psql -U petuser -d petdb -f /migrations/latest.sql
   
   # Restart services with new images
   docker compose up -d
   ```

3. **Verification Steps**
   ```bash
   # Check all services are running
   docker compose ps
   
   # Health check
   curl http://localhost:8000/health
   
   # Test AI service
   docker compose exec api python demo_scripts/ollama_direct_test.py
   
   # Run critical compliance tests
   docker compose exec api python -m pytest tests/clause_control_tests/test_e1_medical_disclaimer.py -v
   ```

### Post-deployment Monitoring
- [ ] Monitor container logs: `docker compose logs -f`
- [ ] Check resource usage: `docker stats`
- [ ] Verify AI response quality with demo scripts
- [ ] Monitor error rates for 30 minutes
```

## Back-pressure & Kill Switches

### **Current FastAPI Rate Limiting**
```python
# app/core/rate_limiting.py (Future Implementation)
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from fastapi import Request, HTTPException

# Current rate limiting would be implemented as:
class CurrentRateLimiter:
    
    @staticmethod
    async def protect_ai_service(request: Request):
        """Protect Ollama AI service from overload"""
        
        # Check Ollama service health
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("http://ollama:11434/api/tags", timeout=1) as response:
                    if response.status != 200:
                        raise HTTPException(503, "AI service temporarily unavailable")
        except (aiohttp.ClientError, asyncio.TimeoutError):
            raise HTTPException(503, "AI service temporarily unavailable")
        
        # Check current AI processing load (future implementation)
        current_assessments = await redis.get("active_ai_assessments") or 0
        if int(current_assessments) > 5:  # Limit concurrent AI requests
            raise HTTPException(429, "AI service at capacity, please try again")
    
    @staticmethod  
    async def user_tier_limits(user_id: str) -> dict:
        """Current user limits (simplified)"""
        # For now, all users have same limits
        return {
            "ai_assessments_per_hour": 10,
            "api_requests_per_minute": 30
        }
```

### **Docker Compose Kill Switches**
```python
# app/core/kill_switches.py (Current Implementation Approach)
import os
from typing import Dict, Optional
from fastapi import HTTPException

class DockerKillSwitchManager:
    """Kill switch manager for Docker Compose deployment"""
    
    def __init__(self):
        # Use environment variables for kill switches
        self.switches = {
            "ai_service": os.getenv("ENABLE_AI_SERVICE", "true").lower() == "true",
            "user_registration": os.getenv("ENABLE_USER_REGISTRATION", "true").lower() == "true",
            "symptom_assessment": os.getenv("ENABLE_SYMPTOM_ASSESSMENT", "true").lower() == "true",
        }
    
    async def check_ai_service_health(self) -> bool:
        """Check if Ollama AI service is healthy"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "http://ollama:11434/api/tags", 
                    timeout=aiohttp.ClientTimeout(total=2)
                ) as response:
                    return response.status == 200
        except:
            return False
    
    async def emergency_disable_ai(self):
        """Emergency disable AI service"""
        # In Docker environment, this could stop the Ollama container
        # docker compose stop ollama
        
        # For now, set environment flag and restart
        os.environ["ENABLE_AI_SERVICE"] = "false"
        logger.critical("AI SERVICE EMERGENCY DISABLED")
    
    async def validate_service_availability(self, service: str):
        """Check if service should be available"""
        
        if service == "ai_assessment":
            if not self.switches.get("ai_service", True):
                raise HTTPException(503, "AI assessment temporarily disabled")
            
            if not await self.check_ai_service_health():
                raise HTTPException(503, "AI service health check failed")
        
        elif service == "user_registration":
            if not self.switches.get("user_registration", True):
                raise HTTPException(503, "User registration temporarily disabled")

# Usage in FastAPI endpoints
kill_switch_manager = DockerKillSwitchManager()

@router.post("/symptoms/assess")
async def assess_symptoms(request: SymptomAssessmentCreate):
    # Check kill switches before processing
    await kill_switch_manager.validate_service_availability("ai_assessment")
    
    # Proceed with assessment...
    return await symptom_service.create_assessment(request)

@router.post("/auth/register") 
async def register_user(user_data: UserCreate):
    # Check registration kill switch
    await kill_switch_manager.validate_service_availability("user_registration")
    
    # Proceed with registration...
    return await user_service.create_user(user_data)
```

### **Container Health Monitoring**
```bash
#!/bin/bash
# monitoring/health_check.sh - Current implementation approach

# Check all Docker Compose services
check_services() {
    echo "Checking Docker Compose service health..."
    
    # Check if all containers are running
    docker compose ps --format "table" | grep -v "Up" | grep -v "NAME" && {
        echo "ERROR: Some containers are not running"
        docker compose ps
        return 1
    }
    
    # Check API health
    curl -f http://localhost:8000/health || {
        echo "ERROR: API health check failed"
        return 1
    }
    
    # Check Ollama AI service
    curl -f http://localhost:11434/api/tags || {
        echo "ERROR: AI service health check failed"
        return 1
    }
    
    # Check PostgreSQL
    docker compose exec -T postgres pg_isready -U petuser || {
        echo "ERROR: Database health check failed" 
        return 1
    }
    
    # Check Redis
    docker compose exec -T redis redis-cli ping | grep -q "PONG" || {
        echo "ERROR: Redis health check failed"
        return 1
    }
    
    echo "All services healthy"
    return 0
}

# Auto-restart unhealthy services
auto_recovery() {
    if ! check_services; then
        echo "Attempting automatic service recovery..."
        
        # Restart all services
        docker compose restart
        
        # Wait for services to start
        sleep 30
        
        # Re-check health
        if check_services; then
            echo "Auto-recovery successful"
        else
            echo "Auto-recovery failed - manual intervention required"
            # Send alert (email, Slack, etc.)
        fi
    fi
}

# Run health check
check_services
```

This comprehensive operability guide now reflects the current Docker Compose implementation with realistic cost models, operational procedures, and monitoring approaches suitable for the current deployment architecture.