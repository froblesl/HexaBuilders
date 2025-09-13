from dataclasses import dataclass, field
from datetime import datetime, date
from typing import List, Dict, Any, Optional
from enum import Enum
from decimal import Decimal

from campaign_management.seedwork.dominio.entidades import BaseEntity, ValueObject, AggregateRoot, DomainEvent
from campaign_management.seedwork.dominio.excepciones import CampaignException, InvalidCampaignDataException


class CampaignStatus(Enum):
    DRAFT = "DRAFT"
    SCHEDULED = "SCHEDULED"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class CampaignType(Enum):
    AWARENESS = "AWARENESS"
    CONVERSION = "CONVERSION"
    ENGAGEMENT = "ENGAGEMENT"
    RETARGETING = "RETARGETING"
    LEAD_GENERATION = "LEAD_GENERATION"


class BudgetType(Enum):
    DAILY = "DAILY"
    TOTAL = "TOTAL"
    MONTHLY = "MONTHLY"


@dataclass
class Budget(ValueObject):
    amount: Decimal
    currency: str = "USD"
    budget_type: BudgetType = BudgetType.TOTAL
    spent: Decimal = Decimal('0')
    remaining: Decimal = field(init=False)
    
    def __post_init__(self):
        super().__post_init__()
        self.remaining = self.amount - self.spent
    
    def _validate(self):
        if self.amount <= 0:
            raise InvalidCampaignDataException("Budget amount must be positive")
        
        if self.spent < 0:
            raise InvalidCampaignDataException("Spent amount cannot be negative")
        
        if self.spent > self.amount:
            raise InvalidCampaignDataException("Spent amount cannot exceed budget")


@dataclass
class Targeting(ValueObject):
    demographics: Dict[str, Any] = field(default_factory=dict)
    interests: List[str] = field(default_factory=list)
    behaviors: List[str] = field(default_factory=list)
    locations: List[str] = field(default_factory=list)
    devices: List[str] = field(default_factory=list)
    age_range: Optional[Dict[str, int]] = None
    languages: List[str] = field(default_factory=list)
    
    def _validate(self):
        if self.age_range:
            if 'min' in self.age_range and 'max' in self.age_range:
                if self.age_range['min'] > self.age_range['max']:
                    raise InvalidCampaignDataException("Invalid age range")


@dataclass
class CreativeAsset(ValueObject):
    asset_id: str
    asset_type: str  # "image", "video", "text", "banner"
    url: str
    title: str
    description: Optional[str] = None
    dimensions: Optional[Dict[str, int]] = None
    file_size: Optional[int] = None
    duration: Optional[int] = None  # For videos
    
    def _validate(self):
        if not self.asset_id or not self.asset_type or not self.url:
            raise InvalidCampaignDataException("Asset ID, type, and URL are required")


@dataclass
class PerformanceMetrics(ValueObject):
    impressions: int = 0
    clicks: int = 0
    conversions: int = 0
    cost: Decimal = Decimal('0')
    ctr: float = 0.0  # Click-through rate
    cpc: Decimal = Decimal('0')  # Cost per click
    cpm: Decimal = Decimal('0')  # Cost per mille
    conversion_rate: float = 0.0
    roas: float = 0.0  # Return on ad spend
    
    def _validate(self):
        if any(val < 0 for val in [self.impressions, self.clicks, self.conversions]):
            raise InvalidCampaignDataException("Metrics cannot be negative")
    
    def calculate_derived_metrics(self):
        """Calculate CTR, CPC, CPM, and conversion rate"""
        # CTR = (clicks / impressions) * 100
        self.ctr = (self.clicks / self.impressions * 100) if self.impressions > 0 else 0.0
        
        # CPC = cost / clicks
        self.cpc = self.cost / self.clicks if self.clicks > 0 else Decimal('0')
        
        # CPM = (cost / impressions) * 1000
        self.cpm = (self.cost / self.impressions * 1000) if self.impressions > 0 else Decimal('0')
        
        # Conversion Rate = (conversions / clicks) * 100
        self.conversion_rate = (self.conversions / self.clicks * 100) if self.clicks > 0 else 0.0


# Domain Events
@dataclass
class CampaignCreated(DomainEvent):
    campaign_id: str
    partner_id: str
    name: str
    campaign_type: str
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "campaign_id": self.campaign_id,
            "partner_id": self.partner_id,
            "name": self.name,
            "campaign_type": self.campaign_type
        })
        return data


@dataclass
class CampaignLaunched(DomainEvent):
    campaign_id: str
    partner_id: str
    launch_date: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "campaign_id": self.campaign_id,
            "partner_id": self.partner_id,
            "launch_date": self.launch_date.isoformat()
        })
        return data


@dataclass
class CampaignPaused(DomainEvent):
    campaign_id: str
    reason: str
    paused_by: str
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "campaign_id": self.campaign_id,
            "reason": self.reason,
            "paused_by": self.paused_by
        })
        return data


@dataclass
class CampaignCompleted(DomainEvent):
    campaign_id: str
    partner_id: str
    completion_date: datetime
    final_metrics: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "campaign_id": self.campaign_id,
            "partner_id": self.partner_id,
            "completion_date": self.completion_date.isoformat(),
            "final_metrics": self.final_metrics
        })
        return data


@dataclass
class BudgetAlert(DomainEvent):
    campaign_id: str
    partner_id: str
    alert_type: str  # "threshold", "exhausted", "overspend"
    current_spend: Decimal
    budget_limit: Decimal
    threshold_percentage: float
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "campaign_id": self.campaign_id,
            "partner_id": self.partner_id,
            "alert_type": self.alert_type,
            "current_spend": str(self.current_spend),
            "budget_limit": str(self.budget_limit),
            "threshold_percentage": self.threshold_percentage
        })
        return data


class Campaign(AggregateRoot):
    def __init__(self, campaign_id: str = None):
        super().__init__()
        if campaign_id:
            self._id = campaign_id
        self._partner_id: Optional[str] = None
        self._name: str = ""
        self._description: str = ""
        self._campaign_type: Optional[CampaignType] = None
        self._status: CampaignStatus = CampaignStatus.DRAFT
        self._budget: Optional[Budget] = None
        self._targeting: Optional[Targeting] = None
        self._creative_assets: List[CreativeAsset] = []
        self._start_date: Optional[datetime] = None
        self._end_date: Optional[datetime] = None
        self._performance_metrics: PerformanceMetrics = PerformanceMetrics()
        self._created_by: str = ""
        self._tags: List[str] = []
        self._optimization_settings: Dict[str, Any] = {}
        self._daily_metrics: List[Dict[str, Any]] = []
        self._alerts_enabled: bool = True
        self._budget_alert_thresholds: List[float] = [50.0, 80.0, 95.0]  # Percentage thresholds
    
    @property
    def partner_id(self) -> str:
        return self._partner_id
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def status(self) -> CampaignStatus:
        return self._status
    
    @property
    def budget(self) -> Budget:
        return self._budget
    
    @property
    def performance_metrics(self) -> PerformanceMetrics:
        return self._performance_metrics
    
    @property
    def is_active(self) -> bool:
        return self._status == CampaignStatus.ACTIVE
    
    @property
    def is_completed(self) -> bool:
        return self._status in [CampaignStatus.COMPLETED, CampaignStatus.CANCELLED]
    
    @classmethod
    def create_campaign(
        cls,
        partner_id: str,
        name: str,
        description: str,
        campaign_type: CampaignType,
        budget: Budget,
        created_by: str
    ) -> 'Campaign':
        """Create a new campaign"""
        campaign = cls()
        campaign._partner_id = partner_id
        campaign._name = name
        campaign._description = description
        campaign._campaign_type = campaign_type
        campaign._budget = budget
        campaign._created_by = created_by
        campaign._created_at = datetime.utcnow()
        campaign._updated_at = campaign._created_at
        
        campaign.publicar_evento(
            CampaignCreated(
                campaign_id=campaign.id,
                partner_id=partner_id,
                name=name,
                campaign_type=campaign_type.value
            )
        )
        
        campaign._increment_version()
        return campaign
    
    def update_targeting(self, targeting: Targeting):
        """Update campaign targeting"""
        if self._status in [CampaignStatus.COMPLETED, CampaignStatus.CANCELLED]:
            raise CampaignException(f"Cannot update targeting for {self._status.value} campaign")
        
        self._targeting = targeting
        self._updated_at = datetime.utcnow()
        self._increment_version()
    
    def add_creative_asset(self, asset: CreativeAsset):
        """Add a creative asset to the campaign"""
        if self._status in [CampaignStatus.COMPLETED, CampaignStatus.CANCELLED]:
            raise CampaignException(f"Cannot add assets to {self._status.value} campaign")
        
        # Remove existing asset with same ID
        self._creative_assets = [a for a in self._creative_assets if a.asset_id != asset.asset_id]
        self._creative_assets.append(asset)
        self._updated_at = datetime.utcnow()
        self._increment_version()
    
    def schedule_campaign(self, start_date: datetime, end_date: datetime):
        """Schedule the campaign"""
        if self._status != CampaignStatus.DRAFT:
            raise CampaignException(f"Cannot schedule campaign in {self._status.value} status")
        
        if start_date >= end_date:
            raise InvalidCampaignDataException("Start date must be before end date")
        
        if start_date < datetime.utcnow():
            raise InvalidCampaignDataException("Start date cannot be in the past")
        
        self._start_date = start_date
        self._end_date = end_date
        self._status = CampaignStatus.SCHEDULED
        self._updated_at = datetime.utcnow()
        self._increment_version()
    
    def launch_campaign(self):
        """Launch the campaign"""
        if self._status not in [CampaignStatus.DRAFT, CampaignStatus.SCHEDULED]:
            raise CampaignException(f"Cannot launch campaign in {self._status.value} status")
        
        if not self._budget:
            raise CampaignException("Budget is required to launch campaign")
        
        if not self._targeting:
            raise CampaignException("Targeting is required to launch campaign")
        
        if not self._creative_assets:
            raise CampaignException("At least one creative asset is required")
        
        self._status = CampaignStatus.ACTIVE
        if not self._start_date:
            self._start_date = datetime.utcnow()
        
        self.publicar_evento(
            CampaignLaunched(
                campaign_id=self.id,
                partner_id=self._partner_id,
                launch_date=self._start_date
            )
        )
        
        self._updated_at = datetime.utcnow()
        self._increment_version()
    
    def pause_campaign(self, reason: str, paused_by: str):
        """Pause the campaign"""
        if self._status != CampaignStatus.ACTIVE:
            raise CampaignException(f"Cannot pause campaign in {self._status.value} status")
        
        self._status = CampaignStatus.PAUSED
        
        self.publicar_evento(
            CampaignPaused(
                campaign_id=self.id,
                reason=reason,
                paused_by=paused_by
            )
        )
        
        self._updated_at = datetime.utcnow()
        self._increment_version()
    
    def resume_campaign(self):
        """Resume paused campaign"""
        if self._status != CampaignStatus.PAUSED:
            raise CampaignException(f"Cannot resume campaign in {self._status.value} status")
        
        # Check if campaign should still be active
        if self._end_date and datetime.utcnow() > self._end_date:
            self.complete_campaign()
            return
        
        self._status = CampaignStatus.ACTIVE
        self._updated_at = datetime.utcnow()
        self._increment_version()
    
    def complete_campaign(self):
        """Complete the campaign"""
        if self._status not in [CampaignStatus.ACTIVE, CampaignStatus.PAUSED]:
            raise CampaignException(f"Cannot complete campaign in {self._status.value} status")
        
        self._status = CampaignStatus.COMPLETED
        completion_date = datetime.utcnow()
        
        # Calculate final metrics
        self._performance_metrics.calculate_derived_metrics()
        
        self.publicar_evento(
            CampaignCompleted(
                campaign_id=self.id,
                partner_id=self._partner_id,
                completion_date=completion_date,
                final_metrics={
                    "impressions": self._performance_metrics.impressions,
                    "clicks": self._performance_metrics.clicks,
                    "conversions": self._performance_metrics.conversions,
                    "cost": str(self._performance_metrics.cost),
                    "ctr": self._performance_metrics.ctr,
                    "cpc": str(self._performance_metrics.cpc),
                    "conversion_rate": self._performance_metrics.conversion_rate
                }
            )
        )
        
        self._updated_at = completion_date
        self._increment_version()
    
    def cancel_campaign(self, reason: str):
        """Cancel the campaign"""
        if self._status in [CampaignStatus.COMPLETED, CampaignStatus.CANCELLED]:
            raise CampaignException(f"Cannot cancel campaign in {self._status.value} status")
        
        self._status = CampaignStatus.CANCELLED
        self._updated_at = datetime.utcnow()
        self._increment_version()
    
    def update_metrics(self, new_metrics: Dict[str, Any]):
        """Update campaign performance metrics"""
        if not self.is_active:
            raise CampaignException("Cannot update metrics for inactive campaign")
        
        # Update metrics
        for key, value in new_metrics.items():
            if hasattr(self._performance_metrics, key):
                setattr(self._performance_metrics, key, value)
        
        # Recalculate derived metrics
        self._performance_metrics.calculate_derived_metrics()
        
        # Update budget spent
        if 'cost' in new_metrics:
            new_cost = Decimal(str(new_metrics['cost']))
            self._budget.spent = new_cost
            self._budget.remaining = self._budget.amount - self._budget.spent
            
            # Check for budget alerts
            self._check_budget_alerts()
        
        # Store daily snapshot
        self._daily_metrics.append({
            'date': datetime.utcnow().date().isoformat(),
            'metrics': new_metrics,
            'timestamp': datetime.utcnow().isoformat()
        })
        
        self._updated_at = datetime.utcnow()
        self._increment_version()
    
    def _check_budget_alerts(self):
        """Check if budget alerts should be triggered"""
        if not self._alerts_enabled or not self._budget:
            return
        
        spend_percentage = (self._budget.spent / self._budget.amount) * 100
        
        for threshold in self._budget_alert_thresholds:
            if spend_percentage >= threshold:
                alert_type = "exhausted" if spend_percentage >= 100 else "threshold"
                
                self.publicar_evento(
                    BudgetAlert(
                        campaign_id=self.id,
                        partner_id=self._partner_id,
                        alert_type=alert_type,
                        current_spend=self._budget.spent,
                        budget_limit=self._budget.amount,
                        threshold_percentage=threshold
                    )
                )
                break
    
    def get_daily_performance(self, date_range: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """Get daily performance metrics"""
        if not date_range:
            return self._daily_metrics
        
        start_date, end_date = date_range
        return [
            metric for metric in self._daily_metrics
            if start_date <= datetime.fromisoformat(metric['timestamp']).date() <= end_date
        ]
    
    def calculate_roi(self, revenue: Decimal) -> float:
        """Calculate return on investment"""
        if self._performance_metrics.cost > 0:
            return float((revenue - self._performance_metrics.cost) / self._performance_metrics.cost * 100)
        return 0.0
    
    @classmethod
    def from_events(cls, events: List[DomainEvent]) -> 'Campaign':
        """Reconstruct campaign from events"""
        campaign = cls()
        
        for event in events:
            if isinstance(event, CampaignCreated):
                campaign._partner_id = event.partner_id
                campaign._name = event.name
                campaign._campaign_type = CampaignType(event.campaign_type)
                campaign._created_at = event.timestamp
                campaign._updated_at = event.timestamp
            
            elif isinstance(event, CampaignLaunched):
                campaign._status = CampaignStatus.ACTIVE
                campaign._start_date = event.launch_date
                campaign._updated_at = event.timestamp
            
            elif isinstance(event, CampaignPaused):
                campaign._status = CampaignStatus.PAUSED
                campaign._updated_at = event.timestamp
            
            elif isinstance(event, CampaignCompleted):
                campaign._status = CampaignStatus.COMPLETED
                campaign._updated_at = event.completion_date
            
            campaign._increment_version()
        
        return campaign