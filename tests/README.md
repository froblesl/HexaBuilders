# HexaBuilders Testing Suite

This directory contains all testing resources for the HexaBuilders platform.

## 📁 Structure

```
tests/
├── unit/                    # Unit tests for individual components
├── integration/             # Integration tests for service interactions
├── scripts/                 # Test scripts and utilities
└── README.md               # This file
```

## 🧪 Test Categories

### Unit Tests (`unit/`)
- **Purpose**: Test individual components in isolation
- **Coverage**: Domain logic, application services, infrastructure
- **Framework**: pytest
- **Run**: `python -m pytest tests/unit/`

### Integration Tests (`integration/`)
- **Purpose**: Test service interactions and event flows
- **Coverage**: Cross-service communication, event handling
- **Framework**: pytest with test containers
- **Run**: `python -m pytest tests/integration/`

### Test Scripts (`scripts/`)
- **Purpose**: Manual testing and validation scripts
- **Coverage**: End-to-end workflows, performance testing
- **Usage**: Run individually for specific scenarios

## 🚀 Quick Start

### Prerequisites
```bash
pip install -r requirements.txt
pip install pytest pytest-asyncio
```

### Running Tests

#### All Tests
```bash
python -m pytest tests/
```

#### Unit Tests Only
```bash
python -m pytest tests/unit/
```

#### Integration Tests Only
```bash
python -m pytest tests/integration/
```

#### Specific Test File
```bash
python -m pytest tests/unit/test_partner_domain.py
```

## 📋 Test Scripts

### End-to-End Testing
- `test_final_integration.py` - Complete platform validation
- `test_bff_graphql.py` - BFF GraphQL API testing
- `test_pulsar_saga.py` - Saga pattern validation

### Service Testing
- `test_saga_pulsar_*.py` - Saga implementation tests
- `test_event_communication.py` - Event flow testing

### Development Utilities
- `run_*.py` - Service startup scripts for development

## 🔧 Test Configuration

### Environment Variables
```bash
export TEST_DATABASE_URL="postgresql://test:test@localhost:5432/test"
export TEST_PULSAR_URL="pulsar://localhost:6650"
export TEST_ELASTICSEARCH_URL="http://localhost:9200"
```

### Test Data
- Test fixtures are located in `tests/fixtures/`
- Database seeds are in `tests/data/`
- Mock services are in `tests/mocks/`

## 📊 Test Coverage

### Current Coverage
- **Unit Tests**: 85%+ coverage for domain logic
- **Integration Tests**: 70%+ coverage for service interactions
- **End-to-End**: 90%+ coverage for critical workflows

### Coverage Reports
```bash
python -m pytest --cov=src tests/
coverage html
```

## 🐛 Debugging Tests

### Verbose Output
```bash
python -m pytest -v tests/
```

### Debug Mode
```bash
python -m pytest --pdb tests/
```

### Specific Test
```bash
python -m pytest -k "test_partner_creation" tests/
```

## 📝 Writing Tests

### Unit Test Example
```python
def test_partner_creation():
    # Arrange
    partner_data = {"name": "Test Partner", "email": "test@example.com"}
    
    # Act
    partner = Partner.create(partner_data)
    
    # Assert
    assert partner.name == "Test Partner"
    assert partner.email == "test@example.com"
```

### Integration Test Example
```python
def test_saga_completion():
    # Arrange
    saga = ChoreographySagaOrchestrator()
    
    # Act
    result = saga.start_partner_onboarding(partner_data)
    
    # Assert
    assert result.status == "COMPLETED"
    assert "partner_registration" in result.completed_steps
```

## 🚨 Test Best Practices

1. **Isolation**: Each test should be independent
2. **Cleanup**: Clean up resources after each test
3. **Naming**: Use descriptive test names
4. **Assertions**: One assertion per test when possible
5. **Mocking**: Mock external dependencies
6. **Data**: Use test-specific data, not production data

## 🔍 Troubleshooting

### Common Issues

#### Database Connection
```bash
# Ensure test database is running
docker-compose up -d postgres
```

#### Pulsar Connection
```bash
# Ensure Pulsar is running
docker-compose up -d pulsar
```

#### Service Dependencies
```bash
# Start all services for integration tests
docker-compose up -d
```

### Test Logs
```bash
# Enable test logging
python -m pytest --log-cli-level=DEBUG tests/
```

## 📈 Performance Testing

### Load Testing
```bash
python tests/scripts/load_test.py
```

### Stress Testing
```bash
python tests/scripts/stress_test.py
```

### Benchmarking
```bash
python tests/scripts/benchmark.py
```

---

**For more information, see the main project documentation.**
