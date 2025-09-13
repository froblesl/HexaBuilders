import logging
from typing import Dict, Any
from datetime import datetime

from partner_management.seedwork.dominio.eventos_integracion import (
    ContractSignedIntegrationEvent,
    ContractActivatedIntegrationEvent,
    CandidateMatchedIntegrationEvent,
    CandidateHiredIntegrationEvent,
    CampaignPerformanceReportIntegrationEvent,
    BudgetAlertIntegrationEvent
)

logger = logging.getLogger(__name__)


class IntegrationEventHandler:
    """Handles integration events from other services"""
    
    def __init__(self, partner_repository, uow, notification_service=None):
        self.partner_repository = partner_repository
        self.uow = uow
        self.notification_service = notification_service
    
    async def handle_contract_signed(self, event: ContractSignedIntegrationEvent):
        """Handle contract signed event from Onboarding service"""
        try:
            with self.uow:
                partner = await self.partner_repository.get_by_id(event.partner_id)
                if partner:
                    # Update partner status or metadata
                    partner.actualizar_estado_contrato("SIGNED")
                    partner.agregar_metadatos({
                        "contract_id": event.contract_id,
                        "contract_type": event.contract_type,
                        "contract_signed_at": event.effective_date.isoformat()
                    })
                    
                    await self.partner_repository.save(partner)
                    self.uow.commit()
                    
                    # Send notification
                    if self.notification_service:
                        await self.notification_service.send_notification(
                            partner_id=event.partner_id,
                            message=f"Contract {event.contract_id} has been signed successfully",
                            type="contract_signed"
                        )
                    
                    logger.info(f"Contract signed processed for partner {event.partner_id}")
                    
        except Exception as e:
            logger.error(f"Error handling contract signed event: {str(e)}")
            raise
    
    async def handle_contract_activated(self, event: ContractActivatedIntegrationEvent):
        """Handle contract activated event from Onboarding service"""
        try:
            with self.uow:
                partner = await self.partner_repository.get_by_id(event.partner_id)
                if partner:
                    # Update partner permissions and status
                    partner.actualizar_estado_contrato("ACTIVE")
                    partner.actualizar_permisos(event.permissions)
                    
                    # Enable campaign functionality if permitted
                    if event.permissions.get("can_create_campaigns", False):
                        partner.habilitar_funcionalidad("CAMPAIGNS")
                    
                    await self.partner_repository.save(partner)
                    self.uow.commit()
                    
                    logger.info(f"Contract activated processed for partner {event.partner_id}")
                    
        except Exception as e:
            logger.error(f"Error handling contract activated event: {str(e)}")
            raise
    
    async def handle_candidate_matched(self, event: CandidateMatchedIntegrationEvent):
        """Handle candidate matched event from Recruitment service"""
        try:
            with self.uow:
                partner = await self.partner_repository.get_by_id(event.partner_id)
                if partner:
                    # Update partner metrics
                    partner.actualizar_metricas_reclutamiento({
                        "candidates_matched": 1,
                        "last_match_score": event.match_score,
                        "last_match_date": datetime.utcnow().isoformat()
                    })
                    
                    await self.partner_repository.save(partner)
                    self.uow.commit()
                    
                    # Send notification about new candidate match
                    if self.notification_service:
                        await self.notification_service.send_notification(
                            partner_id=event.partner_id,
                            message=f"New candidate matched for job {event.job_id} with score {event.match_score}%",
                            type="candidate_matched",
                            data={
                                "candidate_id": event.candidate_id,
                                "job_id": event.job_id,
                                "match_score": event.match_score
                            }
                        )
                    
                    logger.info(f"Candidate matched processed for partner {event.partner_id}")
                    
        except Exception as e:
            logger.error(f"Error handling candidate matched event: {str(e)}")
            raise
    
    async def handle_candidate_hired(self, event: CandidateHiredIntegrationEvent):
        """Handle candidate hired event from Recruitment service"""
        try:
            with self.uow:
                partner = await self.partner_repository.get_by_id(event.partner_id)
                if partner:
                    # Update partner hiring metrics
                    partner.actualizar_metricas_reclutamiento({
                        "candidates_hired": 1,
                        "total_hiring_cost": event.salary * 12 if event.salary else 0,
                        "last_hire_date": event.start_date.isoformat()
                    })
                    
                    # Calculate commission if applicable
                    if event.salary:
                        commission = self._calculate_hiring_commission(partner, event.salary)
                        partner.agregar_comision({
                            "type": "hiring",
                            "amount": commission,
                            "candidate_id": event.candidate_id,
                            "position": event.position,
                            "base_salary": event.salary
                        })
                    
                    await self.partner_repository.save(partner)
                    self.uow.commit()
                    
                    logger.info(f"Candidate hired processed for partner {event.partner_id}")
                    
        except Exception as e:
            logger.error(f"Error handling candidate hired event: {str(e)}")
            raise
    
    async def handle_campaign_performance_report(self, event: CampaignPerformanceReportIntegrationEvent):
        """Handle campaign performance report from Campaign Management service"""
        try:
            with self.uow:
                partner = await self.partner_repository.get_by_id(event.partner_id)
                if partner:
                    # Update partner campaign metrics
                    performance = event.performance_data
                    partner.actualizar_metricas_campanas({
                        "campaign_id": event.campaign_id,
                        "period": event.period,
                        "impressions": performance.get("impressions", 0),
                        "clicks": performance.get("clicks", 0),
                        "conversions": performance.get("conversions", 0),
                        "cost": performance.get("cost", 0),
                        "ctr": performance.get("ctr", 0),
                        "conversion_rate": performance.get("conversion_rate", 0),
                        "last_updated": datetime.utcnow().isoformat()
                    })
                    
                    await self.partner_repository.save(partner)
                    self.uow.commit()
                    
                    logger.info(f"Campaign performance report processed for partner {event.partner_id}")
                    
        except Exception as e:
            logger.error(f"Error handling campaign performance report: {str(e)}")
            raise
    
    async def handle_budget_alert(self, event: BudgetAlertIntegrationEvent):
        """Handle budget alert from Campaign Management service"""
        try:
            with self.uow:
                partner = await self.partner_repository.get_by_id(event.partner_id)
                if partner:
                    # Add alert to partner's alert history
                    partner.agregar_alerta({
                        "type": "budget_alert",
                        "campaign_id": event.campaign_id,
                        "alert_type": event.alert_type,
                        "current_spend": event.current_spend,
                        "budget_limit": event.budget_limit,
                        "threshold": event.threshold_percentage,
                        "timestamp": datetime.utcnow().isoformat()
                    })
                    
                    await self.partner_repository.save(partner)
                    self.uow.commit()
                    
                    # Send urgent notification for budget alerts
                    if self.notification_service:
                        urgency = "high" if event.alert_type == "exhausted" else "medium"
                        await self.notification_service.send_notification(
                            partner_id=event.partner_id,
                            message=f"Budget alert for campaign {event.campaign_id}: {event.alert_type}",
                            type="budget_alert",
                            urgency=urgency,
                            data={
                                "campaign_id": event.campaign_id,
                                "alert_type": event.alert_type,
                                "current_spend": event.current_spend,
                                "budget_limit": event.budget_limit
                            }
                        )
                    
                    logger.info(f"Budget alert processed for partner {event.partner_id}")
                    
        except Exception as e:
            logger.error(f"Error handling budget alert: {str(e)}")
            raise
    
    def _calculate_hiring_commission(self, partner, salary: float) -> float:
        """Calculate commission for hiring"""
        # Base commission rate of 15% of first year salary
        base_rate = 0.15
        
        # Apply partner tier multiplier
        tier_multipliers = {
            "BRONZE": 1.0,
            "SILVER": 1.1,
            "GOLD": 1.2,
            "PLATINUM": 1.3
        }
        
        partner_tier = getattr(partner, 'tier', 'BRONZE')
        multiplier = tier_multipliers.get(partner_tier, 1.0)
        
        return salary * base_rate * multiplier


class IntegrationEventDispatcher:
    """Dispatches integration events to appropriate handlers"""
    
    def __init__(self, handler: IntegrationEventHandler):
        self.handler = handler
        self.event_handlers = {
            'ContractSigned': self.handler.handle_contract_signed,
            'ContractActivated': self.handler.handle_contract_activated,
            'CandidateMatched': self.handler.handle_candidate_matched,
            'CandidateHired': self.handler.handle_candidate_hired,
            'CampaignPerformanceReport': self.handler.handle_campaign_performance_report,
            'BudgetAlert': self.handler.handle_budget_alert,
        }
    
    async def dispatch(self, event_type: str, event_data: Dict[str, Any]):
        """Dispatch event to appropriate handler"""
        if event_type in self.event_handlers:
            handler_func = self.event_handlers[event_type]
            
            # Convert event_data to appropriate event object
            try:
                if event_type == 'ContractSigned':
                    event = ContractSignedIntegrationEvent(**event_data)
                elif event_type == 'ContractActivated':
                    event = ContractActivatedIntegrationEvent(**event_data)
                elif event_type == 'CandidateMatched':
                    event = CandidateMatchedIntegrationEvent(**event_data)
                elif event_type == 'CandidateHired':
                    event = CandidateHiredIntegrationEvent(**event_data)
                elif event_type == 'CampaignPerformanceReport':
                    event = CampaignPerformanceReportIntegrationEvent(**event_data)
                elif event_type == 'BudgetAlert':
                    event = BudgetAlertIntegrationEvent(**event_data)
                else:
                    logger.warning(f"Unknown event type: {event_type}")
                    return
                
                await handler_func(event)
                
            except Exception as e:
                logger.error(f"Error dispatching event {event_type}: {str(e)}")
                raise
        else:
            logger.warning(f"No handler found for event type: {event_type}")