from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from .entidades import Contract, ContractTemplate, ContractVersion


class ContractRepository(ABC):
    @abstractmethod
    async def save(self, contract: Contract):
        pass
    
    @abstractmethod
    async def get_by_id(self, contract_id: str) -> Optional[Contract]:
        pass
    
    @abstractmethod
    async def get_by_partner_id(self, partner_id: str) -> List[Contract]:
        pass
    
    @abstractmethod
    async def search(self, criterios: Dict[str, Any]) -> List[Contract]:
        pass
    
    @abstractmethod
    async def delete(self, contract_id: str):
        pass


class ContractTemplateRepository(ABC):
    @abstractmethod
    async def get_by_id(self, template_id: str) -> Optional[ContractTemplate]:
        pass
    
    @abstractmethod
    async def get_by_type(self, contract_type: str) -> List[ContractTemplate]:
        pass
    
    @abstractmethod
    async def save(self, template: ContractTemplate):
        pass
    
    @abstractmethod
    async def get_all(self) -> List[ContractTemplate]:
        pass


class ContractVersionRepository(ABC):
    @abstractmethod
    async def save_version(self, version: ContractVersion):
        pass
    
    @abstractmethod
    async def get_versions(self, contract_id: str) -> List[ContractVersion]:
        pass
    
    @abstractmethod
    async def get_version(self, contract_id: str, version_number: int) -> Optional[ContractVersion]:
        pass