# Cost Model & Operability Guide

## Cost Model Analysis

### **Development Phase Costs**

#### **Zero-Cost Development Setup**
```yaml
Local Development (Free):
  - Hardware: Developer laptop (existing)
  - Software: All open-source tools
  - Docker Desktop: Free for individual use
  - Ollama + Local LLM: Free forever
  - GitHub: Free tier for public repos
  - IDE: VS Code (free)
  - Total: $0/month
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

#### **Local LLM (Ollama) - Recommended**
```yaml
Infrastructure Costs:
  - GPU Server (development): $0 (use laptop)
  - GPU Server (production): $150-300/month
  - Model storage: 7GB (one-time download)
  - Processing: No per-request costs
  - Scaling: Linear with server costs

Cost per AI Request: $0.00 (after infrastructure)
Monthly at 10K requests: $0.00
Monthly at 100K requests: $0.00
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

#### **Infrastructure Optimization**
```yaml
Auto-scaling Configuration:
  - Minimum instances: 2 (high availability)
  - Scale up trigger: CPU > 70% for 5 minutes
  - Scale down trigger: CPU < 30% for 10 minutes
  - Maximum instances: 10
  
Cost Savings:
  - Off-peak scaling: 40-60% cost reduction
  - Spot instances: Additional 50-70% savings
  - Reserved instances: 30-50% discount for 1-year commit
```

#### **Database Cost Management**
```yaml
Database Optimization:
  - Read replicas for analytics: $20/month
  - Query optimization: 30-50% performance improvement
  - Connection pooling: Reduce connection overhead
  - Automated backups: 7-day retention included

Storage Tiering:
  - Hot data (recent symptoms): SSD storage
  - Warm data (6+ months): HDD storage  
  - Cold data (2+ years): Archive storage
  - Cost reduction: 60-80% for historical data
```

## Monetization Guardrails

### **Freemium Model Controls**
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

#### **SEV1 - System Outage Response**
```markdown
## Immediate Actions (0-15 minutes)
1. **Acknowledge Alert**
   - Page on-call engineer immediately
   - Update status page: "Investigating issue"
   - Start incident bridge call

2. **Initial Assessment**
   - Check health dashboard
   - Verify monitoring systems operational
   - Identify affected services and user impact

3. **Emergency Mitigation**
   - Apply immediate fixes if obvious
   - Consider fallback to backup systems
   - Implement read-only mode if necessary

## Investigation Phase (15-60 minutes)
1. **Root Cause Analysis**
   - Check recent deployments
   - Review system logs and metrics
   - Identify timeline of events

2. **Communication**
   - Update stakeholders every 15 minutes
   - Provide ETA for resolution if known
   - Prepare user communication

3. **Fix Implementation**
   - Apply fix in staging first if possible
   - Monitor metrics during deployment
   - Verify fix resolves issue

## Recovery Phase (1+ hours)
1. **System Validation**
   - Run health checks
   - Verify all services operational
   - Check data integrity

2. **Post-Incident**
   - Update status page: "Resolved"
   - Schedule post-mortem within 48 hours
   - Document lessons learned
```

#### **AI Service Failure Response**
```python
# app/core/ai_fallback.py
class AIFallbackService:
    
    async def handle_ai_service_failure(self, pet_data: dict, symptoms: list):
        """Provide fallback response when AI service fails"""
        
        # Check for emergency symptoms first
        emergency_keywords = [
            "difficulty breathing", "seizure", "unconscious", 
            "severe bleeding", "poisoning", "trauma"
        ]
        
        symptom_text = " ".join([s.get("description", "") for s in symptoms]).lower()
        
        if any(keyword in symptom_text for keyword in emergency_keywords):
            return {
                "urgency_level": "emergency",
                "message": "EMERGENCY: Seek immediate veterinary care",
                "recommendations": [
                    "Contact your veterinarian or emergency animal hospital immediately",
                    "Do not wait for AI analysis - this requires immediate attention"
                ],
                "fallback_reason": "AI service unavailable - emergency protocol activated"
            }
        
        # Provide conservative guidance for non-emergency cases
        return {
            "urgency_level": "moderate",
            "message": "AI analysis temporarily unavailable",
            "recommendations": [
                "Monitor your pet closely",
                "Contact your veterinarian if symptoms persist or worsen",
                "Keep detailed notes about symptom changes"
            ],
            "fallback_reason": "AI service unavailable - conservative guidance provided"
        }
```

## Runbooks

### **Database Maintenance Runbook**
```markdown
## Monthly Database Maintenance

### Pre-maintenance Checklist
- [ ] Schedule maintenance window (low traffic period)
- [ ] Notify stakeholders 48 hours in advance
- [ ] Create full database backup
- [ ] Verify backup integrity
- [ ] Prepare rollback procedures

### Maintenance Tasks
1. **Update Statistics**
   ```sql
   ANALYZE;
   VACUUM;
   REINDEX;
   ```

2. **Check Index Usage**
   ```sql
   SELECT schemaname, tablename, attname, n_distinct, correlation 
   FROM pg_stats 
   WHERE tablename IN ('pets', 'symptoms', 'assessments');
   ```

3. **Archive Old Data**
   - Move symptoms > 2 years to archive tables
   - Compress old assessment data
   - Update retention policies

### Post-maintenance Verification
- [ ] Verify all services operational
- [ ] Check response times within SLA
- [ ] Validate recent data integrity
- [ ] Monitor for any performance issues
```

### **Deployment Runbook**
```markdown
## Production Deployment Process

### Pre-deployment
- [ ] Code review approved
- [ ] All tests passing
- [ ] Database migrations tested
- [ ] Feature flags configured
- [ ] Rollback plan documented

### Deployment Steps
1. **Enable Maintenance Mode** (if required)
   ```bash
   kubectl patch deployment api -p '{"spec":{"replicas":0}}'
   kubectl apply -f maintenance-page.yaml
   ```

2. **Database Migration**
   ```bash
   kubectl exec -it postgres-pod -- psql -U petuser -d petdb -f /migrations/latest.sql
   ```

3. **Application Deployment**
   ```bash
   kubectl set image deployment/api api=pethealth/api:v1.2.3
   kubectl rollout status deployment/api
   ```

4. **Smoke Tests**
   - Health check endpoints
   - Authentication flow
   - Basic API functionality
   - AI service connectivity

### Post-deployment
- [ ] Monitor error rates for 30 minutes
- [ ] Verify all features working
- [ ] Check performance metrics
- [ ] Disable maintenance mode
```

## Back-pressure & Kill Switches

### **Rate Limiting Implementation**
```python
# app/core/rate_limiting.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)

class AdvancedRateLimiter:
    
    @staticmethod
    async def adaptive_rate_limit(request, user_tier: str):
        """Apply different rate limits based on user tier"""
        
        limits = {
            "free": "10/minute",
            "premium": "100/minute", 
            "pro": "1000/minute"
        }
        
        return limits.get(user_tier, "5/minute")
    
    @staticmethod
    async def ai_service_protection():
        """Protect AI service from overload"""
        
        current_load = await get_ai_service_load()
        
        if current_load > 0.8:  # 80% capacity
            # Implement back-pressure
            return "1/minute"  # Severely limited
        elif current_load > 0.6:  # 60% capacity
            return "5/minute"  # Moderately limited
        else:
            return "30/minute"  # Normal rate
```

### **Circuit Breaker Kill Switches**
```python
# app/core/kill_switches.py
class KillSwitchManager:
    
    def __init__(self):
        self.switches = {
            "ai_service": True,
            "user_registration": True,
            "symptom_logging": True,
            "premium_features": True
        }
    
    async def disable_feature(self, feature: str, reason: str):
        """Emergency disable of system features"""
        
        await redis.set(f"killswitch:{feature}", "disabled")
        await redis.set(f"killswitch:{feature}:reason", reason)
        
        # Log the kill switch activation
        logger.critical(f"KILL SWITCH ACTIVATED: {feature} - {reason}")
        
        # Send alert to operations team
        await self.send_kill_switch_alert(feature, reason)
    
    async def is_feature_enabled(self, feature: str) -> bool:
        """Check if feature is enabled"""
        
        status = await redis.get(f"killswitch:{feature}")
        return status != "disabled"
    
    # Usage in API endpoints
    async def protected_endpoint(self, feature_name: str):
        if not await self.is_feature_enabled(feature_name):
            raise HTTPException(
                status_code=503,
                detail=f"Service temporarily unavailable"
            )

# Middleware to check kill switches
async def kill_switch_middleware(request: Request, call_next):
    endpoint = request.url.path
    
    kill_switch_map = {
        "/auth/register": "user_registration",
        "/ai-vet": "ai_service", 
        "/symptoms": "symptom_logging"
    }
    
    for pattern, switch in kill_switch_map.items():
        if pattern in endpoint:
            if not await kill_switch_manager.is_feature_enabled(switch):
                return JSONResponse(
                    status_code=503,
                    content={"error": "Service temporarily unavailable"}
                )
    
    return await call_next(request)
```

This comprehensive operability guide ensures smooth system operation with proper cost controls, incident response procedures, and emergency controls.