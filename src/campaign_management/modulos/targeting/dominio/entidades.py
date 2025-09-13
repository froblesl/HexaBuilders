from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Dict, Any, Optional, Set
from uuid import uuid4

from campaign_management.seedwork.dominio.entidades import AggregateRoot
from campaign_management.seedwork.dominio.eventos import DomainEvent


class TargetingType(Enum):
    DEMOGRAPHIC = "DEMOGRAPHIC"
    GEOGRAPHIC = "GEOGRAPHIC"
    BEHAVIORAL = "BEHAVIORAL"
    INTEREST_BASED = "INTEREST_BASED"
    LOOKALIKE = "LOOKALIKE"
    CUSTOM_AUDIENCE = "CUSTOM_AUDIENCE"
    RETARGETING = "RETARGETING"
    CONTEXTUAL = "CONTEXTUAL"


class AudienceSize(Enum):
    VERY_NARROW = "VERY_NARROW"    # < 10K
    NARROW = "NARROW"              # 10K - 100K
    MODERATE = "MODERATE"          # 100K - 1M
    BROAD = "BROAD"                # 1M - 10M
    VERY_BROAD = "VERY_BROAD"      # > 10M


class TargetingStatus(Enum):
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    LEARNING = "LEARNING"
    OPTIMIZING = "OPTIMIZING"
    UNDERPERFORMING = "UNDERPERFORMING"
    EXHAUSTED = "EXHAUSTED"


class OptimizationGoal(Enum):
    REACH = "REACH"
    ENGAGEMENT = "ENGAGEMENT"
    CONVERSIONS = "CONVERSIONS"
    BRAND_AWARENESS = "BRAND_AWARENESS"
    TRAFFIC = "TRAFFIC"
    LEAD_GENERATION = "LEAD_GENERATION"


@dataclass
class DemographicCriteria:
    age_min: Optional[int] = None
    age_max: Optional[int] = None
    genders: List[str] = field(default_factory=list)  # "MALE", "FEMALE", "ALL"
    income_levels: List[str] = field(default_factory=list)  # "LOW", "MEDIUM", "HIGH"
    education_levels: List[str] = field(default_factory=list)
    marital_status: List[str] = field(default_factory=list)
    parental_status: List[str] = field(default_factory=list)


@dataclass
class GeographicCriteria:
    countries: List[str] = field(default_factory=list)
    regions: List[str] = field(default_factory=list)
    cities: List[str] = field(default_factory=list)
    postal_codes: List[str] = field(default_factory=list)
    radius_targeting: Optional[Dict[str, Any]] = None  # {"lat": 40.7128, "lng": -74.0060, "radius_km": 25}
    location_types: List[str] = field(default_factory=list)  # "HOME", "WORK", "TRAVEL"


@dataclass
class BehavioralCriteria:
    purchase_behaviors: List[str] = field(default_factory=list)
    digital_activities: List[str] = field(default_factory=list)
    device_usage: List[str] = field(default_factory=list)
    travel_patterns: List[str] = field(default_factory=list)
    life_events: List[str] = field(default_factory=list)


@dataclass
class InterestCriteria:
    interests: List[str] = field(default_factory=list)
    hobbies: List[str] = field(default_factory=list)
    brands_affinity: List[str] = field(default_factory=list)
    industries: List[str] = field(default_factory=list)
    topics: List[str] = field(default_factory=list)


@dataclass
class CustomAudience:
    audience_id: str
    name: str
    description: str
    source_type: str  # "CUSTOMER_LIST", "WEBSITE_TRAFFIC", "APP_ACTIVITY", "ENGAGEMENT"
    size_estimate: int
    last_updated: datetime
    match_rate: Optional[float] = None  # 0.0 to 1.0


@dataclass
class LookalikeAudience:
    audience_id: str
    name: str
    source_audience_id: str
    similarity_percentage: int  # 1-10, where 1 is most similar
    size_estimate: int
    countries: List[str]
    created_at: datetime


@dataclass
class TargetingPerformance:
    impressions: int = 0
    clicks: int = 0
    conversions: int = 0
    cost: float = 0.0
    ctr: float = 0.0
    cvr: float = 0.0
    cpc: float = 0.0
    cpa: float = 0.0


# Domain Events
@dataclass
class TargetingCreated(DomainEvent):
    targeting_id: str
    campaign_id: str
    targeting_types: List[TargetingType]
    estimated_audience_size: int


@dataclass
class TargetingOptimized(DomainEvent):
    targeting_id: str
    campaign_id: str
    optimization_type: str
    previous_performance: Dict[str, float]
    expected_improvement: Dict[str, float]


@dataclass
class AudienceExhausted(DomainEvent):
    targeting_id: str
    campaign_id: str
    audience_type: TargetingType
    exhaustion_percentage: float
    recommended_actions: List[str]


@dataclass
class TargetingRecommendationGenerated(DomainEvent):
    targeting_id: str
    campaign_id: str
    recommendation_type: str
    confidence_score: float
    expected_impact: str


class TargetingStrategy(AggregateRoot):
    def __init__(
        self,
        campaign_id: str,
        optimization_goal: OptimizationGoal,
        name: str = ""
    ):
        super().__init__()
        self.id = str(uuid4())
        self._campaign_id = campaign_id
        self._name = name or f"Targeting Strategy {datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        self._optimization_goal = optimization_goal
        self._status = TargetingStatus.ACTIVE
        self._demographic_criteria: Optional[DemographicCriteria] = None
        self._geographic_criteria: Optional[GeographicCriteria] = None
        self._behavioral_criteria: Optional[BehavioralCriteria] = None
        self._interest_criteria: Optional[InterestCriteria] = None
        self._custom_audiences: List[CustomAudience] = []
        self._lookalike_audiences: List[LookalikeAudience] = []
        self._excluded_audiences: List[str] = []
        self._estimated_audience_size: int = 0
        self._actual_reach: int = 0
        self._performance: TargetingPerformance = TargetingPerformance()
        self._learning_phase_complete = False
        self._optimization_history: List[Dict[str, Any]] = []
        self._created_at = datetime.utcnow()
        self._updated_at = datetime.utcnow()

    @property
    def campaign_id(self) -> str:
        return self._campaign_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def optimization_goal(self) -> OptimizationGoal:
        return self._optimization_goal

    @property
    def status(self) -> TargetingStatus:
        return self._status

    @property
    def estimated_audience_size(self) -> int:
        return self._estimated_audience_size

    @property
    def actual_reach(self) -> int:
        return self._actual_reach

    @property
    def performance(self) -> TargetingPerformance:
        return self._performance

    @property
    def demographic_criteria(self) -> Optional[DemographicCriteria]:
        return self._demographic_criteria

    @property
    def geographic_criteria(self) -> Optional[GeographicCriteria]:
        return self._geographic_criteria

    @property
    def behavioral_criteria(self) -> Optional[BehavioralCriteria]:
        return self._behavioral_criteria

    @property
    def interest_criteria(self) -> Optional[InterestCriteria]:
        return self._interest_criteria

    @property
    def custom_audiences(self) -> List[CustomAudience]:
        return self._custom_audiences.copy()

    @property
    def lookalike_audiences(self) -> List[LookalikeAudience]:
        return self._lookalike_audiences.copy()

    def set_demographic_targeting(self, criteria: DemographicCriteria):
        self._demographic_criteria = criteria
        self._estimate_audience_size()
        self._updated_at = datetime.utcnow()

    def set_geographic_targeting(self, criteria: GeographicCriteria):
        self._geographic_criteria = criteria
        self._estimate_audience_size()
        self._updated_at = datetime.utcnow()

    def set_behavioral_targeting(self, criteria: BehavioralCriteria):
        self._behavioral_criteria = criteria
        self._estimate_audience_size()
        self._updated_at = datetime.utcnow()

    def set_interest_targeting(self, criteria: InterestCriteria):
        self._interest_criteria = criteria
        self._estimate_audience_size()
        self._updated_at = datetime.utcnow()

    def add_custom_audience(self, audience: CustomAudience):
        # Remove existing audience with same ID
        self._custom_audiences = [a for a in self._custom_audiences if a.audience_id != audience.audience_id]
        self._custom_audiences.append(audience)
        self._estimate_audience_size()
        self._updated_at = datetime.utcnow()

    def add_lookalike_audience(self, audience: LookalikeAudience):
        # Remove existing audience with same ID
        self._lookalike_audiences = [a for a in self._lookalike_audiences if a.audience_id != audience.audience_id]
        self._lookalike_audiences.append(audience)
        self._estimate_audience_size()
        self._updated_at = datetime.utcnow()

    def exclude_audience(self, audience_id: str):
        if audience_id not in self._excluded_audiences:
            self._excluded_audiences.append(audience_id)
            self._estimate_audience_size()
            self._updated_at = datetime.utcnow()

    def update_performance_metrics(
        self,
        impressions: int,
        clicks: int,
        conversions: int,
        cost: float
    ):
        self._performance.impressions = impressions
        self._performance.clicks = clicks
        self._performance.conversions = conversions
        self._performance.cost = cost
        
        # Calculate derived metrics
        if impressions > 0:
            self._performance.ctr = (clicks / impressions) * 100
        if clicks > 0:
            self._performance.cvr = (conversions / clicks) * 100
            self._performance.cpc = cost / clicks
        if conversions > 0:
            self._performance.cpa = cost / conversions

        self._actual_reach = impressions  # Simplified assumption
        
        # Check if learning phase should be complete
        if not self._learning_phase_complete and impressions >= 500:
            self._learning_phase_complete = True
            self._status = TargetingStatus.OPTIMIZING

        # Assess performance status
        self._assess_performance_status()
        
        self._updated_at = datetime.utcnow()

    def optimize_targeting(self, optimization_type: str) -> Dict[str, Any]:
        if not self._learning_phase_complete:
            raise ValueError("Cannot optimize before learning phase is complete")

        previous_performance = {
            "ctr": self._performance.ctr,
            "cvr": self._performance.cvr,
            "cpc": self._performance.cpc,
            "cpa": self._performance.cpa
        }

        optimization_result = {}

        if optimization_type == "EXPAND_AUDIENCE":
            optimization_result = self._expand_audience()
        elif optimization_type == "NARROW_AUDIENCE":
            optimization_result = self._narrow_audience()
        elif optimization_type == "LOOKALIKE_EXPANSION":
            optimization_result = self._create_lookalike_expansion()
        elif optimization_type == "BEHAVIORAL_REFINEMENT":
            optimization_result = self._refine_behavioral_targeting()
        elif optimization_type == "GEOGRAPHIC_OPTIMIZATION":
            optimization_result = self._optimize_geographic_targeting()
        else:
            raise ValueError(f"Unknown optimization type: {optimization_type}")

        # Record optimization in history
        self._optimization_history.append({
            "timestamp": datetime.utcnow().isoformat(),
            "optimization_type": optimization_type,
            "previous_performance": previous_performance,
            "expected_improvement": optimization_result.get("expected_improvement", {}),
            "changes_made": optimization_result.get("changes_made", [])
        })

        self._updated_at = datetime.utcnow()

        self.publicar_evento(TargetingOptimized(
            event_id=str(uuid4()),
            occurred_on=datetime.utcnow(),
            targeting_id=self.id,
            campaign_id=self._campaign_id,
            optimization_type=optimization_type,
            previous_performance=previous_performance,
            expected_improvement=optimization_result.get("expected_improvement", {})
        ))

        return optimization_result

    def generate_targeting_recommendations(self) -> List[Dict[str, Any]]:
        recommendations = []

        # Check audience size
        audience_size_category = self._categorize_audience_size()
        
        if audience_size_category == AudienceSize.VERY_NARROW:
            recommendations.append({
                "type": "EXPAND_AUDIENCE",
                "priority": "HIGH",
                "description": "Audience is very narrow, consider expanding targeting criteria",
                "expected_impact": "Increase reach by 50-200%",
                "confidence": 0.8
            })
        elif audience_size_category == AudienceSize.VERY_BROAD:
            recommendations.append({
                "type": "NARROW_AUDIENCE",
                "priority": "MEDIUM",
                "description": "Audience is very broad, consider adding more specific criteria",
                "expected_impact": "Improve relevance and reduce CPA by 10-30%",
                "confidence": 0.7
            })

        # Performance-based recommendations
        if self._performance.ctr < 1.0 and self._performance.impressions > 1000:
            recommendations.append({
                "type": "IMPROVE_RELEVANCE",
                "priority": "HIGH",
                "description": "Low CTR indicates poor audience relevance",
                "expected_impact": "Increase CTR by 20-50%",
                "confidence": 0.9
            })

        if self._performance.cvr < 2.0 and self._performance.clicks > 100:
            recommendations.append({
                "type": "OPTIMIZE_LANDING_EXPERIENCE",
                "priority": "HIGH",
                "description": "Low conversion rate may indicate audience-landing page mismatch",
                "expected_impact": "Increase CVR by 15-40%",
                "confidence": 0.8
            })

        # Suggest lookalike audiences if none exist
        if not self._lookalike_audiences and self._performance.conversions > 50:
            recommendations.append({
                "type": "CREATE_LOOKALIKE",
                "priority": "MEDIUM",
                "description": "Create lookalike audiences based on converters",
                "expected_impact": "Find new high-quality audiences",
                "confidence": 0.7
            })

        # Geographic optimization
        if self._geographic_criteria and len(self._geographic_criteria.countries) > 5:
            recommendations.append({
                "type": "GEOGRAPHIC_ANALYSIS",
                "priority": "MEDIUM",
                "description": "Analyze performance by geography and optimize",
                "expected_impact": "Improve efficiency by 10-25%",
                "confidence": 0.6
            })

        return recommendations

    def _estimate_audience_size(self):
        # Simplified audience size estimation
        base_size = 1000000  # 1M base
        
        # Apply demographic filters
        if self._demographic_criteria:
            if self._demographic_criteria.age_min or self._demographic_criteria.age_max:
                base_size *= 0.4  # Age targeting reduces audience
            if self._demographic_criteria.genders and len(self._demographic_criteria.genders) < 2:
                base_size *= 0.5  # Gender targeting
            if self._demographic_criteria.income_levels:
                base_size *= 0.3  # Income targeting
        
        # Apply geographic filters
        if self._geographic_criteria:
            if self._geographic_criteria.countries:
                country_factor = min(len(self._geographic_criteria.countries) * 0.1, 1.0)
                base_size *= country_factor
            if self._geographic_criteria.cities:
                base_size *= 0.1  # City targeting is very specific
        
        # Apply interest and behavioral filters
        if self._interest_criteria:
            interest_count = len(self._interest_criteria.interests + self._interest_criteria.hobbies)
            if interest_count > 0:
                base_size *= max(0.1, 1.0 - (interest_count * 0.1))
        
        if self._behavioral_criteria:
            behavior_count = len(
                self._behavioral_criteria.purchase_behaviors + 
                self._behavioral_criteria.digital_activities + 
                self._behavioral_criteria.life_events
            )
            if behavior_count > 0:
                base_size *= max(0.1, 1.0 - (behavior_count * 0.05))
        
        # Add custom and lookalike audiences
        for audience in self._custom_audiences:
            base_size += audience.size_estimate
        
        for audience in self._lookalike_audiences:
            base_size += audience.size_estimate
        
        self._estimated_audience_size = max(int(base_size), 1000)  # Minimum 1k

    def _categorize_audience_size(self) -> AudienceSize:
        size = self._estimated_audience_size
        
        if size < 10000:
            return AudienceSize.VERY_NARROW
        elif size < 100000:
            return AudienceSize.NARROW
        elif size < 1000000:
            return AudienceSize.MODERATE
        elif size < 10000000:
            return AudienceSize.BROAD
        else:
            return AudienceSize.VERY_BROAD

    def _assess_performance_status(self):
        if not self._learning_phase_complete:
            self._status = TargetingStatus.LEARNING
            return

        # Define performance thresholds based on optimization goal
        thresholds = self._get_performance_thresholds()
        
        if self._performance.ctr < thresholds["min_ctr"] or self._performance.cvr < thresholds["min_cvr"]:
            self._status = TargetingStatus.UNDERPERFORMING
        elif self._actual_reach < self._estimated_audience_size * 0.1:
            self._status = TargetingStatus.EXHAUSTED
        else:
            self._status = TargetingStatus.OPTIMIZING

    def _get_performance_thresholds(self) -> Dict[str, float]:
        # Define minimum thresholds by optimization goal
        thresholds = {
            OptimizationGoal.REACH: {"min_ctr": 0.5, "min_cvr": 0.5},
            OptimizationGoal.ENGAGEMENT: {"min_ctr": 1.0, "min_cvr": 1.0},
            OptimizationGoal.CONVERSIONS: {"min_ctr": 0.8, "min_cvr": 2.0},
            OptimizationGoal.BRAND_AWARENESS: {"min_ctr": 0.3, "min_cvr": 0.3},
            OptimizationGoal.TRAFFIC: {"min_ctr": 1.5, "min_cvr": 0.5},
            OptimizationGoal.LEAD_GENERATION: {"min_ctr": 0.7, "min_cvr": 3.0}
        }
        
        return thresholds.get(self._optimization_goal, {"min_ctr": 0.8, "min_cvr": 1.5})

    def _expand_audience(self) -> Dict[str, Any]:
        changes_made = []
        
        # Expand age range
        if self._demographic_criteria:
            if self._demographic_criteria.age_min and self._demographic_criteria.age_min > 18:
                self._demographic_criteria.age_min -= 5
                changes_made.append("Reduced minimum age by 5 years")
            
            if self._demographic_criteria.age_max and self._demographic_criteria.age_max < 65:
                self._demographic_criteria.age_max += 5
                changes_made.append("Increased maximum age by 5 years")
        
        # Expand geographic targeting
        if self._geographic_criteria and len(self._geographic_criteria.countries) < 10:
            # Add similar countries (simplified logic)
            self._geographic_criteria.countries.extend(["SIMILAR_COUNTRY_1", "SIMILAR_COUNTRY_2"])
            changes_made.append("Added similar geographic markets")
        
        self._estimate_audience_size()
        
        return {
            "changes_made": changes_made,
            "expected_improvement": {
                "reach_increase": "30-100%",
                "cpc_change": "May increase 10-20%"
            }
        }

    def _narrow_audience(self) -> Dict[str, Any]:
        changes_made = []
        
        # Add more specific interests
        if not self._interest_criteria:
            self._interest_criteria = InterestCriteria()
        
        if len(self._interest_criteria.interests) < 5:
            self._interest_criteria.interests.extend(["SPECIFIC_INTEREST_1", "SPECIFIC_INTEREST_2"])
            changes_made.append("Added specific interest targeting")
        
        # Add behavioral criteria
        if not self._behavioral_criteria:
            self._behavioral_criteria = BehavioralCriteria()
        
        if len(self._behavioral_criteria.purchase_behaviors) < 3:
            self._behavioral_criteria.purchase_behaviors.extend(["RECENT_PURCHASER", "BRAND_AFFINITY"])
            changes_made.append("Added purchase behavior criteria")
        
        self._estimate_audience_size()
        
        return {
            "changes_made": changes_made,
            "expected_improvement": {
                "ctr_increase": "15-30%",
                "cvr_increase": "10-25%",
                "reach_decrease": "20-40%"
            }
        }

    def _create_lookalike_expansion(self) -> Dict[str, Any]:
        if not self._custom_audiences:
            return {
                "changes_made": ["No source audience available for lookalike creation"],
                "expected_improvement": {}
            }

        # Create lookalike based on best performing custom audience
        source_audience = self._custom_audiences[0]  # Simplified selection
        
        lookalike = LookalikeAudience(
            audience_id=str(uuid4()),
            name=f"Lookalike - {source_audience.name}",
            source_audience_id=source_audience.audience_id,
            similarity_percentage=3,  # 3% similarity for broader reach
            size_estimate=source_audience.size_estimate * 10,
            countries=self._geographic_criteria.countries if self._geographic_criteria else ["US"],
            created_at=datetime.utcnow()
        )
        
        self.add_lookalike_audience(lookalike)
        
        return {
            "changes_made": [f"Created lookalike audience based on {source_audience.name}"],
            "expected_improvement": {
                "reach_increase": "200-500%",
                "quality_maintenance": "High similarity to converters"
            }
        }

    def _refine_behavioral_targeting(self) -> Dict[str, Any]:
        changes_made = []
        
        if not self._behavioral_criteria:
            self._behavioral_criteria = BehavioralCriteria()
        
        # Add more refined behavioral targeting based on performance
        if self._performance.conversions > 0:
            self._behavioral_criteria.purchase_behaviors.extend([
                "FREQUENT_ONLINE_SHOPPER",
                "PREMIUM_BRAND_AFFINITY",
                "PRICE_CONSCIOUS"
            ])
            changes_made.append("Added refined purchase behavior targeting")
        
        if self._performance.clicks > 100:
            self._behavioral_criteria.digital_activities.extend([
                "SOCIAL_MEDIA_ENGAGER",
                "CONTENT_CONSUMER",
                "MOBILE_HEAVY_USER"
            ])
            changes_made.append("Added digital activity targeting")
        
        self._estimate_audience_size()
        
        return {
            "changes_made": changes_made,
            "expected_improvement": {
                "relevance_increase": "20-40%",
                "cvr_increase": "15-30%"
            }
        }

    def _optimize_geographic_targeting(self) -> Dict[str, Any]:
        changes_made = []
        
        if not self._geographic_criteria:
            return {
                "changes_made": ["No geographic targeting to optimize"],
                "expected_improvement": {}
            }
        
        # Simplified geographic optimization
        # In reality, this would analyze performance by geography
        if len(self._geographic_criteria.countries) > 3:
            # Keep top performing countries (simplified)
            self._geographic_criteria.countries = self._geographic_criteria.countries[:3]
            changes_made.append("Focused on top-performing geographic markets")
        
        # Add location types for better targeting
        if not self._geographic_criteria.location_types:
            self._geographic_criteria.location_types = ["HOME", "WORK"]
            changes_made.append("Added location type targeting")
        
        self._estimate_audience_size()
        
        return {
            "changes_made": changes_made,
            "expected_improvement": {
                "efficiency_increase": "10-25%",
                "cpc_decrease": "5-15%"
            }
        }

    def get_targeting_summary(self) -> Dict[str, Any]:
        return {
            "targeting_id": self.id,
            "campaign_id": self._campaign_id,
            "name": self._name,
            "optimization_goal": self._optimization_goal.value,
            "status": self._status.value,
            "estimated_audience_size": self._estimated_audience_size,
            "actual_reach": self._actual_reach,
            "audience_size_category": self._categorize_audience_size().value,
            "learning_phase_complete": self._learning_phase_complete,
            "performance": {
                "impressions": self._performance.impressions,
                "clicks": self._performance.clicks,
                "conversions": self._performance.conversions,
                "cost": self._performance.cost,
                "ctr": round(self._performance.ctr, 2),
                "cvr": round(self._performance.cvr, 2),
                "cpc": round(self._performance.cpc, 2),
                "cpa": round(self._performance.cpa, 2)
            },
            "targeting_criteria": {
                "demographic": self._demographic_criteria.__dict__ if self._demographic_criteria else None,
                "geographic": self._geographic_criteria.__dict__ if self._geographic_criteria else None,
                "behavioral": self._behavioral_criteria.__dict__ if self._behavioral_criteria else None,
                "interest": self._interest_criteria.__dict__ if self._interest_criteria else None,
                "custom_audiences_count": len(self._custom_audiences),
                "lookalike_audiences_count": len(self._lookalike_audiences),
                "excluded_audiences_count": len(self._excluded_audiences)
            },
            "optimizations_performed": len(self._optimization_history),
            "created_at": self._created_at.isoformat(),
            "updated_at": self._updated_at.isoformat()
        }

    @classmethod
    def from_events(cls, events: List[DomainEvent]) -> 'TargetingStrategy':
        raise NotImplementedError("TargetingStrategy event sourcing not implemented")