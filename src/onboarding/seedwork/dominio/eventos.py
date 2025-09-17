from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional
from .entidades import DomainEvent, IntegrationEvent


@dataclass
class EventEnvelope:
    event_id: str = field(default_factory=lambda: "")
    aggregate_id: str = field(default_factory=lambda: "")
    event_type: str = field(default_factory=lambda: "")
    event_data: Dict[str, Any] = field(default_factory=dict)
    version: int = field(default_factory=lambda: 0)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    correlation_id: Optional[str] = field(default=None)
    
    def to_cloud_event(self) -> Dict[str, Any]:
        return {
            "specversion": "1.0",
            "type": f"com.hexabuilders.onboarding.{self.event_type}",
            "source": "onboarding-service",
            "id": self.event_id,
            "time": self.timestamp.isoformat(),
            "datacontenttype": "application/json",
            "data": self.event_data,
            "subject": self.aggregate_id,
            "traceid": self.correlation_id
        }


# Contract Domain Events
@dataclass
class ContractCreated(DomainEvent):
    contract_id: str = field(default_factory=lambda: "")
    partner_id: str = field(default_factory=lambda: "")
    contract_type: str = field(default_factory=lambda: "")
    template_id: str = field(default_factory=lambda: "")
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "contract_id": self.contract_id,
            "partner_id": self.partner_id,
            "contract_type": self.contract_type,
            "template_id": self.template_id
        })
        return data


@dataclass
class ContractTermsUpdated(DomainEvent):
    contract_id: str = field(default_factory=lambda: "")
    updated_terms: Dict[str, Any] = field(default_factory=dict)
    updated_by: str = field(default_factory=lambda: "")
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "contract_id": self.contract_id,
            "updated_terms": self.updated_terms,
            "updated_by": self.updated_by
        })
        return data


@dataclass
class ContractSubmittedForLegalReview(DomainEvent):
    contract_id: str = field(default_factory=lambda: "")
    submitted_by: str = field(default_factory=lambda: "")
    legal_reviewer: str = field(default_factory=lambda: "")
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "contract_id": self.contract_id,
            "submitted_by": self.submitted_by,
            "legal_reviewer": self.legal_reviewer
        })
        return data


@dataclass
class ContractSigned(DomainEvent):
    contract_id: str = field(default_factory=lambda: "")
    partner_id: str = field(default_factory=lambda: "")
    signatory: str = field(default_factory=lambda: "")
    signature_method: str = field(default_factory=lambda: "")
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "contract_id": self.contract_id,
            "partner_id": self.partner_id,
            "signatory": self.signatory,
            "signature_method": self.signature_method
        })
        return data


@dataclass
class ContractActivated(DomainEvent):
    contract_id: str = field(default_factory=lambda: "")
    partner_id: str = field(default_factory=lambda: "")
    activation_date: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "contract_id": self.contract_id,
            "partner_id": self.partner_id,
            "activation_date": self.activation_date.isoformat()
        })
        return data


# Negotiation Domain Events
@dataclass
class NegotiationStarted(DomainEvent):
    negotiation_id: str = field(default_factory=lambda: "")
    contract_id: str = field(default_factory=lambda: "")
    initiator: str = field(default_factory=lambda: "")
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "negotiation_id": self.negotiation_id,
            "contract_id": self.contract_id,
            "initiator": self.initiator
        })
        return data


@dataclass
class ProposalSubmitted(DomainEvent):
    negotiation_id: str = field(default_factory=lambda: "")
    proposal_id: str = field(default_factory=lambda: "")
    proposer: str = field(default_factory=lambda: "")
    terms: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "negotiation_id": self.negotiation_id,
            "proposal_id": self.proposal_id,
            "proposer": self.proposer,
            "terms": self.terms
        })
        return data


@dataclass
class ProposalAccepted(DomainEvent):
    negotiation_id: str = field(default_factory=lambda: "")
    proposal_id: str = field(default_factory=lambda: "")
    acceptor: str = field(default_factory=lambda: "")
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "negotiation_id": self.negotiation_id,
            "proposal_id": self.proposal_id,
            "acceptor": self.acceptor
        })
        return data


@dataclass
class NegotiationCompleted(DomainEvent):
    negotiation_id: str = field(default_factory=lambda: "")
    contract_id: str = field(default_factory=lambda: "")
    final_terms: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "negotiation_id": self.negotiation_id,
            "contract_id": self.contract_id,
            "final_terms": self.final_terms
        })
        return data


# Legal Domain Events
@dataclass
class LegalValidationRequested(DomainEvent):
    validation_id: str = field(default_factory=lambda: "")
    contract_id: str = field(default_factory=lambda: "")
    validator: str = field(default_factory=lambda: "")
    validation_type: str = field(default_factory=lambda: "")
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "validation_id": self.validation_id,
            "contract_id": self.contract_id,
            "validator": self.validator,
            "validation_type": self.validation_type
        })
        return data


@dataclass
class LegalValidationCompleted(DomainEvent):
    validation_id: str = field(default_factory=lambda: "")
    contract_id: str = field(default_factory=lambda: "")
    result: str = field(default_factory=lambda: "")
    issues: list = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "validation_id": self.validation_id,
            "contract_id": self.contract_id,
            "result": self.result,
            "issues": self.issues
        })
        return data


# Document Domain Events
@dataclass
class DocumentUploaded(DomainEvent):
    document_id: str = field(default_factory=lambda: "")
    contract_id: str = field(default_factory=lambda: "")
    document_type: str = field(default_factory=lambda: "")
    file_path: str = field(default_factory=lambda: "")
    uploaded_by: str = field(default_factory=lambda: "")
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "document_id": self.document_id,
            "contract_id": self.contract_id,
            "document_type": self.document_type,
            "file_path": self.file_path,
            "uploaded_by": self.uploaded_by
        })
        return data


@dataclass
class DocumentSigned(DomainEvent):
    document_id: str = field(default_factory=lambda: "")
    signature_id: str = field(default_factory=lambda: "")
    signer: str = field(default_factory=lambda: "")
    signature_hash: str = field(default_factory=lambda: "")
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "document_id": self.document_id,
            "signature_id": self.signature_id,
            "signer": self.signer,
            "signature_hash": self.signature_hash
        })
        return data


# Integration Events
@dataclass
class ContractSignedIntegrationEvent(IntegrationEvent):
    contract_id: str = field(default_factory=lambda: "")
    partner_id: str = field(default_factory=lambda: "")
    contract_type: str = field(default_factory=lambda: "")
    effective_date: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "contract_id": self.contract_id,
            "partner_id": self.partner_id,
            "contract_type": self.contract_type,
            "effective_date": self.effective_date.isoformat()
        })
        return data


@dataclass
class ContractActivatedIntegrationEvent(IntegrationEvent):
    contract_id: str = field(default_factory=lambda: "")
    partner_id: str = field(default_factory=lambda: "")
    contract_type: str = field(default_factory=lambda: "")
    permissions: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "contract_id": self.contract_id,
            "partner_id": self.partner_id,
            "contract_type": self.contract_type,
            "permissions": self.permissions
        })
        return data


@dataclass
class EmploymentContractSignedIntegrationEvent(IntegrationEvent):
    contract_id: str = field(default_factory=lambda: "")
    candidate_id: str = field(default_factory=lambda: "")
    partner_id: str = field(default_factory=lambda: "")
    position: str = field(default_factory=lambda: "")
    start_date: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "contract_id": self.contract_id,
            "candidate_id": self.candidate_id,
            "partner_id": self.partner_id,
            "position": self.position,
            "start_date": self.start_date.isoformat()
        })
        return data