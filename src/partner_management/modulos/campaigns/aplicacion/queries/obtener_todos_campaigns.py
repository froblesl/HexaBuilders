"""
Get All Campaigns query implementation for HexaBuilders.
"""

import logging
from dataclasses import dataclass
from typing import Optional, List

from partner_management.seedwork.aplicacion.queries import ejecutar_query
from partner_management.seedwork.infraestructura.uow import UnitOfWork
from partner_management.seedwork.dominio.excepciones import DomainException
from ...infraestructura.dto import CampaignDTO, CampaignListResponseDTO
from .base import QueryCampaign, QueryResultCampaign

logger = logging.getLogger(__name__)


@dataclass
class ObtenerTodosCampaigns(QueryCampaign):
    """Query to get all campaigns with optional filters."""
    partner_id: Optional[str] = None
    status: Optional[str] = None
    tipo_campaign: Optional[str] = None
    page: int = 1
    page_size: int = 10
    sort_by: str = "created_at"
    sort_order: str = "desc"


@dataclass
class RespuestaObtenerTodosCampaigns(QueryResultCampaign):
    """Response for GetAllCampaigns query."""
    campaigns: List[CampaignDTO] = None
    total: int = 0
    page: int = 1
    page_size: int = 10
    total_pages: int = 0
    
    def __post_init__(self):
        if self.campaigns is None:
            self.campaigns = []


@ejecutar_query.register
def handle_obtener_todos_campaigns(query: ObtenerTodosCampaigns) -> RespuestaObtenerTodosCampaigns:
    """
    Handle GetAllCampaigns query.
    """
    logger.info(f"Executing GetAllCampaigns query with filters: partner_id={query.partner_id}, status={query.status}")
    
    try:
        # Validate input
        _validate_obtener_todos_campaigns_query(query)
        
        # Use Unit of Work for read operations
        with UnitOfWork() as uow:
            repo = uow.campaigns
            
            # Build filters
            filters = {}
            if query.partner_id:
                filters['partner_id'] = query.partner_id
            if query.status:
                filters['status'] = query.status
            if query.tipo_campaign:
                filters['tipo'] = query.tipo_campaign
            
            # Get campaigns with pagination
            campaigns, total = repo.obtener_con_filtros(
                filtros=filters,
                page=query.page,
                page_size=query.page_size,
                sort_by=query.sort_by,
                sort_order=query.sort_order
            )
            
            # Convert to DTOs
            campaign_dtos = [CampaignDTO.from_entity(campaign) for campaign in campaigns]
            
            # Calculate total pages
            total_pages = (total + query.page_size - 1) // query.page_size
            
            logger.info(f"Retrieved {len(campaigns)} campaigns out of {total} total")
            
            return RespuestaObtenerTodosCampaigns(
                campaigns=campaign_dtos,
                total=total,
                page=query.page,
                page_size=query.page_size,
                total_pages=total_pages
            )
    
    except Exception as e:
        logger.error(f"Failed to get campaigns: {str(e)}")
        raise


def _validate_obtener_todos_campaigns_query(query: ObtenerTodosCampaigns):
    """Validate GetAllCampaigns query data."""
    
    if query.page < 1:
        raise DomainException("Page must be 1 or greater")
    
    if query.page_size < 1 or query.page_size > 100:
        raise DomainException("Page size must be between 1 and 100")
    
    valid_statuses = ['DRAFT', 'ACTIVE', 'PAUSED', 'COMPLETED', 'CANCELLED']
    if query.status and query.status not in valid_statuses:
        raise DomainException(f"Invalid status. Valid options: {valid_statuses}")
    
    valid_types = ['PERFORMANCE', 'BRAND_AWARENESS', 'LEAD_GENERATION', 'SALES', 'ENGAGEMENT']
    if query.tipo_campaign and query.tipo_campaign not in valid_types:
        raise DomainException(f"Invalid campaign type. Valid options: {valid_types}")
    
    valid_sort_fields = ['created_at', 'updated_at', 'nombre', 'start_date', 'end_date', 'status']
    if query.sort_by not in valid_sort_fields:
        raise DomainException(f"Invalid sort field. Valid options: {valid_sort_fields}")
    
    valid_sort_orders = ['asc', 'desc']
    if query.sort_order not in valid_sort_orders:
        raise DomainException(f"Invalid sort order. Valid options: {valid_sort_orders}")
    
    logger.debug("GetAllCampaigns query validation passed")