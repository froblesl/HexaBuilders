"""
Base classes for candidate queries.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from recruitment.seedwork.aplicacion.queries import Query, QueryResult

logger = logging.getLogger(__name__)


@dataclass
class QueryCandidate(Query):
    """Base query for candidate operations."""
    pass


@dataclass
class QueryResultCandidate(QueryResult):
    """Base query result for candidate operations."""
    pass


class QueryHandlerCandidate(ABC):
    """Base query handler for candidate operations."""
    
    def __init__(self):
        self._logger = logger
    
    @abstractmethod
    def handle(self, query: QueryCandidate) -> QueryResultCandidate:
        """Handle the query."""
        pass
    
    def _log_query_start(self, query: QueryCandidate):
        """Log query execution start."""
        self._logger.info(f"Starting query execution: {query.__class__.__name__}")
    
    def _log_query_success(self, query: QueryCandidate, result: QueryResultCandidate):
        """Log successful query execution."""
        self._logger.info(f"Query executed successfully: {query.__class__.__name__}")
    
    def _log_query_error(self, query: QueryCandidate, error: Exception):
        """Log query execution error."""
        self._logger.error(f"Query execution failed: {query.__class__.__name__} - {str(error)}")