"""
Commission domain entities implementation for HexaBuilders.
Implements Commission aggregate root with full business logic.
"""

from typing import Optional, Dict, Any
from datetime import datetime
from decimal import Decimal

from partner_management.seedwork.dominio.entidades import AggregateRoot, DomainEntity
from partner_management.seedwork.dominio.excepciones import DomainException, BusinessRuleException
from .objetos_valor import (
    CommissionAmount, CommissionRate, CommissionPeriod, TransactionReference,
    PaymentDetails, CommissionCalculation, CommissionStatus, CommissionType,
    PaymentMethod
)
from .eventos import (
    CommissionCreated, CommissionStatusChanged, CommissionApproved,
    CommissionPaid, CommissionCancelled, CommissionDisputed,
    CommissionCalculated, CommissionRecalculated, CommissionHeld,
    CommissionReleased, CommissionAdjusted
)


class Commission(AggregateRoot):
    """
    Commission aggregate root.
    
    Represents a commission earned by a partner in the HexaBuilders platform.
    Commissions are calculated based on partner performance and transactions,
    and go through approval and payment processes.
    """
    
    def __init__(
        self,
        partner_id: str,
        commission_amount: CommissionAmount,
        commission_rate: CommissionRate,
        commission_type: CommissionType,
        transaction_reference: TransactionReference,
        calculation_period: CommissionPeriod,
        commission_id: Optional[str] = None,
        status: CommissionStatus = CommissionStatus.PENDING,
        calculation_details: Optional[CommissionCalculation] = None,
        payment_details: Optional[PaymentDetails] = None
    ):
        super().__init__(commission_id)
        
        # Validate required fields
        if not partner_id:
            raise DomainException("Commission must have a partner")
        
        # Set attributes
        self._partner_id = partner_id
        self._commission_amount = commission_amount
        self._commission_rate = commission_rate
        self._commission_type = commission_type
        self._transaction_reference = transaction_reference
        self._calculation_period = calculation_period
        self._status = status
        self._calculation_details = calculation_details
        self._payment_details = payment_details
        
        # Additional fields
        self._approval_date: Optional[datetime] = None
        self._approved_by: Optional[str] = None
        self._approval_notes: Optional[str] = None
        
        self._payment_date: Optional[datetime] = None
        self._payment_reference: Optional[str] = None
        
        self._cancellation_date: Optional[datetime] = None
        self._cancellation_reason: Optional[str] = None
        self._cancelled_by: Optional[str] = None
        
        self._hold_date: Optional[datetime] = None
        self._hold_reason: Optional[str] = None
        self._held_by: Optional[str] = None
        
        # Domain event
        self.agregar_evento(CommissionCreated(
            aggregate_id=self.id,
            partner_id=self._partner_id,
            commission_amount=str(self._commission_amount.amount),
            commission_rate=str(self._commission_rate.rate),
            commission_type=self._commission_type.value,
            transaction_reference=self._transaction_reference.transaction_id,
            calculation_date=self._calculation_period.start_date.isoformat()
        ))
    
    @property
    def partner_id(self) -> str:
        return self._partner_id
    
    @property
    def commission_amount(self) -> CommissionAmount:
        return self._commission_amount
    
    @property
    def commission_rate(self) -> CommissionRate:
        return self._commission_rate
    
    @property
    def commission_type(self) -> CommissionType:
        return self._commission_type
    
    @property
    def transaction_reference(self) -> TransactionReference:
        return self._transaction_reference
    
    @property
    def calculation_period(self) -> CommissionPeriod:
        return self._calculation_period
    
    @property
    def status(self) -> CommissionStatus:
        return self._status
    
    @property
    def calculation_details(self) -> Optional[CommissionCalculation]:
        return self._calculation_details
    
    @property
    def payment_details(self) -> Optional[PaymentDetails]:
        return self._payment_details
    
    @property
    def approval_date(self) -> Optional[datetime]:
        return self._approval_date
    
    @property
    def approved_by(self) -> Optional[str]:
        return self._approved_by
    
    @property
    def approval_notes(self) -> Optional[str]:
        return self._approval_notes
    
    @property
    def payment_date(self) -> Optional[datetime]:
        return self._payment_date
    
    @property
    def payment_reference(self) -> Optional[str]:
        return self._payment_reference
    
    def aprobar(self, approved_by: str, approval_notes: Optional[str] = None) -> None:
        """Approve commission for payment."""
        
        if self._status == CommissionStatus.APPROVED:
            return  # Already approved
        
        # Business rules for approval
        if self._status not in [CommissionStatus.PENDING]:
            raise BusinessRuleException("Only pending commissions can be approved")
        
        if not approved_by:
            raise DomainException("Approval must specify who approved")
        
        # Check if commission period is valid
        if self._calculation_period.is_expired():
            raise BusinessRuleException("Cannot approve commission for expired period")
        
        old_status = self._status
        self._status = CommissionStatus.APPROVED
        self._approval_date = datetime.now()
        self._approved_by = approved_by
        self._approval_notes = approval_notes
        
        self._mark_updated()
        
        # Domain events
        self.agregar_evento(CommissionStatusChanged(
            aggregate_id=self.id,
            partner_id=self._partner_id,
            old_status=old_status.value,
            new_status=self._status.value,
            reason="Commission approved",
            changed_by=approved_by
        ))
        
        self.agregar_evento(CommissionApproved(
            aggregate_id=self.id,
            partner_id=self._partner_id,
            commission_amount=str(self._commission_amount.amount),
            approved_by=approved_by,
            approval_date=self._approval_date.isoformat(),
            approval_notes=approval_notes
        ))
    
    def procesar_pago(
        self, 
        payment_method: PaymentMethod, 
        payment_reference: str,
        payment_fee: Decimal = Decimal('0.00'),
        bank_details: Optional[str] = None
    ) -> None:
        """Process commission payment."""
        
        if self._status == CommissionStatus.PAID:
            return  # Already paid
        
        # Business rules for payment
        if self._status != CommissionStatus.APPROVED:
            raise BusinessRuleException("Only approved commissions can be paid")
        
        if not payment_reference:
            raise DomainException("Payment reference is required")
        
        old_status = self._status
        self._status = CommissionStatus.PAID
        self._payment_date = datetime.now()
        self._payment_reference = payment_reference
        
        # Create payment details
        self._payment_details = PaymentDetails(
            payment_method=payment_method,
            payment_reference=payment_reference,
            payment_date=self._payment_date,
            payment_fee=payment_fee,
            bank_details=bank_details
        )
        
        self._mark_updated()
        
        # Domain events
        self.agregar_evento(CommissionStatusChanged(
            aggregate_id=self.id,
            partner_id=self._partner_id,
            old_status=old_status.value,
            new_status=self._status.value,
            reason="Commission paid",
            changed_by="payment_system"
        ))
        
        self.agregar_evento(CommissionPaid(
            aggregate_id=self.id,
            partner_id=self._partner_id,
            commission_amount=str(self._commission_amount.amount),
            payment_method=payment_method.value,
            payment_reference=payment_reference,
            payment_date=self._payment_date.isoformat(),
            payment_fee=str(payment_fee)
        ))
    
    def cancelar(self, cancellation_reason: str, cancelled_by: str) -> None:
        """Cancel commission."""
        
        if self._status == CommissionStatus.CANCELLED:
            return  # Already cancelled
        
        # Business rules for cancellation
        if self._status == CommissionStatus.PAID:
            raise BusinessRuleException("Paid commissions cannot be cancelled")
        
        if not cancellation_reason or not cancelled_by:
            raise DomainException("Cancellation reason and user are required")
        
        old_status = self._status
        self._status = CommissionStatus.CANCELLED
        self._cancellation_date = datetime.now()
        self._cancellation_reason = cancellation_reason
        self._cancelled_by = cancelled_by
        
        self._mark_updated()
        
        # Domain events
        self.agregar_evento(CommissionStatusChanged(
            aggregate_id=self.id,
            partner_id=self._partner_id,
            old_status=old_status.value,
            new_status=self._status.value,
            reason=cancellation_reason,
            changed_by=cancelled_by
        ))
        
        self.agregar_evento(CommissionCancelled(
            aggregate_id=self.id,
            partner_id=self._partner_id,
            commission_amount=str(self._commission_amount.amount),
            cancellation_reason=cancellation_reason,
            cancelled_by=cancelled_by,
            cancellation_date=self._cancellation_date.isoformat()
        ))
    
    def disputar(self, dispute_reason: str, disputed_by: str, 
                dispute_details: Optional[Dict[str, Any]] = None) -> None:
        """Mark commission as disputed."""
        
        if self._status == CommissionStatus.DISPUTED:
            return  # Already disputed
        
        # Business rules for disputes
        if self._status == CommissionStatus.CANCELLED:
            raise BusinessRuleException("Cancelled commissions cannot be disputed")
        
        if not dispute_reason or not disputed_by:
            raise DomainException("Dispute reason and user are required")
        
        old_status = self._status
        self._status = CommissionStatus.DISPUTED
        
        self._mark_updated()
        
        # Domain events
        self.agregar_evento(CommissionStatusChanged(
            aggregate_id=self.id,
            partner_id=self._partner_id,
            old_status=old_status.value,
            new_status=self._status.value,
            reason="Commission disputed",
            changed_by=disputed_by
        ))
        
        self.agregar_evento(CommissionDisputed(
            aggregate_id=self.id,
            partner_id=self._partner_id,
            commission_amount=str(self._commission_amount.amount),
            dispute_reason=dispute_reason,
            disputed_by=disputed_by,
            dispute_date=datetime.now().isoformat(),
            dispute_details=dispute_details
        ))
    
    def poner_en_espera(self, hold_reason: str, held_by: str, 
                       expected_release_date: Optional[datetime] = None) -> None:
        """Put commission on hold."""
        
        if self._status == CommissionStatus.ON_HOLD:
            return  # Already on hold
        
        # Business rules for holding
        if self._status in [CommissionStatus.PAID, CommissionStatus.CANCELLED]:
            raise BusinessRuleException("Paid or cancelled commissions cannot be put on hold")
        
        if not hold_reason or not held_by:
            raise DomainException("Hold reason and user are required")
        
        old_status = self._status
        self._status = CommissionStatus.ON_HOLD
        self._hold_date = datetime.now()
        self._hold_reason = hold_reason
        self._held_by = held_by
        
        self._mark_updated()
        
        # Domain events
        self.agregar_evento(CommissionStatusChanged(
            aggregate_id=self.id,
            partner_id=self._partner_id,
            old_status=old_status.value,
            new_status=self._status.value,
            reason=hold_reason,
            changed_by=held_by
        ))
        
        self.agregar_evento(CommissionHeld(
            aggregate_id=self.id,
            partner_id=self._partner_id,
            commission_amount=str(self._commission_amount.amount),
            hold_reason=hold_reason,
            held_by=held_by,
            hold_date=self._hold_date.isoformat(),
            expected_release_date=expected_release_date.isoformat() if expected_release_date else None
        ))
    
    def liberar_de_espera(self, release_reason: str, released_by: str) -> None:
        """Release commission from hold."""
        
        if self._status != CommissionStatus.ON_HOLD:
            raise BusinessRuleException("Only held commissions can be released")
        
        if not release_reason or not released_by:
            raise DomainException("Release reason and user are required")
        
        old_status = self._status
        # Return to pending status when released from hold
        self._status = CommissionStatus.PENDING
        
        # Clear hold information
        self._hold_date = None
        self._hold_reason = None
        self._held_by = None
        
        self._mark_updated()
        
        # Domain events
        self.agregar_evento(CommissionStatusChanged(
            aggregate_id=self.id,
            partner_id=self._partner_id,
            old_status=old_status.value,
            new_status=self._status.value,
            reason=release_reason,
            changed_by=released_by
        ))
        
        self.agregar_evento(CommissionReleased(
            aggregate_id=self.id,
            partner_id=self._partner_id,
            commission_amount=str(self._commission_amount.amount),
            release_reason=release_reason,
            released_by=released_by,
            release_date=datetime.now().isoformat()
        ))
    
    def ajustar_monto(
        self, 
        nuevo_monto: CommissionAmount, 
        adjustment_reason: str, 
        adjusted_by: str,
        adjustment_type: str = "manual"
    ) -> None:
        """Adjust commission amount."""
        
        # Business rules for adjustment
        if self._status == CommissionStatus.PAID:
            raise BusinessRuleException("Paid commissions cannot be adjusted")
        
        if self._status == CommissionStatus.CANCELLED:
            raise BusinessRuleException("Cancelled commissions cannot be adjusted")
        
        if not adjustment_reason or not adjusted_by:
            raise DomainException("Adjustment reason and user are required")
        
        if nuevo_monto.amount == self._commission_amount.amount:
            return  # No change needed
        
        original_amount = self._commission_amount
        self._commission_amount = nuevo_monto
        
        self._mark_updated()
        
        # Domain event
        self.agregar_evento(CommissionAdjusted(
            aggregate_id=self.id,
            partner_id=self._partner_id,
            original_amount=str(original_amount.amount),
            adjusted_amount=str(nuevo_monto.amount),
            adjustment_reason=adjustment_reason,
            adjusted_by=adjusted_by,
            adjustment_date=datetime.now().isoformat(),
            adjustment_type=adjustment_type
        ))
    
    def recalcular(
        self, 
        nueva_rate: CommissionRate, 
        nuevo_base_amount: Decimal,
        recalculation_reason: str, 
        recalculated_by: str
    ) -> None:
        """Recalculate commission with new rate or base amount."""
        
        # Business rules for recalculation
        if self._status in [CommissionStatus.PAID, CommissionStatus.CANCELLED]:
            raise BusinessRuleException("Paid or cancelled commissions cannot be recalculated")
        
        if not recalculation_reason or not recalculated_by:
            raise DomainException("Recalculation reason and user are required")
        
        old_amount = self._commission_amount.amount
        
        # Recalculate commission amount
        new_commission_amount = nueva_rate.calculate_commission(nuevo_base_amount)
        self._commission_amount = CommissionAmount(new_commission_amount, self._commission_amount.currency)
        self._commission_rate = nueva_rate
        
        # Update calculation details
        self._calculation_details = CommissionCalculation(
            base_amount=nuevo_base_amount,
            commission_rate=nueva_rate,
            commission_amount=self._commission_amount,
            calculation_method="percentage",
            calculation_date=datetime.now()
        )
        
        self._mark_updated()
        
        # Domain events
        self.agregar_evento(CommissionRecalculated(
            aggregate_id=self.id,
            partner_id=self._partner_id,
            old_amount=str(old_amount),
            new_amount=str(self._commission_amount.amount),
            recalculation_reason=recalculation_reason,
            recalculated_by=recalculated_by,
            recalculation_date=datetime.now().isoformat()
        ))
    
    def puede_ser_pagada(self) -> bool:
        """Check if commission can be paid."""
        return self._status == CommissionStatus.APPROVED
    
    def puede_ser_cancelada(self) -> bool:
        """Check if commission can be cancelled."""
        return self._status not in [CommissionStatus.PAID, CommissionStatus.CANCELLED]
    
    def puede_ser_ajustada(self) -> bool:
        """Check if commission can be adjusted."""
        return self._status not in [CommissionStatus.PAID, CommissionStatus.CANCELLED]
    
    def esta_vencida(self) -> bool:
        """Check if commission calculation period has expired."""
        return self._calculation_period.is_expired()
    
    def monto_neto(self) -> Decimal:
        """Get net commission amount after fees."""
        if self._payment_details:
            return self._payment_details.net_amount(self._commission_amount.amount)
        return self._commission_amount.amount
    
    def validate(self) -> None:
        """Validate commission state."""
        
        if not self._partner_id:
            raise DomainException("Commission must be assigned to a partner")
        
        if not self._commission_amount or not self._commission_rate:
            raise DomainException("Commission must have amount and rate")
        
        if not self._transaction_reference or not self._calculation_period:
            raise DomainException("Commission must have transaction reference and calculation period")
        
        # Validate status-specific requirements
        if self._status == CommissionStatus.APPROVED:
            if not self._approved_by or not self._approval_date:
                raise DomainException("Approved commission must have approval details")
        
        if self._status == CommissionStatus.PAID:
            if not self._payment_details or not self._payment_date:
                raise DomainException("Paid commission must have payment details")
        
        if self._status == CommissionStatus.CANCELLED:
            if not self._cancelled_by or not self._cancellation_reason:
                raise DomainException("Cancelled commission must have cancellation details")
        
        if self._status == CommissionStatus.ON_HOLD:
            if not self._held_by or not self._hold_reason:
                raise DomainException("Held commission must have hold details")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get commission summary."""
        
        return {
            'id': self.id,
            'partner_id': self._partner_id,
            'commission_amount': str(self._commission_amount.amount),
            'commission_currency': self._commission_amount.currency,
            'commission_rate': str(self._commission_rate.as_percentage()),
            'commission_type': self._commission_type.value,
            'status': self._status.value,
            'transaction_reference': self._transaction_reference.transaction_id,
            'transaction_amount': str(self._transaction_reference.transaction_amount),
            'calculation_period': {
                'start_date': self._calculation_period.start_date.isoformat(),
                'end_date': self._calculation_period.end_date.isoformat(),
                'period_name': self._calculation_period.period_name
            },
            'approval_details': {
                'approved_by': self._approved_by,
                'approval_date': self._approval_date.isoformat() if self._approval_date else None,
                'approval_notes': self._approval_notes
            } if self._status in [CommissionStatus.APPROVED, CommissionStatus.PAID] else None,
            'payment_details': {
                'payment_method': self._payment_details.payment_method.value if self._payment_details else None,
                'payment_date': self._payment_date.isoformat() if self._payment_date else None,
                'payment_reference': self._payment_reference,
                'net_amount': str(self.monto_neto())
            } if self._status == CommissionStatus.PAID else None,
            'timestamps': {
                'created_at': self.created_at.isoformat(),
                'updated_at': self.updated_at.isoformat()
            },
            'version': self.version
        }
    
    def __repr__(self) -> str:
        return (f"Commission(id={self.id}, partner_id={self._partner_id}, "
                f"amount={self._commission_amount.amount}, status={self._status.value})")