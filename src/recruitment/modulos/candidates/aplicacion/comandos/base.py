"""
Base classes for candidate commands.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from recruitment.seedwork.aplicacion.comandos import Command
from recruitment.seedwork.infraestructura.uow import UnitOfWork

logger = logging.getLogger(__name__)


@dataclass
class CommandCandidate(Command):
    """Base command for candidate operations."""
    pass


class ComandoHandlerCandidate(ABC):
    """Base command handler for candidate operations."""
    
    def __init__(self, uow: UnitOfWork):
        self._uow = uow
        self._logger = logger
    
    @abstractmethod
    def handle(self, comando: CommandCandidate) -> Any:
        """Handle the command."""
        pass
    
    def _log_command_start(self, comando: CommandCandidate):
        """Log command execution start."""
        self._logger.info(f"Starting command execution: {comando.__class__.__name__}")
    
    def _log_command_success(self, comando: CommandCandidate, result: Any = None):
        """Log successful command execution."""
        self._logger.info(f"Command executed successfully: {comando.__class__.__name__}")
    
    def _log_command_error(self, comando: CommandCandidate, error: Exception):
        """Log command execution error."""
        self._logger.error(f"Command execution failed: {comando.__class__.__name__} - {str(error)}")