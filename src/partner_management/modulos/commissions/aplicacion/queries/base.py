"""
Base query classes for Commission module.
"""

from partner_management.seedwork.aplicacion.queries import Query, QueryHandler, QueryResult
from partner_management.seedwork.dominio.repositorio import Repositorio
from ...dominio.entidades import Commission


class QueryCommission(Query):
    """Base query for Commission operations."""
    pass


class QueryHandlerCommissionBaseHandler(QueryHandler):
    """Base query handler for Commission operations."""
    
    def __init__(self, repositorio_commission: Repositorio):
        self._repositorio_commission: Repositorio = repositorio_commission


class CommissionQueryResult(QueryResult):
    """Commission query result."""
    pass