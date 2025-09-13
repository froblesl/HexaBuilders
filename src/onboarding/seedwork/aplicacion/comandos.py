from abc import ABC, abstractmethod
from dataclasses import dataclass
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
    partner_id: str
    contract_type: str
    template_id: str
    initial_terms: Dict[str, Any]


@dataclass
class UpdateContractTerms(BaseCommand):
    contract_id: str
    updated_terms: Dict[str, Any]


@dataclass
class SubmitForLegalReview(BaseCommand):
    contract_id: str
    legal_reviewer: str


@dataclass
class ApprovalLegalReview(BaseCommand):
    contract_id: str
    reviewer: str


@dataclass
class RejectLegalReview(BaseCommand):
    contract_id: str
    reviewer: str
    reason: str


@dataclass
class SignContract(BaseCommand):
    contract_id: str
    signer: str
    signature_method: str
    signature_data: str
    ip_address: Optional[str] = None


@dataclass
class ActivateContract(BaseCommand):
    contract_id: str


@dataclass
class CancelContract(BaseCommand):
    contract_id: str
    reason: str


# Negotiation Commands
@dataclass
class StartNegotiation(BaseCommand):
    contract_id: str
    initiator: str


@dataclass
class SubmitProposal(BaseCommand):
    negotiation_id: str
    proposer: str
    terms: Dict[str, Any]
    message: Optional[str] = None


@dataclass
class AcceptProposal(BaseCommand):
    negotiation_id: str
    proposal_id: str
    acceptor: str


@dataclass
class RejectProposal(BaseCommand):
    negotiation_id: str
    proposal_id: str
    rejector: str
    reason: str


@dataclass
class CompleteNegotiation(BaseCommand):
    negotiation_id: str
    final_terms: Dict[str, Any]


# Legal Commands
@dataclass
class RequestLegalValidation(BaseCommand):
    contract_id: str
    validation_type: str
    validator: str


@dataclass
class CompleteLegalValidation(BaseCommand):
    validation_id: str
    result: str
    issues: list
    recommendations: Optional[str] = None


# Document Commands
@dataclass
class UploadDocument(BaseCommand):
    contract_id: str
    document_type: str
    file_name: str
    file_content: bytes
    content_type: str


@dataclass
class SignDocument(BaseCommand):
    document_id: str
    signer: str
    signature_data: str
    signature_method: str


@dataclass
class ValidateSignature(BaseCommand):
    document_id: str
    signature_id: str