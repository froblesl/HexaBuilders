"""
Commands module for candidate management.
"""

from .crear_candidate import CrearCandidate
from .actualizar_candidate import ActualizarCandidate
from .activar_candidate import ActivarCandidate
from .desactivar_candidate import DesactivarCandidate

__all__ = [
    'CrearCandidate',
    'ActualizarCandidate',
    'ActivarCandidate',
    'DesactivarCandidate',
]