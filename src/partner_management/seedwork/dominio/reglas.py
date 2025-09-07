"""
Framework de reglas de negocio para encapsulación de lógica de dominio.
Implementa patrones de Business Rules y Specification.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Callable, Union
from enum import Enum
from dataclasses import dataclass

from .entidades import Entity, AggregateRoot
from .excepciones import BusinessRuleViolationException


class RulePriority(Enum):
    """Niveles de prioridad para la ejecución de reglas de negocio."""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4


class RuleResult(Enum):
    """Resultado de la evaluación de reglas de negocio."""
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


@dataclass
class RuleEvaluation:
    """Resultado de la evaluación de una regla individual."""
    rule_name: str
    result: RuleResult
    message: str
    priority: RulePriority
    context: Dict[str, Any]
    execution_time_ms: Optional[float] = None
    error: Optional[Exception] = None


class BusinessRule(ABC):
    """
    Clase base para encapsulación de reglas de negocio.
    
    Siguiendo el patrón Business Rules:
    - Encapsula una sola regla de negocio
    - Puede ser compuesta con otras reglas
    - Proporciona resultado claro de evaluación
    - Incluye contexto para depuración
    """
    
    def __init__(
        self, 
        name: str, 
        priority: RulePriority = RulePriority.MEDIUM,
        error_message: str = "Violación de regla de negocio"
    ):
        self._name = name
        self._priority = priority
        self._error_message = error_message
        self._is_enabled = True
        self._context: Dict[str, Any] = {}
    
    @property
    def name(self) -> str:
        """Obtener el nombre de la regla."""
        return self._name
    
    @property
    def priority(self) -> RulePriority:
        """Obtener la prioridad de la regla."""
        return self._priority
    
    @property
    def error_message(self) -> str:
        """Obtener el mensaje de error para violación de regla."""
        return self._error_message
    
    @property
    def is_enabled(self) -> bool:
        """Verificar si la regla está habilitada."""
        return self._is_enabled
    
    def enable(self) -> 'BusinessRule':
        """Habilitar la regla."""
        self._is_enabled = True
        return self
    
    def disable(self) -> 'BusinessRule':
        """Deshabilitar la regla."""
        self._is_enabled = False
        return self
    
    def set_context(self, context: Dict[str, Any]) -> 'BusinessRule':
        """Establecer el contexto de ejecución para la regla."""
        self._context = context.copy()
        return self
    
    @abstractmethod
    def evaluate(self, entity: Entity) -> bool:
        """
        Evaluar la regla de negocio contra una entidad.
        
        Args:
            entity: Entidad a evaluar
            
        Returns:
            True si la regla es satisfecha, False en caso contrario
        """
        pass
    
    def evaluate_with_result(self, entity: Entity) -> RuleEvaluation:
        """
        Evaluar regla y retornar resultado detallado.
        
        Args:
            entity: Entidad a evaluar
            
        Returns:
            Resultado detallado de la evaluación
        """
        if not self._is_enabled:
            return RuleEvaluation(
                rule_name=self._name,
                result=RuleResult.SKIPPED,
                message="La regla está deshabilitada",
                priority=self._priority,
                context=self._context
            )
        
        import time
        start_time = time.time()
        
        try:
            result = self.evaluate(entity)
            execution_time = (time.time() - start_time) * 1000
            
            return RuleEvaluation(
                rule_name=self._name,
                result=RuleResult.PASSED if result else RuleResult.FAILED,
                message="Regla aprobada" if result else self._error_message,
                priority=self._priority,
                context=self._context,
                execution_time_ms=execution_time
            )
        
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            
            return RuleEvaluation(
                rule_name=self._name,
                result=RuleResult.ERROR,
                message=f"Error en evaluación de regla: {str(e)}",
                priority=self._priority,
                context=self._context,
                execution_time_ms=execution_time,
                error=e
            )
    
    def and_rule(self, other: 'BusinessRule') -> 'CompositeAndRule':
        """Combinar con otra regla usando lógica AND."""
        return CompositeAndRule([self, other])
    
    def or_rule(self, other: 'BusinessRule') -> 'CompositeOrRule':
        """Combinar con otra regla usando lógica OR."""
        return CompositeOrRule([self, other])
    
    def not_rule(self) -> 'NotRule':
        """Crear negación de esta regla."""
        return NotRule(self)


class CompositeRule(BusinessRule, ABC):
    """Clase base para reglas que combinan múltiples reglas."""
    
    def __init__(
        self, 
        rules: List[BusinessRule], 
        name: str, 
        priority: RulePriority = RulePriority.MEDIUM
    ):
        super().__init__(name, priority)
        self._rules = rules
    
    @property
    def rules(self) -> List[BusinessRule]:
        """Obtener reglas constituyentes."""
        return self._rules.copy()
    
    def add_rule(self, rule: BusinessRule) -> 'CompositeRule':
        """Agregar regla a la composición."""
        self._rules.append(rule)
        return self
    
    def evaluate_all(self, entity: Entity) -> List[RuleEvaluation]:
        """Evaluar todas las reglas constituyentes y retornar resultados."""
        return [rule.evaluate_with_result(entity) for rule in self._rules]


class CompositeAndRule(CompositeRule):
    """Regla que requiere que TODAS las reglas constituyentes pasen."""
    
    def __init__(self, rules: List[BusinessRule]):
        super().__init__(rules, f"AND({', '.join(r.name for r in rules)})")
    
    def evaluate(self, entity: Entity) -> bool:
        """Todas las reglas deben pasar para que la regla AND pase."""
        return all(rule.evaluate(entity) for rule in self._rules if rule.is_enabled)


class CompositeOrRule(CompositeRule):
    """Regla que requiere que CUALQUIER regla constituyente pase."""
    
    def __init__(self, rules: List[BusinessRule]):
        super().__init__(rules, f"OR({', '.join(r.name for r in rules)})")
    
    def evaluate(self, entity: Entity) -> bool:
        """Cualquier regla que pase es suficiente para que la regla OR pase."""
        return any(rule.evaluate(entity) for rule in self._rules if rule.is_enabled)


class NotRule(BusinessRule):
    """Regla que niega otra regla."""
    
    def __init__(self, rule: BusinessRule):
        super().__init__(f"NOT({rule.name})", rule.priority)
        self._rule = rule
    
    def evaluate(self, entity: Entity) -> bool:
        """Niega el resultado de la regla envuelta."""
        return not self._rule.evaluate(entity)


class ConditionalRule(BusinessRule):
    """Regla que sólo se evalúa si se cumple una condición."""
    
    def __init__(
        self, 
        condition: Callable[[Entity], bool],
        rule: BusinessRule,
        name: Optional[str] = None
    ):
        rule_name = name or f"IF({rule.name})"
        super().__init__(rule_name, rule.priority, rule.error_message)
        self._condition = condition
        self._rule = rule
    
    def evaluate(self, entity: Entity) -> bool:
        """Sólo evaluar la regla envuelta si se cumple la condición."""
        if not self._condition(entity):
            return True  # La regla pasa si no se cumple la condición
        return self._rule.evaluate(entity)


class RuleEngine:
    """
    Motor para evaluar múltiples reglas de negocio.
    
    Características:
    - Registro y gestión de reglas
    - Evaluación en lote de reglas
    - Ejecución basada en prioridades
    - Monitoreo de rendimiento
    - Manejo y reporte de errores
    """
    
    def __init__(self):
        self._rules: Dict[str, BusinessRule] = {}
        self._rule_groups: Dict[str, List[str]] = {}
        self._global_context: Dict[str, Any] = {}
        self._performance_metrics: Dict[str, List[float]] = {}
    
    def register_rule(self, rule: BusinessRule, groups: Optional[List[str]] = None) -> 'RuleEngine':
        """
        Registrar una regla de negocio.
        
        Args:
            rule: Regla a registrar
            groups: Grupos opcionales a los que asignar la regla
            
        Returns:
            Motor de reglas para encadenamiento
        """
        self._rules[rule.name] = rule
        
        # Agregar a grupos
        if groups:
            for group in groups:
                if group not in self._rule_groups:
                    self._rule_groups[group] = []
                if rule.name not in self._rule_groups[group]:
                    self._rule_groups[group].append(rule.name)
        
        return self
    
    def unregister_rule(self, rule_name: str) -> 'RuleEngine':
        """Desregistrar una regla."""
        if rule_name in self._rules:
            del self._rules[rule_name]
            
            # Remover de grupos
            for group_rules in self._rule_groups.values():
                if rule_name in group_rules:
                    group_rules.remove(rule_name)
        
        return self
    
    def create_group(self, group_name: str, rule_names: List[str]) -> 'RuleEngine':
        """Crear un grupo de reglas."""
        self._rule_groups[group_name] = rule_names.copy()
        return self
    
    def set_global_context(self, context: Dict[str, Any]) -> 'RuleEngine':
        """Establecer contexto global para todas las reglas."""
        self._global_context = context.copy()
        return self
    
    def evaluate_all(self, entity: Entity) -> List[RuleEvaluation]:
        """
        Evaluar todas las reglas registradas contra una entidad.
        
        Args:
            entity: Entidad a evaluar
            
        Returns:
            Lista de resultados de evaluación de reglas
        """
        return self._evaluate_rules(list(self._rules.keys()), entity)
    
    def evaluate_group(self, group_name: str, entity: Entity) -> List[RuleEvaluation]:
        """
        Evaluar reglas en un grupo específico.
        
        Args:
            group_name: Nombre del grupo de reglas
            entity: Entidad a evaluar
            
        Returns:
            Lista de resultados de evaluación de reglas
        """
        if group_name not in self._rule_groups:
            return []
        
        return self._evaluate_rules(self._rule_groups[group_name], entity)
    
    def evaluate_by_priority(self, entity: Entity, max_priority: RulePriority = RulePriority.LOW) -> List[RuleEvaluation]:
        """
        Evaluar reglas hasta un cierto nivel de prioridad.
        
        Args:
            entity: Entidad a evaluar
            max_priority: Nivel de prioridad máximo a evaluar
            
        Returns:
            Lista de resultados de evaluación de reglas
        """
        rule_names = [
            name for name, rule in self._rules.items()
            if rule.priority.value <= max_priority.value
        ]
        
        return self._evaluate_rules(rule_names, entity)
    
    def validate_entity(self, entity: Entity, groups: Optional[List[str]] = None) -> None:
        """
        Validar entidad contra reglas y lanzar excepción si alguna falla.
        
        Args:
            entity: Entidad a validar
            groups: Grupos de reglas opcionales contra los cuales validar
            
        Raises:
            BusinessRuleViolationException: Si alguna regla falla
        """
        if groups:
            evaluations = []
            for group in groups:
                evaluations.extend(self.evaluate_group(group, entity))
        else:
            evaluations = self.evaluate_all(entity)
        
        # Verificar fallas
        failures = [eval_result for eval_result in evaluations if eval_result.result == RuleResult.FAILED]
        
        if failures:
            violation_messages = [f"{failure.rule_name}: {failure.message}" for failure in failures]
            
            raise BusinessRuleViolationException(
                message=f"Validación de entidad falló: {len(failures)} regla(s) violada(s)",
                rule_name="ENTITY_VALIDATION",
                violations=violation_messages,
                entity_id=entity.id if hasattr(entity, 'id') else None
            )
    
    def _evaluate_rules(self, rule_names: List[str], entity: Entity) -> List[RuleEvaluation]:
        """Evaluar reglas específicas contra una entidad."""
        evaluations = []
        
        # Ordenar reglas por prioridad
        sorted_rules = sorted(
            [(name, self._rules[name]) for name in rule_names if name in self._rules],
            key=lambda x: x[1].priority.value
        )
        
        for rule_name, rule in sorted_rules:
            # Establecer contexto global en regla
            rule.set_context(self._global_context)
            
            # Evaluar regla
            evaluation = rule.evaluate_with_result(entity)
            evaluations.append(evaluation)
            
            # Registrar métricas de rendimiento
            if evaluation.execution_time_ms is not None:
                if rule_name not in self._performance_metrics:
                    self._performance_metrics[rule_name] = []
                self._performance_metrics[rule_name].append(evaluation.execution_time_ms)
        
        return evaluations
    
    def get_performance_metrics(self) -> Dict[str, Dict[str, float]]:
        """Obtener métricas de rendimiento para todas las reglas."""
        metrics = {}
        
        for rule_name, times in self._performance_metrics.items():
            if times:
                metrics[rule_name] = {
                    'avg_time_ms': sum(times) / len(times),
                    'min_time_ms': min(times),
                    'max_time_ms': max(times),
                    'execution_count': len(times)
                }
        
        return metrics
    
    def clear_performance_metrics(self) -> None:
        """Limpiar todas las métricas de rendimiento."""
        self._performance_metrics.clear()
    
    def get_registered_rules(self) -> List[str]:
        """Obtener nombres de todas las reglas registradas."""
        return list(self._rules.keys())
    
    def get_rule_groups(self) -> Dict[str, List[str]]:
        """Obtener todos los grupos de reglas."""
        return self._rule_groups.copy()


# Implementaciones comunes de reglas de negocio
class RequiredFieldRule(BusinessRule):
    """Regla que valida que los campos requeridos no estén vacíos."""
    
    def __init__(self, field_name: str, error_message: Optional[str] = None):
        message = error_message or f"El campo '{field_name}' es requerido"
        super().__init__(f"REQUIRED_{field_name.upper()}", RulePriority.HIGH, message)
        self._field_name = field_name
    
    def evaluate(self, entity: Entity) -> bool:
        if not hasattr(entity, self._field_name):
            return False
        
        value = getattr(entity, self._field_name)
        return value is not None and value != ""


class RangeRule(BusinessRule):
    """Regla que valida que los valores numéricos estén dentro de un rango."""
    
    def __init__(self, field_name: str, min_value: float, max_value: float):
        super().__init__(
            f"RANGE_{field_name.upper()}",
            RulePriority.MEDIUM,
            f"El campo '{field_name}' debe estar entre {min_value} y {max_value}"
        )
        self._field_name = field_name
        self._min_value = min_value
        self._max_value = max_value
    
    def evaluate(self, entity: Entity) -> bool:
        if not hasattr(entity, self._field_name):
            return True  # La regla no aplica si el campo no existe
        
        value = getattr(entity, self._field_name)
        if value is None:
            return True  # La regla no aplica a valores None
        
        try:
            numeric_value = float(value)
            return self._min_value <= numeric_value <= self._max_value
        except (ValueError, TypeError):
            return False


class UniqueValueRule(BusinessRule):
    """Regla que valida que los valores de campo sean únicos dentro de una colección."""
    
    def __init__(self, field_name: str, existing_values: List[Any]):
        super().__init__(
            f"UNIQUE_{field_name.upper()}",
            RulePriority.HIGH,
            f"El campo '{field_name}' debe tener un valor único"
        )
        self._field_name = field_name
        self._existing_values = existing_values
    
    def evaluate(self, entity: Entity) -> bool:
        if not hasattr(entity, self._field_name):
            return True
        
        value = getattr(entity, self._field_name)
        return value not in self._existing_values
