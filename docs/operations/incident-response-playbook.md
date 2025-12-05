# Incident Response Playbook

*Last Updated: December 5, 2025*

**Related Documents:**
- [SLA/SLO Definitions](./sla-slo-definitions.md) - Service level requirements
- [Disaster Recovery Runbook](./disaster-recovery-runbook.md) - System recovery procedures
- [Monitoring Configuration](../testing/reliability-testing.md) - Observability setup

## Incident Classification & Response Times

### Severity Levels

#### P0 - Critical (Response: 15 minutes)
- Complete service outage affecting all users
- Data breach or security incident
- Data corruption or loss
- Payment/billing system failure

#### P1 - High (Response: 1 hour)
- Major functionality unavailable (AI assessments, user registration)
- Significant performance degradation (>5 second response times)
- Database connectivity issues affecting multiple users
- Authentication system failures

#### P2 - Medium (Response: 4 hours)
- Minor feature degradation
- Isolated user account issues
- Non-critical third-party integration failures
- Performance issues affecting <10% of users

#### P3 - Low (Response: Next business day)
- Documentation issues
- Minor UI/UX problems
- Non-essential feature requests
- Cosmetic bugs

## Incident Response Team

### Primary Roles

#### Incident Commander (IC)
- **Responsibility**: Overall incident coordination and decision making
- **Contact**: Primary on-call engineer
- **Backup**: Engineering team lead

#### Technical Lead
- **Responsibility**: Technical investigation and resolution
- **Contact**: Backend/DevOps specialist
- **Backup**: Senior developer

#### Communications Lead  
- **Responsibility**: Stakeholder communication and status updates
- **Contact**: Product manager or team lead
- **Backup**: Project coordinator

### Escalation Contacts
```yaml
Engineering Team:
  - Primary: aria231 (GitHub: @aria231)
  - Secondary: tc2780 (GitHub: @tc2780)

Faculty Advisor:
  - CPSC 436C Instructor
  - TA Team Contact

External Resources:
  - Docker Support (if container issues)
  - Ollama Community (if AI model issues)
```

## Incident Response Procedures

### Initial Response (First 15 minutes)

#### 1. Incident Detection
```bash
# Common alert sources
- Prometheus alerts (system metrics)
- Grafana dashboard anomalies
- User reports via GitHub issues
- Automated test failures
- Health check failures

# Immediate verification
curl http://localhost:8000/health
docker compose ps
docker compose logs --tail 50
```

#### 2. Initial Assessment
```yaml
Severity Assessment Questions:
- How many users are affected?
- What functionality is impacted?
- Is data at risk?
- Are there security implications?
- What is the business impact?

Technical Assessment:
- Which services are affected?
- Are error rates elevated?
- Is the database accessible?
- Are AI services responding?
- What do the logs indicate?
```

#### 3. Incident Declaration
```bash
# Create incident tracking issue
gh issue create --title "INCIDENT: [P0/P1/P2/P3] - Brief Description" \
  --body "**Severity**: P[X]
**Impact**: [Description]
**Start Time**: $(date)
**Status**: Investigating
**Assigned**: @username"

# Notify team (for P0/P1)
# Use configured notification channels (Slack, email, etc.)
```

### Investigation & Diagnosis

#### System Health Check
```bash
#!/bin/bash
# incident-health-check.sh

echo "=== INCIDENT HEALTH CHECK - $(date) ==="

echo "Container Status:"
docker compose ps

echo "Service Health:"
curl -s http://localhost:8000/health || echo "API Health Check FAILED"

echo "Database Connectivity:"
docker compose exec postgres pg_isready -U postgres || echo "Database FAILED"

echo "AI Service:"
docker compose exec ollama curl -s http://localhost:11434/api/tags || echo "Ollama FAILED"

echo "Recent Errors (Last 100 lines):"
docker compose logs --tail 100 | grep -i "error\|exception\|failed"

echo "Resource Usage:"
docker stats --no-stream

echo "Disk Space:"
df -h

echo "=== END HEALTH CHECK ==="
```

#### Log Analysis
```bash
# Check for common error patterns
docker compose logs api | grep -E "(500|error|exception|failed)" | tail -20

# Database connection issues
docker compose logs api | grep -i "database\|connection\|pool"

# AI service issues  
docker compose logs ollama | grep -E "(error|failed|timeout)"

# Authentication/JWT issues
docker compose logs api | grep -i "jwt\|auth\|token"

# Export logs for analysis
docker compose logs > incident_logs_$(date +%Y%m%d_%H%M).txt
```

#### Performance Investigation
```bash
# Check response times
for endpoint in health api/v1/auth/me api/v1/pets; do
  echo "Testing $endpoint:"
  curl -w "Time: %{time_total}s\n" -o /dev/null -s http://localhost:8000/$endpoint
done

# Database query performance
docker compose exec postgres psql -U postgres -d pettech_db -c "
SELECT query, calls, total_time, mean_time 
FROM pg_stat_statements 
ORDER BY total_time DESC LIMIT 10;"

# AI inference times
docker compose logs ollama | grep -E "processing|inference|response" | tail -10
```

### Resolution Procedures

#### Common Resolution Steps

#### API Service Issues
```bash
# 1. Check API container status
docker compose ps api

# 2. Restart API service
docker compose restart api

# 3. Verify startup logs
docker compose logs api --tail 50 -f

# 4. Test critical endpoints
curl http://localhost:8000/health
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password"}'
```

#### Database Connection Issues
```bash
# 1. Check database status
docker compose exec postgres pg_isready -U postgres

# 2. Check connection pool
docker compose logs api | grep -i "pool\|connection" | tail -10

# 3. Restart database (last resort)
docker compose restart postgres
sleep 30
docker compose restart api

# 4. Verify connectivity
docker compose exec api python -c "
from app.core.database import engine
print('DB Connection:', engine.execute('SELECT 1').scalar())
"
```

#### AI Service Failures
```bash
# 1. Check Ollama status
docker compose exec ollama ps aux | grep ollama

# 2. Verify model availability
docker compose exec ollama ollama list

# 3. Test model inference
docker compose exec ollama ollama run llama3.2:3b "Hello world"

# 4. Restart if necessary
docker compose restart ollama
sleep 60
docker compose exec ollama ollama pull llama3.2:3b

# 5. Verify AI endpoint
curl -X POST http://localhost:8000/api/v1/symptoms/assess \
  -H "Authorization: Bearer <valid_token>" \
  -H "Content-Type: application/json" \
  -d '{"pet_id": "<valid_pet_id>"}'
```

#### High Load/Performance Issues
```bash
# 1. Check resource utilization
docker stats --no-stream

# 2. Scale services if needed (development approach)
# Restart services to clear memory leaks
docker compose restart

# 3. Check for memory leaks
docker compose logs api | grep -i "memory\|oom"

# 4. Database optimization
docker compose exec postgres psql -U postgres -d pettech_db -c "
REINDEX DATABASE pettech_db;
VACUUM ANALYZE;
"
```

### Communication Templates

#### Initial Notification (P0/P1)
```markdown
Subject: [INCIDENT P{X}] Pet Health AI Service Issues

We are currently investigating service issues with the Pet Health AI API.

**Impact**: {Brief description of user impact}
**Started**: {timestamp}
**Current Status**: Investigating
**Next Update**: {15-30 minutes}

We will provide updates every 15 minutes until resolved.

Incident Tracking: GitHub Issue #{number}
```

#### Progress Update
```markdown
Subject: [UPDATE] Pet Health AI Service Incident

**Update #{number}** - {timestamp}

**Current Status**: {Investigating/Identified/Resolving/Monitoring}
**Progress**: {What we've found/done}
**Next Steps**: {What we're doing next}
**ETA**: {If known}

Next update in {time period} or when status changes.
```

#### Resolution Notification
```markdown
Subject: [RESOLVED] Pet Health AI Service Restored

The Pet Health AI service incident has been resolved.

**Resolution Time**: {timestamp}
**Duration**: {total duration}
**Root Cause**: {brief explanation}
**Fix Applied**: {what was done}

**Follow-up Actions**:
- Post-mortem scheduled for {date}
- Preventive measures being implemented
- Monitoring enhanced

Thank you for your patience.
```

### Post-Incident Activities

#### Immediate Post-Resolution (within 2 hours)
```bash
# 1. Verify full system functionality
./run-docker-tests.sh standard

# 2. Monitor for recurrence
# Check key metrics for 1 hour
watch -n 60 'curl -w "Time: %{time_total}s\n" -o /dev/null -s http://localhost:8000/health'

# 3. Document timeline
# Update incident GitHub issue with complete timeline
```

#### Post-Incident Review (within 48 hours)

#### Post-Mortem Template
```markdown
# Post-Mortem: {Date} - {Brief Incident Description}

## Incident Summary
- **Date/Time**: {Start} - {End}
- **Duration**: {Total downtime}
- **Impact**: {User/system impact}
- **Severity**: P{X}

## Timeline
| Time | Event | Action Taken |
|------|-------|--------------|
| {time} | {event} | {action} |

## Root Cause Analysis
### Primary Cause
{Detailed explanation of what caused the incident}

### Contributing Factors
- {Factor 1}
- {Factor 2}

## Resolution
### What Fixed It
{Description of the resolution}

### Why It Worked
{Technical explanation}

## Lessons Learned
### What Went Well
- {Positive aspects}

### What Could Be Improved
- {Areas for improvement}

## Action Items
- [ ] {Preventive action} - Owner: {name} - Due: {date}
- [ ] {Process improvement} - Owner: {name} - Due: {date}
- [ ] {Monitoring enhancement} - Owner: {name} - Due: {date}

## Prevention
### Immediate Actions (next 7 days)
- {Immediate fixes}

### Short-term Actions (next 30 days)  
- {Monitoring/alerting improvements}

### Long-term Actions (next quarter)
- {Architecture/process changes}
```

### Incident Metrics Tracking

#### Key Metrics to Track
```yaml
Response Metrics:
- Time to Detection (TTD)
- Time to Acknowledgment (TTA)  
- Time to Resolution (TTR)
- Time to Recovery (TTRec)

Impact Metrics:
- Users Affected
- Functionality Impact Percentage
- Data Loss (if any)
- Revenue Impact (if applicable)

Process Metrics:
- Communication Effectiveness
- Escalation Appropriateness
- Team Coordination Quality
- Documentation Completeness
```

#### Monthly Incident Review
- Analyze incident trends and patterns
- Review response time performance against SLA
- Identify recurring issues requiring architectural changes
- Update runbooks based on lessons learned
- Team training needs assessment

### Incident Prevention

#### Proactive Measures
```bash
# 1. Regular health monitoring
# Set up Prometheus alerts for key metrics

# 2. Automated testing in production
# Scheduled smoke tests every hour
cron: "0 * * * * curl -f http://localhost:8000/health || echo 'Health check failed'"

# 3. Capacity monitoring
# Alert on resource utilization trends

# 4. Dependency health checks
# Monitor external service availability

# 5. Log analysis automation
# Set up log aggregation and automated anomaly detection
```

#### Team Preparedness
- Monthly incident response drills
- Runbook updates and validation
- Cross-training for critical system knowledge
- Emergency contact list maintenance
- Tool access verification and updates