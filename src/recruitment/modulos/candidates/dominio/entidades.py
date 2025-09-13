from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum

from recruitment.seedwork.dominio.entidades import BaseEntity, ValueObject
from recruitment.seedwork.dominio.excepciones import InvalidCandidateDataException


class AvailabilityStatus(Enum):
    AVAILABLE = "AVAILABLE"
    BUSY = "BUSY"
    NOT_LOOKING = "NOT_LOOKING"
    HIRED = "HIRED"


class ExperienceLevel(Enum):
    JUNIOR = "JUNIOR"
    MID = "MID"
    SENIOR = "SENIOR"
    LEAD = "LEAD"
    PRINCIPAL = "PRINCIPAL"


@dataclass
class ContactInfo(ValueObject):
    email: str
    phone: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    portfolio: Optional[str] = None
    
    def _validate(self):
        if not self.email or '@' not in self.email:
            raise InvalidCandidateDataException("Valid email is required")


@dataclass
class Address(ValueObject):
    street: Optional[str] = None
    city: str = ""
    state: Optional[str] = None
    country: str = ""
    postal_code: Optional[str] = None
    is_remote_friendly: bool = True
    
    def _validate(self):
        if not self.city and not self.is_remote_friendly:
            raise InvalidCandidateDataException("City is required for non-remote candidates")


@dataclass
class Skill(ValueObject):
    name: str
    level: int  # 1-10 scale
    years_experience: int
    category: str  # "technical", "soft", "language", etc.
    
    def _validate(self):
        if not self.name:
            raise InvalidCandidateDataException("Skill name is required")
        
        if not 1 <= self.level <= 10:
            raise InvalidCandidateDataException("Skill level must be between 1 and 10")
        
        if self.years_experience < 0:
            raise InvalidCandidateDataException("Years of experience cannot be negative")


@dataclass
class WorkExperience(ValueObject):
    company: str
    position: str
    start_date: datetime
    end_date: Optional[datetime] = None
    description: Optional[str] = None
    technologies: List[str] = field(default_factory=list)
    achievements: List[str] = field(default_factory=list)
    is_current: bool = False
    
    def _validate(self):
        if not self.company or not self.position:
            raise InvalidCandidateDataException("Company and position are required")
        
        if self.end_date and self.end_date < self.start_date:
            raise InvalidCandidateDataException("End date cannot be before start date")
        
        if self.is_current and self.end_date:
            raise InvalidCandidateDataException("Current position cannot have end date")


@dataclass
class Education(ValueObject):
    institution: str
    degree: str
    field_of_study: str
    start_date: datetime
    end_date: Optional[datetime] = None
    gpa: Optional[float] = None
    is_current: bool = False
    
    def _validate(self):
        if not self.institution or not self.degree or not self.field_of_study:
            raise InvalidCandidateDataException("Institution, degree, and field of study are required")
        
        if self.gpa and not 0.0 <= self.gpa <= 4.0:
            raise InvalidCandidateDataException("GPA must be between 0.0 and 4.0")


@dataclass
class SalaryExpectation(ValueObject):
    min_salary: float
    max_salary: float
    currency: str = "USD"
    frequency: str = "yearly"  # "yearly", "monthly", "hourly"
    
    def _validate(self):
        if self.min_salary < 0 or self.max_salary < 0:
            raise InvalidCandidateDataException("Salary cannot be negative")
        
        if self.min_salary > self.max_salary:
            raise InvalidCandidateDataException("Minimum salary cannot exceed maximum salary")


@dataclass
class Candidate(BaseEntity):
    name: str = ""
    contact_info: Optional[ContactInfo] = None
    address: Optional[Address] = None
    skills: List[Skill] = field(default_factory=list)
    work_experience: List[WorkExperience] = field(default_factory=list)
    education: List[Education] = field(default_factory=list)
    availability: AvailabilityStatus = AvailabilityStatus.AVAILABLE
    experience_level: ExperienceLevel = ExperienceLevel.JUNIOR
    salary_expectation: Optional[SalaryExpectation] = None
    summary: str = ""
    certifications: List[str] = field(default_factory=list)
    languages: List[Dict[str, str]] = field(default_factory=list)  # [{"name": "English", "level": "Native"}]
    preferences: Dict[str, Any] = field(default_factory=dict)
    total_experience_years: int = 0
    
    def __post_init__(self):
        if not self.name:
            raise InvalidCandidateDataException("Candidate name is required")
        
        if not self.contact_info:
            raise InvalidCandidateDataException("Contact information is required")
        
        self._calculate_total_experience()
    
    def _calculate_total_experience(self):
        """Calculate total years of experience from work history"""
        total_days = 0
        current_date = datetime.utcnow()
        
        for experience in self.work_experience:
            end_date = experience.end_date or current_date
            duration = end_date - experience.start_date
            total_days += duration.days
        
        self.total_experience_years = max(0, total_days // 365)
    
    def add_skill(self, skill: Skill):
        """Add a skill to the candidate"""
        # Remove existing skill with same name
        self.skills = [s for s in self.skills if s.name.lower() != skill.name.lower()]
        self.skills.append(skill)
        self.update_timestamp()
    
    def update_skill_level(self, skill_name: str, new_level: int, new_experience: int):
        """Update skill level and experience"""
        for skill in self.skills:
            if skill.name.lower() == skill_name.lower():
                skill.level = new_level
                skill.years_experience = new_experience
                self.update_timestamp()
                return
        
        raise InvalidCandidateDataException(f"Skill '{skill_name}' not found")
    
    def add_work_experience(self, experience: WorkExperience):
        """Add work experience"""
        if experience.is_current:
            # Set other experiences as not current
            for exp in self.work_experience:
                exp.is_current = False
        
        self.work_experience.append(experience)
        self._calculate_total_experience()
        self.update_timestamp()
    
    def update_availability(self, status: AvailabilityStatus, reason: str = None):
        """Update candidate availability"""
        old_status = self.availability
        self.availability = status
        self.update_timestamp()
        
        # Add to preferences for tracking
        if 'availability_history' not in self.preferences:
            self.preferences['availability_history'] = []
        
        self.preferences['availability_history'].append({
            'from_status': old_status.value,
            'to_status': status.value,
            'reason': reason,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    def get_skills_by_category(self, category: str) -> List[Skill]:
        """Get skills filtered by category"""
        return [skill for skill in self.skills if skill.category.lower() == category.lower()]
    
    def get_technical_skills(self) -> List[str]:
        """Get list of technical skill names"""
        technical_skills = self.get_skills_by_category("technical")
        return [skill.name for skill in technical_skills]
    
    def get_experience_in_role(self, role: str) -> int:
        """Get years of experience in a specific role"""
        years = 0
        current_date = datetime.utcnow()
        
        for experience in self.work_experience:
            if role.lower() in experience.position.lower():
                end_date = experience.end_date or current_date
                duration = end_date - experience.start_date
                years += duration.days // 365
        
        return years
    
    def matches_criteria(self, criteria: Dict[str, Any]) -> Dict[str, Any]:
        """Check if candidate matches given criteria and return match details"""
        match_score = 0.0
        max_score = 0.0
        match_details = {}
        
        # Required skills matching
        if 'required_skills' in criteria:
            required_skills = criteria['required_skills']
            candidate_skills = [skill.name.lower() for skill in self.skills]
            
            matched_skills = []
            for required_skill in required_skills:
                if required_skill.lower() in candidate_skills:
                    matched_skills.append(required_skill)
                    match_score += 10
                max_score += 10
            
            match_details['skills'] = {
                'required': required_skills,
                'matched': matched_skills,
                'match_rate': len(matched_skills) / len(required_skills) if required_skills else 1.0
            }
        
        # Experience level matching
        if 'experience_level' in criteria:
            required_level = ExperienceLevel(criteria['experience_level'])
            level_map = {
                ExperienceLevel.JUNIOR: 1,
                ExperienceLevel.MID: 2,
                ExperienceLevel.SENIOR: 3,
                ExperienceLevel.LEAD: 4,
                ExperienceLevel.PRINCIPAL: 5
            }
            
            candidate_level = level_map.get(self.experience_level, 0)
            required_level_val = level_map.get(required_level, 0)
            
            if candidate_level >= required_level_val:
                match_score += 20
            elif candidate_level == required_level_val - 1:
                match_score += 15  # Close match
            elif candidate_level == required_level_val + 1:
                match_score += 10  # Overqualified
            
            max_score += 20
            match_details['experience_level'] = {
                'required': required_level.value,
                'candidate': self.experience_level.value,
                'match': candidate_level >= required_level_val
            }
        
        # Years of experience matching
        if 'min_experience_years' in criteria:
            min_years = criteria['min_experience_years']
            if self.total_experience_years >= min_years:
                match_score += 15
            elif self.total_experience_years >= min_years * 0.8:
                match_score += 10  # Close match
            
            max_score += 15
            match_details['experience_years'] = {
                'required': min_years,
                'candidate': self.total_experience_years,
                'match': self.total_experience_years >= min_years
            }
        
        # Location matching
        if 'location' in criteria and self.address:
            required_location = criteria['location'].lower()
            candidate_location = f"{self.address.city} {self.address.country}".lower()
            
            if required_location == "remote" and self.address.is_remote_friendly:
                match_score += 10
            elif required_location in candidate_location:
                match_score += 10
            elif self.address.is_remote_friendly:
                match_score += 5  # Can work remotely
            
            max_score += 10
            match_details['location'] = {
                'required': criteria['location'],
                'candidate': candidate_location,
                'remote_friendly': self.address.is_remote_friendly
            }
        
        # Salary matching
        if 'max_salary' in criteria and self.salary_expectation:
            max_offered = criteria['max_salary']
            if self.salary_expectation.min_salary <= max_offered:
                if self.salary_expectation.max_salary <= max_offered:
                    match_score += 10  # Perfect fit
                else:
                    match_score += 5  # Minimum is acceptable
            
            max_score += 10
            match_details['salary'] = {
                'max_offered': max_offered,
                'candidate_range': [self.salary_expectation.min_salary, self.salary_expectation.max_salary],
                'match': self.salary_expectation.min_salary <= max_offered
            }
        
        final_score = (match_score / max_score * 100) if max_score > 0 else 0
        
        return {
            'match_score': round(final_score, 2),
            'details': match_details,
            'is_available': self.availability == AvailabilityStatus.AVAILABLE
        }
    
    def to_search_document(self) -> Dict[str, Any]:
        """Convert candidate to search document for indexing"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.contact_info.email if self.contact_info else '',
            'skills': [skill.name for skill in self.skills],
            'technical_skills': self.get_technical_skills(),
            'experience_level': self.experience_level.value,
            'total_experience_years': self.total_experience_years,
            'availability': self.availability.value,
            'summary': self.summary,
            'location': {
                'city': self.address.city if self.address else '',
                'country': self.address.country if self.address else '',
                'remote_friendly': self.address.is_remote_friendly if self.address else True
            },
            'salary_expectation': {
                'min': self.salary_expectation.min_salary if self.salary_expectation else 0,
                'max': self.salary_expectation.max_salary if self.salary_expectation else 0,
                'currency': self.salary_expectation.currency if self.salary_expectation else 'USD'
            },
            'work_experience': [
                {
                    'company': exp.company,
                    'position': exp.position,
                    'technologies': exp.technologies,
                    'is_current': exp.is_current
                } for exp in self.work_experience
            ],
            'education': [
                {
                    'institution': edu.institution,
                    'degree': edu.degree,
                    'field_of_study': edu.field_of_study
                } for edu in self.education
            ],
            'certifications': self.certifications,
            'languages': self.languages,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }