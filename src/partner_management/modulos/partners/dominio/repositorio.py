"""
Partner repository interfaces.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict
from .entidades import Partner
from .objetos_valor import PartnerStatus, PartnerType


class PartnerRepository(ABC):
    """Abstract repository for Partner aggregates."""

    @abstractmethod
    def obtener_por_id(self, partner_id: str) -> Optional[Partner]:
        """Get partner by ID."""
        pass

    @abstractmethod  
    def obtener_por_email(self, email: str) -> Optional[Partner]:
        """Get partner by email."""
        pass

    @abstractmethod
    def obtener_todos(
        self, 
        filtros: Optional[Dict[str, str]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Partner]:
        """Get all partners with optional filtering."""
        pass

    @abstractmethod
    def contar_con_filtros(self, filtros: Optional[Dict[str, str]] = None) -> int:
        """Count partners with filters."""
        pass

    @abstractmethod
    def agregar(self, partner: Partner) -> None:
        """Add new partner."""
        pass

    @abstractmethod
    def actualizar(self, partner: Partner) -> None:
        """Update existing partner."""
        pass

    @abstractmethod
    def eliminar(self, partner: Partner) -> None:
        """Remove partner."""
        pass

    @abstractmethod
    def obtener_por_status(self, status: PartnerStatus) -> List[Partner]:
        """Get partners by status."""
        pass

    @abstractmethod
    def obtener_por_tipo(self, tipo: PartnerType) -> List[Partner]:
        """Get partners by type."""
        pass

    @abstractmethod
    def obtener_activos(self) -> List[Partner]:
        """Get active partners."""
        pass

    @abstractmethod
    def buscar_por_nombre(self, nombre_parcial: str) -> List[Partner]:
        """Search partners by partial name match."""
        pass

    @abstractmethod
    def existe_con_email(self, email: str) -> bool:
        """Check if partner with email exists."""
        pass