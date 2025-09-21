#!/usr/bin/env python3
"""
Test script para demostrar el funcionamiento del SagaLog
"""

import sys
import os
import time
import logging
from datetime import datetime, timezone

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

from partner_management.seedwork.infraestructura.saga_log import get_saga_log, SagaLogLevel, SagaEventType
from partner_management.seedwork.infraestructura.saga_audit_trail import get_saga_audit_trail
from partner_management.seedwork.infraestructura.saga_metrics import get_saga_metrics

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_saga_logging():
    """Test completo del sistema de logging de Sagas"""
    
    print("🚀 Testing SagaLog System")
    print("=" * 50)
    
    # Initialize components with local paths
    import tempfile
    import os
    
    # Create temporary directory for logs
    temp_dir = tempfile.mkdtemp()
    log_file_path = os.path.join(temp_dir, "saga_logs.json")
    audit_file_path = os.path.join(temp_dir, "saga_audit.json")
    
    # Initialize with local paths
    from partner_management.seedwork.infraestructura.saga_log import SagaLog
    from partner_management.seedwork.infraestructura.saga_audit_trail import SagaAuditTrail
    from partner_management.seedwork.infraestructura.saga_metrics import SagaMetrics
    
    saga_log = SagaLog(log_file_path=log_file_path, enable_file_logging=True)
    audit_trail = SagaAuditTrail(audit_file_path=audit_file_path, enable_persistence=True)
    saga_metrics = SagaMetrics(enable_real_time_monitoring=False)  # Disable monitoring thread for test
    
    # Test data
    saga_id = "test_saga_123"
    partner_id = "partner_456"
    correlation_id = "corr_789"
    service_name = "partner-management"
    
    print(f"📊 Testing with Saga ID: {saga_id}")
    print(f"👤 Partner ID: {partner_id}")
    print()
    
    # 1. Test Saga Start
    print("1️⃣ Testing Saga Start...")
    partner_data = {
        "nombre": "Test Partner",
        "email": "test@example.com",
        "telefono": "+1234567890"
    }
    
    saga_log.saga_started(saga_id, partner_id, correlation_id, service_name, partner_data)
    audit_trail.record_saga_start(saga_id, partner_id, correlation_id, service_name, partner_data)
    print("✅ Saga started logged")
    
    # 2. Test Step Processing
    print("\n2️⃣ Testing Step Processing...")
    steps = [
        ("partner_registration", "Partner Registration"),
        ("contract_creation", "Contract Creation"),
        ("document_verification", "Document Verification"),
        ("campaign_enablement", "Campaign Enablement"),
        ("recruitment_setup", "Recruitment Setup")
    ]
    
    for step_name, step_description in steps:
        print(f"   📝 Processing step: {step_description}")
        
        # Start step
        saga_log.step_started(saga_id, partner_id, step_name, correlation_id, service_name)
        audit_trail.record_step_start(saga_id, partner_id, step_name, correlation_id, service_name)
        
        # Simulate processing time
        time.sleep(0.1)
        
        # Complete step
        duration_ms = 100 + (hash(step_name) % 200)  # Random duration between 100-300ms
        saga_log.step_completed(saga_id, partner_id, step_name, correlation_id, service_name, duration_ms)
        audit_trail.record_step_success(saga_id, partner_id, step_name, correlation_id, service_name, duration_ms)
        
        print(f"   ✅ Step completed in {duration_ms}ms")
    
    # 3. Test Event Processing
    print("\n3️⃣ Testing Event Processing...")
    events = [
        ("PartnerRegistrationCompleted", {"status": "success"}),
        ("ContractCreated", {"contract_id": "contract_123"}),
        ("DocumentsVerified", {"verification_id": "verify_456"}),
        ("CampaignsEnabled", {"campaign_count": 5}),
        ("RecruitmentSetupCompleted", {"setup_id": "setup_789"})
    ]
    
    for event_name, event_data in events:
        print(f"   📨 Processing event: {event_name}")
        
        # Event received
        saga_log.event_received(saga_id, partner_id, event_name, correlation_id, service_name, event_data)
        audit_trail.record_event_received(saga_id, partner_id, event_name, correlation_id, service_name, event_data)
        
        # Simulate processing
        time.sleep(0.05)
        
        # Event processed
        saga_log.event_processed(saga_id, partner_id, event_name, correlation_id, service_name, 50)
        audit_trail.record_event_processed(saga_id, partner_id, event_name, correlation_id, service_name, 50)
        
        print(f"   ✅ Event processed")
    
    # 4. Test Saga Completion
    print("\n4️⃣ Testing Saga Completion...")
    saga_log.saga_completed(saga_id, partner_id, correlation_id, service_name)
    audit_trail.record_saga_completion(saga_id, partner_id, correlation_id, service_name, "completed")
    print("✅ Saga completed logged")
    
    # 5. Test Error Handling
    print("\n5️⃣ Testing Error Handling...")
    error_saga_id = "error_saga_999"
    error_partner_id = "error_partner_999"
    
    saga_log.saga_started(error_saga_id, error_partner_id, correlation_id, service_name, partner_data)
    audit_trail.record_saga_start(error_saga_id, error_partner_id, correlation_id, service_name, partner_data)
    
    # Simulate step failure
    saga_log.step_started(error_saga_id, error_partner_id, "failing_step", correlation_id, service_name)
    audit_trail.record_step_start(error_saga_id, error_partner_id, "failing_step", correlation_id, service_name)
    
    time.sleep(0.1)
    
    # Log step failure
    error = Exception("Simulated error for testing")
    saga_log.step_failed(error_saga_id, error_partner_id, "failing_step", correlation_id, service_name, error, 100)
    audit_trail.record_step_failure(error_saga_id, error_partner_id, "failing_step", correlation_id, service_name, error, 100)
    
    # Log saga failure
    saga_log.saga_failed(error_saga_id, error_partner_id, correlation_id, service_name, error)
    audit_trail.record_saga_completion(error_saga_id, error_partner_id, correlation_id, service_name, "failed")
    
    print("✅ Error handling tested")
    
    # 6. Test Metrics and Analytics
    print("\n6️⃣ Testing Metrics and Analytics...")
    
    # Calculate performance metrics
    performance = saga_metrics.calculate_saga_performance(saga_id)
    if performance:
        print(f"   📈 Performance Metrics:")
        print(f"      - Total Duration: {performance.total_duration_ms:.2f}ms")
        print(f"      - Average Step Duration: {performance.average_step_duration_ms:.2f}ms")
        print(f"      - Slowest Step: {performance.slowest_step} ({performance.slowest_step_duration_ms:.2f}ms)")
        print(f"      - Fastest Step: {performance.fastest_step} ({performance.fastest_step_duration_ms:.2f}ms)")
        print(f"      - Throughput: {performance.throughput_events_per_second:.2f} events/sec")
    
    # Get system metrics
    system_metrics = saga_metrics.get_system_metrics()
    if system_metrics:
        print(f"   🖥️ System Metrics:")
        print(f"      - Total Sagas: {system_metrics.total_sagas}")
        print(f"      - Active Sagas: {system_metrics.active_sagas}")
        print(f"      - Success Rate: {system_metrics.success_rate_percent:.1f}%")
        print(f"      - Error Rate: {system_metrics.error_rate_percent:.1f}%")
        print(f"      - Events/sec: {system_metrics.events_per_second:.2f}")
    
    # Get trends
    trends = saga_metrics.get_performance_trends(hours=1)
    print(f"   📊 Trends:")
    print(f"      - Duration Trend: {trends.get('duration_trend', 'unknown')}")
    print(f"      - Error Rate Trend: {trends.get('error_rate_trend', 'unknown')}")
    print(f"      - Success Rate Trend: {trends.get('success_rate_trend', 'unknown')}")
    
    # 7. Test Log Queries
    print("\n7️⃣ Testing Log Queries...")
    
    # Get saga logs
    saga_logs = saga_log.get_saga_logs(saga_id)
    print(f"   📋 Saga Logs: {len(saga_logs)} entries")
    
    # Get recent logs
    recent_logs = saga_log.get_recent_logs(limit=10)
    print(f"   📋 Recent Logs: {len(recent_logs)} entries")
    
    # Search logs
    error_logs = saga_log.search_logs(level=SagaLogLevel.ERROR)
    print(f"   📋 Error Logs: {len(error_logs)} entries")
    
    # Get audit records
    audit_records = audit_trail.get_audit_records(saga_id=saga_id)
    print(f"   📋 Audit Records: {len(audit_records)} entries")
    
    # Get saga timeline
    timeline = audit_trail.get_saga_timeline(saga_id)
    if timeline:
        print(f"   📋 Timeline Steps: {len(timeline.steps)}")
        print(f"   📋 Timeline Events: {len(timeline.events)}")
    
    # 8. Test Health Status
    print("\n8️⃣ Testing Health Status...")
    
    log_health = saga_log.get_health_status()
    audit_health = audit_trail.get_health_status()
    metrics_health = saga_metrics.get_health_status()
    
    print(f"   🏥 SagaLog Health: {log_health['status']}")
    print(f"   🏥 AuditTrail Health: {audit_health['status']}")
    print(f"   🏥 Metrics Health: {metrics_health['status']}")
    
    # 9. Test Alerts
    print("\n9️⃣ Testing Alerts...")
    
    active_alerts = saga_metrics.get_active_alerts()
    print(f"   🚨 Active Alerts: {len(active_alerts)}")
    
    for alert in active_alerts:
        print(f"      - {alert.severity}: {alert.message}")
    
    # 10. Test Recommendations
    print("\n🔟 Testing Recommendations...")
    
    recommendations = saga_metrics.get_performance_recommendations(saga_id)
    print(f"   💡 Recommendations: {len(recommendations)}")
    
    for i, rec in enumerate(recommendations, 1):
        print(f"      {i}. {rec}")
    
    print("\n" + "=" * 50)
    print("✅ SagaLog System Test Completed Successfully!")
    print(f"📊 Total Saga Logs: {len(saga_log.get_recent_logs(limit=1000))}")
    print(f"📊 Total Audit Records: {len(audit_trail.get_audit_records())}")
    print(f"📊 Total Performance Metrics: {len(saga_metrics.get_all_performance_metrics())}")

if __name__ == "__main__":
    test_saga_logging()
