"""
Configuration for integration tests

This module provides shared fixtures and configuration for integration tests
across the HexaBuilders microservices platform.
"""

import pytest
import asyncio
import httpx
import time
import os
from typing import Dict, Any


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def service_base_urls():
    """Base URLs for all microservices"""
    return {
        "partner_management": os.getenv("PARTNER_MANAGEMENT_URL", "http://localhost:5000"),
        "onboarding": os.getenv("ONBOARDING_URL", "http://localhost:5001"),
        "recruitment": os.getenv("RECRUITMENT_URL", "http://localhost:5002"),
        "campaign_management": os.getenv("CAMPAIGN_MANAGEMENT_URL", "http://localhost:5003"),
        "notifications": os.getenv("NOTIFICATIONS_URL", "http://localhost:5004")
    }


@pytest.fixture(scope="session")
async def service_health_check(service_base_urls):
    """
    Verify all services are healthy before running integration tests.
    This fixture runs once per test session.
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        max_attempts = 30
        services_ready = {}
        
        for service_name, base_url in service_base_urls.items():
            print(f"Checking health of {service_name} at {base_url}")
            
            for attempt in range(max_attempts):
                try:
                    response = await client.get(f"{base_url}/health")
                    if response.status_code == 200:
                        services_ready[service_name] = True
                        print(f"✓ {service_name} is healthy")
                        break
                except Exception as e:
                    if attempt == max_attempts - 1:
                        print(f"✗ {service_name} health check failed: {e}")
                        services_ready[service_name] = False
                    else:
                        await asyncio.sleep(1)
        
        # Report service status
        healthy_services = sum(services_ready.values())
        total_services = len(services_ready)
        
        print(f"\nService Health Summary: {healthy_services}/{total_services} services healthy")
        for service, is_healthy in services_ready.items():
            status = "✓" if is_healthy else "✗"
            print(f"  {status} {service}")
        
        if healthy_services < total_services:
            pytest.skip(f"Only {healthy_services}/{total_services} services are healthy. Skipping integration tests.")
        
        return services_ready


@pytest.fixture
async def http_client():
    """HTTP client for making requests to services"""
    limits = httpx.Limits(max_keepalive_connections=10, max_connections=50)
    timeout = httpx.Timeout(30.0)
    
    async with httpx.AsyncClient(limits=limits, timeout=timeout) as client:
        yield client


@pytest.fixture
def sample_partner_data():
    """Sample partner data for testing"""
    from uuid import uuid4
    
    return {
        "nombre": f"Test Partner {uuid4()}",
        "email": f"test-{uuid4()}@example.com",
        "telefono": "+1-555-0123",
        "tipo": "EMPRESA",
        "direccion": "123 Test Street",
        "ciudad": "Test City",
        "pais": "Test Country"
    }


@pytest.fixture
def sample_candidate_data():
    """Sample candidate data for testing"""
    from uuid import uuid4
    
    return {
        "name": f"Test Candidate {uuid4()}",
        "email": f"candidate-{uuid4()}@example.com",
        "phone": "+1-555-0199",
        "location": "Remote",
        "years_of_experience": 5,
        "expected_salary": 75000.0,
        "skills": ["Python", "Flask", "PostgreSQL", "Docker"],
        "education": [
            {
                "degree": "Bachelor of Computer Science",
                "institution": "Test University",
                "year": 2018
            }
        ],
        "availability": "AVAILABLE"
    }


@pytest.fixture
def sample_job_data():
    """Sample job data for testing"""
    from uuid import uuid4
    
    return {
        "title": f"Test Position {uuid4()}",
        "description": "A test job posting for integration tests",
        "location": "Remote",
        "salary_min": 60000.0,
        "salary_max": 90000.0,
        "job_type": "FULL_TIME",
        "experience_level": "MID_LEVEL",
        "required_skills": ["Python", "Flask", "PostgreSQL"],
        "preferred_skills": ["Docker", "Kubernetes"],
        "requirements": {
            "education": "Bachelor's degree preferred",
            "experience_years": 3
        }
    }


@pytest.fixture
def sample_campaign_data():
    """Sample campaign data for testing"""
    from uuid import uuid4
    from datetime import datetime, timedelta
    
    return {
        "name": f"Test Campaign {uuid4()}",
        "description": "A test marketing campaign for integration tests",
        "campaign_type": "DIGITAL_MARKETING",
        "budget": 10000.0,
        "target_audience": {
            "age_range": "25-45",
            "interests": ["technology", "business"],
            "location": "North America"
        },
        "schedule": {
            "start_date": (datetime.utcnow() + timedelta(days=1)).isoformat(),
            "end_date": (datetime.utcnow() + timedelta(days=30)).isoformat()
        }
    }


@pytest.fixture
def sample_contract_data():
    """Sample contract data for testing"""
    return {
        "contract_type": "STANDARD",
        "terms": {
            "duration": "12_MONTHS",
            "commission_rate": 0.15,
            "can_create_campaigns": True,
            "can_post_jobs": True,
            "max_campaign_budget": 50000.0,
            "max_concurrent_jobs": 10
        }
    }


@pytest.fixture
async def test_partner(http_client, service_base_urls, sample_partner_data):
    """Create a test partner for use in integration tests"""
    response = await http_client.post(
        f"{service_base_urls['partner_management']}/partners",
        json=sample_partner_data
    )
    
    if response.status_code == 201:
        partner = response.json()
        yield partner
        
        # Cleanup: In a real scenario, you might want to clean up test data
        # For now, we'll leave the test data for manual inspection
    else:
        pytest.fail(f"Failed to create test partner: {response.status_code} - {response.text}")


@pytest.fixture
async def test_contract(http_client, service_base_urls, test_partner, sample_contract_data):
    """Create a test contract for use in integration tests"""
    contract_data = {**sample_contract_data, "partner_id": test_partner["id"]}
    
    response = await http_client.post(
        f"{service_base_urls['onboarding']}/contracts",
        json=contract_data
    )
    
    if response.status_code == 201:
        contract = response.json()
        yield contract
    else:
        pytest.fail(f"Failed to create test contract: {response.status_code} - {response.text}")


@pytest.fixture
async def test_campaign(http_client, service_base_urls, test_partner, sample_campaign_data):
    """Create a test campaign for use in integration tests"""
    campaign_data = {**sample_campaign_data, "partner_id": test_partner["id"]}
    
    response = await http_client.post(
        f"{service_base_urls['campaign_management']}/campaigns",
        json=campaign_data
    )
    
    if response.status_code == 201:
        campaign = response.json()
        yield campaign
    else:
        pytest.fail(f"Failed to create test campaign: {response.status_code} - {response.text}")


@pytest.fixture
async def test_job(http_client, service_base_urls, test_partner, sample_job_data):
    """Create a test job for use in integration tests"""
    job_data = {**sample_job_data, "partner_id": test_partner["id"]}
    
    response = await http_client.post(
        f"{service_base_urls['recruitment']}/jobs",
        json=job_data
    )
    
    if response.status_code == 201:
        job = response.json()
        yield job
    else:
        pytest.fail(f"Failed to create test job: {response.status_code} - {response.text}")


@pytest.fixture
async def test_candidate(http_client, service_base_urls, sample_candidate_data):
    """Create a test candidate for use in integration tests"""
    response = await http_client.post(
        f"{service_base_urls['recruitment']}/candidates",
        json=sample_candidate_data
    )
    
    if response.status_code == 201:
        candidate = response.json()
        yield candidate
    else:
        pytest.fail(f"Failed to create test candidate: {response.status_code} - {response.text}")


@pytest.mark.asyncio
async def wait_for_event_propagation(seconds: float = 2.0):
    """Helper function to wait for integration events to propagate between services"""
    await asyncio.sleep(seconds)


# Performance testing utilities
class PerformanceMetrics:
    """Utility class for collecting and analyzing performance metrics"""
    
    def __init__(self):
        self.response_times = []
        self.success_count = 0
        self.error_count = 0
        self.start_time = None
        self.end_time = None
    
    def start(self):
        self.start_time = time.time()
    
    def end(self):
        self.end_time = time.time()
    
    def record_response(self, response_time: float, success: bool = True):
        self.response_times.append(response_time)
        if success:
            self.success_count += 1
        else:
            self.error_count += 1
    
    @property
    def total_requests(self):
        return self.success_count + self.error_count
    
    @property
    def success_rate(self):
        if self.total_requests == 0:
            return 0
        return self.success_count / self.total_requests
    
    @property
    def average_response_time(self):
        if not self.response_times:
            return 0
        return sum(self.response_times) / len(self.response_times)
    
    @property
    def p95_response_time(self):
        if not self.response_times:
            return 0
        sorted_times = sorted(self.response_times)
        index = int(0.95 * len(sorted_times))
        return sorted_times[index] if index < len(sorted_times) else sorted_times[-1]
    
    @property
    def throughput(self):
        if not self.start_time or not self.end_time:
            return 0
        duration = self.end_time - self.start_time
        return self.success_count / duration if duration > 0 else 0
    
    def summary(self):
        return {
            "total_requests": self.total_requests,
            "success_count": self.success_count,
            "error_count": self.error_count,
            "success_rate": self.success_rate,
            "average_response_time": self.average_response_time,
            "p95_response_time": self.p95_response_time,
            "throughput": self.throughput
        }


@pytest.fixture
def performance_metrics():
    """Fixture providing performance metrics collection"""
    return PerformanceMetrics()


# Test markers for different types of integration tests
pytest_plugins = []

def pytest_configure(config):
    """Configure custom markers for integration tests"""
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as a performance test"
    )
    config.addinivalue_line(
        "markers", "event_driven: mark test as testing event-driven functionality"
    )
    config.addinivalue_line(
        "markers", "cross_service: mark test as testing cross-service communication"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


# Test collection hooks
def pytest_collection_modifyitems(config, items):
    """Automatically mark integration tests based on file location"""
    for item in items:
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
            
        if "performance" in item.name.lower():
            item.add_marker(pytest.mark.performance)
            item.add_marker(pytest.mark.slow)
            
        if "event" in item.name.lower():
            item.add_marker(pytest.mark.event_driven)
            
        if "cross_service" in item.name.lower():
            item.add_marker(pytest.mark.cross_service)