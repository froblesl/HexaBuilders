"""
Base command classes for Analytics module.
"""

from .....seedwork.aplicacion.comandos import Comando, ComandoHandler
from .....seedwork.dominio.repositorio import Repositorio
from ...dominio.entidades import AnalyticsReport


class ComandoAnalytics(Comando):
    """Base command for Analytics operations."""
    pass


class ComandoAnalyticsHandler(ComandoHandler):
    """Base command handler for Analytics operations."""
    
    def __init__(self, repositorio_analytics: Repositorio):
        self._repositorio_analytics: Repositorio = repositorio_analytics