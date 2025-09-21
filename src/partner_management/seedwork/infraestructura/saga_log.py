"""
SagaLog - Sistema de Logging y Auditoría para Sagas
Proporciona trazabilidad completa, métricas y debugging para transacciones distribuidas.
"""

import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass, asdict
from uuid import uuid4
import os
import threading
from collections import deque

class SagaLogLevel(Enum):
    """Niveles de logging para Saga"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class SagaEventType(Enum):
    """Tipos de eventos de Saga"""
    SAGA_STARTED = "SAGA_STARTED"
    SAGA_STEP_STARTED = "SAGA_STEP_STARTED"
    SAGA_STEP_COMPLETED = "SAGA_STEP_COMPLETED"
    SAGA_STEP_FAILED = "SAGA_STEP_FAILED"
    SAGA_STEP_COMPENSATED = "SAGA_STEP_COMPENSATED"
    SAGA_COMPLETED = "SAGA_COMPLETED"
    SAGA_FAILED = "SAGA_FAILED"
    SAGA_COMPENSATED = "SAGA_COMPENSATED"
    EVENT_PUBLISHED = "EVENT_PUBLISHED"
    EVENT_RECEIVED = "EVENT_RECEIVED"
    EVENT_PROCESSED = "EVENT_PROCESSED"
    EVENT_FAILED = "EVENT_FAILED"
    COMPENSATION_STARTED = "COMPENSATION_STARTED"
    COMPENSATION_COMPLETED = "COMPENSATION_COMPLETED"
    COMPENSATION_FAILED = "COMPENSATION_FAILED"

@dataclass
class SagaLogEntry:
    """Entrada individual del log de Saga"""
    id: str
    timestamp: datetime
    level: SagaLogLevel
    event_type: SagaEventType
    saga_id: str
    partner_id: str
    step_name: Optional[str] = None
    message: str = ""
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    service_name: Optional[str] = None
    event_data: Optional[Dict[str, Any]] = None
    error_details: Optional[Dict[str, Any]] = None
    duration_ms: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convierte la entrada a diccionario"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['level'] = self.level.value
        data['event_type'] = self.event_type.value
        return data

@dataclass
class SagaMetrics:
    """Métricas de performance de la Saga"""
    saga_id: str
    partner_id: str
    total_steps: int
    completed_steps: int
    failed_steps: int
    compensated_steps: int
    total_duration_ms: float
    average_step_duration_ms: float
    start_time: datetime
    end_time: Optional[datetime] = None
    status: str = "IN_PROGRESS"
    error_count: int = 0
    compensation_count: int = 0

class SagaLog:
    """Sistema principal de logging para Sagas"""
    
    def __init__(self, 
                 log_file_path: str = "/app/logs/saga_logs.json",
                 max_entries: int = 10000,
                 enable_console_logging: bool = True,
                 enable_file_logging: bool = True):
        self.log_file_path = log_file_path
        self.max_entries = max_entries
        self.enable_console_logging = enable_console_logging
        self.enable_file_logging = enable_file_logging
        
        # Storage
        self._entries: deque = deque(maxlen=max_entries)
        self._saga_metrics: Dict[str, SagaMetrics] = {}
        self._step_timers: Dict[str, Dict[str, datetime]] = {}
        
        # Threading
        self._lock = threading.RLock()
        
        # Logger
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Ensure log directory exists
        if self.enable_file_logging:
            os.makedirs(os.path.dirname(self.log_file_path), exist_ok=True)
        
        # Load existing logs if file exists
        self._load_existing_logs()
    
    def _load_existing_logs(self):
        """Carga logs existentes del archivo"""
        if not os.path.exists(self.log_file_path):
            return
        
        try:
            with open(self.log_file_path, 'r', encoding='utf-8') as f:
                logs = json.load(f)
                for log_data in logs:
                    entry = SagaLogEntry(
                        id=log_data['id'],
                        timestamp=datetime.fromisoformat(log_data['timestamp']),
                        level=SagaLogLevel(log_data['level']),
                        event_type=SagaEventType(log_data['event_type']),
                        saga_id=log_data['saga_id'],
                        partner_id=log_data['partner_id'],
                        step_name=log_data.get('step_name'),
                        message=log_data.get('message', ''),
                        correlation_id=log_data.get('correlation_id'),
                        causation_id=log_data.get('causation_id'),
                        service_name=log_data.get('service_name'),
                        event_data=log_data.get('event_data'),
                        error_details=log_data.get('error_details'),
                        duration_ms=log_data.get('duration_ms'),
                        metadata=log_data.get('metadata')
                    )
                    self._entries.append(entry)
        except Exception as e:
            self.logger.warning(f"Failed to load existing logs: {e}")
    
    def _save_logs(self):
        """Guarda logs al archivo"""
        if not self.enable_file_logging:
            return
        
        try:
            with open(self.log_file_path, 'w', encoding='utf-8') as f:
                json.dump([entry.to_dict() for entry in self._entries], f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save logs: {e}")
    
    def _log(self, 
             level: SagaLogLevel,
             event_type: SagaEventType,
             saga_id: str,
             partner_id: str,
             message: str = "",
             step_name: Optional[str] = None,
             correlation_id: Optional[str] = None,
             causation_id: Optional[str] = None,
             service_name: Optional[str] = None,
             event_data: Optional[Dict[str, Any]] = None,
             error_details: Optional[Dict[str, Any]] = None,
             duration_ms: Optional[float] = None,
             metadata: Optional[Dict[str, Any]] = None):
        """Método interno para logging"""
        
        with self._lock:
            entry = SagaLogEntry(
                id=str(uuid4()),
                timestamp=datetime.now(timezone.utc),
                level=level,
                event_type=event_type,
                saga_id=saga_id,
                partner_id=partner_id,
                step_name=step_name,
                message=message,
                correlation_id=correlation_id,
                causation_id=causation_id,
                service_name=service_name,
                event_data=event_data,
                error_details=error_details,
                duration_ms=duration_ms,
                metadata=metadata
            )
            
            self._entries.append(entry)
            
            # Console logging
            if self.enable_console_logging:
                log_message = f"[{entry.timestamp.isoformat()}] {level.value} - {event_type.value} - Saga: {saga_id} - Partner: {partner_id}"
                if step_name:
                    log_message += f" - Step: {step_name}"
                if message:
                    log_message += f" - {message}"
                
                if level == SagaLogLevel.DEBUG:
                    self.logger.debug(log_message)
                elif level == SagaLogLevel.INFO:
                    self.logger.info(log_message)
                elif level == SagaLogLevel.WARNING:
                    self.logger.warning(log_message)
                elif level == SagaLogLevel.ERROR:
                    self.logger.error(log_message)
                elif level == SagaLogLevel.CRITICAL:
                    self.logger.critical(log_message)
            
            # File logging
            if self.enable_file_logging:
                self._save_logs()
    
    def saga_started(self, saga_id: str, partner_id: str, correlation_id: str, service_name: str, event_data: Dict[str, Any] = None):
        """Registra el inicio de una Saga"""
        self._log(
            level=SagaLogLevel.INFO,
            event_type=SagaEventType.SAGA_STARTED,
            saga_id=saga_id,
            partner_id=partner_id,
            message=f"Saga started for partner {partner_id}",
            correlation_id=correlation_id,
            service_name=service_name,
            event_data=event_data
        )
        
        # Initialize metrics
        with self._lock:
            self._saga_metrics[saga_id] = SagaMetrics(
                saga_id=saga_id,
                partner_id=partner_id,
                total_steps=0,
                completed_steps=0,
                failed_steps=0,
                compensated_steps=0,
                total_duration_ms=0.0,
                average_step_duration_ms=0.0,
                start_time=datetime.now(timezone.utc)
            )
    
    def step_started(self, saga_id: str, partner_id: str, step_name: str, correlation_id: str, service_name: str):
        """Registra el inicio de un paso de la Saga"""
        self._log(
            level=SagaLogLevel.INFO,
            event_type=SagaEventType.SAGA_STEP_STARTED,
            saga_id=saga_id,
            partner_id=partner_id,
            step_name=step_name,
            message=f"Step '{step_name}' started",
            correlation_id=correlation_id,
            service_name=service_name
        )
        
        # Start timer
        with self._lock:
            if saga_id not in self._step_timers:
                self._step_timers[saga_id] = {}
            self._step_timers[saga_id][step_name] = datetime.now(timezone.utc)
    
    def step_completed(self, saga_id: str, partner_id: str, step_name: str, correlation_id: str, service_name: str, duration_ms: float = None):
        """Registra la finalización exitosa de un paso"""
        if duration_ms is None:
            # Calculate duration
            with self._lock:
                if saga_id in self._step_timers and step_name in self._step_timers[saga_id]:
                    start_time = self._step_timers[saga_id][step_name]
                    duration_ms = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
                    del self._step_timers[saga_id][step_name]
        
        self._log(
            level=SagaLogLevel.INFO,
            event_type=SagaEventType.SAGA_STEP_COMPLETED,
            saga_id=saga_id,
            partner_id=partner_id,
            step_name=step_name,
            message=f"Step '{step_name}' completed successfully",
            correlation_id=correlation_id,
            service_name=service_name,
            duration_ms=duration_ms
        )
        
        # Update metrics
        with self._lock:
            if saga_id in self._saga_metrics:
                metrics = self._saga_metrics[saga_id]
                metrics.completed_steps += 1
                if duration_ms:
                    metrics.total_duration_ms += duration_ms
                    metrics.average_step_duration_ms = metrics.total_duration_ms / metrics.completed_steps
    
    def step_failed(self, saga_id: str, partner_id: str, step_name: str, correlation_id: str, service_name: str, error: Exception, duration_ms: float = None):
        """Registra el fallo de un paso"""
        if duration_ms is None:
            # Calculate duration
            with self._lock:
                if saga_id in self._step_timers and step_name in self._step_timers[saga_id]:
                    start_time = self._step_timers[saga_id][step_name]
                    duration_ms = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
                    del self._step_timers[saga_id][step_name]
        
        error_details = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": str(error.__traceback__) if hasattr(error, '__traceback__') else None
        }
        
        self._log(
            level=SagaLogLevel.ERROR,
            event_type=SagaEventType.SAGA_STEP_FAILED,
            saga_id=saga_id,
            partner_id=partner_id,
            step_name=step_name,
            message=f"Step '{step_name}' failed: {str(error)}",
            correlation_id=correlation_id,
            service_name=service_name,
            error_details=error_details,
            duration_ms=duration_ms
        )
        
        # Update metrics
        with self._lock:
            if saga_id in self._saga_metrics:
                metrics = self._saga_metrics[saga_id]
                metrics.failed_steps += 1
                metrics.error_count += 1
                if duration_ms:
                    metrics.total_duration_ms += duration_ms
    
    def step_compensated(self, saga_id: str, partner_id: str, step_name: str, correlation_id: str, service_name: str, duration_ms: float = None):
        """Registra la compensación de un paso"""
        self._log(
            level=SagaLogLevel.WARNING,
            event_type=SagaEventType.SAGA_STEP_COMPENSATED,
            saga_id=saga_id,
            partner_id=partner_id,
            step_name=step_name,
            message=f"Step '{step_name}' compensated",
            correlation_id=correlation_id,
            service_name=service_name,
            duration_ms=duration_ms
        )
        
        # Update metrics
        with self._lock:
            if saga_id in self._saga_metrics:
                metrics = self._saga_metrics[saga_id]
                metrics.compensated_steps += 1
                metrics.compensation_count += 1
                if duration_ms:
                    metrics.total_duration_ms += duration_ms
    
    def saga_completed(self, saga_id: str, partner_id: str, correlation_id: str, service_name: str):
        """Registra la finalización exitosa de la Saga"""
        self._log(
            level=SagaLogLevel.INFO,
            event_type=SagaEventType.SAGA_COMPLETED,
            saga_id=saga_id,
            partner_id=partner_id,
            message=f"Saga completed successfully for partner {partner_id}",
            correlation_id=correlation_id,
            service_name=service_name
        )
        
        # Update metrics
        with self._lock:
            if saga_id in self._saga_metrics:
                metrics = self._saga_metrics[saga_id]
                metrics.status = "COMPLETED"
                metrics.end_time = datetime.now(timezone.utc)
                metrics.total_duration_ms = (metrics.end_time - metrics.start_time).total_seconds() * 1000
    
    def saga_failed(self, saga_id: str, partner_id: str, correlation_id: str, service_name: str, error: Exception):
        """Registra el fallo de la Saga"""
        error_details = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": str(error.__traceback__) if hasattr(error, '__traceback__') else None
        }
        
        self._log(
            level=SagaLogLevel.ERROR,
            event_type=SagaEventType.SAGA_FAILED,
            saga_id=saga_id,
            partner_id=partner_id,
            message=f"Saga failed for partner {partner_id}: {str(error)}",
            correlation_id=correlation_id,
            service_name=service_name,
            error_details=error_details
        )
        
        # Update metrics
        with self._lock:
            if saga_id in self._saga_metrics:
                metrics = self._saga_metrics[saga_id]
                metrics.status = "FAILED"
                metrics.end_time = datetime.now(timezone.utc)
                metrics.total_duration_ms = (metrics.end_time - metrics.start_time).total_seconds() * 1000
    
    def event_published(self, saga_id: str, partner_id: str, event_name: str, correlation_id: str, service_name: str, event_data: Dict[str, Any] = None):
        """Registra la publicación de un evento"""
        self._log(
            level=SagaLogLevel.DEBUG,
            event_type=SagaEventType.EVENT_PUBLISHED,
            saga_id=saga_id,
            partner_id=partner_id,
            message=f"Event '{event_name}' published",
            correlation_id=correlation_id,
            service_name=service_name,
            event_data=event_data
        )
    
    def event_received(self, saga_id: str, partner_id: str, event_name: str, correlation_id: str, service_name: str, event_data: Dict[str, Any] = None):
        """Registra la recepción de un evento"""
        self._log(
            level=SagaLogLevel.DEBUG,
            event_type=SagaEventType.EVENT_RECEIVED,
            saga_id=saga_id,
            partner_id=partner_id,
            message=f"Event '{event_name}' received",
            correlation_id=correlation_id,
            service_name=service_name,
            event_data=event_data
        )
    
    def event_processed(self, saga_id: str, partner_id: str, event_name: str, correlation_id: str, service_name: str, duration_ms: float = None):
        """Registra el procesamiento exitoso de un evento"""
        self._log(
            level=SagaLogLevel.DEBUG,
            event_type=SagaEventType.EVENT_PROCESSED,
            saga_id=saga_id,
            partner_id=partner_id,
            message=f"Event '{event_name}' processed successfully",
            correlation_id=correlation_id,
            service_name=service_name,
            duration_ms=duration_ms
        )
    
    def event_failed(self, saga_id: str, partner_id: str, event_name: str, correlation_id: str, service_name: str, error: Exception):
        """Registra el fallo en el procesamiento de un evento"""
        error_details = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": str(error.__traceback__) if hasattr(error, '__traceback__') else None
        }
        
        self._log(
            level=SagaLogLevel.ERROR,
            event_type=SagaEventType.EVENT_FAILED,
            saga_id=saga_id,
            partner_id=partner_id,
            message=f"Event '{event_name}' processing failed: {str(error)}",
            correlation_id=correlation_id,
            service_name=service_name,
            error_details=error_details
        )
    
    def compensation_started(self, saga_id: str, partner_id: str, step_name: str, correlation_id: str, service_name: str):
        """Registra el inicio de una compensación"""
        self._log(
            level=SagaLogLevel.WARNING,
            event_type=SagaEventType.COMPENSATION_STARTED,
            saga_id=saga_id,
            partner_id=partner_id,
            step_name=step_name,
            message=f"Compensation started for step '{step_name}'",
            correlation_id=correlation_id,
            service_name=service_name
        )
    
    def compensation_completed(self, saga_id: str, partner_id: str, step_name: str, correlation_id: str, service_name: str, duration_ms: float = None):
        """Registra la finalización de una compensación"""
        self._log(
            level=SagaLogLevel.WARNING,
            event_type=SagaEventType.COMPENSATION_COMPLETED,
            saga_id=saga_id,
            partner_id=partner_id,
            step_name=step_name,
            message=f"Compensation completed for step '{step_name}'",
            correlation_id=correlation_id,
            service_name=service_name,
            duration_ms=duration_ms
        )
    
    def compensation_failed(self, saga_id: str, partner_id: str, step_name: str, correlation_id: str, service_name: str, error: Exception):
        """Registra el fallo de una compensación"""
        error_details = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": str(error.__traceback__) if hasattr(error, '__traceback__') else None
        }
        
        self._log(
            level=SagaLogLevel.CRITICAL,
            event_type=SagaEventType.COMPENSATION_FAILED,
            saga_id=saga_id,
            partner_id=partner_id,
            step_name=step_name,
            message=f"Compensation failed for step '{step_name}': {str(error)}",
            correlation_id=correlation_id,
            service_name=service_name,
            error_details=error_details
        )
    
    def get_saga_logs(self, saga_id: str) -> List[SagaLogEntry]:
        """Obtiene todos los logs de una Saga específica"""
        with self._lock:
            return [entry for entry in self._entries if entry.saga_id == saga_id]
    
    def get_partner_logs(self, partner_id: str) -> List[SagaLogEntry]:
        """Obtiene todos los logs de un Partner específico"""
        with self._lock:
            return [entry for entry in self._entries if entry.partner_id == partner_id]
    
    def get_saga_metrics(self, saga_id: str) -> Optional[SagaMetrics]:
        """Obtiene las métricas de una Saga específica"""
        with self._lock:
            return self._saga_metrics.get(saga_id)
    
    def get_all_metrics(self) -> Dict[str, SagaMetrics]:
        """Obtiene todas las métricas de Sagas"""
        with self._lock:
            return self._saga_metrics.copy()
    
    def get_recent_logs(self, limit: int = 100) -> List[SagaLogEntry]:
        """Obtiene los logs más recientes"""
        with self._lock:
            return list(self._entries)[-limit:]
    
    def search_logs(self, 
                   saga_id: Optional[str] = None,
                   partner_id: Optional[str] = None,
                   event_type: Optional[SagaEventType] = None,
                   level: Optional[SagaLogLevel] = None,
                   step_name: Optional[str] = None,
                   service_name: Optional[str] = None,
                   start_time: Optional[datetime] = None,
                   end_time: Optional[datetime] = None) -> List[SagaLogEntry]:
        """Busca logs con filtros específicos"""
        with self._lock:
            results = list(self._entries)
            
            if saga_id:
                results = [entry for entry in results if entry.saga_id == saga_id]
            if partner_id:
                results = [entry for entry in results if entry.partner_id == partner_id]
            if event_type:
                results = [entry for entry in results if entry.event_type == event_type]
            if level:
                results = [entry for entry in results if entry.level == level]
            if step_name:
                results = [entry for entry in results if entry.step_name == step_name]
            if service_name:
                results = [entry for entry in results if entry.service_name == service_name]
            if start_time:
                results = [entry for entry in results if entry.timestamp >= start_time]
            if end_time:
                results = [entry for entry in results if entry.timestamp <= end_time]
            
            return results
    
    def clear_logs(self, older_than_days: int = 30):
        """Limpia logs más antiguos que el número de días especificado"""
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=older_than_days)
        
        with self._lock:
            self._entries = deque(
                [entry for entry in self._entries if entry.timestamp >= cutoff_date],
                maxlen=self.max_entries
            )
            
            # Remove old metrics
            old_sagas = [
                saga_id for saga_id, metrics in self._saga_metrics.items()
                if metrics.start_time < cutoff_date
            ]
            for saga_id in old_sagas:
                del self._saga_metrics[saga_id]
            
            # Save updated logs
            if self.enable_file_logging:
                self._save_logs()
    
    def export_logs(self, file_path: str, saga_id: Optional[str] = None):
        """Exporta logs a un archivo JSON"""
        logs_to_export = self.get_saga_logs(saga_id) if saga_id else list(self._entries)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump([entry.to_dict() for entry in logs_to_export], f, indent=2)
    
    def get_health_status(self) -> Dict[str, Any]:
        """Obtiene el estado de salud del sistema de logging"""
        with self._lock:
            total_logs = len(self._entries)
            active_sagas = len([m for m in self._saga_metrics.values() if m.status == "IN_PROGRESS"])
            completed_sagas = len([m for m in self._saga_metrics.values() if m.status == "COMPLETED"])
            failed_sagas = len([m for m in self._saga_metrics.values() if m.status == "FAILED"])
            
            return {
                "status": "healthy",
                "total_logs": total_logs,
                "active_sagas": active_sagas,
                "completed_sagas": completed_sagas,
                "failed_sagas": failed_sagas,
                "log_file_path": self.log_file_path,
                "max_entries": self.max_entries,
                "console_logging_enabled": self.enable_console_logging,
                "file_logging_enabled": self.enable_file_logging
            }

# Singleton instance
_saga_log_instance = None

def get_saga_log() -> SagaLog:
    """Obtiene la instancia singleton del SagaLog"""
    global _saga_log_instance
    if _saga_log_instance is None:
        _saga_log_instance = SagaLog()
    return _saga_log_instance
