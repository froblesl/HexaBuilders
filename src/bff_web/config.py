"""
Configuración para el BFF Web.
"""

import os
from typing import List


class Settings:
    """Configuración de la aplicación"""
    
    # Configuración de la aplicación
    APP_NAME: str = "HexaBuilders BFF Web"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Configuración del servidor
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Configuración de CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",  # React dev server
        "http://localhost:3001",  # Next.js dev server
        "http://localhost:8080",  # Vue dev server
        "http://localhost:4200",  # Angular dev server
    ]
    
    # Configuración de servicios
    SAGA_SERVICE_URL: str = os.getenv("SAGA_SERVICE_URL", "http://localhost:5000")
    SAGA_SERVICE_TIMEOUT: int = int(os.getenv("SAGA_SERVICE_TIMEOUT", "30"))
    
    # Configuración de logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Configuración de GraphQL
    GRAPHQL_PATH: str = "/api/v1/graphql"
    GRAPHQL_PLAYGROUND: bool = os.getenv("GRAPHQL_PLAYGROUND", "true").lower() == "true"
    
    # Configuración de health checks
    HEALTH_CHECK_INTERVAL: int = int(os.getenv("HEALTH_CHECK_INTERVAL", "30"))


# Instancia global de configuración
settings = Settings()
