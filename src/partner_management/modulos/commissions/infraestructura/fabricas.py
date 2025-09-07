"""
Factory classes for Commission module in HexaBuilders.
"""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from ....seedwork.dominio.fabricas import Fabrica
from ....seedwork.dominio.excepciones import DomainException

from ..dominio.entidades import Commission
from ..dominio.objetos_valor import (
    CommissionAmount, CommissionRate, CommissionPeriod, TransactionReference,
    CommissionType, CommissionStatus, CommissionCalculation, PaymentDetails,
    PaymentMethod
)
from .dto import CommissionDTO


class FabricaCommission(Fabrica):
    """Factory for creating Commission entities and related objects."""
    
    def crear_commission(
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
    ) -> Commission:
        """Create a Commission entity."""
        
        # Validate required parameters
        if not partner_id:
            raise DomainException("Partner ID is required to create commission")
        
        if not commission_amount or not commission_rate:
            raise DomainException("Commission amount and rate are required")
        
        if not transaction_reference or not calculation_period:
            raise DomainException("Transaction reference and calculation period are required")
        
        # Generate ID if not provided
        if not commission_id:
            commission_id = str(uuid.uuid4())
        
        # Create Commission entity
        commission = Commission(
            partner_id=partner_id,
            commission_amount=commission_amount,
            commission_rate=commission_rate,
            commission_type=commission_type,
            transaction_reference=transaction_reference,
            calculation_period=calculation_period,
            commission_id=commission_id,
            status=status,
            calculation_details=calculation_details,
            payment_details=payment_details
        )
        
        return commission
    
    def crear_commission_from_dto(self, dto: CommissionDTO) -> Commission:
        """Create Commission entity from DTO."""
        
        # Create value objects
        commission_amount = CommissionAmount(dto.commission_amount, dto.commission_currency)
        commission_rate = CommissionRate(dto.commission_rate)
        commission_type = CommissionType(dto.commission_type)
        
        transaction_reference = TransactionReference(
            transaction_id=dto.transaction_id,
            transaction_type=dto.transaction_type,
            transaction_amount=dto.transaction_amount,
            transaction_date=dto.transaction_date
        )
        
        calculation_period = CommissionPeriod(
            start_date=dto.calculation_period_start,
            end_date=dto.calculation_period_end,
            period_name=dto.period_name
        )
        
        status = CommissionStatus(dto.status)
        
        # Create calculation details if available
        calculation_details = None
        if dto.calculation_method:
            calculation_details = CommissionCalculation(
                base_amount=dto.base_amount or Decimal('0'),
                commission_rate=commission_rate,
                commission_amount=commission_amount,
                calculation_method=dto.calculation_method,
                calculation_date=dto.calculation_date or datetime.now()
            )
        
        # Create payment details if available
        payment_details = None
        if dto.payment_method:
            payment_details = PaymentDetails(
                payment_method=PaymentMethod(dto.payment_method),
                payment_reference=dto.payment_reference or "",
                payment_date=dto.payment_date or datetime.now(),
                payment_fee=dto.payment_fee or Decimal('0'),
                bank_details=dto.bank_details
            )
        
        # Create Commission entity
        commission = Commission(
            partner_id=dto.partner_id,
            commission_amount=commission_amount,
            commission_rate=commission_rate,
            commission_type=commission_type,
            transaction_reference=transaction_reference,
            calculation_period=calculation_period,
            commission_id=dto.id,
            status=status,
            calculation_details=calculation_details,
            payment_details=payment_details
        )
        
        # Set additional fields that aren't in constructor
        if dto.approval_date:
            commission._approval_date = dto.approval_date
            commission._approved_by = dto.approved_by
            commission._approval_notes = dto.approval_notes
        
        if dto.payment_date:
            commission._payment_date = dto.payment_date
            commission._payment_reference = dto.payment_reference
        
        if dto.cancellation_date:
            commission._cancellation_date = dto.cancellation_date
            commission._cancellation_reason = dto.cancellation_reason
            commission._cancelled_by = dto.cancelled_by
        
        if dto.hold_date:
            commission._hold_date = dto.hold_date
            commission._hold_reason = dto.hold_reason
            commission._held_by = dto.held_by
        
        # Set metadata
        commission._created_at = dto.created_at
        commission._updated_at = dto.updated_at
        commission._version = dto.version
        commission._is_deleted = dto.is_deleted
        
        return commission
    
    def crear_commission_automatica(
        self,
        partner_id: str,
        transaction_amount: Decimal,
        commission_rate: Decimal,
        transaction_id: str,
        transaction_type: str = "SALE",
        commission_type: str = "SALE_COMMISSION",
        currency: str = "USD"
    ) -> Commission:
        """
        Create an automatic commission based on transaction data.
        """
        
        # Calculate commission amount
        commission_amount_value = transaction_amount * commission_rate
        
        # Create value objects
        commission_amount = CommissionAmount(commission_amount_value, currency)
        commission_rate_obj = CommissionRate(commission_rate)
        commission_type_obj = CommissionType(commission_type)
        
        transaction_reference = TransactionReference(
            transaction_id=transaction_id,
            transaction_type=transaction_type,
            transaction_amount=transaction_amount,
            transaction_date=datetime.now()
        )
        
        # Create calculation period (current month)
        now = datetime.now()
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        calculation_period = CommissionPeriod(
            start_date=start_of_month,
            end_date=now,
            period_name=f"Auto Commission - {now.strftime('%Y-%m')}"
        )
        
        # Create calculation details
        calculation_details = CommissionCalculation(
            base_amount=transaction_amount,
            commission_rate=commission_rate_obj,
            commission_amount=commission_amount,
            calculation_method="percentage",
            calculation_date=datetime.now()
        )
        
        return self.crear_commission(
            partner_id=partner_id,
            commission_amount=commission_amount,
            commission_rate=commission_rate_obj,
            commission_type=commission_type_obj,
            transaction_reference=transaction_reference,
            calculation_period=calculation_period,
            calculation_details=calculation_details
        )
    
    def crear_commission_performance_bonus(
        self,
        partner_id: str,
        performance_data: dict,
        bonus_rate: Decimal = Decimal('0.05'),
        currency: str = "USD"
    ) -> Commission:
        """
        Create a performance bonus commission.
        """
        
        # Calculate performance bonus
        base_amount = Decimal(str(performance_data.get('total_value', 0)))
        success_multiplier = min(performance_data.get('success_rate', 0), 1.0)
        bonus_amount = base_amount * bonus_rate * Decimal(str(success_multiplier))
        
        # Create value objects
        commission_amount = CommissionAmount(bonus_amount, currency)
        commission_rate_obj = CommissionRate(bonus_rate)
        commission_type_obj = CommissionType('PERFORMANCE_BONUS')
        
        transaction_reference = TransactionReference(
            transaction_id=f"perf_{uuid.uuid4().hex[:8]}",
            transaction_type="PERFORMANCE_BONUS",
            transaction_amount=base_amount,
            transaction_date=datetime.now()
        )
        
        # Create calculation period
        now = datetime.now()
        calculation_period = CommissionPeriod(
            start_date=now,
            end_date=now,
            period_name=f"Performance Bonus - {now.strftime('%Y-%m')}"
        )
        
        # Create calculation details
        calculation_details = CommissionCalculation(
            base_amount=base_amount,
            commission_rate=commission_rate_obj,
            commission_amount=commission_amount,
            calculation_method="performance_based",
            calculation_date=datetime.now()
        )
        
        return self.crear_commission(
            partner_id=partner_id,
            commission_amount=commission_amount,
            commission_rate=commission_rate_obj,
            commission_type=commission_type_obj,
            transaction_reference=transaction_reference,
            calculation_period=calculation_period,
            calculation_details=calculation_details
        )