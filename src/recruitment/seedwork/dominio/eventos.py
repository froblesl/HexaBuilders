from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional, List
from .entidades import DomainEvent, IntegrationEvent


# Candidate Domain Events
@dataclass
class CandidateRegistered(DomainEvent):
    candidate_id: str = field(default_factory=lambda: "")
    name: str = field(default_factory=lambda: "")
    email: str = field(default_factory=lambda: "")
    skills: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "candidate_id": self.candidate_id,
            "name": self.name,
            "email": self.email,
            "skills": self.skills
        })
        return data


@dataclass
class CandidateProfileUpdated(DomainEvent):
    candidate_id: str = field(default_factory=lambda: "")
    updated_fields: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "candidate_id": self.candidate_id,
            "updated_fields": self.updated_fields
        })
        return data


@dataclass
class CandidateAvailabilityChanged(DomainEvent):
    candidate_id: str = field(default_factory=lambda: "")
    availability: str = field(default_factory=lambda: "")
    reason: Optional[str] = field(default=None)
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "candidate_id": self.candidate_id,
            "availability": self.availability,
            "reason": self.reason
        })
        return data


# Job Domain Events
@dataclass
class JobPosted(DomainEvent):
    job_id: str = field(default_factory=lambda: "")
    partner_id: str = field(default_factory=lambda: "")
    title: str = field(default_factory=lambda: "")
    required_skills: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "job_id": self.job_id,
            "partner_id": self.partner_id,
            "title": self.title,
            "required_skills": self.required_skills
        })
        return data


@dataclass
class JobUpdated(DomainEvent):
    job_id: str = field(default_factory=lambda: "")
    updated_fields: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "job_id": self.job_id,
            "updated_fields": self.updated_fields
        })
        return data


@dataclass
class JobClosed(DomainEvent):
    job_id: str = field(default_factory=lambda: "")
    reason: str = field(default_factory=lambda: "")
    closed_by: str = field(default_factory=lambda: "")
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "job_id": self.job_id,
            "reason": self.reason,
            "closed_by": self.closed_by
        })
        return data


# Matching Domain Events
@dataclass
class CandidateMatchFound(DomainEvent):
    job_id: str = field(default_factory=lambda: "")
    candidate_id: str = field(default_factory=lambda: "")
    match_score: float = field(default_factory=lambda: 0.0)
    matching_criteria: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "job_id": self.job_id,
            "candidate_id": self.candidate_id,
            "match_score": self.match_score,
            "matching_criteria": self.matching_criteria
        })
        return data


@dataclass
class CandidateApplied(DomainEvent):
    job_id: str = field(default_factory=lambda: "")
    candidate_id: str = field(default_factory=lambda: "")
    application_data: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "job_id": self.job_id,
            "candidate_id": self.candidate_id,
            "application_data": self.application_data
        })
        return data


@dataclass
class ApplicationStatusChanged(DomainEvent):
    application_id: str = field(default_factory=lambda: "")
    job_id: str = field(default_factory=lambda: "")
    candidate_id: str = field(default_factory=lambda: "")
    old_status: str = field(default_factory=lambda: "")
    new_status: str = field(default_factory=lambda: "")
    changed_by: str = field(default_factory=lambda: "")
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "application_id": self.application_id,
            "job_id": self.job_id,
            "candidate_id": self.candidate_id,
            "old_status": self.old_status,
            "new_status": self.new_status,
            "changed_by": self.changed_by
        })
        return data


# Interview Domain Events
@dataclass
class InterviewScheduled(DomainEvent):
    interview_id: str = field(default_factory=lambda: "")
    job_id: str = field(default_factory=lambda: "")
    candidate_id: str = field(default_factory=lambda: "")
    interviewer: str = field(default_factory=lambda: "")
    scheduled_time: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "interview_id": self.interview_id,
            "job_id": self.job_id,
            "candidate_id": self.candidate_id,
            "interviewer": self.interviewer,
            "scheduled_time": self.scheduled_time.isoformat()
        })
        return data


@dataclass
class InterviewCompleted(DomainEvent):
    interview_id: str = field(default_factory=lambda: "")
    job_id: str = field(default_factory=lambda: "")
    candidate_id: str = field(default_factory=lambda: "")
    result: str = field(default_factory=lambda: "")
    feedback: str = field(default_factory=lambda: "")
    score: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "interview_id": self.interview_id,
            "job_id": self.job_id,
            "candidate_id": self.candidate_id,
            "result": self.result,
            "feedback": self.feedback,
            "score": self.score
        })
        return data


# Integration Events
@dataclass
class CandidateMatchedIntegrationEvent(IntegrationEvent):
    job_id: str = field(default_factory=lambda: "")
    candidate_id: str = field(default_factory=lambda: "")
    partner_id: str = field(default_factory=lambda: "")
    match_score: float = field(default_factory=lambda: 0.0)
    candidate_profile: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "job_id": self.job_id,
            "candidate_id": self.candidate_id,
            "partner_id": self.partner_id,
            "match_score": self.match_score,
            "candidate_profile": self.candidate_profile
        })
        return data


@dataclass
class CandidateHiredIntegrationEvent(IntegrationEvent):
    job_id: str = field(default_factory=lambda: "")
    candidate_id: str = field(default_factory=lambda: "")
    partner_id: str = field(default_factory=lambda: "")
    position: str = field(default_factory=lambda: "")
    start_date: datetime = field(default_factory=datetime.utcnow)
    salary: Optional[float] = field(default=None)
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "job_id": self.job_id,
            "candidate_id": self.candidate_id,
            "partner_id": self.partner_id,
            "position": self.position,
            "start_date": self.start_date.isoformat(),
            "salary": self.salary
        })
        return data


@dataclass
class RecruitmentRequiredIntegrationEvent(IntegrationEvent):
    partner_id: str = field(default_factory=lambda: "")
    job_requirements: Dict[str, Any] = field(default_factory=dict)
    urgency: str = field(default_factory=lambda: "")
    budget: Optional[float] = field(default=None)
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "partner_id": self.partner_id,
            "job_requirements": self.job_requirements,
            "urgency": self.urgency,
            "budget": self.budget
        })
        return data


@dataclass
class CampaignStaffingRequestIntegrationEvent(IntegrationEvent):
    campaign_id: str = field(default_factory=lambda: "")
    partner_id: str = field(default_factory=lambda: "")
    positions_needed: List[Dict[str, Any]] = field(default_factory=list)
    timeline: str = field(default_factory=lambda: "")
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "campaign_id": self.campaign_id,
            "partner_id": self.partner_id,
            "positions_needed": self.positions_needed,
            "timeline": self.timeline
        })
        return data