"""
Query to get a negotiation by ID.
"""

import logging
from dataclasses import dataclass
from typing import Optional

from onboarding.seedwork.aplicacion.queries import ejecutar_query
from onboarding.seedwork.infraestructura.uow import UnitOfWork
from onboarding.seedwork.dominio.excepciones import DomainException
from ...infraestructura.dto import NegotiationDTO
from .base import QueryNegotiation, QueryResultNegotiation

logger = logging.getLogger(__name__)


@dataclass
class ObtenerNegotiation:
    """Query to get a negotiation by ID."""
    negotiation_id: str


@dataclass
class RespuestaObtenerNegotiation:
    """Response for GetNegotiation query."""
    negotiation: Optional[NegotiationDTO] = None


@ejecutar_query.register
def handle_obtener_negotiation(query: ObtenerNegotiation) -> RespuestaObtenerNegotiation:
    """
    Handle GetNegotiation query.
    """
    logger.info(f"Executing GetNegotiation query for negotiation: {query.negotiation_id}")
    
    try:
        if not query.negotiation_id:
            raise DomainException("Negotiation ID is required")
        
        with UnitOfWork() as uow:
            repo = uow.negotiations
            negotiation = repo.obtener_por_id(query.negotiation_id)
            
            if not negotiation:
                logger.warning(f"Negotiation not found: {query.negotiation_id}")
                return RespuestaObtenerNegotiation(negotiation=None)
            
            negotiation_dto = NegotiationDTO.from_entity(negotiation)
            
            logger.info(f"Negotiation retrieved successfully: {negotiation.id}")
            return RespuestaObtenerNegotiation(negotiation=negotiation_dto)
    
    except Exception as e:
        logger.error(f"Failed to get negotiation {query.negotiation_id}: {str(e)}")
        raise