"""
Campaign factory implementation for HexaBuilders.
"""

import uuid
from typing import Optional

from partner_management.seedwork.dominio.fabricas import Fabrica
from partner_management.seedwork.dominio.repositorios import Repositorio
from ..dominio.entidades import Campaign
from ..dominio.objetos_valor import (
    CampaignName, CampaignDescription, CampaignBudget, CampaignDateRange,
    CampaignType, CampaignStatus, CampaignTargeting, CampaignSettings,
    CampaignMetrics, CampaignApproval
)


class FabricaCampaign(Fabrica):
    """Factory for creating Campaign entities."""
    
    def crear_campaign(
        self,
        nombre: CampaignName,
        descripcion: CampaignDescription,
        partner_id: str,
        tipo: CampaignType,
        presupuesto: CampaignBudget,
        fecha_rango: CampaignDateRange,
        campaign_id: Optional[str] = None,
        status: CampaignStatus = CampaignStatus.DRAFT,
        targeting: Optional[CampaignTargeting] = None,
        settings: Optional[CampaignSettings] = None,
        metricas: Optional[CampaignMetrics] = None,
        approval: Optional[CampaignApproval] = None
    ) -> Campaign:
        """Create a new Campaign entity."""
        
        # Generate ID if not provided
        if not campaign_id:
            campaign_id = str(uuid.uuid4())
        
        # Create default objects if not provided
        if targeting is None:
            targeting = CampaignTargeting()
        
        if settings is None:
            settings = CampaignSettings()
        
        if metricas is None:
            metricas = CampaignMetrics()
        
        if approval is None:
            approval = CampaignApproval()
        
        # Create and return campaign
        campaign = Campaign(
            nombre=nombre,
            descripcion=descripcion,
            partner_id=partner_id,
            tipo=tipo,
            presupuesto=presupuesto,
            fecha_rango=fecha_rango,
            campaign_id=campaign_id,
            status=status,
            targeting=targeting,
            settings=settings,
            metricas=metricas,
            approval=approval
        )
        
        return campaign
    
    def crear_campaign_desde_dto(self, dto: 'CreateCampaignDTO') -> Campaign:
        """Create Campaign from DTO."""
        
        from .dto import CreateCampaignDTO
        
        # Create value objects
        nombre = CampaignName(dto.nombre)
        descripcion = CampaignDescription(dto.descripcion)
        tipo = CampaignType(dto.tipo)
        presupuesto = CampaignBudget(dto.presupuesto, dto.moneda)
        fecha_rango = CampaignDateRange(dto.fecha_inicio, dto.fecha_fin)
        
        # Create targeting if data provided
        targeting = None
        if any([dto.paises, dto.rango_edad, dto.intereses, dto.palabras_clave]):
            targeting = CampaignTargeting(
                countries=dto.paises or [],
                age_range=dto.rango_edad,
                interests=dto.intereses or [],
                keywords=dto.palabras_clave or []
            )
        
        # Create settings
        settings = CampaignSettings(
            auto_pause_on_budget_exceeded=dto.auto_pausar_presupuesto,
            daily_budget_limit=dto.limite_presupuesto_diario
        )
        
        return self.crear_campaign(
            nombre=nombre,
            descripcion=descripcion,
            partner_id=dto.partner_id,
            tipo=tipo,
            presupuesto=presupuesto,
            fecha_rango=fecha_rango,
            targeting=targeting,
            settings=settings
        )


class RepositorioCampaigns(Repositorio):
    """Repository interface for Campaign entities."""
    
    def obtener_por_id(self, campaign_id: str) -> Optional[Campaign]:
        """Get campaign by ID."""
        raise NotImplementedError
    
    def obtener_por_partner(self, partner_id: str) -> list[Campaign]:
        """Get campaigns by partner ID."""
        raise NotImplementedError
    
    def obtener_por_status(self, status: CampaignStatus) -> list[Campaign]:
        """Get campaigns by status."""
        raise NotImplementedError
    
    def obtener_con_filtros(
        self,
        filtros: dict,
        page: int = 1,
        page_size: int = 10,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> tuple[list[Campaign], int]:
        """Get campaigns with filters and pagination."""
        raise NotImplementedError
    
    def agregar(self, campaign: Campaign) -> None:
        """Add campaign to repository."""
        raise NotImplementedError
    
    def actualizar(self, campaign: Campaign) -> None:
        """Update campaign in repository."""
        raise NotImplementedError
    
    def eliminar(self, campaign_id: str) -> None:
        """Delete campaign from repository."""
        raise NotImplementedError