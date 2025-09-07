from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TypeVar, Generic
from ..dominio.entidades import AggregateRoot
from ..dominio.eventos import DomainEvent
from ..dominio.excepciones import DomainException, BusinessRuleViolationException


T = TypeVar('T', bound=AggregateRoot)


class DomainService(ABC):
    """
    Clase base para servicios de dominio.
    Proporciona contexto y funcionalidad común para servicios del dominio.
    """
    def __init__(self):
        self._context: Dict[str, Any] = {}
    
    @property
    def context(self) -> Dict[str, Any]:
        """Obtener copia del contexto actual."""
        return self._context.copy()
    
    def set_context(self, key: str, value: Any) -> None:
        """Establecer un valor en el contexto."""
        self._context[key] = value
    
    def clear_context(self) -> None:
        """Limpiar todo el contexto."""
        self._context.clear()


class BusinessRuleValidationService(DomainService):
    """
    Servicio para validación de reglas de negocio en agregados.
    Coordina la validación y recolecta violaciones de reglas.
    """
    def __init__(self):
        super().__init__()
        self._violations: List[str] = []
    
    def validate_rule(self, rule_name: str, condition: bool, error_message: str) -> None:
        """Validar una regla individual y registrar violación si falla."""
        if not condition:
            self._violations.append(f"{rule_name}: {error_message}")
    
    def validate_all_rules(self, entity: AggregateRoot) -> None:
        """Validar todas las reglas para una entidad y lanzar excepción si hay violaciones."""
        self._violations.clear()
        self._perform_validation(entity)
        
        if self._violations:
            raise BusinessRuleViolationException(
                message=f"Validación de reglas de negocio falló para {entity.__class__.__name__}",
                rule_name="AGGREGATE_VALIDATION",
                violations=self._violations,
                entity_id=entity.id
            )
    
    @abstractmethod
    def _perform_validation(self, entity: AggregateRoot) -> None:
        """Método abstracto para implementar validación específica."""
        pass
    
    def has_violations(self) -> bool:
        """Verificar si hay violaciones de reglas."""
        return len(self._violations) > 0
    
    def get_violations(self) -> List[str]:
        """Obtener lista de violaciones de reglas."""
        return self._violations.copy()


class DomainEventService(DomainService):
    """
    Servicio para manejo y coordinación de eventos de dominio.
    Facilita la creación de eventos correlacionados y cadenas de eventos.
    """
    def create_correlated_event(
        self,
        source_event: DomainEvent,
        target_aggregate: AggregateRoot,
        event_type: type,
        **event_data
    ) -> DomainEvent:
        """Crear un evento correlacionado basado en un evento fuente."""
        new_event = event_type(
            aggregate_id=target_aggregate.id,
            metadata=source_event.metadata.with_correlation(source_event.metadata.correlation_id),
            **event_data
        )
        
        return new_event.with_causation(source_event)
    
    def create_event_chain(
        self,
        initial_event: DomainEvent,
        aggregates: List[AggregateRoot],
        event_factory_func
    ) -> List[DomainEvent]:
        """Crear una cadena de eventos correlacionados para múltiples agregados."""
        events = []
        previous_event = initial_event
        
        for aggregate in aggregates:
            new_event = event_factory_func(aggregate, previous_event)
            events.append(new_event)
            previous_event = new_event
        
        return events


class AggregateCoordinationService(DomainService, Generic[T]):
    """
    Servicio para coordinar operaciones entre múltiples agregados.
    Maneja transacciones distribuidas y eventos resultantes.
    """
    def coordinate_operation(
        self,
        primary_aggregate: T,
        related_aggregates: List[AggregateRoot],
        operation_func
    ) -> List[DomainEvent]:
        """Coordinar una operación entre agregados y recopilar eventos resultantes."""
        all_events = []
        
        try:
            operation_func(primary_aggregate, related_aggregates)
            
            all_events.extend(primary_aggregate.obtener_eventos())
            
            for aggregate in related_aggregates:
                all_events.extend(aggregate.obtener_eventos())
            
            return all_events
            
        except Exception as e:
            self._handle_coordination_failure(primary_aggregate, related_aggregates, e)
            raise
    
    def _handle_coordination_failure(
        self,
        primary_aggregate: T,
        related_aggregates: List[AggregateRoot],
        error: Exception
    ) -> None:
        """Manejar fallas en coordinación limpiando eventos y registrando contexto."""
        primary_aggregate.limpiar_eventos()
        for aggregate in related_aggregates:
            aggregate.limpiar_eventos()
        
        self.set_context("coordination_error", str(error))
        self.set_context("affected_aggregates", [
            primary_aggregate.id
        ] + [agg.id for agg in related_aggregates])


class CalculationService(DomainService):
    """
    Servicio para cálculos de dominio con trazabilidad.
    Registra pasos de cálculo para auditoría y depuración.
    """
    def __init__(self):
        super().__init__()
        self._calculation_steps: List[str] = []
    
    def record_calculation_step(self, step_description: str, value: Any) -> None:
        """Registrar un paso de cálculo para trazabilidad."""
        self._calculation_steps.append(f"{step_description}: {value}")
    
    def get_calculation_audit_trail(self) -> List[str]:
        """Obtener pista de auditoría de cálculos."""
        return self._calculation_steps.copy()
    
    def clear_audit_trail(self) -> None:
        """Limpiar pista de auditoría de cálculos."""
        self._calculation_steps.clear()


class ExternalIntegrationService(DomainService):
    """
    Servicio base para integraciones con sistemas externos.
    Proporciona manejo de fallas y lógica de respaldo.
    """
    @abstractmethod
    def is_available(self) -> bool:
        """Verificar si el servicio externo está disponible."""
        pass
    
    @abstractmethod
    def validate_external_data(self, data: Dict[str, Any]) -> bool:
        """Validar datos provenientes del sistema externo."""
        pass
    
    def handle_integration_failure(self, operation: str, error: Exception) -> None:
        """Manejar fallas de integración registrando contexto y ejecutando lógica de respaldo."""
        self.set_context("integration_failure", {
            "operation": operation,
            "error": str(error),
            "timestamp": __import__('datetime').datetime.utcnow().isoformat()
        })
        
        self._execute_fallback_logic(operation)
    
    @abstractmethod
    def _execute_fallback_logic(self, operation: str) -> None:
        """Ejecutar lógica de respaldo cuando falla la integración."""
        pass


class PolicyEnforcementService(DomainService):
    """
    Servicio para aplicación de políticas de dominio.
    Registra y aplica políticas configurables sobre entidades.
    """
    def __init__(self):
        super().__init__()
        self._active_policies: Dict[str, Any] = {}
    
    def register_policy(self, policy_name: str, policy_func) -> None:
        """Registrar una política con su función de evaluación."""
        self._active_policies[policy_name] = policy_func
    
    def enforce_policy(
        self, 
        policy_name: str, 
        entity: AggregateRoot,
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Aplicar una política específica a una entidad con contexto opcional."""
        if policy_name not in self._active_policies:
            raise DomainException(
                message=f"Política desconocida: {policy_name}",
                error_code="UNKNOWN_POLICY"
            )
        
        policy_func = self._active_policies[policy_name]
        evaluation_context = context or {}
        evaluation_context.update(self._context)
        
        return policy_func(entity, evaluation_context)
    
    def enforce_all_policies(
        self, 
        entity: AggregateRoot,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, bool]:
        """Aplicar todas las políticas activas a una entidad."""
        results = {}
        for policy_name in self._active_policies.keys():
            results[policy_name] = self.enforce_policy(policy_name, entity, context)
        
        return results
    
    def get_active_policies(self) -> List[str]:
        """Obtener lista de políticas activas registradas."""
        return list(self._active_policies.keys())
