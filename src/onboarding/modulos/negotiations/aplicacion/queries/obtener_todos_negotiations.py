"""
Query to get all negotiations with filtering.
"""

import logging
from dataclasses import dataclass
from typing import List, Optional

from onboarding.seedwork.aplicacion.queries import ejecutar_query
from onboarding.seedwork.infraestructura.uow import UnitOfWork
from ...infraestructura.dto import NegotiationDTO
from .base import QueryNegotiation, QueryResultNegotiation

logger = logging.getLogger(__name__)


@dataclass
class ObtenerTodosNegotiations:
    """Query to get all negotiations with filtering."""
    partner_id: Optional[str] = None
    negotiation_type: Optional[str] = None
    status: Optional[str] = None
    negotiator: Optional[str] = None
    limit: Optional[int] = None
    offset: Optional[int] = None


@dataclass
class RespuestaObtenerTodosNegotiations:
    """Response for GetAllNegotiations query."""
    negotiations: List[NegotiationDTO]
    total_count: int


@ejecutar_query.register
def handle_obtener_todos_negotiations(query: ObtenerTodosNegotiations) -> RespuestaObtenerTodosNegotiations:
    """
    Handle GetAllNegotiations query.
    """
    logger.info("Executing GetAllNegotiations query")
    
    try:
        with UnitOfWork() as uow:
            repo = uow.negotiations
            
            filters = {}
            if query.partner_id:
                filters['partner_id'] = query.partner_id
            if query.negotiation_type:
                filters['negotiation_type'] = query.negotiation_type
            if query.status:
                filters['status'] = query.status
            if query.negotiator:
                filters['negotiator'] = query.negotiator
            
            negotiations = repo.obtener_todos(
                filters=filters,
                limit=query.limit,
                offset=query.offset
            )
            
            total_count = repo.contar(filters=filters)
            negotiation_dtos = [NegotiationDTO.from_entity(n) for n in negotiations]
            
            logger.info(f"Retrieved {len(negotiation_dtos)} negotiations successfully")
            return RespuestaObtenerTodosNegotiations(
                negotiations=negotiation_dtos,
                total_count=total_count
            )
    
    except Exception as e:
        logger.error(f"Failed to get negotiations: {str(e)}")
        raise