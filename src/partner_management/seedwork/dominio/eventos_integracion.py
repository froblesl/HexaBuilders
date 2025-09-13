from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Optional
from .eventos import IntegrationEvent


# Events published by Partner Management
@dataclass
class PartnerRegistrationCompletedIntegrationEvent(IntegrationEvent):
    partner_id: str
    partner_data: Dict[str, Any]
    registration_type: str
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "partner_id": self.partner_id,
            "partner_data": self.partner_data,
            "registration_type": self.registration_type
        })
        return data


@dataclass
class RecruitmentRequestedIntegrationEvent(IntegrationEvent):
    partner_id: str
    job_requirements: Dict[str, Any]
    urgency: str
    budget: Optional[float] = None
    
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
class PartnerStatusChangedIntegrationEvent(IntegrationEvent):
    partner_id: str
    old_status: str
    new_status: str
    reason: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "partner_id": self.partner_id,
            "old_status": self.old_status,
            "new_status": self.new_status,
            "reason": self.reason
        })
        return data


# Events received by Partner Management
@dataclass
class ContractSignedIntegrationEvent(IntegrationEvent):
    contract_id: str
    partner_id: str
    contract_type: str
    effective_date: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "contract_id": self.contract_id,
            "partner_id": self.partner_id,
            "contract_type": self.contract_type,
            "effective_date": self.effective_date.isoformat()
        })
        return data


@dataclass
class ContractActivatedIntegrationEvent(IntegrationEvent):
    contract_id: str
    partner_id: str
    contract_type: str
    permissions: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "contract_id": self.contract_id,
            "partner_id": self.partner_id,
            "contract_type": self.contract_type,
            "permissions": self.permissions
        })
        return data


@dataclass
class CandidateMatchedIntegrationEvent(IntegrationEvent):
    job_id: str
    candidate_id: str
    partner_id: str
    match_score: float
    candidate_profile: Dict[str, Any]
    
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
    job_id: str
    candidate_id: str
    partner_id: str
    position: str
    start_date: datetime
    salary: Optional[float] = None
    
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
class CampaignPerformanceReportIntegrationEvent(IntegrationEvent):
    campaign_id: str
    partner_id: str
    performance_data: Dict[str, Any]
    period: str
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "campaign_id": self.campaign_id,
            "partner_id": self.partner_id,
            "performance_data": self.performance_data,
            "period": self.period
        })
        return data


@dataclass
class BudgetAlertIntegrationEvent(IntegrationEvent):
    campaign_id: str
    partner_id: str
    alert_type: str
    current_spend: float
    budget_limit: float
    threshold_percentage: float
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "campaign_id": self.campaign_id,
            "partner_id": self.partner_id,
            "alert_type": self.alert_type,
            "current_spend": self.current_spend,
            "budget_limit": self.budget_limit,
            "threshold_percentage": self.threshold_percentage
        })
        return data