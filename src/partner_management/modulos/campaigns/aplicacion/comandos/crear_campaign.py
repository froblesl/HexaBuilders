"""
Create Campaign command implementation for HexaBuilders.
"""

import logging
from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

from .....seedwork.aplicacion.comandos import ejecutar_comando
from .....seedwork.infraestructura.uow import UnitOfWork
from .....seedwork.dominio.excepciones import DomainException
from ...dominio.entidades import Campaign
from ...dominio.objetos_valor import (
    CampaignName, CampaignDescription, CampaignBudget, CampaignDateRange,
    CampaignType, CampaignTargeting, CampaignSettings
)
from ...infraestructura.fabricas import FabricaCampaign
from .base import ComandoCampaign

logger = logging.getLogger(__name__)


@dataclass
class CrearCampaign(ComandoCampaign):
    """Command to create a new campaign."""
    
    nombre: str
    descripcion: str
    partner_id: str
    tipo_campaign: str
    presupuesto: Decimal
    fecha_inicio: datetime
    fecha_fin: datetime
    moneda: str = "USD"
    paises: Optional[List[str]] = None
    rango_edad: Optional[tuple[int, int]] = None
    intereses: Optional[List[str]] = None
    palabras_clave: Optional[List[str]] = None
    auto_pausar_presupuesto: bool = True
    limite_presupuesto_diario: Optional[Decimal] = None


@ejecutar_comando.register
def handle_crear_campaign(comando: CrearCampaign) -> str:
    """
    Handle CreateCampaign command.
    """
    logger.info(f"Executing CreateCampaign command for partner: {comando.partner_id}")
    
    try:
        # Validate input data
        _validate_crear_campaign_command(comando)
        
        # Create value objects
        campaign_name = CampaignName(comando.nombre)
        campaign_description = CampaignDescription(comando.descripcion)
        campaign_budget = CampaignBudget(comando.presupuesto, comando.moneda)
        campaign_type = CampaignType(comando.tipo_campaign)
        
        date_range = CampaignDateRange(
            start_date=comando.fecha_inicio,
            end_date=comando.fecha_fin
        )
        
        # Create targeting if provided
        targeting = None
        if any([comando.paises, comando.rango_edad, comando.intereses, comando.palabras_clave]):
            targeting = CampaignTargeting(
                countries=comando.paises or [],
                age_range=comando.rango_edad,
                interests=comando.intereses or [],
                keywords=comando.palabras_clave or []
            )
        
        # Create settings
        settings = CampaignSettings(
            auto_pause_on_budget_exceeded=comando.auto_pausar_presupuesto,
            daily_budget_limit=comando.limite_presupuesto_diario
        )
        
        # Create campaign using factory
        fabrica = FabricaCampaign()
        campaign = fabrica.crear_campaign(
            nombre=campaign_name,
            descripcion=campaign_description,
            partner_id=comando.partner_id,
            tipo=campaign_type,
            presupuesto=campaign_budget,
            fecha_rango=date_range,
            targeting=targeting,
            settings=settings
        )
        
        # Use Unit of Work to persist
        with UnitOfWork() as uow:
            repo = uow.campaigns
            
            # Check if partner exists (business rule)
            partner_repo = uow.partners
            partner = partner_repo.obtener_por_id(comando.partner_id)
            if not partner:
                raise DomainException(f"Partner with ID {comando.partner_id} not found")
            
            # Check if partner can create campaigns
            if not partner.puede_crear_campanas():
                raise DomainException(f"Partner {comando.partner_id} cannot create campaigns")
            
            # Save campaign
            repo.agregar(campaign)
            
            # Commit transaction - this will also publish domain events
            uow.commit()
            
            logger.info(f"Campaign created successfully: {campaign.id}")
            return campaign.id
    
    except Exception as e:
        logger.error(f"Failed to create campaign: {str(e)}")
        raise


def _validate_crear_campaign_command(comando: CrearCampaign):
    """Validate CreateCampaign command data."""
    
    if not comando.nombre or len(comando.nombre.strip()) < 3:
        raise DomainException("Campaign name must be at least 3 characters")
    
    if not comando.descripcion or len(comando.descripcion.strip()) < 10:
        raise DomainException("Campaign description must be at least 10 characters")
    
    if not comando.partner_id:
        raise DomainException("Partner ID is required")
    
    if not comando.presupuesto or comando.presupuesto <= 0:
        raise DomainException("Valid positive budget is required")
    
    if comando.presupuesto > Decimal('1000000'):
        raise DomainException("Budget cannot exceed 1,000,000")
    
    valid_types = ['PERFORMANCE', 'BRAND_AWARENESS', 'LEAD_GENERATION', 'SALES', 'ENGAGEMENT']
    if comando.tipo_campaign not in valid_types:
        raise DomainException(f"Campaign type must be one of: {valid_types}")
    
    if not comando.fecha_inicio or not comando.fecha_fin:
        raise DomainException("Start date and end date are required")
    
    if comando.fecha_inicio >= comando.fecha_fin:
        raise DomainException("Start date must be before end date")
    
    # Check if campaign duration is reasonable
    duration = (comando.fecha_fin - comando.fecha_inicio).days
    if duration < 1:
        raise DomainException("Campaign must run for at least 1 day")
    
    if duration > 365:
        raise DomainException("Campaign cannot run for more than 1 year")
    
    # Validate targeting data
    if comando.rango_edad:
        if len(comando.rango_edad) != 2:
            raise DomainException("Age range must be a tuple of (min_age, max_age)")
        
        min_age, max_age = comando.rango_edad
        if min_age < 13 or max_age > 100 or min_age >= max_age:
            raise DomainException("Age range must be between 13-100 with min < max")
    
    if comando.paises and len(comando.paises) > 50:
        raise DomainException("Cannot target more than 50 countries")
    
    if comando.intereses and len(comando.intereses) > 20:
        raise DomainException("Cannot target more than 20 interests")
    
    if comando.palabras_clave and len(comando.palabras_clave) > 100:
        raise DomainException("Cannot target more than 100 keywords")
    
    if comando.limite_presupuesto_diario and comando.limite_presupuesto_diario <= 0:
        raise DomainException("Daily budget limit must be positive")
    
    logger.debug("CreateCampaign command validation passed")