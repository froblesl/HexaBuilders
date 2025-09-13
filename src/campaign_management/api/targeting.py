from flask import Blueprint, request, jsonify
from datetime import datetime

targeting_bp = Blueprint('targeting', __name__)


@targeting_bp.route('/<campaign_id>', methods=['GET'])
def get_targeting(campaign_id):
    """Get campaign targeting configuration"""
    try:
        return jsonify({
            'campaign_id': campaign_id,
            'targeting': {
                'demographics': {'age_range': {'min': 25, 'max': 45}},
                'interests': ['technology', 'software'],
                'locations': ['US', 'CA', 'UK']
            },
            'estimated_reach': 2500000,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@targeting_bp.route('/<campaign_id>', methods=['PUT'])
def update_targeting(campaign_id):
    """Update campaign targeting"""
    try:
        data = request.get_json()
        return jsonify({
            'campaign_id': campaign_id,
            'targeting': data.get('targeting'),
            'message': 'Targeting updated successfully',
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500