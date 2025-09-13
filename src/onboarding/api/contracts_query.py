from flask import Blueprint, request, jsonify, current_app
from datetime import datetime

from onboarding.seedwork.aplicacion.queries import (
    GetContract,
    GetContractsByPartner,
    SearchContracts,
    GetContractHistory,
    GetContractTemplates,
    GetContractTemplate,
    GetContractsDashboard,
    GetContractsMetrics
)

contracts_query_bp = Blueprint('contracts_query', __name__)


@contracts_query_bp.route('/<contract_id>', methods=['GET'])
async def get_contract(contract_id):
    """Get contract by ID"""
    try:
        query = GetContract(
            contract_id=contract_id,
            user_id=request.headers.get('X-User-ID', 'anonymous')
        )
        
        result = await current_app.query_bus.execute(query)
        
        if result.success:
            return jsonify({
                'contract': result.data,
                'timestamp': datetime.utcnow().isoformat()
            }), 200
        else:
            return jsonify({
                'error': result.message,
                'timestamp': datetime.utcnow().isoformat()
            }), 404 if 'not found' in result.message.lower() else 400
            
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'message': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500


@contracts_query_bp.route('', methods=['GET'])
async def search_contracts():
    """Search contracts with filters"""
    try:
        # Get query parameters
        filters = {}
        
        partner_id = request.args.get('partner_id')
        if partner_id:
            filters['partner_id'] = partner_id
        
        state = request.args.get('state')
        if state:
            filters['state'] = state
        
        contract_type = request.args.get('contract_type')
        if contract_type:
            filters['contract_type'] = contract_type
        
        created_from = request.args.get('created_from')
        if created_from:
            filters['created_from'] = datetime.fromisoformat(created_from)
        
        created_to = request.args.get('created_to')
        if created_to:
            filters['created_to'] = datetime.fromisoformat(created_to)
        
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        sort_by = request.args.get('sort_by', 'created_at')
        sort_order = request.args.get('sort_order', 'desc')
        
        query = SearchContracts(
            filters=filters,
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            sort_order=sort_order,
            user_id=request.headers.get('X-User-ID', 'anonymous')
        )
        
        result = await current_app.query_bus.execute(query)
        
        if result.success:
            return jsonify({
                'contracts': result.data.get('contracts', []),
                'total': result.data.get('total', 0),
                'page': page,
                'page_size': page_size,
                'timestamp': datetime.utcnow().isoformat()
            }), 200
        else:
            return jsonify({
                'error': result.message,
                'timestamp': datetime.utcnow().isoformat()
            }), 400
            
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'message': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500


@contracts_query_bp.route('/partner/<partner_id>', methods=['GET'])
async def get_contracts_by_partner(partner_id):
    """Get all contracts for a partner"""
    try:
        include_inactive = request.args.get('include_inactive', 'false').lower() == 'true'
        
        query = GetContractsByPartner(
            partner_id=partner_id,
            include_inactive=include_inactive,
            user_id=request.headers.get('X-User-ID', 'anonymous')
        )
        
        result = await current_app.query_bus.execute(query)
        
        if result.success:
            return jsonify({
                'partner_id': partner_id,
                'contracts': result.data.get('contracts', []),
                'timestamp': datetime.utcnow().isoformat()
            }), 200
        else:
            return jsonify({
                'error': result.message,
                'timestamp': datetime.utcnow().isoformat()
            }), 400
            
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'message': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500


@contracts_query_bp.route('/<contract_id>/history', methods=['GET'])
async def get_contract_history(contract_id):
    """Get contract event history"""
    try:
        query = GetContractHistory(
            contract_id=contract_id,
            user_id=request.headers.get('X-User-ID', 'anonymous')
        )
        
        result = await current_app.query_bus.execute(query)
        
        if result.success:
            return jsonify({
                'contract_id': contract_id,
                'history': result.data,
                'timestamp': datetime.utcnow().isoformat()
            }), 200
        else:
            return jsonify({
                'error': result.message,
                'timestamp': datetime.utcnow().isoformat()
            }), 404 if 'not found' in result.message.lower() else 400
            
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'message': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500


@contracts_query_bp.route('/templates', methods=['GET'])
async def get_contract_templates():
    """Get contract templates"""
    try:
        contract_type = request.args.get('contract_type')
        
        if contract_type:
            query = GetContractTemplates(
                contract_type=contract_type,
                user_id=request.headers.get('X-User-ID', 'anonymous')
            )
        else:
            query = GetContractTemplates(
                user_id=request.headers.get('X-User-ID', 'anonymous')
            )
        
        result = await current_app.query_bus.execute(query)
        
        if result.success:
            return jsonify({
                'templates': result.data,
                'timestamp': datetime.utcnow().isoformat()
            }), 200
        else:
            return jsonify({
                'error': result.message,
                'timestamp': datetime.utcnow().isoformat()
            }), 400
            
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'message': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500


@contracts_query_bp.route('/templates/<template_id>', methods=['GET'])
async def get_contract_template(template_id):
    """Get contract template by ID"""
    try:
        query = GetContractTemplate(
            template_id=template_id,
            user_id=request.headers.get('X-User-ID', 'anonymous')
        )
        
        result = await current_app.query_bus.execute(query)
        
        if result.success:
            return jsonify({
                'template': result.data,
                'timestamp': datetime.utcnow().isoformat()
            }), 200
        else:
            return jsonify({
                'error': result.message,
                'timestamp': datetime.utcnow().isoformat()
            }), 404 if 'not found' in result.message.lower() else 400
            
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'message': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500


@contracts_query_bp.route('/dashboard', methods=['GET'])
async def get_contracts_dashboard():
    """Get contracts dashboard data"""
    try:
        partner_id = request.args.get('partner_id')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        query = GetContractsDashboard(
            partner_id=partner_id,
            date_from=datetime.fromisoformat(date_from) if date_from else None,
            date_to=datetime.fromisoformat(date_to) if date_to else None,
            user_id=request.headers.get('X-User-ID', 'anonymous')
        )
        
        result = await current_app.query_bus.execute(query)
        
        if result.success:
            return jsonify({
                'dashboard': result.data,
                'timestamp': datetime.utcnow().isoformat()
            }), 200
        else:
            return jsonify({
                'error': result.message,
                'timestamp': datetime.utcnow().isoformat()
            }), 400
            
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'message': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500


@contracts_query_bp.route('/metrics', methods=['GET'])
async def get_contracts_metrics():
    """Get contracts metrics"""
    try:
        metric_type = request.args.get('metric_type', 'completion_rate')
        period = request.args.get('period', 'month')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        query = GetContractsMetrics(
            metric_type=metric_type,
            period=period,
            date_from=datetime.fromisoformat(date_from) if date_from else None,
            date_to=datetime.fromisoformat(date_to) if date_to else None,
            user_id=request.headers.get('X-User-ID', 'anonymous')
        )
        
        result = await current_app.query_bus.execute(query)
        
        if result.success:
            return jsonify({
                'metrics': result.data,
                'metric_type': metric_type,
                'period': period,
                'timestamp': datetime.utcnow().isoformat()
            }), 200
        else:
            return jsonify({
                'error': result.message,
                'timestamp': datetime.utcnow().isoformat()
            }), 400
            
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'message': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500