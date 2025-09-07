"""
Factory classes for Analytics module in HexaBuilders.
"""

import uuid
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from decimal import Decimal

from ....seedwork.dominio.fabricas import Fabrica
from ....seedwork.dominio.excepciones import DomainException

from ..dominio.entidades import AnalyticsReport
from ..dominio.objetos_valor import (
    ReportType, ReportPeriod, ReportConfiguration, DataFilter, ReportStatus,
    AnalyticsMetrics, Insight, TrendAnalysis, BenchmarkComparison
)
from .dto import AnalyticsReportDTO


class FabricaAnalytics(Fabrica):
    """Factory for creating Analytics entities and related objects."""
    
    def crear_analytics_report(
        self,
        partner_id: str,
        report_type: ReportType,
        report_period: ReportPeriod,
        configuration: ReportConfiguration,
        report_id: Optional[str] = None,
        data_filter: Optional[DataFilter] = None,
        status: ReportStatus = ReportStatus.PENDING
    ) -> AnalyticsReport:
        """Create an AnalyticsReport entity."""
        
        # Validate required parameters
        if not partner_id:
            raise DomainException("Partner ID is required to create analytics report")
        
        if not report_type or not report_period:
            raise DomainException("Report type and period are required")
        
        if not configuration:
            raise DomainException("Report configuration is required")
        
        # Generate ID if not provided
        if not report_id:
            report_id = str(uuid.uuid4())
        
        # Create AnalyticsReport entity
        report = AnalyticsReport(
            partner_id=partner_id,
            report_type=report_type,
            report_period=report_period,
            configuration=configuration,
            report_id=report_id,
            data_filter=data_filter,
            status=status
        )
        
        return report
    
    def crear_analytics_report_from_dto(self, dto: AnalyticsReportDTO) -> AnalyticsReport:
        """Create AnalyticsReport entity from DTO."""
        
        import json
        
        # Create value objects
        report_type = ReportType(dto.report_type)
        report_period = ReportPeriod(
            start_date=dto.period_start,
            end_date=dto.period_end,
            period_name=dto.period_name
        )
        
        configuration = ReportConfiguration(
            include_charts=dto.include_charts,
            include_comparisons=dto.include_comparisons,
            include_trends=dto.include_trends,
            chart_types=dto.chart_types,
            export_formats=dto.export_formats
        )
        
        status = ReportStatus(dto.status)
        
        # Create data filter if available
        data_filter = None
        if dto.data_filters:
            data_filter = DataFilter(**dto.data_filters)
        
        # Create metrics if available
        metrics = None
        if dto.total_campaigns is not None:
            metrics = AnalyticsMetrics(
                total_campaigns=dto.total_campaigns,
                active_campaigns=dto.active_campaigns or 0,
                completed_campaigns=dto.completed_campaigns or 0,
                total_commissions=dto.total_commissions or 0,
                total_commission_amount=Decimal(dto.total_commission_amount or '0'),
                average_commission=Decimal(dto.average_commission or '0'),
                partner_rating=dto.partner_rating or 0.0,
                conversion_rate=dto.conversion_rate or 0.0,
                performance_score=dto.performance_score or 0.0
            )
        
        # Deserialize insights
        insights = []
        if dto.insights_json:
            insights_data = json.loads(dto.insights_json)
            for insight_data in insights_data:
                insights.append(Insight(
                    insight_type=insight_data['insight_type'],
                    title=insight_data['title'],
                    description=insight_data['description'],
                    severity=insight_data['severity'],
                    confidence=insight_data['confidence'],
                    actionable=insight_data['actionable'],
                    recommendations=insight_data['recommendations']
                ))
        
        # Deserialize trends
        trends = []
        if dto.trends_json:
            trends_data = json.loads(dto.trends_json)
            for trend_data in trends_data:
                trends.append(TrendAnalysis(
                    metric_name=trend_data['metric_name'],
                    trend_direction=trend_data['trend_direction'],
                    trend_strength=trend_data['trend_strength'],
                    period_comparison=trend_data['period_comparison'],
                    data_points=trend_data['data_points'],
                    analysis=trend_data['analysis'],
                    confidence=trend_data['confidence']
                ))
        
        # Deserialize benchmarks
        benchmarks = []
        if dto.benchmarks_json:
            benchmarks_data = json.loads(dto.benchmarks_json)
            for benchmark_data in benchmarks_data:
                benchmarks.append(BenchmarkComparison(
                    metric_name=benchmark_data['metric_name'],
                    partner_value=benchmark_data['partner_value'],
                    benchmark_value=benchmark_data['benchmark_value'],
                    benchmark_type=benchmark_data['benchmark_type'],
                    comparison_result=benchmark_data['comparison_result'],
                    percentile_rank=benchmark_data['percentile_rank'],
                    peer_comparison=benchmark_data['peer_comparison']
                ))
        
        # Create AnalyticsReport entity
        report = AnalyticsReport(
            partner_id=dto.partner_id,
            report_type=report_type,
            report_period=report_period,
            configuration=configuration,
            report_id=dto.id,
            data_filter=data_filter,
            status=status,
            metrics=metrics,
            insights=insights,
            trends=trends,
            benchmarks=benchmarks
        )
        
        # Set additional fields
        if dto.generated_date:
            report._generated_date = dto.generated_date
            report._generated_by = dto.generated_by
            report._generation_time_seconds = dto.generation_time_seconds
            report._error_message = dto.error_message
        
        # Set metadata
        report._created_at = dto.created_at
        report._updated_at = dto.updated_at
        report._version = dto.version
        report._is_deleted = dto.is_deleted
        
        return report
    
    def crear_reporte_performance(
        self,
        partner_id: str,
        period_days: int = 30,
        include_predictions: bool = True
    ) -> AnalyticsReport:
        """Create a partner performance report."""
        
        # Calculate period
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days)
        
        # Create value objects
        report_type = ReportType('PARTNER_PERFORMANCE')
        
        report_period = ReportPeriod(
            start_date=start_date,
            end_date=end_date,
            period_name=f"Partner Performance - {period_days} days"
        )
        
        configuration = ReportConfiguration(
            include_charts=True,
            include_comparisons=True,
            include_trends=True,
            chart_types=['line', 'bar', 'pie'],
            export_formats=['pdf', 'json']
        )
        
        return self.crear_analytics_report(
            partner_id=partner_id,
            report_type=report_type,
            report_period=report_period,
            configuration=configuration
        )
    
    def crear_reporte_comisiones(
        self,
        partner_id: str,
        period_months: int = 3
    ) -> AnalyticsReport:
        """Create a commission summary report."""
        
        # Calculate period
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_months * 30)
        
        # Create value objects
        report_type = ReportType('COMMISSION_SUMMARY')
        
        report_period = ReportPeriod(
            start_date=start_date,
            end_date=end_date,
            period_name=f"Commission Summary - {period_months} months"
        )
        
        configuration = ReportConfiguration(
            include_charts=True,
            include_comparisons=False,
            include_trends=True,
            chart_types=['line', 'bar'],
            export_formats=['pdf', 'csv']
        )
        
        return self.crear_analytics_report(
            partner_id=partner_id,
            report_type=report_type,
            report_period=report_period,
            configuration=configuration
        )
    
    def crear_reporte_campanas(
        self,
        partner_id: str,
        period_months: int = 6,
        campaign_filters: Optional[Dict[str, Any]] = None
    ) -> AnalyticsReport:
        """Create a campaign analysis report."""
        
        # Calculate period
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_months * 30)
        
        # Create value objects
        report_type = ReportType('CAMPAIGN_ANALYSIS')
        
        report_period = ReportPeriod(
            start_date=start_date,
            end_date=end_date,
            period_name=f"Campaign Analysis - {period_months} months"
        )
        
        configuration = ReportConfiguration(
            include_charts=True,
            include_comparisons=True,
            include_trends=True,
            chart_types=['line', 'bar', 'scatter'],
            export_formats=['pdf', 'json']
        )
        
        # Create data filter if filters provided
        data_filter = None
        if campaign_filters:
            data_filter = DataFilter(**campaign_filters)
        
        return self.crear_analytics_report(
            partner_id=partner_id,
            report_type=report_type,
            report_period=report_period,
            configuration=configuration,
            data_filter=data_filter
        )
    
    def crear_reporte_comprehensivo(
        self,
        partner_id: str,
        period_months: int = 12
    ) -> AnalyticsReport:
        """Create a comprehensive analytics report."""
        
        # Calculate period
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_months * 30)
        
        # Create value objects
        report_type = ReportType('COMPREHENSIVE')
        
        report_period = ReportPeriod(
            start_date=start_date,
            end_date=end_date,
            period_name=f"Comprehensive Report - {period_months} months"
        )
        
        configuration = ReportConfiguration(
            include_charts=True,
            include_comparisons=True,
            include_trends=True,
            chart_types=['line', 'bar', 'pie', 'scatter', 'area'],
            export_formats=['pdf', 'json', 'xlsx']
        )
        
        return self.crear_analytics_report(
            partner_id=partner_id,
            report_type=report_type,
            report_period=report_period,
            configuration=configuration
        )
    
    def crear_insight(
        self,
        insight_type: str,
        title: str,
        description: str,
        severity: str = "info",
        confidence: float = 0.8,
        actionable: bool = True,
        recommendations: Optional[List[str]] = None
    ) -> Insight:
        """Create an Insight value object."""
        
        return Insight(
            insight_type=insight_type,
            title=title,
            description=description,
            severity=severity,
            confidence=confidence,
            actionable=actionable,
            recommendations=recommendations or []
        )
    
    def crear_trend_analysis(
        self,
        metric_name: str,
        trend_direction: str,
        trend_strength: float,
        period_comparison: str,
        data_points: List[float],
        analysis: str,
        confidence: float = 0.75
    ) -> TrendAnalysis:
        """Create a TrendAnalysis value object."""
        
        return TrendAnalysis(
            metric_name=metric_name,
            trend_direction=trend_direction,
            trend_strength=trend_strength,
            period_comparison=period_comparison,
            data_points=data_points,
            analysis=analysis,
            confidence=confidence
        )
    
    def crear_benchmark_comparison(
        self,
        metric_name: str,
        partner_value: float,
        benchmark_value: float,
        benchmark_type: str,
        percentile_rank: Optional[float] = None
    ) -> BenchmarkComparison:
        """Create a BenchmarkComparison value object."""
        
        # Determine comparison result
        if partner_value > benchmark_value:
            comparison_result = "above"
            peer_comparison = "above_average"
        elif partner_value < benchmark_value:
            comparison_result = "below"
            peer_comparison = "below_average"
        else:
            comparison_result = "equal"
            peer_comparison = "average"
        
        return BenchmarkComparison(
            metric_name=metric_name,
            partner_value=partner_value,
            benchmark_value=benchmark_value,
            benchmark_type=benchmark_type,
            comparison_result=comparison_result,
            percentile_rank=percentile_rank or 50.0,
            peer_comparison=peer_comparison
        )