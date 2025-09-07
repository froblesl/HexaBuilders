from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TypeVar, Generic, Type, Callable
from dataclasses import dataclass, field
from contextlib import contextmanager

from .comandos import Command, CommandResult
from .queries import Query, QueryResult
from ..dominio.entidades import AggregateRoot
from ..dominio.eventos import DomainEvent, IntegrationEvent
from ..dominio.excepciones import DomainException, ValidationException


T = TypeVar('T', bound=AggregateRoot)


@dataclass
class ServiceContext:
    """Contexto para ejecución de servicio de aplicación."""
    
    service_name: str
    user_id: Optional[str] = None
    tenant_id: Optional[str] = None
    correlation_id: Optional[str] = None
    trace_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_metadata(self, key: str, value: Any) -> None:
        """Agregar metadatos al contexto."""
        self.metadata[key] = value


class ApplicationService(ABC):
    """
    Clase base para servicios de aplicación que orquestan casos de uso.
    
    Los Servicios de Aplicación:
    - Orquestan operaciones de dominio
    - Gestionan límites de transacción
    - Coordinan publicación de eventos
    - Manejan preocupaciones transversales
    - Implementan flujos de trabajo de casos de uso
    """
    
    def __init__(self, name: Optional[str] = None):
        self._name = name or self.__class__.__name__
        self._unit_of_work: Optional['UnitOfWork'] = None
        self._event_bus: Optional['EventBus'] = None
        self._integration_event_publisher: Optional['IntegrationEventPublisher'] = None
        self._domain_event_handlers: Dict[Type[DomainEvent], List[Callable]] = {}
        self._logger = self._get_logger()
    
    @property
    def name(self) -> str:
        """Obtener nombre del servicio."""
        return self._name
    
    def set_unit_of_work(self, uow: 'UnitOfWork') -> 'ApplicationService':
        """Establecer Unit of Work para gestión de transacciones."""
        self._unit_of_work = uow
        return self
    
    def set_event_bus(self, event_bus: 'EventBus') -> 'ApplicationService':
        """Establecer bus de eventos para eventos de dominio."""
        self._event_bus = event_bus
        return self
    
    def set_integration_event_publisher(self, publisher: 'IntegrationEventPublisher') -> 'ApplicationService':
        """Establecer publicador para eventos de integración."""
        self._integration_event_publisher = publisher
        return self
    
    def register_domain_event_handler(
        self, 
        event_type: Type[DomainEvent], 
        handler: Callable[[DomainEvent], None]
    ) -> 'ApplicationService':
        """Registrar handler para tipo de evento de dominio específico."""
        if event_type not in self._domain_event_handlers:
            self._domain_event_handlers[event_type] = []
        self._domain_event_handlers[event_type].append(handler)
        return self
    
    def create_context(
        self, 
        user_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        correlation_id: Optional[str] = None
    ) -> ServiceContext:
        """Crear contexto de ejecución del servicio."""
        return ServiceContext(
            service_name=self._name,
            user_id=user_id,
            tenant_id=tenant_id,
            correlation_id=correlation_id
        )
    
    @contextmanager
    def transaction_scope(self, context: ServiceContext):
        """
        Crear ámbito de transacción para operaciones del servicio.
        Asegura que los eventos de dominio sean publicados después del commit exitoso.
        """
        collected_events = []
        
        try:
            # Iniciar transacción
            if self._unit_of_work:
                self._unit_of_work.begin()
            
            yield collected_events
            
            # Recopilar eventos de dominio antes del commit
            if self._unit_of_work:
                aggregates = self._unit_of_work.get_aggregates_with_events()
                for aggregate in aggregates:
                    events = aggregate.obtener_eventos()
                    collected_events.extend(events)
                    # No limpiar eventos aún - esperar commit exitoso
                
                # Confirmar transacción
                self._unit_of_work.commit()
            
            # Publicar eventos después del commit exitoso
            self._publish_domain_events(collected_events, context)
            
            # Limpiar eventos de agregados después de publicación exitosa
            if self._unit_of_work:
                for aggregate in self._unit_of_work.get_aggregates_with_events():
                    aggregate.limpiar_eventos()
            
        except Exception as e:
            # Revertir transacción en caso de error
            if self._unit_of_work:
                self._unit_of_work.rollback()
            
            self._logger.error(f"Transacción falló en {self._name}: {str(e)}")
            raise
    
    def _publish_domain_events(self, events: List[DomainEvent], context: ServiceContext) -> None:
        """Publicar eventos de dominio al bus de eventos y handlers locales."""
        for event in events:
            try:
                # Publicar al bus de eventos
                if self._event_bus:
                    self._event_bus.publish(event)
                
                # Manejar handlers registrados localmente
                event_type = type(event)
                if event_type in self._domain_event_handlers:
                    for handler in self._domain_event_handlers[event_type]:
                        handler(event)
                
                self._logger.debug(f"Evento de dominio publicado: {event.__class__.__name__}")
                
            except Exception as e:
                self._logger.error(f"Falló al publicar evento de dominio {event.__class__.__name__}: {str(e)}")
                # Continuar con otros eventos aunque uno falle
    
    def publish_integration_event(self, event: IntegrationEvent, context: ServiceContext) -> None:
        """Publicar evento de integración a sistemas externos."""
        if self._integration_event_publisher:
            try:
                self._integration_event_publisher.publish(event)
                self._logger.info(f"Evento de integración publicado: {event.__class__.__name__}")
            except Exception as e:
                self._logger.error(f"Falló al publicar evento de integración {event.__class__.__name__}: {str(e)}")
                # El fallo de eventos de integración podría necesitar acciones compensatorias
                self._handle_integration_event_failure(event, context, e)
    
    def _handle_integration_event_failure(
        self, 
        event: IntegrationEvent, 
        context: ServiceContext,
        error: Exception
    ) -> None:
        """
        Manejar fallo de publicación de evento de integración.
        Sobrescribir en servicios concretos para manejo específico de errores.
        """
        context.add_metadata('integration_event_failure', {
            'event_type': event.__class__.__name__,
            'error': str(error)
        })
    
    def _get_logger(self):
        """Obtener instancia del logger."""
        import logging
        return logging.getLogger(f"{__name__}.{self.__class__.__name__}")


class CrudApplicationService(ApplicationService, Generic[T]):
    """
    Servicio de aplicación para operaciones CRUD básicas.
    
    Proporciona operaciones estándar Create, Read, Update, Delete
    con gestión de transacciones y manejo de eventos.
    """
    
    def __init__(self, name: Optional[str] = None):
        super().__init__(name)
        self._repository: Optional['Repository[T]'] = None
        self._factory: Optional['Factory[T]'] = None
    
    def set_repository(self, repository: 'Repository[T]') -> 'CrudApplicationService[T]':
        """Establecer repositorio para persistencia de entidades."""
        self._repository = repository
        return self
    
    def set_factory(self, factory: 'Factory[T]') -> 'CrudApplicationService[T]':
        """Establecer fábrica para creación de entidades."""
        self._factory = factory
        return self
    
    def create_entity(self, creation_data: Dict[str, Any], context: ServiceContext) -> T:
        """
        Crear nueva entidad con gestión de transacciones.
        
        Args:
            creation_data: Datos para creación de entidad
            context: Contexto de ejecución del servicio
            
        Returns:
            Entidad creada
            
        Raises:
            ValidationException: Si los datos de creación son inválidos
            DomainException: Si se violan reglas de negocio
        """
        if not self._repository:
            raise DomainException(
                message="Repositorio no configurado",
                error_code="REPOSITORY_NOT_CONFIGURED"
            )
        
        with self.transaction_scope(context) as events:
            # Crear entidad usando fábrica o instanciación directa
            if self._factory:
                entity = self._factory.create(**creation_data)
            else:
                # Esto necesitaría ser implementado basado en el tipo de entidad específico
                raise NotImplementedError("Fábrica no configurada y creación directa no implementada")
            
            # Persistir entidad
            self._repository.agregar(entity)
            
            self._logger.info(f"Entidad creada {entity.__class__.__name__} con ID: {entity.id}")
            
            return entity
    
    def get_entity_by_id(self, entity_id: str, context: ServiceContext) -> Optional[T]:
        """
        Obtener entidad por ID.
        
        Args:
            entity_id: Identificador de entidad
            context: Contexto de ejecución del servicio
            
        Returns:
            Entidad si se encuentra, None en caso contrario
        """
        if not self._repository:
            raise DomainException(
                message="Repositorio no configurado",
                error_code="REPOSITORY_NOT_CONFIGURED"
            )
        
        entity = self._repository.obtener_por_id(entity_id)
        
        if entity:
            self._logger.debug(f"Entidad obtenida {entity.__class__.__name__} con ID: {entity_id}")
        else:
            self._logger.debug(f"Entidad no encontrada con ID: {entity_id}")
        
        return entity
    
    def update_entity(self, entity: T, update_data: Dict[str, Any], context: ServiceContext) -> T:
        """
        Actualizar entidad existente con gestión de transacciones.
        
        Args:
            entity: Entidad a actualizar
            update_data: Datos para actualización de entidad
            context: Contexto de ejecución del servicio
            
        Returns:
            Entidad actualizada
        """
        if not self._repository:
            raise DomainException(
                message="Repositorio no configurado",
                error_code="REPOSITORY_NOT_CONFIGURED"
            )
        
        with self.transaction_scope(context) as events:
            # Aplicar actualizaciones a la entidad
            self._apply_updates(entity, update_data)
            
            # Validar entidad después de actualizaciones
            if hasattr(entity, 'validate'):
                entity.validate()
            
            # Persistir cambios
            self._repository.actualizar(entity)
            
            self._logger.info(f"Entidad actualizada {entity.__class__.__name__} con ID: {entity.id}")
            
            return entity
    
    def delete_entity(self, entity_id: str, context: ServiceContext, soft_delete: bool = True) -> bool:
        """
        Eliminar entidad con gestión de transacciones.
        
        Args:
            entity_id: Identificador de entidad
            context: Contexto de ejecución del servicio
            soft_delete: Si realizar eliminación lógica
            
        Returns:
            True si la entidad fue eliminada, False si no se encontró
        """
        if not self._repository:
            raise DomainException(
                message="Repositorio no configurado",
                error_code="REPOSITORY_NOT_CONFIGURED"
            )
        
        with self.transaction_scope(context) as events:
            entity = self._repository.obtener_por_id(entity_id)
            
            if not entity:
                return False
            
            if soft_delete and hasattr(entity, 'soft_delete'):
                entity.soft_delete(deleted_by=context.user_id)
                self._repository.actualizar(entity)
                self._logger.info(f"Entidad eliminada lógicamente {entity.__class__.__name__} con ID: {entity_id}")
            else:
                self._repository.eliminar(entity_id)
                self._logger.info(f"Entidad eliminada físicamente {entity.__class__.__name__} con ID: {entity_id}")
            
            return True
    
    def _apply_updates(self, entity: T, update_data: Dict[str, Any]) -> None:
        """
        Aplicar datos de actualización a la entidad.
        Sobrescribir en servicios concretos para lógica de actualización específica.
        """
        for field, value in update_data.items():
            if hasattr(entity, field):
                setattr(entity, field, value)
        
        # Marcar entidad como actualizada si tiene timestamp mixin
        if hasattr(entity, 'mark_updated'):
            entity.mark_updated()


class WorkflowApplicationService(ApplicationService):
    """
    Servicio de aplicación para flujos de trabajo de negocio complejos.
    
    Orquesta procesos de negocio multi-paso con:
    - Ejecución paso a paso
    - Lógica de compensación para fallos
    - Seguimiento de progreso
    - Persistencia de estado
    """
    
    def __init__(self, name: Optional[str] = None):
        super().__init__(name)
        self._workflow_steps: List['WorkflowStep'] = []
        self._compensation_steps: List['CompensationStep'] = []
    
    def add_step(self, step: 'WorkflowStep') -> 'WorkflowApplicationService':
        """Agregar paso de flujo de trabajo."""
        self._workflow_steps.append(step)
        return self
    
    def add_compensation_step(self, step: 'CompensationStep') -> 'WorkflowApplicationService':
        """Agregar paso de compensación para escenarios de fallo."""
        self._compensation_steps.append(step)
        return self
    
    def execute_workflow(self, workflow_data: Dict[str, Any], context: ServiceContext) -> 'WorkflowResult':
        """
        Ejecutar flujo de trabajo completo con compensación en caso de fallo.
        
        Args:
            workflow_data: Datos para ejecución de flujo de trabajo
            context: Contexto de ejecución del servicio
            
        Returns:
            Resultado de ejecución de flujo de trabajo
        """
        executed_steps = []
        workflow_context = WorkflowContext(workflow_data, context)
        
        try:
            with self.transaction_scope(context) as events:
                # Ejecutar todos los pasos
                for step in self._workflow_steps:
                    self._logger.info(f"Ejecutando paso de flujo de trabajo: {step.name}")
                    
                    step_result = step.execute(workflow_context)
                    executed_steps.append((step, step_result))
                    
                    if not step_result.success:
                        raise DomainException(
                            message=f"Paso de flujo de trabajo falló: {step.name} - {step_result.error}",
                            error_code="WORKFLOW_STEP_FAILED"
                        )
                    
                    # Actualizar contexto del flujo de trabajo con resultado del paso
                    workflow_context.add_step_result(step.name, step_result)
            
            self._logger.info(f"Flujo de trabajo {self._name} completado exitosamente")
            
            return WorkflowResult(
                success=True,
                executed_steps=[step.name for step, _ in executed_steps],
                result_data=workflow_context.data
            )
            
        except Exception as e:
            self._logger.error(f"Flujo de trabajo {self._name} falló: {str(e)}")
            
            # Ejecutar pasos de compensación para pasos ejecutados (en orden inverso)
            self._execute_compensation(executed_steps, workflow_context)
            
            return WorkflowResult(
                success=False,
                executed_steps=[step.name for step, _ in executed_steps],
                error=str(e),
                error_code=getattr(e, 'error_code', 'WORKFLOW_EXECUTION_FAILED')
            )
    
    def _execute_compensation(self, executed_steps: List[tuple], workflow_context: 'WorkflowContext') -> None:
        """Ejecutar pasos de compensación para flujo de trabajo fallido."""
        for step, step_result in reversed(executed_steps):
            try:
                if hasattr(step, 'compensate'):
                    self._logger.info(f"Compensando paso de flujo de trabajo: {step.name}")
                    step.compensate(workflow_context, step_result)
            except Exception as e:
                self._logger.error(f"Compensación falló para paso {step.name}: {str(e)}")
                # Continuar con otras compensaciones aunque una falle


@dataclass
class WorkflowContext:
    """Contexto para ejecución de flujo de trabajo."""
    
    data: Dict[str, Any]
    service_context: ServiceContext
    step_results: Dict[str, Any] = field(default_factory=dict)
    
    def add_step_result(self, step_name: str, result: Any) -> None:
        """Agregar resultado de ejecución de paso al contexto."""
        self.step_results[step_name] = result
    
    def get_step_result(self, step_name: str) -> Any:
        """Obtener resultado de paso anterior."""
        return self.step_results.get(step_name)


@dataclass
class WorkflowResult:
    """Resultado de ejecución de flujo de trabajo."""
    
    success: bool
    executed_steps: List[str]
    result_data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    error_code: Optional[str] = None


class WorkflowStep(ABC):
    """Paso abstracto de flujo de trabajo."""
    
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    def execute(self, context: WorkflowContext) -> 'StepResult':
        """Ejecutar paso de flujo de trabajo."""
        pass
    
    def compensate(self, context: WorkflowContext, step_result: 'StepResult') -> None:
        """Compensar por ejecución de paso (opcional)."""
        pass


@dataclass
class StepResult:
    """Resultado de ejecución de paso."""
    
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None


class CompensationStep(ABC):
    """Paso abstracto de compensación."""
    
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    def execute(self, context: WorkflowContext) -> None:
        """Ejecutar lógica de compensación."""
        pass


# Interfaces abstractas para dependencias
class UnitOfWork(ABC):
    """Interfaz abstracta de Unit of Work."""
    
    @abstractmethod
    def begin(self) -> None:
        """Iniciar transacción."""
        pass
    
    @abstractmethod
    def commit(self) -> None:
        """Confirmar transacción."""
        pass
    
    @abstractmethod
    def rollback(self) -> None:
        """Revertir transacción."""
        pass
    
    @abstractmethod
    def get_aggregates_with_events(self) -> List[AggregateRoot]:
        """Obtener agregados con eventos pendientes."""
        pass


class EventBus(ABC):
    """Interfaz abstracta de bus de eventos."""
    
    @abstractmethod
    def publish(self, event: DomainEvent) -> None:
        """Publicar evento de dominio."""
        pass


class IntegrationEventPublisher(ABC):
    """Interfaz abstracta de publicador de eventos de integración."""
    
    @abstractmethod
    def publish(self, event: IntegrationEvent) -> None:
        """Publicar evento de integración."""
        pass


class Repository(ABC, Generic[T]):
    """Interfaz abstracta de repositorio."""
    
    @abstractmethod
    def agregar(self, entity: T) -> None:
        """Agregar entidad."""
        pass
    
    @abstractmethod
    def obtener_por_id(self, entity_id: str) -> Optional[T]:
        """Obtener entidad por ID."""
        pass
    
    @abstractmethod
    def actualizar(self, entity: T) -> None:
        """Actualizar entidad."""
        pass
    
    @abstractmethod
    def eliminar(self, entity_id: str) -> bool:
        """Eliminar entidad."""
        pass


class Factory(ABC, Generic[T]):
    """Interfaz abstracta de fábrica."""
    
    @abstractmethod
    def create(self, **kwargs) -> T:
        """Crear entidad."""
        pass
