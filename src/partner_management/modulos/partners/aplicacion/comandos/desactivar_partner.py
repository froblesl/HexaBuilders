"""
"""

import logging
from dataclasses import dataclass
from typing import Optional

from partner_management.seedwork.aplicacion.comandos import ejecutar_comando
from partner_management.seedwork.infraestructura.uow import UnitOfWork
from partner_management.seedwork.dominio.excepciones import DomainException
from ...dominio.objetos_valor import PartnerStatus
from .base import CommandPartner

logger = logging.getLogger(__name__)


@dataclass
class DesactivarPartner:
    """Command to deactivate a partner."""
    
    partner_id: str
    desactivado_por: Optional[str] = None
    razon_desactivacion: Optional[str] = None


@ejecutar_comando.register
def handle_desactivar_partner(comando: DesactivarPartner) -> str:
    """
    Handle DeactivatePartner command.
    """
    logger.info(f"Executing DeactivatePartner command for partner: {comando.partner_id}")
    
    try:
        # Validate input
        _validate_desactivar_partner_command(comando)
        
        # Use Unit of Work
        with UnitOfWork() as uow:
            repo = uow.partners
            
            # Get existing partner
            partner = repo.obtener_por_id(comando.partner_id)
            if not partner:
                raise DomainException(f"Partner with ID {comando.partner_id} not found")
            
            # Check current status
            if partner.status == PartnerStatus.INACTIVO:
                raise DomainException(f"Partner {comando.partner_id} is already inactive")
            
            # Business rule: Cannot deactivate deleted partners
            if partner.status == PartnerStatus.ELIMINADO:
                raise DomainException(f"Cannot deactivate deleted partner {comando.partner_id}")
            
            # Store old status for event
            old_status = partner.status
            
            # Deactivate partner
            partner.desactivar(
                desactivado_por=comando.desactivado_por,
                razon=comando.razon_desactivacion or "Partner deactivation requested"
            )
            
            # Save changes
            repo.actualizar(partner)
            uow.commit()
            
            logger.info(f"Partner deactivated successfully: {partner.id} ({old_status.value} -> {partner.status.value})")
            return partner.id
    
    except Exception as e:
        logger.error(f"Failed to deactivate partner {comando.partner_id}: {str(e)}")
        raise


def _validate_desactivar_partner_command(comando: DesactivarPartner):
    """Validate DeactivatePartner command data."""
    
    if not comando.partner_id:
        raise DomainException("Partner ID is required")
    
    if comando.desactivado_por and len(comando.desactivado_por.strip()) < 1:
        raise DomainException("Invalid desactivado_por value")
    
    if comando.razon_desactivacion and len(comando.razon_desactivacion.strip()) < 3:
        raise DomainException("Deactivation reason must be at least 3 characters")
    
    logger.debug("DeactivatePartner command validation passed")