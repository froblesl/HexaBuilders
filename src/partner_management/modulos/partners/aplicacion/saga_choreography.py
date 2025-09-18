"""
Implementación de Saga basada en Choreography usando eventos.
Cada servicio maneja su propio estado y publica eventos para coordinar.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4

from ...seedwork.dominio.eventos import IntegrationEvent
from ...seedwork.infraestructura.utils import EventDispatcher


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


# Eventos de la Saga de Choreography
class PartnerOnboardingInitiated(IntegrationEvent):
    """Evento que inicia el proceso de onboarding"""
    partner_id: str
    partner_data: Dict[str, Any]
    correlation_id: str
    causation_id: str


class PartnerRegistrationCompleted(IntegrationEvent):
    """Evento cuando el partner se registra exitosamente"""
    partner_id: str
    partner_data: Dict[str, Any]
    correlation_id: str
    causation_id: str


class ContractCreationRequested(IntegrationEvent):
    """Evento para solicitar creación de contrato"""
    partner_id: str
    contract_type: str
    correlation_id: str
    causation_id: str


class ContractCreated(IntegrationEvent):
    """Evento cuando el contrato se crea exitosamente"""
    partner_id: str
    contract_id: str
    contract_type: str
    correlation_id: str
    causation_id: str


class DocumentVerificationRequested(IntegrationEvent):
    """Evento para solicitar verificación de documentos"""
    partner_id: str
    required_documents: List[str]
    correlation_id: str
    causation_id: str


class DocumentsVerified(IntegrationEvent):
    """Evento cuando los documentos se verifican exitosamente"""
    partner_id: str
    package_id: str
    verification_level: str
    correlation_id: str
    causation_id: str


class CampaignEnablementRequested(IntegrationEvent):
    """Evento para solicitar habilitación de campañas"""
    partner_id: str
    permissions: Dict[str, Any]
    correlation_id: str
    causation_id: str


class CampaignsEnabled(IntegrationEvent):
    """Evento cuando las campañas se habilitan exitosamente"""
    partner_id: str
    permissions: Dict[str, Any]
    correlation_id: str
    causation_id: str


class RecruitmentSetupRequested(IntegrationEvent):
    """Evento para solicitar configuración de reclutamiento"""
    partner_id: str
    preferences: Dict[str, Any]
    correlation_id: str
    causation_id: str


class RecruitmentSetupCompleted(IntegrationEvent):
    """Evento cuando el reclutamiento se configura exitosamente"""
    partner_id: str
    preferences: Dict[str, Any]
    correlation_id: str
    causation_id: str


class PartnerOnboardingCompleted(IntegrationEvent):
    """Evento cuando el onboarding se completa exitosamente"""
    partner_id: str
    contract_id: str
    package_id: str
    correlation_id: str
    causation_id: str


# Eventos de compensación
class PartnerOnboardingFailed(IntegrationEvent):
    """Evento cuando el onboarding falla"""
    partner_id: str
    failure_step: str
    error_message: str
    correlation_id: str
    causation_id: str


class CompensationRequested(IntegrationEvent):
    """Evento para solicitar compensación"""
    partner_id: str
    failed_step: str
    compensation_data: Dict[str, Any]
    correlation_id: str
    causation_id: str


class CompensationCompleted(IntegrationEvent):
    """Evento cuando la compensación se completa"""
    partner_id: str
    compensated_steps: List[str]
    correlation_id: str
    causation_id: str


class ChoreographySagaOrchestrator:
    """
    Orquestador de Saga basado en Choreography.
    Maneja el estado de la Saga y coordina eventos entre servicios.
    """
    
    def __init__(self, event_dispatcher: EventDispatcher, saga_state_repository):
        self.event_dispatcher = event_dispatcher
        self.saga_state_repository = saga_state_repository
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Registrar handlers de eventos
        self._register_event_handlers()
    
    def _register_event_handlers(self):
        """Registra los handlers de eventos de la Saga"""
        self.event_dispatcher.subscribe(PartnerOnboardingInitiated, self._handle_onboarding_initiated)
        self.event_dispatcher.subscribe(PartnerRegistrationCompleted, self._handle_partner_registered)
        self.event_dispatcher.subscribe(ContractCreated, self._handle_contract_created)
        self.event_dispatcher.subscribe(DocumentsVerified, self._handle_documents_verified)
        self.event_dispatcher.subscribe(CampaignsEnabled, self._handle_campaigns_enabled)
        self.event_dispatcher.subscribe(RecruitmentSetupCompleted, self._handle_recruitment_setup)
        self.event_dispatcher.subscribe(PartnerOnboardingFailed, self._handle_onboarding_failed)
    
    async def start_partner_onboarding(self, partner_data: Dict[str, Any], correlation_id: str) -> str:
        """Inicia el proceso de onboarding de un partner"""
        partner_id = partner_data.get('partner_id')
        causation_id = str(uuid4())
        
        # Crear estado inicial de la Saga
        saga_state = {
            "partner_id": partner_id,
            "status": ChoreographySagaStatus.INITIATED,
            "correlation_id": correlation_id,
            "causation_id": causation_id,
            "partner_data": partner_data,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "completed_steps": [],
            "failed_steps": []
        }
        
        await self.saga_state_repository.save(partner_id, saga_state)
        
        # Publicar evento de inicio
        event = PartnerOnboardingInitiated(
            partner_id=partner_id,
            partner_data=partner_data,
            correlation_id=correlation_id,
            causation_id=causation_id
        )
        
        self.event_dispatcher.publish(event)
        
        return partner_id
    
    async def _handle_onboarding_initiated(self, event: PartnerOnboardingInitiated):
        """Maneja el evento de onboarding iniciado"""
        self.logger.info(f"Partner onboarding initiated for {event.partner_id}")
        
        # Solicitar registro del partner
        registration_event = PartnerRegistrationRequested(
            partner_id=event.partner_id,
            partner_data=event.partner_data,
            correlation_id=event.correlation_id,
            causation_id=event.causation_id
        )
        
        self.event_dispatcher.publish(registration_event)
    
    async def _handle_partner_registered(self, event: PartnerRegistrationCompleted):
        """Maneja el evento de partner registrado"""
        self.logger.info(f"Partner registered: {event.partner_id}")
        
        # Actualizar estado de la Saga
        await self._update_saga_state(
            event.partner_id,
            ChoreographySagaStatus.PARTNER_REGISTERED,
            ["partner_registration"]
        )
        
        # Solicitar creación de contrato
        contract_event = ContractCreationRequested(
            partner_id=event.partner_id,
            contract_type=event.partner_data.get('preferred_contract_type', 'STANDARD'),
            correlation_id=event.correlation_id,
            causation_id=event.causation_id
        )
        
        self.event_dispatcher.publish(contract_event)
    
    async def _handle_contract_created(self, event: ContractCreated):
        """Maneja el evento de contrato creado"""
        self.logger.info(f"Contract created for partner {event.partner_id}: {event.contract_id}")
        
        # Actualizar estado de la Saga
        await self._update_saga_state(
            event.partner_id,
            ChoreographySagaStatus.CONTRACT_CREATED,
            ["contract_creation"]
        )
        
        # Solicitar verificación de documentos
        documents_event = DocumentVerificationRequested(
            partner_id=event.partner_id,
            required_documents=event.partner_data.get('required_documents', []),
            correlation_id=event.correlation_id,
            causation_id=event.causation_id
        )
        
        self.event_dispatcher.publish(documents_event)
    
    async def _handle_documents_verified(self, event: DocumentsVerified):
        """Maneja el evento de documentos verificados"""
        self.logger.info(f"Documents verified for partner {event.partner_id}: {event.package_id}")
        
        # Actualizar estado de la Saga
        await self._update_saga_state(
            event.partner_id,
            ChoreographySagaStatus.DOCUMENTS_VERIFIED,
            ["document_verification"]
        )
        
        # Solicitar habilitación de campañas
        campaigns_event = CampaignEnablementRequested(
            partner_id=event.partner_id,
            permissions=event.partner_data.get('campaign_permissions', {}),
            correlation_id=event.correlation_id,
            causation_id=event.causation_id
        )
        
        self.event_dispatcher.publish(campaigns_event)
    
    async def _handle_campaigns_enabled(self, event: CampaignsEnabled):
        """Maneja el evento de campañas habilitadas"""
        self.logger.info(f"Campaigns enabled for partner {event.partner_id}")
        
        # Actualizar estado de la Saga
        await self._update_saga_state(
            event.partner_id,
            ChoreographySagaStatus.CAMPAIGNS_ENABLED,
            ["campaign_enablement"]
        )
        
        # Solicitar configuración de reclutamiento
        recruitment_event = RecruitmentSetupRequested(
            partner_id=event.partner_id,
            preferences=event.partner_data.get('recruitment_preferences', {}),
            correlation_id=event.correlation_id,
            causation_id=event.causation_id
        )
        
        self.event_dispatcher.publish(recruitment_event)
    
    async def _handle_recruitment_setup(self, event: RecruitmentSetupCompleted):
        """Maneja el evento de reclutamiento configurado"""
        self.logger.info(f"Recruitment setup completed for partner {event.partner_id}")
        
        # Actualizar estado de la Saga
        await self._update_saga_state(
            event.partner_id,
            ChoreographySagaStatus.RECRUITMENT_SETUP,
            ["recruitment_setup"]
        )
        
        # Completar la Saga
        await self._complete_saga(event.partner_id, event.correlation_id, event.causation_id)
    
    async def _handle_onboarding_failed(self, event: PartnerOnboardingFailed):
        """Maneja el evento de onboarding fallido"""
        self.logger.error(f"Partner onboarding failed for {event.partner_id}: {event.error_message}")
        
        # Actualizar estado de la Saga
        await self._update_saga_state(
            event.partner_id,
            ChoreographySagaStatus.FAILED,
            failed_steps=[event.failure_step]
        )
        
        # Iniciar compensación
        await self._initiate_compensation(event.partner_id, event.failure_step, event.correlation_id)
    
    async def _update_saga_state(self, partner_id: str, status: ChoreographySagaStatus, 
                                completed_steps: List[str] = None, failed_steps: List[str] = None):
        """Actualiza el estado de la Saga"""
        saga_state = await self.saga_state_repository.get(partner_id)
        
        if saga_state:
            saga_state["status"] = status
            saga_state["updated_at"] = datetime.now(timezone.utc).isoformat()
            
            if completed_steps:
                saga_state["completed_steps"].extend(completed_steps)
            
            if failed_steps:
                saga_state["failed_steps"].extend(failed_steps)
            
            await self.saga_state_repository.save(partner_id, saga_state)
    
    async def _complete_saga(self, partner_id: str, correlation_id: str, causation_id: str):
        """Completa la Saga exitosamente"""
        saga_state = await self.saga_state_repository.get(partner_id)
        
        if saga_state:
            saga_state["status"] = ChoreographySagaStatus.COMPLETED
            saga_state["updated_at"] = datetime.now(timezone.utc).isoformat()
            await self.saga_state_repository.save(partner_id, saga_state)
        
        # Publicar evento de completado
        completed_event = PartnerOnboardingCompleted(
            partner_id=partner_id,
            contract_id=saga_state.get("contract_id"),
            package_id=saga_state.get("package_id"),
            correlation_id=correlation_id,
            causation_id=causation_id
        )
        
        self.event_dispatcher.publish(completed_event)
    
    async def _initiate_compensation(self, partner_id: str, failed_step: str, correlation_id: str):
        """Inicia el proceso de compensación"""
        saga_state = await self.saga_state_repository.get(partner_id)
        
        if not saga_state:
            return
        
        # Determinar pasos a compensar
        completed_steps = saga_state.get("completed_steps", [])
        steps_to_compensate = self._get_compensation_order(completed_steps, failed_step)
        
        # Actualizar estado
        saga_state["status"] = ChoreographySagaStatus.COMPENSATING
        saga_state["updated_at"] = datetime.now(timezone.utc).isoformat()
        await self.saga_state_repository.save(partner_id, saga_state)
        
        # Publicar eventos de compensación
        for step in steps_to_compensate:
            compensation_event = CompensationRequested(
                partner_id=partner_id,
                failed_step=step,
                compensation_data=saga_state.get("step_data", {}).get(step, {}),
                correlation_id=correlation_id,
                causation_id=saga_state.get("causation_id")
            )
            
            self.event_dispatcher.publish(compensation_event)
    
    def _get_compensation_order(self, completed_steps: List[str], failed_step: str) -> List[str]:
        """Determina el orden de compensación (orden inverso)"""
        step_order = [
            "recruitment_setup",
            "campaign_enablement", 
            "document_verification",
            "contract_creation",
            "partner_registration"
        ]
        
        # Encontrar el índice del paso fallido
        failed_index = step_order.index(failed_step) if failed_step in step_order else len(step_order)
        
        # Retornar pasos completados en orden inverso hasta el paso fallido
        compensation_steps = []
        for step in reversed(completed_steps):
            if step in step_order:
                step_index = step_order.index(step)
                if step_index < failed_index:
                    compensation_steps.append(step)
        
        return compensation_steps


# Repositorio para estado de Saga
class SagaStateRepository:
    """Repositorio para persistir el estado de las Sagas de Choreography"""
    
    def __init__(self, storage_backend):
        self.storage = storage_backend
        self.logger = logging.getLogger(self.__class__.__name__)
        # Almacenamiento en memoria para simplicidad
        self._memory_storage = {}
    
    async def save(self, partner_id: str, saga_state: Dict[str, Any]):
        """Guarda el estado de la Saga"""
        try:
            # Guardar en memoria
            self._memory_storage[partner_id] = saga_state
            
            # Si hay un storage backend, también guardar ahí
            if hasattr(self.storage, 'set'):
                await self.storage.set(f"saga_state:{partner_id}", saga_state)
            
            self.logger.debug(f"Saga state saved for partner {partner_id}")
        except Exception as e:
            self.logger.error(f"Failed to save saga state for partner {partner_id}: {str(e)}")
            raise
    
    async def get(self, partner_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene el estado de la Saga"""
        try:
            # Primero intentar desde memoria
            if partner_id in self._memory_storage:
                return self._memory_storage[partner_id]
            
            # Si hay un storage backend, intentar desde ahí
            if hasattr(self.storage, 'get'):
                return await self.storage.get(f"saga_state:{partner_id}")
            
            return None
        except Exception as e:
            self.logger.error(f"Failed to get saga state for partner {partner_id}: {str(e)}")
            return None
    
    async def delete(self, partner_id: str):
        """Elimina el estado de la Saga"""
        try:
            # Eliminar de memoria
            if partner_id in self._memory_storage:
                del self._memory_storage[partner_id]
            
            # Si hay un storage backend, también eliminar de ahí
            if hasattr(self.storage, 'delete'):
                await self.storage.delete(f"saga_state:{partner_id}")
            
            self.logger.debug(f"Saga state deleted for partner {partner_id}")
        except Exception as e:
            self.logger.error(f"Failed to delete saga state for partner {partner_id}: {str(e)}")
            raise
