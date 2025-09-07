"""
Activate Campaign command implementation for HexaBuilders.
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
class ActivarCampaign(ComandoCampaign):
    """Command to activate a campaign."""
    
    campaign_id: str
    activated_by: Optional[str] = None


@ejecutar_comando.register
def handle_activar_campaign(comando: ActivarCampaign) -> str:
    """
    Handle ActivateCampaign command.
    """
    logger.info(f"Executing ActivateCampaign command for campaign: {comando.campaign_id}")
    
    try:
        # Validate input data
        _validate_activar_campaign_command(comando)
        
        # Use Unit of Work to activate
        with UnitOfWork() as uow:
            repo = uow.campaigns
            
            # Get existing campaign
            campaign = repo.obtener_por_id(comando.campaign_id)
            if not campaign:
                raise DomainException(f"Campaign with ID {comando.campaign_id} not found")
            
            # Check if partner can activate campaigns
            partner_repo = uow.partners
            partner = partner_repo.obtener_por_id(campaign.partner_id)
            if not partner:
                raise DomainException(f"Partner {campaign.partner_id} not found")
            
            if not partner.puede_crear_campanas():
                raise DomainException(f"Partner {campaign.partner_id} cannot activate campaigns")
            
            # Activate campaign
            campaign.activar()
            
            # Save changes
            repo.actualizar(campaign)
            
            # Commit transaction
            uow.commit()
            
            logger.info(f"Campaign activated successfully: {campaign.id}")
            return campaign.id
    
    except Exception as e:
        logger.error(f"Failed to activate campaign {comando.campaign_id}: {str(e)}")
        raise


def _validate_activar_campaign_command(comando: ActivarCampaign):
    """Validate ActivateCampaign command data."""
    
    if not comando.campaign_id:
        raise DomainException("Campaign ID is required")
    
    logger.debug("ActivateCampaign command validation passed")