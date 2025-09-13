from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Any, Dict, Optional
import uuid


@dataclass
class DomainEvent:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "event_type": self.__class__.__name__
        }


@dataclass
class IntegrationEvent(DomainEvent):
    correlation_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        if self.correlation_id:
            data["correlation_id"] = self.correlation_id
        return data


class BaseEntity:
    def __init__(self):
        self._id = str(uuid.uuid4())
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
    
    def update_timestamp(self):
        self._updated_at = datetime.utcnow()


class AggregateRoot(BaseEntity):
    def __init__(self):
        super().__init__()
        self._eventos: List[DomainEvent] = []
        self._version = 0
    
    @property
    def eventos(self) -> List[DomainEvent]:
        return self._eventos.copy()
    
    @property
    def version(self) -> int:
        return self._version
    
    def publicar_evento(self, evento: DomainEvent):
        self._eventos.append(evento)
    
    def marcar_eventos_como_procesados(self):
        self._eventos.clear()
    
    def _increment_version(self):
        self._version += 1
    
    @classmethod
    @abstractmethod
    def from_events(cls, events: List[DomainEvent]) -> 'AggregateRoot':
        pass


@dataclass
class ValueObject(ABC):
    def __post_init__(self):
        self._validate()
    
    @abstractmethod
    def _validate(self):
        pass


class Repository(ABC):
    @abstractmethod
    async def save(self, entity: BaseEntity):
        pass
    
    @abstractmethod
    async def get_by_id(self, entity_id: str) -> Optional[BaseEntity]:
        pass
    
    @abstractmethod
    async def search(self, criteria: Dict[str, Any]) -> List[BaseEntity]:
        pass
    
    @abstractmethod
    async def delete(self, entity_id: str):
        pass