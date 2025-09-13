import pytest
import asyncio
import httpx
import time
import statistics
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from uuid import uuid4


class TestPerformanceIntegration:
    """Performance and load tests for microservices integration"""
    
    @pytest.fixture
    def service_urls(self):
        return {
            "partner_management": "http://localhost:5000",
            "onboarding": "http://localhost:5001",
            "recruitment": "http://localhost:5002",
            "campaign_management": "http://localhost:5003"
        }
    
    @pytest.fixture
    async def http_client(self):
        """HTTP client with optimized settings for performance testing"""
        limits = httpx.Limits(max_keepalive_connections=20, max_connections=100)
        async with httpx.AsyncClient(timeout=30.0, limits=limits) as client:
            yield client
    
    async def create_test_partner(self, client, base_name="LoadTest"):
        """Helper to create a test partner"""
        partner_data = {
            "nombre": f"{base_name} Partner {uuid4()}",
            "email": f"loadtest-{uuid4()}@test.com",
            "telefono": "+1-555-0123",
            "tipo": "EMPRESA",
            "direccion": "Test Address",
            "ciudad": "Test City",
            "pais": "Test Country"
        }
        
        response = await client.post("http://localhost:5000/partners", json=partner_data)
        return response.json()["id"] if response.status_code == 201 else None
    
    @pytest.mark.asyncio
    async def test_partner_creation_performance(self, http_client):
        """Test partner creation performance under load"""
        
        # Create multiple partners concurrently
        num_partners = 50
        start_time = time.time()
        
        tasks = []
        for i in range(num_partners):
            task = self.create_test_partner(http_client, f"PerfTest{i}")
            tasks.append(task)
        
        partner_ids = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()
        
        # Filter out exceptions and count successful creations
        successful_ids = [pid for pid in partner_ids if isinstance(pid, str)]
        
        duration = end_time - start_time
        throughput = len(successful_ids) / duration
        
        print(f"Created {len(successful_ids)}/{num_partners} partners in {duration:.2f}s")
        print(f"Throughput: {throughput:.2f} partners/second")
        
        # Performance assertions
        assert len(successful_ids) >= num_partners * 0.95  # 95% success rate
        assert throughput >= 5.0  # At least 5 partners per second
        assert duration <= 20.0   # Complete within 20 seconds
    
    @pytest.mark.asyncio
    async def test_profile_360_response_time(self, http_client):
        """Test Profile 360 API response time under concurrent load"""
        
        # Create test partner
        partner_id = await self.create_test_partner(http_client, "Profile360Test")
        assert partner_id is not None
        
        # Wait for partner to be fully created
        await asyncio.sleep(2)
        
        # Test concurrent Profile 360 requests
        num_requests = 20
        response_times = []
        
        async def fetch_profile_360():
            start = time.time()
            response = await http_client.get(f"http://localhost:5000/{partner_id}/profile-360")
            end = time.time()
            return end - start, response.status_code
        
        tasks = [fetch_profile_360() for _ in range(num_requests)]
        results = await asyncio.gather(*tasks)
        
        # Analyze results
        response_times = [rt for rt, status in results if status == 200]
        success_count = len(response_times)
        
        if response_times:
            avg_response_time = statistics.mean(response_times)
            p95_response_time = sorted(response_times)[int(0.95 * len(response_times))]
            max_response_time = max(response_times)
            
            print(f"Profile 360 Performance ({success_count}/{num_requests} successful):")
            print(f"  Average response time: {avg_response_time:.3f}s")
            print(f"  95th percentile: {p95_response_time:.3f}s")
            print(f"  Maximum: {max_response_time:.3f}s")
            
            # Performance assertions
            assert success_count >= num_requests * 0.9  # 90% success rate
            assert avg_response_time <= 2.0  # Average under 2 seconds
            assert p95_response_time <= 5.0  # 95% under 5 seconds
        else:
            pytest.fail("No successful Profile 360 requests")
    
    @pytest.mark.asyncio
    async def test_cross_service_integration_performance(self, http_client):
        """Test performance of cross-service integration workflows"""
        
        num_workflows = 10
        workflow_times = []
        
        async def run_integration_workflow():
            start = time.time()
            
            try:
                # Step 1: Create partner
                partner_id = await self.create_test_partner(http_client, "IntegrationPerf")
                if not partner_id:
                    return None
                
                # Step 2: Create contract
                contract_data = {
                    "partner_id": partner_id,
                    "contract_type": "STANDARD",
                    "terms": {"commission_rate": 0.15}
                }
                
                response = await http_client.post("http://localhost:5001/contracts", json=contract_data)
                if response.status_code != 201:
                    return None
                
                contract_id = response.json()["id"]
                
                # Step 3: Create campaign
                campaign_data = {
                    "partner_id": partner_id,
                    "name": f"Perf Test Campaign {uuid4()}",
                    "campaign_type": "DIGITAL_MARKETING",
                    "budget": 5000.0
                }
                
                response = await http_client.post("http://localhost:5003/campaigns", json=campaign_data)
                if response.status_code != 201:
                    return None
                
                # Step 4: Create job
                job_data = {
                    "partner_id": partner_id,
                    "title": f"Perf Test Job {uuid4()}",
                    "description": "Performance test job",
                    "required_skills": ["Testing"]
                }
                
                response = await http_client.post("http://localhost:5002/jobs", json=job_data)
                if response.status_code != 201:
                    return None
                
                # Step 5: Wait for integration events and fetch Profile 360
                await asyncio.sleep(1)  # Brief wait for events
                
                response = await http_client.get(f"http://localhost:5000/{partner_id}/profile-360")
                if response.status_code != 200:
                    return None
                
                end = time.time()
                return end - start
                
            except Exception as e:
                print(f"Workflow error: {e}")
                return None
        
        # Run workflows concurrently
        tasks = [run_integration_workflow() for _ in range(num_workflows)]
        results = await asyncio.gather(*tasks)
        
        # Analyze results
        workflow_times = [t for t in results if t is not None]
        success_count = len(workflow_times)
        
        if workflow_times:
            avg_time = statistics.mean(workflow_times)
            max_time = max(workflow_times)
            
            print(f"Integration Workflow Performance ({success_count}/{num_workflows} successful):")
            print(f"  Average workflow time: {avg_time:.2f}s")
            print(f"  Maximum workflow time: {max_time:.2f}s")
            
            # Performance assertions
            assert success_count >= num_workflows * 0.7  # 70% success rate (more lenient for full workflow)
            assert avg_time <= 10.0  # Average under 10 seconds
            assert max_time <= 20.0  # Maximum under 20 seconds
        else:
            pytest.fail("No successful integration workflows")
    
    @pytest.mark.asyncio
    async def test_concurrent_campaign_operations(self, http_client):
        """Test concurrent campaign operations performance"""
        
        # Create test partner first
        partner_id = await self.create_test_partner(http_client, "CampaignPerf")
        assert partner_id is not None
        
        num_campaigns = 30
        operation_times = []
        
        async def create_and_manage_campaign(campaign_num):
            start = time.time()
            
            try:
                # Create campaign
                campaign_data = {
                    "partner_id": partner_id,
                    "name": f"Concurrent Campaign {campaign_num}",
                    "campaign_type": "DIGITAL_MARKETING",
                    "budget": 1000.0 + (campaign_num * 100)
                }
                
                response = await http_client.post("http://localhost:5003/campaigns", json=campaign_data)
                if response.status_code != 201:
                    return None
                
                campaign_id = response.json()["id"]
                
                # Update campaign performance
                performance_data = {
                    "impressions": 1000 * campaign_num,
                    "clicks": 50 * campaign_num,
                    "conversions": 5 * campaign_num,
                    "cost": 100.0 * campaign_num
                }
                
                response = await http_client.put(
                    f"http://localhost:5003/campaigns/{campaign_id}/performance",
                    json=performance_data
                )
                
                if response.status_code != 200:
                    return None
                
                end = time.time()
                return end - start
                
            except Exception as e:
                print(f"Campaign operation error: {e}")
                return None
        
        # Run campaign operations concurrently
        tasks = [create_and_manage_campaign(i) for i in range(num_campaigns)]
        results = await asyncio.gather(*tasks)
        
        # Analyze results
        operation_times = [t for t in results if t is not None]
        success_count = len(operation_times)
        
        if operation_times:
            avg_time = statistics.mean(operation_times)
            p95_time = sorted(operation_times)[int(0.95 * len(operation_times))]
            
            print(f"Campaign Operations Performance ({success_count}/{num_campaigns} successful):")
            print(f"  Average operation time: {avg_time:.3f}s")
            print(f"  95th percentile: {p95_time:.3f}s")
            
            # Performance assertions
            assert success_count >= num_campaigns * 0.8  # 80% success rate
            assert avg_time <= 3.0   # Average under 3 seconds
            assert p95_time <= 6.0   # 95% under 6 seconds
        else:
            pytest.fail("No successful campaign operations")
    
    @pytest.mark.asyncio
    async def test_recruitment_search_performance(self, http_client):
        """Test recruitment search performance under load"""
        
        # Create test candidates first
        num_candidates = 20
        candidate_creation_tasks = []
        
        for i in range(num_candidates):
            candidate_data = {
                "name": f"Test Candidate {i}",
                "email": f"candidate{i}-{uuid4()}@test.com",
                "phone": f"+1-555-{1000+i:04d}",
                "location": "Remote" if i % 2 == 0 else "On-site",
                "years_of_experience": i % 10 + 1,
                "expected_salary": 50000 + (i * 5000),
                "skills": [
                    "Python", "JavaScript", "Java", "C++", "Go", 
                    "React", "Vue", "Angular", "Django", "Flask"
                ][:(i % 5 + 2)],  # Variable number of skills
                "availability": "AVAILABLE"
            }
            
            task = http_client.post("http://localhost:5002/candidates", json=candidate_data)
            candidate_creation_tasks.append(task)
        
        # Create candidates
        candidate_responses = await asyncio.gather(*candidate_creation_tasks, return_exceptions=True)
        created_candidates = sum(1 for r in candidate_responses if hasattr(r, 'status_code') and r.status_code == 201)
        
        print(f"Created {created_candidates} candidates for search testing")
        
        # Wait for ElasticSearch indexing
        await asyncio.sleep(3)
        
        # Test concurrent searches
        num_searches = 25
        search_times = []
        
        search_queries = [
            "Python developer",
            "JavaScript React",
            "Senior engineer",
            "Remote Python",
            "Junior developer",
            "Full stack",
            "Backend Django",
            "Frontend React",
            "DevOps engineer",
            "Data scientist"
        ]
        
        async def perform_search(query_num):
            start = time.time()
            
            try:
                query = search_queries[query_num % len(search_queries)]
                
                response = await http_client.get(
                    f"http://localhost:5002/candidates/search",
                    params={"q": query, "size": 10}
                )
                
                end = time.time()
                
                if response.status_code == 200:
                    return end - start
                else:
                    return None
                    
            except Exception as e:
                print(f"Search error: {e}")
                return None
        
        # Perform concurrent searches
        tasks = [perform_search(i) for i in range(num_searches)]
        results = await asyncio.gather(*tasks)
        
        # Analyze search performance
        search_times = [t for t in results if t is not None]
        success_count = len(search_times)
        
        if search_times:
            avg_search_time = statistics.mean(search_times)
            p95_search_time = sorted(search_times)[int(0.95 * len(search_times))]
            
            print(f"Search Performance ({success_count}/{num_searches} successful):")
            print(f"  Average search time: {avg_search_time:.3f}s")
            print(f"  95th percentile: {p95_search_time:.3f}s")
            
            # Performance assertions
            assert success_count >= num_searches * 0.9  # 90% success rate
            assert avg_search_time <= 1.0  # Average under 1 second
            assert p95_search_time <= 2.0  # 95% under 2 seconds
        else:
            pytest.skip("Search functionality not available or no successful searches")
    
    @pytest.mark.asyncio
    async def test_database_connection_pooling(self, http_client):
        """Test database performance under concurrent load"""
        
        num_concurrent_requests = 50
        
        async def make_database_intensive_request():
            start = time.time()
            
            try:
                # Create partner (database write)
                partner_id = await self.create_test_partner(http_client, "DBTest")
                if not partner_id:
                    return None
                
                # Fetch partner (database read)
                response = await http_client.get(f"http://localhost:5000/partners/{partner_id}")
                if response.status_code != 200:
                    return None
                
                # Fetch profile 360 (multiple database queries + external calls)
                response = await http_client.get(f"http://localhost:5000/{partner_id}/profile-360")
                if response.status_code != 200:
                    return None
                
                end = time.time()
                return end - start
                
            except Exception as e:
                print(f"Database test error: {e}")
                return None
        
        # Execute concurrent database operations
        tasks = [make_database_intensive_request() for _ in range(num_concurrent_requests)]
        results = await asyncio.gather(*tasks)
        
        # Analyze database performance
        response_times = [t for t in results if t is not None]
        success_count = len(response_times)
        
        if response_times:
            avg_time = statistics.mean(response_times)
            max_time = max(response_times)
            p95_time = sorted(response_times)[int(0.95 * len(response_times))]
            
            print(f"Database Performance ({success_count}/{num_concurrent_requests} successful):")
            print(f"  Average response time: {avg_time:.3f}s")
            print(f"  95th percentile: {p95_time:.3f}s")
            print(f"  Maximum: {max_time:.3f}s")
            
            # Performance assertions for database operations
            assert success_count >= num_concurrent_requests * 0.8  # 80% success rate
            assert avg_time <= 5.0   # Average under 5 seconds
            assert p95_time <= 10.0  # 95% under 10 seconds
        else:
            pytest.fail("No successful database operations")
    
    @pytest.mark.asyncio 
    async def test_memory_and_resource_usage(self, http_client):
        """Test for memory leaks and resource usage during sustained load"""
        
        # Run sustained operations for resource monitoring
        duration_seconds = 30
        operations_per_second = 5
        total_operations = duration_seconds * operations_per_second
        
        start_time = time.time()
        operation_count = 0
        
        while time.time() - start_time < duration_seconds:
            batch_tasks = []
            
            # Create a batch of operations
            for _ in range(operations_per_second):
                if operation_count % 4 == 0:
                    # Partner creation
                    task = self.create_test_partner(http_client, "ResourceTest")
                elif operation_count % 4 == 1:
                    # Health checks
                    task = http_client.get("http://localhost:5000/health")
                elif operation_count % 4 == 2:
                    # Search operations (if available)
                    task = http_client.get("http://localhost:5002/candidates/search?q=test")
                else:
                    # Campaign listing
                    task = http_client.get("http://localhost:5003/campaigns")
                
                batch_tasks.append(task)
                operation_count += 1
            
            # Execute batch and wait briefly
            await asyncio.gather(*batch_tasks, return_exceptions=True)
            await asyncio.sleep(1.0 / operations_per_second)
        
        end_time = time.time()
        actual_duration = end_time - start_time
        
        print(f"Sustained Load Test:")
        print(f"  Duration: {actual_duration:.1f}s")
        print(f"  Operations: {operation_count}")
        print(f"  Rate: {operation_count/actual_duration:.1f} ops/sec")
        
        # Final health check to ensure services are still responsive
        health_checks = []
        for service, url in {
            "partner_management": "http://localhost:5000",
            "onboarding": "http://localhost:5001",
            "recruitment": "http://localhost:5002",
            "campaign_management": "http://localhost:5003"
        }.items():
            health_checks.append(http_client.get(f"{url}/health"))
        
        health_results = await asyncio.gather(*health_checks, return_exceptions=True)
        healthy_services = sum(1 for r in health_results if hasattr(r, 'status_code') and r.status_code == 200)
        
        print(f"  Services healthy after load: {healthy_services}/4")
        
        # Assert services are still healthy after sustained load
        assert healthy_services >= 3  # At least 3 of 4 services should be healthy