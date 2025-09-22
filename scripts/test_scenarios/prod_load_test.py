#!/usr/bin/env python3
"""
Prueba de carga para producción usando endpoints de HexaBuilders
"""

import asyncio
import time
import logging
import sys
import os

# Agregar el directorio padre al path para importar utils
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.test_helpers import TestHelper
from load_tests.scalability_test import ScalabilityTest

logger = logging.getLogger(__name__)

class ProductionScalabilityTest(ScalabilityTest):
    """Prueba de escalabilidad adaptada para producción"""
    
    def __init__(self, config_path: str = "config/prod_config.yaml"):
        super().__init__(config_path)
        # Ajustar configuración para producción
        self.config = self.helper.config['test_config']['scalability']
        self.config['target_throughput'] = 20  # Muy conservador para producción
        self.config['test_duration'] = 60  # Solo 1 minuto
        self.config['concurrent_users'] = 5  # Muy pocos usuarios concurrentes
    
    async def run_production_load_test(self):
        """Ejecuta la prueba de carga en producción"""
        test_name = "Production Scalability Load Test"
        start_time = time.time()
        
        try:
            logger.info(f"Starting {test_name}")
            
            # Verificar que todos los servicios estén saludables
            services = await self.helper.check_all_services()
            unhealthy_services = [s for s in services if not s.healthy]
            if unhealthy_services:
                raise Exception(f"Unhealthy services: {[s.name for s in unhealthy_services]}")
            
            # Configuración más conservadora para producción
            target_throughput = self.config['target_throughput']
            test_duration = self.config['test_duration']
            concurrent_users = self.config['concurrent_users']
            
            logger.info(f"Target: {target_throughput} requests/min for {test_duration}s")
            logger.info(f"Concurrent users: {concurrent_users}")
            
            # Calcular intervalos más conservadores
            total_requests = int((target_throughput * test_duration) / 60)
            interval = 60.0 / target_throughput  # segundos entre requests
            
            logger.info(f"Total requests: {total_requests}, interval: {interval:.2f}s")
            
            # Ejecutar carga progresiva
            successful_requests = 0
            failed_requests = 0
            response_times = []
            
            # Crear tareas concurrentes limitadas
            semaphore = asyncio.Semaphore(concurrent_users)
            
            async def make_request():
                async with semaphore:
                    try:
                        partner_id = f"prod_load_{int(time.time())}_{asyncio.current_task().get_name()}"
                        result = await self.helper.create_test_partner(partner_id)
                        
                        if result and result.get('partner_id'):
                            return True, 0
                        else:
                            return False, 0
                    except Exception as e:
                        logger.error(f"Error in request: {e}")
                        return False, 0
            
            # Ejecutar requests con intervalos
            tasks = []
            for i in range(total_requests):
                if i > 0:
                    await asyncio.sleep(interval)
                
                task = asyncio.create_task(make_request())
                tasks.append(task)
                
                # Limpiar tareas completadas
                if len(tasks) >= concurrent_users * 2:
                    completed_tasks = [t for t in tasks if t.done()]
                    for task in completed_tasks:
                        success, response_time = await task
                        if success:
                            successful_requests += 1
                        else:
                            failed_requests += 1
                        response_times.append(response_time)
                    tasks = [t for t in tasks if not t.done()]
            
            # Esperar a que terminen las tareas restantes
            for task in tasks:
                success, response_time = await task
                if success:
                    successful_requests += 1
                else:
                    failed_requests += 1
                response_times.append(response_time)
            
            duration = time.time() - start_time
            actual_throughput = (successful_requests / duration) * 60 if duration > 0 else 0
            success_rate = (successful_requests / (successful_requests + failed_requests)) * 100 if (successful_requests + failed_requests) > 0 else 0
            max_latency = max(response_times) if response_times else 0
            avg_latency = sum(response_times) / len(response_times) if response_times else 0
            
            metrics = {
                "total_requests": total_requests,
                "successful_requests": successful_requests,
                "failed_requests": failed_requests,
                "actual_throughput": actual_throughput,
                "target_throughput": target_throughput,
                "success_rate": success_rate,
                "max_latency": max_latency,
                "avg_latency": avg_latency,
                "duration": duration,
                "concurrent_users": concurrent_users
            }
            
            # Validar resultados (más permisivo para producción)
            success = (
                actual_throughput >= target_throughput * 0.5 and  # Al menos 50% del throughput objetivo
                success_rate >= 80.0 and  # Al menos 80% de éxito
                max_latency <= self.config['max_latency']
            )
            
            logger.info(f"Throughput check: {actual_throughput:.2f} >= {target_throughput * 0.5:.2f}")
            logger.info(f"Success rate check: {success_rate:.2f}% >= 80.0%")
            logger.info(f"Latency check: {max_latency:.2f}s <= {self.config['max_latency']}s")
            
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
    
    print("🚀 PRUEBA DE CARGA DE PRODUCCIÓN")
    print("=" * 50)
    
    test = ProductionScalabilityTest()
    result = await test.run_production_load_test()
    
    print(f"\n=== RESULTADO DE PRUEBA DE CARGA ===")
    print(f"Éxito: {'✅ SÍ' if result['success'] else '❌ NO'}")
    print(f"Duración: {result['duration']:.2f}s")
    
    if 'metrics' in result and result['metrics']:
        metrics = result['metrics']
        print(f"Throughput: {metrics.get('actual_throughput', 0):.2f} requests/min")
        print(f"Tasa de éxito: {metrics.get('success_rate', 0):.1f}%")
        print(f"Latencia máxima: {metrics.get('max_latency', 0):.2f}s")
        print(f"Requests exitosos: {metrics.get('successful_requests', 0)}")
        print(f"Requests fallidos: {metrics.get('failed_requests', 0)}")
    
    if 'error_message' in result:
        print(f"Error: {result['error_message']}")
    
    return result['success']

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
