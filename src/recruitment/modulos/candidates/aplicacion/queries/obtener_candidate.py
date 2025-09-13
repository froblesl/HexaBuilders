"""
Query to get a candidate by ID.
"""

import logging
from dataclasses import dataclass
from typing import Optional

from recruitment.seedwork.aplicacion.queries import ejecutar_query
from recruitment.seedwork.infraestructura.uow import UnitOfWork
from recruitment.seedwork.dominio.excepciones import DomainException
from ...infraestructura.dto import CandidateDTO
from .base import QueryCandidate, QueryResultCandidate

logger = logging.getLogger(__name__)


@dataclass
class ObtenerCandidate:
    """Query to get a candidate by ID."""
    candidate_id: str


@dataclass
class RespuestaObtenerCandidate:
    """Response for GetCandidate query."""
    candidate: Optional[CandidateDTO] = None


@ejecutar_query.register
def handle_obtener_candidate(query: ObtenerCandidate) -> RespuestaObtenerCandidate:
    """
    Handle GetCandidate query.
    """
    logger.info(f"Executing GetCandidate query for candidate: {query.candidate_id}")
    
    try:
        if not query.candidate_id:
            raise DomainException("Candidate ID is required")
        
        with UnitOfWork() as uow:
            repo = uow.candidates
            candidate = repo.obtener_por_id(query.candidate_id)
            
            if not candidate:
                logger.warning(f"Candidate not found: {query.candidate_id}")
                return RespuestaObtenerCandidate(candidate=None)
            
            candidate_dto = CandidateDTO.from_entity(candidate)
            
            logger.info(f"Candidate retrieved successfully: {candidate.id}")
            return RespuestaObtenerCandidate(candidate=candidate_dto)
    
    except Exception as e:
        logger.error(f"Failed to get candidate {query.candidate_id}: {str(e)}")
        raise