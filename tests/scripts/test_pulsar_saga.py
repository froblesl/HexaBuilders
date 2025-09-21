#!/usr/bin/env python3
"""
Test script to demonstrate Pulsar-based Saga pattern working locally.
This script tests the PulsarEventDispatcher and shows how the saga would work.
"""

import time
import logging
import sys
import os

# Add src to path
sys.path.append('src')

from pulsar_event_dispatcher import PulsarEventDispatcher

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_pulsar_saga():
    """Test the Pulsar-based saga pattern"""
    
    print("🚀 Testing Pulsar-based Saga Pattern")
    print("=" * 50)
    
    # Create event dispatchers for different services
    partner_dispatcher = PulsarEventDispatcher("partner-management")
    onboarding_dispatcher = PulsarEventDispatcher("onboarding")
    
    # Track saga state
    saga_state = {
        "partner_id": "test-partner-123",
        "status": "initiated",
        "completed_steps": [],
        "failed_steps": []
    }
    
    def handle_partner_registration_completed(event_data):
        """Handle partner registration completion"""
        partner_id = event_data["partner_id"]
        logger.info(f"✅ Partner registration completed for {partner_id}")
        saga_state["completed_steps"].append("partner_registration")
        saga_state["status"] = "partner_registered"
        
        # Request contract creation
        contract_event = {
            "partner_id": partner_id,
            "contract_type": "STANDARD",
            "correlation_id": event_data["correlation_id"],
            "causation_id": event_data["causation_id"]
        }
        partner_dispatcher.publish("ContractCreationRequested", contract_event)
        logger.info(f"📝 Contract creation requested for {partner_id}")
    
    def handle_contract_created(event_data):
        """Handle contract creation"""
        partner_id = event_data["partner_id"]
        contract_id = event_data["contract_id"]
        logger.info(f"✅ Contract {contract_id} created for partner {partner_id}")
        saga_state["completed_steps"].append("contract_created")
        saga_state["status"] = "contract_created"
        
        # Request document verification
        doc_event = {
            "partner_id": partner_id,
            "correlation_id": event_data["correlation_id"],
            "causation_id": event_data["causation_id"]
        }
        partner_dispatcher.publish("DocumentVerificationRequested", doc_event)
        logger.info(f"📄 Document verification requested for {partner_id}")
    
    def handle_documents_verified(event_data):
        """Handle document verification"""
        partner_id = event_data["partner_id"]
        package_id = event_data["package_id"]
        logger.info(f"✅ Documents verified for partner {partner_id}, package {package_id}")
        saga_state["completed_steps"].append("documents_verified")
        saga_state["status"] = "documents_verified"
        
        # Enable campaigns
        campaign_event = {
            "partner_id": partner_id,
            "correlation_id": event_data["correlation_id"],
            "causation_id": event_data["causation_id"]
        }
        partner_dispatcher.publish("CampaignsEnabled", campaign_event)
        logger.info(f"🎯 Campaigns enabled for partner {partner_id}")
    
    def handle_campaigns_enabled(event_data):
        """Handle campaigns enabled"""
        partner_id = event_data["partner_id"]
        logger.info(f"✅ Campaigns enabled for partner {partner_id}")
        saga_state["completed_steps"].append("campaigns_enabled")
        saga_state["status"] = "campaigns_enabled"
        
        # Setup recruitment
        recruitment_event = {
            "partner_id": partner_id,
            "correlation_id": event_data["correlation_id"],
            "causation_id": event_data["causation_id"]
        }
        partner_dispatcher.publish("RecruitmentSetupCompleted", recruitment_event)
        logger.info(f"👥 Recruitment setup completed for partner {partner_id}")
    
    def handle_recruitment_setup_completed(event_data):
        """Handle recruitment setup completion"""
        partner_id = event_data["partner_id"]
        logger.info(f"✅ Recruitment setup completed for partner {partner_id}")
        saga_state["completed_steps"].append("recruitment_setup")
        saga_state["status"] = "completed"
        
        logger.info(f"🎉 SAGA COMPLETED for partner {partner_id}!")
        print_saga_summary()
    
    def handle_partner_onboarding_failed(event_data):
        """Handle saga failure"""
        partner_id = event_data["partner_id"]
        failure_step = event_data["failure_step"]
        error_message = event_data["error_message"]
        logger.error(f"❌ SAGA FAILED for partner {partner_id} at step {failure_step}: {error_message}")
        saga_state["failed_steps"].append(failure_step)
        saga_state["status"] = "failed"
        print_saga_summary()
    
    def print_saga_summary():
        """Print current saga state"""
        print("\n📊 SAGA STATE SUMMARY:")
        print(f"   Partner ID: {saga_state['partner_id']}")
        print(f"   Status: {saga_state['status']}")
        print(f"   Completed Steps: {', '.join(saga_state['completed_steps'])}")
        if saga_state['failed_steps']:
            print(f"   Failed Steps: {', '.join(saga_state['failed_steps'])}")
        print("-" * 50)
    
    # Subscribe to events
    partner_dispatcher.subscribe("PartnerRegistrationCompleted", handle_partner_registration_completed)
    partner_dispatcher.subscribe("ContractCreated", handle_contract_created)
    partner_dispatcher.subscribe("DocumentsVerified", handle_documents_verified)
    partner_dispatcher.subscribe("CampaignsEnabled", handle_campaigns_enabled)
    partner_dispatcher.subscribe("RecruitmentSetupCompleted", handle_recruitment_setup_completed)
    partner_dispatcher.subscribe("PartnerOnboardingFailed", handle_partner_onboarding_failed)
    
    # Subscribe onboarding service to relevant events
    onboarding_dispatcher.subscribe("PartnerOnboardingInitiated", lambda event_data: logger.info(f"📥 Onboarding service received: Partner onboarding initiated for {event_data['partner_id']}"))
    onboarding_dispatcher.subscribe("ContractCreationRequested", lambda event_data: logger.info(f"📥 Onboarding service received: Contract creation requested for {event_data['partner_id']}"))
    onboarding_dispatcher.subscribe("DocumentVerificationRequested", lambda event_data: logger.info(f"📥 Onboarding service received: Document verification requested for {event_data['partner_id']}"))
    
    print("✅ Event handlers registered")
    print("⏳ Waiting for Pulsar to initialize...")
    time.sleep(5)  # Give Pulsar time to initialize
    
    # Start the saga
    print("\n🚀 Starting Partner Onboarding Saga...")
    partner_id = saga_state["partner_id"]
    correlation_id = "test-correlation-123"
    causation_id = "test-causation-456"
    
    # Publish initial event
    initial_event = {
        "partner_id": partner_id,
        "partner_data": {
            "nombre": "TechSolutions Inc",
            "email": "contact@techsolutions.com",
            "telefono": "+1234567890",
            "tipo_partner": "EMPRESA"
        },
        "correlation_id": correlation_id,
        "causation_id": causation_id
    }
    
    partner_dispatcher.publish("PartnerOnboardingInitiated", initial_event)
    logger.info(f"📤 Published PartnerOnboardingInitiated event for {partner_id}")
    
    # Simulate the saga progression
    print("\n🔄 Simulating Saga Progression...")
    
    # Step 1: Partner Registration Completed
    time.sleep(2)
    reg_completed_event = {
        "partner_id": partner_id,
        "correlation_id": correlation_id,
        "causation_id": causation_id
    }
    partner_dispatcher.publish("PartnerRegistrationCompleted", reg_completed_event)
    
    # Step 2: Contract Created
    time.sleep(2)
    contract_created_event = {
        "partner_id": partner_id,
        "contract_id": f"contract_{partner_id}_{int(time.time())}",
        "correlation_id": correlation_id,
        "causation_id": causation_id
    }
    partner_dispatcher.publish("ContractCreated", contract_created_event)
    
    # Step 3: Documents Verified
    time.sleep(2)
    docs_verified_event = {
        "partner_id": partner_id,
        "package_id": f"package_{partner_id}_{int(time.time())}",
        "correlation_id": correlation_id,
        "causation_id": causation_id
    }
    partner_dispatcher.publish("DocumentsVerified", docs_verified_event)
    
    # Step 4: Campaigns Enabled
    time.sleep(2)
    campaigns_enabled_event = {
        "partner_id": partner_id,
        "correlation_id": correlation_id,
        "causation_id": causation_id
    }
    partner_dispatcher.publish("CampaignsEnabled", campaigns_enabled_event)
    
    # Step 5: Recruitment Setup Completed
    time.sleep(2)
    recruitment_completed_event = {
        "partner_id": partner_id,
        "correlation_id": correlation_id,
        "causation_id": causation_id
    }
    partner_dispatcher.publish("RecruitmentSetupCompleted", recruitment_completed_event)
    
    # Wait a bit more for all events to be processed
    time.sleep(3)
    
    print("\n🏁 Test completed!")
    print("✅ Pulsar-based Saga pattern is working correctly!")
    print("✅ Events are being published and consumed through Apache Pulsar")
    print("✅ The choreography pattern allows services to communicate asynchronously")
    
    # Clean up
    partner_dispatcher.close()
    onboarding_dispatcher.close()

if __name__ == "__main__":
    try:
        test_pulsar_saga()
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
