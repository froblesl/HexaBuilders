"""
Get All Commissions query implementation for HexaBuilders.
"""

import logging
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

from .....seedwork.aplicacion.queries import ejecutar_query
from .....seedwork.infraestructura.uow import UnitOfWork
from .....seedwork.dominio.excepciones import DomainException
from .base import QueryCommission, CommissionQueryResult

logger = logging.getLogger(__name__)


@dataclass
class ObtenerTodosCommissions(QueryCommission):
    """Query to get all commissions with optional filtering."""
    
    partner_id: Optional[str] = None
    status: Optional[str] = None
    commission_type: Optional[str] = None
    limit: int = 100
    offset: int = 0


class CommissionsListResult(CommissionQueryResult):
    """Commissions list query result."""
    
    def __init__(self, commissions_data: List[Dict[str, Any]], total_count: int):
        self.commissions = commissions_data
        self.total_count = total_count
        self.count = len(commissions_data)


@ejecutar_query.register
def handle_obtener_todos_commissions(query: ObtenerTodosCommissions) -> CommissionsListResult:
    """
    Handle GetAllCommissions query.
    """
    logger.info(f"Executing GetAllCommissions query with filters - partner_id: {query.partner_id}, status: {query.status}")
    
    try:
        # Validate input data
        _validate_obtener_todos_commissions_query(query)
        
        # Use Unit of Work to fetch data
        with UnitOfWork() as uow:
            repo = uow.commissions
            
            # Build filters
            filters = {}
            if query.partner_id:
                filters['partner_id'] = query.partner_id
            if query.status:
                filters['status'] = query.status
            if query.commission_type:
                filters['commission_type'] = query.commission_type
            
            # Get commissions with pagination
            commissions = repo.obtener_todos_con_filtros(
                filters=filters,
                limit=query.limit,
                offset=query.offset
            )
            
            # Get total count
            total_count = repo.contar_con_filtros(filters)
            
            # Convert to summary format
            commissions_data = [commission.get_summary() for commission in commissions]
            
            logger.info(f"Retrieved {len(commissions)} commissions out of {total_count} total")
            return CommissionsListResult(commissions_data, total_count)
    
    except Exception as e:
        logger.error(f"Failed to get commissions: {str(e)}")
        raise


def _validate_obtener_todos_commissions_query(query: ObtenerTodosCommissions):
    """Validate GetAllCommissions query data."""
    
    if query.limit <= 0 or query.limit > 1000:
        raise DomainException("Limit must be between 1 and 1000")
    
    if query.offset < 0:
        raise DomainException("Offset cannot be negative")
    
    if query.status:
        valid_statuses = ['PENDING', 'APPROVED', 'PAID', 'CANCELLED', 'DISPUTED', 'ON_HOLD']
        if query.status not in valid_statuses:
            raise DomainException(f"Status must be one of: {valid_statuses}")
    
    if query.commission_type:
        valid_types = ['SALE_COMMISSION', 'LEAD_COMMISSION', 'PERFORMANCE_BONUS', 'REFERRAL_BONUS', 'MILESTONE_BONUS']
        if query.commission_type not in valid_types:
            raise DomainException(f"Commission type must be one of: {valid_types}")
    
    logger.debug("GetAllCommissions query validation passed")