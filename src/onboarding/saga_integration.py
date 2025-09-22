"""
Integración de Saga para el servicio de Onboarding.
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


class OnboardingSagaIntegration:
    """Integración de Saga para el servicio de Onboarding usando Apache Pulsar"""
    
    def __init__(self, event_dispatcher: PulsarEventDispatcher):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.event_dispatcher = event_dispatcher
        self._subscribe_to_events()
    
    def _subscribe_to_events(self):
        """Suscribirse a eventos relevantes"""
        # Eventos normales
        self.event_dispatcher.subscribe("PartnerOnboardingInitiated", self._handle_partner_onboarding_initiated)
        self.event_dispatcher.subscribe("ContractCreationRequested", self._handle_contract_creation_requested)
        self.event_dispatcher.subscribe("DocumentVerificationRequested", self._handle_document_verification_requested)
        
        # Eventos de compensación
        self.event_dispatcher.subscribe("ContractCancellationRequested", self._handle_contract_cancellation_requested)
        self.event_dispatcher.subscribe("DocumentVerificationRevertRequested", self._handle_document_verification_revert_requested)
        self.event_dispatcher.subscribe("PartnerRegistrationRevertRequested", self._handle_partner_registration_revert_requested)
    
    def _handle_partner_onboarding_initiated(self, event_data: Dict[str, Any]):
        """Maneja el evento de onboarding iniciado"""
        partner_id = event_data["partner_id"]
        self.logger.info(f"Onboarding service received: Partner onboarding initiated for {partner_id}")
        
        try:
            # Procesar registro del partner
            self.logger.info(f"Processing partner registration for {partner_id}")
            
            # Simular procesamiento
            time.sleep(1)
            
            # Publicar evento de completado
            self.event_dispatcher.publish("PartnerRegistrationCompleted", {
                "partner_id": partner_id,
                "correlation_id": event_data["correlation_id"],
                "causation_id": event_data["causation_id"]
            })
            
            self.logger.info(f"Partner {partner_id} registration completed")
            
        except Exception as e:
            self.logger.error(f"Error processing partner registration for {partner_id}: {str(e)}")
    
    def _handle_contract_creation_requested(self, event_data: Dict[str, Any]):
        """Maneja la solicitud de creación de contrato"""
        partner_id = event_data["partner_id"]
        self.logger.info(f"Creating contract for partner {partner_id}")
        
        try:
            # Simular creación de contrato
            time.sleep(1)
            
            contract_id = f"contract_{partner_id}_{int(datetime.now().timestamp())}"
            
            # Publicar evento de contrato creado
            self.event_dispatcher.publish("ContractCreated", {
                "partner_id": partner_id,
                "contract_id": contract_id,
                "correlation_id": event_data["correlation_id"],
                "causation_id": event_data["causation_id"]
            })
            
            self.logger.info(f"Contract {contract_id} created for partner {partner_id}")
            
        except Exception as e:
            self.logger.error(f"Error creating contract for {partner_id}: {str(e)}")
    
    def _handle_document_verification_requested(self, event_data: Dict[str, Any]):
        """Maneja la solicitud de verificación de documentos"""
        partner_id = event_data["partner_id"]
        self.logger.info(f"Verifying documents for partner {partner_id}")
        
        try:
            # Simular verificación de documentos
            time.sleep(1)
            
            package_id = f"package_{partner_id}_{int(datetime.now().timestamp())}"
            
            # Publicar evento de documentos verificados
            self.event_dispatcher.publish("DocumentsVerified", {
                "partner_id": partner_id,
                "package_id": package_id,
                "correlation_id": event_data["correlation_id"],
                "causation_id": event_data["causation_id"]
            })
            
            self.logger.info(f"Documents verified for partner {partner_id}, package {package_id}")
            
        except Exception as e:
            self.logger.error(f"Error verifying documents for {partner_id}: {str(e)}")
    
    def _handle_contract_cancellation_requested(self, event_data: Dict[str, Any]):
        """Maneja la solicitud de cancelación de contrato (compensación)"""
        partner_id = event_data["partner_id"]
        saga_id = event_data.get("saga_id")
        self.logger.info(f"Compensating: Cancelling contract for partner {partner_id}")
        
        try:
            # Simular cancelación de contrato
            time.sleep(0.5)
            
            # Aquí iría la lógica real de cancelación:
            # - Marcar contrato como cancelado en BD
            # - Revertir permisos otorgados
            # - Notificar sistemas dependientes
            
            # Publicar evento de contrato cancelado
            self.event_dispatcher.publish("ContractCancelled", {
                "partner_id": partner_id,
                "saga_id": saga_id,
                "correlation_id": event_data["correlation_id"],
                "causation_id": event_data["causation_id"],
                "step": "contract_creation"
            })
            
            self.logger.info(f"Contract cancelled for partner {partner_id} (compensation completed)")
            
        except Exception as e:
            self.logger.error(f"Error cancelling contract for {partner_id}: {str(e)}")
            # En caso de error, aún publicamos el evento para continuar la compensación
            self.event_dispatcher.publish("ContractCancelled", {
                "partner_id": partner_id,
                "saga_id": saga_id,
                "correlation_id": event_data["correlation_id"],
                "causation_id": event_data["causation_id"],
                "step": "contract_creation",
                "error": str(e)
            })
    
    def _handle_document_verification_revert_requested(self, event_data: Dict[str, Any]):
        """Maneja la solicitud de reversión de verificación de documentos (compensación)"""
        partner_id = event_data["partner_id"]
        saga_id = event_data.get("saga_id")
        self.logger.info(f"Compensating: Reverting document verification for partner {partner_id}")
        
        try:
            # Simular reversión de verificación
            time.sleep(0.5)
            
            # Aquí iría la lógica real de reversión:
            # - Marcar documentos como no verificados
            # - Revertir estado de verificación
            # - Limpiar metadatos de verificación
            
            # Publicar evento de verificación revertida
            self.event_dispatcher.publish("DocumentVerificationReverted", {
                "partner_id": partner_id,
                "saga_id": saga_id,
                "correlation_id": event_data["correlation_id"],
                "causation_id": event_data["causation_id"],
                "step": "document_verification"
            })
            
            self.logger.info(f"Document verification reverted for partner {partner_id} (compensation completed)")
            
        except Exception as e:
            self.logger.error(f"Error reverting document verification for {partner_id}: {str(e)}")
            # En caso de error, aún publicamos el evento para continuar la compensación
            self.event_dispatcher.publish("DocumentVerificationReverted", {
                "partner_id": partner_id,
                "saga_id": saga_id,
                "correlation_id": event_data["correlation_id"],
                "causation_id": event_data["causation_id"],
                "step": "document_verification",
                "error": str(e)
            })
    
    def _handle_partner_registration_revert_requested(self, event_data: Dict[str, Any]):
        """Maneja la solicitud de reversión de registro de partner (compensación)"""
        partner_id = event_data["partner_id"]
        saga_id = event_data.get("saga_id")
        self.logger.info(f"Compensating: Reverting partner registration for partner {partner_id}")
        
        try:
            # Simular reversión de registro
            time.sleep(0.5)
            
            # Aquí iría la lógica real de reversión:
            # - Marcar partner como inactivo o eliminado
            # - Revertir datos de registro
            # - Limpiar permisos y configuraciones
            
            # Publicar evento de registro revertido
            self.event_dispatcher.publish("PartnerRegistrationReverted", {
                "partner_id": partner_id,
                "saga_id": saga_id,
                "correlation_id": event_data["correlation_id"],
                "causation_id": event_data["causation_id"],
                "step": "partner_registration"
            })
            
            self.logger.info(f"Partner registration reverted for partner {partner_id} (compensation completed)")
            
        except Exception as e:
            self.logger.error(f"Error reverting partner registration for {partner_id}: {str(e)}")
            # En caso de error, aún publicamos el evento para continuar la compensación
            self.event_dispatcher.publish("PartnerRegistrationReverted", {
                "partner_id": partner_id,
                "saga_id": saga_id,
                "correlation_id": event_data["correlation_id"],
                "causation_id": event_data["causation_id"],
                "step": "partner_registration",
                "error": str(e)
            })

    def handle_partner_onboarding_initiated(self, event_data: Dict[str, Any]):
        """Método público para compatibilidad con endpoints REST"""
        return self._handle_partner_onboarding_initiated(event_data)
