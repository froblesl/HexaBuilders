import uuid
from abc import ABC
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Callable
from dataclasses import dataclass, field

from .eventos import DomainEvent, EventMetadata
from .excepciones import ValidationException


class TimestampMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        current_time = datetime.now(timezone.utc)
        self._created_at = current_time
        self._updated_at = current_time
    
    @property
    def created_at(self) -> datetime:
        return self._created_at
    
    @property
    def updated_at(self) -> datetime:
        return self._updated_at
    
    def mark_updated(self) -> None:
        self._updated_at = datetime.now(timezone.utc)
    
    def was_created_after(self, timestamp: datetime) -> bool:
        return self._created_at > timestamp
    
    def was_updated_after(self, timestamp: datetime) -> bool:
        return self._updated_at > timestamp
    
    def age_in_seconds(self) -> float:
        return (datetime.now(timezone.utc) - self._created_at).total_seconds()
    
    def seconds_since_update(self) -> float:
        return (datetime.now(timezone.utc) - self._updated_at).total_seconds()


class ValidatorMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._validation_rules: List[Callable[[], None]] = []
        self._validation_errors: List[str] = []
        self._is_validation_enabled = True
    
    def add_validation_rule(self, rule: Callable[[], None]) -> None:
        self._validation_rules.append(rule)
    
    def enable_validation(self) -> None:
        self._is_validation_enabled = True
    
    def disable_validation(self) -> None:
        self._is_validation_enabled = False
    
    def validate(self) -> None:
        if not self._is_validation_enabled:
            return
        
        self._validation_errors.clear()
        
        for rule in self._validation_rules:
            try:
                rule()
            except Exception as e:
                self._validation_errors.append(str(e))
        
        if self._validation_errors:
            raise ValidationException(
                message=f"Validation failed: {len(self._validation_errors)} errors",
                field_errors={"entity": self._validation_errors}
            )
    
    def is_valid(self) -> bool:
        try:
            self.validate()
            return True
        except ValidationException:
            return False
    
    def get_validation_errors(self) -> List[str]:
        return self._validation_errors.copy()


class EventPublisherMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._pending_events: List[DomainEvent] = []
        self._event_subscribers: Dict[str, List[Callable[[DomainEvent], None]]] = {}
    
    def publish_event(self, event: DomainEvent) -> None:
        self._pending_events.append(event)
        self._notify_subscribers(event)
    
    def subscribe_to_event(self, event_type: str, handler: Callable[[DomainEvent], None]) -> None:
        if event_type not in self._event_subscribers:
            self._event_subscribers[event_type] = []
        self._event_subscribers[event_type].append(handler)
    
    def get_pending_events(self) -> List[DomainEvent]:
        return self._pending_events.copy()
    
    def clear_events(self) -> None:
        self._pending_events.clear()
    
    def has_pending_events(self) -> bool:
        return len(self._pending_events) > 0
    
    def _notify_subscribers(self, event: DomainEvent) -> None:
        event_type = event.__class__.__name__
        if event_type in self._event_subscribers:
            for handler in self._event_subscribers[event_type]:
                try:
                    handler(event)
                except Exception as e:
                    # Log error but don't fail event publication
                    self._handle_subscriber_error(handler, event, e)
    
    def _handle_subscriber_error(self, handler: Callable, event: DomainEvent, error: Exception) -> None:
        pass


class AuditableMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._created_by: Optional[str] = None
        self._updated_by: Optional[str] = None
        self._change_history: List['ChangeRecord'] = []
    
    @property
    def created_by(self) -> Optional[str]:
        return self._created_by
    
    @property
    def updated_by(self) -> Optional[str]:
        return self._updated_by
    
    def set_created_by(self, user_id: str) -> None:
        if self._created_by is None:
            self._created_by = user_id
    
    def set_updated_by(self, user_id: str, change_description: Optional[str] = None) -> None:
        old_updated_by = self._updated_by
        self._updated_by = user_id
        
        change_record = ChangeRecord(
            timestamp=datetime.now(timezone.utc),
            user_id=user_id,
            previous_user=old_updated_by,
            description=change_description
        )
        self._change_history.append(change_record)
    
    def get_change_history(self) -> List['ChangeRecord']:
        return self._change_history.copy()
    
    def get_recent_changes(self, limit: int = 10) -> List['ChangeRecord']:
        return self._change_history[-limit:] if self._change_history else []
    
    def was_changed_by_user(self, user_id: str) -> bool:
        return any(change.user_id == user_id for change in self._change_history)


@dataclass
class ChangeRecord:
    timestamp: datetime
    user_id: str
    previous_user: Optional[str] = None
    description: Optional[str] = None
    
    def __str__(self) -> str:
        desc = f" - {self.description}" if self.description else ""
        return f"{self.timestamp.isoformat()} by {self.user_id}{desc}"


class SoftDeleteMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._is_deleted = False
        self._deleted_at: Optional[datetime] = None
        self._deleted_by: Optional[str] = None
        self._deletion_reason: Optional[str] = None
    
    @property
    def is_deleted(self) -> bool:
        return self._is_deleted
    
    @property
    def deleted_at(self) -> Optional[datetime]:
        return self._deleted_at
    
    @property
    def deleted_by(self) -> Optional[str]:
        return self._deleted_by
    
    @property
    def deletion_reason(self) -> Optional[str]:
        return self._deletion_reason
    
    def soft_delete(
        self, 
        deleted_by: Optional[str] = None, 
        reason: Optional[str] = None
    ) -> None:
        if self._is_deleted:
            return
        
        self._is_deleted = True
        self._deleted_at = datetime.now(timezone.utc)
        self._deleted_by = deleted_by
        self._deletion_reason = reason
        
        if hasattr(self, 'mark_updated'):
            self.mark_updated()
    
    def restore(self, restored_by: Optional[str] = None) -> None:
        if not self._is_deleted:
            return
        
        self._is_deleted = False
        
        old_deleted_at = self._deleted_at
        old_deleted_by = self._deleted_by
        old_reason = self._deletion_reason
        
        self._deleted_at = None
        self._deleted_by = None
        self._deletion_reason = None
        
        if hasattr(self, 'set_updated_by') and restored_by:
            self.set_updated_by(
                restored_by, 
                f"Restored entity (was deleted at {old_deleted_at} by {old_deleted_by})"
            )
        elif hasattr(self, 'mark_updated'):
            self.mark_updated()
    
    def days_since_deletion(self) -> Optional[float]:
        if not self._is_deleted or not self._deleted_at:
            return None
        
        return (datetime.now(timezone.utc) - self._deleted_at).total_seconds() / 86400


class VersionedMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._version = 1
        self._version_lock: Set[str] = set()
    
    @property
    def version(self) -> int:
        return self._version
    
    def increment_version(self) -> None:
        self._version += 1
        
        self._version_lock.clear()
        
        if hasattr(self, 'mark_updated'):
            self.mark_updated()
    
    def check_version(self, expected_version: int) -> bool:
        return self._version == expected_version
    
    def acquire_version_lock(self, lock_id: str) -> bool:
        if lock_id in self._version_lock:
            return False
        
        self._version_lock.add(lock_id)
        return True
    
    def release_version_lock(self, lock_id: str) -> None:
        self._version_lock.discard(lock_id)
    
    def is_version_locked(self) -> bool:
        return len(self._version_lock) > 0
    
    def get_active_locks(self) -> Set[str]:
        return self._version_lock.copy()


class IdentityMixin:
    def __init__(self, entity_id: Optional[str] = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._id = entity_id or str(uuid.uuid4())
        self._alternative_ids: Dict[str, str] = {}
    
    @property
    def id(self) -> str:
        return self._id
    
    def add_alternative_id(self, id_type: str, id_value: str) -> None:
        self._alternative_ids[id_type] = id_value
    
    def get_alternative_id(self, id_type: str) -> Optional[str]:
        return self._alternative_ids.get(id_type)
    
    def has_alternative_id(self, id_type: str) -> bool:
        return id_type in self._alternative_ids
    
    def get_all_alternative_ids(self) -> Dict[str, str]:
        return self._alternative_ids.copy()
    
    def remove_alternative_id(self, id_type: str) -> None:
        self._alternative_ids.pop(id_type, None)
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return False
        return self._id == other._id
    
    def __hash__(self) -> int:
        return hash(self._id)


class MetadataMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._metadata: Dict[str, Any] = {}
    
    def set_metadata(self, key: str, value: Any) -> None:
        self._metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        return self._metadata.get(key, default)
    
    def has_metadata(self, key: str) -> bool:
        return key in self._metadata
    
    def remove_metadata(self, key: str) -> None:
        self._metadata.pop(key, None)
    
    def clear_metadata(self) -> None:
        self._metadata.clear()
    
    def get_all_metadata(self) -> Dict[str, Any]:
        return self._metadata.copy()
    
    def update_metadata(self, metadata: Dict[str, Any]) -> None:
        self._metadata.update(metadata)


# Composite mixins for common combinations
class FullAuditMixin(TimestampMixin, AuditableMixin, VersionedMixin):
    pass


class SoftDeletableAuditMixin(FullAuditMixin, SoftDeleteMixin):
    pass


class EventDrivenEntityMixin(EventPublisherMixin, ValidatorMixin, TimestampMixin):
    pass
