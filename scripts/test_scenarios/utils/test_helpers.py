"""
Utilidades para pruebas de escenarios de calidad.
"""

import asyncio
import httpx
import time
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import yaml
import os

logger = logging.getLogger(__name__)

@dataclass
class TestResult:
    """Resultado de una prueba individual"""
    test_name: str
    success: bool
    duration: float
    metrics: Dict[str, Any]
    error_message: Optional[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

@dataclass
class ServiceStatus:
    """Estado de un servicio"""
    name: str
    url: str
    healthy: bool
    response_time: float
    last_check: datetime
    error_message: Optional[str] = None

class TestHelper:
    """Clase helper para pruebas"""
    
    def __init__(self, config_path: str = "config/test_config.yaml"):
        self.config = self._load_config(config_path)
        self.services = self.config['test_config']['services']
        self.results: List[TestResult] = []
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Carga la configuración desde archivo YAML"""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.warning(f"Config file {config_path} not found, using defaults")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Configuración por defecto"""
        return {
            'test_config': {
                'services': {
                    'partner_management': 'http://localhost:5000',
                    'bff_web': 'http://localhost:8000',
                    'campaign_management': 'http://localhost:5003',
                    'onboarding': 'http://localhost:5001',
                    'recruitment': 'http://localhost:5002',
                    'notifications': 'http://localhost:5004'
                }
            }
        }
    
    async def check_service_health(self, service_name: str, url: str) -> ServiceStatus:
        """Verifica el estado de salud de un servicio"""
        start_time = time.time()
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{url}/health")
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    return ServiceStatus(
                        name=service_name,
                        url=url,
                        healthy=data.get('status') == 'healthy',
                        response_time=response_time,
                        last_check=datetime.now()
                    )
                else:
                    return ServiceStatus(
                        name=service_name,
                        url=url,
                        healthy=False,
                        response_time=response_time,
                        last_check=datetime.now(),
                        error_message=f"HTTP {response.status_code}"
                    )
        except Exception as e:
            response_time = time.time() - start_time
            return ServiceStatus(
                name=service_name,
                url=url,
                healthy=False,
                response_time=response_time,
                last_check=datetime.now(),
                error_message=str(e)
            )
    
    async def check_all_services(self) -> List[ServiceStatus]:
        """Verifica el estado de todos los servicios"""
        tasks = []
        for name, url in self.services.items():
            tasks.append(self.check_service_health(name, url))
        
        return await asyncio.gather(*tasks)
    
    async def create_test_partner(self, partner_id: str = None) -> Dict[str, Any]:
        """Crea un partner de prueba"""
        if partner_id is None:
            partner_id = f"test_partner_{int(time.time())}"
        
        partner_data = {
            "partner_id": partner_id,
            "nombre": f"Test Partner {partner_id}",
            "email": f"test_{partner_id}@example.com",
            "telefono": "+1234567890",
            "tipo_partner": "EMPRESA",
            "direccion": "123 Test Street",
            "ciudad": "Test City",
            "pais": "US"
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.services['partner_management']}/api/v1/saga/partner-onboarding",
                    json={"partner_data": partner_data}
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error creating test partner: {e}")
            raise
    
    async def create_test_partner_bff(self, partner_id: str = None) -> Dict[str, Any]:
        """Crea un partner de prueba usando BFF GraphQL"""
        if partner_id is None:
            partner_id = f"test_bff_partner_{int(time.time())}"
        
        query = """
        mutation StartPartnerOnboarding($input: PartnerOnboardingInput!) {
            startPartnerOnboarding(input: $input) {
                success
                message
                partnerId
                sagaState {
                    status
                    completedSteps
                    failedSteps
                }
                timestamp
            }
        }
        """
        
        variables = {
            "input": {
                "partnerData": {
                    "partnerId": partner_id,
                    "nombre": f"Test BFF Partner {partner_id}",
                    "email": f"test_bff_{partner_id}@example.com",
                    "telefono": "+1234567890",
                    "tipoPartner": "EMPRESA",
                    "preferredContractType": "BASIC",
                    "requiredDocuments": ["IDENTITY", "BUSINESS_REGISTRATION"],
                    "campaignPermissions": "can_create_campaigns",
                    "recruitmentPreferences": "job_posting_enabled"
                },
                "correlationId": f"test-{int(time.time())}"
            }
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.services['bff_web']}/api/v1/graphql",
                    json={"query": query, "variables": variables}
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error creating test partner via BFF: {e}")
            raise
    
    async def get_saga_status(self, partner_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene el estado de una Saga"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.services['partner_management']}/api/v1/saga/{partner_id}/status"
                )
                if response.status_code == 404:
                    return None
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error getting saga status: {e}")
            return None
    
    async def get_dashboard_status(self) -> Dict[str, Any]:
        """Obtiene el estado del dashboard"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.services['partner_management']}/api/v1/saga-dashboard/system-status"
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error getting dashboard status: {e}")
            return {}
    
    async def get_saga_timeline(self, partner_id: str) -> Dict[str, Any]:
        """Obtiene la timeline de una Saga"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.services['partner_management']}/api/v1/saga-dashboard/timeline/{partner_id}"
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error getting saga timeline: {e}")
            return {}
    
    def add_result(self, result: TestResult):
        """Agrega un resultado de prueba"""
        self.results.append(result)
        logger.info(f"Test {result.test_name}: {'PASS' if result.success else 'FAIL'}")
    
    def get_summary(self) -> Dict[str, Any]:
        """Obtiene un resumen de los resultados"""
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.success)
        failed_tests = total_tests - passed_tests
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            "total_duration": sum(r.duration for r in self.results),
            "average_duration": sum(r.duration for r in self.results) / total_tests if total_tests > 0 else 0
        }
    
    def save_results(self, filename: str = None):
        """Guarda los resultados en un archivo"""
        if filename is None:
            filename = f"reports/test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        results_data = {
            "summary": self.get_summary(),
            "results": [
                {
                    "test_name": r.test_name,
                    "success": r.success,
                    "duration": r.duration,
                    "metrics": r.metrics,
                    "error_message": r.error_message,
                    "timestamp": r.timestamp.isoformat()
                }
                for r in self.results
            ]
        }
        
        import json
        with open(filename, 'w') as f:
            json.dump(results_data, f, indent=2)
        
        logger.info(f"Results saved to {filename}")
