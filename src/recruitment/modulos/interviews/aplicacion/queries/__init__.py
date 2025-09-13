"""
Queries module.
"""

from .obtener_interview import ObtenerInterview, RespuestaObtenerInterview
from .obtener_todos_interviews import ObtenerTodosInterviews, RespuestaObtenerTodosInterviews

__all__ = [
    'ObtenerInterview',
    'RespuestaObtenerInterview',
    'ObtenerTodosInterviews',
    'RespuestaObtenerTodosInterviews',
]
