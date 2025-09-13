from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum

from recruitment.seedwork.dominio.entidades import BaseEntity, ValueObject
from recruitment.seedwork.dominio.excepciones import InvalidJobDataException


class JobStatus(Enum):
    DRAFT = "DRAFT"
    OPEN = "OPEN"
    PAUSED = "PAUSED"
    CLOSED = "CLOSED"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"


class JobType(Enum):
    FULL_TIME = "FULL_TIME"
    PART_TIME = "PART_TIME"
    CONTRACT = "CONTRACT"
    TEMPORARY = "TEMPORARY"
    INTERNSHIP = "INTERNSHIP"
    FREELANCE = "FREELANCE"


class ExperienceLevel(Enum):
    JUNIOR = "JUNIOR"
    MID = "MID"
    SENIOR = "SENIOR"
    LEAD = "LEAD"
    PRINCIPAL = "PRINCIPAL"


class ApplicationStatus(Enum):
    SUBMITTED = "SUBMITTED"
    SCREENING = "SCREENING"
    INTERVIEWING = "INTERVIEWING"
    TECHNICAL_ASSESSMENT = "TECHNICAL_ASSESSMENT"
    FINAL_REVIEW = "FINAL_REVIEW"
    OFFERED = "OFFERED"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    WITHDRAWN = "WITHDRAWN"


@dataclass
class JobRequirements(ValueObject):
    required_skills: List[str] = field(default_factory=list)
    nice_to_have_skills: List[str] = field(default_factory=list)
    min_experience_years: int = 0
    max_experience_years: Optional[int] = None
    experience_level: ExperienceLevel = ExperienceLevel.JUNIOR
    education_level: Optional[str] = None
    certifications: List[str] = field(default_factory=list)
    languages: List[Dict[str, str]] = field(default_factory=list)
    
    def _validate(self):
        if self.min_experience_years < 0:
            raise InvalidJobDataException("Minimum experience years cannot be negative")
        
        if self.max_experience_years and self.max_experience_years < self.min_experience_years:
            raise InvalidJobDataException("Maximum experience cannot be less than minimum")


@dataclass
class SalaryRange(ValueObject):
    min_salary: float
    max_salary: float
    currency: str = "USD"
    frequency: str = "yearly"  # "yearly", "monthly", "hourly"
    is_negotiable: bool = True
    
    def _validate(self):
        if self.min_salary < 0 or self.max_salary < 0:
            raise InvalidJobDataException("Salary cannot be negative")
        
        if self.min_salary > self.max_salary:
            raise InvalidJobDataException("Minimum salary cannot exceed maximum salary")


@dataclass
class JobLocation(ValueObject):
    city: str = ""
    state: Optional[str] = None
    country: str = ""
    is_remote: bool = False
    is_hybrid: bool = False
    timezone: Optional[str] = None
    
    def _validate(self):
        if not self.is_remote and not self.city:
            raise InvalidJobDataException("City is required for non-remote positions")


@dataclass
class Job(BaseEntity):
    title: str = ""
    description: str = ""
    partner_id: str = ""
    requirements: Optional[JobRequirements] = None
    salary_range: Optional[SalaryRange] = None
    location: Optional[JobLocation] = None
    job_type: JobType = JobType.FULL_TIME
    status: JobStatus = JobStatus.DRAFT
    posted_date: Optional[datetime] = None
    closing_date: Optional[datetime] = None
    filled_date: Optional[datetime] = None
    department: str = ""
    reporting_to: str = ""
    team_size: Optional[int] = None
    benefits: List[str] = field(default_factory=list)
    perks: List[str] = field(default_factory=list)
    application_deadline: Optional[datetime] = None
    expected_start_date: Optional[datetime] = None
    max_applications: Optional[int] = None
    current_applications: int = 0
    tags: List[str] = field(default_factory=list)
    internal_notes: str = ""
    contact_person: str = ""
    
    def __post_init__(self):
        if not self.title:
            raise InvalidJobDataException("Job title is required")
        
        if not self.partner_id:
            raise InvalidJobDataException("Partner ID is required")
        
        if not self.requirements:
            self.requirements = JobRequirements()
        
        if not self.location:
            self.location = JobLocation(is_remote=True)
    
    def post_job(self):
        """Post the job (make it available for applications)"""
        if self.status != JobStatus.DRAFT:
            raise InvalidJobDataException(f"Cannot post job in {self.status.value} status")
        
        if not self.description:
            raise InvalidJobDataException("Job description is required to post")
        
        self.status = JobStatus.OPEN
        self.posted_date = datetime.utcnow()
        self.update_timestamp()
    
    def pause_job(self, reason: str = ""):
        """Pause job applications"""
        if self.status != JobStatus.OPEN:
            raise InvalidJobDataException(f"Cannot pause job in {self.status.value} status")
        
        self.status = JobStatus.PAUSED
        if reason:
            self.internal_notes += f"\nPaused: {reason} ({datetime.utcnow().isoformat()})"
        self.update_timestamp()
    
    def resume_job(self):
        """Resume job applications"""
        if self.status != JobStatus.PAUSED:
            raise InvalidJobDataException(f"Cannot resume job in {self.status.value} status")
        
        self.status = JobStatus.OPEN
        self.internal_notes += f"\nResumed: {datetime.utcnow().isoformat()}"
        self.update_timestamp()
    
    def close_job(self, reason: str = ""):
        """Close job (no longer accepting applications)"""
        if self.status in [JobStatus.CLOSED, JobStatus.FILLED, JobStatus.CANCELLED]:
            raise InvalidJobDataException(f"Job is already {self.status.value}")
        
        self.status = JobStatus.CLOSED
        self.closing_date = datetime.utcnow()
        if reason:
            self.internal_notes += f"\nClosed: {reason} ({self.closing_date.isoformat()})"
        self.update_timestamp()
    
    def mark_as_filled(self, candidate_id: str = ""):
        """Mark job as filled"""
        if self.status not in [JobStatus.OPEN, JobStatus.PAUSED]:
            raise InvalidJobDataException(f"Cannot mark job as filled in {self.status.value} status")
        
        self.status = JobStatus.FILLED
        self.filled_date = datetime.utcnow()
        if candidate_id:
            self.internal_notes += f"\nFilled by candidate: {candidate_id} ({self.filled_date.isoformat()})"
        self.update_timestamp()
    
    def cancel_job(self, reason: str):
        """Cancel the job"""
        if self.status in [JobStatus.FILLED, JobStatus.CANCELLED]:
            raise InvalidJobDataException(f"Cannot cancel job in {self.status.value} status")
        
        self.status = JobStatus.CANCELLED
        self.internal_notes += f"\nCancelled: {reason} ({datetime.utcnow().isoformat()})"
        self.update_timestamp()
    
    def can_accept_applications(self) -> bool:
        """Check if job can accept new applications"""
        if self.status != JobStatus.OPEN:
            return False
        
        if self.application_deadline and datetime.utcnow() > self.application_deadline:
            return False
        
        if self.max_applications and self.current_applications >= self.max_applications:
            return False
        
        return True
    
    def increment_applications(self):
        """Increment application count"""
        self.current_applications += 1
        self.update_timestamp()
    
    def decrement_applications(self):
        """Decrement application count"""
        if self.current_applications > 0:
            self.current_applications -= 1
            self.update_timestamp()
    
    def update_requirements(self, new_requirements: Dict[str, Any]):
        """Update job requirements"""
        if self.status == JobStatus.FILLED:
            raise InvalidJobDataException("Cannot update requirements for filled job")
        
        # Update requirements fields
        for key, value in new_requirements.items():
            if hasattr(self.requirements, key):
                setattr(self.requirements, key, value)
        
        self.update_timestamp()
    
    def add_tag(self, tag: str):
        """Add a tag to the job"""
        if tag not in self.tags:
            self.tags.append(tag)
            self.update_timestamp()
    
    def remove_tag(self, tag: str):
        """Remove a tag from the job"""
        if tag in self.tags:
            self.tags.remove(tag)
            self.update_timestamp()
    
    def calculate_match_score(self, candidate_profile: Dict[str, Any]) -> float:
        """Calculate how well a candidate matches this job"""
        score = 0.0
        max_score = 0.0
        
        # Skills matching (40% of total score)
        if self.requirements.required_skills:
            candidate_skills = [skill.lower() for skill in candidate_profile.get('skills', [])]
            required_skills = [skill.lower() for skill in self.requirements.required_skills]
            
            matched_required = sum(1 for skill in required_skills if skill in candidate_skills)
            score += (matched_required / len(required_skills)) * 40
            
            # Bonus for nice-to-have skills
            if self.requirements.nice_to_have_skills:
                nice_to_have = [skill.lower() for skill in self.requirements.nice_to_have_skills]
                matched_nice = sum(1 for skill in nice_to_have if skill in candidate_skills)
                score += (matched_nice / len(nice_to_have)) * 10
        
        max_score += 50  # 40 for required + 10 for nice-to-have
        
        # Experience level matching (25% of total score)
        candidate_level = candidate_profile.get('experience_level', '').upper()
        level_hierarchy = {
            'JUNIOR': 1, 'MID': 2, 'SENIOR': 3, 'LEAD': 4, 'PRINCIPAL': 5
        }
        
        candidate_level_val = level_hierarchy.get(candidate_level, 0)
        required_level_val = level_hierarchy.get(self.requirements.experience_level.value, 1)
        
        if candidate_level_val >= required_level_val:
            score += 25
        elif candidate_level_val == required_level_val - 1:
            score += 20  # Close match
        
        max_score += 25
        
        # Experience years matching (15% of total score)
        candidate_years = candidate_profile.get('total_experience_years', 0)
        if candidate_years >= self.requirements.min_experience_years:
            if self.requirements.max_experience_years:
                if candidate_years <= self.requirements.max_experience_years:
                    score += 15  # Perfect fit
                elif candidate_years <= self.requirements.max_experience_years * 1.2:
                    score += 12  # Slightly overqualified
                else:
                    score += 8  # Overqualified
            else:
                score += 15
        elif candidate_years >= self.requirements.min_experience_years * 0.8:
            score += 10  # Close match
        
        max_score += 15
        
        # Location matching (10% of total score)
        if self.location.is_remote or candidate_profile.get('location', {}).get('remote_friendly', False):
            score += 10
        elif self.location.city and candidate_profile.get('location', {}).get('city', ''):
            if self.location.city.lower() == candidate_profile['location']['city'].lower():
                score += 10
            elif self.location.country.lower() == candidate_profile['location']['country'].lower():
                score += 7  # Same country
        
        max_score += 10
        
        return min(100.0, (score / max_score * 100)) if max_score > 0 else 0.0
    
    def to_search_document(self) -> Dict[str, Any]:
        """Convert job to search document for indexing"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'partner_id': self.partner_id,
            'status': self.status.value,
            'job_type': self.job_type.value,
            'department': self.department,
            'required_skills': self.requirements.required_skills if self.requirements else [],
            'nice_to_have_skills': self.requirements.nice_to_have_skills if self.requirements else [],
            'experience_level': self.requirements.experience_level.value if self.requirements else 'JUNIOR',
            'min_experience_years': self.requirements.min_experience_years if self.requirements else 0,
            'max_experience_years': self.requirements.max_experience_years if self.requirements else None,
            'location': {
                'city': self.location.city if self.location else '',
                'country': self.location.country if self.location else '',
                'is_remote': self.location.is_remote if self.location else False,
                'is_hybrid': self.location.is_hybrid if self.location else False
            },
            'salary_range': {
                'min': self.salary_range.min_salary if self.salary_range else 0,
                'max': self.salary_range.max_salary if self.salary_range else 0,
                'currency': self.salary_range.currency if self.salary_range else 'USD'
            },
            'benefits': self.benefits,
            'perks': self.perks,
            'tags': self.tags,
            'posted_date': self.posted_date.isoformat() if self.posted_date else None,
            'application_deadline': self.application_deadline.isoformat() if self.application_deadline else None,
            'max_applications': self.max_applications,
            'current_applications': self.current_applications,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


@dataclass
class JobApplication(BaseEntity):
    job_id: str = ""
    candidate_id: str = ""
    status: ApplicationStatus = ApplicationStatus.SUBMITTED
    cover_letter: str = ""
    resume_url: Optional[str] = None
    application_answers: Dict[str, Any] = field(default_factory=dict)
    recruiter_notes: str = ""
    interview_feedback: List[Dict[str, Any]] = field(default_factory=list)
    status_history: List[Dict[str, Any]] = field(default_factory=list)
    withdrawn_reason: Optional[str] = None
    rejection_reason: Optional[str] = None
    
    def __post_init__(self):
        if not self.job_id:
            raise InvalidJobDataException("Job ID is required")
        
        if not self.candidate_id:
            raise InvalidJobDataException("Candidate ID is required")
        
        # Initialize status history
        if not self.status_history:
            self.status_history = [{
                'status': self.status.value,
                'timestamp': self.created_at.isoformat(),
                'changed_by': 'system',
                'notes': 'Application submitted'
            }]
    
    def update_status(self, new_status: ApplicationStatus, changed_by: str, notes: str = ""):
        """Update application status"""
        if self.status == new_status:
            return
        
        old_status = self.status
        self.status = new_status
        self.update_timestamp()
        
        # Add to history
        self.status_history.append({
            'from_status': old_status.value,
            'to_status': new_status.value,
            'timestamp': self.updated_at.isoformat(),
            'changed_by': changed_by,
            'notes': notes
        })
    
    def withdraw_application(self, reason: str, withdrawn_by: str):
        """Withdraw the application"""
        if self.status in [ApplicationStatus.ACCEPTED, ApplicationStatus.REJECTED]:
            raise InvalidJobDataException(f"Cannot withdraw application in {self.status.value} status")
        
        self.withdrawn_reason = reason
        self.update_status(ApplicationStatus.WITHDRAWN, withdrawn_by, f"Withdrawn: {reason}")
    
    def reject_application(self, reason: str, rejected_by: str):
        """Reject the application"""
        if self.status in [ApplicationStatus.ACCEPTED, ApplicationStatus.WITHDRAWN]:
            raise InvalidJobDataException(f"Cannot reject application in {self.status.value} status")
        
        self.rejection_reason = reason
        self.update_status(ApplicationStatus.REJECTED, rejected_by, f"Rejected: {reason}")
    
    def add_interview_feedback(self, interviewer: str, feedback: str, score: int = None):
        """Add interview feedback"""
        self.interview_feedback.append({
            'interviewer': interviewer,
            'feedback': feedback,
            'score': score,
            'timestamp': datetime.utcnow().isoformat()
        })
        self.update_timestamp()
    
    def can_be_updated(self) -> bool:
        """Check if application can be updated"""
        return self.status not in [ApplicationStatus.ACCEPTED, ApplicationStatus.REJECTED, ApplicationStatus.WITHDRAWN]