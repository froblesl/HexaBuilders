"""
Event handlers for Analytics module in HexaBuilders.
Implements Tutorial 5 (Events) patterns with PyDispatcher integration.
"""

import logging
from datetime import datetime, timedelta
from pydispatch import dispatcher

from partner_management.seedwork.dominio.eventos import DomainEvent
from ...partners.dominio.eventos import PartnerCreated, PartnerActivated, PartnerDeactivated, PartnerUpdated
from ...campaigns.dominio.eventos import CampaignCompleted, CampaignActivated, CampaignCreated
from ...commissions.dominio.eventos import CommissionCreated, CommissionPaid, CommissionApproved
from .comandos.generar_reporte import GenerarReporte, handle_generar_reporte
from ..dominio.eventos import (
    AnalyticsReportGenerated, AnalyticsInsightDiscovered, AnalyticsReportFailed
)

logger = logging.getLogger(__name__)


class AnalyticsEventHandler:
    """
    Event handler for Analytics-related domain events.
    Implements cross-module integration through domain events.
    """
    
    def __init__(self):
        self._setup_event_subscriptions()
    
    def _setup_event_subscriptions(self):
        """Setup domain event subscriptions using PyDispatcher."""
        
        # Partner events
        dispatcher.connect(
            self.handle_partner_created,
            signal='DomainEvent',
            sender='PartnerCreated'
        )
        
        dispatcher.connect(
            self.handle_partner_activated,
            signal='DomainEvent',
            sender='PartnerActivated'
        )
        
        dispatcher.connect(
            self.handle_partner_updated,
            signal='DomainEvent',
            sender='PartnerUpdated'
        )
        
        # Campaign events
        dispatcher.connect(
            self.handle_campaign_created,
            signal='DomainEvent',
            sender='CampaignCreated'
        )
        
        dispatcher.connect(
            self.handle_campaign_completed,
            signal='DomainEvent',
            sender='CampaignCompleted'
        )
        
        # Commission events
        dispatcher.connect(
            self.handle_commission_created,
            signal='DomainEvent',
            sender='CommissionCreated'
        )
        
        dispatcher.connect(
            self.handle_commission_paid,
            signal='DomainEvent',
            sender='CommissionPaid'
        )
        
        # Analytics events (internal)
        dispatcher.connect(
            self.handle_analytics_report_generated,
            signal='DomainEvent',
            sender='AnalyticsReportGenerated'
        )
        
        dispatcher.connect(
            self.handle_analytics_insight_discovered,
            signal='DomainEvent',
            sender='AnalyticsInsightDiscovered'
        )
    
    def handle_partner_created(self, sender, evento: PartnerCreated):
        """
        Handle partner creation event.
        Generate initial analytics baseline for new partner.
        """
        try:
            logger.info(f"Handling PartnerCreated event for partner: {evento.aggregate_id}")
            
            # Generate initial analytics report after a delay to allow data to accumulate
            # This would typically be scheduled rather than immediate
            self._schedule_initial_analytics_report(evento.aggregate_id)
            
            logger.info(f"Initial analytics setup scheduled for partner: {evento.aggregate_id}")
            
        except Exception as e:
            logger.error(f"Error handling PartnerCreated event: {str(e)}")
            raise
    
    def handle_partner_activated(self, sender, evento: PartnerActivated):
        """
        Handle partner activation event.
        Generate performance baseline report.
        """
        try:
            logger.info(f"Handling PartnerActivated event for partner: {evento.aggregate_id}")
            
            # Generate activation performance report
            self._generate_activation_report(evento.aggregate_id)
            
            logger.info(f"Activation analytics report generated for partner: {evento.aggregate_id}")
            
        except Exception as e:
            logger.error(f"Error handling PartnerActivated event: {str(e)}")
            raise
    
    def handle_partner_updated(self, sender, evento: PartnerUpdated):
        """
        Handle partner update event.
        Update analytics profiles and trigger recalculation if needed.
        """
        try:
            logger.info(f"Handling PartnerUpdated event for partner: {evento.aggregate_id}")
            
            # Check if significant changes require analytics update
            old_data = getattr(evento, 'old_data', {})
            new_data = getattr(evento, 'new_data', {})
            
            if self._requires_analytics_update(old_data, new_data):
                self._schedule_analytics_refresh(evento.aggregate_id, "partner_update")
            
            logger.info(f"Analytics update processed for partner: {evento.aggregate_id}")
            
        except Exception as e:
            logger.error(f"Error handling PartnerUpdated event: {str(e)}")
            raise
    
    def handle_campaign_created(self, sender, evento: CampaignCreated):
        """
        Handle campaign creation event.
        Update partner performance projections.
        """
        try:
            logger.info(f"Handling CampaignCreated event for campaign: {evento.aggregate_id}")
            
            partner_id = getattr(evento, 'partner_id', None)
            if partner_id:
                # Update analytics to reflect new campaign activity
                self._update_campaign_analytics(partner_id, "campaign_created", evento.aggregate_id)
            
            logger.info(f"Campaign creation analytics updated for campaign: {evento.aggregate_id}")
            
        except Exception as e:
            logger.error(f"Error handling CampaignCreated event: {str(e)}")
            raise
    
    def handle_campaign_completed(self, sender, evento: CampaignCompleted):
        """
        Handle campaign completion event.
        Generate campaign performance analytics and update partner metrics.
        """
        try:
            logger.info(f"Handling CampaignCompleted event for campaign: {evento.aggregate_id}")
            
            partner_id = getattr(evento, 'partner_id', None)
            if partner_id:
                # Generate comprehensive campaign analytics
                performance_data = getattr(evento, 'performance_data', {})
                
                # Trigger analytics report if campaign performance is significant
                if self._is_significant_campaign_completion(performance_data):
                    self._generate_campaign_completion_report(
                        partner_id, evento.aggregate_id, performance_data
                    )
                
                # Update ongoing analytics
                self._update_campaign_analytics(partner_id, "campaign_completed", evento.aggregate_id)
            
            logger.info(f"Campaign completion analytics processed for campaign: {evento.aggregate_id}")
            
        except Exception as e:
            logger.error(f"Error handling CampaignCompleted event: {str(e)}")
            raise
    
    def handle_commission_created(self, sender, evento: CommissionCreated):
        """
        Handle commission creation event.
        Update partner earnings analytics.
        """
        try:
            logger.info(f"Handling CommissionCreated event for commission: {evento.aggregate_id}")
            
            partner_id = getattr(evento, 'partner_id', None)
            if partner_id:
                # Update commission analytics
                self._update_commission_analytics(partner_id, "commission_created", evento)
                
                # Check if partner has reached earnings milestones
                self._check_earnings_milestones(partner_id, evento)
            
            logger.info(f"Commission analytics updated for commission: {evento.aggregate_id}")
            
        except Exception as e:
            logger.error(f"Error handling CommissionCreated event: {str(e)}")
            raise
    
    def handle_commission_paid(self, sender, evento: CommissionPaid):
        """
        Handle commission payment event.
        Update payment analytics and partner financial metrics.
        """
        try:
            logger.info(f"Handling CommissionPaid event for commission: {evento.aggregate_id}")
            
            partner_id = getattr(evento, 'partner_id', None)
            if partner_id:
                # Update payment analytics
                self._update_commission_analytics(partner_id, "commission_paid", evento)
                
                # Generate quarterly earnings report if applicable
                if self._should_generate_earnings_report(partner_id, evento):
                    self._generate_earnings_report(partner_id)
            
            logger.info(f"Commission payment analytics updated for commission: {evento.aggregate_id}")
            
        except Exception as e:
            logger.error(f"Error handling CommissionPaid event: {str(e)}")
            raise
    
    def handle_analytics_report_generated(self, sender, evento: AnalyticsReportGenerated):
        """
        Handle analytics report generation completion.
        Trigger follow-up actions and notifications.
        """
        try:
            logger.info(f"Handling AnalyticsReportGenerated event for report: {evento.aggregate_id}")
            
            partner_id = getattr(evento, 'partner_id', None)
            if partner_id:
                # Send notification about completed report
                self._send_report_notification(partner_id, evento.aggregate_id, "completed")
                
                # Schedule next automated report if applicable
                self._schedule_next_report(partner_id, evento.aggregate_id)
            
            logger.info(f"Report generation follow-up completed for report: {evento.aggregate_id}")
            
        except Exception as e:
            logger.error(f"Error handling AnalyticsReportGenerated event: {str(e)}")
            raise
    
    def handle_analytics_insight_discovered(self, sender, evento: AnalyticsInsightDiscovered):
        """
        Handle discovery of significant analytics insights.
        Trigger alerts and recommendations.
        """
        try:
            logger.info(f"Handling AnalyticsInsightDiscovered event for insight: {evento.insight_type}")
            
            partner_id = getattr(evento, 'partner_id', None)
            severity = getattr(evento, 'severity', 'info')
            
            if partner_id and severity in ['warning', 'critical']:
                # Send alert for critical insights
                self._send_insight_alert(partner_id, evento)
                
                # Generate action items based on insight
                self._generate_action_items(partner_id, evento)
            
            logger.info(f"Insight discovery processed for partner: {partner_id}")
            
        except Exception as e:
            logger.error(f"Error handling AnalyticsInsightDiscovered event: {str(e)}")
            raise
    
    def _schedule_initial_analytics_report(self, partner_id: str):
        """Schedule initial analytics report for new partner."""
        # In a real implementation, this would use a job queue or scheduler
        logger.info(f"Scheduling initial analytics report for partner: {partner_id}")
    
    def _generate_activation_report(self, partner_id: str):
        """Generate partner activation analytics report."""
        try:
            # Create activation report
            now = datetime.now()
            comando = GenerarReporte(
                partner_id=partner_id,
                report_type="PARTNER_PERFORMANCE",
                period_start=now - timedelta(days=30),  # Last 30 days
                period_end=now,
                period_name="Partner Activation Report",
                generated_by="analytics_system"
            )
            
            report_id = handle_generar_reporte(comando)
            logger.info(f"Activation report generated: {report_id}")
            
        except Exception as e:
            logger.error(f"Failed to generate activation report: {str(e)}")
    
    def _requires_analytics_update(self, old_data: dict, new_data: dict) -> bool:
        """Check if partner updates require analytics refresh."""
        # Check for significant changes that affect analytics
        significant_fields = ['nombre', 'telefono', 'status']
        
        for field in significant_fields:
            if old_data.get(field) != new_data.get(field):
                return True
        
        return False
    
    def _schedule_analytics_refresh(self, partner_id: str, reason: str):
        """Schedule analytics refresh for partner."""
        logger.info(f"Scheduling analytics refresh for partner {partner_id}, reason: {reason}")
    
    def _update_campaign_analytics(self, partner_id: str, event_type: str, campaign_id: str):
        """Update campaign-related analytics."""
        logger.info(f"Updating campaign analytics for partner {partner_id}, event: {event_type}, campaign: {campaign_id}")
    
    def _update_commission_analytics(self, partner_id: str, event_type: str, evento):
        """Update commission-related analytics."""
        logger.info(f"Updating commission analytics for partner {partner_id}, event: {event_type}")
    
    def _is_significant_campaign_completion(self, performance_data: dict) -> bool:
        """Check if campaign completion is significant enough for special report."""
        # Generate report for high-value or high-performance campaigns
        total_value = performance_data.get('total_value', 0)
        success_rate = performance_data.get('success_rate', 0)
        
        return total_value > 5000 or success_rate > 0.9  # High value or high success
    
    def _generate_campaign_completion_report(self, partner_id: str, campaign_id: str, performance_data: dict):
        """Generate special report for significant campaign completions."""
        try:
            now = datetime.now()
            comando = GenerarReporte(
                partner_id=partner_id,
                report_type="CAMPAIGN_ANALYSIS",
                period_start=now - timedelta(days=7),  # Focus on recent performance
                period_end=now,
                period_name=f"Campaign Completion Analysis - {campaign_id[:8]}",
                generated_by="analytics_system"
            )
            
            report_id = handle_generar_reporte(comando)
            logger.info(f"Campaign completion report generated: {report_id}")
            
        except Exception as e:
            logger.error(f"Failed to generate campaign completion report: {str(e)}")
    
    def _check_earnings_milestones(self, partner_id: str, evento):
        """Check if partner has reached earnings milestones."""
        # Implementation would check cumulative earnings and trigger milestone reports
        logger.info(f"Checking earnings milestones for partner: {partner_id}")
    
    def _should_generate_earnings_report(self, partner_id: str, evento) -> bool:
        """Check if quarterly earnings report should be generated."""
        # Generate report at end of quarters or for high earners
        return datetime.now().month % 3 == 0  # End of quarter
    
    def _generate_earnings_report(self, partner_id: str):
        """Generate quarterly earnings report."""
        try:
            now = datetime.now()
            comando = GenerarReporte(
                partner_id=partner_id,
                report_type="COMMISSION_SUMMARY",
                period_start=now - timedelta(days=90),  # Last quarter
                period_end=now,
                period_name="Quarterly Earnings Report",
                generated_by="analytics_system"
            )
            
            report_id = handle_generar_reporte(comando)
            logger.info(f"Earnings report generated: {report_id}")
            
        except Exception as e:
            logger.error(f"Failed to generate earnings report: {str(e)}")
    
    def _send_report_notification(self, partner_id: str, report_id: str, status: str):
        """Send notification about report status."""
        logger.info(f"Sending report notification - Partner: {partner_id}, Report: {report_id}, Status: {status}")
    
    def _schedule_next_report(self, partner_id: str, current_report_id: str):
        """Schedule next automated report."""
        logger.info(f"Scheduling next report for partner: {partner_id}")
    
    def _send_insight_alert(self, partner_id: str, evento):
        """Send alert for critical insights."""
        insight_type = getattr(evento, 'insight_type', 'unknown')
        severity = getattr(evento, 'severity', 'info')
        
        logger.info(f"Sending insight alert - Partner: {partner_id}, Type: {insight_type}, Severity: {severity}")
    
    def _generate_action_items(self, partner_id: str, evento):
        """Generate action items based on insights."""
        logger.info(f"Generating action items for partner: {partner_id} based on insight discovery")


# Global handler instance
analytics_handler = AnalyticsEventHandler()