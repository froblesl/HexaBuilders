from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Dict, Any, Optional
from uuid import uuid4

from recruitment.seedwork.dominio.entidades import AggregateRoot
from recruitment.seedwork.dominio.eventos import DomainEvent


class InterviewType(Enum):
    PHONE_SCREENING = "PHONE_SCREENING"
    VIDEO_INTERVIEW = "VIDEO_INTERVIEW"
    TECHNICAL_INTERVIEW = "TECHNICAL_INTERVIEW"
    BEHAVIORAL_INTERVIEW = "BEHAVIORAL_INTERVIEW"
    PANEL_INTERVIEW = "PANEL_INTERVIEW"
    ON_SITE_INTERVIEW = "ON_SITE_INTERVIEW"
    FINAL_INTERVIEW = "FINAL_INTERVIEW"


class InterviewStatus(Enum):
    SCHEDULED = "SCHEDULED"
    CONFIRMED = "CONFIRMED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    NO_SHOW = "NO_SHOW"
    RESCHEDULED = "RESCHEDULED"


class InterviewRound(Enum):
    FIRST_ROUND = "FIRST_ROUND"
    SECOND_ROUND = "SECOND_ROUND"
    THIRD_ROUND = "THIRD_ROUND"
    FINAL_ROUND = "FINAL_ROUND"


class EvaluationScore(Enum):
    EXCELLENT = 5
    GOOD = 4
    SATISFACTORY = 3
    NEEDS_IMPROVEMENT = 2
    POOR = 1


class InterviewDecision(Enum):
    STRONGLY_RECOMMEND = "STRONGLY_RECOMMEND"
    RECOMMEND = "RECOMMEND"
    NEUTRAL = "NEUTRAL"
    NOT_RECOMMEND = "NOT_RECOMMEND"
    STRONGLY_NOT_RECOMMEND = "STRONGLY_NOT_RECOMMEND"


@dataclass
class InterviewQuestion:
    question_id: str
    question_text: str
    category: str
    difficulty_level: str
    expected_answer: Optional[str] = None
    scoring_criteria: List[str] = field(default_factory=list)


@dataclass
class InterviewResponse:
    question_id: str
    candidate_answer: str
    score: EvaluationScore
    interviewer_notes: str
    time_taken_minutes: Optional[int] = None


@dataclass
class EvaluationCriteria:
    criteria_id: str
    name: str
    description: str
    weight: float  # 0.0 to 1.0
    max_score: int = 5


@dataclass
class InterviewEvaluation:
    evaluation_id: str
    interviewer_id: str
    overall_score: float
    decision: InterviewDecision
    strengths: List[str]
    weaknesses: List[str]
    detailed_feedback: str
    criteria_scores: Dict[str, int]  # criteria_id -> score
    recommendation_notes: str
    evaluated_at: datetime


@dataclass
class InterviewFeedback:
    feedback_id: str
    candidate_id: str
    interviewer_id: str
    interview_experience_rating: int  # 1-5
    process_feedback: str
    suggestions_for_improvement: str
    would_recommend_company: bool
    submitted_at: datetime


# Domain Events
@dataclass
class InterviewScheduled(DomainEvent):
    interview_id: str
    job_id: str
    candidate_id: str
    interviewer_id: str
    interview_type: InterviewType
    scheduled_datetime: datetime
    duration_minutes: int


@dataclass
class InterviewConfirmed(DomainEvent):
    interview_id: str
    candidate_id: str
    interviewer_id: str
    confirmed_by: str
    confirmation_timestamp: datetime


@dataclass
class InterviewCompleted(DomainEvent):
    interview_id: str
    job_id: str
    candidate_id: str
    interviewer_id: str
    duration_minutes: int
    overall_score: float
    decision: InterviewDecision


@dataclass
class InterviewCancelled(DomainEvent):
    interview_id: str
    cancelled_by: str
    cancellation_reason: str
    cancelled_at: datetime


@dataclass
class InterviewRescheduled(DomainEvent):
    interview_id: str
    old_datetime: datetime
    new_datetime: datetime
    rescheduled_by: str
    reason: str


@dataclass
class InterviewNoShow(DomainEvent):
    interview_id: str
    candidate_id: str
    job_id: str
    scheduled_datetime: datetime
    no_show_type: str  # CANDIDATE_NO_SHOW, INTERVIEWER_NO_SHOW


class Interview(AggregateRoot):
    def __init__(
        self,
        job_id: str,
        candidate_id: str,
        interviewer_id: str,
        interview_type: InterviewType,
        scheduled_datetime: datetime,
        duration_minutes: int = 60,
        interview_round: InterviewRound = InterviewRound.FIRST_ROUND
    ):
        super().__init__()
        self.id = str(uuid4())
        self._job_id = job_id
        self._candidate_id = candidate_id
        self._interviewer_id = interviewer_id
        self._interview_type = interview_type
        self._interview_round = interview_round
        self._status = InterviewStatus.SCHEDULED
        self._scheduled_datetime = scheduled_datetime
        self._duration_minutes = duration_minutes
        self._actual_start_time: Optional[datetime] = None
        self._actual_end_time: Optional[datetime] = None
        self._location: Optional[str] = None
        self._meeting_link: Optional[str] = None
        self._questions: List[InterviewQuestion] = []
        self._responses: List[InterviewResponse] = []
        self._evaluation: Optional[InterviewEvaluation] = None
        self._feedback: Optional[InterviewFeedback] = None
        self._notes: str = ""
        self._created_at = datetime.utcnow()
        self._updated_at = datetime.utcnow()
        self._rescheduled_count = 0

    @property
    def job_id(self) -> str:
        return self._job_id

    @property
    def candidate_id(self) -> str:
        return self._candidate_id

    @property
    def interviewer_id(self) -> str:
        return self._interviewer_id

    @property
    def interview_type(self) -> InterviewType:
        return self._interview_type

    @property
    def status(self) -> InterviewStatus:
        return self._status

    @property
    def scheduled_datetime(self) -> datetime:
        return self._scheduled_datetime

    @property
    def duration_minutes(self) -> int:
        return self._duration_minutes

    @property
    def actual_duration_minutes(self) -> Optional[int]:
        if self._actual_start_time and self._actual_end_time:
            return int((self._actual_end_time - self._actual_start_time).total_seconds() / 60)
        return None

    @property
    def questions(self) -> List[InterviewQuestion]:
        return self._questions.copy()

    @property
    def responses(self) -> List[InterviewResponse]:
        return self._responses.copy()

    @property
    def evaluation(self) -> Optional[InterviewEvaluation]:
        return self._evaluation

    @property
    def feedback(self) -> Optional[InterviewFeedback]:
        return self._feedback

    @property
    def is_confirmed(self) -> bool:
        return self._status == InterviewStatus.CONFIRMED

    @property
    def is_completed(self) -> bool:
        return self._status == InterviewStatus.COMPLETED

    @property
    def can_reschedule(self) -> bool:
        return (self._status in [InterviewStatus.SCHEDULED, InterviewStatus.CONFIRMED] and 
                self._rescheduled_count < 3 and
                self._scheduled_datetime > datetime.utcnow() + timedelta(hours=24))

    def set_location(self, location: str):
        if self._status not in [InterviewStatus.SCHEDULED, InterviewStatus.CONFIRMED]:
            raise ValueError(f"Cannot set location for interview in status: {self._status}")
        
        self._location = location
        self._updated_at = datetime.utcnow()

    def set_meeting_link(self, meeting_link: str):
        if self._status not in [InterviewStatus.SCHEDULED, InterviewStatus.CONFIRMED]:
            raise ValueError(f"Cannot set meeting link for interview in status: {self._status}")
        
        self._meeting_link = meeting_link
        self._updated_at = datetime.utcnow()

    def confirm_interview(self, confirmed_by: str):
        if self._status != InterviewStatus.SCHEDULED:
            raise ValueError(f"Cannot confirm interview in status: {self._status}")

        self._status = InterviewStatus.CONFIRMED
        self._updated_at = datetime.utcnow()

        self.publicar_evento(InterviewConfirmed(
            event_id=str(uuid4()),
            occurred_on=datetime.utcnow(),
            interview_id=self.id,
            candidate_id=self._candidate_id,
            interviewer_id=self._interviewer_id,
            confirmed_by=confirmed_by,
            confirmation_timestamp=datetime.utcnow()
        ))

    def start_interview(self):
        if self._status != InterviewStatus.CONFIRMED:
            raise ValueError(f"Cannot start interview in status: {self._status}")

        if datetime.utcnow() < self._scheduled_datetime - timedelta(minutes=15):
            raise ValueError("Cannot start interview more than 15 minutes early")

        self._status = InterviewStatus.IN_PROGRESS
        self._actual_start_time = datetime.utcnow()
        self._updated_at = datetime.utcnow()

    def add_question(self, question: InterviewQuestion):
        if self._status not in [InterviewStatus.SCHEDULED, InterviewStatus.CONFIRMED, InterviewStatus.IN_PROGRESS]:
            raise ValueError(f"Cannot add questions in status: {self._status}")

        self._questions.append(question)
        self._updated_at = datetime.utcnow()

    def add_response(self, response: InterviewResponse):
        if self._status != InterviewStatus.IN_PROGRESS:
            raise ValueError(f"Cannot add responses in status: {self._status}")

        # Verify question exists
        question_exists = any(q.question_id == response.question_id for q in self._questions)
        if not question_exists:
            raise ValueError(f"Question {response.question_id} not found in interview")

        self._responses.append(response)
        self._updated_at = datetime.utcnow()

    def complete_interview(self, evaluation: InterviewEvaluation):
        if self._status != InterviewStatus.IN_PROGRESS:
            raise ValueError(f"Cannot complete interview in status: {self._status}")

        if evaluation.interviewer_id != self._interviewer_id:
            raise ValueError("Evaluation must be from the assigned interviewer")

        self._status = InterviewStatus.COMPLETED
        self._actual_end_time = datetime.utcnow()
        self._evaluation = evaluation
        self._updated_at = datetime.utcnow()

        self.publicar_evento(InterviewCompleted(
            event_id=str(uuid4()),
            occurred_on=datetime.utcnow(),
            interview_id=self.id,
            job_id=self._job_id,
            candidate_id=self._candidate_id,
            interviewer_id=self._interviewer_id,
            duration_minutes=self.actual_duration_minutes or self._duration_minutes,
            overall_score=evaluation.overall_score,
            decision=evaluation.decision
        ))

    def cancel_interview(self, cancelled_by: str, reason: str):
        if self._status in [InterviewStatus.COMPLETED, InterviewStatus.CANCELLED]:
            raise ValueError(f"Cannot cancel interview in status: {self._status}")

        self._status = InterviewStatus.CANCELLED
        self._updated_at = datetime.utcnow()

        self.publicar_evento(InterviewCancelled(
            event_id=str(uuid4()),
            occurred_on=datetime.utcnow(),
            interview_id=self.id,
            cancelled_by=cancelled_by,
            cancellation_reason=reason,
            cancelled_at=datetime.utcnow()
        ))

    def reschedule_interview(
        self,
        new_datetime: datetime,
        rescheduled_by: str,
        reason: str = ""
    ):
        if not self.can_reschedule:
            raise ValueError("Interview cannot be rescheduled")

        if new_datetime <= datetime.utcnow():
            raise ValueError("New interview time must be in the future")

        old_datetime = self._scheduled_datetime
        self._scheduled_datetime = new_datetime
        self._status = InterviewStatus.RESCHEDULED
        self._rescheduled_count += 1
        self._updated_at = datetime.utcnow()

        self.publicar_evento(InterviewRescheduled(
            event_id=str(uuid4()),
            occurred_on=datetime.utcnow(),
            interview_id=self.id,
            old_datetime=old_datetime,
            new_datetime=new_datetime,
            rescheduled_by=rescheduled_by,
            reason=reason
        ))

    def mark_no_show(self, no_show_type: str = "CANDIDATE_NO_SHOW"):
        if self._status not in [InterviewStatus.CONFIRMED, InterviewStatus.SCHEDULED]:
            raise ValueError(f"Cannot mark no-show for interview in status: {self._status}")

        if datetime.utcnow() < self._scheduled_datetime + timedelta(minutes=15):
            raise ValueError("Cannot mark no-show until 15 minutes after scheduled time")

        self._status = InterviewStatus.NO_SHOW
        self._updated_at = datetime.utcnow()

        self.publicar_evento(InterviewNoShow(
            event_id=str(uuid4()),
            occurred_on=datetime.utcnow(),
            interview_id=self.id,
            candidate_id=self._candidate_id,
            job_id=self._job_id,
            scheduled_datetime=self._scheduled_datetime,
            no_show_type=no_show_type
        ))

    def add_feedback(self, feedback: InterviewFeedback):
        if not self.is_completed:
            raise ValueError("Can only add feedback to completed interviews")

        if feedback.candidate_id != self._candidate_id:
            raise ValueError("Feedback must be from the interviewed candidate")

        self._feedback = feedback
        self._updated_at = datetime.utcnow()

    def add_notes(self, notes: str):
        self._notes = notes
        self._updated_at = datetime.utcnow()

    def get_interview_summary(self) -> Dict[str, Any]:
        return {
            "interview_id": self.id,
            "job_id": self._job_id,
            "candidate_id": self._candidate_id,
            "interviewer_id": self._interviewer_id,
            "interview_type": self._interview_type.value,
            "interview_round": self._interview_round.value,
            "status": self._status.value,
            "scheduled_datetime": self._scheduled_datetime.isoformat(),
            "duration_minutes": self._duration_minutes,
            "actual_duration_minutes": self.actual_duration_minutes,
            "location": self._location,
            "meeting_link": self._meeting_link,
            "questions_count": len(self._questions),
            "responses_count": len(self._responses),
            "rescheduled_count": self._rescheduled_count,
            "overall_score": self._evaluation.overall_score if self._evaluation else None,
            "decision": self._evaluation.decision.value if self._evaluation else None,
            "has_feedback": self._feedback is not None,
            "created_at": self._created_at.isoformat(),
            "updated_at": self._updated_at.isoformat()
        }

    def get_detailed_evaluation(self) -> Dict[str, Any]:
        if not self._evaluation:
            return {}

        return {
            "evaluation_id": self._evaluation.evaluation_id,
            "interviewer_id": self._evaluation.interviewer_id,
            "overall_score": self._evaluation.overall_score,
            "decision": self._evaluation.decision.value,
            "strengths": self._evaluation.strengths,
            "weaknesses": self._evaluation.weaknesses,
            "detailed_feedback": self._evaluation.detailed_feedback,
            "criteria_scores": self._evaluation.criteria_scores,
            "recommendation_notes": self._evaluation.recommendation_notes,
            "evaluated_at": self._evaluation.evaluated_at.isoformat(),
            "responses": [
                {
                    "question_id": resp.question_id,
                    "candidate_answer": resp.candidate_answer,
                    "score": resp.score.value,
                    "interviewer_notes": resp.interviewer_notes,
                    "time_taken_minutes": resp.time_taken_minutes
                }
                for resp in self._responses
            ]
        }

    @classmethod
    def from_events(cls, events: List[DomainEvent]) -> 'Interview':
        raise NotImplementedError("Interview event sourcing not implemented")


class InterviewScheduler(AggregateRoot):
    def __init__(self, job_id: str):
        super().__init__()
        self.id = str(uuid4())
        self._job_id = job_id
        self._interviews: List[Interview] = []
        self._interview_process_stages: List[InterviewType] = []
        self._evaluation_criteria: List[EvaluationCriteria] = []
        self._question_bank: List[InterviewQuestion] = []
        self._created_at = datetime.utcnow()

    @property
    def job_id(self) -> str:
        return self._job_id

    @property
    def interviews(self) -> List[Interview]:
        return self._interviews.copy()

    @property
    def interview_process_stages(self) -> List[InterviewType]:
        return self._interview_process_stages.copy()

    def configure_interview_process(
        self,
        stages: List[InterviewType],
        evaluation_criteria: List[EvaluationCriteria]
    ):
        self._interview_process_stages = stages
        self._evaluation_criteria = evaluation_criteria

    def add_question_to_bank(self, question: InterviewQuestion):
        self._question_bank.append(question)

    def schedule_interview(
        self,
        candidate_id: str,
        interviewer_id: str,
        interview_type: InterviewType,
        scheduled_datetime: datetime,
        duration_minutes: int = 60
    ) -> Interview:
        # Determine interview round based on existing interviews for this candidate
        candidate_interviews = [i for i in self._interviews if i.candidate_id == candidate_id]
        interview_round = InterviewRound.FIRST_ROUND
        
        if len(candidate_interviews) == 1:
            interview_round = InterviewRound.SECOND_ROUND
        elif len(candidate_interviews) == 2:
            interview_round = InterviewRound.THIRD_ROUND
        elif len(candidate_interviews) >= 3:
            interview_round = InterviewRound.FINAL_ROUND

        interview = Interview(
            job_id=self._job_id,
            candidate_id=candidate_id,
            interviewer_id=interviewer_id,
            interview_type=interview_type,
            scheduled_datetime=scheduled_datetime,
            duration_minutes=duration_minutes,
            interview_round=interview_round
        )

        # Add relevant questions from question bank
        relevant_questions = [
            q for q in self._question_bank 
            if interview_type.value.lower() in q.category.lower()
        ]
        
        for question in relevant_questions[:10]:  # Limit to 10 questions
            interview.add_question(question)

        self._interviews.append(interview)

        self.publicar_evento(InterviewScheduled(
            event_id=str(uuid4()),
            occurred_on=datetime.utcnow(),
            interview_id=interview.id,
            job_id=self._job_id,
            candidate_id=candidate_id,
            interviewer_id=interviewer_id,
            interview_type=interview_type,
            scheduled_datetime=scheduled_datetime,
            duration_minutes=duration_minutes
        ))

        return interview

    def get_candidate_interview_history(self, candidate_id: str) -> List[Interview]:
        return [i for i in self._interviews if i.candidate_id == candidate_id]

    def get_interviewer_schedule(self, interviewer_id: str, date: datetime) -> List[Interview]:
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        
        return [
            i for i in self._interviews 
            if (i.interviewer_id == interviewer_id and 
                start_of_day <= i.scheduled_datetime < end_of_day)
        ]

    def get_interview_statistics(self) -> Dict[str, Any]:
        total_interviews = len(self._interviews)
        if total_interviews == 0:
            return {"total_interviews": 0}

        completed_interviews = [i for i in self._interviews if i.is_completed]
        
        return {
            "total_interviews": total_interviews,
            "completed_interviews": len(completed_interviews),
            "completion_rate": len(completed_interviews) / total_interviews * 100,
            "average_score": sum(i.evaluation.overall_score for i in completed_interviews if i.evaluation) / len(completed_interviews) if completed_interviews else 0,
            "by_type": {
                interview_type.value: len([i for i in self._interviews if i.interview_type == interview_type])
                for interview_type in InterviewType
            },
            "by_status": {
                status.value: len([i for i in self._interviews if i.status == status])
                for status in InterviewStatus
            }
        }

    @classmethod
    def from_events(cls, events: List[DomainEvent]) -> 'InterviewScheduler':
        raise NotImplementedError("InterviewScheduler event sourcing not implemented")