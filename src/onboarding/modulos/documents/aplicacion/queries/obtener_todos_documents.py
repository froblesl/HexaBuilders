"""
Query to get all documents with optional filtering.
"""

import logging
from dataclasses import dataclass
from typing import List, Optional

from onboarding.seedwork.aplicacion.queries import ejecutar_query
from onboarding.seedwork.infraestructura.uow import UnitOfWork
from ...infraestructura.dto import DocumentDTO
from .base import QueryDocument, QueryResultDocument

logger = logging.getLogger(__name__)


@dataclass
class ObtenerTodosDocuments:
    """Query to get all documents with optional filtering."""
    partner_id: Optional[str] = None
    document_type: Optional[str] = None
    status: Optional[str] = None
    limit: Optional[int] = None
    offset: Optional[int] = None


@dataclass
class RespuestaObtenerTodosDocuments:
    """Response for GetAllDocuments query."""
    documents: List[DocumentDTO]
    total_count: int


@ejecutar_query.register
def handle_obtener_todos_documents(query: ObtenerTodosDocuments) -> RespuestaObtenerTodosDocuments:
    """
    Handle GetAllDocuments query.
    """
    logger.info("Executing GetAllDocuments query")
    
    try:
        # Use Unit of Work for read operations
        with UnitOfWork() as uow:
            repo = uow.documents
            
            # Apply filters based on query parameters
            filters = {}
            if query.partner_id:
                filters['partner_id'] = query.partner_id
            if query.document_type:
                filters['document_type'] = query.document_type
            if query.status:
                filters['status'] = query.status
            
            # Get documents with filters
            documents = repo.obtener_todos(
                filters=filters,
                limit=query.limit,
                offset=query.offset
            )
            
            # Get total count for pagination
            total_count = repo.contar(filters=filters)
            
            # Convert to DTOs
            document_dtos = [DocumentDTO.from_entity(document) for document in documents]
            
            logger.info(f"Retrieved {len(document_dtos)} documents successfully")
            return RespuestaObtenerTodosDocuments(
                documents=document_dtos,
                total_count=total_count
            )
    
    except Exception as e:
        logger.error(f"Failed to get documents: {str(e)}")
        raise