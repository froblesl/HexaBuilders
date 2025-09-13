"""
Query to get all contracts with optional filtering.
"""

import logging
from dataclasses import dataclass
from typing import List, Optional

from onboarding.seedwork.aplicacion.queries import ejecutar_query
from onboarding.seedwork.infraestructura.uow import UnitOfWork
from ...infraestructura.dto import ContractDTO
from .base import QueryContract, QueryResultContract

logger = logging.getLogger(__name__)


@dataclass
class ObtenerTodosContracts:
    """Query to get all contracts with optional filtering."""
    partner_id: Optional[str] = None
    contract_type: Optional[str] = None
    status: Optional[str] = None
    limit: Optional[int] = None
    offset: Optional[int] = None


@dataclass
class RespuestaObtenerTodosContracts:
    """Response for GetAllContracts query."""
    contracts: List[ContractDTO]
    total_count: int


@ejecutar_query.register
def handle_obtener_todos_contracts(query: ObtenerTodosContracts) -> RespuestaObtenerTodosContracts:
    """
    Handle GetAllContracts query.
    """
    logger.info("Executing GetAllContracts query")
    
    try:
        # Use Unit of Work for read operations
        with UnitOfWork() as uow:
            repo = uow.contracts
            
            # Apply filters based on query parameters
            filters = {}
            if query.partner_id:
                filters['partner_id'] = query.partner_id
            if query.contract_type:
                filters['contract_type'] = query.contract_type
            if query.status:
                filters['status'] = query.status
            
            # Get contracts with filters
            contracts = repo.obtener_todos(
                filters=filters,
                limit=query.limit,
                offset=query.offset
            )
            
            # Get total count for pagination
            total_count = repo.contar(filters=filters)
            
            # Convert to DTOs
            contract_dtos = [ContractDTO.from_entity(contract) for contract in contracts]
            
            logger.info(f"Retrieved {len(contract_dtos)} contracts successfully")
            return RespuestaObtenerTodosContracts(
                contracts=contract_dtos,
                total_count=total_count
            )
    
    except Exception as e:
        logger.error(f"Failed to get contracts: {str(e)}")
        raise