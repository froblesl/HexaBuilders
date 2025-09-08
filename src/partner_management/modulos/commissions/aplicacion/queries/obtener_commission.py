"""
Get Commission query implementation for HexaBuilders.
"""

import logging
from dataclasses import dataclass
from typing import Optional, Dict, Any

from partner_management.seedwork.aplicacion.queries import ejecutar_query
from partner_management.seedwork.infraestructura.uow import UnitOfWork
from partner_management.seedwork.dominio.excepciones import DomainException
from .base import QueryCommission, CommissionQueryResult

logger = logging.getLogger(__name__)


@dataclass
class ObtenerCommission(QueryCommission):
    """Query to get commission by ID."""
    
    commission_id: str


class CommissionResult(CommissionQueryResult):
    """Commission query result."""
    
    def __init__(self, commission_data: Dict[str, Any]):
        self.commission_data = commission_data
    
    def __dict__(self):
        return self.commission_data


@ejecutar_query.register
def handle_obtener_commission(query: ObtenerCommission) -> CommissionResult:
    """
    Handle GetCommission query.
    """
    logger.info(f"Executing GetCommission query for commission: {query.commission_id}")
    
    try:
        # Validate input data
        _validate_obtener_commission_query(query)
        
        # Use Unit of Work to fetch data
        with UnitOfWork() as uow:
            repo = uow.commissions
            
            # Get commission
            commission = repo.obtener_por_id(query.commission_id)
            if not commission:
                raise DomainException(f"Commission with ID {query.commission_id} not found")
            
            # Get commission summary
            commission_data = commission.get_summary()
            
            logger.info(f"Commission retrieved successfully: {commission.id}")
            return CommissionResult(commission_data)
    
    except Exception as e:
        logger.error(f"Failed to get commission: {str(e)}")
        raise


def _validate_obtener_commission_query(query: ObtenerCommission):
    """Validate GetCommission query data."""
    
    if not query.commission_id:
        raise DomainException("Commission ID is required")
    
    if len(query.commission_id.strip()) < 1:
        raise DomainException("Valid commission ID is required")
    
    logger.debug("GetCommission query validation passed")