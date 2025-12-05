# Trust Model - Pet Health API System

*Last Updated: December 5, 2025*

## Overview
This document outlines the trust model for the Pet Health API system, identifying trust boundaries, threat vectors, and security controls implemented in the current Docker-based deployment.

**Related Documents:**
- [Ethics Framework](./ethics-framework.md) - Ethical principles and implementation
- [Clause Control Tests](./clause-control-test.md) - Automated security and compliance verification
- [Ethics Debt Ledger](./ethics_debt_ledger.md) - Ongoing security and privacy improvements

## Trust Boundaries

### **Level 1: Public Internet (Untrusted)**
- **Actors**: Anonymous internet users, potential attackers
- **Trust Level**: Zero trust
- **Access**: Rate-limited public endpoints only
- **Controls**: WAF, DDoS protection, input validation

### **Level 2: Authenticated Users (Limited Trust)**
- **Actors**: Registered pet owners with valid accounts
- **Trust Level**: Limited - trusted for their own data only
- **Access**: Pet and symptom management for owned pets
- **Controls**: JWT authentication, ownership validation, API rate limiting

### **Level 3: Application Services (Internal Trust)**
- **Actors**: FastAPI backend, Ollama AI service, Redis cache, PostgreSQL database
- **Trust Level**: High - services can communicate internally via Docker network
- **Access**: Inter-service communication via internal Docker networks (api, ollama, redis, postgres)
- **Controls**: Container isolation, internal DNS resolution, encrypted connections, service mesh policies

### **Level 4: Infrastructure (Full Trust)**
- **Actors**: Docker containers, volumes, host system
- **Trust Level**: Full trust within encrypted container boundaries
- **Access**: All application data and system operations within containerized environment
- **Controls**: Container runtime security, encrypted volumes, network isolation, host system hardening

## Data Classification

### **Highly Sensitive**
- **Pet Medical Records**: Symptoms, diagnoses, AI health assessments
- **User Credentials**: Hashed passwords, JWT tokens, API keys
- **AI Analysis**: Health assessments from Ollama llama3.2:3b model, symptom analysis
- **Controls**: AES-256 encryption at rest (PostgreSQL), TLS 1.3 in transit, audit logging, strict access controls

### **Sensitive**
- **Pet Profiles**: Names, species, breed, age information
- **User Profiles**: Email addresses, account preferences, ownership relationships
- **Usage Patterns**: API access logs, assessment request patterns, error logs
- **Controls**: TLS encryption in transit, PostgreSQL access controls, data retention policies

### **Internal**
- **System Metrics**: Performance data, error logs
- **Configuration**: Non-secret system settings
- **Controls**: Internal network access, monitoring

## Threat Model

### **External Threats**

#### **T1: Unauthorized Data Access**
- **Attack Vector**: API exploitation, credential theft
- **Impact**: High - exposure of pet medical records
- **Likelihood**: Medium
- **Mitigations**: 
  - Strong authentication (JWT + refresh tokens)
  - API rate limiting and monitoring
  - Input validation and sanitization
  - Regular security audits

#### **T2: AI Prompt Injection and Manipulation**
- **Attack Vector**: Malicious symptom descriptions to manipulate Ollama AI responses
- **Impact**: Medium - incorrect health advice, potential medical misguidance
- **Likelihood**: Medium
- **Current Mitigations**:
  - Input sanitization in FastAPI endpoints
  - Structured prompt templates with safety constraints
  - Medical disclaimer injection in all AI responses
  - Conservative bias in urgency level assignment
  - Fallback rule-based assessment when AI fails
  - Automated testing of AI response safety (test_e2_conservative_advice.py)

#### **T3: DDoS and Resource Exhaustion**
- **Attack Vector**: High-volume requests to overwhelm FastAPI or Ollama services
- **Impact**: Medium - service unavailability affecting pet health assessments
- **Likelihood**: High
- **Current Mitigations**:
  - FastAPI built-in rate limiting
  - Docker container resource limits
  - Ollama service isolation and timeouts
  - Circuit breakers for AI service failures
  - Containerized scaling capabilities
  - Redis caching to reduce database load

### **Internal Threats**

#### **T4: Container Escape and Privilege Escalation**
- **Attack Vector**: Compromised container gaining access to host system or other containers
- **Impact**: High - potential access to all containerized services
- **Likelihood**: Low
- **Current Mitigations**:
  - Docker security best practices (non-root containers)
  - Container resource constraints
  - Network segmentation between services
  - Minimal container images (distroless where possible)
  - Regular container image security scanning

#### **T5: Data Breach via Container or Database Compromise**
- **Attack Vector**: PostgreSQL container compromise or data exfiltration
- **Impact**: Critical - exposure of all pet health data and user information
- **Likelihood**: Low
- **Current Mitigations**:
  - PostgreSQL container isolation with custom networks
  - Database access only via application layer (no direct external access)
  - Encrypted database connections (SSL/TLS)
  - Container volume encryption for persistent data
  - Regular PostgreSQL security updates
  - Database query logging and monitoring

#### **T6: AI Service Data Leakage**
- **Attack Vector**: Ollama model or service logging sensitive pet health data
- **Impact**: High - exposure of pet medical information outside system boundaries
- **Likelihood**: Low
- **Current Mitigations**:
  - Local Ollama deployment (no external AI service calls)
  - Network isolation of AI service container
  - Automated testing for external network calls (test_p4_local_ai_processing.py)
  - AI service logs review and sanitization
  - Container resource limits preventing data persistence

## Security Controls

### **Authentication & Authorization**
```yaml
Current Implementation:
  - JWT-based authentication with configurable expiry
  - Bcrypt password hashing with salt
  - Pet ownership validation on all CRUD operations
  - User isolation enforced at API layer
  - Role-based access control for future admin features

Automated Testing:
  - User data isolation tests (clause_control_tests/test_p3_user_control.py)
  - Authorization bypass prevention
  - Cross-user data access prevention
```

### **Data Protection**
```yaml
Current Implementation:
  - TLS 1.3 for all external API communications
  - PostgreSQL connection encryption (SSL/TLS)
  - Docker secrets management for sensitive configuration
  - Data retention policies implemented in service layer
  - Local AI processing prevents external data leakage

Security Verification:
  - Network isolation testing (test_p4_local_ai_processing.py)
  - Data encryption verification
  - Secure configuration auditing
```

### **Application Security**
```yaml
Current Implementation:
  - Pydantic model validation for all API inputs
  - SQLAlchemy ORM preventing SQL injection
  - FastAPI automatic request validation
  - CORS policy configuration
  - Rate limiting per endpoint
  - Error handling without information disclosure

Compliance Testing:
  - Input validation tests across all endpoints
  - Data minimization verification (test_p1_data_minimization.py)
  - Purpose limitation enforcement (test_p2_purpose_limitation.py)
```

### **Infrastructure Security**
```yaml
Current Implementation:
  - Docker container isolation with custom networks
  - Service-specific network segments (api, postgres, redis, ollama)
  - Container resource limits and security policies
  - Minimal container images with security patches
  - Volume encryption for persistent data storage
  - Health check endpoints for service monitoring

Container Security:
  - Non-root user execution in containers
  - Read-only filesystems where applicable
  - Capability dropping for enhanced security
  - Regular base image updates and vulnerability scanning
```

## Trust Verification

### **Continuous Monitoring**
```yaml
Current Implementation:
  - FastAPI automatic request/response logging
  - PostgreSQL query logging for audit trails
  - Container health monitoring via Docker
  - AI service response quality tracking
  - User access pattern monitoring

Automated Alerts:
  - Failed authentication attempt thresholds
  - Unusual API access patterns
  - AI service failures or timeouts
  - Database connection issues
  - Container resource exhaustion
```

### **Automated Compliance Testing**
```yaml
Test Suite (187 total tests, 31 compliance-focused):
  - Privacy controls: Data minimization, user control, purpose limitation
  - Security controls: Local AI processing, network isolation
  - Ethics controls: Medical disclaimers, conservative advice, bias prevention
  - Integration testing: End-to-end workflow validation

Continuous Validation:
  - All tests run in containerized environment
  - Compliance verification on every deployment
  - Red bar tests for critical security requirements
  - Performance and chaos testing for reliability
```

### **Regular Security Assessments**
```yaml
Implemented Processes:
  - Monthly compliance test review
  - Quarterly security configuration audit
  - Container image vulnerability scanning
  - Dependency security update monitoring
  - Ethics framework compliance verification

Future Enhancements:
  - Annual penetration testing
  - External security audits
  - Code security reviews with static analysis
  - Third-party privacy assessments
```

### **Incident Response**
```yaml
Current Capabilities:
  - Container-level isolation for incident containment
  - Automated service restart and recovery via Docker
  - Comprehensive logging for forensic analysis
  - Database backup and recovery procedures
  - AI service fallback mechanisms for continuity

Response Procedures:
  - Security incident detection and alerting
  - Container isolation and investigation protocols
  - Data breach notification and user communication
  - Service recovery and validation procedures
  - Post-incident analysis and improvement implementation
```

## Privacy by Design Implementation

### **Current Data Minimization**
```yaml
Implemented Controls:
  - Simplified assessment API (pet_id only, no duplicate symptom data)
  - Optional fields for enhanced features (breed-specific advice)
  - Automatic data aggregation from existing symptoms
  - No unnecessary personal information collection
  - User-controlled data deletion with cascade operations

Technical Implementation:
  - Pydantic model validation rejecting unnecessary fields
  - Database foreign key constraints for data integrity
  - Service layer enforcement of data minimization principles
```

### **User Transparency and Control**
```yaml
Current Features:
  - Clear API documentation with data usage explanations
  - Medical disclaimer in all AI responses
  - User ownership validation for all operations
  - Simplified consent model (account creation = consent)

Planned Enhancements:
  - Granular privacy settings for data sharing preferences
  - Data export capabilities in machine-readable format
  - Enhanced consent management for AI processing
  - Privacy dashboard for user data visibility
```

## Compliance Implementation

### **Current Privacy Compliance**
```yaml
Data Protection Principles:
  - Lawful basis: Legitimate interest for pet health management
  - Data minimization: Only collect necessary pet health information
  - Purpose limitation: Health management only, no marketing or analytics
  - User rights: Access, rectification, erasure implemented in API

Technical Implementation:
  - User data isolation at application layer
  - Ownership validation on all operations
  - Local AI processing prevents data transfer to third parties
  - Automated compliance testing ensures ongoing adherence
```

### **Security Standards Compliance**
```yaml
Current Implementation:
  - Container security best practices (CIS Docker Benchmark alignment)
  - OWASP Top 10 protection measures in FastAPI application
  - Secure coding practices with input validation and sanitization
  - Regular dependency updates and vulnerability management

Ongoing Improvements:
  - ISO 27001 security management principles adoption
  - Security training integration into development workflow
  - Third-party security assessment planning
  - Continuous security monitoring enhancement
```

### **Healthcare-Adjacent Compliance**
```yaml
Medical Disclaimer Requirements:
  - All AI responses include mandatory medical disclaimers
  - Clear education-only positioning of AI advice
  - Conservative bias in health recommendations
  - Emergency symptom escalation to professional care

Ethical AI Implementation:
  - Transparency in AI decision-making process
  - Bias prevention across pet species and breeds
  - User control over AI feature usage
  - Regular ethics compliance validation
```

## Trust Model Evolution

### **Current Deployment Status (Dec 2025)**
```yaml
Production Readiness:
  ✅ Container-based deployment with security isolation
  ✅ Local AI processing with Ollama llama3.2:3b
  ✅ Comprehensive compliance testing suite (187 tests)
  ✅ Privacy by design implementation
  ✅ Medical disclaimer and conservative AI advice
  
Areas for Enhancement:
  🔄 Multi-factor authentication implementation
  🔄 Enhanced audit logging and monitoring
  🔄 External security assessment and penetration testing
  🔄 Granular user consent and privacy controls
```

### **Quarterly Review Process**
```yaml
Review Scope:
  - Threat landscape changes and new attack vectors
  - Technology updates and security patches
  - Compliance requirement changes
  - User feedback on privacy and security features

Update Procedures:
  - Trust boundary reassessment
  - Threat model updates and mitigation reviews
  - Security control effectiveness evaluation
  - Compliance testing suite enhancements
```

---

*This trust model is maintained as a living document, updated quarterly or after significant system changes. Last comprehensive review: December 2025.*