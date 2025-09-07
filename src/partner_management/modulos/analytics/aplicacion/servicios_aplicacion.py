"""
Application services for Analytics module in HexaBuilders.
Implements CQRS pattern with command and query separation.
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from ....seedwork.aplicacion.servicios import ServicioAplicacion
from ....seedwork.infraestructura.uow import UnitOfWork
from ....seedwork.dominio.excepciones import DomainException

from .comandos.generar_reporte import GenerarReporte, handle_generar_reporte
from .comandos.archivar_reporte import ArchivarReporte, handle_archivar_reporte
from .comandos.regenerar_reporte import RegenerarReporte, handle_regenerar_reporte

from .queries.obtener_reporte import ObtenerReporte, handle_obtener_reporte
from .queries.obtener_todos_reportes import ObtenerTodosReportes, handle_obtener_todos_reportes
from .queries.obtener_profile_360 import ObtenerProfile360, handle_obtener_profile_360

logger = logging.getLogger(__name__)


class ServicioAnalytics(ServicioAplicacion):
    """
    Application service for Analytics operations.
    Coordinates CQRS operations and business workflows.
    """
    
    def __init__(self):
        super().__init__()
        self._logger = logging.getLogger(self.__class__.__name__)
    
    # Command operations
    
    def generar_reporte(
        self,
        partner_id: str,
        report_type: str,
        period_start: datetime,
        period_end: datetime,
        period_name: str,
        include_charts: bool = True,
        include_comparisons: bool = True,
        include_trends: bool = True,
        chart_types: Optional[List[str]] = None,
        export_formats: Optional[List[str]] = None,
        data_filters: Optional[Dict[str, Any]] = None,
        generated_by: str = "system"
    ) -> str:
        """
        Generate a new analytics report.
        """
        self._logger.info(f"Generating analytics report for partner: {partner_id}")
        
        comando = GenerarReporte(
            partner_id=partner_id,
            report_type=report_type,
            period_start=period_start,
            period_end=period_end,
            period_name=period_name,
            include_charts=include_charts,
            include_comparisons=include_comparisons,
            include_trends=include_trends,
            chart_types=chart_types,
            export_formats=export_formats,
            data_filters=data_filters,
            generated_by=generated_by
        )
        
        return handle_generar_reporte(comando)
    
    def archivar_reporte(
        self,
        report_id: str,
        archived_by: str,
        archive_reason: Optional[str] = None
    ) -> str:
        """
        Archive an analytics report.
        """
        self._logger.info(f"Archiving analytics report: {report_id}")
        
        comando = ArchivarReporte(
            report_id=report_id,
            archived_by=archived_by,
            archive_reason=archive_reason
        )
        
        return handle_archivar_reporte(comando)
    
    def regenerar_reporte(
        self,
        report_id: str,
        regenerated_by: str,
        update_configuration: bool = False,
        include_trends: Optional[bool] = None,
        include_comparisons: Optional[bool] = None
    ) -> str:
        """
        Regenerate an analytics report with fresh data.
        """
        self._logger.info(f"Regenerating analytics report: {report_id}")
        
        comando = RegenerarReporte(
            report_id=report_id,
            regenerated_by=regenerated_by,
            update_configuration=update_configuration,
            include_trends=include_trends,
            include_comparisons=include_comparisons
        )
        
        return handle_regenerar_reporte(comando)
    
    # Query operations
    
    def obtener_reporte(
        self,
        report_id: str,
        include_full_data: bool = True
    ) -> Dict[str, Any]:
        """
        Get analytics report by ID.
        """
        self._logger.info(f"Getting analytics report: {report_id}")
        
        query = ObtenerReporte(
            report_id=report_id,
            include_full_data=include_full_data
        )
        result = handle_obtener_reporte(query)
        
        return result.report_data
    
    def obtener_todos_reportes(
        self,
        partner_id: Optional[str] = None,
        report_type: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        include_summary_only: bool = True
    ) -> Dict[str, Any]:
        """
        Get all analytics reports with optional filtering.
        """
        self._logger.info(f"Getting analytics reports with filters - partner_id: {partner_id}, status: {status}")
        
        query = ObtenerTodosReportes(
            partner_id=partner_id,
            report_type=report_type,
            status=status,
            limit=limit,
            offset=offset,
            include_summary_only=include_summary_only
        )
        result = handle_obtener_todos_reportes(query)
        
        return {
            'reports': result.reports,
            'total_count': result.total_count,
            'count': result.count
        }
    
    def obtener_profile_360(
        self,
        partner_id: str,
        period_months: int = 6,
        include_predictions: bool = True,
        include_recommendations: bool = True
    ) -> Dict[str, Any]:
        """
        Get comprehensive 360-degree partner analytics profile.
        """
        self._logger.info(f"Getting 360-degree profile for partner: {partner_id}")
        
        query = ObtenerProfile360(
            partner_id=partner_id,
            period_months=period_months,
            include_predictions=include_predictions,
            include_recommendations=include_recommendations
        )
        result = handle_obtener_profile_360(query)
        
        return result.profile_data
    
    # Business workflows
    
    def generar_reporte_automatico(
        self,
        partner_id: str,
        report_type: str = "COMPREHENSIVE",
        period_days: int = 30
    ) -> str:
        """
        Generate an automatic periodic report for a partner.
        """
        self._logger.info(f"Generating automatic report for partner: {partner_id}")
        
        try:
            # Calculate period
            end_date = datetime.now()
            start_date = end_date - timedelta(days=period_days)
            
            return self.generar_reporte(
                partner_id=partner_id,
                report_type=report_type,
                period_start=start_date,
                period_end=end_date,
                period_name=f"Automatic {report_type.title()} Report - {end_date.strftime('%Y-%m-%d')}",
                generated_by="auto_scheduler"
            )
            
        except Exception as e:
            self._logger.error(f"Failed to generate automatic report: {str(e)}")
            raise DomainException(f"Automatic report generation failed: {str(e)}")
    
    def generar_reportes_batch(
        self,
        partner_ids: List[str],
        report_type: str = "PARTNER_PERFORMANCE",
        period_days: int = 30,
        generated_by: str = "batch_system"
    ) -> Dict[str, Any]:
        """
        Generate reports for multiple partners in batch.
        """
        self._logger.info(f"Batch generating reports for {len(partner_ids)} partners")
        
        successful = []
        failed = []
        
        # Calculate common period
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days)
        
        for partner_id in partner_ids:
            try:
                report_id = self.generar_reporte(
                    partner_id=partner_id,
                    report_type=report_type,
                    period_start=start_date,
                    period_end=end_date,
                    period_name=f"Batch {report_type.title()} Report - {end_date.strftime('%Y-%m')}",
                    generated_by=generated_by
                )
                successful.append({
                    'partner_id': partner_id,
                    'report_id': report_id
                })
            except Exception as e:
                failed.append({
                    'partner_id': partner_id,
                    'error': str(e)
                })
                self._logger.error(f"Failed to generate report for partner {partner_id}: {str(e)}")
        
        return {
            'successful': successful,
            'failed': failed,
            'success_count': len(successful),
            'failure_count': len(failed)
        }
    
    def obtener_insights_criticos(
        self,
        partner_id: Optional[str] = None,
        period_days: int = 30
    ) -> Dict[str, Any]:
        """
        Get critical insights across all recent reports.
        """
        self._logger.info(f"Getting critical insights for partner: {partner_id}")
        
        try:
            # Get recent reports
            reports_data = self.obtener_todos_reportes(
                partner_id=partner_id,
                status="COMPLETED",
                limit=50,
                include_summary_only=False
            )
            
            critical_insights = []
            warning_insights = []
            
            # Extract insights from all reports
            for report in reports_data['reports']:
                if 'insights' in report:
                    for insight in report['insights']:
                        if insight['severity'] == 'critical':
                            critical_insights.append({
                                'report_id': report['id'],
                                'partner_id': report['partner_id'],
                                'insight': insight,
                                'generated_at': report['generation_info']['generated_date']
                            })
                        elif insight['severity'] == 'warning':
                            warning_insights.append({
                                'report_id': report['id'],
                                'partner_id': report['partner_id'],
                                'insight': insight,
                                'generated_at': report['generation_info']['generated_date']
                            })
            
            return {
                'critical_insights': critical_insights,
                'warning_insights': warning_insights,
                'critical_count': len(critical_insights),
                'warning_count': len(warning_insights),
                'analyzed_reports': len(reports_data['reports'])
            }
            
        except Exception as e:
            self._logger.error(f"Failed to get critical insights: {str(e)}")
            raise DomainException(f"Critical insights retrieval failed: {str(e)}")
    
    def generar_dashboard_data(
        self,
        partner_id: Optional[str] = None,
        period_days: int = 90
    ) -> Dict[str, Any]:
        """
        Generate dashboard data with key metrics and trends.
        """
        self._logger.info(f"Generating dashboard data for partner: {partner_id}")
        
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=period_days)
            
            # Get summary metrics
            if partner_id:
                profile_data = self.obtener_profile_360(
                    partner_id=partner_id,
                    period_months=period_days // 30,
                    include_predictions=True,
                    include_recommendations=False
                )
                
                dashboard_data = {
                    'partner_overview': profile_data['partner_overview'],
                    'key_metrics': profile_data['performance_metrics'],
                    'trends': profile_data['trend_analysis'],
                    'predictions': profile_data.get('predictions', {}),
                    'latest_insights': self._get_latest_insights(partner_id, 5),
                    'health_score': self._calculate_health_score(profile_data)
                }
            else:
                # Platform-wide dashboard
                dashboard_data = self._generate_platform_dashboard(start_date, end_date)
            
            return dashboard_data
            
        except Exception as e:
            self._logger.error(f"Failed to generate dashboard data: {str(e)}")
            raise DomainException(f"Dashboard data generation failed: {str(e)}")
    
    def obtener_benchmarks_comparativos(
        self,
        partner_id: str,
        comparison_type: str = "platform_average"
    ) -> Dict[str, Any]:
        """
        Get comparative benchmarks for a partner.
        """
        self._logger.info(f"Getting comparative benchmarks for partner: {partner_id}")
        
        try:
            # Get partner 360 profile
            profile_data = self.obtener_profile_360(
                partner_id=partner_id,
                include_predictions=False,
                include_recommendations=False
            )
            
            # Get platform averages for comparison
            platform_data = self._get_platform_averages()
            
            # Generate comparisons
            benchmarks = {
                'partner_metrics': profile_data['performance_metrics'],
                'platform_averages': platform_data,
                'comparisons': self._calculate_benchmark_comparisons(
                    profile_data['performance_metrics'],
                    platform_data
                ),
                'percentile_rankings': self._calculate_percentile_rankings(partner_id),
                'peer_group_comparison': self._get_peer_group_comparison(partner_id)
            }
            
            return benchmarks
            
        except Exception as e:
            self._logger.error(f"Failed to get benchmarks: {str(e)}")
            raise DomainException(f"Benchmarks retrieval failed: {str(e)}")
    
    def _get_latest_insights(self, partner_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get latest insights for partner."""
        
        # Get recent completed reports
        reports_data = self.obtener_todos_reportes(
            partner_id=partner_id,
            status="COMPLETED",
            limit=10,
            include_summary_only=False
        )
        
        insights = []
        for report in reports_data['reports']:
            if 'insights' in report:
                for insight in report['insights']:
                    insights.append({
                        'insight': insight,
                        'report_id': report['id'],
                        'generated_at': report['generation_info']['generated_date']
                    })
        
        # Sort by generation date and return latest
        insights.sort(key=lambda x: x['generated_at'], reverse=True)
        return insights[:limit]
    
    def _calculate_health_score(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall partner health score."""
        
        performance_metrics = profile_data.get('performance_metrics', {})
        overall_score = performance_metrics.get('overall_score', {})
        
        # Mock health score calculation
        health_score = (
            overall_score.get('performance_score', 0.5) * 0.4 +
            overall_score.get('reliability_score', 0.5) * 0.3 +
            overall_score.get('engagement_score', 0.5) * 0.3
        )
        
        return {
            'score': round(health_score * 100, 1),
            'grade': self._score_to_grade(health_score),
            'components': {
                'performance': overall_score.get('performance_score', 0.5) * 100,
                'reliability': overall_score.get('reliability_score', 0.5) * 100,
                'engagement': overall_score.get('engagement_score', 0.5) * 100
            }
        }
    
    def _score_to_grade(self, score: float) -> str:
        """Convert numeric score to letter grade."""
        if score >= 0.9:
            return 'A+'
        elif score >= 0.8:
            return 'A'
        elif score >= 0.7:
            return 'B'
        elif score >= 0.6:
            return 'C'
        else:
            return 'D'
    
    def _generate_platform_dashboard(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Generate platform-wide dashboard data."""
        
        # Mock platform dashboard data
        return {
            'platform_overview': {
                'total_partners': 150,
                'active_partners': 125,
                'total_campaigns': 450,
                'total_commissions': 1250
            },
            'platform_metrics': {
                'average_performance_score': 0.75,
                'total_earnings': '125000.00',
                'campaign_success_rate': 0.82,
                'partner_satisfaction': 4.3
            },
            'growth_trends': {
                'partner_growth': '+12%',
                'campaign_volume': '+18%',
                'earnings_growth': '+25%'
            }
        }
    
    def _get_platform_averages(self) -> Dict[str, Any]:
        """Get platform average metrics for comparison."""
        
        # Mock platform averages
        return {
            'campaign_success_rate': 0.75,
            'average_commission': 185.50,
            'monthly_campaigns': 3.2,
            'approval_rate': 0.88,
            'performance_score': 0.72
        }
    
    def _calculate_benchmark_comparisons(
        self,
        partner_metrics: Dict[str, Any],
        platform_averages: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate benchmark comparisons."""
        
        comparisons = {}
        
        # Compare campaign metrics
        campaigns = partner_metrics.get('campaigns', {})
        if 'success_rate' in campaigns:
            platform_success_rate = platform_averages.get('campaign_success_rate', 0.75)
            partner_success_rate = campaigns['success_rate']
            
            comparisons['campaign_success_rate'] = {
                'partner_value': partner_success_rate,
                'platform_average': platform_success_rate,
                'difference': partner_success_rate - platform_success_rate,
                'percentage_difference': ((partner_success_rate - platform_success_rate) / platform_success_rate) * 100
            }
        
        return comparisons
    
    def _calculate_percentile_rankings(self, partner_id: str) -> Dict[str, float]:
        """Calculate percentile rankings for partner."""
        
        # Mock percentile rankings
        return {
            'performance_score': 75.0,
            'earnings': 68.0,
            'campaign_success_rate': 82.0,
            'reliability': 79.0
        }
    
    def _get_peer_group_comparison(self, partner_id: str) -> Dict[str, Any]:
        """Get comparison with similar partners."""
        
        # Mock peer group comparison
        return {
            'peer_group': 'Mid-tier Enterprise Partners',
            'peer_count': 25,
            'ranking': 8,  # 8th out of 25
            'percentile': 68,
            'comparison': {
                'above_peers': ['campaign_success_rate', 'reliability_score'],
                'below_peers': ['average_commission', 'monthly_volume'],
                'similar_peers': ['engagement_score']
            }
        }