"""
"""

import logging
from dataclasses import dataclass, field
from typing import Optional

from src.partner_management.seedwork.aplicacion.comandos import ejecutar_comando
from src.partner_management.seedwork.infraestructura.uow import UnitOfWork
from src.partner_management.seedwork.dominio.excepciones import DomainException
from ...dominio.entidades import Partner
from ...dominio.objetos_valor import PartnerName, PartnerType, PartnerEmail, PartnerPhone
from ...dominio.eventos import PartnerCreated
from ...infraestructura.fabricas import FabricaPartner
from .base import CommandPartner

logger = logging.getLogger(__name__)


@dataclass
class CrearPartner:
    """Command to create a new partner."""
    
    nombre: str
    email: str
    telefono: str
    tipo_partner: str
    direccion: Optional[str] = None
    ciudad: Optional[str] = None
    pais: Optional[str] = None


@ejecutar_comando.register
def handle_crear_partner(comando: CrearPartner) -> str:
    """
    Handle CreatePartner command.
    """
    logger.info(f"Executing CreatePartner command for: {comando.email}")
    
    try:
        # Validate input data
        _validate_crear_partner_command(comando)
        
        # Create value objects
        partner_name = PartnerName(comando.nombre)
        partner_email = PartnerEmail(comando.email)
        partner_phone = PartnerPhone(comando.telefono)
        partner_type = PartnerType(comando.tipo_partner)
        
        # Create partner using factory
        fabrica = FabricaPartner()
        partner = fabrica.crear_partner(
            nombre=partner_name,
            email=partner_email, 
            telefono=partner_phone,
            tipo=partner_type,
            direccion=comando.direccion,
            ciudad=comando.ciudad,
            pais=comando.pais
        )
        
        # Use Unit of Work to persist
        with UnitOfWork() as uow:
            repo = uow.partners
            
            # Check if partner already exists
            existing = repo.obtener_por_email(partner_email.value)
            if existing:
                raise DomainException(f"Partner with email {partner_email.value} already exists")
            
            # Save partner
            repo.agregar(partner)
            
            # Commit transaction - this will also publish domain events
            uow.commit()
            
            logger.info(f"Partner created successfully: {partner.id}")
            return partner.id
    
    except Exception as e:
        logger.error(f"Failed to create partner: {str(e)}")
        raise


def _validate_crear_partner_command(comando: CrearPartner):
    """Validate CreatePartner command data."""
    
    if not comando.nombre or len(comando.nombre.strip()) < 2:
        raise DomainException("Partner name must be at least 2 characters")
    
    if not comando.email or '@' not in comando.email:
        raise DomainException("Valid email is required")
    
    if not comando.telefono or len(comando.telefono.strip()) < 7:
        raise DomainException("Valid phone number is required")
    
    valid_types = ['INDIVIDUAL', 'EMPRESA', 'STARTUP']
    if comando.tipo_partner not in valid_types:
        raise DomainException(f"Partner type must be one of: {valid_types}")
    
    logger.debug("CreatePartner command validation passed")