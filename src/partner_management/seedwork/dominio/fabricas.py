from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TypeVar, Generic, Callable
from enum import Enum

from .entidades import AggregateRoot, Entity
from .eventos import DomainEvent, EventMetadata
from .excepciones import DomainException, ValidationException


T = TypeVar('T', bound=AggregateRoot)
E = TypeVar('E', bound=Entity)


class CreationStrategy(Enum):
    """Estrategias de creación disponibles para las fábricas."""
    DEFAULT = "default"
    BUILDER = "builder"
    TEMPLATE = "template"
    PROTOTYPE = "prototype"


class Factory(ABC, Generic[T]):
    """
    Clase base para fábricas de agregados.
    Proporciona validación, listeners de creación y estrategias configurables.
    """
    def __init__(self):
        self._validators: List[Callable[[T], None]] = []
        self._creation_listeners: List[Callable[[T], None]] = []
        self._strategy: CreationStrategy = CreationStrategy.DEFAULT
    
    def add_validator(self, validator: Callable[[T], None]) -> 'Factory[T]':
        """Añadir un validador que se ejecutará después de crear el agregado."""
        self._validators.append(validator)
        return self
    
    def add_creation_listener(self, listener: Callable[[T], None]) -> 'Factory[T]':
        """Añadir un listener que se ejecutará después de crear y validar el agregado."""
        self._creation_listeners.append(listener)
        return self
    
    def set_strategy(self, strategy: CreationStrategy) -> 'Factory[T]':
        """Establecer la estrategia de creación a utilizar."""
        self._strategy = strategy
        return self
    
    def create(self, **kwargs) -> T:
        """Crear un agregado aplicando validaciones, listeners y eventos de creación."""
        self._validate_creation_parameters(kwargs)
        
        aggregate = self._create_instance(**kwargs)
        
        self._validate_created_aggregate(aggregate)
        
        self._notify_creation_listeners(aggregate)
        
        creation_events = self._generate_creation_events(aggregate, kwargs)
        for event in creation_events:
            aggregate.agregar_evento(event)
        
        return aggregate
    
    @abstractmethod
    def _create_instance(self, **kwargs) -> T:
        """Método abstracto para crear la instancia del agregado."""
        pass
    
    def _validate_creation_parameters(self, parameters: Dict[str, Any]) -> None:
        """Validar que todos los parámetros requeridos estén presentes."""
        required_params = self._get_required_parameters()
        missing_params = [param for param in required_params if param not in parameters]
        
        if missing_params:
            raise ValidationException(
                message=f"Faltan parámetros requeridos: {', '.join(missing_params)}",
                field_errors={param: ["Parámetro requerido faltante"] for param in missing_params}
            )
    
    def _validate_created_aggregate(self, aggregate: T) -> None:
        """Validar el agregado creado usando validación interna y validadores externos."""
        if hasattr(aggregate, 'validate'):
            aggregate.validate()
        
        for validator in self._validators:
            validator(aggregate)
    
    def _notify_creation_listeners(self, aggregate: T) -> None:
        """Notificar a todos los listeners de creación."""
        for listener in self._creation_listeners:
            try:
                listener(aggregate)
            except Exception as e:
                # Registrar errores de listener pero no fallar la creación
                self._handle_listener_error(listener, aggregate, e)
    
    def _handle_listener_error(self, listener: Callable, aggregate: T, error: Exception) -> None:
        """Manejar errores en listeners de creación."""
        pass
    
    def _generate_creation_events(self, aggregate: T, parameters: Dict[str, Any]) -> List[DomainEvent]:
        """Generar eventos de creación para el agregado."""
        return []
    
    def _get_required_parameters(self) -> List[str]:
        """Obtener lista de parámetros requeridos para la creación."""
        return []


class Builder(ABC, Generic[T]):
    """
    Constructor fluido para agregados complejos.
    Proporciona validación por campo y construcción paso a paso.
    """
    def __init__(self):
        self._data: Dict[str, Any] = {}
        self._validation_rules: Dict[str, List[Callable]] = {}
        self._is_built = False
    
    def add_validation_rule(self, field: str, validator: Callable[[Any], bool]) -> 'Builder[T]':
        """Añadir regla de validación para un campo específico."""
        if field not in self._validation_rules:
            self._validation_rules[field] = []
        self._validation_rules[field].append(validator)
        return self
    
    def set_field(self, field: str, value: Any) -> 'Builder[T]':
        """Establecer valor de campo con validación."""
        if self._is_built:
            raise DomainException(
                message="No se puede modificar el builder después de llamar build()",
                error_code="BUILDER_ALREADY_BUILT"
            )
        
        self._validate_field(field, value)
        
        self._data[field] = value
        return self
    
    def get_field(self, field: str, default: Any = None) -> Any:
        """Obtener valor de un campo o valor por defecto."""
        return self._data.get(field, default)
    
    def has_field(self, field: str) -> bool:
        """Verificar si un campo tiene valor asignado."""
        return field in self._data
    
    def build(self) -> T:
        """Construir la instancia final validando campos requeridos."""
        if self._is_built:
            raise DomainException(
                message="El builder sólo puede usarse una vez",
                error_code="BUILDER_ALREADY_BUILT"
            )
        
        self._validate_required_fields()
        
        result = self._build_instance()
        
        self._is_built = True
        
        return result
    
    @abstractmethod
    def _build_instance(self) -> T:
        """Método abstracto para construir la instancia."""
        pass
    
    def _validate_field(self, field: str, value: Any) -> None:
        """Validar un campo usando sus reglas de validación."""
        if field in self._validation_rules:
            for validator in self._validation_rules[field]:
                if not validator(value):
                    raise ValidationException(
                        message=f"Validación falló para el campo: {field}",
                        field_errors={field: ["Validación de campo falló"]}
                    )
    
    def _validate_required_fields(self) -> None:
        """Validar que todos los campos requeridos estén presentes."""
        required_fields = self._get_required_fields()
        missing_fields = [field for field in required_fields if field not in self._data]
        
        if missing_fields:
            raise ValidationException(
                message="Faltan campos requeridos",
                field_errors={field: ["Campo requerido faltante"] for field in missing_fields}
            )
    
    def _get_required_fields(self) -> List[str]:
        """Obtener lista de campos requeridos."""
        return []


class TemplateFactory(Factory[T]):
    """
    Fábrica que utiliza plantillas predefinidas para creación.
    Permite reutilizar configuraciones comunes con personalizaciones.
    """
    def __init__(self):
        super().__init__()
        self._templates: Dict[str, Dict[str, Any]] = {}
    
    def register_template(self, name: str, template: Dict[str, Any]) -> 'TemplateFactory[T]':
        """Registrar una plantilla con nombre y parámetros."""
        self._templates[name] = template.copy()
        return self
    
    def create_from_template(self, template_name: str, **overrides) -> T:
        """Crear instancia desde plantilla con posibilidad de sobrescribir valores."""
        if template_name not in self._templates:
            raise DomainException(
                message=f"Plantilla no encontrada: {template_name}",
                error_code="TEMPLATE_NOT_FOUND"
            )
        
        # Fusionar plantilla con personalizaciones
        parameters = self._templates[template_name].copy()
        parameters.update(overrides)
        
        return self.create(**parameters)
    
    def get_template_names(self) -> List[str]:
        """Obtener nombres de todas las plantillas registradas."""
        return list(self._templates.keys())
    
    def has_template(self, name: str) -> bool:
        """Verificar si existe una plantilla con el nombre dado."""
        return name in self._templates


class PrototypeFactory(Factory[T]):
    """
    Fábrica que utiliza prototipos para clonación.
    Crea nuevas instancias clonando objetos existentes con modificaciones.
    """
    def __init__(self):
        super().__init__()
        self._prototypes: Dict[str, T] = {}
    
    def register_prototype(self, name: str, prototype: T) -> 'PrototypeFactory[T]':
        """Registrar un prototipo para clonación futura."""
        self._prototypes[name] = prototype
        return self
    
    def create_from_prototype(self, prototype_name: str, **modifications) -> T:
        """Crear instancia clonando prototipo con modificaciones opcionales."""
        if prototype_name not in self._prototypes:
            raise DomainException(
                message=f"Prototipo no encontrado: {prototype_name}",
                error_code="PROTOTYPE_NOT_FOUND"
            )
        
        prototype = self._prototypes[prototype_name]
        clone = self._clone_prototype(prototype)
        
        self._apply_modifications(clone, modifications)
        
        return clone
    
    @abstractmethod
    def _clone_prototype(self, prototype: T) -> T:
        """Método abstracto para clonar un prototipo."""
        pass
    
    def _apply_modifications(self, object_instance: T, modifications: Dict[str, Any]) -> None:
        """Aplicar modificaciones a la instancia clonada."""
        for field, value in modifications.items():
            if hasattr(object_instance, field):
                setattr(object_instance, field, value)


class CompositeFactory(Factory[T]):
    """
    Fábrica compuesta que selecciona la fábrica apropiada basada en condiciones.
    Permite delegar la creación a diferentes fábricas según los parámetros.
    """
    def __init__(self):
        super().__init__()
        self._factories: List[tuple[Callable[[Dict[str, Any]], bool], Factory[T]]] = []
        self._default_factory: Optional[Factory[T]] = None
    
    def add_factory(
        self, 
        condition: Callable[[Dict[str, Any]], bool], 
        factory: Factory[T]
    ) -> 'CompositeFactory[T]':
        """Añadir fábrica con condición para su selección."""
        self._factories.append((condition, factory))
        return self
    
    def set_default_factory(self, factory: Factory[T]) -> 'CompositeFactory[T]':
        """Establecer fábrica por defecto cuando ninguna condición se cumple."""
        self._default_factory = factory
        return self
    
    def _create_instance(self, **kwargs) -> T:
        """Crear instancia usando la primera fábrica cuya condición se cumple."""
        for condition, factory in self._factories:
            if condition(kwargs):
                return factory._create_instance(**kwargs)
        
        if self._default_factory:
            return self._default_factory._create_instance(**kwargs)
        
        raise DomainException(
            message="No se encontró fábrica adecuada para los parámetros de creación",
            error_code="NO_FACTORY_MATCH"
        )
