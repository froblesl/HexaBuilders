"""
Get Analytics Report query implementation for HexaBuilders.
"""

import logging
from dataclasses import dataclass
from typing import Dict, Any

from .....seedwork.aplicacion.queries import ejecutar_query
from .....seedwork.infraestructura.uow import UnitOfWork
from .....seedwork.dominio.excepciones import DomainException
from .base import QueryAnalytics, AnalyticsQueryResult

logger = logging.getLogger(__name__)


@dataclass
class ObtenerReporte(QueryAnalytics):
    """Query to get analytics report by ID."""
    
    report_id: str
    include_full_data: bool = True


class ReporteResult(AnalyticsQueryResult):
    """Analytics report query result."""
    
    def __init__(self, report_data: Dict[str, Any]):
        self.report_data = report_data
    
    def __dict__(self):
        return self.report_data


@ejecutar_query.register
def handle_obtener_reporte(query: ObtenerReporte) -> ReporteResult:
    """
    Handle GetReport query.
    """
    logger.info(f"Executing GetReport query for report: {query.report_id}")
    
    try:
        # Validate input data
        _validate_obtener_reporte_query(query)
        
        # Use Unit of Work to fetch data
        with UnitOfWork() as uow:
            repo = uow.analytics
            
            # Get report
            report = repo.obtener_por_id(query.report_id)
            if not report:
                raise DomainException(f"Analytics report with ID {query.report_id} not found")
            
            # Get report data based on requested detail level
            if query.include_full_data:
                report_data = _get_full_report_data(report)
            else:
                report_data = report.get_summary()
            
            logger.info(f"Analytics report retrieved successfully: {report.id}")
            return ReporteResult(report_data)
    
    except Exception as e:
        logger.error(f"Failed to get analytics report: {str(e)}")
        raise


def _get_full_report_data(report) -> Dict[str, Any]:
    """Get full report data including all details."""
    
    base_data = report.get_summary()
    
    # Add detailed metrics
    if report.metrics:
        base_data['metrics'] = {
            'total_campaigns': report.metrics.total_campaigns,
            'active_campaigns': report.metrics.active_campaigns,
            'completed_campaigns': report.metrics.completed_campaigns,
            'total_commissions': report.metrics.total_commissions,
            'total_commission_amount': str(report.metrics.total_commission_amount),
            'average_commission': str(report.metrics.average_commission),
            'partner_rating': report.metrics.partner_rating,
            'conversion_rate': report.metrics.conversion_rate,
            'performance_score': report.metrics.performance_score
        }
    
    # Add detailed insights
    base_data['insights'] = [
        {
            'type': insight.insight_type,
            'title': insight.title,
            'description': insight.description,
            'severity': insight.severity,
            'confidence': insight.confidence,
            'actionable': insight.actionable,
            'recommendations': insight.recommendations
        }
        for insight in report.insights
    ]
    
    # Add trend analysis
    base_data['trends'] = [
        {
            'metric_name': trend.metric_name,
            'trend_direction': trend.trend_direction,
            'trend_strength': trend.trend_strength,
            'period_comparison': trend.period_comparison,
            'data_points': trend.data_points,
            'analysis': trend.analysis,
            'confidence': trend.confidence
        }
        for trend in report.trends
    ]
    
    # Add benchmark comparisons
    base_data['benchmarks'] = [
        {
            'metric_name': benchmark.metric_name,
            'partner_value': benchmark.partner_value,
            'benchmark_value': benchmark.benchmark_value,
            'benchmark_type': benchmark.benchmark_type,
            'comparison_result': benchmark.comparison_result,
            'percentile_rank': benchmark.percentile_rank,
            'peer_comparison': benchmark.peer_comparison
        }
        for benchmark in report.benchmarks
    ]
    
    return base_data


def _validate_obtener_reporte_query(query: ObtenerReporte):
    """Validate GetReport query data."""
    
    if not query.report_id:
        raise DomainException("Report ID is required")
    
    if len(query.report_id.strip()) < 1:
        raise DomainException("Valid report ID is required")
    
    logger.debug("GetReport query validation passed")