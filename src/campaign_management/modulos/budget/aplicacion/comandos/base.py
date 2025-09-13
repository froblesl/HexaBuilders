"""
Base classes for budget commands.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from campaign_management.seedwork.aplicacion.comandos import Command
from campaign_management.seedwork.infraestructura.uow import UnitOfWork

logger = logging.getLogger(__name__)


@dataclass
class CommandBudget(Command):
    """Base command for budget operations."""
    pass


class ComandoHandlerBudget(ABC):
    """Base command handler for budget operations."""
    
    def __init__(self, uow: UnitOfWork):
        self._uow = uow
        self._logger = logger
    
    @abstractmethod
    def handle(self, comando: CommandBudget) -> Any:
        """Handle the command."""
        pass
    
    def _log_command_start(self, comando: CommandBudget):
        """Log command execution start."""
        self._logger.info(f"Starting command execution: {comando.__class__.__name__}")
    
    def _log_command_success(self, comando: CommandBudget, result: Any = None):
        """Log successful command execution."""
        self._logger.info(f"Command executed successfully: {comando.__class__.__name__}")
    
    def _log_command_error(self, comando: CommandBudget, error: Exception):
        """Log command execution error."""
        self._logger.error(f"Command execution failed: {comando.__class__.__name__} - {str(error)}")
