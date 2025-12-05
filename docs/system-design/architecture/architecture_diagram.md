# Pet Health API - Architecture Diagram

## System Architecture Overview

```mermaid
graph TB
    subgraph "Client Layer"
        WEB[Web Browser]
        MOBILE[Mobile App]
        API_CLIENT[API Clients]
        DOCS[OpenAPI Documentation]
    end
    
    subgraph "Application Layer"
        API[FastAPI Application]
        HEALTH[Health Endpoints]
        AUTH[Authentication Service]
    end
    
    subgraph "AI Processing Layer"
        PROMPT[Prompt Engine]
        OLLAMA[Ollama LLM Service]
        MODEL[llama3.2:3b Model]
    end
    
    subgraph "Data Layer"
        POSTGRES[(PostgreSQL Database)]
        REDIS[(Redis Cache)]
        VOLUMES[Persistent Storage]
    end
    
    subgraph "Monitoring & Observability"
        PROMETHEUS[Prometheus Metrics]
        GRAFANA[Grafana Dashboard]
        LOGS[Application Logs]
        HEALTH_CHECKS[Health Monitoring]
    end
    
    subgraph "Infrastructure"
        DOCKER[Docker Network]
        VOLUMES_MGMT[Volume Management]
    end
    
    %% Client connections
    WEB --> API
    MOBILE --> API
    API_CLIENT --> API
    DOCS --> API
    
    %% Application layer connections
    API --> AUTH
    API --> HEALTH
    API --> PROMPT
    API --> POSTGRES
    API --> REDIS
    
    %% AI processing flow
    PROMPT --> OLLAMA
    OLLAMA --> MODEL
    
    %% Data layer connections
    POSTGRES --> VOLUMES
    REDIS --> VOLUMES
    
    %% Monitoring connections
    API --> PROMETHEUS
    API --> LOGS
    HEALTH --> HEALTH_CHECKS
    PROMETHEUS --> GRAFANA
    LOGS --> HEALTH_CHECKS
    
    %% Infrastructure connections
    DOCKER -.-> API
    DOCKER -.-> OLLAMA
    DOCKER -.-> POSTGRES
    DOCKER -.-> REDIS
    VOLUMES_MGMT -.-> VOLUMES

    %% Styling
    style API fill:#e1f5fe
    style PROMPT fill:#f3e5f5
    style OLLAMA fill:#f3e5f5
    style POSTGRES fill:#e8f5e8
    style REDIS fill:#fff3e0
    style PROMETHEUS fill:#fff9c4
    style GRAFANA fill:#fff9c4
```

## Component Architecture Details

### **Application Layer Components**
- **FastAPI Application**: Async Python web framework handling all API requests
- **Authentication Service**: JWT-based authentication and user session management
- **Health Endpoints**: System health monitoring and service status checks

### **AI Processing Pipeline**
- **Prompt Engine**: Intelligent prompt generation and veterinary context formatting
  - Structures pet health data into effective LLM prompts
  - Handles medical domain-specific prompt engineering
  - Manages response parsing and validation
- **Ollama LLM Service**: Local language model processing for privacy-first AI
- **llama3.2:3b Model**: Specialized 3B parameter model optimized for medical assessments

### **Data Architecture**
- **PostgreSQL Database**: Primary data store with ACID compliance for critical pet health data
- **Redis Cache**: High-performance caching layer for sessions and frequent queries
- **Persistent Storage**: Volume management for database and AI model persistence

### **Monitoring & Observability**
- **Application Logs**: Comprehensive logging for debugging and audit trails
- **System Metrics**: Performance monitoring and resource utilization tracking
- **Health Monitoring**: Real-time service health checks and availability monitoring
- **Error Alerting**: Automated alert system for critical failures and anomalies

### **Infrastructure Layer**
- **Docker Network**: Containerized service orchestration and network isolation
- **Volume Management**: Persistent data storage across container lifecycles

## System Configuration

### **Service Architecture**
```yaml
Application Services:
  - FastAPI: RESTful API with async request handling
  - Authentication: JWT token management and user sessions
  - Prompt Engine: AI prompt generation and response processing
  
Data Services:
  - PostgreSQL: Primary database with transactional integrity
  - Redis: Caching layer with session management
  
AI Services:
  - Ollama: Local LLM inference engine
  - Model Storage: Persistent model and configuration storage
  
Monitoring Services:
  - Health Checks: Service availability monitoring
  - Metrics Collection: Performance and usage analytics
  - Log Aggregation: Centralized logging and audit trails
```

### **Data Flow Architecture**
```yaml
Request Processing:
1. Client authentication and authorization
2. Request validation and routing
3. Business logic processing
4. Data persistence operations
5. Response formatting and delivery

AI Assessment Pipeline:
1. Pet health data retrieval
2. Prompt engineering and generation
3. LLM inference processing
4. Response parsing and validation
5. Result caching and storage

Monitoring Pipeline:
1. Request logging and metrics collection
2. Performance monitoring and alerting
3. Health status aggregation
4. Error tracking and notification
```

## Current Data Flow

### **AI Assessment Workflow**
```mermaid
sequenceDiagram
    participant C as Client
    participant A as FastAPI Application
    participant P as Prompt Engine
    participant O as Ollama LLM
    participant DB as PostgreSQL
    participant R as Redis Cache
    participant M as Monitoring
    
    C->>A: POST /api/v1/symptoms/assess
    A->>DB: Fetch pet profile & symptoms
    A->>R: Check assessment cache
    A->>P: Generate structured prompt
    P->>P: Build veterinary assessment prompt
    P->>O: Send formatted prompt
    O->>O: llama3.2:3b inference
    O-->>P: Raw AI response
    P-->>A: Structured assessment response
    A->>DB: Store assessment record
    A->>R: Cache recent assessments
    A->>M: Log assessment metrics
    A-->>C: Complete assessment with disclaimers
```

### **Symptom Tracking Flow**
```mermaid
sequenceDiagram
    participant C as Client
    participant A as FastAPI Application
    participant AUTH as Authentication
    participant DB as PostgreSQL
    participant R as Redis Cache
    participant M as Monitoring
    
    C->>A: POST /api/v1/symptoms/
    A->>AUTH: Validate JWT token
    AUTH-->>A: User authentication confirmed
    A->>DB: Verify pet ownership
    DB-->>A: Pet ownership validated
    A->>DB: Store symptom record
    A->>R: Cache recent symptoms for pet
    A->>M: Log symptom creation metrics
    A-->>C: Created symptom with ID
    
    Note over C,M: User can also update, delete, or retrieve symptoms
    
    C->>A: GET /api/v1/symptoms/pet/{pet_id}
    A->>AUTH: Validate JWT token
    A->>DB: Fetch pet symptoms
    A->>R: Check symptom cache
    DB-->>A: Return symptom history
    A->>M: Log symptom retrieval metrics
    A-->>C: List of pet symptoms
```

### **Health Check Flow**
```mermaid
sequenceDiagram
    participant C as Client
    participant A as FastAPI Application
    participant DB as PostgreSQL
    participant R as Redis Cache
    participant O as Ollama LLM
    participant M as Health Monitoring
    
    C->>A: GET /health
    A->>DB: Database connectivity check
    A->>R: Redis connectivity check  
    A->>O: AI service health check
    A->>M: Update system health status
    M->>M: Aggregate health metrics
    A-->>C: System health status
```

## Deployment Architecture

### **Development Environment**
```yaml
Local Development:
  Platform: Docker Compose orchestration
  Services: All components running on single machine
  Database: PostgreSQL with development data
  AI Processing: Local Ollama with llama3.2:3b model
  Caching: Redis for development optimization
  Monitoring: Basic health checks and logging
  
Development Features:
  - Hot reload for rapid development
  - Comprehensive test suite integration
  - Interactive API documentation
  - Real-time log monitoring
```

### **Production Environment**
```yaml
Production Deployment:
  Platform: Cloud VPS or container orchestration
  Architecture: Scalable multi-container deployment
  Database: PostgreSQL with backup and replication
  AI Processing: Optimized Ollama with resource allocation
  Load Balancing: Nginx reverse proxy with SSL termination
  Monitoring: Full observability stack with alerting
  
Production Features:
  - Horizontal scaling capabilities
  - Comprehensive monitoring and alerting
  - Automated backup and recovery
  - Security hardening and compliance
```

### **Scalability Considerations**
```yaml
Horizontal Scaling:
  - API layer: Multiple application instances behind load balancer
  - Database: Read replicas and connection pooling
  - AI Processing: Multiple Ollama instances for load distribution
  - Caching: Redis cluster for high availability
  
Performance Optimization:
  - Database indexing and query optimization
  - Intelligent caching strategies
  - AI response caching for similar assessments
  - Asynchronous request processing
```

## Security and Privacy Architecture

### **Container Security**
- **Network Isolation**: Services communicate via Docker internal network
- **Secret Management**: Environment variables and Docker secrets
- **Image Security**: Official base images with minimal attack surface
- **User Privileges**: Non-root container execution where possible

### **Data Protection**
- **Local AI Processing**: All inference happens within Docker network
- **Encryption**: TLS for external connections, encrypted volumes
- **Access Control**: JWT-based authentication and authorization
- **Data Retention**: Configurable retention policies for assessments

### **Privacy-First Design**  
- **No External AI Calls**: Ollama processing stays local
- **GDPR Compliance**: User data export and deletion endpoints
- **Audit Logging**: Comprehensive logging for compliance
- **Medical Disclaimers**: Automatic inclusion in AI responses

## Performance and Monitoring

### **Comprehensive Monitoring Stack**
```yaml
Application Monitoring:
  - API Response Times: Track endpoint performance and latency
  - Request Volume: Monitor traffic patterns and peak usage
  - Error Rates: Track 4xx/5xx responses and failure patterns
  - User Activity: Authentication and session management metrics

AI Performance Monitoring:
  - Inference Times: LLM response latency and throughput
  - Model Accuracy: Assessment quality and confidence scoring
  - Prompt Performance: Effectiveness of different prompt strategies
  - Resource Usage: GPU/CPU utilization for AI processing

Infrastructure Monitoring:
  - Container Health: Service availability and restart patterns
  - Resource Utilization: CPU, memory, disk, and network usage
  - Database Performance: Query times, connection pools, lock waits
  - Cache Efficiency: Redis hit rates and memory usage

Business Metrics:
  - Assessment Volume: Daily/monthly health assessments performed
  - User Engagement: Active users and feature adoption
  - System Reliability: Uptime and availability metrics
  - Data Growth: Storage usage and scaling requirements
```

### **Alerting and Incident Response**
```yaml
Critical Alerts:
  - Service Downtime: API, database, or AI service failures
  - Performance Degradation: Response times exceeding thresholds
  - Error Spikes: Unusual increase in application errors
  - Resource Exhaustion: High memory/CPU usage warnings

Monitoring Tools Integration:
  - Log Aggregation: Centralized logging with search capabilities
  - Metrics Dashboard: Real-time system and business metrics
  - Health Check Endpoints: Automated service availability testing
  - Error Tracking: Detailed error analysis and stack traces
```

### **Resource Management and Optimization**
```yaml
Performance Targets:
  API Response Time: < 200ms for standard endpoints
  AI Assessment Time: < 45 seconds for complete analysis
  Database Query Time: < 100ms for common operations
  System Uptime: 99.9% availability target

Resource Allocation:
  API Services: Optimized for concurrent request handling
  Database Layer: Balanced for read/write performance
  AI Processing: Dedicated resources for model inference
  Caching Layer: Memory optimization for frequent queries

Optimization Strategies:
  - Database indexing for pet and symptom lookups
  - Redis caching for user sessions and frequent queries
  - AI response caching for similar assessment patterns
  - Connection pooling for database efficiency
```

## Integration Points

### **External Service Integration**
- **Veterinary Systems**: Mock sync endpoints for future integration
- **Third-Party APIs**: Extensible design for additional AI providers
- **Mobile Apps**: RESTful API design for cross-platform development
- **Web Frontend**: OpenAPI specification for automatic client generation

### **Development Tools Integration**
- **Testing**: 187 automated tests including 31 compliance tests
- **Documentation**: Auto-generated OpenAPI docs at `/docs`
- **Development**: Hot reload and debugging support
- **CI/CD**: Docker-based build and deployment pipeline