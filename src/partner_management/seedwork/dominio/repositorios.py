from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TypeVar, Generic, Callable
from enum import Enum

from .entidades import AggregateRoot, Entity


T = TypeVar('T', bound=AggregateRoot)
E = TypeVar('E', bound=Entity)


class SortDirection(Enum):
    """Direcciones de ordenamiento para consultas."""
    ASC = "asc"
    DESC = "desc"


class Repository(ABC, Generic[T]):
    """
    Interfaz base para repositorios de agregados.
    Define operaciones CRUD básicas para persistencia de agregados.
    """
    @abstractmethod
    def agregar(self, entity: T) -> None:
        """Agregar una nueva entidad al repositorio."""
        pass
    
    @abstractmethod
    def obtener_por_id(self, entity_id: str) -> Optional[T]:
        """Obtener entidad por su identificador único."""
        pass
    
    @abstractmethod
    def actualizar(self, entity: T) -> None:
        """Actualizar una entidad existente."""
        pass
    
    @abstractmethod
    def eliminar(self, entity_id: str) -> bool:
        """Eliminar entidad por ID. Retorna True si fue eliminada."""
        pass
    
    @abstractmethod
    def existe(self, entity_id: str) -> bool:
        """Verificar si existe una entidad con el ID dado."""
        pass
    
    @abstractmethod
    def obtener_todos(self) -> List[T]:
        """Obtener todas las entidades del repositorio."""
        pass


class SpecificationRepository(Repository[T], ABC):
    """
    Repositorio que soporta consultas usando el patrón Specification.
    Permite consultas complejas mediante especificaciones combinables.
    """
    @abstractmethod
    def obtener_por_especificacion(self, specification: 'Specification[T]') -> List[T]:
        """Obtener entidades que satisfacen la especificación."""
        pass
    
    @abstractmethod
    def contar_por_especificacion(self, specification: 'Specification[T]') -> int:
        """Contar entidades que satisfacen la especificación."""
        pass
    
    @abstractmethod
    def existe_por_especificacion(self, specification: 'Specification[T]') -> bool:
        """Verificar si existe al menos una entidad que satisface la especificación."""
        pass


class Specification(ABC, Generic[T]):
    """
    Clase base para especificaciones del dominio.
    Implementa el patrón Specification con capacidades de combinación lógica.
    """
    @abstractmethod
    def is_satisfied_by(self, entity: T) -> bool:
        """Verificar si la entidad satisface esta especificación."""
        pass
    
    def and_(self, other: 'Specification[T]') -> 'AndSpecification[T]':
        """Combinar con otra especificación usando lógica AND."""
        return AndSpecification(self, other)
    
    def or_(self, other: 'Specification[T]') -> 'OrSpecification[T]':
        """Combinar con otra especificación usando lógica OR."""
        return OrSpecification(self, other)
    
    def not_(self) -> 'NotSpecification[T]':
        """Crear negación de esta especificación."""
        return NotSpecification(self)


class AndSpecification(Specification[T]):
    """Especificación que requiere que ambas especificaciones se cumplan."""
    def __init__(self, left: Specification[T], right: Specification[T]):
        self._left = left
        self._right = right
    
    def is_satisfied_by(self, entity: T) -> bool:
        """Ambas especificaciones deben satisfacerse."""
        return self._left.is_satisfied_by(entity) and self._right.is_satisfied_by(entity)


class OrSpecification(Specification[T]):
    """Especificación que requiere que al menos una especificación se cumpla."""
    def __init__(self, left: Specification[T], right: Specification[T]):
        self._left = left
        self._right = right
    
    def is_satisfied_by(self, entity: T) -> bool:
        return self._left.is_satisfied_by(entity) or self._right.is_satisfied_by(entity)


class NotSpecification(Specification[T]):
    """Especificación que niega otra especificación."""
    def __init__(self, specification: Specification[T]):
        self._specification = specification
    
    def is_satisfied_by(self, entity: T) -> bool:
        return not self._specification.is_satisfied_by(entity)


class QueryCriteria:
    """
    Constructor de criterios de consulta con filtros, ordenamiento y paginación.
    Proporciona interfaz fluida para construcción de consultas complejas.
    """
    def __init__(self):
        self._filters: Dict[str, Any] = {}
        self._sort_by: Optional[str] = None
        self._sort_direction: SortDirection = SortDirection.ASC
        self._limit: Optional[int] = None
        self._offset: int = 0
    
    def filter_by(self, field: str, value: Any) -> 'QueryCriteria':
        """Añadir filtro por campo y valor."""
        self._filters[field] = value
        return self
    
    def sort_by(self, field: str, direction: SortDirection = SortDirection.ASC) -> 'QueryCriteria':
        """Establecer ordenamiento por campo y dirección."""
        self._sort_by = field
        self._sort_direction = direction
        return self
    
    def limit(self, limit: int) -> 'QueryCriteria':
        """Establecer límite de resultados."""
        self._limit = limit
        return self
    
    def offset(self, offset: int) -> 'QueryCriteria':
        """Establecer offset para paginación."""
        self._offset = offset
        return self
    
    @property
    def filters(self) -> Dict[str, Any]:
        """Obtener copia de los filtros aplicados."""
        return self._filters.copy()
    
    @property
    def sort_field(self) -> Optional[str]:
        """Obtener campo de ordenamiento."""
        return self._sort_by
    
    @property
    def sort_direction(self) -> SortDirection:
        """Obtener dirección de ordenamiento."""
        return self._sort_direction
    
    @property
    def result_limit(self) -> Optional[int]:
        """Obtener límite de resultados."""
        return self._limit
    
    @property
    def result_offset(self) -> int:
        """Obtener offset de paginación."""
        return self._offset


class PagedRepository(Repository[T], ABC):
    """
    Repositorio con soporte para paginación de resultados.
    Extiende Repository con capacidades de consulta paginada.
    """
    @abstractmethod
    def obtener_pagina(
        self, 
        criteria: QueryCriteria,
        page_size: int = 20,
        page_number: int = 1
    ) -> 'PagedResult[T]':
        """Obtener página de resultados según criterios y parámetros de paginación."""
        pass


class PagedResult(Generic[T]):
    """
    Resultado paginado que encapsula elementos e información de paginación.
    Proporciona metadatos sobre la página actual y navegación.
    """
    def __init__(
        self,
        items: List[T],
        total_count: int,
        page_size: int,
        page_number: int
    ):
        self._items = items
        self._total_count = total_count
        self._page_size = page_size
        self._page_number = page_number
    
    @property
    def items(self) -> List[T]:
        """Obtener elementos de la página actual."""
        return self._items
    
    @property
    def total_count(self) -> int:
        """Obtener número total de elementos."""
        return self._total_count
    
    @property
    def page_size(self) -> int:
        """Obtener tamaño de página."""
        return self._page_size
    
    @property
    def page_number(self) -> int:
        """Obtener número de página actual."""
        return self._page_number
    
    @property
    def total_pages(self) -> int:
        """Calcular número total de páginas."""
        return (self._total_count + self._page_size - 1) // self._page_size
    
    @property
    def has_next_page(self) -> bool:
        """Verificar si existe página siguiente."""
        return self._page_number < self.total_pages
    
    @property
    def has_previous_page(self) -> bool:
        """Verificar si existe página anterior."""
        return self._page_number > 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir resultado paginado a diccionario."""
        return {
            'items': [item.to_dict() if hasattr(item, 'to_dict') else str(item) for item in self._items],
            'pagination': {
                'total_count': self._total_count,
                'page_size': self._page_size,
                'page_number': self._page_number,
                'total_pages': self.total_pages,
                'has_next_page': self.has_next_page,
                'has_previous_page': self.has_previous_page
            }
        }


class UnitOfWorkRepository(Repository[T], ABC):
    """
    Repositorio que integra con Unit of Work para transacciones consistentes.
    Registra cambios para procesamiento en lote al confirmar la unidad de trabajo.
    """
    @abstractmethod
    def registrar_agregado(self, entity: T) -> None:
        """Registrar nuevo agregado para persistencia diferida."""
        pass
    
    @abstractmethod
    def registrar_modificado(self, entity: T) -> None:
        """Registrar agregado modificado para actualización diferida."""
        pass
    
    @abstractmethod
    def registrar_eliminado(self, entity: T) -> None:
        """Registrar agregado para eliminación diferida."""
        pass
    
    @abstractmethod
    def confirmar_cambios(self) -> None:
        """Confirmar todos los cambios registrados de forma atómica."""
        pass
    
    @abstractmethod
    def descartar_cambios(self) -> None:
        """Descartar todos los cambios registrados sin persistir."""
        pass


class ReadOnlyRepository(ABC, Generic[T]):
    """
    Repositorio de solo lectura para consultas sin capacidad de modificación.
    Ideal para reportes y consultas de análisis.
    """
    @abstractmethod
    def obtener_por_id(self, entity_id: str) -> Optional[T]:
        """Obtener entidad por ID."""
        pass
    
    @abstractmethod
    def buscar(self, criteria: QueryCriteria) -> List[T]:
        """Buscar entidades según criterios."""
        pass
    
    @abstractmethod
    def contar(self, criteria: QueryCriteria) -> int:
        """Contar entidades que satisfacen los criterios."""
        pass


class RepositoryFactory(ABC):
    """
    Fábrica abstracta para creación de repositorios.
    Permite abstraer la creación de diferentes tipos de repositorio.
    """
    @abstractmethod
    def create_repository(self, repository_type: type) -> Repository:
        """Crear repositorio del tipo especificado."""
        pass
    
    @abstractmethod
    def cleanup_repository(self, repository: Repository) -> None:
        """Limpiar recursos asociados al repositorio."""
        pass


# Especificaciones comunes para consultas de negocio típicas
class IdSpecification(Specification[T]):
    """Especificación para filtrar por ID de entidad."""
    def __init__(self, entity_id: str):
        self._entity_id = entity_id
    
    def is_satisfied_by(self, entity: T) -> bool:
        """Verificar si la entidad tiene el ID especificado."""
        return entity.id == self._entity_id


class StatusSpecification(Specification[T]):
    """Especificación para filtrar por estado de entidad."""
    def __init__(self, status: str):
        self._status = status
    
    def is_satisfied_by(self, entity: T) -> bool:
        return hasattr(entity, 'status') and entity.status == self._status


class DateRangeSpecification(Specification[T]):
    """Especificación para filtrar por rango de fechas."""
    def __init__(self, start_date: str, end_date: str, date_field: str = 'created_at'):
        self._start_date = start_date
        self._end_date = end_date
        self._date_field = date_field
    
    def is_satisfied_by(self, entity: T) -> bool:
        if not hasattr(entity, self._date_field):
            return False
        
        entity_date = getattr(entity, self._date_field)
        return self._start_date <= str(entity_date) <= self._end_date
