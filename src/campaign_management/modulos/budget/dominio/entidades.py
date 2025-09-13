from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Dict, Any, Optional
from uuid import uuid4
from decimal import Decimal

from campaign_management.seedwork.dominio.entidades import AggregateRoot
from campaign_management.seedwork.dominio.eventos import DomainEvent


class BudgetType(Enum):
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    TOTAL_CAMPAIGN = "TOTAL_CAMPAIGN"
    LIFETIME = "LIFETIME"


class BudgetStatus(Enum):
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    EXHAUSTED = "EXHAUSTED"
    EXCEEDED = "EXCEEDED"
    SUSPENDED = "SUSPENDED"


class SpendingPace(Enum):
    SLOW = "SLOW"
    NORMAL = "NORMAL"
    FAST = "FAST"
    ACCELERATED = "ACCELERATED"


class AlertType(Enum):
    THRESHOLD_WARNING = "THRESHOLD_WARNING"
    THRESHOLD_REACHED = "THRESHOLD_REACHED"
    BUDGET_EXHAUSTED = "BUDGET_EXHAUSTED"
    BUDGET_EXCEEDED = "BUDGET_EXCEEDED"
    PACE_WARNING = "PACE_WARNING"
    UNDERSPENDING = "UNDERSPENDING"


@dataclass
class BudgetAllocation:
    allocation_id: str
    category: str  # e.g., "advertising", "creative", "management"
    allocated_amount: Decimal
    spent_amount: Decimal
    percentage_of_total: float
    is_flexible: bool = True


@dataclass
class BudgetThreshold:
    threshold_id: str
    threshold_percentage: float  # 0.0 to 1.0
    alert_type: AlertType
    is_active: bool = True
    last_triggered: Optional[datetime] = None


@dataclass
class SpendingEntry:
    entry_id: str
    amount: Decimal
    category: str
    description: str
    reference_id: Optional[str]
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BudgetForecast:
    forecast_id: str
    projected_total_spend: Decimal
    projected_end_date: datetime
    confidence_level: float
    assumptions: List[str]
    generated_at: datetime


@dataclass
class BudgetAlert:
    alert_id: str
    alert_type: AlertType
    message: str
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    triggered_at: datetime
    threshold_percentage: Optional[float] = None
    current_spend_percentage: Optional[float] = None
    recommended_actions: List[str] = field(default_factory=list)


# Domain Events
@dataclass
class BudgetCreated(DomainEvent):
    budget_id: str
    campaign_id: str
    total_budget: Decimal
    budget_type: BudgetType
    start_date: datetime
    end_date: Optional[datetime]


@dataclass
class BudgetThresholdTriggered(DomainEvent):
    budget_id: str
    campaign_id: str
    alert_type: AlertType
    threshold_percentage: float
    current_spend: Decimal
    total_budget: Decimal


@dataclass
class BudgetExhausted(DomainEvent):
    budget_id: str
    campaign_id: str
    exhausted_at: datetime
    total_spent: Decimal
    overspend_amount: Decimal


@dataclass
class BudgetPaceAlert(DomainEvent):
    budget_id: str
    campaign_id: str
    current_pace: SpendingPace
    projected_exhaustion_date: datetime
    recommended_action: str


@dataclass
class BudgetAdjusted(DomainEvent):
    budget_id: str
    campaign_id: str
    old_budget: Decimal
    new_budget: Decimal
    adjustment_reason: str
    adjusted_by: str


class Budget(AggregateRoot):
    def __init__(
        self,
        campaign_id: str,
        total_budget: Decimal,
        budget_type: BudgetType,
        start_date: datetime,
        end_date: Optional[datetime] = None
    ):
        super().__init__()
        self.id = str(uuid4())
        self._campaign_id = campaign_id
        self._total_budget = total_budget
        self._budget_type = budget_type
        self._status = BudgetStatus.ACTIVE
        self._start_date = start_date
        self._end_date = end_date
        self._spent_amount = Decimal("0.00")
        self._allocations: List[BudgetAllocation] = []
        self._thresholds: List[BudgetThreshold] = self._get_default_thresholds()
        self._spending_entries: List[SpendingEntry] = []
        self._alerts: List[BudgetAlert] = []
        self._daily_budget_limit: Optional[Decimal] = None
        self._created_at = datetime.utcnow()
        self._updated_at = datetime.utcnow()

    @property
    def campaign_id(self) -> str:
        return self._campaign_id

    @property
    def total_budget(self) -> Decimal:
        return self._total_budget

    @property
    def budget_type(self) -> BudgetType:
        return self._budget_type

    @property
    def status(self) -> BudgetStatus:
        return self._status

    @property
    def spent_amount(self) -> Decimal:
        return self._spent_amount

    @property
    def remaining_budget(self) -> Decimal:
        return max(self._total_budget - self._spent_amount, Decimal("0.00"))

    @property
    def spend_percentage(self) -> float:
        if self._total_budget == 0:
            return 0.0
        return float(self._spent_amount / self._total_budget * 100)

    @property
    def allocations(self) -> List[BudgetAllocation]:
        return self._allocations.copy()

    @property
    def spending_entries(self) -> List[SpendingEntry]:
        return self._spending_entries.copy()

    @property
    def alerts(self) -> List[BudgetAlert]:
        return self._alerts.copy()

    @property
    def is_active(self) -> bool:
        return self._status == BudgetStatus.ACTIVE

    @property
    def is_exhausted(self) -> bool:
        return self._status in [BudgetStatus.EXHAUSTED, BudgetStatus.EXCEEDED]

    @property
    def daily_spend_average(self) -> Decimal:
        if not self._start_date:
            return Decimal("0.00")
        
        days_elapsed = (datetime.utcnow() - self._start_date).days
        if days_elapsed <= 0:
            return Decimal("0.00")
        
        return self._spent_amount / Decimal(str(days_elapsed))

    def set_daily_budget_limit(self, daily_limit: Decimal):
        if daily_limit <= 0:
            raise ValueError("Daily budget limit must be positive")
        
        self._daily_budget_limit = daily_limit
        self._updated_at = datetime.utcnow()

    def add_allocation(self, allocation: BudgetAllocation):
        # Check if total allocations don't exceed budget
        total_allocated = sum(a.allocated_amount for a in self._allocations) + allocation.allocated_amount
        
        if total_allocated > self._total_budget:
            raise ValueError(f"Total allocations ({total_allocated}) exceed budget ({self._total_budget})")
        
        # Check if category already exists
        existing_allocation = next((a for a in self._allocations if a.category == allocation.category), None)
        if existing_allocation:
            raise ValueError(f"Allocation for category '{allocation.category}' already exists")
        
        self._allocations.append(allocation)
        self._updated_at = datetime.utcnow()

    def update_allocation(self, category: str, new_amount: Decimal):
        allocation = next((a for a in self._allocations if a.category == category), None)
        if not allocation:
            raise ValueError(f"No allocation found for category '{category}'")
        
        old_amount = allocation.allocated_amount
        allocation.allocated_amount = new_amount
        
        # Update percentage
        allocation.percentage_of_total = float(new_amount / self._total_budget * 100)
        
        self._updated_at = datetime.utcnow()

    def add_threshold(self, threshold: BudgetThreshold):
        # Remove existing threshold of same type
        self._thresholds = [t for t in self._thresholds if t.alert_type != threshold.alert_type]
        self._thresholds.append(threshold)
        self._updated_at = datetime.utcnow()

    def record_spending(
        self,
        amount: Decimal,
        category: str,
        description: str,
        reference_id: Optional[str] = None,
        metadata: Dict[str, Any] = None
    ) -> SpendingEntry:
        if amount <= 0:
            raise ValueError("Spending amount must be positive")
        
        if self._status not in [BudgetStatus.ACTIVE, BudgetStatus.PAUSED]:
            raise ValueError(f"Cannot record spending in status: {self._status}")

        # Check daily budget limit if set
        if self._daily_budget_limit:
            today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            today_spending = sum(
                entry.amount for entry in self._spending_entries
                if entry.timestamp >= today_start
            )
            
            if today_spending + amount > self._daily_budget_limit:
                raise ValueError(f"Daily spending limit ({self._daily_budget_limit}) would be exceeded")

        # Create spending entry
        entry = SpendingEntry(
            entry_id=str(uuid4()),
            amount=amount,
            category=category,
            description=description,
            reference_id=reference_id,
            timestamp=datetime.utcnow(),
            metadata=metadata or {}
        )

        self._spending_entries.append(entry)
        self._spent_amount += amount
        
        # Update allocation if it exists
        allocation = next((a for a in self._allocations if a.category == category), None)
        if allocation:
            allocation.spent_amount += amount

        # Check thresholds and update status
        self._check_thresholds()
        self._update_status()
        
        self._updated_at = datetime.utcnow()
        
        return entry

    def adjust_budget(self, new_budget: Decimal, reason: str, adjusted_by: str):
        if new_budget <= 0:
            raise ValueError("Budget must be positive")
        
        if new_budget < self._spent_amount:
            raise ValueError(f"New budget ({new_budget}) cannot be less than spent amount ({self._spent_amount})")
        
        old_budget = self._total_budget
        self._total_budget = new_budget
        
        # Update allocation percentages
        for allocation in self._allocations:
            allocation.percentage_of_total = float(allocation.allocated_amount / self._total_budget * 100)
        
        # Update status if budget was exhausted
        if self._status in [BudgetStatus.EXHAUSTED, BudgetStatus.EXCEEDED]:
            self._status = BudgetStatus.ACTIVE
        
        self._updated_at = datetime.utcnow()
        
        self.publicar_evento(BudgetAdjusted(
            event_id=str(uuid4()),
            occurred_on=datetime.utcnow(),
            budget_id=self.id,
            campaign_id=self._campaign_id,
            old_budget=old_budget,
            new_budget=new_budget,
            adjustment_reason=reason,
            adjusted_by=adjusted_by
        ))

    def pause_budget(self):
        if self._status != BudgetStatus.ACTIVE:
            raise ValueError(f"Cannot pause budget in status: {self._status}")
        
        self._status = BudgetStatus.PAUSED
        self._updated_at = datetime.utcnow()

    def resume_budget(self):
        if self._status != BudgetStatus.PAUSED:
            raise ValueError(f"Cannot resume budget in status: {self._status}")
        
        self._status = BudgetStatus.ACTIVE
        self._updated_at = datetime.utcnow()

    def _check_thresholds(self):
        current_percentage = self.spend_percentage / 100
        
        for threshold in self._thresholds:
            if not threshold.is_active:
                continue
                
            if current_percentage >= threshold.threshold_percentage:
                # Check if threshold was already triggered recently (within 1 hour)
                if (threshold.last_triggered and 
                    datetime.utcnow() - threshold.last_triggered < timedelta(hours=1)):
                    continue
                
                threshold.last_triggered = datetime.utcnow()
                
                alert = self._create_threshold_alert(threshold, current_percentage)
                self._alerts.append(alert)
                
                self.publicar_evento(BudgetThresholdTriggered(
                    event_id=str(uuid4()),
                    occurred_on=datetime.utcnow(),
                    budget_id=self.id,
                    campaign_id=self._campaign_id,
                    alert_type=threshold.alert_type,
                    threshold_percentage=threshold.threshold_percentage,
                    current_spend=self._spent_amount,
                    total_budget=self._total_budget
                ))

    def _update_status(self):
        if self._spent_amount >= self._total_budget:
            if self._spent_amount > self._total_budget:
                self._status = BudgetStatus.EXCEEDED
                overspend = self._spent_amount - self._total_budget
                
                self.publicar_evento(BudgetExhausted(
                    event_id=str(uuid4()),
                    occurred_on=datetime.utcnow(),
                    budget_id=self.id,
                    campaign_id=self._campaign_id,
                    exhausted_at=datetime.utcnow(),
                    total_spent=self._spent_amount,
                    overspend_amount=overspend
                ))
            else:
                self._status = BudgetStatus.EXHAUSTED
                
                self.publicar_evento(BudgetExhausted(
                    event_id=str(uuid4()),
                    occurred_on=datetime.utcnow(),
                    budget_id=self.id,
                    campaign_id=self._campaign_id,
                    exhausted_at=datetime.utcnow(),
                    total_spent=self._spent_amount,
                    overspend_amount=Decimal("0.00")
                ))

    def _create_threshold_alert(self, threshold: BudgetThreshold, current_percentage: float) -> BudgetAlert:
        severity_map = {
            AlertType.THRESHOLD_WARNING: "MEDIUM",
            AlertType.THRESHOLD_REACHED: "HIGH",
            AlertType.BUDGET_EXHAUSTED: "CRITICAL",
            AlertType.BUDGET_EXCEEDED: "CRITICAL",
            AlertType.PACE_WARNING: "MEDIUM",
            AlertType.UNDERSPENDING: "LOW"
        }
        
        message_map = {
            AlertType.THRESHOLD_WARNING: f"Budget threshold warning: {threshold.threshold_percentage * 100:.1f}% of budget spent",
            AlertType.THRESHOLD_REACHED: f"Budget threshold reached: {threshold.threshold_percentage * 100:.1f}% of budget spent",
            AlertType.BUDGET_EXHAUSTED: "Budget has been exhausted",
            AlertType.BUDGET_EXCEEDED: "Budget has been exceeded",
            AlertType.PACE_WARNING: "Spending pace is concerning",
            AlertType.UNDERSPENDING: "Campaign is underspending"
        }
        
        recommendations = self._get_threshold_recommendations(threshold.alert_type, current_percentage)
        
        return BudgetAlert(
            alert_id=str(uuid4()),
            alert_type=threshold.alert_type,
            message=message_map.get(threshold.alert_type, "Budget alert triggered"),
            severity=severity_map.get(threshold.alert_type, "MEDIUM"),
            triggered_at=datetime.utcnow(),
            threshold_percentage=threshold.threshold_percentage,
            current_spend_percentage=current_percentage,
            recommended_actions=recommendations
        )

    def _get_threshold_recommendations(self, alert_type: AlertType, current_percentage: float) -> List[str]:
        recommendations = []
        
        if alert_type == AlertType.THRESHOLD_WARNING:
            recommendations.extend([
                "Monitor spending closely",
                "Review campaign performance",
                "Consider budget reallocation"
            ])
        elif alert_type == AlertType.THRESHOLD_REACHED:
            recommendations.extend([
                "Pause non-essential spending",
                "Optimize campaign targeting",
                "Consider increasing budget if ROI is positive"
            ])
        elif alert_type in [AlertType.BUDGET_EXHAUSTED, AlertType.BUDGET_EXCEEDED]:
            recommendations.extend([
                "Pause campaign immediately",
                "Increase budget if performance justifies",
                "Review final campaign metrics"
            ])
        elif alert_type == AlertType.PACE_WARNING:
            recommendations.extend([
                "Reduce daily spending limits",
                "Optimize bid strategies",
                "Review targeting settings"
            ])
        elif alert_type == AlertType.UNDERSPENDING:
            recommendations.extend([
                "Increase daily spending limits",
                "Expand targeting criteria",
                "Review bid competitiveness"
            ])
        
        return recommendations

    def _get_default_thresholds(self) -> List[BudgetThreshold]:
        return [
            BudgetThreshold(
                threshold_id=str(uuid4()),
                threshold_percentage=0.5,
                alert_type=AlertType.THRESHOLD_WARNING
            ),
            BudgetThreshold(
                threshold_id=str(uuid4()),
                threshold_percentage=0.8,
                alert_type=AlertType.THRESHOLD_REACHED
            ),
            BudgetThreshold(
                threshold_id=str(uuid4()),
                threshold_percentage=1.0,
                alert_type=AlertType.BUDGET_EXHAUSTED
            )
        ]

    def get_spending_analysis(self) -> Dict[str, Any]:
        if not self._spending_entries:
            return {
                "total_spent": float(self._spent_amount),
                "remaining_budget": float(self.remaining_budget),
                "spend_percentage": self.spend_percentage,
                "daily_average": 0.0,
                "by_category": {},
                "recent_spending": []
            }

        # Spending by category
        category_spending = {}
        for entry in self._spending_entries:
            if entry.category not in category_spending:
                category_spending[entry.category] = Decimal("0.00")
            category_spending[entry.category] += entry.amount

        # Recent spending (last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_entries = [
            entry for entry in self._spending_entries
            if entry.timestamp >= week_ago
        ]

        return {
            "total_spent": float(self._spent_amount),
            "remaining_budget": float(self.remaining_budget),
            "spend_percentage": self.spend_percentage,
            "daily_average": float(self.daily_spend_average),
            "by_category": {cat: float(amount) for cat, amount in category_spending.items()},
            "recent_spending": [
                {
                    "amount": float(entry.amount),
                    "category": entry.category,
                    "description": entry.description,
                    "timestamp": entry.timestamp.isoformat()
                }
                for entry in sorted(recent_entries, key=lambda x: x.timestamp, reverse=True)[:10]
            ],
            "allocation_utilization": [
                {
                    "category": alloc.category,
                    "allocated": float(alloc.allocated_amount),
                    "spent": float(alloc.spent_amount),
                    "utilization_percentage": (float(alloc.spent_amount) / float(alloc.allocated_amount) * 100) if alloc.allocated_amount > 0 else 0
                }
                for alloc in self._allocations
            ]
        }

    def get_budget_forecast(self, days_ahead: int = 30) -> BudgetForecast:
        if not self._spending_entries or self.daily_spend_average == 0:
            projected_spend = self._spent_amount
            projected_end_date = datetime.utcnow() + timedelta(days=days_ahead)
            confidence = 0.0
        else:
            daily_average = self.daily_spend_average
            projected_additional_spend = daily_average * Decimal(str(days_ahead))
            projected_spend = self._spent_amount + projected_additional_spend
            
            if projected_spend >= self._total_budget:
                days_to_exhaustion = float(self.remaining_budget / daily_average) if daily_average > 0 else days_ahead
                projected_end_date = datetime.utcnow() + timedelta(days=days_to_exhaustion)
            else:
                projected_end_date = datetime.utcnow() + timedelta(days=days_ahead)
            
            # Simple confidence calculation based on spending consistency
            spending_variance = self._calculate_spending_variance()
            confidence = max(0.0, min(1.0, 1.0 - spending_variance))

        return BudgetForecast(
            forecast_id=str(uuid4()),
            projected_total_spend=projected_spend,
            projected_end_date=projected_end_date,
            confidence_level=confidence,
            assumptions=["Based on historical spending patterns", f"Assumes consistent daily spend of {self.daily_spend_average}"],
            generated_at=datetime.utcnow()
        )

    def _calculate_spending_variance(self) -> float:
        if len(self._spending_entries) < 2:
            return 0.0
        
        # Calculate daily spending amounts
        daily_spending = {}
        for entry in self._spending_entries:
            date_key = entry.timestamp.date()
            if date_key not in daily_spending:
                daily_spending[date_key] = Decimal("0.00")
            daily_spending[date_key] += entry.amount

        if len(daily_spending) < 2:
            return 0.0

        amounts = [float(amount) for amount in daily_spending.values()]
        mean = sum(amounts) / len(amounts)
        variance = sum((x - mean) ** 2 for x in amounts) / len(amounts)
        
        # Normalize variance (coefficient of variation)
        return (variance ** 0.5) / mean if mean > 0 else 0.0

    @classmethod
    def from_events(cls, events: List[DomainEvent]) -> 'Budget':
        raise NotImplementedError("Budget event sourcing not implemented")