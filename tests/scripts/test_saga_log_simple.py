#!/usr/bin/env python3
"""
Test script simplificado para demostrar el funcionamiento del SagaLog
"""

import sys
import os
import time
import logging
import tempfile
from datetime import datetime, timezone

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

from partner_management.seedwork.infraestructura.saga_log import SagaLog, SagaLogLevel, SagaEventType

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_saga_log_simple():
    """Test simplificado del sistema de logging de Sagas"""
    
    print("🚀 Testing SagaLog System (Simple)")
    print("=" * 50)
    
    # Create temporary directory for logs
    temp_dir = tempfile.mkdtemp()
    log_file_path = os.path.join(temp_dir, "saga_logs.json")
    
    print(f"📁 Using temporary directory: {temp_dir}")
    print()
    
    # Initialize SagaLog with local path
    saga_log = SagaLog(
        log_file_path=log_file_path,
        enable_file_logging=True,
        enable_console_logging=True
    )
    
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
        
        # Simulate processing time
        time.sleep(0.1)
        
        # Complete step
        duration_ms = 100 + (hash(step_name) % 200)  # Random duration between 100-300ms
        saga_log.step_completed(saga_id, partner_id, step_name, correlation_id, service_name, duration_ms)
        
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
        
        # Simulate processing
        time.sleep(0.05)
        
        # Event processed
        saga_log.event_processed(saga_id, partner_id, event_name, correlation_id, service_name, 50)
        
        print(f"   ✅ Event processed")
    
    # 4. Test Saga Completion
    print("\n4️⃣ Testing Saga Completion...")
    saga_log.saga_completed(saga_id, partner_id, correlation_id, service_name)
    print("✅ Saga completed logged")
    
    # 5. Test Error Handling
    print("\n5️⃣ Testing Error Handling...")
    error_saga_id = "error_saga_999"
    error_partner_id = "error_partner_999"
    
    saga_log.saga_started(error_saga_id, error_partner_id, correlation_id, service_name, partner_data)
    
    # Simulate step failure
    saga_log.step_started(error_saga_id, error_partner_id, "failing_step", correlation_id, service_name)
    
    time.sleep(0.1)
    
    # Log step failure
    error = Exception("Simulated error for testing")
    saga_log.step_failed(error_saga_id, error_partner_id, "failing_step", correlation_id, service_name, error, 100)
    
    # Log saga failure
    saga_log.saga_failed(error_saga_id, error_partner_id, correlation_id, service_name, error)
    
    print("✅ Error handling tested")
    
    # 6. Test Log Queries
    print("\n6️⃣ Testing Log Queries...")
    
    # Get saga logs
    saga_logs = saga_log.get_saga_logs(saga_id)
    print(f"   📋 Saga Logs: {len(saga_logs)} entries")
    
    # Get recent logs
    recent_logs = saga_log.get_recent_logs(limit=10)
    print(f"   📋 Recent Logs: {len(recent_logs)} entries")
    
    # Search logs
    error_logs = saga_log.search_logs(level=SagaLogLevel.ERROR)
    print(f"   📋 Error Logs: {len(error_logs)} entries")
    
    # Search by event type
    step_logs = saga_log.search_logs(event_type=SagaEventType.SAGA_STEP_COMPLETED)
    print(f"   📋 Step Completion Logs: {len(step_logs)} entries")
    
    # 7. Test Health Status
    print("\n7️⃣ Testing Health Status...")
    
    health = saga_log.get_health_status()
    print(f"   🏥 SagaLog Health: {health['status']}")
    print(f"   📊 Total Logs: {health['total_logs']}")
    print(f"   🔄 Console Logging: {health['console_logging_enabled']}")
    print(f"   💾 File Logging: {health['file_logging_enabled']}")
    
    # 8. Test Export
    print("\n8️⃣ Testing Export...")
    
    export_file = os.path.join(temp_dir, "exported_logs.json")
    saga_log.export_logs(export_file, saga_id)
    
    if os.path.exists(export_file):
        file_size = os.path.getsize(export_file)
        print(f"   📤 Exported {file_size} bytes to {export_file}")
    
    # 9. Show Sample Log Entries
    print("\n9️⃣ Sample Log Entries...")
    
    sample_logs = saga_log.get_recent_logs(limit=5)
    for i, log in enumerate(sample_logs, 1):
        print(f"   {i}. [{log.timestamp.strftime('%H:%M:%S')}] {log.level.value} - {log.event_type.value}")
        print(f"      Saga: {log.saga_id} | Partner: {log.partner_id}")
        if log.step_name:
            print(f"      Step: {log.step_name}")
        print(f"      Message: {log.message}")
        if log.duration_ms:
            print(f"      Duration: {log.duration_ms:.2f}ms")
        print()
    
    print("=" * 50)
    print("✅ SagaLog System Test Completed Successfully!")
    print(f"📊 Total Logs: {len(saga_log.get_recent_logs(limit=1000))}")
    print(f"📁 Log file: {log_file_path}")
    print(f"📁 Export file: {export_file}")
    print(f"📁 Temp directory: {temp_dir}")

if __name__ == "__main__":
    test_saga_log_simple()
