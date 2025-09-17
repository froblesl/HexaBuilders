from abc import ABC, abstractmethod
from typing import List, Optional, Any, Dict, TypeVar, Generic
from dataclasses import dataclass
from contextlib import contextmanager

from .entidades import AggregateRoot
from .eventos import DomainEvent

T = TypeVar('T', bound=AggregateRoot)


class UnitOfWork(ABC):
    """
    Unit of Work pattern implementation.
    
    Manages transaction boundaries and coordinates 
    writing out changes and resolving concurrency conflicts.
    """
    
    def __init__(self):
        self._aggregates: Dict[str, AggregateRoot] = {}
        self._committed = False
        self._rolled_back = False
    
    @abstractmethod
    def commit(self) -> None:
        """Commit all changes in the unit of work."""
        pass
    
    @abstractmethod
    def rollback(self) -> None:
        """Rollback all changes in the unit of work."""
        pass
    
    def get_aggregates_with_events(self) -> List[AggregateRoot]:
        """Get all aggregates that have pending domain events."""
        return [
            aggregate for aggregate in self._aggregates.values()
            if hasattr(aggregate, 'obtener_eventos') and aggregate.obtener_eventos()
        ]
    
    def register_aggregate(self, aggregate: AggregateRoot) -> None:
        """Register an aggregate for tracking."""
        if hasattr(aggregate, 'id'):
            self._aggregates[str(aggregate.id)] = aggregate
    
    def get_aggregate(self, aggregate_id: str) -> Optional[AggregateRoot]:
        """Get a tracked aggregate by ID."""
        return self._aggregates.get(aggregate_id)
    
    @property
    def is_committed(self) -> bool:
        """Check if the unit of work has been committed."""
        return self._committed
    
    @property
    def is_rolled_back(self) -> bool:
        """Check if the unit of work has been rolled back."""
        return self._rolled_back


class InMemoryUnitOfWork(UnitOfWork):
    """Simple in-memory implementation of Unit of Work for testing."""
    
    def __init__(self):
        super().__init__()
        self._changes: List[Dict[str, Any]] = []
    
    def commit(self) -> None:
        """Commit changes (no-op for in-memory implementation)."""
        if self._rolled_back:
            raise RuntimeError("Cannot commit after rollback")
        
        self._committed = True
        self._changes.clear()
    
    def rollback(self) -> None:
        """Rollback changes."""
        if self._committed:
            raise RuntimeError("Cannot rollback after commit")
        
        self._rolled_back = True
        self._changes.clear()
        self._aggregates.clear()
    
    def track_change(self, change_type: str, entity: Any, **kwargs) -> None:
        """Track a change for potential rollback."""
        self._changes.append({
            'type': change_type,
            'entity': entity,
            'metadata': kwargs
        })


@contextmanager
def unit_of_work_scope(uow: UnitOfWork):
    """Context manager for unit of work transactions."""
    try:
        yield uow
        uow.commit()
    except Exception:
        uow.rollback()
        raise


# Repository interface that works with Unit of Work
class Repository(ABC):
    """Base repository interface that works with Unit of Work."""
    
    def __init__(self, uow: Optional[UnitOfWork] = None):
        self._uow = uow or InMemoryUnitOfWork()
    
    @property
    def unit_of_work(self) -> UnitOfWork:
        """Get the unit of work instance."""
        return self._uow
    
    def _register_aggregate(self, aggregate: AggregateRoot) -> None:
        """Register an aggregate with the unit of work."""
        self._uow.register_aggregate(aggregate)
