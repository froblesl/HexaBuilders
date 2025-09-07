import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from functools import singledispatch
from typing import Any, Dict, Optional, TypeVar, Generic, List, Union
from enum import Enum

from ..dominio.eventos import EventMetadata
from ..dominio.excepciones import DomainException, ValidationException


class CommandStatus(Enum):
    PENDING = "pending"
    EXECUTING = "executing" 
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class CommandPriority(Enum):
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


@dataclass(frozen=True)
class CommandContext:    
    command_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    causation_id: Optional[str] = None
    user_id: Optional[str] = None
    tenant_id: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    source_system: Optional[str] = None
    trace_id: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def with_causation(self, causation_id: str) -> 'CommandContext':
        return CommandContext(
            command_id=str(uuid.uuid4()),
            correlation_id=self.correlation_id,
            causation_id=causation_id,
            user_id=self.user_id,
            tenant_id=self.tenant_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            source_system=self.source_system,
            trace_id=self.trace_id,
            session_id=self.session_id,
            metadata=self.metadata
        )


@dataclass
class Command:
    context: CommandContext = field(default_factory=CommandContext)
    priority: CommandPriority = CommandPriority.NORMAL
    
    def __post_init__(self):
        self.validate()
    
    def validate(self) -> None:
        pass
    
    @property
    def command_id(self) -> str:
        return self.context.command_id
    
    @property
    def correlation_id(self) -> str:
        return self.context.correlation_id
    
    @property
    def user_id(self) -> Optional[str]:
        return self.context.user_id
    
    @property
    def timestamp(self) -> str:
        return self.context.timestamp
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'command_type': self.__class__.__name__,
            'command_id': self.command_id,
            'correlation_id': self.correlation_id,
            'context': {
                'user_id': self.context.user_id,
                'tenant_id': self.context.tenant_id,
                'timestamp': self.context.timestamp,
                'source_system': self.context.source_system,
                'trace_id': self.context.trace_id,
                'session_id': self.context.session_id,
                'metadata': self.context.metadata
            },
            'priority': self.priority.name,
            'data': self._get_command_data()
        }
    
    def _get_command_data(self) -> Dict[str, Any]:
        data = {}
        for key, value in self.__dict__.items():
            if key not in ['context', 'priority']:
                data[key] = value
        return data

T = TypeVar('T')


@dataclass
class CommandResult(Generic[T]):
    success: bool
    command_id: str
    correlation_id: str
    result: Optional[T] = None
    error: Optional[str] = None
    error_code: Optional[str] = None
    execution_time_ms: Optional[float] = None
    events_generated: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def success_result(
        cls, 
        command: Command, 
        result: Optional[T] = None,
        execution_time_ms: Optional[float] = None,
        events_generated: int = 0
    ) -> 'CommandResult[T]':
        return cls(
            success=True,
            command_id=command.command_id,
            correlation_id=command.correlation_id,
            result=result,
            execution_time_ms=execution_time_ms,
            events_generated=events_generated
        )
    
    @classmethod
    def failure_result(
        cls,
        command: Command,
        error: str,
        error_code: Optional[str] = None,
        execution_time_ms: Optional[float] = None
    ) -> 'CommandResult[T]':
        return cls(
            success=False,
            command_id=command.command_id,
            correlation_id=command.correlation_id,
            error=error,
            error_code=error_code,
            execution_time_ms=execution_time_ms
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'success': self.success,
            'command_id': self.command_id,
            'correlation_id': self.correlation_id,
            'result': self.result,
            'error': self.error,
            'error_code': self.error_code,
            'execution_time_ms': self.execution_time_ms,
            'events_generated': self.events_generated,
            'metadata': self.metadata
        }


class CommandHandler(ABC, Generic[T]):
    @abstractmethod
    def handle(self, command: Command) -> CommandResult[T]:
        pass
    
    def can_handle(self, command: Command) -> bool:
        return True
    
    def get_supported_command_types(self) -> List[type]:
        return []


class AsyncCommandHandler(CommandHandler[T], ABC):
    @abstractmethod
    async def handle_async(self, command: Command) -> CommandResult[T]:
        pass
    
    def handle(self, command: Command) -> CommandResult[T]:
        import asyncio
        return asyncio.run(self.handle_async(command))


# SingleDispatch decorator for command routing (from tutorial)
@singledispatch
def ejecutar_comando(comando: Command) -> CommandResult[Any]:
    raise DomainException(
        message=f"No handler registered for command type: {type(comando).__name__}",
        error_code="NO_COMMAND_HANDLER"
    )


class CommandBus:
    def __init__(self):
        self._handlers: Dict[type, CommandHandler] = {}
        self._middleware: List['CommandMiddleware'] = []
        self._metrics: Dict[str, Any] = {}
    
    def register_handler(self, command_type: type, handler: CommandHandler) -> None:
        self._handlers[command_type] = handler
        
        ejecutar_comando.register(command_type, handler.handle)
    
    def add_middleware(self, middleware: 'CommandMiddleware') -> None:
        self._middleware.append(middleware)
    
    def dispatch(self, command: Command) -> CommandResult[Any]:
        import time
        start_time = time.time()
        
        try:
            # Find handler
            handler = self._find_handler(command)
            
            # Execute middleware pipeline
            result = self._execute_with_middleware(command, handler)
            
            # Record metrics
            execution_time = (time.time() - start_time) * 1000
            self._record_metrics(command, result, execution_time)
            
            return result
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            
            error_result = CommandResult.failure_result(
                command=command,
                error=str(e),
                error_code=getattr(e, 'error_code', 'COMMAND_EXECUTION_ERROR'),
                execution_time_ms=execution_time
            )
            
            self._record_metrics(command, error_result, execution_time)
            return error_result
    
    def _find_handler(self, command: Command) -> CommandHandler:
        command_type = type(command)
        
        if command_type in self._handlers:
            return self._handlers[command_type]
        
        for handler in self._handlers.values():
            if handler.can_handle(command):
                return handler
        
        raise DomainException(
            message=f"No handler found for command: {command_type.__name__}",
            error_code="NO_COMMAND_HANDLER"
        )
    
    def _execute_with_middleware(self, command: Command, handler: CommandHandler) -> CommandResult[Any]:
        if not self._middleware:
            return handler.handle(command)
        
        # Build middleware chain
        def execute_handler(cmd: Command) -> CommandResult[Any]:
            return handler.handle(cmd)
        
        # Apply middleware in reverse order
        for middleware in reversed(self._middleware):
            next_handler = execute_handler
            execute_handler = lambda cmd, mw=middleware, next_h=next_handler: mw.handle(cmd, next_h)
        
        return execute_handler(command)
    
    def _record_metrics(self, command: Command, result: CommandResult, execution_time: float) -> None:
        command_type = type(command).__name__
        
        if command_type not in self._metrics:
            self._metrics[command_type] = {
                'total_executions': 0,
                'successful_executions': 0,
                'failed_executions': 0,
                'total_execution_time': 0,
                'avg_execution_time': 0
            }
        
        metrics = self._metrics[command_type]
        metrics['total_executions'] += 1
        metrics['total_execution_time'] += execution_time
        
        if result.success:
            metrics['successful_executions'] += 1
        else:
            metrics['failed_executions'] += 1
        
        metrics['avg_execution_time'] = metrics['total_execution_time'] / metrics['total_executions']
    
    def get_metrics(self) -> Dict[str, Any]:
        return self._metrics.copy()
    
    def clear_metrics(self) -> None:
        self._metrics.clear()


class CommandMiddleware(ABC):
    @abstractmethod
    def handle(self, command: Command, next_handler: callable) -> CommandResult[Any]:
        pass


class ValidationMiddleware(CommandMiddleware):
    def handle(self, command: Command, next_handler: callable) -> CommandResult[Any]:
        try:
            command.validate()
            return next_handler(command)
        except ValidationException as e:
            return CommandResult.failure_result(
                command=command,
                error=str(e),
                error_code="COMMAND_VALIDATION_FAILED"
            )


class LoggingMiddleware(CommandMiddleware):
    def __init__(self, logger=None):
        self._logger = logger or self._get_default_logger()
    
    def handle(self, command: Command, next_handler: callable) -> CommandResult[Any]:
        command_type = type(command).__name__
        
        self._logger.info(f"Executing command: {command_type} ({command.command_id})")
        
        result = next_handler(command)
        
        if result.success:
            self._logger.info(f"Command completed successfully: {command_type} ({command.command_id})")
        else:
            self._logger.error(f"Command failed: {command_type} ({command.command_id}) - {result.error}")
        
        return result
    
    def _get_default_logger(self):
        import logging
        return logging.getLogger(__name__)


# Command validation decorators
def validate_required_fields(*field_names: str):
    def decorator(command_class):
        original_validate = getattr(command_class, 'validate', lambda self: None)
        
        def validate(self):
            original_validate(self)
            
            missing_fields = []
            for field_name in field_names:
                if not hasattr(self, field_name) or getattr(self, field_name) is None:
                    missing_fields.append(field_name)
            
            if missing_fields:
                raise ValidationException(
                    message=f"Required fields missing: {', '.join(missing_fields)}",
                    field_errors={field: ["Field is required"] for field in missing_fields}
                )
        
        command_class.validate = validate
        return command_class
    
    return decorator


def validate_field_format(field_name: str, pattern: str, message: str = None):
    def decorator(command_class):
        import re
        original_validate = getattr(command_class, 'validate', lambda self: None)
        
        def validate(self):
            original_validate(self)
            
            if hasattr(self, field_name):
                value = getattr(self, field_name)
                if value and not re.match(pattern, str(value)):
                    error_msg = message or f"Field '{field_name}' has invalid format"
                    raise ValidationException(
                        message=error_msg,
                        field_errors={field_name: [error_msg]}
                    )
        
        command_class.validate = validate
        return command_class
    
    return decorator
