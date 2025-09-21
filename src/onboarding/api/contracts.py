from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
import uuid

from src.onboarding.seedwork.aplicacion.comandos import (
    CreateContract,
    UpdateContractTerms,
    SubmitForLegalReview,
    ApprovalLegalReview,
    RejectLegalReview,
    SignContract,
    ActivateContract,
    CancelContract
)

contracts_bp = Blueprint('contracts', __name__)


@contracts_bp.route('', methods=['POST'])
async def create_contract():
    """Create a new contract"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['partner_id', 'contract_type', 'template_id', 'initial_terms']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'error': f'Missing required field: {field}',
                    'timestamp': datetime.utcnow().isoformat()
                }), 400
        
        # Create command
        command = CreateContract(
            partner_id=data['partner_id'],
            contract_type=data['contract_type'],
            template_id=data['template_id'],
            initial_terms=data['initial_terms'],
            user_id=data.get('user_id', 'system')
        )
        
        # Execute command
        result = await current_app.command_bus.execute(command)
        
        if result.success:
            return jsonify({
                'command_id': command.id,
                'contract_id': result.data.get('contract_id'),
                'message': result.message,
                'timestamp': datetime.utcnow().isoformat()
            }), 202  # Accepted
        else:
            return jsonify({
                'error': result.message,
                'errors': result.errors,
                'timestamp': datetime.utcnow().isoformat()
            }), 400
            
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'message': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500


@contracts_bp.route('/<contract_id>/terms', methods=['PUT'])
async def update_contract_terms(contract_id):
    """Update contract terms"""
    try:
        data = request.get_json()
        
        if 'updated_terms' not in data:
            return jsonify({
                'error': 'Missing required field: updated_terms',
                'timestamp': datetime.utcnow().isoformat()
            }), 400
        
        command = UpdateContractTerms(
            contract_id=contract_id,
            updated_terms=data['updated_terms'],
            user_id=data.get('user_id', 'system')
        )
        
        result = await current_app.command_bus.execute(command)
        
        if result.success:
            return jsonify({
                'command_id': command.id,
                'message': result.message,
                'timestamp': datetime.utcnow().isoformat()
            }), 202
        else:
            return jsonify({
                'error': result.message,
                'errors': result.errors,
                'timestamp': datetime.utcnow().isoformat()
            }), 400
            
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'message': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500


@contracts_bp.route('/<contract_id>/legal-review', methods=['POST'])
async def submit_for_legal_review(contract_id):
    """Submit contract for legal review"""
    try:
        data = request.get_json()
        
        if 'legal_reviewer' not in data:
            return jsonify({
                'error': 'Missing required field: legal_reviewer',
                'timestamp': datetime.utcnow().isoformat()
            }), 400
        
        command = SubmitForLegalReview(
            contract_id=contract_id,
            legal_reviewer=data['legal_reviewer'],
            user_id=data.get('user_id', 'system')
        )
        
        result = await current_app.command_bus.execute(command)
        
        if result.success:
            return jsonify({
                'command_id': command.id,
                'message': result.message,
                'timestamp': datetime.utcnow().isoformat()
            }), 202
        else:
            return jsonify({
                'error': result.message,
                'errors': result.errors,
                'timestamp': datetime.utcnow().isoformat()
            }), 400
            
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'message': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500


@contracts_bp.route('/<contract_id>/legal-review/approve', methods=['POST'])
async def approve_legal_review(contract_id):
    """Approve legal review"""
    try:
        data = request.get_json()
        
        command = ApprovalLegalReview(
            contract_id=contract_id,
            reviewer=data.get('reviewer', 'system'),
            user_id=data.get('user_id', 'system')
        )
        
        result = await current_app.command_bus.execute(command)
        
        if result.success:
            return jsonify({
                'command_id': command.id,
                'message': result.message,
                'timestamp': datetime.utcnow().isoformat()
            }), 202
        else:
            return jsonify({
                'error': result.message,
                'errors': result.errors,
                'timestamp': datetime.utcnow().isoformat()
            }), 400
            
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'message': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500


@contracts_bp.route('/<contract_id>/legal-review/reject', methods=['POST'])
async def reject_legal_review(contract_id):
    """Reject legal review"""
    try:
        data = request.get_json()
        
        if 'reason' not in data:
            return jsonify({
                'error': 'Missing required field: reason',
                'timestamp': datetime.utcnow().isoformat()
            }), 400
        
        command = RejectLegalReview(
            contract_id=contract_id,
            reviewer=data.get('reviewer', 'system'),
            reason=data['reason'],
            user_id=data.get('user_id', 'system')
        )
        
        result = await current_app.command_bus.execute(command)
        
        if result.success:
            return jsonify({
                'command_id': command.id,
                'message': result.message,
                'timestamp': datetime.utcnow().isoformat()
            }), 202
        else:
            return jsonify({
                'error': result.message,
                'errors': result.errors,
                'timestamp': datetime.utcnow().isoformat()
            }), 400
            
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'message': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500


@contracts_bp.route('/<contract_id>/sign', methods=['POST'])
async def sign_contract(contract_id):
    """Sign contract"""
    try:
        data = request.get_json()
        
        required_fields = ['signer', 'signature_method', 'signature_data']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'error': f'Missing required field: {field}',
                    'timestamp': datetime.utcnow().isoformat()
                }), 400
        
        command = SignContract(
            contract_id=contract_id,
            signer=data['signer'],
            signature_method=data['signature_method'],
            signature_data=data['signature_data'],
            ip_address=request.remote_addr,
            user_id=data.get('user_id', 'system')
        )
        
        result = await current_app.command_bus.execute(command)
        
        if result.success:
            return jsonify({
                'command_id': command.id,
                'message': result.message,
                'timestamp': datetime.utcnow().isoformat()
            }), 202
        else:
            return jsonify({
                'error': result.message,
                'errors': result.errors,
                'timestamp': datetime.utcnow().isoformat()
            }), 400
            
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'message': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500


@contracts_bp.route('/<contract_id>/activate', methods=['POST'])
async def activate_contract(contract_id):
    """Activate contract"""
    try:
        data = request.get_json() or {}
        
        command = ActivateContract(
            contract_id=contract_id,
            user_id=data.get('user_id', 'system')
        )
        
        result = await current_app.command_bus.execute(command)
        
        if result.success:
            return jsonify({
                'command_id': command.id,
                'message': result.message,
                'timestamp': datetime.utcnow().isoformat()
            }), 202
        else:
            return jsonify({
                'error': result.message,
                'errors': result.errors,
                'timestamp': datetime.utcnow().isoformat()
            }), 400
            
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'message': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500


@contracts_bp.route('/<contract_id>/cancel', methods=['POST'])
async def cancel_contract(contract_id):
    """Cancel contract"""
    try:
        data = request.get_json()
        
        if 'reason' not in data:
            return jsonify({
                'error': 'Missing required field: reason',
                'timestamp': datetime.utcnow().isoformat()
            }), 400
        
        command = CancelContract(
            contract_id=contract_id,
            reason=data['reason'],
            user_id=data.get('user_id', 'system')
        )
        
        result = await current_app.command_bus.execute(command)
        
        if result.success:
            return jsonify({
                'command_id': command.id,
                'message': result.message,
                'timestamp': datetime.utcnow().isoformat()
            }), 202
        else:
            return jsonify({
                'error': result.message,
                'errors': result.errors,
                'timestamp': datetime.utcnow().isoformat()
            }), 400
            
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'message': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500