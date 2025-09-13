"""
Queries module for contract management.
"""

from .obtener_contract import ObtenerContract, RespuestaObtenerContract
from .obtener_todos_contracts import ObtenerTodosContracts, RespuestaObtenerTodosContracts

__all__ = [
    'ObtenerContract',
    'RespuestaObtenerContract',
    'ObtenerTodosContracts', 
    'RespuestaObtenerTodosContracts',
]