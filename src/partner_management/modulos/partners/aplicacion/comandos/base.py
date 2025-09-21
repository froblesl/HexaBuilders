"""
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from src.partner_management.seedwork.aplicacion.comandos import Command
from src.partner_management.seedwork.infraestructura.uow import UnitOfWork

logger = logging.getLogger(__name__)


@dataclass
class CommandPartner(Command):
    """Base command for partner operations."""
    pass


class ComandoHandlerPartner(ABC):
    """Base command handler for partner operations."""
    
    def __init__(self, uow: UnitOfWork):
        self._uow = uow
        self._logger = logger
    
    @abstractmethod
    def handle(self, comando: CommandPartner) -> Any:
        """Handle the command."""
        pass
    
    def _log_command_start(self, comando: CommandPartner):
        """Log command execution start."""
        self._logger.info(f"Starting command execution: {comando.__class__.__name__}")
    
    def _log_command_success(self, comando: CommandPartner, result: Any = None):
        """Log successful command execution."""
        self._logger.info(f"Command executed successfully: {comando.__class__.__name__}")
    
    def _log_command_error(self, comando: CommandPartner, error: Exception):
        """Log command execution error."""
        self._logger.error(f"Command execution failed: {comando.__class__.__name__} - {str(error)}")