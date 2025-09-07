"""
"""

import logging
from dataclasses import dataclass
from typing import Optional

from ....seedwork.aplicacion.comandos import ejecutar_comando
from ....seedwork.infraestructura.uow import UnitOfWork
from ....seedwork.dominio.excepciones import DomainException
from ...dominio.objetos_valor import PartnerStatus
from .base import ComandoPartner

logger = logging.getLogger(__name__)


@dataclass
class ActivarPartner(ComandoPartner):
    """Command to activate a partner."""
    
    partner_id: str
    activado_por: Optional[str] = None
    razon_activacion: Optional[str] = None


@ejecutar_comando.register
def handle_activar_partner(comando: ActivarPartner) -> str:
    """
    Handle ActivatePartner command.
    """
    logger.info(f"Executing ActivatePartner command for partner: {comando.partner_id}")
    
    try:
        # Validate input
        _validate_activar_partner_command(comando)
        
        # Use Unit of Work
        with UnitOfWork() as uow:
            repo = uow.partners
            
            # Get existing partner
            partner = repo.obtener_por_id(comando.partner_id)
            if not partner:
                raise DomainException(f"Partner with ID {comando.partner_id} not found")
            
            # Check current status
            if partner.status == PartnerStatus.ACTIVO:
                raise DomainException(f"Partner {comando.partner_id} is already active")
            
            # Business rule: Can only activate INACTIVO or SUSPENDIDO partners
            if partner.status not in [PartnerStatus.INACTIVO, PartnerStatus.SUSPENDIDO]:
                raise DomainException(
                    f"Cannot activate partner with status {partner.status.value}. "
                    f"Partner must be INACTIVO or SUSPENDIDO"
                )
            
            # Store old status for event
            old_status = partner.status
            
            # Activate partner
            partner.activar(
                activado_por=comando.activado_por,
                razon=comando.razon_activacion or "Partner activation requested"
            )
            
            # Save changes
            repo.actualizar(partner)
            uow.commit()
            
            logger.info(f"Partner activated successfully: {partner.id} ({old_status.value} -> {partner.status.value})")
            return partner.id
    
    except Exception as e:
        logger.error(f"Failed to activate partner {comando.partner_id}: {str(e)}")
        raise


def _validate_activar_partner_command(comando: ActivarPartner):
    """Validate ActivatePartner command data."""
    
    if not comando.partner_id:
        raise DomainException("Partner ID is required")
    
    if comando.activado_por and len(comando.activado_por.strip()) < 1:
        raise DomainException("Invalid activado_por value")
    
    if comando.razon_activacion and len(comando.razon_activacion.strip()) < 3:
        raise DomainException("Activation reason must be at least 3 characters")
    
    logger.debug("ActivatePartner command validation passed")