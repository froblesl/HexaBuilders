#!/usr/bin/env python3
"""
Punto de entrada para ejecutar Partner Management Service
"""
import sys
import os

# Agregar el directorio src al PYTHONPATH
src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
sys.path.insert(0, src_path)

from partner_management.seedwork.presentacion.api import create_app, register_cqrs_blueprints, register_health_endpoints

def main():
    """Función principal para ejecutar el servicio"""
    print("🚀 Iniciando Partner Management Service...")
    
    # Crear aplicación Flask
    app = create_app({
        'DEBUG': True,
        'HOST': '0.0.0.0',
        'PORT': 5000
    })
    
    # Registrar blueprints y endpoints
    register_cqrs_blueprints(app)
    register_health_endpoints(app)
    
    print("📊 Partner Management Service configurado correctamente")
    print("🌐 Corriendo en http://localhost:5000")
    print("🔗 Health check: http://localhost:5000/health")
    print("📋 API endpoints disponibles:")
    print("  - POST /partners - Crear partner")
    print("  - GET /partners/<id> - Obtener partner") 
    print("  - PUT /partners/<id> - Actualizar partner")
    print("  - GET /partners/<id>/profile360 - Perfil 360")
    
    # Ejecutar aplicación
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        use_reloader=False  # Evitar problemas con múltiples procesos
    )

if __name__ == '__main__':
    main()