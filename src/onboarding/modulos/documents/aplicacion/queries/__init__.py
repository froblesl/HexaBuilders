"""
Queries module for document management.
"""

from .obtener_document import ObtenerDocument, RespuestaObtenerDocument
from .obtener_todos_documents import ObtenerTodosDocuments, RespuestaObtenerTodosDocuments

__all__ = [
    'ObtenerDocument',
    'RespuestaObtenerDocument',
    'ObtenerTodosDocuments',
    'RespuestaObtenerTodosDocuments',
]