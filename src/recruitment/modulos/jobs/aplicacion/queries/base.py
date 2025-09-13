"""
Base classes for jobs queries.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from recruitment.seedwork.aplicacion.queries import Query, QueryResult

logger = logging.getLogger(__name__)


@dataclass
class QueryJobs(Query):
    """Base query for jobs operations."""
    pass


@dataclass
class QueryResultJobs(QueryResult):
    """Base query result for jobs operations."""
    pass


class QueryHandlerJobs(ABC):
    """Base query handler for jobs operations."""
    
    def __init__(self):
        self._logger = logger
    
    @abstractmethod
    def handle(self, query: QueryJobs) -> QueryResultJobs:
        """Handle the query."""
        pass
    
    def _log_query_start(self, query: QueryJobs):
        """Log query execution start."""
        self._logger.info(f"Starting query execution: {query.__class__.__name__}")
    
    def _log_query_success(self, query: QueryJobs, result: QueryResultJobs):
        """Log successful query execution."""
        self._logger.info(f"Query executed successfully: {query.__class__.__name__}")
    
    def _log_query_error(self, query: QueryJobs, error: Exception):
        """Log query execution error."""
        self._logger.error(f"Query execution failed: {query.__class__.__name__} - {str(error)}")
