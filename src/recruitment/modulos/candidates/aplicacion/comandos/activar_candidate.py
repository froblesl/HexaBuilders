"""
Command to activate a candidate.
"""

import logging
from dataclasses import dataclass

from recruitment.seedwork.aplicacion.comandos import ejecutar_comando
from recruitment.seedwork.infraestructura.uow import UnitOfWork
from recruitment.seedwork.dominio.excepciones import DomainException

logger = logging.getLogger(__name__)


@dataclass
class ActivarCandidate:
    """Command to activate a candidate."""
    
    candidate_id: str
    activated_by: str


@ejecutar_comando.register
def handle_activar_candidate(comando: ActivarCandidate) -> None:
    """Handle ActivateCandidate command."""
    logger.info(f"Executing ActivateCandidate command for candidate: {comando.candidate_id}")
    
    try:
        if not comando.candidate_id or not comando.activated_by:
            raise DomainException("Candidate ID and activated by are required")
        
        with UnitOfWork() as uow:
            repo = uow.candidates
            candidate = repo.obtener_por_id(comando.candidate_id)
            if not candidate:
                raise DomainException(f"Candidate not found: {comando.candidate_id}")
            
            candidate.activar(activated_by=comando.activated_by)
            
            repo.actualizar(candidate)
            uow.commit()
            
            logger.info(f"Candidate activated successfully: {candidate.id}")
    
    except Exception as e:
        logger.error(f"Failed to activate candidate {comando.candidate_id}: {str(e)}")
        raise