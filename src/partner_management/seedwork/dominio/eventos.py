import json
import uuid
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Type, Union
from dataclasses import dataclass, field
from enum import Enum


class EventType(Enum):
    DOMAIN = "domain"
    INTEGRATION = "integration"
    NOTIFICATION = "notification"


@dataclass(frozen=True)
class EventMetadata:
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    causation_id: Optional[str] = None
    occurred_on: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    event_version: int = 1
    source: Optional[str] = None
    user_id: Optional[str] = None
    tenant_id: Optional[str] = None
    
    def with_correlation(self, correlation_id: str) -> 'EventMetadata':
        return EventMetadata(
            event_id=str(uuid.uuid4()),
            correlation_id=correlation_id,
            causation_id=self.event_id,
            occurred_on=datetime.now(timezone.utc).isoformat(),
            event_version=self.event_version,
            source=self.source,
            user_id=self.user_id,
            tenant_id=self.tenant_id
        )


class BaseEvent(ABC):
    def __init__(
        self,
        aggregate_id: str,
        metadata: Optional[EventMetadata] = None,
        **kwargs
    ):
        self._aggregate_id = aggregate_id
        self._metadata = metadata or EventMetadata()
        self._event_data = kwargs
        self._event_type = self._get_event_type()
    
    @property
    def aggregate_id(self) -> str:
        return self._aggregate_id
    
    @property
    def metadata(self) -> EventMetadata:
        return self._metadata
    
    @property
    def event_data(self) -> Dict[str, Any]:
        return self._event_data.copy()
    
    @property
    def event_type(self) -> EventType:
        return self._event_type
    
    @property
    def event_name(self) -> str:
        return self.__class__.__name__
    
    @abstractmethod
    def _get_event_type(self) -> EventType:
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'event_name': self.event_name,
            'event_type': self.event_type.value,
            'aggregate_id': self.aggregate_id,
            'metadata': {
                'event_id': self.metadata.event_id,
                'correlation_id': self.metadata.correlation_id,
                'causation_id': self.metadata.causation_id,
                'occurred_on': self.metadata.occurred_on,
                'event_version': self.metadata.event_version,
                'source': self.metadata.source,
                'user_id': self.metadata.user_id,
                'tenant_id': self.metadata.tenant_id
            },
            'event_data': self.event_data
        }
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), default=str)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseEvent':
        metadata_data = data.get('metadata', {})
        metadata = EventMetadata(
            event_id=metadata_data.get('event_id', str(uuid.uuid4())),
            correlation_id=metadata_data.get('correlation_id', str(uuid.uuid4())),
            causation_id=metadata_data.get('causation_id'),
            occurred_on=metadata_data.get('occurred_on', datetime.now(timezone.utc).isoformat()),
            event_version=metadata_data.get('event_version', 1),
            source=metadata_data.get('source'),
            user_id=metadata_data.get('user_id'),
            tenant_id=metadata_data.get('tenant_id')
        )
        
        return cls(
            aggregate_id=data['aggregate_id'],
            metadata=metadata,
            **data.get('event_data', {})
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> 'BaseEvent':
        return cls.from_dict(json.loads(json_str))
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BaseEvent):
            return False
        return self.metadata.event_id == other.metadata.event_id
    
    def __hash__(self) -> int:
        return hash(self.metadata.event_id)
    
    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"aggregate_id={self.aggregate_id}, "
            f"event_id={self.metadata.event_id})"
        )


class DomainEvent(BaseEvent):
    def _get_event_type(self) -> EventType:
        return EventType.DOMAIN
    
    def with_causation(self, causation_event: 'BaseEvent') -> 'DomainEvent':
        new_metadata = self.metadata.with_correlation(causation_event.metadata.correlation_id)
        new_metadata = EventMetadata(
            event_id=new_metadata.event_id,
            correlation_id=new_metadata.correlation_id,
            causation_id=causation_event.metadata.event_id,
            occurred_on=new_metadata.occurred_on,
            event_version=new_metadata.event_version,
            source=new_metadata.source,
            user_id=new_metadata.user_id,
            tenant_id=new_metadata.tenant_id
        )
        
        return self.__class__(
            aggregate_id=self.aggregate_id,
            metadata=new_metadata,
            **self.event_data
        )


class IntegrationEvent(BaseEvent):
    def _get_event_type(self) -> EventType:
        return EventType.INTEGRATION
    
    def to_cloud_event(self) -> Dict[str, Any]:
        return {
            'specversion': '1.0',
            'type': f"com.hexabuilders.partners.{self.event_name}",
            'source': f"//partners/{self.aggregate_id}",
            'id': self.metadata.event_id,
            'time': self.metadata.occurred_on,
            'datacontenttype': 'application/json',
            'subject': self.aggregate_id,
            'data': self.event_data,
            'correlationid': self.metadata.correlation_id,
            'causationid': self.metadata.causation_id
        }
    
    @classmethod
    def from_cloud_event(cls, cloud_event: Dict[str, Any]) -> 'IntegrationEvent':
        aggregate_id = cloud_event.get('subject', '')
        if not aggregate_id and 'source' in cloud_event:
            source_parts = cloud_event['source'].split('/')
            aggregate_id = source_parts[-1] if source_parts else ''
        
        metadata = EventMetadata(
            event_id=cloud_event.get('id', str(uuid.uuid4())),
            correlation_id=cloud_event.get('correlationid', str(uuid.uuid4())),
            causation_id=cloud_event.get('causationid'),
            occurred_on=cloud_event.get('time', datetime.now(timezone.utc).isoformat()),
            event_version=1,
            source=cloud_event.get('source')
        )
        
        return cls(
            aggregate_id=aggregate_id,
            metadata=metadata,
            **cloud_event.get('data', {})
        )


class EventVersionError(Exception):
    def __init__(self, current_version: int, required_version: int, event_name: str):
        self.current_version = current_version
        self.required_version = required_version
        self.event_name = event_name
        super().__init__(
            f"Event {event_name} version {current_version} "
            f"incompatible with required version {required_version}"
        )


class EventSerializer:
    @staticmethod
    def serialize(event: BaseEvent) -> bytes:
        return event.to_json().encode('utf-8')
    
    @staticmethod
    def deserialize(data: bytes, event_class: Type[BaseEvent]) -> BaseEvent:
        json_str = data.decode('utf-8')
        return event_class.from_json(json_str)
    
    @staticmethod
    def is_compatible(event_data: Dict[str, Any], required_version: int) -> bool:
        event_version = event_data.get('metadata', {}).get('event_version', 1)
        # Backward compatibility: newer versions should support older requirements
        return event_version >= required_version
    
    @staticmethod
    def migrate_event(event_data: Dict[str, Any], target_version: int) -> Dict[str, Any]:
        current_version = event_data.get('metadata', {}).get('event_version', 1)
        
        if current_version == target_version:
            return event_data
        
        # Add version-specific migration logic here
        # For now, just update the version number
        migrated_data = event_data.copy()
        migrated_data['metadata']['event_version'] = target_version
        
        return migrated_data


# Concrete domain event examples for the partners domain
class PartnerCreated(DomainEvent):
    def __init__(
        self, 
        aggregate_id: str, 
        business_name: str, 
        email: str,
        metadata: Optional[EventMetadata] = None
    ):
        super().__init__(
            aggregate_id=aggregate_id,
            metadata=metadata,
            business_name=business_name,
            email=email
        )


class PartnerStatusChanged(DomainEvent):
    def __init__(
        self, 
        aggregate_id: str, 
        old_status: str, 
        new_status: str,
        reason: Optional[str] = None,
        metadata: Optional[EventMetadata] = None
    ):
        super().__init__(
            aggregate_id=aggregate_id,
            metadata=metadata,
            old_status=old_status,
            new_status=new_status,
            reason=reason
        )


# Concrete integration event examples
class PartnerRegistrationCompleted(IntegrationEvent):
    def __init__(
        self, 
        aggregate_id: str, 
        business_name: str, 
        email: str,
        category: str,
        metadata: Optional[EventMetadata] = None
    ):
        super().__init__(
            aggregate_id=aggregate_id,
            metadata=metadata,
            business_name=business_name,
            email=email,
            category=category
        )
