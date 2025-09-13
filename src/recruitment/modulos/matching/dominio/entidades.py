from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Dict, Any, Optional, Set
from uuid import uuid4

from recruitment.seedwork.dominio.entidades import AggregateRoot
from recruitment.seedwork.dominio.eventos import DomainEvent


class MatchingAlgorithm(Enum):
    BASIC_SKILLS = "BASIC_SKILLS"
    WEIGHTED_CRITERIA = "WEIGHTED_CRITERIA"
    ADVANCED_ENHANCED = "ADVANCED_ENHANCED"
    SEMANTIC_MATCHING = "SEMANTIC_MATCHING"
    HYBRID_APPROACH = "HYBRID_APPROACH"


class MatchingStatus(Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class MatchQuality(Enum):
    EXCELLENT = "EXCELLENT"  # 90-100%
    GOOD = "GOOD"           # 75-89%
    FAIR = "FAIR"           # 60-74%
    POOR = "POOR"           # 40-59%
    NOT_SUITABLE = "NOT_SUITABLE"  # <40%


class PreferenceType(Enum):
    MUST_HAVE = "MUST_HAVE"
    NICE_TO_HAVE = "NICE_TO_HAVE"
    DEAL_BREAKER = "DEAL_BREAKER"


@dataclass
class SkillMatch:
    skill_name: str
    required_level: int
    candidate_level: int
    match_score: float
    is_critical: bool
    weight: float = 1.0


@dataclass
class LocationMatch:
    job_location: str
    candidate_location: str
    candidate_willing_to_relocate: bool
    distance_km: Optional[float]
    remote_work_possible: bool
    match_score: float


@dataclass
class SalaryMatch:
    job_salary_min: Optional[float]
    job_salary_max: Optional[float]
    candidate_expected_salary: Optional[float]
    candidate_min_salary: Optional[float]
    match_score: float
    within_budget: bool


@dataclass
class ExperienceMatch:
    required_years: int
    candidate_years: int
    relevant_experience_years: int
    industry_match: bool
    role_match: bool
    match_score: float


@dataclass
class CultureMatch:
    company_values: List[str]
    candidate_values: List[str]
    work_style_preferences: Dict[str, Any]
    team_fit_score: float
    culture_alignment_score: float


@dataclass
class MatchingCriteria:
    criteria_id: str
    name: str
    description: str
    weight: float  # 0.0 to 1.0
    preference_type: PreferenceType
    evaluation_function: str  # Name of the evaluation function to use


@dataclass
class MatchResult:
    match_id: str
    job_id: str
    candidate_id: str
    overall_score: float
    match_quality: MatchQuality
    skill_matches: List[SkillMatch]
    location_match: LocationMatch
    salary_match: SalaryMatch
    experience_match: ExperienceMatch
    culture_match: Optional[CultureMatch]
    algorithm_used: MatchingAlgorithm
    confidence_score: float
    explanation: str
    recommendations: List[str]
    generated_at: datetime


# Domain Events
@dataclass
class MatchingProcessStarted(DomainEvent):
    process_id: str
    job_id: str
    algorithm: MatchingAlgorithm
    candidate_count: int
    criteria_count: int


@dataclass
class CandidateMatched(DomainEvent):
    match_id: str
    job_id: str
    candidate_id: str
    overall_score: float
    match_quality: MatchQuality
    algorithm_used: MatchingAlgorithm


@dataclass
class MatchingProcessCompleted(DomainEvent):
    process_id: str
    job_id: str
    total_candidates_evaluated: int
    successful_matches: int
    processing_time_seconds: float


@dataclass
class HighQualityMatchFound(DomainEvent):
    match_id: str
    job_id: str
    candidate_id: str
    overall_score: float
    partner_id: str


class MatchingEngine(AggregateRoot):
    def __init__(
        self,
        algorithm: MatchingAlgorithm = MatchingAlgorithm.WEIGHTED_CRITERIA,
        default_criteria: List[MatchingCriteria] = None
    ):
        super().__init__()
        self.id = str(uuid4())
        self._algorithm = algorithm
        self._matching_criteria = default_criteria or self._get_default_criteria()
        self._match_results: List[MatchResult] = []
        self._performance_metrics: Dict[str, Any] = {}
        self._created_at = datetime.utcnow()
        self._last_updated = datetime.utcnow()

    @property
    def algorithm(self) -> MatchingAlgorithm:
        return self._algorithm

    @property
    def matching_criteria(self) -> List[MatchingCriteria]:
        return self._matching_criteria.copy()

    @property
    def match_results(self) -> List[MatchResult]:
        return self._match_results.copy()

    def configure_criteria(self, criteria: List[MatchingCriteria]):
        total_weight = sum(c.weight for c in criteria)
        if abs(total_weight - 1.0) > 0.01:
            raise ValueError(f"Total criteria weights must sum to 1.0, got {total_weight}")
        
        self._matching_criteria = criteria
        self._last_updated = datetime.utcnow()

    def evaluate_candidate_match(
        self,
        job_data: Dict[str, Any],
        candidate_data: Dict[str, Any]
    ) -> MatchResult:
        start_time = datetime.utcnow()
        
        # Extract data for matching
        job_id = job_data.get("id")
        candidate_id = candidate_data.get("id")
        
        if not job_id or not candidate_id:
            raise ValueError("Job ID and Candidate ID are required")

        # Perform skill matching
        skill_matches = self._evaluate_skills_match(
            job_data.get("required_skills", []),
            job_data.get("preferred_skills", []),
            candidate_data.get("skills", [])
        )

        # Perform location matching
        location_match = self._evaluate_location_match(
            job_data.get("location"),
            candidate_data.get("location"),
            candidate_data.get("preferences", {})
        )

        # Perform salary matching
        salary_match = self._evaluate_salary_match(
            job_data.get("salary_min"),
            job_data.get("salary_max"),
            candidate_data.get("expected_salary"),
            candidate_data.get("min_salary")
        )

        # Perform experience matching
        experience_match = self._evaluate_experience_match(
            job_data.get("experience_level"),
            job_data.get("required_experience_years", 0),
            candidate_data.get("years_of_experience", 0),
            candidate_data.get("work_history", [])
        )

        # Calculate overall score using configured algorithm
        overall_score = self._calculate_overall_score(
            skill_matches, location_match, salary_match, experience_match
        )

        # Determine match quality
        match_quality = self._determine_match_quality(overall_score)

        # Generate explanation and recommendations
        explanation, recommendations = self._generate_explanation_and_recommendations(
            skill_matches, location_match, salary_match, experience_match, overall_score
        )

        # Calculate confidence score
        confidence_score = self._calculate_confidence_score(
            skill_matches, location_match, salary_match, experience_match
        )

        match_result = MatchResult(
            match_id=str(uuid4()),
            job_id=job_id,
            candidate_id=candidate_id,
            overall_score=overall_score,
            match_quality=match_quality,
            skill_matches=skill_matches,
            location_match=location_match,
            salary_match=salary_match,
            experience_match=experience_match,
            culture_match=None,  # TODO: Implement culture matching
            algorithm_used=self._algorithm,
            confidence_score=confidence_score,
            explanation=explanation,
            recommendations=recommendations,
            generated_at=datetime.utcnow()
        )

        self._match_results.append(match_result)

        # Publish events
        self.publicar_evento(CandidateMatched(
            event_id=str(uuid4()),
            occurred_on=datetime.utcnow(),
            match_id=match_result.match_id,
            job_id=job_id,
            candidate_id=candidate_id,
            overall_score=overall_score,
            match_quality=match_quality,
            algorithm_used=self._algorithm
        ))

        # Publish high-quality match event if applicable
        if match_quality in [MatchQuality.EXCELLENT, MatchQuality.GOOD]:
            self.publicar_evento(HighQualityMatchFound(
                event_id=str(uuid4()),
                occurred_on=datetime.utcnow(),
                match_id=match_result.match_id,
                job_id=job_id,
                candidate_id=candidate_id,
                overall_score=overall_score,
                partner_id=job_data.get("partner_id", "")
            ))

        # Update performance metrics
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        self._update_performance_metrics(processing_time, match_quality)

        return match_result

    def batch_evaluate_candidates(
        self,
        job_data: Dict[str, Any],
        candidates_data: List[Dict[str, Any]],
        max_results: int = 50
    ) -> List[MatchResult]:
        process_id = str(uuid4())
        start_time = datetime.utcnow()

        self.publicar_evento(MatchingProcessStarted(
            event_id=str(uuid4()),
            occurred_on=datetime.utcnow(),
            process_id=process_id,
            job_id=job_data.get("id"),
            algorithm=self._algorithm,
            candidate_count=len(candidates_data),
            criteria_count=len(self._matching_criteria)
        ))

        matches = []
        for candidate_data in candidates_data:
            try:
                match_result = self.evaluate_candidate_match(job_data, candidate_data)
                matches.append(match_result)
            except Exception as e:
                # Log error but continue processing other candidates
                continue

        # Sort by overall score and limit results
        matches.sort(key=lambda x: x.overall_score, reverse=True)
        top_matches = matches[:max_results]

        # Calculate processing time
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        successful_matches = len([m for m in top_matches if m.match_quality != MatchQuality.NOT_SUITABLE])

        self.publicar_evento(MatchingProcessCompleted(
            event_id=str(uuid4()),
            occurred_on=datetime.utcnow(),
            process_id=process_id,
            job_id=job_data.get("id"),
            total_candidates_evaluated=len(candidates_data),
            successful_matches=successful_matches,
            processing_time_seconds=processing_time
        ))

        return top_matches

    def _evaluate_skills_match(
        self,
        required_skills: List[str],
        preferred_skills: List[str],
        candidate_skills: List[Dict[str, Any]]
    ) -> List[SkillMatch]:
        skill_matches = []
        
        # Convert candidate skills to lookup dict
        candidate_skill_levels = {
            skill.get("name", "").lower(): skill.get("level", 1)
            for skill in candidate_skills
        }

        # Evaluate required skills
        for required_skill in required_skills:
            skill_name = required_skill.lower()
            candidate_level = candidate_skill_levels.get(skill_name, 0)
            required_level = 3  # Default required level
            
            if candidate_level == 0:
                match_score = 0.0
            else:
                match_score = min(candidate_level / required_level, 1.0)

            skill_matches.append(SkillMatch(
                skill_name=required_skill,
                required_level=required_level,
                candidate_level=candidate_level,
                match_score=match_score,
                is_critical=True,
                weight=1.0
            ))

        # Evaluate preferred skills (bonus points)
        for preferred_skill in preferred_skills:
            skill_name = preferred_skill.lower()
            if skill_name not in [s.skill_name.lower() for s in skill_matches]:
                candidate_level = candidate_skill_levels.get(skill_name, 0)
                match_score = 1.0 if candidate_level > 0 else 0.0

                skill_matches.append(SkillMatch(
                    skill_name=preferred_skill,
                    required_level=1,
                    candidate_level=candidate_level,
                    match_score=match_score,
                    is_critical=False,
                    weight=0.5
                ))

        return skill_matches

    def _evaluate_location_match(
        self,
        job_location: Optional[str],
        candidate_location: Optional[str],
        candidate_preferences: Dict[str, Any]
    ) -> LocationMatch:
        if not job_location:
            return LocationMatch(
                job_location="",
                candidate_location=candidate_location or "",
                candidate_willing_to_relocate=True,
                distance_km=None,
                remote_work_possible=True,
                match_score=1.0
            )

        willing_to_relocate = candidate_preferences.get("willing_to_relocate", False)
        remote_work_acceptable = candidate_preferences.get("remote_work", False)
        
        # Simple location matching logic
        if job_location.lower() == "remote":
            match_score = 1.0
        elif candidate_location and job_location.lower() == candidate_location.lower():
            match_score = 1.0
        elif willing_to_relocate:
            match_score = 0.7
        elif remote_work_acceptable:
            match_score = 0.8
        else:
            match_score = 0.3

        return LocationMatch(
            job_location=job_location,
            candidate_location=candidate_location or "",
            candidate_willing_to_relocate=willing_to_relocate,
            distance_km=None,  # TODO: Calculate actual distance
            remote_work_possible=job_location.lower() == "remote" or remote_work_acceptable,
            match_score=match_score
        )

    def _evaluate_salary_match(
        self,
        job_salary_min: Optional[float],
        job_salary_max: Optional[float],
        candidate_expected_salary: Optional[float],
        candidate_min_salary: Optional[float]
    ) -> SalaryMatch:
        if not job_salary_min and not job_salary_max:
            return SalaryMatch(
                job_salary_min=None,
                job_salary_max=None,
                candidate_expected_salary=candidate_expected_salary,
                candidate_min_salary=candidate_min_salary,
                match_score=1.0,
                within_budget=True
            )

        # Use candidate's minimum salary if available, otherwise expected salary
        candidate_requirement = candidate_min_salary or candidate_expected_salary
        
        if not candidate_requirement:
            return SalaryMatch(
                job_salary_min=job_salary_min,
                job_salary_max=job_salary_max,
                candidate_expected_salary=candidate_expected_salary,
                candidate_min_salary=candidate_min_salary,
                match_score=0.8,  # Neutral score when no salary info
                within_budget=True
            )

        job_max = job_salary_max or job_salary_min
        job_min = job_salary_min or job_salary_max

        if not job_max:
            match_score = 0.8
            within_budget = True
        elif candidate_requirement <= job_max:
            if candidate_requirement >= job_min:
                match_score = 1.0  # Perfect match
            else:
                match_score = 0.9  # Good match, candidate is below range
            within_budget = True
        else:
            # Candidate wants more than job offers
            overage_percent = (candidate_requirement - job_max) / job_max
            if overage_percent <= 0.1:  # Within 10%
                match_score = 0.7
                within_budget = False
            elif overage_percent <= 0.2:  # Within 20%
                match_score = 0.5
                within_budget = False
            else:
                match_score = 0.2
                within_budget = False

        return SalaryMatch(
            job_salary_min=job_salary_min,
            job_salary_max=job_salary_max,
            candidate_expected_salary=candidate_expected_salary,
            candidate_min_salary=candidate_min_salary,
            match_score=match_score,
            within_budget=within_budget
        )

    def _evaluate_experience_match(
        self,
        job_experience_level: Optional[str],
        required_experience_years: int,
        candidate_experience_years: int,
        candidate_work_history: List[Dict[str, Any]]
    ) -> ExperienceMatch:
        # Calculate relevant experience from work history
        relevant_experience_years = candidate_experience_years
        industry_match = False
        role_match = False

        # TODO: Implement more sophisticated experience matching based on work history

        # Simple experience matching
        if candidate_experience_years >= required_experience_years:
            if candidate_experience_years <= required_experience_years * 1.5:
                match_score = 1.0  # Perfect match
            else:
                match_score = 0.9  # Good but overqualified
        else:
            # Under-qualified
            experience_ratio = candidate_experience_years / max(required_experience_years, 1)
            match_score = max(experience_ratio * 0.8, 0.1)

        return ExperienceMatch(
            required_years=required_experience_years,
            candidate_years=candidate_experience_years,
            relevant_experience_years=relevant_experience_years,
            industry_match=industry_match,
            role_match=role_match,
            match_score=match_score
        )

    def _calculate_overall_score(
        self,
        skill_matches: List[SkillMatch],
        location_match: LocationMatch,
        salary_match: SalaryMatch,
        experience_match: ExperienceMatch
    ) -> float:
        if self._algorithm == MatchingAlgorithm.BASIC_SKILLS:
            return self._basic_skills_score(skill_matches)
        elif self._algorithm == MatchingAlgorithm.WEIGHTED_CRITERIA:
            return self._weighted_criteria_score(skill_matches, location_match, salary_match, experience_match)
        else:
            # Default to weighted criteria
            return self._weighted_criteria_score(skill_matches, location_match, salary_match, experience_match)

    def _basic_skills_score(self, skill_matches: List[SkillMatch]) -> float:
        if not skill_matches:
            return 0.0
        
        critical_skills = [s for s in skill_matches if s.is_critical]
        if not critical_skills:
            return 0.0
        
        total_score = sum(s.match_score for s in critical_skills)
        return total_score / len(critical_skills)

    def _weighted_criteria_score(
        self,
        skill_matches: List[SkillMatch],
        location_match: LocationMatch,
        salary_match: SalaryMatch,
        experience_match: ExperienceMatch
    ) -> float:
        # Default weights if no criteria configured
        skills_weight = 0.4
        location_weight = 0.2
        salary_weight = 0.2
        experience_weight = 0.2

        # Calculate skills score
        if skill_matches:
            critical_skills = [s for s in skill_matches if s.is_critical]
            if critical_skills:
                skills_score = sum(s.match_score for s in critical_skills) / len(critical_skills)
            else:
                skills_score = 0.5
        else:
            skills_score = 0.0

        # Combine all scores
        overall_score = (
            skills_score * skills_weight +
            location_match.match_score * location_weight +
            salary_match.match_score * salary_weight +
            experience_match.match_score * experience_weight
        )

        return min(max(overall_score, 0.0), 1.0)

    def _determine_match_quality(self, overall_score: float) -> MatchQuality:
        if overall_score >= 0.9:
            return MatchQuality.EXCELLENT
        elif overall_score >= 0.75:
            return MatchQuality.GOOD
        elif overall_score >= 0.6:
            return MatchQuality.FAIR
        elif overall_score >= 0.4:
            return MatchQuality.POOR
        else:
            return MatchQuality.NOT_SUITABLE

    def _generate_explanation_and_recommendations(
        self,
        skill_matches: List[SkillMatch],
        location_match: LocationMatch,
        salary_match: SalaryMatch,
        experience_match: ExperienceMatch,
        overall_score: float
    ) -> tuple[str, List[str]]:
        explanation_parts = []
        recommendations = []

        # Skills analysis
        critical_skills = [s for s in skill_matches if s.is_critical]
        missing_skills = [s for s in critical_skills if s.match_score < 0.5]
        strong_skills = [s for s in critical_skills if s.match_score >= 0.8]

        if strong_skills:
            explanation_parts.append(f"Strong match on {len(strong_skills)} critical skills")
        if missing_skills:
            explanation_parts.append(f"Missing {len(missing_skills)} required skills")
            recommendations.append("Consider skills training or alternative candidates")

        # Location analysis
        if location_match.match_score < 0.7:
            explanation_parts.append("Location compatibility concerns")
            if not location_match.candidate_willing_to_relocate:
                recommendations.append("Discuss remote work options or relocation package")

        # Salary analysis
        if not salary_match.within_budget:
            explanation_parts.append("Salary expectations exceed budget")
            recommendations.append("Negotiate salary or consider additional benefits")

        # Experience analysis
        if experience_match.match_score < 0.7:
            if experience_match.candidate_years < experience_match.required_years:
                explanation_parts.append("Candidate may be under-qualified")
                recommendations.append("Assess potential and willingness to learn")
            else:
                explanation_parts.append("Candidate may be overqualified")
                recommendations.append("Ensure role provides sufficient challenge")

        explanation = "; ".join(explanation_parts) if explanation_parts else "Good overall match"
        
        if not recommendations:
            recommendations.append("Proceed with interview process")

        return explanation, recommendations

    def _calculate_confidence_score(
        self,
        skill_matches: List[SkillMatch],
        location_match: LocationMatch,
        salary_match: SalaryMatch,
        experience_match: ExperienceMatch
    ) -> float:
        # Confidence based on availability of data and consistency of scores
        confidence_factors = []

        # Skills confidence
        if skill_matches:
            skills_variance = self._calculate_variance([s.match_score for s in skill_matches])
            skills_confidence = 1.0 - min(skills_variance, 0.5)
            confidence_factors.append(skills_confidence)

        # Location confidence (higher when clear yes/no)
        location_confidence = 0.9 if location_match.match_score in [0.0, 1.0] else 0.7
        confidence_factors.append(location_confidence)

        # Salary confidence (higher when salary info is available)
        salary_confidence = 0.9 if salary_match.candidate_expected_salary else 0.6
        confidence_factors.append(salary_confidence)

        # Experience confidence
        experience_confidence = 0.8
        confidence_factors.append(experience_confidence)

        return sum(confidence_factors) / len(confidence_factors) if confidence_factors else 0.5

    def _calculate_variance(self, values: List[float]) -> float:
        if len(values) <= 1:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance

    def _update_performance_metrics(self, processing_time: float, match_quality: MatchQuality):
        if "total_matches" not in self._performance_metrics:
            self._performance_metrics = {
                "total_matches": 0,
                "average_processing_time": 0.0,
                "quality_distribution": {quality.value: 0 for quality in MatchQuality}
            }

        self._performance_metrics["total_matches"] += 1
        
        # Update average processing time
        current_avg = self._performance_metrics["average_processing_time"]
        total_matches = self._performance_metrics["total_matches"]
        new_avg = ((current_avg * (total_matches - 1)) + processing_time) / total_matches
        self._performance_metrics["average_processing_time"] = new_avg

        # Update quality distribution
        self._performance_metrics["quality_distribution"][match_quality.value] += 1

    def _get_default_criteria(self) -> List[MatchingCriteria]:
        return [
            MatchingCriteria(
                criteria_id="skills",
                name="Skills Match",
                description="Match between required skills and candidate skills",
                weight=0.4,
                preference_type=PreferenceType.MUST_HAVE,
                evaluation_function="evaluate_skills"
            ),
            MatchingCriteria(
                criteria_id="experience",
                name="Experience Match",
                description="Match between required experience and candidate experience",
                weight=0.2,
                preference_type=PreferenceType.MUST_HAVE,
                evaluation_function="evaluate_experience"
            ),
            MatchingCriteria(
                criteria_id="location",
                name="Location Match",
                description="Geographic compatibility",
                weight=0.2,
                preference_type=PreferenceType.NICE_TO_HAVE,
                evaluation_function="evaluate_location"
            ),
            MatchingCriteria(
                criteria_id="salary",
                name="Salary Match",
                description="Salary expectations alignment",
                weight=0.2,
                preference_type=PreferenceType.NICE_TO_HAVE,
                evaluation_function="evaluate_salary"
            )
        ]

    def get_performance_summary(self) -> Dict[str, Any]:
        return {
            "algorithm": self._algorithm.value,
            "total_criteria": len(self._matching_criteria),
            "total_matches_processed": len(self._match_results),
            "performance_metrics": self._performance_metrics,
            "last_updated": self._last_updated.isoformat()
        }

    @classmethod
    def from_events(cls, events: List[DomainEvent]) -> 'MatchingEngine':
        raise NotImplementedError("MatchingEngine event sourcing not implemented")