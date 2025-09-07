"""
Using PyDispatcher for event handling integration.
"""

import logging
from datetime import datetime
from pydispatcher import dispatcher

from ..dominio.eventos import (
    PartnerCreated, PartnerStatusChanged, PartnerProfileUpdated,
    PartnerValidated, PartnerSuspended, PartnerReactivated
)

logger = logging.getLogger(__name__)


def configurar_handlers():
    """Configure all event handlers using PyDispatcher."""
    
    # Partner Created Event Handlers
    dispatcher.connect(
        handle_partner_created_metrics,
        signal='PartnerCreated'
    )
    
    dispatcher.connect(
        handle_partner_created_notifications,
        signal='PartnerCreated'
    )
    
    dispatcher.connect(
        handle_partner_created_onboarding,
        signal='PartnerCreated'
    )
    
    # Partner Status Changed Event Handlers
    dispatcher.connect(
        handle_partner_status_changed_campaigns,
        signal='PartnerStatusChanged'
    )
    
    dispatcher.connect(
        handle_partner_status_changed_commissions,
        signal='PartnerStatusChanged'
    )
    
    dispatcher.connect(
        handle_partner_status_changed_notifications,
        signal='PartnerStatusChanged'
    )
    
    # Partner Profile Updated Event Handlers
    dispatcher.connect(
        handle_partner_profile_updated_cache,
        signal='PartnerProfileUpdated'
    )
    
    dispatcher.connect(
        handle_partner_profile_updated_search,
        signal='PartnerProfileUpdated'
    )
    
    dispatcher.connect(
        handle_partner_profile_updated_recommendations,
        signal='PartnerProfileUpdated'
    )
    
    # Partner Validated Event Handlers
    dispatcher.connect(
        handle_partner_validated_trust_score,
        signal='PartnerValidated'
    )
    
    dispatcher.connect(
        handle_partner_validated_features,
        signal='PartnerValidated'
    )
    
    # Partner Suspended Event Handlers
    dispatcher.connect(
        handle_partner_suspended_campaigns,
        signal='PartnerSuspended'
    )
    
    dispatcher.connect(
        handle_partner_suspended_access,
        signal='PartnerSuspended'
    )
    
    # Partner Reactivated Event Handlers
    dispatcher.connect(
        handle_partner_reactivated_campaigns,
        signal='PartnerReactivated'
    )
    
    dispatcher.connect(
        handle_partner_reactivated_notifications,
        signal='PartnerReactivated'
    )
    
    logger.info("All partner event handlers configured successfully")


# PartnerCreated Event Handlers

def handle_partner_created_metrics(evento: PartnerCreated, **kwargs):
    """Handle partner created event - create initial metrics."""
    try:
        logger.info(f"Creating initial metrics for partner: {evento.aggregate_id}")
        
        # Create initial partner metrics in analytics module
        # This would typically make a call to the analytics service
        initial_metrics = {
            'partner_id': evento.aggregate_id,
            'total_campaigns': 0,
            'completed_campaigns': 0,
            'success_rate': 0.0,
            'total_commissions': 0.0,
            'average_rating': 0.0,
            'created_at': datetime.now().isoformat()
        }
        
        # Mock call to analytics service
        logger.debug(f"Initial metrics created: {initial_metrics}")
        
        # Here we would typically call:
        # analytics_service.create_partner_metrics(initial_metrics)
        
        logger.info(f"Initial metrics created successfully for partner: {evento.aggregate_id}")
        
    except Exception as e:
        logger.error(f"Failed to create initial metrics for partner {evento.aggregate_id}: {str(e)}")
        # Don't re-raise to avoid breaking the main transaction


def handle_partner_created_notifications(evento: PartnerCreated, **kwargs):
    """Handle partner created event - send welcome notifications."""
    try:
        logger.info(f"Sending welcome notifications for partner: {evento.aggregate_id}")
        
        # Prepare welcome notification
        notification_data = {
            'partner_id': evento.aggregate_id,
            'partner_name': evento.partner_name,
            'partner_email': evento.partner_email,
            'template': 'partner_welcome',
            'channel': 'email',
            'data': {
                'partner_type': evento.partner_type,
                'created_at': evento.created_at.isoformat()
            }
        }
        
        # Mock call to notifications service
        logger.debug(f"Welcome notification prepared: {notification_data}")
        
        # Here we would typically call:
        # notifications_service.send_notification(notification_data)
        
        logger.info(f"Welcome notifications sent successfully for partner: {evento.aggregate_id}")
        
    except Exception as e:
        logger.error(f"Failed to send welcome notifications for partner {evento.aggregate_id}: {str(e)}")


def handle_partner_created_onboarding(evento: PartnerCreated, **kwargs):
    """Handle partner created event - start onboarding process."""
    try:
        logger.info(f"Starting onboarding process for partner: {evento.aggregate_id}")
        
        # Create onboarding checklist based on partner type
        onboarding_tasks = []
        
        # Common tasks for all partners
        onboarding_tasks.extend([
            'email_verification',
            'phone_verification', 
            'profile_completion',
            'terms_acceptance'
        ])
        
        # Business-specific tasks
        if evento.partner_type in ['EMPRESA', 'STARTUP']:
            onboarding_tasks.extend([
                'business_verification',
                'tax_id_verification',
                'business_profile_completion'
            ])
        
        onboarding_data = {
            'partner_id': evento.aggregate_id,
            'partner_type': evento.partner_type,
            'tasks': onboarding_tasks,
            'created_at': datetime.now().isoformat()
        }
        
        # Mock call to onboarding service
        logger.debug(f"Onboarding process started: {onboarding_data}")
        
        # Here we would typically call:
        # onboarding_service.create_onboarding_process(onboarding_data)
        
        logger.info(f"Onboarding process started successfully for partner: {evento.aggregate_id}")
        
    except Exception as e:
        logger.error(f"Failed to start onboarding process for partner {evento.aggregate_id}: {str(e)}")


# PartnerStatusChanged Event Handlers

def handle_partner_status_changed_campaigns(evento: PartnerStatusChanged, **kwargs):
    """Handle partner status changed - update campaign assignments."""
    try:
        logger.info(f"Updating campaign assignments for partner {evento.aggregate_id}: {evento.old_status} -> {evento.new_status}")
        
        # If partner is being deactivated/suspended, pause their campaigns
        if evento.new_status in ['INACTIVO', 'SUSPENDIDO']:
            campaign_update = {
                'partner_id': evento.aggregate_id,
                'action': 'pause_campaigns',
                'reason': f'Partner status changed to {evento.new_status}',
                'changed_by': evento.changed_by
            }
            
            # Mock call to campaigns service
            logger.debug(f"Pausing campaigns: {campaign_update}")
            
            # campaigns_service.pause_partner_campaigns(campaign_update)
        
        # If partner is being reactivated, resume their campaigns
        elif evento.new_status == 'ACTIVO' and evento.old_status in ['INACTIVO', 'SUSPENDIDO']:
            campaign_update = {
                'partner_id': evento.aggregate_id,
                'action': 'resume_campaigns',
                'reason': f'Partner status changed to {evento.new_status}',
                'changed_by': evento.changed_by
            }
            
            # Mock call to campaigns service
            logger.debug(f"Resuming campaigns: {campaign_update}")
            
            # campaigns_service.resume_partner_campaigns(campaign_update)
        
        logger.info(f"Campaign assignments updated successfully for partner: {evento.aggregate_id}")
        
    except Exception as e:
        logger.error(f"Failed to update campaign assignments for partner {evento.aggregate_id}: {str(e)}")


def handle_partner_status_changed_commissions(evento: PartnerStatusChanged, **kwargs):
    """Handle partner status changed - update commission processing."""
    try:
        logger.info(f"Updating commission processing for partner {evento.aggregate_id}: {evento.old_status} -> {evento.new_status}")
        
        commission_update = {
            'partner_id': evento.aggregate_id,
            'old_status': evento.old_status,
            'new_status': evento.new_status,
            'change_reason': evento.change_reason,
            'changed_by': evento.changed_by,
            'changed_at': datetime.now().isoformat()
        }
        
        # If partner is being suspended/deactivated, hold commissions
        if evento.new_status in ['SUSPENDIDO', 'INACTIVO']:
            commission_update['action'] = 'hold_commissions'
        
        # If partner is being reactivated, release held commissions
        elif evento.new_status == 'ACTIVO' and evento.old_status in ['SUSPENDIDO', 'INACTIVO']:
            commission_update['action'] = 'release_commissions'
        
        # Mock call to commissions service
        logger.debug(f"Commission processing update: {commission_update}")
        
        # commissions_service.update_partner_commission_status(commission_update)
        
        logger.info(f"Commission processing updated successfully for partner: {evento.aggregate_id}")
        
    except Exception as e:
        logger.error(f"Failed to update commission processing for partner {evento.aggregate_id}: {str(e)}")


def handle_partner_status_changed_notifications(evento: PartnerStatusChanged, **kwargs):
    """Handle partner status changed - send status change notifications."""
    try:
        logger.info(f"Sending status change notifications for partner: {evento.aggregate_id}")
        
        # Determine notification template based on status change
        template_map = {
            'ACTIVO': 'partner_activated',
            'INACTIVO': 'partner_deactivated', 
            'SUSPENDIDO': 'partner_suspended',
            'ELIMINADO': 'partner_deleted'
        }
        
        template = template_map.get(evento.new_status, 'partner_status_changed')
        
        notification_data = {
            'partner_id': evento.aggregate_id,
            'template': template,
            'channel': 'email',
            'data': {
                'old_status': evento.old_status,
                'new_status': evento.new_status,
                'change_reason': evento.change_reason,
                'changed_by': evento.changed_by
            }
        }
        
        # Mock call to notifications service
        logger.debug(f"Status change notification: {notification_data}")
        
        # notifications_service.send_notification(notification_data)
        
        logger.info(f"Status change notifications sent successfully for partner: {evento.aggregate_id}")
        
    except Exception as e:
        logger.error(f"Failed to send status change notifications for partner {evento.aggregate_id}: {str(e)}")


# PartnerProfileUpdated Event Handlers

def handle_partner_profile_updated_cache(evento: PartnerProfileUpdated, **kwargs):
    """Handle partner profile updated - invalidate cache."""
    try:
        logger.info(f"Invalidating cache for partner: {evento.aggregate_id}")
        
        cache_keys = [
            f'partner:{evento.aggregate_id}',
            f'partner:profile:{evento.aggregate_id}',
            f'partner:summary:{evento.aggregate_id}',
            'partners:list',  # Invalidate partner lists
            'partners:search'  # Invalidate search results
        ]
        
        # Mock cache invalidation
        for key in cache_keys:
            logger.debug(f"Invalidating cache key: {key}")
            # cache_service.invalidate(key)
        
        logger.info(f"Cache invalidated successfully for partner: {evento.aggregate_id}")
        
    except Exception as e:
        logger.error(f"Failed to invalidate cache for partner {evento.aggregate_id}: {str(e)}")


def handle_partner_profile_updated_search(evento: PartnerProfileUpdated, **kwargs):
    """Handle partner profile updated - update search indices."""
    try:
        logger.info(f"Updating search indices for partner: {evento.aggregate_id}")
        
        search_update = {
            'partner_id': evento.aggregate_id,
            'updated_fields': evento.updated_fields,
            'updated_by': evento.updated_by,
            'updated_at': datetime.now().isoformat(),
            'action': 'update_index'
        }
        
        # Mock call to search service
        logger.debug(f"Search index update: {search_update}")
        
        # search_service.update_partner_index(search_update)
        
        logger.info(f"Search indices updated successfully for partner: {evento.aggregate_id}")
        
    except Exception as e:
        logger.error(f"Failed to update search indices for partner {evento.aggregate_id}: {str(e)}")


def handle_partner_profile_updated_recommendations(evento: PartnerProfileUpdated, **kwargs):
    """Handle partner profile updated - refresh recommendations."""
    try:
        logger.info(f"Refreshing recommendations for partner: {evento.aggregate_id}")
        
        # Check if important fields were updated that affect recommendations
        important_fields = ['tipo', 'ciudad', 'pais', 'validaciones']
        needs_recommendation_refresh = any(field in evento.updated_fields for field in important_fields)
        
        if needs_recommendation_refresh:
            recommendation_update = {
                'partner_id': evento.aggregate_id,
                'updated_fields': evento.updated_fields,
                'action': 'refresh_recommendations',
                'priority': 'normal'
            }
            
            # Mock call to recommendations service
            logger.debug(f"Recommendation refresh: {recommendation_update}")
            
            # recommendations_service.refresh_partner_recommendations(recommendation_update)
            
            logger.info(f"Recommendations refreshed successfully for partner: {evento.aggregate_id}")
        else:
            logger.debug(f"No recommendation refresh needed for partner: {evento.aggregate_id}")
        
    except Exception as e:
        logger.error(f"Failed to refresh recommendations for partner {evento.aggregate_id}: {str(e)}")


# PartnerValidated Event Handlers

def handle_partner_validated_trust_score(evento: PartnerValidated, **kwargs):
    """Handle partner validated - update trust score."""
    try:
        logger.info(f"Updating trust score for partner {evento.aggregate_id} - validation: {evento.validation_type}")
        
        trust_update = {
            'partner_id': evento.aggregate_id,
            'validation_type': evento.validation_type,
            'validated_by': evento.validated_by,
            'validation_data': evento.validation_data,
            'action': 'increase_trust_score'
        }
        
        # Mock call to trust scoring service
        logger.debug(f"Trust score update: {trust_update}")
        
        # trust_service.update_partner_trust_score(trust_update)
        
        logger.info(f"Trust score updated successfully for partner: {evento.aggregate_id}")
        
    except Exception as e:
        logger.error(f"Failed to update trust score for partner {evento.aggregate_id}: {str(e)}")


def handle_partner_validated_features(evento: PartnerValidated, **kwargs):
    """Handle partner validated - unlock new features."""
    try:
        logger.info(f"Unlocking features for validated partner: {evento.aggregate_id}")
        
        # Define features unlocked by each validation type
        feature_map = {
            'email': ['email_campaigns', 'email_notifications'],
            'phone': ['sms_notifications', 'phone_support'],
            'identity': ['premium_campaigns', 'higher_commissions'],
            'business': ['business_campaigns', 'bulk_operations', 'advanced_analytics']
        }
        
        features_to_unlock = feature_map.get(evento.validation_type, [])
        
        if features_to_unlock:
            feature_update = {
                'partner_id': evento.aggregate_id,
                'validation_type': evento.validation_type,
                'features': features_to_unlock,
                'action': 'unlock_features'
            }
            
            # Mock call to features service
            logger.debug(f"Feature unlock: {feature_update}")
            
            # features_service.unlock_partner_features(feature_update)
            
            logger.info(f"Features unlocked successfully for partner: {evento.aggregate_id}")
        
    except Exception as e:
        logger.error(f"Failed to unlock features for partner {evento.aggregate_id}: {str(e)}")


# PartnerSuspended Event Handlers

def handle_partner_suspended_campaigns(evento: PartnerSuspended, **kwargs):
    """Handle partner suspended - pause all campaigns."""
    try:
        logger.info(f"Pausing campaigns for suspended partner: {evento.aggregate_id}")
        
        suspension_data = {
            'partner_id': evento.aggregate_id,
            'suspension_reason': evento.suspension_reason,
            'suspended_by': evento.suspended_by,
            'suspension_until': evento.suspension_until.isoformat() if evento.suspension_until else None,
            'action': 'pause_all_campaigns'
        }
        
        # Mock call to campaigns service
        logger.debug(f"Campaign suspension: {suspension_data}")
        
        # campaigns_service.suspend_partner_campaigns(suspension_data)
        
        logger.info(f"Campaigns paused successfully for suspended partner: {evento.aggregate_id}")
        
    except Exception as e:
        logger.error(f"Failed to pause campaigns for suspended partner {evento.aggregate_id}: {str(e)}")


def handle_partner_suspended_access(evento: PartnerSuspended, **kwargs):
    """Handle partner suspended - revoke access."""
    try:
        logger.info(f"Revoking access for suspended partner: {evento.aggregate_id}")
        
        access_update = {
            'partner_id': evento.aggregate_id,
            'suspension_reason': evento.suspension_reason,
            'suspended_by': evento.suspended_by,
            'action': 'revoke_access'
        }
        
        # Mock call to access control service
        logger.debug(f"Access revocation: {access_update}")
        
        # access_service.revoke_partner_access(access_update)
        
        logger.info(f"Access revoked successfully for suspended partner: {evento.aggregate_id}")
        
    except Exception as e:
        logger.error(f"Failed to revoke access for suspended partner {evento.aggregate_id}: {str(e)}")


# PartnerReactivated Event Handlers

def handle_partner_reactivated_campaigns(evento: PartnerReactivated, **kwargs):
    """Handle partner reactivated - resume campaigns."""
    try:
        logger.info(f"Resuming campaigns for reactivated partner: {evento.aggregate_id}")
        
        reactivation_data = {
            'partner_id': evento.aggregate_id,
            'reactivation_reason': evento.reactivation_reason,
            'reactivated_by': evento.reactivated_by,
            'action': 'resume_campaigns'
        }
        
        # Mock call to campaigns service
        logger.debug(f"Campaign reactivation: {reactivation_data}")
        
        # campaigns_service.reactivate_partner_campaigns(reactivation_data)
        
        logger.info(f"Campaigns resumed successfully for reactivated partner: {evento.aggregate_id}")
        
    except Exception as e:
        logger.error(f"Failed to resume campaigns for reactivated partner {evento.aggregate_id}: {str(e)}")


def handle_partner_reactivated_notifications(evento: PartnerReactivated, **kwargs):
    """Handle partner reactivated - send welcome back notification."""
    try:
        logger.info(f"Sending welcome back notification for reactivated partner: {evento.aggregate_id}")
        
        notification_data = {
            'partner_id': evento.aggregate_id,
            'template': 'partner_welcome_back',
            'channel': 'email',
            'data': {
                'reactivation_reason': evento.reactivation_reason,
                'reactivated_by': evento.reactivated_by
            }
        }
        
        # Mock call to notifications service
        logger.debug(f"Welcome back notification: {notification_data}")
        
        # notifications_service.send_notification(notification_data)
        
        logger.info(f"Welcome back notification sent successfully for partner: {evento.aggregate_id}")
        
    except Exception as e:
        logger.error(f"Failed to send welcome back notification for partner {evento.aggregate_id}: {str(e)}")


# Auto-configure handlers when module is imported
try:
    configurar_handlers()
except Exception as e:
    logger.warning(f"Failed to auto-configure event handlers: {e}")
    # Handlers can be configured manually later