"""
Data Transfer Objects (DTOs) for Commission module in HexaBuilders.
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict, Any


@dataclass
class CommissionDTO:
    """Commission Data Transfer Object."""
    
    id: str
    partner_id: str
    commission_amount: Decimal
    commission_currency: str
    commission_rate: Decimal
    commission_type: str
    status: str
    
    # Transaction reference
    transaction_id: str
    transaction_type: str
    transaction_amount: Decimal
    transaction_date: datetime
    
    # Calculation period
    calculation_period_start: datetime
    calculation_period_end: datetime
    period_name: str
    
    # Approval details
    approval_date: Optional[datetime] = None
    approved_by: Optional[str] = None
    approval_notes: Optional[str] = None
    
    # Payment details
    payment_date: Optional[datetime] = None
    payment_reference: Optional[str] = None
    payment_method: Optional[str] = None
    payment_fee: Optional[Decimal] = None
    bank_details: Optional[str] = None
    
    # Cancellation details
    cancellation_date: Optional[datetime] = None
    cancellation_reason: Optional[str] = None
    cancelled_by: Optional[str] = None
    
    # Hold details
    hold_date: Optional[datetime] = None
    hold_reason: Optional[str] = None
    held_by: Optional[str] = None
    
    # Calculation details
    calculation_method: Optional[str] = None
    calculation_date: Optional[datetime] = None
    base_amount: Optional[Decimal] = None
    
    # Metadata
    created_at: datetime
    updated_at: datetime
    version: int
    is_deleted: bool = False
    
    @classmethod
    def from_entity(cls, commission) -> 'CommissionDTO':
        """Create DTO from Commission entity."""
        
        return cls(
            id=commission.id,
            partner_id=commission.partner_id,
            commission_amount=commission.commission_amount.amount,
            commission_currency=commission.commission_amount.currency,
            commission_rate=commission.commission_rate.rate,
            commission_type=commission.commission_type.value,
            status=commission.status.value,
            
            # Transaction reference
            transaction_id=commission.transaction_reference.transaction_id,
            transaction_type=commission.transaction_reference.transaction_type,
            transaction_amount=commission.transaction_reference.transaction_amount,
            transaction_date=commission.transaction_reference.transaction_date,
            
            # Calculation period
            calculation_period_start=commission.calculation_period.start_date,
            calculation_period_end=commission.calculation_period.end_date,
            period_name=commission.calculation_period.period_name,
            
            # Approval details
            approval_date=commission.approval_date,
            approved_by=commission.approved_by,
            approval_notes=commission.approval_notes,
            
            # Payment details
            payment_date=commission.payment_date,
            payment_reference=commission.payment_reference,
            payment_method=commission.payment_details.payment_method.value if commission.payment_details else None,
            payment_fee=commission.payment_details.payment_fee if commission.payment_details else None,
            bank_details=commission.payment_details.bank_details if commission.payment_details else None,
            
            # Cancellation details (these need to be added to entity)
            cancellation_date=getattr(commission, '_cancellation_date', None),
            cancellation_reason=getattr(commission, '_cancellation_reason', None),
            cancelled_by=getattr(commission, '_cancelled_by', None),
            
            # Hold details
            hold_date=getattr(commission, '_hold_date', None),
            hold_reason=getattr(commission, '_hold_reason', None),
            held_by=getattr(commission, '_held_by', None),
            
            # Calculation details
            calculation_method=commission.calculation_details.calculation_method if commission.calculation_details else None,
            calculation_date=commission.calculation_details.calculation_date if commission.calculation_details else None,
            base_amount=commission.calculation_details.base_amount if commission.calculation_details else None,
            
            # Metadata
            created_at=commission.created_at,
            updated_at=commission.updated_at,
            version=commission.version,
            is_deleted=commission.is_deleted
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert DTO to dictionary."""
        
        return {
            'id': self.id,
            'partner_id': self.partner_id,
            'commission_amount': str(self.commission_amount),
            'commission_currency': self.commission_currency,
            'commission_rate': str(self.commission_rate),
            'commission_type': self.commission_type,
            'status': self.status,
            
            'transaction_reference': {
                'transaction_id': self.transaction_id,
                'transaction_type': self.transaction_type,
                'transaction_amount': str(self.transaction_amount),
                'transaction_date': self.transaction_date.isoformat()
            },
            
            'calculation_period': {
                'start_date': self.calculation_period_start.isoformat(),
                'end_date': self.calculation_period_end.isoformat(),
                'period_name': self.period_name
            },
            
            'approval_details': {
                'approval_date': self.approval_date.isoformat() if self.approval_date else None,
                'approved_by': self.approved_by,
                'approval_notes': self.approval_notes
            } if self.approval_date else None,
            
            'payment_details': {
                'payment_date': self.payment_date.isoformat() if self.payment_date else None,
                'payment_reference': self.payment_reference,
                'payment_method': self.payment_method,
                'payment_fee': str(self.payment_fee) if self.payment_fee else None,
                'bank_details': self.bank_details
            } if self.payment_date else None,
            
            'cancellation_details': {
                'cancellation_date': self.cancellation_date.isoformat() if self.cancellation_date else None,
                'cancellation_reason': self.cancellation_reason,
                'cancelled_by': self.cancelled_by
            } if self.cancellation_date else None,
            
            'hold_details': {
                'hold_date': self.hold_date.isoformat() if self.hold_date else None,
                'hold_reason': self.hold_reason,
                'held_by': self.held_by
            } if self.hold_date else None,
            
            'calculation_details': {
                'calculation_method': self.calculation_method,
                'calculation_date': self.calculation_date.isoformat() if self.calculation_date else None,
                'base_amount': str(self.base_amount) if self.base_amount else None
            } if self.calculation_method else None,
            
            'metadata': {
                'created_at': self.created_at.isoformat(),
                'updated_at': self.updated_at.isoformat(),
                'version': self.version,
                'is_deleted': self.is_deleted
            }
        }


@dataclass
class CommissionSummaryDTO:
    """Commission Summary Data Transfer Object for list views."""
    
    id: str
    partner_id: str
    commission_amount: Decimal
    commission_currency: str
    commission_type: str
    status: str
    transaction_id: str
    created_at: datetime
    approval_date: Optional[datetime] = None
    payment_date: Optional[datetime] = None
    
    @classmethod
    def from_entity(cls, commission) -> 'CommissionSummaryDTO':
        """Create summary DTO from Commission entity."""
        
        return cls(
            id=commission.id,
            partner_id=commission.partner_id,
            commission_amount=commission.commission_amount.amount,
            commission_currency=commission.commission_amount.currency,
            commission_type=commission.commission_type.value,
            status=commission.status.value,
            transaction_id=commission.transaction_reference.transaction_id,
            created_at=commission.created_at,
            approval_date=commission.approval_date,
            payment_date=commission.payment_date
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert summary DTO to dictionary."""
        
        return {
            'id': self.id,
            'partner_id': self.partner_id,
            'commission_amount': str(self.commission_amount),
            'commission_currency': self.commission_currency,
            'commission_type': self.commission_type,
            'status': self.status,
            'transaction_id': self.transaction_id,
            'created_at': self.created_at.isoformat(),
            'approval_date': self.approval_date.isoformat() if self.approval_date else None,
            'payment_date': self.payment_date.isoformat() if self.payment_date else None
        }


@dataclass
class CommissionAnalyticsDTO:
    """Commission Analytics Data Transfer Object."""
    
    partner_id: str
    total_commissions: int
    total_earned: Decimal
    total_paid: Decimal
    total_pending: Decimal
    average_commission: Decimal
    success_rate: float
    status_breakdown: Dict[str, int]
    type_breakdown: Dict[str, int]
    monthly_summary: Dict[str, Dict[str, Any]]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert analytics DTO to dictionary."""
        
        return {
            'partner_id': self.partner_id,
            'total_commissions': self.total_commissions,
            'total_earned': str(self.total_earned),
            'total_paid': str(self.total_paid),
            'total_pending': str(self.total_pending),
            'average_commission': str(self.average_commission),
            'success_rate': self.success_rate,
            'status_breakdown': self.status_breakdown,
            'type_breakdown': self.type_breakdown,
            'monthly_summary': self.monthly_summary
        }