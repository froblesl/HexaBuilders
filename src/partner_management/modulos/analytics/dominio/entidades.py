"""
Analytics domain entities implementation for HexaBuilders.
Implements Analytics Report aggregate root with full business logic.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime

from partner_management.seedwork.dominio.entidades import AggregateRoot
from partner_management.seedwork.dominio.excepciones import DomainException, BusinessRuleException
from .objetos_valor import (
    ReportType, ReportStatus, ReportPeriod, AnalyticsMetrics,
    ReportConfiguration, DataFilter, Insight, TrendAnalysis, BenchmarkComparison
)
from .eventos import (
    AnalyticsReportCreated, AnalyticsReportGenerated, AnalyticsReportFailed,
    AnalyticsReportArchived, AnalyticsInsightDiscovered
)


class AnalyticsReport(AggregateRoot):
    """
    Analytics Report aggregate root.
    
    Represents an analytics report in the HexaBuilders platform.
    Reports aggregate data from partners, campaigns, and commissions
    to provide insights and performance metrics.
    """
    
    def __init__(
        self,
        partner_id: str,
        report_type: ReportType,
        report_period: ReportPeriod,
        configuration: ReportConfiguration,
        report_id: Optional[str] = None,
        data_filter: Optional[DataFilter] = None,
        status: ReportStatus = ReportStatus.PENDING,
        metrics: Optional[AnalyticsMetrics] = None,
        insights: Optional[List[Insight]] = None,
        trends: Optional[List[TrendAnalysis]] = None,
        benchmarks: Optional[List[BenchmarkComparison]] = None
    ):
        super().__init__(report_id)
        
        # Validate required fields
        if not partner_id:
            raise DomainException("Analytics report must have a partner")
        
        # Set attributes
        self._partner_id = partner_id
        self._report_type = report_type
        self._report_period = report_period
        self._configuration = configuration
        self._data_filter = data_filter
        self._status = status
        self._metrics = metrics
        self._insights = insights or []
        self._trends = trends or []
        self._benchmarks = benchmarks or []
        
        # Additional fields
        self._generated_date: Optional[datetime] = None
        self._generated_by: Optional[str] = None
        self._generation_time_seconds: Optional[float] = None
        self._error_message: Optional[str] = None
        
        # Domain event
        self.agregar_evento(AnalyticsReportCreated(
            aggregate_id=self.id,
            partner_id=self._partner_id,
            report_type=self._report_type.value,
            period_start=self._report_period.start_date.isoformat(),
            period_end=self._report_period.end_date.isoformat(),
            period_name=self._report_period.period_name
        ))
    
    @property
    def partner_id(self) -> str:
        return self._partner_id
    
    @property
    def report_type(self) -> ReportType:
        return self._report_type
    
    @property
    def report_period(self) -> ReportPeriod:
        return self._report_period
    
    @property
    def configuration(self) -> ReportConfiguration:
        return self._configuration
    
    @property
    def data_filter(self) -> Optional[DataFilter]:
        return self._data_filter
    
    @property
    def status(self) -> ReportStatus:
        return self._status
    
    @property
    def metrics(self) -> Optional[AnalyticsMetrics]:
        return self._metrics
    
    @property
    def insights(self) -> List[Insight]:
        return self._insights.copy()
    
    @property
    def trends(self) -> List[TrendAnalysis]:
        return self._trends.copy()
    
    @property
    def benchmarks(self) -> List[BenchmarkComparison]:
        return self._benchmarks.copy()
    
    @property
    def generated_date(self) -> Optional[datetime]:
        return self._generated_date
    
    @property
    def generated_by(self) -> Optional[str]:
        return self._generated_by
    
    def iniciar_generacion(self, generated_by: str) -> None:
        """Start report generation process."""
        
        if self._status != ReportStatus.PENDING:
            raise BusinessRuleException("Only pending reports can be generated")
        
        if not generated_by:
            raise DomainException("Report generation must specify who initiated it")
        
        self._status = ReportStatus.GENERATING
        self._generated_by = generated_by
        self._mark_updated()
    
    def completar_generacion(
        self,
        metrics: AnalyticsMetrics,
        generation_time_seconds: float,
        insights: Optional[List[Insight]] = None,
        trends: Optional[List[TrendAnalysis]] = None,
        benchmarks: Optional[List[BenchmarkComparison]] = None
    ) -> None:
        """Complete report generation with results."""
        
        if self._status != ReportStatus.GENERATING:
            raise BusinessRuleException("Only generating reports can be completed")
        
        self._status = ReportStatus.COMPLETED
        self._generated_date = datetime.now()
        self._generation_time_seconds = generation_time_seconds
        self._metrics = metrics
        self._insights = insights or []
        self._trends = trends or []
        self._benchmarks = benchmarks or []
        
        self._mark_updated()
        
        # Domain event
        self.agregar_evento(AnalyticsReportGenerated(
            aggregate_id=self.id,
            partner_id=self._partner_id,
            report_type=self._report_type.value,
            metrics_count=metrics.total_metrics_count(),
            insights_count=len(self._insights),
            generation_time=generation_time_seconds,
            generated_by=self._generated_by
        ))
        
        # Generate events for significant insights
        for insight in self._insights:
            if insight.severity in ['warning', 'critical']:
                self.agregar_evento(AnalyticsInsightDiscovered(
                    aggregate_id=self.id,
                    partner_id=self._partner_id,
                    insight_type=insight.insight_type,
                    insight_title=insight.title,
                    insight_description=insight.description,
                    severity=insight.severity,
                    confidence=insight.confidence
                ))
    
    def fallar_generacion(self, error_message: str) -> None:
        """Mark report generation as failed."""
        
        if self._status != ReportStatus.GENERATING:
            raise BusinessRuleException("Only generating reports can be marked as failed")
        
        if not error_message:
            raise DomainException("Error message is required for failed reports")
        
        self._status = ReportStatus.FAILED
        self._error_message = error_message
        
        self._mark_updated()
        
        # Domain event
        self.agregar_evento(AnalyticsReportFailed(
            aggregate_id=self.id,
            partner_id=self._partner_id,
            report_type=self._report_type.value,
            error_message=error_message,
            generated_by=self._generated_by
        ))
    
    def archivar(self, archived_by: str, archive_reason: Optional[str] = None) -> None:
        """Archive the report."""
        
        if self._status == ReportStatus.ARCHIVED:
            return  # Already archived
        
        if self._status not in [ReportStatus.COMPLETED, ReportStatus.FAILED]:
            raise BusinessRuleException("Only completed or failed reports can be archived")
        
        if not archived_by:
            raise DomainException("Archive operation must specify who archived")
        
        old_status = self._status
        self._status = ReportStatus.ARCHIVED
        
        self._mark_updated()
        
        # Domain event
        self.agregar_evento(AnalyticsReportArchived(
            aggregate_id=self.id,
            partner_id=self._partner_id,
            report_type=self._report_type.value,
            archived_by=archived_by,
            archive_reason=archive_reason or "Manual archive"
        ))
    
    def agregar_insight(self, insight: Insight) -> None:
        """Add new insight to the report."""
        
        if self._status != ReportStatus.COMPLETED:
            raise BusinessRuleException("Can only add insights to completed reports")
        
        self._insights.append(insight)
        self._mark_updated()
        
        # Generate event for significant insights
        if insight.severity in ['warning', 'critical']:
            self.agregar_evento(AnalyticsInsightDiscovered(
                aggregate_id=self.id,
                partner_id=self._partner_id,
                insight_type=insight.insight_type,
                insight_title=insight.title,
                insight_description=insight.description,
                severity=insight.severity,
                confidence=insight.confidence
            ))
    
    def obtener_insight_por_tipo(self, insight_type: str) -> List[Insight]:
        """Get insights by type."""
        return [insight for insight in self._insights if insight.insight_type == insight_type]
    
    def obtener_insights_criticos(self) -> List[Insight]:
        """Get critical insights."""
        return [insight for insight in self._insights if insight.severity == 'critical']
    
    def obtener_trend_por_metrica(self, metric_name: str) -> Optional[TrendAnalysis]:
        """Get trend analysis for specific metric."""
        for trend in self._trends:
            if trend.metric_name == metric_name:
                return trend
        return None
    
    def obtener_benchmark_por_metrica(self, metric_name: str) -> Optional[BenchmarkComparison]:
        """Get benchmark comparison for specific metric."""
        for benchmark in self._benchmarks:
            if benchmark.metric_name == metric_name:
                return benchmark
        return None
    
    def esta_actualizado(self) -> bool:
        """Check if report data is up to date."""
        if not self._generated_date:
            return False
        
        # Consider report outdated if generated more than 24 hours ago
        hours_since_generation = (datetime.now() - self._generated_date).total_seconds() / 3600
        return hours_since_generation < 24
    
    def puede_ser_regenerado(self) -> bool:
        """Check if report can be regenerated."""
        return self._status in [ReportStatus.COMPLETED, ReportStatus.FAILED]
    
    def get_summary(self) -> Dict[str, Any]:
        """Get report summary."""
        
        return {
            'id': self.id,
            'partner_id': self._partner_id,
            'report_type': self._report_type.value,
            'status': self._status.value,
            'report_period': {
                'start_date': self._report_period.start_date.isoformat(),
                'end_date': self._report_period.end_date.isoformat(),
                'period_name': self._report_period.period_name,
                'duration_days': self._report_period.duration_in_days()
            },
            'configuration': {
                'include_charts': self._configuration.include_charts,
                'include_comparisons': self._configuration.include_comparisons,
                'include_trends': self._configuration.include_trends,
                'chart_types': self._configuration.chart_types,
                'export_formats': self._configuration.export_formats
            },
            'generation_info': {
                'generated_date': self._generated_date.isoformat() if self._generated_date else None,
                'generated_by': self._generated_by,
                'generation_time_seconds': self._generation_time_seconds,
                'error_message': self._error_message
            },
            'content_summary': {
                'metrics_count': self._metrics.total_metrics_count() if self._metrics else 0,
                'insights_count': len(self._insights),
                'critical_insights_count': len(self.obtener_insights_criticos()),
                'trends_count': len(self._trends),
                'benchmarks_count': len(self._benchmarks)
            },
            'timestamps': {
                'created_at': self.created_at.isoformat(),
                'updated_at': self.updated_at.isoformat()
            },
            'version': self.version,
            'is_up_to_date': self.esta_actualizado()
        }
    
    def validate(self) -> None:
        """Validate report state."""
        
        if not self._partner_id:
            raise DomainException("Report must be assigned to a partner")
        
        if not self._report_type or not self._report_period:
            raise DomainException("Report must have type and period")
        
        if not self._configuration:
            raise DomainException("Report must have configuration")
        
        # Validate status-specific requirements
        if self._status == ReportStatus.COMPLETED:
            if not self._metrics or not self._generated_date:
                raise DomainException("Completed report must have metrics and generation date")
        
        if self._status == ReportStatus.FAILED:
            if not self._error_message:
                raise DomainException("Failed report must have error message")
    
    def __repr__(self) -> str:
        return (f"AnalyticsReport(id={self.id}, partner_id={self._partner_id}, "
                f"type={self._report_type.value}, status={self._status.value})")