import pytest
import asyncio
import httpx
import json
from datetime import datetime, timedelta
from uuid import uuid4
import time


class TestCrossServiceIntegration:
    """Integration tests for cross-service communication and workflows"""
    
    @pytest.fixture
    def service_urls(self):
        """Service URLs for testing"""
        return {
            "partner_management": "http://localhost:5000",
            "onboarding": "http://localhost:5001", 
            "recruitment": "http://localhost:5002",
            "campaign_management": "http://localhost:5003"
        }
    
    @pytest.fixture
    async def http_client(self):
        """Async HTTP client for testing"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            yield client
    
    @pytest.fixture
    def sample_partner_data(self):
        """Sample partner data for testing"""
        return {
            "nombre": "Test Partner Corp",
            "email": f"test-{uuid4()}@testcorp.com",
            "telefono": "+1-555-0123",
            "tipo": "EMPRESA",
            "direccion": "123 Test Street",
            "ciudad": "Test City",
            "pais": "Test Country"
        }
    
    async def wait_for_service(self, client: httpx.AsyncClient, url: str, max_attempts=30):
        """Wait for service to be ready"""
        for attempt in range(max_attempts):
            try:
                response = await client.get(f"{url}/health")
                if response.status_code == 200:
                    return True
            except:
                pass
            await asyncio.sleep(1)
        return False
    
    @pytest.mark.asyncio
    async def test_services_health_check(self, http_client, service_urls):
        """Test that all services are healthy and responding"""
        for service_name, url in service_urls.items():
            assert await self.wait_for_service(http_client, url), f"{service_name} service not healthy"
            
            response = await http_client.get(f"{url}/health")
            assert response.status_code == 200
            health_data = response.json()
            assert health_data["status"] == "healthy"
            assert service_name.replace("_", "-") in health_data["service"]
    
    @pytest.mark.asyncio
    async def test_partner_registration_to_onboarding_flow(self, http_client, service_urls, sample_partner_data):
        """Test complete partner registration -> contract creation flow"""
        
        # Step 1: Create partner in Partner Management
        response = await http_client.post(
            f"{service_urls['partner_management']}/partners",
            json=sample_partner_data
        )
        assert response.status_code == 201
        partner = response.json()
        partner_id = partner["id"]
        
        # Wait a moment for integration events to propagate
        await asyncio.sleep(2)
        
        # Step 2: Create contract in Onboarding service for the partner
        contract_data = {
            "partner_id": partner_id,
            "contract_type": "STANDARD",
            "terms": {
                "duration": "12_MONTHS",
                "commission_rate": 0.15,
                "can_create_campaigns": True,
                "max_budget": 50000.0
            }
        }
        
        response = await http_client.post(
            f"{service_urls['onboarding']}/contracts",
            json=contract_data
        )
        assert response.status_code == 201
        contract = response.json()
        contract_id = contract["id"]
        
        # Step 3: Sign the contract
        signature_data = {
            "signer": "John Doe",
            "signature_method": "DIGITAL",
            "signature_data": "digital_signature_hash_123",
            "ip_address": "192.168.1.100"
        }
        
        response = await http_client.post(
            f"{service_urls['onboarding']}/contracts/{contract_id}/sign",
            json=signature_data
        )
        assert response.status_code == 200
        
        # Step 4: Activate the contract
        response = await http_client.post(
            f"{service_urls['onboarding']}/contracts/{contract_id}/activate"
        )
        assert response.status_code == 200
        
        # Wait for integration events to propagate back to Partner Management
        await asyncio.sleep(3)
        
        # Step 5: Verify partner status was updated in Partner Management
        response = await http_client.get(
            f"{service_urls['partner_management']}/{partner_id}/validation-status"
        )
        assert response.status_code == 200
        validation_status = response.json()
        assert validation_status["is_validated"] == True
        assert validation_status["can_create_campaigns"] == True
    
    @pytest.mark.asyncio
    async def test_campaign_creation_with_partner_validation(self, http_client, service_urls, sample_partner_data):
        """Test campaign creation with partner validation flow"""
        
        # Step 1: Create and activate partner
        response = await http_client.post(
            f"{service_urls['partner_management']}/partners",
            json=sample_partner_data
        )
        partner_id = response.json()["id"]
        
        await asyncio.sleep(1)
        
        # Step 2: Create campaign
        campaign_data = {
            "partner_id": partner_id,
            "name": "Test Marketing Campaign",
            "description": "Integration test campaign",
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
        
        response = await http_client.post(
            f"{service_urls['campaign_management']}/campaigns",
            json=campaign_data
        )
        assert response.status_code == 201
        campaign = response.json()
        campaign_id = campaign["id"]
        
        # Step 3: Launch the campaign
        response = await http_client.post(
            f"{service_urls['campaign_management']}/campaigns/{campaign_id}/launch"
        )
        assert response.status_code == 200
        
        # Wait for events to propagate
        await asyncio.sleep(2)
        
        # Step 4: Verify campaign appears in partner profile 360
        response = await http_client.get(
            f"{service_urls['partner_management']}/{partner_id}/profile-360"
        )
        assert response.status_code == 200
        profile = response.json()
        assert profile["campaigns"]["total"] >= 1
        assert any(c["id"] == campaign_id for c in profile["campaigns"]["recent_campaigns"])
    
    @pytest.mark.asyncio 
    async def test_recruitment_job_posting_flow(self, http_client, service_urls, sample_partner_data):
        """Test job posting and candidate matching flow"""
        
        # Step 1: Create partner
        response = await http_client.post(
            f"{service_urls['partner_management']}/partners",
            json=sample_partner_data
        )
        partner_id = response.json()["id"]
        
        # Step 2: Create job posting
        job_data = {
            "partner_id": partner_id,
            "title": "Senior Software Engineer",
            "description": "Looking for an experienced software engineer",
            "location": "Remote",
            "salary_min": 80000.0,
            "salary_max": 120000.0,
            "job_type": "FULL_TIME",
            "experience_level": "SENIOR",
            "required_skills": ["Python", "Flask", "PostgreSQL", "Docker"],
            "preferred_skills": ["Kubernetes", "AWS", "React"],
            "requirements": {
                "education": "Bachelor's degree preferred",
                "experience_years": 5
            }
        }
        
        response = await http_client.post(
            f"{service_urls['recruitment']}/jobs",
            json=job_data
        )
        assert response.status_code == 201
        job = response.json()
        job_id = job["id"]
        
        # Step 3: Publish the job
        response = await http_client.post(
            f"{service_urls['recruitment']}/jobs/{job_id}/publish"
        )
        assert response.status_code == 200
        
        # Step 4: Create a candidate
        candidate_data = {
            "name": "Jane Smith",
            "email": f"jane.smith.{uuid4()}@email.com",
            "phone": "+1-555-0199",
            "location": "Remote",
            "years_of_experience": 6,
            "expected_salary": 95000.0,
            "skills": ["Python", "Flask", "PostgreSQL", "Docker", "Kubernetes"],
            "education": [
                {
                    "degree": "Bachelor of Computer Science",
                    "institution": "Test University",
                    "year": 2017
                }
            ],
            "work_history": [
                {
                    "company": "Tech Corp",
                    "position": "Software Engineer",
                    "duration": "3 years",
                    "description": "Backend development"
                }
            ]
        }
        
        response = await http_client.post(
            f"{service_urls['recruitment']}/candidates",
            json=candidate_data
        )
        assert response.status_code == 201
        candidate = response.json()
        candidate_id = candidate["id"]
        
        # Step 5: Apply for the job
        application_data = {
            "cover_letter": "I am very interested in this position and believe my skills align well."
        }
        
        response = await http_client.post(
            f"{service_urls['recruitment']}/jobs/{job_id}/apply/{candidate_id}",
            json=application_data
        )
        assert response.status_code == 201
        application = response.json()
        assert application["match_score"] > 70  # Should be a good match
        
        # Wait for events to propagate
        await asyncio.sleep(2)
        
        # Step 6: Verify job appears in partner profile 360
        response = await http_client.get(
            f"{service_urls['partner_management']}/{partner_id}/profile-360"
        )
        assert response.status_code == 200
        profile = response.json()
        assert profile["recruitment"]["total_jobs"] >= 1
    
    @pytest.mark.asyncio
    async def test_campaign_performance_reporting_integration(self, http_client, service_urls, sample_partner_data):
        """Test campaign performance reporting between services"""
        
        # Step 1: Create partner and campaign (abbreviated)
        response = await http_client.post(
            f"{service_urls['partner_management']}/partners",
            json=sample_partner_data
        )
        partner_id = response.json()["id"]
        
        campaign_data = {
            "partner_id": partner_id,
            "name": "Performance Test Campaign",
            "campaign_type": "DIGITAL_MARKETING",
            "budget": 5000.0
        }
        
        response = await http_client.post(
            f"{service_urls['campaign_management']}/campaigns",
            json=campaign_data
        )
        campaign_id = response.json()["id"]
        
        # Step 2: Simulate campaign performance update
        performance_data = {
            "impressions": 10000,
            "clicks": 250,
            "conversions": 15,
            "cost": 500.0,
            "ctr": 2.5,
            "conversion_rate": 6.0
        }
        
        response = await http_client.put(
            f"{service_urls['campaign_management']}/campaigns/{campaign_id}/performance",
            json=performance_data
        )
        assert response.status_code == 200
        
        # Wait for integration events
        await asyncio.sleep(2)
        
        # Step 3: Check dashboard metrics
        response = await http_client.get(
            f"{service_urls['partner_management']}/{partner_id}/metrics/dashboard"
        )
        assert response.status_code == 200
        metrics = response.json()
        assert metrics["campaigns"]["total_spend"] > 0
    
    @pytest.mark.asyncio
    async def test_complete_partner_lifecycle(self, http_client, service_urls, sample_partner_data):
        """Test complete partner lifecycle across all services"""
        
        # Step 1: Partner Registration
        response = await http_client.post(
            f"{service_urls['partner_management']}/partners",
            json=sample_partner_data
        )
        assert response.status_code == 201
        partner_id = response.json()["id"]
        
        # Step 2: Contract Creation & Activation
        contract_data = {
            "partner_id": partner_id,
            "contract_type": "PREMIUM",
            "terms": {"commission_rate": 0.20}
        }
        
        response = await http_client.post(
            f"{service_urls['onboarding']}/contracts",
            json=contract_data
        )
        contract_id = response.json()["id"]
        
        # Sign and activate contract
        await http_client.post(
            f"{service_urls['onboarding']}/contracts/{contract_id}/sign",
            json={"signer": "Test User", "signature_method": "DIGITAL", "signature_data": "sig123"}
        )
        await http_client.post(
            f"{service_urls['onboarding']}/contracts/{contract_id}/activate"
        )
        
        # Step 3: Campaign Creation
        campaign_data = {
            "partner_id": partner_id,
            "name": "Lifecycle Test Campaign",
            "campaign_type": "DIGITAL_MARKETING",
            "budget": 15000.0
        }
        
        response = await http_client.post(
            f"{service_urls['campaign_management']}/campaigns",
            json=campaign_data
        )
        campaign_id = response.json()["id"]
        
        # Step 4: Job Posting
        job_data = {
            "partner_id": partner_id,
            "title": "Integration Test Position",
            "description": "Test job posting",
            "required_skills": ["Testing", "Integration"]
        }
        
        response = await http_client.post(
            f"{service_urls['recruitment']}/jobs",
            json=job_data
        )
        job_id = response.json()["id"]
        
        # Wait for all events to propagate
        await asyncio.sleep(5)
        
        # Step 5: Verify Complete Profile 360
        response = await http_client.get(
            f"{service_urls['partner_management']}/{partner_id}/profile-360"
        )
        assert response.status_code == 200
        profile = response.json()
        
        # Verify all integrations
        assert profile["contracts"]["total"] >= 1
        assert profile["campaigns"]["total"] >= 1
        assert profile["recruitment"]["total_jobs"] >= 1
        assert profile["engagement_score"] > 0
        
        # Verify partner is validated
        response = await http_client.get(
            f"{service_urls['partner_management']}/{partner_id}/validation-status"
        )
        validation = response.json()
        assert validation["is_validated"] == True
        assert validation["can_create_campaigns"] == True
        assert validation["can_post_jobs"] == True


@pytest.mark.asyncio
async def test_service_resilience_and_fallback():
    """Test service resilience when other services are unavailable"""
    
    async with httpx.AsyncClient(timeout=5.0) as client:
        # Test Partner Management continues to work even if other services are down
        try:
            response = await client.get("http://localhost:5000/health")
            assert response.status_code == 200
        except:
            pytest.skip("Partner Management service not available")
        
        # Test Profile 360 handles service unavailability gracefully
        partner_data = {
            "nombre": "Resilience Test Partner",
            "email": f"resilience-{uuid4()}@test.com",
            "telefono": "+1-555-0100",
            "tipo": "EMPRESA"
        }
        
        response = await client.post("http://localhost:5000/partners", json=partner_data)
        if response.status_code == 201:
            partner_id = response.json()["id"]
            
            # This should work even if other services are down
            response = await client.get(f"http://localhost:5000/{partner_id}/profile-360")
            assert response.status_code == 200
            
            profile = response.json()
            # Should have default values when services are unavailable
            assert "partner" in profile
            assert "summary" in profile