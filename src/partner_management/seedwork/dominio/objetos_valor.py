import re
from abc import ABC
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from typing import Any, Optional, Dict
from enum import Enum


class ValueObject(ABC):
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__
    
    def __hash__(self) -> int:
        return hash(tuple(sorted(self.__dict__.items())))
    
    def __repr__(self) -> str:
        attrs = ', '.join(f'{k}={v!r}' for k, v in self.__dict__.items())
        return f"{self.__class__.__name__}({attrs})"


@dataclass(frozen=True)
class Email(ValueObject):
    value: str
    
    def __post_init__(self):
        if not self.value:
            raise ValueError("El email no puede estar vacío")
        
        # Validación básica de email
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, self.value):
            raise ValueError(f"Formato de email inválido: {self.value}")
    
    def domain(self) -> str:
        return self.value.split('@')[1]
    
    def local_part(self) -> str:
        return self.value.split('@')[0]
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class PhoneNumber(ValueObject):
    value: str
    country_code: Optional[str] = None
    
    def __post_init__(self):
        if not self.value:
            raise ValueError("El número de teléfono no puede estar vacío")
        
        # Remover separadores comunes y validar que sea numérico
        clean_number = re.sub(r'[\s\-\(\)\+]', '', self.value)
        if not clean_number.isdigit():
            raise ValueError(f"Formato de número de teléfono inválido: {self.value}")
        
        if len(clean_number) < 7 or len(clean_number) > 15:
            raise ValueError(f"Longitud de número de teléfono inválida: {self.value}")
    
    def formatted(self) -> str:
        clean = re.sub(r'[\s\-\(\)\+]', '', self.value)
        if self.country_code and not self.value.startswith('+'):
            return f"+{self.country_code} {clean}"
        return self.value
    
    def __str__(self) -> str:
        return self.formatted()


class CurrencyCode(Enum):
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    COP = "COP"
    MXN = "MXN"
    BRL = "BRL"
    CAD = "CAD"
    AUD = "AUD"


@dataclass(frozen=True)
class Currency(ValueObject):
    amount: Decimal
    code: CurrencyCode
    
    def __post_init__(self):
        if not isinstance(self.amount, Decimal):
            try:
                # Convertir a Decimal si no lo es ya
                object.__setattr__(self, 'amount', Decimal(str(self.amount)))
            except (ValueError, InvalidOperation):
                raise ValueError(f"Cantidad de moneda inválida: {self.amount}")
        
        if self.amount < 0:
            raise ValueError("La cantidad de moneda no puede ser negativa")
    
    def add(self, other: 'Currency') -> 'Currency':
        if self.code != other.code:
            raise ValueError(f"No se pueden sumar monedas diferentes: {self.code} + {other.code}")
        return Currency(self.amount + other.amount, self.code)
    
    def subtract(self, other: 'Currency') -> 'Currency':
        if self.code != other.code:
            raise ValueError(f"No se pueden restar monedas diferentes: {self.code} - {other.code}")
        result_amount = self.amount - other.amount
        if result_amount < 0:
            raise ValueError("La cantidad de moneda no puede ser negativa después de la resta")
        return Currency(result_amount, self.code)
    
    def multiply(self, factor: Decimal) -> 'Currency':
        if not isinstance(factor, Decimal):
            factor = Decimal(str(factor))
        return Currency(self.amount * factor, self.code)
    
    def __str__(self) -> str:
        return f"{self.amount} {self.code.value}"


@dataclass(frozen=True)
class Percentage(ValueObject):
    value: Decimal
    
    def __post_init__(self):
        if not isinstance(self.value, Decimal):
            try:
                object.__setattr__(self, 'value', Decimal(str(self.value)))
            except (ValueError, InvalidOperation):
                raise ValueError(f"Valor de porcentaje inválido: {self.value}")
        
        if not (Decimal('0') <= self.value <= Decimal('100')):
            raise ValueError(f"El porcentaje debe estar entre 0 y 100: {self.value}")
    
    def as_decimal(self) -> Decimal:
        return self.value / Decimal('100')
    
    def apply_to(self, amount: Decimal) -> Decimal:
        return amount * self.as_decimal()
    
    def __str__(self) -> str:
        return f"{self.value}%"


@dataclass(frozen=True)
class BusinessId(ValueObject):
    value: str
    prefix: Optional[str] = None
    
    def __post_init__(self):
        if not self.value:
            raise ValueError("El ID de negocio no puede estar vacío")
        
        if len(self.value) < 3:
            raise ValueError("El ID de negocio debe tener al menos 3 caracteres")
        
        # Validación alfanumérica
        if not re.match(r'^[A-Za-z0-9\-_]+$', self.value):
            raise ValueError(f"El ID de negocio contiene caracteres inválidos: {self.value}")
    
    def formatted(self) -> str:
        return f"{self.prefix}-{self.value}" if self.prefix else self.value
    
    def __str__(self) -> str:
        return self.formatted()


@dataclass(frozen=True)
class Address(ValueObject):
    street: str
    city: str
    country: str
    postal_code: str
    state: Optional[str] = None
    
    def __post_init__(self):
        if not all([self.street, self.city, self.country, self.postal_code]):
            raise ValueError("La dirección debe tener calle, ciudad, país y código postal")
        
        if len(self.country) != 2:
            raise ValueError("El país debe ser un código ISO 3166-1 alpha-2")
        
        # Validación básica de código postal
        if len(self.postal_code) < 3:
            raise ValueError("Código postal demasiado corto")
    
    def full_address(self) -> str:
        parts = [self.street, self.city]
        if self.state:
            parts.append(self.state)
        parts.extend([self.postal_code, self.country.upper()])
        return ', '.join(parts)
    
    def __str__(self) -> str:
        return self.full_address()


class Status(Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    PENDING = "PENDING"
    SUSPENDED = "SUSPENDED"
    DELETED = "DELETED"


@dataclass(frozen=True)
class DateRange(ValueObject):
    start_date: str  # Fecha en formato ISO
    end_date: Optional[str] = None  # Fecha en formato ISO
    
    def __post_init__(self):
        if not self.start_date:
            raise ValueError("La fecha de inicio es requerida")
        
        # Validar formato de fecha ISO
        import datetime
        try:
            start = datetime.datetime.fromisoformat(self.start_date.replace('Z', '+00:00'))
            if self.end_date:
                end = datetime.datetime.fromisoformat(self.end_date.replace('Z', '+00:00'))
                if end <= start:
                    raise ValueError("La fecha de fin debe ser posterior a la fecha de inicio")
        except ValueError as e:
            raise ValueError(f"Formato de fecha inválido: {e}")
    
    def is_ongoing(self) -> bool:
        return self.end_date is None
    
    def duration_days(self) -> Optional[int]:
        if not self.end_date:
            return None
        
        import datetime
        start = datetime.datetime.fromisoformat(self.start_date.replace('Z', '+00:00'))
        end = datetime.datetime.fromisoformat(self.end_date.replace('Z', '+00:00'))
        return (end - start).days


@dataclass(frozen=True)
class Metadata(ValueObject):
    data: Dict[str, Any] = field(default_factory=dict)
    
    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)
    
    def has(self, key: str) -> bool:
        return key in self.data
    
    def with_data(self, key: str, value: Any) -> 'Metadata':
        new_data = self.data.copy()
        new_data[key] = value
        return Metadata(new_data)
    
    def __bool__(self) -> bool:
        return bool(self.data)
