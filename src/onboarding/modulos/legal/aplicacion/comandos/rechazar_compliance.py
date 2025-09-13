"""
Command to reject a legal compliance record.
"""

import logging
from dataclasses import dataclass
from typing import Optional

from onboarding.seedwork.aplicacion.comandos import ejecutar_comando
from onboarding.seedwork.infraestructura.uow import UnitOfWork
from onboarding.seedwork.dominio.excepciones import DomainException

logger = logging.getLogger(__name__)


@dataclass
class RechazarCompliance:
    """Command to reject a legal compliance record."""
    
    compliance_id: str
    rejected_by: str
    rejection_reason: str
    rejection_notes: Optional[str] = None


@ejecutar_comando.register
def handle_rechazar_compliance(comando: RechazarCompliance) -> None:
    """Handle RejectCompliance command."""
    logger.info(f"Executing RejectCompliance command for compliance: {comando.compliance_id}")
    
    try:
        if not comando.compliance_id or not comando.rejected_by or not comando.rejection_reason:
            raise DomainException("Compliance ID, rejected by, and rejection reason are required")
        
        with UnitOfWork() as uow:
            repo = uow.compliance
            compliance = repo.obtener_por_id(comando.compliance_id)
            if not compliance:
                raise DomainException(f"Compliance not found: {comando.compliance_id}")
            
            compliance.rechazar(
                rejected_by=comando.rejected_by,
                rejection_reason=comando.rejection_reason,
                rejection_notes=comando.rejection_notes
            )
            
            repo.actualizar(compliance)
            uow.commit()
            
            logger.info(f"Compliance rejected successfully: {compliance.id}")
    
    except Exception as e:
        logger.error(f"Failed to reject compliance {comando.compliance_id}: {str(e)}")
        raise