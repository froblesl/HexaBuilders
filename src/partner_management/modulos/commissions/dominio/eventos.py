"""
Commission domain events for HexaBuilders.
Implements all commission-related domain events following CQRS patterns.
"""

from typing import Dict, Any, Optional
from decimal import Decimal

from partner_management.seedwork.dominio.eventos import DomainEvent, IntegrationEvent, EventMetadata


class CommissionCreated(DomainEvent):
    """Event raised when a commission is created."""
    
    def __init__(
        self,
        aggregate_id: str,
        partner_id: str,
        commission_amount: str,
        commission_rate: str,
        commission_type: str,
        transaction_reference: str,
        calculation_date: str,
        metadata: Optional[EventMetadata] = None
    ):
        super().__init__(
            aggregate_id=aggregate_id,
            metadata=metadata,
            partner_id=partner_id,
            commission_amount=commission_amount,
            commission_rate=commission_rate,
            commission_type=commission_type,
            transaction_reference=transaction_reference,
            calculation_date=calculation_date
        )


class CommissionStatusChanged(DomainEvent):
    """Event raised when commission status changes."""
    
    def __init__(
        self,
        aggregate_id: str,
        partner_id: str,
        old_status: str,
        new_status: str,
        reason: Optional[str] = None,
        changed_by: Optional[str] = None,
        metadata: Optional[EventMetadata] = None
    ):
        super().__init__(
            aggregate_id=aggregate_id,
            metadata=metadata,
            partner_id=partner_id,
            old_status=old_status,
            new_status=new_status,
            reason=reason,
            changed_by=changed_by
        )


class CommissionApproved(DomainEvent):
    """Event raised when commission is approved."""
    
    def __init__(
        self,
        aggregate_id: str,
        partner_id: str,
        commission_amount: str,
        approved_by: str,
        approval_date: str,
        approval_notes: Optional[str] = None,
        metadata: Optional[EventMetadata] = None
    ):
        super().__init__(
            aggregate_id=aggregate_id,
            metadata=metadata,
            partner_id=partner_id,
            commission_amount=commission_amount,
            approved_by=approved_by,
            approval_date=approval_date,
            approval_notes=approval_notes
        )


class CommissionPaid(DomainEvent):
    """Event raised when commission is paid."""
    
    def __init__(
        self,
        aggregate_id: str,
        partner_id: str,
        commission_amount: str,
        payment_method: str,
        payment_reference: str,
        payment_date: str,
        payment_fee: str = "0.00",
        metadata: Optional[EventMetadata] = None
    ):
        super().__init__(
            aggregate_id=aggregate_id,
            metadata=metadata,
            partner_id=partner_id,
            commission_amount=commission_amount,
            payment_method=payment_method,
            payment_reference=payment_reference,
            payment_date=payment_date,
            payment_fee=payment_fee
        )


class CommissionCancelled(DomainEvent):
    """Event raised when commission is cancelled."""
    
    def __init__(
        self,
        aggregate_id: str,
        partner_id: str,
        commission_amount: str,
        cancellation_reason: str,
        cancelled_by: str,
        cancellation_date: str,
        metadata: Optional[EventMetadata] = None
    ):
        super().__init__(
            aggregate_id=aggregate_id,
            metadata=metadata,
            partner_id=partner_id,
            commission_amount=commission_amount,
            cancellation_reason=cancellation_reason,
            cancelled_by=cancelled_by,
            cancellation_date=cancellation_date
        )


class CommissionDisputed(DomainEvent):
    """Event raised when commission is disputed."""
    
    def __init__(
        self,
        aggregate_id: str,
        partner_id: str,
        commission_amount: str,
        dispute_reason: str,
        disputed_by: str,
        dispute_date: str,
        dispute_details: Optional[Dict[str, Any]] = None,
        metadata: Optional[EventMetadata] = None
    ):
        super().__init__(
            aggregate_id=aggregate_id,
            metadata=metadata,
            partner_id=partner_id,
            commission_amount=commission_amount,
            dispute_reason=dispute_reason,
            disputed_by=disputed_by,
            dispute_date=dispute_date,
            dispute_details=dispute_details or {}
        )


class CommissionCalculated(DomainEvent):
    """Event raised when commission is calculated."""
    
    def __init__(
        self,
        aggregate_id: str,
        partner_id: str,
        base_amount: str,
        commission_rate: str,
        commission_amount: str,
        calculation_method: str,
        calculation_date: str,
        transaction_reference: str,
        metadata: Optional[EventMetadata] = None
    ):
        super().__init__(
            aggregate_id=aggregate_id,
            metadata=metadata,
            partner_id=partner_id,
            base_amount=base_amount,
            commission_rate=commission_rate,
            commission_amount=commission_amount,
            calculation_method=calculation_method,
            calculation_date=calculation_date,
            transaction_reference=transaction_reference
        )


class CommissionRecalculated(DomainEvent):
    """Event raised when commission is recalculated."""
    
    def __init__(
        self,
        aggregate_id: str,
        partner_id: str,
        old_amount: str,
        new_amount: str,
        recalculation_reason: str,
        recalculated_by: str,
        recalculation_date: str,
        metadata: Optional[EventMetadata] = None
    ):
        super().__init__(
            aggregate_id=aggregate_id,
            metadata=metadata,
            partner_id=partner_id,
            old_amount=old_amount,
            new_amount=new_amount,
            recalculation_reason=recalculation_reason,
            recalculated_by=recalculated_by,
            recalculation_date=recalculation_date
        )


class CommissionHeld(DomainEvent):
    """Event raised when commission is put on hold."""
    
    def __init__(
        self,
        aggregate_id: str,
        partner_id: str,
        commission_amount: str,
        hold_reason: str,
        held_by: str,
        hold_date: str,
        expected_release_date: Optional[str] = None,
        metadata: Optional[EventMetadata] = None
    ):
        super().__init__(
            aggregate_id=aggregate_id,
            metadata=metadata,
            partner_id=partner_id,
            commission_amount=commission_amount,
            hold_reason=hold_reason,
            held_by=held_by,
            hold_date=hold_date,
            expected_release_date=expected_release_date
        )


class CommissionReleased(DomainEvent):
    """Event raised when commission hold is released."""
    
    def __init__(
        self,
        aggregate_id: str,
        partner_id: str,
        commission_amount: str,
        release_reason: str,
        released_by: str,
        release_date: str,
        metadata: Optional[EventMetadata] = None
    ):
        super().__init__(
            aggregate_id=aggregate_id,
            metadata=metadata,
            partner_id=partner_id,
            commission_amount=commission_amount,
            release_reason=release_reason,
            released_by=released_by,
            release_date=release_date
        )


class CommissionAdjusted(DomainEvent):
    """Event raised when commission amount is adjusted."""
    
    def __init__(
        self,
        aggregate_id: str,
        partner_id: str,
        original_amount: str,
        adjusted_amount: str,
        adjustment_reason: str,
        adjusted_by: str,
        adjustment_date: str,
        adjustment_type: str = "manual",
        metadata: Optional[EventMetadata] = None
    ):
        super().__init__(
            aggregate_id=aggregate_id,
            metadata=metadata,
            partner_id=partner_id,
            original_amount=original_amount,
            adjusted_amount=adjusted_amount,
            adjustment_reason=adjustment_reason,
            adjusted_by=adjusted_by,
            adjustment_date=adjustment_date,
            adjustment_type=adjustment_type
        )


# Integration Events

class CommissionPaymentInitiated(IntegrationEvent):
    """Integration event for commission payment initiation."""
    
    def __init__(
        self,
        aggregate_id: str,
        partner_id: str,
        commission_amount: str,
        payment_method: str,
        payment_details: Dict[str, Any],
        payment_scheduled_date: str,
        metadata: Optional[EventMetadata] = None
    ):
        super().__init__(
            aggregate_id=aggregate_id,
            metadata=metadata,
            partner_id=partner_id,
            commission_amount=commission_amount,
            payment_method=payment_method,
            payment_details=payment_details,
            payment_scheduled_date=payment_scheduled_date
        )


class CommissionPaymentCompleted(IntegrationEvent):
    """Integration event for commission payment completion."""
    
    def __init__(
        self,
        aggregate_id: str,
        partner_id: str,
        commission_amount: str,
        payment_method: str,
        payment_reference: str,
        payment_date: str,
        net_amount: str,
        payment_fees: str,
        metadata: Optional[EventMetadata] = None
    ):
        super().__init__(
            aggregate_id=aggregate_id,
            metadata=metadata,
            partner_id=partner_id,
            commission_amount=commission_amount,
            payment_method=payment_method,
            payment_reference=payment_reference,
            payment_date=payment_date,
            net_amount=net_amount,
            payment_fees=payment_fees
        )


class CommissionPaymentFailed(IntegrationEvent):
    """Integration event for commission payment failure."""
    
    def __init__(
        self,
        aggregate_id: str,
        partner_id: str,
        commission_amount: str,
        payment_method: str,
        failure_reason: str,
        failure_date: str,
        retry_scheduled: bool = False,
        next_retry_date: Optional[str] = None,
        metadata: Optional[EventMetadata] = None
    ):
        super().__init__(
            aggregate_id=aggregate_id,
            metadata=metadata,
            partner_id=partner_id,
            commission_amount=commission_amount,
            payment_method=payment_method,
            failure_reason=failure_reason,
            failure_date=failure_date,
            retry_scheduled=retry_scheduled,
            next_retry_date=next_retry_date
        )


class CommissionTaxCalculated(IntegrationEvent):
    """Integration event for commission tax calculation."""
    
    def __init__(
        self,
        aggregate_id: str,
        partner_id: str,
        commission_amount: str,
        tax_amount: str,
        tax_rate: str,
        tax_jurisdiction: str,
        calculation_date: str,
        metadata: Optional[EventMetadata] = None
    ):
        super().__init__(
            aggregate_id=aggregate_id,
            metadata=metadata,
            partner_id=partner_id,
            commission_amount=commission_amount,
            tax_amount=tax_amount,
            tax_rate=tax_rate,
            tax_jurisdiction=tax_jurisdiction,
            calculation_date=calculation_date
        )


class CommissionReportGenerated(IntegrationEvent):
    """Integration event for commission report generation."""
    
    def __init__(
        self,
        aggregate_id: str,
        partner_id: str,
        report_period: str,
        report_type: str,
        total_commissions: str,
        commission_count: int,
        report_date: str,
        report_data: Dict[str, Any],
        metadata: Optional[EventMetadata] = None
    ):
        super().__init__(
            aggregate_id=aggregate_id,
            metadata=metadata,
            partner_id=partner_id,
            report_period=report_period,
            report_type=report_type,
            total_commissions=total_commissions,
            commission_count=commission_count,
            report_date=report_date,
            report_data=report_data
        )


class CommissionThresholdReached(IntegrationEvent):
    """Integration event for commission threshold notifications."""
    
    def __init__(
        self,
        aggregate_id: str,
        partner_id: str,
        threshold_type: str,
        threshold_value: str,
        current_value: str,
        period: str,
        reached_date: str,
        metadata: Optional[EventMetadata] = None
    ):
        super().__init__(
            aggregate_id=aggregate_id,
            metadata=metadata,
            partner_id=partner_id,
            threshold_type=threshold_type,
            threshold_value=threshold_value,
            current_value=current_value,
            period=period,
            reached_date=reached_date
        )