"""
Base query classes for Analytics module.
"""

from .....seedwork.aplicacion.queries import Query, QueryHandler, QueryResult
from .....seedwork.dominio.repositorio import Repositorio
from ...dominio.entidades import AnalyticsReport


class QueryAnalytics(Query):
    """Base query for Analytics operations."""
    pass


class QueryHandlerAnalyticsBaseHandler(QueryHandler):
    """Base query handler for Analytics operations."""
    
    def __init__(self, repositorio_analytics: Repositorio):
        self._repositorio_analytics: Repositorio = repositorio_analytics


class AnalyticsQueryResult(QueryResult):
    """Analytics query result."""
    pass