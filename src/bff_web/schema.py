"""
Schema GraphQL para el BFF Web usando Strawberry.
Define los tipos, queries y mutations para la gestión de Sagas.
"""

import strawberry
from typing import List, Optional
from datetime import datetime
from enum import Enum


@strawberry.enum
class ChoreographySagaStatus:
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


@strawberry.enum
class PartnerType:
    """Tipos de Partner"""
    EMPRESA = "EMPRESA"
    INDIVIDUAL = "INDIVIDUAL"
    FREELANCER = "FREELANCER"


@strawberry.enum
class ContractType:
    """Tipos de Contrato"""
    BASIC = "BASIC"
    STANDARD = "STANDARD"
    PREMIUM = "PREMIUM"
    ENTERPRISE = "ENTERPRISE"


@strawberry.type
class PartnerData:
    """Datos del Partner para el onboarding"""
    partner_id: Optional[str] = None
    nombre: str
    email: str
    telefono: str
    tipo_partner: PartnerType
    preferred_contract_type: ContractType
    required_documents: List[str] = strawberry.field(default_factory=list)
    campaign_permissions: Optional[str] = None
    recruitment_preferences: Optional[str] = None


@strawberry.type
class SagaStep:
    """Paso de una Saga"""
    step_name: str
    status: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None


@strawberry.type
class SagaState:
    """Estado actual de una Saga"""
    partner_id: str
    saga_type: str
    status: ChoreographySagaStatus
    completed_steps: List[str]
    failed_steps: List[str]
    created_at: datetime
    updated_at: datetime
    correlation_id: str
    steps: List[SagaStep] = strawberry.field(default_factory=list)


@strawberry.type
class SagaResponse:
    """Respuesta de operaciones de Saga"""
    success: bool
    message: str
    partner_id: Optional[str] = None
    saga_state: Optional[SagaState] = None
    timestamp: datetime


@strawberry.type
class HealthStatus:
    """Estado de salud del servicio"""
    service: str
    status: str
    pattern: str
    saga_types: List[str]
    event_dispatcher: str
    timestamp: datetime


@strawberry.input
class PartnerOnboardingInput:
    """Input para iniciar onboarding de partner"""
    partner_data: 'PartnerDataInput'
    correlation_id: Optional[str] = None


@strawberry.input
class PartnerDataInput:
    """Input para datos del partner"""
    partner_id: Optional[str] = None
    nombre: str
    email: str
    telefono: str
    tipo_partner: PartnerType
    preferred_contract_type: ContractType
    required_documents: List[str] = strawberry.field(default_factory=list)
    campaign_permissions: Optional[str] = None
    recruitment_preferences: Optional[str] = None


@strawberry.input
class CompensationInput:
    """Input para compensación de Saga"""
    reason: str = "Manual compensation request"


@strawberry.type
class Query:
    """Queries GraphQL para el BFF"""
    
    @strawberry.field
    async def saga_status(self, partner_id: str) -> Optional[SagaState]:
        """Obtiene el estado de una Saga por partner_id"""
        from .resolvers import saga_resolvers
        return await saga_resolvers.get_saga_status(partner_id)
    
    @strawberry.field
    async def health(self) -> HealthStatus:
        """Health check del servicio de Saga"""
        from .resolvers import saga_resolvers
        return await saga_resolvers.get_health_status()


@strawberry.type
class Mutation:
    """Mutations GraphQL para el BFF"""
    
    @strawberry.field
    async def start_partner_onboarding(self, input: PartnerOnboardingInput) -> SagaResponse:
        """Inicia el proceso de onboarding de un partner"""
        from .resolvers import saga_resolvers
        return await saga_resolvers.start_partner_onboarding(input)
    
    @strawberry.field
    async def compensate_saga(self, partner_id: str, input: CompensationInput) -> SagaResponse:
        """Inicia la compensación de una Saga"""
        from .resolvers import saga_resolvers
        return await saga_resolvers.compensate_saga(partner_id, input)


# Schema principal
schema = strawberry.Schema(query=Query, mutation=Mutation)
