from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Optional
import uuid
from datetime import datetime


@dataclass
class BaseCommand:
    id: str = None
    timestamp: datetime = None
    user_id: str = None
    
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
    partner_id: str = field()
    contract_type: str = field()
    template_id: str = field()
    initial_terms: Dict[str, Any] = field()


@dataclass
class UpdateContractTerms(BaseCommand):
    contract_id: str = field()
    updated_terms: Dict[str, Any] = field()


@dataclass
class SubmitForLegalReview(BaseCommand):
    contract_id: str = field()
    legal_reviewer: str = field()


@dataclass
class ApprovalLegalReview(BaseCommand):
    contract_id: str = field()
    reviewer: str = field()


@dataclass
class RejectLegalReview(BaseCommand):
    contract_id: str = field()
    reviewer: str = field()
    reason: str = field()


@dataclass
class SignContract(BaseCommand):
    contract_id: str = field()
    signer: str = field()
    signature_method: str = field()
    signature_data: str = field()
    ip_address: Optional[str] = None


@dataclass
class ActivateContract(BaseCommand):
    contract_id: str = field()


@dataclass
class CancelContract(BaseCommand):
    contract_id: str = field()
    reason: str = field()


# Negotiation Commands
@dataclass
class StartNegotiation(BaseCommand):
    contract_id: str = field()
    initiator: str = field()


@dataclass
class SubmitProposal(BaseCommand):
    negotiation_id: str = field()
    proposer: str = field()
    terms: Dict[str, Any] = field()
    message: Optional[str] = None


@dataclass
class AcceptProposal(BaseCommand):
    negotiation_id: str = field()
    proposal_id: str = field()
    acceptor: str = field()


@dataclass
class RejectProposal(BaseCommand):
    negotiation_id: str = field()
    proposal_id: str = field()
    rejector: str = field()
    reason: str = field()


@dataclass
class CompleteNegotiation(BaseCommand):
    negotiation_id: str = field()
    final_terms: Dict[str, Any] = field()


# Legal Commands
@dataclass
class RequestLegalValidation(BaseCommand):
    contract_id: str = field()
    validation_type: str = field()
    validator: str = field()


@dataclass
class CompleteLegalValidation(BaseCommand):
    validation_id: str = field()
    result: str = field()
    issues: list = field()
    recommendations: Optional[str] = None


# Document Commands
@dataclass
class UploadDocument(BaseCommand):
    contract_id: str = field()
    document_type: str = field()
    file_name: str = field()
    file_content: bytes = field()
    content_type: str = field()


@dataclass
class SignDocument(BaseCommand):
    document_id: str = field()
    signer: str = field()
    signature_data: str = field()
    signature_method: str = field()


@dataclass
class ValidateSignature(BaseCommand):
    document_id: str = field()
    signature_id: str = field()