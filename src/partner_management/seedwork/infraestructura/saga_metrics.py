"""
SagaMetrics - Sistema de Métricas y Análisis de Performance para Sagas
Proporciona métricas detalladas, análisis de performance y alertas para optimización.
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import statistics
import threading

from .saga_log import SagaLog, SagaMetrics as BaseSagaMetrics, get_saga_log
from .saga_audit_trail import SagaAuditTrail, get_saga_audit_trail

@dataclass
class PerformanceMetrics:
    """Métricas de performance de una Saga"""
    saga_id: str
    partner_id: str
    total_duration_ms: float
    average_step_duration_ms: float
    slowest_step: Optional[str] = None
    slowest_step_duration_ms: Optional[float] = None
    fastest_step: Optional[str] = None
    fastest_step_duration_ms: Optional[float] = None
    step_durations: Dict[str, float] = None
    error_count: int = 0
    compensation_count: int = 0
    retry_count: int = 0
    throughput_events_per_second: float = 0.0
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0

@dataclass
class SystemMetrics:
    """Métricas del sistema de Sagas"""
    total_sagas: int
    active_sagas: int
    completed_sagas: int
    failed_sagas: int
    compensated_sagas: int
    average_saga_duration_ms: float
    total_events_processed: int
    events_per_second: float
    error_rate_percent: float
    compensation_rate_percent: float
    success_rate_percent: float
    system_uptime_hours: float
    memory_usage_mb: float
    cpu_usage_percent: float

@dataclass
class AlertThreshold:
    """Umbral para alertas"""
    metric_name: str
    threshold_value: float
    comparison_operator: str  # ">", "<", ">=", "<=", "==", "!="
    severity: str  # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    message: str

@dataclass
class Alert:
    """Alerta generada por el sistema"""
    id: str
    timestamp: datetime
    saga_id: Optional[str]
    partner_id: Optional[str]
    metric_name: str
    current_value: float
    threshold_value: float
    severity: str
    message: str
    resolved: bool = False
    resolved_at: Optional[datetime] = None

class SagaMetrics:
    """Sistema de métricas y análisis de performance para Sagas"""
    
    def __init__(self, 
                 enable_real_time_monitoring: bool = True,
                 alert_check_interval_seconds: int = 30,
                 max_metrics_history: int = 1000):
        self.enable_real_time_monitoring = enable_real_time_monitoring
        self.alert_check_interval_seconds = alert_check_interval_seconds
        self.max_metrics_history = max_metrics_history
        
        # Storage
        self._performance_metrics: Dict[str, PerformanceMetrics] = {}
        self._saga_metrics: Dict[str, Dict[str, Any]] = {}
        self._system_metrics_history: deque = deque(maxlen=max_metrics_history)
        self._alerts: List[Alert] = []
        self._alert_thresholds: List[AlertThreshold] = []
        
        # Threading
        self._lock = threading.RLock()
        
        # Logger
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Dependencies
        self.saga_log = get_saga_log()
        self.audit_trail = get_saga_audit_trail()
        
        # Initialize default thresholds
        self._initialize_default_thresholds()
        
        # Start monitoring thread if enabled
        if self.enable_real_time_monitoring:
            self._start_monitoring_thread()
    
    def _initialize_default_thresholds(self):
        """Inicializa umbrales de alerta por defecto"""
        default_thresholds = [
            AlertThreshold("saga_duration_ms", 300000, ">", "HIGH", "Saga taking too long (>5 minutes)"),
            AlertThreshold("error_rate_percent", 10.0, ">", "MEDIUM", "High error rate detected"),
            AlertThreshold("compensation_rate_percent", 5.0, ">", "MEDIUM", "High compensation rate detected"),
            AlertThreshold("events_per_second", 100, "<", "LOW", "Low event processing rate"),
            AlertThreshold("memory_usage_mb", 1000, ">", "HIGH", "High memory usage detected"),
            AlertThreshold("cpu_usage_percent", 80, ">", "HIGH", "High CPU usage detected"),
            AlertThreshold("success_rate_percent", 90, "<", "MEDIUM", "Low success rate detected")
        ]
        
        self._alert_thresholds.extend(default_thresholds)
    
    def _start_monitoring_thread(self):
        """Inicia el hilo de monitoreo en tiempo real"""
        def monitoring_worker():
            while True:
                try:
                    self._collect_system_metrics()
                    self._check_alerts()
                    threading.Event().wait(self.alert_check_interval_seconds)
                except Exception as e:
                    self.logger.error(f"Error in monitoring thread: {e}")
        
        monitoring_thread = threading.Thread(target=monitoring_worker, daemon=True)
        monitoring_thread.start()
        self.logger.info("Real-time monitoring thread started")
    
    def _collect_system_metrics(self):
        """Recolecta métricas del sistema"""
        with self._lock:
            # Calculate metrics from _saga_metrics
            total_sagas = len(self._saga_metrics)
            active_sagas = len([m for m in self._saga_metrics.values() if m["status"] == "IN_PROGRESS"])
            completed_sagas = len([m for m in self._saga_metrics.values() if m["status"] == "COMPLETED"])
            failed_sagas = len([m for m in self._saga_metrics.values() if m["status"] == "FAILED"])
            compensated_sagas = len([m for m in self._saga_metrics.values() if m["status"] == "COMPENSATED"])
            
            # Calculate average duration
            total_duration = sum(m["total_duration_ms"] for m in self._saga_metrics.values() if m["total_duration_ms"] > 0)
            avg_duration = total_duration / max(completed_sagas, 1)
            
            # Calculate events per second (last hour)
            one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
            recent_records = self.audit_trail.get_audit_records(start_time=one_hour_ago)
            events_per_second = len(recent_records) / 3600 if recent_records else 0
            
            # Calculate rates
            success_rate = (completed_sagas / max(total_sagas, 1)) * 100
            failure_rate = (failed_sagas / max(total_sagas, 1)) * 100
            compensation_rate = (compensated_sagas / max(total_sagas, 1)) * 100
            
            # System metrics
            system_metrics = SystemMetrics(
                total_sagas=total_sagas,
                active_sagas=active_sagas,
                completed_sagas=completed_sagas,
                failed_sagas=failed_sagas,
                compensated_sagas=compensated_sagas,
                average_saga_duration_ms=avg_duration,
                total_events_processed=len(self.audit_trail.get_audit_records()),
                events_per_second=events_per_second,
                error_rate_percent=failure_rate,
                compensation_rate_percent=compensation_rate,
                success_rate_percent=success_rate,
                system_uptime_hours=0,  # Would need to track system start time
                memory_usage_mb=0,  # Would need system monitoring
                cpu_usage_percent=0  # Would need system monitoring
            )
            
            self._system_metrics_history.append(system_metrics)
    
    def _check_alerts(self):
        """Verifica si se han alcanzado umbrales de alerta"""
        if not self._system_metrics_history:
            return
        
        current_metrics = self._system_metrics_history[-1]
        
        for threshold in self._alert_thresholds:
            current_value = getattr(current_metrics, threshold.metric_name, 0)
            
            # Check if threshold is exceeded
            threshold_exceeded = False
            if threshold.comparison_operator == ">":
                threshold_exceeded = current_value > threshold.threshold_value
            elif threshold.comparison_operator == "<":
                threshold_exceeded = current_value < threshold.threshold_value
            elif threshold.comparison_operator == ">=":
                threshold_exceeded = current_value >= threshold.threshold_value
            elif threshold.comparison_operator == "<=":
                threshold_exceeded = current_value <= threshold.threshold_value
            elif threshold.comparison_operator == "==":
                threshold_exceeded = current_value == threshold.threshold_value
            elif threshold.comparison_operator == "!=":
                threshold_exceeded = current_value != threshold.threshold_value
            
            if threshold_exceeded:
                # Check if alert already exists and is not resolved
                existing_alert = next(
                    (alert for alert in self._alerts 
                     if alert.metric_name == threshold.metric_name 
                     and not alert.resolved), 
                    None
                )
                
                if not existing_alert:
                    # Create new alert
                    alert = Alert(
                        id=f"alert_{len(self._alerts) + 1}",
                        timestamp=datetime.now(timezone.utc),
                        saga_id=None,
                        partner_id=None,
                        metric_name=threshold.metric_name,
                        current_value=current_value,
                        threshold_value=threshold.threshold_value,
                        severity=threshold.severity,
                        message=threshold.message
                    )
                    self._alerts.append(alert)
                    self.logger.warning(f"Alert triggered: {alert.message}")
    
    def record_saga_start(self, saga_id: str, partner_id: str, correlation_id: str):
        """Registra el inicio de una saga"""
        with self._lock:
            if saga_id not in self._saga_metrics:
                self._saga_metrics[saga_id] = {
                    "saga_id": saga_id,
                    "partner_id": partner_id,
                    "correlation_id": correlation_id,
                    "status": "IN_PROGRESS",
                    "start_time": datetime.now(timezone.utc),
                    "end_time": None,
                    "total_duration_ms": 0,
                    "steps_completed": 0,
                    "steps_failed": 0,
                    "events_processed": 0,
                    "errors": 0,
                    "compensations": 0
                }
                self.logger.info(f"Saga {saga_id} started for partner {partner_id}")
    
    def record_saga_completion(self, saga_id: str, status: str = "COMPLETED"):
        """Registra la finalización de una saga"""
        with self._lock:
            if saga_id in self._saga_metrics:
                self._saga_metrics[saga_id]["status"] = status
                self._saga_metrics[saga_id]["end_time"] = datetime.now(timezone.utc)
                
                # Calculate total duration
                start_time = self._saga_metrics[saga_id]["start_time"]
                end_time = self._saga_metrics[saga_id]["end_time"]
                duration = (end_time - start_time).total_seconds() * 1000
                self._saga_metrics[saga_id]["total_duration_ms"] = duration
                
                self.logger.info(f"Saga {saga_id} completed with status {status}")
    
    def record_saga_step(self, saga_id: str, step_name: str, duration_ms: float, success: bool = True):
        """Registra un paso completado de una saga"""
        with self._lock:
            if saga_id in self._saga_metrics:
                if success:
                    self._saga_metrics[saga_id]["steps_completed"] += 1
                else:
                    self._saga_metrics[saga_id]["steps_failed"] += 1
                    self._saga_metrics[saga_id]["errors"] += 1
                
                self.logger.debug(f"Saga {saga_id} step {step_name} {'completed' if success else 'failed'} in {duration_ms}ms")
    
    def record_saga_event(self, saga_id: str):
        """Registra un evento procesado por una saga"""
        with self._lock:
            if saga_id in self._saga_metrics:
                self._saga_metrics[saga_id]["events_processed"] += 1
    
    def calculate_saga_performance(self, saga_id: str) -> Optional[PerformanceMetrics]:
        """Calcula métricas de performance para una Saga específica"""
        with self._lock:
            # Get saga metrics from log
            base_metrics = self.saga_log.get_saga_metrics(saga_id)
            if not base_metrics:
                return None
            
            # Get audit records for detailed analysis
            audit_records = self.audit_trail.get_audit_records(saga_id=saga_id)
            
            # Calculate step durations
            step_durations = {}
            step_times = defaultdict(list)
            
            for record in audit_records:
                if record.event_type == "SAGA_STEP_COMPLETED" and record.duration_ms:
                    step_durations[record.step_name] = record.duration_ms
                    step_times[record.step_name].append(record.duration_ms)
            
            # Find slowest and fastest steps
            slowest_step = None
            slowest_duration = 0
            fastest_step = None
            fastest_duration = float('inf')
            
            for step_name, duration in step_durations.items():
                if duration > slowest_duration:
                    slowest_step = step_name
                    slowest_duration = duration
                if duration < fastest_duration:
                    fastest_step = step_name
                    fastest_duration = duration
            
            # Calculate throughput (events per second)
            if base_metrics.total_duration_ms > 0:
                total_events = len(audit_records)
                throughput = (total_events / base_metrics.total_duration_ms) * 1000
            else:
                throughput = 0
            
            # Create performance metrics
            performance_metrics = PerformanceMetrics(
                saga_id=saga_id,
                partner_id=base_metrics.partner_id,
                total_duration_ms=base_metrics.total_duration_ms,
                average_step_duration_ms=base_metrics.average_step_duration_ms,
                slowest_step=slowest_step,
                slowest_step_duration_ms=slowest_duration if slowest_duration > 0 else None,
                fastest_step=fastest_step,
                fastest_step_duration_ms=fastest_duration if fastest_duration < float('inf') else None,
                step_durations=step_durations,
                error_count=base_metrics.error_count,
                compensation_count=base_metrics.compensation_count,
                retry_count=0,  # Would need to track retries
                throughput_events_per_second=throughput,
                memory_usage_mb=0,  # Would need system monitoring
                cpu_usage_percent=0  # Would need system monitoring
            )
            
            self._performance_metrics[saga_id] = performance_metrics
            return performance_metrics
    
    def get_saga_performance(self, saga_id: str) -> Optional[PerformanceMetrics]:
        """Obtiene métricas de performance de una Saga"""
        with self._lock:
            return self._performance_metrics.get(saga_id)
    
    def get_all_performance_metrics(self) -> Dict[str, PerformanceMetrics]:
        """Obtiene todas las métricas de performance"""
        with self._lock:
            # Convert _saga_metrics to PerformanceMetrics objects
            result = {}
            for saga_id, metrics in self._saga_metrics.items():
                result[saga_id] = PerformanceMetrics(
                    saga_id=metrics["saga_id"],
                    partner_id=metrics["partner_id"],
                    total_duration_ms=metrics["total_duration_ms"],
                    average_step_duration_ms=metrics["total_duration_ms"] / max(metrics["steps_completed"], 1),
                    slowest_step="unknown",  # Would need to track this separately
                    slowest_step_duration_ms=0,  # Would need to track this separately
                    fastest_step="unknown",  # Would need to track this separately
                    fastest_step_duration_ms=0,  # Would need to track this separately
                    error_count=metrics["errors"],
                    compensation_count=metrics["compensations"],
                    retry_count=0,  # Would need to track this separately
                    throughput_events_per_second=metrics["events_processed"] / max(metrics["total_duration_ms"] / 1000, 1)
                )
            return result
    
    def get_system_metrics(self) -> Optional[SystemMetrics]:
        """Obtiene las métricas actuales del sistema"""
        with self._lock:
            return self._system_metrics_history[-1] if self._system_metrics_history else None
    
    def get_current_system_metrics(self) -> SystemMetrics:
        """Calcula las métricas actuales del sistema en tiempo real"""
        with self._lock:
            # Calculate metrics from _saga_metrics
            total_sagas = len(self._saga_metrics)
            active_sagas = len([m for m in self._saga_metrics.values() if m["status"] == "IN_PROGRESS"])
            completed_sagas = len([m for m in self._saga_metrics.values() if m["status"] == "COMPLETED"])
            failed_sagas = len([m for m in self._saga_metrics.values() if m["status"] == "FAILED"])
            compensated_sagas = len([m for m in self._saga_metrics.values() if m["status"] == "COMPENSATED"])
            
            # Calculate average duration
            total_duration = sum(m["total_duration_ms"] for m in self._saga_metrics.values() if m["total_duration_ms"] > 0)
            avg_duration = total_duration / max(completed_sagas, 1)
            
            # Calculate events per second (last hour)
            one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
            recent_records = self.audit_trail.get_audit_records(start_time=one_hour_ago)
            events_per_second = len(recent_records) / 3600 if recent_records else 0
            
            # Calculate rates
            success_rate = (completed_sagas / max(total_sagas, 1)) * 100
            failure_rate = (failed_sagas / max(total_sagas, 1)) * 100
            compensation_rate = (compensated_sagas / max(total_sagas, 1)) * 100
            
            # System metrics
            return SystemMetrics(
                total_sagas=total_sagas,
                active_sagas=active_sagas,
                completed_sagas=completed_sagas,
                failed_sagas=failed_sagas,
                compensated_sagas=compensated_sagas,
                average_saga_duration_ms=avg_duration,
                total_events_processed=len(self.audit_trail.get_audit_records()),
                events_per_second=events_per_second,
                error_rate_percent=failure_rate,
                compensation_rate_percent=compensation_rate,
                success_rate_percent=success_rate,
                system_uptime_hours=0,  # Would need to track system start time
                memory_usage_mb=0,  # Would need system monitoring
                cpu_usage_percent=0  # Would need system monitoring
            )
    
    def get_system_metrics_history(self, hours: int = 24) -> List[SystemMetrics]:
        """Obtiene el historial de métricas del sistema"""
        with self._lock:
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
            return [metrics for metrics in self._system_metrics_history 
                   if hasattr(metrics, 'timestamp') and metrics.timestamp >= cutoff_time]
    
    def get_performance_trends(self, hours: int = 24) -> Dict[str, Any]:
        """Analiza tendencias de performance"""
        with self._lock:
            history = self.get_system_metrics_history(hours)
            
            if not history:
                return {"error": "No metrics history available"}
            
            # Calculate trends
            durations = [m.average_saga_duration_ms for m in history]
            error_rates = [m.error_rate_percent for m in history]
            success_rates = [m.success_rate_percent for m in history]
            events_per_second = [m.events_per_second for m in history]
            
            trends = {
                "duration_trend": "increasing" if durations[-1] > durations[0] else "decreasing",
                "error_rate_trend": "increasing" if error_rates[-1] > error_rates[0] else "decreasing",
                "success_rate_trend": "increasing" if success_rates[-1] > success_rates[0] else "decreasing",
                "throughput_trend": "increasing" if events_per_second[-1] > events_per_second[0] else "decreasing",
                "average_duration_ms": statistics.mean(durations) if durations else 0,
                "average_error_rate": statistics.mean(error_rates) if error_rates else 0,
                "average_success_rate": statistics.mean(success_rates) if success_rates else 0,
                "average_throughput": statistics.mean(events_per_second) if events_per_second else 0,
                "duration_volatility": statistics.stdev(durations) if len(durations) > 1 else 0,
                "error_rate_volatility": statistics.stdev(error_rates) if len(error_rates) > 1 else 0
            }
            
            return trends
    
    def get_active_alerts(self) -> List[Alert]:
        """Obtiene alertas activas (no resueltas)"""
        with self._lock:
            return [alert for alert in self._alerts if not alert.resolved]
    
    def get_all_alerts(self) -> List[Alert]:
        """Obtiene todas las alertas"""
        with self._lock:
            return self._alerts.copy()
    
    def resolve_alert(self, alert_id: str):
        """Resuelve una alerta"""
        with self._lock:
            for alert in self._alerts:
                if alert.id == alert_id and not alert.resolved:
                    alert.resolved = True
                    alert.resolved_at = datetime.now(timezone.utc)
                    self.logger.info(f"Alert resolved: {alert_id}")
                    break
    
    def add_alert_threshold(self, threshold: AlertThreshold):
        """Añade un nuevo umbral de alerta"""
        with self._lock:
            self._alert_thresholds.append(threshold)
            self.logger.info(f"Alert threshold added: {threshold.metric_name}")
    
    def remove_alert_threshold(self, metric_name: str):
        """Elimina un umbral de alerta"""
        with self._lock:
            self._alert_thresholds = [t for t in self._alert_thresholds if t.metric_name != metric_name]
            self.logger.info(f"Alert threshold removed: {metric_name}")
    
    def get_performance_recommendations(self, saga_id: str) -> List[str]:
        """Genera recomendaciones de optimización para una Saga"""
        performance = self.get_saga_performance(saga_id)
        if not performance:
            return ["No performance data available for this saga"]
        
        recommendations = []
        
        # Duration recommendations
        if performance.total_duration_ms > 300000:  # 5 minutes
            recommendations.append("Consider optimizing saga steps - total duration exceeds 5 minutes")
        
        if performance.slowest_step_duration_ms and performance.slowest_step_duration_ms > 60000:  # 1 minute
            recommendations.append(f"Optimize step '{performance.slowest_step}' - taking {performance.slowest_step_duration_ms/1000:.1f}s")
        
        # Error recommendations
        if performance.error_count > 0:
            recommendations.append(f"Investigate {performance.error_count} errors in this saga")
        
        # Compensation recommendations
        if performance.compensation_count > 0:
            recommendations.append(f"Review {performance.compensation_count} compensations - consider improving error handling")
        
        # Throughput recommendations
        if performance.throughput_events_per_second < 1:
            recommendations.append("Consider optimizing event processing - low throughput detected")
        
        # Step duration variance
        if performance.step_durations:
            durations = list(performance.step_durations.values())
            if len(durations) > 1:
                variance = statistics.stdev(durations)
                mean_duration = statistics.mean(durations)
                if variance > mean_duration * 0.5:  # High variance
                    recommendations.append("High variance in step durations - consider standardizing processes")
        
        return recommendations
    
    def get_health_status(self) -> Dict[str, Any]:
        """Obtiene el estado de salud del sistema de métricas"""
        with self._lock:
            current_metrics = self.get_system_metrics()
            active_alerts = self.get_active_alerts()
            
            health_status = {
                "status": "healthy",
                "monitoring_enabled": self.enable_real_time_monitoring,
                "total_sagas": current_metrics.total_sagas if current_metrics else 0,
                "active_sagas": current_metrics.active_sagas if current_metrics else 0,
                "success_rate": current_metrics.success_rate_percent if current_metrics else 0,
                "error_rate": current_metrics.error_rate_percent if current_metrics else 0,
                "active_alerts": len(active_alerts),
                "critical_alerts": len([a for a in active_alerts if a.severity == "CRITICAL"]),
                "high_alerts": len([a for a in active_alerts if a.severity == "HIGH"]),
                "alert_thresholds": len(self._alert_thresholds),
                "metrics_history_size": len(self._system_metrics_history)
            }
            
            # Determine overall health
            if health_status["critical_alerts"] > 0:
                health_status["status"] = "critical"
            elif health_status["high_alerts"] > 0:
                health_status["status"] = "warning"
            elif health_status["error_rate"] > 10:
                health_status["status"] = "degraded"
            
            return health_status

# Singleton instance
_saga_metrics_instance = None

def get_saga_metrics() -> SagaMetrics:
    """Obtiene la instancia singleton del SagaMetrics"""
    global _saga_metrics_instance
    if _saga_metrics_instance is None:
        _saga_metrics_instance = SagaMetrics()
    return _saga_metrics_instance
