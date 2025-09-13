# Integration Tests

This directory contains comprehensive integration tests for the HexaBuilders microservices platform.

## Test Structure

### Test Files

- **`test_cross_service_integration.py`** - Tests for cross-service communication and complete workflows
- **`test_event_integration.py`** - Tests for event-driven integration between services  
- **`test_performance_integration.py`** - Performance and load tests for the integrated system
- **`conftest.py`** - Shared fixtures and configuration for all integration tests

### Test Categories

#### Cross-Service Integration Tests
- Partner registration → Contract creation → Campaign/Job workflows
- Complete partner lifecycle testing
- Profile 360 API integration across all services
- Service resilience and fallback behavior

#### Event Integration Tests  
- Integration event handling between services
- Event dispatching and routing
- Commission calculation workflows
- Notification system integration
- Error handling in event processing

#### Performance Integration Tests
- Concurrent partner creation performance
- Profile 360 API response time under load
- Cross-service workflow performance
- Database connection pooling under load
- Search performance with ElasticSearch
- Memory and resource usage testing

## Running Integration Tests

### Prerequisites

1. **Start all services** using Docker Compose:
   ```bash
   cd HexaBuilders
   docker-compose up -d
   ```

2. **Wait for services to be ready** (about 30-60 seconds for full startup)

3. **Verify service health**:
   ```bash
   curl http://localhost:5000/health  # Partner Management
   curl http://localhost:5001/health  # Onboarding
   curl http://localhost:5002/health  # Recruitment
   curl http://localhost:5003/health  # Campaign Management
   ```

### Run All Integration Tests

```bash
# Run all integration tests
pytest tests/integration/ -v

# Run with coverage
pytest tests/integration/ --cov=src --cov-report=html -v

# Run only cross-service tests
pytest tests/integration/test_cross_service_integration.py -v

# Run only event integration tests  
pytest tests/integration/test_event_integration.py -v

# Run only performance tests (these take longer)
pytest tests/integration/test_performance_integration.py -v
```

### Run Tests by Marker

```bash
# Run only performance tests
pytest -m performance tests/integration/ -v

# Run only event-driven tests
pytest -m event_driven tests/integration/ -v

# Run only cross-service tests
pytest -m cross_service tests/integration/ -v

# Skip slow tests
pytest -m "not slow" tests/integration/ -v
```

### Parallel Test Execution

For faster execution (requires pytest-xdist):

```bash
# Install pytest-xdist if not already installed
pip install pytest-xdist

# Run tests in parallel
pytest tests/integration/ -n auto -v
```

## Test Configuration

### Environment Variables

You can override service URLs using environment variables:

```bash
export PARTNER_MANAGEMENT_URL=http://localhost:5000
export ONBOARDING_URL=http://localhost:5001
export RECRUITMENT_URL=http://localhost:5002
export CAMPAIGN_MANAGEMENT_URL=http://localhost:5003
export NOTIFICATIONS_URL=http://localhost:5004
```

### Service Health Checks

The integration tests automatically perform health checks before running. If services are not healthy, tests will be skipped with appropriate messages.

## Test Data Management

### Fixtures

The tests use pytest fixtures to create consistent test data:

- `test_partner` - Creates a test partner for use across tests
- `test_contract` - Creates a test contract linked to a partner
- `test_campaign` - Creates a test campaign 
- `test_job` - Creates a test job posting
- `test_candidate` - Creates a test candidate

### Cleanup

Currently, test data is left in the system for manual inspection. In production, you may want to implement cleanup routines.

## Performance Benchmarks

The performance tests include the following benchmarks:

### Response Time Targets
- Partner creation: < 2 seconds average
- Profile 360 API: < 2 seconds average, < 5 seconds 95th percentile
- Search operations: < 1 second average, < 2 seconds 95th percentile
- Cross-service workflows: < 10 seconds average

### Throughput Targets
- Partner creation: > 5 partners/second
- Concurrent operations: 80%+ success rate under load

### Load Testing
- 50 concurrent partner creations
- 30 concurrent campaign operations  
- 25 concurrent search operations
- 50 concurrent database operations

## Troubleshooting

### Common Issues

1. **Services not starting**: Check Docker Compose logs
   ```bash
   docker-compose logs partner-management
   docker-compose logs onboarding
   # etc.
   ```

2. **Database connection issues**: Ensure PostgreSQL is healthy
   ```bash
   docker-compose logs postgres
   ```

3. **ElasticSearch issues**: Check ElasticSearch service
   ```bash
   docker-compose logs elasticsearch
   curl http://localhost:9200/_health
   ```

4. **Pulsar issues**: Check message broker
   ```bash
   docker-compose logs broker
   ```

### Test Failures

1. **Service health check failures**: Wait longer for services to start, or check service logs

2. **Performance test failures**: May indicate resource constraints or service issues

3. **Event integration failures**: Check Pulsar broker and event handling

### Debug Mode

Run tests with more verbose output:

```bash
# Maximum verbosity
pytest tests/integration/ -vvv -s

# Show test output
pytest tests/integration/ -v -s --tb=long
```

## Integration Test Development

### Adding New Tests

1. **Cross-service tests**: Add to `test_cross_service_integration.py`
2. **Event tests**: Add to `test_event_integration.py`  
3. **Performance tests**: Add to `test_performance_integration.py`

### Test Guidelines

1. Use async/await for all HTTP operations
2. Include proper error handling and timeouts
3. Use fixtures for consistent test data
4. Add performance assertions for load tests
5. Include cleanup when necessary
6. Use descriptive test names and docstrings

### Fixture Development

Add new fixtures to `conftest.py` for reusable test components.

## Continuous Integration

These integration tests are designed to run in CI/CD pipelines:

1. **Docker Compose** setup for service orchestration
2. **Health checks** ensure services are ready
3. **Automatic skipping** when services are unavailable
4. **Performance benchmarks** to catch regressions
5. **Comprehensive coverage** of integration scenarios