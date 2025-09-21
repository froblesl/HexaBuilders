from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import logging
from datetime import datetime
import uuid

from src.onboarding.seedwork.aplicacion.comandos import CommandBus
from src.onboarding.seedwork.aplicacion.queries import QueryBus
from src.onboarding.saga_integration import OnboardingSagaIntegration
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../..'))
from src.pulsar_event_dispatcher import PulsarEventDispatcher


def crear_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'onboarding-dev-secret')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://hexauser:hexapass123@localhost:5432/onboarding')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['CORS_ORIGINS'] = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')
    
    # CORS
    CORS(app, origins=app.config['CORS_ORIGINS'])
    
    # Logging
    setup_logging()
    
    # Initialize command and query buses
    command_bus = CommandBus()
    query_bus = QueryBus()
    
    # Store buses in app context
    app.command_bus = command_bus
    app.query_bus = query_bus
    
    # Register blueprints
    from src.onboarding.api.contracts import contracts_bp
    from src.onboarding.api.contracts_query import contracts_query_bp
    from src.onboarding.api.negotiations import negotiations_bp
    from src.onboarding.api.legal import legal_bp
    from src.onboarding.api.documents import documents_bp
    
    app.register_blueprint(contracts_bp, url_prefix='/contracts')
    app.register_blueprint(contracts_query_bp, url_prefix='/contracts-query')
    app.register_blueprint(negotiations_bp, url_prefix='/negotiations')
    app.register_blueprint(legal_bp, url_prefix='/legal')
    app.register_blueprint(documents_bp, url_prefix='/documents')
    
    # Initialize saga integration
    event_dispatcher = PulsarEventDispatcher("onboarding")
    onboarding_saga = OnboardingSagaIntegration(event_dispatcher)
    
    # Add saga integration endpoints
    add_saga_endpoints(app, onboarding_saga)
    
    # Health check endpoints
    @app.route('/health')
    def health():
        return jsonify({
            'status': 'healthy',
            'service': 'onboarding',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.0'
        }), 200
    
    @app.route('/health/ready')
    def ready():
        # Check database connection
        try:
            # TODO: Add actual database check
            return jsonify({
                'status': 'ready',
                'checks': {
                    'database': 'ok',
                    'event_store': 'ok'
                }
            }), 200
        except Exception as e:
            return jsonify({
                'status': 'not ready',
                'error': str(e)
            }), 503
    
    @app.route('/health/live')
    def live():
        return jsonify({
            'status': 'alive',
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    
    # Error handlers
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'error': 'Bad Request',
            'message': 'Invalid request data',
            'timestamp': datetime.utcnow().isoformat()
        }), 400
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'error': 'Not Found',
            'message': 'Resource not found',
            'timestamp': datetime.utcnow().isoformat()
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred',
            'timestamp': datetime.utcnow().isoformat()
        }), 500
    
    # Request/Response middleware
    @app.before_request
    def before_request():
        # Add correlation ID
        if not hasattr(request, 'correlation_id'):
            request.correlation_id = str(uuid.uuid4())
        
        # Log request
        app.logger.info(f"Request: {request.method} {request.path}", extra={
            'correlation_id': request.correlation_id,
            'user_agent': request.headers.get('User-Agent'),
            'remote_addr': request.remote_addr
        })
    
    @app.after_request
    def after_request(response):
        # Add correlation ID to response
        response.headers['X-Correlation-ID'] = getattr(request, 'correlation_id', '')
        
        # Log response
        app.logger.info(f"Response: {response.status_code}", extra={
            'correlation_id': getattr(request, 'correlation_id', ''),
            'status_code': response.status_code
        })
        
        return response
    
    return app


def setup_logging():
    """Configure structured logging"""
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Add custom filter for correlation ID
    class CorrelationIDFilter(logging.Filter):
        def filter(self, record):
            record.correlation_id = getattr(record, 'correlation_id', 'N/A')
            return True
    
    logging.getLogger().addFilter(CorrelationIDFilter())


def add_saga_endpoints(app, onboarding_saga):
    """Agregar endpoints de integración de saga"""
    
    @app.route('/saga/partner-onboarding', methods=['POST'])
    def handle_saga_partner_onboarding():
        """Endpoint para manejar eventos de saga de onboarding de partners"""
        try:
            data = request.get_json()
            
            # Crear evento de onboarding iniciado
            event_data = {
                'partner_id': data['partner_id'],
                'partner_data': data['partner_data'],
                'correlation_id': data.get('correlation_id', str(uuid.uuid4())),
                'causation_id': data.get('causation_id', str(uuid.uuid4()))
            }
            
            # Procesar el evento
            result = onboarding_saga.handle_partner_onboarding_initiated(event_data)
            
            return jsonify({
                'status': 'success',
                'message': 'Partner onboarding processed by Onboarding service',
                'partner_id': data['partner_id'],
                'result': result,
                'timestamp': datetime.utcnow().isoformat()
            }), 200
            
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'Error processing partner onboarding: {str(e)}',
                'timestamp': datetime.utcnow().isoformat()
            }), 500


if __name__ == '__main__':
    app = crear_app()
    port = int(os.environ.get('SERVICE_PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)