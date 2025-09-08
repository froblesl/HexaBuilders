"""
Base classes for campaign queries in HexaBuilders.
"""

from abc import ABC
from dataclasses import dataclass

from partner_management.seedwork.aplicacion.queries import Query, QueryHandler, QueryResult


@dataclass
class QueryCampaign(Query, ABC):
    """Base class for all campaign queries."""
    pass


@dataclass
class QueryResultCampaign(QueryResult, ABC):
    """Base class for all campaign query results."""
    pass


class QueryCampaignHandler(QueryHandler, ABC):
    """Base class for all campaign query handlers."""
    pass