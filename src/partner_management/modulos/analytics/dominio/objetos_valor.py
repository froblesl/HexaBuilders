"""
Analytics domain value objects for HexaBuilders.
Implements analytics-related value objects following DDD patterns.
"""

import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional
from datetime import datetime
from decimal import Decimal

from partner_management.seedwork.dominio.objetos_valor import ValueObject
from partner_management.seedwork.dominio.excepciones import DomainException


class ReportType(Enum):
    """Report type enumeration."""
    PARTNER_PERFORMANCE = "PARTNER_PERFORMANCE"
    CAMPAIGN_ANALYTICS = "CAMPAIGN_ANALYTICS"
    COMMISSION_SUMMARY = "COMMISSION_SUMMARY"
    REVENUE_ANALYSIS = "REVENUE_ANALYSIS"
    CONVERSION_METRICS = "CONVERSION_METRICS"
    PROFILE_360 = "PROFILE_360"


class ReportStatus(Enum):
    """Report status enumeration."""
    PENDING = "PENDING"
    GENERATING = "GENERATING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    ARCHIVED = "ARCHIVED"


class MetricType(Enum):
    """Metric type enumeration."""
    COUNTER = "COUNTER"
    GAUGE = "GAUGE"
    PERCENTAGE = "PERCENTAGE"
    CURRENCY = "CURRENCY"
    RATIO = "RATIO"


@dataclass(frozen=True)
class ReportPeriod(ValueObject):
    """Report period value object."""
    
    start_date: datetime
    end_date: datetime
    period_name: str
    
    def __post_init__(self):
        self._validate()
    
    def _validate(self):
        if not isinstance(self.start_date, datetime):
            raise DomainException("Start date must be a datetime")
        
        if not isinstance(self.end_date, datetime):
            raise DomainException("End date must be a datetime")
        
        if self.start_date >= self.end_date:
            raise DomainException("Start date must be before end date")
        
        if not self.period_name or len(self.period_name.strip()) < 2:
            raise DomainException("Period name must be at least 2 characters")
        
        # Check reasonable period duration
        duration = self.end_date - self.start_date
        if duration.days > 731:  # More than 2 years
            raise DomainException("Report period cannot exceed 2 years")
        
        if duration.days < 1:
            raise DomainException("Report period must be at least 1 day")
    
    def duration_in_days(self) -> int:
        """Get period duration in days."""
        return (self.end_date - self.start_date).days
    
    def is_current(self) -> bool:
        """Check if period includes current date."""
        now = datetime.now()
        return self.start_date <= now <= self.end_date


@dataclass(frozen=True)
class MetricValue(ValueObject):
    """Metric value with type and metadata."""
    
    value: Any
    metric_type: MetricType
    unit: Optional[str] = None
    
    def __post_init__(self):
        self._validate()
    
    def _validate(self):
        if self.value is None:
            raise DomainException("Metric value cannot be None")
        
        if not isinstance(self.metric_type, MetricType):
            raise DomainException("Metric type must be a valid MetricType")
        
        # Type-specific validations
        if self.metric_type == MetricType.COUNTER:
            if not isinstance(self.value, (int, float)) or self.value < 0:
                raise DomainException("Counter metrics must be non-negative numbers")
        
        elif self.metric_type == MetricType.PERCENTAGE:
            if not isinstance(self.value, (int, float)) or not (0 <= self.value <= 100):
                raise DomainException("Percentage metrics must be between 0 and 100")
        
        elif self.metric_type == MetricType.CURRENCY:
            if not isinstance(self.value, (Decimal, int, float)) or self.value < 0:
                raise DomainException("Currency metrics must be non-negative")
    
    def formatted_value(self) -> str:
        """Get formatted value based on metric type."""
        if self.metric_type == MetricType.PERCENTAGE:
            return f"{self.value:.2f}%"
        elif self.metric_type == MetricType.CURRENCY:
            return f"${self.value:,.2f}"
        elif self.metric_type == MetricType.COUNTER:
            return f"{int(self.value):,}"
        else:
            return str(self.value)


@dataclass(frozen=True)
class AnalyticsMetrics(ValueObject):
    """Collection of analytics metrics."""
    
    partner_metrics: Dict[str, MetricValue]
    campaign_metrics: Dict[str, MetricValue]
    commission_metrics: Dict[str, MetricValue]
    performance_metrics: Dict[str, MetricValue]
    
    def __post_init__(self):
        # Set defaults if None
        if self.partner_metrics is None:
            object.__setattr__(self, 'partner_metrics', {})
        if self.campaign_metrics is None:
            object.__setattr__(self, 'campaign_metrics', {})
        if self.commission_metrics is None:
            object.__setattr__(self, 'commission_metrics', {})
        if self.performance_metrics is None:
            object.__setattr__(self, 'performance_metrics', {})
        
        self._validate()
    
    def _validate(self):
        # Validate all metrics are MetricValue instances
        all_metrics = {
            **self.partner_metrics,
            **self.campaign_metrics, 
            **self.commission_metrics,
            **self.performance_metrics
        }
        
        for key, value in all_metrics.items():
            if not isinstance(value, MetricValue):
                raise DomainException(f"Metric '{key}' must be a MetricValue instance")
    
    def get_metric(self, category: str, metric_name: str) -> Optional[MetricValue]:
        """Get specific metric by category and name."""
        category_mapping = {
            'partner': self.partner_metrics,
            'campaign': self.campaign_metrics,
            'commission': self.commission_metrics,
            'performance': self.performance_metrics
        }
        
        category_metrics = category_mapping.get(category)
        if category_metrics:
            return category_metrics.get(metric_name)
        
        return None
    
    def total_metrics_count(self) -> int:
        """Get total number of metrics."""
        return (len(self.partner_metrics) + len(self.campaign_metrics) + 
                len(self.commission_metrics) + len(self.performance_metrics))


@dataclass(frozen=True)
class ReportConfiguration(ValueObject):
    """Report configuration value object."""
    
    report_type: ReportType
    include_charts: bool = True
    include_comparisons: bool = True
    include_trends: bool = True
    chart_types: List[str] = None
    export_formats: List[str] = None
    
    def __post_init__(self):
        if self.chart_types is None:
            object.__setattr__(self, 'chart_types', ['bar', 'line', 'pie'])
        if self.export_formats is None:
            object.__setattr__(self, 'export_formats', ['pdf', 'excel'])
        
        self._validate()
    
    def _validate(self):
        if not isinstance(self.report_type, ReportType):
            raise DomainException("Report type must be a valid ReportType")
        
        valid_chart_types = ['bar', 'line', 'pie', 'scatter', 'area', 'histogram']
        for chart_type in self.chart_types:
            if chart_type not in valid_chart_types:
                raise DomainException(f"Invalid chart type: {chart_type}")
        
        valid_formats = ['pdf', 'excel', 'csv', 'json']
        for format_type in self.export_formats:
            if format_type not in valid_formats:
                raise DomainException(f"Invalid export format: {format_type}")


@dataclass(frozen=True)
class DataFilter(ValueObject):
    """Data filter for analytics queries."""
    
    partner_ids: Optional[List[str]] = None
    campaign_ids: Optional[List[str]] = None
    commission_statuses: Optional[List[str]] = None
    date_range: Optional[ReportPeriod] = None
    minimum_amount: Optional[Decimal] = None
    maximum_amount: Optional[Decimal] = None
    
    def __post_init__(self):
        self._validate()
    
    def _validate(self):
        if self.minimum_amount is not None and self.minimum_amount < 0:
            raise DomainException("Minimum amount cannot be negative")
        
        if self.maximum_amount is not None and self.maximum_amount < 0:
            raise DomainException("Maximum amount cannot be negative")
        
        if (self.minimum_amount is not None and self.maximum_amount is not None and 
            self.minimum_amount >= self.maximum_amount):
            raise DomainException("Minimum amount must be less than maximum amount")
        
        if self.commission_statuses:
            valid_statuses = ['PENDING', 'APPROVED', 'PAID', 'CANCELLED', 'DISPUTED', 'ON_HOLD']
            for status in self.commission_statuses:
                if status not in valid_statuses:
                    raise DomainException(f"Invalid commission status: {status}")
    
    def has_filters(self) -> bool:
        """Check if any filters are applied."""
        return any([
            self.partner_ids,
            self.campaign_ids, 
            self.commission_statuses,
            self.date_range,
            self.minimum_amount is not None,
            self.maximum_amount is not None
        ])


@dataclass(frozen=True)
class Insight(ValueObject):
    """Analytics insight value object."""
    
    insight_type: str
    title: str
    description: str
    severity: str = "info"  # info, warning, critical
    confidence: float = 1.0
    recommendation: Optional[str] = None
    
    def __post_init__(self):
        self._validate()
    
    def _validate(self):
        if not self.insight_type or len(self.insight_type.strip()) < 3:
            raise DomainException("Insight type must be at least 3 characters")
        
        if not self.title or len(self.title.strip()) < 5:
            raise DomainException("Insight title must be at least 5 characters")
        
        if not self.description or len(self.description.strip()) < 10:
            raise DomainException("Insight description must be at least 10 characters")
        
        valid_severities = ['info', 'warning', 'critical']
        if self.severity not in valid_severities:
            raise DomainException(f"Severity must be one of: {valid_severities}")
        
        if not (0.0 <= self.confidence <= 1.0):
            raise DomainException("Confidence must be between 0.0 and 1.0")


@dataclass(frozen=True)
class TrendAnalysis(ValueObject):
    """Trend analysis value object."""
    
    metric_name: str
    trend_direction: str  # 'up', 'down', 'stable'
    trend_strength: float  # 0.0 to 1.0
    period_over_period_change: float
    historical_data: List[Dict[str, Any]]
    
    def __post_init__(self):
        if self.historical_data is None:
            object.__setattr__(self, 'historical_data', [])
        
        self._validate()
    
    def _validate(self):
        if not self.metric_name or len(self.metric_name.strip()) < 2:
            raise DomainException("Metric name must be at least 2 characters")
        
        valid_directions = ['up', 'down', 'stable']
        if self.trend_direction not in valid_directions:
            raise DomainException(f"Trend direction must be one of: {valid_directions}")
        
        if not (0.0 <= self.trend_strength <= 1.0):
            raise DomainException("Trend strength must be between 0.0 and 1.0")
        
        # Validate historical data structure
        for data_point in self.historical_data:
            if not isinstance(data_point, dict):
                raise DomainException("Historical data points must be dictionaries")
            
            required_keys = ['date', 'value']
            for key in required_keys:
                if key not in data_point:
                    raise DomainException(f"Historical data point missing key: {key}")
    
    def is_significant_trend(self) -> bool:
        """Check if trend is statistically significant."""
        return self.trend_strength > 0.5 and abs(self.period_over_period_change) > 0.1


@dataclass(frozen=True)
class BenchmarkComparison(ValueObject):
    """Benchmark comparison value object."""
    
    metric_name: str
    actual_value: MetricValue
    benchmark_value: MetricValue
    comparison_result: str  # 'above', 'below', 'at'
    percentage_difference: float
    
    def __post_init__(self):
        self._validate()
    
    def _validate(self):
        if not self.metric_name:
            raise DomainException("Metric name is required")
        
        if not isinstance(self.actual_value, MetricValue):
            raise DomainException("Actual value must be a MetricValue")
        
        if not isinstance(self.benchmark_value, MetricValue):
            raise DomainException("Benchmark value must be a MetricValue")
        
        if self.actual_value.metric_type != self.benchmark_value.metric_type:
            raise DomainException("Actual and benchmark values must have same metric type")
        
        valid_results = ['above', 'below', 'at']
        if self.comparison_result not in valid_results:
            raise DomainException(f"Comparison result must be one of: {valid_results}")
    
    def is_performing_above_benchmark(self) -> bool:
        """Check if actual value is above benchmark."""
        return self.comparison_result == 'above'