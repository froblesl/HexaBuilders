"""
Base classes for contract queries.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from onboarding.seedwork.aplicacion.queries import Query, QueryResult

logger = logging.getLogger(__name__)


@dataclass
class QueryContract(Query):
    """Base query for contract operations."""
    pass


@dataclass
class QueryResultContract(QueryResult):
    """Base query result for contract operations."""
    pass


class QueryHandlerContract(ABC):
    """Base query handler for contract operations."""
    
    def __init__(self):
        self._logger = logger
    
    @abstractmethod
    def handle(self, query: QueryContract) -> QueryResultContract:
        """Handle the query."""
        pass
    
    def _log_query_start(self, query: QueryContract):
        """Log query execution start."""
        self._logger.info(f"Starting query execution: {query.__class__.__name__}")
    
    def _log_query_success(self, query: QueryContract, result: QueryResultContract):
        """Log successful query execution."""
        self._logger.info(f"Query executed successfully: {query.__class__.__name__}")
    
    def _log_query_error(self, query: QueryContract, error: Exception):
        """Log query execution error."""
        self._logger.error(f"Query execution failed: {query.__class__.__name__} - {str(error)}")