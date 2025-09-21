#!/usr/bin/env python3
"""
Script de inicio para el BFF Web con GraphQL.
"""

import os
import sys
import uvicorn
from pathlib import Path

# Agregar el directorio src al path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Configurar variables de entorno
os.environ.setdefault("PYTHONPATH", str(src_path))
os.environ.setdefault("SAGA_SERVICE_URL", "http://localhost:5000")
os.environ.setdefault("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001")
os.environ.setdefault("LOG_LEVEL", "INFO")
os.environ.setdefault("DEBUG", "false")

if __name__ == "__main__":
    print("🚀 Starting HexaBuilders BFF Web...")
    print("📊 GraphQL endpoint: http://localhost:8000/api/v1/graphql")
    print("🔍 Health check: http://localhost:8000/health")
    print("📖 Schema: http://localhost:8000/api/v1/schema")
    print("=" * 50)
    
    uvicorn.run(
        "bff_web.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
