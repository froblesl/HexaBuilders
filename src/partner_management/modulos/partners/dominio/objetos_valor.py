"""
"""

import re
from dataclasses import dataclass
from enum import Enum
from typing import Any

from ...seedwork.dominio.objetos_valor import ObjetoValor
from ...seedwork.dominio.excepciones import DomainException


class PartnerType(Enum):
    """Partner types enumeration."""
    INDIVIDUAL = "INDIVIDUAL"
    EMPRESA = "EMPRESA" 
    STARTUP = "STARTUP"


class PartnerStatus(Enum):
    """Partner status enumeration."""
    ACTIVO = "ACTIVO"
    INACTIVO = "INACTIVO"
    SUSPENDIDO = "SUSPENDIDO"
    ELIMINADO = "ELIMINADO"
    VALIDADO = "VALIDADO"


@dataclass(frozen=True)
class PartnerName(ObjetoValor):
    """Partner name value object."""
    
    value: str
    
    def __post_init__(self):
        self._validate()
    
    def _validate(self):
        if not self.value or not isinstance(self.value, str):
            raise DomainException("Partner name cannot be empty")
        
        if len(self.value.strip()) < 2:
            raise DomainException("Partner name must be at least 2 characters long")
        
        if len(self.value.strip()) > 100:
            raise DomainException("Partner name cannot exceed 100 characters")
        
        # Only allow letters, numbers, spaces and common punctuation
        if not re.match(r'^[a-zA-ZÀ-ÿ0-9\s\.\-\_\&\,]+$', self.value.strip()):
            raise DomainException("Partner name contains invalid characters")


@dataclass(frozen=True)
class PartnerEmail(ObjetoValor):
    """Partner email value object."""
    
    value: str
    
    def __post_init__(self):
        self._validate()
    
    def _validate(self):
        if not self.value or not isinstance(self.value, str):
            raise DomainException("Email cannot be empty")
        
        # Basic email validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, self.value.lower()):
            raise DomainException("Invalid email format")
        
        if len(self.value) > 254:  # RFC 5321 limit
            raise DomainException("Email address too long")


@dataclass(frozen=True)
class PartnerPhone(ObjetoValor):
    """Partner phone value object."""
    
    value: str
    
    def __post_init__(self):
        self._validate()
    
    def _validate(self):
        if not self.value or not isinstance(self.value, str):
            raise DomainException("Phone number cannot be empty")
        
        # Remove spaces and common separators for validation
        clean_phone = re.sub(r'[\s\-\(\)\+]', '', self.value)
        
        if len(clean_phone) < 7:
            raise DomainException("Phone number too short")
        
        if len(clean_phone) > 15:
            raise DomainException("Phone number too long")
        
        # Only allow digits, spaces, parentheses, plus, and hyphens
        if not re.match(r'^[\d\s\-\(\)\+]+$', self.value):
            raise DomainException("Phone number contains invalid characters")


@dataclass(frozen=True)
class PartnerAddress(ObjetoValor):
    """Partner address value object."""
    
    direccion: str
    ciudad: str
    pais: str
    codigo_postal: str = ""
    
    def __post_init__(self):
        self._validate()
    
    def _validate(self):
        if not self.direccion or len(self.direccion.strip()) < 5:
            raise DomainException("Address must be at least 5 characters long")
        
        if not self.ciudad or len(self.ciudad.strip()) < 2:
            raise DomainException("City must be at least 2 characters long")
        
        if not self.pais or len(self.pais.strip()) < 2:
            raise DomainException("Country must be at least 2 characters long")
        
        if len(self.direccion) > 200:
            raise DomainException("Address cannot exceed 200 characters")
        
        if len(self.ciudad) > 50:
            raise DomainException("City cannot exceed 50 characters")
        
        if len(self.pais) > 50:
            raise DomainException("Country cannot exceed 50 characters")


@dataclass(frozen=True)
class PartnerValidationData(ObjetoValor):
    """Partner validation data value object."""
    
    email_validated: bool = False
    phone_validated: bool = False
    identity_validated: bool = False
    business_validated: bool = False
    
    def is_fully_validated(self) -> bool:
        """Check if partner is fully validated."""
        return all([
            self.email_validated,
            self.phone_validated,
            self.identity_validated
        ])
    
    def is_business_validated(self) -> bool:
        """Check if business validation is complete (for business partners)."""
        return self.business_validated
    
    def validation_percentage(self) -> float:
        """Get validation completion percentage."""
        validations = [
            self.email_validated,
            self.phone_validated, 
            self.identity_validated,
            self.business_validated
        ]
        return sum(validations) / len(validations)


@dataclass(frozen=True)
class PartnerMetrics(ObjetoValor):
    """Partner performance metrics value object."""
    
    total_campaigns: int = 0
    completed_campaigns: int = 0
    success_rate: float = 0.0
    total_commissions: float = 0.0
    average_rating: float = 0.0
    
    def __post_init__(self):
        self._validate()
    
    def _validate(self):
        if self.total_campaigns < 0:
            raise DomainException("Total campaigns cannot be negative")
        
        if self.completed_campaigns < 0:
            raise DomainException("Completed campaigns cannot be negative")
        
        if self.completed_campaigns > self.total_campaigns:
            raise DomainException("Completed campaigns cannot exceed total campaigns")
        
        if not (0.0 <= self.success_rate <= 1.0):
            raise DomainException("Success rate must be between 0.0 and 1.0")
        
        if self.total_commissions < 0:
            raise DomainException("Total commissions cannot be negative")
        
        if not (0.0 <= self.average_rating <= 5.0):
            raise DomainException("Average rating must be between 0.0 and 5.0")
    
    def calculate_success_rate(self) -> float:
        """Calculate success rate from completed vs total campaigns."""
        if self.total_campaigns == 0:
            return 0.0
        return self.completed_campaigns / self.total_campaigns