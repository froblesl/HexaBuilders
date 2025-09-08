"""
Mock repository implementation for Campaigns in HexaBuilders.
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from decimal import Decimal

from partner_management.seedwork.infraestructura.repositorios import RepositorioMock
from ..dominio.entidades import Campaign
from ..dominio.objetos_valor import (
    CampaignName, CampaignDescription, CampaignBudget, CampaignDateRange,
    CampaignType, CampaignStatus, CampaignTargeting, CampaignSettings,
    CampaignMetrics, CampaignApproval
)
from .fabricas import RepositorioCampaigns


class RepositorioCampaignsMock(RepositorioCampaigns, RepositorioMock):
    """Mock implementation of CampaignRepository."""
    
    def __init__(self):
        super().__init__()
        self._campaigns: Dict[str, Campaign] = {}
        self._initialize_mock_data()
    
    def _initialize_mock_data(self):
        """Initialize with some mock campaign data."""
        
        # Mock Campaign 1: Active Performance Campaign
        campaign1_id = str(uuid.uuid4())
        campaign1 = Campaign(
            nombre=CampaignName("Summer Sales Boost"),
            descripcion=CampaignDescription("Drive summer sales with targeted performance marketing campaign focusing on key products and demographics."),
            partner_id="partner-001",
            tipo=CampaignType.PERFORMANCE,
            presupuesto=CampaignBudget(Decimal("5000.00"), "USD"),
            fecha_rango=CampaignDateRange(
                start_date=datetime(2024, 6, 1, 0, 0, 0),
                end_date=datetime(2024, 8, 31, 23, 59, 59)
            ),
            campaign_id=campaign1_id,
            status=CampaignStatus.ACTIVE,
            targeting=CampaignTargeting(
                countries=["US", "CA", "MX"],
                age_range=(25, 45),
                interests=["shopping", "fashion", "technology"],
                keywords=["summer sale", "discount", "deals"]
            ),
            settings=CampaignSettings(
                auto_pause_on_budget_exceeded=True,
                daily_budget_limit=Decimal("200.00")
            ),
            metricas=CampaignMetrics(
                impressions=150000,
                clicks=7500,
                conversions=375,
                spend=Decimal("2500.00"),
                revenue=Decimal("15000.00")
            ),
            approval=CampaignApproval(
                is_approved=True,
                approved_by="admin-001",
                approved_at=datetime(2024, 5, 25, 10, 0, 0)
            )
        )
        campaign1._created_at = datetime(2024, 5, 20, 10, 0, 0)
        campaign1._updated_at = datetime(2024, 6, 15, 14, 30, 0)
        self._campaigns[campaign1_id] = campaign1
        
        # Mock Campaign 2: Draft Brand Awareness Campaign
        campaign2_id = str(uuid.uuid4())
        campaign2 = Campaign(
            nombre=CampaignName("Brand Awareness Q3"),
            descripcion=CampaignDescription("Increase brand awareness and reach new audiences through strategic brand marketing initiatives."),
            partner_id="partner-002",
            tipo=CampaignType.BRAND_AWARENESS,
            presupuesto=CampaignBudget(Decimal("10000.00"), "USD"),
            fecha_rango=CampaignDateRange(
                start_date=datetime(2024, 7, 1, 0, 0, 0),
                end_date=datetime(2024, 9, 30, 23, 59, 59)
            ),
            campaign_id=campaign2_id,
            status=CampaignStatus.DRAFT,
            targeting=CampaignTargeting(
                countries=["US", "UK", "DE", "FR"],
                age_range=(18, 65),
                interests=["business", "entrepreneurship", "innovation"]
            ),
            approval=CampaignApproval(
                is_approved=False
            )
        )
        campaign2._created_at = datetime(2024, 6, 10, 16, 0, 0)
        campaign2._updated_at = datetime(2024, 6, 12, 9, 15, 0)
        self._campaigns[campaign2_id] = campaign2
        
        # Mock Campaign 3: Completed Lead Generation Campaign
        campaign3_id = str(uuid.uuid4())
        campaign3 = Campaign(
            nombre=CampaignName("Q2 Lead Generation"),
            descripcion=CampaignDescription("Generate high-quality leads through targeted content marketing and lead magnets."),
            partner_id="partner-001",
            tipo=CampaignType.LEAD_GENERATION,
            presupuesto=CampaignBudget(Decimal("3000.00"), "USD"),
            fecha_rango=CampaignDateRange(
                start_date=datetime(2024, 4, 1, 0, 0, 0),
                end_date=datetime(2024, 6, 30, 23, 59, 59)
            ),
            campaign_id=campaign3_id,
            status=CampaignStatus.COMPLETED,
            targeting=CampaignTargeting(
                countries=["US"],
                age_range=(30, 55),
                interests=["b2b", "software", "productivity"],
                keywords=["lead generation", "b2b tools", "business software"]
            ),
            metricas=CampaignMetrics(
                impressions=80000,
                clicks=3200,
                conversions=160,
                spend=Decimal("2800.00"),
                revenue=Decimal("8000.00")
            ),
            approval=CampaignApproval(
                is_approved=True,
                approved_by="admin-001",
                approved_at=datetime(2024, 3, 28, 11, 0, 0)
            )
        )
        campaign3._created_at = datetime(2024, 3, 15, 14, 0, 0)
        campaign3._updated_at = datetime(2024, 6, 30, 23, 59, 59)
        self._campaigns[campaign3_id] = campaign3
    
    def obtener_por_id(self, campaign_id: str) -> Optional[Campaign]:
        """Get campaign by ID."""
        return self._campaigns.get(campaign_id)
    
    def obtener_por_partner(self, partner_id: str) -> List[Campaign]:
        """Get campaigns by partner ID."""
        return [
            campaign for campaign in self._campaigns.values()
            if campaign.partner_id == partner_id
        ]
    
    def obtener_por_status(self, status: CampaignStatus) -> List[Campaign]:
        """Get campaigns by status."""
        return [
            campaign for campaign in self._campaigns.values()
            if campaign.status == status
        ]
    
    def obtener_con_filtros(
        self,
        filtros: Dict,
        page: int = 1,
        page_size: int = 10,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> Tuple[List[Campaign], int]:
        """Get campaigns with filters and pagination."""
        
        campaigns = list(self._campaigns.values())
        
        # Apply filters
        if filtros.get('partner_id'):
            campaigns = [c for c in campaigns if c.partner_id == filtros['partner_id']]
        
        if filtros.get('status'):
            campaigns = [c for c in campaigns if c.status.value == filtros['status']]
        
        if filtros.get('tipo'):
            campaigns = [c for c in campaigns if c.tipo.value == filtros['tipo']]
        
        if filtros.get('fecha_inicio_desde'):
            fecha_desde = datetime.fromisoformat(filtros['fecha_inicio_desde'])
            campaigns = [c for c in campaigns if c.fecha_rango.start_date >= fecha_desde]
        
        if filtros.get('fecha_inicio_hasta'):
            fecha_hasta = datetime.fromisoformat(filtros['fecha_inicio_hasta'])
            campaigns = [c for c in campaigns if c.fecha_rango.start_date <= fecha_hasta]
        
        if filtros.get('presupuesto_min'):
            campaigns = [c for c in campaigns if c.presupuesto.amount >= filtros['presupuesto_min']]
        
        if filtros.get('presupuesto_max'):
            campaigns = [c for c in campaigns if c.presupuesto.amount <= filtros['presupuesto_max']]
        
        if filtros.get('is_approved') is not None:
            campaigns = [c for c in campaigns if c.approval.is_approved == filtros['is_approved']]
        
        total = len(campaigns)
        
        # Apply sorting
        reverse_order = sort_order.lower() == 'desc'
        
        if sort_by == 'created_at':
            campaigns.sort(key=lambda c: c.created_at, reverse=reverse_order)
        elif sort_by == 'updated_at':
            campaigns.sort(key=lambda c: c.updated_at, reverse=reverse_order)
        elif sort_by == 'nombre':
            campaigns.sort(key=lambda c: c.nombre.value, reverse=reverse_order)
        elif sort_by == 'start_date':
            campaigns.sort(key=lambda c: c.fecha_rango.start_date, reverse=reverse_order)
        elif sort_by == 'end_date':
            campaigns.sort(key=lambda c: c.fecha_rango.end_date, reverse=reverse_order)
        elif sort_by == 'status':
            campaigns.sort(key=lambda c: c.status.value, reverse=reverse_order)
        else:
            campaigns.sort(key=lambda c: c.created_at, reverse=reverse_order)
        
        # Apply pagination
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_campaigns = campaigns[start_idx:end_idx]
        
        return paginated_campaigns, total
    
    def obtener_todos(self) -> List[Campaign]:
        """Get all campaigns."""
        return list(self._campaigns.values())
    
    def agregar(self, campaign: Campaign) -> None:
        """Add campaign to repository."""
        self._campaigns[campaign.id] = campaign
    
    def actualizar(self, campaign: Campaign) -> None:
        """Update campaign in repository."""
        if campaign.id in self._campaigns:
            self._campaigns[campaign.id] = campaign
        else:
            raise ValueError(f"Campaign with ID {campaign.id} not found")
    
    def eliminar(self, campaign_id: str) -> None:
        """Delete campaign from repository."""
        if campaign_id in self._campaigns:
            del self._campaigns[campaign_id]
        else:
            raise ValueError(f"Campaign with ID {campaign_id} not found")
    
    def obtener_activas_por_partner(self, partner_id: str) -> List[Campaign]:
        """Get active campaigns for a partner."""
        return [
            campaign for campaign in self._campaigns.values()
            if campaign.partner_id == partner_id and campaign.status == CampaignStatus.ACTIVE
        ]
    
    def obtener_por_presupuesto_rango(self, min_budget: Decimal, max_budget: Decimal) -> List[Campaign]:
        """Get campaigns within budget range."""
        return [
            campaign for campaign in self._campaigns.values()
            if min_budget <= campaign.presupuesto.amount <= max_budget
        ]
    
    def obtener_vencidas(self) -> List[Campaign]:
        """Get expired campaigns."""
        now = datetime.now()
        return [
            campaign for campaign in self._campaigns.values()
            if campaign.fecha_rango.end_date < now and campaign.status in [CampaignStatus.ACTIVE, CampaignStatus.PAUSED]
        ]
    
    def contar_por_partner(self, partner_id: str) -> int:
        """Count campaigns for a partner."""
        return len([
            campaign for campaign in self._campaigns.values()
            if campaign.partner_id == partner_id
        ])
    
    def contar_por_status(self, status: CampaignStatus) -> int:
        """Count campaigns by status."""
        return len([
            campaign for campaign in self._campaigns.values()
            if campaign.status == status
        ])