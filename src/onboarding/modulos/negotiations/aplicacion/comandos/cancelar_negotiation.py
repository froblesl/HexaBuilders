"""
Command to cancel a negotiation.
"""

import logging
from dataclasses import dataclass
from typing import Optional

from onboarding.seedwork.aplicacion.comandos import ejecutar_comando
from onboarding.seedwork.infraestructura.uow import UnitOfWork
from onboarding.seedwork.dominio.excepciones import DomainException

logger = logging.getLogger(__name__)


@dataclass
class CancelarNegotiation:
    """Command to cancel a negotiation."""
    
    negotiation_id: str
    cancelled_by: str
    cancellation_reason: str
    cancellation_notes: Optional[str] = None


@ejecutar_comando.register
def handle_cancelar_negotiation(comando: CancelarNegotiation) -> None:
    """Handle CancelNegotiation command."""
    logger.info(f"Executing CancelNegotiation command for negotiation: {comando.negotiation_id}")
    
    try:
        if not all([comando.negotiation_id, comando.cancelled_by, comando.cancellation_reason]):
            raise DomainException("Negotiation ID, cancelled by, and cancellation reason are required")
        
        with UnitOfWork() as uow:
            repo = uow.negotiations
            negotiation = repo.obtener_por_id(comando.negotiation_id)
            if not negotiation:
                raise DomainException(f"Negotiation not found: {comando.negotiation_id}")
            
            negotiation.cancelar(
                cancelled_by=comando.cancelled_by,
                cancellation_reason=comando.cancellation_reason,
                cancellation_notes=comando.cancellation_notes
            )
            
            repo.actualizar(negotiation)
            uow.commit()
            
            logger.info(f"Negotiation cancelled successfully: {negotiation.id}")
    
    except Exception as e:
        logger.error(f"Failed to cancel negotiation {comando.negotiation_id}: {str(e)}")
        raise