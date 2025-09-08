"""
Campaign Data Transfer Objects for HexaBuilders.
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, Any, Optional, List
from decimal import Decimal

from ..dominio.entidades import Campaign


@dataclass
class CampaignDTO:
    """Data Transfer Object for Campaign entity."""
    
    id: str
    nombre: str
    descripcion: str
    partner_id: str
    tipo: str
    status: str
    presupuesto_amount: str
    presupuesto_currency: str
    fecha_inicio: str
    fecha_fin: str
    fecha_creacion: Optional[str] = None
    fecha_actualizacion: Optional[str] = None
    targeting: Optional[Dict[str, Any]] = None
    settings: Optional[Dict[str, Any]] = None
    metricas: Optional[Dict[str, Any]] = None
    approval: Optional[Dict[str, Any]] = None
    
    @classmethod
    def from_entity(cls, campaign: Campaign) -> 'CampaignDTO':
        """Create DTO from Campaign entity."""
        
        # Convert targeting data
        targeting = None
        if campaign.targeting:
            targeting = {
                'countries': campaign.targeting.countries,
                'age_range': campaign.targeting.age_range,
                'interests': campaign.targeting.interests,
                'keywords': campaign.targeting.keywords
            }
        
        # Convert settings
        settings = None
        if campaign.settings:
            settings = {
                'auto_pause_on_budget_exceeded': campaign.settings.auto_pause_on_budget_exceeded,
                'daily_budget_limit': str(campaign.settings.daily_budget_limit) if campaign.settings.daily_budget_limit else None,
                'bid_strategy': campaign.settings.bid_strategy,
                'placement_types': campaign.settings.placement_types
            }
        
        # Convert metrics
        metricas = None
        if campaign.metricas:
            metricas = {
                'impressions': campaign.metricas.impressions,
                'clicks': campaign.metricas.clicks,
                'conversions': campaign.metricas.conversions,
                'spend': str(campaign.metricas.spend),
                'revenue': str(campaign.metricas.revenue),
                'click_through_rate': campaign.metricas.click_through_rate(),
                'conversion_rate': campaign.metricas.conversion_rate(),
                'cost_per_click': str(campaign.metricas.cost_per_click()),
                'cost_per_conversion': str(campaign.metricas.cost_per_conversion()),
                'return_on_ad_spend': str(campaign.metricas.return_on_ad_spend())
            }
        
        # Convert approval data
        approval = None
        if campaign.approval:
            approval = {
                'is_approved': campaign.approval.is_approved,
                'approved_by': campaign.approval.approved_by,
                'approved_at': campaign.approval.approved_at.isoformat() if campaign.approval.approved_at else None,
                'rejection_reason': campaign.approval.rejection_reason
            }
        
        return cls(
            id=campaign.id,
            nombre=campaign.nombre.value,
            descripcion=campaign.descripcion.value,
            partner_id=campaign.partner_id,
            tipo=campaign.tipo.value,
            status=campaign.status.value,
            presupuesto_amount=str(campaign.presupuesto.amount),
            presupuesto_currency=campaign.presupuesto.currency,
            fecha_inicio=campaign.fecha_rango.start_date.isoformat(),
            fecha_fin=campaign.fecha_rango.end_date.isoformat(),
            fecha_creacion=campaign.created_at.isoformat() if campaign.created_at else None,
            fecha_actualizacion=campaign.updated_at.isoformat() if campaign.updated_at else None,
            targeting=targeting,
            settings=settings,
            metricas=metricas,
            approval=approval
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert DTO to dictionary."""
        return asdict(self)


@dataclass
class CreateCampaignDTO:
    """DTO for creating a campaign."""
    
    nombre: str
    descripcion: str
    partner_id: str
    tipo: str
    presupuesto: Decimal
    fecha_inicio: datetime
    fecha_fin: datetime
    moneda: str = "USD"
    paises: Optional[List[str]] = None
    rango_edad: Optional[tuple[int, int]] = None
    intereses: Optional[List[str]] = None
    palabras_clave: Optional[List[str]] = None
    auto_pausar_presupuesto: bool = True
    limite_presupuesto_diario: Optional[Decimal] = None


@dataclass
class UpdateCampaignDTO:
    """DTO for updating a campaign."""
    
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    presupuesto: Optional[Decimal] = None
    fecha_inicio: Optional[datetime] = None
    fecha_fin: Optional[datetime] = None
    moneda: Optional[str] = None
    paises: Optional[List[str]] = None
    rango_edad: Optional[tuple[int, int]] = None
    intereses: Optional[List[str]] = None
    palabras_clave: Optional[List[str]] = None


@dataclass
class CampaignFilterDTO:
    """DTO for filtering campaigns."""
    
    partner_id: Optional[str] = None
    status: Optional[str] = None
    tipo: Optional[str] = None
    fecha_inicio_desde: Optional[str] = None
    fecha_inicio_hasta: Optional[str] = None
    fecha_fin_desde: Optional[str] = None
    fecha_fin_hasta: Optional[str] = None
    presupuesto_min: Optional[Decimal] = None
    presupuesto_max: Optional[Decimal] = None
    is_approved: Optional[bool] = None


@dataclass
class CampaignListResponseDTO:
    """DTO for campaign list response."""
    
    campaigns: List[CampaignDTO]
    total: int
    page: int
    page_size: int
    total_pages: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'campaigns': [campaign.to_dict() for campaign in self.campaigns],
            'total': self.total,
            'page': self.page,
            'page_size': self.page_size,
            'total_pages': self.total_pages
        }


@dataclass
class CampaignStatusChangeDTO:
    """DTO for campaign status changes."""
    
    campaign_id: str
    new_status: str
    reason: Optional[str] = None
    changed_by: Optional[str] = None


@dataclass
class CampaignApprovalDTO:
    """DTO for campaign approval operations."""
    
    campaign_id: str
    action: str  # 'approve' or 'reject'
    approved_by: Optional[str] = None
    rejected_by: Optional[str] = None
    approval_notes: Optional[str] = None
    rejection_reason: Optional[str] = None
    required_changes: Optional[List[str]] = None


@dataclass
class CampaignMetricsDTO:
    """DTO for campaign metrics."""
    
    campaign_id: str
    impressions: int = 0
    clicks: int = 0
    conversions: int = 0
    spend: Decimal = Decimal('0.00')
    revenue: Decimal = Decimal('0.00')
    metric_date: Optional[str] = None
    source: str = "system"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class CampaignTargetingDTO:
    """DTO for campaign targeting data."""
    
    campaign_id: str
    paises: Optional[List[str]] = None
    rango_edad: Optional[tuple[int, int]] = None
    intereses: Optional[List[str]] = None
    palabras_clave: Optional[List[str]] = None
    updated_by: Optional[str] = None


@dataclass
class CampaignSummaryDTO:
    """DTO for campaign summary information."""
    
    id: str
    nombre: str
    partner_id: str
    tipo: str
    status: str
    presupuesto_amount: str
    fecha_inicio: str
    fecha_fin: str
    impressions: int = 0
    clicks: int = 0
    conversions: int = 0
    spend: str = "0.00"
    
    @classmethod
    def from_campaign_dto(cls, campaign_dto: CampaignDTO) -> 'CampaignSummaryDTO':
        """Create summary from full CampaignDTO."""
        return cls(
            id=campaign_dto.id,
            nombre=campaign_dto.nombre,
            partner_id=campaign_dto.partner_id,
            tipo=campaign_dto.tipo,
            status=campaign_dto.status,
            presupuesto_amount=campaign_dto.presupuesto_amount,
            fecha_inicio=campaign_dto.fecha_inicio,
            fecha_fin=campaign_dto.fecha_fin,
            impressions=campaign_dto.metricas.get('impressions', 0) if campaign_dto.metricas else 0,
            clicks=campaign_dto.metricas.get('clicks', 0) if campaign_dto.metricas else 0,
            conversions=campaign_dto.metricas.get('conversions', 0) if campaign_dto.metricas else 0,
            spend=campaign_dto.metricas.get('spend', '0.00') if campaign_dto.metricas else '0.00'
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class CampaignPerformanceDTO:
    """DTO for campaign performance analysis."""
    
    campaign_id: str
    partner_id: str
    performance_period: str  # 'daily', 'weekly', 'monthly'
    metrics: Dict[str, Any]
    benchmarks: Optional[Dict[str, Any]] = None
    insights: Optional[List[str]] = None
    recommendations: Optional[List[str]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)