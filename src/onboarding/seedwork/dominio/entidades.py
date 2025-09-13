from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Any, Dict
import uuid


@dataclass
class BaseEvent:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "event_type": self.__class__.__name__
        }


@dataclass
class DomainEvent(BaseEvent):
    pass


@dataclass
class IntegrationEvent(BaseEvent):
    correlation_id: str = None
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        if self.correlation_id:
            data["correlation_id"] = self.correlation_id
        return data


class Entity(ABC):
    def __init__(self):
        self._id = str(uuid.uuid4())
        self._eventos: List[DomainEvent] = []
    
    @property
    def id(self) -> str:
        return self._id
    
    @property
    def eventos(self) -> List[DomainEvent]:
        return self._eventos.copy()
    
    def publicar_evento(self, evento: DomainEvent):
        self._eventos.append(evento)
    
    def marcar_eventos_como_procesados(self):
        self._eventos.clear()


class AggregateRoot(Entity, ABC):
    def __init__(self):
        super().__init__()
        self._version = 0
    
    @property
    def version(self) -> int:
        return self._version
    
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
    async def save(self, aggregate: AggregateRoot):
        pass
    
    @abstractmethod
    async def get_by_id(self, aggregate_id: str) -> AggregateRoot:
        pass


class EventStore(ABC):
    @abstractmethod
    async def save_events(self, aggregate_id: str, events: List[DomainEvent], expected_version: int):
        pass
    
    @abstractmethod
    async def get_events(self, aggregate_id: str, from_version: int = 0) -> List[DomainEvent]:
        pass