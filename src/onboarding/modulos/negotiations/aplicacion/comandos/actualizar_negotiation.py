"""
Command to update an existing negotiation.
"""

import logging
from dataclasses import dataclass
from typing import Optional
from decimal import Decimal

from src.onboarding.seedwork.aplicacion.comandos import ejecutar_comando
from src.onboarding.seedwork.infraestructura.uow import UnitOfWork
from src.onboarding.seedwork.dominio.excepciones import DomainException

logger = logging.getLogger(__name__)


@dataclass
class ActualizarNegotiation:
    """Command to update an existing negotiation."""
    
    negotiation_id: str
    subject: Optional[str] = None
    current_offer: Optional[Decimal] = None
    target_value: Optional[Decimal] = None
    notes: Optional[str] = None
    updated_by: Optional[str] = None


@ejecutar_comando.register
def handle_actualizar_negotiation(comando: ActualizarNegotiation) -> None:
    """Handle UpdateNegotiation command."""
    logger.info(f"Executing UpdateNegotiation command for negotiation: {comando.negotiation_id}")
    
    try:
        if not comando.negotiation_id:
            raise DomainException("Negotiation ID is required")
        
        with UnitOfWork() as uow:
            repo = uow.negotiations
            negotiation = repo.obtener_por_id(comando.negotiation_id)
            if not negotiation:
                raise DomainException(f"Negotiation not found: {comando.negotiation_id}")
            
            if comando.subject:
                negotiation.actualizar_subject(comando.subject)
            if comando.current_offer is not None:
                negotiation.actualizar_current_offer(comando.current_offer)
            if comando.target_value is not None:
                negotiation.actualizar_target_value(comando.target_value)
            if comando.notes is not None:
                negotiation.actualizar_notes(comando.notes)
            if comando.updated_by:
                negotiation.actualizar_metadata(updated_by=comando.updated_by)
            
            repo.actualizar(negotiation)
            uow.commit()
            
            logger.info(f"Negotiation updated successfully: {negotiation.id}")
    
    except Exception as e:
        logger.error(f"Failed to update negotiation {comando.negotiation_id}: {str(e)}")
        raise