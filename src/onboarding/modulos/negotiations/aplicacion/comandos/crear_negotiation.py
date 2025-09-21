"""
Command to create a new negotiation.
"""

import logging
from dataclasses import dataclass
from typing import Optional
from decimal import Decimal

from src.onboarding.seedwork.aplicacion.comandos import ejecutar_comando
from src.onboarding.seedwork.infraestructura.uow import UnitOfWork
from src.onboarding.seedwork.dominio.excepciones import DomainException
from ...dominio.entidades import Negotiation
from ...dominio.objetos_valor import NegotiationType, NegotiationStatus
from ...infraestructura.fabricas import FabricaNegotiation
from .base import CommandNegotiation

logger = logging.getLogger(__name__)


@dataclass
class CrearNegotiation:
    """Command to create a new negotiation."""
    
    partner_id: str
    negotiation_type: str
    subject: str
    initial_offer: Decimal
    target_value: Optional[Decimal] = None
    negotiator: str
    notes: Optional[str] = None


@ejecutar_comando.register
def handle_crear_negotiation(comando: CrearNegotiation) -> str:
    """Handle CreateNegotiation command."""
    logger.info(f"Executing CreateNegotiation command for partner: {comando.partner_id}")
    
    try:
        _validate_crear_negotiation_command(comando)
        
        negotiation_type = NegotiationType(comando.negotiation_type)
        negotiation_status = NegotiationStatus("OPEN")
        
        fabrica = FabricaNegotiation()
        negotiation = fabrica.crear_negotiation(
            partner_id=comando.partner_id,
            negotiation_type=negotiation_type,
            subject=comando.subject,
            initial_offer=comando.initial_offer,
            target_value=comando.target_value,
            status=negotiation_status,
            negotiator=comando.negotiator,
            notes=comando.notes
        )
        
        with UnitOfWork() as uow:
            repo = uow.negotiations
            repo.agregar(negotiation)
            uow.commit()
            
            logger.info(f"Negotiation created successfully: {negotiation.id}")
            return negotiation.id
    
    except Exception as e:
        logger.error(f"Failed to create negotiation: {str(e)}")
        raise


def _validate_crear_negotiation_command(comando: CrearNegotiation):
    """Validate CreateNegotiation command data."""
    if not comando.partner_id:
        raise DomainException("Partner ID is required")
    
    valid_types = ['COMMISSION_RATE', 'CONTRACT_TERMS', 'PAYMENT_TERMS', 'SLA', 'OTHER']
    if comando.negotiation_type not in valid_types:
        raise DomainException(f"Negotiation type must be one of: {valid_types}")
    
    if not comando.subject or len(comando.subject.strip()) < 5:
        raise DomainException("Subject must be at least 5 characters")
    
    if comando.initial_offer <= 0:
        raise DomainException("Initial offer must be greater than 0")
    
    if not comando.negotiator:
        raise DomainException("Negotiator is required")
    
    logger.debug("CreateNegotiation command validation passed")