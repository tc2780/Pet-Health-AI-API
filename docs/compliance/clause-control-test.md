# Clause→Control→Test Implementation

## Overview
This document maps privacy/ethics clauses to technical controls and automated tests, ensuring our pet health API maintains ethical standards and privacy compliance.

**Test Implementation Location:** 
The actual test implementations described in this document are located in:
`backend/tests/clause_control_tests/`

## Privacy Clauses & Controls

### **Clause P1: Data Minimization**
*"Collect only data necessary for pet health management"*

#### **Technical Controls**
- **API Validation**: Pydantic models reject unnecessary fields
- **Database Schema**: No storage of non-essential personal data
- **Optional Fields**: Breed, weight marked as optional with clear benefits

#### **Automated Tests**
```python
async def test_pet_creation_data_minimization(client: AsyncClient):
    """Test that only necessary fields are required"""
    auth_headers = await get_auth_headers(client)
    minimal_pet = {
        "name": "Buddy",
        "species": "dog"
    }
    response = await client.post("/api/v1/pets/", json=minimal_pet, headers=auth_headers)
    assert response.status_code == 201
    
async def test_excessive_data_rejection(client: AsyncClient):
    """Test rejection of unnecessary personal data"""
    auth_headers = await get_auth_headers(client)
    pet_with_pii = {
        "name": "Buddy", 
        "species": "dog",
        "owner_ssn": "123-45-6789",  # Should be rejected
        "owner_income": 50000         # Should be rejected
    }
    response = await client.post("/api/v1/pets/", json=pet_with_pii, headers=auth_headers)
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
async def test_no_marketing_endpoints(client: AsyncClient):
    """Ensure no marketing-related endpoints exist"""
    auth_headers = await get_auth_headers(client)
    marketing_endpoints = ["/ads", "/marketing", "/promotions", "/analytics/marketing"]
    for endpoint in marketing_endpoints:
        response = await client.get(endpoint, headers=auth_headers)
        assert response.status_code == 404

async def test_data_usage_logging(client: AsyncClient):
    """Test that data access is logged with purpose"""
    auth_headers = await get_auth_headers(client)
    pet_id = await create_test_pet(client, auth_headers)
    response = await client.get(f"/api/v1/symptoms/pet/{pet_id}", headers=auth_headers)
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
async def test_complete_data_export(client: AsyncClient):
    """Test user can export all their data"""
    auth_headers = await get_auth_headers(client)
    response = await client.get("/api/v1/users/me/export", headers=auth_headers)
    assert response.status_code == 200
    
    exported_data = response.json()
    required_sections = ["pets", "symptoms", "assessments", "user_profile"]
    for section in required_sections:
        assert section in exported_data

async def test_user_data_deletion(client: AsyncClient):
    """Test complete user data deletion"""
    auth_headers = await get_auth_headers(client)
    user_id = await get_current_user_id(client, auth_headers)
    pet_id = await create_test_pet(client, auth_headers)
    await create_test_symptoms(client, auth_headers, pet_id)
    
    # Delete user
    response = await client.delete("/api/v1/users/me", headers=auth_headers)
    assert response.status_code == 204
    
    # Verify all data deleted (this would need database access in real test)
    # assert db.query(User).filter(User.id == user_id).first() is None
    # assert db.query(Pet).filter(Pet.user_id == user_id).first() is None
    # assert db.query(Symptom).filter(Symptom.pet_id == pet_id).first() is None
```

### **Clause P4: Local AI Processing**
*"AI processing occurs locally, data doesn't leave infrastructure"*

#### **Technical Controls**
- **Network Isolation**: AI service has no external internet access
- **Local LLM**: Ollama deployment with llama3.2:3b (default) or llama3.2:1b without external APIs
- **Monitoring**: Network traffic monitoring for data leakage

#### **Automated Tests**
```python
async def test_ai_service_network_isolation(client: AsyncClient):
    """Test AI service cannot access external networks"""
    # Monitor network calls during AI processing
    with network_monitor() as monitor:
        auth_headers = await get_auth_headers(client)
        pet_id = await create_test_pet(client, auth_headers)
        await create_test_symptoms(client, auth_headers, pet_id)
        
        # Trigger AI analysis
        response = await client.post(
            "/api/v1/symptoms/assess",
            json={"pet_id": str(pet_id)},
            headers=auth_headers
        )
        assert response.status_code == 200
    
    # Verify no external calls were made
    external_calls = monitor.get_external_calls()
    assert len(external_calls) == 0

async def test_local_llm_processing(client: AsyncClient):
    """Test AI processing uses local LLM only (Ollama at llama3.2:3b)"""
    auth_headers = await get_auth_headers(client)
    pet_id = await create_test_pet(client, auth_headers)
    await create_test_symptoms(client, auth_headers, pet_id)
    
    # Mock external requests to ensure none are made
    with mock.patch('aiohttp.ClientSession.post') as mock_external:
        response = await client.post(
            "/api/v1/symptoms/assess",
            json={"pet_id": str(pet_id)},
            headers=auth_headers
        )
        
        # Should succeed without external API calls
        assert response.status_code == 200
        data = response.json()
        assert "urgency_level" in data
        
        # Verify no external calls were attempted
        mock_external.assert_not_called()
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
async def test_ai_response_contains_disclaimer(client: AsyncClient):
    """Test all AI responses include medical disclaimer"""
    auth_headers = await get_auth_headers(client)
    pet_id = await create_test_pet(client, auth_headers)
    
    # Add symptoms to the pet first
    symptom_data = {
        "pet_id": str(pet_id), 
        "symptom_name": "lethargy", 
        "severity": "moderate", 
        "description": "Pet seems tired",
        "observed_at": datetime.now().isoformat() + "Z", 
        "duration_hours": 24
    }
    await client.post("/api/v1/symptoms/", json=symptom_data, headers=auth_headers)
    
    # Create assessment with simplified format
    response = await client.post(
        "/api/v1/symptoms/assess",
        json={"pet_id": str(pet_id)},
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    
    disclaimer_phrases = [
        "not professional veterinary advice",
        "consult a licensed veterinarian",
        "educational purposes only",
        "disclaimer"
    ]
    
    response_text = json.dumps(data).lower()
    assert any(phrase in response_text for phrase in disclaimer_phrases)

async def test_emergency_symptom_immediate_vet_referral(client: AsyncClient):
    """Test emergency symptoms trigger immediate vet recommendation"""
    auth_headers = await get_auth_headers(client)
    pet_id = await create_test_pet(client, auth_headers)
    
    # Add emergency symptoms
    emergency_symptoms = [
        {"pet_id": str(pet_id), "symptom_name": "difficulty breathing", "severity": "severe"},
        {"pet_id": str(pet_id), "symptom_name": "seizure", "severity": "severe"}
    ]
    
    for symptom in emergency_symptoms:
        await client.post("/api/v1/symptoms/", json=symptom, headers=auth_headers)
    
    response = await client.post(
        "/api/v1/symptoms/assess",
        json={"pet_id": str(pet_id)},
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["urgency_level"] == "emergency"
    assert "immediate veterinary care" in data["recommendations"][0].lower()
```

### **Clause E2: Conservative Health Advice**
*"AI should err on the side of caution for health recommendations"*

#### **Technical Controls**
- **Urgency Escalation**: Bias toward higher urgency levels
- **Prompt Engineering**: Conservative advice prompts
- **Response Validation**: Flag overly casual recommendations

#### **Automated Tests**
```python
async def test_conservative_urgency_assessment(client: AsyncClient):
    """Test AI tends toward conservative urgency levels"""
    auth_headers = await get_auth_headers(client)
    
    responses = []
    for i in range(10):  # Test multiple times for consistency
        pet_id = await create_test_pet(client, auth_headers, name=f"TestPet{i}")
        
        # Add ambiguous symptoms
        ambiguous_symptoms = [
            {"pet_id": str(pet_id), "symptom_name": "mild lethargy", "severity": "mild"},
            {"pet_id": str(pet_id), "symptom_name": "decreased appetite", "severity": "mild"}
        ]
        
        for symptom in ambiguous_symptoms:
            await client.post("/api/v1/symptoms/", json=symptom, headers=auth_headers)
        
        response = await client.post(
            "/api/v1/symptoms/assess",
            json={"pet_id": str(pet_id)},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        responses.append(data["urgency_level"])
    
    # Should tend toward moderate/high rather than low
    conservative_responses = sum(1 for r in responses if r in ["moderate", "high", "emergency"])
    assert conservative_responses >= len(responses) * 0.7  # 70% conservative

async def test_no_definitive_diagnoses(client: AsyncClient):
    """Test AI avoids definitive medical diagnoses"""
    auth_headers = await get_auth_headers(client)
    pet_id = await create_test_pet(client, auth_headers)
    
    # Add moderate symptoms
    symptom_data = {
        "pet_id": str(pet_id),
        "symptom_name": "vomiting", 
        "severity": "moderate"
    }
    await client.post("/api/v1/symptoms/", json=symptom_data, headers=auth_headers)
    
    response = await client.post(
        "/api/v1/symptoms/assess",
        json={"pet_id": str(pet_id)},
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Check that responses use cautious language
    causes_text = " ".join(data["possible_causes"]).lower()
    
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
async def test_consistent_advice_across_breeds(client: AsyncClient):
    """Test AI provides consistent advice regardless of breed"""
    auth_headers = await get_auth_headers(client)
    
    breeds_to_test = ["golden_retriever", "chihuahua", "german_shepherd", "mixed_breed"]
    responses = {}
    
    for breed in breeds_to_test:
        pet_data = {"name": f"Test{breed}", "species": "dog", "breed": breed, "age_years": 5}
        pet_id = await create_test_pet(client, auth_headers, **pet_data)
        
        # Add consistent symptoms
        symptom_data = {
            "pet_id": str(pet_id),
            "symptom_name": "lethargy", 
            "severity": "moderate"
        }
        await client.post("/api/v1/symptoms/", json=symptom_data, headers=auth_headers)
        
        response = await client.post(
            "/api/v1/symptoms/assess",
            json={"pet_id": str(pet_id)},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        responses[breed] = data["urgency_level"]
    
    # Urgency levels should be similar across breeds for same symptoms
    unique_urgencies = set(responses.values())
    assert len(unique_urgencies) <= 2  # Allow some variation but not extreme

async def test_species_appropriate_advice(client: AsyncClient):
    """Test AI provides species-appropriate advice"""
    auth_headers = await get_auth_headers(client)
    
    # Test cat (appropriate for hairball) vs dog (inappropriate symptom)
    cat_id = await create_test_pet(client, auth_headers, name="TestCat", species="cat")
    dog_id = await create_test_pet(client, auth_headers, name="TestDog", species="dog")
    
    hairball_symptom = {"symptom_name": "hairball", "severity": "mild"}
    
    # Add hairball symptom to both pets
    await client.post("/api/v1/symptoms/", 
                     json={**hairball_symptom, "pet_id": str(cat_id)}, 
                     headers=auth_headers)
    await client.post("/api/v1/symptoms/", 
                     json={**hairball_symptom, "pet_id": str(dog_id)}, 
                     headers=auth_headers)
    
    # Get assessments for both
    cat_response = await client.post("/api/v1/symptoms/assess",
                                   json={"pet_id": str(cat_id)},
                                   headers=auth_headers)
    dog_response = await client.post("/api/v1/symptoms/assess",
                                   json={"pet_id": str(dog_id)},
                                   headers=auth_headers)
    
    assert cat_response.status_code == 200
    assert dog_response.status_code == 200
    
    cat_data = cat_response.json()
    dog_data = dog_response.json()
    
    # Cat should have normal hairball advice
    assert "normal" in cat_data["recommendations"][0].lower()
    
    # Dog should flag as unusual (dogs don't get hairballs)
    assert dog_data["urgency_level"] in ["moderate", "high"]
```

## Compliance Monitoring

### **Automated Compliance Checks**
```python
class ComplianceMonitor:
    def __init__(self, client: AsyncClient):
        self.client = client
        self.compliance_tests = [
            self.check_data_minimization,
            self.check_medical_disclaimers,
            self.check_privacy_controls,
            self.check_ai_conservative_bias
        ]
    
    async def run_daily_compliance_check(self):
        """Run all compliance tests daily using current API"""
        results = {}
        auth_headers = await get_auth_headers(self.client)
        
        for test in self.compliance_tests:
            try:
                test_result = await test(auth_headers)
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
    
    async def check_medical_disclaimers(self, auth_headers):
        """Verify all AI assessments contain medical disclaimers"""
        pet_id = await create_test_pet(self.client, auth_headers)
        await create_test_symptoms(self.client, auth_headers, pet_id)
        
        response = await self.client.post(
            "/api/v1/symptoms/assess",
            json={"pet_id": str(pet_id)},
            headers=auth_headers
        )
        
        if response.status_code != 200:
            return False
            
        data = response.json()
        disclaimer_text = json.dumps(data).lower()
        return "disclaimer" in disclaimer_text or "not professional veterinary advice" in disclaimer_text
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
    
    async def test_no_external_ai_calls(self, client: AsyncClient):
        """CRITICAL: Ensure no data leaves our infrastructure"""
        auth_headers = await get_auth_headers(client)
        pet_id = await create_test_pet(client, auth_headers)
        await create_test_symptoms(client, auth_headers, pet_id)
        
        with monitor_network_traffic() as monitor:
            response = await client.post(
                "/api/v1/symptoms/assess",
                json={"pet_id": str(pet_id)},
                headers=auth_headers
            )
            assert response.status_code == 200
            
        external_calls = monitor.get_external_network_calls()
        assert len(external_calls) == 0, f"Unauthorized external calls: {external_calls}"
    
    async def test_user_data_isolation(self, client: AsyncClient):
        """CRITICAL: Users can only access their own data"""
        user1_headers = await get_auth_headers(client, username="user1")
        user2_headers = await get_auth_headers(client, username="user2")
        
        user1_pet_id = await create_test_pet(client, user1_headers)
        
        # User2 should not be able to access User1's pet
        response = await client.get(f"/api/v1/pets/{user1_pet_id}", headers=user2_headers)
        assert response.status_code == 404, "Users can access other users' data!"
    
    async def test_ai_never_gives_definitive_diagnosis(self, client: AsyncClient):
        """CRITICAL: AI never provides definitive medical diagnoses"""
        auth_headers = await get_auth_headers(client)
        
        # Test with various symptom combinations
        test_symptoms = [
            ["vomiting", "diarrhea"],
            ["lethargy", "loss_of_appetite"],
            ["coughing", "difficulty_breathing"]
        ]
        
        for symptom_names in test_symptoms:
            pet_id = await create_test_pet(client, auth_headers)
            
            for symptom_name in symptom_names:
                symptom_data = {
                    "pet_id": str(pet_id),
                    "symptom_name": symptom_name,
                    "severity": "moderate"
                }
                await client.post("/api/v1/symptoms/", json=symptom_data, headers=auth_headers)
            
            response = await client.post(
                "/api/v1/symptoms/assess",
                json={"pet_id": str(pet_id)},
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            response_text = json.dumps(data).lower()
            
            forbidden_phrases = ["diagnosed with", "definitely has", "certainly"]
            for phrase in forbidden_phrases:
                assert phrase not in response_text, f"AI gave definitive diagnosis: {phrase}"
```

## Ethics Debt Tracking

Ethics debt items are now tracked in a dedicated ledger for better organization and visibility.

**See: [Ethics Debt Ledger](./ethics_debt_ledger.md)**

The ethics debt ledger includes:
- Current open ethics debt items with priorities and target dates
- Recently resolved ethics debt with implementation details
- Ethics debt management process and prioritization framework
- Progress tracking and transparency commitments

This framework ensures continuous monitoring of ethical and privacy commitments through automated testing and compliance tracking.