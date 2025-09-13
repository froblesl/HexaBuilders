# Recruitment Service Design - HexaBuilders

## 🎯 Contexto de Negocio

El **Recruitment Service** es el marketplace de talentos de HexaBuilders que conecta partners con candidatos calificados mediante algoritmos de matching inteligente. Este servicio crítico maneja:

- 👥 **Gestión de candidatos** con perfiles detallados
- 💼 **Ofertas laborales** con requisitos específicos  
- 🎯 **Matching inteligente** candidato-trabajo
- 📞 **Proceso de entrevistas** completo
- 📊 **Métricas de reclutamiento** y éxito

---

## 🏗️ Arquitectura del Servicio

### **Patrón de Almacenamiento**: CRUD Clásico
**Justificación**: El recruitment requiere búsquedas complejas, filtros avanzados, queries de agregación para matching y optimización de rendimiento para experiencia de usuario responsiva.

```
┌─────────────────────────────────────────────────────────────┐
│                 Recruitment Service                         │
├─────────────────────────────────────────────────────────────┤
│  🔍 API Layer (Flask + ElasticSearch)                      │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │ Candidates  │ │    Jobs     │ │ Interviews  │          │
│  │ Controller  │ │ Controller  │ │ Controller  │          │
│  └─────────────┘ └─────────────┘ └─────────────┘          │
├─────────────────────────────────────────────────────────────┤
│  🔄 Application Layer                                       │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │  Commands   │ │   Queries   │ │  Matching   │          │
│  │  & Events   │ │  & Search   │ │ Algorithms  │          │
│  └─────────────┘ └─────────────┘ └─────────────┘          │
├─────────────────────────────────────────────────────────────┤
│  🏛️ Domain Layer                                           │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │ Aggregates  │ │Value Objects│ │Domain Events│          │
│  │& Entities   │ │& Rules      │ │& Services   │          │
│  └─────────────┘ └─────────────┘ └─────────────┘          │
├─────────────────────────────────────────────────────────────┤
│  🔌 Infrastructure Layer                                   │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │PostgreSQL   │ │ElasticSearch│ │Pulsar Queue │          │
│  │(Primary DB) │ │(Search Eng) │ │Integration  │          │
│  └─────────────┘ └─────────────┘ └─────────────┘          │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 Estructura de Módulos

```
src/recruitment/
├── seedwork/                    # 🏗️ Infraestructura compartida
│   ├── dominio/                # Entidades base, eventos, excepciones
│   ├── aplicacion/             # Comandos, queries, handlers base
│   ├── infraestructura/        # Repository base, UoW, adaptadores
│   └── presentacion/           # API factory, middleware
├── modulos/
│   ├── candidates/             # 👥 Gestión de candidatos
│   │   ├── dominio/
│   │   │   ├── entidades.py           # Candidate (Aggregate Root)
│   │   │   ├── objetos_valor.py       # Skills, Experience, Education
│   │   │   ├── eventos.py             # Candidate domain events
│   │   │   ├── reglas.py              # Candidate business rules
│   │   │   └── repositorio.py         # Candidate repository interface
│   │   ├── aplicacion/
│   │   │   ├── comandos/
│   │   │   │   ├── registrar_candidato.py
│   │   │   │   ├── actualizar_perfil.py
│   │   │   │   ├── actualizar_skills.py
│   │   │   │   └── cambiar_disponibilidad.py
│   │   │   ├── queries/
│   │   │   │   ├── buscar_candidatos.py
│   │   │   │   ├── obtener_candidato.py
│   │   │   │   ├── obtener_candidatos_por_skill.py
│   │   │   │   └── obtener_estadisticas_candidato.py
│   │   │   ├── handlers.py             # Command & Query handlers
│   │   │   └── servicios_aplicacion.py # Application services
│   │   └── infraestructura/
│   │       ├── repositorios.py         # CRUD repositories
│   │       ├── search_engine.py        # ElasticSearch integration
│   │       ├── dto.py                  # Data transfer objects
│   │       ├── fabricas.py             # Domain factories
│   │       └── schema/                 # Search schemas
│   ├── jobs/                   # 💼 Ofertas laborales
│   │   ├── dominio/
│   │   │   ├── entidades.py           # Job (Aggregate Root)
│   │   │   ├── objetos_valor.py       # JobRequirements, Salary, Location
│   │   │   ├── eventos.py             # Job domain events
│   │   │   └── reglas.py              # Job business rules
│   │   ├── aplicacion/
│   │   │   ├── comandos/
│   │   │   │   ├── crear_trabajo.py
│   │   │   │   ├── actualizar_requisitos.py
│   │   │   │   ├── publicar_trabajo.py
│   │   │   │   └── cerrar_trabajo.py
│   │   │   └── queries/
│   │   │       ├── buscar_trabajos.py
│   │   │       ├── obtener_trabajo.py
│   │   │       └── obtener_trabajos_activos.py
│   │   └── infraestructura/
│   │       ├── repositorios.py
│   │       └── servicios_externos.py  # Job boards integration
│   ├── matching/               # 🎯 Algoritmos de matching
│   │   ├── dominio/
│   │   │   ├── entidades.py           # Match, MatchingCriteria
│   │   │   ├── objetos_valor.py       # MatchScore, MatchReason
│   │   │   ├── eventos.py             # Matching events
│   │   │   └── servicios.py           # Matching domain services
│   │   ├── aplicacion/
│   │   │   ├── comandos/
│   │   │   │   ├── ejecutar_matching.py
│   │   │   │   ├── refinar_matching.py
│   │   │   │   └── aprobar_match.py
│   │   │   ├── queries/
│   │   │   │   ├── obtener_matches.py
│   │   │   │   └── obtener_ranking_matches.py
│   │   │   ├── algoritmos/
│   │   │   │   ├── skill_matching.py
│   │   │   │   ├── experience_matching.py
│   │   │   │   ├── location_matching.py
│   │   │   │   └── composite_matching.py
│   │   │   └── servicios/
│   │   │       ├── matching_engine.py
│   │   │       └── ranking_service.py
│   │   └── infraestructura/
│   │       ├── advanced_models.py      # Advanced analytics models
│   │       └── analytics_service.py   # Matching analytics
│   └── interviews/             # 📞 Gestión de entrevistas
│       ├── dominio/
│       │   ├── entidades.py           # Interview, InterviewFeedback
│       │   ├── objetos_valor.py       # InterviewType, Rating, Schedule
│       │   ├── eventos.py             # Interview events
│       │   └── reglas.py              # Interview business rules
│       ├── aplicacion/
│       │   ├── comandos/
│       │   │   ├── programar_entrevista.py
│       │   │   ├── completar_entrevista.py
│       │   │   ├── enviar_feedback.py
│       │   │   └── tomar_decision.py
│       │   └── queries/
│       │       ├── obtener_entrevista.py
│       │       ├── obtener_calendario.py
│       │       └── obtener_feedback.py
│       └── infraestructura/
│           ├── calendar_service.py    # Google Calendar integration
│           ├── video_service.py       # Zoom/Teams integration
│           └── notification_service.py # Email/SMS notifications
└── api/                        # 🌐 REST API endpoints
    ├── candidates_api.py
    ├── jobs_api.py
    ├── matching_api.py
    └── interviews_api.py
```

---

## 🏛️ Diseño del Dominio

### **Aggregate Roots**

#### **1. Candidate (Aggregate Root)**
```python
class Candidate(AggregateRoot):
    """
    Candidato con perfil completo y capacidades de búsqueda optimizada.
    """
    def __init__(
        self,
        basic_info: BasicInfo,
        contact_info: ContactInfo,
        candidate_id: Optional[str] = None
    ):
        super().__init__(candidate_id)
        self._basic_info = basic_info
        self._contact_info = contact_info
        self._skills: List[Skill] = []
        self._experience: List[WorkExperience] = []
        self._education: List[Education] = []
        self._availability_status = AvailabilityStatus.AVAILABLE
        self._profile_completeness = 0.0
        self._verification_status = VerificationStatus.UNVERIFIED
        self._search_preferences = SearchPreferences()
        
        # Domain event
        self.agregar_evento(CandidateRegistered(
            aggregate_id=self.id,
            basic_info=basic_info.to_dict(),
            registration_source="DIRECT",
            initial_skills=[],
            availability_status=self._availability_status.value
        ))
        
        self._calculate_profile_completeness()
    
    def update_skills(self, new_skills: List[Skill], updated_by: str) -> None:
        """Actualizar skills del candidato"""
        old_skills = self._skills.copy()
        
        # Validar skills
        for skill in new_skills:
            if not skill.is_valid():
                raise BusinessRuleException(f"Invalid skill: {skill.name}")
        
        self._skills = new_skills
        self._calculate_profile_completeness()
        self._mark_updated()
        
        # Categorizar cambios
        added_skills = [s for s in new_skills if s not in old_skills]
        removed_skills = [s for s in old_skills if s not in new_skills]
        updated_levels = [s for s in new_skills if s in old_skills and s.level_changed(old_skills)]
        
        self.agregar_evento(CandidateSkillsUpdated(
            aggregate_id=self.id,
            added_skills=[s.to_dict() for s in added_skills],
            removed_skills=[s.to_dict() for s in removed_skills],
            updated_skill_levels={s.name: s.level.value for s in updated_levels},
            verification_status=self._verification_status.to_dict()
        ))
    
    def add_work_experience(self, experience: WorkExperience) -> None:
        """Añadir experiencia laboral"""
        # Validar que no se solape con experiencia existente
        if self._has_overlapping_experience(experience):
            raise BusinessRuleException("Work experience overlaps with existing experience")
        
        self._experience.append(experience)
        self._calculate_profile_completeness()
        self._mark_updated()
        
        self.agregar_evento(CandidateProfileUpdated(
            aggregate_id=self.id,
            updated_sections=["experience"],
            old_profile_data={"experience_count": len(self._experience) - 1},
            new_profile_data={"experience_count": len(self._experience)},
            update_source="MANUAL"
        ))
    
    def calculate_match_score(self, job: 'Job') -> MatchScore:
        """Calcular puntuación de matching con un trabajo"""
        from .matching.servicios import MatchingService
        
        matching_service = MatchingService()
        return matching_service.calculate_match(self, job)
    
    def change_availability(self, new_status: AvailabilityStatus, reason: str = None) -> None:
        """Cambiar estado de disponibilidad"""
        if self._availability_status == new_status:
            return
        
        old_status = self._availability_status
        self._availability_status = new_status
        self._mark_updated()
        
        self.agregar_evento(CandidateAvailabilityChanged(
            aggregate_id=self.id,
            old_status=old_status.value,
            new_status=new_status.value,
            change_reason=reason,
            changed_at=datetime.utcnow().isoformat()
        ))
    
    def _calculate_profile_completeness(self) -> None:
        """Calcular completitud del perfil"""
        completeness_factors = {
            'basic_info': 20,
            'contact_info': 10,
            'skills': 25,
            'experience': 25,
            'education': 15,
            'portfolio': 5
        }
        
        score = 0
        if self._basic_info.is_complete():
            score += completeness_factors['basic_info']
        if self._contact_info.is_complete():
            score += completeness_factors['contact_info']
        if len(self._skills) >= 3:
            score += completeness_factors['skills']
        if len(self._experience) >= 1:
            score += completeness_factors['experience']
        if len(self._education) >= 1:
            score += completeness_factors['education']
        
        self._profile_completeness = score / 100.0
```

#### **2. Job (Aggregate Root)**
```python
class Job(AggregateRoot):
    """
    Oferta laboral con requisitos específicos y proceso de matching.
    """
    def __init__(
        self,
        partner_id: str,
        job_title: str,
        job_description: str,
        requirements: JobRequirements,
        job_id: Optional[str] = None
    ):
        super().__init__(job_id)
        self._partner_id = partner_id
        self._job_title = job_title
        self._job_description = job_description
        self._requirements = requirements
        self._status = JobStatus.DRAFT
        self._posted_date: Optional[datetime] = None
        self._application_deadline: Optional[datetime] = None
        self._matches: List[str] = []  # candidate_ids
        self._applications: List[str] = []  # candidate_ids
        self._hired_candidate_id: Optional[str] = None
        
        # Domain event
        self.agregar_evento(JobCreated(
            aggregate_id=self.id,
            partner_id=partner_id,
            job_title=job_title,
            requirements=requirements.to_dict(),
            created_by="system"
        ))
    
    def publish(self, published_by: str, application_deadline: datetime = None) -> None:
        """Publicar oferta laboral"""
        if self._status != JobStatus.DRAFT:
            raise BusinessRuleException("Job can only be published from draft status")
        
        if not self._requirements.is_complete():
            raise BusinessRuleException("Job requirements must be complete before publishing")
        
        self._status = JobStatus.PUBLISHED
        self._posted_date = datetime.utcnow()
        self._application_deadline = application_deadline
        self._mark_updated()
        
        self.agregar_evento(JobPosted(
            aggregate_id=self.id,
            partner_id=self._partner_id,
            job_title=self._job_title,
            requirements=self._requirements.to_dict(),
            salary_range=self._requirements.salary_range.to_dict(),
            job_type=self._requirements.job_type.value
        ))
    
    def update_requirements(self, new_requirements: JobRequirements, updated_by: str) -> None:
        """Actualizar requisitos del trabajo"""
        if self._status in [JobStatus.FILLED, JobStatus.CANCELLED]:
            raise BusinessRuleException("Cannot update requirements for filled or cancelled job")
        
        old_requirements = self._requirements
        self._requirements = new_requirements
        self._mark_updated()
        
        # Si está publicado, podría afectar matches existentes
        if self._status == JobStatus.PUBLISHED:
            self.agregar_evento(JobRequirementsUpdated(
                aggregate_id=self.id,
                old_requirements=old_requirements.to_dict(),
                new_requirements=new_requirements.to_dict(),
                updated_by=updated_by,
                impact_on_matches=len(self._matches)
            ))
    
    def add_match(self, candidate_id: str, match_score: float) -> None:
        """Añadir candidato como match"""
        if candidate_id in self._matches:
            return  # Ya existe el match
        
        if self._status != JobStatus.PUBLISHED:
            raise BusinessRuleException("Job must be published to add matches")
        
        self._matches.append(candidate_id)
        self._mark_updated()
        
        self.agregar_evento(CandidateMatched(
            aggregate_id=self.id,
            candidate_id=candidate_id,
            match_score=match_score,
            match_timestamp=datetime.utcnow().isoformat(),
            total_matches=len(self._matches)
        ))
    
    def hire_candidate(self, candidate_id: str, hired_by: str) -> None:
        """Contratar candidato para el puesto"""
        if candidate_id not in self._matches and candidate_id not in self._applications:
            raise BusinessRuleException("Candidate must be matched or have applied")
        
        if self._status != JobStatus.PUBLISHED:
            raise BusinessRuleException("Job must be published to hire")
        
        self._hired_candidate_id = candidate_id
        self._status = JobStatus.FILLED
        self._mark_updated()
        
        self.agregar_evento(JobFilled(
            aggregate_id=self.id,
            partner_id=self._partner_id,
            hired_candidate_id=candidate_id,
            hired_by=hired_by,
            hired_date=datetime.utcnow().isoformat(),
            total_applicants=len(self._applications)
        ))
```

### **Value Objects**

#### **Skills**
```python
@dataclass(frozen=True)
class Skill(ValueObject):
    """Skill técnico con nivel de competencia"""
    
    name: str
    category: SkillCategory  # TECHNICAL, SOFT, LANGUAGE, CERTIFICATION
    level: SkillLevel        # BEGINNER, INTERMEDIATE, ADVANCED, EXPERT
    years_experience: int
    verified: bool = False
    verification_source: Optional[str] = None
    last_used: Optional[datetime] = None
    
    def __post_init__(self):
        self._validate()
    
    def _validate(self):
        if not self.name or len(self.name.strip()) < 2:
            raise DomainException("Skill name must be at least 2 characters")
        
        if self.years_experience < 0:
            raise DomainException("Years of experience cannot be negative")
        
        if self.years_experience > 50:
            raise DomainException("Years of experience seems unrealistic")
    
    def calculate_proficiency_score(self) -> float:
        """Calcular puntuación de competencia (0.0-1.0)"""
        base_score = {
            SkillLevel.BEGINNER: 0.25,
            SkillLevel.INTERMEDIATE: 0.5,
            SkillLevel.ADVANCED: 0.75,
            SkillLevel.EXPERT: 1.0
        }[self.level]
        
        # Ajustar por años de experiencia
        experience_multiplier = min(1.0, self.years_experience / 10.0)
        
        # Bonus por verificación
        verification_bonus = 0.1 if self.verified else 0.0
        
        # Penalty por falta de uso reciente
        recency_penalty = 0.0
        if self.last_used:
            months_since_use = (datetime.utcnow() - self.last_used).days / 30
            recency_penalty = min(0.2, months_since_use / 12 * 0.2)
        
        return min(1.0, base_score * experience_multiplier + verification_bonus - recency_penalty)
```

#### **JobRequirements**
```python
@dataclass(frozen=True)
class JobRequirements(ValueObject):
    """Requisitos completos para una oferta laboral"""
    
    # Skills requeridos
    required_skills: List[RequiredSkill]
    preferred_skills: List[RequiredSkill]
    
    # Experiencia
    minimum_years_experience: int
    preferred_years_experience: int
    industry_experience: List[str]
    
    # Educación
    minimum_education: EducationLevel
    preferred_education: EducationLevel
    required_certifications: List[str]
    
    # Ubicación y modalidad
    job_type: JobType              # FULL_TIME, PART_TIME, CONTRACT, FREELANCE
    work_mode: WorkMode            # REMOTE, HYBRID, ON_SITE
    locations: List[Location]
    travel_requirement: TravelRequirement
    
    # Compensación
    salary_range: SalaryRange
    benefits_package: List[str]
    equity_offered: bool
    
    # Otros
    security_clearance_required: bool
    language_requirements: List[LanguageRequirement]
    availability_requirements: AvailabilityRequirement
    
    def __post_init__(self):
        self._validate()
    
    def _validate(self):
        if not self.required_skills:
            raise DomainException("At least one required skill must be specified")
        
        if self.minimum_years_experience < 0:
            raise DomainException("Minimum years experience cannot be negative")
        
        if self.preferred_years_experience < self.minimum_years_experience:
            raise DomainException("Preferred experience cannot be less than minimum")
        
        if not self.salary_range.is_valid():
            raise DomainException("Invalid salary range")
    
    def calculate_match_score(self, candidate: 'Candidate') -> float:
        """Calcular puntuación de match con un candidato"""
        scores = {
            'skills': self._score_skills_match(candidate),
            'experience': self._score_experience_match(candidate),
            'education': self._score_education_match(candidate),
            'location': self._score_location_match(candidate),
            'availability': self._score_availability_match(candidate)
        }
        
        # Pesos para cada factor
        weights = {
            'skills': 0.4,
            'experience': 0.3,
            'education': 0.15,
            'location': 0.1,
            'availability': 0.05
        }
        
        total_score = sum(scores[factor] * weights[factor] for factor in scores)
        return min(1.0, total_score)
```

---

## 🎯 Algoritmos de Matching

### **Matching Engine**
```python
class MatchingEngine:
    """Motor de matching principal con múltiples algoritmos"""
    
    def __init__(self):
        self.skill_matcher = SkillMatcher()
        self.experience_matcher = ExperienceMatcher()
        self.location_matcher = LocationMatcher()
        self.ml_matcher = MLBasedMatcher()
    
    async def find_matches(
        self, 
        job: Job, 
        criteria: MatchingCriteria,
        max_candidates: int = 50
    ) -> List[CandidateMatch]:
        """Encontrar candidatos que matcheen con el trabajo"""
        
        # 1. Filtrado inicial por criterios básicos
        initial_candidates = await self._filter_by_basic_criteria(job, criteria)
        
        # 2. Scoring detallado
        scored_candidates = []
        for candidate in initial_candidates:
            match_score = await self._calculate_detailed_score(job, candidate)
            
            if match_score.total_score >= criteria.minimum_score:
                candidate_match = CandidateMatch(
                    candidate_id=candidate.id,
                    job_id=job.id,
                    match_score=match_score,
                    match_reasons=match_score.get_reasons(),
                    confidence_level=self._calculate_confidence(match_score)
                )
                scored_candidates.append(candidate_match)
        
        # 3. Ranking y selección de top matches
        ranked_matches = sorted(
            scored_candidates, 
            key=lambda m: m.match_score.total_score, 
            reverse=True
        )
        
        return ranked_matches[:max_candidates]
    
    async def _calculate_detailed_score(self, job: Job, candidate: Candidate) -> MatchScore:
        """Cálculo detallado de puntuación de match"""
        
        # Skill matching
        skill_score = self.skill_matcher.calculate_score(
            job.requirements.required_skills,
            candidate.skills
        )
        
        # Experience matching  
        experience_score = self.experience_matcher.calculate_score(
            job.requirements.minimum_years_experience,
            candidate.total_experience_years
        )
        
        # Location matching
        location_score = self.location_matcher.calculate_score(
            job.requirements.locations,
            candidate.location_preferences
        )
        
        # Advanced analytics matching (considera patrones históricos)
        analytics_score = await self.analytics_matcher.predict_match_score(job, candidate)
        
        return MatchScore(
            skill_match=skill_score,
            experience_match=experience_score,
            location_match=location_score,
            analytics_prediction=analytics_score,
            total_score=self._compute_weighted_total(
                skill_score, experience_score, location_score, analytics_score
            )
        )

class SkillMatcher:
    """Matching específico por skills"""
    
    def calculate_score(
        self, 
        required_skills: List[RequiredSkill], 
        candidate_skills: List[Skill]
    ) -> float:
        """Calcular puntuación de matching de skills"""
        
        if not required_skills:
            return 1.0
        
        total_score = 0.0
        total_weight = 0.0
        
        for required_skill in required_skills:
            # Encontrar skill matching en candidato
            matching_skill = self._find_matching_skill(
                required_skill, candidate_skills
            )
            
            if matching_skill:
                # Calcular score para este skill específico
                skill_score = self._calculate_skill_score(required_skill, matching_skill)
                weight = required_skill.importance_weight
                
                total_score += skill_score * weight
                total_weight += weight
            else:
                # Skill requerido no encontrado
                if required_skill.is_mandatory:
                    return 0.0  # Match automáticamente descalificado
                
                # Para skills opcionales, continuar sin penalty severa
                total_weight += required_skill.importance_weight * 0.1
        
        return total_score / total_weight if total_weight > 0 else 0.0
    
    def _calculate_skill_score(
        self, 
        required: RequiredSkill, 
        candidate: Skill
    ) -> float:
        """Calcular score para un skill específico"""
        
        # Score base por nivel
        level_scores = {
            SkillLevel.BEGINNER: 0.25,
            SkillLevel.INTERMEDIATE: 0.5, 
            SkillLevel.ADVANCED: 0.75,
            SkillLevel.EXPERT: 1.0
        }
        
        candidate_level_score = level_scores[candidate.level]
        required_level_score = level_scores[required.minimum_level]
        
        # Bonus si excede el nivel requerido
        if candidate_level_score >= required_level_score:
            base_score = 1.0
            expertise_bonus = (candidate_level_score - required_level_score) * 0.2
            score = min(1.0, base_score + expertise_bonus)
        else:
            # Penalty si no alcanza el nivel
            score = candidate_level_score / required_level_score
        
        # Ajustar por años de experiencia
        if candidate.years_experience >= required.minimum_years:
            experience_bonus = min(0.2, 
                (candidate.years_experience - required.minimum_years) / 5 * 0.1
            )
            score += experience_bonus
        
        # Bonus por verificación
        if candidate.verified:
            score += 0.1
        
        return min(1.0, score)
```

---

## 📊 Queries y Búsqueda

### **Advanced Search Capabilities**
```python
class CandidateSearchQuery:
    """Query avanzada para búsqueda de candidatos"""
    
    def __init__(self):
        # Filtros básicos
        self.skills: List[str] = []
        self.skill_levels: List[SkillLevel] = []
        self.min_experience_years: Optional[int] = None
        self.max_experience_years: Optional[int] = None
        
        # Filtros de ubicación
        self.locations: List[str] = []
        self.max_distance_km: Optional[int] = None
        self.remote_work_ok: Optional[bool] = None
        
        # Filtros de disponibilidad
        self.availability_status: List[AvailabilityStatus] = []
        self.start_date_range: Optional[DateRange] = None
        
        # Filtros de educación
        self.education_levels: List[EducationLevel] = []
        self.institutions: List[str] = []
        self.certifications: List[str] = []
        
        # Filtros de compensación
        self.min_salary_expectation: Optional[int] = None
        self.max_salary_expectation: Optional[int] = None
        
        # Filtros de perfil
        self.min_profile_completeness: float = 0.0
        self.verified_profiles_only: bool = False
        
        # Ordenamiento y paginación
        self.sort_by: SortBy = SortBy.RELEVANCE
        self.sort_order: SortOrder = SortOrder.DESC
        self.limit: int = 20
        self.offset: int = 0

class ElasticSearchCandidateRepository:
    """Repository con búsqueda avanzada usando ElasticSearch"""
    
    async def search_candidates(
        self, 
        query: CandidateSearchQuery
    ) -> SearchResult[Candidate]:
        """Búsqueda avanzada de candidatos"""
        
        es_query = {
            "query": {
                "bool": {
                    "must": [],
                    "filter": [],
                    "should": [],
                    "must_not": []
                }
            },
            "sort": self._build_sort_criteria(query),
            "from": query.offset,
            "size": query.limit,
            "highlight": {
                "fields": {
                    "skills.name": {},
                    "experience.description": {},
                    "education.field_of_study": {}
                }
            }
        }
        
        # Skills matching
        if query.skills:
            es_query["query"]["bool"]["must"].append({
                "nested": {
                    "path": "skills",
                    "query": {
                        "bool": {
                            "must": [
                                {"terms": {"skills.name": query.skills}}
                            ]
                        }
                    }
                }
            })
        
        # Experience range
        if query.min_experience_years or query.max_experience_years:
            range_filter = {"range": {"total_experience_years": {}}}
            if query.min_experience_years:
                range_filter["range"]["total_experience_years"]["gte"] = query.min_experience_years
            if query.max_experience_years:
                range_filter["range"]["total_experience_years"]["lte"] = query.max_experience_years
            es_query["query"]["bool"]["filter"].append(range_filter)
        
        # Location-based search
        if query.locations or query.max_distance_km:
            location_query = self._build_location_query(query)
            es_query["query"]["bool"]["must"].append(location_query)
        
        # Availability
        if query.availability_status:
            es_query["query"]["bool"]["filter"].append({
                "terms": {"availability_status": [s.value for s in query.availability_status]}
            })
        
        # Execute search
        response = await self.es_client.search(
            index="candidates",
            body=es_query
        )
        
        # Parse results
        candidates = []
        for hit in response["hits"]["hits"]:
            candidate = self._parse_candidate_from_hit(hit)
            candidates.append(candidate)
        
        return SearchResult(
            items=candidates,
            total_count=response["hits"]["total"]["value"],
            facets=self._extract_facets(response),
            query_time_ms=response["took"]
        )
```

---

## 🔄 Integration Events

### **Eventos Entrantes**
```python
@event_handler('partner-management/recruitment-requests')
async def on_recruitment_requested(event: RecruitmentRequested):
    """Procesar solicitud de reclutamiento desde Partner Management"""
    
    # Crear trabajo basado en la solicitud
    command = CreateJob(
        partner_id=event.partner_id,
        job_title=event.job_requirements.get('title'),
        job_description=event.job_requirements.get('description'),
        requirements=JobRequirements.from_dict(event.job_requirements),
        created_by="system"
    )
    
    job_id = await self.command_bus.dispatch(command)
    
    # Iniciar proceso de matching automático
    matching_command = StartMatching(
        job_id=job_id,
        criteria=MatchingCriteria.from_request(event),
        max_candidates=event.max_candidates or 10,
        urgency_level=event.urgency_level
    )
    
    await self.command_bus.dispatch(matching_command)
    
    # Notificar que el proceso ha iniciado
    response_event = RecruitmentProcessStarted(
        request_id=event.request_id,
        job_id=job_id,
        estimated_completion_time=self._estimate_completion_time(event)
    )
    
    await self.event_publisher.publish(
        'recruitment/process-started',
        response_event
    )
```

### **Eventos Salientes**
```python
class CandidateHired(IntegrationEvent):
    """Candidato contratado exitosamente"""
    
    def __init__(
        self,
        hiring_id: str,
        partner_id: str,
        candidate_id: str,
        job_id: str,
        **kwargs
    ):
        super().__init__(
            aggregate_id=hiring_id,
            partner_id=partner_id,
            candidate_id=candidate_id,
            job_id=job_id,
            employment_details=kwargs.get('employment_details', {}),
            hiring_process_metrics=kwargs.get('process_metrics', {}),
            **kwargs
        )
    
    def get_routing_keys(self) -> List[str]:
        """Routing a múltiples servicios"""
        return [
            f"recruitment.candidate.hired.{self.event_data['partner_id']}",
            "recruitment.candidate.hired.all"
        ]

# Publicación del evento
async def publish_candidate_hired_event(
    hiring_id: str,
    partner_id: str, 
    candidate_id: str,
    job_id: str,
    employment_details: dict
):
    """Publicar evento de candidato contratado"""
    
    event = CandidateHired(
        hiring_id=hiring_id,
        partner_id=partner_id,
        candidate_id=candidate_id,
        job_id=job_id,
        employment_details=employment_details,
        process_metrics=await get_hiring_process_metrics(hiring_id)
    )
    
    # Publicar a múltiples topics
    await self.event_publisher.publish_to_multiple(
        topics=[
            'recruitment/candidate-hired',
            'partner-management/partner-updates'
        ],
        event=event
    )
```

---

Este diseño del Recruitment Service proporciona un marketplace de talentos robusto y escalable, con capacidades avanzadas de búsqueda, matching inteligente y gestión completa del proceso de reclutamiento, optimizado para la experiencia tanto de partners como de candidatos.