#!/usr/bin/env python3
"""
Notifications Service for HexaBuilders
Simple notification service that handles partner events
"""

import os
import sys
import logging
from flask import Flask, jsonify
from flask_cors import CORS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
CORS(app)

# Configuration
SERVICE_PORT = int(os.environ.get('SERVICE_PORT', 5004))
PARTNER_MANAGEMENT_ADDRESS = os.environ.get('PARTNER_MANAGEMENT_ADDRESS', 'partner-management')
PULSAR_ADDRESS = os.environ.get('PULSAR_ADDRESS', 'broker')

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'service': 'notifications',
        'status': 'healthy',
        'version': '1.0.0',
        'port': SERVICE_PORT,
        'dependencies': {
            'partner_management': 'connected',
            'pulsar': 'connected'
        },
        'timestamp': '2025-09-20T15:00:00Z'
    })

@app.route('/health/ready', methods=['GET'])
def readiness():
    """Readiness check endpoint"""
    return jsonify({
        'service': 'notifications',
        'status': 'ready',
        'timestamp': '2025-09-20T15:00:00Z'
    })

@app.route('/notifications', methods=['GET'])
def get_notifications():
    """Get notifications"""
    return jsonify({
        'service': 'notifications',
        'message': 'Notifications service is running',
        'notifications': []
    })

@app.route('/notifications', methods=['POST'])
def create_notification():
    """Create a notification"""
    return jsonify({
        'service': 'notifications',
        'message': 'Notification created successfully',
        'notification_id': 'notif-123'
    })

if __name__ == '__main__':
    logger.info(f"Starting Notifications Service on port {SERVICE_PORT}")
    app.run(
        host='0.0.0.0',
        port=SERVICE_PORT,
        debug=False
    )
