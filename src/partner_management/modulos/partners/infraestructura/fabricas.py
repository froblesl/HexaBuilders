"""
"""

import logging
from datetime import datetime
from typing import Optional

from ..dominio.entidades import Partner
from ..dominio.objetos_valor import (
    PartnerName, PartnerEmail, PartnerPhone, PartnerType, PartnerStatus,
    PartnerAddress, PartnerValidationData, PartnerMetrics
)
from ...seedwork.dominio.fabricas import Fabrica
from ...seedwork.dominio.excepciones import DomainException

logger = logging.getLogger(__name__)


class FabricaPartner(Fabrica):
    """
    Factory for creating Partner entities.
    Encapsulates partner creation logic and validation.
    """
    
    def crear_partner(
        self,
        nombre: PartnerName,
        email: PartnerEmail,
        telefono: PartnerPhone,
        tipo: PartnerType,
        direccion: Optional[str] = None,
        ciudad: Optional[str] = None,
        pais: Optional[str] = None
    ) -> Partner:
        """
        Create a new Partner entity with business rules validation.
        
        Args:
            nombre: Partner name value object
            email: Partner email value object  
            telefono: Partner phone value object
            tipo: Partner type enum
            direccion: Optional address
            ciudad: Optional city
            pais: Optional country
            
        Returns:
            New Partner entity
            
        Raises:
            DomainException: If business rules are violated
        """
        try:
            logger.info(f"Creating partner with email: {email.value}")
            
            # Create address value object if address info provided
            address = None
            if direccion and ciudad and pais:
                address = PartnerAddress(
                    direccion=direccion,
                    ciudad=ciudad,
                    pais=pais
                )
            
            # Create initial validation data (all false initially)
            validation_data = PartnerValidationData()
            
            # Create initial metrics (all zeros)
            metrics = PartnerMetrics()
            
            # Create partner entity
            partner = Partner(
                name=nombre,
                email=email,
                phone=telefono,
                type=tipo,
                status=PartnerStatus.INACTIVO,  # New partners start inactive
                direccion=direccion,
                ciudad=ciudad,
                pais=pais,
                address=address,
                validation_data=validation_data,
                metrics=metrics,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # Apply business rules
            self._aplicar_reglas_negocio(partner)
            
            # Add creation event
            partner.crear_evento_creacion()
            
            logger.info(f"Partner created successfully: {partner.id}")
            return partner
            
        except Exception as e:
            logger.error(f"Failed to create partner: {str(e)}")
            raise
    
    def crear_partner_desde_dto(self, partner_data: dict) -> Partner:
        """
        Create partner from DTO/dictionary data.
        
        Args:
            partner_data: Dictionary with partner data
            
        Returns:
            New Partner entity
        """
        try:
            # Validate required fields
            required_fields = ['nombre', 'email', 'telefono', 'tipo_partner']
            for field in required_fields:
                if field not in partner_data:
                    raise DomainException(f"Missing required field: {field}")
            
            # Create value objects
            nombre = PartnerName(partner_data['nombre'])
            email = PartnerEmail(partner_data['email'])
            telefono = PartnerPhone(partner_data['telefono'])
            tipo = PartnerType(partner_data['tipo_partner'])
            
            return self.crear_partner(
                nombre=nombre,
                email=email,
                telefono=telefono,
                tipo=tipo,
                direccion=partner_data.get('direccion'),
                ciudad=partner_data.get('ciudad'),
                pais=partner_data.get('pais')
            )
            
        except Exception as e:
            logger.error(f"Failed to create partner from DTO: {str(e)}")
            raise
    
    def recrear_partner(
        self,
        partner_id: str,
        nombre: PartnerName,
        email: PartnerEmail,
        telefono: PartnerPhone,
        tipo: PartnerType,
        status: PartnerStatus,
        direccion: Optional[str] = None,
        ciudad: Optional[str] = None,
        pais: Optional[str] = None,
        validation_data: Optional[PartnerValidationData] = None,
        metrics: Optional[PartnerMetrics] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ) -> Partner:
        """
        Recreate partner from persisted data (for repository loading).
        
        Args:
            partner_id: Partner ID
            nombre: Partner name
            email: Partner email
            telefono: Partner phone
            tipo: Partner type
            status: Partner status
            direccion: Partner address
            ciudad: Partner city
            pais: Partner country
            validation_data: Partner validation data
            metrics: Partner metrics
            created_at: Creation timestamp
            updated_at: Update timestamp
            
        Returns:
            Recreated Partner entity
        """
        try:
            # Create address if available
            address = None
            if direccion and ciudad and pais:
                address = PartnerAddress(
                    direccion=direccion,
                    ciudad=ciudad,
                    pais=pais
                )
            
            # Use provided or default values
            validation_data = validation_data or PartnerValidationData()
            metrics = metrics or PartnerMetrics()
            created_at = created_at or datetime.now()
            updated_at = updated_at or datetime.now()
            
            # Create partner entity with existing data
            partner = Partner(
                id=partner_id,
                name=nombre,
                email=email,
                phone=telefono,
                type=tipo,
                status=status,
                direccion=direccion,
                ciudad=ciudad,
                pais=pais,
                address=address,
                validation_data=validation_data,
                metrics=metrics,
                created_at=created_at,
                updated_at=updated_at
            )
            
            logger.debug(f"Partner recreated: {partner.id}")
            return partner
            
        except Exception as e:
            logger.error(f"Failed to recreate partner {partner_id}: {str(e)}")
            raise
    
    def _aplicar_reglas_negocio(self, partner: Partner):
        """
        Apply business rules to new partner.
        
        Args:
            partner: Partner entity to validate
            
        Raises:
            DomainException: If business rules are violated
        """
        # Business rule: Business partners must have address
        if partner.type in [PartnerType.EMPRESA, PartnerType.STARTUP]:
            if not partner.direccion or not partner.ciudad or not partner.pais:
                raise DomainException(
                    f"Business partners of type {partner.type.value} must have complete address information"
                )
        
        # Business rule: Email domain validation for business partners
        if partner.type == PartnerType.EMPRESA:
            if partner.email.value.endswith(('@gmail.com', '@hotmail.com', '@yahoo.com')):
                logger.warning(f"Business partner {partner.id} using personal email domain")
        
        # Business rule: All new partners start inactive and need validation
        if partner.status != PartnerStatus.INACTIVO:
            partner._status = PartnerStatus.INACTIVO
            logger.info(f"Reset partner status to INACTIVO as per business rules: {partner.id}")
        
        logger.debug(f"Business rules applied successfully for partner: {partner.id}")
    
    def crear_partner_con_validacion_email(
        self,
        nombre: PartnerName,
        email: PartnerEmail,
        telefono: PartnerPhone,
        tipo: PartnerType,
        direccion: Optional[str] = None,
        ciudad: Optional[str] = None,
        pais: Optional[str] = None
    ) -> Partner:
        """
        Create partner with immediate email validation.
        
        Args:
            nombre: Partner name
            email: Partner email
            telefono: Partner phone
            tipo: Partner type
            direccion: Optional address
            ciudad: Optional city
            pais: Optional country
            
        Returns:
            Partner with email validated
        """
        partner = self.crear_partner(
            nombre=nombre,
            email=email,
            telefono=telefono,
            tipo=tipo,
            direccion=direccion,
            ciudad=ciudad,
            pais=pais
        )
        
        # Mark email as validated
        partner.validar_email("system")
        
        logger.info(f"Partner created with email validation: {partner.id}")
        return partner