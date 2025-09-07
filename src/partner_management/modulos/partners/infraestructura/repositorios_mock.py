"""
This provides an in-memory implementation for testing and development.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional
from uuid import uuid4

from ..dominio.entidades import Partner
from ..dominio.repositorio import PartnerRepository
from ..dominio.objetos_valor import PartnerStatus, PartnerType
from ...seedwork.dominio.excepciones import DomainException

logger = logging.getLogger(__name__)


class MockPartnerRepository(PartnerRepository):
    """
    Mock implementation of PartnerRepository using in-memory storage.
    For development, testing, and demonstration purposes.
    """
    
    def __init__(self):
        self._partners: Dict[str, Partner] = {}
        self._email_index: Dict[str, str] = {}  # email -> partner_id mapping
        self._logger = logger
        
        # Add some sample data for testing
        self._initialize_sample_data()
    
    def obtener_por_id(self, partner_id: str) -> Optional[Partner]:
        """Get partner by ID."""
        partner = self._partners.get(partner_id)
        if partner:
            self._logger.debug(f"Partner found by ID: {partner_id}")
        else:
            self._logger.debug(f"Partner not found by ID: {partner_id}")
        return partner
    
    def obtener_por_email(self, email: str) -> Optional[Partner]:
        """Get partner by email."""
        partner_id = self._email_index.get(email.lower())
        if partner_id:
            partner = self._partners.get(partner_id)
            if partner:
                self._logger.debug(f"Partner found by email: {email}")
                return partner
        
        self._logger.debug(f"Partner not found by email: {email}")
        return None
    
    def obtener_todos(
        self, 
        filtros: Optional[Dict[str, str]] = None, 
        limit: Optional[int] = None, 
        offset: Optional[int] = None
    ) -> List[Partner]:
        """Get all partners with optional filtering and pagination."""
        partners = list(self._partners.values())
        
        # Apply filters
        if filtros:
            partners = self._apply_filters(partners, filtros)
        
        # Apply pagination
        if offset:
            partners = partners[offset:]
        
        if limit:
            partners = partners[:limit]
        
        self._logger.debug(f"Retrieved {len(partners)} partners with filters: {filtros}")
        return partners
    
    def contar_con_filtros(self, filtros: Optional[Dict[str, str]] = None) -> int:
        """Count partners with filters."""
        partners = list(self._partners.values())
        
        if filtros:
            partners = self._apply_filters(partners, filtros)
        
        count = len(partners)
        self._logger.debug(f"Counted {count} partners with filters: {filtros}")
        return count
    
    def agregar(self, partner: Partner):
        """Add new partner."""
        if partner.id in self._partners:
            raise DomainException(f"Partner with ID {partner.id} already exists")
        
        if self._email_index.get(partner.email.value.lower()):
            raise DomainException(f"Partner with email {partner.email.value} already exists")
        
        self._partners[partner.id] = partner
        self._email_index[partner.email.value.lower()] = partner.id
        
        self._logger.info(f"Partner added: {partner.id}")
    
    def actualizar(self, partner: Partner):
        """Update existing partner."""
        if partner.id not in self._partners:
            raise DomainException(f"Partner with ID {partner.id} does not exist")
        
        # Check if email is being changed and if new email is available
        old_partner = self._partners[partner.id]
        if old_partner.email.value.lower() != partner.email.value.lower():
            if self._email_index.get(partner.email.value.lower()):
                raise DomainException(f"Partner with email {partner.email.value} already exists")
            
            # Update email index
            del self._email_index[old_partner.email.value.lower()]
            self._email_index[partner.email.value.lower()] = partner.id
        
        # Update partner
        partner.updated_at = datetime.now()
        self._partners[partner.id] = partner
        
        self._logger.info(f"Partner updated: {partner.id}")
    
    def eliminar(self, partner: Partner):
        """Remove partner."""
        if partner.id not in self._partners:
            raise DomainException(f"Partner with ID {partner.id} does not exist")
        
        # Remove from email index
        del self._email_index[partner.email.value.lower()]
        
        # Remove from partners
        del self._partners[partner.id]
        
        self._logger.info(f"Partner removed: {partner.id}")
    
    def obtener_por_status(self, status: PartnerStatus) -> List[Partner]:
        """Get partners by status."""
        partners = [p for p in self._partners.values() if p.status == status]
        self._logger.debug(f"Retrieved {len(partners)} partners with status: {status.value}")
        return partners
    
    def obtener_por_tipo(self, tipo: PartnerType) -> List[Partner]:
        """Get partners by type."""
        partners = [p for p in self._partners.values() if p.type == tipo]
        self._logger.debug(f"Retrieved {len(partners)} partners with type: {tipo.value}")
        return partners
    
    def obtener_activos(self) -> List[Partner]:
        """Get active partners."""
        return self.obtener_por_status(PartnerStatus.ACTIVO)
    
    def buscar_por_nombre(self, nombre_parcial: str) -> List[Partner]:
        """Search partners by partial name match."""
        nombre_lower = nombre_parcial.lower()
        partners = [
            p for p in self._partners.values() 
            if nombre_lower in p.name.value.lower()
        ]
        self._logger.debug(f"Found {len(partners)} partners matching name: {nombre_parcial}")
        return partners
    
    def obtener_por_ubicacion(self, ciudad: Optional[str] = None, pais: Optional[str] = None) -> List[Partner]:
        """Get partners by location."""
        partners = []
        
        for partner in self._partners.values():
            match = True
            
            if ciudad and (not partner.ciudad or partner.ciudad.lower() != ciudad.lower()):
                match = False
            
            if pais and (not partner.pais or partner.pais.lower() != pais.lower()):
                match = False
            
            if match:
                partners.append(partner)
        
        self._logger.debug(f"Retrieved {len(partners)} partners by location - city: {ciudad}, country: {pais}")
        return partners
    
    def contar_total(self) -> int:
        """Count total partners."""
        return len(self._partners)
    
    def existe_con_email(self, email: str) -> bool:
        """Check if partner with email exists."""
        return email.lower() in self._email_index
    
    def _apply_filters(self, partners: List[Partner], filtros: Dict[str, str]) -> List[Partner]:
        """Apply filters to partner list."""
        filtered_partners = partners
        
        for field, value in filtros.items():
            if field == 'status':
                try:
                    status = PartnerStatus(value.upper())
                    filtered_partners = [p for p in filtered_partners if p.status == status]
                except ValueError:
                    self._logger.warning(f"Invalid status filter value: {value}")
            
            elif field == 'tipo':
                try:
                    tipo = PartnerType(value.upper())
                    filtered_partners = [p for p in filtered_partners if p.type == tipo]
                except ValueError:
                    self._logger.warning(f"Invalid type filter value: {value}")
            
            elif field == 'ciudad':
                filtered_partners = [
                    p for p in filtered_partners 
                    if p.ciudad and p.ciudad.lower() == value.lower()
                ]
            
            elif field == 'pais':
                filtered_partners = [
                    p for p in filtered_partners 
                    if p.pais and p.pais.lower() == value.lower()
                ]
            
            elif field == 'email_validado':
                email_validated = value.lower() == 'true'
                filtered_partners = [
                    p for p in filtered_partners 
                    if p.validation_data and p.validation_data.email_validated == email_validated
                ]
        
        return filtered_partners
    
    def _initialize_sample_data(self):
        """Initialize repository with sample data for testing."""
        try:
            from .fabricas import FabricaPartner
            from ..dominio.objetos_valor import PartnerName, PartnerEmail, PartnerPhone, PartnerType
            
            fabrica = FabricaPartner()
            
            # Sample partners
            sample_partners = [
                {
                    'nombre': 'Juan Pérez',
                    'email': 'juan.perez@email.com',
                    'telefono': '+57-300-1234567',
                    'tipo': PartnerType.INDIVIDUAL,
                    'ciudad': 'Bogotá',
                    'pais': 'Colombia'
                },
                {
                    'nombre': 'TechCorp S.A.S.',
                    'email': 'info@techcorp.com',
                    'telefono': '+57-1-2345678',
                    'tipo': PartnerType.EMPRESA,
                    'direccion': 'Carrera 7 # 71-52',
                    'ciudad': 'Bogotá',
                    'pais': 'Colombia'
                },
                {
                    'nombre': 'InnovaStartup',
                    'email': 'contact@innovastartup.co',
                    'telefono': '+57-312-7654321',
                    'tipo': PartnerType.STARTUP,
                    'direccion': 'Calle 93 # 11-29',
                    'ciudad': 'Medellín',
                    'pais': 'Colombia'
                }
            ]
            
            for partner_data in sample_partners:
                try:
                    partner = fabrica.crear_partner(
                        nombre=PartnerName(partner_data['nombre']),
                        email=PartnerEmail(partner_data['email']),
                        telefono=PartnerPhone(partner_data['telefono']),
                        tipo=partner_data['tipo'],
                        direccion=partner_data.get('direccion'),
                        ciudad=partner_data.get('ciudad'),
                        pais=partner_data.get('pais')
                    )
                    
                    # Clear events to avoid triggering during initialization
                    partner.limpiar_eventos()
                    
                    # Add to repository
                    self._partners[partner.id] = partner
                    self._email_index[partner.email.value.lower()] = partner.id
                    
                except Exception as e:
                    self._logger.warning(f"Failed to create sample partner: {str(e)}")
            
            self._logger.info(f"Initialized mock repository with {len(self._partners)} sample partners")
            
        except Exception as e:
            self._logger.warning(f"Failed to initialize sample data: {str(e)}")
    
    def limpiar(self):
        """Clear all data (for testing)."""
        self._partners.clear()
        self._email_index.clear()
        self._logger.info("Mock repository cleared")
    
    def obtener_estadisticas(self) -> Dict[str, int]:
        """Get repository statistics."""
        stats = {
            'total_partners': len(self._partners),
            'activos': len([p for p in self._partners.values() if p.status == PartnerStatus.ACTIVO]),
            'inactivos': len([p for p in self._partners.values() if p.status == PartnerStatus.INACTIVO]),
            'suspendidos': len([p for p in self._partners.values() if p.status == PartnerStatus.SUSPENDIDO]),
            'individuales': len([p for p in self._partners.values() if p.type == PartnerType.INDIVIDUAL]),
            'empresas': len([p for p in self._partners.values() if p.type == PartnerType.EMPRESA]),
            'startups': len([p for p in self._partners.values() if p.type == PartnerType.STARTUP])
        }
        
        self._logger.debug(f"Repository statistics: {stats}")
        return stats