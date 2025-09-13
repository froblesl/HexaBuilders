import logging
from typing import Dict, Any
from datetime import datetime

from onboarding.seedwork.aplicacion.comandos import Command, CommandHandler
from onboarding.seedwork.aplicacion.queries import Query, QueryHandler
from onboarding.seedwork.aplicacion.handlers import Handler
from onboarding.seedwork.dominio.uow import UnitOfWork

from ..dominio.entidades import Document, DocumentPackage, DocumentType, VerificationLevel, DocumentStatus
from ..dominio.repositorios import DocumentRepository, DocumentPackageRepository, DocumentQueryRepository

logger = logging.getLogger(__name__)


# Commands
class UploadDocumentCommand(Command):
    def __init__(
        self,
        partner_id: str,
        document_type: str,
        file_name: str,
        file_size: int,
        mime_type: str,
        storage_path: str,
        checksum: str,
        verification_level: str = "STANDARD",
        required: bool = True,
        expiry_date: datetime = None
    ):
        self.partner_id = partner_id
        self.document_type = DocumentType(document_type)
        self.file_name = file_name
        self.file_size = file_size
        self.mime_type = mime_type
        self.storage_path = storage_path
        self.checksum = checksum
        self.verification_level = VerificationLevel(verification_level)
        self.required = required
        self.expiry_date = expiry_date


class ReviewDocumentCommand(Command):
    def __init__(
        self,
        document_id: str,
        reviewer_id: str,
        decision: str,
        comments: str,
        confidence_score: float = None,
        automated: bool = False
    ):
        self.document_id = document_id
        self.reviewer_id = reviewer_id
        self.decision = decision
        self.comments = comments
        self.confidence_score = confidence_score
        self.automated = automated


class PerformComplianceCheckCommand(Command):
    def __init__(
        self,
        document_id: str,
        check_type: str,
        regulation: str,
        passed: bool,
        details: Dict[str, Any]
    ):
        self.document_id = document_id
        self.check_type = check_type
        self.regulation = regulation
        self.passed = passed
        self.details = details


class CreateDocumentPackageCommand(Command):
    def __init__(
        self,
        partner_id: str,
        verification_level: str,
        required_document_types: list
    ):
        self.partner_id = partner_id
        self.verification_level = VerificationLevel(verification_level)
        self.required_document_types = [DocumentType(dt) for dt in required_document_types]


# Queries
class GetDocumentQuery(Query):
    def __init__(self, document_id: str):
        self.document_id = document_id


class GetPartnerDocumentsQuery(Query):
    def __init__(self, partner_id: str):
        self.partner_id = partner_id


class GetDocumentPackageQuery(Query):
    def __init__(self, partner_id: str):
        self.partner_id = partner_id


class GetDocumentsForReviewQuery(Query):
    def __init__(self, reviewer_id: str = None):
        self.reviewer_id = reviewer_id


class GetPartnerVerificationStatusQuery(Query):
    def __init__(self, partner_id: str):
        self.partner_id = partner_id


# Command Handlers
class UploadDocumentHandler(CommandHandler):
    def __init__(
        self,
        document_repository: DocumentRepository,
        package_repository: DocumentPackageRepository,
        uow: UnitOfWork
    ):
        self.document_repository = document_repository
        self.package_repository = package_repository
        self.uow = uow

    async def handle(self, command: UploadDocumentCommand) -> Dict[str, Any]:
        try:
            with self.uow:
                # Check if document already exists for this partner and type
                existing_document = await self.document_repository.get_by_partner_and_type(
                    command.partner_id, 
                    command.document_type
                )

                if existing_document and existing_document.status != DocumentStatus.REJECTED:
                    raise ValueError(f"Document of type {command.document_type.value} already exists for partner")

                # Create new document
                document = Document(
                    partner_id=command.partner_id,
                    document_type=command.document_type,
                    verification_level=command.verification_level,
                    required=command.required,
                    expiry_date=command.expiry_date
                )

                # Upload document
                document.upload_document(
                    file_name=command.file_name,
                    file_size=command.file_size,
                    mime_type=command.mime_type,
                    storage_path=command.storage_path,
                    checksum=command.checksum
                )

                # Submit for review immediately
                document.submit_for_review()

                await self.document_repository.save(document)

                # Update document package
                package = await self.package_repository.get_by_partner_id(command.partner_id)
                if package:
                    package.add_document(document)
                    await self.package_repository.save(package)

                self.uow.commit()

                logger.info(f"Document uploaded successfully: {document.id}")

                return {
                    "document_id": document.id,
                    "status": document.status.value,
                    "message": "Document uploaded and submitted for review"
                }

        except Exception as e:
            logger.error(f"Error uploading document: {str(e)}")
            raise


class ReviewDocumentHandler(CommandHandler):
    def __init__(self, document_repository: DocumentRepository, uow: UnitOfWork):
        self.document_repository = document_repository
        self.uow = uow

    async def handle(self, command: ReviewDocumentCommand) -> Dict[str, Any]:
        try:
            with self.uow:
                document = await self.document_repository.get_by_id(command.document_id)
                if not document:
                    raise ValueError(f"Document not found: {command.document_id}")

                document.review_document(
                    reviewer_id=command.reviewer_id,
                    decision=command.decision,
                    comments=command.comments,
                    confidence_score=command.confidence_score,
                    automated=command.automated
                )

                await self.document_repository.save(document)
                self.uow.commit()

                logger.info(f"Document reviewed: {document.id} - Decision: {command.decision}")

                return {
                    "document_id": document.id,
                    "status": document.status.value,
                    "decision": command.decision,
                    "message": "Document review completed"
                }

        except Exception as e:
            logger.error(f"Error reviewing document: {str(e)}")
            raise


class ComplianceCheckHandler(CommandHandler):
    def __init__(self, document_repository: DocumentRepository, uow: UnitOfWork):
        self.document_repository = document_repository
        self.uow = uow

    async def handle(self, command: PerformComplianceCheckCommand) -> Dict[str, Any]:
        try:
            with self.uow:
                document = await self.document_repository.get_by_id(command.document_id)
                if not document:
                    raise ValueError(f"Document not found: {command.document_id}")

                compliance_check = document.perform_compliance_check(
                    check_type=command.check_type,
                    regulation=command.regulation,
                    passed=command.passed,
                    details=command.details
                )

                await self.document_repository.save(document)
                self.uow.commit()

                logger.info(f"Compliance check performed: {document.id} - {command.check_type}")

                return {
                    "document_id": document.id,
                    "check_type": command.check_type,
                    "passed": compliance_check.passed,
                    "timestamp": compliance_check.check_timestamp.isoformat(),
                    "message": "Compliance check completed"
                }

        except Exception as e:
            logger.error(f"Error performing compliance check: {str(e)}")
            raise


class CreateDocumentPackageHandler(CommandHandler):
    def __init__(self, package_repository: DocumentPackageRepository, uow: UnitOfWork):
        self.package_repository = package_repository
        self.uow = uow

    async def handle(self, command: CreateDocumentPackageCommand) -> Dict[str, Any]:
        try:
            with self.uow:
                # Check if package already exists
                existing_package = await self.package_repository.get_by_partner_id(command.partner_id)
                if existing_package:
                    raise ValueError(f"Document package already exists for partner: {command.partner_id}")

                # Create new package
                package = DocumentPackage(
                    partner_id=command.partner_id,
                    verification_level=command.verification_level,
                    required_document_types=command.required_document_types
                )

                await self.package_repository.save(package)
                self.uow.commit()

                logger.info(f"Document package created: {package.id}")

                return {
                    "package_id": package.id,
                    "partner_id": command.partner_id,
                    "verification_level": command.verification_level.value,
                    "required_documents": len(command.required_document_types),
                    "message": "Document package created successfully"
                }

        except Exception as e:
            logger.error(f"Error creating document package: {str(e)}")
            raise


# Query Handlers
class GetDocumentHandler(QueryHandler):
    def __init__(self, document_repository: DocumentRepository):
        self.document_repository = document_repository

    async def handle(self, query: GetDocumentQuery) -> Dict[str, Any]:
        document = await self.document_repository.get_by_id(query.document_id)
        if not document:
            raise ValueError(f"Document not found: {query.document_id}")

        return {
            "id": document.id,
            "partner_id": document.partner_id,
            "document_type": document.document_type.value,
            "status": document.status.value,
            "verification_level": document.verification_level.value,
            "required": document.required,
            "expiry_date": document.expiry_date.isoformat() if document.expiry_date else None,
            "is_expired": document.is_expired,
            "is_approved": document.is_approved,
            "metadata": {
                "file_name": document.metadata.file_name if document.metadata else None,
                "file_size": document.metadata.file_size if document.metadata else None,
                "mime_type": document.metadata.mime_type if document.metadata else None,
                "upload_timestamp": document.metadata.upload_timestamp.isoformat() if document.metadata else None,
                "version": document.metadata.version if document.metadata else None
            },
            "review_history": [
                {
                    "reviewer_id": review.reviewer_id,
                    "review_timestamp": review.review_timestamp.isoformat(),
                    "decision": review.decision,
                    "comments": review.comments,
                    "confidence_score": review.confidence_score,
                    "automated": review.automated
                }
                for review in document.review_history
            ],
            "compliance_checks": [
                {
                    "check_type": check.check_type,
                    "check_timestamp": check.check_timestamp.isoformat(),
                    "passed": check.passed,
                    "regulation": check.regulation,
                    "details": check.details
                }
                for check in document.compliance_checks
            ]
        }


class GetPartnerDocumentsHandler(QueryHandler):
    def __init__(self, document_repository: DocumentRepository):
        self.document_repository = document_repository

    async def handle(self, query: GetPartnerDocumentsQuery) -> Dict[str, Any]:
        documents = await self.document_repository.get_by_partner_id(query.partner_id)

        return {
            "partner_id": query.partner_id,
            "total_documents": len(documents),
            "documents": [
                {
                    "id": doc.id,
                    "document_type": doc.document_type.value,
                    "status": doc.status.value,
                    "verification_level": doc.verification_level.value,
                    "required": doc.required,
                    "is_expired": doc.is_expired,
                    "is_approved": doc.is_approved,
                    "upload_date": doc.metadata.upload_timestamp.isoformat() if doc.metadata else None,
                    "latest_review": {
                        "decision": doc.latest_review.decision if doc.latest_review else None,
                        "timestamp": doc.latest_review.review_timestamp.isoformat() if doc.latest_review else None
                    }
                }
                for doc in documents
            ]
        }


class GetDocumentPackageHandler(QueryHandler):
    def __init__(self, package_repository: DocumentPackageRepository):
        self.package_repository = package_repository

    async def handle(self, query: GetDocumentPackageQuery) -> Dict[str, Any]:
        package = await self.package_repository.get_by_partner_id(query.partner_id)
        if not package:
            raise ValueError(f"Document package not found for partner: {query.partner_id}")

        return {
            "package_id": package.id,
            "partner_id": package.partner_id,
            "verification_level": package.verification_level.value,
            "completion_status": package.completion_status,
            "completion_percentage": package.completion_percentage,
            "completion_timestamp": package._completion_timestamp.isoformat() if package._completion_timestamp else None,
            "missing_documents": [dt.value for dt in package.get_missing_documents()],
            "total_required": len(package._required_document_types),
            "documents_submitted": len(package.get_all_documents())
        }


class GetPartnerVerificationStatusHandler(QueryHandler):
    def __init__(self, query_repository: DocumentQueryRepository):
        self.query_repository = query_repository

    async def handle(self, query: GetPartnerVerificationStatusQuery) -> Dict[str, Any]:
        verification_progress = await self.query_repository.get_verification_progress(query.partner_id)
        compliance_status = await self.query_repository.get_compliance_status(query.partner_id)
        document_summary = await self.query_repository.get_partner_document_summary(query.partner_id)

        return {
            "partner_id": query.partner_id,
            "verification_progress": verification_progress,
            "compliance_status": compliance_status,
            "document_summary": document_summary,
            "overall_status": "COMPLETED" if verification_progress.get("completion_percentage", 0) == 100 else "IN_PROGRESS"
        }