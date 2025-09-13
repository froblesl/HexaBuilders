"""
Queries module.
"""

from .obtener_job import ObtenerJob, RespuestaObtenerJob
from .obtener_todos_jobs import ObtenerTodosJobs, RespuestaObtenerTodosJobs

__all__ = [
    'ObtenerJob',
    'RespuestaObtenerJob',
    'ObtenerTodosJobs',
    'RespuestaObtenerTodosJobs',
]
