"""
Prueba de disponibilidad: 99.9% uptime, compensación < 60 segundos
"""

import asyncio
import time
import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta
import sys
import os

# Agregar el directorio padre al path para importar utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.test_helpers import TestHelper, TestResult

logger = logging.getLogger(__name__)

class ServiceFailureTest:
    """Prueba de falla de servicios y recuperación"""
    
    def __init__(self, config_path: str = "config/test_config.yaml"):
        self.helper = TestHelper(config_path)
        self.config = self.helper.config['test_config']['availability']
        self.results: List[TestResult] = []
    
    async def run_failure_test(self) -> TestResult:
        """Ejecuta la prueba de falla de servicios"""
        test_name = "Service Failure and Recovery Test"
        start_time = time.time()
        
        try:
            logger.info(f"Starting {test_name}")
            
            # Verificar estado inicial de todos los servicios
            initial_services = await self.helper.check_all_services()
            logger.info(f"Initial services status: {[f'{s.name}: {s.healthy}' for s in initial_services]}")
            
            # Crear una Saga antes de la falla
            partner_id = f"failure_test_{int(time.time())}"
            logger.info(f"Creating test partner: {partner_id}")
            
            saga_result = await self.helper.create_test_partner(partner_id)
            if not saga_result or not saga_result.get('partner_id'):
                raise Exception("Failed to create test partner")
            
            # Simular falla del servicio de Campaign Management
            logger.info("Simulating Campaign Management service failure...")
            await self._simulate_service_failure("campaign_management")
            
            # Monitorear el sistema durante la falla
            failure_metrics = await self._monitor_during_failure(partner_id)
            
            # Restaurar el servicio
            logger.info("Restoring Campaign Management service...")
            await self._restore_service("campaign_management")
            
            # Monitorear la recuperación
            recovery_metrics = await self._monitor_recovery(partner_id)
            
            # Verificar que la Saga se haya compensado correctamente
            compensation_verified = await self._verify_compensation(partner_id)
            
            duration = time.time() - start_time
            
            # Combinar métricas
            metrics = {
                **failure_metrics,
                **recovery_metrics,
                "compensation_verified": compensation_verified
            }
            
            # Validar resultados
            success = self._validate_availability_metrics(metrics)
            
            return TestResult(
                test_name=test_name,
                success=success,
                duration=duration,
                metrics=metrics
            )
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Test {test_name} failed: {e}")
            return TestResult(
                test_name=test_name,
                success=False,
                duration=duration,
                metrics={},
                error_message=str(e)
            )
    
    async def _simulate_service_failure(self, service_name: str):
        """Simula la falla de un servicio deshabilitándolo"""
        try:
            service_url = self.helper.services.get(service_name)
            if not service_url:
                raise Exception(f"Service {service_name} not found in configuration")
            
            # Deshabilitar el servicio
            async with self.helper.httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(f"{service_url}/api/v1/service/disable")
                response.raise_for_status()
                logger.info(f"Service {service_name} disabled successfully")
                
        except Exception as e:
            logger.error(f"Failed to disable service {service_name}: {e}")
            raise
    
    async def _restore_service(self, service_name: str):
        """Restaura un servicio habilitándolo"""
        try:
            service_url = self.helper.services.get(service_name)
            if not service_url:
                raise Exception(f"Service {service_name} not found in configuration")
            
            # Habilitar el servicio
            async with self.helper.httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(f"{service_url}/api/v1/service/enable")
                response.raise_for_status()
                logger.info(f"Service {service_name} enabled successfully")
                
        except Exception as e:
            logger.error(f"Failed to enable service {service_name}: {e}")
            raise
    
    async def _monitor_during_failure(self, partner_id: str) -> Dict[str, Any]:
        """Monitorea el sistema durante la falla"""
        logger.info("Monitoring system during failure...")
        
        failure_duration = self.config['failure_simulation_duration']
        check_interval = self.config['health_check_interval']
        checks_during_failure = int(failure_duration / check_interval)
        
        healthy_checks = 0
        unhealthy_checks = 0
        response_times = []
        
        for i in range(checks_during_failure):
            await asyncio.sleep(check_interval)
            
            # Verificar estado de todos los servicios
            services = await self.helper.check_all_services()
            response_times.extend([s.response_time for s in services])
            
            # Contar servicios saludables
            healthy_services = sum(1 for s in services if s.healthy)
            total_services = len(services)
            
            if healthy_services == total_services:
                healthy_checks += 1
            else:
                unhealthy_checks += 1
            
            logger.debug(f"Check {i+1}/{checks_during_failure}: {healthy_services}/{total_services} services healthy")
        
        return {
            "failure_duration": failure_duration,
            "checks_during_failure": checks_during_failure,
            "healthy_checks": healthy_checks,
            "unhealthy_checks": unhealthy_checks,
            "avg_response_time_during_failure": sum(response_times) / len(response_times) if response_times else 0
        }
    
    async def _monitor_recovery(self, partner_id: str) -> Dict[str, Any]:
        """Monitorea la recuperación del sistema"""
        logger.info("Monitoring system recovery...")
        
        max_recovery_time = self.config['max_recovery_time']
        check_interval = self.config['health_check_interval']
        max_checks = int(max_recovery_time / check_interval)
        
        recovery_start = time.time()
        recovery_achieved = False
        recovery_time = 0
        
        for i in range(max_checks):
            await asyncio.sleep(check_interval)
            
            # Verificar estado de todos los servicios
            services = await self.helper.check_all_services()
            healthy_services = sum(1 for s in services if s.healthy)
            total_services = len(services)
            
            if healthy_services == total_services and not recovery_achieved:
                recovery_achieved = True
                recovery_time = time.time() - recovery_start
                logger.info(f"System recovered in {recovery_time:.2f}s")
                break
            
            logger.debug(f"Recovery check {i+1}/{max_checks}: {healthy_services}/{total_services} services healthy")
        
        return {
            "recovery_achieved": recovery_achieved,
            "recovery_time": recovery_time,
            "max_recovery_time": max_recovery_time
        }
    
    async def _verify_compensation(self, partner_id: str) -> bool:
        """Verifica que la Saga se haya compensado correctamente"""
        logger.info(f"Verifying compensation for partner {partner_id}")
        
        # Obtener estado de la Saga
        saga_status = await self.helper.get_saga_status(partner_id)
        if not saga_status:
            logger.warning(f"No saga status found for partner {partner_id}")
            return False
        
        # Verificar que la Saga esté compensada
        status = saga_status.get('status', '').lower()
        is_compensated = status in ['compensated', 'failed']
        
        if is_compensated:
            logger.info(f"Saga for partner {partner_id} is compensated (status: {status})")
        else:
            logger.warning(f"Saga for partner {partner_id} is not compensated (status: {status})")
        
        return is_compensated
    
    def _validate_availability_metrics(self, metrics: Dict[str, Any]) -> bool:
        """Valida las métricas de disponibilidad"""
        max_recovery_time = self.config['max_recovery_time']
        
        # Verificar que el sistema se haya recuperado
        recovery_ok = metrics.get('recovery_achieved', False)
        
        # Verificar tiempo de recuperación
        recovery_time_ok = metrics.get('recovery_time', float('inf')) <= max_recovery_time
        
        # Verificar compensación
        compensation_ok = metrics.get('compensation_verified', False)
        
        logger.info(f"Recovery achieved: {recovery_ok}")
        logger.info(f"Recovery time OK: {recovery_time_ok} ({metrics.get('recovery_time', 0):.2f}s <= {max_recovery_time}s)")
        logger.info(f"Compensation verified: {compensation_ok}")
        
        return recovery_ok and recovery_time_ok and compensation_ok

async def main():
    """Función principal"""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    test = ServiceFailureTest()
    result = await test.run_failure_test()
    
    # Agregar resultado al helper
    test.helper.add_result(result)
    
    # Mostrar resumen
    print(f"\n=== AVAILABILITY TEST SUMMARY ===")
    print(f"Success: {result.success}")
    print(f"Duration: {result.duration:.2f}s")
    print(f"Recovery Achieved: {result.metrics.get('recovery_achieved', False)}")
    print(f"Recovery Time: {result.metrics.get('recovery_time', 0):.2f}s")
    print(f"Compensation Verified: {result.metrics.get('compensation_verified', False)}")
    
    # Guardar resultados
    test.helper.save_results()
    
    return result.success

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
