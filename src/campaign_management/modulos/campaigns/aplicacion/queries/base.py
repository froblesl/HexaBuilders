"""
Base classes for campaigns queries.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from campaign_management.seedwork.aplicacion.queries import Query, QueryResult

logger = logging.getLogger(__name__)


@dataclass
class QueryCampaigns(Query):
    """Base query for campaigns operations."""
    pass


@dataclass
class QueryResultCampaigns(QueryResult):
    """Base query result for campaigns operations."""
    pass


class QueryHandlerCampaigns(ABC):
    """Base query handler for campaigns operations."""
    
    def __init__(self):
        self._logger = logger
    
    @abstractmethod
    def handle(self, query: QueryCampaigns) -> QueryResultCampaigns:
        """Handle the query."""
        pass
    
    def _log_query_start(self, query: QueryCampaigns):
        """Log query execution start."""
        self._logger.info(f"Starting query execution: {query.__class__.__name__}")
    
    def _log_query_success(self, query: QueryCampaigns, result: QueryResultCampaigns):
        """Log successful query execution."""
        self._logger.info(f"Query executed successfully: {query.__class__.__name__}")
    
    def _log_query_error(self, query: QueryCampaigns, error: Exception):
        """Log query execution error."""
        self._logger.error(f"Query execution failed: {query.__class__.__name__} - {str(error)}")
