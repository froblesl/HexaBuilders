"""
Archive Analytics Report command implementation for HexaBuilders.
"""

import logging
from dataclasses import dataclass
from typing import Optional

from partner_management.seedwork.aplicacion.comandos import ejecutar_comando
from partner_management.seedwork.infraestructura.uow import UnitOfWork
from partner_management.seedwork.dominio.excepciones import DomainException
from .base import CommandAnalytics

logger = logging.getLogger(__name__)


@dataclass
class ArchivarReporte(ComandoAnalytics):
    """Command to archive an analytics report."""
    
    report_id: str
    archived_by: str
    archive_reason: Optional[str] = None


@ejecutar_comando.register
def handle_archivar_reporte(comando: ArchivarReporte) -> str:
    """
    Handle ArchiveReport command.
    """
    logger.info(f"Executing ArchiveReport command for report: {comando.report_id}")
    
    try:
        # Validate input data
        _validate_archivar_reporte_command(comando)
        
        # Use Unit of Work to persist
        with UnitOfWork() as uow:
            repo = uow.analytics
            
            # Get existing report
            report = repo.obtener_por_id(comando.report_id)
            if not report:
                raise DomainException(f"Analytics report with ID {comando.report_id} not found")
            
            # Archive report
            report.archivar(comando.archived_by, comando.archive_reason)
            
            # Save updated report
            repo.actualizar(report)
            
            # Commit transaction - this will also publish domain events
            uow.commit()
            
            logger.info(f"Analytics report archived successfully: {report.id}")
            return report.id
    
    except Exception as e:
        logger.error(f"Failed to archive report: {str(e)}")
        raise


def _validate_archivar_reporte_command(comando: ArchivarReporte):
    """Validate ArchiveReport command data."""
    
    if not comando.report_id:
        raise DomainException("Report ID is required")
    
    if not comando.archived_by or len(comando.archived_by.strip()) < 2:
        raise DomainException("User performing archive is required")
    
    if comando.archive_reason and len(comando.archive_reason.strip()) > 500:
        raise DomainException("Archive reason cannot exceed 500 characters")
    
    logger.debug("ArchiveReport command validation passed")