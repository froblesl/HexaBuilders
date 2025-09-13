from flask import Blueprint, request, jsonify
from datetime import datetime
import asyncio
from typing import Dict, Any

from onboarding.modulos.documents.aplicacion.handlers import (
    UploadDocumentCommand, UploadDocumentHandler,
    ReviewDocumentCommand, ReviewDocumentHandler,
    PerformComplianceCheckCommand, ComplianceCheckHandler,
    CreateDocumentPackageCommand, CreateDocumentPackageHandler,
    GetDocumentQuery, GetDocumentHandler,
    GetPartnerDocumentsQuery, GetPartnerDocumentsHandler,
    GetDocumentPackageQuery, GetDocumentPackageHandler,
    GetPartnerVerificationStatusQuery, GetPartnerVerificationStatusHandler
)

documents_bp = Blueprint('documents', __name__)


@documents_bp.route('/document-packages', methods=['POST'])
def create_document_package():
    """Create a document package for partner verification"""
    try:
        data = request.get_json()
        
        required_fields = ['partner_id', 'verification_level', 'required_document_types']
        if not all(field in data for field in required_fields):
            return jsonify({
                'error': 'Missing required fields',
                'required': required_fields
            }), 400

        command = CreateDocumentPackageCommand(
            partner_id=data['partner_id'],
            verification_level=data['verification_level'],
            required_document_types=data['required_document_types']
        )

        # In real implementation, inject dependencies
        handler = CreateDocumentPackageHandler(None, None)  # TODO: Inject repositories
        result = asyncio.run(handler.handle(command))

        return jsonify(result), 201

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'message': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500


@documents_bp.route('', methods=['POST'])
def upload_document():
    """Upload a document for verification"""
    try:
        data = request.get_json()
        
        required_fields = [
            'partner_id', 'document_type', 'file_name', 
            'file_size', 'mime_type', 'storage_path', 'checksum'
        ]
        if not all(field in data for field in required_fields):
            return jsonify({
                'error': 'Missing required fields',
                'required': required_fields
            }), 400

        # Parse expiry_date if provided
        expiry_date = None
        if 'expiry_date' in data and data['expiry_date']:
            expiry_date = datetime.fromisoformat(data['expiry_date'].replace('Z', '+00:00'))

        command = UploadDocumentCommand(
            partner_id=data['partner_id'],
            document_type=data['document_type'],
            file_name=data['file_name'],
            file_size=data['file_size'],
            mime_type=data['mime_type'],
            storage_path=data['storage_path'],
            checksum=data['checksum'],
            verification_level=data.get('verification_level', 'STANDARD'),
            required=data.get('required', True),
            expiry_date=expiry_date
        )

        # In real implementation, inject dependencies
        handler = UploadDocumentHandler(None, None, None)  # TODO: Inject repositories
        result = asyncio.run(handler.handle(command))

        return jsonify(result), 201

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'message': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500


@documents_bp.route('/<document_id>', methods=['GET'])
def get_document(document_id):
    """Get document details"""
    try:
        query = GetDocumentQuery(document_id=document_id)
        
        # In real implementation, inject dependencies
        handler = GetDocumentHandler(None)  # TODO: Inject repository
        result = asyncio.run(handler.handle(query))

        return jsonify(result), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'message': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500


@documents_bp.route('/<document_id>/review', methods=['POST'])
def review_document(document_id):
    """Review a document"""
    try:
        data = request.get_json()
        
        required_fields = ['reviewer_id', 'decision', 'comments']
        if not all(field in data for field in required_fields):
            return jsonify({
                'error': 'Missing required fields',
                'required': required_fields
            }), 400

        if data['decision'] not in ['APPROVED', 'REJECTED', 'NEEDS_CLARIFICATION']:
            return jsonify({
                'error': 'Invalid decision',
                'valid_decisions': ['APPROVED', 'REJECTED', 'NEEDS_CLARIFICATION']
            }), 400

        command = ReviewDocumentCommand(
            document_id=document_id,
            reviewer_id=data['reviewer_id'],
            decision=data['decision'],
            comments=data['comments'],
            confidence_score=data.get('confidence_score'),
            automated=data.get('automated', False)
        )

        # In real implementation, inject dependencies
        handler = ReviewDocumentHandler(None, None)  # TODO: Inject repositories
        result = asyncio.run(handler.handle(command))

        return jsonify(result), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'message': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500


@documents_bp.route('/<document_id>/compliance-check', methods=['POST'])
def perform_compliance_check(document_id):
    """Perform compliance check on document"""
    try:
        data = request.get_json()
        
        required_fields = ['check_type', 'regulation', 'passed', 'details']
        if not all(field in data for field in required_fields):
            return jsonify({
                'error': 'Missing required fields',
                'required': required_fields
            }), 400

        command = PerformComplianceCheckCommand(
            document_id=document_id,
            check_type=data['check_type'],
            regulation=data['regulation'],
            passed=data['passed'],
            details=data['details']
        )

        # In real implementation, inject dependencies
        handler = ComplianceCheckHandler(None, None)  # TODO: Inject repositories
        result = asyncio.run(handler.handle(command))

        return jsonify(result), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'message': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500


@documents_bp.route('/partners/<partner_id>/documents', methods=['GET'])
def get_partner_documents(partner_id):
    """Get all documents for a partner"""
    try:
        query = GetPartnerDocumentsQuery(partner_id=partner_id)
        
        # In real implementation, inject dependencies
        handler = GetPartnerDocumentsHandler(None)  # TODO: Inject repository
        result = asyncio.run(handler.handle(query))

        return jsonify(result), 200

    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'message': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500


@documents_bp.route('/partners/<partner_id>/document-package', methods=['GET'])
def get_document_package(partner_id):
    """Get document package for a partner"""
    try:
        query = GetDocumentPackageQuery(partner_id=partner_id)
        
        # In real implementation, inject dependencies
        handler = GetDocumentPackageHandler(None)  # TODO: Inject repository
        result = asyncio.run(handler.handle(query))

        return jsonify(result), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'message': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500


@documents_bp.route('/partners/<partner_id>/verification-status', methods=['GET'])
def get_verification_status(partner_id):
    """Get complete verification status for a partner"""
    try:
        query = GetPartnerVerificationStatusQuery(partner_id=partner_id)
        
        # In real implementation, inject dependencies
        handler = GetPartnerVerificationStatusHandler(None)  # TODO: Inject repository
        result = asyncio.run(handler.handle(query))

        return jsonify(result), 200

    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'message': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500


@documents_bp.route('/pending-review', methods=['GET'])
def get_documents_for_review():
    """Get documents pending review"""
    try:
        # Mock response for now
        documents = [
            {
                "id": "doc-123",
                "partner_id": "partner-456",
                "document_type": "IDENTITY",
                "status": "UNDER_REVIEW",
                "submitted_at": "2024-01-15T10:30:00Z",
                "file_name": "passport.pdf",
                "verification_level": "STANDARD"
            },
            {
                "id": "doc-124",
                "partner_id": "partner-457",
                "document_type": "BUSINESS_REGISTRATION",
                "status": "UNDER_REVIEW",
                "submitted_at": "2024-01-15T11:45:00Z",
                "file_name": "business_cert.pdf",
                "verification_level": "ENHANCED"
            }
        ]

        return jsonify({
            "pending_documents": documents,
            "total_count": len(documents)
        }), 200

    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'message': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500


@documents_bp.route('/types', methods=['GET'])
def get_document_types():
    """Get available document types and their requirements"""
    try:
        document_types = {
            "IDENTITY": {
                "name": "Identity Document",
                "description": "Government-issued photo ID (passport, driver's license, etc.)",
                "required_for": ["BASIC", "STANDARD", "ENHANCED", "PREMIUM"],
                "expiry_required": True,
                "max_file_size": 10485760,  # 10MB
                "accepted_formats": ["pdf", "jpg", "jpeg", "png"]
            },
            "BUSINESS_REGISTRATION": {
                "name": "Business Registration",
                "description": "Official business registration certificate",
                "required_for": ["STANDARD", "ENHANCED", "PREMIUM"],
                "expiry_required": False,
                "max_file_size": 10485760,
                "accepted_formats": ["pdf"]
            },
            "TAX_CERTIFICATE": {
                "name": "Tax Certificate",
                "description": "Current tax registration certificate",
                "required_for": ["ENHANCED", "PREMIUM"],
                "expiry_required": True,
                "max_file_size": 10485760,
                "accepted_formats": ["pdf"]
            },
            "BANK_STATEMENT": {
                "name": "Bank Statement",
                "description": "Recent bank statement (last 3 months)",
                "required_for": ["ENHANCED", "PREMIUM"],
                "expiry_required": False,
                "max_file_size": 10485760,
                "accepted_formats": ["pdf"]
            },
            "FINANCIAL_STATEMENT": {
                "name": "Financial Statement",
                "description": "Audited financial statement (annual)",
                "required_for": ["PREMIUM"],
                "expiry_required": False,
                "max_file_size": 20971520,  # 20MB
                "accepted_formats": ["pdf"]
            },
            "INSURANCE_CERTIFICATE": {
                "name": "Insurance Certificate",
                "description": "Professional liability insurance certificate",
                "required_for": ["PREMIUM"],
                "expiry_required": True,
                "max_file_size": 10485760,
                "accepted_formats": ["pdf"]
            }
        }

        return jsonify({
            "document_types": document_types,
            "verification_levels": {
                "BASIC": ["IDENTITY"],
                "STANDARD": ["IDENTITY", "BUSINESS_REGISTRATION"],
                "ENHANCED": ["IDENTITY", "BUSINESS_REGISTRATION", "TAX_CERTIFICATE", "BANK_STATEMENT"],
                "PREMIUM": ["IDENTITY", "BUSINESS_REGISTRATION", "TAX_CERTIFICATE", "BANK_STATEMENT", "FINANCIAL_STATEMENT", "INSURANCE_CERTIFICATE"]
            }
        }), 200

    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'message': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500


@documents_bp.route('/stats', methods=['GET'])
def get_document_statistics():
    """Get document processing statistics"""
    try:
        # Mock statistics for now
        stats = {
            "total_documents": 1247,
            "pending_upload": 45,
            "under_review": 89,
            "approved": 1056,
            "rejected": 57,
            "expired": 12,
            "by_type": {
                "IDENTITY": 543,
                "BUSINESS_REGISTRATION": 387,
                "TAX_CERTIFICATE": 201,
                "BANK_STATEMENT": 116,
                "FINANCIAL_STATEMENT": 78,
                "INSURANCE_CERTIFICATE": 34
            },
            "by_verification_level": {
                "BASIC": 234,
                "STANDARD": 567,
                "ENHANCED": 334,
                "PREMIUM": 112
            },
            "processing_times": {
                "average_review_time_hours": 24.5,
                "average_compliance_check_hours": 4.2,
                "approval_rate": 94.3
            }
        }

        return jsonify(stats), 200

    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'message': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500