"""
Query to get all candidates with filtering.
"""

import logging
from dataclasses import dataclass
from typing import List, Optional

from recruitment.seedwork.aplicacion.queries import ejecutar_query
from recruitment.seedwork.infraestructura.uow import UnitOfWork
from ...infraestructura.dto import CandidateDTO
from .base import QueryCandidate, QueryResultCandidate

logger = logging.getLogger(__name__)


@dataclass
class ObtenerTodosCandidates:
    """Query to get all candidates with filtering."""
    status: Optional[str] = None
    skills: Optional[List[str]] = None
    min_experience: Optional[int] = None
    max_experience: Optional[int] = None
    current_company: Optional[str] = None
    limit: Optional[int] = None
    offset: Optional[int] = None


@dataclass
class RespuestaObtenerTodosCandidates:
    """Response for GetAllCandidates query."""
    candidates: List[CandidateDTO]
    total_count: int


@ejecutar_query.register
def handle_obtener_todos_candidates(query: ObtenerTodosCandidates) -> RespuestaObtenerTodosCandidates:
    """
    Handle GetAllCandidates query.
    """
    logger.info("Executing GetAllCandidates query")
    
    try:
        with UnitOfWork() as uow:
            repo = uow.candidates
            
            filters = {}
            if query.status:
                filters['status'] = query.status
            if query.skills:
                filters['skills'] = query.skills
            if query.min_experience is not None:
                filters['min_experience'] = query.min_experience
            if query.max_experience is not None:
                filters['max_experience'] = query.max_experience
            if query.current_company:
                filters['current_company'] = query.current_company
            
            candidates = repo.obtener_todos(
                filters=filters,
                limit=query.limit,
                offset=query.offset
            )
            
            total_count = repo.contar(filters=filters)
            candidate_dtos = [CandidateDTO.from_entity(c) for c in candidates]
            
            logger.info(f"Retrieved {len(candidate_dtos)} candidates successfully")
            return RespuestaObtenerTodosCandidates(
                candidates=candidate_dtos,
                total_count=total_count
            )
    
    except Exception as e:
        logger.error(f"Failed to get candidates: {str(e)}")
        raise