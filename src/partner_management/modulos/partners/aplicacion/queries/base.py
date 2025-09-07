"""
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from ....seedwork.aplicacion.queries import Query, QueryResult

logger = logging.getLogger(__name__)


@dataclass
class QueryPartner(Query):
    """Base query for partner operations."""
    pass


@dataclass
class QueryResultPartner(QueryResult):
    """Base query result for partner operations."""
    pass


class QueryHandlerPartner(ABC):
    """Base query handler for partner operations."""
    
    def __init__(self):
        self._logger = logger
    
    @abstractmethod
    def handle(self, query: QueryPartner) -> QueryResultPartner:
        """Handle the query."""
        pass
    
    def _log_query_start(self, query: QueryPartner):
        """Log query execution start."""
        self._logger.info(f"Starting query execution: {query.__class__.__name__}")
    
    def _log_query_success(self, query: QueryPartner, result: QueryResultPartner):
        """Log successful query execution."""
        self._logger.info(f"Query executed successfully: {query.__class__.__name__}")
    
    def _log_query_error(self, query: QueryPartner, error: Exception):
        """Log query execution error."""
        self._logger.error(f"Query execution failed: {query.__class__.__name__} - {str(error)}")