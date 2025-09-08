"""
Partner queries module initialization.
"""

from .obtener_partner import ObtenerPartner
from .obtener_todos_partners import ObtenerTodosPartners  
from .obtener_profile_360 import ObtenerProfile360

__all__ = [
    'ObtenerPartner',
    'ObtenerTodosPartners',
    'ObtenerProfile360'
]