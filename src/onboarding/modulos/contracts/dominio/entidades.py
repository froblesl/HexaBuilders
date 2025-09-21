from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, List, Optional
from enum import Enum

from src.onboarding.seedwork.dominio.entidades import AggregateRoot, ValueObject, DomainEvent
from src.onboarding.seedwork.dominio.excepciones import (
    ContractInvalidStateException,
    ContractAlreadySignedException,
    ContractValidationException
)
from src.onboarding.seedwork.dominio.eventos import (
    ContractCreated,
    ContractTermsUpdated,
    ContractSubmittedForLegalReview,
    ContractSigned,
    ContractActivated
)


class ContractState(Enum):
    DRAFT = "DRAFT"
    IN_NEGOTIATION = "IN_NEGOTIATION"
    LEGAL_REVIEW = "LEGAL_REVIEW"
    PENDING_SIGNATURE = "PENDING_SIGNATURE"
    SIGNED = "SIGNED"
    ACTIVE = "ACTIVE"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"
    TERMINATED = "TERMINATED"


class ContractType(Enum):
    STANDARD = "STANDARD"
    PREMIUM = "PREMIUM"
    ENTERPRISE = "ENTERPRISE"
    CUSTOM = "CUSTOM"
    EMPLOYMENT = "EMPLOYMENT"


@dataclass
class ContractTerms(ValueObject):
    commission_rate: float
    payment_terms: str
    termination_clause: str
    liability_limit: float
    intellectual_property: Dict[str, Any]
    data_protection: Dict[str, Any]
    performance_metrics: Dict[str, Any]
    
    def _validate(self):
        if not 0 <= self.commission_rate <= 1:
            raise ContractValidationException("Commission rate must be between 0 and 1")
        
        if self.liability_limit < 0:
            raise ContractValidationException("Liability limit cannot be negative")
        
        if not self.payment_terms:
            raise ContractValidationException("Payment terms cannot be empty")


@dataclass
class Signature(ValueObject):
    signer: str
    signature_method: str
    signature_data: str
    timestamp: datetime
    ip_address: Optional[str] = None
    
    def _validate(self):
        if not self.signer:
            raise ContractValidationException("Signer cannot be empty")
        
        if not self.signature_data:
            raise ContractValidationException("Signature data cannot be empty")
        
        if self.signature_method not in ["digital", "electronic", "wet"]:
            raise ContractValidationException("Invalid signature method")


class Contract(AggregateRoot):
    def __init__(self, contract_id: str = None):
        super().__init__()
        if contract_id:
            self._id = contract_id
        self._partner_id: Optional[str] = None
        self._contract_type: Optional[ContractType] = None
        self._template_id: Optional[str] = None
        self._state: ContractState = ContractState.DRAFT
        self._terms: Optional[ContractTerms] = None
        self._legal_reviewer: Optional[str] = None
        self._signatures: List[Signature] = []
        self._created_at: Optional[datetime] = None
        self._updated_at: Optional[datetime] = None
        self._signed_at: Optional[datetime] = None
        self._activated_at: Optional[datetime] = None
        self._metadata: Dict[str, Any] = {}
    
    @property
    def partner_id(self) -> str:
        return self._partner_id
    
    @property
    def contract_type(self) -> ContractType:
        return self._contract_type
    
    @property
    def template_id(self) -> str:
        return self._template_id
    
    @property
    def state(self) -> ContractState:
        return self._state
    
    @property
    def terms(self) -> ContractTerms:
        return self._terms
    
    @property
    def signatures(self) -> List[Signature]:
        return self._signatures.copy()
    
    @property
    def is_signed(self) -> bool:
        return self._state in [ContractState.SIGNED, ContractState.ACTIVE]
    
    @property
    def is_active(self) -> bool:
        return self._state == ContractState.ACTIVE
    
    @classmethod
    def create_contract(
        cls,
        partner_id: str,
        contract_type: ContractType,
        template_id: str,
        initial_terms: Dict[str, Any]
    ) -> 'Contract':
        contract = cls()
        contract._partner_id = partner_id
        contract._contract_type = contract_type
        contract._template_id = template_id
        contract._created_at = datetime.utcnow()
        contract._updated_at = contract._created_at
        
        # Convert dict to ContractTerms
        terms = ContractTerms(**initial_terms)
        contract._terms = terms
        
        contract.publicar_evento(
            ContractCreated(
                contract_id=contract.id,
                partner_id=partner_id,
                contract_type=contract_type.value,
                template_id=template_id
            )
        )
        
        contract._increment_version()
        return contract
    
    def update_terms(self, new_terms: Dict[str, Any], updated_by: str):
        if self.is_signed:
            raise ContractAlreadySignedException(
                f"Cannot update terms of signed contract {self.id}"
            )
        
        if self._state not in [ContractState.DRAFT, ContractState.IN_NEGOTIATION]:
            raise ContractInvalidStateException(
                f"Cannot update terms in state {self._state.value}"
            )
        
        # Merge existing terms with new terms
        current_terms_dict = {
            "commission_rate": self._terms.commission_rate,
            "payment_terms": self._terms.payment_terms,
            "termination_clause": self._terms.termination_clause,
            "liability_limit": self._terms.liability_limit,
            "intellectual_property": self._terms.intellectual_property,
            "data_protection": self._terms.data_protection,
            "performance_metrics": self._terms.performance_metrics
        }
        
        current_terms_dict.update(new_terms)
        self._terms = ContractTerms(**current_terms_dict)
        self._updated_at = datetime.utcnow()
        
        self.publicar_evento(
            ContractTermsUpdated(
                contract_id=self.id,
                updated_terms=new_terms,
                updated_by=updated_by
            )
        )
        
        self._increment_version()
    
    def start_negotiation(self):
        if self._state != ContractState.DRAFT:
            raise ContractInvalidStateException(
                f"Cannot start negotiation from state {self._state.value}"
            )
        
        self._state = ContractState.IN_NEGOTIATION
        self._updated_at = datetime.utcnow()
        self._increment_version()
    
    def submit_for_legal_review(self, submitted_by: str, legal_reviewer: str):
        if self._state not in [ContractState.DRAFT, ContractState.IN_NEGOTIATION]:
            raise ContractInvalidStateException(
                f"Cannot submit for legal review from state {self._state.value}"
            )
        
        self._state = ContractState.LEGAL_REVIEW
        self._legal_reviewer = legal_reviewer
        self._updated_at = datetime.utcnow()
        
        self.publicar_evento(
            ContractSubmittedForLegalReview(
                contract_id=self.id,
                submitted_by=submitted_by,
                legal_reviewer=legal_reviewer
            )
        )
        
        self._increment_version()
    
    def approve_legal_review(self):
        if self._state != ContractState.LEGAL_REVIEW:
            raise ContractInvalidStateException(
                f"Cannot approve legal review from state {self._state.value}"
            )
        
        self._state = ContractState.PENDING_SIGNATURE
        self._updated_at = datetime.utcnow()
        self._increment_version()
    
    def reject_legal_review(self, reason: str):
        if self._state != ContractState.LEGAL_REVIEW:
            raise ContractInvalidStateException(
                f"Cannot reject legal review from state {self._state.value}"
            )
        
        self._state = ContractState.DRAFT
        self._metadata["legal_rejection_reason"] = reason
        self._updated_at = datetime.utcnow()
        self._increment_version()
    
    def sign_contract(
        self,
        signer: str,
        signature_method: str,
        signature_data: str,
        ip_address: str = None
    ):
        if self._state != ContractState.PENDING_SIGNATURE:
            raise ContractInvalidStateException(
                f"Cannot sign contract in state {self._state.value}"
            )
        
        signature = Signature(
            signer=signer,
            signature_method=signature_method,
            signature_data=signature_data,
            timestamp=datetime.utcnow(),
            ip_address=ip_address
        )
        
        self._signatures.append(signature)
        self._state = ContractState.SIGNED
        self._signed_at = datetime.utcnow()
        self._updated_at = self._signed_at
        
        self.publicar_evento(
            ContractSigned(
                contract_id=self.id,
                partner_id=self._partner_id,
                signatory=signer,
                signature_method=signature_method
            )
        )
        
        self._increment_version()
    
    def activate_contract(self):
        if self._state != ContractState.SIGNED:
            raise ContractInvalidStateException(
                f"Cannot activate contract in state {self._state.value}"
            )
        
        self._state = ContractState.ACTIVE
        self._activated_at = datetime.utcnow()
        self._updated_at = self._activated_at
        
        self.publicar_evento(
            ContractActivated(
                contract_id=self.id,
                partner_id=self._partner_id,
                activation_date=self._activated_at
            )
        )
        
        self._increment_version()
    
    def cancel_contract(self, reason: str):
        if self._state in [ContractState.ACTIVE, ContractState.EXPIRED, ContractState.TERMINATED]:
            raise ContractInvalidStateException(
                f"Cannot cancel contract in state {self._state.value}"
            )
        
        self._state = ContractState.CANCELLED
        self._metadata["cancellation_reason"] = reason
        self._updated_at = datetime.utcnow()
        self._increment_version()
    
    def terminate_contract(self, reason: str):
        if self._state != ContractState.ACTIVE:
            raise ContractInvalidStateException(
                f"Cannot terminate contract in state {self._state.value}"
            )
        
        self._state = ContractState.TERMINATED
        self._metadata["termination_reason"] = reason
        self._updated_at = datetime.utcnow()
        self._increment_version()
    
    @classmethod
    def from_events(cls, events: List[DomainEvent]) -> 'Contract':
        contract = cls()
        
        for event in events:
            if isinstance(event, ContractCreated):
                contract._partner_id = event.partner_id
                contract._contract_type = ContractType(event.contract_type)
                contract._template_id = event.template_id
                contract._created_at = event.timestamp
                contract._updated_at = event.timestamp
                contract._state = ContractState.DRAFT
            
            elif isinstance(event, ContractTermsUpdated):
                # Apply terms update logic
                contract._updated_at = event.timestamp
            
            elif isinstance(event, ContractSubmittedForLegalReview):
                contract._state = ContractState.LEGAL_REVIEW
                contract._legal_reviewer = event.legal_reviewer
                contract._updated_at = event.timestamp
            
            elif isinstance(event, ContractSigned):
                contract._state = ContractState.SIGNED
                contract._signed_at = event.timestamp
                contract._updated_at = event.timestamp
            
            elif isinstance(event, ContractActivated):
                contract._state = ContractState.ACTIVE
                contract._activated_at = event.activation_date
                contract._updated_at = event.timestamp
            
            contract._increment_version()
        
        return contract


@dataclass
class ContractTemplate(ValueObject):
    template_id: str
    name: str
    contract_type: ContractType
    default_terms: Dict[str, Any]
    required_fields: List[str]
    optional_fields: List[str]
    
    def _validate(self):
        if not self.template_id:
            raise ContractValidationException("Template ID cannot be empty")
        
        if not self.name:
            raise ContractValidationException("Template name cannot be empty")
        
        if not self.default_terms:
            raise ContractValidationException("Default terms cannot be empty")


@dataclass
class ContractVersion(ValueObject):
    version_id: str
    contract_id: str
    version_number: int
    terms: ContractTerms
    changes: Dict[str, Any]
    created_by: str
    created_at: datetime
    
    def _validate(self):
        if self.version_number < 1:
            raise ContractValidationException("Version number must be positive")
        
        if not self.created_by:
            raise ContractValidationException("Created by cannot be empty")