from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import logging
from datetime import datetime
import uuid

# Importar integración de saga
from src.recruitment.saga_integration import create_recruitment_saga_integration


def crear_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'recruitment-dev-secret')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://hexauser:hexapass123@localhost:5432/recruitment')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['ELASTICSEARCH_URL'] = os.getenv('ELASTICSEARCH_URL', 'http://localhost:9200')
    app.config['CORS_ORIGINS'] = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')
    
    # CORS
    CORS(app, origins=app.config['CORS_ORIGINS'])
    
    # Logging
    setup_logging()
    
    # Register blueprints
    from src.recruitment.api.candidates import candidates_bp
    from src.recruitment.api.jobs import jobs_bp
    from src.recruitment.api.applications import applications_bp
    from src.recruitment.api.search import search_bp
    from src.recruitment.api.matching import matching_bp
    
    app.register_blueprint(candidates_bp, url_prefix='/candidates')
    app.register_blueprint(jobs_bp, url_prefix='/jobs')
    app.register_blueprint(applications_bp, url_prefix='/applications')
    app.register_blueprint(search_bp, url_prefix='/search')
    app.register_blueprint(matching_bp, url_prefix='/matching')
    
    # Inicializar integración de saga
    try:
        logging.info("Attempting to initialize Recruitment saga integration...")
        saga_integration = create_recruitment_saga_integration()
        if saga_integration:
            logging.info("Recruitment saga integration initialized successfully")
        else:
            logging.warning("Failed to initialize Recruitment saga integration")
    except Exception as e:
        logging.error(f"Error initializing Recruitment saga integration: {str(e)}")
        import traceback
        logging.error(f"Traceback: {traceback.format_exc()}")
    
    # Health check endpoints
    @app.route('/health')
    def health():
        return jsonify({
            'status': 'healthy',
            'service': 'recruitment',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.0'
        }), 200
    
    @app.route('/health/ready')
    def ready():
        try:
            # TODO: Add actual database and elasticsearch checks
            return jsonify({
                'status': 'ready',
                'checks': {
                    'database': 'ok',
                    'elasticsearch': 'ok'
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


if __name__ == '__main__':
    app = crear_app()
    port = int(os.environ.get('SERVICE_PORT', 5002))
    app.run(host='0.0.0.0', port=port, debug=True)