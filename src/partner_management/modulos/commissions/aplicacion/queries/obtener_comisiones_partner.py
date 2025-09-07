"""
Get Partner Commissions query implementation for HexaBuilders.
"""

import logging
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime
from decimal import Decimal

from .....seedwork.aplicacion.queries import ejecutar_query
from .....seedwork.infraestructura.uow import UnitOfWork
from .....seedwork.dominio.excepciones import DomainException
from .base import QueryCommission, CommissionQueryResult

logger = logging.getLogger(__name__)


@dataclass
class ObtenerComisionesPartner(QueryCommission):
    """Query to get commissions for a specific partner with analytics."""
    
    partner_id: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: Optional[str] = None
    include_analytics: bool = True


class PartnerCommissionsResult(CommissionQueryResult):
    """Partner commissions query result with analytics."""
    
    def __init__(self, partner_id: str, commissions_data: List[Dict[str, Any]], analytics: Dict[str, Any]):
        self.partner_id = partner_id
        self.commissions = commissions_data
        self.analytics = analytics
        self.count = len(commissions_data)


@ejecutar_query.register
def handle_obtener_comisiones_partner(query: ObtenerComisionesPartner) -> PartnerCommissionsResult:
    """
    Handle GetPartnerCommissions query.
    """
    logger.info(f"Executing GetPartnerCommissions query for partner: {query.partner_id}")
    
    try:
        # Validate input data
        _validate_obtener_comisiones_partner_query(query)
        
        # Use Unit of Work to fetch data
        with UnitOfWork() as uow:
            repo = uow.commissions
            partner_repo = uow.partners
            
            # Verify partner exists
            partner = partner_repo.obtener_por_id(query.partner_id)
            if not partner:
                raise DomainException(f"Partner with ID {query.partner_id} not found")
            
            # Build filters
            filters = {'partner_id': query.partner_id}
            if query.status:
                filters['status'] = query.status
            if query.start_date:
                filters['start_date'] = query.start_date
            if query.end_date:
                filters['end_date'] = query.end_date
            
            # Get partner commissions
            commissions = repo.obtener_todos_con_filtros(filters=filters)
            
            # Convert to summary format
            commissions_data = [commission.get_summary() for commission in commissions]
            
            # Calculate analytics if requested
            analytics = {}
            if query.include_analytics:
                analytics = _calculate_commission_analytics(commissions)
            
            logger.info(f"Retrieved {len(commissions)} commissions for partner {query.partner_id}")
            return PartnerCommissionsResult(query.partner_id, commissions_data, analytics)
    
    except Exception as e:
        logger.error(f"Failed to get partner commissions: {str(e)}")
        raise


def _calculate_commission_analytics(commissions) -> Dict[str, Any]:
    """Calculate analytics for partner commissions."""
    
    if not commissions:
        return {
            'total_commissions': 0,
            'total_earned': '0.00',
            'total_paid': '0.00',
            'total_pending': '0.00',
            'average_commission': '0.00',
            'status_breakdown': {},
            'type_breakdown': {},
            'monthly_summary': {}
        }
    
    total_earned = Decimal('0')
    total_paid = Decimal('0')
    total_pending = Decimal('0')
    status_counts = {}
    type_counts = {}
    monthly_summary = {}
    
    for commission in commissions:
        amount = commission.commission_amount.amount
        status = commission.status.value
        comm_type = commission.commission_type.value
        
        # Total earnings
        total_earned += amount
        
        # Status-based totals
        if status == 'PAID':
            total_paid += amount
        elif status in ['PENDING', 'APPROVED']:
            total_pending += amount
        
        # Status breakdown
        status_counts[status] = status_counts.get(status, 0) + 1
        
        # Type breakdown
        type_counts[comm_type] = type_counts.get(comm_type, 0) + 1
        
        # Monthly summary
        month_key = commission.created_at.strftime('%Y-%m')
        if month_key not in monthly_summary:
            monthly_summary[month_key] = {'count': 0, 'total_amount': Decimal('0')}
        monthly_summary[month_key]['count'] += 1
        monthly_summary[month_key]['total_amount'] += amount
    
    # Convert monthly summary amounts to strings
    for month in monthly_summary:
        monthly_summary[month]['total_amount'] = str(monthly_summary[month]['total_amount'])
    
    average_commission = total_earned / len(commissions) if commissions else Decimal('0')
    
    return {
        'total_commissions': len(commissions),
        'total_earned': str(total_earned),
        'total_paid': str(total_paid),
        'total_pending': str(total_pending),
        'average_commission': str(average_commission),
        'status_breakdown': status_counts,
        'type_breakdown': type_counts,
        'monthly_summary': monthly_summary
    }


def _validate_obtener_comisiones_partner_query(query: ObtenerComisionesPartner):
    """Validate GetPartnerCommissions query data."""
    
    if not query.partner_id:
        raise DomainException("Partner ID is required")
    
    if query.start_date and query.end_date:
        if query.start_date >= query.end_date:
            raise DomainException("Start date must be before end date")
    
    if query.status:
        valid_statuses = ['PENDING', 'APPROVED', 'PAID', 'CANCELLED', 'DISPUTED', 'ON_HOLD']
        if query.status not in valid_statuses:
            raise DomainException(f"Status must be one of: {valid_statuses}")
    
    logger.debug("GetPartnerCommissions query validation passed")