"""
"""

import logging
from dataclasses import dataclass
from typing import Optional

from src.partner_management.seedwork.aplicacion.comandos import ejecutar_comando
from src.partner_management.seedwork.infraestructura.uow import UnitOfWork
from src.partner_management.seedwork.dominio.excepciones import DomainException
from ...dominio.objetos_valor import PartnerName, PartnerEmail, PartnerPhone
from .base import CommandPartner

logger = logging.getLogger(__name__)


@dataclass
class ActualizarPartner:
    """Command to update an existing partner."""
    
    partner_id: str
    nombre: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    ciudad: Optional[str] = None
    pais: Optional[str] = None


@ejecutar_comando.register
def handle_actualizar_partner(comando: ActualizarPartner) -> str:
    """
    Handle UpdatePartner command.
    """
    logger.info(f"Executing UpdatePartner command for partner: {comando.partner_id}")
    
    try:
        # Validate input
        _validate_actualizar_partner_command(comando)
        
        # Use Unit of Work
        with UnitOfWork() as uow:
            repo = uow.partners
            
            # Get existing partner
            partner = repo.obtener_por_id(comando.partner_id)
            if not partner:
                raise DomainException(f"Partner with ID {comando.partner_id} not found")
            
            # Track changes for events
            cambios = []
            
            # Update fields if provided
            if comando.nombre:
                partner_name = PartnerName(comando.nombre)
                partner.actualizar_nombre(partner_name)
                cambios.append('nombre')
            
            if comando.email:
                partner_email = PartnerEmail(comando.email)
                
                # Check email uniqueness
                existing_with_email = repo.obtener_por_email(partner_email.value)
                if existing_with_email and existing_with_email.id != partner.id:
                    raise DomainException(f"Email {partner_email.value} is already in use")
                
                partner.actualizar_email(partner_email)
                cambios.append('email')
            
            if comando.telefono:
                partner_phone = PartnerPhone(comando.telefono)
                partner.actualizar_telefono(partner_phone)
                cambios.append('telefono')
            
            if comando.direccion is not None:
                partner.actualizar_direccion(comando.direccion)
                cambios.append('direccion')
            
            if comando.ciudad is not None:
                partner.actualizar_ciudad(comando.ciudad)
                cambios.append('ciudad')
            
            if comando.pais is not None:
                partner.actualizar_pais(comando.pais)
                cambios.append('pais')
            
            # Create profile updated event
            if cambios:
                partner.agregar_evento_dominio(
                    partner.crear_evento_profile_actualizado(cambios)
                )
            
            # Save changes
            repo.actualizar(partner)
            uow.commit()
            
            logger.info(f"Partner updated successfully: {partner.id}, changes: {cambios}")
            return partner.id
    
    except Exception as e:
        logger.error(f"Failed to update partner {comando.partner_id}: {str(e)}")
        raise


def _validate_actualizar_partner_command(comando: ActualizarPartner):
    """Validate UpdatePartner command data."""
    
    if not comando.partner_id:
        raise DomainException("Partner ID is required")
    
    # At least one field must be provided for update
    update_fields = [
        comando.nombre, comando.email, comando.telefono,
        comando.direccion, comando.ciudad, comando.pais
    ]
    
    if not any(field is not None for field in update_fields):
        raise DomainException("At least one field must be provided for update")
    
    # Validate individual fields if provided
    if comando.nombre and len(comando.nombre.strip()) < 2:
        raise DomainException("Partner name must be at least 2 characters")
    
    if comando.email and '@' not in comando.email:
        raise DomainException("Valid email is required")
    
    if comando.telefono and len(comando.telefono.strip()) < 7:
        raise DomainException("Valid phone number is required")
    
    logger.debug("UpdatePartner command validation passed")