#!/usr/bin/env python3
"""
Ejecutor principal para todas las pruebas de producción
"""

import asyncio
import logging
import sys
import os
from datetime import datetime

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.test_helpers import TestHelper
from prod_test import main as prod_test_main
from prod_load_test import main as prod_load_test_main
from prod_availability_test import main as prod_availability_test_main

logger = logging.getLogger(__name__)

class ProductionTestRunner:
    """Ejecutor principal de todas las pruebas de producción"""
    
    def __init__(self, config_path: str = "config/prod_config.yaml"):
        self.helper = TestHelper(config_path)
        self.results = []
    
    async def run_all_production_tests(self):
        """Ejecuta todas las pruebas de producción"""
        logger.info("Starting comprehensive production testing...")
        
        print("🚀 PRUEBAS DE PRODUCCIÓN HEXABUILDERS")
        print("=" * 60)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Environment: Production")
        print("=" * 60)
        
        # Verificar que todos los servicios estén saludables antes de comenzar
        print("\n🔍 Verificando servicios de producción...")
        services = await self.helper.check_all_services()
        unhealthy_services = [s for s in services if not s.healthy]
        
        if unhealthy_services:
            print(f"❌ Servicios no saludables encontrados:")
            for service in unhealthy_services:
                print(f"   - {service.name}: {service.url}")
            print("⚠️ Continuando con las pruebas...")
        else:
            print("✅ Todos los servicios están saludables")
        
        # Lista de pruebas a ejecutar
        tests = [
            ("Prueba Básica", prod_test_main, "Verificación básica del sistema"),
            ("Prueba de Carga", prod_load_test_main, "Prueba de escalabilidad"),
            ("Prueba de Disponibilidad", prod_availability_test_main, "Prueba de fallas y recuperación")
        ]
        
        print(f"\n📋 Ejecutando {len(tests)} pruebas de producción...")
        
        # Ejecutar cada prueba
        for test_name, test_func, description in tests:
            print(f"\n🧪 {test_name}: {description}")
            print("-" * 40)
            
            try:
                start_time = asyncio.get_event_loop().time()
                success = await test_func()
                duration = asyncio.get_event_loop().time() - start_time
                
                status = "✅ PASS" if success else "❌ FAIL"
                print(f"{status} - {test_name} ({duration:.2f}s)")
                
                self.results.append({
                    "test_name": test_name,
                    "success": success,
                    "duration": duration,
                    "description": description
                })
                
            except Exception as e:
                duration = asyncio.get_event_loop().time() - start_time
                logger.error(f"Test {test_name} failed with exception: {e}")
                print(f"❌ ERROR - {test_name} ({duration:.2f}s): {str(e)}")
                
                self.results.append({
                    "test_name": test_name,
                    "success": False,
                    "duration": duration,
                    "description": description,
                    "error": str(e)
                })
        
        # Mostrar resumen final
        self._print_summary()
        
        # Guardar resultados
        self._save_results()
        
        return self.results
    
    def _print_summary(self):
        """Imprime el resumen de resultados"""
        print("\n" + "=" * 60)
        print("📊 RESUMEN DE PRUEBAS DE PRODUCCIÓN")
        print("=" * 60)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total de pruebas: {total_tests}")
        print(f"Exitosas: {passed_tests} ✅")
        print(f"Fallidas: {failed_tests} ❌")
        print(f"Tasa de éxito: {(passed_tests/total_tests)*100:.1f}%")
        
        print("\nDetalles por prueba:")
        for result in self.results:
            status = "✅" if result['success'] else "❌"
            print(f"  {status} {result['test_name']}: {result['duration']:.2f}s")
            if 'error' in result:
                print(f"      Error: {result['error']}")
        
        print("\n" + "=" * 60)
        
        if failed_tests == 0:
            print("🎉 ¡TODAS LAS PRUEBAS PASARON!")
        else:
            print(f"⚠️ {failed_tests} prueba(s) fallaron")
        
        print("=" * 60)
    
    def _save_results(self):
        """Guarda los resultados en un archivo"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"reports/prod_test_results_{timestamp}.json"
        
        # Crear directorio si no existe
        os.makedirs("reports", exist_ok=True)
        
        import json
        with open(filename, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "environment": "production",
                "total_tests": len(self.results),
                "passed_tests": sum(1 for r in self.results if r['success']),
                "failed_tests": sum(1 for r in self.results if not r['success']),
                "results": self.results
            }, f, indent=2)
        
        print(f"📁 Resultados guardados en: {filename}")

async def main():
    """Función principal"""
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(f'reports/prod_tests_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
        ]
    )
    
    # Crear directorio de reportes
    os.makedirs("reports", exist_ok=True)
    
    # Ejecutar pruebas
    runner = ProductionTestRunner()
    results = await runner.run_all_production_tests()
    
    # Determinar código de salida
    all_passed = all(r['success'] for r in results)
    return all_passed

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
