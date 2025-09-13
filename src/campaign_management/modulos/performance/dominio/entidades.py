from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Dict, Any, Optional
from uuid import uuid4
from decimal import Decimal

from campaign_management.seedwork.dominio.entidades import AggregateRoot
from campaign_management.seedwork.dominio.eventos import DomainEvent


class MetricType(Enum):
    IMPRESSIONS = "IMPRESSIONS"
    CLICKS = "CLICKS"
    CONVERSIONS = "CONVERSIONS"
    COST = "COST"
    REVENUE = "REVENUE"
    CTR = "CTR"  # Click-through rate
    CVR = "CVR"  # Conversion rate
    CPC = "CPC"  # Cost per click
    CPA = "CPA"  # Cost per acquisition
    ROAS = "ROAS"  # Return on ad spend
    ROI = "ROI"  # Return on investment


class PerformancePeriod(Enum):
    HOURLY = "HOURLY"
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    CAMPAIGN_LIFETIME = "CAMPAIGN_LIFETIME"


class TrendDirection(Enum):
    INCREASING = "INCREASING"
    DECREASING = "DECREASING"
    STABLE = "STABLE"
    VOLATILE = "VOLATILE"


class BenchmarkType(Enum):
    INDUSTRY_AVERAGE = "INDUSTRY_AVERAGE"
    HISTORICAL_PERFORMANCE = "HISTORICAL_PERFORMANCE"
    COMPETITOR_ANALYSIS = "COMPETITOR_ANALYSIS"
    INTERNAL_TARGET = "INTERNAL_TARGET"


class PerformanceStatus(Enum):
    EXCELLENT = "EXCELLENT"
    GOOD = "GOOD"
    AVERAGE = "AVERAGE"
    BELOW_AVERAGE = "BELOW_AVERAGE"
    POOR = "POOR"


@dataclass
class MetricValue:
    metric_type: MetricType
    value: Decimal
    timestamp: datetime
    period: PerformancePeriod
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceBenchmark:
    benchmark_id: str
    metric_type: MetricType
    benchmark_type: BenchmarkType
    target_value: Decimal
    industry: Optional[str] = None
    description: str = ""
    valid_from: datetime = field(default_factory=datetime.utcnow)
    valid_until: Optional[datetime] = None


@dataclass
class TrendAnalysis:
    metric_type: MetricType
    trend_direction: TrendDirection
    trend_strength: float  # -1.0 to 1.0
    period_analyzed: int  # Number of periods analyzed
    confidence_score: float  # 0.0 to 1.0
    projected_next_value: Optional[Decimal] = None


@dataclass
class PerformanceInsight:
    insight_id: str
    insight_type: str
    title: str
    description: str
    impact_score: float  # 0.0 to 1.0
    confidence: float  # 0.0 to 1.0
    recommended_actions: List[str]
    generated_at: datetime
    metrics_involved: List[MetricType] = field(default_factory=list)


@dataclass
class OptimizationRecommendation:
    recommendation_id: str
    category: str  # e.g., "targeting", "bidding", "creative"
    title: str
    description: str
    expected_impact: str  # e.g., "Increase CTR by 15%"
    implementation_difficulty: str  # EASY, MEDIUM, HARD
    priority: str  # LOW, MEDIUM, HIGH, CRITICAL
    estimated_implementation_time: str
    supporting_data: Dict[str, Any] = field(default_factory=dict)


# Domain Events
@dataclass
class PerformanceMetricUpdated(DomainEvent):
    campaign_id: str
    metric_type: MetricType
    new_value: Decimal
    previous_value: Optional[Decimal]
    timestamp: datetime


@dataclass
class PerformanceThresholdBreached(DomainEvent):
    campaign_id: str
    metric_type: MetricType
    threshold_type: str  # MIN, MAX, TARGET
    threshold_value: Decimal
    actual_value: Decimal
    severity: str


@dataclass
class PerformanceInsightGenerated(DomainEvent):
    campaign_id: str
    insight_id: str
    insight_type: str
    impact_score: float
    confidence: float


@dataclass
class PerformanceOptimizationRecommended(DomainEvent):
    campaign_id: str
    recommendation_id: str
    category: str
    priority: str
    expected_impact: str


class PerformanceTracker(AggregateRoot):
    def __init__(
        self,
        campaign_id: str,
        tracking_start_date: datetime,
        benchmarks: List[PerformanceBenchmark] = None
    ):
        super().__init__()
        self.id = str(uuid4())
        self._campaign_id = campaign_id
        self._tracking_start_date = tracking_start_date
        self._metrics_history: Dict[MetricType, List[MetricValue]] = {}
        self._benchmarks = benchmarks or []
        self._trend_analyses: Dict[MetricType, TrendAnalysis] = {}
        self._insights: List[PerformanceInsight] = []
        self._recommendations: List[OptimizationRecommendation] = []
        self._performance_thresholds: Dict[MetricType, Dict[str, Decimal]] = {}
        self._created_at = datetime.utcnow()
        self._last_updated = datetime.utcnow()

    @property
    def campaign_id(self) -> str:
        return self._campaign_id

    @property
    def tracking_start_date(self) -> datetime:
        return self._tracking_start_date

    @property
    def metrics_history(self) -> Dict[MetricType, List[MetricValue]]:
        return {k: v.copy() for k, v in self._metrics_history.items()}

    @property
    def benchmarks(self) -> List[PerformanceBenchmark]:
        return self._benchmarks.copy()

    @property
    def insights(self) -> List[PerformanceInsight]:
        return self._insights.copy()

    @property
    def recommendations(self) -> List[OptimizationRecommendation]:
        return self._recommendations.copy()

    def record_metric(
        self,
        metric_type: MetricType,
        value: Decimal,
        timestamp: datetime = None,
        period: PerformancePeriod = PerformancePeriod.DAILY,
        metadata: Dict[str, Any] = None
    ):
        if timestamp is None:
            timestamp = datetime.utcnow()

        if value < 0:
            raise ValueError("Metric value cannot be negative")

        metric_value = MetricValue(
            metric_type=metric_type,
            value=value,
            timestamp=timestamp,
            period=period,
            metadata=metadata or {}
        )

        if metric_type not in self._metrics_history:
            self._metrics_history[metric_type] = []

        # Get previous value for comparison
        previous_value = None
        if self._metrics_history[metric_type]:
            previous_value = self._metrics_history[metric_type][-1].value

        self._metrics_history[metric_type].append(metric_value)
        
        # Keep only recent metrics (last 90 days by default)
        cutoff_date = datetime.utcnow() - timedelta(days=90)
        self._metrics_history[metric_type] = [
            mv for mv in self._metrics_history[metric_type] 
            if mv.timestamp >= cutoff_date
        ]

        # Check thresholds
        self._check_performance_thresholds(metric_type, value)

        # Update trend analysis
        self._update_trend_analysis(metric_type)

        # Generate insights if enough data
        if len(self._metrics_history[metric_type]) >= 5:
            self._generate_insights(metric_type)

        self._last_updated = datetime.utcnow()

        self.publicar_evento(PerformanceMetricUpdated(
            event_id=str(uuid4()),
            occurred_on=datetime.utcnow(),
            campaign_id=self._campaign_id,
            metric_type=metric_type,
            new_value=value,
            previous_value=previous_value,
            timestamp=timestamp
        ))

    def set_performance_threshold(
        self,
        metric_type: MetricType,
        threshold_type: str,  # MIN, MAX, TARGET
        threshold_value: Decimal
    ):
        if metric_type not in self._performance_thresholds:
            self._performance_thresholds[metric_type] = {}
        
        self._performance_thresholds[metric_type][threshold_type] = threshold_value
        self._last_updated = datetime.utcnow()

    def add_benchmark(self, benchmark: PerformanceBenchmark):
        # Remove existing benchmark of same type and metric
        self._benchmarks = [
            b for b in self._benchmarks 
            if not (b.metric_type == benchmark.metric_type and b.benchmark_type == benchmark.benchmark_type)
        ]
        
        self._benchmarks.append(benchmark)
        self._last_updated = datetime.utcnow()

    def get_current_performance_summary(self) -> Dict[str, Any]:
        summary = {
            "campaign_id": self._campaign_id,
            "summary_generated_at": datetime.utcnow().isoformat(),
            "metrics": {},
            "calculated_metrics": {},
            "benchmark_comparisons": {},
            "performance_status": {},
            "trends": {}
        }

        # Get latest metrics
        for metric_type, history in self._metrics_history.items():
            if history:
                latest = history[-1]
                summary["metrics"][metric_type.value] = {
                    "current_value": float(latest.value),
                    "timestamp": latest.timestamp.isoformat(),
                    "period": latest.period.value
                }

        # Calculate derived metrics
        summary["calculated_metrics"] = self._calculate_derived_metrics()

        # Benchmark comparisons
        for benchmark in self._benchmarks:
            if benchmark.metric_type in self._metrics_history:
                latest_value = self._metrics_history[benchmark.metric_type][-1].value
                comparison = {
                    "benchmark_value": float(benchmark.target_value),
                    "actual_value": float(latest_value),
                    "performance_ratio": float(latest_value / benchmark.target_value) if benchmark.target_value > 0 else 0,
                    "status": self._get_benchmark_status(latest_value, benchmark.target_value, benchmark.metric_type)
                }
                summary["benchmark_comparisons"][f"{benchmark.metric_type.value}_{benchmark.benchmark_type.value}"] = comparison

        # Performance status for each metric
        for metric_type in self._metrics_history:
            summary["performance_status"][metric_type.value] = self._assess_metric_performance(metric_type).value

        # Trend information
        for metric_type, trend in self._trend_analyses.items():
            summary["trends"][metric_type.value] = {
                "direction": trend.trend_direction.value,
                "strength": trend.trend_strength,
                "confidence": trend.confidence_score,
                "projected_next_value": float(trend.projected_next_value) if trend.projected_next_value else None
            }

        return summary

    def get_performance_report(
        self,
        start_date: datetime,
        end_date: datetime,
        period: PerformancePeriod = PerformancePeriod.DAILY
    ) -> Dict[str, Any]:
        if start_date >= end_date:
            raise ValueError("Start date must be before end date")

        report = {
            "campaign_id": self._campaign_id,
            "period": period.value,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "metrics_data": {},
            "aggregated_metrics": {},
            "insights": [insight.__dict__ for insight in self._insights if start_date <= insight.generated_at <= end_date],
            "recommendations": [rec.__dict__ for rec in self._recommendations]
        }

        # Filter metrics by date range
        for metric_type, history in self._metrics_history.items():
            filtered_metrics = [
                mv for mv in history 
                if start_date <= mv.timestamp <= end_date and mv.period == period
            ]
            
            if filtered_metrics:
                report["metrics_data"][metric_type.value] = [
                    {
                        "value": float(mv.value),
                        "timestamp": mv.timestamp.isoformat(),
                        "metadata": mv.metadata
                    }
                    for mv in filtered_metrics
                ]

                # Calculate aggregations
                values = [mv.value for mv in filtered_metrics]
                report["aggregated_metrics"][metric_type.value] = {
                    "total": float(sum(values)),
                    "average": float(sum(values) / len(values)),
                    "min": float(min(values)),
                    "max": float(max(values)),
                    "data_points": len(values)
                }

        return report

    def _check_performance_thresholds(self, metric_type: MetricType, value: Decimal):
        if metric_type not in self._performance_thresholds:
            return

        thresholds = self._performance_thresholds[metric_type]
        
        for threshold_type, threshold_value in thresholds.items():
            breach_detected = False
            severity = "MEDIUM"
            
            if threshold_type == "MIN" and value < threshold_value:
                breach_detected = True
                severity = "HIGH"
            elif threshold_type == "MAX" and value > threshold_value:
                breach_detected = True
                severity = "HIGH"
            elif threshold_type == "TARGET":
                deviation = abs(value - threshold_value) / threshold_value
                if deviation > 0.2:  # 20% deviation
                    breach_detected = True
                    severity = "MEDIUM"

            if breach_detected:
                self.publicar_evento(PerformanceThresholdBreached(
                    event_id=str(uuid4()),
                    occurred_on=datetime.utcnow(),
                    campaign_id=self._campaign_id,
                    metric_type=metric_type,
                    threshold_type=threshold_type,
                    threshold_value=threshold_value,
                    actual_value=value,
                    severity=severity
                ))

    def _update_trend_analysis(self, metric_type: MetricType):
        if metric_type not in self._metrics_history or len(self._metrics_history[metric_type]) < 3:
            return

        history = self._metrics_history[metric_type][-10:]  # Last 10 data points
        values = [float(mv.value) for mv in history]
        
        # Simple trend calculation
        if len(values) >= 3:
            # Calculate slope of linear regression
            n = len(values)
            x = list(range(n))
            x_mean = sum(x) / n
            y_mean = sum(values) / n
            
            numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
            denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
            
            if denominator != 0:
                slope = numerator / denominator
                
                # Determine trend direction and strength
                if abs(slope) < 0.01:
                    direction = TrendDirection.STABLE
                    strength = 0.0
                elif slope > 0:
                    direction = TrendDirection.INCREASING
                    strength = min(slope / max(values), 1.0)
                else:
                    direction = TrendDirection.DECREASING
                    strength = max(slope / max(values), -1.0)
                
                # Calculate confidence based on variance
                variance = sum((v - y_mean) ** 2 for v in values) / n
                confidence = max(0.1, 1.0 - (variance / (y_mean ** 2)) if y_mean != 0 else 0.1)
                
                # Project next value
                projected_next = Decimal(str(values[-1] + slope))
                
                self._trend_analyses[metric_type] = TrendAnalysis(
                    metric_type=metric_type,
                    trend_direction=direction,
                    trend_strength=strength,
                    period_analyzed=n,
                    confidence_score=confidence,
                    projected_next_value=projected_next
                )

    def _generate_insights(self, metric_type: MetricType):
        if metric_type not in self._metrics_history:
            return

        history = self._metrics_history[metric_type]
        if len(history) < 5:
            return

        recent_values = [mv.value for mv in history[-7:]]  # Last week
        older_values = [mv.value for mv in history[-14:-7]]  # Previous week

        if len(older_values) >= 3:
            recent_avg = sum(recent_values) / len(recent_values)
            older_avg = sum(older_values) / len(older_values)
            
            change_percent = float((recent_avg - older_avg) / older_avg * 100) if older_avg > 0 else 0
            
            if abs(change_percent) > 10:  # Significant change
                insight_type = "performance_change"
                if change_percent > 0:
                    title = f"{metric_type.value} Improvement Detected"
                    description = f"{metric_type.value} has increased by {change_percent:.1f}% compared to previous period"
                else:
                    title = f"{metric_type.value} Decline Detected"
                    description = f"{metric_type.value} has decreased by {abs(change_percent):.1f}% compared to previous period"
                
                impact_score = min(abs(change_percent) / 100, 1.0)
                confidence = 0.8  # High confidence for clear trend
                
                actions = self._get_recommended_actions_for_metric(metric_type, change_percent > 0)
                
                insight = PerformanceInsight(
                    insight_id=str(uuid4()),
                    insight_type=insight_type,
                    title=title,
                    description=description,
                    impact_score=impact_score,
                    confidence=confidence,
                    recommended_actions=actions,
                    generated_at=datetime.utcnow(),
                    metrics_involved=[metric_type]
                )
                
                self._insights.append(insight)
                
                self.publicar_evento(PerformanceInsightGenerated(
                    event_id=str(uuid4()),
                    occurred_on=datetime.utcnow(),
                    campaign_id=self._campaign_id,
                    insight_id=insight.insight_id,
                    insight_type=insight_type,
                    impact_score=impact_score,
                    confidence=confidence
                ))

    def _calculate_derived_metrics(self) -> Dict[str, float]:
        derived = {}
        
        # Get latest values
        metrics = {}
        for metric_type, history in self._metrics_history.items():
            if history:
                metrics[metric_type] = float(history[-1].value)

        # Calculate CTR (Click-Through Rate)
        if MetricType.CLICKS in metrics and MetricType.IMPRESSIONS in metrics:
            impressions = metrics[MetricType.IMPRESSIONS]
            if impressions > 0:
                derived["CTR"] = (metrics[MetricType.CLICKS] / impressions) * 100

        # Calculate CVR (Conversion Rate)
        if MetricType.CONVERSIONS in metrics and MetricType.CLICKS in metrics:
            clicks = metrics[MetricType.CLICKS]
            if clicks > 0:
                derived["CVR"] = (metrics[MetricType.CONVERSIONS] / clicks) * 100

        # Calculate CPC (Cost Per Click)
        if MetricType.COST in metrics and MetricType.CLICKS in metrics:
            clicks = metrics[MetricType.CLICKS]
            if clicks > 0:
                derived["CPC"] = metrics[MetricType.COST] / clicks

        # Calculate CPA (Cost Per Acquisition)
        if MetricType.COST in metrics and MetricType.CONVERSIONS in metrics:
            conversions = metrics[MetricType.CONVERSIONS]
            if conversions > 0:
                derived["CPA"] = metrics[MetricType.COST] / conversions

        # Calculate ROAS (Return On Ad Spend)
        if MetricType.REVENUE in metrics and MetricType.COST in metrics:
            cost = metrics[MetricType.COST]
            if cost > 0:
                derived["ROAS"] = metrics[MetricType.REVENUE] / cost

        # Calculate ROI (Return On Investment)
        if MetricType.REVENUE in metrics and MetricType.COST in metrics:
            cost = metrics[MetricType.COST]
            if cost > 0:
                derived["ROI"] = ((metrics[MetricType.REVENUE] - cost) / cost) * 100

        return derived

    def _get_benchmark_status(self, actual_value: Decimal, benchmark_value: Decimal, metric_type: MetricType) -> str:
        ratio = float(actual_value / benchmark_value) if benchmark_value > 0 else 0
        
        # For metrics where higher is better (CTR, CVR, ROAS, ROI)
        higher_is_better = metric_type in [MetricType.CTR, MetricType.CVR, MetricType.ROAS, MetricType.ROI, MetricType.CONVERSIONS, MetricType.REVENUE]
        
        if higher_is_better:
            if ratio >= 1.2:
                return "EXCELLENT"
            elif ratio >= 1.0:
                return "GOOD"
            elif ratio >= 0.8:
                return "AVERAGE"
            else:
                return "BELOW_AVERAGE"
        else:
            # For metrics where lower is better (CPC, CPA, Cost)
            if ratio <= 0.8:
                return "EXCELLENT"
            elif ratio <= 1.0:
                return "GOOD"
            elif ratio <= 1.2:
                return "AVERAGE"
            else:
                return "BELOW_AVERAGE"

    def _assess_metric_performance(self, metric_type: MetricType) -> PerformanceStatus:
        # Simple assessment based on benchmarks and trends
        if metric_type not in self._metrics_history:
            return PerformanceStatus.AVERAGE

        # Check against benchmarks
        benchmark_status = None
        for benchmark in self._benchmarks:
            if benchmark.metric_type == metric_type:
                latest_value = self._metrics_history[metric_type][-1].value
                status = self._get_benchmark_status(latest_value, benchmark.target_value, metric_type)
                if status == "EXCELLENT":
                    benchmark_status = PerformanceStatus.EXCELLENT
                elif status == "GOOD":
                    benchmark_status = PerformanceStatus.GOOD
                elif status == "BELOW_AVERAGE":
                    benchmark_status = PerformanceStatus.BELOW_AVERAGE
                break

        # Check trend
        trend_status = PerformanceStatus.AVERAGE
        if metric_type in self._trend_analyses:
            trend = self._trend_analyses[metric_type]
            if trend.trend_direction == TrendDirection.INCREASING:
                trend_status = PerformanceStatus.GOOD
            elif trend.trend_direction == TrendDirection.DECREASING:
                trend_status = PerformanceStatus.BELOW_AVERAGE

        # Combine benchmark and trend
        if benchmark_status:
            return benchmark_status
        else:
            return trend_status

    def _get_recommended_actions_for_metric(self, metric_type: MetricType, is_improving: bool) -> List[str]:
        actions = []
        
        if metric_type == MetricType.CTR:
            if is_improving:
                actions.extend(["Maintain current creative strategy", "Consider scaling successful ad variations"])
            else:
                actions.extend(["Review ad creative quality", "Test new ad copy variations", "Improve targeting relevance"])
        
        elif metric_type == MetricType.CONVERSIONS:
            if is_improving:
                actions.extend(["Increase budget allocation", "Scale to similar audiences"])
            else:
                actions.extend(["Review landing page experience", "Optimize conversion funnel", "Test different calls-to-action"])
        
        elif metric_type == MetricType.COST:
            if is_improving:
                actions.extend(["Monitor for sustained efficiency", "Consider expanding reach"])
            else:
                actions.extend(["Review bidding strategy", "Improve targeting precision", "Pause underperforming placements"])
        
        else:
            if is_improving:
                actions.append("Continue current optimization strategy")
            else:
                actions.append("Review and adjust campaign settings")
        
        return actions

    @classmethod
    def from_events(cls, events: List[DomainEvent]) -> 'PerformanceTracker':
        raise NotImplementedError("PerformanceTracker event sourcing not implemented")