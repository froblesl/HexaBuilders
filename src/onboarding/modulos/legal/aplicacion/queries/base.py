"""
Base classes for legal compliance queries.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from onboarding.seedwork.aplicacion.queries import Query, QueryResult

logger = logging.getLogger(__name__)


@dataclass
class QueryCompliance(Query):
    """Base query for legal compliance operations."""
    pass


@dataclass
class QueryResultCompliance(QueryResult):
    """Base query result for legal compliance operations."""
    pass


class QueryHandlerCompliance(ABC):
    """Base query handler for legal compliance operations."""
    
    def __init__(self):
        self._logger = logger
    
    @abstractmethod
    def handle(self, query: QueryCompliance) -> QueryResultCompliance:
        """Handle the query."""
        pass
    
    def _log_query_start(self, query: QueryCompliance):
        """Log query execution start."""
        self._logger.info(f"Starting query execution: {query.__class__.__name__}")
    
    def _log_query_success(self, query: QueryCompliance, result: QueryResultCompliance):
        """Log successful query execution."""
        self._logger.info(f"Query executed successfully: {query.__class__.__name__}")
    
    def _log_query_error(self, query: QueryCompliance, error: Exception):
        """Log query execution error."""
        self._logger.error(f"Query execution failed: {query.__class__.__name__} - {str(error)}")