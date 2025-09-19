"""
Aplicación principal del BFF Web usando FastAPI y Strawberry GraphQL.
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter
from contextlib import asynccontextmanager

from .schema import schema
from .resolvers import saga_resolvers

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manejo del ciclo de vida de la aplicación"""
    logger.info("Starting BFF Web service...")
    yield
    logger.info("Shutting down BFF Web service...")


# Crear aplicación FastAPI
app = FastAPI(
    title="HexaBuilders BFF Web",
    description="Backend for Frontend para Web usando GraphQL",
    version="1.0.0",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Crear router GraphQL
graphql_app = GraphQLRouter(schema, path="/graphql")

# Incluir router GraphQL
app.include_router(graphql_app, prefix="/api/v1")

# Endpoints adicionales
@app.get("/")
async def root():
    """Endpoint raíz"""
    return {
        "service": "HexaBuilders BFF Web",
        "version": "1.0.0",
        "graphql_endpoint": "/api/v1/graphql",
        "health_endpoint": "/health"
    }

@app.get("/health")
async def health_check():
    """Health check del BFF"""
    try:
        # Verificar salud del servicio de Saga
        health_status = await saga_resolvers.get_health_status()
        
        return {
            "service": "bff-web",
            "status": "healthy" if health_status.status == "healthy" else "degraded",
            "dependencies": {
                "saga_service": health_status.status,
                "event_dispatcher": health_status.event_dispatcher
            },
            "timestamp": health_status.timestamp.isoformat()
        }
    except Exception as e:
        logger.error("Health check failed: %s", str(e))
        return {
            "service": "bff-web",
            "status": "unhealthy",
            "error": str(e),
            "timestamp": "2024-01-01T00:00:00Z"
        }

@app.get("/api/v1/schema")
async def get_schema():
    """Obtiene el schema GraphQL en formato SDL"""
    return {"schema": str(schema)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
