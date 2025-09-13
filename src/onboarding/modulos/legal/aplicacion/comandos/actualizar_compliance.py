"""
Command to update an existing legal compliance record.
"""

import logging
from dataclasses import dataclass
from typing import Optional

from onboarding.seedwork.aplicacion.comandos import ejecutar_comando
from onboarding.seedwork.infraestructura.uow import UnitOfWork
from onboarding.seedwork.dominio.excepciones import DomainException

logger = logging.getLogger(__name__)


@dataclass
class ActualizarCompliance:
    """Command to update an existing legal compliance record."""
    
    compliance_id: str
    requirements: Optional[str] = None
    jurisdiction: Optional[str] = None
    notes: Optional[str] = None
    updated_by: Optional[str] = None


@ejecutar_comando.register
def handle_actualizar_compliance(comando: ActualizarCompliance) -> None:
    """Handle UpdateCompliance command."""
    logger.info(f"Executing UpdateCompliance command for compliance: {comando.compliance_id}")
    
    try:
        if not comando.compliance_id:
            raise DomainException("Compliance ID is required")
        
        with UnitOfWork() as uow:
            repo = uow.compliance
            compliance = repo.obtener_por_id(comando.compliance_id)
            if not compliance:
                raise DomainException(f"Compliance not found: {comando.compliance_id}")
            
            if comando.requirements:
                compliance.actualizar_requirements(comando.requirements)
            if comando.jurisdiction:
                compliance.actualizar_jurisdiction(comando.jurisdiction)
            if comando.notes is not None:
                compliance.actualizar_notes(comando.notes)
            if comando.updated_by:
                compliance.actualizar_metadata(updated_by=comando.updated_by)
            
            repo.actualizar(compliance)
            uow.commit()
            
            logger.info(f"Compliance updated successfully: {compliance.id}")
    
    except Exception as e:
        logger.error(f"Failed to update compliance {comando.compliance_id}: {str(e)}")
        raise