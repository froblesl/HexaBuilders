"""
Campaign event handlers for HexaBuilders using PyDispatcher.
"""

import logging
from datetime import datetime
from pydispatcher import dispatcher

from ..dominio.eventos import (
    CampaignCreated, CampaignStatusChanged, CampaignActivated,
    CampaignPaused, CampaignCompleted, CampaignCancelled,
    CampaignUpdated, CampaignBudgetExceeded, CampaignMetricsUpdated,
    CampaignApproved, CampaignRejected
)

logger = logging.getLogger(__name__)


def configurar_handlers():
    """Configure all campaign event handlers using PyDispatcher."""
    
    # Campaign Created Event Handlers
    dispatcher.connect(
        handle_campaign_created_notifications,
        signal='CampaignCreated'
    )
    
    dispatcher.connect(
        handle_campaign_created_analytics,
        signal='CampaignCreated'
    )
    
    dispatcher.connect(
        handle_campaign_created_partner_metrics,
        signal='CampaignCreated'
    )
    
    # Campaign Status Changed Event Handlers
    dispatcher.connect(
        handle_campaign_status_changed_notifications,
        signal='CampaignStatusChanged'
    )
    
    dispatcher.connect(
        handle_campaign_status_changed_reporting,
        signal='CampaignStatusChanged'
    )
    
    # Campaign Activated Event Handlers
    dispatcher.connect(
        handle_campaign_activated_ad_platforms,
        signal='CampaignActivated'
    )
    
    dispatcher.connect(
        handle_campaign_activated_monitoring,
        signal='CampaignActivated'
    )
    
    # Campaign Paused Event Handlers
    dispatcher.connect(
        handle_campaign_paused_ad_platforms,
        signal='CampaignPaused'
    )
    
    dispatcher.connect(
        handle_campaign_paused_notifications,
        signal='CampaignPaused'
    )
    
    # Campaign Completed Event Handlers
    dispatcher.connect(
        handle_campaign_completed_final_reporting,
        signal='CampaignCompleted'
    )
    
    dispatcher.connect(
        handle_campaign_completed_commissions,
        signal='CampaignCompleted'
    )
    
    # Campaign Budget Exceeded Event Handlers
    dispatcher.connect(
        handle_campaign_budget_exceeded_alerts,
        signal='CampaignBudgetExceeded'
    )
    
    dispatcher.connect(
        handle_campaign_budget_exceeded_auto_actions,
        signal='CampaignBudgetExceeded'
    )
    
    # Campaign Metrics Updated Event Handlers
    dispatcher.connect(
        handle_campaign_metrics_updated_analytics,
        signal='CampaignMetricsUpdated'
    )
    
    dispatcher.connect(
        handle_campaign_metrics_updated_alerts,
        signal='CampaignMetricsUpdated'
    )
    
    # Campaign Approval Event Handlers
    dispatcher.connect(
        handle_campaign_approved_notifications,
        signal='CampaignApproved'
    )
    
    dispatcher.connect(
        handle_campaign_rejected_notifications,
        signal='CampaignRejected'
    )
    
    logger.info("All campaign event handlers configured successfully")


# Campaign Created Event Handlers

def handle_campaign_created_notifications(evento: CampaignCreated, **kwargs):
    """Handle campaign created event - send notifications."""
    try:
        logger.info(f"Sending campaign creation notifications for: {evento.aggregate_id}")
        
        notification_data = {
            'campaign_id': evento.aggregate_id,
            'campaign_name': evento.campaign_name,
            'partner_id': evento.partner_id,
            'campaign_type': evento.campaign_type,
            'budget_amount': evento.budget_amount,
            'template': 'campaign_created',
            'channel': 'email',
            'data': {
                'start_date': evento.start_date,
                'end_date': evento.end_date,
                'created_at': evento.created_at.isoformat()
            }
        }
        
        # Mock call to notifications service
        logger.debug(f"Campaign creation notification: {notification_data}")
        
        # notifications_service.send_notification(notification_data)
        
        logger.info(f"Campaign creation notifications sent for: {evento.aggregate_id}")
        
    except Exception as e:
        logger.error(f"Failed to send campaign creation notifications for {evento.aggregate_id}: {str(e)}")


def handle_campaign_created_analytics(evento: CampaignCreated, **kwargs):
    """Handle campaign created event - initialize analytics tracking."""
    try:
        logger.info(f"Initializing analytics tracking for campaign: {evento.aggregate_id}")
        
        analytics_data = {
            'campaign_id': evento.aggregate_id,
            'partner_id': evento.partner_id,
            'campaign_name': evento.campaign_name,
            'campaign_type': evento.campaign_type,
            'budget_amount': evento.budget_amount,
            'start_date': evento.start_date,
            'end_date': evento.end_date,
            'action': 'initialize_tracking'
        }
        
        # Mock call to analytics service
        logger.debug(f"Analytics tracking initialized: {analytics_data}")
        
        # analytics_service.initialize_campaign_tracking(analytics_data)
        
        logger.info(f"Analytics tracking initialized for campaign: {evento.aggregate_id}")
        
    except Exception as e:
        logger.error(f"Failed to initialize analytics tracking for {evento.aggregate_id}: {str(e)}")


def handle_campaign_created_partner_metrics(evento: CampaignCreated, **kwargs):
    """Handle campaign created event - update partner metrics."""
    try:
        logger.info(f"Updating partner metrics for campaign creation: {evento.aggregate_id}")
        
        partner_update = {
            'partner_id': evento.partner_id,
            'action': 'increment_total_campaigns',
            'campaign_id': evento.aggregate_id,
            'campaign_type': evento.campaign_type,
            'budget_amount': evento.budget_amount
        }
        
        # Mock call to partner metrics service
        logger.debug(f"Partner metrics update: {partner_update}")
        
        # partner_metrics_service.update_metrics(partner_update)
        
        logger.info(f"Partner metrics updated for campaign: {evento.aggregate_id}")
        
    except Exception as e:
        logger.error(f"Failed to update partner metrics for {evento.aggregate_id}: {str(e)}")


# Campaign Status Changed Event Handlers

def handle_campaign_status_changed_notifications(evento: CampaignStatusChanged, **kwargs):
    """Handle campaign status changed event - send notifications."""
    try:
        logger.info(f"Sending status change notifications for campaign: {evento.aggregate_id}")
        
        template_map = {
            'ACTIVE': 'campaign_activated',
            'PAUSED': 'campaign_paused',
            'COMPLETED': 'campaign_completed',
            'CANCELLED': 'campaign_cancelled'
        }
        
        template = template_map.get(evento.new_status, 'campaign_status_changed')
        
        notification_data = {
            'campaign_id': evento.aggregate_id,
            'template': template,
            'channel': 'email',
            'data': {
                'old_status': evento.old_status,
                'new_status': evento.new_status,
                'reason': evento.reason,
                'changed_by': evento.changed_by
            }
        }
        
        # Mock call to notifications service
        logger.debug(f"Status change notification: {notification_data}")
        
        # notifications_service.send_notification(notification_data)
        
        logger.info(f"Status change notifications sent for campaign: {evento.aggregate_id}")
        
    except Exception as e:
        logger.error(f"Failed to send status change notifications for {evento.aggregate_id}: {str(e)}")


def handle_campaign_status_changed_reporting(evento: CampaignStatusChanged, **kwargs):
    """Handle campaign status changed event - update reporting."""
    try:
        logger.info(f"Updating reporting for campaign status change: {evento.aggregate_id}")
        
        reporting_data = {
            'campaign_id': evento.aggregate_id,
            'status_change': {
                'old_status': evento.old_status,
                'new_status': evento.new_status,
                'reason': evento.reason,
                'changed_by': evento.changed_by,
                'timestamp': datetime.now().isoformat()
            },
            'action': 'log_status_change'
        }
        
        # Mock call to reporting service
        logger.debug(f"Reporting update: {reporting_data}")
        
        # reporting_service.log_campaign_status_change(reporting_data)
        
        logger.info(f"Reporting updated for campaign: {evento.aggregate_id}")
        
    except Exception as e:
        logger.error(f"Failed to update reporting for {evento.aggregate_id}: {str(e)}")


# Campaign Activated Event Handlers

def handle_campaign_activated_ad_platforms(evento: CampaignActivated, **kwargs):
    """Handle campaign activated event - sync with ad platforms."""
    try:
        logger.info(f"Syncing activated campaign with ad platforms: {evento.aggregate_id}")
        
        ad_platform_data = {
            'campaign_id': evento.aggregate_id,
            'campaign_name': evento.campaign_name,
            'partner_id': evento.partner_id,
            'start_date': evento.start_date,
            'end_date': evento.end_date,
            'budget_amount': evento.budget_amount,
            'action': 'activate_campaign'
        }
        
        # Mock call to ad platforms service
        logger.debug(f"Ad platform sync: {ad_platform_data}")
        
        # ad_platforms_service.activate_campaign(ad_platform_data)
        
        logger.info(f"Campaign synced with ad platforms: {evento.aggregate_id}")
        
    except Exception as e:
        logger.error(f"Failed to sync campaign with ad platforms {evento.aggregate_id}: {str(e)}")


def handle_campaign_activated_monitoring(evento: CampaignActivated, **kwargs):
    """Handle campaign activated event - start monitoring."""
    try:
        logger.info(f"Starting monitoring for activated campaign: {evento.aggregate_id}")
        
        monitoring_data = {
            'campaign_id': evento.aggregate_id,
            'partner_id': evento.partner_id,
            'budget_amount': evento.budget_amount,
            'end_date': evento.end_date,
            'monitoring_rules': [
                'budget_threshold_80_percent',
                'budget_threshold_95_percent',
                'performance_below_average',
                'campaign_expiry_reminder'
            ],
            'action': 'start_monitoring'
        }
        
        # Mock call to monitoring service
        logger.debug(f"Monitoring setup: {monitoring_data}")
        
        # monitoring_service.start_campaign_monitoring(monitoring_data)
        
        logger.info(f"Monitoring started for campaign: {evento.aggregate_id}")
        
    except Exception as e:
        logger.error(f"Failed to start monitoring for {evento.aggregate_id}: {str(e)}")


# Campaign Budget Exceeded Event Handlers

def handle_campaign_budget_exceeded_alerts(evento: CampaignBudgetExceeded, **kwargs):
    """Handle campaign budget exceeded event - send alerts."""
    try:
        logger.info(f"Sending budget exceeded alerts for campaign: {evento.aggregate_id}")
        
        alert_data = {
            'campaign_id': evento.aggregate_id,
            'campaign_name': evento.campaign_name,
            'partner_id': evento.partner_id,
            'budget_amount': evento.budget_amount,
            'spent_amount': evento.spent_amount,
            'auto_paused': evento.auto_paused,
            'alert_type': 'budget_exceeded',
            'severity': 'high',
            'template': 'campaign_budget_exceeded'
        }
        
        # Mock call to alerts service
        logger.debug(f"Budget exceeded alert: {alert_data}")
        
        # alerts_service.send_budget_alert(alert_data)
        
        logger.info(f"Budget exceeded alerts sent for campaign: {evento.aggregate_id}")
        
    except Exception as e:
        logger.error(f"Failed to send budget exceeded alerts for {evento.aggregate_id}: {str(e)}")


def handle_campaign_budget_exceeded_auto_actions(evento: CampaignBudgetExceeded, **kwargs):
    """Handle campaign budget exceeded event - perform auto actions."""
    try:
        logger.info(f"Performing auto actions for budget exceeded campaign: {evento.aggregate_id}")
        
        if evento.auto_paused:
            auto_action_data = {
                'campaign_id': evento.aggregate_id,
                'partner_id': evento.partner_id,
                'action': 'auto_pause',
                'reason': 'budget_exceeded',
                'original_budget': evento.budget_amount,
                'spent_amount': evento.spent_amount
            }
            
            # Mock call to auto actions service
            logger.debug(f"Auto action executed: {auto_action_data}")
            
            # auto_actions_service.execute_campaign_action(auto_action_data)
        
        logger.info(f"Auto actions completed for campaign: {evento.aggregate_id}")
        
    except Exception as e:
        logger.error(f"Failed to perform auto actions for {evento.aggregate_id}: {str(e)}")


# Campaign Metrics Updated Event Handlers

def handle_campaign_metrics_updated_analytics(evento: CampaignMetricsUpdated, **kwargs):
    """Handle campaign metrics updated event - update analytics."""
    try:
        logger.info(f"Updating analytics for campaign metrics: {evento.aggregate_id}")
        
        analytics_update = {
            'campaign_id': evento.aggregate_id,
            'old_metrics': evento.old_metrics,
            'new_metrics': evento.new_metrics,
            'source': evento.source,
            'updated_at': datetime.now().isoformat(),
            'action': 'update_metrics'
        }
        
        # Mock call to analytics service
        logger.debug(f"Analytics metrics update: {analytics_update}")
        
        # analytics_service.update_campaign_metrics(analytics_update)
        
        logger.info(f"Analytics updated for campaign: {evento.aggregate_id}")
        
    except Exception as e:
        logger.error(f"Failed to update analytics for {evento.aggregate_id}: {str(e)}")


def handle_campaign_metrics_updated_alerts(evento: CampaignMetricsUpdated, **kwargs):
    """Handle campaign metrics updated event - check for alerts."""
    try:
        logger.info(f"Checking metrics-based alerts for campaign: {evento.aggregate_id}")
        
        # Check for performance alerts
        new_metrics = evento.new_metrics
        
        alerts_to_send = []
        
        # Check click-through rate
        if new_metrics.get('clicks', 0) > 100:  # Only check if sufficient data
            impressions = new_metrics.get('impressions', 1)
            clicks = new_metrics.get('clicks', 0)
            ctr = clicks / impressions if impressions > 0 else 0
            
            if ctr < 0.005:  # Less than 0.5% CTR
                alerts_to_send.append({
                    'type': 'low_ctr',
                    'message': f'Campaign CTR ({ctr:.2%}) is below recommended threshold',
                    'severity': 'medium'
                })
        
        # Check conversion rate
        if new_metrics.get('conversions', 0) == 0 and new_metrics.get('clicks', 0) > 50:
            alerts_to_send.append({
                'type': 'no_conversions',
                'message': 'Campaign has clicks but no conversions - check tracking',
                'severity': 'high'
            })
        
        # Send alerts if any
        for alert in alerts_to_send:
            alert_data = {
                'campaign_id': evento.aggregate_id,
                'alert_type': alert['type'],
                'message': alert['message'],
                'severity': alert['severity'],
                'metrics': new_metrics
            }
            
            # Mock call to alerts service
            logger.debug(f"Performance alert: {alert_data}")
            
            # alerts_service.send_performance_alert(alert_data)
        
        logger.info(f"Metrics alerts checked for campaign: {evento.aggregate_id}")
        
    except Exception as e:
        logger.error(f"Failed to check metrics alerts for {evento.aggregate_id}: {str(e)}")


# Campaign Approval Event Handlers

def handle_campaign_approved_notifications(evento: CampaignApproved, **kwargs):
    """Handle campaign approved event - send notifications."""
    try:
        logger.info(f"Sending approval notifications for campaign: {evento.aggregate_id}")
        
        notification_data = {
            'campaign_id': evento.aggregate_id,
            'campaign_name': evento.campaign_name,
            'partner_id': evento.partner_id,
            'approved_by': evento.approved_by,
            'approval_notes': evento.approval_notes,
            'template': 'campaign_approved',
            'channel': 'email'
        }
        
        # Mock call to notifications service
        logger.debug(f"Approval notification: {notification_data}")
        
        # notifications_service.send_notification(notification_data)
        
        logger.info(f"Approval notifications sent for campaign: {evento.aggregate_id}")
        
    except Exception as e:
        logger.error(f"Failed to send approval notifications for {evento.aggregate_id}: {str(e)}")


def handle_campaign_rejected_notifications(evento: CampaignRejected, **kwargs):
    """Handle campaign rejected event - send notifications."""
    try:
        logger.info(f"Sending rejection notifications for campaign: {evento.aggregate_id}")
        
        notification_data = {
            'campaign_id': evento.aggregate_id,
            'campaign_name': evento.campaign_name,
            'partner_id': evento.partner_id,
            'rejected_by': evento.rejected_by,
            'rejection_reason': evento.rejection_reason,
            'required_changes': evento.required_changes,
            'template': 'campaign_rejected',
            'channel': 'email'
        }
        
        # Mock call to notifications service
        logger.debug(f"Rejection notification: {notification_data}")
        
        # notifications_service.send_notification(notification_data)
        
        logger.info(f"Rejection notifications sent for campaign: {evento.aggregate_id}")
        
    except Exception as e:
        logger.error(f"Failed to send rejection notifications for {evento.aggregate_id}: {str(e)}")


# Auto-configure handlers when module is imported
try:
    configurar_handlers()
except Exception as e:
    logger.warning(f"Failed to auto-configure campaign event handlers: {e}")
    # Handlers can be configured manually later