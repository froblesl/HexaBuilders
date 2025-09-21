"""
Business rules for Partner domain.
"""

from typing import Optional
from src.partner_management.seedwork.dominio.reglas import BusinessRule
from .objetos_valor import PartnerEmail, PartnerPhone, PartnerValidationData


class PartnerMustHaveValidEmail(BusinessRule):
    """Business rule: Partner must have a valid email."""
    
    def __init__(self, email: PartnerEmail):
        self.email = email
    
    def is_valid(self) -> bool:
        """Check if email is valid."""
        try:
            return bool(self.email and self.email.value and '@' in self.email.value)
        except Exception:
            return False
    
    def evaluate(self) -> bool:
        """Evaluate the business rule."""
        return self.is_valid()
    
    def get_message(self) -> str:
        return "Partner must have a valid email address"


class PartnerMustHaveValidPhone(BusinessRule):
    """Business rule: Partner must have a valid phone number."""
    
    def __init__(self, phone: PartnerPhone):
        self.phone = phone
    
    def is_valid(self) -> bool:
        """Check if phone is valid."""
        try:
            return bool(self.phone and self.phone.value and len(self.phone.value) >= 10)
        except Exception:
            return False
    
    def evaluate(self) -> bool:
        """Evaluate the business rule."""
        return self.is_valid()
    
    def get_message(self) -> str:
        return "Partner must have a valid phone number"


class PartnerCanOnlyBeActivatedIfValidated(BusinessRule):
    """Business rule: Partner can only be activated if validated."""
    
    def __init__(self, validation_data: Optional[PartnerValidationData]):
        self.validation_data = validation_data
    
    def is_valid(self) -> bool:
        """Check if partner can be activated."""
        if not self.validation_data:
            return False
        return self.validation_data.email_validated
    
    def evaluate(self) -> bool:
        """Evaluate the business rule."""
        return self.is_valid()
    
    def get_message(self) -> str:
        return "Partner must have validated email to be activated"


class PartnerCannotBeDeletedWithActiveCampaigns(BusinessRule):
    """Business rule: Partner cannot be deleted if they have active campaigns."""
    
    def __init__(self, active_campaigns_count: int):
        self.active_campaigns_count = active_campaigns_count
    
    def is_valid(self) -> bool:
        """Check if partner can be deleted."""
        return self.active_campaigns_count == 0
    
    def evaluate(self) -> bool:
        """Evaluate the business rule."""
        return self.is_valid()
    
    def get_message(self) -> str:
        return f"Partner cannot be deleted with {self.active_campaigns_count} active campaigns"