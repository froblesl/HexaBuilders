"""
Partner domain events for HexaBuilders.
Implements all partner-related domain events following CQRS patterns.
"""

from typing import Dict, Any, Optional

from partner_management.seedwork.dominio.eventos import DomainEvent, IntegrationEvent, EventMetadata


class PartnerCreated(DomainEvent):
    """Event raised when a partner is created."""
    
    def __init__(
        self,
        aggregate_id: str,
        business_name: str,
        email: str,
        partner_type: str,
        phone: str,
        metadata: Optional[EventMetadata] = None
    ):
        super().__init__(
            aggregate_id=aggregate_id,
            metadata=metadata,
            business_name=business_name,
            email=email,
            partner_type=partner_type,
            phone=phone
        )


class PartnerStatusChanged(DomainEvent):
    """Event raised when partner status changes."""
    
    def __init__(
        self,
        aggregate_id: str,
        old_status: str,
        new_status: str,
        reason: Optional[str] = None,
        metadata: Optional[EventMetadata] = None
    ):
        super().__init__(
            aggregate_id=aggregate_id,
            metadata=metadata,
            old_status=old_status,
            new_status=new_status,
            reason=reason
        )


class PartnerActivated(DomainEvent):
    """Event raised when partner is activated."""
    
    def __init__(
        self,
        aggregate_id: str,
        partner_email: str,
        partner_name: str,
        metadata: Optional[EventMetadata] = None
    ):
        super().__init__(
            aggregate_id=aggregate_id,
            metadata=metadata,
            partner_email=partner_email,
            partner_name=partner_name
        )


class PartnerDeactivated(DomainEvent):
    """Event raised when partner is deactivated."""
    
    def __init__(
        self,
        aggregate_id: str,
        partner_email: str,
        partner_name: str,
        reason: Optional[str] = None,
        metadata: Optional[EventMetadata] = None
    ):
        super().__init__(
            aggregate_id=aggregate_id,
            metadata=metadata,
            partner_email=partner_email,
            partner_name=partner_name,
            reason=reason
        )


class PartnerUpdated(DomainEvent):
    """Event raised when partner information is updated."""
    
    def __init__(
        self,
        aggregate_id: str,
        old_data: Dict[str, Any],
        new_data: Dict[str, Any],
        metadata: Optional[EventMetadata] = None
    ):
        super().__init__(
            aggregate_id=aggregate_id,
            metadata=metadata,
            old_data=old_data,
            new_data=new_data
        )


class PartnerValidationCompleted(DomainEvent):
    """Event raised when partner validation is completed."""
    
    def __init__(
        self,
        aggregate_id: str,
        validation_type: str,
        partner_email: str,
        metadata: Optional[EventMetadata] = None
    ):
        super().__init__(
            aggregate_id=aggregate_id,
            metadata=metadata,
            validation_type=validation_type,
            partner_email=partner_email
        )


class PartnerSuspended(DomainEvent):
    """Event raised when partner is suspended."""
    
    def __init__(
        self,
        aggregate_id: str,
        suspension_reason: str,
        partner_email: str,
        metadata: Optional[EventMetadata] = None
    ):
        super().__init__(
            aggregate_id=aggregate_id,
            metadata=metadata,
            suspension_reason=suspension_reason,
            partner_email=partner_email
        )


class PartnerDeleted(DomainEvent):
    """Event raised when partner is deleted."""
    
    def __init__(
        self,
        aggregate_id: str,
        partner_email: str,
        deletion_reason: str,
        metadata: Optional[EventMetadata] = None
    ):
        super().__init__(
            aggregate_id=aggregate_id,
            metadata=metadata,
            partner_email=partner_email,
            deletion_reason=deletion_reason
        )


class PartnerMetricsUpdated(DomainEvent):
    """Event raised when partner metrics are updated."""
    
    def __init__(
        self,
        aggregate_id: str,
        old_metrics: Dict[str, Any],
        new_metrics: Dict[str, Any],
        source: str = "system",
        metadata: Optional[EventMetadata] = None
    ):
        super().__init__(
            aggregate_id=aggregate_id,
            metadata=metadata,
            old_metrics=old_metrics,
            new_metrics=new_metrics,
            source=source
        )


# Integration Events
class PartnerRegistrationCompleted(IntegrationEvent):
    """Integration event for partner registration completion."""
    
    def __init__(
        self,
        aggregate_id: str,
        business_name: str,
        email: str,
        partner_type: str,
        metadata: Optional[EventMetadata] = None
    ):
        super().__init__(
            aggregate_id=aggregate_id,
            metadata=metadata,
            business_name=business_name,
            email=email,
            partner_type=partner_type
        )


class PartnerStatusUpdated(IntegrationEvent):
    """Integration event for partner status updates."""
    
    def __init__(
        self,
        aggregate_id: str,
        partner_email: str,
        old_status: str,
        new_status: str,
        metadata: Optional[EventMetadata] = None
    ):
        super().__init__(
            aggregate_id=aggregate_id,
            metadata=metadata,
            partner_email=partner_email,
            old_status=old_status,
            new_status=new_status
        )


class PartnerValidationStatusChanged(IntegrationEvent):
    """Integration event for partner validation status changes."""
    
    def __init__(
        self,
        aggregate_id: str,
        partner_email: str,
        validation_type: str,
        is_validated: bool,
        metadata: Optional[EventMetadata] = None
    ):
        super().__init__(
            aggregate_id=aggregate_id,
            metadata=metadata,
            partner_email=partner_email,
            validation_type=validation_type,
            is_validated=is_validated
        )