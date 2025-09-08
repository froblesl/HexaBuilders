"""
Campaign domain entities implementation for HexaBuilders.
Implements Campaign aggregate root with full business logic.
"""

from typing import Optional, Dict, Any
from datetime import datetime
from decimal import Decimal

from partner_management.seedwork.dominio.entidades import AggregateRoot, DomainEntity
from partner_management.seedwork.dominio.excepciones import DomainException, BusinessRuleException
from .objetos_valor import (
    CampaignName, CampaignDescription, CampaignBudget, CampaignDateRange,
    CampaignStatus, CampaignType, CampaignMetrics, CampaignTargeting,
    CampaignSettings, CampaignApproval
)
from .eventos import (
    CampaignCreated, CampaignStatusChanged, CampaignActivated,
    CampaignPaused, CampaignCompleted, CampaignCancelled,
    CampaignUpdated, CampaignBudgetExceeded, CampaignMetricsUpdated,
    CampaignApproved, CampaignRejected, CampaignTargetingUpdated
)


class Campaign(AggregateRoot):
    """
    Campaign aggregate root.
    
    Represents a marketing campaign in the HexaBuilders platform.
    Campaigns are created and managed by partners to promote
    their products/services and generate commissions.
    """
    
    def __init__(
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
    ):
        super().__init__(campaign_id)
        
        # Validate required fields
        if not partner_id:
            raise DomainException("Campaign must have a partner")
        
        # Set attributes
        self._nombre = nombre
        self._descripcion = descripcion
        self._partner_id = partner_id
        self._tipo = tipo
        self._presupuesto = presupuesto
        self._fecha_rango = fecha_rango
        self._status = status
        self._targeting = targeting or CampaignTargeting()
        self._settings = settings or CampaignSettings()
        self._metricas = metricas or CampaignMetrics()
        self._approval = approval or CampaignApproval()
        
        # Domain event
        self.agregar_evento(CampaignCreated(
            aggregate_id=self.id,
            campaign_name=self._nombre.value,
            partner_id=self._partner_id,
            campaign_type=self._tipo.value,
            budget_amount=self._presupuesto.amount,
            start_date=self._fecha_rango.start_date.isoformat(),
            end_date=self._fecha_rango.end_date.isoformat()
        ))
    
    @property
    def nombre(self) -> CampaignName:
        return self._nombre
    
    @property
    def descripcion(self) -> CampaignDescription:
        return self._descripcion
    
    @property
    def partner_id(self) -> str:
        return self._partner_id
    
    @property
    def tipo(self) -> CampaignType:
        return self._tipo
    
    @property
    def presupuesto(self) -> CampaignBudget:
        return self._presupuesto
    
    @property
    def fecha_rango(self) -> CampaignDateRange:
        return self._fecha_rango
    
    @property
    def status(self) -> CampaignStatus:
        return self._status
    
    @property
    def targeting(self) -> CampaignTargeting:
        return self._targeting
    
    @property
    def settings(self) -> CampaignSettings:
        return self._settings
    
    @property
    def metricas(self) -> CampaignMetrics:
        return self._metricas
    
    @property
    def approval(self) -> CampaignApproval:
        return self._approval
    
    def actualizar_informacion(
        self,
        nombre: Optional[CampaignName] = None,
        descripcion: Optional[CampaignDescription] = None,
        presupuesto: Optional[CampaignBudget] = None,
        fecha_rango: Optional[CampaignDateRange] = None,
        updated_by: Optional[str] = None
    ) -> None:
        """Update campaign information."""
        
        # Can only update if campaign is in draft or paused status
        if self._status not in [CampaignStatus.DRAFT, CampaignStatus.PAUSED]:
            raise BusinessRuleException("Campaign can only be updated in draft or paused status")
        
        old_data = {
            'nombre': self._nombre.value,
            'descripcion': self._descripcion.value,
            'presupuesto': str(self._presupuesto.amount),
            'start_date': self._fecha_rango.start_date.isoformat(),
            'end_date': self._fecha_rango.end_date.isoformat()
        }
        
        updated_fields = []
        
        if nombre and nombre != self._nombre:
            self._nombre = nombre
            updated_fields.append('nombre')
        
        if descripcion and descripcion != self._descripcion:
            self._descripcion = descripcion
            updated_fields.append('descripcion')
        
        if presupuesto and presupuesto != self._presupuesto:
            self._presupuesto = presupuesto
            updated_fields.append('presupuesto')
        
        if fecha_rango and fecha_rango != self._fecha_rango:
            # Validate new date range doesn't conflict with active status
            if self._status == CampaignStatus.ACTIVE:
                if fecha_rango.start_date > datetime.now():
                    raise BusinessRuleException("Cannot change start date of active campaign to future")
            
            self._fecha_rango = fecha_rango
            updated_fields.append('fecha_rango')
        
        if updated_fields:
            self._mark_updated()
            
            new_data = {
                'nombre': self._nombre.value,
                'descripcion': self._descripcion.value,
                'presupuesto': str(self._presupuesto.amount),
                'start_date': self._fecha_rango.start_date.isoformat(),
                'end_date': self._fecha_rango.end_date.isoformat()
            }
            
            # Domain event
            self.agregar_evento(CampaignUpdated(
                aggregate_id=self.id,
                updated_fields={field: True for field in updated_fields},
                old_data=old_data,
                new_data=new_data,
                updated_by=updated_by
            ))
    
    def activar(self) -> None:
        """Activate campaign."""
        
        if self._status == CampaignStatus.ACTIVE:
            return  # Already active
        
        # Business rules for activation
        if self._status not in [CampaignStatus.DRAFT, CampaignStatus.PAUSED]:
            raise BusinessRuleException("Campaign can only be activated from draft or paused status")
        
        if not self._approval.is_approved:
            raise BusinessRuleException("Campaign must be approved before activation")
        
        if self._fecha_rango.end_date <= datetime.now():
            raise BusinessRuleException("Cannot activate expired campaign")
        
        if self._presupuesto.amount <= 0:
            raise BusinessRuleException("Campaign must have positive budget to activate")
        
        old_status = self._status
        self._status = CampaignStatus.ACTIVE
        self._mark_updated()
        
        # Domain events
        self.agregar_evento(CampaignStatusChanged(
            aggregate_id=self.id,
            old_status=old_status.value,
            new_status=self._status.value,
            reason="Campaign activated"
        ))
        
        self.agregar_evento(CampaignActivated(
            aggregate_id=self.id,
            campaign_name=self._nombre.value,
            partner_id=self._partner_id,
            start_date=self._fecha_rango.start_date.isoformat(),
            end_date=self._fecha_rango.end_date.isoformat(),
            budget_amount=str(self._presupuesto.amount)
        ))
    
    def pausar(self, reason: str, paused_by: Optional[str] = None) -> None:
        """Pause campaign."""
        
        if self._status == CampaignStatus.PAUSED:
            return  # Already paused
        
        if self._status not in [CampaignStatus.ACTIVE, CampaignStatus.DRAFT]:
            raise BusinessRuleException("Only active or draft campaigns can be paused")
        
        if not reason:
            raise DomainException("Pause reason is required")
        
        old_status = self._status
        self._status = CampaignStatus.PAUSED
        self._mark_updated()
        
        # Domain events
        self.agregar_evento(CampaignStatusChanged(
            aggregate_id=self.id,
            old_status=old_status.value,
            new_status=self._status.value,
            reason=reason,
            changed_by=paused_by
        ))
        
        self.agregar_evento(CampaignPaused(
            aggregate_id=self.id,
            campaign_name=self._nombre.value,
            partner_id=self._partner_id,
            pause_reason=reason,
            paused_by=paused_by
        ))
    
    def completar(self, completion_reason: str = "ended") -> None:
        """Complete campaign."""
        
        if self._status == CampaignStatus.COMPLETED:
            return  # Already completed
        
        if self._status not in [CampaignStatus.ACTIVE, CampaignStatus.PAUSED]:
            raise BusinessRuleException("Only active or paused campaigns can be completed")
        
        old_status = self._status
        self._status = CampaignStatus.COMPLETED
        self._mark_updated()
        
        # Capture final metrics
        final_metrics = {
            'impressions': self._metricas.impressions,
            'clicks': self._metricas.clicks,
            'conversions': self._metricas.conversions,
            'spend': str(self._metricas.spend),
            'revenue': str(self._metricas.revenue),
            'ctr': self._metricas.click_through_rate(),
            'conversion_rate': self._metricas.conversion_rate(),
            'roas': str(self._metricas.return_on_ad_spend())
        }
        
        # Domain events
        self.agregar_evento(CampaignStatusChanged(
            aggregate_id=self.id,
            old_status=old_status.value,
            new_status=self._status.value,
            reason=completion_reason
        ))
        
        self.agregar_evento(CampaignCompleted(
            aggregate_id=self.id,
            campaign_name=self._nombre.value,
            partner_id=self._partner_id,
            final_metrics=final_metrics,
            completion_reason=completion_reason
        ))
    
    def cancelar(self, cancellation_reason: str, cancelled_by: Optional[str] = None, 
                 refund_amount: Optional[Decimal] = None) -> None:
        """Cancel campaign."""
        
        if self._status == CampaignStatus.CANCELLED:
            return  # Already cancelled
        
        if self._status == CampaignStatus.COMPLETED:
            raise BusinessRuleException("Completed campaigns cannot be cancelled")
        
        if not cancellation_reason:
            raise DomainException("Cancellation reason is required")
        
        old_status = self._status
        self._status = CampaignStatus.CANCELLED
        self._mark_updated()
        
        # Domain events
        self.agregar_evento(CampaignStatusChanged(
            aggregate_id=self.id,
            old_status=old_status.value,
            new_status=self._status.value,
            reason=cancellation_reason,
            changed_by=cancelled_by
        ))
        
        self.agregar_evento(CampaignCancelled(
            aggregate_id=self.id,
            campaign_name=self._nombre.value,
            partner_id=self._partner_id,
            cancellation_reason=cancellation_reason,
            cancelled_by=cancelled_by,
            refund_amount=str(refund_amount) if refund_amount else None
        ))
    
    def actualizar_targeting(self, nuevo_targeting: CampaignTargeting, 
                           updated_by: Optional[str] = None) -> None:
        """Update campaign targeting."""
        
        if self._status not in [CampaignStatus.DRAFT, CampaignStatus.PAUSED]:
            raise BusinessRuleException("Campaign targeting can only be updated in draft or paused status")
        
        old_targeting = {
            'countries': self._targeting.countries,
            'age_range': self._targeting.age_range,
            'interests': self._targeting.interests,
            'keywords': self._targeting.keywords
        }
        
        self._targeting = nuevo_targeting
        self._mark_updated()
        
        new_targeting = {
            'countries': nuevo_targeting.countries,
            'age_range': nuevo_targeting.age_range,
            'interests': nuevo_targeting.interests,
            'keywords': nuevo_targeting.keywords
        }
        
        # Domain event
        self.agregar_evento(CampaignTargetingUpdated(
            aggregate_id=self.id,
            old_targeting=old_targeting,
            new_targeting=new_targeting,
            updated_by=updated_by
        ))
    
    def actualizar_metricas(self, nuevas_metricas: CampaignMetrics, 
                           source: str = "system") -> None:
        """Update campaign performance metrics."""
        
        old_metrics = {
            'impressions': self._metricas.impressions,
            'clicks': self._metricas.clicks,
            'conversions': self._metricas.conversions,
            'spend': str(self._metricas.spend),
            'revenue': str(self._metricas.revenue)
        }
        
        self._metricas = nuevas_metricas
        self._mark_updated()
        
        new_metrics = {
            'impressions': nuevas_metricas.impressions,
            'clicks': nuevas_metricas.clicks,
            'conversions': nuevas_metricas.conversions,
            'spend': str(nuevas_metricas.spend),
            'revenue': str(nuevas_metricas.revenue)
        }
        
        # Check for budget exceeded
        if (self._settings.auto_pause_on_budget_exceeded and 
            nuevas_metricas.spend >= self._presupuesto.amount and 
            self._status == CampaignStatus.ACTIVE):
            
            self.agregar_evento(CampaignBudgetExceeded(
                aggregate_id=self.id,
                campaign_name=self._nombre.value,
                partner_id=self._partner_id,
                budget_amount=str(self._presupuesto.amount),
                spent_amount=str(nuevas_metricas.spend),
                auto_paused=True
            ))
            
            # Auto-pause campaign
            self.pausar("Budget exceeded", "system")
        
        # Domain event
        self.agregar_evento(CampaignMetricsUpdated(
            aggregate_id=self.id,
            old_metrics=old_metrics,
            new_metrics=new_metrics,
            source=source
        ))
    
    def aprobar(self, approved_by: str, approval_notes: Optional[str] = None) -> None:
        """Approve campaign."""
        
        if self._approval.is_approved:
            return  # Already approved
        
        if self._status != CampaignStatus.DRAFT:
            raise BusinessRuleException("Only draft campaigns can be approved")
        
        if not approved_by:
            raise DomainException("Approval must specify who approved")
        
        self._approval = CampaignApproval(
            is_approved=True,
            approved_by=approved_by,
            approved_at=datetime.now(),
            rejection_reason=None
        )
        
        self._mark_updated()
        
        # Domain event
        self.agregar_evento(CampaignApproved(
            aggregate_id=self.id,
            campaign_name=self._nombre.value,
            partner_id=self._partner_id,
            approved_by=approved_by,
            approval_notes=approval_notes
        ))
    
    def rechazar(self, rejected_by: str, rejection_reason: str, 
                required_changes: Optional[list[str]] = None) -> None:
        """Reject campaign."""
        
        if self._status != CampaignStatus.DRAFT:
            raise BusinessRuleException("Only draft campaigns can be rejected")
        
        if not rejected_by or not rejection_reason:
            raise DomainException("Rejection must specify who rejected and why")
        
        self._approval = CampaignApproval(
            is_approved=False,
            approved_by=None,
            approved_at=None,
            rejection_reason=rejection_reason
        )
        
        self._mark_updated()
        
        # Domain event
        self.agregar_evento(CampaignRejected(
            aggregate_id=self.id,
            campaign_name=self._nombre.value,
            partner_id=self._partner_id,
            rejected_by=rejected_by,
            rejection_reason=rejection_reason,
            required_changes=required_changes
        ))
    
    def puede_ser_editada(self) -> bool:
        """Check if campaign can be edited."""
        return self._status in [CampaignStatus.DRAFT, CampaignStatus.PAUSED]
    
    def esta_activa(self) -> bool:
        """Check if campaign is currently active."""
        return (self._status == CampaignStatus.ACTIVE and 
                self._fecha_rango.is_active_on(datetime.now()))
    
    def esta_vencida(self) -> bool:
        """Check if campaign has expired."""
        return self._fecha_rango.is_expired()
    
    def porcentaje_presupuesto_usado(self) -> float:
        """Get percentage of budget used."""
        if self._presupuesto.amount == 0:
            return 0.0
        return float(self._metricas.spend / self._presupuesto.amount)
    
    def validate(self) -> None:
        """Validate campaign state."""
        
        if not self._nombre or not self._descripcion:
            raise DomainException("Campaign must have name and description")
        
        if not self._partner_id:
            raise DomainException("Campaign must be assigned to a partner")
        
        if not self._tipo or not self._presupuesto:
            raise DomainException("Campaign must have type and budget")
        
        if not self._fecha_rango:
            raise DomainException("Campaign must have date range")
        
        # Validate active campaign requirements
        if self._status == CampaignStatus.ACTIVE:
            if not self._approval.is_approved:
                raise DomainException("Active campaign must be approved")
            
            if self._fecha_rango.is_expired():
                raise DomainException("Active campaign cannot be expired")
    
    def __repr__(self) -> str:
        return (f"Campaign(id={self.id}, name={self._nombre.value}, "
                f"partner_id={self._partner_id}, status={self._status.value})")