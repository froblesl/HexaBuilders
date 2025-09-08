"""
Partner application layer initialization.
"""

from .servicios_aplicacion import PartnerApplicationService, get_partner_application_service

# Command imports
from .comandos.crear_partner import CrearPartner
from .comandos.actualizar_partner import ActualizarPartner
from .comandos.activar_partner import ActivarPartner
from .comandos.desactivar_partner import DesactivarPartner

# Query imports
from .queries.obtener_partner import ObtenerPartner
from .queries.obtener_todos_partners import ObtenerTodosPartners
from .queries.obtener_profile_360 import ObtenerProfile360

# Event handler configuration
# TODO: Fix pydispatcher dependency
# from . import handlers

__all__ = [
    # Services
    'PartnerApplicationService',
    'get_partner_application_service',
    
    # Commands
    'CrearPartner',
    'ActualizarPartner', 
    'ActivarPartner',
    'DesactivarPartner',
    
    # Queries
    'ObtenerPartner',
    'ObtenerTodosPartners',
    'ObtenerProfile360',
    
    # Handlers module (commented out due to pydispatcher dependency)
    # 'handlers'
]