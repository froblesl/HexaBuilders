from typing import Dict, Any, List
from .mensajes import BASE_MESSAGE_SCHEMA


# Base command schema extending base message
BASE_COMMAND_SCHEMA = {
    "type": "record",
    "name": "BaseCommand",
    "namespace": "com.hexabuilders.partners.commands",
    "doc": "Base schema for all commands with common metadata",
    "fields": BASE_MESSAGE_SCHEMA["fields"] + [
        {
            "name": "command_name",
            "type": "string",
            "doc": "Human-readable command name"
        },
        {
            "name": "priority",
            "type": {
                "type": "enum",
                "name": "CommandPriority",
                "symbols": ["LOW", "NORMAL", "HIGH", "URGENT"]
            },
            "doc": "Command execution priority",
            "default": "NORMAL"
        },
        {
            "name": "expected_execution_time_ms",
            "type": ["null", "long"],
            "doc": "Expected execution time in milliseconds",
            "default": None
        },
        {
            "name": "timeout_ms",
            "type": ["null", "long"],
            "doc": "Command timeout in milliseconds",
            "default": None
        }
    ]
}


# Command result schema for asynchronous processing
COMMAND_RESULT_SCHEMA = {
    "type": "record",
    "name": "CommandResult",
    "namespace": "com.hexabuilders.partners.commands.results",
    "doc": "Result of command execution",
    "fields": [
        {
            "name": "command_id",
            "type": "string",
            "doc": "ID of executed command"
        },
        {
            "name": "correlation_id", 
            "type": "string",
            "doc": "Correlation ID for tracing"
        },
        {
            "name": "success",
            "type": "boolean",
            "doc": "Whether command executed successfully"
        },
        {
            "name": "result_data",
            "type": ["null", "bytes"],
            "doc": "Serialized result data",
            "default": None
        },
        {
            "name": "error_code",
            "type": ["null", "string"],
            "doc": "Error code if command failed",
            "default": None
        },
        {
            "name": "error_message",
            "type": ["null", "string"],
            "doc": "Error message if command failed", 
            "default": None
        },
        {
            "name": "execution_time_ms",
            "type": ["null", "double"],
            "doc": "Actual execution time in milliseconds",
            "default": None
        },
        {
            "name": "events_generated",
            "type": "int",
            "doc": "Number of domain events generated",
            "default": 0
        },
        {
            "name": "result_metadata",
            "type": {
                "type": "map",
                "values": "string"
            },
            "doc": "Additional result metadata",
            "default": {}
        }
    ]
}


# Partner command schemas
CREATE_PARTNER_COMMAND_SCHEMA = {
    "type": "record",
    "name": "CreatePartnerCommand",
    "namespace": "com.hexabuilders.partners.commands.partner",
    "doc": "Command to create a new partner",
    "fields": BASE_COMMAND_SCHEMA["fields"] + [
        {
            "name": "partner_data",
            "type": {
                "type": "record",
                "name": "CreatePartnerPayload",
                "fields": [
                    {"name": "business_name", "type": "string"},
                    {"name": "email", "type": "string"},
                    {"name": "category", "type": {
                        "type": "enum",
                        "name": "PartnerCategory",
                        "symbols": ["AFFILIATE", "INFLUENCER", "MEDIA", "B2B_PARTNER"]
                    }},
                    {"name": "country", "type": "string"},
                    {"name": "contact_person", "type": ["null", "string"], "default": None},
                    {"name": "phone_number", "type": ["null", "string"], "default": None},
                    {"name": "website", "type": ["null", "string"], "default": None},
                    {"name": "tax_id", "type": ["null", "string"], "default": None},
                    {"name": "initial_commission_rates", "type": {
                        "type": "array",
                        "items": {
                            "type": "record",
                            "name": "InitialCommissionRate",
                            "fields": [
                                {"name": "rate_type", "type": "string"},
                                {"name": "percentage", "type": "double"},
                                {"name": "currency", "type": "string"}
                            ]
                        }
                    }, "default": []}
                ]
            },
            "doc": "Partner creation data"
        }
    ]
}


UPDATE_PARTNER_COMMAND_SCHEMA = {
    "type": "record",
    "name": "UpdatePartnerCommand",
    "namespace": "com.hexabuilders.partners.commands.partner",
    "doc": "Command to update existing partner",
    "fields": BASE_COMMAND_SCHEMA["fields"] + [
        {
            "name": "partner_update_data",
            "type": {
                "type": "record",
                "name": "UpdatePartnerPayload",
                "fields": [
                    {"name": "partner_id", "type": "string"},
                    {"name": "business_name", "type": ["null", "string"], "default": None},
                    {"name": "email", "type": ["null", "string"], "default": None},
                    {"name": "contact_person", "type": ["null", "string"], "default": None},
                    {"name": "phone_number", "type": ["null", "string"], "default": None},
                    {"name": "website", "type": ["null", "string"], "default": None},
                    {"name": "tax_id", "type": ["null", "string"], "default": None},
                    {"name": "expected_version", "type": ["null", "int"], "default": None}
                ]
            },
            "doc": "Partner update data with optional fields"
        }
    ]
}


ACTIVATE_PARTNER_COMMAND_SCHEMA = {
    "type": "record",
    "name": "ActivatePartnerCommand",
    "namespace": "com.hexabuilders.partners.commands.partner",
    "doc": "Command to activate a partner",
    "fields": BASE_COMMAND_SCHEMA["fields"] + [
        {
            "name": "activation_data",
            "type": {
                "type": "record",
                "name": "ActivatePartnerPayload",
                "fields": [
                    {"name": "partner_id", "type": "string"},
                    {"name": "activation_reason", "type": ["null", "string"], "default": None},
                    {"name": "commission_rates", "type": {
                        "type": "array",
                        "items": {
                            "type": "record",
                            "name": "ActivationCommissionRate",
                            "fields": [
                                {"name": "rate_type", "type": "string"},
                                {"name": "percentage", "type": "double"},
                                {"name": "currency", "type": "string"},
                                {"name": "effective_date", "type": "long"},
                                {"name": "expiration_date", "type": ["null", "long"], "default": None}
                            ]
                        }
                    }},
                    {"name": "terms_accepted", "type": "boolean"},
                    {"name": "compliance_verified", "type": "boolean"}
                ]
            },
            "doc": "Partner activation data"
        }
    ]
}


SUSPEND_PARTNER_COMMAND_SCHEMA = {
    "type": "record",
    "name": "SuspendPartnerCommand",
    "namespace": "com.hexabuilders.partners.commands.partner",
    "doc": "Command to suspend a partner",
    "fields": BASE_COMMAND_SCHEMA["fields"] + [
        {
            "name": "suspension_data",
            "type": {
                "type": "record",
                "name": "SuspendPartnerPayload",
                "fields": [
                    {"name": "partner_id", "type": "string"},
                    {"name": "suspension_reason", "type": "string"},
                    {"name": "suspension_type", "type": {
                        "type": "enum",
                        "name": "SuspensionType",
                        "symbols": ["TEMPORARY", "PERMANENT", "INVESTIGATION"]
                    }},
                    {"name": "suspension_until", "type": ["null", "long"], "default": None},
                    {"name": "notify_partner", "type": "boolean", "default": true}
                ]
            },
            "doc": "Partner suspension data"
        }
    ]
}


# Campaign command schemas
CREATE_CAMPAIGN_COMMAND_SCHEMA = {
    "type": "record",
    "name": "CreateCampaignCommand",
    "namespace": "com.hexabuilders.partners.commands.campaign",
    "doc": "Command to create a new campaign",
    "fields": BASE_COMMAND_SCHEMA["fields"] + [
        {
            "name": "campaign_data",
            "type": {
                "type": "record",
                "name": "CreateCampaignPayload",
                "fields": [
                    {"name": "name", "type": "string"},
                    {"name": "description", "type": ["null", "string"], "default": None},
                    {"name": "advertiser_name", "type": "string"},
                    {"name": "advertiser_id", "type": ["null", "string"], "default": None},
                    {"name": "start_date", "type": "long"},
                    {"name": "end_date", "type": ["null", "long"], "default": None},
                    {"name": "budget_amount", "type": "double"},
                    {"name": "budget_currency", "type": "string"},
                    {"name": "campaign_type", "type": "string"},
                    {"name": "target_audience", "type": ["null", "string"], "default": None},
                    {"name": "default_commission_rate", "type": {
                        "type": "record",
                        "name": "DefaultCommissionRate",
                        "fields": [
                            {"name": "rate_type", "type": "string"},
                            {"name": "percentage", "type": "double"}
                        ]
                    }}
                ]
            },
            "doc": "Campaign creation data"
        }
    ]
}


ASSIGN_PARTNER_TO_CAMPAIGN_COMMAND_SCHEMA = {
    "type": "record",
    "name": "AssignPartnerToCampaignCommand",
    "namespace": "com.hexabuilders.partners.commands.campaign",
    "doc": "Command to assign partner to campaign",
    "fields": BASE_COMMAND_SCHEMA["fields"] + [
        {
            "name": "assignment_data",
            "type": {
                "type": "record",
                "name": "AssignPartnerToCampaignPayload",
                "fields": [
                    {"name": "campaign_id", "type": "string"},
                    {"name": "partner_id", "type": "string"},
                    {"name": "assignment_date", "type": "long"},
                    {"name": "custom_commission_rate", "type": ["null", {
                        "type": "record",
                        "name": "CustomCommissionRate",
                        "fields": [
                            {"name": "rate_type", "type": "string"},
                            {"name": "percentage", "type": "double"},
                            {"name": "effective_date", "type": "long"},
                            {"name": "expiration_date", "type": ["null", "long"], "default": None}
                        ]
                    }], "default": None},
                    {"name": "assignment_notes", "type": ["null", "string"], "default": None}
                ]
            },
            "doc": "Partner-campaign assignment data"
        }
    ]
}


# Commission command schemas  
CALCULATE_COMMISSION_COMMAND_SCHEMA = {
    "type": "record",
    "name": "CalculateCommissionCommand",
    "namespace": "com.hexabuilders.partners.commands.commission",
    "doc": "Command to calculate commission for partner",
    "fields": BASE_COMMAND_SCHEMA["fields"] + [
        {
            "name": "calculation_data",
            "type": {
                "type": "record",
                "name": "CalculateCommissionPayload", 
                "fields": [
                    {"name": "partner_id", "type": "string"},
                    {"name": "campaign_id", "type": "string"},
                    {"name": "calculation_period_start", "type": "long"},
                    {"name": "calculation_period_end", "type": "long"},
                    {"name": "transaction_data", "type": {
                        "type": "array",
                        "items": {
                            "type": "record",
                            "name": "TransactionData",
                            "fields": [
                                {"name": "transaction_id", "type": "string"},
                                {"name": "transaction_date", "type": "long"},
                                {"name": "amount", "type": "double"},
                                {"name": "currency", "type": "string"},
                                {"name": "conversion_type", "type": "string"}
                            ]
                        }
                    }},
                    {"name": "override_rate", "type": ["null", {
                        "type": "record", 
                        "name": "OverrideCommissionRate",
                        "fields": [
                            {"name": "rate_type", "type": "string"},
                            {"name": "percentage", "type": "double"},
                            {"name": "reason", "type": "string"}
                        ]
                    }], "default": None}
                ]
            },
            "doc": "Commission calculation data"
        }
    ]
}


APPROVE_COMMISSION_COMMAND_SCHEMA = {
    "type": "record",
    "name": "ApproveCommissionCommand",
    "namespace": "com.hexabuilders.partners.commands.commission",
    "doc": "Command to approve calculated commission",
    "fields": BASE_COMMAND_SCHEMA["fields"] + [
        {
            "name": "approval_data",
            "type": {
                "type": "record",
                "name": "ApproveCommissionPayload",
                "fields": [
                    {"name": "commission_id", "type": "string"},
                    {"name": "approved_amount", "type": "double"},
                    {"name": "approval_notes", "type": ["null", "string"], "default": None},
                    {"name": "payment_due_date", "type": "long"},
                    {"name": "payment_method", "type": ["null", "string"], "default": None}
                ]
            },
            "doc": "Commission approval data"
        }
    ]
}


PROCESS_PAYMENT_COMMAND_SCHEMA = {
    "type": "record",
    "name": "ProcessPaymentCommand",
    "namespace": "com.hexabuilders.partners.commands.commission",
    "doc": "Command to process commission payment",
    "fields": BASE_COMMAND_SCHEMA["fields"] + [
        {
            "name": "payment_data",
            "type": {
                "type": "record",
                "name": "ProcessPaymentPayload",
                "fields": [
                    {"name": "commission_id", "type": "string"},
                    {"name": "payment_amount", "type": "double"},
                    {"name": "payment_currency", "type": "string"},
                    {"name": "payment_method", "type": "string"},
                    {"name": "payment_reference", "type": ["null", "string"], "default": None},
                    {"name": "payment_provider", "type": ["null", "string"], "default": None},
                    {"name": "external_transaction_id", "type": ["null", "string"], "default": None}
                ]
            },
            "doc": "Commission payment processing data"
        }
    ]
}


# Analytics command schemas
CALCULATE_ANALYTICS_COMMAND_SCHEMA = {
    "type": "record",
    "name": "CalculateAnalyticsCommand",
    "namespace": "com.hexabuilders.partners.commands.analytics",
    "doc": "Command to calculate analytics for partner or campaign",
    "fields": BASE_COMMAND_SCHEMA["fields"] + [
        {
            "name": "analytics_calculation_data",
            "type": {
                "type": "record",
                "name": "CalculateAnalyticsPayload",
                "fields": [
                    {"name": "partner_id", "type": ["null", "string"], "default": None},
                    {"name": "campaign_id", "type": ["null", "string"], "default": None},
                    {"name": "calculation_period_start", "type": "long"},
                    {"name": "calculation_period_end", "type": "long"},
                    {"name": "metrics_to_calculate", "type": {
                        "type": "array",
                        "items": "string"
                    }},
                    {"name": "include_projections", "type": "boolean", "default": false},
                    {"name": "aggregation_level", "type": {
                        "type": "enum",
                        "name": "AggregationLevel",
                        "symbols": ["DAILY", "WEEKLY", "MONTHLY", "QUARTERLY"]
                    }, "default": "DAILY"}
                ]
            },
            "doc": "Analytics calculation parameters"
        }
    ]
}


# Command routing and correlation schemas
COMMAND_ROUTING_SCHEMA = {
    "type": "record",
    "name": "CommandRouting",
    "namespace": "com.hexabuilders.partners.commands.routing",
    "doc": "Schema for command routing information",
    "fields": [
        {
            "name": "command_id",
            "type": "string",
            "doc": "Command identifier"
        },
        {
            "name": "handler_service",
            "type": "string",
            "doc": "Service responsible for handling the command"
        },
        {
            "name": "routing_key",
            "type": "string",
            "doc": "Message queue routing key"
        },
        {
            "name": "retry_policy",
            "type": {
                "type": "record",
                "name": "RetryPolicy",
                "fields": [
                    {"name": "max_attempts", "type": "int", "default": 3},
                    {"name": "base_delay_ms", "type": "long", "default": 1000},
                    {"name": "max_delay_ms", "type": "long", "default": 60000},
                    {"name": "exponential_backoff", "type": "boolean", "default": true}
                ]
            },
            "doc": "Retry policy for command processing"
        },
        {
            "name": "circuit_breaker_key",
            "type": ["null", "string"],
            "doc": "Circuit breaker key for error handling",
            "default": None
        }
    ]
}


# Error handling and retry schemas
COMMAND_ERROR_SCHEMA = {
    "type": "record",
    "name": "CommandError",
    "namespace": "com.hexabuilders.partners.commands.errors",
    "doc": "Schema for command processing errors",
    "fields": [
        {
            "name": "command_id",
            "type": "string",
            "doc": "Failed command identifier"
        },
        {
            "name": "error_type",
            "type": {
                "type": "enum",
                "name": "CommandErrorType",
                "symbols": ["VALIDATION", "BUSINESS_RULE", "TECHNICAL", "TIMEOUT", "EXTERNAL_SERVICE"]
            },
            "doc": "Type of command error"
        },
        {
            "name": "error_code",
            "type": "string",
            "doc": "Machine-readable error code"
        },
        {
            "name": "error_message",
            "type": "string",
            "doc": "Human-readable error message"
        },
        {
            "name": "retry_attempt",
            "type": "int",
            "doc": "Current retry attempt number"
        },
        {
            "name": "max_retries",
            "type": "int",
            "doc": "Maximum number of retry attempts"
        },
        {
            "name": "next_retry_at",
            "type": ["null", "long"],
            "doc": "Timestamp for next retry attempt",
            "default": None
        },
        {
            "name": "stack_trace",
            "type": ["null", "string"],
            "doc": "Error stack trace for debugging",
            "default": None
        }
    ]
}


# Command lifecycle tracking schema
COMMAND_LIFECYCLE_SCHEMA = {
    "type": "record",
    "name": "CommandLifecycle",
    "namespace": "com.hexabuilders.partners.commands.lifecycle",
    "doc": "Schema for tracking command lifecycle events",
    "fields": [
        {
            "name": "command_id",
            "type": "string",
            "doc": "Command identifier"
        },
        {
            "name": "lifecycle_event",
            "type": {
                "type": "enum",
                "name": "CommandLifecycleEvent",
                "symbols": ["RECEIVED", "VALIDATED", "EXECUTING", "COMPLETED", "FAILED", "RETRYING", "CANCELLED"]
            },
            "doc": "Command lifecycle event type"
        },
        {
            "name": "timestamp",
            "type": "long",
            "doc": "Event timestamp"
        },
        {
            "name": "handler_instance",
            "type": ["null", "string"],
            "doc": "Handler instance that processed the command",
            "default": None
        },
        {
            "name": "execution_context",
            "type": {
                "type": "map",
                "values": "string"
            },
            "doc": "Additional execution context",
            "default": {}
        }
    ]
}


# Command validation rules
COMMAND_VALIDATION_RULES = {
    "partner_commands": [
        "business_name must not be empty",
        "email must be valid email format",
        "category must be valid enum value",
        "country must be ISO 3166-1 alpha-2 code",
        "commission rates must have positive percentages"
    ],
    "campaign_commands": [
        "name must not be empty",
        "start_date must be in future or present", 
        "end_date must be after start_date if provided",
        "budget_amount must be positive",
        "budget_currency must be ISO 4217 code"
    ],
    "commission_commands": [
        "partner_id must be valid UUID",
        "campaign_id must be valid UUID", 
        "calculation_period_end must be after start",
        "transaction amounts must be positive",
        "currencies must be ISO 4217 codes"
    ]
}


def get_command_schema_by_name(command_name: str) -> Dict[str, Any]:
    """Get command schema by command name."""
    schema_map = {
        "CreatePartnerCommand": CREATE_PARTNER_COMMAND_SCHEMA,
        "UpdatePartnerCommand": UPDATE_PARTNER_COMMAND_SCHEMA,
        "ActivatePartnerCommand": ACTIVATE_PARTNER_COMMAND_SCHEMA,
        "SuspendPartnerCommand": SUSPEND_PARTNER_COMMAND_SCHEMA,
        "CreateCampaignCommand": CREATE_CAMPAIGN_COMMAND_SCHEMA,
        "AssignPartnerToCampaignCommand": ASSIGN_PARTNER_TO_CAMPAIGN_COMMAND_SCHEMA,
        "CalculateCommissionCommand": CALCULATE_COMMISSION_COMMAND_SCHEMA,
        "ApproveCommissionCommand": APPROVE_COMMISSION_COMMAND_SCHEMA,
        "ProcessPaymentCommand": PROCESS_PAYMENT_COMMAND_SCHEMA,
        "CalculateAnalyticsCommand": CALCULATE_ANALYTICS_COMMAND_SCHEMA
    }
    
    return schema_map.get(command_name)


def get_command_validation_rules(command_category: str) -> List[str]:
    """Get validation rules for command category."""
    return COMMAND_VALIDATION_RULES.get(command_category, [])
