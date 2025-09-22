#!/usr/bin/env python3
"""
Script principal para ejecutar todas las pruebas de escenarios de calidad.
"""

import asyncio
import logging
import sys
import os
from datetime import datetime
from typing import List, Dict, Any

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.test_helpers import TestHelper, TestResult
from load_tests.scalability_test import ScalabilityTest
from availability_tests.service_failure_test import ServiceFailureTest
from interoperability_tests.event_sync_test import EventSyncTest

logger = logging.getLogger(__name__)

class TestRunner:
    """Ejecutor principal de todas las pruebas"""
    
    def __init__(self, config_path: str = "config/test_config.yaml"):
        self.helper = TestHelper(config_path)
        self.results: List[TestResult] = []
        self.test_suites = [
            ("Scalability", ScalabilityTest),
            ("Availability", ServiceFailureTest),
            ("Interoperability", EventSyncTest),
        ]
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Ejecuta todas las pruebas de escenarios"""
        logger.info("Starting comprehensive quality scenario testing...")
        
        # Verificar que todos los servicios estén disponibles
        logger.info("Checking service availability...")
        services = await self.helper.check_all_services()
        unhealthy_services = [s for s in services if not s.healthy]
        
        if unhealthy_services:
            logger.error(f"Unhealthy services detected: {[s.name for s in unhealthy_services]}")
            logger.error("Please ensure all services are running before running tests")
            return {"success": False, "error": "Unhealthy services detected"}
        
        logger.info("All services are healthy, proceeding with tests...")
        
        # Ejecutar cada suite de pruebas
        for suite_name, test_class in self.test_suites:
            logger.info(f"Running {suite_name} tests...")
            try:
                test_instance = test_class()
                if suite_name == "Availability":
                    result = await test_instance.run_failure_test()
                elif suite_name == "Scalability":
                    result = await test_instance.run_load_test()
                elif suite_name == "Interoperability":
                    result = await test_instance.run_sync_test()
                else:
                    raise Exception(f"Unknown test suite: {suite_name}")
                
                self.results.append(result)
                self.helper.add_result(result)
                
                status = "PASS" if result.success else "FAIL"
                logger.info(f"{suite_name} tests: {status}")
                
            except Exception as e:
                logger.error(f"Error running {suite_name} tests: {e}")
                error_result = TestResult(
                    test_name=f"{suite_name} Test Suite",
                    success=False,
                    duration=0,
                    metrics={},
                    error_message=str(e)
                )
                self.results.append(error_result)
                self.helper.add_result(error_result)
        
        # Generar reporte final
        summary = self.helper.get_summary()
        self._generate_final_report(summary)
        
        return {
            "success": summary["failed_tests"] == 0,
            "summary": summary,
            "results": self.results
        }
    
    def _generate_final_report(self, summary: Dict[str, Any]):
        """Genera el reporte final de todas las pruebas"""
        report_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"\n{'='*60}")
        print(f"HEXABUILDERS QUALITY SCENARIOS TEST REPORT")
        print(f"Generated: {report_time}")
        print(f"{'='*60}")
        
        print(f"\nOVERALL SUMMARY:")
        print(f"  Total Tests: {summary['total_tests']}")
        print(f"  Passed: {summary['passed_tests']}")
        print(f"  Failed: {summary['failed_tests']}")
        print(f"  Success Rate: {summary['success_rate']:.1f}%")
        print(f"  Total Duration: {summary['total_duration']:.2f}s")
        print(f"  Average Duration: {summary['average_duration']:.2f}s")
        
        print(f"\nDETAILED RESULTS:")
        for result in self.results:
            status = "✅ PASS" if result.success else "❌ FAIL"
            print(f"  {status} {result.test_name} ({result.duration:.2f}s)")
            if not result.success and result.error_message:
                print(f"    Error: {result.error_message}")
        
        # Verificar cumplimiento de escenarios
        self._check_scenario_compliance()
        
        print(f"\n{'='*60}")
        
        # Guardar reporte en archivo
        self.helper.save_results(f"reports/final_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    
    def _check_scenario_compliance(self):
        """Verifica el cumplimiento de cada escenario"""
        print(f"\nSCENARIO COMPLIANCE:")
        
        # Escalabilidad
        scalability_result = next((r for r in self.results if "Scalability" in r.test_name), None)
        if scalability_result and scalability_result.success:
            throughput = scalability_result.metrics.get('actual_throughput', 0)
            max_latency = scalability_result.metrics.get('max_response_time', 0)
            print(f"  ✅ Escalabilidad: {throughput:.1f} req/min, {max_latency:.1f}s max latency")
        else:
            print(f"  ❌ Escalabilidad: FAILED")
        
        # Disponibilidad
        availability_result = next((r for r in self.results if "Availability" in r.test_name), None)
        if availability_result and availability_result.success:
            recovery_time = availability_result.metrics.get('recovery_time', 0)
            compensation = availability_result.metrics.get('compensation_verified', False)
            print(f"  ✅ Disponibilidad: {recovery_time:.1f}s recovery, compensation: {compensation}")
        else:
            print(f"  ❌ Disponibilidad: FAILED")
        
        # Interoperabilidad
        interoperability_result = next((r for r in self.results if "Interoperability" in r.test_name), None)
        if interoperability_result and interoperability_result.success:
            sync_time = interoperability_result.metrics.get('max_sync_time', 0)
            consistency = interoperability_result.metrics.get('consistency_rate', 0)
            print(f"  ✅ Interoperabilidad: {sync_time:.1f}s sync, {consistency:.1f}% consistency")
        else:
            print(f"  ❌ Interoperabilidad: FAILED")

async def main():
    """Función principal"""
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(f'reports/test_run_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
        ]
    )
    
    # Crear directorio de reportes
    os.makedirs('reports', exist_ok=True)
    
    # Ejecutar pruebas
    runner = TestRunner()
    result = await runner.run_all_tests()
    
    # Retornar código de salida apropiado
    return 0 if result["success"] else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
