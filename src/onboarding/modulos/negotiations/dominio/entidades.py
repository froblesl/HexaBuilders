from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Dict, Any, Optional
from uuid import uuid4

from src.onboarding.seedwork.dominio.entidades import AggregateRoot
from src.onboarding.seedwork.dominio.eventos import DomainEvent


class NegotiationStatus(Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"


class ProposalStatus(Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    COUNTERED = "COUNTERED"
    WITHDRAWN = "WITHDRAWN"
    EXPIRED = "EXPIRED"


class NegotiationPriority(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"


class ProposalType(Enum):
    INITIAL_OFFER = "INITIAL_OFFER"
    COUNTER_OFFER = "COUNTER_OFFER"
    FINAL_OFFER = "FINAL_OFFER"
    AMENDMENT = "AMENDMENT"


class TermCategory(Enum):
    FINANCIAL = "FINANCIAL"
    LEGAL = "LEGAL"
    TECHNICAL = "TECHNICAL"
    OPERATIONAL = "OPERATIONAL"
    COMMERCIAL = "COMMERCIAL"


@dataclass
class NegotiationTerm:
    term_id: str
    category: TermCategory
    name: str
    description: str
    current_value: Any
    proposed_value: Any
    negotiable: bool
    priority: NegotiationPriority
    constraints: Dict[str, Any] = field(default_factory=dict)
    comments: str = ""


@dataclass
class Proposal:
    proposal_id: str
    proposal_type: ProposalType
    proposed_by: str
    proposed_at: datetime
    status: ProposalStatus
    terms: List[NegotiationTerm]
    summary: str
    response_deadline: Optional[datetime] = None
    justification: str = ""
    estimated_value: Optional[float] = None


@dataclass
class NegotiationMessage:
    message_id: str
    sender_id: str
    recipient_id: str
    message: str
    sent_at: datetime
    message_type: str = "GENERAL"  # GENERAL, PROPOSAL, CLARIFICATION, DECISION
    attachments: List[str] = field(default_factory=list)
    related_proposal_id: Optional[str] = None


@dataclass
class NegotiationMilestone:
    milestone_id: str
    name: str
    description: str
    target_date: datetime
    completed: bool = False
    completed_at: Optional[datetime] = None
    conditions: List[str] = field(default_factory=list)


# Domain Events
@dataclass
class NegotiationStarted(DomainEvent):
    negotiation_id: str = field(default_factory=lambda: "")
    partner_id: str = field(default_factory=lambda: "")
    contract_type: str = field(default_factory=lambda: "")
    initiated_by: str = field(default_factory=lambda: "")
    initial_terms: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class ProposalSubmitted(DomainEvent):
    negotiation_id: str = field(default_factory=lambda: "")
    proposal_id: str = field(default_factory=lambda: "")
    proposal_type: ProposalType = field(default_factory=lambda: ProposalType.INITIAL_OFFER)
    proposed_by: str = field(default_factory=lambda: "")
    terms_count: int = field(default_factory=lambda: 0)
    estimated_value: Optional[float] = field(default=None)


@dataclass
class ProposalResponded(DomainEvent):
    negotiation_id: str = field(default_factory=lambda: "")
    proposal_id: str = field(default_factory=lambda: "")
    response: ProposalStatus = field(default_factory=lambda: ProposalStatus.PENDING)
    responded_by: str = field(default_factory=lambda: "")
    response_message: str = field(default_factory=lambda: "")


@dataclass
class NegotiationCompleted(DomainEvent):
    negotiation_id: str = field(default_factory=lambda: "")
    partner_id: str = field(default_factory=lambda: "")
    final_terms: List[Dict[str, Any]] = field(default_factory=list)
    total_proposals: int = field(default_factory=lambda: 0)
    duration_days: int = field(default_factory=lambda: 0)
    completed_by: str = field(default_factory=lambda: "")


@dataclass
class NegotiationCancelled(DomainEvent):
    negotiation_id: str = field(default_factory=lambda: "")
    partner_id: str = field(default_factory=lambda: "")
    cancelled_by: str = field(default_factory=lambda: "")
    cancellation_reason: str = field(default_factory=lambda: "")


@dataclass
class DeadlineExtended(DomainEvent):
    negotiation_id: str = field(default_factory=lambda: "")
    proposal_id: str = field(default_factory=lambda: "")
    old_deadline: datetime = field(default_factory=datetime.utcnow)
    new_deadline: datetime = field(default_factory=datetime.utcnow)
    extended_by: str = field(default_factory=lambda: "")
    reason: str


class Negotiation(AggregateRoot):
    def __init__(
        self,
        partner_id: str,
        contract_type: str,
        initiated_by: str,
        initial_terms: List[NegotiationTerm],
        deadline: Optional[datetime] = None
    ):
        super().__init__()
        self.id = str(uuid4())
        self._partner_id = partner_id
        self._contract_type = contract_type
        self._initiated_by = initiated_by
        self._status = NegotiationStatus.DRAFT
        self._priority = NegotiationPriority.MEDIUM
        self._current_terms = initial_terms
        self._proposals: List[Proposal] = []
        self._messages: List[NegotiationMessage] = []
        self._milestones: List[NegotiationMilestone] = []
        self._participants: List[str] = [initiated_by]
        self._created_at = datetime.utcnow()
        self._started_at: Optional[datetime] = None
        self._completed_at: Optional[datetime] = None
        self._deadline = deadline or (datetime.utcnow() + timedelta(days=30))
        self._estimated_value: Optional[float] = None
        self._final_agreed_terms: Optional[List[NegotiationTerm]] = None

    @property
    def partner_id(self) -> str:
        return self._partner_id

    @property
    def contract_type(self) -> str:
        return self._contract_type

    @property
    def status(self) -> NegotiationStatus:
        return self._status

    @property
    def priority(self) -> NegotiationPriority:
        return self._priority

    @property
    def current_terms(self) -> List[NegotiationTerm]:
        return self._current_terms.copy()

    @property
    def proposals(self) -> List[Proposal]:
        return self._proposals.copy()

    @property
    def messages(self) -> List[NegotiationMessage]:
        return self._messages.copy()

    @property
    def milestones(self) -> List[NegotiationMilestone]:
        return self._milestones.copy()

    @property
    def participants(self) -> List[str]:
        return self._participants.copy()

    @property
    def deadline(self) -> datetime:
        return self._deadline

    @property
    def is_active(self) -> bool:
        return self._status == NegotiationStatus.ACTIVE

    @property
    def is_expired(self) -> bool:
        return datetime.utcnow() > self._deadline and self._status == NegotiationStatus.ACTIVE

    @property
    def duration_days(self) -> Optional[int]:
        if self._started_at:
            end_time = self._completed_at or datetime.utcnow()
            return (end_time - self._started_at).days
        return None

    @property
    def active_proposal(self) -> Optional[Proposal]:
        for proposal in reversed(self._proposals):
            if proposal.status == ProposalStatus.PENDING:
                return proposal
        return None

    def start_negotiation(self):
        if self._status != NegotiationStatus.DRAFT:
            raise ValueError(f"Cannot start negotiation in status: {self._status}")

        self._status = NegotiationStatus.ACTIVE
        self._started_at = datetime.utcnow()

        # Create initial milestone
        initial_milestone = NegotiationMilestone(
            milestone_id=str(uuid4()),
            name="Negotiation Started",
            description="Initial negotiation phase begun",
            target_date=self._deadline,
            completed=True,
            completed_at=datetime.utcnow()
        )
        self._milestones.append(initial_milestone)

        self.publicar_evento(NegotiationStarted(
            event_id=str(uuid4()),
            occurred_on=datetime.utcnow(),
            negotiation_id=self.id,
            partner_id=self._partner_id,
            contract_type=self._contract_type,
            initiated_by=self._initiated_by,
            initial_terms=[{
                "term_id": term.term_id,
                "category": term.category.value,
                "name": term.name,
                "current_value": term.current_value,
                "proposed_value": term.proposed_value
            } for term in self._current_terms]
        ))

    def submit_proposal(
        self,
        proposed_by: str,
        proposal_type: ProposalType,
        terms: List[NegotiationTerm],
        summary: str,
        justification: str = "",
        response_deadline: Optional[datetime] = None,
        estimated_value: Optional[float] = None
    ) -> Proposal:
        if self._status != NegotiationStatus.ACTIVE:
            raise ValueError(f"Cannot submit proposal in status: {self._status}")

        if proposed_by not in self._participants:
            self._participants.append(proposed_by)

        # Set default response deadline
        if not response_deadline:
            response_deadline = datetime.utcnow() + timedelta(days=7)

        proposal = Proposal(
            proposal_id=str(uuid4()),
            proposal_type=proposal_type,
            proposed_by=proposed_by,
            proposed_at=datetime.utcnow(),
            status=ProposalStatus.PENDING,
            terms=terms,
            summary=summary,
            response_deadline=response_deadline,
            justification=justification,
            estimated_value=estimated_value
        )

        self._proposals.append(proposal)

        # Update estimated value if provided
        if estimated_value:
            self._estimated_value = estimated_value

        self.publicar_evento(ProposalSubmitted(
            event_id=str(uuid4()),
            occurred_on=datetime.utcnow(),
            negotiation_id=self.id,
            proposal_id=proposal.proposal_id,
            proposal_type=proposal_type,
            proposed_by=proposed_by,
            terms_count=len(terms),
            estimated_value=estimated_value
        ))

        return proposal

    def respond_to_proposal(
        self,
        proposal_id: str,
        response: ProposalStatus,
        responded_by: str,
        response_message: str = ""
    ):
        if self._status != NegotiationStatus.ACTIVE:
            raise ValueError(f"Cannot respond to proposal in status: {self._status}")

        proposal = None
        for p in self._proposals:
            if p.proposal_id == proposal_id:
                proposal = p
                break

        if not proposal:
            raise ValueError(f"Proposal {proposal_id} not found")

        if proposal.status != ProposalStatus.PENDING:
            raise ValueError(f"Cannot respond to proposal with status: {proposal.status}")

        if response not in [ProposalStatus.ACCEPTED, ProposalStatus.REJECTED, ProposalStatus.COUNTERED]:
            raise ValueError(f"Invalid response: {response}")

        proposal.status = response

        # If accepted, update current terms
        if response == ProposalStatus.ACCEPTED:
            self._current_terms = proposal.terms
            
            # If this was a final offer, complete the negotiation
            if proposal.proposal_type == ProposalType.FINAL_OFFER:
                self._complete_negotiation(responded_by)

        self.publicar_evento(ProposalResponded(
            event_id=str(uuid4()),
            occurred_on=datetime.utcnow(),
            negotiation_id=self.id,
            proposal_id=proposal_id,
            response=response,
            responded_by=responded_by,
            response_message=response_message
        ))

    def add_message(
        self,
        sender_id: str,
        recipient_id: str,
        message: str,
        message_type: str = "GENERAL",
        attachments: List[str] = None,
        related_proposal_id: str = None
    ) -> NegotiationMessage:
        if self._status not in [NegotiationStatus.ACTIVE, NegotiationStatus.PAUSED]:
            raise ValueError(f"Cannot add message in status: {self._status}")

        if sender_id not in self._participants:
            self._participants.append(sender_id)

        msg = NegotiationMessage(
            message_id=str(uuid4()),
            sender_id=sender_id,
            recipient_id=recipient_id,
            message=message,
            sent_at=datetime.utcnow(),
            message_type=message_type,
            attachments=attachments or [],
            related_proposal_id=related_proposal_id
        )

        self._messages.append(msg)
        return msg

    def add_milestone(self, milestone: NegotiationMilestone):
        self._milestones.append(milestone)

    def complete_milestone(self, milestone_id: str):
        for milestone in self._milestones:
            if milestone.milestone_id == milestone_id:
                milestone.completed = True
                milestone.completed_at = datetime.utcnow()
                break

    def extend_deadline(self, new_deadline: datetime, extended_by: str, reason: str):
        if new_deadline <= self._deadline:
            raise ValueError("New deadline must be later than current deadline")

        old_deadline = self._deadline
        self._deadline = new_deadline

        # Also extend active proposal deadlines
        for proposal in self._proposals:
            if proposal.status == ProposalStatus.PENDING and proposal.response_deadline:
                if proposal.response_deadline <= old_deadline:
                    days_extended = (new_deadline - old_deadline).days
                    proposal.response_deadline = proposal.response_deadline + timedelta(days=days_extended)

        self.publicar_evento(DeadlineExtended(
            event_id=str(uuid4()),
            occurred_on=datetime.utcnow(),
            negotiation_id=self.id,
            proposal_id=self.active_proposal.proposal_id if self.active_proposal else "",
            old_deadline=old_deadline,
            new_deadline=new_deadline,
            extended_by=extended_by,
            reason=reason
        ))

    def pause_negotiation(self, paused_by: str, reason: str = ""):
        if self._status != NegotiationStatus.ACTIVE:
            raise ValueError(f"Cannot pause negotiation in status: {self._status}")

        self._status = NegotiationStatus.PAUSED
        
        # Add pause message
        self.add_message(
            sender_id=paused_by,
            recipient_id="ALL",
            message=f"Negotiation paused. Reason: {reason}",
            message_type="DECISION"
        )

    def resume_negotiation(self, resumed_by: str):
        if self._status != NegotiationStatus.PAUSED:
            raise ValueError(f"Cannot resume negotiation in status: {self._status}")

        self._status = NegotiationStatus.ACTIVE
        
        # Add resume message
        self.add_message(
            sender_id=resumed_by,
            recipient_id="ALL",
            message="Negotiation resumed",
            message_type="DECISION"
        )

    def cancel_negotiation(self, cancelled_by: str, reason: str):
        if self._status in [NegotiationStatus.COMPLETED, NegotiationStatus.CANCELLED]:
            raise ValueError(f"Cannot cancel negotiation in status: {self._status}")

        self._status = NegotiationStatus.CANCELLED
        self._completed_at = datetime.utcnow()

        self.publicar_evento(NegotiationCancelled(
            event_id=str(uuid4()),
            occurred_on=datetime.utcnow(),
            negotiation_id=self.id,
            partner_id=self._partner_id,
            cancelled_by=cancelled_by,
            cancellation_reason=reason
        ))

    def _complete_negotiation(self, completed_by: str):
        self._status = NegotiationStatus.COMPLETED
        self._completed_at = datetime.utcnow()
        self._final_agreed_terms = self._current_terms.copy()

        # Complete all pending milestones
        for milestone in self._milestones:
            if not milestone.completed:
                milestone.completed = True
                milestone.completed_at = datetime.utcnow()

        self.publicar_evento(NegotiationCompleted(
            event_id=str(uuid4()),
            occurred_on=datetime.utcnow(),
            negotiation_id=self.id,
            partner_id=self._partner_id,
            final_terms=[{
                "term_id": term.term_id,
                "category": term.category.value,
                "name": term.name,
                "agreed_value": term.proposed_value
            } for term in self._final_agreed_terms],
            total_proposals=len(self._proposals),
            duration_days=self.duration_days or 0,
            completed_by=completed_by
        ))

    def check_expiration(self):
        if self.is_expired and self._status == NegotiationStatus.ACTIVE:
            self._status = NegotiationStatus.EXPIRED
            self._completed_at = datetime.utcnow()

            # Expire any pending proposals
            for proposal in self._proposals:
                if proposal.status == ProposalStatus.PENDING:
                    proposal.status = ProposalStatus.EXPIRED

    def get_negotiation_summary(self) -> Dict[str, Any]:
        return {
            "negotiation_id": self.id,
            "partner_id": self._partner_id,
            "contract_type": self._contract_type,
            "status": self._status.value,
            "priority": self._priority.value,
            "created_at": self._created_at.isoformat(),
            "started_at": self._started_at.isoformat() if self._started_at else None,
            "completed_at": self._completed_at.isoformat() if self._completed_at else None,
            "deadline": self._deadline.isoformat(),
            "duration_days": self.duration_days,
            "participants_count": len(self._participants),
            "total_proposals": len(self._proposals),
            "total_messages": len(self._messages),
            "completed_milestones": len([m for m in self._milestones if m.completed]),
            "total_milestones": len(self._milestones),
            "estimated_value": self._estimated_value,
            "active_proposal": {
                "proposal_id": self.active_proposal.proposal_id,
                "proposed_by": self.active_proposal.proposed_by,
                "response_deadline": self.active_proposal.response_deadline.isoformat() if self.active_proposal.response_deadline else None
            } if self.active_proposal else None
        }

    def get_terms_comparison(self) -> Dict[str, Any]:
        if not self._proposals:
            return {"original_terms": self._current_terms, "proposals": []}

        comparison = {
            "current_terms": [
                {
                    "term_id": term.term_id,
                    "name": term.name,
                    "category": term.category.value,
                    "current_value": term.current_value,
                    "proposed_value": term.proposed_value
                }
                for term in self._current_terms
            ],
            "proposals_history": []
        }

        for proposal in self._proposals:
            proposal_terms = [
                {
                    "term_id": term.term_id,
                    "name": term.name,
                    "category": term.category.value,
                    "proposed_value": term.proposed_value,
                    "change_from_current": term.proposed_value != term.current_value
                }
                for term in proposal.terms
            ]
            
            comparison["proposals_history"].append({
                "proposal_id": proposal.proposal_id,
                "proposal_type": proposal.proposal_type.value,
                "proposed_by": proposal.proposed_by,
                "proposed_at": proposal.proposed_at.isoformat(),
                "status": proposal.status.value,
                "terms": proposal_terms
            })

        return comparison

    @classmethod
    def from_events(cls, events: List[DomainEvent]) -> 'Negotiation':
        raise NotImplementedError("Negotiation event sourcing not fully implemented")