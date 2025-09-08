"""
Get All Analytics Reports query implementation for HexaBuilders.
"""

import logging
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

from partner_management.seedwork.aplicacion.queries import ejecutar_query
from partner_management.seedwork.infraestructura.uow import UnitOfWork
from partner_management.seedwork.dominio.excepciones import DomainException
from .base import QueryAnalytics, AnalyticsQueryResult

logger = logging.getLogger(__name__)


@dataclass
class ObtenerTodosReportes(QueryAnalytics):
    """Query to get all analytics reports with optional filtering."""
    
    partner_id: Optional[str] = None
    report_type: Optional[str] = None
    status: Optional[str] = None
    limit: int = 100
    offset: int = 0
    include_summary_only: bool = True


class ReportesListResult(AnalyticsQueryResult):
    """Analytics reports list query result."""
    
    def __init__(self, reports_data: List[Dict[str, Any]], total_count: int):
        self.reports = reports_data
        self.total_count = total_count
        self.count = len(reports_data)


@ejecutar_query.register
def handle_obtener_todos_reportes(query: ObtenerTodosReportes) -> ReportesListResult:
    """
    Handle GetAllReports query.
    """
    logger.info(f"Executing GetAllReports query with filters - partner_id: {query.partner_id}, status: {query.status}")
    
    try:
        # Validate input data
        _validate_obtener_todos_reportes_query(query)
        
        # Use Unit of Work to fetch data
        with UnitOfWork() as uow:
            repo = uow.analytics
            
            # Build filters
            filters = {}
            if query.partner_id:
                filters['partner_id'] = query.partner_id
            if query.status:
                filters['status'] = query.status
            if query.report_type:
                filters['report_type'] = query.report_type
            
            # Get reports with pagination
            reports = repo.obtener_todos_con_filtros(
                filters=filters,
                limit=query.limit,
                offset=query.offset
            )
            
            # Get total count
            total_count = repo.contar_con_filtros(filters)
            
            # Convert to appropriate format
            if query.include_summary_only:
                reports_data = [report.get_summary() for report in reports]
            else:
                reports_data = [_get_detailed_report_data(report) for report in reports]
            
            logger.info(f"Retrieved {len(reports)} analytics reports out of {total_count} total")
            return ReportesListResult(reports_data, total_count)
    
    except Exception as e:
        logger.error(f"Failed to get analytics reports: {str(e)}")
        raise


def _get_detailed_report_data(report) -> Dict[str, Any]:
    """Get detailed report data for list view."""
    
    summary = report.get_summary()
    
    # Add key metrics preview
    if report.metrics:
        summary['metrics_preview'] = {
            'total_campaigns': report.metrics.total_campaigns,
            'total_commissions': report.metrics.total_commissions,
            'total_commission_amount': str(report.metrics.total_commission_amount),
            'performance_score': report.metrics.performance_score
        }
    
    # Add insights count by severity
    insights_by_severity = {}
    for insight in report.insights:
        severity = insight.severity
        insights_by_severity[severity] = insights_by_severity.get(severity, 0) + 1
    
    summary['insights_by_severity'] = insights_by_severity
    
    # Add key indicators
    summary['key_indicators'] = {
        'has_critical_insights': len(report.obtener_insights_criticos()) > 0,
        'is_up_to_date': report.esta_actualizado(),
        'generation_success': report.status.value == 'COMPLETED'
    }
    
    return summary


def _validate_obtener_todos_reportes_query(query: ObtenerTodosReportes):
    """Validate GetAllReports query data."""
    
    if query.limit <= 0 or query.limit > 1000:
        raise DomainException("Limit must be between 1 and 1000")
    
    if query.offset < 0:
        raise DomainException("Offset cannot be negative")
    
    if query.status:
        valid_statuses = ['PENDING', 'GENERATING', 'COMPLETED', 'FAILED', 'ARCHIVED']
        if query.status not in valid_statuses:
            raise DomainException(f"Status must be one of: {valid_statuses}")
    
    if query.report_type:
        valid_types = ['PARTNER_PERFORMANCE', 'COMMISSION_SUMMARY', 'CAMPAIGN_ANALYSIS', 'COMPREHENSIVE']
        if query.report_type not in valid_types:
            raise DomainException(f"Report type must be one of: {valid_types}")
    
    logger.debug("GetAllReports query validation passed")