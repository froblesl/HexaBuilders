"""
Data Transfer Objects (DTOs) for Analytics module in HexaBuilders.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any, List


@dataclass
class AnalyticsReportDTO:
    """Analytics Report Data Transfer Object."""
    
    id: str
    partner_id: str
    report_type: str
    status: str
    
    # Report period
    period_start: datetime
    period_end: datetime
    period_name: str
    
    # Configuration
    include_charts: bool
    include_comparisons: bool
    include_trends: bool
    chart_types: List[str]
    export_formats: List[str]
    
    # Generation info
    generated_date: Optional[datetime] = None
    generated_by: Optional[str] = None
    generation_time_seconds: Optional[float] = None
    error_message: Optional[str] = None
    
    # Metrics data
    total_campaigns: Optional[int] = None
    active_campaigns: Optional[int] = None
    completed_campaigns: Optional[int] = None
    total_commissions: Optional[int] = None
    total_commission_amount: Optional[str] = None
    average_commission: Optional[str] = None
    partner_rating: Optional[float] = None
    conversion_rate: Optional[float] = None
    performance_score: Optional[float] = None
    
    # Data filters
    data_filters: Optional[Dict[str, Any]] = None
    
    # Insights, trends, benchmarks (stored as JSON)
    insights_json: Optional[str] = None
    trends_json: Optional[str] = None
    benchmarks_json: Optional[str] = None
    
    # Metadata
    created_at: datetime
    updated_at: datetime
    version: int
    is_deleted: bool = False
    
    @classmethod
    def from_entity(cls, report) -> 'AnalyticsReportDTO':
        """Create DTO from AnalyticsReport entity."""
        
        import json
        
        # Serialize insights
        insights_json = None
        if report.insights:
            insights_data = []
            for insight in report.insights:
                insights_data.append({
                    'insight_type': insight.insight_type,
                    'title': insight.title,
                    'description': insight.description,
                    'severity': insight.severity,
                    'confidence': insight.confidence,
                    'actionable': insight.actionable,
                    'recommendations': insight.recommendations
                })
            insights_json = json.dumps(insights_data)
        
        # Serialize trends
        trends_json = None
        if report.trends:
            trends_data = []
            for trend in report.trends:
                trends_data.append({
                    'metric_name': trend.metric_name,
                    'trend_direction': trend.trend_direction,
                    'trend_strength': trend.trend_strength,
                    'period_comparison': trend.period_comparison,
                    'data_points': trend.data_points,
                    'analysis': trend.analysis,
                    'confidence': trend.confidence
                })
            trends_json = json.dumps(trends_data)
        
        # Serialize benchmarks
        benchmarks_json = None
        if report.benchmarks:
            benchmarks_data = []
            for benchmark in report.benchmarks:
                benchmarks_data.append({
                    'metric_name': benchmark.metric_name,
                    'partner_value': benchmark.partner_value,
                    'benchmark_value': benchmark.benchmark_value,
                    'benchmark_type': benchmark.benchmark_type,
                    'comparison_result': benchmark.comparison_result,
                    'percentile_rank': benchmark.percentile_rank,
                    'peer_comparison': benchmark.peer_comparison
                })
            benchmarks_json = json.dumps(benchmarks_data)
        
        return cls(
            id=report.id,
            partner_id=report.partner_id,
            report_type=report.report_type.value,
            status=report.status.value,
            
            # Report period
            period_start=report.report_period.start_date,
            period_end=report.report_period.end_date,
            period_name=report.report_period.period_name,
            
            # Configuration
            include_charts=report.configuration.include_charts,
            include_comparisons=report.configuration.include_comparisons,
            include_trends=report.configuration.include_trends,
            chart_types=report.configuration.chart_types,
            export_formats=report.configuration.export_formats,
            
            # Generation info
            generated_date=report.generated_date,
            generated_by=report.generated_by,
            generation_time_seconds=getattr(report, '_generation_time_seconds', None),
            error_message=getattr(report, '_error_message', None),
            
            # Metrics data
            total_campaigns=report.metrics.total_campaigns if report.metrics else None,
            active_campaigns=report.metrics.active_campaigns if report.metrics else None,
            completed_campaigns=report.metrics.completed_campaigns if report.metrics else None,
            total_commissions=report.metrics.total_commissions if report.metrics else None,
            total_commission_amount=str(report.metrics.total_commission_amount) if report.metrics else None,
            average_commission=str(report.metrics.average_commission) if report.metrics else None,
            partner_rating=report.metrics.partner_rating if report.metrics else None,
            conversion_rate=report.metrics.conversion_rate if report.metrics else None,
            performance_score=report.metrics.performance_score if report.metrics else None,
            
            # Data filters
            data_filters=report.data_filter.__dict__ if report.data_filter else None,
            
            # Serialized complex data
            insights_json=insights_json,
            trends_json=trends_json,
            benchmarks_json=benchmarks_json,
            
            # Metadata
            created_at=report.created_at,
            updated_at=report.updated_at,
            version=report.version,
            is_deleted=report.is_deleted
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert DTO to dictionary."""
        
        import json
        
        return {
            'id': self.id,
            'partner_id': self.partner_id,
            'report_type': self.report_type,
            'status': self.status,
            
            'report_period': {
                'start_date': self.period_start.isoformat(),
                'end_date': self.period_end.isoformat(),
                'period_name': self.period_name
            },
            
            'configuration': {
                'include_charts': self.include_charts,
                'include_comparisons': self.include_comparisons,
                'include_trends': self.include_trends,
                'chart_types': self.chart_types,
                'export_formats': self.export_formats
            },
            
            'generation_info': {
                'generated_date': self.generated_date.isoformat() if self.generated_date else None,
                'generated_by': self.generated_by,
                'generation_time_seconds': self.generation_time_seconds,
                'error_message': self.error_message
            },
            
            'metrics': {
                'total_campaigns': self.total_campaigns,
                'active_campaigns': self.active_campaigns,
                'completed_campaigns': self.completed_campaigns,
                'total_commissions': self.total_commissions,
                'total_commission_amount': self.total_commission_amount,
                'average_commission': self.average_commission,
                'partner_rating': self.partner_rating,
                'conversion_rate': self.conversion_rate,
                'performance_score': self.performance_score
            } if self.total_campaigns is not None else None,
            
            'data_filters': self.data_filters,
            
            'insights': json.loads(self.insights_json) if self.insights_json else [],
            'trends': json.loads(self.trends_json) if self.trends_json else [],
            'benchmarks': json.loads(self.benchmarks_json) if self.benchmarks_json else [],
            
            'metadata': {
                'created_at': self.created_at.isoformat(),
                'updated_at': self.updated_at.isoformat(),
                'version': self.version,
                'is_deleted': self.is_deleted
            }
        }


@dataclass
class AnalyticsReportSummaryDTO:
    """Analytics Report Summary Data Transfer Object for list views."""
    
    id: str
    partner_id: str
    report_type: str
    status: str
    period_name: str
    generated_date: Optional[datetime] = None
    generated_by: Optional[str] = None
    created_at: datetime
    is_up_to_date: bool = False
    has_critical_insights: bool = False
    
    @classmethod
    def from_entity(cls, report) -> 'AnalyticsReportSummaryDTO':
        """Create summary DTO from AnalyticsReport entity."""
        
        return cls(
            id=report.id,
            partner_id=report.partner_id,
            report_type=report.report_type.value,
            status=report.status.value,
            period_name=report.report_period.period_name,
            generated_date=report.generated_date,
            generated_by=report.generated_by,
            created_at=report.created_at,
            is_up_to_date=report.esta_actualizado(),
            has_critical_insights=len(report.obtener_insights_criticos()) > 0
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert summary DTO to dictionary."""
        
        return {
            'id': self.id,
            'partner_id': self.partner_id,
            'report_type': self.report_type,
            'status': self.status,
            'period_name': self.period_name,
            'generated_date': self.generated_date.isoformat() if self.generated_date else None,
            'generated_by': self.generated_by,
            'created_at': self.created_at.isoformat(),
            'is_up_to_date': self.is_up_to_date,
            'has_critical_insights': self.has_critical_insights
        }


@dataclass
class InsightDTO:
    """Insight Data Transfer Object."""
    
    insight_type: str
    title: str
    description: str
    severity: str
    confidence: float
    actionable: bool
    recommendations: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert insight DTO to dictionary."""
        
        return {
            'insight_type': self.insight_type,
            'title': self.title,
            'description': self.description,
            'severity': self.severity,
            'confidence': self.confidence,
            'actionable': self.actionable,
            'recommendations': self.recommendations
        }


@dataclass
class TrendAnalysisDTO:
    """Trend Analysis Data Transfer Object."""
    
    metric_name: str
    trend_direction: str
    trend_strength: float
    period_comparison: str
    data_points: List[float]
    analysis: str
    confidence: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert trend DTO to dictionary."""
        
        return {
            'metric_name': self.metric_name,
            'trend_direction': self.trend_direction,
            'trend_strength': self.trend_strength,
            'period_comparison': self.period_comparison,
            'data_points': self.data_points,
            'analysis': self.analysis,
            'confidence': self.confidence
        }


@dataclass
class BenchmarkComparisonDTO:
    """Benchmark Comparison Data Transfer Object."""
    
    metric_name: str
    partner_value: float
    benchmark_value: float
    benchmark_type: str
    comparison_result: str
    percentile_rank: float
    peer_comparison: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert benchmark DTO to dictionary."""
        
        return {
            'metric_name': self.metric_name,
            'partner_value': self.partner_value,
            'benchmark_value': self.benchmark_value,
            'benchmark_type': self.benchmark_type,
            'comparison_result': self.comparison_result,
            'percentile_rank': self.percentile_rank,
            'peer_comparison': self.peer_comparison
        }