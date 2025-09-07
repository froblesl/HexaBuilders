"""
Get Campaign Profile 360 query implementation for HexaBuilders.
Provides comprehensive campaign information including performance metrics and insights.
"""

import logging
from dataclasses import dataclass
from typing import Optional, Dict, Any

from .....seedwork.aplicacion.queries import ejecutar_query
from .....seedwork.infraestructura.uow import UnitOfWork
from .....seedwork.dominio.excepciones import DomainException
from .base import QueryCampaign, QueryResultCampaign

logger = logging.getLogger(__name__)


@dataclass
class ObtenerCampaignProfile360(QueryCampaign):
    """Query to get comprehensive campaign profile with analytics."""
    campaign_id: str
    include_partner_data: bool = False
    include_recommendations: bool = False


@dataclass
class RespuestaCampaignProfile360(QueryResultCampaign):
    """Response for GetCampaignProfile360 query."""
    campaign_data: Optional[Dict[str, Any]] = None
    performance_metrics: Optional[Dict[str, Any]] = None
    partner_data: Optional[Dict[str, Any]] = None
    targeting_analysis: Optional[Dict[str, Any]] = None
    recommendations: Optional[Dict[str, Any]] = None
    insights: Optional[Dict[str, Any]] = None


@ejecutar_query.register
def handle_obtener_campaign_profile_360(query: ObtenerCampaignProfile360) -> RespuestaCampaignProfile360:
    """
    Handle GetCampaignProfile360 query.
    """
    logger.info(f"Executing GetCampaignProfile360 query for campaign: {query.campaign_id}")
    
    try:
        # Validate input
        if not query.campaign_id:
            raise DomainException("Campaign ID is required")
        
        # Use Unit of Work for read operations
        with UnitOfWork() as uow:
            campaign_repo = uow.campaigns
            partner_repo = uow.partners
            
            # Get campaign
            campaign = campaign_repo.obtener_por_id(query.campaign_id)
            if not campaign:
                logger.warning(f"Campaign not found: {query.campaign_id}")
                return RespuestaCampaignProfile360()
            
            # Build comprehensive campaign data
            campaign_data = {
                'id': campaign.id,
                'nombre': campaign.nombre.value,
                'descripcion': campaign.descripcion.value,
                'partner_id': campaign.partner_id,
                'tipo': campaign.tipo.value,
                'status': campaign.status.value,
                'presupuesto': {
                    'amount': str(campaign.presupuesto.amount),
                    'currency': campaign.presupuesto.currency
                },
                'fecha_rango': {
                    'start_date': campaign.fecha_rango.start_date.isoformat(),
                    'end_date': campaign.fecha_rango.end_date.isoformat(),
                    'duration_days': campaign.fecha_rango.duration_in_days(),
                    'is_expired': campaign.fecha_rango.is_expired()
                },
                'approval': {
                    'is_approved': campaign.approval.is_approved,
                    'approved_by': campaign.approval.approved_by,
                    'approved_at': campaign.approval.approved_at.isoformat() if campaign.approval.approved_at else None,
                    'rejection_reason': campaign.approval.rejection_reason
                },
                'timestamps': {
                    'created_at': campaign.created_at.isoformat(),
                    'updated_at': campaign.updated_at.isoformat()
                },
                'version': campaign.version
            }
            
            # Build performance metrics
            performance_metrics = {
                'impressions': campaign.metricas.impressions,
                'clicks': campaign.metricas.clicks,
                'conversions': campaign.metricas.conversions,
                'spend': str(campaign.metricas.spend),
                'revenue': str(campaign.metricas.revenue),
                'calculated_metrics': {
                    'click_through_rate': campaign.metricas.click_through_rate(),
                    'conversion_rate': campaign.metricas.conversion_rate(),
                    'cost_per_click': str(campaign.metricas.cost_per_click()),
                    'cost_per_conversion': str(campaign.metricas.cost_per_conversion()),
                    'return_on_ad_spend': str(campaign.metricas.return_on_ad_spend()),
                    'budget_utilization': campaign.porcentaje_presupuesto_usado()
                }
            }
            
            # Build targeting analysis
            targeting_analysis = {
                'countries': campaign.targeting.countries,
                'age_range': campaign.targeting.age_range,
                'interests': campaign.targeting.interests,
                'keywords': campaign.targeting.keywords,
                'targeting_breadth': {
                    'country_count': len(campaign.targeting.countries),
                    'interest_count': len(campaign.targeting.interests),
                    'keyword_count': len(campaign.targeting.keywords),
                    'has_age_targeting': campaign.targeting.age_range is not None
                }
            }
            
            # Get partner data if requested
            partner_data = None
            if query.include_partner_data:
                partner = partner_repo.obtener_por_id(campaign.partner_id)
                if partner:
                    partner_data = {
                        'id': partner.id,
                        'nombre': partner.nombre.value,
                        'email': partner.email.value,
                        'tipo': partner.tipo.value,
                        'status': partner.status.value,
                        'validation_data': {
                            'email_validated': partner.validation_data.email_validated,
                            'phone_validated': partner.validation_data.phone_validated,
                            'identity_validated': partner.validation_data.identity_validated,
                            'business_validated': partner.validation_data.business_validated,
                            'validation_percentage': partner.validation_data.validation_percentage()
                        },
                        'metrics': {
                            'total_campaigns': partner.metrics.total_campaigns,
                            'completed_campaigns': partner.metrics.completed_campaigns,
                            'success_rate': partner.metrics.success_rate,
                            'total_commissions': partner.metrics.total_commissions,
                            'average_rating': partner.metrics.average_rating
                        }
                    }
            
            # Generate insights
            insights = _generate_campaign_insights(campaign)
            
            # Generate recommendations if requested
            recommendations = None
            if query.include_recommendations:
                recommendations = _generate_campaign_recommendations(campaign)
            
            logger.info(f"Campaign profile 360 retrieved successfully: {campaign.id}")
            
            return RespuestaCampaignProfile360(
                campaign_data=campaign_data,
                performance_metrics=performance_metrics,
                partner_data=partner_data,
                targeting_analysis=targeting_analysis,
                recommendations=recommendations,
                insights=insights
            )
    
    except Exception as e:
        logger.error(f"Failed to get campaign profile 360 {query.campaign_id}: {str(e)}")
        raise


def _generate_campaign_insights(campaign) -> Dict[str, Any]:
    """Generate insights based on campaign data."""
    
    insights = {
        'status_insights': [],
        'performance_insights': [],
        'targeting_insights': [],
        'budget_insights': []
    }
    
    # Status insights
    if campaign.status.value == 'DRAFT':
        insights['status_insights'].append("Campaign is in draft status and needs approval before activation")
        
        if not campaign.approval.is_approved:
            insights['status_insights'].append("Campaign requires approval before it can be activated")
    
    elif campaign.status.value == 'ACTIVE':
        if campaign.esta_vencida():
            insights['status_insights'].append("Campaign has expired and should be completed")
        elif campaign.fecha_rango.end_date:
            days_remaining = (campaign.fecha_rango.end_date - campaign.fecha_rango.start_date).days
            insights['status_insights'].append(f"Campaign has {days_remaining} days remaining")
    
    # Performance insights
    if campaign.metricas.impressions > 0:
        ctr = campaign.metricas.click_through_rate()
        if ctr < 0.01:  # Less than 1% CTR
            insights['performance_insights'].append("Click-through rate is below industry average (1%)")
        elif ctr > 0.05:  # Greater than 5% CTR
            insights['performance_insights'].append("Click-through rate is above industry average - great performance!")
        
        if campaign.metricas.conversions > 0:
            conversion_rate = campaign.metricas.conversion_rate()
            if conversion_rate > 0.1:  # Greater than 10% conversion rate
                insights['performance_insights'].append("Excellent conversion rate - campaign is highly effective")
    else:
        insights['performance_insights'].append("No performance data available yet")
    
    # Budget insights
    budget_used = campaign.porcentaje_presupuesto_usado()
    if budget_used > 0.8:  # More than 80% budget used
        insights['budget_insights'].append("Campaign has used more than 80% of budget")
    elif budget_used > 0.5:  # More than 50% budget used
        insights['budget_insights'].append("Campaign has used more than 50% of budget")
    
    # Targeting insights
    if len(campaign.targeting.countries) > 20:
        insights['targeting_insights'].append("Broad geographic targeting may reduce campaign effectiveness")
    elif len(campaign.targeting.countries) == 0:
        insights['targeting_insights'].append("No geographic targeting set - campaign will run globally")
    
    if len(campaign.targeting.interests) > 15:
        insights['targeting_insights'].append("Many interest targets - consider narrowing focus for better performance")
    
    return insights


def _generate_campaign_recommendations(campaign) -> Dict[str, Any]:
    """Generate recommendations based on campaign performance and setup."""
    
    recommendations = {
        'optimization_recommendations': [],
        'targeting_recommendations': [],
        'budget_recommendations': [],
        'creative_recommendations': []
    }
    
    # Performance-based recommendations
    if campaign.metricas.impressions > 1000:
        ctr = campaign.metricas.click_through_rate()
        if ctr < 0.01:
            recommendations['optimization_recommendations'].append({
                'type': 'improve_ctr',
                'priority': 'high',
                'suggestion': 'Consider refreshing ad creative or adjusting targeting to improve click-through rate',
                'expected_impact': 'Increase CTR by 20-50%'
            })
        
        if campaign.metricas.conversions == 0 and campaign.metricas.clicks > 50:
            recommendations['optimization_recommendations'].append({
                'type': 'improve_conversion',
                'priority': 'high', 
                'suggestion': 'Review landing page experience and conversion tracking setup',
                'expected_impact': 'Establish conversion tracking and optimize funnel'
            })
    
    # Budget recommendations
    budget_used = campaign.porcentaje_presupuesto_usado()
    if budget_used > 0.9 and campaign.status.value == 'ACTIVE':
        recommendations['budget_recommendations'].append({
            'type': 'increase_budget',
            'priority': 'medium',
            'suggestion': 'Consider increasing budget to maintain campaign performance',
            'expected_impact': 'Extend campaign reach and duration'
        })
    
    # Targeting recommendations
    if len(campaign.targeting.countries) > 10:
        recommendations['targeting_recommendations'].append({
            'type': 'narrow_targeting',
            'priority': 'medium',
            'suggestion': 'Focus on top-performing countries to improve efficiency',
            'expected_impact': 'Improve cost-per-conversion by 15-30%'
        })
    
    if campaign.targeting.age_range and (campaign.targeting.age_range[1] - campaign.targeting.age_range[0]) > 40:
        recommendations['targeting_recommendations'].append({
            'type': 'refine_age_targeting',
            'priority': 'low',
            'suggestion': 'Narrow age range to focus on most relevant audience segments',
            'expected_impact': 'Improve relevance and engagement rates'
        })
    
    return recommendations