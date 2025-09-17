from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod


@dataclass
class BaseCommand:
    id: Optional[str] = field(default=None)
    timestamp: Optional[datetime] = field(default=None)
    user_id: Optional[str] = field(default=None)
    correlation_id: Optional[str] = field(default=None)
    metadata: Optional[Dict[str, Any]] = field(default=None)

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


# Alias for compatibility
Command = BaseCommand


# Base Command Handler
class BaseCommandHandler(ABC):
    """Base command handler interface."""
    
    @abstractmethod
    async def handle(self, command: Command) -> Any:
        """Handle the command."""
        pass


# Campaign Commands
@dataclass
class CreateCampaign(BaseCommand):
    partner_id: str = field(default_factory=lambda: "")
    campaign_name: str = field(default_factory=lambda: "")
    description: str = field(default_factory=lambda: "")
    campaign_type: str = field(default_factory=lambda: "")
    start_date: datetime = field(default_factory=datetime.utcnow)
    end_date: datetime = field(default_factory=datetime.utcnow)


@dataclass
class UpdateCampaign(BaseCommand):
    campaign_id: str = field(default_factory=lambda: "")
    updated_fields: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ActivateCampaign(BaseCommand):
    campaign_id: str = field(default_factory=lambda: "")


@dataclass
class DeactivateCampaign(BaseCommand):
    campaign_id: str = field(default_factory=lambda: "")
    reason: str = field(default_factory=lambda: "")


# Budget Commands
@dataclass
class AllocateBudget(BaseCommand):
    campaign_id: str = field(default_factory=lambda: "")
    total_budget: float = field(default_factory=lambda: 0.0)
    budget_breakdown: Dict[str, float] = field(default_factory=dict)


@dataclass
class UpdateBudget(BaseCommand):
    campaign_id: str = field(default_factory=lambda: "")
    budget_updates: Dict[str, float] = field(default_factory=dict)


@dataclass
class ReleaseBudget(BaseCommand):
    campaign_id: str = field(default_factory=lambda: "")
    amount: float = field(default_factory=lambda: 0.0)
    reason: str = field(default_factory=lambda: "")


# Targeting Commands
@dataclass
class SetTargetingCriteria(BaseCommand):
    campaign_id: str = field(default_factory=lambda: "")
    criteria: Dict[str, Any] = field(default_factory=dict)
    target_audience: List[str] = field(default_factory=list)


@dataclass
class UpdateTargeting(BaseCommand):
    campaign_id: str = field(default_factory=lambda: "")
    updated_criteria: Dict[str, Any] = field(default_factory=dict)


# Performance Commands
@dataclass
class RecordCampaignMetric(BaseCommand):
    campaign_id: str = field(default_factory=lambda: "")
    metric_name: str = field(default_factory=lambda: "")
    metric_value: float = field(default_factory=lambda: 0.0)
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class UpdatePerformanceGoals(BaseCommand):
    campaign_id: str = field(default_factory=lambda: "")
    goals: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TriggerPerformanceAnalysis(BaseCommand):
    campaign_id: str = field(default_factory=lambda: "")
    analysis_type: str = field(default_factory=lambda: "")
