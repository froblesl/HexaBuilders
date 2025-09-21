from typing import List, Optional, Dict, Any
from sqlalchemy import Column, String, DateTime, Text, Enum as SqlEnum, Float, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from datetime import datetime
import json

from src.onboarding.modulos.contracts.dominio.entidades import Contract, ContractState, ContractType, ContractTerms, Signature
from src.onboarding.modulos.contracts.dominio.repositorios import ContractRepository, ContractTemplateRepository
from src.onboarding.seedwork.infraestructura.event_store import SqlAlchemyEventStore


Base = declarative_base()


class ContractModel(Base):
    __tablename__ = 'contracts'
    
    id = Column(String, primary_key=True)
    partner_id = Column(String, nullable=False, index=True)
    contract_type = Column(SqlEnum(ContractType), nullable=False)
    template_id = Column(String, nullable=False)
    state = Column(SqlEnum(ContractState), nullable=False, default=ContractState.DRAFT)
    terms_json = Column(Text, nullable=True)
    legal_reviewer = Column(String, nullable=True)
    signatures_json = Column(Text, nullable=True)
    metadata_json = Column(Text, nullable=True)
    version = Column(String, nullable=False, default="1")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    signed_at = Column(DateTime, nullable=True)
    activated_at = Column(DateTime, nullable=True)


class ContractTemplateModel(Base):
    __tablename__ = 'contract_templates'
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    contract_type = Column(SqlEnum(ContractType), nullable=False)
    default_terms_json = Column(Text, nullable=False)
    required_fields_json = Column(Text, nullable=False)
    optional_fields_json = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class SqlAlchemyContractRepository(ContractRepository):
    def __init__(self, session: Session, event_store: SqlAlchemyEventStore):
        self.session = session
        self.event_store = event_store
    
    async def save(self, contract: Contract):
        """Save contract to database"""
        try:
            # Convert contract to model
            contract_model = self._contract_to_model(contract)
            
            # Check if exists
            existing = self.session.query(ContractModel).filter(
                ContractModel.id == contract.id
            ).first()
            
            if existing:
                # Update existing
                existing.state = contract_model.state
                existing.terms_json = contract_model.terms_json
                existing.legal_reviewer = contract_model.legal_reviewer
                existing.signatures_json = contract_model.signatures_json
                existing.metadata_json = contract_model.metadata_json
                existing.updated_at = datetime.utcnow()
                existing.signed_at = contract_model.signed_at
                existing.activated_at = contract_model.activated_at
            else:
                # Create new
                self.session.add(contract_model)
            
            self.session.commit()
            
        except Exception as e:
            self.session.rollback()
            raise Exception(f"Failed to save contract: {str(e)}")
    
    async def get_by_id(self, contract_id: str) -> Optional[Contract]:
        """Retrieve contract by ID using event sourcing"""
        try:
            # Get events from event store
            events = await self.event_store.get_events(contract_id)
            
            if not events:
                return None
            
            # Reconstruct contract from events
            contract = Contract.from_events(events)
            return contract
            
        except Exception as e:
            raise Exception(f"Failed to retrieve contract: {str(e)}")
    
    async def get_by_partner_id(self, partner_id: str) -> List[Contract]:
        """Get all contracts for a partner"""
        try:
            contract_models = self.session.query(ContractModel).filter(
                ContractModel.partner_id == partner_id
            ).all()
            
            contracts = []
            for model in contract_models:
                # Get full contract using event sourcing
                contract = await self.get_by_id(model.id)
                if contract:
                    contracts.append(contract)
            
            return contracts
            
        except Exception as e:
            raise Exception(f"Failed to retrieve contracts by partner: {str(e)}")
    
    async def search(self, criterios: Dict[str, Any]) -> List[Contract]:
        """Search contracts based on criteria"""
        try:
            query = self.session.query(ContractModel)
            
            if 'state' in criterios:
                query = query.filter(ContractModel.state == ContractState(criterios['state']))
            
            if 'contract_type' in criterios:
                query = query.filter(ContractModel.contract_type == ContractType(criterios['contract_type']))
            
            if 'partner_id' in criterios:
                query = query.filter(ContractModel.partner_id == criterios['partner_id'])
            
            if 'created_from' in criterios:
                query = query.filter(ContractModel.created_at >= criterios['created_from'])
            
            if 'created_to' in criterios:
                query = query.filter(ContractModel.created_at <= criterios['created_to'])
            
            contract_models = query.all()
            
            contracts = []
            for model in contract_models:
                contract = await self.get_by_id(model.id)
                if contract:
                    contracts.append(contract)
            
            return contracts
            
        except Exception as e:
            raise Exception(f"Failed to search contracts: {str(e)}")
    
    async def delete(self, contract_id: str):
        """Delete contract (soft delete by marking as cancelled)"""
        try:
            contract = await self.get_by_id(contract_id)
            if contract:
                contract.cancel_contract("Contract deleted")
                await self.save(contract)
            
        except Exception as e:
            raise Exception(f"Failed to delete contract: {str(e)}")
    
    def _contract_to_model(self, contract: Contract) -> ContractModel:
        """Convert domain contract to database model"""
        terms_json = None
        if contract.terms:
            terms_json = json.dumps({
                'commission_rate': contract.terms.commission_rate,
                'payment_terms': contract.terms.payment_terms,
                'termination_clause': contract.terms.termination_clause,
                'liability_limit': contract.terms.liability_limit,
                'intellectual_property': contract.terms.intellectual_property,
                'data_protection': contract.terms.data_protection,
                'performance_metrics': contract.terms.performance_metrics
            })
        
        signatures_json = None
        if contract.signatures:
            signatures_json = json.dumps([
                {
                    'signer': sig.signer,
                    'signature_method': sig.signature_method,
                    'signature_data': sig.signature_data,
                    'timestamp': sig.timestamp.isoformat(),
                    'ip_address': sig.ip_address
                } for sig in contract.signatures
            ])
        
        return ContractModel(
            id=contract.id,
            partner_id=contract.partner_id,
            contract_type=contract.contract_type,
            template_id=contract.template_id,
            state=contract.state,
            terms_json=terms_json,
            signatures_json=signatures_json,
            version=str(contract.version),
            signed_at=getattr(contract, '_signed_at', None),
            activated_at=getattr(contract, '_activated_at', None)
        )


class SqlAlchemyContractTemplateRepository(ContractTemplateRepository):
    def __init__(self, session: Session):
        self.session = session
    
    async def get_by_id(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Get template by ID"""
        try:
            template = self.session.query(ContractTemplateModel).filter(
                ContractTemplateModel.id == template_id,
                ContractTemplateModel.is_active == True
            ).first()
            
            if not template:
                return None
            
            return {
                'id': template.id,
                'name': template.name,
                'contract_type': template.contract_type.value,
                'default_terms': json.loads(template.default_terms_json),
                'required_fields': json.loads(template.required_fields_json),
                'optional_fields': json.loads(template.optional_fields_json)
            }
            
        except Exception as e:
            raise Exception(f"Failed to retrieve template: {str(e)}")
    
    async def get_by_type(self, contract_type: str) -> List[Dict[str, Any]]:
        """Get templates by contract type"""
        try:
            templates = self.session.query(ContractTemplateModel).filter(
                ContractTemplateModel.contract_type == ContractType(contract_type),
                ContractTemplateModel.is_active == True
            ).all()
            
            return [
                {
                    'id': template.id,
                    'name': template.name,
                    'contract_type': template.contract_type.value,
                    'default_terms': json.loads(template.default_terms_json),
                    'required_fields': json.loads(template.required_fields_json),
                    'optional_fields': json.loads(template.optional_fields_json)
                } for template in templates
            ]
            
        except Exception as e:
            raise Exception(f"Failed to retrieve templates by type: {str(e)}")
    
    async def save(self, template_data: Dict[str, Any]):
        """Save template"""
        try:
            template = ContractTemplateModel(
                id=template_data['id'],
                name=template_data['name'],
                contract_type=ContractType(template_data['contract_type']),
                default_terms_json=json.dumps(template_data['default_terms']),
                required_fields_json=json.dumps(template_data['required_fields']),
                optional_fields_json=json.dumps(template_data['optional_fields'])
            )
            
            self.session.add(template)
            self.session.commit()
            
        except Exception as e:
            self.session.rollback()
            raise Exception(f"Failed to save template: {str(e)}")
    
    async def get_all(self) -> List[Dict[str, Any]]:
        """Get all active templates"""
        try:
            templates = self.session.query(ContractTemplateModel).filter(
                ContractTemplateModel.is_active == True
            ).all()
            
            return [
                {
                    'id': template.id,
                    'name': template.name,
                    'contract_type': template.contract_type.value,
                    'default_terms': json.loads(template.default_terms_json),
                    'required_fields': json.loads(template.required_fields_json),
                    'optional_fields': json.loads(template.optional_fields_json)
                } for template in templates
            ]
            
        except Exception as e:
            raise Exception(f"Failed to retrieve all templates: {str(e)}")