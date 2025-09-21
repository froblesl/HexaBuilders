"""
This provides a complete 360-degree view of a partner with related data.
"""

import logging
from dataclasses import dataclass
from typing import Optional, List, Dict, Any

from src.partner_management.seedwork.aplicacion.queries import ejecutar_query
from src.partner_management.seedwork.infraestructura.uow import UnitOfWork
from src.partner_management.seedwork.dominio.excepciones import DomainException
from ...infraestructura.dto import PartnerDTO
from .base import QueryPartner, QueryResultPartner

logger = logging.getLogger(__name__)


@dataclass
class ObtenerProfile360:
    """Query to get a complete 360-degree partner profile."""
    partner_id: str


@dataclass
class Profile360Data:
    """Complete partner profile data."""
    
    partner: PartnerDTO
    metricas: Dict[str, Any]
    campanas_activas: List[Dict[str, Any]]
    campanas_completadas: List[Dict[str, Any]] 
    comisiones_pendientes: List[Dict[str, Any]]
    comisiones_pagadas: List[Dict[str, Any]]
    historial_actividad: List[Dict[str, Any]]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'partner': self.partner.to_dict(),
            'metricas': self.metricas,
            'campanas_activas': self.campanas_activas,
            'campanas_completadas': self.campanas_completadas,
            'comisiones_pendientes': self.comisiones_pendientes,
            'comisiones_pagadas': self.comisiones_pagadas,
            'historial_actividad': self.historial_actividad
        }


@dataclass
class RespuestaProfile360:
    """Response for GetProfile360 query."""
    profile: Optional[Profile360Data] = None


@ejecutar_query.register
def handle_obtener_profile_360(query: ObtenerProfile360) -> RespuestaProfile360:
    """
    Handle GetProfile360 query.
    """
    logger.info(f"Executing GetProfile360 query for partner: {query.partner_id}")
    
    try:
        # Validate input
        if not query.partner_id:
            raise DomainException("Partner ID is required")
        
        # Use Unit of Work for read operations
        with UnitOfWork() as uow:
            repo = uow.partners
            
            # Get base partner
            partner = repo.obtener_por_id(query.partner_id)
            if not partner:
                logger.warning(f"Partner not found: {query.partner_id}")
                return RespuestaProfile360(profile=None)
            
            # Convert to DTO
            partner_dto = PartnerDTO.from_entity(partner)
            
            # Gather related data (mocked for now - would integrate with other modules)
            profile_data = Profile360Data(
                partner=partner_dto,
                metricas=_get_partner_metrics(query.partner_id),
                campanas_activas=_get_active_campaigns(query.partner_id),
                campanas_completadas=_get_completed_campaigns(query.partner_id),
                comisiones_pendientes=_get_pending_commissions(query.partner_id),
                comisiones_pagadas=_get_paid_commissions(query.partner_id),
                historial_actividad=_get_activity_history(query.partner_id)
            )
            
            logger.info(f"Profile 360 retrieved successfully for partner: {partner.id}")
            return RespuestaProfile360(profile=profile_data)
    
    except Exception as e:
        logger.error(f"Failed to get profile 360 for partner {query.partner_id}: {str(e)}")
        raise


def _get_partner_metrics(partner_id: str) -> Dict[str, Any]:
    """Get partner performance metrics (mock implementation)."""
    return {
        'total_campaigns': 12,
        'active_campaigns': 3,
        'completed_campaigns': 9,
        'success_rate': 0.85,
        'total_commissions_earned': 15750.00,
        'pending_commissions': 2340.00,
        'average_campaign_duration': 21, # days
        'partner_rating': 4.7,
        'last_activity': '2023-09-07T10:30:00Z'
    }


def _get_active_campaigns(partner_id: str) -> List[Dict[str, Any]]:
    """Get active campaigns for partner (mock implementation)."""
    return [
        {
            'id': 'camp-001',
            'nombre': 'Summer Social Media Campaign',
            'fecha_inicio': '2023-08-15T00:00:00Z',
            'fecha_estimada_fin': '2023-09-30T23:59:59Z',
            'progreso': 0.65,
            'presupuesto': 5000.00,
            'comision_estimada': 750.00
        },
        {
            'id': 'camp-002', 
            'nombre': 'Product Launch Campaign',
            'fecha_inicio': '2023-09-01T00:00:00Z',
            'fecha_estimada_fin': '2023-10-15T23:59:59Z',
            'progreso': 0.25,
            'presupuesto': 8000.00,
            'comision_estimada': 1200.00
        }
    ]


def _get_completed_campaigns(partner_id: str) -> List[Dict[str, Any]]:
    """Get completed campaigns for partner (mock implementation)."""
    return [
        {
            'id': 'camp-comp-001',
            'nombre': 'Spring Email Campaign',
            'fecha_inicio': '2023-03-01T00:00:00Z',
            'fecha_fin': '2023-04-30T23:59:59Z',
            'resultado': 'EXITOSA',
            'presupuesto': 3000.00,
            'comision_ganada': 450.00
        }
    ]


def _get_pending_commissions(partner_id: str) -> List[Dict[str, Any]]:
    """Get pending commissions for partner (mock implementation)."""
    return [
        {
            'id': 'comm-001',
            'campaign_id': 'camp-001',
            'cantidad': 750.00,
            'fecha_generacion': '2023-08-30T15:30:00Z',
            'fecha_estimada_pago': '2023-09-15T00:00:00Z',
            'estado': 'PENDIENTE'
        },
        {
            'id': 'comm-002',
            'campaign_id': 'camp-002',
            'cantidad': 1590.00,
            'fecha_generacion': '2023-09-05T09:15:00Z',
            'fecha_estimada_pago': '2023-09-20T00:00:00Z',
            'estado': 'CALCULADA'
        }
    ]


def _get_paid_commissions(partner_id: str) -> List[Dict[str, Any]]:
    """Get paid commissions for partner (mock implementation)."""
    return [
        {
            'id': 'comm-paid-001',
            'campaign_id': 'camp-comp-001',
            'cantidad': 450.00,
            'fecha_pago': '2023-05-15T10:00:00Z',
            'metodo_pago': 'TRANSFERENCIA_BANCARIA',
            'estado': 'PAGADA'
        }
    ]


def _get_activity_history(partner_id: str) -> List[Dict[str, Any]]:
    """Get activity history for partner (mock implementation)."""
    return [
        {
            'fecha': '2023-09-07T10:30:00Z',
            'tipo': 'LOGIN',
            'descripcion': 'Partner logged into dashboard',
            'ip': '192.168.1.100'
        },
        {
            'fecha': '2023-09-06T14:20:00Z',
            'tipo': 'CAMPAIGN_UPDATE',
            'descripcion': 'Updated campaign progress: Summer Social Media Campaign',
            'detalles': {'campaign_id': 'camp-001', 'progreso_anterior': 0.60, 'progreso_nuevo': 0.65}
        },
        {
            'fecha': '2023-09-05T09:15:00Z',
            'tipo': 'COMMISSION_CALCULATED',
            'descripcion': 'Commission calculated for completed milestone',
            'detalles': {'campaign_id': 'camp-002', 'cantidad': 1590.00}
        }
    ]