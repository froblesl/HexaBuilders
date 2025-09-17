from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Dict, Any, Optional
from uuid import uuid4

from onboarding.seedwork.dominio.entidades import AggregateRoot
from onboarding.seedwork.dominio.eventos import DomainEvent


class DocumentType(Enum):
    IDENTITY = "IDENTITY"
    BUSINESS_REGISTRATION = "BUSINESS_REGISTRATION"
    TAX_CERTIFICATE = "TAX_CERTIFICATE"
    BANK_STATEMENT = "BANK_STATEMENT"
    FINANCIAL_STATEMENT = "FINANCIAL_STATEMENT"
    REFERENCE_LETTER = "REFERENCE_LETTER"
    INSURANCE_CERTIFICATE = "INSURANCE_CERTIFICATE"
    CONTRACT_TEMPLATE = "CONTRACT_TEMPLATE"
    COMPLIANCE_CERTIFICATE = "COMPLIANCE_CERTIFICATE"


class DocumentStatus(Enum):
    PENDING_UPLOAD = "PENDING_UPLOAD"
    UPLOADED = "UPLOADED"
    UNDER_REVIEW = "UNDER_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"
    ARCHIVED = "ARCHIVED"


class VerificationLevel(Enum):
    BASIC = "BASIC"
    STANDARD = "STANDARD"
    ENHANCED = "ENHANCED"
    PREMIUM = "PREMIUM"


@dataclass
class DocumentMetadata:
    file_name: str
    file_size: int
    mime_type: str
    upload_timestamp: datetime
    checksum: str
    storage_path: str
    version: int = 1


@dataclass
class ReviewResult:
    reviewer_id: str
    review_timestamp: datetime
    decision: str  # APPROVED, REJECTED, NEEDS_CLARIFICATION
    comments: str
    confidence_score: Optional[float] = None
    automated: bool = False


@dataclass
class ComplianceCheck:
    check_type: str
    check_timestamp: datetime
    passed: bool
    details: Dict[str, Any]
    regulation: str


# Domain Events
@dataclass
class DocumentUploaded(DomainEvent):
    document_id: str = field(default_factory=lambda: "")
    partner_id: str = field(default_factory=lambda: "")
    document_type: DocumentType = field(default_factory=lambda: DocumentType.IDENTITY)
    metadata: DocumentMetadata = field(default_factory=lambda: DocumentMetadata("", 0, "", datetime.utcnow(), "", ""))


@dataclass
class DocumentReviewed(DomainEvent):
    document_id: str = field(default_factory=lambda: "")
    partner_id: str = field(default_factory=lambda: "")
    review_result: ReviewResult = field(default_factory=lambda: ReviewResult("", datetime.utcnow(), "", ""))
    previous_status: DocumentStatus = field(default_factory=lambda: DocumentStatus.PENDING_UPLOAD)
    new_status: DocumentStatus = field(default_factory=lambda: DocumentStatus.UPLOADED)


@dataclass
class DocumentExpired(DomainEvent):
    document_id: str = field(default_factory=lambda: "")
    partner_id: str = field(default_factory=lambda: "")
    document_type: DocumentType = field(default_factory=lambda: DocumentType.IDENTITY)
    expiry_date: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ComplianceCheckCompleted(DomainEvent):
    document_id: str = field(default_factory=lambda: "")
    partner_id: str = field(default_factory=lambda: "")
    compliance_check: ComplianceCheck = field(default_factory=lambda: ComplianceCheck("", datetime.utcnow(), False, {}, ""))


@dataclass
class DocumentPackageCompleted(DomainEvent):
    partner_id: str = field(default_factory=lambda: "")
    verification_level: VerificationLevel = field(default_factory=lambda: VerificationLevel.BASIC)
    completed_documents: List[str] = field(default_factory=list)
    completion_timestamp: datetime = field(default_factory=datetime.utcnow)


class Document(AggregateRoot):
    def __init__(
        self,
        partner_id: str,
        document_type: DocumentType,
        verification_level: VerificationLevel,
        required: bool = True,
        expiry_date: Optional[datetime] = None
    ):
        super().__init__()
        self.id = str(uuid4())
        self._partner_id = partner_id
        self._document_type = document_type
        self._verification_level = verification_level
        self._status = DocumentStatus.PENDING_UPLOAD
        self._required = required
        self._expiry_date = expiry_date
        self._metadata: Optional[DocumentMetadata] = None
        self._review_history: List[ReviewResult] = []
        self._compliance_checks: List[ComplianceCheck] = []
        self._created_at = datetime.utcnow()
        self._updated_at = datetime.utcnow()

    @property
    def partner_id(self) -> str:
        return self._partner_id

    @property
    def document_type(self) -> DocumentType:
        return self._document_type

    @property
    def status(self) -> DocumentStatus:
        return self._status

    @property
    def verification_level(self) -> VerificationLevel:
        return self._verification_level

    @property
    def required(self) -> bool:
        return self._required

    @property
    def expiry_date(self) -> Optional[datetime]:
        return self._expiry_date

    @property
    def metadata(self) -> Optional[DocumentMetadata]:
        return self._metadata

    @property
    def review_history(self) -> List[ReviewResult]:
        return self._review_history.copy()

    @property
    def compliance_checks(self) -> List[ComplianceCheck]:
        return self._compliance_checks.copy()

    @property
    def is_expired(self) -> bool:
        if not self._expiry_date:
            return False
        return datetime.utcnow() > self._expiry_date

    @property
    def is_approved(self) -> bool:
        return self._status == DocumentStatus.APPROVED

    @property
    def latest_review(self) -> Optional[ReviewResult]:
        return self._review_history[-1] if self._review_history else None

    def upload_document(
        self,
        file_name: str,
        file_size: int,
        mime_type: str,
        storage_path: str,
        checksum: str
    ):
        if self._status not in [DocumentStatus.PENDING_UPLOAD, DocumentStatus.REJECTED]:
            raise ValueError(f"Cannot upload document in status: {self._status}")

        metadata = DocumentMetadata(
            file_name=file_name,
            file_size=file_size,
            mime_type=mime_type,
            upload_timestamp=datetime.utcnow(),
            checksum=checksum,
            storage_path=storage_path,
            version=1 if not self._metadata else self._metadata.version + 1
        )

        self._metadata = metadata
        self._status = DocumentStatus.UPLOADED
        self._updated_at = datetime.utcnow()

        self.publicar_evento(DocumentUploaded(
            event_id=str(uuid4()),
            occurred_on=datetime.utcnow(),
            document_id=self.id,
            partner_id=self._partner_id,
            document_type=self._document_type,
            metadata=metadata
        ))

    def submit_for_review(self):
        if self._status != DocumentStatus.UPLOADED:
            raise ValueError(f"Cannot submit for review from status: {self._status}")

        self._status = DocumentStatus.UNDER_REVIEW
        self._updated_at = datetime.utcnow()

    def review_document(
        self,
        reviewer_id: str,
        decision: str,
        comments: str,
        confidence_score: Optional[float] = None,
        automated: bool = False
    ):
        if self._status != DocumentStatus.UNDER_REVIEW:
            raise ValueError(f"Cannot review document in status: {self._status}")

        if decision not in ["APPROVED", "REJECTED", "NEEDS_CLARIFICATION"]:
            raise ValueError(f"Invalid decision: {decision}")

        previous_status = self._status
        review_result = ReviewResult(
            reviewer_id=reviewer_id,
            review_timestamp=datetime.utcnow(),
            decision=decision,
            comments=comments,
            confidence_score=confidence_score,
            automated=automated
        )

        self._review_history.append(review_result)

        if decision == "APPROVED":
            self._status = DocumentStatus.APPROVED
        elif decision == "REJECTED":
            self._status = DocumentStatus.REJECTED
        else:  # NEEDS_CLARIFICATION
            self._status = DocumentStatus.UPLOADED

        self._updated_at = datetime.utcnow()

        self.publicar_evento(DocumentReviewed(
            event_id=str(uuid4()),
            occurred_on=datetime.utcnow(),
            document_id=self.id,
            partner_id=self._partner_id,
            review_result=review_result,
            previous_status=previous_status,
            new_status=self._status
        ))

    def perform_compliance_check(
        self,
        check_type: str,
        regulation: str,
        passed: bool,
        details: Dict[str, Any]
    ):
        compliance_check = ComplianceCheck(
            check_type=check_type,
            check_timestamp=datetime.utcnow(),
            passed=passed,
            details=details,
            regulation=regulation
        )

        self._compliance_checks.append(compliance_check)
        self._updated_at = datetime.utcnow()

        self.publicar_evento(ComplianceCheckCompleted(
            event_id=str(uuid4()),
            occurred_on=datetime.utcnow(),
            document_id=self.id,
            partner_id=self._partner_id,
            compliance_check=compliance_check
        ))

        return compliance_check

    def mark_as_expired(self):
        if self.is_expired:
            previous_status = self._status
            self._status = DocumentStatus.EXPIRED
            self._updated_at = datetime.utcnow()

            self.publicar_evento(DocumentExpired(
                event_id=str(uuid4()),
                occurred_on=datetime.utcnow(),
                document_id=self.id,
                partner_id=self._partner_id,
                document_type=self._document_type,
                expiry_date=self._expiry_date
            ))

    def archive_document(self):
        if self._status not in [DocumentStatus.APPROVED, DocumentStatus.EXPIRED]:
            raise ValueError(f"Cannot archive document in status: {self._status}")

        self._status = DocumentStatus.ARCHIVED
        self._updated_at = datetime.utcnow()

    def get_compliance_status(self) -> Dict[str, bool]:
        compliance_status = {}
        for check in self._compliance_checks:
            compliance_status[check.check_type] = check.passed
        return compliance_status

    @classmethod
    def from_events(cls, events: List[DomainEvent]) -> 'Document':
        if not events:
            raise ValueError("Cannot reconstruct Document from empty events list")

        # Find creation event or reconstruct from first upload
        document = None
        
        for event in events:
            if isinstance(event, DocumentUploaded):
                if document is None:
                    document = cls(
                        partner_id=event.partner_id,
                        document_type=event.document_type,
                        verification_level=VerificationLevel.STANDARD,  # Default
                        required=True
                    )
                    document.id = event.document_id
                document._apply_document_uploaded(event)
            elif isinstance(event, DocumentReviewed):
                document._apply_document_reviewed(event)
            elif isinstance(event, ComplianceCheckCompleted):
                document._apply_compliance_check_completed(event)
            elif isinstance(event, DocumentExpired):
                document._apply_document_expired(event)

        if document is None:
            raise ValueError("No DocumentUploaded event found in events list")

        return document

    def _apply_document_uploaded(self, event: DocumentUploaded):
        self._metadata = event.metadata
        self._status = DocumentStatus.UPLOADED

    def _apply_document_reviewed(self, event: DocumentReviewed):
        self._review_history.append(event.review_result)
        self._status = event.new_status

    def _apply_compliance_check_completed(self, event: ComplianceCheckCompleted):
        self._compliance_checks.append(event.compliance_check)

    def _apply_document_expired(self, event: DocumentExpired):
        self._status = DocumentStatus.EXPIRED


class DocumentPackage(AggregateRoot):
    def __init__(
        self,
        partner_id: str,
        verification_level: VerificationLevel,
        required_document_types: List[DocumentType]
    ):
        super().__init__()
        self.id = str(uuid4())
        self._partner_id = partner_id
        self._verification_level = verification_level
        self._required_document_types = required_document_types
        self._documents: Dict[DocumentType, Document] = {}
        self._completion_status = "IN_PROGRESS"
        self._completion_timestamp: Optional[datetime] = None
        self._created_at = datetime.utcnow()

    @property
    def partner_id(self) -> str:
        return self._partner_id

    @property
    def verification_level(self) -> VerificationLevel:
        return self._verification_level

    @property
    def completion_status(self) -> str:
        return self._completion_status

    @property
    def completion_percentage(self) -> float:
        if not self._required_document_types:
            return 100.0
        
        approved_count = sum(
            1 for doc_type in self._required_document_types
            if doc_type in self._documents and self._documents[doc_type].is_approved
        )
        
        return (approved_count / len(self._required_document_types)) * 100.0

    def add_document(self, document: Document):
        if document.document_type in self._documents:
            raise ValueError(f"Document type {document.document_type} already exists in package")

        self._documents[document.document_type] = document
        self._check_completion()

    def get_document(self, document_type: DocumentType) -> Optional[Document]:
        return self._documents.get(document_type)

    def get_all_documents(self) -> List[Document]:
        return list(self._documents.values())

    def get_missing_documents(self) -> List[DocumentType]:
        return [
            doc_type for doc_type in self._required_document_types
            if doc_type not in self._documents or not self._documents[doc_type].is_approved
        ]

    def _check_completion(self):
        if self._completion_status == "COMPLETED":
            return

        if self.completion_percentage == 100.0:
            self._completion_status = "COMPLETED"
            self._completion_timestamp = datetime.utcnow()

            completed_document_ids = [
                doc.id for doc in self._documents.values() if doc.is_approved
            ]

            self.publicar_evento(DocumentPackageCompleted(
                event_id=str(uuid4()),
                occurred_on=datetime.utcnow(),
                partner_id=self._partner_id,
                verification_level=self._verification_level,
                completed_documents=completed_document_ids,
                completion_timestamp=self._completion_timestamp
            ))

    @classmethod
    def from_events(cls, events: List[DomainEvent]) -> 'DocumentPackage':
        raise NotImplementedError("DocumentPackage event sourcing not implemented")