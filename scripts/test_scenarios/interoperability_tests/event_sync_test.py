"""
Prueba de interoperabilidad: Sincronización < 5 segundos entre servicios
"""

import asyncio
import time
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import sys
import os

# Agregar el directorio padre al path para importar utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.test_helpers import TestHelper, TestResult

logger = logging.getLogger(__name__)

class EventSyncTest:
    """Prueba de sincronización de eventos entre servicios"""
    
    def __init__(self, config_path: str = "config/test_config.yaml"):
        self.helper = TestHelper(config_path)
        self.config = self.helper.config['test_config']['interoperability']
        self.results: List[TestResult] = []
    
    async def run_sync_test(self) -> TestResult:
        """Ejecuta la prueba de sincronización de eventos"""
        test_name = "Event Synchronization Test"
        start_time = time.time()
        
        try:
            logger.info(f"Starting {test_name}")
            
            # Verificar que todos los servicios estén saludables
            services = await self.helper.check_all_services()
            unhealthy_services = [s for s in services if not s.healthy]
            if unhealthy_services:
                raise Exception(f"Unhealthy services: {[s.name for s in unhealthy_services]}")
            
            # Crear una Saga y monitorear la sincronización de eventos
            partner_id = f"sync_test_{int(time.time())}"
            logger.info(f"Creating test partner: {partner_id}")
            
            # Crear partner y medir tiempo de sincronización
            sync_metrics = await self._measure_event_synchronization(partner_id)
            
            # Verificar consistencia entre servicios
            consistency_metrics = await self._verify_service_consistency(partner_id)
            
            # Verificar sincronización del dashboard
            dashboard_metrics = await self._verify_dashboard_sync(partner_id)
            
            duration = time.time() - start_time
            
            # Combinar métricas
            metrics = {
                **sync_metrics,
                **consistency_metrics,
                **dashboard_metrics
            }
            
            # Validar resultados
            success = self._validate_sync_metrics(metrics)
            
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
    
    async def _measure_event_synchronization(self, partner_id: str) -> Dict[str, Any]:
        """Mide el tiempo de sincronización de eventos"""
        logger.info("Measuring event synchronization...")
        
        # Crear partner y medir tiempos de respuesta
        start_time = time.time()
        
        # Crear partner
        partner_result = await self.helper.create_test_partner(partner_id)
        if not partner_result or not partner_result.get('partner_id'):
            raise Exception("Failed to create test partner")
        
        creation_time = time.time() - start_time
        
        # Monitorear propagación de eventos
        max_sync_latency = self.config['max_sync_latency']
        check_interval = self.config['consistency_check_interval']
        max_checks = int(max_sync_latency / check_interval)
        
        sync_times = []
        events_detected = []
        
        for i in range(max_checks):
            await asyncio.sleep(check_interval)
            
            # Verificar estado en cada servicio
            check_start = time.time()
            
            # Verificar Partner Management
            pm_status = await self.helper.get_saga_status(partner_id)
            pm_time = time.time() - check_start
            
            # Verificar Dashboard
            dashboard_status = await self.helper.get_dashboard_status()
            dashboard_time = time.time() - check_start
            
            # Verificar que la Saga esté progresando
            if pm_status and pm_status.get('status'):
                sync_times.append(pm_time)
                events_detected.append({
                    'service': 'partner_management',
                    'time': pm_time,
                    'status': pm_status.get('status')
                })
            
            # Si la Saga está completa, detener el monitoreo
            if pm_status and pm_status.get('status') in ['completed', 'failed', 'compensated']:
                break
        
        return {
            "creation_time": creation_time,
            "sync_times": sync_times,
            "events_detected": events_detected,
            "max_sync_time": max(sync_times) if sync_times else 0,
            "avg_sync_time": sum(sync_times) / len(sync_times) if sync_times else 0
        }
    
    async def _verify_service_consistency(self, partner_id: str) -> Dict[str, Any]:
        """Verifica la consistencia entre servicios"""
        logger.info("Verifying service consistency...")
        
        # Obtener estado de la Saga desde diferentes perspectivas
        pm_status = await self.helper.get_saga_status(partner_id)
        dashboard_status = await self.helper.get_dashboard_status()
        
        # Verificar consistencia de datos
        consistency_checks = []
        
        if pm_status and dashboard_status:
            # Verificar que el partner_id sea consistente
            pm_partner_id = pm_status.get('partner_id')
            dashboard_sagas = dashboard_status.get('sagas', [])
            dashboard_partner_found = any(saga.get('partner_id') == partner_id for saga in dashboard_sagas)
            
            consistency_checks.append({
                'check': 'partner_id_consistency',
                'passed': pm_partner_id == partner_id,
                'pm_id': pm_partner_id,
                'expected_id': partner_id
            })
            
            consistency_checks.append({
                'check': 'dashboard_visibility',
                'passed': dashboard_partner_found,
                'found_in_dashboard': dashboard_partner_found
            })
        
        # Verificar que los eventos se propaguen correctamente
        timeline = await self.helper.get_saga_timeline(partner_id)
        timeline_consistency = timeline is not None and len(timeline.get('steps', [])) > 0
        
        consistency_checks.append({
            'check': 'timeline_consistency',
            'passed': timeline_consistency,
            'timeline_steps': len(timeline.get('steps', [])) if timeline else 0
        })
        
        return {
            "consistency_checks": consistency_checks,
            "total_checks": len(consistency_checks),
            "passed_checks": sum(1 for c in consistency_checks if c['passed']),
            "consistency_rate": sum(1 for c in consistency_checks if c['passed']) / len(consistency_checks) * 100 if consistency_checks else 0
        }
    
    async def _verify_dashboard_sync(self, partner_id: str) -> Dict[str, Any]:
        """Verifica la sincronización del dashboard"""
        logger.info("Verifying dashboard synchronization...")
        
        # Medir tiempo de respuesta del dashboard
        dashboard_times = []
        dashboard_updates = []
        
        for i in range(5):  # 5 verificaciones
            start_time = time.time()
            
            # Obtener estado del dashboard
            dashboard_status = await self.helper.get_dashboard_status()
            response_time = time.time() - start_time
            
            dashboard_times.append(response_time)
            dashboard_updates.append({
                'check': i + 1,
                'time': response_time,
                'timestamp': datetime.now().isoformat()
            })
            
            await asyncio.sleep(1)  # Esperar 1 segundo entre verificaciones
        
        # Verificar que el partner aparezca en el dashboard
        partner_found = False
        if dashboard_status and 'sagas' in dashboard_status:
            partner_found = any(saga.get('partner_id') == partner_id for saga in dashboard_status['sagas'])
        
        return {
            "dashboard_response_times": dashboard_times,
            "avg_dashboard_time": sum(dashboard_times) / len(dashboard_times),
            "max_dashboard_time": max(dashboard_times),
            "partner_found_in_dashboard": partner_found,
            "dashboard_updates": dashboard_updates
        }
    
    def _validate_sync_metrics(self, metrics: Dict[str, Any]) -> bool:
        """Valida las métricas de sincronización"""
        max_sync_latency = self.config['max_sync_latency']
        
        # Verificar tiempo máximo de sincronización
        sync_time_ok = metrics.get('max_sync_time', 0) <= max_sync_latency
        
        # Verificar consistencia entre servicios
        consistency_rate = metrics.get('consistency_rate', 0)
        consistency_ok = consistency_rate >= 90.0  # 90% de consistencia mínimo
        
        # Verificar tiempo de respuesta del dashboard
        dashboard_time_ok = metrics.get('max_dashboard_time', 0) <= 5.0  # 5 segundos máximo
        
        # Verificar que el partner aparezca en el dashboard
        dashboard_visibility_ok = metrics.get('partner_found_in_dashboard', False)
        
        logger.info(f"Sync time check: {sync_time_ok} (max: {metrics.get('max_sync_time', 0):.2f}s <= {max_sync_latency}s)")
        logger.info(f"Consistency check: {consistency_ok} (rate: {consistency_rate:.1f}% >= 90%)")
        logger.info(f"Dashboard time check: {dashboard_time_ok} (max: {metrics.get('max_dashboard_time', 0):.2f}s <= 5s)")
        logger.info(f"Dashboard visibility check: {dashboard_visibility_ok}")
        
        return sync_time_ok and consistency_ok and dashboard_time_ok and dashboard_visibility_ok

async def main():
    """Función principal"""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    test = EventSyncTest()
    result = await test.run_sync_test()
    
    # Agregar resultado al helper
    test.helper.add_result(result)
    
    # Mostrar resumen
    print(f"\n=== INTEROPERABILITY TEST SUMMARY ===")
    print(f"Success: {result.success}")
    print(f"Duration: {result.duration:.2f}s")
    print(f"Max Sync Time: {result.metrics.get('max_sync_time', 0):.2f}s")
    print(f"Consistency Rate: {result.metrics.get('consistency_rate', 0):.1f}%")
    print(f"Dashboard Max Time: {result.metrics.get('max_dashboard_time', 0):.2f}s")
    print(f"Partner Found in Dashboard: {result.metrics.get('partner_found_in_dashboard', False)}")
    
    # Guardar resultados
    test.helper.save_results()
    
    return result.success

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
