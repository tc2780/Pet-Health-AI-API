# Clause→Control→Test Implementation

## Overview
This document maps privacy/ethics clauses to technical controls and automated tests, ensuring our pet health API maintains ethical standards and privacy compliance.

## Privacy Clauses & Controls

### **Clause P1: Data Minimization**
*"Collect only data necessary for pet health management"*

#### **Technical Controls**
- **API Validation**: Pydantic models reject unnecessary fields
- **Database Schema**: No storage of non-essential personal data
- **Optional Fields**: Breed, weight marked as optional with clear benefits

#### **Automated Tests**
```python
def test_pet_creation_data_minimization():
    """Test that only necessary fields are required"""
    minimal_pet = {
        "name": "Buddy",
        "species": "dog"
    }
    response = client.post("/pets", json=minimal_pet)
    assert response.status_code == 201
    
def test_excessive_data_rejection():
    """Test rejection of unnecessary personal data"""
    pet_with_pii = {
        "name": "Buddy", 
        "species": "dog",
        "owner_ssn": "123-45-6789",  # Should be rejected
        "owner_income": 50000         # Should be rejected
    }
    response = client.post("/pets", json=pet_with_pii)
    # Should succeed but ignore unnecessary fields
    assert response.status_code == 201
    pet_data = response.json()
    assert "owner_ssn" not in pet_data
    assert "owner_income" not in pet_data
```

### **Clause P2: Purpose Limitation** 
*"Use pet data only for health management, not marketing"*

#### **Technical Controls**
- **Code Review**: All data access requires health-related purpose
- **API Endpoints**: No marketing or advertising endpoints
- **Data Export**: Only health-related data in user exports

#### **Automated Tests**
```python
def test_no_marketing_endpoints():
    """Ensure no marketing-related endpoints exist"""
    marketing_endpoints = ["/ads", "/marketing", "/promotions", "/analytics/marketing"]
    for endpoint in marketing_endpoints:
        response = client.get(endpoint)
        assert response.status_code == 404

def test_data_usage_logging():
    """Test that data access is logged with purpose"""
    response = client.get("/pets/123/symptoms")
    # Check audit log contains health purpose
    audit_log = get_last_audit_entry()
    assert audit_log["purpose"] == "health_management"
    assert audit_log["data_type"] == "pet_symptoms"
```

### **Clause P3: User Control**
*"Users can access, modify, and delete their data"*

#### **Technical Controls**
- **Data Export API**: Complete user data download
- **Deletion Cascade**: Proper foreign key constraints
- **Update Permissions**: Users can modify their own data only

#### **Automated Tests**
```python
def test_complete_data_export():
    """Test user can export all their data"""
    response = client.get("/users/me/export", headers=auth_headers)
    assert response.status_code == 200
    
    exported_data = response.json()
    required_sections = ["pets", "symptoms", "assessments", "user_profile"]
    for section in required_sections:
        assert section in exported_data

def test_user_data_deletion():
    """Test complete user data deletion"""
    user_id = create_test_user()
    pet_id = create_test_pet(user_id)
    create_test_symptoms(pet_id)
    
    # Delete user
    response = client.delete("/users/me", headers=auth_headers)
    assert response.status_code == 204
    
    # Verify all data deleted
    assert db.query(User).filter(User.id == user_id).first() is None
    assert db.query(Pet).filter(Pet.user_id == user_id).first() is None
    assert db.query(Symptom).filter(Symptom.pet_id == pet_id).first() is None
```

### **Clause P4: Local AI Processing**
*"AI processing occurs locally, data doesn't leave infrastructure"*

#### **Technical Controls**
- **Network Isolation**: AI service has no external internet access
- **Local LLM**: Ollama deployment without external APIs
- **Monitoring**: Network traffic monitoring for data leakage

#### **Automated Tests**
```python
def test_ai_service_network_isolation():
    """Test AI service cannot access external networks"""
    with pytest.raises(ConnectionError):
        # AI service should not be able to make external calls
        ai_service.test_external_connectivity()

def test_local_llm_processing():
    """Test AI processing uses local LLM only"""
    with mock.patch('requests.post') as mock_post:
        ai_response = ai_service.analyze_symptoms(pet_data, symptoms)
        
        # Should not make any external API calls
        mock_post.assert_not_called()
        assert ai_response is not None
        assert "urgency_level" in ai_response
```

## Ethics Clauses & Controls

### **Clause E1: Medical Disclaimer**
*"All AI responses must include medical disclaimer"*

#### **Technical Controls**
- **Response Wrapper**: Automatic disclaimer injection
- **Template Validation**: All AI prompts include disclaimer requirement
- **Response Filtering**: Check for disclaimer presence

#### **Automated Tests**
```python
def test_ai_response_contains_disclaimer():
    """Test all AI responses include medical disclaimer"""
    pet_data = {"species": "dog", "age_years": 5}
    symptoms = [{"name": "lethargy", "severity": "moderate"}]
    
    response = ai_service.analyze_symptoms(pet_data, symptoms)
    
    disclaimer_phrases = [
        "not professional veterinary advice",
        "consult a licensed veterinarian",
        "educational purposes only"
    ]
    
    response_text = json.dumps(response).lower()
    assert any(phrase in response_text for phrase in disclaimer_phrases)

def test_emergency_symptom_immediate_vet_referral():
    """Test emergency symptoms trigger immediate vet recommendation"""
    emergency_symptoms = [
        {"name": "difficulty breathing", "severity": "severe"},
        {"name": "seizure", "severity": "severe"}
    ]
    
    response = ai_service.analyze_symptoms(pet_data, emergency_symptoms)
    
    assert response["urgency_level"] == "emergency"
    assert "immediate veterinary care" in response["recommendations"][0].lower()
```

### **Clause E2: Conservative Health Advice**
*"AI should err on the side of caution for health recommendations"*

#### **Technical Controls**
- **Urgency Escalation**: Bias toward higher urgency levels
- **Prompt Engineering**: Conservative advice prompts
- **Response Validation**: Flag overly casual recommendations

#### **Automated Tests**
```python
def test_conservative_urgency_assessment():
    """Test AI tends toward conservative urgency levels"""
    ambiguous_symptoms = [
        {"name": "mild lethargy", "severity": "mild"},
        {"name": "decreased appetite", "severity": "mild"}
    ]
    
    responses = []
    for _ in range(10):  # Test multiple times for consistency
        response = ai_service.analyze_symptoms(pet_data, ambiguous_symptoms)
        responses.append(response["urgency_level"])
    
    # Should tend toward moderate/high rather than low
    conservative_responses = sum(1 for r in responses if r in ["moderate", "high", "emergency"])
    assert conservative_responses >= len(responses) * 0.7  # 70% conservative

def test_no_definitive_diagnoses():
    """Test AI avoids definitive medical diagnoses"""
    symptoms = [{"name": "vomiting", "severity": "moderate"}]
    response = ai_service.analyze_symptoms(pet_data, symptoms)
    
    # Check that responses use cautious language
    causes_text = " ".join(response["possible_causes"]).lower()
    
    prohibited_phrases = ["definitely", "certainly", "diagnosed with", "has"]
    cautious_phrases = ["possible", "may", "could", "might", "potential"]
    
    for phrase in prohibited_phrases:
        assert phrase not in causes_text
    
    assert any(phrase in causes_text for phrase in cautious_phrases)
```

### **Clause E3: Bias Prevention**
*"AI advice should be fair across all pet breeds and species"*

#### **Technical Controls**
- **Bias Testing**: Regular testing across breed/species combinations
- **Prompt Standardization**: Consistent prompts regardless of pet characteristics
- **Response Monitoring**: Track recommendation patterns by demographics

#### **Automated Tests**
```python
def test_consistent_advice_across_breeds():
    """Test AI provides consistent advice regardless of breed"""
    base_symptoms = [{"name": "lethargy", "severity": "moderate"}]
    
    breeds_to_test = ["golden_retriever", "chihuahua", "german_shepherd", "mixed_breed"]
    responses = {}
    
    for breed in breeds_to_test:
        pet_data = {"species": "dog", "breed": breed, "age_years": 5}
        response = ai_service.analyze_symptoms(pet_data, base_symptoms)
        responses[breed] = response["urgency_level"]
    
    # Urgency levels should be similar across breeds for same symptoms
    unique_urgencies = set(responses.values())
    assert len(unique_urgencies) <= 2  # Allow some variation but not extreme

def test_species_appropriate_advice():
    """Test AI provides species-appropriate advice"""
    symptoms = [{"name": "hairball", "severity": "mild"}]
    
    # Test cat (appropriate) vs dog (inappropriate symptom)
    cat_response = ai_service.analyze_symptoms(
        {"species": "cat"}, symptoms
    )
    dog_response = ai_service.analyze_symptoms(
        {"species": "dog"}, symptoms
    )
    
    # Cat should have normal hairball advice
    assert "normal" in cat_response["recommendations"][0].lower()
    
    # Dog should flag as unusual (dogs don't get hairballs)
    assert dog_response["urgency_level"] in ["moderate", "high"]
```

## Compliance Monitoring

### **Automated Compliance Checks**
```python
class ComplianceMonitor:
    def __init__(self):
        self.compliance_tests = [
            self.check_data_minimization,
            self.check_medical_disclaimers,
            self.check_privacy_controls,
            self.check_ai_conservative_bias
        ]
    
    async def run_daily_compliance_check(self):
        """Run all compliance tests daily"""
        results = {}
        
        for test in self.compliance_tests:
            try:
                test_result = await test()
                results[test.__name__] = {
                    "status": "PASS" if test_result else "FAIL",
                    "timestamp": datetime.utcnow()
                }
            except Exception as e:
                results[test.__name__] = {
                    "status": "ERROR",
                    "error": str(e),
                    "timestamp": datetime.utcnow()
                }
        
        # Alert on failures
        failed_tests = [name for name, result in results.items() 
                       if result["status"] != "PASS"]
        
        if failed_tests:
            await self.send_compliance_alert(failed_tests)
        
        return results
```

### **Telemetry Matrix**
```yaml
Privacy Metrics:
  - data_minimization_violations: Count of unnecessary data collection attempts
  - user_data_export_requests: Number of data export requests processed
  - data_deletion_requests: Number of complete data deletions
  - consent_withdrawal_events: Tracking of privacy preference changes

Ethics Metrics:
  - ai_disclaimer_coverage: Percentage of AI responses with disclaimers
  - emergency_escalation_rate: Rate of emergency symptom detection
  - conservative_bias_score: Measure of AI conservativeness in advice
  - cross_breed_consistency: Variance in advice across pet demographics

Compliance Metrics:
  - gdpr_response_time: Time to respond to privacy requests
  - audit_trail_completeness: Coverage of data access logging
  - security_incident_count: Number of privacy/security incidents
  - external_data_sharing_events: Should always be zero
```

### **Red Bar Tests (Must Never Fail)**
```python
class RedBarTests:
    """Critical tests that must never fail in production"""
    
    def test_no_external_ai_calls(self):
        """CRITICAL: Ensure no data leaves our infrastructure"""
        with monitor_network_traffic():
            ai_service.analyze_symptoms(test_pet_data, test_symptoms)
            
        external_calls = get_external_network_calls()
        assert len(external_calls) == 0, f"Unauthorized external calls: {external_calls}"
    
    def test_user_data_isolation(self):
        """CRITICAL: Users can only access their own data"""
        user1_pet = create_test_pet(user1_id)
        user2_headers = get_auth_headers(user2_id)
        
        response = client.get(f"/pets/{user1_pet.id}", headers=user2_headers)
        assert response.status_code == 404, "Users can access other users' data!"
    
    def test_ai_never_gives_definitive_diagnosis(self):
        """CRITICAL: AI never provides definitive medical diagnoses"""
        all_symptoms = load_symptom_test_cases()
        
        for symptoms in all_symptoms:
            response = ai_service.analyze_symptoms(test_pet_data, symptoms)
            response_text = json.dumps(response).lower()
            
            forbidden_phrases = ["diagnosed with", "definitely has", "certainly"]
            for phrase in forbidden_phrases:
                assert phrase not in response_text, f"AI gave definitive diagnosis: {phrase}"
```

## Ethics Debt Tracking

### **Ethics Debt Ledger**
```yaml
Current Ethics Debt:
  - ED-001: "AI model bias testing needs expansion to exotic pets"
    Priority: Medium
    Target Resolution: Q2 2026
    
  - ED-002: "Need veterinary professional review of AI prompt templates"
    Priority: High  
    Target Resolution: Q1 2026
    
  - ED-003: "Privacy policy needs simplification for better user comprehension"
    Priority: Medium
    Target Resolution: Q2 2026

Resolved Ethics Debt:
  - ED-004: "Medical disclaimer missing from some AI responses" 
    Resolution: Automatic disclaimer injection implemented
    Resolved: 2025-11-30
```

This framework ensures continuous monitoring of ethical and privacy commitments through automated testing and compliance tracking.