# Scripts de Pruebas de Escenarios de Calidad

Este directorio contiene scripts para ejecutar las pruebas de los escenarios de calidad acotados al sistema HexaBuilders.

## Estructura

```
test_scenarios/
├── README.md                           # Este archivo
├── requirements.txt                    # Dependencias de Python
├── config/
│   ├── test_config.yaml              # Configuración de pruebas
│   └── scenarios.yaml                # Definición de escenarios
├── load_tests/
│   ├── scalability_test.py           # Prueba de escalabilidad
│   └── concurrent_sagas_test.py      # Prueba de Sagas concurrentes
├── availability_tests/
│   ├── service_failure_test.py       # Prueba de falla de servicios
│   └── recovery_test.py              # Prueba de recuperación
├── interoperability_tests/
│   ├── event_sync_test.py            # Prueba de sincronización
│   └── saga_progression_test.py      # Prueba de progresión de Sagas
├── recoverability_tests/
│   ├── compensation_test.py          # Prueba de compensación
│   └── timeout_test.py               # Prueba de timeouts
├── observability_tests/
│   ├── dashboard_test.py             # Prueba del dashboard
│   └── metrics_test.py               # Prueba de métricas
├── utils/
│   ├── test_helpers.py               # Utilidades de prueba
│   ├── data_generators.py            # Generadores de datos
│   └── result_analyzers.py           # Analizadores de resultados
└── reports/
    └── (se generan automáticamente)   # Reportes de pruebas
```

## Escenarios de Prueba

### 1. Escalabilidad
- **Objetivo**: 100 registros de partners/min, latencia < 30 segundos
- **Método**: Carga progresiva con Sagas concurrentes
- **Métricas**: Throughput, latencia, uso de recursos

### 2. Disponibilidad
- **Objetivo**: 99.9% uptime, compensación < 60 segundos
- **Método**: Simulación de fallas de servicios
- **Métricas**: Tiempo de recuperación, tasa de éxito

### 3. Interoperabilidad
- **Objetivo**: Sincronización < 5 segundos
- **Método**: Verificación de eventos entre servicios
- **Métricas**: Latencia de eventos, consistencia

## Ejecución

### Prerequisitos
```bash
# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
export PARTNER_MANAGEMENT_URL=http://localhost:5000
export BFF_WEB_URL=http://localhost:8000
export CAMPAIGN_MANAGEMENT_URL=http://localhost:5003
```

### Ejecutar todas las pruebas
```bash
python -m pytest test_scenarios/ -v --html=reports/report.html
```

### Ejecutar escenario específico
```bash
python test_scenarios/scalability_test.py
python test_scenarios/availability_tests/service_failure_test.py
```

### Ejecutar con configuración personalizada
```bash
python test_scenarios/load_tests/scalability_test.py --config config/test_config.yaml
```

## Reportes

Los reportes se generan automáticamente en:
- `reports/report.html` - Reporte HTML completo
- `reports/metrics.json` - Métricas en formato JSON
- `reports/logs/` - Logs detallados de cada prueba
