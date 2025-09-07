"""
Cancel Commission command implementation for HexaBuilders.
"""

import logging
from dataclasses import dataclass

from .....seedwork.aplicacion.comandos import ejecutar_comando
from .....seedwork.infraestructura.uow import UnitOfWork
from .....seedwork.dominio.excepciones import DomainException
from .base import ComandoCommission

logger = logging.getLogger(__name__)


@dataclass
class CancelarCommission(ComandoCommission):
    """Command to cancel a commission."""
    
    commission_id: str
    cancellation_reason: str
    cancelled_by: str


@ejecutar_comando.register
def handle_cancelar_commission(comando: CancelarCommission) -> str:
    """
    Handle CancelCommission command.
    """
    logger.info(f"Executing CancelCommission command for commission: {comando.commission_id}")
    
    try:
        # Validate input data
        _validate_cancelar_commission_command(comando)
        
        # Use Unit of Work to persist
        with UnitOfWork() as uow:
            repo = uow.commissions
            
            # Get existing commission
            commission = repo.obtener_por_id(comando.commission_id)
            if not commission:
                raise DomainException(f"Commission with ID {comando.commission_id} not found")
            
            # Check if commission can be cancelled
            if not commission.puede_ser_cancelada():
                raise DomainException("Commission cannot be cancelled in current state")
            
            # Cancel commission
            commission.cancelar(comando.cancellation_reason, comando.cancelled_by)
            
            # Save updated commission
            repo.actualizar(commission)
            
            # Commit transaction - this will also publish domain events
            uow.commit()
            
            logger.info(f"Commission cancelled successfully: {commission.id}")
            return commission.id
    
    except Exception as e:
        logger.error(f"Failed to cancel commission: {str(e)}")
        raise


def _validate_cancelar_commission_command(comando: CancelarCommission):
    """Validate CancelCommission command data."""
    
    if not comando.commission_id:
        raise DomainException("Commission ID is required")
    
    if not comando.cancellation_reason or len(comando.cancellation_reason.strip()) < 3:
        raise DomainException("Cancellation reason must be at least 3 characters")
    
    if len(comando.cancellation_reason.strip()) > 500:
        raise DomainException("Cancellation reason cannot exceed 500 characters")
    
    if not comando.cancelled_by or len(comando.cancelled_by.strip()) < 2:
        raise DomainException("User performing cancellation is required")
    
    logger.debug("CancelCommission command validation passed")