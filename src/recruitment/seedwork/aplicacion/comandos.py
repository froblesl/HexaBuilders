from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod


@dataclass
class BaseCommand:
    id: Optional[str] = field(default=None)
    timestamp: Optional[datetime] = field(default=None)
    user_id: Optional[str] = field(default=None)
    correlation_id: Optional[str] = field(default=None)
    metadata: Optional[Dict[str, Any]] = field(default=None)

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


# Alias for compatibility
Command = BaseCommand


# Command execution function
async def ejecutar_comando(comando: Command, handler=None, uow=None):
    """Execute a command with optional handler and unit of work."""
    if handler:
        if uow:
            return await handler.handle(comando, uow)
        return await handler.handle(comando)
    return None


# Base Command Handler
class BaseCommandHandler(ABC):
    """Base command handler interface."""
    
    @abstractmethod
    async def handle(self, command: Command, uow=None) -> Any:
        """Handle the command."""
        pass


# Candidate Commands
@dataclass
class RegisterCandidate(BaseCommand):
    name: str = field(default_factory=lambda: "")
    email: str = field(default_factory=lambda: "")
    skills: List[str] = field(default_factory=list)
    experience_years: int = field(default_factory=lambda: 0)
    availability: str = field(default_factory=lambda: "")


@dataclass
class UpdateCandidateProfile(BaseCommand):
    candidate_id: str = field(default_factory=lambda: "")
    updated_fields: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ActivateCandidate(BaseCommand):
    candidate_id: str = field(default_factory=lambda: "")


@dataclass
class DeactivateCandidate(BaseCommand):
    candidate_id: str = field(default_factory=lambda: "")
    reason: str = field(default_factory=lambda: "")


# Job Commands
@dataclass
class PostJob(BaseCommand):
    partner_id: str = field(default_factory=lambda: "")
    title: str = field(default_factory=lambda: "")
    description: str = field(default_factory=lambda: "")
    requirements: List[str] = field(default_factory=list)
    salary_range: Dict[str, Any] = field(default_factory=dict)
    location: str = field(default_factory=lambda: "")


@dataclass
class UpdateJob(BaseCommand):
    job_id: str = field(default_factory=lambda: "")
    updated_fields: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CloseJob(BaseCommand):
    job_id: str = field(default_factory=lambda: "")
    reason: str = field(default_factory=lambda: "")


# Matching Commands
@dataclass
class CreateMatch(BaseCommand):
    candidate_id: str = field(default_factory=lambda: "")
    job_id: str = field(default_factory=lambda: "")
    score: float = field(default_factory=lambda: 0.0)
    matching_criteria: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AcceptMatch(BaseCommand):
    match_id: str = field(default_factory=lambda: "")
    candidate_id: str = field(default_factory=lambda: "")


@dataclass
class RejectMatch(BaseCommand):
    match_id: str = field(default_factory=lambda: "")
    candidate_id: str = field(default_factory=lambda: "")
    reason: str = field(default_factory=lambda: "")


# Interview Commands
@dataclass
class ScheduleInterview(BaseCommand):
    match_id: str = field(default_factory=lambda: "")
    candidate_id: str = field(default_factory=lambda: "")
    partner_id: str = field(default_factory=lambda: "")
    scheduled_date: datetime = field(default_factory=datetime.utcnow)
    interview_type: str = field(default_factory=lambda: "")


@dataclass
class CompleteInterview(BaseCommand):
    interview_id: str = field(default_factory=lambda: "")
    outcome: str = field(default_factory=lambda: "")
    notes: str = field(default_factory=lambda: "")
    score: Optional[int] = field(default=None)


@dataclass
class CancelInterview(BaseCommand):
    interview_id: str = field(default_factory=lambda: "")
    reason: str = field(default_factory=lambda: "")
