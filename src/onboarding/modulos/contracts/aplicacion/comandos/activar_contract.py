"""
Command to activate a contract.
"""

import logging
from dataclasses import dataclass

from onboarding.seedwork.aplicacion.comandos import ejecutar_comando
from onboarding.seedwork.infraestructura.uow import UnitOfWork
from onboarding.seedwork.dominio.excepciones import DomainException
from ...dominio.objetos_valor import ContractStatus
from .base import CommandContract

logger = logging.getLogger(__name__)


@dataclass
class ActivarContract:
    """Command to activate a contract."""
    
    contract_id: str
    activated_by: str


@ejecutar_comando.register
def handle_activar_contract(comando: ActivarContract) -> None:
    """
    Handle ActivateContract command.
    """
    logger.info(f"Executing ActivateContract command for contract: {comando.contract_id}")
    
    try:
        # Validate input data
        _validate_activar_contract_command(comando)
        
        # Use Unit of Work to update
        with UnitOfWork() as uow:
            repo = uow.contracts
            
            # Get existing contract
            contract = repo.obtener_por_id(comando.contract_id)
            if not contract:
                raise DomainException(f"Contract not found: {comando.contract_id}")
            
            # Activate contract
            contract.activar(activated_by=comando.activated_by)
            
            # Save updated contract
            repo.actualizar(contract)
            
            # Commit transaction
            uow.commit()
            
            logger.info(f"Contract activated successfully: {contract.id}")
    
    except Exception as e:
        logger.error(f"Failed to activate contract {comando.contract_id}: {str(e)}")
        raise


def _validate_activar_contract_command(comando: ActivarContract):
    """Validate ActivateContract command data."""
    
    if not comando.contract_id:
        raise DomainException("Contract ID is required")
    
    if not comando.activated_by:
        raise DomainException("Activated by user is required")
    
    logger.debug("ActivateContract command validation passed")