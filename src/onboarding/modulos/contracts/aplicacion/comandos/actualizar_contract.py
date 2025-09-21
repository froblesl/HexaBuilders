"""
Command to update an existing contract.
"""

import logging
from dataclasses import dataclass
from typing import Optional
from datetime import date

from src.onboarding.seedwork.aplicacion.comandos import ejecutar_comando
from src.onboarding.seedwork.infraestructura.uow import UnitOfWork
from src.onboarding.seedwork.dominio.excepciones import DomainException
from ...dominio.objetos_valor import ContractType
from .base import CommandContract

logger = logging.getLogger(__name__)


@dataclass
class ActualizarContract:
    """Command to update an existing contract."""
    
    contract_id: str
    contract_type: Optional[str] = None
    terms: Optional[str] = None
    commission_rate: Optional[float] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    notes: Optional[str] = None


@ejecutar_comando.register
def handle_actualizar_contract(comando: ActualizarContract) -> None:
    """
    Handle UpdateContract command.
    """
    logger.info(f"Executing UpdateContract command for contract: {comando.contract_id}")
    
    try:
        # Validate input data
        _validate_actualizar_contract_command(comando)
        
        # Use Unit of Work to update
        with UnitOfWork() as uow:
            repo = uow.contracts
            
            # Get existing contract
            contract = repo.obtener_por_id(comando.contract_id)
            if not contract:
                raise DomainException(f"Contract not found: {comando.contract_id}")
            
            # Update contract fields
            if comando.contract_type:
                contract.actualizar_tipo(ContractType(comando.contract_type))
            
            if comando.terms:
                contract.actualizar_terms(comando.terms)
                
            if comando.commission_rate is not None:
                contract.actualizar_commission_rate(comando.commission_rate)
                
            if comando.start_date:
                contract.actualizar_start_date(comando.start_date)
                
            if comando.end_date:
                contract.actualizar_end_date(comando.end_date)
                
            if comando.notes:
                contract.actualizar_notes(comando.notes)
            
            # Save updated contract
            repo.actualizar(contract)
            
            # Commit transaction
            uow.commit()
            
            logger.info(f"Contract updated successfully: {contract.id}")
    
    except Exception as e:
        logger.error(f"Failed to update contract {comando.contract_id}: {str(e)}")
        raise


def _validate_actualizar_contract_command(comando: ActualizarContract):
    """Validate UpdateContract command data."""
    
    if not comando.contract_id:
        raise DomainException("Contract ID is required")
    
    if comando.contract_type:
        valid_types = ['STANDARD', 'PREMIUM', 'ENTERPRISE', 'CUSTOM']
        if comando.contract_type not in valid_types:
            raise DomainException(f"Contract type must be one of: {valid_types}")
    
    if comando.terms and len(comando.terms.strip()) < 10:
        raise DomainException("Contract terms must be at least 10 characters")
    
    if comando.commission_rate is not None and (comando.commission_rate <= 0 or comando.commission_rate >= 1):
        raise DomainException("Commission rate must be between 0 and 1")
    
    if comando.start_date and comando.end_date and comando.end_date <= comando.start_date:
        raise DomainException("End date must be after start date")
    
    logger.debug("UpdateContract command validation passed")