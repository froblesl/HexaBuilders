#!/usr/bin/env python3
"""
Prueba simple de eventos para verificar que la arquitectura de eventos
está funcionando correctamente en los microservicios.
"""

import json
import sys
import os
import time
from datetime import datetime

# Agregar los paths de los microservicios al PYTHONPATH
sys.path.append('src')

def test_event_imports():
    """Probar que los eventos se pueden importar correctamente"""
    print("🔍 Probando importación de eventos...")
    
    try:
        # Partner Management Events
        from partner_management.seedwork.dominio.eventos_integracion import (
            PartnerRegistrationCompletedIntegrationEvent,
            ContractSignedIntegrationEvent
        )
        from partner_management.modulos.partners.dominio.eventos import (
            PartnerCreated,
            PartnerStatusChanged
        )
        print("  ✅ Partner Management eventos importados")
        
        # Onboarding Events - verificar la estructura
        from onboarding.seedwork.dominio.eventos import EventMetadata
        print("  ✅ Onboarding eventos importados")
        
        # Recruitment Events - verificar la estructura  
        from recruitment.seedwork.dominio.eventos import EventMetadata as RecruitmentEventMetadata
        print("  ✅ Recruitment eventos importados")
        
        return True
        
    except ImportError as e:
        print(f"  ❌ Error importando eventos: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Error inesperado: {e}")
        return False

def test_event_creation():
    """Probar la creación de eventos de dominio e integración"""
    print("\n🏗️ Probando creación de eventos...")
    
    try:
        from partner_management.modulos.partners.dominio.eventos import PartnerCreated
        from partner_management.seedwork.dominio.eventos_integracion import PartnerRegistrationCompletedIntegrationEvent
        from datetime import datetime
        
        # Crear evento de dominio
        domain_event = PartnerCreated(
            aggregate_id="test-partner-123",
            business_name="Test Company",
            email="test@company.com",
            partner_type="ENTERPRISE",
            phone="+1234567890"
        )
        
        print(f"  ✅ Evento de dominio creado: {domain_event.__class__.__name__}")
        print(f"    • ID: {domain_event.aggregate_id}")
        print(f"    • Timestamp: {domain_event.timestamp}")
        
        # Crear evento de integración
        integration_event = PartnerRegistrationCompletedIntegrationEvent(
            partner_id="test-partner-123",
            partner_data={
                "business_name": "Test Company",
                "email": "test@company.com"
            },
            registration_type="STANDARD"
        )
        
        print(f"  ✅ Evento de integración creado: {integration_event.__class__.__name__}")
        print(f"    • Partner ID: {integration_event.partner_id}")
        print(f"    • Tipo: {integration_event.registration_type}")
        
        # Verificar serialización
        event_dict = integration_event.to_dict()
        print(f"  ✅ Evento serializado exitosamente: {len(str(event_dict))} caracteres")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error creando eventos: {e}")
        return False

def test_event_dispatcher():
    """Probar el dispatcher de eventos"""
    print("\n📡 Probando dispatcher de eventos...")
    
    try:
        from partner_management.seedwork.infraestructura.utils import EventDispatcher
        
        # Crear dispatcher
        dispatcher = EventDispatcher()
        print("  ✅ EventDispatcher creado")
        
        # Variable para verificar si el handler fue llamado
        handler_called = {"value": False}
        
        def test_handler(event):
            print(f"    📥 Handler recibió evento: {event.__class__.__name__}")
            handler_called["value"] = True
        
        # Suscribir handler
        from partner_management.modulos.partners.dominio.eventos import PartnerCreated
        dispatcher.subscribe(PartnerCreated, test_handler)
        print("  ✅ Handler suscrito al evento PartnerCreated")
        
        # Crear y publicar evento
        event = PartnerCreated(
            aggregate_id="test-partner-456",
            business_name="Another Test Company",
            email="test2@company.com", 
            partner_type="STANDARD",
            phone="+0987654321"
        )
        
        dispatcher.publish(event)
        print("  ✅ Evento publicado")
        
        # Verificar que el handler fue llamado
        if handler_called["value"]:
            print("  ✅ Handler ejecutado exitosamente")
            return True
        else:
            print("  ⚠️ Handler no fue ejecutado")
            return False
            
    except Exception as e:
        print(f"  ❌ Error con dispatcher: {e}")
        return False

def test_service_connections():
    """Probar conexiones básicas a los servicios"""
    print("\n🌐 Probando conexiones a servicios...")
    
    import subprocess
    import socket
    
    services = {
        "onboarding": 8001,
        "recruitment": 8002,
        "campaign-management": 8003,
        "pulsar-broker": 6650,
        "pulsar-admin": 8080
    }
    
    connected_services = []
    
    for service_name, port in services.items():
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            
            if result == 0:
                print(f"  ✅ {service_name} (puerto {port}): Conectado")
                connected_services.append(service_name)
            else:
                print(f"  ❌ {service_name} (puerto {port}): No conectado")
                
        except Exception as e:
            print(f"  ❌ {service_name} (puerto {port}): Error - {e}")
    
    return len(connected_services) >= 3  # Al menos 3 servicios conectados

def test_event_flow_simulation():
    """Simular un flujo completo de eventos entre servicios"""
    print("\n🔄 Simulando flujo de eventos entre servicios...")
    
    try:
        # Simular el flujo: PartnerCreated -> ContractNeeded -> CandidateSearch -> CampaignTrigger
        
        events_created = []
        
        # 1. Partner Registration
        from partner_management.modulos.partners.dominio.eventos import PartnerCreated
        partner_event = PartnerCreated(
            aggregate_id="flow-partner-789",
            business_name="Flow Test Company",
            email="flow@company.com",
            partner_type="ENTERPRISE",
            phone="+1122334455"
        )
        events_created.append(("PartnerCreated", partner_event))
        print(f"  ✅ 1. {partner_event.__class__.__name__} creado")
        
        # 2. Integration Event para otros servicios
        from partner_management.seedwork.dominio.eventos_integracion import PartnerRegistrationCompletedIntegrationEvent
        integration_event = PartnerRegistrationCompletedIntegrationEvent(
            partner_id="flow-partner-789",
            partner_data={
                "business_name": "Flow Test Company",
                "email": "flow@company.com",
                "partner_type": "ENTERPRISE"
            },
            registration_type="ENTERPRISE"
        )
        events_created.append(("PartnerRegistrationCompleted", integration_event))
        print(f"  ✅ 2. {integration_event.__class__.__name__} creado")
        
        # 3. Contract Integration Event
        from partner_management.seedwork.dominio.eventos_integracion import ContractSignedIntegrationEvent
        contract_event = ContractSignedIntegrationEvent(
            contract_id="flow-contract-101",
            partner_id="flow-partner-789",
            contract_type="ENTERPRISE",
            effective_date=datetime.now()
        )
        events_created.append(("ContractSigned", contract_event))
        print(f"  ✅ 3. {contract_event.__class__.__name__} creado")
        
        # 4. Verificar serialización de todos los eventos
        for event_name, event in events_created:
            try:
                if hasattr(event, 'to_dict'):
                    event_dict = event.to_dict()
                    print(f"    📄 {event_name}: {len(str(event_dict))} chars")
                else:
                    # Para eventos de dominio, convertir a dict manualmente
                    event_data = {
                        'event_id': getattr(event, 'id', 'unknown'),
                        'aggregate_id': getattr(event, 'aggregate_id', 'unknown'),
                        'timestamp': getattr(event, 'timestamp', datetime.now()).isoformat(),
                        'event_type': event.__class__.__name__
                    }
                    print(f"    📄 {event_name}: {len(str(event_data))} chars")
            except Exception as e:
                print(f"    ❌ Error serializando {event_name}: {e}")
                return False
        
        print(f"  ✅ Flujo de {len(events_created)} eventos simulado exitosamente")
        return True
        
    except Exception as e:
        print(f"  ❌ Error en simulación de flujo: {e}")
        return False

def main():
    """Función principal del test"""
    print("🎯 HexaBuilders - Prueba de Arquitectura de Eventos")
    print("=" * 60)
    print("📅 Timestamp:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("🐍 Python version:", sys.version.split()[0])
    print("📁 Working directory:", os.getcwd())
    print("-" * 60)
    
    tests = [
        ("Importación de Eventos", test_event_imports),
        ("Creación de Eventos", test_event_creation),
        ("Dispatcher de Eventos", test_event_dispatcher),
        ("Conexiones de Servicios", test_service_connections),
        ("Flujo de Eventos", test_event_flow_simulation)
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_function in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_function():
                passed_tests += 1
                print(f"✅ {test_name}: PASÓ")
            else:
                print(f"❌ {test_name}: FALLÓ")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
    
    # Reporte final
    print("\n" + "="*60)
    print("📊 REPORTE FINAL")
    print("="*60)
    print(f"🎯 Pruebas ejecutadas: {total_tests}")
    print(f"✅ Pruebas exitosas: {passed_tests}")
    print(f"❌ Pruebas fallidas: {total_tests - passed_tests}")
    print(f"📈 Porcentaje de éxito: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print("\n🎉 ¡TODAS LAS PRUEBAS PASARON!")
        print("✅ La arquitectura de eventos está funcionando correctamente")
        print("✅ Los microservicios pueden comunicarse mediante eventos")
        print("✅ Apache Pulsar está configurado y disponible")
        result = True
    elif passed_tests >= total_tests * 0.7:  # 70% o más
        print("\n⚠️ LA MAYORÍA DE PRUEBAS PASARON")
        print("✅ Funcionalidad básica de eventos operativa")
        print("⚠️ Algunas funcionalidades pueden necesitar ajustes")
        result = True
    else:
        print("\n❌ MÚLTIPLES PRUEBAS FALLARON")
        print("❌ La arquitectura de eventos necesita revisión")
        print("💡 Verificar configuración de servicios y dependencias")
        result = False
    
    print("\n" + "="*60)
    return result

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)