"""
Deactivate Campaign command implementation for HexaBuilders.
"""

import logging
from dataclasses import dataclass
from typing import Optional

from .....seedwork.aplicacion.comandos import ejecutar_comando
from .....seedwork.infraestructura.uow import UnitOfWork
from .....seedwork.dominio.excepciones import DomainException
from .base import ComandoCampaign

logger = logging.getLogger(__name__)


@dataclass
class DesactivarCampaign(ComandoCampaign):
    """Command to deactivate (pause) a campaign."""
    
    campaign_id: str
    reason: str
    paused_by: Optional[str] = None


@ejecutar_comando.register
def handle_desactivar_campaign(comando: DesactivarCampaign) -> str:
    """
    Handle DeactivateCampaign command.
    """
    logger.info(f"Executing DeactivateCampaign command for campaign: {comando.campaign_id}")
    
    try:
        # Validate input data
        _validate_desactivar_campaign_command(comando)
        
        # Use Unit of Work to deactivate
        with UnitOfWork() as uow:
            repo = uow.campaigns
            
            # Get existing campaign
            campaign = repo.obtener_por_id(comando.campaign_id)
            if not campaign:
                raise DomainException(f"Campaign with ID {comando.campaign_id} not found")
            
            # Pause campaign
            campaign.pausar(comando.reason, comando.paused_by)
            
            # Save changes
            repo.actualizar(campaign)
            
            # Commit transaction
            uow.commit()
            
            logger.info(f"Campaign deactivated successfully: {campaign.id}")
            return campaign.id
    
    except Exception as e:
        logger.error(f"Failed to deactivate campaign {comando.campaign_id}: {str(e)}")
        raise


def _validate_desactivar_campaign_command(comando: DesactivarCampaign):
    """Validate DeactivateCampaign command data."""
    
    if not comando.campaign_id:
        raise DomainException("Campaign ID is required")
    
    if not comando.reason or len(comando.reason.strip()) < 5:
        raise DomainException("Deactivation reason must be at least 5 characters")
    
    logger.debug("DeactivateCampaign command validation passed")