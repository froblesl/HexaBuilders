"""
Command to deactivate a candidate.
"""

import logging
from dataclasses import dataclass
from typing import Optional

from recruitment.seedwork.aplicacion.comandos import ejecutar_comando
from recruitment.seedwork.infraestructura.uow import UnitOfWork
from recruitment.seedwork.dominio.excepciones import DomainException

logger = logging.getLogger(__name__)


@dataclass
class DesactivarCandidate:
    """Command to deactivate a candidate."""
    
    candidate_id: str
    deactivated_by: str
    reason: Optional[str] = None


@ejecutar_comando.register
def handle_desactivar_candidate(comando: DesactivarCandidate) -> None:
    """Handle DeactivateCandidate command."""
    logger.info(f"Executing DeactivateCandidate command for candidate: {comando.candidate_id}")
    
    try:
        if not comando.candidate_id or not comando.deactivated_by:
            raise DomainException("Candidate ID and deactivated by are required")
        
        with UnitOfWork() as uow:
            repo = uow.candidates
            candidate = repo.obtener_por_id(comando.candidate_id)
            if not candidate:
                raise DomainException(f"Candidate not found: {comando.candidate_id}")
            
            candidate.desactivar(
                deactivated_by=comando.deactivated_by,
                reason=comando.reason
            )
            
            repo.actualizar(candidate)
            uow.commit()
            
            logger.info(f"Candidate deactivated successfully: {candidate.id}")
    
    except Exception as e:
        logger.error(f"Failed to deactivate candidate {comando.candidate_id}: {str(e)}")
        raise