from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Dict, Any, Optional
from uuid import uuid4

from onboarding.seedwork.dominio.entidades import AggregateRoot
from onboarding.seedwork.dominio.eventos import DomainEvent


class LegalDocumentType(Enum):
    TERMS_OF_SERVICE = "TERMS_OF_SERVICE"
    PRIVACY_POLICY = "PRIVACY_POLICY"
    DATA_PROCESSING_AGREEMENT = "DATA_PROCESSING_AGREEMENT"
    SERVICE_LEVEL_AGREEMENT = "SERVICE_LEVEL_AGREEMENT"
    NON_DISCLOSURE_AGREEMENT = "NON_DISCLOSURE_AGREEMENT"
    COMPLIANCE_AGREEMENT = "COMPLIANCE_AGREEMENT"
    INTELLECTUAL_PROPERTY_AGREEMENT = "INTELLECTUAL_PROPERTY_AGREEMENT"


class ComplianceStatus(Enum):
    PENDING = "PENDING"
    UNDER_REVIEW = "UNDER_REVIEW"
    COMPLIANT = "COMPLIANT"
    NON_COMPLIANT = "NON_COMPLIANT"
    REQUIRES_ACTION = "REQUIRES_ACTION"
    EXPIRED = "EXPIRED"


class RiskLevel(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Jurisdiction(Enum):
    US = "US"
    EU = "EU"
    UK = "UK"
    CANADA = "CANADA"
    AUSTRALIA = "AUSTRALIA"
    GLOBAL = "GLOBAL"


@dataclass
class LegalRequirement:
    requirement_id: str
    name: str
    description: str
    jurisdiction: Jurisdiction
    mandatory: bool
    regulation_reference: str
    deadline: Optional[datetime] = None
    risk_level: RiskLevel = RiskLevel.MEDIUM


@dataclass
class ComplianceCheck:
    check_id: str
    requirement_id: str
    performed_by: str
    performed_at: datetime
    status: ComplianceStatus
    findings: str
    recommendations: List[str]
    next_review_date: Optional[datetime] = None
    evidence_documents: List[str] = field(default_factory=list)


@dataclass
class LegalOpinion:
    opinion_id: str
    lawyer_id: str
    topic: str
    content: str
    risk_assessment: RiskLevel
    recommendations: List[str]
    issued_at: datetime
    valid_until: Optional[datetime] = None
    tags: List[str] = field(default_factory=list)


@dataclass
class ContractClause:
    clause_id: str
    title: str
    content: str
    category: str
    mandatory: bool
    jurisdiction_specific: Optional[Jurisdiction] = None
    risk_mitigation: List[str] = field(default_factory=list)


# Domain Events
@dataclass
class LegalReviewRequested(DomainEvent):
    partner_id: str = field(default_factory=lambda: "")
    document_type: LegalDocumentType = field(default_factory=lambda: LegalDocumentType.TERMS_OF_SERVICE)
    jurisdiction: Jurisdiction = field(default_factory=lambda: Jurisdiction.GLOBAL)
    priority: str = field(default_factory=lambda: "")
    requested_by: str = field(default_factory=lambda: "")


@dataclass
class ComplianceCheckCompleted(DomainEvent):
    partner_id: str = field(default_factory=lambda: "")
    requirement_id: str = field(default_factory=lambda: "")
    status: ComplianceStatus = field(default_factory=lambda: ComplianceStatus.PENDING)
    risk_level: RiskLevel = field(default_factory=lambda: RiskLevel.LOW)
    performed_by: str = field(default_factory=lambda: "")


@dataclass
class LegalOpinionIssued(DomainEvent):
    partner_id: str = field(default_factory=lambda: "")
    opinion_id: str = field(default_factory=lambda: "")
    topic: str = field(default_factory=lambda: "")
    risk_assessment: RiskLevel = field(default_factory=lambda: RiskLevel.LOW)
    lawyer_id: str = field(default_factory=lambda: "")


@dataclass
class ContractTemplateUpdated(DomainEvent):
    template_id: str = field(default_factory=lambda: "")
    document_type: LegalDocumentType = field(default_factory=lambda: LegalDocumentType.TERMS_OF_SERVICE)
    version: str = field(default_factory=lambda: "")
    updated_by: str = field(default_factory=lambda: "")
    changes_summary: str = field(default_factory=lambda: "")


@dataclass
class ComplianceViolationDetected(DomainEvent):
    partner_id: str = field(default_factory=lambda: "")
    violation_type: str = field(default_factory=lambda: "")
    risk_level: RiskLevel = field(default_factory=lambda: RiskLevel.LOW)
    description: str = field(default_factory=lambda: "")
    required_actions: List[str] = field(default_factory=list)


class LegalDocument(AggregateRoot):
    def __init__(
        self,
        partner_id: str,
        document_type: LegalDocumentType,
        jurisdiction: Jurisdiction,
        content: str,
        version: str = "1.0"
    ):
        super().__init__()
        self.id = str(uuid4())
        self._partner_id = partner_id
        self._document_type = document_type
        self._jurisdiction = jurisdiction
        self._content = content
        self._version = version
        self._status = ComplianceStatus.PENDING
        self._legal_requirements: List[LegalRequirement] = []
        self._compliance_checks: List[ComplianceCheck] = []
        self._legal_opinions: List[LegalOpinion] = []
        self._contract_clauses: List[ContractClause] = []
        self._created_at = datetime.utcnow()
        self._updated_at = datetime.utcnow()
        self._reviewed_by: Optional[str] = None
        self._reviewed_at: Optional[datetime] = None

    @property
    def partner_id(self) -> str:
        return self._partner_id

    @property
    def document_type(self) -> LegalDocumentType:
        return self._document_type

    @property
    def jurisdiction(self) -> Jurisdiction:
        return self._jurisdiction

    @property
    def content(self) -> str:
        return self._content

    @property
    def version(self) -> str:
        return self._version

    @property
    def status(self) -> ComplianceStatus:
        return self._status

    @property
    def legal_requirements(self) -> List[LegalRequirement]:
        return self._legal_requirements.copy()

    @property
    def compliance_checks(self) -> List[ComplianceCheck]:
        return self._compliance_checks.copy()

    @property
    def legal_opinions(self) -> List[LegalOpinion]:
        return self._legal_opinions.copy()

    @property
    def contract_clauses(self) -> List[ContractClause]:
        return self._contract_clauses.copy()

    @property
    def overall_risk_level(self) -> RiskLevel:
        if not self._compliance_checks and not self._legal_opinions:
            return RiskLevel.MEDIUM

        risk_levels = []
        
        # Consider latest compliance checks
        for check in self._compliance_checks:
            if check.status == ComplianceStatus.NON_COMPLIANT:
                for req in self._legal_requirements:
                    if req.requirement_id == check.requirement_id:
                        risk_levels.append(req.risk_level)
                        break

        # Consider legal opinions
        for opinion in self._legal_opinions:
            risk_levels.append(opinion.risk_assessment)

        if not risk_levels:
            return RiskLevel.LOW

        # Return highest risk level
        if RiskLevel.CRITICAL in risk_levels:
            return RiskLevel.CRITICAL
        elif RiskLevel.HIGH in risk_levels:
            return RiskLevel.HIGH
        elif RiskLevel.MEDIUM in risk_levels:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW

    def update_content(self, new_content: str, updated_by: str, version: str = None):
        if not new_content.strip():
            raise ValueError("Content cannot be empty")

        self._content = new_content
        if version:
            self._version = version
        else:
            # Auto-increment version
            try:
                major, minor = map(int, self._version.split('.'))
                self._version = f"{major}.{minor + 1}"
            except:
                self._version = "1.1"

        self._updated_at = datetime.utcnow()
        self._status = ComplianceStatus.PENDING  # Reset status when content changes

        # Clear previous reviews when content changes
        self._reviewed_by = None
        self._reviewed_at = None

        self.publicar_evento(ContractTemplateUpdated(
            event_id=str(uuid4()),
            occurred_on=datetime.utcnow(),
            template_id=self.id,
            document_type=self._document_type,
            version=self._version,
            updated_by=updated_by,
            changes_summary=f"Content updated to version {self._version}"
        ))

    def add_legal_requirement(self, requirement: LegalRequirement):
        # Check if requirement already exists
        for existing_req in self._legal_requirements:
            if existing_req.requirement_id == requirement.requirement_id:
                raise ValueError(f"Legal requirement {requirement.requirement_id} already exists")

        self._legal_requirements.append(requirement)
        self._updated_at = datetime.utcnow()

    def perform_compliance_check(
        self,
        requirement_id: str,
        performed_by: str,
        status: ComplianceStatus,
        findings: str,
        recommendations: List[str],
        evidence_documents: List[str] = None
    ):
        # Verify requirement exists
        requirement = None
        for req in self._legal_requirements:
            if req.requirement_id == requirement_id:
                requirement = req
                break

        if not requirement:
            raise ValueError(f"Legal requirement {requirement_id} not found")

        check = ComplianceCheck(
            check_id=str(uuid4()),
            requirement_id=requirement_id,
            performed_by=performed_by,
            performed_at=datetime.utcnow(),
            status=status,
            findings=findings,
            recommendations=recommendations,
            evidence_documents=evidence_documents or []
        )

        # Set next review date based on requirement and status
        if status == ComplianceStatus.COMPLIANT:
            if requirement.mandatory and requirement.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
                check.next_review_date = datetime.utcnow().replace(month=datetime.utcnow().month + 3)  # 3 months
            else:
                check.next_review_date = datetime.utcnow().replace(year=datetime.utcnow().year + 1)  # 1 year

        self._compliance_checks.append(check)
        self._updated_at = datetime.utcnow()

        # Update overall document status
        self._update_overall_status()

        self.publicar_evento(ComplianceCheckCompleted(
            event_id=str(uuid4()),
            occurred_on=datetime.utcnow(),
            partner_id=self._partner_id,
            requirement_id=requirement_id,
            status=status,
            risk_level=requirement.risk_level,
            performed_by=performed_by
        ))

        # Check for violations
        if status == ComplianceStatus.NON_COMPLIANT and requirement.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            self.publicar_evento(ComplianceViolationDetected(
                event_id=str(uuid4()),
                occurred_on=datetime.utcnow(),
                partner_id=self._partner_id,
                violation_type=requirement.name,
                risk_level=requirement.risk_level,
                description=findings,
                required_actions=recommendations
            ))

        return check

    def add_legal_opinion(self, opinion: LegalOpinion):
        self._legal_opinions.append(opinion)
        self._updated_at = datetime.utcnow()

        self.publicar_evento(LegalOpinionIssued(
            event_id=str(uuid4()),
            occurred_on=datetime.utcnow(),
            partner_id=self._partner_id,
            opinion_id=opinion.opinion_id,
            topic=opinion.topic,
            risk_assessment=opinion.risk_assessment,
            lawyer_id=opinion.lawyer_id
        ))

    def add_contract_clause(self, clause: ContractClause):
        # Check if clause already exists
        for existing_clause in self._contract_clauses:
            if existing_clause.clause_id == clause.clause_id:
                raise ValueError(f"Contract clause {clause.clause_id} already exists")

        # Validate jurisdiction compatibility
        if clause.jurisdiction_specific and clause.jurisdiction_specific != self._jurisdiction:
            raise ValueError(f"Clause jurisdiction {clause.jurisdiction_specific} doesn't match document jurisdiction {self._jurisdiction}")

        self._contract_clauses.append(clause)
        self._updated_at = datetime.utcnow()

    def request_legal_review(self, requested_by: str, priority: str = "MEDIUM"):
        if self._status == ComplianceStatus.UNDER_REVIEW:
            raise ValueError("Legal review already in progress")

        self._status = ComplianceStatus.UNDER_REVIEW
        self._updated_at = datetime.utcnow()

        self.publicar_evento(LegalReviewRequested(
            event_id=str(uuid4()),
            occurred_on=datetime.utcnow(),
            partner_id=self._partner_id,
            document_type=self._document_type,
            jurisdiction=self._jurisdiction,
            priority=priority,
            requested_by=requested_by
        ))

    def complete_legal_review(self, reviewed_by: str, status: ComplianceStatus):
        if self._status != ComplianceStatus.UNDER_REVIEW:
            raise ValueError("No active legal review to complete")

        self._status = status
        self._reviewed_by = reviewed_by
        self._reviewed_at = datetime.utcnow()
        self._updated_at = datetime.utcnow()

    def _update_overall_status(self):
        if not self._compliance_checks:
            return

        # Get latest check for each requirement
        latest_checks = {}
        for check in self._compliance_checks:
            if (check.requirement_id not in latest_checks or
                check.performed_at > latest_checks[check.requirement_id].performed_at):
                latest_checks[check.requirement_id] = check

        # Determine overall status
        has_non_compliant = False
        has_pending = False

        for check in latest_checks.values():
            if check.status == ComplianceStatus.NON_COMPLIANT:
                has_non_compliant = True
            elif check.status == ComplianceStatus.PENDING:
                has_pending = True

        if has_non_compliant:
            self._status = ComplianceStatus.NON_COMPLIANT
        elif has_pending:
            self._status = ComplianceStatus.PENDING
        else:
            self._status = ComplianceStatus.COMPLIANT

    def get_compliance_summary(self) -> Dict[str, Any]:
        latest_checks = {}
        for check in self._compliance_checks:
            if (check.requirement_id not in latest_checks or
                check.performed_at > latest_checks[check.requirement_id].performed_at):
                latest_checks[check.requirement_id] = check

        total_requirements = len(self._legal_requirements)
        compliant_count = sum(1 for check in latest_checks.values() if check.status == ComplianceStatus.COMPLIANT)
        non_compliant_count = sum(1 for check in latest_checks.values() if check.status == ComplianceStatus.NON_COMPLIANT)
        pending_count = total_requirements - len(latest_checks)

        return {
            "total_requirements": total_requirements,
            "compliant": compliant_count,
            "non_compliant": non_compliant_count,
            "pending": pending_count,
            "compliance_percentage": (compliant_count / total_requirements * 100) if total_requirements > 0 else 0,
            "overall_status": self._status.value,
            "overall_risk_level": self.overall_risk_level.value
        }

    @classmethod
    def from_events(cls, events: List[DomainEvent]) -> 'LegalDocument':
        raise NotImplementedError("LegalDocument event sourcing not fully implemented")


class LegalComplianceManager(AggregateRoot):
    def __init__(self, partner_id: str, jurisdiction: Jurisdiction):
        super().__init__()
        self.id = str(uuid4())
        self._partner_id = partner_id
        self._jurisdiction = jurisdiction
        self._legal_documents: Dict[LegalDocumentType, LegalDocument] = {}
        self._compliance_status = ComplianceStatus.PENDING
        self._created_at = datetime.utcnow()
        self._last_compliance_review: Optional[datetime] = None

    @property
    def partner_id(self) -> str:
        return self._partner_id

    @property
    def jurisdiction(self) -> Jurisdiction:
        return self._jurisdiction

    @property
    def compliance_status(self) -> ComplianceStatus:
        return self._compliance_status

    @property
    def legal_documents(self) -> Dict[LegalDocumentType, LegalDocument]:
        return self._legal_documents.copy()

    def add_legal_document(self, document: LegalDocument):
        if document.partner_id != self._partner_id:
            raise ValueError("Document partner ID doesn't match compliance manager")

        if document.jurisdiction != self._jurisdiction:
            raise ValueError("Document jurisdiction doesn't match compliance manager")

        self._legal_documents[document.document_type] = document
        self._update_overall_compliance_status()

    def get_legal_document(self, document_type: LegalDocumentType) -> Optional[LegalDocument]:
        return self._legal_documents.get(document_type)

    def get_overall_compliance_summary(self) -> Dict[str, Any]:
        if not self._legal_documents:
            return {
                "overall_status": ComplianceStatus.PENDING.value,
                "documents_count": 0,
                "compliant_documents": 0,
                "non_compliant_documents": 0,
                "overall_risk_level": RiskLevel.MEDIUM.value,
                "last_review": None,
                "documents": {}
            }

        compliant_count = 0
        non_compliant_count = 0
        risk_levels = []

        documents_summary = {}
        for doc_type, document in self._legal_documents.items():
            doc_summary = document.get_compliance_summary()
            documents_summary[doc_type.value] = doc_summary

            if document.status == ComplianceStatus.COMPLIANT:
                compliant_count += 1
            elif document.status == ComplianceStatus.NON_COMPLIANT:
                non_compliant_count += 1

            risk_levels.append(document.overall_risk_level)

        # Determine overall risk level
        overall_risk = RiskLevel.LOW
        if RiskLevel.CRITICAL in risk_levels:
            overall_risk = RiskLevel.CRITICAL
        elif RiskLevel.HIGH in risk_levels:
            overall_risk = RiskLevel.HIGH
        elif RiskLevel.MEDIUM in risk_levels:
            overall_risk = RiskLevel.MEDIUM

        return {
            "overall_status": self._compliance_status.value,
            "documents_count": len(self._legal_documents),
            "compliant_documents": compliant_count,
            "non_compliant_documents": non_compliant_count,
            "overall_risk_level": overall_risk.value,
            "last_review": self._last_compliance_review.isoformat() if self._last_compliance_review else None,
            "documents": documents_summary
        }

    def _update_overall_compliance_status(self):
        if not self._legal_documents:
            self._compliance_status = ComplianceStatus.PENDING
            return

        has_non_compliant = any(
            doc.status == ComplianceStatus.NON_COMPLIANT 
            for doc in self._legal_documents.values()
        )
        has_pending = any(
            doc.status == ComplianceStatus.PENDING 
            for doc in self._legal_documents.values()
        )

        if has_non_compliant:
            self._compliance_status = ComplianceStatus.NON_COMPLIANT
        elif has_pending:
            self._compliance_status = ComplianceStatus.PENDING
        else:
            self._compliance_status = ComplianceStatus.COMPLIANT

        self._last_compliance_review = datetime.utcnow()

    @classmethod
    def from_events(cls, events: List[DomainEvent]) -> 'LegalComplianceManager':
        raise NotImplementedError("LegalComplianceManager event sourcing not implemented")