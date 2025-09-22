#!/usr/bin/env python3
"""
Prueba de producción usando endpoints de HexaBuilders
"""

import asyncio
import time
import logging
import sys
import os

# Agregar el directorio padre al path para importar utils
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.test_helpers import TestHelper

logger = logging.getLogger(__name__)

async def main():
    """Función principal para pruebas de producción"""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Usar configuración de producción
    helper = TestHelper("config/prod_config.yaml")
    
    print("🚀 PRUEBAS DE PRODUCCIÓN HEXABUILDERS")
    print("=" * 50)
    
    print("\n🔍 Verificando servicios de producción...")
    
    # Verificar que todos los servicios estén saludables
    services = await helper.check_all_services()
    unhealthy_services = [s for s in services if not s.healthy]
    
    if unhealthy_services:
        print(f"❌ Servicios no saludables:")
        for service in unhealthy_services:
            print(f"   - {service.name}: {service.url} ({service.error_message})")
        return False
    else:
        print("✅ Todos los servicios de producción están saludables")
        for service in services:
            print(f"   - {service.name}: {service.response_time:.2f}s")
    
    print("\n🧪 Creando partner de prueba en producción...")
    
    # Crear un partner de prueba
    partner_id = f"prod_test_{int(time.time())}"
    result = await helper.create_test_partner(partner_id)
    
    if result and result.get('partner_id'):
        print(f"✅ Partner creado exitosamente: {result['partner_id']}")
        print(f"   - Saga ID: {result.get('saga_id', 'N/A')}")
        print(f"   - Status: {result.get('status', 'N/A')}")
        
        # Esperar un poco para que la saga progrese
        print("\n⏳ Esperando 15 segundos para que la saga progrese...")
        await asyncio.sleep(15)
        
        # Verificar el estado de la saga
        print("🔍 Verificando estado de la saga...")
        saga_status = await helper.get_saga_status(partner_id)
        
        if saga_status:
            print(f"✅ Estado de la saga: {saga_status.get('status', 'unknown')}")
            print(f"   - Pasos completados: {saga_status.get('completed_steps', [])}")
            print(f"   - Pasos fallidos: {saga_status.get('failed_steps', [])}")
        else:
            print("⚠️ No se pudo obtener el estado de la saga")
        
        # Verificar el dashboard
        print("\n📊 Verificando dashboard de producción...")
        dashboard_status = await helper.get_dashboard_status()
        
        if dashboard_status and 'sagas' in dashboard_status:
            sagas = dashboard_status['sagas']
            print(f"✅ Dashboard muestra {len(sagas)} sagas")
            
            # Buscar nuestra saga
            our_saga = next((s for s in sagas if s.get('partner_id') == partner_id), None)
            if our_saga:
                print(f"✅ Nuestra saga encontrada en el dashboard:")
                print(f"   - Status: {our_saga.get('status')}")
                print(f"   - Duración: {our_saga.get('total_duration_ms', 0)}ms")
                print(f"   - Pasos: {our_saga.get('total_steps', 0)}")
            else:
                print("⚠️ Nuestra saga no encontrada en el dashboard")
        else:
            print("⚠️ No se pudo obtener el estado del dashboard")
        
        # Verificar timeline de la saga
        print("\n📈 Verificando timeline de la saga...")
        timeline = await helper.get_saga_timeline(partner_id)
        
        if timeline:
            steps = timeline.get('steps', [])
            print(f"✅ Timeline muestra {len(steps)} pasos:")
            for i, step in enumerate(steps[:5]):  # Mostrar solo los primeros 5
                print(f"   {i+1}. {step.get('step_name', 'unknown')}: {step.get('result', 'unknown')}")
            if len(steps) > 5:
                print(f"   ... y {len(steps) - 5} pasos más")
        else:
            print("⚠️ No se pudo obtener el timeline de la saga")
        
        return True
    else:
        print(f"❌ Error creando partner: {result}")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    print(f"\n{'✅ ÉXITO' if success else '❌ FALLO'}")
    print("=" * 50)
    exit(0 if success else 1)
