"""
Base classes for campaign commands in HexaBuilders.
"""

from abc import ABC
from dataclasses import dataclass

from partner_management.seedwork.aplicacion.comandos import Command, ComandoHandler


@dataclass
class ComandoCampaign(Comando, ABC):
    """Base class for all campaign commands."""
    pass


class ComandoCampaignHandler(ComandoHandler, ABC):
    """Base class for all campaign command handlers."""
    pass