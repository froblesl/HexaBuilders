"""
Create Commission command implementation for HexaBuilders.
"""

import logging
from dataclasses import dataclass
from typing import Optional
from datetime import datetime
from decimal import Decimal

from partner_management.seedwork.aplicacion.comandos import ejecutar_comando
from partner_management.seedwork.infraestructura.uow import UnitOfWork
from partner_management.seedwork.dominio.excepciones import DomainException
from ...dominio.entidades import Commission
from ...dominio.objetos_valor import (
    CommissionAmount, CommissionRate, CommissionPeriod, TransactionReference,
    CommissionType, CommissionStatus, CommissionCalculation
)
from ...infraestructura.fabricas import FabricaCommission
from .base import CommandCommission

logger = logging.getLogger(__name__)


@dataclass
class CrearCommission(ComandoCommission):
    """Command to create a new commission."""
    
    partner_id: str
    commission_amount: Decimal
    commission_rate: Decimal
    commission_type: str
    transaction_id: str
    transaction_type: str
    transaction_amount: Decimal
    transaction_date: datetime
    calculation_period_start: datetime
    calculation_period_end: datetime
    period_name: str
    currency: str = "USD"
    calculation_method: str = "percentage"


@ejecutar_comando.register
def handle_crear_commission(comando: CrearCommission) -> str:
    """
    Handle CreateCommission command.
    """
    logger.info(f"Executing CreateCommission command for partner: {comando.partner_id}")
    
    try:
        # Validate input data
        _validate_crear_commission_command(comando)
        
        # Create value objects
        commission_amount = CommissionAmount(comando.commission_amount, comando.currency)
        commission_rate = CommissionRate(comando.commission_rate)
        commission_type = CommissionType(comando.commission_type)
        
        transaction_reference = TransactionReference(
            transaction_id=comando.transaction_id,
            transaction_type=comando.transaction_type,
            transaction_amount=comando.transaction_amount,
            transaction_date=comando.transaction_date
        )
        
        calculation_period = CommissionPeriod(
            start_date=comando.calculation_period_start,
            end_date=comando.calculation_period_end,
            period_name=comando.period_name
        )
        
        # Create calculation details
        calculation_details = CommissionCalculation(
            base_amount=comando.transaction_amount,
            commission_rate=commission_rate,
            commission_amount=commission_amount,
            calculation_method=comando.calculation_method,
            calculation_date=datetime.now()
        )
        
        # Create commission using factory
        fabrica = FabricaCommission()
        commission = fabrica.crear_commission(
            partner_id=comando.partner_id,
            commission_amount=commission_amount,
            commission_rate=commission_rate,
            commission_type=commission_type,
            transaction_reference=transaction_reference,
            calculation_period=calculation_period,
            calculation_details=calculation_details
        )
        
        # Use Unit of Work to persist
        with UnitOfWork() as uow:
            repo = uow.commissions
            
            # Check if partner exists
            partner_repo = uow.partners
            partner = partner_repo.obtener_por_id(comando.partner_id)
            if not partner:
                raise DomainException(f"Partner with ID {comando.partner_id} not found")
            
            # Check if partner can receive commissions
            if not partner.puede_recibir_comisiones():
                raise DomainException(f"Partner {comando.partner_id} cannot receive commissions")
            
            # Check for duplicate transaction
            existing_commission = repo.obtener_por_transaction_id(comando.transaction_id)
            if existing_commission:
                raise DomainException(f"Commission for transaction {comando.transaction_id} already exists")
            
            # Save commission
            repo.agregar(commission)
            
            # Commit transaction - this will also publish domain events
            uow.commit()
            
            logger.info(f"Commission created successfully: {commission.id}")
            return commission.id
    
    except Exception as e:
        logger.error(f"Failed to create commission: {str(e)}")
        raise


def _validate_crear_commission_command(comando: CrearCommission):
    """Validate CreateCommission command data."""
    
    if not comando.partner_id:
        raise DomainException("Partner ID is required")
    
    if not comando.commission_amount or comando.commission_amount <= 0:
        raise DomainException("Valid positive commission amount is required")
    
    if comando.commission_amount > Decimal('100000'):
        raise DomainException("Commission amount cannot exceed 100,000")
    
    if not comando.commission_rate or comando.commission_rate < 0 or comando.commission_rate > 1:
        raise DomainException("Commission rate must be between 0 and 1")
    
    valid_types = ['SALE_COMMISSION', 'LEAD_COMMISSION', 'PERFORMANCE_BONUS', 'REFERRAL_BONUS', 'MILESTONE_BONUS']
    if comando.commission_type not in valid_types:
        raise DomainException(f"Commission type must be one of: {valid_types}")
    
    if not comando.transaction_id or len(comando.transaction_id.strip()) < 3:
        raise DomainException("Transaction ID must be at least 3 characters")
    
    if not comando.transaction_type:
        raise DomainException("Transaction type is required")
    
    if not comando.transaction_amount or comando.transaction_amount <= 0:
        raise DomainException("Valid positive transaction amount is required")
    
    if not comando.transaction_date:
        raise DomainException("Transaction date is required")
    
    if not comando.calculation_period_start or not comando.calculation_period_end:
        raise DomainException("Calculation period start and end dates are required")
    
    if comando.calculation_period_start >= comando.calculation_period_end:
        raise DomainException("Period start date must be before end date")
    
    if not comando.period_name or len(comando.period_name.strip()) < 2:
        raise DomainException("Period name must be at least 2 characters")
    
    valid_methods = ['percentage', 'fixed', 'tiered', 'progressive']
    if comando.calculation_method not in valid_methods:
        raise DomainException(f"Calculation method must be one of: {valid_methods}")
    
    logger.debug("CreateCommission command validation passed")