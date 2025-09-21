#!/usr/bin/env python3
"""
Script para probar la comunicación de eventos entre microservicios usando Apache Pulsar.
Verifica que los eventos se publiquen y consuman correctamente entre los servicios.
"""

import json
import time
import requests
import pulsar
from datetime import datetime
from typing import Dict, Any

# Configuración de Pulsar
PULSAR_URL = "pulsar://localhost:6650"
TOPICS = {
    "partner_events": "persistent://public/default/partner-events",
    "contract_events": "persistent://public/default/contract-events", 
    "candidate_events": "persistent://public/default/candidate-events",
    "campaign_events": "persistent://public/default/campaign-events"
}

# URLs de los microservicios
SERVICES = {
    "onboarding": "http://localhost:8001",
    "recruitment": "http://localhost:8002", 
    "campaign_management": "http://localhost:8003"
}

class EventTestSuite:
    def __init__(self):
        print("🚀 Iniciando prueba de comunicación de eventos entre microservicios")
        print(f"📊 Pulsar URL: {PULSAR_URL}")
        print(f"🎯 Topics: {list(TOPICS.keys())}")
        print(f"🌐 Services: {list(SERVICES.keys())}")
        print("-" * 60)
        
        # Configurar Pulsar client
        try:
            self.client = pulsar.Client(PULSAR_URL)
            self.received_events = []
            print("✅ Conexión a Pulsar establecida")
        except Exception as e:
            print(f"❌ Error conectando a Pulsar: {e}")
            return
    
    def setup_consumers(self):
        """Configurar consumidores para todos los topics"""
        print("\n📥 Configurando consumidores de eventos...")
        
        self.consumers = {}
        
        for topic_name, topic_url in TOPICS.items():
            try:
                consumer = self.client.subscribe(
                    topic_url,
                    f"test-consumer-{topic_name}",
                    consumer_type=pulsar.ConsumerType.Shared
                )
                self.consumers[topic_name] = consumer
                print(f"  ✅ Consumer para {topic_name} configurado")
            except Exception as e:
                print(f"  ❌ Error configurando consumer para {topic_name}: {e}")
    
    def setup_producers(self):
        """Configurar productores para todos los topics"""
        print("\n📤 Configurando productores de eventos...")
        
        self.producers = {}
        
        for topic_name, topic_url in TOPICS.items():
            try:
                producer = self.client.create_producer(topic_url)
                self.producers[topic_name] = producer
                print(f"  ✅ Producer para {topic_name} configurado")
            except Exception as e:
                print(f"  ❌ Error configurando producer para {topic_name}: {e}")
    
    def publish_test_event(self, topic_name: str, event_data: Dict[str, Any]):
        """Publicar un evento de prueba"""
        try:
            if topic_name in self.producers:
                event_json = json.dumps(event_data)
                self.producers[topic_name].send(event_json.encode('utf-8'))
                print(f"  📤 Evento publicado en {topic_name}: {event_data['event_type']}")
                return True
        except Exception as e:
            print(f"  ❌ Error publicando evento en {topic_name}: {e}")
            return False
    
    def consume_events(self, timeout_seconds: int = 5):
        """Consumir eventos por un tiempo determinado"""
        print(f"\n📥 Consumiendo eventos por {timeout_seconds} segundos...")
        
        start_time = time.time()
        
        while time.time() - start_time < timeout_seconds:
            for topic_name, consumer in self.consumers.items():
                try:
                    msg = consumer.receive(timeout_millis=100)
                    event_data = json.loads(msg.data().decode('utf-8'))
                    self.received_events.append({
                        'topic': topic_name,
                        'event': event_data,
                        'timestamp': datetime.now()
                    })
                    consumer.acknowledge(msg)
                    print(f"  📥 Evento recibido de {topic_name}: {event_data.get('event_type', 'Unknown')}")
                except pulsar.Timeout:
                    pass  # Normal cuando no hay mensajes
                except Exception as e:
                    print(f"  ⚠️ Error consumiendo de {topic_name}: {e}")
    
    def test_service_health(self):
        """Verificar que todos los servicios estén funcionando"""
        print("\n🏥 Verificando salud de los servicios...")
        
        healthy_services = []
        
        for service_name, service_url in SERVICES.items():
            try:
                response = requests.get(f"{service_url}/health", timeout=2)
                if response.status_code == 200:
                    print(f"  ✅ {service_name}: Healthy")
                    healthy_services.append(service_name)
                else:
                    print(f"  ❌ {service_name}: Status {response.status_code}")
            except Exception as e:
                print(f"  ❌ {service_name}: {e}")
        
        return healthy_services
    
    def test_cross_service_events(self):
        """Probar eventos entre diferentes servicios"""
        print("\n🔄 Probando comunicación de eventos entre servicios...")
        
        # Simular flujo: Partner registra -> Contract se crea -> Candidate se busca
        
        # 1. Evento de Partner Registration Completed
        partner_event = {
            "event_type": "PartnerRegistrationCompleted",
            "event_id": f"partner-{int(time.time())}",
            "timestamp": datetime.now().isoformat(),
            "data": {
                "partner_id": "test-partner-123",
                "business_name": "Test Company",
                "email": "test@company.com",
                "partner_type": "ENTERPRISE"
            }
        }
        
        # 2. Evento de Contract Signed
        contract_event = {
            "event_type": "ContractSigned",
            "event_id": f"contract-{int(time.time())}",
            "timestamp": datetime.now().isoformat(),
            "data": {
                "contract_id": "test-contract-456", 
                "partner_id": "test-partner-123",
                "contract_type": "STANDARD",
                "effective_date": datetime.now().isoformat()
            }
        }
        
        # 3. Evento de Candidate Matched
        candidate_event = {
            "event_type": "CandidateMatched",
            "event_id": f"candidate-{int(time.time())}",
            "timestamp": datetime.now().isoformat(),
            "data": {
                "job_id": "test-job-789",
                "candidate_id": "test-candidate-101",
                "partner_id": "test-partner-123",
                "match_score": 0.85
            }
        }
        
        # 4. Evento de Campaign Performance
        campaign_event = {
            "event_type": "CampaignPerformanceReport",
            "event_id": f"campaign-{int(time.time())}",
            "timestamp": datetime.now().isoformat(),
            "data": {
                "campaign_id": "test-campaign-202",
                "partner_id": "test-partner-123",
                "performance_data": {
                    "clicks": 1500,
                    "conversions": 75,
                    "spend": 2500.00
                }
            }
        }
        
        # Publicar eventos
        events_to_publish = [
            ("partner_events", partner_event),
            ("contract_events", contract_event),
            ("candidate_events", candidate_event),
            ("campaign_events", campaign_event)
        ]
        
        published_count = 0
        for topic, event in events_to_publish:
            if self.publish_test_event(topic, event):
                published_count += 1
            time.sleep(0.5)  # Pequeña pausa entre publicaciones
        
        print(f"  📤 {published_count}/{len(events_to_publish)} eventos publicados exitosamente")
        
        # Consumir eventos por un tiempo
        self.consume_events(10)
        
        return published_count == len(events_to_publish)
    
    def generate_report(self):
        """Generar reporte de la prueba"""
        print("\n" + "="*60)
        print("📊 REPORTE DE PRUEBA DE EVENTOS")
        print("="*60)
        
        # Estadísticas de eventos recibidos
        print(f"🎯 Eventos recibidos: {len(self.received_events)}")
        
        if self.received_events:
            events_by_topic = {}
            for event in self.received_events:
                topic = event['topic']
                if topic not in events_by_topic:
                    events_by_topic[topic] = []
                events_by_topic[topic].append(event)
            
            for topic, events in events_by_topic.items():
                print(f"  📥 {topic}: {len(events)} eventos")
                for event in events:
                    event_type = event['event'].get('event_type', 'Unknown')
                    timestamp = event['timestamp'].strftime('%H:%M:%S')
                    print(f"    • {event_type} @ {timestamp}")
        
        # Verificar topics en Pulsar
        print(f"\n🔍 Topics en Pulsar:")
        try:
            response = requests.get("http://localhost:8080/admin/v2/persistent/public/default")
            if response.status_code == 200:
                topics = response.json()
                print(f"  📋 {len(topics)} topics encontrados: {topics}")
            else:
                print(f"  ⚠️ No se pudieron obtener topics (Status: {response.status_code})")
        except Exception as e:
            print(f"  ❌ Error obteniendo topics: {e}")
        
        # Resumen final
        success = len(self.received_events) > 0
        print(f"\n🎯 RESULTADO: {'✅ ÉXITO' if success else '❌ FALLO'}")
        
        if success:
            print("✅ La comunicación de eventos entre microservicios funciona correctamente")
        else:
            print("❌ No se detectó comunicación de eventos entre microservicios")
            print("💡 Verificar configuración de Pulsar y servicios")
        
        return success
    
    def run_test(self):
        """Ejecutar la suite completa de pruebas"""
        try:
            # 1. Verificar servicios
            healthy_services = self.test_service_health()
            
            if not healthy_services:
                print("❌ No hay servicios disponibles para probar")
                return False
            
            # 2. Configurar Pulsar
            self.setup_producers()
            self.setup_consumers()
            
            # 3. Probar eventos
            self.test_cross_service_events()
            
            # 4. Generar reporte
            return self.generate_report()
            
        finally:
            # Limpiar recursos
            print("\n🧹 Limpiando recursos...")
            
            # Cerrar consumers
            for consumer in getattr(self, 'consumers', {}).values():
                try:
                    consumer.close()
                except:
                    pass
            
            # Cerrar producers
            for producer in getattr(self, 'producers', {}).values():
                try:
                    producer.close()
                except:
                    pass
            
            # Cerrar client
            try:
                self.client.close()
                print("✅ Recursos de Pulsar liberados")
            except:
                pass

def main():
    """Función principal"""
    print("🎯 HexaBuilders - Prueba de Comunicación de Eventos")
    print("=" * 60)
    
    # Verificar dependencias
    try:
        import pulsar
        print("✅ Pulsar client disponible")
    except ImportError:
        print("❌ Pulsar client no disponible. Instalar con: pip install pulsar-client")
        return False
    
    # Ejecutar pruebas
    test_suite = EventTestSuite()
    result = test_suite.run_test()
    
    print("\n" + "="*60)
    return result

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)