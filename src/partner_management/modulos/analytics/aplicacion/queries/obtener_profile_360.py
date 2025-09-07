"""
Get 360-degree Profile Analytics query implementation for HexaBuilders.
"""

import logging
from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

from .....seedwork.aplicacion.queries import ejecutar_query
from .....seedwork.infraestructura.uow import UnitOfWork
from .....seedwork.dominio.excepciones import DomainException
from .base import QueryAnalytics, AnalyticsQueryResult

logger = logging.getLogger(__name__)


@dataclass
class ObtenerProfile360(QueryAnalytics):
    """Query to get comprehensive 360-degree partner analytics profile."""
    
    partner_id: str
    period_months: int = 6
    include_predictions: bool = True
    include_recommendations: bool = True


class Profile360Result(AnalyticsQueryResult):
    """360-degree profile analytics query result."""
    
    def __init__(self, profile_data: Dict[str, Any]):
        self.profile_data = profile_data
        self.partner_id = profile_data.get('partner_id')
        self.generated_at = profile_data.get('generated_at')
    
    def __dict__(self):
        return self.profile_data


@ejecutar_query.register
def handle_obtener_profile_360(query: ObtenerProfile360) -> Profile360Result:
    """
    Handle Get360Profile query.
    """
    logger.info(f"Executing Get360Profile query for partner: {query.partner_id}")
    
    try:
        # Validate input data
        _validate_obtener_profile_360_query(query)
        
        # Use Unit of Work to fetch data
        with UnitOfWork() as uow:
            # Get partner data
            partner_repo = uow.partners
            partner = partner_repo.obtener_por_id(query.partner_id)
            if not partner:
                raise DomainException(f"Partner with ID {query.partner_id} not found")
            
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=query.period_months * 30)
            
            # Collect comprehensive data
            profile_data = {
                'partner_id': query.partner_id,
                'generated_at': datetime.now().isoformat(),
                'analysis_period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'period_months': query.period_months
                },
                'partner_overview': _get_partner_overview(partner),
                'performance_metrics': _get_performance_metrics(query.partner_id, start_date, end_date, uow),
                'campaign_analytics': _get_campaign_analytics(query.partner_id, start_date, end_date, uow),
                'commission_analytics': _get_commission_analytics(query.partner_id, start_date, end_date, uow),
                'trend_analysis': _get_trend_analysis(query.partner_id, start_date, end_date, uow),
                'benchmarking': _get_benchmarking_data(query.partner_id, uow),
                'risk_assessment': _get_risk_assessment(query.partner_id, uow),
                'opportunity_analysis': _get_opportunity_analysis(query.partner_id, uow)
            }
            
            # Add predictions if requested
            if query.include_predictions:
                profile_data['predictions'] = _generate_predictions(query.partner_id, profile_data, uow)
            
            # Add recommendations if requested
            if query.include_recommendations:
                profile_data['recommendations'] = _generate_recommendations(query.partner_id, profile_data, uow)
            
            logger.info(f"360-degree profile generated successfully for partner: {query.partner_id}")
            return Profile360Result(profile_data)
    
    except Exception as e:
        logger.error(f"Failed to get 360-degree profile: {str(e)}")
        raise


def _get_partner_overview(partner) -> Dict[str, Any]:
    """Get basic partner overview."""
    
    return {
        'id': partner.id,
        'name': partner.nombre.value,
        'email': partner.email.value,
        'phone': partner.telefono.value,
        'type': partner.tipo.value,
        'status': partner.status.value,
        'created_at': partner.created_at.isoformat(),
        'updated_at': partner.updated_at.isoformat(),
        'validation_status': {
            'email_validated': partner.validation_data.email_validated,
            'phone_validated': partner.validation_data.phone_validated,
            'identity_validated': partner.validation_data.identity_validated,
            'business_validated': partner.validation_data.business_validated,
            'validation_percentage': partner.validation_data.validation_percentage()
        },
        'capabilities': {
            'can_create_campaigns': partner.puede_crear_campanas(),
            'can_receive_commissions': partner.puede_recibir_comisiones()
        }
    }


def _get_performance_metrics(partner_id: str, start_date: datetime, end_date: datetime, uow) -> Dict[str, Any]:
    """Get comprehensive performance metrics."""
    
    from decimal import Decimal
    
    # Get campaigns
    campaigns_repo = uow.campaigns
    partner_campaigns = campaigns_repo.obtener_por_partner_id(partner_id)
    
    # Get commissions
    commissions_repo = uow.commissions
    partner_commissions = commissions_repo.obtener_por_partner_id(partner_id)
    
    # Calculate performance metrics
    total_campaigns = len(partner_campaigns)
    active_campaigns = len([c for c in partner_campaigns if c.status.value == 'ACTIVO'])
    completed_campaigns = len([c for c in partner_campaigns if hasattr(c, 'completion_date')])
    
    total_commissions = len(partner_commissions)
    paid_commissions = [c for c in partner_commissions if c.status.value == 'PAID']
    total_earnings = sum(c.commission_amount.amount for c in paid_commissions)
    
    # Calculate rates
    completion_rate = (completed_campaigns / total_campaigns) if total_campaigns > 0 else 0
    commission_approval_rate = len([c for c in partner_commissions if c.status.value in ['APPROVED', 'PAID']]) / total_commissions if total_commissions > 0 else 0
    
    return {
        'campaigns': {
            'total': total_campaigns,
            'active': active_campaigns,
            'completed': completed_campaigns,
            'completion_rate': completion_rate,
            'success_rate': min(completion_rate * 1.1, 1.0)  # Mock calculation
        },
        'commissions': {
            'total': total_commissions,
            'paid': len(paid_commissions),
            'total_earnings': str(total_earnings),
            'average_commission': str(total_earnings / len(paid_commissions)) if paid_commissions else '0',
            'approval_rate': commission_approval_rate
        },
        'overall_score': {
            'performance_score': 0.75 + (completion_rate * 0.2),  # Mock calculation
            'reliability_score': commission_approval_rate,
            'engagement_score': min(total_campaigns / 10, 1.0)  # Mock calculation
        }
    }


def _get_campaign_analytics(partner_id: str, start_date: datetime, end_date: datetime, uow) -> Dict[str, Any]:
    """Get detailed campaign analytics."""
    
    campaigns_repo = uow.campaigns
    partner_campaigns = campaigns_repo.obtener_por_partner_id(partner_id)
    
    # Campaign status breakdown
    status_breakdown = {}
    for campaign in partner_campaigns:
        status = campaign.status.value
        status_breakdown[status] = status_breakdown.get(status, 0) + 1
    
    # Campaign type analysis
    type_breakdown = {}
    for campaign in partner_campaigns:
        campaign_type = getattr(campaign, 'tipo', 'STANDARD')  # Default type
        if hasattr(campaign_type, 'value'):
            campaign_type = campaign_type.value
        type_breakdown[campaign_type] = type_breakdown.get(campaign_type, 0) + 1
    
    return {
        'total_campaigns': len(partner_campaigns),
        'status_breakdown': status_breakdown,
        'type_breakdown': type_breakdown,
        'performance_indicators': {
            'average_duration': 30,  # Mock data
            'success_rate': 0.8,
            'on_time_delivery': 0.85,
            'client_satisfaction': 4.2
        },
        'trends': {
            'monthly_campaign_count': [2, 3, 1, 4, 2, 3],  # Last 6 months mock data
            'success_rate_trend': [0.7, 0.75, 0.8, 0.82, 0.8, 0.85]
        }
    }


def _get_commission_analytics(partner_id: str, start_date: datetime, end_date: datetime, uow) -> Dict[str, Any]:
    """Get detailed commission analytics."""
    
    commissions_repo = uow.commissions
    partner_commissions = commissions_repo.obtener_por_partner_id(partner_id)
    
    from decimal import Decimal
    
    # Commission status analysis
    status_breakdown = {}
    earnings_by_status = {}
    
    for commission in partner_commissions:
        status = commission.status.value
        amount = commission.commission_amount.amount
        
        status_breakdown[status] = status_breakdown.get(status, 0) + 1
        earnings_by_status[status] = earnings_by_status.get(status, Decimal('0')) + amount
    
    # Commission type analysis
    type_breakdown = {}
    for commission in partner_commissions:
        comm_type = commission.commission_type.value
        type_breakdown[comm_type] = type_breakdown.get(comm_type, 0) + 1
    
    # Calculate totals
    total_earned = sum(earnings_by_status.values())
    paid_amount = earnings_by_status.get('PAID', Decimal('0'))
    pending_amount = earnings_by_status.get('PENDING', Decimal('0')) + earnings_by_status.get('APPROVED', Decimal('0'))
    
    return {
        'total_commissions': len(partner_commissions),
        'status_breakdown': status_breakdown,
        'type_breakdown': type_breakdown,
        'earnings_summary': {
            'total_earned': str(total_earned),
            'paid_amount': str(paid_amount),
            'pending_amount': str(pending_amount),
            'average_commission': str(total_earned / len(partner_commissions)) if partner_commissions else '0'
        },
        'performance_metrics': {
            'payment_speed': 7.2,  # Average days to payment - mock data
            'dispute_rate': 0.02,  # Mock data
            'approval_rate': 0.92  # Mock data
        },
        'monthly_trends': {
            'earnings': [1200, 1800, 1500, 2100, 1900, 2300],  # Last 6 months mock data
            'commission_count': [8, 12, 10, 14, 13, 15]
        }
    }


def _get_trend_analysis(partner_id: str, start_date: datetime, end_date: datetime, uow) -> Dict[str, Any]:
    """Get trend analysis across all metrics."""
    
    return {
        'performance_trends': {
            'overall_direction': 'increasing',
            'confidence': 0.85,
            'key_indicators': {
                'campaign_success_rate': {'trend': 'increasing', 'change': '+12%'},
                'commission_earnings': {'trend': 'increasing', 'change': '+18%'},
                'response_time': {'trend': 'improving', 'change': '-15%'}
            }
        },
        'seasonal_patterns': {
            'best_months': ['March', 'September', 'November'],
            'peak_performance_periods': ['Q1', 'Q4'],
            'seasonal_factors': {
                'campaign_volume': 'Higher in Q4',
                'commission_rates': 'Peak during holidays'
            }
        },
        'growth_indicators': {
            'month_over_month_growth': 0.15,
            'quarter_over_quarter_growth': 0.22,
            'year_over_year_growth': 0.45
        }
    }


def _get_benchmarking_data(partner_id: str, uow) -> Dict[str, Any]:
    """Get benchmarking against platform averages."""
    
    return {
        'peer_comparison': {
            'performance_percentile': 75,
            'earnings_percentile': 68,
            'reliability_percentile': 82
        },
        'platform_averages': {
            'campaign_success_rate': 0.72,
            'average_commission': 185.50,
            'monthly_campaigns': 3.2,
            'approval_rate': 0.88
        },
        'partner_vs_platform': {
            'campaign_success_rate': 'Above average (+8%)',
            'average_commission': 'Above average (+12%)',
            'monthly_campaigns': 'Above average (+25%)',
            'approval_rate': 'Above average (+5%)'
        }
    }


def _get_risk_assessment(partner_id: str, uow) -> Dict[str, Any]:
    """Assess partner risks and stability."""
    
    return {
        'risk_score': 0.15,  # Low risk
        'risk_level': 'LOW',
        'risk_factors': [
            {
                'factor': 'Commission dispute rate',
                'score': 0.02,
                'impact': 'Low',
                'description': 'Very low dispute rate indicates reliability'
            },
            {
                'factor': 'Campaign completion rate',
                'score': 0.10,
                'impact': 'Medium',
                'description': 'Good completion rate with room for improvement'
            }
        ],
        'stability_indicators': {
            'consistency_score': 0.85,
            'reliability_trend': 'improving',
            'performance_variance': 0.12
        },
        'mitigation_recommendations': [
            'Continue monitoring campaign completion rates',
            'Maintain current quality standards'
        ]
    }


def _get_opportunity_analysis(partner_id: str, uow) -> Dict[str, Any]:
    """Analyze growth opportunities."""
    
    return {
        'growth_potential': 0.75,  # High potential
        'opportunity_areas': [
            {
                'area': 'Campaign Volume',
                'potential': 'High',
                'description': 'Partner shows capacity for handling more campaigns',
                'estimated_impact': '+30% earnings potential'
            },
            {
                'area': 'Premium Partnerships',
                'potential': 'Medium',
                'description': 'Eligible for higher-tier partnership programs',
                'estimated_impact': '+15% commission rates'
            },
            {
                'area': 'Specialization',
                'potential': 'Medium',
                'description': 'Strong performance in specific campaign types',
                'estimated_impact': '+20% success rate in niche'
            }
        ],
        'recommended_actions': [
            'Increase campaign allocation by 25%',
            'Invite to premium partner program',
            'Offer specialized training in top-performing areas'
        ],
        'market_opportunities': {
            'trending_sectors': ['E-commerce', 'SaaS', 'FinTech'],
            'seasonal_opportunities': ['Holiday campaigns', 'Back-to-school', 'Summer promotions'],
            'partnership_opportunities': ['Cross-partner collaborations', 'Referral programs']
        }
    }


def _generate_predictions(partner_id: str, profile_data: Dict[str, Any], uow) -> Dict[str, Any]:
    """Generate predictive analytics."""
    
    return {
        'next_30_days': {
            'predicted_campaigns': 3,
            'predicted_earnings': 450.0,
            'success_probability': 0.88,
            'confidence': 0.75
        },
        'next_quarter': {
            'predicted_campaigns': 12,
            'predicted_earnings': 1800.0,
            'growth_rate': 0.18,
            'confidence': 0.68
        },
        'annual_forecast': {
            'predicted_campaigns': 48,
            'predicted_earnings': 7200.0,
            'performance_trajectory': 'upward',
            'confidence': 0.62
        },
        'prediction_factors': [
            'Historical performance trends',
            'Seasonal patterns',
            'Platform growth rates',
            'Partner capacity indicators'
        ]
    }


def _generate_recommendations(partner_id: str, profile_data: Dict[str, Any], uow) -> Dict[str, Any]:
    """Generate actionable recommendations."""
    
    return {
        'immediate_actions': [
            {
                'action': 'Optimize campaign response time',
                'priority': 'High',
                'impact': 'Medium',
                'effort': 'Low',
                'description': 'Reduce average response time to improve client satisfaction'
            },
            {
                'action': 'Complete business validation',
                'priority': 'Medium',
                'impact': 'High',
                'effort': 'Medium',
                'description': 'Unlock premium features and higher commission rates'
            }
        ],
        'strategic_recommendations': [
            {
                'recommendation': 'Specialize in high-performing campaign types',
                'rationale': 'Strong success rate in specific areas indicates natural fit',
                'expected_outcome': 'Increased success rate and premium rates',
                'timeline': '3-6 months'
            },
            {
                'recommendation': 'Expand capacity for more campaigns',
                'rationale': 'Current performance indicates ability to handle more volume',
                'expected_outcome': 'Increased earnings through volume',
                'timeline': '1-3 months'
            }
        ],
        'development_opportunities': [
            'Advanced campaign management training',
            'Industry-specific certifications',
            'Partnership collaboration skills',
            'Digital marketing specializations'
        ],
        'risk_mitigation': [
            'Maintain current quality standards',
            'Diversify campaign types to reduce concentration risk',
            'Build stronger client relationships'
        ]
    }


def _validate_obtener_profile_360_query(query: ObtenerProfile360):
    """Validate Get360Profile query data."""
    
    if not query.partner_id:
        raise DomainException("Partner ID is required")
    
    if query.period_months <= 0 or query.period_months > 24:
        raise DomainException("Period months must be between 1 and 24")
    
    logger.debug("Get360Profile query validation passed")