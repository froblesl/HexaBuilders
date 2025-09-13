#!/usr/bin/env python3
"""
Script para ejecutar todos los microservicios HexaBuilders
"""
import sys
import os
from flask import Flask, jsonify
from flask_cors import CORS

# Agregar el directorio src al PYTHONPATH
src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
sys.path.insert(0, src_path)

def create_service_app(service_name, port):
    """Crear aplicación Flask para un microservicio"""
    app = Flask(service_name)
    
    # Configurar CORS
    CORS(app, origins=['http://localhost:3000'])
    
    # Endpoint de salud
    @app.route('/health', methods=['GET'])
    def health():
        return jsonify({
            'status': 'healthy',
            'service': service_name,
            'version': '1.0.0',
            'port': port,
            'timestamp': '2025-09-12T22:47:00Z'
        })
    
    # Endpoints específicos por servicio
    if service_name == 'partner-management':
        @app.route('/partners', methods=['GET', 'POST'])
        def partners():
            return jsonify({
                'service': 'partner-management',
                'message': 'Partners endpoints funcionando',
                'port': port
            })
        
        @app.route('/partners/<partner_id>/profile360', methods=['GET'])
        def profile_360(partner_id):
            return jsonify({
                'service': 'partner-management',
                'partner_id': partner_id,
                'profile_360': 'datos simulados',
                'port': port
            })
    
    elif service_name == 'onboarding':
        @app.route('/contracts', methods=['GET', 'POST'])
        def contracts():
            return jsonify({
                'service': 'onboarding',
                'message': 'Contracts endpoints funcionando',
                'port': port
            })
        
        @app.route('/documents', methods=['GET', 'POST'])
        def documents():
            return jsonify({
                'service': 'onboarding',
                'message': 'Documents endpoints funcionando',
                'port': port
            })
    
    elif service_name == 'recruitment':
        @app.route('/candidates', methods=['GET', 'POST'])
        def candidates():
            return jsonify({
                'service': 'recruitment',
                'message': 'Candidates endpoints funcionando',
                'port': port
            })
        
        @app.route('/jobs', methods=['GET', 'POST'])
        def jobs():
            return jsonify({
                'service': 'recruitment',
                'message': 'Jobs endpoints funcionando',
                'port': port
            })
    
    elif service_name == 'campaign-management':
        @app.route('/campaigns', methods=['GET', 'POST'])
        def campaigns():
            return jsonify({
                'service': 'campaign-management',
                'message': 'Campaigns endpoints funcionando',
                'port': port
            })
        
        @app.route('/budget', methods=['GET'])
        def budget():
            return jsonify({
                'service': 'campaign-management',
                'message': 'Budget endpoints funcionando',
                'port': port
            })
    
    return app

def run_service(service_name, port):
    """Ejecutar un microservicio en un puerto específico"""
    print(f"🚀 Iniciando {service_name} en puerto {port}...")
    
    app = create_service_app(service_name, port)
    
    print(f"📊 {service_name} configurado")
    print(f"🌐 Corriendo en http://localhost:{port}")
    print(f"🔗 Health check: http://localhost:{port}/health")
    
    try:
        app.run(
            host='0.0.0.0',
            port=port,
            debug=False,
            use_reloader=False
        )
    except Exception as e:
        print(f"❌ Error ejecutando {service_name}: {e}")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) != 2:
        print("Uso: python run_services.py <service_name>")
        print("Services: partner-management, onboarding, recruitment, campaign-management")
        sys.exit(1)
    
    service_name = sys.argv[1]
    
    service_ports = {
        'partner-management': 9000,
        'onboarding': 9001,
        'recruitment': 9002,
        'campaign-management': 9003
    }
    
    if service_name not in service_ports:
        print(f"❌ Servicio desconocido: {service_name}")
        print("Services disponibles:", list(service_ports.keys()))
        sys.exit(1)
    
    run_service(service_name, service_ports[service_name])