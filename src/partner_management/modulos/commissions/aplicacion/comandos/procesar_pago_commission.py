"""
Process Commission Payment command implementation for HexaBuilders.
"""

import logging
from dataclasses import dataclass
from typing import Optional
from decimal import Decimal

from .....seedwork.aplicacion.comandos import ejecutar_comando
from .....seedwork.infraestructura.uow import UnitOfWork
from .....seedwork.dominio.excepciones import DomainException
from ...dominio.objetos_valor import PaymentMethod
from .base import ComandoCommission

logger = logging.getLogger(__name__)


@dataclass
class ProcesarPagoCommission(ComandoCommission):
    """Command to process payment for a commission."""
    
    commission_id: str
    payment_method: str
    payment_reference: str
    payment_fee: Decimal = Decimal('0.00')
    bank_details: Optional[str] = None


@ejecutar_comando.register
def handle_procesar_pago_commission(comando: ProcesarPagoCommission) -> str:
    """
    Handle ProcessCommissionPayment command.
    """
    logger.info(f"Executing ProcessCommissionPayment command for commission: {comando.commission_id}")
    
    try:
        # Validate input data
        _validate_procesar_pago_commission_command(comando)
        
        # Use Unit of Work to persist
        with UnitOfWork() as uow:
            repo = uow.commissions
            
            # Get existing commission
            commission = repo.obtener_por_id(comando.commission_id)
            if not commission:
                raise DomainException(f"Commission with ID {comando.commission_id} not found")
            
            # Check if commission can be paid
            if not commission.puede_ser_pagada():
                raise DomainException("Commission cannot be paid in current state - must be approved first")
            
            # Create payment method value object
            payment_method = PaymentMethod(comando.payment_method)
            
            # Process payment
            commission.procesar_pago(
                payment_method=payment_method,
                payment_reference=comando.payment_reference,
                payment_fee=comando.payment_fee,
                bank_details=comando.bank_details
            )
            
            # Save updated commission
            repo.actualizar(commission)
            
            # Commit transaction - this will also publish domain events
            uow.commit()
            
            logger.info(f"Commission payment processed successfully: {commission.id}")
            return commission.id
    
    except Exception as e:
        logger.error(f"Failed to process commission payment: {str(e)}")
        raise


def _validate_procesar_pago_commission_command(comando: ProcesarPagoCommission):
    """Validate ProcessCommissionPayment command data."""
    
    if not comando.commission_id:
        raise DomainException("Commission ID is required")
    
    valid_payment_methods = ['BANK_TRANSFER', 'PAYPAL', 'STRIPE', 'WIRE_TRANSFER', 'CHECK', 'CRYPTO']
    if comando.payment_method not in valid_payment_methods:
        raise DomainException(f"Payment method must be one of: {valid_payment_methods}")
    
    if not comando.payment_reference or len(comando.payment_reference.strip()) < 3:
        raise DomainException("Payment reference must be at least 3 characters")
    
    if len(comando.payment_reference.strip()) > 100:
        raise DomainException("Payment reference cannot exceed 100 characters")
    
    if comando.payment_fee < Decimal('0'):
        raise DomainException("Payment fee cannot be negative")
    
    if comando.payment_fee > Decimal('1000'):
        raise DomainException("Payment fee cannot exceed 1,000")
    
    if comando.bank_details and len(comando.bank_details.strip()) > 500:
        raise DomainException("Bank details cannot exceed 500 characters")
    
    logger.debug("ProcessCommissionPayment command validation passed")