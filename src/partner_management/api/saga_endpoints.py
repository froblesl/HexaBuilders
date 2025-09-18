"""
Endpoints para manejo de Sagas de transacciones largas usando Choreography Pattern.
Proporciona APIs para iniciar, monitorear y gestionar Sagas basadas en eventos.
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
import logging
from uuid import uuid4

from ..modulos.partners.aplicacion.saga_choreography import (
    ChoreographySagaOrchestrator, 
    SagaStateRepository
)
from ..seedwork.infraestructura.utils import EventDispatcher

saga_bp = Blueprint('sagas', __name__)
logger = logging.getLogger(__name__)

# Inicializar componentes de Saga de Choreography
event_dispatcher = EventDispatcher()
saga_state_repository = SagaStateRepository(event_dispatcher)  # Usar EventDispatcher como storage

# Crear orquestador de Saga de Choreography
choreography_saga = ChoreographySagaOrchestrator(
    event_dispatcher=event_dispatcher,
    saga_state_repository=saga_state_repository
)


@saga_bp.route('/partner-onboarding', methods=['POST'])
async def start_partner_onboarding():
    """
    Inicia el onboarding de un partner usando Saga de Choreografía.
    
    Body:
    {
        "partner_data": {
            "partner_id": "optional-uuid",
            "nombre": "TechSolutions Inc",
            "email": "contact@techsolutions.com",
            "telefono": "+1234567890",
            "tipo_partner": "EMPRESA",
            "preferred_contract_type": "PREMIUM",
            "required_documents": ["IDENTITY", "BUSINESS_REGISTRATION"],
            "campaign_permissions": {...},
            "recruitment_preferences": {...}
        },
        "correlation_id": "optional-correlation-id"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'partner_data' not in data:
            return jsonify({
                'error': 'Missing required field: partner_data',
                'timestamp': datetime.utcnow().isoformat()
            }), 400
        
        partner_data = data['partner_data']
        correlation_id = data.get('correlation_id', str(uuid4()))
        
        # Validar datos requeridos
        required_fields = ['nombre', 'email', 'telefono', 'tipo_partner']
        for field in required_fields:
            if field not in partner_data:
                return jsonify({
                    'error': f'Missing required field in partner_data: {field}',
                    'timestamp': datetime.utcnow().isoformat()
                }), 400
        
        # Agregar partner_id si no existe
        if 'partner_id' not in partner_data:
            partner_data['partner_id'] = str(uuid4())
        
        # Iniciar Saga de Choreografía
        partner_id = await choreography_saga.start_partner_onboarding(
            partner_data=partner_data,
            correlation_id=correlation_id
        )
        
        return jsonify({
            'partner_id': partner_id,
            'saga_type': 'partner_onboarding',
            'pattern': 'choreography',
            'status': 'initiated',
            'message': 'Partner onboarding saga initiated successfully',
            'timestamp': datetime.utcnow().isoformat()
        }), 202
        
    except Exception as e:
        logger.error("Error starting partner onboarding: %s", str(e))
        return jsonify({
            'error': 'Internal server error',
            'message': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500


@saga_bp.route('/<partner_id>/status', methods=['GET'])
async def get_saga_status(partner_id):
    """
    Obtiene el estado actual de una Saga de Choreografía.
    """
    try:
        # Obtener estado de Saga de Choreografía
        saga_state = await saga_state_repository.get(partner_id)
        
        if not saga_state:
            return jsonify({
                'error': 'Saga not found',
                'timestamp': datetime.utcnow().isoformat()
            }), 404
        
        return jsonify({
            'partner_id': saga_state['partner_id'],
            'saga_type': 'partner_onboarding',
            'status': saga_state['status'].value,
            'completed_steps': saga_state['completed_steps'],
            'failed_steps': saga_state['failed_steps'],
            'created_at': saga_state['created_at'],
            'updated_at': saga_state['updated_at'],
            'correlation_id': saga_state['correlation_id']
        }), 200
        
    except Exception as e:
        logger.error("Error getting saga status: %s", str(e))
        return jsonify({
            'error': 'Internal server error',
            'message': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500


@saga_bp.route('/<partner_id>/compensate', methods=['POST'])
async def compensate_saga(partner_id):
    """
    Inicia la compensación de una Saga de Choreografía.
    
    Body:
    {
        "reason": "Manual compensation request"
    }
    """
    try:
        data = request.get_json() or {}
        reason = data.get('reason', 'Manual compensation request')
        
        # Compensar Saga de Choreografía
        saga_state = await saga_state_repository.get(partner_id)
        
        if not saga_state:
            return jsonify({
                'error': 'Saga not found',
                'timestamp': datetime.utcnow().isoformat()
            }), 404
        
        # Iniciar compensación
        failed_step = saga_state.get('failed_steps', [])[-1] if saga_state.get('failed_steps') else 'unknown'
        correlation_id = saga_state.get('correlation_id')
        
        # Llamar al método de compensación (acceso directo para simplicidad)
        await choreography_saga._initiate_compensation(partner_id, failed_step, correlation_id)
        
        return jsonify({
            'partner_id': partner_id,
            'status': 'compensating',
            'reason': reason,
            'message': 'Saga compensation initiated',
            'timestamp': datetime.utcnow().isoformat()
        }), 202
        
    except Exception as e:
        logger.error("Error compensating saga: %s", str(e))
        return jsonify({
            'error': 'Internal server error',
            'message': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500


@saga_bp.route('/health', methods=['GET'])
def saga_health_check():
    """Health check para el servicio de Sagas de Choreography"""
    try:
        health_status = {
            'service': 'saga-choreography-management',
            'status': 'healthy',
            'pattern': 'choreography',
            'saga_types': ['partner_onboarding'],
            'event_dispatcher': 'active',
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return jsonify(health_status), 200
        
    except Exception as e:
        logger.error("Saga health check failed: %s", str(e))
        return jsonify({
            'service': 'saga-choreography-management',
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 503
