"""
Cliente para comunicarse con el servicio de Saga.
Maneja las llamadas HTTP al servicio de Partner Management.
"""

import httpx
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from .config import settings

logger = logging.getLogger(__name__)


class SagaClient:
    """Cliente para el servicio de Saga"""
    
    def __init__(self, base_url: str = None):
        self.base_url = base_url or settings.SAGA_SERVICE_URL
        self.timeout = settings.SAGA_SERVICE_TIMEOUT
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def start_partner_onboarding(self, partner_data: Dict[str, Any], correlation_id: Optional[str] = None) -> Dict[str, Any]:
        """Inicia el proceso de onboarding de un partner"""
        try:
            payload = {
                "partner_data": partner_data,
                "correlation_id": correlation_id
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/saga/partner-onboarding",
                    json=payload
                )
                response.raise_for_status()
                return response.json()
                
        except httpx.HTTPStatusError as e:
            self.logger.error("HTTP error starting partner onboarding: %s", str(e))
            raise Exception(f"HTTP error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            self.logger.error("Error starting partner onboarding: %s", str(e))
            raise
    
    async def get_saga_status(self, partner_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene el estado de una Saga"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/api/v1/saga/{partner_id}/status")
                
                if response.status_code == 404:
                    return None
                
                response.raise_for_status()
                return response.json()
                
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            self.logger.error("HTTP error getting saga status: %s", str(e))
            raise Exception(f"HTTP error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            self.logger.error("Error getting saga status: %s", str(e))
            raise
    
    async def compensate_saga(self, partner_id: str, reason: str = "Manual compensation request") -> Dict[str, Any]:
        """Inicia la compensación de una Saga"""
        try:
            payload = {"reason": reason}
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/saga/{partner_id}/compensate",
                    json=payload
                )
                response.raise_for_status()
                return response.json()
                
        except httpx.HTTPStatusError as e:
            self.logger.error("HTTP error compensating saga: %s", str(e))
            raise Exception(f"HTTP error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            self.logger.error("Error compensating saga: %s", str(e))
            raise
    
    async def health_check(self) -> Dict[str, Any]:
        """Verifica el estado de salud del servicio"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/api/v1/saga/health")
                response.raise_for_status()
                return response.json()
                
        except httpx.HTTPStatusError as e:
            self.logger.error("HTTP error in health check: %s", str(e))
            raise Exception(f"HTTP error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            self.logger.error("Error in health check: %s", str(e))
            raise


# Instancia global del cliente
saga_client = SagaClient()
