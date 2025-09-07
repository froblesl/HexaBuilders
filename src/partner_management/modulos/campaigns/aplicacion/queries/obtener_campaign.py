"""
Get Campaign query implementation for HexaBuilders.
"""

import logging
from dataclasses import dataclass
from typing import Optional

from .....seedwork.aplicacion.queries import ejecutar_query
from .....seedwork.infraestructura.uow import UnitOfWork
from .....seedwork.dominio.excepciones import DomainException
from ...infraestructura.dto import CampaignDTO
from .base import QueryCampaign, QueryResultCampaign

logger = logging.getLogger(__name__)


@dataclass
class ObtenerCampaign(QueryCampaign):
    """Query to get a campaign by ID."""
    campaign_id: str


@dataclass
class RespuestaObtenerCampaign(QueryResultCampaign):
    """Response for GetCampaign query."""
    campaign: Optional[CampaignDTO] = None


@ejecutar_query.register
def handle_obtener_campaign(query: ObtenerCampaign) -> RespuestaObtenerCampaign:
    """
    Handle GetCampaign query.
    """
    logger.info(f"Executing GetCampaign query for campaign: {query.campaign_id}")
    
    try:
        # Validate input
        if not query.campaign_id:
            raise DomainException("Campaign ID is required")
        
        # Use Unit of Work for read operations
        with UnitOfWork() as uow:
            repo = uow.campaigns
            
            # Get campaign
            campaign = repo.obtener_por_id(query.campaign_id)
            
            if not campaign:
                logger.warning(f"Campaign not found: {query.campaign_id}")
                return RespuestaObtenerCampaign(campaign=None)
            
            # Convert to DTO
            campaign_dto = CampaignDTO.from_entity(campaign)
            
            logger.info(f"Campaign retrieved successfully: {campaign.id}")
            return RespuestaObtenerCampaign(campaign=campaign_dto)
    
    except Exception as e:
        logger.error(f"Failed to get campaign {query.campaign_id}: {str(e)}")
        raise