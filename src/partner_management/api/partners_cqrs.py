"""
Separates commands (write operations) from queries (read operations).
"""

import logging
from flask import Blueprint, request, jsonify, Response
from datetime import datetime

from src.partner_management.seedwork.aplicacion.comandos import ejecutar_comando
from src.partner_management.seedwork.aplicacion.queries import ejecutar_query
from src.partner_management.seedwork.dominio.excepciones import DomainException
from src.partner_management.modulos.partners.aplicacion.comandos.crear_partner import CrearPartner
from src.partner_management.modulos.partners.aplicacion.comandos.actualizar_partner import ActualizarPartner
from src.partner_management.modulos.partners.aplicacion.comandos.activar_partner import ActivarPartner
from src.partner_management.modulos.partners.aplicacion.comandos.desactivar_partner import DesactivarPartner
from src.partner_management.modulos.partners.aplicacion.queries.obtener_partner import ObtenerPartner
from src.partner_management.modulos.partners.aplicacion.queries.obtener_todos_partners import ObtenerTodosPartners
from src.partner_management.modulos.partners.aplicacion.queries.obtener_profile_360 import ObtenerProfile360

logger = logging.getLogger(__name__)

# Create Blueprint
bp = Blueprint('partners_cqrs', __name__, url_prefix='/api/v1')


# ============================================================================
# COMMAND ENDPOINTS (WRITE OPERATIONS) - Async, return HTTP 202
# ============================================================================

@bp.route('/partners-comando', methods=['POST'])
def crear_partner_comando():
    """
    Create partner command endpoint.
    """
    try:
        logger.info("Processing CreatePartner command")
        
        # Validate request
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['nombre', 'email', 'telefono', 'tipo_partner']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Create command
        comando = CrearPartner(
            nombre=data['nombre'],
            email=data['email'],
            telefono=data['telefono'],
            tipo_partner=data['tipo_partner'],
            direccion=data.get('direccion'),
            ciudad=data.get('ciudad'),
            pais=data.get('pais')
        )
        
        # Execute command asynchronously
        partner_id = ejecutar_comando(comando)
        
        # Return immediately with 202 (Accepted)
        logger.info(f"CreatePartner command accepted for processing: {partner_id}")
        return Response(
            '{}', 
            status=202,
            mimetype='application/json',
            headers={'Location': f'/api/v1/partners-query/{partner_id}'}
        )
    
    except DomainException as e:
        logger.warning(f"CreatePartner command validation error: {str(e)}")
        return jsonify({'error': str(e)}), 400
    
    except Exception as e:
        logger.error(f"CreatePartner command error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@bp.route('/partners-comando/<string:partner_id>', methods=['PUT'])
def actualizar_partner_comando(partner_id):
    """
    Update partner command endpoint.
    """
    try:
        logger.info(f"Processing UpdatePartner command for: {partner_id}")
        
        # Validate request
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        
        data = request.get_json()
        
        # Create command
        comando = ActualizarPartner(
            partner_id=partner_id,
            nombre=data.get('nombre'),
            email=data.get('email'),
            telefono=data.get('telefono'),
            direccion=data.get('direccion'),
            ciudad=data.get('ciudad'),
            pais=data.get('pais')
        )
        
        # Execute command asynchronously
        result_partner_id = ejecutar_comando(comando)
        
        # Return immediately with 202 (Accepted)
        logger.info(f"UpdatePartner command accepted for processing: {result_partner_id}")
        return Response(
            '{}',
            status=202,
            mimetype='application/json',
            headers={'Location': f'/api/v1/partners-query/{result_partner_id}'}
        )
    
    except DomainException as e:
        logger.warning(f"UpdatePartner command validation error: {str(e)}")
        return jsonify({'error': str(e)}), 400
    
    except Exception as e:
        logger.error(f"UpdatePartner command error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@bp.route('/partners-comando/<string:partner_id>/activar', methods=['PUT'])
def activar_partner_comando(partner_id):
    """
    Activate partner command endpoint.
    """
    try:
        logger.info(f"Processing ActivatePartner command for: {partner_id}")
        
        data = request.get_json() if request.is_json else {}
        
        # Create command
        comando = ActivarPartner(
            partner_id=partner_id,
            activado_por=data.get('activado_por'),
            razon_activacion=data.get('razon_activacion')
        )
        
        # Execute command asynchronously
        result_partner_id = ejecutar_comando(comando)
        
        # Return immediately with 202 (Accepted)
        logger.info(f"ActivatePartner command accepted for processing: {result_partner_id}")
        return Response(
            '{}',
            status=202,
            mimetype='application/json',
            headers={'Location': f'/api/v1/partners-query/{result_partner_id}'}
        )
    
    except DomainException as e:
        logger.warning(f"ActivatePartner command validation error: {str(e)}")
        return jsonify({'error': str(e)}), 400
    
    except Exception as e:
        logger.error(f"ActivatePartner command error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@bp.route('/partners-comando/<string:partner_id>/desactivar', methods=['PUT'])
def desactivar_partner_comando(partner_id):
    """
    Deactivate partner command endpoint.
    """
    try:
        logger.info(f"Processing DeactivatePartner command for: {partner_id}")
        
        data = request.get_json() if request.is_json else {}
        
        # Create command
        comando = DesactivarPartner(
            partner_id=partner_id,
            desactivado_por=data.get('desactivado_por'),
            razon_desactivacion=data.get('razon_desactivacion')
        )
        
        # Execute command asynchronously
        result_partner_id = ejecutar_comando(comando)
        
        # Return immediately with 202 (Accepted)
        logger.info(f"DeactivatePartner command accepted for processing: {result_partner_id}")
        return Response(
            '{}',
            status=202,
            mimetype='application/json',
            headers={'Location': f'/api/v1/partners-query/{result_partner_id}'}
        )
    
    except DomainException as e:
        logger.warning(f"DeactivatePartner command validation error: {str(e)}")
        return jsonify({'error': str(e)}), 400
    
    except Exception as e:
        logger.error(f"DeactivatePartner command error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


# ============================================================================
# QUERY ENDPOINTS (READ OPERATIONS) - Sync, return HTTP 200 with data
# ============================================================================

@bp.route('/partners-query/<string:partner_id>', methods=['GET'])
def obtener_partner_query(partner_id):
    """
    Get partner query endpoint.
    """
    try:
        logger.info(f"Processing GetPartner query for: {partner_id}")
        
        # Create query
        query = ObtenerPartner(partner_id=partner_id)
        
        # Execute query synchronously
        resultado = ejecutar_query(query)
        
        # Return data immediately with 200 (OK)
        if resultado.partner:
            response_data = resultado.partner.to_dict()
            logger.info(f"GetPartner query completed successfully: {partner_id}")
            return jsonify(response_data), 200
        else:
            logger.warning(f"Partner not found: {partner_id}")
            return jsonify({'error': 'Partner not found'}), 404
    
    except Exception as e:
        logger.error(f"GetPartner query error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@bp.route('/partners-query', methods=['GET'])
def obtener_todos_partners_query():
    """
    Get all partners query endpoint with filtering and pagination.
    """
    try:
        logger.info("Processing GetAllPartners query")
        
        # Extract query parameters
        status = request.args.get('status')
        tipo = request.args.get('tipo')
        ciudad = request.args.get('ciudad')
        pais = request.args.get('pais')
        
        # Pagination parameters
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', type=int, default=0)
        
        # Validate limit
        if limit is not None and limit > 100:
            limit = 100  # Max 100 items per page
        
        # Create query
        query = ObtenerTodosPartners(
            status=status,
            tipo=tipo,
            ciudad=ciudad,
            pais=pais,
            limit=limit,
            offset=offset
        )
        
        # Execute query synchronously
        resultado = ejecutar_query(query)
        
        # Prepare response with pagination info
        response_data = {
            'partners': [partner.to_dict() for partner in resultado.partners],
            'pagination': {
                'total': resultado.total,
                'limit': resultado.limit,
                'offset': resultado.offset,
                'has_next': resultado.offset + len(resultado.partners) < resultado.total if resultado.limit else False
            }
        }
        
        logger.info(f"GetAllPartners query completed: {len(resultado.partners)} partners returned")
        return jsonify(response_data), 200
    
    except Exception as e:
        logger.error(f"GetAllPartners query error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@bp.route('/partners-query/<string:partner_id>/profile-360', methods=['GET'])
def obtener_profile_360_query(partner_id):
    """
    Get partner 360 profile query endpoint.
    """
    try:
        logger.info(f"Processing GetProfile360 query for: {partner_id}")
        
        # Create query
        query = ObtenerProfile360(partner_id=partner_id)
        
        # Execute query synchronously
        resultado = ejecutar_query(query)
        
        # Return comprehensive data immediately with 200 (OK)
        if resultado.profile:
            response_data = resultado.profile.to_dict()
            logger.info(f"GetProfile360 query completed successfully: {partner_id}")
            return jsonify(response_data), 200
        else:
            logger.warning(f"Partner profile not found: {partner_id}")
            return jsonify({'error': 'Partner profile not found'}), 404
    
    except Exception as e:
        logger.error(f"GetProfile360 query error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


# ============================================================================
# HEALTH CHECK ENDPOINTS
# ============================================================================

@bp.route('/partners-health', methods=['GET'])
def health_check():
    """Health check endpoint for partners CQRS API."""
    try:
        # Basic health check
        health_data = {
            'service': 'partner-management-cqrs',
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0',
            'endpoints': {
                'commands': {
                    'create_partner': '/api/v1/partners-comando [POST]',
                    'update_partner': '/api/v1/partners-comando/{id} [PUT]',
                    'activate_partner': '/api/v1/partners-comando/{id}/activar [PUT]',
                    'deactivate_partner': '/api/v1/partners-comando/{id}/desactivar [PUT]'
                },
                'queries': {
                    'get_partner': '/api/v1/partners-query/{id} [GET]',
                    'get_all_partners': '/api/v1/partners-query [GET]',
                    'get_profile_360': '/api/v1/partners-query/{id}/profile-360 [GET]'
                }
            }
        }
        
        return jsonify(health_data), 200
    
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return jsonify({
            'service': 'partner-management-cqrs',
            'status': 'unhealthy',
            'error': str(e)
        }), 503


@bp.route('/partners-info', methods=['GET'])
def api_info():
    """API information endpoint."""
    info_data = {
        'name': 'Partner Management CQRS API',
        'version': '1.0.0',
        'architecture': 'CQRS + Event Sourcing + Hexagonal Architecture',
        'patterns': [
            'Command Query Responsibility Segregation (CQRS)',
            'Domain-Driven Design (DDD)',
            'Event-Driven Architecture',
            'Single Dispatch Pattern',
            'Unit of Work Pattern'
        ],
        'endpoints_summary': {
            'commands': 4,
            'queries': 3,
            'utility': 2
        },
        'documentation': '/api/v1/partners-health'
    }
    
    return jsonify(info_data), 200


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@bp.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Endpoint not found'}), 404


@bp.errorhandler(405)
def method_not_allowed_error(error):
    """Handle 405 errors."""
    return jsonify({'error': 'Method not allowed'}), 405


@bp.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500


# Register blueprint with Flask app (this would be done in the main app file)
def register_partners_cqrs_blueprint(app):
    """Register the partners CQRS blueprint with Flask app."""
    app.register_blueprint(bp)
    logger.info("Partners CQRS blueprint registered successfully")