"""
"""

import logging
from dataclasses import dataclass
from typing import List, Optional

from partner_management.seedwork.aplicacion.queries import ejecutar_query
from partner_management.seedwork.infraestructura.uow import UnitOfWork
from ...infraestructura.dto import PartnerDTO
from .base import QueryPartner, QueryResultPartner

logger = logging.getLogger(__name__)


@dataclass
class ObtenerTodosPartners:
    """Query to get all partners with optional filtering."""
    
    status: Optional[str] = None
    tipo: Optional[str] = None
    ciudad: Optional[str] = None
    pais: Optional[str] = None
    limit: Optional[int] = None
    offset: Optional[int] = None


@dataclass
class RespuestaObtenerTodosPartners:
    """Response for GetAllPartners query."""
    
    partners: List[PartnerDTO]
    total: int
    limit: Optional[int] = None
    offset: Optional[int] = None


@ejecutar_query.register
def handle_obtener_todos_partners(query: ObtenerTodosPartners) -> RespuestaObtenerTodosPartners:
    """
    Handle GetAllPartners query.
    """
    logger.info(f"Executing GetAllPartners query with filters: status={query.status}, tipo={query.tipo}")
    
    try:
        # Use Unit of Work for read operations
        with UnitOfWork() as uow:
            repo = uow.partners
            
            # Build filter criteria
            filtros = {}
            if query.status:
                filtros['status'] = query.status
            if query.tipo:
                filtros['tipo'] = query.tipo
            if query.ciudad:
                filtros['ciudad'] = query.ciudad
            if query.pais:
                filtros['pais'] = query.pais
            
            # Get partners with filters
            partners = repo.obtener_todos(
                filtros=filtros,
                limit=query.limit,
                offset=query.offset
            )
            
            # Get total count for pagination
            total = repo.contar_con_filtros(filtros)
            
            # Convert to DTOs
            partner_dtos = [PartnerDTO.from_entity(partner) for partner in partners]
            
            logger.info(f"Retrieved {len(partner_dtos)} partners (total: {total})")
            
            return RespuestaObtenerTodosPartners(
                partners=partner_dtos,
                total=total,
                limit=query.limit,
                offset=query.offset
            )
    
    except Exception as e:
        logger.error(f"Failed to get all partners: {str(e)}")
        raise