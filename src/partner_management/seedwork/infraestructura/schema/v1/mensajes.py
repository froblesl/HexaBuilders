import json
from typing import Dict, Any, Optional
from dataclasses import dataclass


# Esquema de sobre CloudEvent para estandarización
CLOUD_EVENT_ENVELOPE_SCHEMA = {
    "type": "record",
    "name": "CloudEventEnvelope",
    "namespace": "com.alpes.partners.events",
    "doc": "Sobre CloudEvent siguiendo la especificación CloudEvents v1.0",
    "fields": [
        {
            "name": "specversion",
            "type": "string",
            "doc": "Versión de especificación CloudEvent",
            "default": "1.0"
        },
        {
            "name": "type",
            "type": "string",
            "doc": "Identificador de tipo de evento calificado"
        },
        {
            "name": "source",
            "type": "string",
            "doc": "URI del servicio que generó el evento"
        },
        {
            "name": "id",
            "type": "string",
            "doc": "Identificador único de evento (UUID)"
        },
        {
            "name": "time",
            "type": "string",
            "doc": "Timestamp RFC3339 de cuándo ocurrió el evento"
        },
        {
            "name": "datacontenttype",
            "type": "string",
            "doc": "Tipo MIME de carga de datos",
            "default": "application/json"
        },
        {
            "name": "subject",
            "type": ["null", "string"],
            "doc": "Identificador de recurso al que se relaciona el evento",
            "default": None
        },
        {
            "name": "data",
            "type": "bytes",
            "doc": "Carga de evento serializada"
        }
    ]
}


# Esquema de mensaje base para todos los mensajes
BASE_MESSAGE_SCHEMA = {
    "type": "record",
    "name": "BaseMessage",
    "namespace": "com.alpes.partners.messages",
    "doc": "Esquema de mensaje base con campos de metadatos comunes",
    "fields": [
        {
            "name": "message_id",
            "type": "string",
            "doc": "Identificador único de mensaje (UUID)"
        },
        {
            "name": "correlation_id",
            "type": "string",
            "doc": "ID de correlación para trazabilidad de mensajes"
        },
        {
            "name": "causation_id",
            "type": ["null", "string"],
            "doc": "ID del mensaje que causó este mensaje",
            "default": None
        },
        {
            "name": "message_type",
            "type": {
                "type": "enum",
                "name": "MessageType",
                "symbols": ["COMMAND", "EVENT", "QUERY", "RESPONSE"]
            },
            "doc": "Tipo de mensaje"
        },
        {
            "name": "aggregate_id",
            "type": ["null", "string"],
            "doc": "ID del agregado al que se relaciona este mensaje",
            "default": None
        },
        {
            "name": "aggregate_type",
            "type": ["null", {
                "type": "enum",
                "name": "AggregateType",
                "symbols": ["PARTNER", "CAMPAIGN", "COMMISSION", "ANALYTICS"]
            }],
            "doc": "Tipo de agregado al que se relaciona este mensaje",
            "default": None
        },
        {
            "name": "version",
            "type": "int",
            "doc": "Versión de esquema de mensaje",
            "default": 1
        },
        {
            "name": "timestamp",
            "type": "long",
            "doc": "Timestamp Unix en milisegundos de cuándo se creó el mensaje"
        },
        {
            "name": "user_id",
            "type": ["null", "string"],
            "doc": "ID del usuario que desencadenó este mensaje",
            "default": None
        },
        {
            "name": "tenant_id",
            "type": ["null", "string"],
            "doc": "ID de inquilino para soporte multi-tenancy",
            "default": None
        },
        {
            "name": "metadata",
            "type": {
                "type": "map",
                "values": "string"
            },
            "doc": "Metadatos adicionales del mensaje",
            "default": {}
        }
    ]
}


# Esquema de carga de tasa de comisión
COMMISSION_RATE_PAYLOAD_SCHEMA = {
    "type": "record",
    "name": "CommissionRatePayload",
    "namespace": "com.alpes.partners.payloads",
    "doc": "Carga de configuración de tasa de comisión",
    "fields": [
        {
            "name": "rate_type",
            "type": {
                "type": "enum",
                "name": "RateType",
                "symbols": ["CPA", "CPL", "CPC", "REVENUE_SHARE"]
            },
            "doc": "Tipo de tasa de comisión"
        },
        {
            "name": "percentage",
            "type": "double",
            "doc": "Porcentaje de comisión (0.0 a 100.0)"
        },
        {
            "name": "minimum_amount",
            "type": ["null", "double"],
            "doc": "Cantidad mínima de comisión",
            "default": None
        },
        {
            "name": "maximum_amount",
            "type": ["null", "double"],
            "doc": "Cantidad máxima de comisión",
            "default": None
        },
        {
            "name": "currency",
            "type": "string",
            "doc": "Código de moneda ISO 4217"
        },
        {
            "name": "effective_date",
            "type": "long",
            "doc": "Timestamp Unix de cuándo la tasa se vuelve efectiva"
        },
        {
            "name": "expiration_date",
            "type": ["null", "long"],
            "doc": "Timestamp Unix de cuándo expira la tasa",
            "default": None
        }
    ]
}


# Esquema de carga de evento de socio
PARTNER_EVENT_PAYLOAD_SCHEMA = {
    "type": "record",
    "name": "PartnerEventPayload",
    "namespace": "com.alpes.partners.payloads",
    "doc": "Carga de evento de socio con información completa del socio",
    "fields": [
        {
            "name": "partner_id",
            "type": "string",
            "doc": "Unique partner identifier"
        },
        {
            "name": "business_name",
            "type": "string",
            "doc": "Nombre del negocio del socio"
        },
        {
            "name": "email",
            "type": "string",
            "doc": "Email de contacto del socio"
        },
        {
            "name": "category",
            "type": {
                "type": "enum",
                "name": "PartnerCategory",
                "symbols": ["AFFILIATE", "INFLUENCER", "MEDIA", "B2B_PARTNER"]
            },
            "doc": "Clasificación de categoría del socio"
        },
        {
            "name": "status",
            "type": {
                "type": "enum",
                "name": "PartnerStatus",
                "symbols": ["PENDING", "ACTIVE", "INACTIVE", "SUSPENDED"]
            },
            "doc": "Estado actual del socio"
        },
        {
            "name": "country",
            "type": "string",
            "doc": "País del socio (código ISO 3166-1 alfa-2)"
        },
        {
            "name": "registration_date",
            "type": "long",
            "doc": "Timestamp Unix de registro del socio"
        },
        {
            "name": "activation_date",
            "type": ["null", "long"],
            "doc": "Timestamp Unix de activación del socio",
            "default": None
        },
        {
            "name": "commission_rates",
            "type": {
                "type": "array",
                "items": "CommissionRatePayload"
            },
            "doc": "Array de tasas de comisión para el socio",
            "default": []
        },
        {
            "name": "previous_status",
            "type": ["null", "string"],
            "doc": "Estado previo del socio para eventos de cambio de estado",
            "default": None
        },
        {
            "name": "change_reason",
            "type": ["null", "string"],
            "doc": "Razón para el cambio de estado (pista de auditoría)",
            "default": None
        }
    ]
}


# Esquema de carga de evento de campaña
CAMPAIGN_EVENT_PAYLOAD_SCHEMA = {
    "type": "record",
    "name": "CampaignEventPayload",
    "namespace": "com.alpes.partners.payloads",
    "doc": "Carga de evento de campaña con información de campaña",
    "fields": [
        {
            "name": "campaign_id",
            "type": "string",
            "doc": "Identificador único de campaña"
        },
        {
            "name": "name",
            "type": "string",
            "doc": "Nombre de campaña"
        },
        {
            "name": "advertiser_name",
            "type": "string",
            "doc": "Nombre del anunciante que ejecuta la campaña"
        },
        {
            "name": "status",
            "type": {
                "type": "enum",
                "name": "CampaignStatus",
                "symbols": ["DRAFT", "ACTIVE", "PAUSED", "COMPLETED"]
            },
            "doc": "Estado actual de la campaña"
        },
        {
            "name": "start_date",
            "type": "long",
            "doc": "Timestamp Unix de cuándo inicia la campaña"
        },
        {
            "name": "end_date",
            "type": ["null", "long"],
            "doc": "Timestamp Unix de cuándo termina la campaña",
            "default": None
        },
        {
            "name": "budget_amount",
            "type": "double",
            "doc": "Cantidad de presupuesto de campaña"
        },
        {
            "name": "budget_currency",
            "type": "string",
            "doc": "Moneda de presupuesto de campaña (ISO 4217)"
        },
        {
            "name": "assigned_partners",
            "type": {
                "type": "array",
                "items": "string"
            },
            "doc": "Array de IDs de socios asignados",
            "default": []
        },
        {
            "name": "commission_structure",
            "type": "CommissionRatePayload",
            "doc": "Estructura de comisión para esta campaña"
        }
    ]
}


# Esquema de carga de métricas de comisión
COMMISSION_METRICS_PAYLOAD_SCHEMA = {
    "type": "record",
    "name": "CommissionMetricsPayload",
    "namespace": "com.alpes.partners.payloads",
    "doc": "Métricas de comisión y datos de rendimiento",
    "fields": [
        {
            "name": "transaction_count",
            "type": "int",
            "doc": "Número de transacciones procesadas"
        },
        {
            "name": "conversion_count",
            "type": "int",
            "doc": "Número de conversiones exitosas"
        },
        {
            "name": "click_count",
            "type": "int",
            "doc": "Número de clics generados"
        },
        {
            "name": "conversion_rate",
            "type": "double",
            "doc": "Tasa de conversión (0.0 a 1.0)"
        },
        {
            "name": "average_order_value",
            "type": "double",
            "doc": "Valor promedio de pedido para conversiones"
        }
    ]
}


# Esquema de carga de evento de comisión
COMMISSION_EVENT_PAYLOAD_SCHEMA = {
    "type": "record",
    "name": "CommissionEventPayload",
    "namespace": "com.alpes.partners.payloads",
    "doc": "Carga de evento de comisión con detalles de comisión",
    "fields": [
        {
            "name": "commission_id",
            "type": "string",
            "doc": "Identificador único de comisión"
        },
        {
            "name": "partner_id",
            "type": "string",
            "doc": "ID del socio que gana la comisión"
        },
        {
            "name": "campaign_id",
            "type": "string",
            "doc": "ID de campaña que generó la comisión"
        },
        {
            "name": "amount",
            "type": "double",
            "doc": "Cantidad de comisión"
        },
        {
            "name": "currency",
            "type": "string",
            "doc": "Moneda de comisión (ISO 4217)"
        },
        {
            "name": "commission_type",
            "type": "string",
            "doc": "Tipo de cálculo de comisión"
        },
        {
            "name": "calculation_date",
            "type": "long",
            "doc": "Timestamp Unix de cuándo se calculó la comisión"
        },
        {
            "name": "due_date",
            "type": "long",
            "doc": "Timestamp Unix de cuándo vence la comisión para pago"
        },
        {
            "name": "payment_date",
            "type": ["null", "long"],
            "doc": "Timestamp Unix de cuándo se pagó la comisión",
            "default": None
        },
        {
            "name": "status",
            "type": {
                "type": "enum",
                "name": "CommissionStatus",
                "symbols": ["PENDING", "APPROVED", "PAID", "DISPUTED"]
            },
            "doc": "Estado actual de la comisión"
        },
        {
            "name": "metrics",
            "type": "CommissionMetricsPayload",
            "doc": "Métricas de rendimiento para esta comisión"
        }
    ]
}


# Esquema de carga de métricas de analíticas
ANALYTICS_METRICS_PAYLOAD_SCHEMA = {
    "type": "record",
    "name": "AnalyticsMetricsPayload",
    "namespace": "com.alpes.partners.payloads",
    "doc": "Carga de métricas de analíticas para reportes",
    "fields": [
        {
            "name": "total_clicks",
            "type": "long",
            "doc": "Número total de clics en el período"
        },
        {
            "name": "total_conversions",
            "type": "long",
            "doc": "Número total de conversiones en el período"
        },
        {
            "name": "total_revenue",
            "type": "double",
            "doc": "Ingresos totales generados en el período"
        },
        {
            "name": "total_commission",
            "type": "double",
            "doc": "Comisión total ganada en el período"
        },
        {
            "name": "currency",
            "type": "string",
            "doc": "Moneda para cantidades de ingresos y comisiones"
        },
        {
            "name": "top_campaigns",
            "type": {
                "type": "array",
                "items": "string"
            },
            "doc": "Array de IDs de campañas con mejor rendimiento",
            "default": []
        }
    ]
}


# Esquema de carga de evento de analíticas
ANALYTICS_EVENT_PAYLOAD_SCHEMA = {
    "type": "record",
    "name": "AnalyticsEventPayload",
    "namespace": "com.alpes.partners.payloads",
    "doc": "Carga de evento de analíticas con datos de rendimiento",
    "fields": [
        {
            "name": "partner_id",
            "type": "string",
            "doc": "ID de socio para datos de analíticas"
        },
        {
            "name": "campaign_id",
            "type": ["null", "string"],
            "doc": "ID de campaña opcional para analíticas específicas de campaña",
            "default": None
        },
        {
            "name": "period_start",
            "type": "long",
            "doc": "Timestamp Unix para inicio del período de analíticas"
        },
        {
            "name": "period_end",
            "type": "long",
            "doc": "Timestamp Unix para fin del período de analíticas"
        },
        {
            "name": "metrics",
            "type": "AnalyticsMetricsPayload",
            "doc": "Métricas de analíticas para el período"
        }
    ]
}


# Esquema de carga de error
ERROR_PAYLOAD_SCHEMA = {
    "type": "record",
    "name": "ErrorPayload",
    "namespace": "com.alpes.partners.payloads",
    "doc": "Carga de información de error para eventos de error",
    "fields": [
        {
            "name": "error_code",
            "type": "string",
            "doc": "Código de error legible por máquina"
        },
        {
            "name": "error_message",
            "type": "string",
            "doc": "Mensaje de error legible por humanos"
        },
        {
            "name": "error_type",
            "type": {
                "type": "enum",
                "name": "ErrorType",
                "symbols": ["VALIDATION", "BUSINESS_RULE", "TECHNICAL", "EXTERNAL"]
            },
            "doc": "Clasificación del tipo de error"
        },
        {
            "name": "stack_trace",
            "type": ["null", "string"],
            "doc": "Stack trace para errores técnicos",
            "default": None
        },
        {
            "name": "context",
            "type": {
                "type": "map",
                "values": "string"
            },
            "doc": "Información adicional de contexto del error",
            "default": {}
        }
    ]
}


@dataclass
class SchemaRegistry:
    """
    Registro de esquemas para gestionar esquemas Avro con versionado.
    
    Proporciona:
    - Registro y recuperación de esquemas
    - Verificación de compatibilidad de versiones
    - Soporte de evolución de esquemas
    - Validación de compatibilidad hacia atrás
    """
    
    def __init__(self):
        self._schemas: Dict[str, Dict[str, Dict[str, Any]]] = {
            "cloud_event_envelope": {
                "v1.0": CLOUD_EVENT_ENVELOPE_SCHEMA
            },
            "base_message": {
                "v1.0": BASE_MESSAGE_SCHEMA
            },
            "commission_rate_payload": {
                "v1.0": COMMISSION_RATE_PAYLOAD_SCHEMA
            },
            "partner_event_payload": {
                "v1.0": PARTNER_EVENT_PAYLOAD_SCHEMA
            },
            "campaign_event_payload": {
                "v1.0": CAMPAIGN_EVENT_PAYLOAD_SCHEMA
            },
            "commission_event_payload": {
                "v1.0": COMMISSION_EVENT_PAYLOAD_SCHEMA
            },
            "commission_metrics_payload": {
                "v1.0": COMMISSION_METRICS_PAYLOAD_SCHEMA
            },
            "analytics_event_payload": {
                "v1.0": ANALYTICS_EVENT_PAYLOAD_SCHEMA
            },
            "analytics_metrics_payload": {
                "v1.0": ANALYTICS_METRICS_PAYLOAD_SCHEMA
            },
            "error_payload": {
                "v1.0": ERROR_PAYLOAD_SCHEMA
            }
        }
    
    def get_schema(self, schema_name: str, version: str = "v1.0") -> Optional[Dict[str, Any]]:
        """Obtener esquema por nombre y versión."""
        return self._schemas.get(schema_name, {}).get(version)
    
    def register_schema(self, schema_name: str, version: str, schema: Dict[str, Any]) -> None:
        """Registrar nueva versión de esquema."""
        if schema_name not in self._schemas:
            self._schemas[schema_name] = {}
        
        self._schemas[schema_name][version] = schema
    
    def get_latest_version(self, schema_name: str) -> Optional[str]:
        """Obtener última versión del esquema."""
        if schema_name not in self._schemas:
            return None
        
        versions = list(self._schemas[schema_name].keys())
        if not versions:
            return None
        
        # Ordenamiento simple de versiones (asume formato v1.0)
        versions.sort(key=lambda x: tuple(map(int, x[1:].split('.'))))
        return versions[-1]
    
    def is_compatible(self, schema_name: str, from_version: str, to_version: str) -> bool:
        """
        Verificar si las versiones de esquemas son compatibles.
        
        Por ahora, implementa compatibilidad hacia adelante simple:
        - La misma versión mayor es compatible
        - Las versiones menores más altas son compatibles con las más bajas
        """
        if schema_name not in self._schemas:
            return False
        
        if from_version == to_version:
            return True
        
        try:
            from_parts = from_version[1:].split('.')  # Remove 'v' prefix
            to_parts = to_version[1:].split('.')
            
            from_major, from_minor = int(from_parts[0]), int(from_parts[1])
            to_major, to_minor = int(to_parts[0]), int(to_parts[1])
            
            # La misma versión mayor con versión menor igual o superior es compatible
            return from_major == to_major and to_minor >= from_minor
            
        except (IndexError, ValueError):
            return False
    
    def get_all_schemas(self) -> Dict[str, Dict[str, Dict[str, Any]]]:
        """Obtener todos los esquemas registrados."""
        return self._schemas.copy()
    
    def validate_schema_evolution(self, schema_name: str, new_schema: Dict[str, Any]) -> List[str]:
        """
        Validar reglas de evolución de esquemas.
        
        Retorna lista de problemas de compatibilidad, vacía si es compatible.
        """
        issues = []
        
        latest_version = self.get_latest_version(schema_name)
        if not latest_version:
            return issues  # No hay versión anterior para comparar
        
        current_schema = self.get_schema(schema_name, latest_version)
        if not current_schema:
            return issues
        
        # Verificaciones básicas de compatibilidad
        # 1. No se pueden eliminar campos requeridos
        current_fields = {f["name"]: f for f in current_schema.get("fields", [])}
        new_fields = {f["name"]: f for f in new_schema.get("fields", [])}
        
        for field_name, field_def in current_fields.items():
            if field_name not in new_fields:
                # Campo eliminado - verificar si tenía un valor por defecto
                if "default" not in field_def:
                    issues.append(f"Campo requerido '{field_name}' eliminado sin valor por defecto")
            else:
                # Campo existe - verificar compatibilidad de tipos
                current_type = field_def.get("type")
                new_type = new_fields[field_name].get("type")
                
                if current_type != new_type:
                    # Tipo cambiado - esto podría romper compatibilidad
                    issues.append(f"Campo '{field_name}' cambió de tipo de {current_type} a {new_type}")
        
        # 2. Los nuevos campos requeridos deben tener valores por defecto
        for field_name, field_def in new_fields.items():
            if field_name not in current_fields:
                # Campo nuevo
                if "default" not in field_def and not self._is_optional_type(field_def.get("type")):
                    issues.append(f"Nuevo campo requerido '{field_name}' agregado sin valor por defecto")
        
        return issues
    
    def _is_optional_type(self, field_type) -> bool:
        """Verificar si el tipo de campo es opcional (unión con null)."""
        if isinstance(field_type, list):
            return "null" in field_type
        return False


# Instancia global del registro de esquemas
schema_registry = SchemaRegistry()


# Funciones de utilidad para operaciones de esquemas
def get_cloud_event_schema() -> Dict[str, Any]:
    """Obtener esquema de sobre CloudEvent."""
    return CLOUD_EVENT_ENVELOPE_SCHEMA


def get_base_message_schema() -> Dict[str, Any]:
    """Obtener esquema de mensaje base."""
    return BASE_MESSAGE_SCHEMA


def create_cloud_event_envelope(event_type: str, source: str, data: bytes, **kwargs) -> Dict[str, Any]:
    """Crear sobre CloudEvent con datos proporcionados."""
    import uuid
    from datetime import datetime, timezone
    
    envelope = {
        "specversion": "1.0",
        "type": event_type,
        "source": source,
        "id": str(uuid.uuid4()),
        "time": datetime.now(timezone.utc).isoformat(),
        "datacontenttype": "application/json",
        "data": data
    }
    
    # Agregar campos opcionales
    if "subject" in kwargs:
        envelope["subject"] = kwargs["subject"]
    
    return envelope


def validate_message_schema(message_data: Dict[str, Any], schema_name: str, version: str = "v1.0") -> bool:
    """
    Validar mensaje contra esquema.
    
    Esta es una validación simplificada - en producción, usarías una librería Avro apropiada.
    """
    schema = schema_registry.get_schema(schema_name, version)
    if not schema:
        return False
    
    # Validación básica de campos
    required_fields = [
        field["name"] for field in schema.get("fields", [])
        if "default" not in field and not schema_registry._is_optional_type(field.get("type"))
    ]
    
    for field_name in required_fields:
        if field_name not in message_data:
            return False
    
    return True
