"""
Queries module.
"""

from .obtener_campaign import ObtenerCampaign, RespuestaObtenerCampaign
from .obtener_todos_campaigns import ObtenerTodosCampaigns, RespuestaObtenerTodosCampaigns

__all__ = [
    'ObtenerCampaign',
    'RespuestaObtenerCampaign',
    'ObtenerTodosCampaigns',
    'RespuestaObtenerTodosCampaigns',
]
