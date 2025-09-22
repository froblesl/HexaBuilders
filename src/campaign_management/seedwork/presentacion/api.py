from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import logging
from datetime import datetime
import uuid

# Importar integración de saga
from src.campaign_management.saga_integration import create_campaign_saga_integration

# Importar control de estado del servicio
from src.campaign_management.service_state import get_service_state, set_service_state


def crear_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'campaign-dev-secret')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://hexauser:hexapass123@localhost:5432/campaign_management')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['CORS_ORIGINS'] = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')
    
    # CORS
    CORS(app, origins=app.config['CORS_ORIGINS'])
    
    # Logging
    setup_logging()
    
    # Register blueprints
    from src.campaign_management.api.campaigns import campaigns_bp
    from src.campaign_management.api.campaigns_query import campaigns_query_bp
    from src.campaign_management.api.performance import performance_bp
    from src.campaign_management.api.budget import budget_bp
    from src.campaign_management.api.targeting import targeting_bp
    
    app.register_blueprint(campaigns_bp, url_prefix='/campaigns')
    app.register_blueprint(campaigns_query_bp, url_prefix='/campaigns-query')
    app.register_blueprint(performance_bp, url_prefix='/performance')
    app.register_blueprint(budget_bp, url_prefix='/budget')
    app.register_blueprint(targeting_bp, url_prefix='/targeting')
    
    # Inicializar integración de saga
    try:
        logging.info("Attempting to initialize Campaign Management saga integration...")
        saga_integration = create_campaign_saga_integration()
        if saga_integration:
            logging.info("Campaign Management saga integration initialized successfully")
        else:
            logging.warning("Failed to initialize Campaign Management saga integration")
    except Exception as e:
        logging.error(f"Error initializing Campaign Management saga integration: {str(e)}")
        import traceback
        logging.error(f"Traceback: {traceback.format_exc()}")
    
    # Health check endpoints
    @app.route('/health')
    def health():
        return jsonify({
            'status': 'healthy',
            'service': 'campaign-management',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.0'
        }), 200
    
    @app.route('/health/ready')
    def ready():
        try:
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
        if not hasattr(request, 'correlation_id'):
            request.correlation_id = str(uuid.uuid4())
        
        app.logger.info(f"Request: {request.method} {request.path}", extra={
            'correlation_id': request.correlation_id,
            'user_agent': request.headers.get('User-Agent'),
            'remote_addr': request.remote_addr
        })
    
    @app.after_request
    def after_request(response):
        response.headers['X-Correlation-ID'] = getattr(request, 'correlation_id', '')
        
        app.logger.info(f"Response: {response.status_code}", extra={
            'correlation_id': getattr(request, 'correlation_id', ''),
            'status_code': response.status_code
        })
        
        return response
    
    # Add service control endpoints
    add_service_control_endpoints(app)
    
    return app


def setup_logging():
    """Configure structured logging"""
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    class CorrelationIDFilter(logging.Filter):
        def filter(self, record):
            record.correlation_id = getattr(record, 'correlation_id', 'N/A')
            return True
    
    logging.getLogger().addFilter(CorrelationIDFilter())


def add_service_control_endpoints(app):
    """Agrega endpoints para controlar el estado del servicio"""
    
    @app.route('/api/v1/service/status', methods=['GET'])
    def get_service_status():
        """Obtiene el estado actual del servicio"""
        enabled = get_service_state()
        return jsonify({
            "service": "campaign-management",
            "enabled": enabled,
            "status": "enabled" if enabled else "disabled",
            "timestamp": datetime.utcnow().isoformat()
        })
    
    @app.route('/api/v1/service/disable', methods=['POST'])
    def disable_service():
        """Deshabilita el servicio para pruebas de compensación"""
        set_service_state(False)
        
        logging.info("Campaign Management service DISABLED for compensation testing")
        
        return jsonify({
            "message": "Campaign Management service disabled successfully",
            "service": "campaign-management",
            "enabled": False,
            "status": "disabled",
            "timestamp": datetime.utcnow().isoformat()
        })
    
    @app.route('/api/v1/service/enable', methods=['POST'])
    def enable_service():
        """Habilita el servicio"""
        set_service_state(True)
        
        logging.info("Campaign Management service ENABLED")
        
        return jsonify({
            "message": "Campaign Management service enabled successfully",
            "service": "campaign-management",
            "enabled": True,
            "status": "enabled",
            "timestamp": datetime.utcnow().isoformat()
        })
    
    @app.route('/api/v1/service/toggle', methods=['POST'])
    def toggle_service():
        """Alterna el estado del servicio"""
        current_state = get_service_state()
        new_state = not current_state
        set_service_state(new_state)
        
        status = "enabled" if new_state else "disabled"
        logging.info(f"Campaign Management service TOGGLED to {status}")
        
        return jsonify({
            "message": f"Campaign Management service {status} successfully",
            "service": "campaign-management",
            "enabled": new_state,
            "status": status,
            "timestamp": datetime.utcnow().isoformat()
        })


if __name__ == '__main__':
    app = crear_app()
    port = int(os.environ.get('SERVICE_PORT', 5003))
    app.run(host='0.0.0.0', port=port, debug=True)