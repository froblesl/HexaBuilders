"""
Command to update an existing document.
"""

import logging
from dataclasses import dataclass
from typing import Optional

from src.onboarding.seedwork.aplicacion.comandos import ejecutar_comando
from src.onboarding.seedwork.infraestructura.uow import UnitOfWork
from src.onboarding.seedwork.dominio.excepciones import DomainException
from ...dominio.objetos_valor import DocumentType
from .base import CommandDocument

logger = logging.getLogger(__name__)


@dataclass
class ActualizarDocument:
    """Command to update an existing document."""
    
    document_id: str
    file_name: Optional[str] = None
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    description: Optional[str] = None
    updated_by: Optional[str] = None


@ejecutar_comando.register
def handle_actualizar_document(comando: ActualizarDocument) -> None:
    """
    Handle UpdateDocument command.
    """
    logger.info(f"Executing UpdateDocument command for document: {comando.document_id}")
    
    try:
        # Validate input data
        _validate_actualizar_document_command(comando)
        
        # Use Unit of Work to update
        with UnitOfWork() as uow:
            repo = uow.documents
            
            # Get existing document
            document = repo.obtener_por_id(comando.document_id)
            if not document:
                raise DomainException(f"Document not found: {comando.document_id}")
            
            # Update document fields
            if comando.file_name:
                document.actualizar_file_name(comando.file_name)
            
            if comando.file_path:
                document.actualizar_file_path(comando.file_path)
                
            if comando.file_size is not None:
                document.actualizar_file_size(comando.file_size)
                
            if comando.mime_type:
                document.actualizar_mime_type(comando.mime_type)
                
            if comando.description is not None:
                document.actualizar_description(comando.description)
                
            if comando.updated_by:
                document.actualizar_metadata(updated_by=comando.updated_by)
            
            # Save updated document
            repo.actualizar(document)
            
            # Commit transaction
            uow.commit()
            
            logger.info(f"Document updated successfully: {document.id}")
    
    except Exception as e:
        logger.error(f"Failed to update document {comando.document_id}: {str(e)}")
        raise


def _validate_actualizar_document_command(comando: ActualizarDocument):
    """Validate UpdateDocument command data."""
    
    if not comando.document_id:
        raise DomainException("Document ID is required")
    
    if comando.file_name is not None and len(comando.file_name.strip()) < 1:
        raise DomainException("File name cannot be empty")
    
    if comando.file_path is not None and len(comando.file_path.strip()) < 1:
        raise DomainException("File path cannot be empty")
    
    if comando.file_size is not None and comando.file_size <= 0:
        raise DomainException("File size must be greater than 0")
    
    if comando.file_size is not None and comando.file_size > 50 * 1024 * 1024:  # 50MB limit
        raise DomainException("File size cannot exceed 50MB")
    
    if comando.mime_type:
        valid_mime_types = ['image/jpeg', 'image/png', 'image/jpg', 'application/pdf', 'image/gif']
        if comando.mime_type not in valid_mime_types:
            raise DomainException(f"MIME type must be one of: {valid_mime_types}")
    
    logger.debug("UpdateDocument command validation passed")