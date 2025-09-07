import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TypeVar, Generic, Callable
from contextlib import contextmanager
from dataclasses import dataclass, field

from .comandos import Command, CommandResult, CommandHandler
from .queries import Query, QueryResult, QueryHandler
from ..dominio.entidades import AggregateRoot
from ..dominio.eventos import DomainEvent
from ..dominio.excepciones import DomainException


T = TypeVar('T')


@dataclass
class HandlerContext:
    """Contexto para ejecución de handler."""
    
    handler_name: str
    correlation_id: str
    user_id: Optional[str] = None
    tenant_id: Optional[str] = None
    start_time: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def elapsed_time_ms(self) -> float:
        """Obtener tiempo transcurrido en milisegundos."""
        return (time.time() - self.start_time) * 1000
    
    def add_metadata(self, key: str, value: Any) -> None:
        """Agregar metadatos al contexto."""
        self.metadata[key] = value


class Handler(ABC):
    """
    Clase base de handler con funcionalidad común.
    
    Proporciona:
    - Manejo de errores y logging
    - Monitoreo de rendimiento
    - Lógica de reintento para fallas transitorias
    - Gestión de preocupaciones transversales
    """
    
    def __init__(self, name: Optional[str] = None):
        self._name = name or self.__class__.__name__
        self._logger = self._get_logger()
        self._metrics: Dict[str, Any] = {
            'total_executions': 0,
            'successful_executions': 0,
            'failed_executions': 0,
            'total_execution_time': 0.0,
            'average_execution_time': 0.0,
            'last_execution_time': None
        }
        self._retry_config = RetryConfig()
        self._middleware: List['HandlerMiddleware'] = []
    
    @property
    def name(self) -> str:
        """Obtener nombre del handler."""
        return self._name
    
    @property
    def metrics(self) -> Dict[str, Any]:
        """Obtener métricas del handler."""
        return self._metrics.copy()
    
    def add_middleware(self, middleware: 'HandlerMiddleware') -> 'Handler':
        """Agregar middleware al handler."""
        self._middleware.append(middleware)
        return self
    
    def set_retry_config(self, config: 'RetryConfig') -> 'Handler':
        """Establecer configuración de reintento."""
        self._retry_config = config
        return self
    
    def _create_context(self, request: Any) -> HandlerContext:
        """Crear contexto de ejecución."""
        correlation_id = getattr(request, 'correlation_id', 'unknown')
        user_id = getattr(request, 'user_id', None)
        tenant_id = getattr(request, 'tenant_id', None)
        
        return HandlerContext(
            handler_name=self._name,
            correlation_id=correlation_id,
            user_id=user_id,
            tenant_id=tenant_id
        )
    
    def _execute_with_monitoring(self, context: HandlerContext, execution_func: Callable) -> Any:
        """Ejecutar función con monitoreo y métricas."""
        self._logger.info(f"Iniciando ejecución de {self._name} para correlation_id: {context.correlation_id}")
        
        try:
            # Ejecutar con middleware
            if self._middleware:
                result = self._execute_with_middleware(context, execution_func)
            else:
                result = execution_func()
            
            # Actualizar métricas de éxito
            execution_time = context.elapsed_time_ms()
            self._update_metrics(success=True, execution_time=execution_time)
            
            self._logger.info(
                f"Completado {self._name} exitosamente en {execution_time:.2f}ms "
                f"para correlation_id: {context.correlation_id}"
            )
            
            return result
            
        except Exception as e:
            # Actualizar métricas de fallo
            execution_time = context.elapsed_time_ms()
            self._update_metrics(success=False, execution_time=execution_time)
            
            self._logger.error(
                f"Falló {self._name} en {execution_time:.2f}ms "
                f"para correlation_id: {context.correlation_id} - Error: {str(e)}"
            )
            
            raise
    
    def _execute_with_middleware(self, context: HandlerContext, execution_func: Callable) -> Any:
        """Ejecutar con cadena de middleware."""
        def execute():
            return execution_func()
        
        # Aplicar middleware en orden inverso
        for middleware in reversed(self._middleware):
            next_func = execute
            execute = lambda mw=middleware, nf=next_func: mw.handle(context, nf)
        
        return execute()
    
    def _execute_with_retry(self, execution_func: Callable) -> Any:
        """Ejecutar función con lógica de reintento."""
        last_exception = None
        
        for attempt in range(self._retry_config.max_attempts):
            try:
                return execution_func()
            except Exception as e:
                last_exception = e
                
                if not self._should_retry(e, attempt):
                    raise e
                
                if attempt < self._retry_config.max_attempts - 1:
                    wait_time = self._calculate_wait_time(attempt)
                    self._logger.warning(
                        f"Intento {attempt + 1} falló, reintentando en {wait_time}s: {str(e)}"
                    )
                    time.sleep(wait_time)
        
        raise last_exception
    
    def _should_retry(self, exception: Exception, attempt: int) -> bool:
        """Verificar si la excepción debe activar un reintento."""
        if attempt >= self._retry_config.max_attempts - 1:
            return False
        
        # No reintentar en excepciones de dominio (errores de lógica de negocio)
        if isinstance(exception, DomainException):
            return False
        
        return True
    
    def _calculate_wait_time(self, attempt: int) -> float:
        """Calcular tiempo de espera para reintento con backoff exponencial."""
        base_wait = self._retry_config.base_wait_seconds
        max_wait = self._retry_config.max_wait_seconds
        
        if self._retry_config.exponential_backoff:
            wait_time = base_wait * (2 ** attempt)
            return min(wait_time, max_wait)
        
        return base_wait
    
    def _update_metrics(self, success: bool, execution_time: float) -> None:
        """Actualizar métricas del handler."""
        self._metrics['total_executions'] += 1
        self._metrics['total_execution_time'] += execution_time
        self._metrics['last_execution_time'] = execution_time
        
        if success:
            self._metrics['successful_executions'] += 1
        else:
            self._metrics['failed_executions'] += 1
        
        # Calcular promedio
        total_executions = self._metrics['total_executions']
        self._metrics['average_execution_time'] = (
            self._metrics['total_execution_time'] / total_executions
        )
    
    def _get_logger(self):
        """Obtener instancia del logger."""
        import logging
        return logging.getLogger(f"{__name__}.{self.__class__.__name__}")


@dataclass
class RetryConfig:
    """Configuración para comportamiento de reintento."""
    
    max_attempts: int = 3
    base_wait_seconds: float = 0.1
    max_wait_seconds: float = 60.0
    exponential_backoff: bool = True


class BaseCommandHandler(Handler, CommandHandler[T], Generic[T]):
    """
    Handler base de comando con gestión de límites de transacción.
    
    Proporciona:
    - Gestión de transacciones
    - Publicación de eventos de dominio
    - Integración con Unit of Work
    - Manejo de errores y compensación
    """
    
    def __init__(self, name: Optional[str] = None):
        super().__init__(name)
        self._unit_of_work: Optional['UnitOfWork'] = None
        self._event_publisher: Optional['EventPublisher'] = None
    
    def set_unit_of_work(self, uow: 'UnitOfWork') -> 'BaseCommandHandler[T]':
        """Establecer Unit of Work para gestión de transacciones."""
        self._unit_of_work = uow
        return self
    
    def set_event_publisher(self, publisher: 'EventPublisher') -> 'BaseCommandHandler[T]':
        """Establecer publicador de eventos para eventos de dominio."""
        self._event_publisher = publisher
        return self
    
    def handle(self, command: Command) -> CommandResult[T]:
        """Manejar comando con límite de transacción."""
        context = self._create_context(command)
        
        def execute():
            return self._execute_with_retry(lambda: self._handle_command_with_transaction(command, context))
        
        return self._execute_with_monitoring(context, execute)
    
    def _handle_command_with_transaction(self, command: Command, context: HandlerContext) -> CommandResult[T]:
        """Manejar comando dentro del límite de transacción."""
        if not self._unit_of_work:
            # Ejecutar sin transacción explícita
            return self._execute_command(command, context)
        
        with self._transaction_scope():
            try:
                result = self._execute_command(command, context)
                
                # Publicar eventos de dominio si es exitoso
                if result.success and self._event_publisher:
                    events_published = self._publish_domain_events()
                    result.events_generated = events_published
                
                return result
                
            except Exception as e:
                # La transacción será revertida automáticamente
                return CommandResult.failure_result(
                    command=command,
                    error=str(e),
                    error_code=getattr(e, 'error_code', 'COMMAND_EXECUTION_ERROR')
                )
    
    @contextmanager
    def _transaction_scope(self):
        """Crear ámbito de transacción usando Unit of Work."""
        try:
            yield
            if self._unit_of_work:
                self._unit_of_work.commit()
        except Exception:
            if self._unit_of_work:
                self._unit_of_work.rollback()
            raise
    
    @abstractmethod
    def _execute_command(self, command: Command, context: HandlerContext) -> CommandResult[T]:
        """
        Ejecutar la lógica real del comando.
        Debe ser implementado por handlers concretos.
        """
        pass
    
    def _publish_domain_events(self) -> int:
        """Publicar eventos de dominio desde agregados."""
        if not self._unit_of_work or not self._event_publisher:
            return 0
        
        events_count = 0
        
        # Obtener todos los agregados con eventos
        for aggregate in self._unit_of_work.get_aggregates_with_events():
            events = aggregate.obtener_eventos()
            for event in events:
                self._event_publisher.publish(event)
                events_count += 1
            
            # Limpiar eventos después de publicar
            aggregate.limpiar_eventos()
        
        return events_count


class BaseQueryHandler(Handler, QueryHandler[T], Generic[T]):
    """
    Handler base de consulta para operaciones de lectura.
    
    Proporciona:
    - Acceso a modelos de lectura
    - Integración de caché
    - Optimización de rendimiento
    - Manejo de errores
    """
    
    def __init__(self, name: Optional[str] = None):
        super().__init__(name)
        self._read_model_factory: Optional['ReadModelFactory'] = None
        self._cache_provider: Optional['CacheProvider'] = None
    
    def set_read_model_factory(self, factory: 'ReadModelFactory') -> 'BaseQueryHandler[T]':
        """Establecer fábrica de modelos de lectura."""
        self._read_model_factory = factory
        return self
    
    def set_cache_provider(self, provider: 'CacheProvider') -> 'BaseQueryHandler[T]':
        """Establecer proveedor de caché."""
        self._cache_provider = provider
        return self
    
    def handle(self, query: Query) -> QueryResult[T]:
        """Manejar consulta con caché y optimización."""
        context = self._create_context(query)
        
        def execute():
            return self._handle_query_with_cache(query, context)
        
        return self._execute_with_monitoring(context, execute)
    
    def _handle_query_with_cache(self, query: Query, context: HandlerContext) -> QueryResult[T]:
        """Manejar consulta con soporte de caché."""
        # Intentar caché primero si está habilitado
        if query.context.cache_enabled and self._cache_provider:
            cache_key = self.get_cache_key(query)
            if cache_key:
                cached_result = self._cache_provider.get(cache_key)
                if cached_result:
                    context.add_metadata('cache_hit', True)
                    return QueryResult.success_result(
                        query=query,
                        data=cached_result,
                        cached=True,
                        cache_key=cache_key
                    )
        
        # Ejecutar consulta
        try:
            result = self._execute_query(query, context)
            
            # Cachear resultado si es exitoso
            if (result.success and query.context.cache_enabled and 
                self._cache_provider and result.data):
                cache_key = self.get_cache_key(query)
                if cache_key:
                    ttl = query.context.cache_ttl_seconds
                    self._cache_provider.set(cache_key, result.data, ttl)
                    result.cache_key = cache_key
            
            return result
            
        except Exception as e:
            return QueryResult.failure_result(
                query=query,
                error=str(e),
                error_code=getattr(e, 'error_code', 'QUERY_EXECUTION_ERROR')
            )
    
    @abstractmethod
    def _execute_query(self, query: Query, context: HandlerContext) -> QueryResult[T]:
        """
        Ejecutar la lógica real de la consulta.
        Debe ser implementado por handlers concretos.
        """
        pass
    
    def get_cache_key(self, query: Query) -> Optional[str]:
        """Generar clave de caché para consulta."""
        if not query.context.cache_enabled:
            return None
        
        # Implementación por defecto
        query_type = type(query).__name__
        tenant_id = query.context.tenant_id or "default"
        
        key_parts = [self._name, query_type, tenant_id]
        
        # Agregar filtros a la clave de caché
        if query.filters:
            filter_str = "_".join(f"{k}={v}" for k, v in sorted(query.filters.items()))
            key_parts.append(filter_str)
        
        # Agregar paginación
        if query.pagination:
            key_parts.extend([
                f"page_{query.pagination.page_number}",
                f"size_{query.pagination.page_size}"
            ])
        
        # Agregar ordenamiento
        if query.sorting:
            sort_str = "_".join(f"{s.field}_{s.direction}" for s in query.sorting)
            key_parts.append(sort_str)
        
        return "_".join(key_parts)


class HandlerMiddleware(ABC):
    """
    Clase base para middleware de handler.
    
    Proporciona puntos de extensión para preocupaciones transversales.
    """
    
    @abstractmethod
    def handle(self, context: HandlerContext, next_handler: Callable) -> Any:
        """
        Procesar petición con lógica de middleware.
        
        Args:
            context: Contexto de ejecución del handler
            next_handler: Siguiente handler en la cadena
            
        Returns:
            Resultado de ejecución del handler
        """
        pass


class ValidationMiddleware(HandlerMiddleware):
    """Middleware para validación de peticiones."""
    
    def handle(self, context: HandlerContext, next_handler: Callable) -> Any:
        context.add_metadata('validation_enabled', True)
        
        # La validación sería manejada por los objetos de petición mismos
        # Este middleware puede agregar lógica de validación adicional si es necesario
        
        return next_handler()


class SecurityMiddleware(HandlerMiddleware):
    """Middleware para verificaciones de seguridad."""
    
    def __init__(self, required_roles: Optional[List[str]] = None):
        self._required_roles = required_roles or []
    
    def handle(self, context: HandlerContext, next_handler: Callable) -> Any:
        # Marcador de posición para verificaciones de seguridad
        if context.user_id is None and self._required_roles:
            raise DomainException(
                message="Autenticación requerida",
                error_code="AUTHENTICATION_REQUIRED"
            )
        
        context.add_metadata('security_checked', True)
        return next_handler()


class LoggingMiddleware(HandlerMiddleware):
    """Middleware para logging detallado."""
    
    def __init__(self):
        self._logger = self._get_logger()
    
    def handle(self, context: HandlerContext, next_handler: Callable) -> Any:
        self._logger.debug(
            f"Handler {context.handler_name} iniciando para usuario {context.user_id}"
        )
        
        try:
            result = next_handler()
            
            self._logger.debug(
                f"Handler {context.handler_name} completado exitosamente en "
                f"{context.elapsed_time_ms():.2f}ms"
            )
            
            return result
            
        except Exception as e:
            self._logger.warning(
                f"Handler {context.handler_name} falló en "
                f"{context.elapsed_time_ms():.2f}ms con error: {str(e)}"
            )
            raise
    
    def _get_logger(self):
        import logging
        return logging.getLogger(f"{__name__}.LoggingMiddleware")


class PerformanceMiddleware(HandlerMiddleware):
    """Middleware para monitoreo de rendimiento."""
    
    def __init__(self, slow_execution_threshold_ms: float = 1000.0):
        self._slow_threshold = slow_execution_threshold_ms
        self._logger = self._get_logger()
    
    def handle(self, context: HandlerContext, next_handler: Callable) -> Any:
        result = next_handler()
        
        execution_time = context.elapsed_time_ms()
        context.add_metadata('execution_time_ms', execution_time)
        
        if execution_time > self._slow_threshold:
            self._logger.warning(
                f"Ejecución lenta de handler detectada: {context.handler_name} "
                f"tomó {execution_time:.2f}ms (umbral: {self._slow_threshold}ms)"
            )
        
        return result
    
    def _get_logger(self):
        import logging
        return logging.getLogger(f"{__name__}.PerformanceMiddleware")


# Interfaces abstractas para dependencias
class UnitOfWork(ABC):
    """Interfaz abstracta de Unit of Work."""
    
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
        """Obtener agregados que tienen eventos pendientes."""
        pass


class EventPublisher(ABC):
    """Interfaz abstracta de publicador de eventos."""
    
    @abstractmethod
    def publish(self, event: DomainEvent) -> None:
        """Publicar evento de dominio."""
        pass


class ReadModelFactory(ABC):
    """Interfaz abstracta de fábrica de modelos de lectura."""
    
    @abstractmethod
    def create_read_model(self, model_type: str) -> Any:
        """Crear instancia de modelo de lectura."""
        pass


class CacheProvider(ABC):
    """Interfaz abstracta de proveedor de caché."""
    
    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Obtener valor del caché."""
        pass
    
    @abstractmethod
    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        """Establecer valor en el caché."""
        pass
