#!/usr/bin/env python3
"""
Prueba simple para verificar que el sistema funciona
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
    """Función principal"""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    helper = TestHelper()
    
    print("🔍 Verificando servicios...")
    
    # Verificar que todos los servicios estén saludables
    services = await helper.check_all_services()
    unhealthy_services = [s for s in services if not s.healthy]
    
    if unhealthy_services:
        print(f"❌ Servicios no saludables: {[s.name for s in unhealthy_services]}")
        return False
    else:
        print("✅ Todos los servicios están saludables")
    
    print("\n🧪 Creando partner de prueba...")
    
    # Crear un partner de prueba
    partner_id = f"simple_test_{int(time.time())}"
    result = await helper.create_test_partner(partner_id)
    
    if result and result.get('partner_id'):
        print(f"✅ Partner creado exitosamente: {result['partner_id']}")
        
        # Esperar un poco para que la saga progrese
        print("⏳ Esperando 10 segundos para que la saga progrese...")
        await asyncio.sleep(10)
        
        # Verificar el estado de la saga
        print("🔍 Verificando estado de la saga...")
        saga_status = await helper.get_saga_status(partner_id)
        
        if saga_status:
            print(f"✅ Estado de la saga: {saga_status.get('status', 'unknown')}")
        else:
            print("⚠️ No se pudo obtener el estado de la saga")
        
        # Verificar el dashboard
        print("📊 Verificando dashboard...")
        dashboard_status = await helper.get_dashboard_status()
        
        if dashboard_status and 'sagas' in dashboard_status:
            sagas = dashboard_status['sagas']
            print(f"✅ Dashboard muestra {len(sagas)} sagas")
            
            # Buscar nuestra saga
            our_saga = next((s for s in sagas if s.get('partner_id') == partner_id), None)
            if our_saga:
                print(f"✅ Nuestra saga encontrada en el dashboard: {our_saga.get('status')}")
            else:
                print("⚠️ Nuestra saga no encontrada en el dashboard")
        else:
            print("⚠️ No se pudo obtener el estado del dashboard")
        
        return True
    else:
        print(f"❌ Error creando partner: {result}")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    print(f"\n{'✅ ÉXITO' if success else '❌ FALLO'}")
    exit(0 if success else 1)
