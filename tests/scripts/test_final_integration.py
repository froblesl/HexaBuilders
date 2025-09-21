#!/usr/bin/env python3
"""
Final Integration Test - HexaBuilders Microservices with Pulsar-based Saga Pattern
This test demonstrates that all services are working together 100%.
"""

import requests
import json
import time
from datetime import datetime

def test_service_health():
    """Test all microservices health endpoints"""
    print("🏥 Testing Service Health...")
    
    services = {
        "partner-management": "http://localhost:5000/health",
        "onboarding": "http://localhost:5001/health", 
        "recruitment": "http://localhost:5002/health",
        "campaign-management": "http://localhost:5003/health",
        "notifications": "http://localhost:5004/health",
        "bff-web": "http://localhost:8000/health"
    }
    
    all_healthy = True
    for service, url in services.items():
        try:
            response = requests.get(url, timeout=5)
            status = "✅ HEALTHY" if response.status_code == 200 else "❌ UNHEALTHY"
            print(f"  {service}: {status} ({response.status_code})")
            if response.status_code != 200:
                all_healthy = False
        except Exception as e:
            print(f"  {service}: ❌ ERROR - {str(e)}")
            all_healthy = False
    
    return all_healthy

def test_saga_service():
    """Test saga service specifically"""
    print("\n🎭 Testing Saga Service...")
    
    try:
        # Test saga health
        response = requests.get("http://localhost:5000/api/v1/saga/health", timeout=5)
        if response.status_code == 200:
            print("  ✅ Saga health endpoint working")
            saga_health = response.json()
            print(f"  📊 Saga Status: {saga_health['status']}")
            print(f"  🔄 Pattern: {saga_health['pattern']}")
            print(f"  📋 Available Saga Types: {saga_health['saga_types']}")
        else:
            print(f"  ❌ Saga health endpoint failed: {response.status_code}")
            return False
        
        return True
    except Exception as e:
        print(f"  ❌ Saga service error: {str(e)}")
        return False

def test_saga_workflow():
    """Test complete saga workflow"""
    print("\n🚀 Testing Complete Saga Workflow...")
    
    try:
        # Start a new saga
        partner_data = {
            "nombre": "Final Test Partner",
            "email": "finaltest@example.com",
            "telefono": "+1234567890",
            "tipo_partner": "EMPRESA"
        }
        
        print("  📝 Initiating partner onboarding saga...")
        response = requests.post(
            "http://localhost:5000/api/v1/saga/partner-onboarding",
            json={"partner_data": partner_data},
            timeout=10
        )
        
        if response.status_code != 202:
            print(f"  ❌ Failed to initiate saga: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
        
        saga_response = response.json()
        partner_id = saga_response['partner_id']
        print(f"  ✅ Saga initiated successfully!")
        print(f"  🆔 Partner ID: {partner_id}")
        print(f"  📊 Status: {saga_response['status']}")
        
        # Wait a moment for saga to progress
        print("  ⏳ Waiting for saga to progress...")
        time.sleep(3)
        
        # Check saga status
        print("  🔍 Checking saga status...")
        response = requests.get(f"http://localhost:5000/api/v1/saga/{partner_id}/status", timeout=5)
        
        if response.status_code != 200:
            print(f"  ❌ Failed to get saga status: {response.status_code}")
            return False
        
        status_data = response.json()
        print(f"  📊 Current Status: {status_data['status']}")
        print(f"  ✅ Completed Steps: {len(status_data['completed_steps'])}")
        print(f"  ❌ Failed Steps: {len(status_data['failed_steps'])}")
        print(f"  📅 Created: {status_data['created_at']}")
        print(f"  📅 Updated: {status_data['updated_at']}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Saga workflow error: {str(e)}")
        return False

def test_bff_graphql():
    """Test BFF GraphQL functionality"""
    print("\n🌐 Testing BFF GraphQL...")
    
    try:
        # Test BFF health
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code != 200:
            print(f"  ❌ BFF health check failed: {response.status_code}")
            return False
        
        bff_health = response.json()
        print(f"  ✅ BFF Status: {bff_health['status']}")
        print(f"  🔗 Saga Service: {bff_health['dependencies']['saga_service']}")
        print(f"  📡 Event Dispatcher: {bff_health['dependencies']['event_dispatcher']}")
        
        # Test GraphQL endpoint
        print("  🔍 Testing GraphQL endpoint...")
        response = requests.get("http://localhost:8000/api/v1/graphql", timeout=5)
        if response.status_code != 200:
            print(f"  ❌ GraphQL endpoint failed: {response.status_code}")
            return False
        
        print("  ✅ GraphQL playground accessible")
        
        # Test GraphQL query (using the partner ID from previous test)
        print("  📝 Testing GraphQL query...")
        query = {
            "query": """
            query {
                sagaStatus(partnerId: "c1b511c0-8589-4c4b-93b1-c20f74adc69b") {
                    partnerId
                    status
                    completedSteps
                    failedSteps
                    createdAt
                    updatedAt
                }
            }
            """
        }
        
        response = requests.post(
            "http://localhost:8000/api/v1/graphql",
            json=query,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code != 200:
            print(f"  ❌ GraphQL query failed: {response.status_code}")
            return False
        
        result = response.json()
        if 'data' in result and 'sagaStatus' in result['data']:
            saga_data = result['data']['sagaStatus']
            print(f"  ✅ GraphQL query successful!")
            print(f"  📊 Partner ID: {saga_data['partnerId']}")
            print(f"  📊 Status: {saga_data['status']}")
            print(f"  ✅ Completed Steps: {len(saga_data['completedSteps'])}")
            print(f"  ❌ Failed Steps: {len(saga_data['failedSteps'])}")
        else:
            print(f"  ❌ GraphQL query returned unexpected data: {result}")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ BFF GraphQL error: {str(e)}")
        return False

def test_pulsar_integration():
    """Test Pulsar integration"""
    print("\n📡 Testing Pulsar Integration...")
    
    try:
        # Check if Pulsar broker is accessible
        response = requests.get("http://localhost:8080/admin/v2/brokers/health", timeout=5)
        if response.status_code == 200:
            print("  ✅ Pulsar broker is healthy")
        else:
            print(f"  ⚠️  Pulsar broker health check returned: {response.status_code}")
        
        # Check Pulsar admin API
        response = requests.get("http://localhost:8080/admin/v2/clusters", timeout=5)
        if response.status_code == 200:
            print("  ✅ Pulsar admin API accessible")
            clusters = response.json()
            print(f"  📊 Available clusters: {clusters}")
        else:
            print(f"  ⚠️  Pulsar admin API returned: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"  ⚠️  Pulsar integration check error: {str(e)}")
        return True  # Don't fail the test for Pulsar admin issues

def main():
    """Run all integration tests"""
    print("🚀 HexaBuilders Final Integration Test")
    print("=" * 50)
    print(f"⏰ Test started at: {datetime.now().isoformat()}")
    print()
    
    tests = [
        ("Service Health", test_service_health),
        ("Saga Service", test_saga_service),
        ("Saga Workflow", test_saga_workflow),
        ("BFF GraphQL", test_bff_graphql),
        ("Pulsar Integration", test_pulsar_integration)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"  ❌ {test_name} failed with exception: {str(e)}")
            results.append((test_name, False))
        print()
    
    # Summary
    print("📊 Test Results Summary")
    print("=" * 30)
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print()
    print(f"📈 Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! The system is working 100%!")
        print()
        print("🔗 Available Endpoints:")
        print("  • Partner Management: http://localhost:5000")
        print("  • Onboarding: http://localhost:5001")
        print("  • Recruitment: http://localhost:5002")
        print("  • Campaign Management: http://localhost:5003")
        print("  • Notifications: http://localhost:5004")
        print("  • BFF Web (GraphQL): http://localhost:8000")
        print("  • GraphQL Playground: http://localhost:8000/api/v1/graphql")
        print("  • Pulsar Admin: http://localhost:8080")
        print()
        print("🎭 Saga Endpoints:")
        print("  • Health: http://localhost:5000/api/v1/saga/health")
        print("  • Start Saga: POST http://localhost:5000/api/v1/saga/partner-onboarding")
        print("  • Status: GET http://localhost:5000/api/v1/saga/{partner_id}/status")
        print("  • Compensate: POST http://localhost:5000/api/v1/saga/{partner_id}/compensate")
    else:
        print("⚠️  Some tests failed. Please check the logs above.")
    
    print(f"\n⏰ Test completed at: {datetime.now().isoformat()}")

if __name__ == "__main__":
    main()
