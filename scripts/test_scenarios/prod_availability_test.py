#!/usr/bin/env python3
"""
Prueba de disponibilidad para producción usando endpoints de HexaBuilders
"""

import asyncio
import time
import logging
import sys
import os

# Agregar el directorio padre al path para importar utils
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.test_helpers import TestHelper
from availability_tests.service_failure_test import ServiceFailureTest

logger = logging.getLogger(__name__)

class ProductionAvailabilityTest(ServiceFailureTest):
    """Prueba de disponibilidad adaptada para producción"""
    
    def __init__(self, config_path: str = "config/prod_config.yaml"):
        super().__init__(config_path)
        # Ajustar configuración para producción
        self.config = self.helper.config['test_config']['availability']
        self.config['max_recovery_time'] = 180  # Más tiempo para producción
        self.config['failure_simulation_duration'] = 30  # Más corto para producción
    
    async def run_production_availability_test(self):
        """Ejecuta la prueba de disponibilidad en producción"""
        test_name = "Production Availability Test"
        start_time = time.time()
        
        try:
            logger.info(f"Starting {test_name}")
            
            # Verificar que todos los servicios estén saludables
            services = await self.helper.check_all_services()
            unhealthy_services = [s for s in services if not s.healthy]
            if unhealthy_services:
                raise Exception(f"Unhealthy services: {[s.name for s in unhealthy_services]}")
            
            logger.info("All services are healthy, proceeding with availability test")
            
            # Crear un partner de prueba
            partner_id = f"prod_avail_{int(time.time())}"
            logger.info(f"Creating test partner: {partner_id}")
            
            partner_result = await self.helper.create_test_partner(partner_id)
            if not partner_result or not partner_result.get('partner_id'):
                raise Exception("Failed to create test partner")
            
            logger.info(f"Partner created successfully: {partner_result['partner_id']}")
            
            # Simular "falla" deshabilitando el servicio de campañas
            logger.info("Simulating service failure by disabling Campaign Management...")
            
            # Deshabilitar servicio de campañas
            disable_result = await self.helper.disable_campaign_service()
            if not disable_result:
                logger.warning("Could not disable campaign service, continuing with test")
            
            # Esperar un poco
            await asyncio.sleep(5)
            
            # Crear otro partner que debería fallar por timeout
            partner_id_2 = f"prod_avail_fail_{int(time.time())}"
            logger.info(f"Creating partner that should fail: {partner_id_2}")
            
            partner_result_2 = await self.helper.create_test_partner(partner_id_2)
            if partner_result_2 and partner_result_2.get('partner_id'):
                logger.info(f"Partner created: {partner_result_2['partner_id']}")
                
                # Esperar a que se active el timeout y compensación
                logger.info("Waiting for timeout and compensation...")
                await asyncio.sleep(40)  # Esperar timeout + compensación
                
                # Verificar que se activó la compensación
                saga_status = await self.helper.get_saga_status(partner_id_2)
                if saga_status:
                    status = saga_status.get('status', 'unknown')
                    logger.info(f"Saga status after timeout: {status}")
                    
                    if status in ['compensated', 'failed']:
                        logger.info("✅ Compensation activated successfully")
                        compensation_verified = True
                    else:
                        logger.warning(f"⚠️ Expected compensation, got: {status}")
                        compensation_verified = False
                else:
                    logger.warning("Could not get saga status")
                    compensation_verified = False
            else:
                logger.warning("Could not create second partner")
                compensation_verified = False
            
            # Rehabilitar servicio de campañas
            logger.info("Re-enabling Campaign Management service...")
            enable_result = await self.helper.enable_campaign_service()
            if enable_result:
                logger.info("Campaign service re-enabled successfully")
            else:
                logger.warning("Could not re-enable campaign service")
            
            # Verificar recuperación
            logger.info("Checking service recovery...")
            await asyncio.sleep(10)
            
            recovery_services = await self.helper.check_all_services()
            recovery_unhealthy = [s for s in recovery_services if not s.healthy]
            
            if not recovery_unhealthy:
                logger.info("✅ All services recovered successfully")
                recovery_verified = True
            else:
                logger.warning(f"⚠️ Some services still unhealthy: {[s.name for s in recovery_unhealthy]}")
                recovery_verified = False
            
            duration = time.time() - start_time
            
            metrics = {
                "total_duration": duration,
                "compensation_verified": compensation_verified,
                "recovery_verified": recovery_verified,
                "services_checked": len(services),
                "unhealthy_after_recovery": len(recovery_unhealthy)
            }
            
            # Validar resultados
            success = compensation_verified and recovery_verified
            
            logger.info(f"Compensation check: {compensation_verified}")
            logger.info(f"Recovery check: {recovery_verified}")
            
            return {
                "test_name": test_name,
                "success": success,
                "duration": duration,
                "metrics": metrics
            }
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Test {test_name} failed: {e}")
            return {
                "test_name": test_name,
                "success": False,
                "duration": duration,
                "metrics": {},
                "error_message": str(e)
            }

async def main():
    """Función principal"""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    print("🚀 PRUEBA DE DISPONIBILIDAD DE PRODUCCIÓN")
    print("=" * 50)
    
    test = ProductionAvailabilityTest()
    result = await test.run_production_availability_test()
    
    print(f"\n=== RESULTADO DE PRUEBA DE DISPONIBILIDAD ===")
    print(f"Éxito: {'✅ SÍ' if result['success'] else '❌ NO'}")
    print(f"Duración: {result['duration']:.2f}s")
    
    if 'metrics' in result and result['metrics']:
        metrics = result['metrics']
        print(f"Compensación verificada: {'✅ SÍ' if metrics.get('compensation_verified', False) else '❌ NO'}")
        print(f"Recuperación verificada: {'✅ SÍ' if metrics.get('recovery_verified', False) else '❌ NO'}")
        print(f"Servicios verificados: {metrics.get('services_checked', 0)}")
        print(f"Servicios no saludables después de recuperación: {metrics.get('unhealthy_after_recovery', 0)}")
    
    if 'error_message' in result:
        print(f"Error: {result['error_message']}")
    
    return result['success']

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
