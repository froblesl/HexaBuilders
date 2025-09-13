from typing import Dict, Any
from datetime import datetime

from onboarding.seedwork.aplicacion.comandos import CommandHandler, CommandResult
from onboarding.seedwork.aplicacion.queries import QueryHandler, QueryResult
from onboarding.seedwork.dominio.entidades import EventStore
from onboarding.modulos.contracts.dominio.entidades import Contract, ContractType
from onboarding.modulos.contracts.dominio.repositorios import (
    ContractRepository, 
    ContractTemplateRepository
)
from onboarding.seedwork.dominio.excepciones import (
    ContractNotFoundException,
    ContractValidationException
)
from onboarding.seedwork.aplicacion.comandos import (
    CreateContract,
    UpdateContractTerms,
    SubmitForLegalReview,
    ApprovalLegalReview,
    RejectLegalReview,
    SignContract,
    ActivateContract,
    CancelContract
)
from onboarding.seedwork.aplicacion.queries import (
    GetContract,
    GetContractsByPartner,
    SearchContracts,
    GetContractHistory,
    GetContractTemplates,
    GetContractTemplate
)


class CreateContractHandler(CommandHandler):
    def __init__(
        self, 
        contract_repository: ContractRepository,
        template_repository: ContractTemplateRepository,
        event_store: EventStore
    ):
        self.contract_repository = contract_repository
        self.template_repository = template_repository
        self.event_store = event_store
    
    async def handle(self, command: CreateContract) -> CommandResult:
        try:
            # Validate template exists
            template = await self.template_repository.get_by_id(command.template_id)
            if not template:
                return CommandResult(
                    success=False,
                    message="Template not found",
                    errors={"template_id": "Invalid template ID"}
                )
            
            # Create contract
            contract = Contract.create_contract(
                partner_id=command.partner_id,
                contract_type=ContractType(command.contract_type),
                template_id=command.template_id,
                initial_terms=command.initial_terms
            )
            
            # Save to repository
            await self.contract_repository.save(contract)
            
            # Save events to event store
            await self.event_store.save_events(
                aggregate_id=contract.id,
                events=contract.eventos,
                expected_version=contract.version - len(contract.eventos)
            )
            
            contract.marcar_eventos_como_procesados()
            
            return CommandResult(
                success=True,
                message="Contract created successfully",
                data={"contract_id": contract.id}
            )
            
        except ContractValidationException as e:
            return CommandResult(
                success=False,
                message=str(e),
                errors={"validation": str(e)}
            )
        except Exception as e:
            return CommandResult(
                success=False,
                message=f"Unexpected error: {str(e)}",
                errors={"system": str(e)}
            )


class UpdateContractTermsHandler(CommandHandler):
    def __init__(self, contract_repository: ContractRepository, event_store: EventStore):
        self.contract_repository = contract_repository
        self.event_store = event_store
    
    async def handle(self, command: UpdateContractTerms) -> CommandResult:
        try:
            contract = await self.contract_repository.get_by_id(command.contract_id)
            if not contract:
                return CommandResult(
                    success=False,
                    message="Contract not found",
                    errors={"contract_id": "Contract does not exist"}
                )
            
            contract.update_terms(command.updated_terms, command.user_id)
            
            await self.contract_repository.save(contract)
            await self.event_store.save_events(
                aggregate_id=contract.id,
                events=contract.eventos,
                expected_version=contract.version - len(contract.eventos)
            )
            
            contract.marcar_eventos_como_procesados()
            
            return CommandResult(
                success=True,
                message="Contract terms updated successfully"
            )
            
        except Exception as e:
            return CommandResult(
                success=False,
                message=f"Error updating contract terms: {str(e)}",
                errors={"system": str(e)}
            )


class SubmitForLegalReviewHandler(CommandHandler):
    def __init__(self, contract_repository: ContractRepository, event_store: EventStore):
        self.contract_repository = contract_repository
        self.event_store = event_store
    
    async def handle(self, command: SubmitForLegalReview) -> CommandResult:
        try:
            contract = await self.contract_repository.get_by_id(command.contract_id)
            if not contract:
                return CommandResult(
                    success=False,
                    message="Contract not found",
                    errors={"contract_id": "Contract does not exist"}
                )
            
            contract.submit_for_legal_review(command.user_id, command.legal_reviewer)
            
            await self.contract_repository.save(contract)
            await self.event_store.save_events(
                aggregate_id=contract.id,
                events=contract.eventos,
                expected_version=contract.version - len(contract.eventos)
            )
            
            contract.marcar_eventos_como_procesados()
            
            return CommandResult(
                success=True,
                message="Contract submitted for legal review"
            )
            
        except Exception as e:
            return CommandResult(
                success=False,
                message=f"Error submitting for legal review: {str(e)}",
                errors={"system": str(e)}
            )


class ApproveLegalReviewHandler(CommandHandler):
    def __init__(self, contract_repository: ContractRepository, event_store: EventStore):
        self.contract_repository = contract_repository
        self.event_store = event_store
    
    async def handle(self, command: ApprovalLegalReview) -> CommandResult:
        try:
            contract = await self.contract_repository.get_by_id(command.contract_id)
            if not contract:
                return CommandResult(
                    success=False,
                    message="Contract not found",
                    errors={"contract_id": "Contract does not exist"}
                )
            
            contract.approve_legal_review()
            
            await self.contract_repository.save(contract)
            await self.event_store.save_events(
                aggregate_id=contract.id,
                events=contract.eventos,
                expected_version=contract.version - len(contract.eventos)
            )
            
            contract.marcar_eventos_como_procesados()
            
            return CommandResult(
                success=True,
                message="Legal review approved"
            )
            
        except Exception as e:
            return CommandResult(
                success=False,
                message=f"Error approving legal review: {str(e)}",
                errors={"system": str(e)}
            )


class SignContractHandler(CommandHandler):
    def __init__(self, contract_repository: ContractRepository, event_store: EventStore):
        self.contract_repository = contract_repository
        self.event_store = event_store
    
    async def handle(self, command: SignContract) -> CommandResult:
        try:
            contract = await self.contract_repository.get_by_id(command.contract_id)
            if not contract:
                return CommandResult(
                    success=False,
                    message="Contract not found",
                    errors={"contract_id": "Contract does not exist"}
                )
            
            contract.sign_contract(
                signer=command.signer,
                signature_method=command.signature_method,
                signature_data=command.signature_data,
                ip_address=command.ip_address
            )
            
            await self.contract_repository.save(contract)
            await self.event_store.save_events(
                aggregate_id=contract.id,
                events=contract.eventos,
                expected_version=contract.version - len(contract.eventos)
            )
            
            contract.marcar_eventos_como_procesados()
            
            return CommandResult(
                success=True,
                message="Contract signed successfully"
            )
            
        except Exception as e:
            return CommandResult(
                success=False,
                message=f"Error signing contract: {str(e)}",
                errors={"system": str(e)}
            )


class ActivateContractHandler(CommandHandler):
    def __init__(self, contract_repository: ContractRepository, event_store: EventStore):
        self.contract_repository = contract_repository
        self.event_store = event_store
    
    async def handle(self, command: ActivateContract) -> CommandResult:
        try:
            contract = await self.contract_repository.get_by_id(command.contract_id)
            if not contract:
                return CommandResult(
                    success=False,
                    message="Contract not found",
                    errors={"contract_id": "Contract does not exist"}
                )
            
            contract.activate_contract()
            
            await self.contract_repository.save(contract)
            await self.event_store.save_events(
                aggregate_id=contract.id,
                events=contract.eventos,
                expected_version=contract.version - len(contract.eventos)
            )
            
            contract.marcar_eventos_como_procesados()
            
            return CommandResult(
                success=True,
                message="Contract activated successfully"
            )
            
        except Exception as e:
            return CommandResult(
                success=False,
                message=f"Error activating contract: {str(e)}",
                errors={"system": str(e)}
            )


# Query Handlers
class GetContractHandler(QueryHandler):
    def __init__(self, contract_repository: ContractRepository):
        self.contract_repository = contract_repository
    
    async def handle(self, query: GetContract) -> QueryResult:
        try:
            contract = await self.contract_repository.get_by_id(query.contract_id)
            if not contract:
                return QueryResult(
                    success=False,
                    message="Contract not found"
                )
            
            return QueryResult(
                success=True,
                data={
                    "id": contract.id,
                    "partner_id": contract.partner_id,
                    "contract_type": contract.contract_type.value,
                    "state": contract.state.value,
                    "terms": {
                        "commission_rate": contract.terms.commission_rate,
                        "payment_terms": contract.terms.payment_terms,
                        "termination_clause": contract.terms.termination_clause,
                        "liability_limit": contract.terms.liability_limit
                    },
                    "is_signed": contract.is_signed,
                    "is_active": contract.is_active,
                    "signatures": [
                        {
                            "signer": sig.signer,
                            "method": sig.signature_method,
                            "timestamp": sig.timestamp.isoformat()
                        } for sig in contract.signatures
                    ]
                }
            )
            
        except Exception as e:
            return QueryResult(
                success=False,
                message=f"Error retrieving contract: {str(e)}"
            )


class GetContractsByPartnerHandler(QueryHandler):
    def __init__(self, contract_repository: ContractRepository):
        self.contract_repository = contract_repository
    
    async def handle(self, query: GetContractsByPartner) -> QueryResult:
        try:
            contracts = await self.contract_repository.get_by_partner_id(query.partner_id)
            
            if not query.include_inactive:
                contracts = [c for c in contracts if c.is_active]
            
            return QueryResult(
                success=True,
                data={
                    "contracts": [
                        {
                            "id": contract.id,
                            "contract_type": contract.contract_type.value,
                            "state": contract.state.value,
                            "is_active": contract.is_active,
                            "is_signed": contract.is_signed
                        } for contract in contracts
                    ]
                }
            )
            
        except Exception as e:
            return QueryResult(
                success=False,
                message=f"Error retrieving contracts: {str(e)}"
            )


class SearchContractsHandler(QueryHandler):
    def __init__(self, contract_repository: ContractRepository):
        self.contract_repository = contract_repository
    
    async def handle(self, query: SearchContracts) -> QueryResult:
        try:
            contracts = await self.contract_repository.search(query.filters)
            
            return QueryResult(
                success=True,
                data={
                    "contracts": [
                        {
                            "id": contract.id,
                            "partner_id": contract.partner_id,
                            "contract_type": contract.contract_type.value,
                            "state": contract.state.value,
                            "is_active": contract.is_active,
                            "is_signed": contract.is_signed
                        } for contract in contracts
                    ],
                    "total": len(contracts)
                }
            )
            
        except Exception as e:
            return QueryResult(
                success=False,
                message=f"Error searching contracts: {str(e)}"
            )