"""
Infraestructura de consultas CQRS con patrón SingleDispatch.
Implementa manejo de consultas y optimización de modelos de lectura siguiendo patrones del tutorial.
"""

import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from functools import singledispatch
from typing import Any, Dict, Optional, TypeVar, Generic, List, Union
from enum import Enum

from ..dominio.excepciones import DomainException, ValidationException


class QueryPriority(Enum):
    """Niveles de prioridad para ejecución de consultas."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


@dataclass(frozen=True)
class QueryContext:
    """Información de contexto para ejecución de consultas."""
    
    query_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[str] = None
    tenant_id: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    source_system: Optional[str] = None
    trace_id: Optional[str] = None
    session_id: Optional[str] = None
    include_soft_deleted: bool = False
    cache_enabled: bool = True
    cache_ttl_seconds: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PaginationInfo:
    """Información de paginación para consultas."""
    
    page_number: int = 1
    page_size: int = 20
    max_page_size: int = 100
    
    def __post_init__(self):
        if self.page_number < 1:
            raise ValidationException(
                message="El número de página debe ser mayor que 0",
                field_errors={"page_number": ["Debe ser mayor que 0"]}
            )
        
        if self.page_size < 1:
            raise ValidationException(
                message="El tamaño de página debe ser mayor que 0",
                field_errors={"page_size": ["Debe ser mayor que 0"]}
            )
        
        if self.page_size > self.max_page_size:
            raise ValidationException(
                message=f"El tamaño de página no puede exceder {self.max_page_size}",
                field_errors={"page_size": [f"No puede exceder {self.max_page_size}"]}
            )
    
    @property
    def offset(self) -> int:
        """Calcular offset para consultas de base de datos."""
        return (self.page_number - 1) * self.page_size
    
    @property
    def limit(self) -> int:
        """Obtener límite para consultas de base de datos."""
        return self.page_size


@dataclass(frozen=True)
class SortInfo:
    """Información de ordenamiento para consultas."""
    
    field: str
    direction: str = "asc"
    
    def __post_init__(self):
        if self.direction.lower() not in ["asc", "desc"]:
            raise ValidationException(
                message="La dirección de ordenamiento debe ser 'asc' o 'desc'",
                field_errors={"direction": ["Debe ser 'asc' o 'desc'"]}
            )


@dataclass
class Query:
    """
    Clase base de consulta para operaciones de lectura.
    
    Siguiendo el patrón CQRS Query del tutorial:
    - Las consultas solicitan datos sin efectos secundarios
    - Objetos de consulta inmutables
    - Contexto rico para optimización
    - Soporte de estrategia de caché
    """
    
    context: QueryContext = field(default_factory=QueryContext)
    priority: QueryPriority = QueryPriority.NORMAL
    pagination: Optional[PaginationInfo] = None
    sorting: Optional[List[SortInfo]] = None
    filters: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validar consulta después de la inicialización."""
        self.validate()
    
    def validate(self) -> None:
        """
        Validar parámetros de consulta.
        Sobrescribir en consultas concretas para validación específica.
        """
        pass
    
    @property
    def query_id(self) -> str:
        """Obtener identificador único de consulta."""
        return self.context.query_id
    
    @property
    def correlation_id(self) -> str:
        """Obtener identificador de correlación para trazabilidad."""
        return self.context.correlation_id
    
    @property
    def user_id(self) -> Optional[str]:
        """Obtener usuario que inició la consulta."""
        return self.context.user_id
    
    @property
    def is_paginated(self) -> bool:
        """Verificar si la consulta usa paginación."""
        return self.pagination is not None
    
    @property
    def is_sorted(self) -> bool:
        """Verificar si la consulta tiene ordenamiento."""
        return self.sorting is not None and len(self.sorting) > 0
    
    def add_filter(self, field: str, value: Any) -> None:
        """Agregar filtro a la consulta."""
        self.filters[field] = value
    
    def remove_filter(self, field: str) -> None:
        """Remover filtro de la consulta."""
        self.filters.pop(field, None)
    
    def has_filter(self, field: str) -> bool:
        """Verificar si la consulta tiene filtro específico."""
        return field in self.filters
    
    def get_filter(self, field: str, default: Any = None) -> Any:
        """Obtener valor del filtro."""
        return self.filters.get(field, default)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir consulta a diccionario para serialización."""
        return {
            'query_type': self.__class__.__name__,
            'query_id': self.query_id,
            'correlation_id': self.correlation_id,
            'context': {
                'user_id': self.context.user_id,
                'tenant_id': self.context.tenant_id,
                'timestamp': self.context.timestamp,
                'source_system': self.context.source_system,
                'trace_id': self.context.trace_id,
                'session_id': self.context.session_id,
                'include_soft_deleted': self.context.include_soft_deleted,
                'cache_enabled': self.context.cache_enabled,
                'cache_ttl_seconds': self.context.cache_ttl_seconds,
                'metadata': self.context.metadata
            },
            'priority': self.priority.name,
            'pagination': {
                'page_number': self.pagination.page_number,
                'page_size': self.pagination.page_size,
                'offset': self.pagination.offset,
                'limit': self.pagination.limit
            } if self.pagination else None,
            'sorting': [
                {'field': sort.field, 'direction': sort.direction}
                for sort in self.sorting
            ] if self.sorting else None,
            'filters': self.filters,
            'data': self._get_query_data()
        }
    
    def _get_query_data(self) -> Dict[str, Any]:
        """
        Obtener datos específicos de consulta para serialización.
        Sobrescribir en consultas concretas.
        """
        # Obtener todos los campos excepto los estándar
        data = {}
        standard_fields = {'context', 'priority', 'pagination', 'sorting', 'filters'}
        for key, value in self.__dict__.items():
            if key not in standard_fields:
                data[key] = value
        return data


T = TypeVar('T')


@dataclass
class QueryResult(Generic[T]):
    """
    Resultado de ejecución de consulta con paginación y metadatos.
    
    Contiene:
    - Datos de consulta o información de error
    - Metadatos de paginación
    - Métricas de rendimiento
    - Información de caché
    """
    
    success: bool
    query_id: str
    correlation_id: str
    data: Optional[List[T]] = None
    single_result: Optional[T] = None
    error: Optional[str] = None
    error_code: Optional[str] = None
    execution_time_ms: Optional[float] = None
    total_count: Optional[int] = None
    page_number: Optional[int] = None
    page_size: Optional[int] = None
    total_pages: Optional[int] = None
    has_next_page: bool = False
    has_previous_page: bool = False
    cached: bool = False
    cache_key: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def success_result(
        cls,
        query: Query,
        data: Optional[Union[List[T], T]] = None,
        total_count: Optional[int] = None,
        execution_time_ms: Optional[float] = None,
        cached: bool = False,
        cache_key: Optional[str] = None
    ) -> 'QueryResult[T]':
        """Crear resultado de consulta exitoso."""
        # Determinar si es resultado único o lista
        single_result = None
        data_list = None
        
        if data is not None:
            if isinstance(data, list):
                data_list = data
                if total_count is None:
                    total_count = len(data_list)
            else:
                single_result = data
                total_count = 1
        
        # Calcular información de paginación
        page_number = query.pagination.page_number if query.pagination else None
        page_size = query.pagination.page_size if query.pagination else None
        total_pages = None
        has_next_page = False
        has_previous_page = False
        
        if query.pagination and total_count is not None:
            total_pages = (total_count + page_size - 1) // page_size
            has_next_page = page_number < total_pages
            has_previous_page = page_number > 1
        
        return cls(
            success=True,
            query_id=query.query_id,
            correlation_id=query.correlation_id,
            data=data_list,
            single_result=single_result,
            total_count=total_count,
            page_number=page_number,
            page_size=page_size,
            total_pages=total_pages,
            has_next_page=has_next_page,
            has_previous_page=has_previous_page,
            execution_time_ms=execution_time_ms,
            cached=cached,
            cache_key=cache_key
        )
    
    @classmethod
    def failure_result(
        cls,
        query: Query,
        error: str,
        error_code: Optional[str] = None,
        execution_time_ms: Optional[float] = None
    ) -> 'QueryResult[T]':
        """Crear resultado de consulta fallido."""
        return cls(
            success=False,
            query_id=query.query_id,
            correlation_id=query.correlation_id,
            error=error,
            error_code=error_code,
            execution_time_ms=execution_time_ms
        )
    
    @classmethod
    def empty_result(cls, query: Query) -> 'QueryResult[T]':
        """Crear resultado exitoso vacío."""
        return cls.success_result(query, data=[])
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            'success': self.success,
            'query_id': self.query_id,
            'correlation_id': self.correlation_id,
            'data': self.data,
            'single_result': self.single_result,
            'error': self.error,
            'error_code': self.error_code,
            'execution_time_ms': self.execution_time_ms,
            'pagination': {
                'total_count': self.total_count,
                'page_number': self.page_number,
                'page_size': self.page_size,
                'total_pages': self.total_pages,
                'has_next_page': self.has_next_page,
                'has_previous_page': self.has_previous_page
            } if self.page_number else None,
            'cached': self.cached,
            'cache_key': self.cache_key,
            'metadata': self.metadata
        }


class QueryHandler(ABC, Generic[T]):
    """
    Interfaz para procesamiento de consultas.
    
    Siguiendo el patrón Query Handler:
    - Responsabilidad única para un tipo de consulta
    - Procesamiento sin estado
    - Optimización de modelo de lectura
    - Implementación de estrategia de caché
    """
    
    @abstractmethod
    def handle(self, query: Query) -> QueryResult[T]:
        """
        Manejar ejecución de consulta.
        
        Args:
            query: Consulta a procesar
            
        Returns:
            Resultado de ejecución de consulta
        """
        pass
    
    def can_handle(self, query: Query) -> bool:
        """
        Verificar si el handler puede procesar la consulta.
        Sobrescribir para manejo condicional.
        
        Args:
            query: Consulta a verificar
            
        Returns:
            True si el handler puede procesar la consulta
        """
        return True
    
    def get_supported_query_types(self) -> List[type]:
        """
        Obtener lista de tipos de consulta que soporta este handler.
        Sobrescribir en handlers concretos.
        
        Returns:
            Lista de tipos de consulta soportados
        """
        return []
    
    def get_cache_key(self, query: Query) -> Optional[str]:
        """
        Generar clave de caché para consulta.
        Sobrescribir para estrategias de caché personalizadas.
        
        Args:
            query: Consulta para la cual generar clave de caché
            
        Returns:
            String de clave de caché o None si el caché está deshabilitado
        """
        if not query.context.cache_enabled:
            return None
        
        # Generación de clave de caché por defecto
        query_type = type(query).__name__
        filter_hash = hash(frozenset(query.filters.items())) if query.filters else 0
        
        key_parts = [
            query_type,
            query.context.tenant_id or "default",
            str(filter_hash)
        ]
        
        if query.pagination:
            key_parts.extend([
                str(query.pagination.page_number),
                str(query.pagination.page_size)
            ])
        
        if query.sorting:
            sort_key = "_".join(f"{s.field}_{s.direction}" for s in query.sorting)
            key_parts.append(sort_key)
        
        return "_".join(key_parts)


class AsyncQueryHandler(QueryHandler[T], ABC):
    """
    Clase base para handlers de consulta asíncronos.
    
    Proporciona framework para procesamiento de consultas de larga duración o en segundo plano.
    """
    
    @abstractmethod
    async def handle_async(self, query: Query) -> QueryResult[T]:
        """
        Manejar consulta asíncronamente.
        
        Args:
            query: Consulta a procesar
            
        Returns:
            Resultado de ejecución de consulta
        """
        pass
    
    def handle(self, query: Query) -> QueryResult[T]:
        """
        Wrapper síncrono para manejo asíncrono.
        Puede ser sobrescrito para handlers sólo síncronos.
        """
        import asyncio
        return asyncio.run(self.handle_async(query))


# Decorador SingleDispatch para enrutamiento de consultas (del tutorial)
@singledispatch
def ejecutar_query(query: Query) -> QueryResult[Any]:
    """
    Ejecutar consulta usando patrón SingleDispatch del tutorial.
    
    Este es el punto de entrada principal para ejecución de consultas.
    Registrar handlers usando decorador @ejecutar_query.register.
    
    Args:
        query: Consulta a ejecutar
        
    Returns:
        Resultado de ejecución de consulta
        
    Raises:
        DomainException: Si no hay handler registrado para el tipo de consulta
    """
    raise DomainException(
        message=f"No hay handler registrado para el tipo de consulta: {type(query).__name__}",
        error_code="NO_QUERY_HANDLER"
    )


class ReadModel(ABC):
    """
    Interfaz para implementaciones de modelos de lectura.
    
    Los modelos de lectura están optimizados para operaciones de consulta:
    - Estructuras de datos desnormalizadas
    - Optimizados para patrones de consulta específicos
    - Eventualmente consistentes con modelo de escritura
    - Vistas cacheadas o materializadas
    """
    
    @abstractmethod
    def refresh(self) -> None:
        """Refrescar datos del modelo de lectura desde la fuente."""
        pass
    
    @abstractmethod
    def is_stale(self) -> bool:
        """Verificar si los datos del modelo de lectura están obsoletos."""
        pass
    
    @abstractmethod
    def get_last_updated(self) -> Optional[datetime]:
        """Obtener timestamp de la última actualización."""
        pass


class CachedReadModel(ReadModel):
    """Modelo de lectura con capacidades de caché."""
    
    def __init__(self, cache_ttl_seconds: int = 300):
        self._cache_ttl_seconds = cache_ttl_seconds
        self._last_updated: Optional[datetime] = None
        self._data_cache: Dict[str, Any] = {}
    
    def get_cached_data(self, key: str) -> Optional[Any]:
        """Obtener datos del caché."""
        if not self.is_cache_valid():
            self.clear_cache()
            return None
        return self._data_cache.get(key)
    
    def set_cached_data(self, key: str, data: Any) -> None:
        """Establecer datos en el caché."""
        self._data_cache[key] = data
        self._last_updated = datetime.now(timezone.utc)
    
    def clear_cache(self) -> None:
        """Limpiar todos los datos cacheados."""
        self._data_cache.clear()
        self._last_updated = None
    
    def is_cache_valid(self) -> bool:
        """Verificar si el caché aún es válido."""
        if not self._last_updated:
            return False
        
        age_seconds = (datetime.now(timezone.utc) - self._last_updated).total_seconds()
        return age_seconds < self._cache_ttl_seconds
    
    def is_stale(self) -> bool:
        """Verificar si el modelo de lectura está obsoleto."""
        return not self.is_cache_valid()
    
    def get_last_updated(self) -> Optional[datetime]:
        """Obtener timestamp de la última actualización."""
        return self._last_updated
    
    def refresh(self) -> None:
        """Refrescar limpiando el caché."""
        self.clear_cache()


class QueryBus:
    """
    Bus de consultas para enrutar consultas a los handlers apropiados.
    
    Proporciona:
    - Registro y descubrimiento de handlers
    - Integración de caché
    - Monitoreo de rendimiento
    - Manejo de errores
    """
    
    def __init__(self):
        self._handlers: Dict[type, QueryHandler] = {}
        self._cache_provider: Optional['CacheProvider'] = None
        self._metrics: Dict[str, Any] = {}
    
    def register_handler(self, query_type: type, handler: QueryHandler) -> None:
        """
        Register query handler.
        
        Args:
            query_type: Type of query to handle
            handler: Handler instance
        """
        self._handlers[query_type] = handler
        
        # Also register with singledispatch
        ejecutar_query.register(query_type, handler.handle)
    
    def set_cache_provider(self, cache_provider: 'CacheProvider') -> None:
        """Set cache provider for query results."""
        self._cache_provider = cache_provider
    
    def dispatch(self, query: Query) -> QueryResult[Any]:
        """
        Dispatch query to appropriate handler.
        
        Args:
            query: Query to dispatch
            
        Returns:
            Query execution result
        """
        import time
        start_time = time.time()
        
        try:
            # Check cache first
            if query.context.cache_enabled and self._cache_provider:
                cached_result = self._try_get_cached_result(query)
                if cached_result:
                    execution_time = (time.time() - start_time) * 1000
                    cached_result.execution_time_ms = execution_time
                    self._record_metrics(query, cached_result, execution_time)
                    return cached_result
            
            # Find and execute handler
            handler = self._find_handler(query)
            result = handler.handle(query)
            
            # Cache result if successful
            if result.success and query.context.cache_enabled and self._cache_provider:
                self._cache_result(query, result)
            
            # Record metrics
            execution_time = (time.time() - start_time) * 1000
            result.execution_time_ms = execution_time
            self._record_metrics(query, result, execution_time)
            
            return result
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            
            error_result = QueryResult.failure_result(
                query=query,
                error=str(e),
                error_code=getattr(e, 'error_code', 'QUERY_EXECUTION_ERROR'),
                execution_time_ms=execution_time
            )
            
            self._record_metrics(query, error_result, execution_time)
            return error_result
    
    def _find_handler(self, query: Query) -> QueryHandler:
        """Find appropriate handler for query."""
        query_type = type(query)
        
        if query_type in self._handlers:
            return self._handlers[query_type]
        
        # Check if any registered handler can handle this query
        for handler in self._handlers.values():
            if handler.can_handle(query):
                return handler
        
        raise DomainException(
            message=f"No handler found for query: {query_type.__name__}",
            error_code="NO_QUERY_HANDLER"
        )
    
    def _try_get_cached_result(self, query: Query) -> Optional[QueryResult]:
        """Try to get cached result for query."""
        handler = self._handlers.get(type(query))
        if not handler:
            return None
        
        cache_key = handler.get_cache_key(query)
        if not cache_key:
            return None
        
        cached_data = self._cache_provider.get(cache_key)
        if cached_data:
            # Create result from cached data
            result = QueryResult.success_result(
                query=query,
                data=cached_data,
                cached=True,
                cache_key=cache_key
            )
            return result
        
        return None
    
    def _cache_result(self, query: Query, result: QueryResult) -> None:
        """Cache query result."""
        handler = self._handlers.get(type(query))
        if not handler:
            return
        
        cache_key = handler.get_cache_key(query)
        if not cache_key:
            return
        
        # Cache the data portion of the result
        data_to_cache = result.data or result.single_result
        if data_to_cache is not None:
            ttl = query.context.cache_ttl_seconds
            self._cache_provider.set(cache_key, data_to_cache, ttl)
            result.cache_key = cache_key
    
    def _record_metrics(self, query: Query, result: QueryResult, execution_time: float) -> None:
        """Record query execution metrics."""
        query_type = type(query).__name__
        
        if query_type not in self._metrics:
            self._metrics[query_type] = {
                'total_executions': 0,
                'successful_executions': 0,
                'failed_executions': 0,
                'cache_hits': 0,
                'cache_misses': 0,
                'total_execution_time': 0,
                'avg_execution_time': 0
            }
        
        metrics = self._metrics[query_type]
        metrics['total_executions'] += 1
        metrics['total_execution_time'] += execution_time
        
        if result.success:
            metrics['successful_executions'] += 1
            if result.cached:
                metrics['cache_hits'] += 1
            else:
                metrics['cache_misses'] += 1
        else:
            metrics['failed_executions'] += 1
            metrics['cache_misses'] += 1
        
        metrics['avg_execution_time'] = metrics['total_execution_time'] / metrics['total_executions']
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get query execution metrics."""
        return self._metrics.copy()
    
    def clear_metrics(self) -> None:
        """Clear all metrics."""
        self._metrics.clear()


class CacheProvider(ABC):
    """Abstract cache provider interface."""
    
    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        pass
    
    @abstractmethod
    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        """Set value in cache with optional TTL."""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> None:
        """Delete value from cache."""
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """Clear all cached values."""
        pass


class InMemoryCacheProvider(CacheProvider):
    """Simple in-memory cache provider."""
    
    def __init__(self):
        self._cache: Dict[str, tuple[Any, Optional[datetime]]] = {}
    
    def get(self, key: str) -> Optional[Any]:
        if key not in self._cache:
            return None
        
        value, expiry = self._cache[key]
        
        # Check expiry
        if expiry and datetime.now(timezone.utc) > expiry:
            del self._cache[key]
            return None
        
        return value
    
    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        expiry = None
        if ttl_seconds:
            expiry = datetime.now(timezone.utc) + datetime.timedelta(seconds=ttl_seconds)
        
        self._cache[key] = (value, expiry)
    
    def delete(self, key: str) -> None:
        self._cache.pop(key, None)
    
    def clear(self) -> None:
        self._cache.clear()
