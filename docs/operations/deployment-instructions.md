# Deployment Instructions

## Prerequisites

### **System Requirements**
- Docker Desktop 4.0+ (for development)
- 8GB+ RAM (for local AI processing)
- 50GB+ free disk space
- Python 3.11+
- Git

### **Account Setup**
```bash
# Required for production deployment
- GitHub account (source code hosting)
- Railway/DigitalOcean/AWS account (hosting)
- Domain name (optional, for custom URLs)
```

## Local Development Setup

### **1. Clone and Setup Repository**
```bash
# Clone the repository
git clone https://github.com/yourusername/pet-health-api
cd pet-health-api

# Create environment file
cp .env.example .env

# Edit .env with your settings
nano .env
```

### **2. Environment Configuration**
```bash
# .env file contents
DATABASE_URL=postgresql://petuser:petpass@localhost:5432/petdb
REDIS_URL=redis://localhost:6379
JWT_SECRET=your-super-secure-jwt-secret-key-here
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO

# AI Service Configuration
AI_PROVIDER=ollama  # or "openai" for OpenAI API
OLLAMA_BASE_URL=http://localhost:11434
OPENAI_API_KEY=sk-your-openai-key-if-using-openai

# Security Settings
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
RATE_LIMIT_ENABLED=true
```

### **3. Docker Development Setup**
```bash
# Start all services
docker-compose up -d

# Verify services are running
docker-compose ps

# Check logs if needed
docker-compose logs api
docker-compose logs postgres
docker-compose logs redis
```

### **4. Database Initialization**
```bash
# Run database migrations
docker-compose exec api python -m alembic upgrade head

# Create initial data (optional)
docker-compose exec api python scripts/seed_data.py
```

### **5. AI Model Setup**
```bash
# Pull Ollama model (for local AI)
docker-compose exec ollama ollama pull llama3.1

# Test AI service
curl http://localhost:11434/api/generate \
  -d '{"model": "llama3.1", "prompt": "Hello, world!", "stream": false}'
```

## Production Deployment Options

### **Option 1: Railway (Recommended for MVP)**

#### **Step 1: Prepare Application**
```bash
# Ensure Dockerfile is optimized for Railway
cat > Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
RUN chown -R app:app /app
USER app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "$PORT"]
EOF
```

#### **Step 2: Railway Deployment**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Initialize project
railway init

# Add environment variables
railway variables set DATABASE_URL=$DATABASE_URL
railway variables set REDIS_URL=$REDIS_URL
railway variables set JWT_SECRET=$JWT_SECRET

# Deploy application
railway up
```

#### **Step 3: Database Setup on Railway**
```bash
# Add PostgreSQL service
railway add postgresql

# Add Redis service  
railway add redis

# Run migrations
railway run python -m alembic upgrade head
```

### **Option 2: DigitalOcean App Platform**

#### **Step 1: Create App Spec**
```yaml
# .do/app.yaml
name: pet-health-api
services:
- name: api
  source_dir: /
  github:
    repo: yourusername/pet-health-api
    branch: main
  run_command: python -m uvicorn app.main:app --host 0.0.0.0 --port 8080
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  envs:
  - key: DATABASE_URL
    scope: RUN_TIME
    type: SECRET
  - key: REDIS_URL  
    scope: RUN_TIME
    type: SECRET
  - key: JWT_SECRET
    scope: RUN_TIME
    type: SECRET
  routes:
  - path: /
databases:
- engine: PG
  name: petdb
  num_nodes: 1
  size: db-s-1vcpu-1gb
  version: "14"
```

#### **Step 2: Deploy to DigitalOcean**
```bash
# Install doctl CLI
brew install doctl  # macOS

# Authenticate
doctl auth init

# Create app
doctl apps create .do/app.yaml

# Check deployment status
doctl apps list
```

### **Option 3: Self-Hosted (VPS)**

#### **Step 1: Server Setup**
```bash
# Connect to your VPS
ssh root@your-server-ip

# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
pip3 install docker-compose

# Create application user
useradd -m -s /bin/bash petapp
usermod -aG docker petapp
su - petapp
```

#### **Step 2: Application Deployment**
```bash
# Clone repository
git clone https://github.com/yourusername/pet-health-api
cd pet-health-api

# Create production environment file
cat > .env.production << 'EOF'
DATABASE_URL=postgresql://petuser:SECURE_PASSWORD@postgres:5432/petdb
REDIS_URL=redis://redis:6379
JWT_SECRET=VERY_SECURE_RANDOM_STRING
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING
CORS_ORIGINS=https://yourdomain.com
EOF

# Start services
docker-compose -f docker-compose.prod.yml up -d
```

#### **Step 3: Nginx Reverse Proxy**
```bash
# Install Nginx
sudo apt install nginx

# Create Nginx config
sudo cat > /etc/nginx/sites-available/pet-health-api << 'EOF'
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/pet-health-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### **Step 4: SSL Setup with Let's Encrypt**
```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Verify auto-renewal
sudo certbot renew --dry-run
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