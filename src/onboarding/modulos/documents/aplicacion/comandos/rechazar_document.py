"""
Command to reject a document.
"""

import logging
from dataclasses import dataclass
from typing import Optional

from onboarding.seedwork.aplicacion.comandos import ejecutar_comando
from onboarding.seedwork.infraestructura.uow import UnitOfWork
from onboarding.seedwork.dominio.excepciones import DomainException
from .base import CommandDocument

logger = logging.getLogger(__name__)


@dataclass
class RechazarDocument:
    """Command to reject a document."""
    
    document_id: str
    rejected_by: str
    rejection_reason: str
    rejection_notes: Optional[str] = None


@ejecutar_comando.register
def handle_rechazar_document(comando: RechazarDocument) -> None:
    """
    Handle RejectDocument command.
    """
    logger.info(f"Executing RejectDocument command for document: {comando.document_id}")
    
    try:
        # Validate input data
        _validate_rechazar_document_command(comando)
        
        # Use Unit of Work to update
        with UnitOfWork() as uow:
            repo = uow.documents
            
            # Get existing document
            document = repo.obtener_por_id(comando.document_id)
            if not document:
                raise DomainException(f"Document not found: {comando.document_id}")
            
            # Reject document
            document.rechazar(
                rejected_by=comando.rejected_by,
                rejection_reason=comando.rejection_reason,
                rejection_notes=comando.rejection_notes
            )
            
            # Save updated document
            repo.actualizar(document)
            
            # Commit transaction
            uow.commit()
            
            logger.info(f"Document rejected successfully: {document.id}")
    
    except Exception as e:
        logger.error(f"Failed to reject document {comando.document_id}: {str(e)}")
        raise


def _validate_rechazar_document_command(comando: RechazarDocument):
    """Validate RejectDocument command data."""
    
    if not comando.document_id:
        raise DomainException("Document ID is required")
    
    if not comando.rejected_by:
        raise DomainException("Rejected by user is required")
    
    if not comando.rejection_reason or len(comando.rejection_reason.strip()) < 3:
        raise DomainException("Rejection reason must be at least 3 characters")
    
    logger.debug("RejectDocument command validation passed")