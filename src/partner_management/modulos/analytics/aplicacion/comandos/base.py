"""
Base command classes for Analytics module.
"""

from partner_management.seedwork.aplicacion.comandos import Command, ComandoHandler
from partner_management.seedwork.dominio.repositorio import Repositorio
from ...dominio.entidades import AnalyticsReport


class ComandoAnalytics(Command):
    """Base command for Analytics operations."""
    pass


class ComandoAnalyticsHandler(ComandoHandler):
    """Base command handler for Analytics operations."""
    
    def __init__(self, repositorio_analytics: Repositorio):
        self._repositorio_analytics: Repositorio = repositorio_analytics