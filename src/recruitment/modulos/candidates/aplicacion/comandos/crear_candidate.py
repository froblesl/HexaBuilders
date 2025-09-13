"""
Command to create a new candidate.
"""

import logging
from dataclasses import dataclass
from typing import Optional, List

from recruitment.seedwork.aplicacion.comandos import ejecutar_comando
from recruitment.seedwork.infraestructura.uow import UnitOfWork
from recruitment.seedwork.dominio.excepciones import DomainException
from ...dominio.entidades import Candidate
from ...dominio.objetos_valor import CandidateStatus
from ...infraestructura.fabricas import FabricaCandidate
from .base import CommandCandidate

logger = logging.getLogger(__name__)


@dataclass
class CrearCandidate:
    """Command to create a new candidate."""
    
    name: str
    email: str
    phone: str
    skills: List[str]
    experience_years: int
    current_position: Optional[str] = None
    current_company: Optional[str] = None
    resume_url: Optional[str] = None
    notes: Optional[str] = None


@ejecutar_comando.register
def handle_crear_candidate(comando: CrearCandidate) -> str:
    """Handle CreateCandidate command."""
    logger.info(f"Executing CreateCandidate command for: {comando.email}")
    
    try:
        _validate_crear_candidate_command(comando)
        
        candidate_status = CandidateStatus("ACTIVE")
        
        fabrica = FabricaCandidate()
        candidate = fabrica.crear_candidate(
            name=comando.name,
            email=comando.email,
            phone=comando.phone,
            skills=comando.skills,
            experience_years=comando.experience_years,
            status=candidate_status,
            current_position=comando.current_position,
            current_company=comando.current_company,
            resume_url=comando.resume_url,
            notes=comando.notes
        )
        
        with UnitOfWork() as uow:
            repo = uow.candidates
            
            # Check if candidate already exists
            existing = repo.obtener_por_email(comando.email)
            if existing:
                raise DomainException(f"Candidate with email {comando.email} already exists")
            
            repo.agregar(candidate)
            uow.commit()
            
            logger.info(f"Candidate created successfully: {candidate.id}")
            return candidate.id
    
    except Exception as e:
        logger.error(f"Failed to create candidate: {str(e)}")
        raise


def _validate_crear_candidate_command(comando: CrearCandidate):
    """Validate CreateCandidate command data."""
    if not comando.name or len(comando.name.strip()) < 2:
        raise DomainException("Name must be at least 2 characters")
    
    if not comando.email or '@' not in comando.email:
        raise DomainException("Valid email is required")
    
    if not comando.phone or len(comando.phone.strip()) < 7:
        raise DomainException("Valid phone number is required")
    
    if not comando.skills or len(comando.skills) == 0:
        raise DomainException("At least one skill is required")
    
    if comando.experience_years < 0 or comando.experience_years > 50:
        raise DomainException("Experience years must be between 0 and 50")
    
    logger.debug("CreateCandidate command validation passed")