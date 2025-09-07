import pickle
import uuid
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Set, Callable, TypeVar
from contextlib import contextmanager
from dataclasses import dataclass, field
from flask import session

from ..dominio.entidades import AggregateRoot
from ..dominio.eventos import DomainEvent
from ..dominio.excepciones import DomainException


T = TypeVar('T', bound=AggregateRoot)


class OperationType:
    """Tipos de operaciones en la unidad de trabajo."""
    INSERT = "insert"
    UPDATE = "update"
    DELETE = "delete"


@dataclass
class BatchOperation:
    """
    Operación por lotes para ejecución diferida (del tutorial).
    
    Las operaciones se registran y ejecutan juntas durante la confirmación
    para garantizar la atomicidad y el orden correcto de los eventos.
    """
    
    operation_id: str
    operation_type: str
    entity: AggregateRoot
    repository_name: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=lambda: __import__('time').time())
    
    def __post_init__(self):
        if not self.operation_id:
            self.operation_id = str(uuid.uuid4())


class UnitOfWork(ABC):
    """
    Clase base de la unidad de trabajo que gestiona los límites transaccionales.
    
    Siguiendo la implementación del tutorial:
    - Registro por lotes para ejecución diferida
    - Gestión de sesiones mediante la serialización de sesiones de Flask
    - Capacidades de punto de guardado y reversión
    - Coordinación de la publicación de eventos de dominio
    """
    
    def __init__(self):
        self._batch_operations: List[BatchOperation] = []
        self._aggregates_with_events: Set[AggregateRoot] = set()
        self._repositories: Dict[str, Any] = {}
        self._is_committed = False
        self._is_rolled_back = False
        self._savepoints: List['Savepoint'] = []
        self._transaction_id = str(uuid.uuid4())
        self._session_key = f"uow_{self._transaction_id}"
        
        # Compatibilidad con serialización para la sesión Flask (del tutorial)
        self._serialized_state: Optional[bytes] = None
        
    @property
    def transaction_id(self) -> str:
        return self._transaction_id
    
    @property
    def is_committed(self) -> bool:
        return self._is_committed
    
    @property
    def is_rolled_back(self) -> bool:
        return self._is_rolled_back
    
    @property
    def is_active(self) -> bool:
        return not (self._is_committed or self._is_rolled_back)
    
    def register_repository(self, name: str, repository: Any) -> None:
        self._repositories[name] = repository
    
    def get_repository(self, name: str) -> Any:
        return self._repositories.get(name)
    
    def register_new(self, entity: AggregateRoot, repository_name: str = None) -> None:
        """
        Registrar nueva entidad para su inserción.
        
        Argumentos:
            entity: Entidad a insertar.
            repository_name: Nombre del repositorio a utilizar.
        """
        self._validate_active_transaction()
        
        repo_name = repository_name or self._get_repository_name(entity)
        operation = BatchOperation(
            operation_id=str(uuid.uuid4()),
            operation_type=OperationType.INSERT,
            entity=entity,
            repository_name=repo_name
        )
        
        self._batch_operations.append(operation)
        self._track_entity_events(entity)
        self._serialize_to_session()
    
    def register_updated(self, entity: AggregateRoot, repository_name: str = None) -> None:
        """
        Registrar entidad para actualización.
        
        Argumentos:
            entity: Entidad que se va a actualizar.
            repository_name: Nombre del repositorio que se va a utilizar.
        """
        self._validate_active_transaction()
        
        repo_name = repository_name or self._get_repository_name(entity)
        operation = BatchOperation(
            operation_id=str(uuid.uuid4()),
            operation_type=OperationType.UPDATE,
            entity=entity,
            repository_name=repo_name
        )
        
        self._batch_operations.append(operation)
        self._track_entity_events(entity)
        self._serialize_to_session()
    
    def register_deleted(self, entity: AggregateRoot, repository_name: str = None) -> None:
        """
        Registrar entidad para su eliminación.
        
        Argumentos:
            entity: Entidad que se va a eliminar.
            repository_name: Nombre del repositorio que se va a utilizar.
        """
        self._validate_active_transaction()
        
        repo_name = repository_name or self._get_repository_name(entity)
        operation = BatchOperation(
            operation_id=str(uuid.uuid4()),
            operation_type=OperationType.DELETE,
            entity=entity,
            repository_name=repo_name
        )
        
        self._batch_operations.append(operation)
        self._track_entity_events(entity)
        self._serialize_to_session()
    
    def create_savepoint(self, name: Optional[str] = None) -> 'Savepoint':
        """
        Crear punto de guardado para reversión parcial.
        
        Argumentos:
            nombre: nombre opcional del punto de guardado
            
        Devuelve:
            Punto de guardado creado
        """
        self._validate_active_transaction()
        
        savepoint_name = name or f"sp_{len(self._savepoints)}"
        savepoint = Savepoint(
            name=savepoint_name,
            operations_count=len(self._batch_operations),
            aggregates_snapshot=self._aggregates_with_events.copy()
        )
        
        self._savepoints.append(savepoint)
        return savepoint
    
    def rollback_to_savepoint(self, savepoint: 'Savepoint') -> None:
        """
        Rollback a un punto de guardado específico.
        
        Argumentos:
            savepoint: Punto de guardado al que retroceder.
        """
        self._validate_active_transaction()
        
        if savepoint not in self._savepoints:
            raise DomainException(
                message="No se ha encontrado el punto de guardado en la transacción actual.",
                error_code="SAVEPOINT_NOT_FOUND"
            )
        
        # Eliminar operaciones después del punto de guardado
        self._batch_operations = self._batch_operations[:savepoint.operations_count]
        
        # Restaurar estado de agregados
        self._aggregates_with_events = savepoint.aggregates_snapshot.copy()
        
        # Eliminar puntos de guardado después de este
        savepoint_index = self._savepoints.index(savepoint)
        self._savepoints = self._savepoints[:savepoint_index + 1]
        
        self._serialize_to_session()
    
    def commit(self) -> None:
        """
        Confirmar la transacción y ejecutar todas las operaciones por lotes.
        Los eventos de dominio se publican tras la confirmación satisfactoria.
        """
        if self._is_committed:
            raise DomainException(
                message="Transacción ya confirmada",
                error_code="TRANSACTION_ALREADY_COMMITTED"
            )
        
        if self._is_rolled_back:
            raise DomainException(
                message="No se puede confirmar la transacción revertida.",
                error_code="TRANSACTION_ROLLED_BACK"
            )
        
        try:
            # Ejecutar todas las operaciones por lotes
            self._execute_batch_operations()
            
            # Confirmar transacción subyacente
            self._commit_transaction()
            
            # Marcar como comprometido
            self._is_committed = True
            
            # Borrar estado de sesión
            self._clear_session_state()
            
        except Exception as e:
            self.rollback()
            raise DomainException(
                message=f"Transaction commit failed: {str(e)}",
                error_code="TRANSACTION_COMMIT_FAILED"
            ) from e
    
    def rollback(self) -> None:
        """
        Revierte la transacción y descarta todas las operaciones.
        """
        if self._is_rolled_back:
            return
        
        try:
            self._rollback_transaction()
            
        finally:
            self._is_rolled_back = True
            
            self._batch_operations.clear()
            self._aggregates_with_events.clear()
            self._savepoints.clear()
            
            self._clear_session_state()
    
    def get_aggregates_with_events(self) -> List[AggregateRoot]:
        return list(self._aggregates_with_events)
    
    def get_pending_operations(self) -> List[BatchOperation]:
        return self._batch_operations.copy()
    
    def get_operations_count(self) -> int:
        return len(self._batch_operations)
    
    def serialize_to_session(self) -> None:
        """
        Serializa el estado UoW a la sesión Flask utilizando pickle (del tutorial).
        Permite la persistencia del estado entre solicitudes HTTP.
        """
        self._serialize_to_session()
    
    def restore_from_session(self) -> bool:
        """
        Restaurar el estado UoW desde la sesión Flask utilizando pickle (del tutorial).
        
        Devuelve:
            True si se ha restaurado el estado, False si no se ha encontrado ningún estado.
        """
        return self._restore_from_session()
    
    def _serialize_to_session(self) -> None:
        try:
            state = {
                'transaction_id': self._transaction_id,
                'batch_operations': self._batch_operations,
                'aggregates_with_events': list(self._aggregates_with_events),
                'is_committed': self._is_committed,
                'is_rolled_back': self._is_rolled_back,
                'savepoints': self._savepoints
            }
            
            self._serialized_state = pickle.dumps(state)
            
            if session is not None:
                session[self._session_key] = self._serialized_state
                
        except Exception as e:
            import logging
            logging.warning(f"Failed to serialize UoW state to session: {str(e)}")
    
    def _restore_from_session(self) -> bool:
        """Método interno para restaurar el estado desde la sesión."""
        try:
            if session is None or self._session_key not in session:
                return False
            
            serialized_data = session[self._session_key]
            if not serialized_data:
                return False
            
            state = pickle.loads(serialized_data)
            
            self._transaction_id = state['transaction_id']
            self._batch_operations = state['batch_operations']
            self._aggregates_with_events = set(state['aggregates_with_events'])
            self._is_committed = state['is_committed']
            self._is_rolled_back = state['is_rolled_back']
            self._savepoints = state['savepoints']
            
            return True
            
        except Exception as e:
            import logging
            logging.warning(f"Failed to restore UoW state from session: {str(e)}")
            return False
    
    def _clear_session_state(self) -> None:
        if session is not None and self._session_key in session:
            del session[self._session_key]
        self._serialized_state = None
    
    def _execute_batch_operations(self) -> None:
        for operation in self._batch_operations:
            repository = self._repositories.get(operation.repository_name)
            if not repository:
                raise DomainException(
                    message=f"Repository not found: {operation.repository_name}",
                    error_code="REPOSITORY_NOT_FOUND"
                )
            
            try:
                if operation.operation_type == OperationType.INSERT:
                    repository.agregar(operation.entity)
                elif operation.operation_type == OperationType.UPDATE:
                    repository.actualizar(operation.entity)
                elif operation.operation_type == OperationType.DELETE:
                    repository.eliminar(operation.entity.id)
                else:
                    raise DomainException(
                        message=f"Unknown operation type: {operation.operation_type}",
                        error_code="UNKNOWN_OPERATION_TYPE"
                    )
                    
            except Exception as e:
                raise DomainException(
                    message=f"Batch operation failed: {operation.operation_type} on {operation.repository_name}",
                    error_code="BATCH_OPERATION_FAILED"
                ) from e
    
    def _track_entity_events(self, entity: AggregateRoot) -> None:
        if hasattr(entity, 'has_events') and entity.has_events:
            self._aggregates_with_events.add(entity)
    
    def _get_repository_name(self, entity: AggregateRoot) -> str:
        return f"{entity.__class__.__name__}Repository"
    
    def _validate_active_transaction(self) -> None:
        if self._is_committed:
            raise DomainException(
                message="No se pueden registrar operaciones en transacciones confirmadas.",
                error_code="TRANSACTION_ALREADY_COMMITTED"
            )
        
        if self._is_rolled_back:
            raise DomainException(
                message="No se pueden registrar operaciones en transacciones revertidas.",
                error_code="TRANSACTION_ROLLED_BACK"
            )
    
    @abstractmethod
    def _commit_transaction(self) -> None:
        pass
    
    @abstractmethod
    def _rollback_transaction(self) -> None:
        pass


@dataclass
class Savepoint:
    name: str
    operations_count: int
    aggregates_snapshot: Set[AggregateRoot]
    timestamp: float = field(default_factory=lambda: __import__('time').time())


class SqlAlchemyUnitOfWork(UnitOfWork):
    """
    Implementación de la unidad de trabajo específica de SQLAlchemy.
    
    Se integra con la sesión de SQLAlchemy para las transacciones de la base de datos.
    """
    
    def __init__(self, session_factory: Callable = None):
        super().__init__()
        self._session_factory = session_factory
        self._session = None
        
        if self._session_factory:
            self._session = self._session_factory()
    
    def set_session(self, session: Any) -> None:
        self._session = session
    
    def get_session(self) -> Any:
        return self._session
    
    def _commit_transaction(self) -> None:
        if self._session:
            self._session.commit()
    
    def _rollback_transaction(self) -> None:
        if self._session:
            self._session.rollback()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.rollback()
        else:
            if self.is_active:
                self.commit()


class InMemoryUnitOfWork(UnitOfWork):
    """
    Unidad de trabajo en memoria para pruebas.
    
    Simula el comportamiento de las transacciones sin persistencia real.
    """
    
    def __init__(self):
        super().__init__()
        self._committed_operations: List[BatchOperation] = []
    
    def get_committed_operations(self) -> List[BatchOperation]:
        return self._committed_operations.copy()
    
    def _commit_transaction(self) -> None:
        self._committed_operations.extend(self._batch_operations)
    
    def _rollback_transaction(self) -> None:
        pass


class UnitOfWorkFactory:
    def __init__(self, default_type: str = "sqlalchemy"):
        self._default_type = default_type
        self._session_factory = None
    
    def set_session_factory(self, factory: Callable) -> None:
        self._session_factory = factory
    
    def create(self, uow_type: Optional[str] = None) -> UnitOfWork:
        uow_type = uow_type or self._default_type
        
        if uow_type == "sqlalchemy":
            return SqlAlchemyUnitOfWork(self._session_factory)
        elif uow_type == "inmemory":
            return InMemoryUnitOfWork()
        else:
            raise DomainException(
                message=f"Unknown UoW type: {uow_type}",
                error_code="UNKNOWN_UOW_TYPE"
            )


# Context manager for simplified UoW usage
@contextmanager
def unit_of_work(uow: UnitOfWork):
    """
    Gestor de contexto para la unidad de trabajo.
    
    Confirma automáticamente en caso de éxito o revierte en caso de excepción.
    """
    try:
        yield uow
        if uow.is_active:
            uow.commit()
    except Exception:
        if uow.is_active:
            uow.rollback()
        raise
