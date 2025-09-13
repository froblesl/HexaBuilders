"""
Query to get all legal compliance records with filtering.
"""

import logging
from dataclasses import dataclass
from typing import List, Optional

from onboarding.seedwork.aplicacion.queries import ejecutar_query
from onboarding.seedwork.infraestructura.uow import UnitOfWork
from ...infraestructura.dto import ComplianceDTO
from .base import QueryCompliance, QueryResultCompliance

logger = logging.getLogger(__name__)


@dataclass
class ObtenerTodosCompliance:
    """Query to get all legal compliance records with filtering."""
    partner_id: Optional[str] = None
    compliance_type: Optional[str] = None
    status: Optional[str] = None
    jurisdiction: Optional[str] = None
    limit: Optional[int] = None
    offset: Optional[int] = None


@dataclass
class RespuestaObtenerTodosCompliance:
    """Response for GetAllCompliance query."""
    compliance: List[ComplianceDTO]
    total_count: int


@ejecutar_query.register
def handle_obtener_todos_compliance(query: ObtenerTodosCompliance) -> RespuestaObtenerTodosCompliance:
    """
    Handle GetAllCompliance query.
    """
    logger.info("Executing GetAllCompliance query")
    
    try:
        with UnitOfWork() as uow:
            repo = uow.compliance
            
            filters = {}
            if query.partner_id:
                filters['partner_id'] = query.partner_id
            if query.compliance_type:
                filters['compliance_type'] = query.compliance_type
            if query.status:
                filters['status'] = query.status
            if query.jurisdiction:
                filters['jurisdiction'] = query.jurisdiction
            
            compliance_records = repo.obtener_todos(
                filters=filters,
                limit=query.limit,
                offset=query.offset
            )
            
            total_count = repo.contar(filters=filters)
            compliance_dtos = [ComplianceDTO.from_entity(c) for c in compliance_records]
            
            logger.info(f"Retrieved {len(compliance_dtos)} compliance records successfully")
            return RespuestaObtenerTodosCompliance(
                compliance=compliance_dtos,
                total_count=total_count
            )
    
    except Exception as e:
        logger.error(f"Failed to get compliance records: {str(e)}")
        raise