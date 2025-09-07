"""
Regenerate Analytics Report command implementation for HexaBuilders.
"""

import logging
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

from .....seedwork.aplicacion.comandos import ejecutar_comando
from .....seedwork.infraestructura.uow import UnitOfWork
from .....seedwork.dominio.excepciones import DomainException
from .base import ComandoAnalytics
from .generar_reporte import _collect_analytics_metrics, _generate_insights, _analyze_trends, _generate_benchmarks

logger = logging.getLogger(__name__)


@dataclass
class RegenerarReporte(ComandoAnalytics):
    """Command to regenerate an analytics report with fresh data."""
    
    report_id: str
    regenerated_by: str
    update_configuration: bool = False
    include_trends: Optional[bool] = None
    include_comparisons: Optional[bool] = None


@ejecutar_comando.register
def handle_regenerar_reporte(comando: RegenerarReporte) -> str:
    """
    Handle RegenerateReport command.
    """
    logger.info(f"Executing RegenerateReport command for report: {comando.report_id}")
    
    try:
        # Validate input data
        _validate_regenerar_reporte_command(comando)
        
        # Use Unit of Work to persist
        with UnitOfWork() as uow:
            repo = uow.analytics
            
            # Get existing report
            report = repo.obtener_por_id(comando.report_id)
            if not report:
                raise DomainException(f"Analytics report with ID {comando.report_id} not found")
            
            # Check if report can be regenerated
            if not report.puede_ser_regenerado():
                raise DomainException("Report cannot be regenerated in current state")
            
            # Update configuration if requested
            if comando.update_configuration:
                if comando.include_trends is not None:
                    report._configuration.include_trends = comando.include_trends
                if comando.include_comparisons is not None:
                    report._configuration.include_comparisons = comando.include_comparisons
            
            # Start regeneration process
            report.iniciar_generacion(comando.regenerated_by)
            
            # Generate the report data
            try:
                start_time = datetime.now()
                
                # Collect fresh data
                metrics = _collect_analytics_metrics(report.partner_id, report.report_period, uow)
                insights = _generate_insights(metrics, report.report_type)
                trends = _analyze_trends(report.partner_id, report.report_period, uow) if report.configuration.include_trends else []
                benchmarks = _generate_benchmarks(metrics) if report.configuration.include_comparisons else []
                
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
                # Mark regeneration as failed
                report.fallar_generacion(f"Regeneration failed: {str(e)}")
                logger.error(f"Report regeneration failed: {str(e)}")
            
            # Update report
            repo.actualizar(report)
            
            # Commit transaction - this will also publish domain events
            uow.commit()
            
            logger.info(f"Analytics report regenerated successfully: {report.id}")
            return report.id
    
    except Exception as e:
        logger.error(f"Failed to regenerate report: {str(e)}")
        raise


def _validate_regenerar_reporte_command(comando: RegenerarReporte):
    """Validate RegenerateReport command data."""
    
    if not comando.report_id:
        raise DomainException("Report ID is required")
    
    if not comando.regenerated_by or len(comando.regenerated_by.strip()) < 2:
        raise DomainException("User performing regeneration is required")
    
    logger.debug("RegenerateReport command validation passed")