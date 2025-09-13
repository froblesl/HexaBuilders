"""
Queries module for legal compliance management.
"""

from .obtener_compliance import ObtenerCompliance, RespuestaObtenerCompliance
from .obtener_todos_compliance import ObtenerTodosCompliance, RespuestaObtenerTodosCompliance

__all__ = [
    'ObtenerCompliance',
    'RespuestaObtenerCompliance',
    'ObtenerTodosCompliance',
    'RespuestaObtenerTodosCompliance',
]