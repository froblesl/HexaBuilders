from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Any, Dict, Optional
import uuid


@dataclass
class BaseEntity:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def update_timestamp(self):
        self.updated_at = datetime.utcnow()


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


class SearchRepository(ABC):
    """Repository for full-text search operations"""
    
    @abstractmethod
    async def index_document(self, document_id: str, document: Dict[str, Any]):
        pass
    
    @abstractmethod
    async def search_documents(
        self, 
        query: str, 
        filters: Dict[str, Any] = None,
        size: int = 10,
        offset: int = 0
    ) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    async def update_document(self, document_id: str, document: Dict[str, Any]):
        pass
    
    @abstractmethod
    async def delete_document(self, document_id: str):
        pass


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


class EventPublisher(ABC):
    @abstractmethod
    async def publish(self, event: DomainEvent):
        pass