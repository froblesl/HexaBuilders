from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime


@dataclass
class BaseQuery:
    timestamp: Optional[datetime] = field(default=None)
    user_id: Optional[str] = field(default=None)
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.utcnow()


@dataclass
class QueryResult:
    success: bool
    data: Optional[Any] = None
    message: str = ""
    errors: Optional[Dict[str, str]] = None


class QueryHandler(ABC):
    @abstractmethod
    async def handle(self, query: BaseQuery) -> QueryResult:
        pass


class QueryBus:
    def __init__(self):
        self._handlers: Dict[type, QueryHandler] = {}
    
    def register_handler(self, query_type: type, handler: QueryHandler):
        self._handlers[query_type] = handler
    
    async def execute(self, query: BaseQuery) -> QueryResult:
        query_type = type(query)
        
        if query_type not in self._handlers:
            return QueryResult(
                success=False,
                message=f"No handler registered for query {query_type.__name__}",
                errors={"query": "Handler not found"}
            )
        
        handler = self._handlers[query_type]
        
        try:
            return await handler.handle(query)
        except Exception as e:
            return QueryResult(
                success=False,
                message=f"Error executing query: {str(e)}",
                errors={"execution": str(e)}
            )


# Contract Queries
@dataclass
class GetContract(BaseQuery):
    contract_id: str = field(default_factory=lambda: "")


@dataclass
class GetContractsByPartner(BaseQuery):
    partner_id: str = field(default_factory=lambda: "")
    include_inactive: bool = False


@dataclass
class SearchContracts(BaseQuery):
    filters: Dict[str, Any] = field(default_factory=dict)
    page: int = 1
    page_size: int = 20
    sort_by: str = "created_at"
    sort_order: str = "desc"


@dataclass
class GetContractHistory(BaseQuery):
    contract_id: str = field(default_factory=lambda: "")


@dataclass
class GetContractTemplates(BaseQuery):
    contract_type: Optional[str] = None


@dataclass
class GetContractTemplate(BaseQuery):
    template_id: str = field(default_factory=lambda: "")


# Negotiation Queries
@dataclass
class GetNegotiation(BaseQuery):
    negotiation_id: str = field(default_factory=lambda: "")


@dataclass
class GetNegotiationsByContract(BaseQuery):
    contract_id: str = field(default_factory=lambda: "")


@dataclass
class GetActiveNegotiations(BaseQuery):
    participant: Optional[str] = None


@dataclass
class GetNegotiationHistory(BaseQuery):
    negotiation_id: str = field(default_factory=lambda: "")


# Legal Queries
@dataclass
class GetLegalValidation(BaseQuery):
    validation_id: str = field(default_factory=lambda: "")


@dataclass
class GetLegalValidationsByContract(BaseQuery):
    contract_id: str = field(default_factory=lambda: "")


@dataclass
class GetPendingLegalValidations(BaseQuery):
    validator: Optional[str] = None


@dataclass
class GetComplianceReport(BaseQuery):
    contract_id: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None


# Document Queries
@dataclass
class GetDocument(BaseQuery):
    document_id: str = field(default_factory=lambda: "")


@dataclass
class GetDocumentsByContract(BaseQuery):
    contract_id: str = field(default_factory=lambda: "")
    document_type: Optional[str] = None


@dataclass
class GetDocumentSignatures(BaseQuery):
    document_id: str = field(default_factory=lambda: "")


@dataclass
class ValidateDocumentSignature(BaseQuery):
    document_id: str = field(default_factory=lambda: "")
    signature_id: str = field(default_factory=lambda: "")


# Dashboard and Analytics Queries
@dataclass
class GetContractsDashboard(BaseQuery):
    partner_id: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None


@dataclass
class GetContractsMetrics(BaseQuery):
    metric_type: str = field(default_factory=lambda: "")  # "completion_rate", "average_duration", "success_rate"
    period: str = "month"  # "day", "week", "month", "year"
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None


@dataclass
class GetNegotiationMetrics(BaseQuery):
    metric_type: str = field(default_factory=lambda: "")
    period: str = "month"
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None


@dataclass
class GetLegalMetrics(BaseQuery):
    metric_type: str = field(default_factory=lambda: "")
    period: str = "month"
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None


# Compatibility aliases for existing imports
Query = BaseQuery