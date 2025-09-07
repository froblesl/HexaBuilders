"""
Generate Analytics Report command implementation for HexaBuilders.
"""

import logging
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime

from .....seedwork.aplicacion.comandos import ejecutar_comando
from .....seedwork.infraestructura.uow import UnitOfWork
from .....seedwork.dominio.excepciones import DomainException
from ...dominio.entidades import AnalyticsReport
from ...dominio.objetos_valor import (
    ReportType, ReportPeriod, ReportConfiguration, DataFilter,
    AnalyticsMetrics, Insight, TrendAnalysis, BenchmarkComparison
)
from ...infraestructura.fabricas import FabricaAnalytics
from .base import ComandoAnalytics

logger = logging.getLogger(__name__)


@dataclass
class GenerarReporte(ComandoAnalytics):
    """Command to generate an analytics report."""
    
    partner_id: str
    report_type: str
    period_start: datetime
    period_end: datetime
    period_name: str
    include_charts: bool = True
    include_comparisons: bool = True
    include_trends: bool = True
    chart_types: Optional[List[str]] = None
    export_formats: Optional[List[str]] = None
    data_filters: Optional[Dict[str, Any]] = None
    generated_by: str = "system"


@ejecutar_comando.register
def handle_generar_reporte(comando: GenerarReporte) -> str:
    """
    Handle GenerateReport command.
    """
    logger.info(f"Executing GenerateReport command for partner: {comando.partner_id}")
    
    try:
        # Validate input data
        _validate_generar_reporte_command(comando)
        
        # Create value objects
        report_type = ReportType(comando.report_type)
        
        report_period = ReportPeriod(
            start_date=comando.period_start,
            end_date=comando.period_end,
            period_name=comando.period_name
        )
        
        configuration = ReportConfiguration(
            include_charts=comando.include_charts,
            include_comparisons=comando.include_comparisons,
            include_trends=comando.include_trends,
            chart_types=comando.chart_types or ['bar', 'line', 'pie'],
            export_formats=comando.export_formats or ['pdf', 'json']
        )
        
        data_filter = None
        if comando.data_filters:
            data_filter = DataFilter(**comando.data_filters)
        
        # Create report using factory
        fabrica = FabricaAnalytics()
        report = fabrica.crear_analytics_report(
            partner_id=comando.partner_id,
            report_type=report_type,
            report_period=report_period,
            configuration=configuration,
            data_filter=data_filter
        )
        
        # Use Unit of Work to persist and generate
        with UnitOfWork() as uow:
            repo = uow.analytics
            
            # Check if partner exists
            partner_repo = uow.partners
            partner = partner_repo.obtener_por_id(comando.partner_id)
            if not partner:
                raise DomainException(f"Partner with ID {comando.partner_id} not found")
            
            # Save report
            repo.agregar(report)
            
            # Start generation process
            report.iniciar_generacion(comando.generated_by)
            
            # Generate the actual report data
            try:
                start_time = datetime.now()
                
                # Collect data from different modules
                metrics = _collect_analytics_metrics(comando.partner_id, report_period, uow)
                insights = _generate_insights(metrics, report_type)
                trends = _analyze_trends(comando.partner_id, report_period, uow) if comando.include_trends else []
                benchmarks = _generate_benchmarks(metrics) if comando.include_comparisons else []
                
                generation_time = (datetime.now() - start_time).total_seconds()
                
                # Complete report generation
                report.completar_generacion(
                    metrics=metrics,
                    generation_time_seconds=generation_time,
                    insights=insights,
                    trends=trends,
                    benchmarks=benchmarks
                )
                
            except Exception as e:
                # Mark generation as failed
                report.fallar_generacion(str(e))
                logger.error(f"Report generation failed: {str(e)}")
            
            # Update report
            repo.actualizar(report)
            
            # Commit transaction - this will also publish domain events
            uow.commit()
            
            logger.info(f"Analytics report created: {report.id}")
            return report.id
    
    except Exception as e:
        logger.error(f"Failed to generate report: {str(e)}")
        raise


def _collect_analytics_metrics(partner_id: str, report_period: ReportPeriod, uow) -> AnalyticsMetrics:
    """Collect metrics from different modules."""
    
    # Get partner data
    partner_repo = uow.partners
    partner = partner_repo.obtener_por_id(partner_id)
    
    # Get campaigns data
    campaigns_repo = uow.campaigns
    partner_campaigns = campaigns_repo.obtener_por_partner_id(partner_id)
    active_campaigns = [c for c in partner_campaigns if c.status.value == 'ACTIVO']
    
    # Get commissions data
    commissions_repo = uow.commissions
    partner_commissions = commissions_repo.obtener_por_partner_id(partner_id)
    paid_commissions = [c for c in partner_commissions if c.status.value == 'PAID']
    
    # Calculate metrics
    from decimal import Decimal
    
    total_commissions_earned = sum(
        c.commission_amount.amount for c in paid_commissions
    )
    
    return AnalyticsMetrics(
        total_campaigns=len(partner_campaigns),
        active_campaigns=len(active_campaigns),
        completed_campaigns=len([c for c in partner_campaigns if hasattr(c, 'completion_date') and c.completion_date]),
        total_commissions=len(partner_commissions),
        total_commission_amount=total_commissions_earned,
        average_commission=total_commissions_earned / len(partner_commissions) if partner_commissions else Decimal('0'),
        partner_rating=getattr(partner, 'rating', 0.0) if partner else 0.0,
        conversion_rate=0.85,  # Mock calculation
        performance_score=0.78  # Mock calculation
    )


def _generate_insights(metrics: AnalyticsMetrics, report_type: ReportType) -> List[Insight]:
    """Generate insights based on metrics."""
    
    insights = []
    
    # Performance insights
    if metrics.performance_score < 0.6:
        insights.append(Insight(
            insight_type="performance",
            title="Low Performance Score",
            description=f"Partner performance score is {metrics.performance_score:.2f}, below recommended threshold",
            severity="warning",
            confidence=0.9,
            actionable=True,
            recommendations=["Review campaign strategies", "Analyze successful campaigns", "Consider training programs"]
        ))
    
    # Commission insights
    if metrics.total_commissions > 0 and metrics.average_commission < 100:
        insights.append(Insight(
            insight_type="commission",
            title="Low Average Commission",
            description=f"Average commission of ${metrics.average_commission} is below industry average",
            severity="info",
            confidence=0.8,
            actionable=True,
            recommendations=["Focus on higher-value campaigns", "Improve conversion rates", "Explore premium partnerships"]
        ))
    
    # Campaign insights
    if metrics.total_campaigns > 0:
        completion_rate = metrics.completed_campaigns / metrics.total_campaigns
        if completion_rate < 0.7:
            insights.append(Insight(
                insight_type="campaign",
                title="Low Campaign Completion Rate",
                description=f"Campaign completion rate is {completion_rate:.2f}, indicating potential issues",
                severity="warning",
                confidence=0.85,
                actionable=True,
                recommendations=["Review campaign planning", "Improve resource allocation", "Set realistic goals"]
            ))
    
    return insights


def _analyze_trends(partner_id: str, report_period: ReportPeriod, uow) -> List[TrendAnalysis]:
    """Analyze trends over time."""
    
    trends = []
    
    # Mock trend analysis - in real implementation, this would analyze historical data
    trends.append(TrendAnalysis(
        metric_name="commission_amount",
        trend_direction="increasing",
        trend_strength=0.75,
        period_comparison="month_over_month",
        data_points=[100, 120, 150, 180, 200],  # Mock data
        analysis="Commission amounts showing steady upward trend",
        confidence=0.85
    ))
    
    trends.append(TrendAnalysis(
        metric_name="campaign_success_rate",
        trend_direction="stable",
        trend_strength=0.3,
        period_comparison="month_over_month",
        data_points=[0.8, 0.82, 0.81, 0.83, 0.82],  # Mock data
        analysis="Campaign success rate remains stable with minor fluctuations",
        confidence=0.7
    ))
    
    return trends


def _generate_benchmarks(metrics: AnalyticsMetrics) -> List[BenchmarkComparison]:
    """Generate benchmark comparisons."""
    
    benchmarks = []
    
    # Performance benchmark
    benchmarks.append(BenchmarkComparison(
        metric_name="performance_score",
        partner_value=metrics.performance_score,
        benchmark_value=0.75,
        benchmark_type="industry_average",
        comparison_result="below" if metrics.performance_score < 0.75 else "above",
        percentile_rank=65.0,  # Mock percentile
        peer_comparison="average"
    ))
    
    # Commission benchmark
    if metrics.total_commissions > 0:
        benchmarks.append(BenchmarkComparison(
            metric_name="average_commission",
            partner_value=float(metrics.average_commission),
            benchmark_value=150.0,
            benchmark_type="platform_average",
            comparison_result="below" if float(metrics.average_commission) < 150 else "above",
            percentile_rank=45.0,  # Mock percentile
            peer_comparison="below_average"
        ))
    
    return benchmarks


def _validate_generar_reporte_command(comando: GenerarReporte):
    """Validate GenerateReport command data."""
    
    if not comando.partner_id:
        raise DomainException("Partner ID is required")
    
    valid_report_types = ['PARTNER_PERFORMANCE', 'COMMISSION_SUMMARY', 'CAMPAIGN_ANALYSIS', 'COMPREHENSIVE']
    if comando.report_type not in valid_report_types:
        raise DomainException(f"Report type must be one of: {valid_report_types}")
    
    if not comando.period_start or not comando.period_end:
        raise DomainException("Report period start and end dates are required")
    
    if comando.period_start >= comando.period_end:
        raise DomainException("Period start date must be before end date")
    
    if not comando.period_name or len(comando.period_name.strip()) < 2:
        raise DomainException("Period name must be at least 2 characters")
    
    if comando.chart_types:
        valid_chart_types = ['bar', 'line', 'pie', 'scatter', 'area']
        for chart_type in comando.chart_types:
            if chart_type not in valid_chart_types:
                raise DomainException(f"Chart type '{chart_type}' is not supported")
    
    if comando.export_formats:
        valid_formats = ['pdf', 'json', 'csv', 'xlsx']
        for format_type in comando.export_formats:
            if format_type not in valid_formats:
                raise DomainException(f"Export format '{format_type}' is not supported")
    
    logger.debug("GenerateReport command validation passed")