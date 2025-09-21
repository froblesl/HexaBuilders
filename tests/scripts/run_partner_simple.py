#!/usr/bin/env python3
"""
Punto de entrada simplificado para Partner Management Service
"""
import sys
import os
from flask import Flask, jsonify
from flask_cors import CORS

# Agregar el directorio src al PYTHONPATH
src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
sys.path.insert(0, src_path)

def create_simple_app():
    """Crear aplicación Flask simplificada"""
    app = Flask(__name__)
    
    # Configurar CORS
    CORS(app, origins=['http://localhost:3000'])
    
    # Endpoint de salud básico
    @app.route('/health', methods=['GET'])
    def health():
        return jsonify({
            'status': 'healthy',
            'service': 'partner-management',
            'version': '1.0.0',
            'timestamp': '2025-09-12T22:46:00Z'
        })
    
    # Endpoint básico de partners
    @app.route('/partners', methods=['GET'])
    def get_partners():
        return jsonify({
            'message': 'Partner Management Service está funcionando',
            'service': 'partner-management',
            'available_endpoints': [
                'GET /health',
                'GET /partners',
                'POST /partners',
                'GET /partners/<id>',
                'PUT /partners/<id>'
            ]
        })
    
    @app.route('/partners', methods=['POST'])
    def create_partner():
        return jsonify({
            'message': 'Partner creation endpoint - Implementation in progress',
            'status': 'success'
        }), 201
    
    return app

def main():
    """Función principal"""
    print("🚀 Iniciando Partner Management Service (Modo Simple)...")
    
    app = create_simple_app()
    
    print("📊 Partner Management Service configurado")
    print("🌐 Corriendo en http://localhost:5001")
    print("🔗 Health check: http://localhost:5001/health")
    
    app.run(
        host='0.0.0.0',
        port=5001,
        debug=True,
        use_reloader=False
    )

if __name__ == '__main__':
    main()