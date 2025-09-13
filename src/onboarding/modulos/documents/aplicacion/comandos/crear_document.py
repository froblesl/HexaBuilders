"""
Command to create a new document.
"""

import logging
from dataclasses import dataclass
from typing import Optional

from onboarding.seedwork.aplicacion.comandos import ejecutar_comando
from onboarding.seedwork.infraestructura.uow import UnitOfWork
from onboarding.seedwork.dominio.excepciones import DomainException
from ...dominio.entidades import Document
from ...dominio.objetos_valor import DocumentType, DocumentStatus
from ...infraestructura.fabricas import FabricaDocument
from .base import CommandDocument

logger = logging.getLogger(__name__)


@dataclass
class CrearDocument:
    """Command to create a new document."""
    
    partner_id: str
    document_type: str
    file_name: str
    file_path: str
    file_size: int
    mime_type: str
    uploaded_by: str
    description: Optional[str] = None


@ejecutar_comando.register
def handle_crear_document(comando: CrearDocument) -> str:
    """
    Handle CreateDocument command.
    """
    logger.info(f"Executing CreateDocument command for partner: {comando.partner_id}")
    
    try:
        # Validate input data
        _validate_crear_document_command(comando)
        
        # Create value objects
        document_type = DocumentType(comando.document_type)
        document_status = DocumentStatus("UPLOADED")
        
        # Create document using factory
        fabrica = FabricaDocument()
        document = fabrica.crear_document(
            partner_id=comando.partner_id,
            document_type=document_type,
            file_name=comando.file_name,
            file_path=comando.file_path,
            file_size=comando.file_size,
            mime_type=comando.mime_type,
            status=document_status,
            uploaded_by=comando.uploaded_by,
            description=comando.description
        )
        
        # Use Unit of Work to persist
        with UnitOfWork() as uow:
            repo = uow.documents
            
            # Save document
            repo.agregar(document)
            
            # Commit transaction - this will also publish domain events
            uow.commit()
            
            logger.info(f"Document created successfully: {document.id}")
            return document.id
    
    except Exception as e:
        logger.error(f"Failed to create document: {str(e)}")
        raise


def _validate_crear_document_command(comando: CrearDocument):
    """Validate CreateDocument command data."""
    
    if not comando.partner_id:
        raise DomainException("Partner ID is required")
    
    if not comando.document_type:
        raise DomainException("Document type is required")
    
    valid_types = ['ID_CARD', 'PASSPORT', 'DRIVER_LICENSE', 'UTILITY_BILL', 'BANK_STATEMENT', 'TAX_DOCUMENT', 'OTHER']
    if comando.document_type not in valid_types:
        raise DomainException(f"Document type must be one of: {valid_types}")
    
    if not comando.file_name or len(comando.file_name.strip()) < 1:
        raise DomainException("File name is required")
    
    if not comando.file_path or len(comando.file_path.strip()) < 1:
        raise DomainException("File path is required")
    
    if comando.file_size <= 0:
        raise DomainException("File size must be greater than 0")
    
    if comando.file_size > 50 * 1024 * 1024:  # 50MB limit
        raise DomainException("File size cannot exceed 50MB")
    
    if not comando.mime_type:
        raise DomainException("MIME type is required")
    
    valid_mime_types = ['image/jpeg', 'image/png', 'image/jpg', 'application/pdf', 'image/gif']
    if comando.mime_type not in valid_mime_types:
        raise DomainException(f"MIME type must be one of: {valid_mime_types}")
    
    if not comando.uploaded_by:
        raise DomainException("Uploaded by user is required")
    
    logger.debug("CreateDocument command validation passed")