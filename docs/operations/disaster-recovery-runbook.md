# Disaster Recovery Runbook

*Last Updated: December 5, 2025*

**Related Documents:**
- [SLA/SLO Definitions](./sla-slo-definitions.md) - Service level requirements
- [Incident Response Playbook](./incident-response-playbook.md) - Emergency procedures
- [Deployment Instructions](./deployment-instructions.md) - System setup procedures

## Disaster Recovery Overview

### Recovery Objectives
- **Recovery Time Objective (RTO)**: 2 hours maximum downtime
- **Recovery Point Objective (RPO)**: 24 hours maximum data loss
- **Mean Time to Recovery (MTTR)**: Target 30 minutes for common failures

### Disaster Classifications

#### Level 1: Service Disruption
- Single container/service failure
- Partial functionality available
- **RTO**: 15 minutes | **RPO**: 0 hours

#### Level 2: Infrastructure Failure  
- Database corruption, host system failure
- Complete service unavailable
- **RTO**: 1 hour | **RPO**: 4 hours

#### Level 3: Complete System Loss
- Data center failure, multiple system corruption
- Full disaster recovery required
- **RTO**: 2 hours | **RPO**: 24 hours

## Pre-Disaster Preparation

### Backup Strategy

#### Automated Database Backups
```bash
# Daily PostgreSQL backup (configure as cron job)
#!/bin/bash
BACKUP_DIR="/backup/postgresql"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup with compression
docker compose exec postgres pg_dump -U postgres -d pettech_db | gzip > $BACKUP_DIR/pettech_backup_$DATE.sql.gz

# Retain last 30 days of backups
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete

# Verify backup integrity
gunzip -t $BACKUP_DIR/pettech_backup_$DATE.sql.gz
if [ $? -eq 0 ]; then
    echo "Backup $DATE completed successfully"
    # Upload to remote storage (AWS S3, Google Cloud, etc.)
else
    echo "ERROR: Backup $DATE failed integrity check"
    # Alert operations team
fi
```

#### Configuration Backup
```bash
# Backup Docker configurations and environment files
tar -czf /backup/config/docker_config_$(date +%Y%m%d).tar.gz \
    docker-compose.yml \
    .env \
    backend/Dockerfile \
    monitoring/ \
    scripts/
```

#### AI Model Backup
```bash
# Backup Ollama models and configurations
docker compose exec ollama ollama list > /backup/ai/ollama_models_$(date +%Y%m%d).txt
docker cp pet-health-ai-api-ollama-1:/root/.ollama/models /backup/ai/ollama_models_$(date +%Y%m%d)/
```

### Recovery Environment Setup

#### Standby Infrastructure
```yaml
# disaster-recovery-compose.yml
version: '3.8'
services:
  postgres-dr:
    image: postgres:15
    environment:
      - POSTGRES_DB=pettech_db_dr
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=${DR_DB_PASSWORD}
    volumes:
      - postgres_dr_data:/var/lib/postgresql/data
    ports:
      - "5433:5432"

  redis-dr:
    image: redis:7-alpine
    ports:
      - "6380:6379"
    volumes:
      - redis_dr_data:/data

volumes:
  postgres_dr_data:
  redis_dr_data:
```

## Disaster Recovery Procedures

### Level 1: Service Disruption Recovery

#### Single Container Failure
```bash
# 1. Identify failed service
docker compose ps

# 2. Check service logs
docker compose logs [service_name] --tail 50

# 3. Restart specific service
docker compose restart [service_name]

# 4. Verify service health
curl http://localhost:8000/health

# 5. Monitor for stability
docker compose logs [service_name] -f
```

#### Database Connection Issues
```bash
# 1. Check database container status
docker compose exec postgres pg_isready -U postgres

# 2. Restart database if needed
docker compose restart postgres

# 3. Verify API can connect
docker compose exec api python -c "from app.core.database import engine; print(engine.execute('SELECT 1').scalar())"

# 4. Check for connection pool issues
docker compose logs api | grep -i "database\|connection\|pool"
```

#### AI Service Failures
```bash
# 1. Check Ollama service status
docker compose exec ollama curl http://localhost:11434/api/tags

# 2. Restart Ollama and reload model
docker compose restart ollama
sleep 30
docker compose exec ollama ollama pull llama3.2:3b

# 3. Test AI assessment endpoint
curl -X POST http://localhost:8000/api/v1/symptoms/assess \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"pet_id": "<test_pet_id>"}'
```

### Level 2: Infrastructure Failure Recovery

#### Database Corruption Recovery
```bash
# 1. Stop all services immediately
docker compose down

# 2. Backup current corrupted state (for analysis)
sudo cp -r ./postgres_data ./postgres_data_corrupted_$(date +%Y%m%d)

# 3. Remove corrupted data
sudo rm -rf ./postgres_data

# 4. Start fresh database
docker compose up -d postgres

# 5. Restore from latest backup
LATEST_BACKUP=$(ls -t /backup/postgresql/*.sql.gz | head -1)
gunzip -c $LATEST_BACKUP | docker compose exec -T postgres psql -U postgres -d pettech_db

# 6. Verify data integrity
docker compose exec postgres psql -U postgres -d pettech_db -c "SELECT COUNT(*) FROM users;"

# 7. Start remaining services
docker compose up -d

# 8. Run health checks
./run-docker-tests.sh standard
```

#### Host System Recovery
```bash
# 1. Prepare new host system
# Install Docker and Docker Compose
curl -fsSL https://get.docker.com | sh
sudo curl -L "https://github.com/docker/compose/releases/download/v2.15.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 2. Restore application code
git clone <repository_url>
cd capstone-final-project

# 3. Restore configuration files
tar -xzf /backup/config/docker_config_latest.tar.gz

# 4. Restore database
docker compose up -d postgres
sleep 30
LATEST_BACKUP=$(ls -t /backup/postgresql/*.sql.gz | head -1)
gunzip -c $LATEST_BACKUP | docker compose exec -T postgres psql -U postgres -d pettech_db

# 5. Restore AI models
docker compose up -d ollama
sleep 60
docker compose exec ollama ollama pull llama3.2:3b

# 6. Start all services
docker compose up -d

# 7. Verify system functionality
./run-docker-tests.sh all
```

### Level 3: Complete System Loss Recovery

#### Full Environment Reconstruction
```bash
# 1. Provision new infrastructure
# - New host system or cloud instance
# - Minimum 8GB RAM, 50GB storage
# - Docker and Docker Compose installed

# 2. Clone repository
git clone <repository_url>
cd capstone-final-project

# 3. Restore environment configuration
# Download latest backup from remote storage
aws s3 cp s3://pettech-dr-bucket/config/latest.tar.gz ./
tar -xzf latest.tar.gz

# 4. Restore database from remote backup
aws s3 cp s3://pettech-dr-bucket/database/latest.sql.gz ./
docker compose up -d postgres
sleep 30
gunzip -c latest.sql.gz | docker compose exec -T postgres psql -U postgres -d pettech_db

# 5. Restore AI models
docker compose up -d ollama
sleep 60
# Restore from backup or re-download
docker compose exec ollama ollama pull llama3.2:3b

# 6. Start all services
docker compose up -d

# 7. Update DNS and routing (if applicable)
# Point domain to new IP address
# Update load balancer configuration

# 8. Comprehensive system validation
./run-docker-tests.sh all
curl http://localhost:8000/health
```

## Recovery Validation Procedures

### Post-Recovery Checklist

#### Data Integrity Verification
```bash
# 1. Verify user data
docker compose exec postgres psql -U postgres -d pettech_db -c "
SELECT 
  COUNT(*) as total_users,
  COUNT(CASE WHEN created_at > NOW() - INTERVAL '7 days' THEN 1 END) as recent_users
FROM users;"

# 2. Verify pet data
docker compose exec postgres psql -U postgres -d pettech_db -c "
SELECT 
  COUNT(*) as total_pets,
  COUNT(DISTINCT user_id) as users_with_pets
FROM pets;"

# 3. Verify symptom data integrity
docker compose exec postgres psql -U postgres -d pettech_db -c "
SELECT 
  COUNT(*) as total_symptoms,
  COUNT(CASE WHEN created_at > NOW() - INTERVAL '24 hours' THEN 1 END) as recent_symptoms
FROM symptoms;"
```

#### Functional Testing
```bash
# 1. Run automated test suite
./run-docker-tests.sh standard

# 2. Test critical user workflows
# Register new user
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "testpass123", "username": "testuser"}'

# 3. Test AI assessment functionality
# (Requires valid user token and pet ID)
curl -X POST http://localhost:8000/api/v1/symptoms/assess \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"pet_id": "<test_pet_id>"}'
```

#### Performance Validation
```bash
# 1. Check response times
curl -w "@curl-format.txt" http://localhost:8000/health

# 2. Verify AI service performance
time docker compose exec ollama ollama run llama3.2:3b "Test prompt"

# 3. Database performance check
docker compose exec postgres psql -U postgres -d pettech_db -c "EXPLAIN ANALYZE SELECT * FROM users LIMIT 10;"
```

## Communication Procedures

### Stakeholder Notification

#### During Disaster (Emergency Communication)
```markdown
Subject: [URGENT] Pet Health AI Service Disruption - [Level X]

Team,

We are experiencing a [Level X] service disruption affecting the Pet Health AI API.

**Impact**: [Brief description of user impact]
**Estimated Resolution**: [Time estimate]
**Current Status**: [What we're doing]

We will provide updates every 30 minutes until resolved.

Next update: [Time]
```

#### Post-Recovery Communication
```markdown
Subject: [RESOLVED] Pet Health AI Service Restored

Team,

The service disruption has been resolved as of [timestamp].

**Root Cause**: [Brief explanation]
**Duration**: [Total downtime]
**Data Loss**: [RPO achieved]
**Preventive Measures**: [Steps to prevent recurrence]

Full post-mortem will be available within 24 hours.
```

### Documentation Updates

#### Post-Recovery Actions
1. **Incident Log**: Document timeline, actions taken, lessons learned
2. **Runbook Updates**: Update procedures based on experience
3. **Backup Verification**: Validate backup and recovery processes
4. **Monitoring Enhancement**: Improve alerting for detected issues
5. **Training**: Share learnings with team members

## Continuous Improvement

### Monthly DR Testing
```bash
# Test backup restoration (staging environment)
# 1. Create test backup
# 2. Destroy test environment  
# 3. Restore from backup
# 4. Validate functionality
# 5. Document any issues

# Schedule: First Friday of each month
# Duration: 2 hours
# Owner: DevOps team
```

### Quarterly DR Simulation
- Full disaster recovery simulation
- External validation of procedures
- Team training and role playing
- Documentation review and updates
- Backup storage verification

### Annual DR Audit
- Complete review of all procedures
- Technology stack evaluation
- Recovery time objective validation
- Business continuity assessment
- Third-party audit consideration