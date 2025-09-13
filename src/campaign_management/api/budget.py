from flask import Blueprint, request, jsonify
from datetime import datetime

budget_bp = Blueprint('budget', __name__)


@budget_bp.route('/<campaign_id>/status', methods=['GET'])
def get_budget_status(campaign_id):
    """Get detailed budget status"""
    try:
        return jsonify({
            'campaign_id': campaign_id,
            'budget': {
                'total': 10000.00,
                'spent': 3450.67,
                'remaining': 6549.33,
                'currency': 'USD',
                'spend_rate': 115.02,
                'projected_end_date': '2024-02-10'
            },
            'alerts': [
                {'type': 'warning', 'message': 'High spend rate detected'}
            ],
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@budget_bp.route('/<campaign_id>/adjust', methods=['POST'])
def adjust_budget(campaign_id):
    """Adjust campaign budget"""
    try:
        data = request.get_json()
        new_amount = data.get('amount')
        
        return jsonify({
            'campaign_id': campaign_id,
            'old_budget': 10000.00,
            'new_budget': new_amount,
            'message': 'Budget adjusted successfully',
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500