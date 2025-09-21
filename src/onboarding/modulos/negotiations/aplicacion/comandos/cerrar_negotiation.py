"""
Command to close a negotiation successfully.
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
class CerrarNegotiation:
    """Command to close a negotiation successfully."""
    
    negotiation_id: str
    final_value: Decimal
    closed_by: str
    closure_notes: Optional[str] = None


@ejecutar_comando.register
def handle_cerrar_negotiation(comando: CerrarNegotiation) -> None:
    """Handle CloseNegotiation command."""
    logger.info(f"Executing CloseNegotiation command for negotiation: {comando.negotiation_id}")
    
    try:
        if not comando.negotiation_id or not comando.closed_by:
            raise DomainException("Negotiation ID and closed by are required")
        
        if comando.final_value <= 0:
            raise DomainException("Final value must be greater than 0")
        
        with UnitOfWork() as uow:
            repo = uow.negotiations
            negotiation = repo.obtener_por_id(comando.negotiation_id)
            if not negotiation:
                raise DomainException(f"Negotiation not found: {comando.negotiation_id}")
            
            negotiation.cerrar(
                final_value=comando.final_value,
                closed_by=comando.closed_by,
                closure_notes=comando.closure_notes
            )
            
            repo.actualizar(negotiation)
            uow.commit()
            
            logger.info(f"Negotiation closed successfully: {negotiation.id}")
    
    except Exception as e:
        logger.error(f"Failed to close negotiation {comando.negotiation_id}: {str(e)}")
        raise