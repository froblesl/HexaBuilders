from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Optional
import uuid
from datetime import datetime


@dataclass
class BaseCommand:
    id: Optional[str] = field(default=None)
    timestamp: Optional[datetime] = field(default=None)
    user_id: Optional[str] = field(default=None)
    
    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())
        if not self.timestamp:
            self.timestamp = datetime.utcnow()


@dataclass
class CommandResult:
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    errors: Optional[Dict[str, str]] = None


class CommandHandler(ABC):
    @abstractmethod
    async def handle(self, command: BaseCommand) -> CommandResult:
        pass


class CommandBus:
    def __init__(self):
        self._handlers: Dict[type, CommandHandler] = {}
    
    def register_handler(self, command_type: type, handler: CommandHandler):
        self._handlers[command_type] = handler
    
    async def execute(self, command: BaseCommand) -> CommandResult:
        command_type = type(command)
        
        if command_type not in self._handlers:
            return CommandResult(
                success=False,
                message=f"No handler registered for command {command_type.__name__}",
                errors={"command": "Handler not found"}
            )
        
        handler = self._handlers[command_type]
        
        try:
            return await handler.handle(command)
        except Exception as e:
            return CommandResult(
                success=False,
                message=f"Error executing command: {str(e)}",
                errors={"execution": str(e)}
            )


# Contract Commands
@dataclass
class CreateContract(BaseCommand):
    partner_id: str = field(default_factory=lambda: "")
    contract_type: str = field(default_factory=lambda: "")
    template_id: str = field(default_factory=lambda: "")
    initial_terms: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UpdateContractTerms(BaseCommand):
    contract_id: str = field(default_factory=lambda: "")
    updated_terms: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SubmitForLegalReview(BaseCommand):
    contract_id: str = field(default_factory=lambda: "")
    legal_reviewer: str = field(default_factory=lambda: "")


@dataclass
class ApprovalLegalReview(BaseCommand):
    contract_id: str = field(default_factory=lambda: "")
    reviewer: str = field(default_factory=lambda: "")


@dataclass
class RejectLegalReview(BaseCommand):
    contract_id: str = field(default_factory=lambda: "")
    reviewer: str = field(default_factory=lambda: "")
    reason: str = field(default_factory=lambda: "")


@dataclass
class SignContract(BaseCommand):
    contract_id: str = field(default_factory=lambda: "")
    signer: str = field(default_factory=lambda: "")
    signature_method: str = field(default_factory=lambda: "")
    signature_data: str = field(default_factory=lambda: "")
    ip_address: Optional[str] = None


@dataclass
class ActivateContract(BaseCommand):
    contract_id: str = field(default_factory=lambda: "")


@dataclass
class CancelContract(BaseCommand):
    contract_id: str = field(default_factory=lambda: "")
    reason: str = field(default_factory=lambda: "")


# Negotiation Commands
@dataclass
class StartNegotiation(BaseCommand):
    contract_id: str = field(default_factory=lambda: "")
    initiator: str = field(default_factory=lambda: "")


@dataclass
class SubmitProposal(BaseCommand):
    negotiation_id: str = field(default_factory=lambda: "")
    proposer: str = field(default_factory=lambda: "")
    terms: Dict[str, Any] = field(default_factory=dict)
    message: Optional[str] = None


@dataclass
class AcceptProposal(BaseCommand):
    negotiation_id: str = field(default_factory=lambda: "")
    proposal_id: str = field(default_factory=lambda: "")
    acceptor: str = field(default_factory=lambda: "")


@dataclass
class RejectProposal(BaseCommand):
    negotiation_id: str = field(default_factory=lambda: "")
    proposal_id: str = field(default_factory=lambda: "")
    rejector: str = field(default_factory=lambda: "")
    reason: str = field(default_factory=lambda: "")


@dataclass
class CompleteNegotiation(BaseCommand):
    negotiation_id: str = field(default_factory=lambda: "")
    final_terms: Dict[str, Any] = field(default_factory=dict)


# Legal Commands
@dataclass
class RequestLegalValidation(BaseCommand):
    contract_id: str = field(default_factory=lambda: "")
    validation_type: str = field(default_factory=lambda: "")
    validator: str = field(default_factory=lambda: "")


@dataclass
class CompleteLegalValidation(BaseCommand):
    validation_id: str = field(default_factory=lambda: "")
    result: str = field(default_factory=lambda: "")
    issues: list = field(default_factory=list)
    recommendations: Optional[str] = None


# Document Commands
@dataclass
class UploadDocument(BaseCommand):
    contract_id: str = field(default_factory=lambda: "")
    document_type: str = field(default_factory=lambda: "")
    file_name: str = field(default_factory=lambda: "")
    file_content: bytes = field(default_factory=bytes)
    content_type: str = field(default_factory=lambda: "")


@dataclass
class SignDocument(BaseCommand):
    document_id: str = field(default_factory=lambda: "")
    signer: str = field(default_factory=lambda: "")
    signature_data: str = field(default_factory=lambda: "")
    signature_method: str = field(default_factory=lambda: "")


@dataclass
class ValidateSignature(BaseCommand):
    document_id: str = field(default_factory=lambda: "")
    signature_id: str = field(default_factory=lambda: "")


# Compatibility aliases for existing imports
Command = BaseCommand