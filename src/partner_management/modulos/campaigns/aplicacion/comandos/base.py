"""
Base classes for campaign commands in HexaBuilders.
"""

from abc import ABC
from dataclasses import dataclass

from .....seedwork.aplicacion.comandos import Comando, ComandoHandler


@dataclass
class ComandoCampaign(Comando, ABC):
    """Base class for all campaign commands."""
    pass


class ComandoCampaignHandler(ComandoHandler, ABC):
    """Base class for all campaign command handlers."""
    pass