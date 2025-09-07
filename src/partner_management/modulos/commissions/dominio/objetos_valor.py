"""
Commission domain value objects for HexaBuilders.
Implements commission-related value objects following DDD patterns.
"""

import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional
from datetime import datetime
from decimal import Decimal

from ....seedwork.dominio.objetos_valor import ObjetoValor
from ....seedwork.dominio.excepciones import DomainException


class CommissionStatus(Enum):
    """Commission status enumeration."""
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    PAID = "PAID"
    CANCELLED = "CANCELLED"
    DISPUTED = "DISPUTED"
    ON_HOLD = "ON_HOLD"


class CommissionType(Enum):
    """Commission type enumeration."""
    SALE_COMMISSION = "SALE_COMMISSION"
    LEAD_COMMISSION = "LEAD_COMMISSION"
    PERFORMANCE_BONUS = "PERFORMANCE_BONUS"
    REFERRAL_BONUS = "REFERRAL_BONUS"
    MILESTONE_BONUS = "MILESTONE_BONUS"


class PaymentMethod(Enum):
    """Payment method enumeration."""
    BANK_TRANSFER = "BANK_TRANSFER"
    PAYPAL = "PAYPAL"
    STRIPE = "STRIPE"
    CHECK = "CHECK"
    CRYPTO = "CRYPTO"


@dataclass(frozen=True)
class CommissionAmount(ObjetoValor):
    """Commission amount value object."""
    
    amount: Decimal
    currency: str = "USD"
    
    def __post_init__(self):
        self._validate()
    
    def _validate(self):
        if not isinstance(self.amount, (Decimal, int, float)):
            raise DomainException("Commission amount must be a number")
        
        if self.amount < 0:
            raise DomainException("Commission amount cannot be negative")
        
        if self.amount > Decimal('100000'):
            raise DomainException("Commission amount cannot exceed 100,000")
        
        if not self.currency or len(self.currency) != 3:
            raise DomainException("Currency must be a valid 3-letter code")
        
        # Convert to Decimal for precision
        if not isinstance(self.amount, Decimal):
            object.__setattr__(self, 'amount', Decimal(str(self.amount)))


@dataclass(frozen=True)
class CommissionRate(ObjetoValor):
    """Commission rate value object."""
    
    rate: Decimal  # Percentage as decimal (0.05 = 5%)
    
    def __post_init__(self):
        self._validate()
    
    def _validate(self):
        if not isinstance(self.rate, (Decimal, int, float)):
            raise DomainException("Commission rate must be a number")
        
        if self.rate < 0:
            raise DomainException("Commission rate cannot be negative")
        
        if self.rate > 1:
            raise DomainException("Commission rate cannot exceed 100% (1.0)")
        
        # Convert to Decimal for precision
        if not isinstance(self.rate, Decimal):
            object.__setattr__(self, 'rate', Decimal(str(self.rate)))
    
    def as_percentage(self) -> Decimal:
        """Get rate as percentage (0.05 -> 5)."""
        return self.rate * 100
    
    def calculate_commission(self, base_amount: Decimal) -> Decimal:
        """Calculate commission amount from base amount."""
        return base_amount * self.rate


@dataclass(frozen=True)
class CommissionPeriod(ObjetoValor):
    """Commission calculation period value object."""
    
    start_date: datetime
    end_date: datetime
    period_name: str
    
    def __post_init__(self):
        self._validate()
    
    def _validate(self):
        if not isinstance(self.start_date, datetime):
            raise DomainException("Start date must be a datetime")
        
        if not isinstance(self.end_date, datetime):
            raise DomainException("End date must be a datetime")
        
        if self.start_date >= self.end_date:
            raise DomainException("Start date must be before end date")
        
        if not self.period_name or len(self.period_name.strip()) < 2:
            raise DomainException("Period name must be at least 2 characters")
        
        # Check reasonable period duration
        duration = self.end_date - self.start_date
        if duration.days > 366:  # More than a year
            raise DomainException("Commission period cannot exceed 1 year")
        
        if duration.days < 1:
            raise DomainException("Commission period must be at least 1 day")
    
    def is_active_on(self, date: datetime) -> bool:
        """Check if commission period is active on given date."""
        return self.start_date <= date <= self.end_date
    
    def duration_in_days(self) -> int:
        """Get period duration in days."""
        return (self.end_date - self.start_date).days
    
    def is_expired(self) -> bool:
        """Check if period has expired."""
        return datetime.now() > self.end_date


@dataclass(frozen=True)
class TransactionReference(ObjetoValor):
    """Transaction reference value object."""
    
    transaction_id: str
    transaction_type: str
    transaction_amount: Decimal
    transaction_date: datetime
    
    def __post_init__(self):
        self._validate()
    
    def _validate(self):
        if not self.transaction_id or len(self.transaction_id.strip()) < 3:
            raise DomainException("Transaction ID must be at least 3 characters")
        
        if not self.transaction_type:
            raise DomainException("Transaction type is required")
        
        valid_types = ['sale', 'lead', 'signup', 'conversion', 'milestone']
        if self.transaction_type.lower() not in valid_types:
            raise DomainException(f"Transaction type must be one of: {valid_types}")
        
        if not isinstance(self.transaction_amount, (Decimal, int, float)):
            raise DomainException("Transaction amount must be a number")
        
        if self.transaction_amount < 0:
            raise DomainException("Transaction amount cannot be negative")
        
        if not isinstance(self.transaction_date, datetime):
            raise DomainException("Transaction date must be a datetime")
        
        # Convert to Decimal for precision
        if not isinstance(self.transaction_amount, Decimal):
            object.__setattr__(self, 'transaction_amount', Decimal(str(self.transaction_amount)))


@dataclass(frozen=True)
class PaymentDetails(ObjetoValor):
    """Payment details value object."""
    
    payment_method: PaymentMethod
    payment_reference: Optional[str] = None
    payment_date: Optional[datetime] = None
    payment_fee: Decimal = Decimal('0.00')
    bank_details: Optional[str] = None
    
    def __post_init__(self):
        self._validate()
    
    def _validate(self):
        if not isinstance(self.payment_method, PaymentMethod):
            raise DomainException("Payment method must be a valid PaymentMethod")
        
        if self.payment_reference and len(self.payment_reference.strip()) < 3:
            raise DomainException("Payment reference must be at least 3 characters")
        
        if self.payment_date and not isinstance(self.payment_date, datetime):
            raise DomainException("Payment date must be a datetime")
        
        if not isinstance(self.payment_fee, (Decimal, int, float)):
            raise DomainException("Payment fee must be a number")
        
        if self.payment_fee < 0:
            raise DomainException("Payment fee cannot be negative")
        
        # Convert to Decimal for precision
        if not isinstance(self.payment_fee, Decimal):
            object.__setattr__(self, 'payment_fee', Decimal(str(self.payment_fee)))
        
        # Validate bank details for bank transfer
        if (self.payment_method == PaymentMethod.BANK_TRANSFER and 
            not self.bank_details):
            raise DomainException("Bank details required for bank transfer")
    
    def net_amount(self, gross_amount: Decimal) -> Decimal:
        """Calculate net amount after payment fees."""
        return gross_amount - self.payment_fee


@dataclass(frozen=True)
class CommissionCalculation(ObjetoValor):
    """Commission calculation details value object."""
    
    base_amount: Decimal
    commission_rate: CommissionRate
    commission_amount: CommissionAmount
    calculation_method: str
    calculation_date: datetime
    
    def __post_init__(self):
        self._validate()
    
    def _validate(self):
        if not isinstance(self.base_amount, (Decimal, int, float)):
            raise DomainException("Base amount must be a number")
        
        if self.base_amount < 0:
            raise DomainException("Base amount cannot be negative")
        
        if not isinstance(self.commission_rate, CommissionRate):
            raise DomainException("Commission rate must be a CommissionRate object")
        
        if not isinstance(self.commission_amount, CommissionAmount):
            raise DomainException("Commission amount must be a CommissionAmount object")
        
        if not self.calculation_method:
            raise DomainException("Calculation method is required")
        
        valid_methods = ['percentage', 'fixed', 'tiered', 'progressive']
        if self.calculation_method not in valid_methods:
            raise DomainException(f"Calculation method must be one of: {valid_methods}")
        
        if not isinstance(self.calculation_date, datetime):
            raise DomainException("Calculation date must be a datetime")
        
        # Convert to Decimal for precision
        if not isinstance(self.base_amount, Decimal):
            object.__setattr__(self, 'base_amount', Decimal(str(self.base_amount)))
        
        # Validate calculation consistency for percentage method
        if self.calculation_method == 'percentage':
            expected_amount = self.commission_rate.calculate_commission(self.base_amount)
            if abs(expected_amount - self.commission_amount.amount) > Decimal('0.01'):
                raise DomainException("Commission amount doesn't match rate calculation")
    
    def verification_hash(self) -> str:
        """Generate verification hash for calculation integrity."""
        import hashlib
        
        data = f"{self.base_amount}:{self.commission_rate.rate}:{self.commission_amount.amount}:{self.calculation_method}:{self.calculation_date.isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]


@dataclass(frozen=True)
class CommissionTier(ObjetoValor):
    """Commission tier for tiered commission structures."""
    
    tier_name: str
    minimum_amount: Decimal
    maximum_amount: Optional[Decimal]
    tier_rate: CommissionRate
    
    def __post_init__(self):
        self._validate()
    
    def _validate(self):
        if not self.tier_name or len(self.tier_name.strip()) < 2:
            raise DomainException("Tier name must be at least 2 characters")
        
        if not isinstance(self.minimum_amount, (Decimal, int, float)):
            raise DomainException("Minimum amount must be a number")
        
        if self.minimum_amount < 0:
            raise DomainException("Minimum amount cannot be negative")
        
        if self.maximum_amount is not None:
            if not isinstance(self.maximum_amount, (Decimal, int, float)):
                raise DomainException("Maximum amount must be a number")
            
            if self.maximum_amount <= self.minimum_amount:
                raise DomainException("Maximum amount must be greater than minimum amount")
        
        if not isinstance(self.tier_rate, CommissionRate):
            raise DomainException("Tier rate must be a CommissionRate object")
        
        # Convert to Decimal for precision
        if not isinstance(self.minimum_amount, Decimal):
            object.__setattr__(self, 'minimum_amount', Decimal(str(self.minimum_amount)))
        
        if self.maximum_amount and not isinstance(self.maximum_amount, Decimal):
            object.__setattr__(self, 'maximum_amount', Decimal(str(self.maximum_amount)))
    
    def applies_to_amount(self, amount: Decimal) -> bool:
        """Check if this tier applies to the given amount."""
        if amount < self.minimum_amount:
            return False
        
        if self.maximum_amount is not None and amount > self.maximum_amount:
            return False
        
        return True
    
    def calculate_tier_commission(self, amount: Decimal) -> Decimal:
        """Calculate commission for this tier."""
        if not self.applies_to_amount(amount):
            return Decimal('0.00')
        
        # Calculate commission on the portion that falls within this tier
        effective_amount = amount
        if self.maximum_amount:
            effective_amount = min(amount, self.maximum_amount)
        
        tier_amount = effective_amount - self.minimum_amount
        return self.tier_rate.calculate_commission(tier_amount)