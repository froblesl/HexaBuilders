"""
Base classes for document queries.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from onboarding.seedwork.aplicacion.queries import Query, QueryResult

logger = logging.getLogger(__name__)


@dataclass
class QueryDocument(Query):
    """Base query for document operations."""
    pass


@dataclass
class QueryResultDocument(QueryResult):
    """Base query result for document operations."""
    pass


class QueryHandlerDocument(ABC):
    """Base query handler for document operations."""
    
    def __init__(self):
        self._logger = logger
    
    @abstractmethod
    def handle(self, query: QueryDocument) -> QueryResultDocument:
        """Handle the query."""
        pass
    
    def _log_query_start(self, query: QueryDocument):
        """Log query execution start."""
        self._logger.info(f"Starting query execution: {query.__class__.__name__}")
    
    def _log_query_success(self, query: QueryDocument, result: QueryResultDocument):
        """Log successful query execution."""
        self._logger.info(f"Query executed successfully: {query.__class__.__name__}")
    
    def _log_query_error(self, query: QueryDocument, error: Exception):
        """Log query execution error."""
        self._logger.error(f"Query execution failed: {query.__class__.__name__} - {str(error)}")