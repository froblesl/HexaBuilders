"""
Prueba de escalabilidad: 100 registros de partners/min, latencia < 30 segundos
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

class ScalabilityTest:
    """Prueba de escalabilidad del sistema"""
    
    def __init__(self, config_path: str = "config/test_config.yaml"):
        self.helper = TestHelper(config_path)
        self.config = self.helper.config['test_config']['scalability']
        self.results: List[TestResult] = []
    
    async def run_load_test(self) -> TestResult:
        """Ejecuta la prueba de carga"""
        test_name = "Scalability Load Test"
        start_time = time.time()
        
        try:
            logger.info(f"Starting {test_name}")
            
            # Verificar que todos los servicios estén saludables
            services = await self.helper.check_all_services()
            unhealthy_services = [s for s in services if not s.healthy]
            if unhealthy_services:
                raise Exception(f"Unhealthy services: {[s.name for s in unhealthy_services]}")
            
            # Configurar parámetros de la prueba
            target_throughput = self.config['target_throughput']  # registros por minuto
            test_duration = self.config['test_duration']  # segundos
            concurrent_users = self.config['concurrent_users']
            ramp_up_time = self.config['ramp_up_time']
            
            # Calcular intervalos
            total_requests = int(target_throughput * test_duration / 60)
            request_interval = test_duration / total_requests
            
            logger.info(f"Target: {target_throughput} requests/min for {test_duration}s")
            logger.info(f"Total requests: {total_requests}, interval: {request_interval:.2f}s")
            
            # Ejecutar prueba de carga
            metrics = await self._execute_load_test(
                total_requests, request_interval, concurrent_users, ramp_up_time
            )
            
            duration = time.time() - start_time
            
            # Verificar métricas
            success = self._validate_metrics(metrics)
            
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
    
    async def _execute_load_test(self, total_requests: int, request_interval: float, 
                                concurrent_users: int, ramp_up_time: float) -> Dict[str, Any]:
        """Ejecuta la prueba de carga real"""
        
        # Crear semáforo para limitar concurrencia
        semaphore = asyncio.Semaphore(concurrent_users)
        
        # Listas para métricas
        response_times = []
        success_count = 0
        error_count = 0
        start_times = []
        end_times = []
        
        async def make_request(request_id: int):
            """Hace una petición individual"""
            async with semaphore:
                try:
                    start_time = time.time()
                    start_times.append(start_time)
                    
                    # Crear partner de prueba
                    partner_id = f"load_test_{request_id}_{int(start_time)}"
                    result = await self.helper.create_test_partner(partner_id)
                    
                    end_time = time.time()
                    end_times.append(end_time)
                    
                    response_time = end_time - start_time
                    response_times.append(response_time)
                    
                    if result and result.get('partner_id'):
                        success_count += 1
                        logger.debug(f"Request {request_id} completed in {response_time:.2f}s")
                    else:
                        error_count += 1
                        logger.warning(f"Request {request_id} failed")
                    
                except Exception as e:
                    error_count += 1
                    logger.error(f"Request {request_id} error: {e}")
        
        # Ejecutar requests con ramp-up
        tasks = []
        for i in range(total_requests):
            # Calcular delay para ramp-up
            if i < concurrent_users:
                delay = i * (ramp_up_time / concurrent_users)
            else:
                delay = i * request_interval
            
            # Programar request
            task = asyncio.create_task(self._delayed_request(make_request, i, delay))
            tasks.append(task)
        
        # Esperar a que terminen todas las tareas
        await asyncio.gather(*tasks, return_exceptions=True)
        
        # Calcular métricas
        total_requests_made = len(start_times)
        actual_duration = max(end_times) - min(start_times) if start_times else 0
        actual_throughput = (success_count / actual_duration * 60) if actual_duration > 0 else 0
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        max_response_time = max(response_times) if response_times else 0
        min_response_time = min(response_times) if response_times else 0
        success_rate = (success_count / total_requests_made * 100) if total_requests_made > 0 else 0
        
        return {
            "total_requests": total_requests_made,
            "successful_requests": success_count,
            "failed_requests": error_count,
            "success_rate": success_rate,
            "actual_throughput": actual_throughput,
            "target_throughput": self.config['target_throughput'],
            "actual_duration": actual_duration,
            "avg_response_time": avg_response_time,
            "max_response_time": max_response_time,
            "min_response_time": min_response_time,
            "concurrent_users": concurrent_users
        }
    
    async def _delayed_request(self, func, request_id: int, delay: float):
        """Ejecuta una función con delay"""
        await asyncio.sleep(delay)
        await func(request_id)
    
    def _validate_metrics(self, metrics: Dict[str, Any]) -> bool:
        """Valida si las métricas cumplen con los requisitos"""
        max_latency = self.config['max_latency']
        target_throughput = self.config['target_throughput']
        
        # Verificar latencia máxima
        latency_ok = metrics['max_response_time'] <= max_latency
        
        # Verificar throughput mínimo (80% del objetivo)
        throughput_ok = metrics['actual_throughput'] >= (target_throughput * 0.8)
        
        # Verificar tasa de éxito (95% mínimo)
        success_rate_ok = metrics['success_rate'] >= 95.0
        
        logger.info(f"Latency check: {latency_ok} (max: {metrics['max_response_time']:.2f}s <= {max_latency}s)")
        logger.info(f"Throughput check: {throughput_ok} (actual: {metrics['actual_throughput']:.2f} >= {target_throughput * 0.8:.2f})")
        logger.info(f"Success rate check: {success_rate_ok} (actual: {metrics['success_rate']:.2f}% >= 95%)")
        
        return latency_ok and throughput_ok and success_rate_ok

async def main():
    """Función principal"""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    test = ScalabilityTest()
    result = await test.run_load_test()
    
    # Agregar resultado al helper
    test.helper.add_result(result)
    
    # Mostrar resumen
    summary = test.helper.get_summary()
    print(f"\n=== SCALABILITY TEST SUMMARY ===")
    print(f"Success: {result.success}")
    print(f"Duration: {result.duration:.2f}s")
    print(f"Throughput: {result.metrics.get('actual_throughput', 0):.2f} requests/min")
    print(f"Max Latency: {result.metrics.get('max_response_time', 0):.2f}s")
    print(f"Success Rate: {result.metrics.get('success_rate', 0):.2f}%")
    
    # Guardar resultados
    test.helper.save_results()
    
    return result.success

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
