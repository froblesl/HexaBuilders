"""
Campaign domain events for HexaBuilders.
Implements all campaign-related domain events following CQRS patterns.
"""

from typing import Dict, Any, Optional
from decimal import Decimal

from partner_management.seedwork.dominio.eventos import DomainEvent, IntegrationEvent, EventMetadata


class CampaignCreated(DomainEvent):
    """Event raised when a campaign is created."""
    
    def __init__(
        self,
        aggregate_id: str,
        campaign_name: str,
        partner_id: str,
        campaign_type: str,
        budget_amount: Decimal,
        start_date: str,
        end_date: str,
        metadata: Optional[EventMetadata] = None
    ):
        super().__init__(
            aggregate_id=aggregate_id,
            metadata=metadata,
            campaign_name=campaign_name,
            partner_id=partner_id,
            campaign_type=campaign_type,
            budget_amount=str(budget_amount),
            start_date=start_date,
            end_date=end_date
        )


class CampaignStatusChanged(DomainEvent):
    """Event raised when campaign status changes."""
    
    def __init__(
        self,
        aggregate_id: str,
        old_status: str,
        new_status: str,
        reason: Optional[str] = None,
        changed_by: Optional[str] = None,
        metadata: Optional[EventMetadata] = None
    ):
        super().__init__(
            aggregate_id=aggregate_id,
            metadata=metadata,
            old_status=old_status,
            new_status=new_status,
            reason=reason,
            changed_by=changed_by
        )


class CampaignActivated(DomainEvent):
    """Event raised when campaign is activated."""
    
    def __init__(
        self,
        aggregate_id: str,
        campaign_name: str,
        partner_id: str,
        start_date: str,
        end_date: str,
        budget_amount: str,
        metadata: Optional[EventMetadata] = None
    ):
        super().__init__(
            aggregate_id=aggregate_id,
            metadata=metadata,
            campaign_name=campaign_name,
            partner_id=partner_id,
            start_date=start_date,
            end_date=end_date,
            budget_amount=budget_amount
        )


class CampaignPaused(DomainEvent):
    """Event raised when campaign is paused."""
    
    def __init__(
        self,
        aggregate_id: str,
        campaign_name: str,
        partner_id: str,
        pause_reason: str,
        paused_by: Optional[str] = None,
        metadata: Optional[EventMetadata] = None
    ):
        super().__init__(
            aggregate_id=aggregate_id,
            metadata=metadata,
            campaign_name=campaign_name,
            partner_id=partner_id,
            pause_reason=pause_reason,
            paused_by=paused_by
        )


class CampaignCompleted(DomainEvent):
    """Event raised when campaign is completed."""
    
    def __init__(
        self,
        aggregate_id: str,
        campaign_name: str,
        partner_id: str,
        final_metrics: Dict[str, Any],
        completion_reason: str = "ended",
        metadata: Optional[EventMetadata] = None
    ):
        super().__init__(
            aggregate_id=aggregate_id,
            metadata=metadata,
            campaign_name=campaign_name,
            partner_id=partner_id,
            final_metrics=final_metrics,
            completion_reason=completion_reason
        )


class CampaignCancelled(DomainEvent):
    """Event raised when campaign is cancelled."""
    
    def __init__(
        self,
        aggregate_id: str,
        campaign_name: str,
        partner_id: str,
        cancellation_reason: str,
        cancelled_by: Optional[str] = None,
        refund_amount: Optional[str] = None,
        metadata: Optional[EventMetadata] = None
    ):
        super().__init__(
            aggregate_id=aggregate_id,
            metadata=metadata,
            campaign_name=campaign_name,
            partner_id=partner_id,
            cancellation_reason=cancellation_reason,
            cancelled_by=cancelled_by,
            refund_amount=refund_amount
        )


class CampaignUpdated(DomainEvent):
    """Event raised when campaign information is updated."""
    
    def __init__(
        self,
        aggregate_id: str,
        updated_fields: Dict[str, Any],
        old_data: Dict[str, Any],
        new_data: Dict[str, Any],
        updated_by: Optional[str] = None,
        metadata: Optional[EventMetadata] = None
    ):
        super().__init__(
            aggregate_id=aggregate_id,
            metadata=metadata,
            updated_fields=updated_fields,
            old_data=old_data,
            new_data=new_data,
            updated_by=updated_by
        )


class CampaignBudgetExceeded(DomainEvent):
    """Event raised when campaign budget is exceeded."""
    
    def __init__(
        self,
        aggregate_id: str,
        campaign_name: str,
        partner_id: str,
        budget_amount: str,
        spent_amount: str,
        auto_paused: bool = True,
        metadata: Optional[EventMetadata] = None
    ):
        super().__init__(
            aggregate_id=aggregate_id,
            metadata=metadata,
            campaign_name=campaign_name,
            partner_id=partner_id,
            budget_amount=budget_amount,
            spent_amount=spent_amount,
            auto_paused=auto_paused
        )


class CampaignMetricsUpdated(DomainEvent):
    """Event raised when campaign metrics are updated."""
    
    def __init__(
        self,
        aggregate_id: str,
        old_metrics: Dict[str, Any],
        new_metrics: Dict[str, Any],
        metric_type: str = "performance",
        source: str = "system",
        metadata: Optional[EventMetadata] = None
    ):
        super().__init__(
            aggregate_id=aggregate_id,
            metadata=metadata,
            old_metrics=old_metrics,
            new_metrics=new_metrics,
            metric_type=metric_type,
            source=source
        )


class CampaignApproved(DomainEvent):
    """Event raised when campaign is approved."""
    
    def __init__(
        self,
        aggregate_id: str,
        campaign_name: str,
        partner_id: str,
        approved_by: str,
        approval_notes: Optional[str] = None,
        metadata: Optional[EventMetadata] = None
    ):
        super().__init__(
            aggregate_id=aggregate_id,
            metadata=metadata,
            campaign_name=campaign_name,
            partner_id=partner_id,
            approved_by=approved_by,
            approval_notes=approval_notes
        )


class CampaignRejected(DomainEvent):
    """Event raised when campaign is rejected."""
    
    def __init__(
        self,
        aggregate_id: str,
        campaign_name: str,
        partner_id: str,
        rejected_by: str,
        rejection_reason: str,
        required_changes: Optional[list[str]] = None,
        metadata: Optional[EventMetadata] = None
    ):
        super().__init__(
            aggregate_id=aggregate_id,
            metadata=metadata,
            campaign_name=campaign_name,
            partner_id=partner_id,
            rejected_by=rejected_by,
            rejection_reason=rejection_reason,
            required_changes=required_changes or []
        )


class CampaignTargetingUpdated(DomainEvent):
    """Event raised when campaign targeting is updated."""
    
    def __init__(
        self,
        aggregate_id: str,
        old_targeting: Dict[str, Any],
        new_targeting: Dict[str, Any],
        updated_by: Optional[str] = None,
        metadata: Optional[EventMetadata] = None
    ):
        super().__init__(
            aggregate_id=aggregate_id,
            metadata=metadata,
            old_targeting=old_targeting,
            new_targeting=new_targeting,
            updated_by=updated_by
        )


# Integration Events

class CampaignLaunched(IntegrationEvent):
    """Integration event for campaign launch."""
    
    def __init__(
        self,
        aggregate_id: str,
        campaign_name: str,
        partner_id: str,
        campaign_type: str,
        budget_amount: str,
        start_date: str,
        targeting_data: Dict[str, Any],
        metadata: Optional[EventMetadata] = None
    ):
        super().__init__(
            aggregate_id=aggregate_id,
            metadata=metadata,
            campaign_name=campaign_name,
            partner_id=partner_id,
            campaign_type=campaign_type,
            budget_amount=budget_amount,
            start_date=start_date,
            targeting_data=targeting_data
        )


class CampaignPerformanceAlert(IntegrationEvent):
    """Integration event for campaign performance alerts."""
    
    def __init__(
        self,
        aggregate_id: str,
        campaign_name: str,
        partner_id: str,
        alert_type: str,
        alert_message: str,
        performance_data: Dict[str, Any],
        severity: str = "medium",
        metadata: Optional[EventMetadata] = None
    ):
        super().__init__(
            aggregate_id=aggregate_id,
            metadata=metadata,
            campaign_name=campaign_name,
            partner_id=partner_id,
            alert_type=alert_type,
            alert_message=alert_message,
            performance_data=performance_data,
            severity=severity
        )


class CampaignBudgetAlert(IntegrationEvent):
    """Integration event for campaign budget alerts."""
    
    def __init__(
        self,
        aggregate_id: str,
        campaign_name: str,
        partner_id: str,
        budget_amount: str,
        spent_amount: str,
        remaining_amount: str,
        percentage_spent: float,
        alert_threshold: str,
        metadata: Optional[EventMetadata] = None
    ):
        super().__init__(
            aggregate_id=aggregate_id,
            metadata=metadata,
            campaign_name=campaign_name,
            partner_id=partner_id,
            budget_amount=budget_amount,
            spent_amount=spent_amount,
            remaining_amount=remaining_amount,
            percentage_spent=percentage_spent,
            alert_threshold=alert_threshold
        )


class CampaignStatusNotification(IntegrationEvent):
    """Integration event for campaign status notifications."""
    
    def __init__(
        self,
        aggregate_id: str,
        campaign_name: str,
        partner_id: str,
        old_status: str,
        new_status: str,
        notification_type: str,
        metadata: Optional[EventMetadata] = None
    ):
        super().__init__(
            aggregate_id=aggregate_id,
            metadata=metadata,
            campaign_name=campaign_name,
            partner_id=partner_id,
            old_status=old_status,
            new_status=new_status,
            notification_type=notification_type
        )