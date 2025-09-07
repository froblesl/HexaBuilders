"""
Event handlers for Commission module in HexaBuilders.
Implements Tutorial 5 (Events) patterns with PyDispatcher integration.
"""

import logging
from pydispatch import dispatcher

from ...seedwork.dominio.eventos import DomainEvent
from ...partners.dominio.eventos import PartnerCreated, PartnerActivated, PartnerDeactivated
from ...campaigns.dominio.eventos import CampaignCompleted, CampaignActivated
from .comandos.crear_commission import CrearCommission, handle_crear_commission
from ..dominio.eventos import (
    CommissionCreated, CommissionApproved, CommissionPaid,
    CommissionCancelled, CommissionDisputed
)

logger = logging.getLogger(__name__)


class CommissionEventHandler:
    """
    Event handler for Commission-related domain events.
    Implements cross-module integration through domain events.
    """
    
    def __init__(self):
        self._setup_event_subscriptions()
    
    def _setup_event_subscriptions(self):
        """Setup domain event subscriptions using PyDispatcher."""
        
        # Partner events
        dispatcher.connect(
            self.handle_partner_activated,
            signal='DomainEvent',
            sender='PartnerActivated'
        )
        
        dispatcher.connect(
            self.handle_partner_deactivated,
            signal='DomainEvent',
            sender='PartnerDeactivated'
        )
        
        # Campaign events
        dispatcher.connect(
            self.handle_campaign_completed,
            signal='DomainEvent',
            sender='CampaignCompleted'
        )
        
        dispatcher.connect(
            self.handle_campaign_activated,
            signal='DomainEvent',
            sender='CampaignActivated'
        )
        
        # Commission events (internal)
        dispatcher.connect(
            self.handle_commission_created,
            signal='DomainEvent',
            sender='CommissionCreated'
        )
        
        dispatcher.connect(
            self.handle_commission_approved,
            signal='DomainEvent',
            sender='CommissionApproved'
        )
        
        dispatcher.connect(
            self.handle_commission_paid,
            signal='DomainEvent',
            sender='CommissionPaid'
        )
    
    def handle_partner_activated(self, sender, evento: PartnerActivated):
        """
        Handle partner activation event.
        Initialize commission tracking for new active partner.
        """
        try:
            logger.info(f"Handling PartnerActivated event for partner: {evento.aggregate_id}")
            
            # Initialize partner commission metrics
            # This could trigger creation of partner commission profile
            # or setup of commission tracking structures
            
            logger.info(f"Commission tracking initialized for activated partner: {evento.aggregate_id}")
            
        except Exception as e:
            logger.error(f"Error handling PartnerActivated event: {str(e)}")
            raise
    
    def handle_partner_deactivated(self, sender, evento: PartnerDeactivated):
        """
        Handle partner deactivation event.
        Suspend pending commissions for deactivated partner.
        """
        try:
            logger.info(f"Handling PartnerDeactivated event for partner: {evento.aggregate_id}")
            
            # Here we would:
            # 1. Put all pending commissions on hold
            # 2. Send notifications about suspended commissions
            # 3. Update commission calculation rules
            
            logger.info(f"Commission processing suspended for deactivated partner: {evento.aggregate_id}")
            
        except Exception as e:
            logger.error(f"Error handling PartnerDeactivated event: {str(e)}")
            raise
    
    def handle_campaign_completed(self, sender, evento: CampaignCompleted):
        """
        Handle campaign completion event.
        Generate performance commissions based on campaign results.
        """
        try:
            logger.info(f"Handling CampaignCompleted event for campaign: {evento.aggregate_id}")
            
            # Extract campaign performance data
            campaign_performance = getattr(evento, 'performance_data', {})
            partner_id = getattr(evento, 'partner_id', None)
            
            if not partner_id:
                logger.warning(f"No partner ID found in CampaignCompleted event: {evento.aggregate_id}")
                return
            
            # Calculate performance-based commission
            if self._should_generate_performance_commission(campaign_performance):
                commission_amount = self._calculate_performance_commission(campaign_performance)
                
                # Create commission command
                from datetime import datetime, timedelta
                from decimal import Decimal
                
                comando = CrearCommission(
                    partner_id=partner_id,
                    commission_amount=commission_amount,
                    commission_rate=Decimal('0.10'),  # 10% performance bonus
                    commission_type='PERFORMANCE_BONUS',
                    transaction_id=f"perf_{evento.aggregate_id}",
                    transaction_type='CAMPAIGN_COMPLETION',
                    transaction_amount=campaign_performance.get('total_value', Decimal('0')),
                    transaction_date=datetime.now(),
                    calculation_period_start=datetime.now() - timedelta(days=30),
                    calculation_period_end=datetime.now(),
                    period_name=f"Performance Period - {datetime.now().strftime('%Y-%m')}"
                )
                
                # Execute commission creation
                commission_id = handle_crear_commission(comando)
                
                logger.info(f"Performance commission created: {commission_id} for campaign: {evento.aggregate_id}")
            
        except Exception as e:
            logger.error(f"Error handling CampaignCompleted event: {str(e)}")
            raise
    
    def handle_campaign_activated(self, sender, evento: CampaignActivated):
        """
        Handle campaign activation event.
        Setup commission structure for new campaign.
        """
        try:
            logger.info(f"Handling CampaignActivated event for campaign: {evento.aggregate_id}")
            
            # Setup commission tracking for campaign
            # This could involve creating commission rules,
            # initializing tracking mechanisms, etc.
            
            logger.info(f"Commission structure setup for activated campaign: {evento.aggregate_id}")
            
        except Exception as e:
            logger.error(f"Error handling CampaignActivated event: {str(e)}")
            raise
    
    def handle_commission_created(self, sender, evento: CommissionCreated):
        """
        Handle commission creation event.
        Trigger notifications and audit logging.
        """
        try:
            logger.info(f"Handling CommissionCreated event for commission: {evento.aggregate_id}")
            
            # Trigger notifications
            self._send_commission_notification(
                partner_id=evento.partner_id,
                commission_id=evento.aggregate_id,
                commission_amount=evento.commission_amount,
                event_type='created'
            )
            
            # Log for audit trail
            logger.info(f"Commission created - ID: {evento.aggregate_id}, "
                       f"Partner: {evento.partner_id}, Amount: {evento.commission_amount}")
            
        except Exception as e:
            logger.error(f"Error handling CommissionCreated event: {str(e)}")
            raise
    
    def handle_commission_approved(self, sender, evento: CommissionApproved):
        """
        Handle commission approval event.
        Trigger payment processing workflow.
        """
        try:
            logger.info(f"Handling CommissionApproved event for commission: {evento.aggregate_id}")
            
            # Trigger payment workflow
            # This could involve:
            # 1. Adding to payment queue
            # 2. Sending approval notifications
            # 3. Updating partner metrics
            
            self._send_commission_notification(
                partner_id=evento.partner_id,
                commission_id=evento.aggregate_id,
                commission_amount=evento.commission_amount,
                event_type='approved'
            )
            
            logger.info(f"Commission approved and queued for payment: {evento.aggregate_id}")
            
        except Exception as e:
            logger.error(f"Error handling CommissionApproved event: {str(e)}")
            raise
    
    def handle_commission_paid(self, sender, evento: CommissionPaid):
        """
        Handle commission payment event.
        Update partner metrics and send confirmations.
        """
        try:
            logger.info(f"Handling CommissionPaid event for commission: {evento.aggregate_id}")
            
            # Update partner metrics
            # This would involve updating partner's total earnings,
            # payment history, etc.
            
            # Send payment confirmation
            self._send_commission_notification(
                partner_id=evento.partner_id,
                commission_id=evento.aggregate_id,
                commission_amount=evento.commission_amount,
                event_type='paid'
            )
            
            logger.info(f"Commission payment processed and confirmed: {evento.aggregate_id}")
            
        except Exception as e:
            logger.error(f"Error handling CommissionPaid event: {str(e)}")
            raise
    
    def _should_generate_performance_commission(self, campaign_performance: dict) -> bool:
        """
        Determine if performance commission should be generated.
        """
        # Business logic to determine if performance warrants commission
        success_rate = campaign_performance.get('success_rate', 0)
        total_value = campaign_performance.get('total_value', 0)
        
        return success_rate >= 0.8 and total_value >= 1000  # 80% success rate and $1000+ value
    
    def _calculate_performance_commission(self, campaign_performance: dict) -> float:
        """
        Calculate performance-based commission amount.
        """
        from decimal import Decimal
        
        base_amount = campaign_performance.get('total_value', Decimal('0'))
        success_rate = campaign_performance.get('success_rate', 0)
        
        # Performance-based calculation
        performance_multiplier = min(success_rate, 1.0)  # Cap at 100%
        commission_rate = Decimal('0.05') + (Decimal(str(performance_multiplier)) * Decimal('0.05'))  # 5-10% based on performance
        
        return float(base_amount * commission_rate)
    
    def _send_commission_notification(self, partner_id: str, commission_id: str, 
                                    commission_amount: str, event_type: str):
        """
        Send commission-related notification.
        """
        # This would integrate with notification service
        logger.info(f"Commission notification sent - Partner: {partner_id}, "
                   f"Commission: {commission_id}, Type: {event_type}, Amount: {commission_amount}")


# Global handler instance
commission_handler = CommissionEventHandler()