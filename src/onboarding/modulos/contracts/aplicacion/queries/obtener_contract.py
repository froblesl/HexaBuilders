"""
Query to get a contract by ID.
"""

import logging
from dataclasses import dataclass
from typing import Optional

from src.onboarding.seedwork.aplicacion.queries import ejecutar_query
from src.onboarding.seedwork.infraestructura.uow import UnitOfWork
from src.onboarding.seedwork.dominio.excepciones import DomainException
from ...infraestructura.dto import ContractDTO
from .base import QueryContract, QueryResultContract

logger = logging.getLogger(__name__)


@dataclass
class ObtenerContract:
    """Query to get a contract by ID."""
    contract_id: str


@dataclass
class RespuestaObtenerContract:
    """Response for GetContract query."""
    contract: Optional[ContractDTO] = None


@ejecutar_query.register
def handle_obtener_contract(query: ObtenerContract) -> RespuestaObtenerContract:
    """
    Handle GetContract query.
    """
    logger.info(f"Executing GetContract query for contract: {query.contract_id}")
    
    try:
        # Validate input
        if not query.contract_id:
            raise DomainException("Contract ID is required")
        
        # Use Unit of Work for read operations
        with UnitOfWork() as uow:
            repo = uow.contracts
            
            # Get contract
            contract = repo.obtener_por_id(query.contract_id)
            
            if not contract:
                logger.warning(f"Contract not found: {query.contract_id}")
                return RespuestaObtenerContract(contract=None)
            
            # Convert to DTO
            contract_dto = ContractDTO.from_entity(contract)
            
            logger.info(f"Contract retrieved successfully: {contract.id}")
            return RespuestaObtenerContract(contract=contract_dto)
    
    except Exception as e:
        logger.error(f"Failed to get contract {query.contract_id}: {str(e)}")
        raise