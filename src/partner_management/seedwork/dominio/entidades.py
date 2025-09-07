"""
Clases base Entity y AggregateRoot siguiendo principios DDD.
Implementa igualdad basada en identidad y gestión de eventos de dominio.
"""

import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Any, Optional
from dataclasses import dataclass, field


class Entity(ABC):
    def __init__(self, entity_id: Optional[str] = None):
        self._id = entity_id or str(uuid.uuid4())
        self._created_at = datetime.utcnow()
        self._updated_at = datetime.utcnow()
    
    @property
    def id(self) -> str:
        return self._id
    
    @property
    def created_at(self) -> datetime:
        return self._created_at
    
    @property
    def updated_at(self) -> datetime:
        return self._updated_at
    
    def _mark_updated(self) -> None:
        self._updated_at = datetime.utcnow()
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Entity):
            return False
        return self._id == other._id
    
    def __hash__(self) -> int:
        return hash(self._id)
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self._id})"


class AggregateRoot(Entity):    
    def __init__(self, entity_id: Optional[str] = None):
        super().__init__(entity_id)
        self._domain_events: List[Any] = []
    
    def agregar_evento(self, evento: Any) -> None:
        self._domain_events.append(evento)
        self._mark_updated()
    
    def limpiar_eventos(self) -> None:
        self._domain_events.clear()
    
    def obtener_eventos(self) -> List[Any]:
        return self._domain_events.copy()
    
    @property
    def has_events(self) -> bool:
        return len(self._domain_events) > 0


@dataclass(frozen=True)
class EntityId:
    value: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    def __post_init__(self):
        if not self.value:
            raise ValueError("El ID de entidad no puede estar vacío")
        
        # Validar formato UUID
        try:
            uuid.UUID(self.value)
        except ValueError:
            raise ValueError(f"Formato UUID inválido: {self.value}")
    
    def __str__(self) -> str:
        return self.value


class DomainEntity(Entity):
    def __init__(self, entity_id: Optional[str] = None):
        super().__init__(entity_id)
        self._version = 1
    
    @property
    def version(self) -> int:
        return self._version
    
    def _increment_version(self) -> None:
        self._version += 1
        self._mark_updated()
    
    @abstractmethod
    def validate(self) -> None:
        pass
    
    def apply_changes(self) -> None:
        self.validate()
        self._increment_version()


class SoftDeletableEntity(DomainEntity):
    def __init__(self, entity_id: Optional[str] = None):
        super().__init__(entity_id)
        self._is_deleted = False
        self._deleted_at: Optional[datetime] = None
    
    @property
    def is_deleted(self) -> bool:
        return self._is_deleted
    
    @property
    def deleted_at(self) -> Optional[datetime]:
        return self._deleted_at
    
    def soft_delete(self) -> None:
        if self._is_deleted:
            return
        
        self._is_deleted = True
        self._deleted_at = datetime.utcnow()
        self._mark_updated()
    
    def restore(self) -> None:
        if not self._is_deleted:
            return
        
        self._is_deleted = False
        self._deleted_at = None
        self._mark_updated()
