"""
Update Commission command implementation for HexaBuilders.
"""

import logging
from dataclasses import dataclass
from typing import Optional
from decimal import Decimal

from .....seedwork.aplicacion.comandos import ejecutar_comando
from .....seedwork.infraestructura.uow import UnitOfWork
from .....seedwork.dominio.excepciones import DomainException
from ...dominio.objetos_valor import CommissionAmount, CommissionRate
from .base import ComandoCommission

logger = logging.getLogger(__name__)


@dataclass
class ActualizarCommission(ComandoCommission):
    """Command to update a commission."""
    
    commission_id: str
    nuevo_monto: Optional[Decimal] = None
    nueva_rate: Optional[Decimal] = None
    adjustment_reason: Optional[str] = None
    adjusted_by: str = "system"
    currency: str = "USD"


@ejecutar_comando.register
def handle_actualizar_commission(comando: ActualizarCommission) -> str:
    """
    Handle UpdateCommission command.
    """
    logger.info(f"Executing UpdateCommission command for commission: {comando.commission_id}")
    
    try:
        # Validate input data
        _validate_actualizar_commission_command(comando)
        
        # Use Unit of Work to persist
        with UnitOfWork() as uow:
            repo = uow.commissions
            
            # Get existing commission
            commission = repo.obtener_por_id(comando.commission_id)
            if not commission:
                raise DomainException(f"Commission with ID {comando.commission_id} not found")
            
            # Update commission amount if provided
            if comando.nuevo_monto is not None:
                nuevo_commission_amount = CommissionAmount(comando.nuevo_monto, comando.currency)
                commission.ajustar_monto(
                    nuevo_commission_amount, 
                    comando.adjustment_reason or "Commission amount updated",
                    comando.adjusted_by
                )
            
            # Update commission rate if provided 
            if comando.nueva_rate is not None:
                nueva_commission_rate = CommissionRate(comando.nueva_rate)
                # Recalculate based on original transaction amount
                original_transaction_amount = commission.transaction_reference.transaction_amount
                commission.recalcular(
                    nueva_commission_rate,
                    original_transaction_amount,
                    comando.adjustment_reason or "Commission rate updated",
                    comando.adjusted_by
                )
            
            # Save updated commission
            repo.actualizar(commission)
            
            # Commit transaction - this will also publish domain events
            uow.commit()
            
            logger.info(f"Commission updated successfully: {commission.id}")
            return commission.id
    
    except Exception as e:
        logger.error(f"Failed to update commission: {str(e)}")
        raise


def _validate_actualizar_commission_command(comando: ActualizarCommission):
    """Validate UpdateCommission command data."""
    
    if not comando.commission_id:
        raise DomainException("Commission ID is required")
    
    if comando.nuevo_monto is not None:
        if comando.nuevo_monto <= 0:
            raise DomainException("New commission amount must be positive")
        
        if comando.nuevo_monto > Decimal('100000'):
            raise DomainException("Commission amount cannot exceed 100,000")
    
    if comando.nueva_rate is not None:
        if comando.nueva_rate < 0 or comando.nueva_rate > 1:
            raise DomainException("Commission rate must be between 0 and 1")
    
    if comando.nuevo_monto is None and comando.nueva_rate is None:
        raise DomainException("At least one field (amount or rate) must be provided for update")
    
    if not comando.adjusted_by:
        raise DomainException("User performing adjustment is required")
    
    logger.debug("UpdateCommission command validation passed")