from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Optional
from .entidades import DomainEvent, IntegrationEvent


@dataclass
class EventEnvelope:
    event_id: str
    aggregate_id: str
    event_type: str
    event_data: Dict[str, Any]
    version: int
    timestamp: datetime
    correlation_id: Optional[str] = None
    
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
    contract_id: str
    partner_id: str
    contract_type: str
    template_id: str
    
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
    contract_id: str
    updated_terms: Dict[str, Any]
    updated_by: str
    
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
    contract_id: str
    submitted_by: str
    legal_reviewer: str
    
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
    contract_id: str
    partner_id: str
    signatory: str
    signature_method: str
    
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
    contract_id: str
    partner_id: str
    activation_date: datetime
    
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
    negotiation_id: str
    contract_id: str
    initiator: str
    
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
    negotiation_id: str
    proposal_id: str
    proposer: str
    terms: Dict[str, Any]
    
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
    negotiation_id: str
    proposal_id: str
    acceptor: str
    
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
    negotiation_id: str
    contract_id: str
    final_terms: Dict[str, Any]
    
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
    validation_id: str
    contract_id: str
    validator: str
    validation_type: str
    
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
    validation_id: str
    contract_id: str
    result: str
    issues: list
    
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
    document_id: str
    contract_id: str
    document_type: str
    file_path: str
    uploaded_by: str
    
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
    document_id: str
    signature_id: str
    signer: str
    signature_hash: str
    
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
    contract_id: str
    partner_id: str
    contract_type: str
    effective_date: datetime
    
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
    contract_id: str
    partner_id: str
    contract_type: str
    permissions: Dict[str, Any]
    
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
    contract_id: str
    candidate_id: str
    partner_id: str
    position: str
    start_date: datetime
    
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