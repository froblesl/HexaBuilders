"""
Command to approve a legal compliance record.
"""

import logging
from dataclasses import dataclass
from typing import Optional

from onboarding.seedwork.aplicacion.comandos import ejecutar_comando
from onboarding.seedwork.infraestructura.uow import UnitOfWork
from onboarding.seedwork.dominio.excepciones import DomainException

logger = logging.getLogger(__name__)


@dataclass
class AprobarCompliance:
    """Command to approve a legal compliance record."""
    
    compliance_id: str
    approved_by: str
    approval_notes: Optional[str] = None


@ejecutar_comando.register
def handle_aprobar_compliance(comando: AprobarCompliance) -> None:
    """Handle ApproveCompliance command."""
    logger.info(f"Executing ApproveCompliance command for compliance: {comando.compliance_id}")
    
    try:
        if not comando.compliance_id or not comando.approved_by:
            raise DomainException("Compliance ID and approved by are required")
        
        with UnitOfWork() as uow:
            repo = uow.compliance
            compliance = repo.obtener_por_id(comando.compliance_id)
            if not compliance:
                raise DomainException(f"Compliance not found: {comando.compliance_id}")
            
            compliance.aprobar(
                approved_by=comando.approved_by,
                approval_notes=comando.approval_notes
            )
            
            repo.actualizar(compliance)
            uow.commit()
            
            logger.info(f"Compliance approved successfully: {compliance.id}")
    
    except Exception as e:
        logger.error(f"Failed to approve compliance {comando.compliance_id}: {str(e)}")
        raise