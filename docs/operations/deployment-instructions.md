# Deployment Instructions

*Last Updated: December 5, 2025*

**Current Implementation:** Docker Compose with FastAPI, PostgreSQL, Redis, and Ollama llama3.2:3b

**Related Documents:**
- [Cost & Operability Guide](./cost-operability.md) - Cost analysis and operational procedures
- [Trust Model](../compliance/trust-model.md) - Security considerations and threat model

## Prerequisites

### **System Requirements (Updated Dec 2025)**
- Docker Desktop 4.20+ with Docker Compose V2
- 8GB+ RAM (4GB for Ollama llama3.2:3b, 4GB for other services)
- 20GB+ free disk space (2GB for AI model, 18GB for containers and data)
- Git 2.30+
- Internet connection for initial model download

### **Hardware Recommendations**
```yaml
Development (Local):
  - CPU: 4+ cores (for AI processing)
  - RAM: 8GB minimum, 16GB recommended
  - Storage: 20GB available space
  - OS: macOS, Linux, or Windows with WSL2

Production (VPS/Cloud):
  - CPU: 2+ cores minimum, 4+ cores recommended
  - RAM: 4GB minimum, 8GB recommended  
  - Storage: 50GB+ SSD storage
  - Network: 1Gbps connection recommended
```

### **Account Setup (For Production)**
```yaml
Required Services:
  - GitHub: Source code hosting (free for public repos)
  - VPS Provider: DigitalOcean, Linode, or AWS EC2 ($20-40/month)
  - Domain Registrar: Namecheap, Cloudflare, etc. ($10-15/year)
  - SSL Certificate: Let's Encrypt (free) or Cloudflare (free)

Optional Services:
  - Monitoring: Grafana Cloud (free tier) or self-hosted
  - Backup Storage: AWS S3, Backblaze B2 ($5/month)
  - CDN: Cloudflare (free) or AWS CloudFront
```

## Local Development Setup

### **1. Clone and Setup Repository**
```bash
# Clone the repository
git clone https://github.com/tracychow/cpsc-436c/capstone-final-project
cd capstone-final-project

# Verify Docker Compose installation
docker compose version

# Check system resources
docker system info | grep -E 'CPUs|Total Memory'
```

### **2. Environment Configuration**
```bash
# The repository already includes a working docker-compose.yml
# No additional environment files needed for basic development

# Optional: Create custom environment overrides
cat > docker-compose.override.yml << 'EOF'
version: '3.8'
services:
  api:
    environment:
      - LOG_LEVEL=DEBUG
      - ENVIRONMENT=development
  postgres:
    ports:
      - "5432:5432"  # Expose PostgreSQL for external tools
  redis:
    ports:
      - "6379:6379"  # Expose Redis for external tools
EOF
```

### **3. Docker Compose Startup**
```bash
# Start all services (API, PostgreSQL, Redis, Ollama)
docker compose up -d

# Verify all services are running
docker compose ps

# Expected output:
# NAME                                    IMAGE               STATUS
# capstone-final-project-api-1           backend_api         Up
# capstone-final-project-postgres-1      postgres:15         Up  
# capstone-final-project-redis-1         redis:7-alpine      Up
# capstone-final-project-ollama-1        ollama/ollama       Up

# Check service health
curl http://localhost:8000/health
# Expected: {"status": "healthy", "database": "connected", "redis": "connected"}
```

### **4. AI Model Setup (Critical Step)**
```bash
# Download the llama3.2:3b model (this will take a few minutes)
docker compose exec ollama ollama pull llama3.2:3b

# Verify model is available
docker compose exec ollama ollama list
# Expected output showing llama3.2:3b model

# Alternative: Use faster but less accurate model for development
docker compose exec ollama ollama pull llama3.2:1b

# Test AI service directly
curl http://localhost:11434/api/tags
# Expected: JSON response with available models
```

### **5. Database Initialization**
```bash
# Database is automatically initialized via Docker
# Check database connectivity
docker compose exec postgres psql -U petuser -d petdb -c "SELECT version();"

# View database tables (should show pets, symptoms, users, etc.)
docker compose exec postgres psql -U petuser -d petdb -c "\dt"
```

### **6. Validate Installation**

#### **Quick Health Check**
```bash
# API health endpoint
curl http://localhost:8000/health
# Expected: {"status": "healthy", "database": "connected", "redis": "connected"}

# API documentation
curl http://localhost:8000/docs
# Expected: OpenAPI/Swagger documentation page

# Test AI service integration
docker compose exec api python demo_scripts/ollama_direct_test.py
# Expected: ✅ AI connectivity test passing
```

#### **Run Demo Scripts**
```bash
# Interactive demo launcher
docker compose exec api python demo_scripts/run_demo.py

# Menu options:
# 1. 🔌 Ollama Connectivity Test (~5 seconds)
# 2. 🏥 AI Veterinary Analysis Demo (~30-60 seconds)  
# 3. 🔧 Service Integration Test (~20-40 seconds)
# 4. 🔄 End-to-End Workflow Test (~10-20 seconds)

# Quick validation: Run option 1 to verify AI is working
```

#### **Comprehensive Testing**
```bash
# Navigate to backend directory
cd backend

# Run core integration tests
docker compose exec api python -m pytest tests/integration/test_health_and_general.py -v
# Expected: All health and API endpoint tests pass

# Run authentication tests  
docker compose exec api python -m pytest tests/integration/test_auth.py -v
# Expected: User registration, login, JWT validation pass

# Run AI integration tests
docker compose exec api python -m pytest tests/ai/test_ollama_integration.py -v
# Expected: AI service connectivity and response validation pass

# Run compliance tests
docker compose exec api python -m pytest tests/clause_control_tests/ -v
# Expected: All privacy and ethics compliance tests pass
```

### **7. Development Workflow**

```bash
# Monitor all service logs
docker compose logs -f

# Monitor specific service
docker compose logs -f api
docker compose logs -f ollama

# Restart services after code changes
docker compose restart api

# Rebuild containers after dependency changes
docker compose build api
docker compose up -d api

# Stop all services
docker compose down

# Stop and remove volumes (full reset)
docker compose down -v
```

## **6. Monitoring and Maintenance**

### **Health Checks**
```bash
# Container health
docker compose ps
docker compose logs api

# Database connectivity  
docker compose exec postgres pg_isready -U petuser

# API health
curl http://localhost:8000/health

# Redis connectivity
docker compose exec redis redis-cli ping

# Ollama model status
docker compose exec ollama ollama list
```

### **Log Management**
```bash
# View logs
docker compose logs -f api
docker compose logs --tail=100 postgres
docker compose logs ollama

# Log rotation (production)
cat > /etc/logrotate.d/docker-compose << 'EOF'
/var/lib/docker/containers/*/*-json.log {
    rotate 7
    daily
    compress
    size=1M
    missingok
    delaycompress
    copytruncate
}
EOF
```

### **Performance Monitoring**
```bash
# Check system resources
docker stats

# Monitor AI model performance
curl -X POST http://localhost:8000/api/v1/ai/test \
  -H "Content-Type: application/json" \
  -d '{"pet_id": "test-123"}'

# Database performance
docker compose exec postgres psql -U petuser -d petdb -c "
SELECT schemaname,tablename,n_tup_ins,n_tup_upd,n_tup_del 
FROM pg_stat_user_tables;"
```

### **8. Troubleshooting Common Issues**

#### **Ollama Model Not Loading**
```bash
# Check Ollama service status
docker compose ps ollama

# Check Ollama logs
docker compose logs ollama

# Manually pull model if missing
docker compose exec ollama ollama pull llama3.2:3b

# Verify model is available
docker compose exec ollama ollama list

# Test AI functionality
curl -X POST http://localhost:8000/api/v1/ai/test \
  -H "Content-Type: application/json" \
  -d '{"pet_id": "test-123"}'
```

#### **Database Connection Issues**
```bash
# Check PostgreSQL status
docker compose ps postgres

# Test database connectivity
docker compose exec postgres pg_isready -U petuser

# Check database logs
docker compose logs postgres

# Reset database if needed
docker compose down
docker volume rm capstone-final-project_postgres_data
docker compose up -d

# Verify tables exist
docker compose exec postgres psql -U petuser -d petdb -c "\dt"
```

#### **API Service Not Responding**
```bash
# Check API container status
docker compose ps api

# Check API logs for errors
docker compose logs api --tail=50

# Test API endpoints
curl http://localhost:8000/health
curl http://localhost:8000/docs

# Restart API service
docker compose restart api

# Rebuild if needed
docker compose build api --no-cache
```

#### **Redis Connection Issues**
```bash
# Check Redis status
docker compose ps redis

# Test Redis connectivity
docker compose exec redis redis-cli ping

# Check Redis logs
docker compose logs redis

# Restart Redis if needed
docker compose restart redis
```

#### **Port Already in Use**
```bash
# Check what's using port 8000
lsof -i :8000

# Stop conflicting services
sudo kill -9 $(lsof -t -i:8000)

# Or use different port
PORT=8001 docker compose up -d
```

### **9. Data Backup and Recovery**

#### **Database Backup**
```bash
# Create backup
docker compose exec postgres pg_dump -U petuser petdb > backup_$(date +%Y%m%d).sql

# Restore from backup
docker compose exec -T postgres psql -U petuser petdb < backup_20231201.sql
```

#### **Volume Backup**
```bash
# Backup all volumes
docker run --rm \
  -v capstone-final-project_postgres_data:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/postgres_backup_$(date +%Y%m%d).tar.gz /data

# Restore volume
docker volume create capstone-final-project_postgres_data
docker run --rm \
  -v capstone-final-project_postgres_data:/data \
  -v $(pwd):/backup \
  alpine tar xzf /backup/postgres_backup_20231201.tar.gz -C /
```

## **7. Production Considerations**

### **Security Checklist**
- [ ] Change default database passwords
- [ ] Generate secure JWT secret (min 32 chars)
- [ ] Enable HTTPS with SSL certificates
- [ ] Configure firewall rules
- [ ] Set up log monitoring
- [ ] Regular security updates

### **Performance Optimization**
- [ ] Ollama model optimization for production
- [ ] Database connection pooling
- [ ] Redis caching configuration
- [ ] Load balancing for multiple instances
- [ ] Resource monitoring and alerts

### **High Availability Setup**
```bash
# Multiple API instances
docker compose up -d --scale api=3

# Load balancer configuration (nginx)
upstream pet_api {
    server localhost:8001;
    server localhost:8002;
    server localhost:8003;
}
```

# Restart API service
docker compose restart api

# Rebuild if code changes
docker compose build api
docker compose up -d api
```

## Production Deployment

### **Recommended: VPS with Docker Compose**

#### **Step 1: Server Setup**
```bash
# Choose a VPS provider (recommended specs for production):
# - DigitalOcean: $20/month droplet (2 CPU, 4GB RAM, 80GB SSD)
# - Linode: $24/month (2 CPU, 4GB RAM, 80GB SSD)
# - Vultr: $20/month (2 CPU, 4GB RAM, 80GB SSD)

# Connect to your server
ssh root@your-server-ip

# Update system packages
apt update && apt upgrade -y

# Install Docker and Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose (if not included)
apt install docker-compose-plugin

# Create application user
useradd -m -s /bin/bash petapi
usermod -aG docker petapi

# Setup firewall
ufw allow ssh
ufw allow 80
ufw allow 443
ufw --force enable
```

#### **Step 2: Application Deployment**
```bash
# Switch to application user
su - petapi

# Clone repository
git clone https://github.com/yourusername/capstone-final-project
cd capstone-final-project

# Create production compose file
cat > docker-compose.prod.yml << 'EOF'
version: '3.8'

services:
  api:
    build: ./backend
    restart: unless-stopped
    environment:
      - ENVIRONMENT=production
      - DATABASE_URL=postgresql://petuser:${DB_PASSWORD}@postgres:5432/petdb
      - REDIS_URL=redis://redis:6379
      - JWT_SECRET=${JWT_SECRET}
      - OLLAMA_BASE_URL=http://ollama:11434
      - OLLAMA_MODEL=llama3.2:3b
    depends_on:
      - postgres
      - redis
      - ollama
    volumes:
      - ./logs:/app/logs
    networks:
      - app-network

  postgres:
    image: postgres:15
    restart: unless-stopped
    environment:
      - POSTGRES_DB=petdb
      - POSTGRES_USER=petuser
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    networks:
      - app-network

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    volumes:
      - redis_data:/data
    networks:
      - app-network

  ollama:
    image: ollama/ollama:latest
    restart: unless-stopped
    volumes:
      - ollama_data:/root/.ollama
    networks:
      - app-network

  nginx:
    image: nginx:alpine
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - api
    networks:
      - app-network

volumes:
  postgres_data:
  redis_data:
  ollama_data:

networks:
  app-network:
    driver: bridge
EOF

# Create secure environment file
cat > .env.production << 'EOF'
DB_PASSWORD=$(openssl rand -hex 32)
JWT_SECRET=$(openssl rand -hex 64)
EOF

# Source environment variables
source .env.production
```

#### **Step 3: Nginx Configuration**
```bash
# Create nginx configuration
cat > nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    upstream api {
        server api:8000;
    }

    server {
        listen 80;
        server_name yourdomain.com;

        # Redirect HTTP to HTTPS
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name yourdomain.com;

        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;

        location / {
            proxy_pass http://api;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /health {
            proxy_pass http://api;
            access_log off;
        }
    }
}
EOF
```

#### **Step 4: SSL Certificate Setup**
```bash
# Install certbot
apt install certbot

# Temporarily start nginx for domain verification
docker compose -f docker-compose.prod.yml up nginx -d

# Get SSL certificate
certbot certonly --webroot -w /var/lib/letsencrypt/ -d yourdomain.com

# Copy certificates to nginx volume
mkdir -p ssl
cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem ssl/
cp /etc/letsencrypt/live/yourdomain.com/privkey.pem ssl/

# Setup automatic renewal
echo "0 12 * * * /usr/bin/certbot renew --quiet" | crontab -
```

#### **Step 5: Deploy Application**
```bash
# Start all services
docker compose -f docker-compose.prod.yml up -d

# Verify services are running
docker compose -f docker-compose.prod.yml ps

# Download AI model
docker compose -f docker-compose.prod.yml exec ollama ollama pull llama3.2:3b

# Test deployment
curl https://yourdomain.com/health
```

### **Alternative: Docker Hub + Cloud Deploy**

#### **For Cloud Platforms (Railway, Heroku, etc.)**
```bash
# Build and push Docker image
docker build -t yourusername/pet-health-api:latest ./backend
docker push yourusername/pet-health-api:latest

# Note: Cloud platforms may not support Ollama due to resource constraints
# Consider using OpenAI API for cloud deployments:

# Add to environment variables:
# AI_PROVIDER=openai
# OPENAI_API_KEY=your-openai-key
# OLLAMA_BASE_URL=  # Leave empty for OpenAI mode
```

#### **Simplified Cloud Deployment**
```yaml
# For platforms that support Docker Compose (some VPS providers)
# Use this simplified compose file:

version: '3.8'
services:
  app:
    image: yourusername/pet-health-api:latest
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}  
      - JWT_SECRET=${JWT_SECRET}
      - AI_PROVIDER=openai
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    ports:
      - "8000:8000"
```

## Database Migration Guide

### **Development to Production Migration**
```bash
# Export development data
pg_dump -h localhost -U petuser -d petdb > development_data.sql

# Import to production (Railway example)
railway run psql $DATABASE_URL < development_data.sql
```

### **Schema Migrations**
```python
# Create new migration
docker-compose exec api python -m alembic revision --autogenerate -m "Add new table"

# Apply migrations
docker-compose exec api python -m alembic upgrade head

# Rollback if needed
docker-compose exec api python -m alembic downgrade -1
```

## Monitoring Setup

### **Production Monitoring Stack**
```yaml
# docker-compose.monitoring.yml
version: '3.8'
services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
    
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=secure_password
    volumes:
      - grafana-storage:/var/lib/grafana
      
volumes:
  grafana-storage:
```

### **Grafana Dashboard Setup**
```bash
# Import pre-built dashboards
curl -X POST http://admin:secure_password@localhost:3000/api/dashboards/db \
  -H "Content-Type: application/json" \
  -d @monitoring/dashboards/api-metrics.json
```

## Security Hardening

### **Production Security Checklist**
- [ ] JWT secrets are cryptographically secure
- [ ] Database passwords are rotated regularly
- [ ] SSL/TLS certificates are valid and auto-renewing
- [ ] Rate limiting is enabled and tuned
- [ ] CORS origins are restricted to known domains
- [ ] Debug mode is disabled
- [ ] Error messages don't expose sensitive information
- [ ] Database connections use SSL
- [ ] Redis is password-protected
- [ ] Firewall rules restrict unnecessary ports
- [ ] Regular security updates are applied

### **Environment Variable Security**
```bash
# Generate secure JWT secret
python -c "import secrets; print(secrets.token_urlsafe(64))"

# Generate secure database password
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Store secrets securely (never commit to git)
echo ".env*" >> .gitignore
```

## Backup & Recovery

### **Automated Backup Setup**
```bash
# Create backup script
cat > scripts/backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/pet-health-api"

# Create backup directory
mkdir -p $BACKUP_DIR

# Database backup
pg_dump $DATABASE_URL > $BACKUP_DIR/database_$DATE.sql

# Compress backup
gzip $BACKUP_DIR/database_$DATE.sql

# Remove backups older than 30 days
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete

echo "Backup completed: $BACKUP_DIR/database_$DATE.sql.gz"
EOF

# Make executable
chmod +x scripts/backup.sh

# Setup cron job for daily backups
(crontab -l 2>/dev/null; echo "0 2 * * * /path/to/scripts/backup.sh") | crontab -
```

### **Disaster Recovery Plan**
```markdown
## Recovery Procedures

### Database Recovery
1. Stop application services
2. Restore database from latest backup
3. Verify data integrity
4. Restart services
5. Monitor for issues

### Full System Recovery
1. Deploy fresh instance from backup
2. Restore database
3. Update DNS if needed
4. Verify all services operational
5. Notify users of any data loss
```

## Scaling Considerations

### **Horizontal Scaling Setup**
```yaml
# docker-compose.scale.yml
version: '3.8'
services:
  api:
    image: pethealth/api:latest
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        delay: 10s
      restart_policy:
        condition: on-failure
        
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - api
```

### **Load Balancer Configuration**
```nginx
# nginx.conf for load balancing
upstream api_servers {
    server api_1:8000;
    server api_2:8000;
    server api_3:8000;
}

server {
    listen 80;
    
    location / {
        proxy_pass http://api_servers;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # Health check endpoint
    location /health {
        access_log off;
        proxy_pass http://api_servers;
    }
}
```

This comprehensive deployment guide covers all scenarios from local development to production scaling, ensuring reliable and secure deployment of the Pet Health API system.