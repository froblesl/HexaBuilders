"""
Approve Commission command implementation for HexaBuilders.
"""

import logging
from dataclasses import dataclass
from typing import Optional

from partner_management.seedwork.aplicacion.comandos import ejecutar_comando
from partner_management.seedwork.infraestructura.uow import UnitOfWork
from partner_management.seedwork.dominio.excepciones import DomainException
from .base import CommandCommission

logger = logging.getLogger(__name__)


@dataclass
class AprobarCommission(ComandoCommission):
    """Command to approve a commission for payment."""
    
    commission_id: str
    approved_by: str
    approval_notes: Optional[str] = None


@ejecutar_comando.register
def handle_aprobar_commission(comando: AprobarCommission) -> str:
    """
    Handle ApproveCommission command.
    """
    logger.info(f"Executing ApproveCommission command for commission: {comando.commission_id}")
    
    try:
        # Validate input data
        _validate_aprobar_commission_command(comando)
        
        # Use Unit of Work to persist
        with UnitOfWork() as uow:
            repo = uow.commissions
            
            # Get existing commission
            commission = repo.obtener_por_id(comando.commission_id)
            if not commission:
                raise DomainException(f"Commission with ID {comando.commission_id} not found")
            
            # Check if commission can be approved
            if not commission.puede_ser_ajustada():
                raise DomainException("Commission cannot be approved in current state")
            
            # Approve commission
            commission.aprobar(comando.approved_by, comando.approval_notes)
            
            # Save updated commission
            repo.actualizar(commission)
            
            # Commit transaction - this will also publish domain events
            uow.commit()
            
            logger.info(f"Commission approved successfully: {commission.id}")
            return commission.id
    
    except Exception as e:
        logger.error(f"Failed to approve commission: {str(e)}")
        raise


def _validate_aprobar_commission_command(comando: AprobarCommission):
    """Validate ApproveCommission command data."""
    
    if not comando.commission_id:
        raise DomainException("Commission ID is required")
    
    if not comando.approved_by or len(comando.approved_by.strip()) < 2:
        raise DomainException("Approver identification is required")
    
    if comando.approval_notes and len(comando.approval_notes.strip()) > 1000:
        raise DomainException("Approval notes cannot exceed 1000 characters")
    
    logger.debug("ApproveCommission command validation passed")