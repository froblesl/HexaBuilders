"""
Base classes for contract commands.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from onboarding.seedwork.aplicacion.comandos import Command
from onboarding.seedwork.infraestructura.uow import UnitOfWork

logger = logging.getLogger(__name__)


@dataclass
class CommandContract(Command):
    """Base command for contract operations."""
    pass


class ComandoHandlerContract(ABC):
    """Base command handler for contract operations."""
    
    def __init__(self, uow: UnitOfWork):
        self._uow = uow
        self._logger = logger
    
    @abstractmethod
    def handle(self, comando: CommandContract) -> Any:
        """Handle the command."""
        pass
    
    def _log_command_start(self, comando: CommandContract):
        """Log command execution start."""
        self._logger.info(f"Starting command execution: {comando.__class__.__name__}")
    
    def _log_command_success(self, comando: CommandContract, result: Any = None):
        """Log successful command execution."""
        self._logger.info(f"Command executed successfully: {comando.__class__.__name__}")
    
    def _log_command_error(self, comando: CommandContract, error: Exception):
        """Log command execution error."""
        self._logger.error(f"Command execution failed: {comando.__class__.__name__} - {str(error)}")