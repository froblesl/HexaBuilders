"""
Implementación de Saga basada en Choreography usando Apache Pulsar.
Cada servicio maneja su propio estado y publica eventos para coordinar.
"""

import logging
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


# Importar el dispatcher de Pulsar
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../../..'))
from src.pulsar_event_dispatcher import PulsarEventDispatcher


class ChoreographySagaOrchestrator:
    """
    Orquestador de Saga basado en Choreography usando Apache Pulsar.
    """
    
    def __init__(self, saga_state_repository: SagaStateRepository, event_dispatcher: PulsarEventDispatcher):
        self.saga_state_repository = saga_state_repository
        self.event_dispatcher = event_dispatcher
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Track processed events to prevent duplicates
        self._processed_events = set()
        
        # Suscribirse a eventos
        self._subscribe_to_events()
    
    def _subscribe_to_events(self):
        """Suscribirse a eventos de la Saga"""
        self.event_dispatcher.subscribe("PartnerRegistrationCompleted", self._handle_partner_registered)
        self.event_dispatcher.subscribe("ContractCreated", self._handle_contract_created)
        self.event_dispatcher.subscribe("DocumentsVerified", self._handle_documents_verified)
        self.event_dispatcher.subscribe("CampaignsEnabledConfirmed", self._handle_campaigns_enabled)
        self.event_dispatcher.subscribe("RecruitmentSetupConfirmed", self._handle_recruitment_setup)
    
    def start_partner_onboarding(self, partner_data: Dict[str, Any], correlation_id: str) -> str:
        """Inicia el proceso de onboarding de un partner"""
        partner_id = partner_data.get('partner_id', str(uuid4()))
        causation_id = str(uuid4())
        
        # Crear estado inicial de la Saga
        saga_state = {
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
        
        # Publicar evento de inicio
        self.event_dispatcher.publish("PartnerOnboardingInitiated", {
            "partner_id": partner_id,
            "partner_data": partner_data,
            "correlation_id": correlation_id,
            "causation_id": causation_id
        })
        
        return partner_id
    
    def _handle_partner_registered(self, event_data: Dict[str, Any]):
        """Maneja el evento de partner registrado"""
        partner_id = event_data["partner_id"]
        event_id = f"partner_registered_{partner_id}_{event_data.get('causation_id', '')}"
        
        # Check if we've already processed this event
        if event_id in self._processed_events:
            self.logger.info(f"Event already processed, skipping: {event_id}")
            return
            
        self._processed_events.add(event_id)
        self.logger.info(f"Partner registered: {partner_id}")
        
        # Actualizar estado
        self._update_saga_state(partner_id, ChoreographySagaStatus.PARTNER_REGISTERED, ["partner_registration"])
        
        # Solicitar creación de contrato
        self.event_dispatcher.publish("ContractCreationRequested", {
            "partner_id": partner_id,
            "contract_data": {"tipo_contrato": "BASIC"},
            "correlation_id": event_data["correlation_id"],
            "causation_id": event_data["causation_id"]
        })
    
    def _handle_contract_created(self, event_data: Dict[str, Any]):
        """Maneja el evento de contrato creado"""
        partner_id = event_data["partner_id"]
        event_id = f"contract_created_{partner_id}_{event_data.get('causation_id', '')}"
        
        # Check if we've already processed this event
        if event_id in self._processed_events:
            self.logger.info(f"Event already processed, skipping: {event_id}")
            return
            
        self._processed_events.add(event_id)
        self.logger.info(f"Contract created for partner: {partner_id}")
        
        # Actualizar estado
        self._update_saga_state(partner_id, ChoreographySagaStatus.CONTRACT_CREATED, ["contract_creation"])
        
        # Solicitar verificación de documentos
        self.event_dispatcher.publish("DocumentVerificationRequested", {
            "partner_id": partner_id,
            "document_types": ["IDENTITY", "BUSINESS_REGISTRATION"],
            "correlation_id": event_data["correlation_id"],
            "causation_id": event_data["causation_id"]
        })
    
    def _handle_documents_verified(self, event_data: Dict[str, Any]):
        """Maneja el evento de documentos verificados"""
        partner_id = event_data["partner_id"]
        event_id = f"documents_verified_{partner_id}_{event_data.get('causation_id', '')}"
        
        # Check if we've already processed this event
        if event_id in self._processed_events:
            self.logger.info(f"Event already processed, skipping: {event_id}")
            return
            
        self._processed_events.add(event_id)
        self.logger.info(f"Documents verified for partner: {partner_id}")
        
        # Actualizar estado
        self._update_saga_state(partner_id, ChoreographySagaStatus.DOCUMENTS_VERIFIED, ["document_verification"])
        
        # Habilitar campañas
        self.event_dispatcher.publish("CampaignsEnabled", {
            "partner_id": partner_id,
            "campaign_permissions": {"can_create_campaigns": True},
            "correlation_id": event_data["correlation_id"],
            "causation_id": event_data["causation_id"]
        })
    
    def _handle_campaigns_enabled(self, event_data: Dict[str, Any]):
        """Maneja el evento de campañas habilitadas"""
        partner_id = event_data["partner_id"]
        event_id = f"campaigns_enabled_{partner_id}_{event_data.get('causation_id', '')}"
        
        # Check if we've already processed this event
        if event_id in self._processed_events:
            self.logger.info(f"Event already processed, skipping: {event_id}")
            return
            
        self._processed_events.add(event_id)
        self.logger.info(f"Campaigns enabled for partner: {partner_id}")
        
        # Actualizar estado
        self._update_saga_state(partner_id, ChoreographySagaStatus.CAMPAIGNS_ENABLED, ["campaigns_enabled"])
        
        # Configurar reclutamiento
        self.event_dispatcher.publish("RecruitmentSetupCompleted", {
            "partner_id": partner_id,
            "recruitment_config": {"can_post_jobs": True},
            "correlation_id": event_data["correlation_id"],
            "causation_id": event_data["causation_id"]
        })
    
    def _handle_recruitment_setup(self, event_data: Dict[str, Any]):
        """Maneja el evento de reclutamiento configurado"""
        partner_id = event_data["partner_id"]
        event_id = f"recruitment_setup_{partner_id}_{event_data.get('causation_id', '')}"
        
        # Check if we've already processed this event
        if event_id in self._processed_events:
            self.logger.info(f"Event already processed, skipping: {event_id}")
            return
            
        self._processed_events.add(event_id)
        self.logger.info(f"Recruitment setup completed for partner: {partner_id}")
        
        # Actualizar estado
        self._update_saga_state(partner_id, ChoreographySagaStatus.RECRUITMENT_SETUP, ["recruitment_setup"])
        
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
            saga_state["status"] = ChoreographySagaStatus.COMPLETED
            saga_state["updated_at"] = datetime.now(timezone.utc).isoformat()
            self.saga_state_repository.save(partner_id, saga_state)
        
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
        
        self.logger.info(f"Compensation initiated for partner {partner_id}, failed step: {failed_step}")
    
    def update(self, partner_id: str, updates: Dict[str, Any]):
        """Actualiza el estado de la Saga con los cambios especificados"""
        saga_state = self.saga_state_repository.get(partner_id)
        
        if saga_state:
            saga_state.update(updates)
            saga_state["updated_at"] = datetime.now(timezone.utc).isoformat()
            self.saga_state_repository.save(partner_id, saga_state)
