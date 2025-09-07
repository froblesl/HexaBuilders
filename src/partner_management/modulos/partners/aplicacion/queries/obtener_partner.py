"""
"""

import logging
from dataclasses import dataclass
from typing import Optional

from ....seedwork.aplicacion.queries import ejecutar_query
from ....seedwork.infraestructura.uow import UnitOfWork
from ....seedwork.dominio.excepciones import DomainException
from ...infraestructura.dto import PartnerDTO
from .base import QueryPartner, QueryResultPartner

logger = logging.getLogger(__name__)


@dataclass
class ObtenerPartner(QueryPartner):
    """Query to get a partner by ID."""
    partner_id: str


@dataclass
class RespuestaObtenerPartner(QueryResultPartner):
    """Response for GetPartner query."""
    partner: Optional[PartnerDTO] = None


@ejecutar_query.register
def handle_obtener_partner(query: ObtenerPartner) -> RespuestaObtenerPartner:
    """
    Handle GetPartner query.
    """
    logger.info(f"Executing GetPartner query for partner: {query.partner_id}")
    
    try:
        # Validate input
        if not query.partner_id:
            raise DomainException("Partner ID is required")
        
        # Use Unit of Work for read operations
        with UnitOfWork() as uow:
            repo = uow.partners
            
            # Get partner
            partner = repo.obtener_por_id(query.partner_id)
            
            if not partner:
                logger.warning(f"Partner not found: {query.partner_id}")
                return RespuestaObtenerPartner(partner=None)
            
            # Convert to DTO
            partner_dto = PartnerDTO.from_entity(partner)
            
            logger.info(f"Partner retrieved successfully: {partner.id}")
            return RespuestaObtenerPartner(partner=partner_dto)
    
    except Exception as e:
        logger.error(f"Failed to get partner {query.partner_id}: {str(e)}")
        raise