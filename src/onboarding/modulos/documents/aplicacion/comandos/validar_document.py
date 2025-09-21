"""
Command to validate a document.
"""

import logging
from dataclasses import dataclass
from typing import Optional

from src.onboarding.seedwork.aplicacion.comandos import ejecutar_comando
from src.onboarding.seedwork.infraestructura.uow import UnitOfWork
from src.onboarding.seedwork.dominio.excepciones import DomainException
from .base import CommandDocument

logger = logging.getLogger(__name__)


@dataclass
class ValidarDocument:
    """Command to validate a document."""
    
    document_id: str
    validated_by: str
    validation_notes: Optional[str] = None


@ejecutar_comando.register
def handle_validar_document(comando: ValidarDocument) -> None:
    """
    Handle ValidateDocument command.
    """
    logger.info(f"Executing ValidateDocument command for document: {comando.document_id}")
    
    try:
        # Validate input data
        _validate_validar_document_command(comando)
        
        # Use Unit of Work to update
        with UnitOfWork() as uow:
            repo = uow.documents
            
            # Get existing document
            document = repo.obtener_por_id(comando.document_id)
            if not document:
                raise DomainException(f"Document not found: {comando.document_id}")
            
            # Validate document
            document.validar(
                validated_by=comando.validated_by,
                validation_notes=comando.validation_notes
            )
            
            # Save updated document
            repo.actualizar(document)
            
            # Commit transaction
            uow.commit()
            
            logger.info(f"Document validated successfully: {document.id}")
    
    except Exception as e:
        logger.error(f"Failed to validate document {comando.document_id}: {str(e)}")
        raise


def _validate_validar_document_command(comando: ValidarDocument):
    """Validate ValidateDocument command data."""
    
    if not comando.document_id:
        raise DomainException("Document ID is required")
    
    if not comando.validated_by:
        raise DomainException("Validated by user is required")
    
    logger.debug("ValidateDocument command validation passed")