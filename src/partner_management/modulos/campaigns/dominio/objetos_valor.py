"""
Campaign domain value objects for HexaBuilders.
Implements campaign-related value objects following DDD patterns.
"""

import re
from dataclasses import dataclass
from enum import Enum
from typing import Any
from datetime import datetime
from decimal import Decimal

from ....seedwork.dominio.objetos_valor import ObjetoValor
from ....seedwork.dominio.excepciones import DomainException


class CampaignStatus(Enum):
    """Campaign status enumeration."""
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class CampaignType(Enum):
    """Campaign type enumeration."""
    PERFORMANCE = "PERFORMANCE"
    BRAND_AWARENESS = "BRAND_AWARENESS"
    LEAD_GENERATION = "LEAD_GENERATION"
    SALES = "SALES"
    ENGAGEMENT = "ENGAGEMENT"


@dataclass(frozen=True)
class CampaignName(ObjetoValor):
    """Campaign name value object."""
    
    value: str
    
    def __post_init__(self):
        self._validate()
    
    def _validate(self):
        if not self.value or not isinstance(self.value, str):
            raise DomainException("Campaign name cannot be empty")
        
        if len(self.value.strip()) < 3:
            raise DomainException("Campaign name must be at least 3 characters long")
        
        if len(self.value.strip()) > 100:
            raise DomainException("Campaign name cannot exceed 100 characters")
        
        # Only allow letters, numbers, spaces and common punctuation
        if not re.match(r'^[a-zA-ZÀ-ÿ0-9\s\.\-\_\&\,\(\)]+$', self.value.strip()):
            raise DomainException("Campaign name contains invalid characters")


@dataclass(frozen=True)
class CampaignDescription(ObjetoValor):
    """Campaign description value object."""
    
    value: str
    
    def __post_init__(self):
        self._validate()
    
    def _validate(self):
        if not self.value or not isinstance(self.value, str):
            raise DomainException("Campaign description cannot be empty")
        
        if len(self.value.strip()) < 10:
            raise DomainException("Campaign description must be at least 10 characters long")
        
        if len(self.value.strip()) > 1000:
            raise DomainException("Campaign description cannot exceed 1000 characters")


@dataclass(frozen=True)
class CampaignBudget(ObjetoValor):
    """Campaign budget value object."""
    
    amount: Decimal
    currency: str = "USD"
    
    def __post_init__(self):
        self._validate()
    
    def _validate(self):
        if not isinstance(self.amount, (Decimal, int, float)):
            raise DomainException("Budget amount must be a number")
        
        if self.amount < 0:
            raise DomainException("Budget amount cannot be negative")
        
        if self.amount > Decimal('1000000'):
            raise DomainException("Budget amount cannot exceed 1,000,000")
        
        if not self.currency or len(self.currency) != 3:
            raise DomainException("Currency must be a valid 3-letter code")
        
        # Convert to Decimal for precision
        if not isinstance(self.amount, Decimal):
            object.__setattr__(self, 'amount', Decimal(str(self.amount)))


@dataclass(frozen=True)
class CampaignDateRange(ObjetoValor):
    """Campaign date range value object."""
    
    start_date: datetime
    end_date: datetime
    
    def __post_init__(self):
        self._validate()
    
    def _validate(self):
        if not isinstance(self.start_date, datetime):
            raise DomainException("Start date must be a datetime")
        
        if not isinstance(self.end_date, datetime):
            raise DomainException("End date must be a datetime")
        
        if self.start_date >= self.end_date:
            raise DomainException("Start date must be before end date")
        
        # Check minimum campaign duration (1 day)
        duration = self.end_date - self.start_date
        if duration.days < 1:
            raise DomainException("Campaign must run for at least 1 day")
        
        # Check maximum campaign duration (1 year)
        if duration.days > 365:
            raise DomainException("Campaign cannot run for more than 1 year")
    
    def is_active_on(self, date: datetime) -> bool:
        """Check if campaign is active on given date."""
        return self.start_date <= date <= self.end_date
    
    def duration_in_days(self) -> int:
        """Get campaign duration in days."""
        return (self.end_date - self.start_date).days
    
    def is_expired(self) -> bool:
        """Check if campaign has expired."""
        return datetime.now() > self.end_date


@dataclass(frozen=True)
class CampaignMetrics(ObjetoValor):
    """Campaign performance metrics value object."""
    
    impressions: int = 0
    clicks: int = 0
    conversions: int = 0
    spend: Decimal = Decimal('0.00')
    revenue: Decimal = Decimal('0.00')
    
    def __post_init__(self):
        self._validate()
    
    def _validate(self):
        if self.impressions < 0:
            raise DomainException("Impressions cannot be negative")
        
        if self.clicks < 0:
            raise DomainException("Clicks cannot be negative")
        
        if self.conversions < 0:
            raise DomainException("Conversions cannot be negative")
        
        if self.clicks > self.impressions:
            raise DomainException("Clicks cannot exceed impressions")
        
        if self.conversions > self.clicks:
            raise DomainException("Conversions cannot exceed clicks")
        
        if self.spend < 0:
            raise DomainException("Spend cannot be negative")
        
        if self.revenue < 0:
            raise DomainException("Revenue cannot be negative")
        
        # Convert to Decimal for precision
        if not isinstance(self.spend, Decimal):
            object.__setattr__(self, 'spend', Decimal(str(self.spend)))
        
        if not isinstance(self.revenue, Decimal):
            object.__setattr__(self, 'revenue', Decimal(str(self.revenue)))
    
    def click_through_rate(self) -> float:
        """Calculate click-through rate."""
        if self.impressions == 0:
            return 0.0
        return self.clicks / self.impressions
    
    def conversion_rate(self) -> float:
        """Calculate conversion rate."""
        if self.clicks == 0:
            return 0.0
        return self.conversions / self.clicks
    
    def cost_per_click(self) -> Decimal:
        """Calculate cost per click."""
        if self.clicks == 0:
            return Decimal('0.00')
        return self.spend / self.clicks
    
    def cost_per_conversion(self) -> Decimal:
        """Calculate cost per conversion."""
        if self.conversions == 0:
            return Decimal('0.00')
        return self.spend / self.conversions
    
    def return_on_ad_spend(self) -> Decimal:
        """Calculate return on ad spend."""
        if self.spend == 0:
            return Decimal('0.00')
        return self.revenue / self.spend


@dataclass(frozen=True)
class CampaignTargeting(ObjetoValor):
    """Campaign targeting criteria value object."""
    
    countries: list[str] = None
    age_range: tuple[int, int] = None
    interests: list[str] = None
    keywords: list[str] = None
    
    def __post_init__(self):
        if self.countries is None:
            object.__setattr__(self, 'countries', [])
        if self.interests is None:
            object.__setattr__(self, 'interests', [])
        if self.keywords is None:
            object.__setattr__(self, 'keywords', [])
        
        self._validate()
    
    def _validate(self):
        if self.countries and not isinstance(self.countries, list):
            raise DomainException("Countries must be a list")
        
        if self.age_range:
            if not isinstance(self.age_range, tuple) or len(self.age_range) != 2:
                raise DomainException("Age range must be a tuple of (min_age, max_age)")
            
            min_age, max_age = self.age_range
            if not isinstance(min_age, int) or not isinstance(max_age, int):
                raise DomainException("Age range values must be integers")
            
            if min_age < 13 or max_age > 100:
                raise DomainException("Age range must be between 13 and 100")
            
            if min_age >= max_age:
                raise DomainException("Minimum age must be less than maximum age")
        
        if self.interests and not isinstance(self.interests, list):
            raise DomainException("Interests must be a list")
        
        if self.keywords and not isinstance(self.keywords, list):
            raise DomainException("Keywords must be a list")
        
        # Validate list lengths
        if len(self.countries) > 50:
            raise DomainException("Cannot target more than 50 countries")
        
        if len(self.interests) > 20:
            raise DomainException("Cannot target more than 20 interests")
        
        if len(self.keywords) > 100:
            raise DomainException("Cannot target more than 100 keywords")


@dataclass(frozen=True)
class CampaignSettings(ObjetoValor):
    """Campaign settings value object."""
    
    auto_pause_on_budget_exceeded: bool = True
    daily_budget_limit: Decimal = None
    bid_strategy: str = "AUTO"
    placement_types: list[str] = None
    
    def __post_init__(self):
        if self.placement_types is None:
            object.__setattr__(self, 'placement_types', ["FEED", "STORIES"])
        
        self._validate()
    
    def _validate(self):
        if self.daily_budget_limit is not None:
            if not isinstance(self.daily_budget_limit, (Decimal, int, float)):
                raise DomainException("Daily budget limit must be a number")
            
            if self.daily_budget_limit <= 0:
                raise DomainException("Daily budget limit must be positive")
            
            # Convert to Decimal
            if not isinstance(self.daily_budget_limit, Decimal):
                object.__setattr__(self, 'daily_budget_limit', Decimal(str(self.daily_budget_limit)))
        
        valid_bid_strategies = ["AUTO", "MANUAL", "TARGET_CPA", "TARGET_ROAS"]
        if self.bid_strategy not in valid_bid_strategies:
            raise DomainException(f"Bid strategy must be one of: {valid_bid_strategies}")
        
        valid_placements = ["FEED", "STORIES", "REELS", "EXPLORE", "BANNER", "VIDEO"]
        for placement in self.placement_types:
            if placement not in valid_placements:
                raise DomainException(f"Invalid placement type: {placement}. Valid types: {valid_placements}")


@dataclass(frozen=True)
class CampaignApproval(ObjetoValor):
    """Campaign approval value object."""
    
    is_approved: bool = False
    approved_by: str = None
    approved_at: datetime = None
    rejection_reason: str = None
    
    def __post_init__(self):
        self._validate()
    
    def _validate(self):
        if self.is_approved and not self.approved_by:
            raise DomainException("Approved campaigns must have approved_by field")
        
        if self.is_approved and not self.approved_at:
            raise DomainException("Approved campaigns must have approved_at field")
        
        if not self.is_approved and self.approved_by:
            raise DomainException("Non-approved campaigns cannot have approved_by field")
        
        if not self.is_approved and self.approved_at:
            raise DomainException("Non-approved campaigns cannot have approved_at field")
        
        if self.rejection_reason and self.is_approved:
            raise DomainException("Approved campaigns cannot have rejection reason")