"""
Base classes for interviews queries.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from recruitment.seedwork.aplicacion.queries import Query, QueryResult

logger = logging.getLogger(__name__)


@dataclass
class QueryInterviews(Query):
    """Base query for interviews operations."""
    pass


@dataclass
class QueryResultInterviews(QueryResult):
    """Base query result for interviews operations."""
    pass


class QueryHandlerInterviews(ABC):
    """Base query handler for interviews operations."""
    
    def __init__(self):
        self._logger = logger
    
    @abstractmethod
    def handle(self, query: QueryInterviews) -> QueryResultInterviews:
        """Handle the query."""
        pass
    
    def _log_query_start(self, query: QueryInterviews):
        """Log query execution start."""
        self._logger.info(f"Starting query execution: {query.__class__.__name__}")
    
    def _log_query_success(self, query: QueryInterviews, result: QueryResultInterviews):
        """Log successful query execution."""
        self._logger.info(f"Query executed successfully: {query.__class__.__name__}")
    
    def _log_query_error(self, query: QueryInterviews, error: Exception):
        """Log query execution error."""
        self._logger.error(f"Query execution failed: {query.__class__.__name__} - {str(error)}")
