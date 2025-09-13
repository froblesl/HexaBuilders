"""
Base classes for budget queries.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from campaign_management.seedwork.aplicacion.queries import Query, QueryResult

logger = logging.getLogger(__name__)


@dataclass
class QueryBudget(Query):
    """Base query for budget operations."""
    pass


@dataclass
class QueryResultBudget(QueryResult):
    """Base query result for budget operations."""
    pass


class QueryHandlerBudget(ABC):
    """Base query handler for budget operations."""
    
    def __init__(self):
        self._logger = logger
    
    @abstractmethod
    def handle(self, query: QueryBudget) -> QueryResultBudget:
        """Handle the query."""
        pass
    
    def _log_query_start(self, query: QueryBudget):
        """Log query execution start."""
        self._logger.info(f"Starting query execution: {query.__class__.__name__}")
    
    def _log_query_success(self, query: QueryBudget, result: QueryResultBudget):
        """Log successful query execution."""
        self._logger.info(f"Query executed successfully: {query.__class__.__name__}")
    
    def _log_query_error(self, query: QueryBudget, error: Exception):
        """Log query execution error."""
        self._logger.error(f"Query execution failed: {query.__class__.__name__} - {str(error)}")
