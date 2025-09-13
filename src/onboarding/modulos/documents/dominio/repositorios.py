from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from uuid import UUID

from .entidades import Document, DocumentPackage, DocumentType, DocumentStatus, VerificationLevel


class DocumentRepository(ABC):
    @abstractmethod
    async def save(self, document: Document) -> None:
        pass

    @abstractmethod
    async def get_by_id(self, document_id: str) -> Optional[Document]:
        pass

    @abstractmethod
    async def get_by_partner_id(self, partner_id: str) -> List[Document]:
        pass

    @abstractmethod
    async def get_by_partner_and_type(self, partner_id: str, document_type: DocumentType) -> Optional[Document]:
        pass

    @abstractmethod
    async def get_by_status(self, status: DocumentStatus) -> List[Document]:
        pass

    @abstractmethod
    async def get_expired_documents(self) -> List[Document]:
        pass

    @abstractmethod
    async def get_pending_review(self) -> List[Document]:
        pass

    @abstractmethod
    async def delete(self, document_id: str) -> None:
        pass


class DocumentPackageRepository(ABC):
    @abstractmethod
    async def save(self, package: DocumentPackage) -> None:
        pass

    @abstractmethod
    async def get_by_id(self, package_id: str) -> Optional[DocumentPackage]:
        pass

    @abstractmethod
    async def get_by_partner_id(self, partner_id: str) -> Optional[DocumentPackage]:
        pass

    @abstractmethod
    async def get_by_verification_level(self, verification_level: VerificationLevel) -> List[DocumentPackage]:
        pass

    @abstractmethod
    async def get_completed_packages(self) -> List[DocumentPackage]:
        pass

    @abstractmethod
    async def delete(self, package_id: str) -> None:
        pass


class DocumentQueryRepository(ABC):
    @abstractmethod
    async def get_partner_document_summary(self, partner_id: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def get_compliance_status(self, partner_id: str) -> Dict[str, bool]:
        pass

    @abstractmethod
    async def get_verification_progress(self, partner_id: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def get_document_statistics(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def search_documents(
        self,
        filters: Dict[str, Any],
        page: int = 1,
        size: int = 20
    ) -> Dict[str, Any]:
        pass