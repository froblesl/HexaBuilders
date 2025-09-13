"""
Base classes for targeting queries.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from campaign_management.seedwork.aplicacion.queries import Query, QueryResult

logger = logging.getLogger(__name__)


@dataclass
class QueryTargeting(Query):
    """Base query for targeting operations."""
    pass


@dataclass
class QueryResultTargeting(QueryResult):
    """Base query result for targeting operations."""
    pass


class QueryHandlerTargeting(ABC):
    """Base query handler for targeting operations."""
    
    def __init__(self):
        self._logger = logger
    
    @abstractmethod
    def handle(self, query: QueryTargeting) -> QueryResultTargeting:
        """Handle the query."""
        pass
    
    def _log_query_start(self, query: QueryTargeting):
        """Log query execution start."""
        self._logger.info(f"Starting query execution: {query.__class__.__name__}")
    
    def _log_query_success(self, query: QueryTargeting, result: QueryResultTargeting):
        """Log successful query execution."""
        self._logger.info(f"Query executed successfully: {query.__class__.__name__}")
    
    def _log_query_error(self, query: QueryTargeting, error: Exception):
        """Log query execution error."""
        self._logger.error(f"Query execution failed: {query.__class__.__name__} - {str(error)}")
