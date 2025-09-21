"""
Query to get a document by ID.
"""

import logging
from dataclasses import dataclass
from typing import Optional

from src.onboarding.seedwork.aplicacion.queries import ejecutar_query
from src.onboarding.seedwork.infraestructura.uow import UnitOfWork
from src.onboarding.seedwork.dominio.excepciones import DomainException
from ...infraestructura.dto import DocumentDTO
from .base import QueryDocument, QueryResultDocument

logger = logging.getLogger(__name__)


@dataclass
class ObtenerDocument:
    """Query to get a document by ID."""
    document_id: str


@dataclass
class RespuestaObtenerDocument:
    """Response for GetDocument query."""
    document: Optional[DocumentDTO] = None


@ejecutar_query.register
def handle_obtener_document(query: ObtenerDocument) -> RespuestaObtenerDocument:
    """
    Handle GetDocument query.
    """
    logger.info(f"Executing GetDocument query for document: {query.document_id}")
    
    try:
        # Validate input
        if not query.document_id:
            raise DomainException("Document ID is required")
        
        # Use Unit of Work for read operations
        with UnitOfWork() as uow:
            repo = uow.documents
            
            # Get document
            document = repo.obtener_por_id(query.document_id)
            
            if not document:
                logger.warning(f"Document not found: {query.document_id}")
                return RespuestaObtenerDocument(document=None)
            
            # Convert to DTO
            document_dto = DocumentDTO.from_entity(document)
            
            logger.info(f"Document retrieved successfully: {document.id}")
            return RespuestaObtenerDocument(document=document_dto)
    
    except Exception as e:
        logger.error(f"Failed to get document {query.document_id}: {str(e)}")
        raise