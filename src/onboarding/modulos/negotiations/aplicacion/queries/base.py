"""
Base classes for negotiation queries.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from src.onboarding.seedwork.aplicacion.queries import Query, QueryResult

logger = logging.getLogger(__name__)


@dataclass
class QueryNegotiation(Query):
    """Base query for negotiation operations."""
    pass


@dataclass
class QueryResultNegotiation(QueryResult):
    """Base query result for negotiation operations."""
    pass


class QueryHandlerNegotiation(ABC):
    """Base query handler for negotiation operations."""
    
    def __init__(self):
        self._logger = logger
    
    @abstractmethod
    def handle(self, query: QueryNegotiation) -> QueryResultNegotiation:
        """Handle the query."""
        pass
    
    def _log_query_start(self, query: QueryNegotiation):
        """Log query execution start."""
        self._logger.info(f"Starting query execution: {query.__class__.__name__}")
    
    def _log_query_success(self, query: QueryNegotiation, result: QueryResultNegotiation):
        """Log successful query execution."""
        self._logger.info(f"Query executed successfully: {query.__class__.__name__}")
    
    def _log_query_error(self, query: QueryNegotiation, error: Exception):
        """Log query execution error."""
        self._logger.error(f"Query execution failed: {query.__class__.__name__} - {str(error)}")