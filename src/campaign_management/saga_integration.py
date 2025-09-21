"""
Integración de Saga para el servicio de Campaign Management.
Escucha eventos de la saga y responde apropiadamente usando Apache Pulsar.
"""

import logging
import time
from datetime import datetime
from typing import Dict, Any

# Importar el dispatcher de Pulsar
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../..'))
from src.pulsar_event_dispatcher import PulsarEventDispatcher


class CampaignManagementSagaIntegration:
    """Integración de Saga para el servicio de Campaign Management usando Apache Pulsar"""
    
    def __init__(self, event_dispatcher: PulsarEventDispatcher):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.event_dispatcher = event_dispatcher
        self._subscribe_to_events()
    
    def _subscribe_to_events(self):
        """Suscribirse a eventos relevantes"""
        self.event_dispatcher.subscribe("CampaignsEnabled", self._handle_campaigns_enabled)
        self.logger.info("Campaign Management service subscribed to saga events")
    
    def _handle_campaigns_enabled(self, event_data: Dict[str, Any]):
        """Maneja el evento de campañas habilitadas"""
        partner_id = event_data["partner_id"]
        campaign_permissions = event_data.get("campaign_permissions", {})
        correlation_id = event_data.get("correlation_id")
        causation_id = event_data.get("causation_id")
        
        self.logger.info(f"Processing campaigns enabled for partner: {partner_id}")
        
        try:
            # Simular procesamiento de habilitación de campañas
            # En una implementación real, aquí se configurarían las campañas del partner
            time.sleep(0.5)  # Simular tiempo de procesamiento
            
            # Configurar campañas para el partner
            self._configure_campaigns_for_partner(partner_id, campaign_permissions)
            
            # Publicar evento de confirmación
            self.event_dispatcher.publish("CampaignsEnabledConfirmed", {
                "partner_id": partner_id,
                "campaign_permissions": campaign_permissions,
                "configuration_status": "completed",
                "correlation_id": correlation_id,
                "causation_id": causation_id
            })
            
            self.logger.info(f"Campaigns successfully configured for partner: {partner_id}")
            
        except Exception as e:
            self.logger.error(f"Error processing campaigns enabled for partner {partner_id}: {str(e)}")
            
            # Publicar evento de error
            self.event_dispatcher.publish("CampaignsEnabledFailed", {
                "partner_id": partner_id,
                "error": str(e),
                "correlation_id": correlation_id,
                "causation_id": causation_id
            })
    
    def _configure_campaigns_for_partner(self, partner_id: str, permissions: Dict[str, Any]):
        """Configura las campañas para un partner"""
        # En una implementación real, aquí se haría:
        # - Crear configuración de campañas
        # - Establecer permisos
        # - Configurar límites de presupuesto
        # - Habilitar tipos de campañas permitidas
        
        self.logger.info(f"Configuring campaigns for partner {partner_id} with permissions: {permissions}")
        
        # Simular configuración
        campaign_config = {
            "partner_id": partner_id,
            "can_create_campaigns": permissions.get("can_create_campaigns", True),
            "max_budget": 10000.0,
            "allowed_campaign_types": ["DISPLAY", "SEARCH", "SOCIAL"],
            "created_at": datetime.utcnow().isoformat()
        }
        
        # En una implementación real, esto se guardaría en la base de datos
        self.logger.info(f"Campaign configuration created: {campaign_config}")


def create_campaign_saga_integration():
    """Factory function para crear la integración de saga de campañas"""
    try:
        event_dispatcher = PulsarEventDispatcher("campaign-management")
        return CampaignManagementSagaIntegration(event_dispatcher)
    except Exception as e:
        logging.error(f"Failed to create campaign saga integration: {e}")
        return None
