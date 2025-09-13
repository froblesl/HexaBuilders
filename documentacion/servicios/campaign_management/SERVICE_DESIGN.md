# Campaign Management Service Design - HexaBuilders

## 🎯 Contexto de Negocio

El **Campaign Management Service** es el motor de gestión de campañas de marketing de HexaBuilders que permite a los partners crear, ejecutar y optimizar campañas con métricas en tiempo real. Este servicio crítico maneja:

- 🎯 **Gestión de campañas** con ciclo de vida completo
- 📊 **Segmentación avanzada** de audiencias objetivo
- 📈 **Métricas en tiempo real** y KPIs automatizados
- 💰 **Control presupuestario** inteligente
- 🤖 **Optimización automática** basada en IA

---

## 🏗️ Arquitectura del Servicio

### **Patrón de Almacenamiento**: Híbrido (CRUD + Event Sourcing)
**Justificación**: 
- **CRUD** para campañas, targeting y budgets (queries frecuentes, dashboards en tiempo real)
- **Event Sourcing** para métricas de performance (auditoría histórica, reconstrucción temporal)

```
┌─────────────────────────────────────────────────────────────┐
│               Campaign Management Service                   │
├─────────────────────────────────────────────────────────────┤
│  📊 API Layer (Flask + Real-time WebSockets)               │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │ Campaigns   │ │ Performance │ │   Budget    │          │
│  │ Controller  │ │ Dashboard   │ │ Controller  │          │
│  └─────────────┘ └─────────────┘ └─────────────┘          │
├─────────────────────────────────────────────────────────────┤
│  🔄 Application Layer                                       │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │  Commands   │ │Real-time    │ │  AI/ML      │          │
│  │  & Events   │ │Queries      │ │Optimization │          │
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
│  │PostgreSQL   │ │Event Store  │ │Time Series  │          │
│  │(CRUD Data)  │ │(Metrics)    │ │DB (InfluxDB)│          │
│  └─────────────┘ └─────────────┘ └─────────────┘          │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 Estructura de Módulos

```
src/campaign_management/
├── seedwork/                    # 🏗️ Infraestructura compartida
│   ├── dominio/                # Entidades base, eventos, excepciones
│   ├── aplicacion/             # Comandos, queries, handlers base
│   ├── infraestructura/        # Repository base, UoW, adaptadores
│   └── presentacion/           # API factory, middleware, WebSockets
├── modulos/
│   ├── campaigns/              # 🎯 Gestión de campañas
│   │   ├── dominio/
│   │   │   ├── entidades.py           # Campaign (Aggregate Root)
│   │   │   ├── objetos_valor.py       # CampaignType, Status, Goals
│   │   │   ├── eventos.py             # Campaign domain events
│   │   │   ├── reglas.py              # Campaign business rules
│   │   │   └── repositorio.py         # Campaign repository interface
│   │   ├── aplicacion/
│   │   │   ├── comandos/
│   │   │   │   ├── crear_campaign.py
│   │   │   │   ├── lanzar_campaign.py
│   │   │   │   ├── pausar_campaign.py
│   │   │   │   ├── reanudar_campaign.py
│   │   │   │   └── completar_campaign.py
│   │   │   ├── queries/
│   │   │   │   ├── obtener_campaign.py
│   │   │   │   ├── obtener_campaigns_activos.py
│   │   │   │   ├── obtener_metricas_campaign.py
│   │   │   │   └── obtener_dashboard_partner.py
│   │   │   ├── handlers.py             # Command & Query handlers
│   │   │   └── servicios_aplicacion.py # Application services
│   │   └── infraestructura/
│   │       ├── repositorios_crud.py    # CRUD repositories
│   │       ├── dto.py                  # Data transfer objects
│   │       ├── fabricas.py             # Domain factories
│   │       └── servicios_externos.py   # Ad platform integrations
│   ├── targeting/              # 🎯 Segmentación de audiencias
│   │   ├── dominio/
│   │   │   ├── entidades.py           # Audience, Segment
│   │   │   ├── objetos_valor.py       # Demographics, Interests, Behavior
│   │   │   ├── eventos.py             # Targeting domain events
│   │   │   └── servicios.py           # Targeting domain services
│   │   ├── aplicacion/
│   │   │   ├── comandos/
│   │   │   │   ├── crear_audiencia.py
│   │   │   │   ├── refinar_segmento.py
│   │   │   │   ├── optimizar_targeting.py
│   │   │   │   └── validar_alcance.py
│   │   │   ├── queries/
│   │   │   │   ├── estimar_alcance.py
│   │   │   │   ├── analizar_overlap.py
│   │   │   │   └── obtener_insights_audiencia.py
│   │   │   ├── algoritmos/
│   │   │   │   ├── lookalike_modeling.py
│   │   │   │   ├── behavioral_clustering.py
│   │   │   │   └── demographic_analysis.py
│   │   │   └── servicios/
│   │   │       ├── audience_builder.py
│   │   │       └── targeting_optimizer.py
│   │   └── infraestructura/
│   │       ├── data_providers.py      # External data sources
│   │       └── ml_models.py           # Machine learning models
│   ├── performance/            # 📈 Métricas en tiempo real
│   │   ├── dominio/
│   │   │   ├── entidades.py           # Metric, KPI, PerformanceSnapshot
│   │   │   ├── objetos_valor.py       # MetricValue, Threshold, Trend
│   │   │   ├── eventos.py             # Performance events (Event Sourced)
│   │   │   └── servicios.py           # Performance calculation services
│   │   ├── aplicacion/
│   │   │   ├── comandos/
│   │   │   │   ├── registrar_metrica.py
│   │   │   │   ├── calcular_kpis.py
│   │   │   │   ├── detectar_anomalias.py
│   │   │   │   └── generar_reporte.py
│   │   │   ├── queries/
│   │   │   │   ├── obtener_metricas_tiempo_real.py
│   │   │   │   ├── obtener_tendencias.py
│   │   │   │   ├── comparar_periodos.py
│   │   │   │   └── obtener_insights_performance.py
│   │   │   ├── real_time/
│   │   │   │   ├── metrics_processor.py
│   │   │   │   ├── streaming_aggregator.py
│   │   │   │   └── alert_engine.py
│   │   │   └── servicios/
│   │   │       ├── metrics_calculator.py
│   │   │       └── anomaly_detector.py
│   │   └── infraestructura/
│   │       ├── event_store_metrics.py  # Event sourcing for metrics
│   │       ├── time_series_db.py       # InfluxDB integration
│   │       ├── streaming_platform.py   # Kafka/Pulsar streaming
│   │       └── external_apis.py        # Facebook/Google Ads APIs
│   └── budgets/                # 💰 Control presupuestario
│       ├── dominio/
│       │   ├── entidades.py           # Budget, BudgetAllocation, Spend
│       │   ├── objetos_valor.py       # BudgetLimit, SpendRate, Forecast
│       │   ├── eventos.py             # Budget domain events
│       │   └── reglas.py              # Budget business rules
│       ├── aplicacion/
│       │   ├── comandos/
│       │   │   ├── asignar_presupuesto.py
│       │   │   ├── reasignar_fondos.py
│       │   │   ├── autorizar_gasto_extra.py
│       │   │   └── pausar_por_presupuesto.py
│       │   ├── queries/
│       │   │   ├── obtener_estado_presupuesto.py
│       │   │   ├── proyectar_gasto.py
│       │   │   └── analizar_eficiencia_gasto.py
│       │   └── servicios/
│       │       ├── budget_optimizer.py
│       │       ├── spend_forecaster.py
│       │       └── alert_manager.py
│       └── infraestructura/
│           ├── payment_gateways.py    # Stripe, PayPal integration
│           └── financial_reporting.py # Financial reporting systems
└── api/                        # 🌐 REST API + WebSockets
    ├── campaigns_api.py
    ├── targeting_api.py
    ├── performance_api.py
    ├── budgets_api.py
    └── websockets/
        ├── real_time_metrics.py
        └── campaign_notifications.py
```

---

## 🏛️ Diseño del Dominio

### **Aggregate Roots**

#### **1. Campaign (Aggregate Root)**
```python
class Campaign(AggregateRoot):
    """
    Campaña de marketing con ciclo de vida completo y métricas integradas.
    """
    def __init__(
        self,
        partner_id: str,
        campaign_name: str,
        campaign_type: CampaignType,
        campaign_goals: CampaignGoals,
        initial_budget: Money,
        campaign_id: Optional[str] = None
    ):
        super().__init__(campaign_id)
        self._partner_id = partner_id
        self._campaign_name = campaign_name
        self._campaign_type = campaign_type
        self._goals = campaign_goals
        self._status = CampaignStatus.DRAFT
        self._total_budget = initial_budget
        self._spent_budget = Money(0, initial_budget.currency)
        self._targeting: Optional[TargetingConfiguration] = None
        self._creative_assets: List[CreativeAsset] = []
        self._schedule: Optional[CampaignSchedule] = None
        self._performance_targets: Dict[str, float] = {}
        self._actual_performance: Dict[str, float] = {}
        
        # Timestamps
        self._created_at = datetime.utcnow()
        self._launched_at: Optional[datetime] = None
        self._completed_at: Optional[datetime] = None
        
        # Domain event
        self.agregar_evento(CampaignCreated(
            aggregate_id=self.id,
            partner_id=partner_id,
            campaign_name=campaign_name,
            campaign_type=campaign_type.value,
            campaign_goals=campaign_goals.to_dict(),
            initial_budget=initial_budget.amount
        ))
    
    def configure_targeting(self, targeting_config: TargetingConfiguration) -> None:
        """Configurar targeting de la campaña"""
        if self._status not in [CampaignStatus.DRAFT, CampaignStatus.SCHEDULED]:
            raise BusinessRuleException("Cannot modify targeting of launched campaign")
        
        # Validar que el targeting sea compatible con el tipo de campaña
        if not self._validate_targeting_compatibility(targeting_config):
            raise BusinessRuleException("Targeting configuration incompatible with campaign type")
        
        old_targeting = self._targeting
        self._targeting = targeting_config
        self._mark_updated()
        
        # Estimar alcance con nueva configuración
        estimated_reach = targeting_config.estimate_reach()
        
        self.agregar_evento(CampaignTargetingConfigured(
            aggregate_id=self.id,
            targeting_config=targeting_config.to_dict(),
            estimated_reach=estimated_reach,
            previous_targeting=old_targeting.to_dict() if old_targeting else None
        ))
    
    def launch(self, launched_by: str, launch_timestamp: datetime = None) -> None:
        """Lanzar campaña activa"""
        if self._status != CampaignStatus.SCHEDULED:
            if self._status == CampaignStatus.DRAFT:
                raise BusinessRuleException("Campaign must be scheduled before launch")
            else:
                raise BusinessRuleException(f"Cannot launch campaign in status {self._status}")
        
        # Validar precondiciones de lanzamiento
        self._validate_launch_readiness()
        
        self._status = CampaignStatus.ACTIVE
        self._launched_at = launch_timestamp or datetime.utcnow()
        self._mark_updated()
        
        self.agregar_evento(CampaignLaunched(
            aggregate_id=self.id,
            launch_timestamp=self._launched_at.isoformat(),
            initial_targeting=self._targeting.to_dict(),
            launch_checklist=self._get_launch_checklist_status(),
            launched_by=launched_by
        ))
    
    def update_performance_metrics(self, metrics: Dict[str, float], timestamp: datetime) -> None:
        """Actualizar métricas de rendimiento en tiempo real"""
        if self._status != CampaignStatus.ACTIVE:
            return  # Solo actualizar métricas para campañas activas
        
        previous_metrics = self._actual_performance.copy()
        
        # Actualizar métricas actuales
        for metric_name, value in metrics.items():
            self._actual_performance[metric_name] = value
        
        # Calcular cambios significativos
        significant_changes = self._detect_significant_changes(previous_metrics, metrics)
        
        # Verificar umbrales de KPI
        threshold_alerts = self._check_kpi_thresholds(metrics)
        
        self._mark_updated()
        
        # Event sourcing para métricas (auditabilidad completa)
        self.agregar_evento(MetricUpdated(
            aggregate_id=self.id,
            metrics_snapshot=metrics,
            previous_metrics=previous_metrics,
            significant_changes=significant_changes,
            threshold_alerts=threshold_alerts,
            update_timestamp=timestamp.isoformat()
        ))
        
        # Eventos específicos para umbrales críticos
        for alert in threshold_alerts:
            if alert['severity'] in ['HIGH', 'CRITICAL']:
                self.agregar_evento(KPIThresholdReached(
                    aggregate_id=self.id,
                    kpi_type=alert['kpi_type'],
                    threshold_type=alert['threshold_type'],
                    threshold_value=alert['threshold_value'],
                    actual_value=alert['actual_value'],
                    alert_level=alert['severity']
                ))
    
    def optimize_automatically(self, optimization_suggestions: List[OptimizationSuggestion]) -> None:
        """Aplicar optimizaciones automáticas basadas en IA"""
        if self._status != CampaignStatus.ACTIVE:
            raise BusinessRuleException("Can only optimize active campaigns")
        
        applied_optimizations = []
        
        for suggestion in optimization_suggestions:
            if suggestion.confidence_score >= 0.8 and suggestion.auto_apply_eligible:
                # Aplicar optimización automáticamente
                if suggestion.optimization_type == OptimizationType.BUDGET_REALLOCATION:
                    self._apply_budget_optimization(suggestion)
                elif suggestion.optimization_type == OptimizationType.TARGETING_REFINEMENT:
                    self._apply_targeting_optimization(suggestion)
                elif suggestion.optimization_type == OptimizationType.BID_ADJUSTMENT:
                    self._apply_bid_optimization(suggestion)
                
                applied_optimizations.append(suggestion)
        
        if applied_optimizations:
            self.agregar_evento(CampaignOptimized(
                aggregate_id=self.id,
                optimizations_applied=applied_optimizations,
                optimization_timestamp=datetime.utcnow().isoformat(),
                expected_impact=self._calculate_expected_impact(applied_optimizations)
            ))
    
    def pause(self, reason: str, paused_by: str) -> None:
        """Pausar campaña temporalmente"""
        if self._status != CampaignStatus.ACTIVE:
            raise BusinessRuleException("Can only pause active campaigns")
        
        self._status = CampaignStatus.PAUSED
        self._mark_updated()
        
        # Capturar métricas al momento de la pausa
        pause_metrics = self._get_current_metrics_snapshot()
        
        self.agregar_evento(CampaignPaused(
            aggregate_id=self.id,
            pause_reason=reason,
            paused_by=paused_by,
            pause_timestamp=datetime.utcnow().isoformat(),
            metrics_at_pause=pause_metrics
        ))
    
    def complete(self, completion_reason: str = "SCHEDULED_END") -> None:
        """Completar campaña"""
        if self._status not in [CampaignStatus.ACTIVE, CampaignStatus.PAUSED]:
            raise BusinessRuleException("Campaign must be active or paused to complete")
        
        self._status = CampaignStatus.COMPLETED
        self._completed_at = datetime.utcnow()
        self._mark_updated()
        
        # Generar métricas finales
        final_metrics = self._generate_final_metrics()
        success_indicators = self._calculate_success_indicators()
        
        self.agregar_evento(CampaignCompleted(
            aggregate_id=self.id,
            completion_reason=completion_reason,
            completion_timestamp=self._completed_at.isoformat(),
            final_metrics=final_metrics,
            success_indicators=success_indicators,
            total_spend=self._spent_budget.amount,
            roi=self._calculate_roi()
        ))
```

#### **2. Budget (Aggregate Root)**
```python
class Budget(AggregateRoot):
    """
    Presupuesto de campaña con control inteligente y alertas automáticas.
    """
    def __init__(
        self,
        campaign_id: str,
        total_budget: Money,
        budget_period: BudgetPeriod,
        budget_id: Optional[str] = None
    ):
        super().__init__(budget_id)
        self._campaign_id = campaign_id
        self._total_budget = total_budget
        self._period = budget_period
        self._allocations: List[BudgetAllocation] = []
        self._spend_history: List[SpendRecord] = []
        self._current_spend = Money(0, total_budget.currency)
        self._daily_limit = self._calculate_daily_limit()
        self._alert_thresholds = self._set_default_thresholds()
        self._auto_pause_enabled = True
        
        # Domain event
        self.agregar_evento(BudgetCreated(
            aggregate_id=self.id,
            campaign_id=campaign_id,
            total_budget=total_budget.amount,
            budget_period=budget_period.to_dict(),
            daily_limit=self._daily_limit.amount
        ))
    
    def allocate_funds(self, allocations: List[BudgetAllocation]) -> None:
        """Asignar fondos a diferentes canales/objetivos"""
        # Validar que las asignaciones no excedan el presupuesto total
        total_allocated = sum(allocation.amount.amount for allocation in allocations)
        if total_allocated > self._total_budget.amount:
            raise BusinessRuleException("Total allocation exceeds budget")
        
        self._allocations = allocations
        self._mark_updated()
        
        self.agregar_evento(BudgetAllocated(
            aggregate_id=self.id,
            campaign_id=self._campaign_id,
            total_budget=self._total_budget.amount,
            allocation_breakdown={
                allocation.category: allocation.amount.amount 
                for allocation in allocations
            },
            allocated_by="system"
        ))
    
    def record_spend(self, amount: Money, spend_category: str, timestamp: datetime = None) -> None:
        """Registrar gasto realizado"""
        timestamp = timestamp or datetime.utcnow()
        
        # Validar que el gasto no exceda el presupuesto
        new_total_spend = self._current_spend.amount + amount.amount
        if new_total_spend > self._total_budget.amount:
            if self._auto_pause_enabled:
                self._trigger_auto_pause("BUDGET_EXCEEDED")
            raise BusinessRuleException("Spend would exceed total budget")
        
        # Registrar gasto
        spend_record = SpendRecord(
            amount=amount,
            category=spend_category,
            timestamp=timestamp,
            running_total=Money(new_total_spend, amount.currency)
        )
        
        self._spend_history.append(spend_record)
        self._current_spend = Money(new_total_spend, amount.currency)
        self._mark_updated()
        
        # Verificar umbrales de alerta
        self._check_spend_thresholds(new_total_spend)
        
        # Event sourcing para gastos (auditoría completa)
        self.agregar_evento(SpendRecorded(
            aggregate_id=self.id,
            campaign_id=self._campaign_id,
            spend_amount=amount.amount,
            spend_category=spend_category,
            running_total=new_total_spend,
            spend_timestamp=timestamp.isoformat(),
            budget_utilization=new_total_spend / self._total_budget.amount
        ))
    
    def _check_spend_thresholds(self, current_spend: float) -> None:
        """Verificar umbrales de gasto y generar alertas"""
        utilization = current_spend / self._total_budget.amount
        
        for threshold in self._alert_thresholds:
            if (utilization >= threshold.percentage and 
                not threshold.already_triggered):
                
                threshold.already_triggered = True
                
                self.agregar_evento(BudgetThresholdReached(
                    aggregate_id=self.id,
                    campaign_id=self._campaign_id,
                    threshold_percentage=threshold.percentage,
                    current_spend=current_spend,
                    budget_limit=self._total_budget.amount,
                    days_remaining=self._calculate_days_remaining(),
                    threshold_type=threshold.severity.value
                ))
                
                # Auto-pausar si es umbral crítico
                if threshold.severity == ThresholdSeverity.CRITICAL and self._auto_pause_enabled:
                    self._trigger_auto_pause("CRITICAL_THRESHOLD_REACHED")
    
    def forecast_spend(self, forecast_period_days: int) -> SpendForecast:
        """Proyectar gasto futuro basado en tendencias"""
        if len(self._spend_history) < 3:
            return SpendForecast.insufficient_data()
        
        # Calcular tendencia de gasto diario
        recent_spends = self._spend_history[-7:]  # Últimos 7 registros
        daily_avg = self._calculate_daily_average_spend(recent_spends)
        
        # Proyección simple lineal (en producción, usar ML)
        projected_total_spend = self._current_spend.amount + (daily_avg * forecast_period_days)
        
        # Calcular probabilidad de exceder presupuesto
        overspend_probability = max(0.0, 
            (projected_total_spend - self._total_budget.amount) / self._total_budget.amount
        )
        
        return SpendForecast(
            projected_total_spend=projected_total_spend,
            daily_average_spend=daily_avg,
            overspend_probability=overspend_probability,
            recommended_daily_limit=self._calculate_optimal_daily_limit(forecast_period_days),
            forecast_confidence=self._calculate_forecast_confidence(recent_spends)
        )
```

### **Value Objects**

#### **CampaignGoals**
```python
@dataclass(frozen=True)
class CampaignGoals(ValueObject):
    """Objetivos específicos de la campaña"""
    
    # Objetivos primarios
    primary_objective: CampaignObjective  # AWARENESS, TRAFFIC, CONVERSIONS, etc.
    target_metrics: Dict[str, float]      # {metric_name: target_value}
    
    # KPIs específicos
    target_impressions: Optional[int] = None
    target_clicks: Optional[int] = None
    target_conversions: Optional[int] = None
    target_ctr: Optional[float] = None      # Click-through rate
    target_cpc: Optional[float] = None      # Cost per click
    target_cpa: Optional[float] = None      # Cost per acquisition
    target_roas: Optional[float] = None     # Return on ad spend
    
    # Métricas de negocio
    target_revenue: Optional[float] = None
    target_leads: Optional[int] = None
    target_brand_lift: Optional[float] = None
    
    def __post_init__(self):
        self._validate()
    
    def _validate(self):
        if not self.target_metrics:
            raise DomainException("At least one target metric must be specified")
        
        # Validar consistencia entre objetivos y métricas
        if self.primary_objective == CampaignObjective.CONVERSIONS:
            if not (self.target_conversions or self.target_cpa):
                raise DomainException("Conversion campaigns must have conversion targets")
        
        if self.primary_objective == CampaignObjective.TRAFFIC:
            if not (self.target_clicks or self.target_ctr):
                raise DomainException("Traffic campaigns must have click targets")
    
    def calculate_success_score(self, actual_metrics: Dict[str, float]) -> float:
        """Calcular puntuación de éxito basada en objetivos vs resultados"""
        success_scores = []
        
        for metric_name, target_value in self.target_metrics.items():
            actual_value = actual_metrics.get(metric_name, 0)
            
            if target_value > 0:
                # Para métricas donde "más es mejor"
                if metric_name in ['impressions', 'clicks', 'conversions', 'revenue']:
                    score = min(1.0, actual_value / target_value)
                # Para métricas donde "menos es mejor" (costos)
                elif metric_name in ['cpc', 'cpa']:
                    score = min(1.0, target_value / actual_value) if actual_value > 0 else 0
                # Para métricas de ratio
                else:
                    score = min(1.0, actual_value / target_value)
                
                success_scores.append(score)
        
        return sum(success_scores) / len(success_scores) if success_scores else 0.0
```

#### **TargetingConfiguration**
```python
@dataclass(frozen=True)
class TargetingConfiguration(ValueObject):
    """Configuración completa de targeting para una campaña"""
    
    # Demographics
    age_range: AgeRange
    genders: List[Gender]
    locations: List[GeographicLocation]
    languages: List[str]
    
    # Interests and Behaviors
    interests: List[Interest]
    behaviors: List[Behavior]
    custom_audiences: List[str]  # IDs de audiencias personalizadas
    lookalike_audiences: List[LookalikeAudience]
    
    # Professional
    job_titles: List[str]
    industries: List[str]
    company_sizes: List[CompanySize]
    income_ranges: List[IncomeRange]
    
    # Digital Behavior
    device_types: List[DeviceType]
    platforms: List[Platform]
    connection_types: List[ConnectionType]
    
    # Advanced
    exclusions: List[ExclusionCriteria]
    bid_strategy: BidStrategy
    frequency_cap: Optional[FrequencyCap] = None
    
    def __post_init__(self):
        self._validate()
    
    def _validate(self):
        if not self.age_range.is_valid():
            raise DomainException("Invalid age range")
        
        if not self.locations:
            raise DomainException("At least one location must be specified")
        
        if len(self.interests) + len(self.behaviors) == 0:
            raise DomainException("At least one interest or behavior must be specified")
    
    def estimate_reach(self) -> ReachEstimate:
        """Estimar alcance potencial de la configuración de targeting"""
        # En producción, esto se conectaría a APIs de las plataformas
        base_reach = self._calculate_base_reach()
        
        # Aplicar factores de reducción por cada criterio
        reach_multipliers = {
            'age_gender': self._calculate_demographic_multiplier(),
            'location': self._calculate_location_multiplier(),
            'interests': self._calculate_interest_multiplier(),
            'professional': self._calculate_professional_multiplier(),
            'device': self._calculate_device_multiplier()
        }
        
        final_reach = base_reach
        for multiplier in reach_multipliers.values():
            final_reach *= multiplier
        
        return ReachEstimate(
            minimum_reach=int(final_reach * 0.8),
            maximum_reach=int(final_reach * 1.2),
            estimated_reach=int(final_reach),
            confidence_level=self._calculate_confidence_level(),
            reach_breakdown=reach_multipliers
        )
    
    def get_overlap_with(self, other: 'TargetingConfiguration') -> float:
        """Calcular solapamiento con otra configuración de targeting"""
        overlap_factors = {
            'demographics': self._calculate_demographic_overlap(other),
            'geography': self._calculate_geographic_overlap(other),
            'interests': self._calculate_interest_overlap(other),
            'professional': self._calculate_professional_overlap(other)
        }
        
        # Promedio ponderado del solapamiento
        weights = {'demographics': 0.3, 'geography': 0.2, 'interests': 0.3, 'professional': 0.2}
        
        total_overlap = sum(
            overlap_factors[factor] * weights[factor] 
            for factor in overlap_factors
        )
        
        return min(1.0, total_overlap)
```

---

## 📊 Real-time Performance Monitoring

### **Event Sourcing para Métricas**
```python
class MetricsEventStore:
    """Event store especializado para métricas de rendimiento"""
    
    async def record_metric_event(self, campaign_id: str, metric_event: MetricEvent) -> None:
        """Registrar evento de métrica con timestamp de alta precisión"""
        
        event_record = {
            'campaign_id': campaign_id,
            'event_type': metric_event.__class__.__name__,
            'metric_name': metric_event.metric_name,
            'metric_value': metric_event.value,
            'timestamp': metric_event.timestamp.isoformat(),
            'microsecond_precision': metric_event.timestamp.microsecond,
            'data_source': metric_event.source,
            'event_metadata': metric_event.metadata,
            'correlation_id': metric_event.correlation_id
        }
        
        # Insertar en event store
        await self.db.execute(
            """
            INSERT INTO campaign_metric_events 
            (campaign_id, event_type, metric_name, metric_value, timestamp, 
             microsecond_precision, data_source, event_metadata, correlation_id)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            """,
            *event_record.values()
        )
        
        # También insertar en time series DB para queries rápidas
        await self._insert_to_time_series(campaign_id, metric_event)
    
    async def reconstruct_metrics_at_time(
        self, 
        campaign_id: str, 
        target_timestamp: datetime
    ) -> CampaignMetrics:
        """Reconstruir métricas exactas en un momento específico"""
        
        events = await self.db.fetch_all(
            """
            SELECT * FROM campaign_metric_events 
            WHERE campaign_id = $1 AND timestamp <= $2
            ORDER BY timestamp, microsecond_precision
            """,
            campaign_id, target_timestamp
        )
        
        # Reconstruir estado aplicando eventos en orden cronológico
        metrics = CampaignMetrics()
        
        for event_record in events:
            event = self._deserialize_metric_event(event_record)
            metrics.apply_event(event)
        
        return metrics

class RealTimeMetricsProcessor:
    """Procesador en tiempo real de métricas de campaña"""
    
    def __init__(self):
        self.websocket_manager = WebSocketManager()
        self.alert_engine = AlertEngine()
        self.ml_anomaly_detector = AnomalyDetector()
    
    async def process_incoming_metric(
        self, 
        campaign_id: str, 
        metric_data: Dict[str, Any]
    ) -> None:
        """Procesar métrica entrante en tiempo real"""
        
        # 1. Validar y normalizar datos
        metric_event = self._create_metric_event(metric_data)
        
        # 2. Persistir en event store
        await self.metrics_store.record_metric_event(campaign_id, metric_event)
        
        # 3. Calcular métricas derivadas
        derived_metrics = await self._calculate_derived_metrics(campaign_id, metric_event)
        
        # 4. Detectar anomalías
        anomalies = await self.ml_anomaly_detector.detect_anomalies(
            campaign_id, metric_event, derived_metrics
        )
        
        # 5. Verificar umbrales de alerta
        alerts = await self.alert_engine.check_thresholds(
            campaign_id, metric_event, derived_metrics
        )
        
        # 6. Actualizar dashboards en tiempo real via WebSocket
        await self._broadcast_metric_update(campaign_id, {
            'metric_event': metric_event.to_dict(),
            'derived_metrics': derived_metrics,
            'anomalies': anomalies,
            'alerts': alerts
        })
        
        # 7. Triggear optimizaciones automáticas si es necesario
        if alerts or anomalies:
            await self._trigger_auto_optimization(campaign_id, alerts, anomalies)
    
    async def _broadcast_metric_update(
        self, 
        campaign_id: str, 
        update_data: Dict[str, Any]
    ) -> None:
        """Broadcast actualización a clientes WebSocket conectados"""
        
        # Formatear datos para el frontend
        dashboard_update = {
            'campaign_id': campaign_id,
            'timestamp': datetime.utcnow().isoformat(),
            'type': 'metrics_update',
            'data': update_data
        }
        
        # Enviar a todos los clientes suscritos a esta campaña
        await self.websocket_manager.broadcast_to_campaign(
            campaign_id, dashboard_update
        )
        
        # Enviar también al dashboard del partner
        partner_id = await self._get_partner_id_for_campaign(campaign_id)
        await self.websocket_manager.broadcast_to_partner(
            partner_id, dashboard_update
        )
```

### **Machine Learning para Optimización**
```python
class CampaignOptimizationEngine:
    """Motor de optimización automática basado en ML"""
    
    def __init__(self):
        self.performance_predictor = PerformancePredictor()
        self.bid_optimizer = BidOptimizer()
        self.audience_optimizer = AudienceOptimizer()
        self.budget_allocator = BudgetAllocator()
    
    async def generate_optimization_suggestions(
        self, 
        campaign_id: str
    ) -> List[OptimizationSuggestion]:
        """Generar sugerencias de optimización basadas en ML"""
        
        # 1. Obtener datos históricos de la campaña
        campaign_data = await self._get_campaign_historical_data(campaign_id)
        
        # 2. Analizar rendimiento actual vs objetivos
        performance_analysis = await self._analyze_current_performance(campaign_id)
        
        # 3. Generar sugerencias por categoría
        suggestions = []
        
        # Optimización de targeting
        if performance_analysis.audience_engagement_low:
            audience_suggestions = await self.audience_optimizer.suggest_optimizations(
                campaign_data, performance_analysis
            )
            suggestions.extend(audience_suggestions)
        
        # Optimización de presupuesto
        if performance_analysis.budget_efficiency_low:
            budget_suggestions = await self.budget_allocator.suggest_reallocations(
                campaign_data, performance_analysis
            )
            suggestions.extend(budget_suggestions)
        
        # Optimización de bidding
        if performance_analysis.bid_performance_suboptimal:
            bid_suggestions = await self.bid_optimizer.suggest_bid_adjustments(
                campaign_data, performance_analysis
            )
            suggestions.extend(bid_suggestions)
        
        # 4. Rankear sugerencias por impacto esperado
        ranked_suggestions = self._rank_suggestions_by_impact(suggestions)
        
        return ranked_suggestions
    
    async def apply_automatic_optimization(
        self, 
        campaign_id: str, 
        suggestion: OptimizationSuggestion
    ) -> OptimizationResult:
        """Aplicar optimización automática"""
        
        try:
            # 1. Validar que la optimización es segura
            safety_check = await self._validate_optimization_safety(campaign_id, suggestion)
            if not safety_check.is_safe:
                return OptimizationResult.unsafe(safety_check.reason)
            
            # 2. Crear snapshot de estado actual para rollback
            current_state = await self._create_campaign_snapshot(campaign_id)
            
            # 3. Aplicar optimización
            if suggestion.optimization_type == OptimizationType.AUDIENCE_EXPANSION:
                result = await self._apply_audience_optimization(campaign_id, suggestion)
            elif suggestion.optimization_type == OptimizationType.BID_ADJUSTMENT:
                result = await self._apply_bid_optimization(campaign_id, suggestion)
            elif suggestion.optimization_type == OptimizationType.BUDGET_REALLOCATION:
                result = await self._apply_budget_optimization(campaign_id, suggestion)
            
            # 4. Monitorear resultados iniciales
            await self._schedule_optimization_monitoring(campaign_id, suggestion, current_state)
            
            return OptimizationResult.success(result)
            
        except Exception as e:
            logger.error(f"Optimization failed for campaign {campaign_id}: {e}")
            return OptimizationResult.failed(str(e))

class PerformancePredictor:
    """Predictor de rendimiento futuro usando ML"""
    
    async def predict_campaign_performance(
        self, 
        campaign_id: str, 
        forecast_days: int = 7
    ) -> PerformanceForecast:
        """Predecir rendimiento futuro de la campaña"""
        
        # 1. Obtener features de la campaña
        features = await self._extract_campaign_features(campaign_id)
        
        # 2. Obtener datos históricos similares
        similar_campaigns = await self._find_similar_campaigns(features)
        
        # 3. Aplicar modelo predictivo
        predictions = await self._apply_ml_model(features, similar_campaigns, forecast_days)
        
        # 4. Calcular intervalos de confianza
        confidence_intervals = self._calculate_confidence_intervals(predictions)
        
        return PerformanceForecast(
            predicted_metrics=predictions,
            confidence_intervals=confidence_intervals,
            forecast_period_days=forecast_days,
            model_accuracy=await self._get_model_accuracy(),
            factors_considered=features.keys()
        )
```

---

## 🔄 Integration Events

### **Eventos Entrantes**
```python
@event_handler('onboarding/contract-activated')
async def on_contract_activated(event: ContractActivated):
    """Habilitar creación de campañas cuando contrato se activa"""
    
    # Configurar permisos de campaña para el partner
    command = ConfigurePartnerCampaignPermissions(
        partner_id=event.partner_id,
        contract_id=event.contract_id,
        campaign_permissions=event.campaign_permissions,
        budget_limits=event.budget_limits,
        feature_flags=event.feature_flags
    )
    
    await self.command_bus.dispatch(command)
    
    # Crear campaña de bienvenida automática si está configurada
    if event.feature_flags.get('auto_welcome_campaign', False):
        welcome_command = CreateWelcomeCampaign(
            partner_id=event.partner_id,
            contract_terms=event.contract_terms,
            initial_budget=event.budget_limits.get('welcome_campaign_budget', 1000)
        )
        
        await self.command_bus.dispatch(welcome_command)

@event_handler('partner-management/partner-validation')
async def on_partner_validation_completed(event: PartnerValidationCompleted):
    """Actualizar límites de campaña cuando partner completa validación"""
    
    if event.validation_status == "FULLY_VALIDATED":
        # Incrementar límites para partners validados
        command = UpdatePartnerCampaignLimits(
            partner_id=event.partner_id,
            new_limits={
                'daily_budget_limit': 10000,  # $10k diario
                'monthly_budget_limit': 100000,  # $100k mensual
                'max_active_campaigns': 10,
                'advanced_targeting_enabled': True
            }
        )
        
        await self.command_bus.dispatch(command)
```

### **Eventos Salientes**
```python
class CampaignPerformanceReport(IntegrationEvent):
    """Reporte periódico de rendimiento → Partner Management + Analytics"""
    
    def __init__(self, campaign_id: str, partner_id: str, **kwargs):
        super().__init__(
            aggregate_id=campaign_id,
            partner_id=partner_id,
            reporting_period=kwargs.get('reporting_period'),
            performance_summary=kwargs.get('performance_summary'),
            kpi_achievements=kwargs.get('kpi_achievements'),
            budget_utilization=kwargs.get('budget_utilization'),
            optimization_opportunities=kwargs.get('optimization_opportunities'),
            **kwargs
        )
    
    def get_routing_keys(self) -> List[str]:
        return [
            f"campaign-management.performance.{self.event_data['partner_id']}",
            "campaign-management.performance.all"
        ]

# Scheduler para reportes automáticos
@scheduler.scheduled_job('cron', hour=0, minute=0)  # Diario a medianoche
async def generate_daily_performance_reports():
    """Generar reportes diarios de rendimiento"""
    
    active_campaigns = await campaign_repository.get_active_campaigns()
    
    for campaign in active_campaigns:
        # Generar métricas del día anterior
        yesterday = datetime.utcnow() - timedelta(days=1)
        performance_data = await metrics_service.get_daily_performance(
            campaign.id, yesterday
        )
        
        # Crear reporte
        report_event = CampaignPerformanceReport(
            campaign_id=campaign.id,
            partner_id=campaign.partner_id,
            reporting_period={
                'start_date': yesterday.date().isoformat(),
                'end_date': yesterday.date().isoformat(),
                'period_type': 'DAILY'
            },
            performance_summary=performance_data.summary,
            kpi_achievements=performance_data.kpi_status,
            budget_utilization=performance_data.budget_usage
        )
        
        # Publicar evento
        await event_publisher.publish(
            'campaign-management/performance-report',
            report_event
        )
```

---

Este diseño del Campaign Management Service proporciona una plataforma completa de gestión de campañas con capacidades avanzadas de targeting, optimización automática basada en IA, métricas en tiempo real y control presupuestario inteligente, todo integrado en la arquitectura de microservicios de HexaBuilders.