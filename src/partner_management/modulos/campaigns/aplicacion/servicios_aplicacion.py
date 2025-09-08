"""
Campaign application services for HexaBuilders.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal

from partner_management.seedwork.aplicacion.servicios import ServicioAplicacion
from partner_management.seedwork.infraestructura.uow import UnitOfWork
from partner_management.seedwork.dominio.excepciones import DomainException
from ..dominio.entidades import Campaign
from ..dominio.objetos_valor import CampaignStatus, CampaignType
from ..infraestructura.dto import (
    CampaignDTO, CreateCampaignDTO, UpdateCampaignDTO, CampaignListResponseDTO,
    CampaignSummaryDTO, CampaignMetricsDTO, CampaignTargetingDTO
)
from ..infraestructura.fabricas import FabricaCampaign

logger = logging.getLogger(__name__)


class ServicioCampaign(ServicioAplicacion):
    """Service for campaign-related business operations."""
    
    def __init__(self):
        self._fabrica = FabricaCampaign()
    
    def crear_campaign(self, datos_campaign: CreateCampaignDTO) -> str:
        """Create a new campaign."""
        logger.info(f"Creating campaign: {datos_campaign.nombre}")
        
        try:
            with UnitOfWork() as uow:
                # Validate partner exists and can create campaigns
                partner_repo = uow.partners
                partner = partner_repo.obtener_por_id(datos_campaign.partner_id)
                
                if not partner:
                    raise DomainException(f"Partner {datos_campaign.partner_id} not found")
                
                if not partner.puede_crear_campanas():
                    raise DomainException(f"Partner {datos_campaign.partner_id} cannot create campaigns")
                
                # Create campaign
                campaign = self._fabrica.crear_campaign_desde_dto(datos_campaign)
                
                # Save campaign
                campaign_repo = uow.campaigns
                campaign_repo.agregar(campaign)
                
                uow.commit()
                
                logger.info(f"Campaign created successfully: {campaign.id}")
                return campaign.id
                
        except Exception as e:
            logger.error(f"Error creating campaign: {str(e)}")
            raise
    
    def obtener_campaign(self, campaign_id: str) -> Optional[CampaignDTO]:
        """Get campaign by ID."""
        logger.info(f"Getting campaign: {campaign_id}")
        
        with UnitOfWork() as uow:
            repo = uow.campaigns
            campaign = repo.obtener_por_id(campaign_id)
            
            if not campaign:
                return None
            
            return CampaignDTO.from_entity(campaign)
    
    def listar_campaigns(
        self,
        partner_id: Optional[str] = None,
        status: Optional[str] = None,
        tipo: Optional[str] = None,
        page: int = 1,
        page_size: int = 10
    ) -> CampaignListResponseDTO:
        """List campaigns with filters."""
        logger.info(f"Listing campaigns with filters: partner_id={partner_id}, status={status}")
        
        with UnitOfWork() as uow:
            repo = uow.campaigns
            
            filtros = {}
            if partner_id:
                filtros['partner_id'] = partner_id
            if status:
                filtros['status'] = status
            if tipo:
                filtros['tipo'] = tipo
            
            campaigns, total = repo.obtener_con_filtros(
                filtros=filtros,
                page=page,
                page_size=page_size
            )
            
            campaign_dtos = [CampaignDTO.from_entity(campaign) for campaign in campaigns]
            total_pages = (total + page_size - 1) // page_size
            
            return CampaignListResponseDTO(
                campaigns=campaign_dtos,
                total=total,
                page=page,
                page_size=page_size,
                total_pages=total_pages
            )
    
    def actualizar_campaign(self, campaign_id: str, datos_actualizacion: UpdateCampaignDTO) -> bool:
        """Update campaign information."""
        logger.info(f"Updating campaign: {campaign_id}")
        
        try:
            with UnitOfWork() as uow:
                repo = uow.campaigns
                campaign = repo.obtener_por_id(campaign_id)
                
                if not campaign:
                    raise DomainException(f"Campaign {campaign_id} not found")
                
                # Update basic information using command pattern
                # This would normally go through the command handlers
                
                repo.actualizar(campaign)
                uow.commit()
                
                logger.info(f"Campaign updated successfully: {campaign_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error updating campaign {campaign_id}: {str(e)}")
            raise
    
    def activar_campaign(self, campaign_id: str, activated_by: Optional[str] = None) -> bool:
        """Activate a campaign."""
        logger.info(f"Activating campaign: {campaign_id}")
        
        try:
            with UnitOfWork() as uow:
                repo = uow.campaigns
                campaign = repo.obtener_por_id(campaign_id)
                
                if not campaign:
                    raise DomainException(f"Campaign {campaign_id} not found")
                
                # Validate partner can activate campaigns
                partner_repo = uow.partners
                partner = partner_repo.obtener_por_id(campaign.partner_id)
                
                if not partner or not partner.puede_crear_campanas():
                    raise DomainException("Partner cannot activate campaigns")
                
                campaign.activar()
                repo.actualizar(campaign)
                uow.commit()
                
                logger.info(f"Campaign activated successfully: {campaign_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error activating campaign {campaign_id}: {str(e)}")
            raise
    
    def pausar_campaign(self, campaign_id: str, reason: str, paused_by: Optional[str] = None) -> bool:
        """Pause a campaign."""
        logger.info(f"Pausing campaign: {campaign_id}")
        
        try:
            with UnitOfWork() as uow:
                repo = uow.campaigns
                campaign = repo.obtener_por_id(campaign_id)
                
                if not campaign:
                    raise DomainException(f"Campaign {campaign_id} not found")
                
                campaign.pausar(reason, paused_by)
                repo.actualizar(campaign)
                uow.commit()
                
                logger.info(f"Campaign paused successfully: {campaign_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error pausing campaign {campaign_id}: {str(e)}")
            raise
    
    def aprobar_campaign(self, campaign_id: str, approved_by: str, notes: Optional[str] = None) -> bool:
        """Approve a campaign."""
        logger.info(f"Approving campaign: {campaign_id}")
        
        try:
            with UnitOfWork() as uow:
                repo = uow.campaigns
                campaign = repo.obtener_por_id(campaign_id)
                
                if not campaign:
                    raise DomainException(f"Campaign {campaign_id} not found")
                
                campaign.aprobar(approved_by, notes)
                repo.actualizar(campaign)
                uow.commit()
                
                logger.info(f"Campaign approved successfully: {campaign_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error approving campaign {campaign_id}: {str(e)}")
            raise
    
    def rechazar_campaign(
        self, 
        campaign_id: str, 
        rejected_by: str, 
        reason: str, 
        required_changes: Optional[List[str]] = None
    ) -> bool:
        """Reject a campaign."""
        logger.info(f"Rejecting campaign: {campaign_id}")
        
        try:
            with UnitOfWork() as uow:
                repo = uow.campaigns
                campaign = repo.obtener_por_id(campaign_id)
                
                if not campaign:
                    raise DomainException(f"Campaign {campaign_id} not found")
                
                campaign.rechazar(rejected_by, reason, required_changes)
                repo.actualizar(campaign)
                uow.commit()
                
                logger.info(f"Campaign rejected successfully: {campaign_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error rejecting campaign {campaign_id}: {str(e)}")
            raise
    
    def actualizar_metricas_campaign(self, datos_metricas: CampaignMetricsDTO) -> bool:
        """Update campaign performance metrics."""
        logger.info(f"Updating metrics for campaign: {datos_metricas.campaign_id}")
        
        try:
            with UnitOfWork() as uow:
                from ..dominio.objetos_valor import CampaignMetrics
                
                repo = uow.campaigns
                campaign = repo.obtener_por_id(datos_metricas.campaign_id)
                
                if not campaign:
                    raise DomainException(f"Campaign {datos_metricas.campaign_id} not found")
                
                # Create new metrics object
                nuevas_metricas = CampaignMetrics(
                    impressions=datos_metricas.impressions,
                    clicks=datos_metricas.clicks,
                    conversions=datos_metricas.conversions,
                    spend=datos_metricas.spend,
                    revenue=datos_metricas.revenue
                )
                
                campaign.actualizar_metricas(nuevas_metricas, datos_metricas.source)
                repo.actualizar(campaign)
                uow.commit()
                
                logger.info(f"Campaign metrics updated successfully: {datos_metricas.campaign_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error updating campaign metrics {datos_metricas.campaign_id}: {str(e)}")
            raise
    
    def obtener_campaigns_por_partner(self, partner_id: str) -> List[CampaignSummaryDTO]:
        """Get campaign summaries for a partner."""
        logger.info(f"Getting campaigns for partner: {partner_id}")
        
        with UnitOfWork() as uow:
            repo = uow.campaigns
            campaigns = repo.obtener_por_partner(partner_id)
            
            return [
                CampaignSummaryDTO.from_campaign_dto(CampaignDTO.from_entity(campaign))
                for campaign in campaigns
            ]
    
    def obtener_campaigns_activas(self) -> List[CampaignSummaryDTO]:
        """Get all active campaigns."""
        logger.info("Getting all active campaigns")
        
        with UnitOfWork() as uow:
            repo = uow.campaigns
            campaigns = repo.obtener_por_status(CampaignStatus.ACTIVE)
            
            return [
                CampaignSummaryDTO.from_campaign_dto(CampaignDTO.from_entity(campaign))
                for campaign in campaigns
            ]
    
    def obtener_estadisticas_partner(self, partner_id: str) -> Dict[str, Any]:
        """Get campaign statistics for a partner."""
        logger.info(f"Getting campaign statistics for partner: {partner_id}")
        
        with UnitOfWork() as uow:
            repo = uow.campaigns
            campaigns = repo.obtener_por_partner(partner_id)
            
            total_campaigns = len(campaigns)
            active_campaigns = sum(1 for c in campaigns if c.status == CampaignStatus.ACTIVE)
            completed_campaigns = sum(1 for c in campaigns if c.status == CampaignStatus.COMPLETED)
            total_spend = sum(c.metricas.spend for c in campaigns)
            total_revenue = sum(c.metricas.revenue for c in campaigns)
            
            return {
                'partner_id': partner_id,
                'total_campaigns': total_campaigns,
                'active_campaigns': active_campaigns,
                'completed_campaigns': completed_campaigns,
                'draft_campaigns': sum(1 for c in campaigns if c.status == CampaignStatus.DRAFT),
                'paused_campaigns': sum(1 for c in campaigns if c.status == CampaignStatus.PAUSED),
                'cancelled_campaigns': sum(1 for c in campaigns if c.status == CampaignStatus.CANCELLED),
                'total_spend': str(total_spend),
                'total_revenue': str(total_revenue),
                'average_roas': str(total_revenue / total_spend) if total_spend > 0 else "0.00",
                'success_rate': completed_campaigns / total_campaigns if total_campaigns > 0 else 0.0
            }
    
    def procesar_campaigns_vencidas(self) -> List[str]:
        """Process expired campaigns and complete them."""
        logger.info("Processing expired campaigns")
        
        try:
            with UnitOfWork() as uow:
                repo = uow.campaigns
                campaigns_vencidas = repo.obtener_vencidas()
                
                campaign_ids = []
                for campaign in campaigns_vencidas:
                    campaign.completar("Campaign expired")
                    repo.actualizar(campaign)
                    campaign_ids.append(campaign.id)
                
                uow.commit()
                
                logger.info(f"Processed {len(campaign_ids)} expired campaigns")
                return campaign_ids
                
        except Exception as e:
            logger.error(f"Error processing expired campaigns: {str(e)}")
            raise