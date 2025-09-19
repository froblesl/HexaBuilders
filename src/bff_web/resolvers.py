"""
Resolvers GraphQL para el BFF Web.
Implementa la lógica de negocio para las queries y mutations.
"""

import logging
from typing import Optional, List
from datetime import datetime

from .schema import (
    SagaState, SagaStep, SagaResponse, HealthStatus,
    ChoreographySagaStatus, PartnerOnboardingInput, CompensationInput
)
from .saga_client import saga_client

logger = logging.getLogger(__name__)


class SagaResolvers:
    """Resolvers para operaciones de Saga"""
    
    def __init__(self):
        self.saga_client = saga_client
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def get_saga_status(self, partner_id: str) -> Optional[SagaState]:
        """Obtiene el estado de una Saga"""
        try:
            response = await self.saga_client.get_saga_status(partner_id)
            
            if not response:
                return None
            
            # Convertir respuesta a SagaState
            return self._convert_to_saga_state(response)
            
        except Exception as e:
            self.logger.error("Error getting saga status: %s", str(e))
            return None
    
    async def start_partner_onboarding(self, input: PartnerOnboardingInput) -> SagaResponse:
        """Inicia el proceso de onboarding de un partner"""
        try:
            # Convertir input a formato esperado por el servicio
            partner_data = {
                "partner_id": input.partner_data.partner_id,
                "nombre": input.partner_data.nombre,
                "email": input.partner_data.email,
                "telefono": input.partner_data.telefono,
                "tipo_partner": input.partner_data.tipo_partner.value,
                "preferred_contract_type": input.partner_data.preferred_contract_type.value,
                "required_documents": input.partner_data.required_documents,
                "campaign_permissions": input.partner_data.campaign_permissions,
                "recruitment_preferences": input.partner_data.recruitment_preferences
            }
            
            response = await self.saga_client.start_partner_onboarding(
                partner_data=partner_data,
                correlation_id=input.correlation_id
            )
            
            return SagaResponse(
                success=True,
                message=response.get("message", "Partner onboarding saga initiated successfully"),
                partner_id=response.get("partner_id"),
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            self.logger.error("Error starting partner onboarding: %s", str(e))
            return SagaResponse(
                success=False,
                message=f"Error starting partner onboarding: {str(e)}",
                timestamp=datetime.utcnow()
            )
    
    async def compensate_saga(self, partner_id: str, input: CompensationInput) -> SagaResponse:
        """Inicia la compensación de una Saga"""
        try:
            response = await self.saga_client.compensate_saga(
                partner_id=partner_id,
                reason=input.reason
            )
            
            return SagaResponse(
                success=True,
                message=response.get("message", "Saga compensation initiated"),
                partner_id=partner_id,
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            self.logger.error("Error compensating saga: %s", str(e))
            return SagaResponse(
                success=False,
                message=f"Error compensating saga: {str(e)}",
                partner_id=partner_id,
                timestamp=datetime.utcnow()
            )
    
    async def get_health_status(self) -> HealthStatus:
        """Obtiene el estado de salud del servicio"""
        try:
            response = await self.saga_client.health_check()
            
            return HealthStatus(
                service=response.get("service", "saga-choreography-management"),
                status=response.get("status", "unknown"),
                pattern=response.get("pattern", "choreography"),
                saga_types=response.get("saga_types", []),
                event_dispatcher=response.get("event_dispatcher", "unknown"),
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            self.logger.error("Error getting health status: %s", str(e))
            return HealthStatus(
                service="saga-choreography-management",
                status="unhealthy",
                pattern="choreography",
                saga_types=[],
                event_dispatcher="error",
                timestamp=datetime.utcnow()
            )
    
    def _convert_to_saga_state(self, response: dict) -> SagaState:
        """Convierte la respuesta del servicio a SagaState"""
        try:
            # Mapear status string a enum
            status_mapping = {
                "initiated": ChoreographySagaStatus.INITIATED,
                "partner_registered": ChoreographySagaStatus.PARTNER_REGISTERED,
                "contract_created": ChoreographySagaStatus.CONTRACT_CREATED,
                "documents_verified": ChoreographySagaStatus.DOCUMENTS_VERIFIED,
                "campaigns_enabled": ChoreographySagaStatus.CAMPAIGNS_ENABLED,
                "recruitment_setup": ChoreographySagaStatus.RECRUITMENT_SETUP,
                "completed": ChoreographySagaStatus.COMPLETED,
                "failed": ChoreographySagaStatus.FAILED,
                "compensating": ChoreographySagaStatus.COMPENSATING,
                "compensated": ChoreographySagaStatus.COMPENSATED
            }
            
            status_str = response.get("status", "initiated")
            status = status_mapping.get(status_str, ChoreographySagaStatus.INITIATED)
            
            # Convertir fechas
            created_at = datetime.fromisoformat(response.get("created_at", datetime.utcnow().isoformat()))
            updated_at = datetime.fromisoformat(response.get("updated_at", datetime.utcnow().isoformat()))
            
            # Crear pasos de la saga (si están disponibles)
            steps = []
            if "steps" in response:
                for step_data in response["steps"]:
                    step = SagaStep(
                        step_name=step_data.get("step_name", "unknown"),
                        status=step_data.get("status", "pending"),
                        started_at=datetime.fromisoformat(step_data["started_at"]) if step_data.get("started_at") else None,
                        completed_at=datetime.fromisoformat(step_data["completed_at"]) if step_data.get("completed_at") else None,
                        error_message=step_data.get("error_message")
                    )
                    steps.append(step)
            
            return SagaState(
                partner_id=response.get("partner_id", ""),
                saga_type=response.get("saga_type", "partner_onboarding"),
                status=status,
                completed_steps=response.get("completed_steps", []),
                failed_steps=response.get("failed_steps", []),
                created_at=created_at,
                updated_at=updated_at,
                correlation_id=response.get("correlation_id", ""),
                steps=steps
            )
            
        except Exception as e:
            self.logger.error("Error converting to saga state: %s", str(e))
            # Retornar estado por defecto en caso de error
            return SagaState(
                partner_id=response.get("partner_id", ""),
                saga_type="partner_onboarding",
                status=ChoreographySagaStatus.FAILED,
                completed_steps=[],
                failed_steps=[],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                correlation_id=response.get("correlation_id", ""),
                steps=[]
            )


# Instancia global de resolvers
saga_resolvers = SagaResolvers()
