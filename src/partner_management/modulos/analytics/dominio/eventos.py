"""
Analytics domain events for HexaBuilders.
Implements all analytics-related domain events following CQRS patterns.
"""

from typing import Dict, Any, Optional

from partner_management.seedwork.dominio.eventos import DomainEvent, IntegrationEvent, EventMetadata


class AnalyticsReportCreated(DomainEvent):
    """Event raised when an analytics report is created."""
    
    def __init__(
        self,
        aggregate_id: str,
        partner_id: str,
        report_type: str,
        period_start: str,
        period_end: str,
        period_name: str,
        metadata: Optional[EventMetadata] = None
    ):
        super().__init__(
            aggregate_id=aggregate_id,
            metadata=metadata,
            partner_id=partner_id,
            report_type=report_type,
            period_start=period_start,
            period_end=period_end,
            period_name=period_name
        )


class AnalyticsReportGenerated(DomainEvent):
    """Event raised when an analytics report is successfully generated."""
    
    def __init__(
        self,
        aggregate_id: str,
        partner_id: str,
        report_type: str,
        metrics_count: int,
        insights_count: int,
        generation_time: float,
        generated_by: str,
        metadata: Optional[EventMetadata] = None
    ):
        super().__init__(
            aggregate_id=aggregate_id,
            metadata=metadata,
            partner_id=partner_id,
            report_type=report_type,
            metrics_count=metrics_count,
            insights_count=insights_count,
            generation_time=generation_time,
            generated_by=generated_by
        )


class AnalyticsReportFailed(DomainEvent):
    """Event raised when analytics report generation fails."""
    
    def __init__(
        self,
        aggregate_id: str,
        partner_id: str,
        report_type: str,
        error_message: str,
        generated_by: str,
        metadata: Optional[EventMetadata] = None
    ):
        super().__init__(
            aggregate_id=aggregate_id,
            metadata=metadata,
            partner_id=partner_id,
            report_type=report_type,
            error_message=error_message,
            generated_by=generated_by
        )


class AnalyticsReportArchived(DomainEvent):
    """Event raised when an analytics report is archived."""
    
    def __init__(
        self,
        aggregate_id: str,
        partner_id: str,
        report_type: str,
        archived_by: str,
        archive_reason: str,
        metadata: Optional[EventMetadata] = None
    ):
        super().__init__(
            aggregate_id=aggregate_id,
            metadata=metadata,
            partner_id=partner_id,
            report_type=report_type,
            archived_by=archived_by,
            archive_reason=archive_reason
        )


class AnalyticsInsightDiscovered(DomainEvent):
    """Event raised when a significant insight is discovered."""
    
    def __init__(
        self,
        aggregate_id: str,
        partner_id: str,
        insight_type: str,
        insight_title: str,
        insight_description: str,
        severity: str,
        confidence: float,
        metadata: Optional[EventMetadata] = None
    ):
        super().__init__(
            aggregate_id=aggregate_id,
            metadata=metadata,
            partner_id=partner_id,
            insight_type=insight_type,
            insight_title=insight_title,
            insight_description=insight_description,
            severity=severity,
            confidence=confidence
        )


# Integration Events

class AnalyticsDataUpdated(IntegrationEvent):
    """Integration event for analytics data updates."""
    
    def __init__(
        self,
        aggregate_id: str,
        partner_id: str,
        data_type: str,
        update_source: str,
        affected_reports: list,
        metadata: Optional[EventMetadata] = None
    ):
        super().__init__(
            aggregate_id=aggregate_id,
            metadata=metadata,
            partner_id=partner_id,
            data_type=data_type,
            update_source=update_source,
            affected_reports=affected_reports
        )


class AnalyticsAlertTriggered(IntegrationEvent):
    """Integration event for analytics alerts."""
    
    def __init__(
        self,
        aggregate_id: str,
        partner_id: str,
        alert_type: str,
        alert_message: str,
        severity: str,
        threshold_value: str,
        actual_value: str,
        metadata: Optional[EventMetadata] = None
    ):
        super().__init__(
            aggregate_id=aggregate_id,
            metadata=metadata,
            partner_id=partner_id,
            alert_type=alert_type,
            alert_message=alert_message,
            severity=severity,
            threshold_value=threshold_value,
            actual_value=actual_value
        )