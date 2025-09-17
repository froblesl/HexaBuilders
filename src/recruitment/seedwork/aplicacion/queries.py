from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod


@dataclass
class BaseQuery:
    timestamp: Optional[datetime] = field(default=None)
    user_id: Optional[str] = field(default=None)
    correlation_id: Optional[str] = field(default=None)
    metadata: Optional[Dict[str, Any]] = field(default=None)
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


# Alias for compatibility
Query = BaseQuery


@dataclass
class BaseQueryResult:
    success: bool = field(default=True)
    data: Any = field(default=None)
    error_message: Optional[str] = field(default=None)
    metadata: Optional[Dict[str, Any]] = field(default=None)


# Alias for compatibility
QueryResult = BaseQueryResult


# Query execution function
async def ejecutar_query(query: Query, handler=None, uow=None) -> QueryResult:
    """Execute a query with optional handler and unit of work."""
    if handler:
        if uow:
            return await handler.handle(query, uow)
        return await handler.handle(query)
    return QueryResult(success=False, error_message="No handler provided")


# Base Query Handler
class BaseQueryHandler(ABC):
    """Base query handler interface."""
    
    @abstractmethod
    async def handle(self, query: Query, uow=None) -> QueryResult:
        """Handle the query."""
        pass


# Candidate Queries
@dataclass
class GetCandidate(BaseQuery):
    candidate_id: str = field(default_factory=lambda: "")


@dataclass
class GetAllCandidates(BaseQuery):
    filters: Dict[str, Any] = field(default_factory=dict)
    limit: int = field(default_factory=lambda: 50)
    offset: int = field(default_factory=lambda: 0)
    order_by: str = field(default_factory=lambda: "created_at")


@dataclass
class SearchCandidates(BaseQuery):
    search_criteria: Dict[str, Any] = field(default_factory=dict)
    skills: List[str] = field(default_factory=list)
    experience_min: int = field(default_factory=lambda: 0)
    experience_max: int = field(default_factory=lambda: 999)
    location: str = field(default_factory=lambda: "")
    limit: int = field(default_factory=lambda: 50)


@dataclass
class GetCandidatesByStatus(BaseQuery):
    status: str = field(default_factory=lambda: "")
    limit: int = field(default_factory=lambda: 50)
    offset: int = field(default_factory=lambda: 0)


# Job Queries
@dataclass
class GetJob(BaseQuery):
    job_id: str = field(default_factory=lambda: "")


@dataclass
class GetAllJobs(BaseQuery):
    partner_id: Optional[str] = field(default=None)
    status: Optional[str] = field(default=None)
    limit: int = field(default_factory=lambda: 50)
    offset: int = field(default_factory=lambda: 0)


@dataclass
class SearchJobs(BaseQuery):
    search_criteria: Dict[str, Any] = field(default_factory=dict)
    location: str = field(default_factory=lambda: "")
    salary_min: float = field(default_factory=lambda: 0.0)
    salary_max: float = field(default_factory=lambda: 999999.0)
    job_type: str = field(default_factory=lambda: "")
    limit: int = field(default_factory=lambda: 50)


@dataclass
class GetJobsByPartner(BaseQuery):
    partner_id: str = field(default_factory=lambda: "")
    status: Optional[str] = field(default=None)
    limit: int = field(default_factory=lambda: 50)
    offset: int = field(default_factory=lambda: 0)


# Matching Queries
@dataclass
class GetMatch(BaseQuery):
    match_id: str = field(default_factory=lambda: "")


@dataclass
class GetMatchesForCandidate(BaseQuery):
    candidate_id: str = field(default_factory=lambda: "")
    status: Optional[str] = field(default=None)
    limit: int = field(default_factory=lambda: 50)


@dataclass
class GetMatchesForJob(BaseQuery):
    job_id: str = field(default_factory=lambda: "")
    status: Optional[str] = field(default=None)
    limit: int = field(default_factory=lambda: 50)


@dataclass
class GetTopMatches(BaseQuery):
    job_id: str = field(default_factory=lambda: "")
    min_score: float = field(default_factory=lambda: 0.7)
    limit: int = field(default_factory=lambda: 20)


# Interview Queries
@dataclass
class GetInterview(BaseQuery):
    interview_id: str = field(default_factory=lambda: "")


@dataclass
class GetInterviewsByCandidate(BaseQuery):
    candidate_id: str = field(default_factory=lambda: "")
    status: Optional[str] = field(default=None)
    limit: int = field(default_factory=lambda: 50)


@dataclass
class GetInterviewsByPartner(BaseQuery):
    partner_id: str = field(default_factory=lambda: "")
    date_from: Optional[datetime] = field(default=None)
    date_to: Optional[datetime] = field(default=None)
    limit: int = field(default_factory=lambda: 50)


@dataclass
class GetUpcomingInterviews(BaseQuery):
    days_ahead: int = field(default_factory=lambda: 7)
    partner_id: Optional[str] = field(default=None)
    limit: int = field(default_factory=lambda: 50)


# Analytics Queries
@dataclass
class GetCandidateStats(BaseQuery):
    candidate_id: str = field(default_factory=lambda: "")


@dataclass
class GetJobStats(BaseQuery):
    job_id: str = field(default_factory=lambda: "")


@dataclass
class GetPartnerRecruitmentStats(BaseQuery):
    partner_id: str = field(default_factory=lambda: "")
    date_from: Optional[datetime] = field(default=None)
    date_to: Optional[datetime] = field(default=None)


@dataclass
class GetSystemStats(BaseQuery):
    date_from: Optional[datetime] = field(default=None)
    date_to: Optional[datetime] = field(default=None)
    include_details: bool = field(default_factory=lambda: False)
