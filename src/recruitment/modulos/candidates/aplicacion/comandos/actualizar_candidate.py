"""
Command to update an existing candidate.
"""

import logging
from dataclasses import dataclass
from typing import Optional, List

from recruitment.seedwork.aplicacion.comandos import ejecutar_comando
from recruitment.seedwork.infraestructura.uow import UnitOfWork
from recruitment.seedwork.dominio.excepciones import DomainException

logger = logging.getLogger(__name__)


@dataclass
class ActualizarCandidate:
    """Command to update an existing candidate."""
    
    candidate_id: str
    name: Optional[str] = None
    phone: Optional[str] = None
    skills: Optional[List[str]] = None
    experience_years: Optional[int] = None
    current_position: Optional[str] = None
    current_company: Optional[str] = None
    resume_url: Optional[str] = None
    notes: Optional[str] = None


@ejecutar_comando.register
def handle_actualizar_candidate(comando: ActualizarCandidate) -> None:
    """Handle UpdateCandidate command."""
    logger.info(f"Executing UpdateCandidate command for candidate: {comando.candidate_id}")
    
    try:
        if not comando.candidate_id:
            raise DomainException("Candidate ID is required")
        
        with UnitOfWork() as uow:
            repo = uow.candidates
            candidate = repo.obtener_por_id(comando.candidate_id)
            if not candidate:
                raise DomainException(f"Candidate not found: {comando.candidate_id}")
            
            if comando.name:
                candidate.actualizar_name(comando.name)
            if comando.phone:
                candidate.actualizar_phone(comando.phone)
            if comando.skills:
                candidate.actualizar_skills(comando.skills)
            if comando.experience_years is not None:
                candidate.actualizar_experience_years(comando.experience_years)
            if comando.current_position is not None:
                candidate.actualizar_current_position(comando.current_position)
            if comando.current_company is not None:
                candidate.actualizar_current_company(comando.current_company)
            if comando.resume_url is not None:
                candidate.actualizar_resume_url(comando.resume_url)
            if comando.notes is not None:
                candidate.actualizar_notes(comando.notes)
            
            repo.actualizar(candidate)
            uow.commit()
            
            logger.info(f"Candidate updated successfully: {candidate.id}")
    
    except Exception as e:
        logger.error(f"Failed to update candidate {comando.candidate_id}: {str(e)}")
        raise