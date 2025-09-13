"""
Base classes for matching queries.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from recruitment.seedwork.aplicacion.queries import Query, QueryResult

logger = logging.getLogger(__name__)


@dataclass
class QueryMatching(Query):
    """Base query for matching operations."""
    pass


@dataclass
class QueryResultMatching(QueryResult):
    """Base query result for matching operations."""
    pass


class QueryHandlerMatching(ABC):
    """Base query handler for matching operations."""
    
    def __init__(self):
        self._logger = logger
    
    @abstractmethod
    def handle(self, query: QueryMatching) -> QueryResultMatching:
        """Handle the query."""
        pass
    
    def _log_query_start(self, query: QueryMatching):
        """Log query execution start."""
        self._logger.info(f"Starting query execution: {query.__class__.__name__}")
    
    def _log_query_success(self, query: QueryMatching, result: QueryResultMatching):
        """Log successful query execution."""
        self._logger.info(f"Query executed successfully: {query.__class__.__name__}")
    
    def _log_query_error(self, query: QueryMatching, error: Exception):
        """Log query execution error."""
        self._logger.error(f"Query execution failed: {query.__class__.__name__} - {str(error)}")
