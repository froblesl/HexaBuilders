"""
Base classes for document commands.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from src.onboarding.seedwork.aplicacion.comandos import Command
from src.onboarding.seedwork.infraestructura.uow import UnitOfWork

logger = logging.getLogger(__name__)


@dataclass
class CommandDocument(Command):
    """Base command for document operations."""
    pass


class ComandoHandlerDocument(ABC):
    """Base command handler for document operations."""
    
    def __init__(self, uow: UnitOfWork):
        self._uow = uow
        self._logger = logger
    
    @abstractmethod
    def handle(self, comando: CommandDocument) -> Any:
        """Handle the command."""
        pass
    
    def _log_command_start(self, comando: CommandDocument):
        """Log command execution start."""
        self._logger.info(f"Starting command execution: {comando.__class__.__name__}")
    
    def _log_command_success(self, comando: CommandDocument, result: Any = None):
        """Log successful command execution."""
        self._logger.info(f"Command executed successfully: {comando.__class__.__name__}")
    
    def _log_command_error(self, comando: CommandDocument, error: Exception):
        """Log command execution error."""
        self._logger.error(f"Command execution failed: {comando.__class__.__name__} - {str(error)}")