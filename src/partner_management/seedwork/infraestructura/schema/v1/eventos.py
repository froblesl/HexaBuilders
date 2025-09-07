from typing import Dict, Any, List
from .mensajes import BASE_MESSAGE_SCHEMA


# Base event schema extending base message
BASE_EVENT_SCHEMA = {
    "type": "record",
    "name": "BaseEvent",
    "namespace": "com.hexabuilders.partners.events",
    "doc": "Base schema for all events with common metadata",
    "fields": BASE_MESSAGE_SCHEMA["fields"] + [
        {
            "name": "event_name",
            "type": "string",
            "doc": "Human-readable event name"
        },
        {
            "name": "event_type",
            "type": {
                "type": "enum",
                "name": "EventTypeClassification",
                "symbols": ["DOMAIN", "INTEGRATION", "NOTIFICATION"]
            },
            "doc": "Event type classification"
        },
        {
            "name": "occurred_on",
            "type": "long",
            "doc": "Unix timestamp when event occurred"
        }
    ]
}


# Domain event schema for internal communication
DOMAIN_EVENT_SCHEMA = {
    "type": "record",
    "name": "DomainEvent",
    "namespace": "com.hexabuilders.partners.events.domain",
    "doc": "Domain event for internal module communication",
    "fields": BASE_EVENT_SCHEMA["fields"] + [
        {
            "name": "bounded_context",
            "type": "string",
            "doc": "Bounded context where event originated"
        },
        {
            "name": "event_data",
            "type": {
                "type": "map",
                "values": ["null", "string", "int", "double", "boolean"]
            },
            "doc": "Event-specific payload data",
            "default": {}
        }
    ]
}


# Integration event schema for external communication
INTEGRATION_EVENT_SCHEMA = {
    "type": "record",
    "name": "IntegrationEvent", 
    "namespace": "com.hexabuilders.partners.events.integration",
    "doc": "Integration event for cross-service communication",
    "fields": BASE_EVENT_SCHEMA["fields"] + [
        {
            "name": "cloud_event_envelope",
            "type": ["null", {
                "type": "map",
                "values": "string"
            }],
            "doc": "CloudEvent envelope metadata",
            "default": None
        },
        {
            "name": "external_system",
            "type": ["null", "string"],
            "doc": "Target external system identifier",
            "default": None
        },
        {
            "name": "event_data",
            "type": "bytes",
            "doc": "Serialized event payload for external systems"
        }
    ]
}


# Partner domain events
PARTNER_CREATED_EVENT_SCHEMA = {
    "type": "record",
    "name": "PartnerCreatedEvent",
    "namespace": "com.hexabuilders.partners.events.domain.partner",
    "doc": "Event fired when a new partner is created",
    "fields": DOMAIN_EVENT_SCHEMA["fields"] + [
        {
            "name": "partner_data",
            "type": {
                "type": "record",
                "name": "PartnerCreatedPayload",
                "fields": [
                    {"name": "partner_id", "type": "string"},
                    {"name": "business_name", "type": "string"},
                    {"name": "email", "type": "string"},
                    {"name": "category", "type": "string"},
                    {"name": "country", "type": "string"},
                    {"name": "registration_date", "type": "long"}
                ]
            },
            "doc": "Partner creation data"
        }
    ]
}


PARTNER_STATUS_CHANGED_EVENT_SCHEMA = {
    "type": "record",
    "name": "PartnerStatusChangedEvent",
    "namespace": "com.hexabuilders.partners.events.domain.partner",
    "doc": "Event fired when partner status changes",
    "fields": DOMAIN_EVENT_SCHEMA["fields"] + [
        {
            "name": "status_change_data",
            "type": {
                "type": "record",
                "name": "PartnerStatusChangePayload",
                "fields": [
                    {"name": "partner_id", "type": "string"},
                    {"name": "old_status", "type": "string"},
                    {"name": "new_status", "type": "string"},
                    {"name": "change_reason", "type": ["null", "string"], "default": None},
                    {"name": "changed_by", "type": ["null", "string"], "default": None},
                    {"name": "change_timestamp", "type": "long"}
                ]
            },
            "doc": "Status change details"
        }
    ]
}


PARTNER_ACTIVATED_EVENT_SCHEMA = {
    "type": "record",
    "name": "PartnerActivatedEvent",
    "namespace": "com.hexabuilders.partners.events.domain.partner",
    "doc": "Event fired when partner is activated",
    "fields": DOMAIN_EVENT_SCHEMA["fields"] + [
        {
            "name": "activation_data",
            "type": {
                "type": "record",
                "name": "PartnerActivationPayload",
                "fields": [
                    {"name": "partner_id", "type": "string"},
                    {"name": "activation_date", "type": "long"},
                    {"name": "activated_by", "type": ["null", "string"], "default": None},
                    {"name": "commission_rates", "type": {
                        "type": "array",
                        "items": {
                            "type": "record",
                            "name": "CommissionRateInfo",
                            "fields": [
                                {"name": "rate_type", "type": "string"},
                                {"name": "percentage", "type": "double"},
                                {"name": "currency", "type": "string"}
                            ]
                        }
                    }, "default": []}
                ]
            },
            "doc": "Partner activation details"
        }
    ]
}


# Campaign domain events
CAMPAIGN_CREATED_EVENT_SCHEMA = {
    "type": "record",
    "name": "CampaignCreatedEvent",
    "namespace": "com.hexabuilders.partners.events.domain.campaign",
    "doc": "Event fired when a new campaign is created",
    "fields": DOMAIN_EVENT_SCHEMA["fields"] + [
        {
            "name": "campaign_data",
            "type": {
                "type": "record",
                "name": "CampaignCreatedPayload",
                "fields": [
                    {"name": "campaign_id", "type": "string"},
                    {"name": "name", "type": "string"},
                    {"name": "advertiser_name", "type": "string"},
                    {"name": "start_date", "type": "long"},
                    {"name": "end_date", "type": ["null", "long"], "default": None},
                    {"name": "budget_amount", "type": "double"},
                    {"name": "budget_currency", "type": "string"}
                ]
            },
            "doc": "Campaign creation data"
        }
    ]
}


PARTNER_ASSIGNED_TO_CAMPAIGN_EVENT_SCHEMA = {
    "type": "record",
    "name": "PartnerAssignedToCampaignEvent",
    "namespace": "com.hexabuilders.partners.events.domain.campaign",
    "doc": "Event fired when partner is assigned to campaign",
    "fields": DOMAIN_EVENT_SCHEMA["fields"] + [
        {
            "name": "assignment_data",
            "type": {
                "type": "record",
                "name": "PartnerCampaignAssignmentPayload",
                "fields": [
                    {"name": "campaign_id", "type": "string"},
                    {"name": "partner_id", "type": "string"},
                    {"name": "assignment_date", "type": "long"},
                    {"name": "assigned_by", "type": ["null", "string"], "default": None},
                    {"name": "commission_rate", "type": {
                        "type": "record",
                        "name": "AssignmentCommissionRate",
                        "fields": [
                            {"name": "rate_type", "type": "string"},
                            {"name": "percentage", "type": "double"}
                        ]
                    }}
                ]
            },
            "doc": "Partner-campaign assignment details"
        }
    ]
}


# Commission domain events
COMMISSION_CALCULATED_EVENT_SCHEMA = {
    "type": "record",
    "name": "CommissionCalculatedEvent",
    "namespace": "com.hexabuilders.partners.events.domain.commission",
    "doc": "Event fired when commission is calculated",
    "fields": DOMAIN_EVENT_SCHEMA["fields"] + [
        {
            "name": "commission_data",
            "type": {
                "type": "record",
                "name": "CommissionCalculatedPayload",
                "fields": [
                    {"name": "commission_id", "type": "string"},
                    {"name": "partner_id", "type": "string"},
                    {"name": "campaign_id", "type": "string"},
                    {"name": "amount", "type": "double"},
                    {"name": "currency", "type": "string"},
                    {"name": "calculation_method", "type": "string"},
                    {"name": "calculation_date", "type": "long"},
                    {"name": "due_date", "type": "long"},
                    {"name": "transaction_count", "type": "int"},
                    {"name": "conversion_count", "type": "int"}
                ]
            },
            "doc": "Commission calculation details"
        }
    ]
}


COMMISSION_PAID_EVENT_SCHEMA = {
    "type": "record",
    "name": "CommissionPaidEvent",
    "namespace": "com.hexabuilders.partners.events.domain.commission",
    "doc": "Event fired when commission is paid",
    "fields": DOMAIN_EVENT_SCHEMA["fields"] + [
        {
            "name": "payment_data",
            "type": {
                "type": "record",
                "name": "CommissionPaymentPayload",
                "fields": [
                    {"name": "commission_id", "type": "string"},
                    {"name": "partner_id", "type": "string"},
                    {"name": "amount_paid", "type": "double"},
                    {"name": "currency", "type": "string"},
                    {"name": "payment_date", "type": "long"},
                    {"name": "payment_method", "type": "string"},
                    {"name": "transaction_reference", "type": ["null", "string"], "default": None},
                    {"name": "paid_by", "type": ["null", "string"], "default": None}
                ]
            },
            "doc": "Commission payment details"
        }
    ]
}


# Analytics domain events
ANALYTICS_CALCULATED_EVENT_SCHEMA = {
    "type": "record",
    "name": "AnalyticsCalculatedEvent",
    "namespace": "com.hexabuilders.partners.events.domain.analytics",
    "doc": "Event fired when analytics are calculated",
    "fields": DOMAIN_EVENT_SCHEMA["fields"] + [
        {
            "name": "analytics_data",
            "type": {
                "type": "record",
                "name": "AnalyticsCalculatedPayload",
                "fields": [
                    {"name": "partner_id", "type": "string"},
                    {"name": "campaign_id", "type": ["null", "string"], "default": None},
                    {"name": "period_start", "type": "long"},
                    {"name": "period_end", "type": "long"},
                    {"name": "total_clicks", "type": "long"},
                    {"name": "total_conversions", "type": "long"},
                    {"name": "total_revenue", "type": "double"},
                    {"name": "total_commission", "type": "double"},
                    {"name": "currency", "type": "string"},
                    {"name": "calculation_date", "type": "long"}
                ]
            },
            "doc": "Analytics calculation data"
        }
    ]
}


# Integration events for external systems
PARTNER_REGISTRATION_COMPLETED_INTEGRATION_EVENT_SCHEMA = {
    "type": "record",
    "name": "PartnerRegistrationCompletedIntegrationEvent",
    "namespace": "com.hexabuilders.partners.events.integration",
    "doc": "Integration event for external systems when partner registration completes",
    "fields": INTEGRATION_EVENT_SCHEMA["fields"] + [
        {
            "name": "partner_registration_data",
            "type": {
                "type": "record",
                "name": "PartnerRegistrationIntegrationPayload",
                "fields": [
                    {"name": "partner_id", "type": "string"},
                    {"name": "business_name", "type": "string"},
                    {"name": "email", "type": "string"},
                    {"name": "category", "type": "string"},
                    {"name": "country", "type": "string"},
                    {"name": "registration_date", "type": "long"},
                    {"name": "external_partner_id", "type": ["null", "string"], "default": None},
                    {"name": "integration_metadata", "type": {
                        "type": "map",
                        "values": "string"
                    }, "default": {}}
                ]
            },
            "doc": "Partner registration data for external systems"
        }
    ]
}


COMMISSION_PROCESSED_INTEGRATION_EVENT_SCHEMA = {
    "type": "record",
    "name": "CommissionProcessedIntegrationEvent",
    "namespace": "com.hexabuilders.partners.events.integration",
    "doc": "Integration event when commission is processed",
    "fields": INTEGRATION_EVENT_SCHEMA["fields"] + [
        {
            "name": "commission_processing_data",
            "type": {
                "type": "record",
                "name": "CommissionProcessingIntegrationPayload",
                "fields": [
                    {"name": "commission_id", "type": "string"},
                    {"name": "partner_id", "type": "string"},
                    {"name": "external_partner_id", "type": ["null", "string"], "default": None},
                    {"name": "amount", "type": "double"},
                    {"name": "currency", "type": "string"},
                    {"name": "status", "type": "string"},
                    {"name": "processing_date", "type": "long"},
                    {"name": "external_system_references", "type": {
                        "type": "map",
                        "values": "string"
                    }, "default": {}}
                ]
            },
            "doc": "Commission processing data for external systems"
        }
    ]
}


# Event metadata schema for event families
EVENT_METADATA_SCHEMA = {
    "type": "record",
    "name": "EventMetadata",
    "namespace": "com.hexabuilders.partners.events.metadata",
    "doc": "Metadata schema for event tracing and correlation",
    "fields": [
        {
            "name": "event_id",
            "type": "string",
            "doc": "Unique event identifier (UUID)"
        },
        {
            "name": "correlation_id", 
            "type": "string",
            "doc": "Correlation ID for tracing related events"
        },
        {
            "name": "causation_id",
            "type": ["null", "string"],
            "doc": "ID of event that caused this event",
            "default": None
        },
        {
            "name": "occurred_on",
            "type": "long",
            "doc": "Unix timestamp when event occurred"
        },
        {
            "name": "event_version",
            "type": "int",
            "doc": "Event schema version",
            "default": 1
        },
        {
            "name": "source",
            "type": ["null", "string"],
            "doc": "Source service that generated the event",
            "default": None
        },
        {
            "name": "user_id",
            "type": ["null", "string"],
            "doc": "User ID who triggered the event",
            "default": None
        },
        {
            "name": "tenant_id",
            "type": ["null", "string"],
            "doc": "Tenant ID for multi-tenancy",
            "default": None
        }
    ]
}


# Event inheritance patterns for event families
PARTNER_EVENT_FAMILY_SCHEMA = {
    "type": "record",
    "name": "PartnerEventFamily",
    "namespace": "com.hexabuilders.partners.events.families",
    "doc": "Base schema for all partner-related events",
    "fields": DOMAIN_EVENT_SCHEMA["fields"] + [
        {
            "name": "partner_context",
            "type": {
                "type": "record",
                "name": "PartnerEventContext",
                "fields": [
                    {"name": "partner_id", "type": "string"},
                    {"name": "partner_category", "type": ["null", "string"], "default": None},
                    {"name": "partner_status", "type": ["null", "string"], "default": None}
                ]
            },
            "doc": "Common partner context for all partner events"
        }
    ]
}


CAMPAIGN_EVENT_FAMILY_SCHEMA = {
    "type": "record", 
    "name": "CampaignEventFamily",
    "namespace": "com.hexabuilders.partners.events.families",
    "doc": "Base schema for all campaign-related events",
    "fields": DOMAIN_EVENT_SCHEMA["fields"] + [
        {
            "name": "campaign_context",
            "type": {
                "type": "record",
                "name": "CampaignEventContext", 
                "fields": [
                    {"name": "campaign_id", "type": "string"},
                    {"name": "campaign_name", "type": ["null", "string"], "default": None},
                    {"name": "campaign_status", "type": ["null", "string"], "default": None}
                ]
            },
            "doc": "Common campaign context for all campaign events"
        }
    ]
}


# Validation rules for event schemas
EVENT_VALIDATION_RULES = {
    "partner_events": [
        "partner_id must be valid UUID",
        "business_name must not be empty",
        "email must be valid email format",
        "category must be one of: AFFILIATE, INFLUENCER, MEDIA, B2B_PARTNER",
        "country must be ISO 3166-1 alpha-2 code"
    ],
    "campaign_events": [
        "campaign_id must be valid UUID", 
        "name must not be empty",
        "start_date must be in future or present",
        "end_date must be after start_date if provided",
        "budget_amount must be positive",
        "budget_currency must be ISO 4217 code"
    ],
    "commission_events": [
        "commission_id must be valid UUID",
        "partner_id must be valid UUID", 
        "campaign_id must be valid UUID",
        "amount must be positive",
        "currency must be ISO 4217 code",
        "due_date must be after calculation_date"
    ]
}


# Cross-service event compatibility matrix
EVENT_COMPATIBILITY_MATRIX = {
    "v1.0": {
        "compatible_with": ["v1.0"],
        "breaking_changes": []
    },
    "v1.1": {
        "compatible_with": ["v1.0", "v1.1"], 
        "breaking_changes": [],
        "new_features": [
            "Added optional external_system field to integration events",
            "Added metadata field to partner events"
        ]
    }
}


def get_event_schema_by_name(event_name: str, namespace: str = None) -> Dict[str, Any]:
    """Get event schema by event name and optional namespace."""
    schema_map = {
        "PartnerCreatedEvent": PARTNER_CREATED_EVENT_SCHEMA,
        "PartnerStatusChangedEvent": PARTNER_STATUS_CHANGED_EVENT_SCHEMA,
        "PartnerActivatedEvent": PARTNER_ACTIVATED_EVENT_SCHEMA,
        "CampaignCreatedEvent": CAMPAIGN_CREATED_EVENT_SCHEMA,
        "PartnerAssignedToCampaignEvent": PARTNER_ASSIGNED_TO_CAMPAIGN_EVENT_SCHEMA,
        "CommissionCalculatedEvent": COMMISSION_CALCULATED_EVENT_SCHEMA,
        "CommissionPaidEvent": COMMISSION_PAID_EVENT_SCHEMA,
        "AnalyticsCalculatedEvent": ANALYTICS_CALCULATED_EVENT_SCHEMA,
        "PartnerRegistrationCompletedIntegrationEvent": PARTNER_REGISTRATION_COMPLETED_INTEGRATION_EVENT_SCHEMA,
        "CommissionProcessedIntegrationEvent": COMMISSION_PROCESSED_INTEGRATION_EVENT_SCHEMA
    }
    
    return schema_map.get(event_name)


def validate_event_compatibility(from_version: str, to_version: str) -> bool:
    """Validate event compatibility between versions."""
    if from_version not in EVENT_COMPATIBILITY_MATRIX:
        return False
    
    return to_version in EVENT_COMPATIBILITY_MATRIX[from_version]["compatible_with"]


def get_event_validation_rules(event_category: str) -> List[str]:
    """Get validation rules for event category."""
    return EVENT_VALIDATION_RULES.get(event_category, [])
