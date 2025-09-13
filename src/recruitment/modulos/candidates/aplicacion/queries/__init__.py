"""
Queries module for candidate management.
"""

from .obtener_candidate import ObtenerCandidate, RespuestaObtenerCandidate
from .obtener_todos_candidates import ObtenerTodosCandidates, RespuestaObtenerTodosCandidates

__all__ = [
    'ObtenerCandidate',
    'RespuestaObtenerCandidate',
    'ObtenerTodosCandidates',
    'RespuestaObtenerTodosCandidates',
]