"""
Mock repositories for Analytics module in HexaBuilders.
Provides in-memory data persistence for development and testing.
"""

import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from decimal import Decimal

from partner_management.seedwork.dominio.repositorio import Repositorio
from partner_management.seedwork.dominio.excepciones import DomainException

from ..dominio.entidades import AnalyticsReport
from ..dominio.objetos_valor import (
    ReportType, ReportPeriod, ReportConfiguration, ReportStatus,
    AnalyticsMetrics, Insight, TrendAnalysis, BenchmarkComparison
)
from .dto import AnalyticsReportDTO
from .fabricas import FabricaAnalytics


class RepositorioAnalyticsMock(Repositorio):
    """Mock repository for AnalyticsReport entities."""
    
    def __init__(self):
        super().__init__()
        self._reports: Dict[str, AnalyticsReport] = {}
        self._fabrica = FabricaAnalytics()
        self._initialize_sample_data()
    
    def obtener_por_id(self, report_id: str) -> Optional[AnalyticsReport]:
        """Get analytics report by ID."""
        return self._reports.get(report_id)
    
    def obtener_todos(self) -> List[AnalyticsReport]:
        """Get all analytics reports."""
        return [r for r in self._reports.values() if not r.is_deleted]
    
    def obtener_por_partner_id(self, partner_id: str) -> List[AnalyticsReport]:
        """Get analytics reports by partner ID."""
        return [
            r for r in self._reports.values() 
            if r.partner_id == partner_id and not r.is_deleted
        ]
    
    def obtener_por_status(self, status: ReportStatus) -> List[AnalyticsReport]:
        """Get analytics reports by status."""
        return [
            r for r in self._reports.values() 
            if r.status == status and not r.is_deleted
        ]
    
    def obtener_por_tipo(self, report_type: ReportType) -> List[AnalyticsReport]:
        """Get analytics reports by type."""
        return [
            r for r in self._reports.values() 
            if r.report_type == report_type and not r.is_deleted
        ]
    
    def obtener_todos_con_filtros(
        self,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[AnalyticsReport]:
        """Get analytics reports with filters and pagination."""
        
        reports = [r for r in self._reports.values() if not r.is_deleted]
        
        if filters:
            # Apply partner_id filter
            if 'partner_id' in filters:
                reports = [r for r in reports if r.partner_id == filters['partner_id']]
            
            # Apply status filter
            if 'status' in filters:
                status_filter = ReportStatus(filters['status'])
                reports = [r for r in reports if r.status == status_filter]
            
            # Apply report_type filter
            if 'report_type' in filters:
                type_filter = ReportType(filters['report_type'])
                reports = [r for r in reports if r.report_type == type_filter]
            
            # Apply date range filters
            if 'start_date' in filters:
                start_date = filters['start_date']
                reports = [r for r in reports if r.created_at >= start_date]
            
            if 'end_date' in filters:
                end_date = filters['end_date']
                reports = [r for r in reports if r.created_at <= end_date]
        
        # Sort by creation date (newest first)
        reports.sort(key=lambda r: r.created_at, reverse=True)
        
        # Apply pagination
        return reports[offset:offset + limit]
    
    def contar_con_filtros(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count analytics reports with filters."""
        return len(self.obtener_todos_con_filtros(filters, limit=10000, offset=0))
    
    def obtener_reportes_recientes(
        self,
        partner_id: Optional[str] = None,
        days: int = 30,
        limit: int = 10
    ) -> List[AnalyticsReport]:
        """Get recent analytics reports."""
        
        cutoff_date = datetime.now() - timedelta(days=days)
        reports = [
            r for r in self._reports.values()
            if r.created_at >= cutoff_date and not r.is_deleted
        ]
        
        if partner_id:
            reports = [r for r in reports if r.partner_id == partner_id]
        
        # Sort by creation date (newest first)
        reports.sort(key=lambda r: r.created_at, reverse=True)
        
        return reports[:limit]
    
    def obtener_reportes_completados(
        self,
        partner_id: Optional[str] = None,
        limit: int = 50
    ) -> List[AnalyticsReport]:
        """Get completed analytics reports."""
        
        reports = [
            r for r in self._reports.values()
            if r.status == ReportStatus.COMPLETED and not r.is_deleted
        ]
        
        if partner_id:
            reports = [r for r in reports if r.partner_id == partner_id]
        
        # Sort by generation date (newest first)
        reports.sort(key=lambda r: r.generated_date or r.created_at, reverse=True)
        
        return reports[:limit]
    
    def obtener_insights_criticos(
        self,
        partner_id: Optional[str] = None,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """Get critical insights from recent reports."""
        
        recent_reports = self.obtener_reportes_recientes(partner_id, days, 20)
        critical_insights = []
        
        for report in recent_reports:
            if report.status == ReportStatus.COMPLETED:
                for insight in report.obtener_insights_criticos():
                    critical_insights.append({
                        'report_id': report.id,
                        'partner_id': report.partner_id,
                        'insight': insight,
                        'generated_at': report.generated_date
                    })
        
        return critical_insights
    
    def agregar(self, report: AnalyticsReport) -> None:
        """Add new analytics report."""
        if report.id in self._reports:
            raise DomainException(f"Analytics report with ID {report.id} already exists")
        self._reports[report.id] = report
    
    def actualizar(self, report: AnalyticsReport) -> None:
        """Update existing analytics report."""
        if report.id not in self._reports:
            raise DomainException(f"Analytics report with ID {report.id} not found")
        self._reports[report.id] = report
    
    def eliminar(self, report: AnalyticsReport) -> None:
        """Soft delete analytics report."""
        if report.id in self._reports:
            report.soft_delete()
            self._reports[report.id] = report
    
    def obtener_estadisticas_plataforma(self) -> Dict[str, Any]:
        """Get platform-wide analytics statistics."""
        
        all_reports = [r for r in self._reports.values() if not r.is_deleted]
        completed_reports = [r for r in all_reports if r.status == ReportStatus.COMPLETED]
        
        # Count by status
        status_counts = {}
        for report in all_reports:
            status = report.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Count by type
        type_counts = {}
        for report in all_reports:
            report_type = report.report_type.value
            type_counts[report_type] = type_counts.get(report_type, 0) + 1
        
        # Partner coverage
        unique_partners = len(set(r.partner_id for r in all_reports))
        
        return {
            'total_reports': len(all_reports),
            'completed_reports': len(completed_reports),
            'status_breakdown': status_counts,
            'type_breakdown': type_counts,
            'unique_partners_analyzed': unique_partners,
            'average_generation_time': self._calculate_average_generation_time(completed_reports),
            'success_rate': len(completed_reports) / len(all_reports) if all_reports else 0
        }
    
    def _calculate_average_generation_time(self, completed_reports: List[AnalyticsReport]) -> float:
        """Calculate average report generation time."""
        
        times = []
        for report in completed_reports:
            if hasattr(report, '_generation_time_seconds') and report._generation_time_seconds:
                times.append(report._generation_time_seconds)
        
        return sum(times) / len(times) if times else 0.0
    
    def _initialize_sample_data(self):
        """Initialize with sample analytics report data."""
        
        # Sample partner IDs (these should match partners in partner mock repo)
        sample_partner_ids = [
            "partner-001", "partner-002", "partner-003", 
            "partner-004", "partner-005"
        ]
        
        # Create sample reports
        base_date = datetime.now() - timedelta(days=60)
        
        for i in range(15):
            partner_id = sample_partner_ids[i % len(sample_partner_ids)]
            
            # Vary report types
            report_types = ['PARTNER_PERFORMANCE', 'COMMISSION_SUMMARY', 'CAMPAIGN_ANALYSIS', 'COMPREHENSIVE']
            report_type = report_types[i % len(report_types)]
            
            # Create report period
            days_ago = i * 4
            period_end = base_date + timedelta(days=days_ago)
            period_start = period_end - timedelta(days=30)
            
            # Create value objects
            report_type_obj = ReportType(report_type)
            
            report_period = ReportPeriod(
                start_date=period_start,
                end_date=period_end,
                period_name=f"{report_type} Report #{i+1}"
            )
            
            configuration = ReportConfiguration(
                include_charts=True,
                include_comparisons=i % 2 == 0,  # Alternate
                include_trends=i % 3 == 0,       # Every third
                chart_types=['bar', 'line', 'pie'],
                export_formats=['pdf', 'json']
            )
            
            # Vary status (more completed reports for realistic data)
            statuses = [
                ReportStatus.COMPLETED, ReportStatus.COMPLETED, 
                ReportStatus.COMPLETED, ReportStatus.PENDING, ReportStatus.FAILED
            ]
            status = statuses[i % len(statuses)]
            
            # Create analytics metrics for completed reports
            metrics = None
            insights = []
            trends = []
            benchmarks = []
            
            if status == ReportStatus.COMPLETED:
                metrics = AnalyticsMetrics(
                    total_campaigns=10 + (i * 2),
                    active_campaigns=3 + (i % 5),
                    completed_campaigns=7 + i,
                    total_commissions=25 + (i * 3),
                    total_commission_amount=Decimal(str(1000 + (i * 200))),
                    average_commission=Decimal(str(40 + (i * 8))),
                    partner_rating=4.0 + (i % 10) * 0.05,
                    conversion_rate=0.7 + (i % 20) * 0.01,
                    performance_score=0.6 + (i % 25) * 0.015
                )
                
                # Add sample insights
                if i % 3 == 0:  # Some reports have insights
                    insights = [
                        self._fabrica.crear_insight(
                            insight_type="performance",
                            title=f"Performance Insight #{i+1}",
                            description=f"Sample performance insight for report #{i+1}",
                            severity="info" if i % 2 == 0 else "warning",
                            confidence=0.8 + (i % 20) * 0.01,
                            recommendations=[f"Recommendation A for report #{i+1}", f"Recommendation B for report #{i+1}"]
                        )
                    ]
                
                # Add sample trends
                if i % 4 == 0:  # Some reports have trends
                    trends = [
                        self._fabrica.crear_trend_analysis(
                            metric_name="commission_amount",
                            trend_direction="increasing" if i % 2 == 0 else "decreasing",
                            trend_strength=0.5 + (i % 30) * 0.015,
                            period_comparison="month_over_month",
                            data_points=[100 + j*10 + (i*5) for j in range(6)],  # Mock data points
                            analysis=f"Sample trend analysis for report #{i+1}",
                            confidence=0.7 + (i % 25) * 0.01
                        )
                    ]
                
                # Add sample benchmarks
                if i % 5 == 0:  # Some reports have benchmarks
                    benchmarks = [
                        self._fabrica.crear_benchmark_comparison(
                            metric_name="performance_score",
                            partner_value=metrics.performance_score,
                            benchmark_value=0.75,
                            benchmark_type="platform_average",
                            percentile_rank=50.0 + (i % 40)
                        )
                    ]
            
            # Create report
            report = self._fabrica.crear_analytics_report(
                partner_id=partner_id,
                report_type=report_type_obj,
                report_period=report_period,
                configuration=configuration,
                status=status
            )
            
            # Set creation date
            report._created_at = base_date + timedelta(days=days_ago)
            report._updated_at = report._created_at
            
            # Complete report if needed
            if status == ReportStatus.COMPLETED:
                generation_time = 2.5 + (i % 10) * 0.5  # Mock generation time
                report.iniciar_generacion("system")
                report.completar_generacion(
                    metrics=metrics,
                    generation_time_seconds=generation_time,
                    insights=insights,
                    trends=trends,
                    benchmarks=benchmarks
                )
            elif status == ReportStatus.FAILED:
                report.iniciar_generacion("system")
                report.fallar_generacion(f"Sample error message for report #{i+1}")
            
            # Store report
            self._reports[report.id] = report