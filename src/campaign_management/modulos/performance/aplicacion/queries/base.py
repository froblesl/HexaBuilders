"""
Base classes for performance queries.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from campaign_management.seedwork.aplicacion.queries import Query, QueryResult

logger = logging.getLogger(__name__)


@dataclass
class QueryPerformance(Query):
    """Base query for performance operations."""
    pass


@dataclass
class QueryResultPerformance(QueryResult):
    """Base query result for performance operations."""
    pass


class QueryHandlerPerformance(ABC):
    """Base query handler for performance operations."""
    
    def __init__(self):
        self._logger = logger
    
    @abstractmethod
    def handle(self, query: QueryPerformance) -> QueryResultPerformance:
        """Handle the query."""
        pass
    
    def _log_query_start(self, query: QueryPerformance):
        """Log query execution start."""
        self._logger.info(f"Starting query execution: {query.__class__.__name__}")
    
    def _log_query_success(self, query: QueryPerformance, result: QueryResultPerformance):
        """Log successful query execution."""
        self._logger.info(f"Query executed successfully: {query.__class__.__name__}")
    
    def _log_query_error(self, query: QueryPerformance, error: Exception):
        """Log query execution error."""
        self._logger.error(f"Query execution failed: {query.__class__.__name__} - {str(error)}")
