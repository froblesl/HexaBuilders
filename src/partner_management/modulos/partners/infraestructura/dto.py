"""
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, Any, Optional

from ..dominio.entidades import Partner


@dataclass
class PartnerDTO:
    """Data Transfer Object for Partner entity."""
    
    id: str
    nombre: str
    email: str
    telefono: str
    tipo: str
    status: str
    direccion: Optional[str] = None
    ciudad: Optional[str] = None
    pais: Optional[str] = None
    fecha_creacion: Optional[str] = None
    fecha_actualizacion: Optional[str] = None
    validaciones: Optional[Dict[str, bool]] = None
    metricas: Optional[Dict[str, Any]] = None
    
    @classmethod
    def from_entity(cls, partner: Partner) -> 'PartnerDTO':
        """Create DTO from Partner entity."""
        
        # Convert validation data
        validaciones = None
        if partner.validation_data:
            validaciones = {
                'email_validado': partner.validation_data.email_validated,
                'telefono_validado': partner.validation_data.phone_validated,
                'identidad_validada': partner.validation_data.identity_validated,
                'negocio_validado': partner.validation_data.business_validated
            }
        
        # Convert metrics
        metricas = None
        if partner.metrics:
            metricas = {
                'total_campanas': partner.metrics.total_campaigns,
                'campanas_completadas': partner.metrics.completed_campaigns,
                'tasa_exito': partner.metrics.success_rate,
                'comisiones_totales': partner.metrics.total_commissions,
                'calificacion_promedio': partner.metrics.average_rating
            }
        
        return cls(
            id=partner.id,
            nombre=partner.name.value,
            email=partner.email.value,
            telefono=partner.phone.value,
            tipo=partner.type.value,
            status=partner.status.value,
            direccion=partner.direccion,
            ciudad=partner.ciudad,
            pais=partner.pais,
            fecha_creacion=partner.created_at.isoformat() if partner.created_at else None,
            fecha_actualizacion=partner.updated_at.isoformat() if partner.updated_at else None,
            validaciones=validaciones,
            metricas=metricas
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert DTO to dictionary."""
        return asdict(self)


@dataclass
class CreatePartnerDTO:
    """DTO for creating a partner."""
    
    nombre: str
    email: str
    telefono: str
    tipo: str
    direccion: Optional[str] = None
    ciudad: Optional[str] = None
    pais: Optional[str] = None


@dataclass
class UpdatePartnerDTO:
    """DTO for updating a partner."""
    
    nombre: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    ciudad: Optional[str] = None
    pais: Optional[str] = None


@dataclass
class PartnerFilterDTO:
    """DTO for filtering partners."""
    
    status: Optional[str] = None
    tipo: Optional[str] = None
    ciudad: Optional[str] = None
    pais: Optional[str] = None
    email_validado: Optional[bool] = None
    fecha_creacion_desde: Optional[str] = None
    fecha_creacion_hasta: Optional[str] = None


@dataclass
class PartnerListResponseDTO:
    """DTO for partner list response."""
    
    partners: list[PartnerDTO]
    total: int
    page: int
    page_size: int
    total_pages: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'partners': [partner.to_dict() for partner in self.partners],
            'total': self.total,
            'page': self.page,
            'page_size': self.page_size,
            'total_pages': self.total_pages
        }


@dataclass
class PartnerStatusChangeDTO:
    """DTO for partner status changes."""
    
    partner_id: str
    new_status: str
    changed_by: Optional[str] = None
    reason: Optional[str] = None


@dataclass
class PartnerValidationDTO:
    """DTO for partner validation operations."""
    
    partner_id: str
    validation_type: str  # email, phone, identity, business
    validation_data: Optional[Dict[str, Any]] = None
    validated_by: Optional[str] = None


@dataclass
class PartnerMetricsDTO:
    """DTO for partner metrics."""
    
    partner_id: str
    total_campaigns: int = 0
    completed_campaigns: int = 0
    success_rate: float = 0.0
    total_commissions: float = 0.0
    average_rating: float = 0.0
    last_activity: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class PartnerSummaryDTO:
    """DTO for partner summary information."""
    
    id: str
    nombre: str
    email: str
    tipo: str
    status: str
    fecha_creacion: Optional[str] = None
    total_campanas: int = 0
    calificacion_promedio: float = 0.0
    
    @classmethod
    def from_partner_dto(cls, partner_dto: PartnerDTO) -> 'PartnerSummaryDTO':
        """Create summary from full PartnerDTO."""
        return cls(
            id=partner_dto.id,
            nombre=partner_dto.nombre,
            email=partner_dto.email,
            tipo=partner_dto.tipo,
            status=partner_dto.status,
            fecha_creacion=partner_dto.fecha_creacion,
            total_campanas=partner_dto.metricas.get('total_campanas', 0) if partner_dto.metricas else 0,
            calificacion_promedio=partner_dto.metricas.get('calificacion_promedio', 0.0) if partner_dto.metricas else 0.0
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)