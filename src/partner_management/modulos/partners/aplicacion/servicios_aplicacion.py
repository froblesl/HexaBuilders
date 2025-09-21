"""
Application services for Partner module integrating all CQRS components.
"""

import logging
from typing import Dict, Any, Optional, List

from ..dominio.repositorio import PartnerRepository
from ..infraestructura.fabricas import FabricaPartner
from src.partner_management.seedwork.infraestructura.uow import UnitOfWork
from src.partner_management.seedwork.aplicacion.comandos import ejecutar_comando
from src.partner_management.seedwork.aplicacion.queries import ejecutar_query
from .comandos.crear_partner import CrearPartner
from .comandos.actualizar_partner import ActualizarPartner
from .comandos.activar_partner import ActivarPartner
from .comandos.desactivar_partner import DesactivarPartner
from .queries.obtener_partner import ObtenerPartner
from .queries.obtener_todos_partners import ObtenerTodosPartners
from .queries.obtener_profile_360 import ObtenerProfile360

logger = logging.getLogger(__name__)


class PartnerApplicationService:
    """
    Partner application service providing high-level operations.
    Orchestrates commands, queries, and domain services.
    """
    
    def __init__(self):
        self._logger = logger
    
    # Command operations (Write side)
    
    def crear_partner(self, datos_partner: Dict[str, Any]) -> str:
        """
        Create a new partner through command.
        
        Args:
            datos_partner: Partner data dictionary
            
        Returns:
            Partner ID
        """
        try:
            self._logger.info("Processing partner creation through application service")
            
            comando = CrearPartner(
                nombre=datos_partner['nombre'],
                email=datos_partner['email'],
                telefono=datos_partner['telefono'],
                tipo_partner=datos_partner['tipo_partner'],
                direccion=datos_partner.get('direccion'),
                ciudad=datos_partner.get('ciudad'),
                pais=datos_partner.get('pais')
            )
            
            partner_id = ejecutar_comando(comando)
            self._logger.info(f"Partner created successfully through application service: {partner_id}")
            return partner_id
            
        except Exception as e:
            self._logger.error(f"Failed to create partner through application service: {str(e)}")
            raise
    
    def actualizar_partner(self, partner_id: str, datos_actualizacion: Dict[str, Any]) -> str:
        """
        Update partner through command.
        
        Args:
            partner_id: Partner ID
            datos_actualizacion: Update data dictionary
            
        Returns:
            Partner ID
        """
        try:
            self._logger.info(f"Processing partner update through application service: {partner_id}")
            
            comando = ActualizarPartner(
                partner_id=partner_id,
                nombre=datos_actualizacion.get('nombre'),
                email=datos_actualizacion.get('email'),
                telefono=datos_actualizacion.get('telefono'),
                direccion=datos_actualizacion.get('direccion'),
                ciudad=datos_actualizacion.get('ciudad'),
                pais=datos_actualizacion.get('pais')
            )
            
            result_id = ejecutar_comando(comando)
            self._logger.info(f"Partner updated successfully through application service: {result_id}")
            return result_id
            
        except Exception as e:
            self._logger.error(f"Failed to update partner {partner_id} through application service: {str(e)}")
            raise
    
    def activar_partner(self, partner_id: str, activado_por: str = None, razon: str = None) -> str:
        """
        Activate partner through command.
        
        Args:
            partner_id: Partner ID
            activado_por: Who activated the partner
            razon: Activation reason
            
        Returns:
            Partner ID
        """
        try:
            self._logger.info(f"Processing partner activation through application service: {partner_id}")
            
            comando = ActivarPartner(
                partner_id=partner_id,
                activado_por=activado_por,
                razon_activacion=razon
            )
            
            result_id = ejecutar_comando(comando)
            self._logger.info(f"Partner activated successfully through application service: {result_id}")
            return result_id
            
        except Exception as e:
            self._logger.error(f"Failed to activate partner {partner_id} through application service: {str(e)}")
            raise
    
    def desactivar_partner(self, partner_id: str, desactivado_por: str = None, razon: str = None) -> str:
        """
        Deactivate partner through command.
        
        Args:
            partner_id: Partner ID
            desactivado_por: Who deactivated the partner
            razon: Deactivation reason
            
        Returns:
            Partner ID
        """
        try:
            self._logger.info(f"Processing partner deactivation through application service: {partner_id}")
            
            comando = DesactivarPartner(
                partner_id=partner_id,
                desactivado_por=desactivado_por,
                razon_desactivacion=razon
            )
            
            result_id = ejecutar_comando(comando)
            self._logger.info(f"Partner deactivated successfully through application service: {result_id}")
            return result_id
            
        except Exception as e:
            self._logger.error(f"Failed to deactivate partner {partner_id} through application service: {str(e)}")
            raise
    
    # Query operations (Read side)
    
    def obtener_partner(self, partner_id: str) -> Optional[Dict[str, Any]]:
        """
        Get partner by ID through query.
        
        Args:
            partner_id: Partner ID
            
        Returns:
            Partner data dictionary or None
        """
        try:
            self._logger.info(f"Retrieving partner through application service: {partner_id}")
            
            query = ObtenerPartner(partner_id=partner_id)
            resultado = ejecutar_query(query)
            
            if resultado.partner:
                partner_data = resultado.partner.to_dict()
                self._logger.info(f"Partner retrieved successfully through application service: {partner_id}")
                return partner_data
            else:
                self._logger.warning(f"Partner not found through application service: {partner_id}")
                return None
            
        except Exception as e:
            self._logger.error(f"Failed to retrieve partner {partner_id} through application service: {str(e)}")
            raise
    
    def obtener_todos_partners(
        self, 
        filtros: Optional[Dict[str, str]] = None,
        limite: Optional[int] = None,
        offset: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get all partners with filtering through query.
        
        Args:
            filtros: Filter criteria
            limite: Result limit
            offset: Result offset
            
        Returns:
            Partners list with pagination info
        """
        try:
            self._logger.info("Retrieving all partners through application service")
            
            query = ObtenerTodosPartners(
                status=filtros.get('status') if filtros else None,
                tipo=filtros.get('tipo') if filtros else None,
                ciudad=filtros.get('ciudad') if filtros else None,
                pais=filtros.get('pais') if filtros else None,
                limit=limite,
                offset=offset
            )
            
            resultado = ejecutar_query(query)
            
            partners_data = {
                'partners': [partner.to_dict() for partner in resultado.partners],
                'total': resultado.total,
                'limit': resultado.limit,
                'offset': resultado.offset
            }
            
            self._logger.info(f"Retrieved {len(resultado.partners)} partners through application service")
            return partners_data
            
        except Exception as e:
            self._logger.error(f"Failed to retrieve partners through application service: {str(e)}")
            raise
    
    def obtener_profile_360(self, partner_id: str) -> Optional[Dict[str, Any]]:
        """
        Get partner 360 profile through query.
        
        Args:
            partner_id: Partner ID
            
        Returns:
            Complete partner profile or None
        """
        try:
            self._logger.info(f"Retrieving partner 360 profile through application service: {partner_id}")
            
            query = ObtenerProfile360(partner_id=partner_id)
            resultado = ejecutar_query(query)
            
            if resultado.profile:
                profile_data = resultado.profile.to_dict()
                self._logger.info(f"Partner 360 profile retrieved successfully through application service: {partner_id}")
                return profile_data
            else:
                self._logger.warning(f"Partner 360 profile not found through application service: {partner_id}")
                return None
            
        except Exception as e:
            self._logger.error(f"Failed to retrieve partner 360 profile {partner_id} through application service: {str(e)}")
            raise
    
    # Batch operations
    
    def crear_partners_lote(self, partners_data: List[Dict[str, Any]]) -> List[str]:
        """
        Create multiple partners in batch.
        
        Args:
            partners_data: List of partner data dictionaries
            
        Returns:
            List of created partner IDs
        """
        try:
            self._logger.info(f"Processing batch partner creation through application service: {len(partners_data)} partners")
            
            partner_ids = []
            errors = []
            
            for i, partner_data in enumerate(partners_data):
                try:
                    partner_id = self.crear_partner(partner_data)
                    partner_ids.append(partner_id)
                except Exception as e:
                    error_msg = f"Failed to create partner {i}: {str(e)}"
                    self._logger.error(error_msg)
                    errors.append(error_msg)
            
            self._logger.info(f"Batch partner creation completed: {len(partner_ids)} created, {len(errors)} errors")
            
            if errors:
                # Log errors but don't fail the entire batch
                self._logger.warning(f"Batch creation had {len(errors)} errors: {errors}")
            
            return partner_ids
            
        except Exception as e:
            self._logger.error(f"Failed to process batch partner creation: {str(e)}")
            raise
    
    # Utility operations
    
    def obtener_estadisticas_partners(self) -> Dict[str, Any]:
        """
        Get partner statistics.
        
        Returns:
            Partner statistics dictionary
        """
        try:
            self._logger.info("Retrieving partner statistics through application service")
            
            # Get all partners to compute statistics
            result = self.obtener_todos_partners()
            partners = result['partners']
            
            stats = {
                'total_partners': len(partners),
                'por_status': {},
                'por_tipo': {},
                'por_ubicacion': {},
                'validaciones': {
                    'email_validado': 0,
                    'telefono_validado': 0,
                    'identidad_validada': 0,
                    'negocio_validado': 0
                }
            }
            
            # Count by status
            for partner in partners:
                status = partner['status']
                stats['por_status'][status] = stats['por_status'].get(status, 0) + 1
            
            # Count by type
            for partner in partners:
                tipo = partner['tipo']
                stats['por_tipo'][tipo] = stats['por_tipo'].get(tipo, 0) + 1
            
            # Count by location
            for partner in partners:
                pais = partner.get('pais', 'Sin especificar')
                stats['por_ubicacion'][pais] = stats['por_ubicacion'].get(pais, 0) + 1
            
            # Count validations
            for partner in partners:
                validaciones = partner.get('validaciones', {})
                if validaciones.get('email_validado'):
                    stats['validaciones']['email_validado'] += 1
                if validaciones.get('telefono_validado'):
                    stats['validaciones']['telefono_validado'] += 1
                if validaciones.get('identidad_validada'):
                    stats['validaciones']['identidad_validada'] += 1
                if validaciones.get('negocio_validado'):
                    stats['validaciones']['negocio_validado'] += 1
            
            self._logger.info("Partner statistics retrieved successfully through application service")
            return stats
            
        except Exception as e:
            self._logger.error(f"Failed to retrieve partner statistics: {str(e)}")
            raise
    
    def validar_integridad_sistema(self) -> Dict[str, Any]:
        """
        Validate system integrity.
        
        Returns:
            System integrity report
        """
        try:
            self._logger.info("Validating system integrity through application service")
            
            report = {
                'validacion_exitosa': True,
                'errores': [],
                'advertencias': [],
                'estadisticas': {}
            }
            
            # Get statistics
            try:
                report['estadisticas'] = self.obtener_estadisticas_partners()
            except Exception as e:
                report['errores'].append(f"Failed to get statistics: {str(e)}")
                report['validacion_exitosa'] = False
            
            # Test basic operations
            try:
                # Test query operations
                test_result = self.obtener_todos_partners(limite=1)
                if not isinstance(test_result, dict):
                    report['errores'].append("Query operation returned invalid format")
                    report['validacion_exitosa'] = False
                
            except Exception as e:
                report['errores'].append(f"Query operation failed: {str(e)}")
                report['validacion_exitosa'] = False
            
            # Check for warnings
            if report['estadisticas'].get('total_partners', 0) == 0:
                report['advertencias'].append("No partners found in system")
            
            self._logger.info(f"System integrity validation completed: {'Success' if report['validacion_exitosa'] else 'Failed'}")
            return report
            
        except Exception as e:
            self._logger.error(f"Failed to validate system integrity: {str(e)}")
            raise


# Global application service instance
partner_application_service = PartnerApplicationService()


def get_partner_application_service() -> PartnerApplicationService:
    """Get global partner application service instance."""
    return partner_application_service