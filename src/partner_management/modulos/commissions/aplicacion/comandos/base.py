"""
Base classes for commission commands in HexaBuilders.
"""

from abc import ABC
from dataclasses import dataclass

from .....seedwork.aplicacion.comandos import Comando, ComandoHandler


@dataclass
class ComandoCommission(Comando, ABC):
    """Base class for all commission commands."""
    pass


class ComandoCommissionHandler(ComandoHandler, ABC):
    """Base class for all commission command handlers."""
    pass