from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TypeVar, Generic
from dataclasses import dataclass, field
import time
import logging

from .comandos import CommandHandler, CommandResult
from .queries import QueryHandler, QueryResult


T = TypeVar('T')


@dataclass
class HandlerContext:
    """Contexto para ejecución de handler."""
    
    handler_name: str
    correlation_id: str
    user_id: Optional[str] = None
    tenant_id: Optional[str] = None
    start_time: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def elapsed_time_ms(self) -> float:
        """Obtener tiempo transcurrido en milisegundos."""
        return (time.time() - self.start_time) * 1000
    
    def add_metadata(self, key: str, value: Any) -> None:
        """Agregar metadatos al contexto."""
        self.metadata[key] = value


class Handler(ABC):
    """
    Clase base de handler con funcionalidad común.
    
    Proporciona:
    - Manejo de errores y logging
    - Monitoreo de rendimiento básico
    """
    
    def __init__(self, name: Optional[str] = None):
        self._name = name or self.__class__.__name__
        self._logger = self._get_logger()
    
    @property
    def name(self) -> str:
        """Obtener nombre del handler."""
        return self._name
    
    def _create_context(self, request: Any) -> HandlerContext:
        """Crear contexto de ejecución."""
        correlation_id = getattr(request, 'correlation_id', 'unknown')
        user_id = getattr(request, 'user_id', None)
        tenant_id = getattr(request, 'tenant_id', None)
        
        return HandlerContext(
            handler_name=self._name,
            correlation_id=correlation_id,
            user_id=user_id,
            tenant_id=tenant_id
        )
    
    def _get_logger(self):
        """Obtener instancia del logger."""
        return logging.getLogger(f"{__name__}.{self.__class__.__name__}")


class BaseCommandHandler(Handler, CommandHandler, Generic[T]):
    """Handler base de comando simplificado."""
    
    def __init__(self, name: Optional[str] = None):
        super().__init__(name)
    
    async def handle(self, command) -> CommandResult:
        """Manejar comando."""
        context = self._create_context(command)
        
        try:
            result = await self._execute_command(command, context)
            return result
        except Exception as e:
            self._logger.error(f"Error handling command {type(command).__name__}: {str(e)}")
            return CommandResult(
                success=False,
                message=f"Error executing command: {str(e)}",
                errors={"execution": str(e)}
            )
    
    @abstractmethod
    async def _execute_command(self, command, context: HandlerContext) -> CommandResult:
        """Ejecutar la lógica real del comando."""
        pass


class BaseQueryHandler(Handler, QueryHandler, Generic[T]):
    """Handler base de consulta simplificado."""
    
    def __init__(self, name: Optional[str] = None):
        super().__init__(name)
    
    async def handle(self, query) -> Any:
        """Manejar consulta."""
        context = self._create_context(query)
        
        try:
            result = await self._execute_query(query, context)
            return result
        except Exception as e:
            self._logger.error(f"Error handling query {type(query).__name__}: {str(e)}")
            raise
    
    @abstractmethod
    async def _execute_query(self, query, context: HandlerContext) -> Any:
        """Ejecutar la lógica real de la consulta."""
        pass
