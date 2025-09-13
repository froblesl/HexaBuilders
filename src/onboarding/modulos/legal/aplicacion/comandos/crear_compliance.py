"""
Command to create a new legal compliance record.
"""

import logging
from dataclasses import dataclass
from typing import Optional

from onboarding.seedwork.aplicacion.comandos import ejecutar_comando
from onboarding.seedwork.infraestructura.uow import UnitOfWork
from onboarding.seedwork.dominio.excepciones import DomainException
from ...dominio.entidades import Compliance
from ...dominio.objetos_valor import ComplianceType, ComplianceStatus
from ...infraestructura.fabricas import FabricaCompliance
from .base import CommandCompliance

logger = logging.getLogger(__name__)


@dataclass
class CrearCompliance:
    """Command to create a new legal compliance record."""
    
    partner_id: str
    compliance_type: str
    jurisdiction: str
    requirements: str
    reviewed_by: str
    notes: Optional[str] = None


@ejecutar_comando.register
def handle_crear_compliance(comando: CrearCompliance) -> str:
    """Handle CreateCompliance command."""
    logger.info(f"Executing CreateCompliance command for partner: {comando.partner_id}")
    
    try:
        _validate_crear_compliance_command(comando)
        
        compliance_type = ComplianceType(comando.compliance_type)
        compliance_status = ComplianceStatus("PENDING")
        
        fabrica = FabricaCompliance()
        compliance = fabrica.crear_compliance(
            partner_id=comando.partner_id,
            compliance_type=compliance_type,
            jurisdiction=comando.jurisdiction,
            requirements=comando.requirements,
            status=compliance_status,
            reviewed_by=comando.reviewed_by,
            notes=comando.notes
        )
        
        with UnitOfWork() as uow:
            repo = uow.compliance
            repo.agregar(compliance)
            uow.commit()
            
            logger.info(f"Compliance created successfully: {compliance.id}")
            return compliance.id
    
    except Exception as e:
        logger.error(f"Failed to create compliance: {str(e)}")
        raise


def _validate_crear_compliance_command(comando: CrearCompliance):
    """Validate CreateCompliance command data."""
    if not comando.partner_id:
        raise DomainException("Partner ID is required")
    
    valid_types = ['KYC', 'AML', 'TAX', 'GDPR', 'PCI_DSS', 'SOX', 'OTHER']
    if comando.compliance_type not in valid_types:
        raise DomainException(f"Compliance type must be one of: {valid_types}")
    
    if not comando.jurisdiction or len(comando.jurisdiction.strip()) < 2:
        raise DomainException("Jurisdiction must be at least 2 characters")
    
    if not comando.requirements or len(comando.requirements.strip()) < 10:
        raise DomainException("Requirements must be at least 10 characters")
    
    if not comando.reviewed_by:
        raise DomainException("Reviewed by user is required")
    
    logger.debug("CreateCompliance command validation passed")