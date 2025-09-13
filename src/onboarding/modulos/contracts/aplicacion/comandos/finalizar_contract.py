"""
Command to finalize/terminate a contract.
"""

import logging
from dataclasses import dataclass
from typing import Optional

from onboarding.seedwork.aplicacion.comandos import ejecutar_comando
from onboarding.seedwork.infraestructura.uow import UnitOfWork
from onboarding.seedwork.dominio.excepciones import DomainException
from .base import CommandContract

logger = logging.getLogger(__name__)


@dataclass
class FinalizarContract:
    """Command to finalize/terminate a contract."""
    
    contract_id: str
    finalized_by: str
    reason: Optional[str] = None


@ejecutar_comando.register
def handle_finalizar_contract(comando: FinalizarContract) -> None:
    """
    Handle FinalizeContract command.
    """
    logger.info(f"Executing FinalizeContract command for contract: {comando.contract_id}")
    
    try:
        # Validate input data
        _validate_finalizar_contract_command(comando)
        
        # Use Unit of Work to update
        with UnitOfWork() as uow:
            repo = uow.contracts
            
            # Get existing contract
            contract = repo.obtener_por_id(comando.contract_id)
            if not contract:
                raise DomainException(f"Contract not found: {comando.contract_id}")
            
            # Finalize contract
            contract.finalizar(
                finalized_by=comando.finalized_by,
                reason=comando.reason
            )
            
            # Save updated contract
            repo.actualizar(contract)
            
            # Commit transaction
            uow.commit()
            
            logger.info(f"Contract finalized successfully: {contract.id}")
    
    except Exception as e:
        logger.error(f"Failed to finalize contract {comando.contract_id}: {str(e)}")
        raise


def _validate_finalizar_contract_command(comando: FinalizarContract):
    """Validate FinalizeContract command data."""
    
    if not comando.contract_id:
        raise DomainException("Contract ID is required")
    
    if not comando.finalized_by:
        raise DomainException("Finalized by user is required")
    
    logger.debug("FinalizeContract command validation passed")