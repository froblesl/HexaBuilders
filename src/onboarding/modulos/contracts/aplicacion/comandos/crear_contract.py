"""
Command to create a new contract.
"""

import logging
from dataclasses import dataclass
from typing import Optional
from datetime import date

from onboarding.seedwork.aplicacion.comandos import ejecutar_comando
from onboarding.seedwork.infraestructura.uow import UnitOfWork
from onboarding.seedwork.dominio.excepciones import DomainException
from ...dominio.entidades import Contract
from ...dominio.objetos_valor import ContractType, ContractStatus
from ...infraestructura.fabricas import FabricaContract
from .base import CommandContract

logger = logging.getLogger(__name__)


@dataclass
class CrearContract:
    """Command to create a new contract."""
    
    partner_id: str
    contract_type: str
    terms: str
    commission_rate: float
    start_date: date
    end_date: Optional[date] = None
    notes: Optional[str] = None


@ejecutar_comando.register
def handle_crear_contract(comando: CrearContract) -> str:
    """
    Handle CreateContract command.
    """
    logger.info(f"Executing CreateContract command for partner: {comando.partner_id}")
    
    try:
        # Validate input data
        _validate_crear_contract_command(comando)
        
        # Create value objects
        contract_type = ContractType(comando.contract_type)
        contract_status = ContractStatus("DRAFT")
        
        # Create contract using factory
        fabrica = FabricaContract()
        contract = fabrica.crear_contract(
            partner_id=comando.partner_id,
            contract_type=contract_type,
            terms=comando.terms,
            commission_rate=comando.commission_rate,
            start_date=comando.start_date,
            end_date=comando.end_date,
            status=contract_status,
            notes=comando.notes
        )
        
        # Use Unit of Work to persist
        with UnitOfWork() as uow:
            repo = uow.contracts
            
            # Save contract
            repo.agregar(contract)
            
            # Commit transaction - this will also publish domain events
            uow.commit()
            
            logger.info(f"Contract created successfully: {contract.id}")
            return contract.id
    
    except Exception as e:
        logger.error(f"Failed to create contract: {str(e)}")
        raise


def _validate_crear_contract_command(comando: CrearContract):
    """Validate CreateContract command data."""
    
    if not comando.partner_id:
        raise DomainException("Partner ID is required")
    
    if not comando.contract_type:
        raise DomainException("Contract type is required")
    
    valid_types = ['STANDARD', 'PREMIUM', 'ENTERPRISE', 'CUSTOM']
    if comando.contract_type not in valid_types:
        raise DomainException(f"Contract type must be one of: {valid_types}")
    
    if not comando.terms or len(comando.terms.strip()) < 10:
        raise DomainException("Contract terms must be at least 10 characters")
    
    if comando.commission_rate <= 0 or comando.commission_rate >= 1:
        raise DomainException("Commission rate must be between 0 and 1")
    
    if comando.end_date and comando.end_date <= comando.start_date:
        raise DomainException("End date must be after start date")
    
    logger.debug("CreateContract command validation passed")