"""
Implementación de Saga basada en Choreography usando Apache Pulsar.
Cada servicio maneja su propio estado y publica eventos para coordinar.
"""

import logging
import threading
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4


class ChoreographySagaStatus(Enum):
    """Estados de una Saga de Choreography"""
    INITIATED = "initiated"
    PARTNER_REGISTERED = "partner_registered"
    CONTRACT_CREATED = "contract_created"
    DOCUMENTS_VERIFIED = "documents_verified"
    CAMPAIGNS_ENABLED = "campaigns_enabled"
    RECRUITMENT_SETUP = "recruitment_setup"
    COMPLETED = "completed"
    FAILED = "failed"
    COMPENSATING = "compensating"
    COMPENSATED = "compensated"


class SagaStateRepository:
    """Repositorio para el estado de la Saga"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self._memory_storage = {}
    
    def save(self, partner_id: str, saga_state: Dict[str, Any]):
        """Guarda el estado de la Saga"""
        self._memory_storage[partner_id] = saga_state
        self.logger.debug(f"Saga state saved for partner {partner_id}")
    
    def get(self, partner_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene el estado de la Saga"""
        return self._memory_storage.get(partner_id)
    
    def delete(self, partner_id: str):
        """Elimina el estado de la Saga"""
        if partner_id in self._memory_storage:
            del self._memory_storage[partner_id]
        self.logger.debug(f"Saga state deleted for partner {partner_id}")


# Importar el dispatcher de Pulsar y SagaLog
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../../..'))
from src.pulsar_event_dispatcher import PulsarEventDispatcher
from src.partner_management.seedwork.infraestructura.saga_log import get_saga_log, SagaLogLevel, SagaEventType
from src.partner_management.seedwork.infraestructura.saga_audit_trail import get_saga_audit_trail
from src.partner_management.seedwork.infraestructura.saga_metrics import get_saga_metrics


class ChoreographySagaOrchestrator:
    """
    Orquestador de Saga basado en Choreography usando Apache Pulsar.
    """
    
    def __init__(self, saga_state_repository: SagaStateRepository, event_dispatcher: PulsarEventDispatcher, timeout_seconds: int = 30):
        self.saga_state_repository = saga_state_repository
        self.event_dispatcher = event_dispatcher
        self.logger = logging.getLogger(self.__class__.__name__)
        self.timeout_seconds = timeout_seconds
        
        # Track processed events to prevent duplicates
        self._processed_events = set()
        
        # Track saga timeouts
        self._saga_timeouts = {}  # saga_id -> timeout_timer
        
        # Initialize logging and monitoring components
        self.saga_log = get_saga_log()
        self.audit_trail = get_saga_audit_trail()
        self.saga_metrics = get_saga_metrics()
        
        # Suscribirse a eventos
        self._subscribe_to_events()
    
    def _subscribe_to_events(self):
        """Suscribirse a eventos de la Saga"""
        # Eventos normales
        self.event_dispatcher.subscribe("PartnerRegistrationCompleted", self._handle_partner_registered)
        self.event_dispatcher.subscribe("ContractCreated", self._handle_contract_created)
        self.event_dispatcher.subscribe("DocumentsVerified", self._handle_documents_verified)
        self.event_dispatcher.subscribe("CampaignsEnabledConfirmed", self._handle_campaigns_enabled)
        self.event_dispatcher.subscribe("RecruitmentSetupConfirmed", self._handle_recruitment_setup)
        
        # Eventos de compensación
        self.event_dispatcher.subscribe("RecruitmentSetupCompensated", self._handle_recruitment_compensated)
        self.event_dispatcher.subscribe("CampaignsDisabled", self._handle_campaigns_compensated)
        self.event_dispatcher.subscribe("DocumentVerificationReverted", self._handle_documents_compensated)
        self.event_dispatcher.subscribe("ContractCancelled", self._handle_contract_compensated)
        self.event_dispatcher.subscribe("PartnerRegistrationReverted", self._handle_partner_compensated)
    
    def start_partner_onboarding(self, partner_data: Dict[str, Any], correlation_id: str) -> str:
        """Inicia el proceso de onboarding de un partner"""
        partner_id = partner_data.get('partner_id', str(uuid4()))
        causation_id = str(uuid4())
        saga_id = f"saga_{partner_id}_{int(datetime.now(timezone.utc).timestamp())}"
        
        # Crear estado inicial de la Saga
        saga_state = {
            "saga_id": saga_id,
            "partner_id": partner_id,
            "saga_type": "partner_onboarding",
            "status": ChoreographySagaStatus.INITIATED,
            "completed_steps": [],
            "failed_steps": [],
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "correlation_id": correlation_id,
            "causation_id": causation_id
        }
        
        self.saga_state_repository.save(partner_id, saga_state)
        
        # Log saga start
        self.saga_log.saga_started(saga_id, partner_id, correlation_id, "partner-management", partner_data)
        self.audit_trail.record_saga_start(saga_id, partner_id, correlation_id, "partner-management", partner_data)
        self.saga_metrics.record_saga_start(saga_id, partner_id, correlation_id)
        
        # Publicar evento de inicio
        self.event_dispatcher.publish("PartnerOnboardingInitiated", {
            "saga_id": saga_id,
            "partner_id": partner_id,
            "partner_data": partner_data,
            "correlation_id": correlation_id,
            "causation_id": causation_id
        })
        
        # Log event published
        self.saga_log.event_published(saga_id, partner_id, "PartnerOnboardingInitiated", correlation_id, "partner-management", partner_data)
        self.audit_trail.record_event_published(saga_id, partner_id, "PartnerOnboardingInitiated", correlation_id, "partner-management", partner_data)
        
        # Set timeout for saga completion
        self._set_saga_timeout(saga_id, partner_id, correlation_id)
        
        return partner_id
    
    def _handle_partner_registered(self, event_data: Dict[str, Any]):
        """Maneja el evento de partner registrado"""
        partner_id = event_data["partner_id"]
        saga_id = event_data.get("saga_id")
        if not saga_id:
            # Try to get saga_id from saga state
            saga_state = self.saga_state_repository.get(partner_id)
            saga_id = saga_state.get("saga_id") if saga_state else f"saga_{partner_id}"
        event_id = f"partner_registered_{partner_id}_{event_data.get('causation_id', '')}"
        
        # Check if we've already processed this event
        if event_id in self._processed_events:
            self.logger.info(f"Event already processed, skipping: {event_id}")
            return
            
        self._processed_events.add(event_id)
        self.logger.info(f"Partner registered: {partner_id}")
        
        # Log event received and step started
        self.saga_log.event_received(saga_id, partner_id, "PartnerRegistrationCompleted", event_data["correlation_id"], "partner-management", event_data)
        self.saga_log.step_started(saga_id, partner_id, "partner_registration", event_data["correlation_id"], "partner-management")
        self.audit_trail.record_event_received(saga_id, partner_id, "PartnerRegistrationCompleted", event_data["correlation_id"], "partner-management", event_data)
        self.audit_trail.record_step_start(saga_id, partner_id, "partner_registration", event_data["correlation_id"], "partner-management")
        
        # Actualizar estado
        self._update_saga_state(partner_id, ChoreographySagaStatus.PARTNER_REGISTERED, ["partner_registration"])
        
        # Log step completed
        self.saga_log.step_completed(saga_id, partner_id, "partner_registration", event_data["correlation_id"], "partner-management")
        self.audit_trail.record_step_success(saga_id, partner_id, "partner_registration", event_data["correlation_id"], "partner-management")
        self.saga_metrics.record_saga_step(saga_id, "partner_registration", 0, True)  # Duration would need to be calculated
        self.saga_metrics.record_saga_event(saga_id)
        
        # Solicitar creación de contrato
        contract_event = {
            "partner_id": partner_id,
            "contract_data": {"tipo_contrato": "BASIC"},
            "correlation_id": event_data["correlation_id"],
            "causation_id": event_data["causation_id"]
        }
        self.event_dispatcher.publish("ContractCreationRequested", contract_event)
        
        # Log event published
        self.saga_log.event_published(saga_id, partner_id, "ContractCreationRequested", event_data["correlation_id"], "partner-management", contract_event)
        self.audit_trail.record_event_published(saga_id, partner_id, "ContractCreationRequested", event_data["correlation_id"], "partner-management", contract_event)
    
    def _handle_contract_created(self, event_data: Dict[str, Any]):
        """Maneja el evento de contrato creado"""
        partner_id = event_data["partner_id"]
        saga_id = event_data.get("saga_id")
        if not saga_id:
            # Try to get saga_id from saga state
            saga_state = self.saga_state_repository.get(partner_id)
            saga_id = saga_state.get("saga_id") if saga_state else f"saga_{partner_id}"
        event_id = f"contract_created_{partner_id}_{event_data.get('causation_id', '')}"
        
        # Check if we've already processed this event
        if event_id in self._processed_events:
            self.logger.info(f"Event already processed, skipping: {event_id}")
            return
            
        self._processed_events.add(event_id)
        self.logger.info(f"Contract created for partner: {partner_id}")
        
        # Log event received and step started
        self.saga_log.event_received(saga_id, partner_id, "ContractCreated", event_data["correlation_id"], "partner-management", event_data)
        self.saga_log.step_started(saga_id, partner_id, "contract_creation", event_data["correlation_id"], "partner-management")
        self.audit_trail.record_event_received(saga_id, partner_id, "ContractCreated", event_data["correlation_id"], "partner-management", event_data)
        self.audit_trail.record_step_start(saga_id, partner_id, "contract_creation", event_data["correlation_id"], "partner-management")
        
        # Actualizar estado
        self._update_saga_state(partner_id, ChoreographySagaStatus.CONTRACT_CREATED, ["contract_creation"])
        
        # Log step completed
        self.saga_log.step_completed(saga_id, partner_id, "contract_creation", event_data["correlation_id"], "partner-management")
        self.audit_trail.record_step_success(saga_id, partner_id, "contract_creation", event_data["correlation_id"], "partner-management")
        self.saga_metrics.record_saga_step(saga_id, "contract_creation", 0, True)
        self.saga_metrics.record_saga_event(saga_id)
        
        # Solicitar verificación de documentos
        self.event_dispatcher.publish("DocumentVerificationRequested", {
            "partner_id": partner_id,
            "document_types": ["IDENTITY", "BUSINESS_REGISTRATION"],
            "correlation_id": event_data["correlation_id"],
            "causation_id": event_data["causation_id"]
        })
        
        # Log event published
        self.saga_log.event_published(saga_id, partner_id, "DocumentVerificationRequested", event_data["correlation_id"], "partner-management", {
            "partner_id": partner_id,
            "document_types": ["IDENTITY", "BUSINESS_REGISTRATION"],
            "correlation_id": event_data["correlation_id"],
            "causation_id": event_data["causation_id"]
        })
        self.audit_trail.record_event_published(saga_id, partner_id, "DocumentVerificationRequested", event_data["correlation_id"], "partner-management", {
            "partner_id": partner_id,
            "document_types": ["IDENTITY", "BUSINESS_REGISTRATION"],
            "correlation_id": event_data["correlation_id"],
            "causation_id": event_data["causation_id"]
        })
    
    def _handle_documents_verified(self, event_data: Dict[str, Any]):
        """Maneja el evento de documentos verificados"""
        partner_id = event_data["partner_id"]
        saga_id = event_data.get("saga_id")
        if not saga_id:
            # Try to get saga_id from saga state
            saga_state = self.saga_state_repository.get(partner_id)
            saga_id = saga_state.get("saga_id") if saga_state else f"saga_{partner_id}"
        event_id = f"documents_verified_{partner_id}_{event_data.get('causation_id', '')}"
        
        # Check if we've already processed this event
        if event_id in self._processed_events:
            self.logger.info(f"Event already processed, skipping: {event_id}")
            return
            
        self._processed_events.add(event_id)
        self.logger.info(f"Documents verified for partner: {partner_id}")
        
        # Log event received and step started
        self.saga_log.event_received(saga_id, partner_id, "DocumentsVerified", event_data["correlation_id"], "partner-management", event_data)
        self.saga_log.step_started(saga_id, partner_id, "document_verification", event_data["correlation_id"], "partner-management")
        self.audit_trail.record_event_received(saga_id, partner_id, "DocumentsVerified", event_data["correlation_id"], "partner-management", event_data)
        self.audit_trail.record_step_start(saga_id, partner_id, "document_verification", event_data["correlation_id"], "partner-management")
        
        # Actualizar estado
        self._update_saga_state(partner_id, ChoreographySagaStatus.DOCUMENTS_VERIFIED, ["document_verification"])
        
        # Log step completed
        self.saga_log.step_completed(saga_id, partner_id, "document_verification", event_data["correlation_id"], "partner-management")
        self.audit_trail.record_step_success(saga_id, partner_id, "document_verification", event_data["correlation_id"], "partner-management")
        self.saga_metrics.record_saga_step(saga_id, "document_verification", 0, True)
        self.saga_metrics.record_saga_event(saga_id)
        
        # Habilitar campañas
        self.event_dispatcher.publish("CampaignsEnabled", {
            "partner_id": partner_id,
            "campaign_permissions": {"can_create_campaigns": True},
            "correlation_id": event_data["correlation_id"],
            "causation_id": event_data["causation_id"]
        })
        
        # Log event published
        self.saga_log.event_published(saga_id, partner_id, "CampaignsEnabled", event_data["correlation_id"], "partner-management", {
            "partner_id": partner_id,
            "campaign_permissions": {"can_create_campaigns": True},
            "correlation_id": event_data["correlation_id"],
            "causation_id": event_data["causation_id"]
        })
        self.audit_trail.record_event_published(saga_id, partner_id, "CampaignsEnabled", event_data["correlation_id"], "partner-management", {
            "partner_id": partner_id,
            "campaign_permissions": {"can_create_campaigns": True},
            "correlation_id": event_data["correlation_id"],
            "causation_id": event_data["causation_id"]
        })
    
    def _handle_campaigns_enabled(self, event_data: Dict[str, Any]):
        """Maneja el evento de campañas habilitadas"""
        partner_id = event_data["partner_id"]
        saga_id = event_data.get("saga_id")
        if not saga_id:
            # Try to get saga_id from saga state
            saga_state = self.saga_state_repository.get(partner_id)
            saga_id = saga_state.get("saga_id") if saga_state else f"saga_{partner_id}"
        event_id = f"campaigns_enabled_{partner_id}_{event_data.get('causation_id', '')}"
        
        # Check if we've already processed this event
        if event_id in self._processed_events:
            self.logger.info(f"Event already processed, skipping: {event_id}")
            return
            
        self._processed_events.add(event_id)
        self.logger.info(f"Campaigns enabled for partner: {partner_id}")
        
        # Log event received and step started
        self.saga_log.event_received(saga_id, partner_id, "CampaignsEnabledConfirmed", event_data["correlation_id"], "partner-management", event_data)
        self.saga_log.step_started(saga_id, partner_id, "campaigns_enabled", event_data["correlation_id"], "partner-management")
        self.audit_trail.record_event_received(saga_id, partner_id, "CampaignsEnabledConfirmed", event_data["correlation_id"], "partner-management", event_data)
        self.audit_trail.record_step_start(saga_id, partner_id, "campaigns_enabled", event_data["correlation_id"], "partner-management")
        
        # Actualizar estado
        self._update_saga_state(partner_id, ChoreographySagaStatus.CAMPAIGNS_ENABLED, ["campaigns_enabled"])
        
        # Log step completed
        self.saga_log.step_completed(saga_id, partner_id, "campaigns_enabled", event_data["correlation_id"], "partner-management")
        self.audit_trail.record_step_success(saga_id, partner_id, "campaigns_enabled", event_data["correlation_id"], "partner-management")
        self.saga_metrics.record_saga_step(saga_id, "campaigns_enabled", 0, True)
        self.saga_metrics.record_saga_event(saga_id)
        
        # Configurar reclutamiento
        self.event_dispatcher.publish("RecruitmentSetupCompleted", {
            "partner_id": partner_id,
            "recruitment_config": {"can_post_jobs": True},
            "correlation_id": event_data["correlation_id"],
            "causation_id": event_data["causation_id"]
        })
        
        # Log event published
        self.saga_log.event_published(saga_id, partner_id, "RecruitmentSetupCompleted", event_data["correlation_id"], "partner-management", {
            "partner_id": partner_id,
            "recruitment_config": {"can_post_jobs": True},
            "correlation_id": event_data["correlation_id"],
            "causation_id": event_data["causation_id"]
        })
        self.audit_trail.record_event_published(saga_id, partner_id, "RecruitmentSetupCompleted", event_data["correlation_id"], "partner-management", {
            "partner_id": partner_id,
            "recruitment_config": {"can_post_jobs": True},
            "correlation_id": event_data["correlation_id"],
            "causation_id": event_data["causation_id"]
        })
    
    def _handle_recruitment_setup(self, event_data: Dict[str, Any]):
        """Maneja el evento de reclutamiento configurado"""
        partner_id = event_data["partner_id"]
        saga_id = event_data.get("saga_id")
        if not saga_id:
            # Try to get saga_id from saga state
            saga_state = self.saga_state_repository.get(partner_id)
            saga_id = saga_state.get("saga_id") if saga_state else f"saga_{partner_id}"
        event_id = f"recruitment_setup_{partner_id}_{event_data.get('causation_id', '')}"
        
        # Check if we've already processed this event
        if event_id in self._processed_events:
            self.logger.info(f"Event already processed, skipping: {event_id}")
            return
            
        self._processed_events.add(event_id)
        self.logger.info(f"Recruitment setup completed for partner: {partner_id}")
        
        # Log event received and step started
        self.saga_log.event_received(saga_id, partner_id, "RecruitmentSetupConfirmed", event_data["correlation_id"], "partner-management", event_data)
        self.saga_log.step_started(saga_id, partner_id, "recruitment_setup", event_data["correlation_id"], "partner-management")
        self.audit_trail.record_event_received(saga_id, partner_id, "RecruitmentSetupConfirmed", event_data["correlation_id"], "partner-management", event_data)
        self.audit_trail.record_step_start(saga_id, partner_id, "recruitment_setup", event_data["correlation_id"], "partner-management")
        
        # Actualizar estado
        self._update_saga_state(partner_id, ChoreographySagaStatus.RECRUITMENT_SETUP, ["recruitment_setup"])
        
        # Log step completed
        self.saga_log.step_completed(saga_id, partner_id, "recruitment_setup", event_data["correlation_id"], "partner-management")
        self.audit_trail.record_step_success(saga_id, partner_id, "recruitment_setup", event_data["correlation_id"], "partner-management")
        self.saga_metrics.record_saga_step(saga_id, "recruitment_setup", 0, True)
        self.saga_metrics.record_saga_event(saga_id)
        
        # Completar la Saga
        self._complete_saga(partner_id, event_data["correlation_id"], event_data["causation_id"])
    
    def _update_saga_state(self, partner_id: str, status: ChoreographySagaStatus, completed_steps: List[str] = None):
        """Actualiza el estado de la Saga"""
        saga_state = self.saga_state_repository.get(partner_id)
        
        if saga_state:
            saga_state["status"] = status
            saga_state["updated_at"] = datetime.now(timezone.utc).isoformat()
            
            if completed_steps:
                if "completed_steps" not in saga_state:
                    saga_state["completed_steps"] = []
                # Only add steps that don't already exist to prevent duplicates
                existing_steps = set(saga_state["completed_steps"])
                new_steps = [step for step in completed_steps if step not in existing_steps]
                saga_state["completed_steps"].extend(new_steps)
            
            self.saga_state_repository.save(partner_id, saga_state)
    
    def _complete_saga(self, partner_id: str, correlation_id: str, causation_id: str):
        """Completa la Saga exitosamente"""
        saga_state = self.saga_state_repository.get(partner_id)
        
        if saga_state:
            saga_id = saga_state.get("saga_id")
            
            # Clear timeout
            if saga_id:
                self._clear_saga_timeout(saga_id)
            
            saga_state["status"] = ChoreographySagaStatus.COMPLETED
            saga_state["updated_at"] = datetime.now(timezone.utc).isoformat()
            self.saga_state_repository.save(partner_id, saga_state)
            
            # Record saga completion in metrics
            if saga_id:
                self.saga_metrics.record_saga_completion(saga_id, "COMPLETED")
        
        self.logger.info(f"Saga completed for partner {partner_id}")
    
    def get_saga_status(self, partner_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene el estado actual de la Saga"""
        return self.saga_state_repository.get(partner_id)
    
    def _initiate_compensation(self, partner_id: str, failed_step: str, correlation_id: str):
        """Inicia la compensación de la Saga"""
        saga_state = self.saga_state_repository.get(partner_id)
        
        if saga_state:
            saga_state["status"] = ChoreographySagaStatus.COMPENSATING
            saga_state["updated_at"] = datetime.now(timezone.utc).isoformat()
            saga_state["failed_steps"] = saga_state.get("failed_steps", []) + [failed_step]
            self.saga_state_repository.save(partner_id, saga_state)
            
            # Record saga failure in metrics
            saga_id = saga_state.get("saga_id")
            if saga_id:
                self.saga_metrics.record_saga_completion(saga_id, "FAILED")
        
        self.logger.info(f"Compensation initiated for partner {partner_id}, failed step: {failed_step}")
    
    def update(self, partner_id: str, updates: Dict[str, Any]):
        """Actualiza el estado de la Saga con los cambios especificados"""
        saga_state = self.saga_state_repository.get(partner_id)
        
        if saga_state:
            saga_state.update(updates)
            saga_state["updated_at"] = datetime.now(timezone.utc).isoformat()
            self.saga_state_repository.save(partner_id, saga_state)
    
    def _set_saga_timeout(self, saga_id: str, partner_id: str, correlation_id: str):
        """Configura un timeout para la saga"""
        def timeout_handler():
            self.logger.warning(f"Saga {saga_id} timed out after {self.timeout_seconds} seconds")
            
            # Check if saga is still active
            saga_state = self.saga_state_repository.get(partner_id)
            if saga_state and saga_state.get("status") in [ChoreographySagaStatus.INITIATED, 
                                                          ChoreographySagaStatus.PARTNER_REGISTERED,
                                                          ChoreographySagaStatus.CONTRACT_CREATED,
                                                          ChoreographySagaStatus.DOCUMENTS_VERIFIED,
                                                          ChoreographySagaStatus.CAMPAIGNS_ENABLED]:
                # Initiate compensation
                self._initiate_compensation(partner_id, "timeout", correlation_id)
                
                # Log timeout
                self.saga_log.saga_failed(saga_id, partner_id, correlation_id, "partner-management", 
                                        {"reason": "timeout", "timeout_seconds": self.timeout_seconds})
                self.audit_trail.record_saga_failure(saga_id, partner_id, correlation_id, "partner-management", 
                                                   {"reason": "timeout", "timeout_seconds": self.timeout_seconds})
        
        # Cancel existing timeout if any
        if saga_id in self._saga_timeouts:
            self._saga_timeouts[saga_id].cancel()
        
        # Set new timeout
        timer = threading.Timer(self.timeout_seconds, timeout_handler)
        timer.start()
        self._saga_timeouts[saga_id] = timer
        
        self.logger.debug(f"Timeout set for saga {saga_id}: {self.timeout_seconds} seconds")
    
    def _clear_saga_timeout(self, saga_id: str):
        """Cancela el timeout de una saga"""
        if saga_id in self._saga_timeouts:
            self._saga_timeouts[saga_id].cancel()
            del self._saga_timeouts[saga_id]
            self.logger.debug(f"Timeout cleared for saga {saga_id}")
    
    def _initiate_compensation(self, partner_id: str, failed_step: str, correlation_id: str):
        """Inicia la compensación de la Saga"""
        saga_state = self.saga_state_repository.get(partner_id)
        
        if saga_state:
            saga_id = saga_state.get("saga_id")
            
            # Clear timeout
            if saga_id:
                self._clear_saga_timeout(saga_id)
            
            saga_state["status"] = ChoreographySagaStatus.COMPENSATING
            saga_state["updated_at"] = datetime.now(timezone.utc).isoformat()
            saga_state["failed_steps"] = saga_state.get("failed_steps", []) + [failed_step]
            self.saga_state_repository.save(partner_id, saga_state)
            
            # Record saga failure in metrics
            if saga_id:
                self.saga_metrics.record_saga_completion(saga_id, "FAILED")
            
            # Log compensation start
            self.saga_log.saga_failed(saga_id, partner_id, correlation_id, "partner-management", 
                                    {"failed_step": failed_step, "reason": "timeout_or_failure"})
            self.audit_trail.record_saga_failure(saga_id, partner_id, correlation_id, "partner-management", 
                                               {"failed_step": failed_step, "reason": "timeout_or_failure"})
            
            # Start compensation process in LIFO order
            self._start_compensation_process(partner_id, saga_id, correlation_id)
        
        self.logger.info(f"Compensation initiated for partner {partner_id}, failed step: {failed_step}")
    
    def _start_compensation_process(self, partner_id: str, saga_id: str, correlation_id: str):
        """Inicia el proceso de compensación en orden LIFO (Last In, First Out)"""
        saga_state = self.saga_state_repository.get(partner_id)
        if not saga_state:
            return
        
        completed_steps = saga_state.get("completed_steps", [])
        if not completed_steps:
            # No steps to compensate, mark as compensated
            self._complete_compensation(partner_id, saga_id, correlation_id)
            return
        
        # Compensate in reverse order (LIFO)
        compensation_steps = list(reversed(completed_steps))
        saga_state["compensation_steps"] = compensation_steps
        saga_state["compensation_index"] = 0
        self.saga_state_repository.save(partner_id, saga_state)
        
        self.logger.info(f"Starting compensation for {len(compensation_steps)} steps: {compensation_steps}")
        
        # Start with the first compensation step
        self._execute_compensation_step(partner_id, saga_id, correlation_id)
    
    def _execute_compensation_step(self, partner_id: str, saga_id: str, correlation_id: str):
        """Ejecuta el siguiente paso de compensación"""
        saga_state = self.saga_state_repository.get(partner_id)
        if not saga_state:
            return
        
        compensation_steps = saga_state.get("compensation_steps", [])
        compensation_index = saga_state.get("compensation_index", 0)
        
        if compensation_index >= len(compensation_steps):
            # All steps compensated
            self._complete_compensation(partner_id, saga_id, correlation_id)
            return
        
        step_to_compensate = compensation_steps[compensation_index]
        self.logger.info(f"Compensating step {compensation_index + 1}/{len(compensation_steps)}: {step_to_compensate}")
        
        # Publish compensation event based on step
        compensation_event = {
            "partner_id": partner_id,
            "saga_id": saga_id,
            "correlation_id": correlation_id,
            "causation_id": str(uuid4()),
            "step": step_to_compensate
        }
        
        if step_to_compensate == "recruitment_setup":
            self.event_dispatcher.publish("RecruitmentSetupCompensationRequested", compensation_event)
        elif step_to_compensate == "campaigns_enabled":
            self.event_dispatcher.publish("CampaignsDisableRequested", compensation_event)
        elif step_to_compensate == "document_verification":
            self.event_dispatcher.publish("DocumentVerificationRevertRequested", compensation_event)
        elif step_to_compensate == "contract_creation":
            self.event_dispatcher.publish("ContractCancellationRequested", compensation_event)
        elif step_to_compensate == "partner_registration":
            self.event_dispatcher.publish("PartnerRegistrationRevertRequested", compensation_event)
        
        # Log compensation step started
        self.saga_log.step_started(saga_id, partner_id, f"compensate_{step_to_compensate}", correlation_id, "partner-management")
        self.audit_trail.record_step_start(saga_id, partner_id, f"compensate_{step_to_compensate}", correlation_id, "partner-management")
    
    def _complete_compensation(self, partner_id: str, saga_id: str, correlation_id: str):
        """Completa el proceso de compensación"""
        saga_state = self.saga_state_repository.get(partner_id)
        if saga_state:
            saga_state["status"] = ChoreographySagaStatus.COMPENSATED
            saga_state["updated_at"] = datetime.now(timezone.utc).isoformat()
            self.saga_state_repository.save(partner_id, saga_state)
            
            # Log compensation completion
            self.saga_log.saga_completed(saga_id, partner_id, correlation_id, "partner-management", 
                                       {"status": "COMPENSATED", "reason": "compensation_completed"})
            self.audit_trail.record_saga_completion(saga_id, partner_id, correlation_id, "partner-management", 
                                                  {"status": "COMPENSATED", "reason": "compensation_completed"})
            
            self.logger.info(f"Compensation completed for partner {partner_id}")
    
    # Compensation event handlers
    def _handle_recruitment_compensated(self, event_data: Dict[str, Any]):
        """Maneja la compensación de recruitment setup"""
        partner_id = event_data["partner_id"]
        saga_id = event_data.get("saga_id")
        correlation_id = event_data["correlation_id"]
        
        self.logger.info(f"Recruitment setup compensated for partner: {partner_id}")
        
        # Log step completed
        self.saga_log.step_completed(saga_id, partner_id, "compensate_recruitment_setup", correlation_id, "partner-management")
        self.audit_trail.record_step_success(saga_id, partner_id, "compensate_recruitment_setup", correlation_id, "partner-management")
        
        # Move to next compensation step
        self._advance_compensation(partner_id, saga_id, correlation_id)
    
    def _handle_campaigns_compensated(self, event_data: Dict[str, Any]):
        """Maneja la compensación de campaigns enabled"""
        partner_id = event_data["partner_id"]
        saga_id = event_data.get("saga_id")
        correlation_id = event_data["correlation_id"]
        
        self.logger.info(f"Campaigns disabled for partner: {partner_id}")
        
        # Log step completed
        self.saga_log.step_completed(saga_id, partner_id, "compensate_campaigns_enabled", correlation_id, "partner-management")
        self.audit_trail.record_step_success(saga_id, partner_id, "compensate_campaigns_enabled", correlation_id, "partner-management")
        
        # Move to next compensation step
        self._advance_compensation(partner_id, saga_id, correlation_id)
    
    def _handle_documents_compensated(self, event_data: Dict[str, Any]):
        """Maneja la compensación de document verification"""
        partner_id = event_data["partner_id"]
        saga_id = event_data.get("saga_id")
        correlation_id = event_data["correlation_id"]
        
        self.logger.info(f"Document verification reverted for partner: {partner_id}")
        
        # Log step completed
        self.saga_log.step_completed(saga_id, partner_id, "compensate_document_verification", correlation_id, "partner-management")
        self.audit_trail.record_step_success(saga_id, partner_id, "compensate_document_verification", correlation_id, "partner-management")
        
        # Move to next compensation step
        self._advance_compensation(partner_id, saga_id, correlation_id)
    
    def _handle_contract_compensated(self, event_data: Dict[str, Any]):
        """Maneja la compensación de contract creation"""
        partner_id = event_data["partner_id"]
        saga_id = event_data.get("saga_id")
        correlation_id = event_data["correlation_id"]
        
        self.logger.info(f"Contract cancelled for partner: {partner_id}")
        
        # Log step completed
        self.saga_log.step_completed(saga_id, partner_id, "compensate_contract_creation", correlation_id, "partner-management")
        self.audit_trail.record_step_success(saga_id, partner_id, "compensate_contract_creation", correlation_id, "partner-management")
        
        # Move to next compensation step
        self._advance_compensation(partner_id, saga_id, correlation_id)
    
    def _handle_partner_compensated(self, event_data: Dict[str, Any]):
        """Maneja la compensación de partner registration"""
        partner_id = event_data["partner_id"]
        saga_id = event_data.get("saga_id")
        correlation_id = event_data["correlation_id"]
        
        self.logger.info(f"Partner registration reverted for partner: {partner_id}")
        
        # Log step completed
        self.saga_log.step_completed(saga_id, partner_id, "compensate_partner_registration", correlation_id, "partner-management")
        self.audit_trail.record_step_success(saga_id, partner_id, "compensate_partner_registration", correlation_id, "partner-management")
        
        # Move to next compensation step
        self._advance_compensation(partner_id, saga_id, correlation_id)
    
    def _advance_compensation(self, partner_id: str, saga_id: str, correlation_id: str):
        """Avanza al siguiente paso de compensación"""
        saga_state = self.saga_state_repository.get(partner_id)
        if not saga_state:
            return
        
        # Increment compensation index
        compensation_index = saga_state.get("compensation_index", 0) + 1
        saga_state["compensation_index"] = compensation_index
        self.saga_state_repository.save(partner_id, saga_state)
        
        # Execute next compensation step
        self._execute_compensation_step(partner_id, saga_id, correlation_id)
