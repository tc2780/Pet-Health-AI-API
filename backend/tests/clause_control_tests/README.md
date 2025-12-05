# Clause Control Tests

This directory contains automated tests that verify privacy and ethics clauses are properly implemented as technical controls in the Pet Health AI API.

## Structure

Each test file corresponds to a specific compliance clause category:

### Privacy Clauses (P1-P4)
- **`test_p1_data_minimization.py`** - P1: "Collect only data necessary for pet health management"
- **`test_p2_purpose_limitation.py`** - P2: "Use pet data only for health management, not marketing"
- **`test_p3_user_control.py`** - P3: "Users can access, modify, and delete their data"
- **`test_p4_local_ai_processing.py`** - P4: "AI processing occurs locally, data doesn't leave infrastructure"

### Ethics Clauses (E1-E3)
- **`test_e1_medical_disclaimer.py`** - E1: "All AI responses must include medical disclaimer"
- **`test_e2_conservative_advice.py`** - E2: "AI should err on the side of caution for health recommendations"
- **`test_e3_bias_prevention.py`** - E3: "AI advice should be fair across all pet breeds and species"

## Support Files
- **`helpers.py`** - Shared helper functions for test setup and execution
- **`conftest.py`** - Pytest configuration and fixtures
- **`__init__.py`** - Package documentation and overview

## Running the Tests

### Docker Testing (Recommended)

Run compliance tests in Docker environment:

```bash
# Run all compliance tests via Docker test runner
./run-docker-tests.sh standard   # Includes compliance tests as part of standard suite

# Manual Docker execution
docker compose up -d
docker compose exec api python -m pytest tests/clause_control_tests/ -v

# Run specific compliance categories
docker compose exec api python -m pytest tests/clause_control_tests/ -m privacy -v
docker compose exec api python -m pytest tests/clause_control_tests/ -m ethics -v
```

### Local Development Testing

```bash
# From backend directory
python -m pytest tests/clause_control_tests/ -v

# Using Docker
docker compose exec api python -m pytest tests/clause_control_tests/ -v
```

### Run Specific Clause Categories
```bash
# Privacy clauses only
python -m pytest tests/clause_control_tests/test_p*.py -v

# Ethics clauses only  
python -m pytest tests/clause_control_tests/test_e*.py -v

# Specific clause
python -m pytest tests/clause_control_tests/test_p1_data_minimization.py -v
```

### Run with Coverage
```bash
python -m pytest tests/clause_control_tests/ --cov=app --cov-report=html
```

## Test Categories

### Privacy Compliance Tests
These tests verify that the system respects user privacy and follows data protection best practices:

- **Data Minimization**: Only necessary data is collected and stored
- **Purpose Limitation**: Data is used only for stated health management purposes
- **User Control**: Users have full control over their data (access, modify, delete)
- **Local Processing**: Sensitive data never leaves the organization's infrastructure

### Ethics Compliance Tests
These tests ensure responsible AI behavior and medical ethics compliance:

- **Medical Disclaimers**: All AI outputs include appropriate medical disclaimers
- **Conservative Advice**: AI errs on the side of caution for health recommendations
- **Bias Prevention**: Fair treatment across all pet breeds and species

## Technical Implementation

### Test Architecture
- **Async Testing**: Uses `httpx.AsyncClient` for realistic API testing
- **Isolated Tests**: Each test creates its own test data to avoid interference
- **Comprehensive Coverage**: Tests cover both positive and negative scenarios
- **Real API Integration**: Tests run against actual FastAPI endpoints

### Compliance Mapping
Each test maps directly to:
1. **Clause**: The specific privacy/ethics requirement
2. **Control**: The technical implementation that enforces the clause  
3. **Verification**: The automated test that validates the control works

### Documentation Standard
Every test includes:
- **Purpose**: What clause is being tested and why
- **Control**: What technical mechanism enforces compliance
- **Verification**: What the test validates
- **Rationale**: Why this clause matters for privacy/ethics

## Compliance Reporting

### Test Results Integration
These tests are integrated into the main test suite and contribute to:
- Overall test coverage metrics
- Compliance dashboard reporting
- CI/CD pipeline validation
- Audit trail documentation

### Failure Handling
- **Critical Tests**: Some tests are marked as "Red Bar" - they must never fail in production
- **Monitoring**: Test failures trigger compliance alerts
- **Documentation**: All test results are logged for audit purposes

## Maintenance

### Adding New Clauses
1. Create new test file following the naming pattern: `test_[category][number]_[description].py`
2. Add comprehensive documentation explaining the clause and its importance
3. Implement tests that verify both compliance and non-compliance scenarios
4. Update this README with the new clause information

### Updating Tests
- Tests should be updated when compliance requirements change
- Always maintain backward compatibility with existing compliance reports
- Document any changes that affect compliance interpretation

## Relationship to Documentation

These tests implement the compliance framework documented in:
- `docs/compliance/clause-control-test.md` - Detailed clause→control→test mapping
- `docs/compliance/ethics-framework.md` - Ethics principles and guidelines
- `docs/compliance/trust-model.md` - Security and privacy model

## Audit Trail

All test executions are logged and can be used to demonstrate compliance during:
- Regulatory audits
- Security assessments
- Privacy compliance reviews
- Ethics committee evaluations