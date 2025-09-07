"""
Update Campaign command implementation for HexaBuilders.
"""

import logging
from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

from .....seedwork.aplicacion.comandos import ejecutar_comando
from .....seedwork.infraestructura.uow import UnitOfWork
from .....seedwork.dominio.excepciones import DomainException
from ...dominio.objetos_valor import (
    CampaignName, CampaignDescription, CampaignBudget, 
    CampaignDateRange, CampaignTargeting
)
from .base import ComandoCampaign

logger = logging.getLogger(__name__)


@dataclass
class ActualizarCampaign(ComandoCampaign):
    """Command to update campaign information."""
    
    campaign_id: str
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    presupuesto: Optional[Decimal] = None
    fecha_inicio: Optional[datetime] = None
    fecha_fin: Optional[datetime] = None
    moneda: Optional[str] = None
    paises: Optional[List[str]] = None
    rango_edad: Optional[tuple[int, int]] = None
    intereses: Optional[List[str]] = None
    palabras_clave: Optional[List[str]] = None
    updated_by: Optional[str] = None


@ejecutar_comando.register
def handle_actualizar_campaign(comando: ActualizarCampaign) -> str:
    """
    Handle UpdateCampaign command.
    """
    logger.info(f"Executing UpdateCampaign command for campaign: {comando.campaign_id}")
    
    try:
        # Validate input data
        _validate_actualizar_campaign_command(comando)
        
        # Use Unit of Work to update
        with UnitOfWork() as uow:
            repo = uow.campaigns
            
            # Get existing campaign
            campaign = repo.obtener_por_id(comando.campaign_id)
            if not campaign:
                raise DomainException(f"Campaign with ID {comando.campaign_id} not found")
            
            # Check if campaign can be updated
            if not campaign.puede_ser_editada():
                raise DomainException("Campaign cannot be updated in its current status")
            
            # Update basic information
            updated_name = None
            if comando.nombre:
                updated_name = CampaignName(comando.nombre)
            
            updated_description = None
            if comando.descripcion:
                updated_description = CampaignDescription(comando.descripcion)
            
            updated_budget = None
            if comando.presupuesto:
                currency = comando.moneda or campaign.presupuesto.currency
                updated_budget = CampaignBudget(comando.presupuesto, currency)
            
            updated_date_range = None
            if comando.fecha_inicio or comando.fecha_fin:
                start_date = comando.fecha_inicio or campaign.fecha_rango.start_date
                end_date = comando.fecha_fin or campaign.fecha_rango.end_date
                updated_date_range = CampaignDateRange(start_date, end_date)
            
            # Update campaign information
            campaign.actualizar_informacion(
                nombre=updated_name,
                descripcion=updated_description,
                presupuesto=updated_budget,
                fecha_rango=updated_date_range,
                updated_by=comando.updated_by
            )
            
            # Update targeting if provided
            if any([comando.paises is not None, comando.rango_edad is not None, 
                   comando.intereses is not None, comando.palabras_clave is not None]):
                
                # Use existing values for fields not being updated
                current_targeting = campaign.targeting
                
                new_targeting = CampaignTargeting(
                    countries=comando.paises if comando.paises is not None else current_targeting.countries,
                    age_range=comando.rango_edad if comando.rango_edad is not None else current_targeting.age_range,
                    interests=comando.intereses if comando.intereses is not None else current_targeting.interests,
                    keywords=comando.palabras_clave if comando.palabras_clave is not None else current_targeting.keywords
                )
                
                campaign.actualizar_targeting(new_targeting, comando.updated_by)
            
            # Save changes
            repo.actualizar(campaign)
            
            # Commit transaction
            uow.commit()
            
            logger.info(f"Campaign updated successfully: {campaign.id}")
            return campaign.id
    
    except Exception as e:
        logger.error(f"Failed to update campaign {comando.campaign_id}: {str(e)}")
        raise


def _validate_actualizar_campaign_command(comando: ActualizarCampaign):
    """Validate UpdateCampaign command data."""
    
    if not comando.campaign_id:
        raise DomainException("Campaign ID is required")
    
    if comando.nombre is not None and len(comando.nombre.strip()) < 3:
        raise DomainException("Campaign name must be at least 3 characters")
    
    if comando.descripcion is not None and len(comando.descripcion.strip()) < 10:
        raise DomainException("Campaign description must be at least 10 characters")
    
    if comando.presupuesto is not None:
        if comando.presupuesto <= 0:
            raise DomainException("Budget must be positive")
        
        if comando.presupuesto > Decimal('1000000'):
            raise DomainException("Budget cannot exceed 1,000,000")
    
    if comando.fecha_inicio and comando.fecha_fin:
        if comando.fecha_inicio >= comando.fecha_fin:
            raise DomainException("Start date must be before end date")
        
        duration = (comando.fecha_fin - comando.fecha_inicio).days
        if duration < 1:
            raise DomainException("Campaign must run for at least 1 day")
        
        if duration > 365:
            raise DomainException("Campaign cannot run for more than 1 year")
    
    # Validate targeting data
    if comando.rango_edad is not None:
        if len(comando.rango_edad) != 2:
            raise DomainException("Age range must be a tuple of (min_age, max_age)")
        
        min_age, max_age = comando.rango_edad
        if min_age < 13 or max_age > 100 or min_age >= max_age:
            raise DomainException("Age range must be between 13-100 with min < max")
    
    if comando.paises is not None and len(comando.paises) > 50:
        raise DomainException("Cannot target more than 50 countries")
    
    if comando.intereses is not None and len(comando.intereses) > 20:
        raise DomainException("Cannot target more than 20 interests")
    
    if comando.palabras_clave is not None and len(comando.palabras_clave) > 100:
        raise DomainException("Cannot target more than 100 keywords")
    
    logger.debug("UpdateCampaign command validation passed")