from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod


@dataclass
class BaseQuery:
    timestamp: Optional[datetime] = field(default=None)
    user_id: Optional[str] = field(default=None)
    correlation_id: Optional[str] = field(default=None)
    metadata: Optional[Dict[str, Any]] = field(default=None)
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


# Alias for compatibility
Query = BaseQuery


@dataclass
class BaseQueryResult:
    success: bool = field(default=True)
    data: Any = field(default=None)
    error_message: Optional[str] = field(default=None)
    metadata: Optional[Dict[str, Any]] = field(default=None)


# Alias for compatibility
QueryResult = BaseQueryResult


# Base Query Handler
class BaseQueryHandler(ABC):
    """Base query handler interface."""
    
    @abstractmethod
    async def handle(self, query: Query) -> QueryResult:
        """Handle the query."""
        pass


# Campaign Queries
@dataclass
class GetCampaign(BaseQuery):
    campaign_id: str = field(default_factory=lambda: "")


@dataclass
class GetAllCampaigns(BaseQuery):
    partner_id: Optional[str] = field(default=None)
    status: Optional[str] = field(default=None)
    campaign_type: Optional[str] = field(default=None)
    limit: int = field(default_factory=lambda: 50)
    offset: int = field(default_factory=lambda: 0)


@dataclass
class GetCampaignsByPartner(BaseQuery):
    partner_id: str = field(default_factory=lambda: "")
    status: Optional[str] = field(default=None)
    limit: int = field(default_factory=lambda: 50)
    offset: int = field(default_factory=lambda: 0)


@dataclass
class SearchCampaigns(BaseQuery):
    search_criteria: Dict[str, Any] = field(default_factory=dict)
    date_from: Optional[datetime] = field(default=None)
    date_to: Optional[datetime] = field(default=None)
    limit: int = field(default_factory=lambda: 50)


# Budget Queries
@dataclass
class GetCampaignBudget(BaseQuery):
    campaign_id: str = field(default_factory=lambda: "")


@dataclass
class GetBudgetUtilization(BaseQuery):
    campaign_id: str = field(default_factory=lambda: "")
    date_from: Optional[datetime] = field(default=None)
    date_to: Optional[datetime] = field(default=None)


@dataclass
class GetBudgetAlerts(BaseQuery):
    partner_id: Optional[str] = field(default=None)
    alert_type: Optional[str] = field(default=None)
    limit: int = field(default_factory=lambda: 50)


# Targeting Queries
@dataclass
class GetTargetingCriteria(BaseQuery):
    campaign_id: str = field(default_factory=lambda: "")


@dataclass
class GetAudienceInsights(BaseQuery):
    campaign_id: str = field(default_factory=lambda: "")
    audience_segment: Optional[str] = field(default=None)


@dataclass
class GetTargetingRecommendations(BaseQuery):
    campaign_id: str = field(default_factory=lambda: "")
    campaign_type: str = field(default_factory=lambda: "")


# Performance Queries
@dataclass
class GetCampaignPerformance(BaseQuery):
    campaign_id: str = field(default_factory=lambda: "")
    date_from: Optional[datetime] = field(default=None)
    date_to: Optional[datetime] = field(default=None)
    metrics: List[str] = field(default_factory=list)


@dataclass
class GetPerformanceMetrics(BaseQuery):
    campaign_id: str = field(default_factory=lambda: "")
    metric_names: List[str] = field(default_factory=list)
    aggregation_level: str = field(default_factory=lambda: "daily")


@dataclass
class GetPerformanceComparison(BaseQuery):
    campaign_ids: List[str] = field(default_factory=list)
    metric_name: str = field(default_factory=lambda: "")
    date_from: Optional[datetime] = field(default=None)
    date_to: Optional[datetime] = field(default=None)


@dataclass
class GetTopPerformingCampaigns(BaseQuery):
    partner_id: Optional[str] = field(default=None)
    metric_name: str = field(default_factory=lambda: "conversion_rate")
    date_from: Optional[datetime] = field(default=None)
    date_to: Optional[datetime] = field(default=None)
    limit: int = field(default_factory=lambda: 10)


# Analytics Queries
@dataclass
class GetCampaignAnalytics(BaseQuery):
    campaign_id: str = field(default_factory=lambda: "")
    analysis_type: str = field(default_factory=lambda: "summary")
    include_predictions: bool = field(default_factory=lambda: False)


@dataclass
class GetPartnerCampaignStats(BaseQuery):
    partner_id: str = field(default_factory=lambda: "")
    date_from: Optional[datetime] = field(default=None)
    date_to: Optional[datetime] = field(default=None)
    include_inactive: bool = field(default_factory=lambda: False)


@dataclass
class GetCampaignTrends(BaseQuery):
    campaign_ids: List[str] = field(default_factory=list)
    metric_names: List[str] = field(default_factory=list)
    time_period: str = field(default_factory=lambda: "30d")
    trend_analysis: bool = field(default_factory=lambda: True)
