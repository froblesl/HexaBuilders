"""
Query to get a legal compliance record by ID.
"""

import logging
from dataclasses import dataclass
from typing import Optional

from onboarding.seedwork.aplicacion.queries import ejecutar_query
from onboarding.seedwork.infraestructura.uow import UnitOfWork
from onboarding.seedwork.dominio.excepciones import DomainException
from ...infraestructura.dto import ComplianceDTO
from .base import QueryCompliance, QueryResultCompliance

logger = logging.getLogger(__name__)


@dataclass
class ObtenerCompliance:
    """Query to get a legal compliance record by ID."""
    compliance_id: str


@dataclass
class RespuestaObtenerCompliance:
    """Response for GetCompliance query."""
    compliance: Optional[ComplianceDTO] = None


@ejecutar_query.register
def handle_obtener_compliance(query: ObtenerCompliance) -> RespuestaObtenerCompliance:
    """
    Handle GetCompliance query.
    """
    logger.info(f"Executing GetCompliance query for compliance: {query.compliance_id}")
    
    try:
        if not query.compliance_id:
            raise DomainException("Compliance ID is required")
        
        with UnitOfWork() as uow:
            repo = uow.compliance
            compliance = repo.obtener_por_id(query.compliance_id)
            
            if not compliance:
                logger.warning(f"Compliance not found: {query.compliance_id}")
                return RespuestaObtenerCompliance(compliance=None)
            
            compliance_dto = ComplianceDTO.from_entity(compliance)
            
            logger.info(f"Compliance retrieved successfully: {compliance.id}")
            return RespuestaObtenerCompliance(compliance=compliance_dto)
    
    except Exception as e:
        logger.error(f"Failed to get compliance {query.compliance_id}: {str(e)}")
        raise