# Pet Health API - Architecture Diagram

## System Overview

```mermaid
graph TB
    subgraph "Client Layer"
        WEB[Web App]
        MOBILE[Mobile App]
        API_CLIENT[3rd Party Clients]
    end
    
    subgraph "API Gateway"
        NGINX[Nginx Load Balancer]
        AUTH[Authentication Service]
    end
    
    subgraph "Application Layer"
        API[FastAPI Application]
        SYMPTOM_SVC[Symptom Service]
        AI_SVC[AI Service]
        USER_SVC[User Service]
    end
    
    subgraph "AI Processing"
        OLLAMA[Ollama Local LLM]
        OPENAI[OpenAI API]
        PROMPT[Prompt Engine]
    end
    
    subgraph "Data Layer"
        POSTGRES[(PostgreSQL)]
        REDIS[(Redis Cache)]
        S3[File Storage]
    end
    
    subgraph "Monitoring"
        PROMETHEUS[Prometheus]
        GRAFANA[Grafana]
        HEALTH[Health Checks]
    end
    
    WEB --> NGINX
    MOBILE --> NGINX
    API_CLIENT --> NGINX
    
    NGINX --> AUTH
    AUTH --> API
    
    API --> SYMPTOM_SVC
    API --> AI_SVC
    API --> USER_SVC
    
    AI_SVC --> PROMPT
    PROMPT --> OLLAMA
    PROMPT --> OPENAI
    
    SYMPTOM_SVC --> POSTGRES
    SYMPTOM_SVC --> REDIS
    USER_SVC --> POSTGRES
    
    API --> HEALTH
    HEALTH --> PROMETHEUS
    PROMETHEUS --> GRAFANA
```

## Component Details

### **API Gateway Layer**
- **Nginx**: Load balancing, SSL termination, rate limiting
- **Authentication**: JWT-based authentication with Redis session storage

### **Application Services**
- **FastAPI**: Async Python web framework for high performance
- **Symptom Service**: Core business logic for symptom tracking
- **AI Service**: AI integration and prompt management
- **User Service**: User and pet profile management

### **AI Processing Pipeline**
- **Prompt Engine**: Structured prompt generation and validation
- **Ollama**: Privacy-first local LLM processing
- **OpenAI**: Optional cloud AI for enhanced capabilities

### **Data Architecture**
- **PostgreSQL**: Primary data store with ACID compliance
- **Redis**: Caching layer and session management
- **File Storage**: Pet images and documents

### **Observability Stack**
- **Prometheus**: Metrics collection and alerting
- **Grafana**: Visualization and dashboards
- **Health Checks**: Comprehensive service monitoring

## Data Flow

### **Symptom Tracking Flow**
```mermaid
sequenceDiagram
    participant C as Client
    participant A as API
    participant S as Symptom Service
    participant D as Database
    participant R as Redis
    
    C->>A: POST /symptoms/{pet_id}
    A->>S: Validate and process symptom
    S->>D: Store symptom record
    S->>R: Cache recent symptoms
    S-->>A: Return symptom ID
    A-->>C: HTTP 201 Created
```

### **AI Assessment Flow**
```mermaid
sequenceDiagram
    participant C as Client
    participant A as API
    participant AI as AI Service
    participant LLM as Ollama/OpenAI
    participant D as Database
    
    C->>A: POST /ai-vet/{pet_id}/assess
    A->>AI: Process symptom assessment
    AI->>D: Fetch pet profile & symptoms
    AI->>LLM: Generate AI analysis
    LLM-->>AI: Return assessment
    AI->>D: Store assessment record
    AI-->>A: Return analysis
    A-->>C: AI assessment response
```

## Deployment Architecture

### **Development Environment**
```yaml
Local Development:
  - Docker Compose with all services
  - Ollama running locally
  - PostgreSQL and Redis containers
  - Hot reload for development
```

### **Production Environment**
```yaml
Cloud Deployment:
  - Kubernetes cluster or container platform
  - Managed PostgreSQL database
  - Redis cluster for high availability
  - Load balancer with SSL termination
  - Horizontal pod autoscaling
```

## Security Architecture

### **Authentication & Authorization**
- JWT tokens with refresh mechanism
- Role-based access control (RBAC)
- Pet ownership validation
- API rate limiting per user

### **Data Protection**
- Encryption at rest (database level)
- Encryption in transit (TLS 1.3)
- PII anonymization for research data
- GDPR compliance measures

### **AI Security**
- Local LLM processing (data never leaves infrastructure)
- Prompt injection protection
- Response validation and filtering
- Audit logging for AI interactions

## Scalability Considerations

### **Horizontal Scaling**
- Stateless API design
- Database connection pooling
- Redis clustering for cache
- CDN for static assets

### **Performance Optimization**
- Database indexing strategy
- Intelligent caching layers
- Async request processing
- Connection pooling

### **Monitoring & Alerting**
- Real-time health monitoring
- Performance metrics tracking
- Error rate monitoring
- Capacity planning alerts