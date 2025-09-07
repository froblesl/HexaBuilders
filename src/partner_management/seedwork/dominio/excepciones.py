from typing import Any, Dict, List, Optional, Union
from enum import Enum


class ErrorSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    VALIDATION = "validation"
    BUSINESS_RULE = "business_rule"
    AUTHORIZATION = "authorization"
    NOT_FOUND = "not_found"
    CONFLICT = "conflict"
    EXTERNAL_SERVICE = "external_service"
    TECHNICAL = "technical"


class DomainException(Exception):
    def __init__(
        self,
        message: str,
        error_code: str,
        category: ErrorCategory = ErrorCategory.TECHNICAL,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        context: Optional[Dict[str, Any]] = None,
        inner_exception: Optional[Exception] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.category = category
        self.severity = severity
        self.context = context or {}
        self.inner_exception = inner_exception
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'error_type': self.__class__.__name__,
            'message': self.message,
            'error_code': self.error_code,
            'category': self.category.value,
            'severity': self.severity.value,
            'context': self.context,
            'inner_exception': str(self.inner_exception) if self.inner_exception else None
        }
    
    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"error_code={self.error_code}, "
            f"category={self.category.value}, "
            f"message='{self.message}')"
        )


class BusinessRuleViolationException(DomainException):
    def __init__(
        self,
        message: str,
        rule_name: str,
        violations: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None,
        entity_id: Optional[str] = None
    ):
        error_code = f"BUSINESS_RULE_VIOLATION_{rule_name.upper()}"
        super().__init__(
            message=message,
            error_code=error_code,
            category=ErrorCategory.BUSINESS_RULE,
            severity=ErrorSeverity.HIGH,
            context=context
        )
        self.rule_name = rule_name
        self.violations = violations or [message]
        self.entity_id = entity_id
    
    def add_violation(self, violation: str) -> None:
        self.violations.append(violation)
    
    def has_multiple_violations(self) -> bool:
        return len(self.violations) > 1
    
    def get_all_violations(self) -> str:
        return "; ".join(self.violations)


class EntityNotFoundException(DomainException):
    def __init__(
        self,
        entity_type: str,
        entity_id: str,
        context: Optional[Dict[str, Any]] = None
    ):
        message = f"{entity_type} with ID '{entity_id}' was not found"
        error_code = f"{entity_type.upper()}_NOT_FOUND"
        
        super().__init__(
            message=message,
            error_code=error_code,
            category=ErrorCategory.NOT_FOUND,
            severity=ErrorSeverity.MEDIUM,
            context=context
        )
        self.entity_type = entity_type
        self.entity_id = entity_id


class InvalidOperationException(DomainException):
    def __init__(
        self,
        message: str,
        operation: str,
        current_state: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        error_code = f"INVALID_OPERATION_{operation.upper()}"
        
        super().__init__(
            message=message,
            error_code=error_code,
            category=ErrorCategory.BUSINESS_RULE,
            severity=ErrorSeverity.HIGH,
            context=context
        )
        self.operation = operation
        self.current_state = current_state


class ValidationException(DomainException):
    def __init__(
        self,
        message: str = "Validation failed",
        field_errors: Optional[Dict[str, List[str]]] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code="VALIDATION_FAILED",
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.MEDIUM,
            context=context
        )
        self.field_errors = field_errors or {}
    
    def add_field_error(self, field: str, error: str) -> None:
        if field not in self.field_errors:
            self.field_errors[field] = []
        self.field_errors[field].append(error)
    
    def has_field_errors(self) -> bool:
        return bool(self.field_errors)
    
    def get_field_errors(self, field: str) -> List[str]:
        return self.field_errors.get(field, [])
    
    def get_all_errors(self) -> List[str]:
        all_errors = [self.message]
        for field, errors in self.field_errors.items():
            for error in errors:
                all_errors.append(f"{field}: {error}")
        return all_errors


class ConcurrencyException(DomainException):
    def __init__(
        self,
        entity_type: str,
        entity_id: str,
        expected_version: int,
        actual_version: int,
        context: Optional[Dict[str, Any]] = None
    ):
        message = (
            f"Concurrency conflict for {entity_type} '{entity_id}': "
            f"expected version {expected_version}, but actual version is {actual_version}"
        )
        
        super().__init__(
            message=message,
            error_code="CONCURRENCY_CONFLICT",
            category=ErrorCategory.CONFLICT,
            severity=ErrorSeverity.HIGH,
            context=context
        )
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.expected_version = expected_version
        self.actual_version = actual_version


class AuthorizationException(DomainException):
    def __init__(
        self,
        message: str,
        user_id: Optional[str] = None,
        resource: Optional[str] = None,
        action: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_FAILED",
            category=ErrorCategory.AUTHORIZATION,
            severity=ErrorSeverity.HIGH,
            context=context
        )
        self.user_id = user_id
        self.resource = resource
        self.action = action


class ExternalServiceException(DomainException):
    def __init__(
        self,
        message: str,
        service_name: str,
        operation: str,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        error_code = f"EXTERNAL_SERVICE_ERROR_{service_name.upper()}"
        
        super().__init__(
            message=message,
            error_code=error_code,
            category=ErrorCategory.EXTERNAL_SERVICE,
            severity=ErrorSeverity.HIGH,
            context=context
        )
        self.service_name = service_name
        self.operation = operation
        self.status_code = status_code
        self.response_data = response_data


class ConfigurationException(DomainException):
    def __init__(
        self,
        message: str,
        config_key: str,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code="CONFIGURATION_ERROR",
            category=ErrorCategory.TECHNICAL,
            severity=ErrorSeverity.CRITICAL,
            context=context
        )
        self.config_key = config_key


class DomainExceptionBuilder:
    def __init__(self):
        self._violations: List[str] = []
        self._field_errors: Dict[str, List[str]] = {}
        self._context: Dict[str, Any] = {}
        self._severity = ErrorSeverity.MEDIUM
        self._entity_id: Optional[str] = None
    
    def add_violation(self, violation: str) -> 'DomainExceptionBuilder':
        self._violations.append(violation)
        return self
    
    def add_field_error(self, field: str, error: str) -> 'DomainExceptionBuilder':
        if field not in self._field_errors:
            self._field_errors[field] = []
        self._field_errors[field].append(error)
        return self
    
    def with_context(self, key: str, value: Any) -> 'DomainExceptionBuilder':
        self._context[key] = value
        return self
    
    def with_severity(self, severity: ErrorSeverity) -> 'DomainExceptionBuilder':
        self._severity = severity
        return self
    
    def with_entity_id(self, entity_id: str) -> 'DomainExceptionBuilder':
        self._entity_id = entity_id
        return self
    
    def build_validation_exception(self, message: str = "Validation failed") -> ValidationException:
        return ValidationException(
            message=message,
            field_errors=self._field_errors,
            context=self._context
        )
    
    def build_business_rule_exception(
        self, 
        message: str, 
        rule_name: str
    ) -> BusinessRuleViolationException:
        return BusinessRuleViolationException(
            message=message,
            rule_name=rule_name,
            violations=self._violations,
            context=self._context,
            entity_id=self._entity_id
        )
    
    def has_errors(self) -> bool:
        return bool(self._violations or self._field_errors)


# Utility functions for common exception scenarios
def entity_not_found(entity_type: str, entity_id: str) -> EntityNotFoundException:
    return EntityNotFoundException(entity_type, entity_id)


def invalid_state_transition(
    current_state: str, 
    attempted_transition: str
) -> InvalidOperationException:
    return InvalidOperationException(
        message=f"Cannot transition from '{current_state}' to '{attempted_transition}'",
        operation="state_transition",
        current_state=current_state
    )


def business_rule_violation(rule_name: str, message: str) -> BusinessRuleViolationException:
    return BusinessRuleViolationException(
        message=message,
        rule_name=rule_name
    )


def validation_failed(field_errors: Dict[str, List[str]]) -> ValidationException:
    return ValidationException(
        message="Input validation failed",
        field_errors=field_errors
    )
