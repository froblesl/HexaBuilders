"""
SagaAuditTrail - Sistema de Auditoría y Trazabilidad para Sagas
Proporciona un historial completo y trazabilidad de eventos para debugging y compliance.
"""

import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from uuid import uuid4
import os
import threading
from collections import defaultdict

from .saga_log import SagaLog, SagaLogEntry, SagaEventType, SagaLogLevel, get_saga_log

@dataclass
class SagaAuditRecord:
    """Registro de auditoría para un evento de Saga"""
    id: str
    timestamp: datetime
    saga_id: str
    partner_id: str
    event_type: str
    step_name: Optional[str]
    service_name: str
    correlation_id: str
    causation_id: str
    event_data: Dict[str, Any]
    result: str  # SUCCESS, FAILED, COMPENSATED
    error_details: Optional[Dict[str, Any]] = None
    duration_ms: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convierte el registro a diccionario"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data

@dataclass
class SagaTimeline:
    """Línea de tiempo de una Saga"""
    saga_id: str
    partner_id: str
    start_time: datetime
    end_time: Optional[datetime]
    total_duration_ms: float
    steps: List[Dict[str, Any]]
    events: List[Dict[str, Any]]
    compensations: List[Dict[str, Any]]
    status: str
    error_summary: Optional[Dict[str, Any]] = None

class SagaAuditTrail:
    """Sistema de auditoría y trazabilidad para Sagas"""
    
    def __init__(self, 
                 audit_file_path: str = "/app/logs/saga_audit.json",
                 max_records: int = 50000,
                 enable_persistence: bool = True):
        self.audit_file_path = audit_file_path
        self.max_records = max_records
        self.enable_persistence = enable_persistence
        
        # Storage
        self._audit_records: List[SagaAuditRecord] = []
        self._saga_timelines: Dict[str, SagaTimeline] = {}
        
        # Threading
        self._lock = threading.RLock()
        
        # Logger
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # SagaLog instance
        self.saga_log = get_saga_log()
        
        # Ensure audit directory exists
        if self.enable_persistence:
            os.makedirs(os.path.dirname(self.audit_file_path), exist_ok=True)
        
        # Load existing audit records
        self._load_existing_audit()
    
    def _load_existing_audit(self):
        """Carga registros de auditoría existentes"""
        if not os.path.exists(self.audit_file_path):
            self.logger.info("No audit file found, starting fresh")
            return
        
        try:
            with open(self.audit_file_path, 'r') as f:
                audit_data = json.load(f)
                self.logger.info(f"Loading {len(audit_data)} audit records from {self.audit_file_path}")
                
                for record_data in audit_data:
                    record = SagaAuditRecord(
                        id=record_data['id'],
                        timestamp=datetime.fromisoformat(record_data['timestamp']),
                        saga_id=record_data['saga_id'],
                        partner_id=record_data['partner_id'],
                        event_type=record_data['event_type'],
                        step_name=record_data.get('step_name'),
                        service_name=record_data['service_name'],
                        correlation_id=record_data['correlation_id'],
                        causation_id=record_data['causation_id'],
                        event_data=record_data['event_data'],
                        result=record_data['result'],
                        error_details=record_data.get('error_details'),
                        duration_ms=record_data.get('duration_ms'),
                        metadata=record_data.get('metadata')
                    )
                    self._audit_records.append(record)
                    # Reconstruir timeline al cargar cada registro
                    self._update_saga_timeline(record)
                
                self.logger.info(f"Successfully loaded {len(self._audit_records)} audit records and {len(self._saga_timelines)} timelines")
        except Exception as e:
            self.logger.warning(f"Failed to load existing audit records: {e}")
    
    def _save_audit_records(self):
        """Guarda registros de auditoría al archivo"""
        if not self.enable_persistence:
            return
        
        try:
            with open(self.audit_file_path, 'w') as f:
                json.dump([record.to_dict() for record in self._audit_records], f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save audit records: {e}")
    
    def _add_audit_record(self, 
                         saga_id: str,
                         partner_id: str,
                         event_type: str,
                         service_name: str,
                         correlation_id: str,
                         causation_id: str,
                         event_data: Dict[str, Any],
                         result: str,
                         step_name: Optional[str] = None,
                         error_details: Optional[Dict[str, Any]] = None,
                         duration_ms: Optional[float] = None,
                         metadata: Optional[Dict[str, Any]] = None):
        """Añade un registro de auditoría"""
        
        with self._lock:
            record = SagaAuditRecord(
                id=str(uuid4()),
                timestamp=datetime.now(timezone.utc),
                saga_id=saga_id,
                partner_id=partner_id,
                event_type=event_type,
                step_name=step_name,
                service_name=service_name,
                correlation_id=correlation_id,
                causation_id=causation_id,
                event_data=event_data,
                result=result,
                error_details=error_details,
                duration_ms=duration_ms,
                metadata=metadata
            )
            
            self._audit_records.append(record)
            
            # Keep only recent records
            if len(self._audit_records) > self.max_records:
                self._audit_records = self._audit_records[-self.max_records:]
            
            # Update timeline
            self._update_saga_timeline(record)
            
            # Save to file
            if self.enable_persistence:
                self._save_audit_records()
    
    def _update_saga_timeline(self, record: SagaAuditRecord):
        """Actualiza la línea de tiempo de la Saga"""
        saga_id = record.saga_id
        
        if saga_id not in self._saga_timelines:
            self._saga_timelines[saga_id] = SagaTimeline(
                saga_id=saga_id,
                partner_id=record.partner_id,
                start_time=record.timestamp,
                end_time=None,
                total_duration_ms=0.0,
                steps=[],
                events=[],
                compensations=[],
                status="IN_PROGRESS"
            )
        
        timeline = self._saga_timelines[saga_id]
        
        # Update timeline based on event type
        if record.event_type in ["SAGA_STARTED", "SAGA_STEP_STARTED", "SAGA_STEP_COMPLETED", "SAGA_STEP_FAILED", "SAGA_STEP_COMPENSATED"]:
            step_info = {
                "step_name": record.step_name,
                "event_type": record.event_type,
                "timestamp": record.timestamp.isoformat(),
                "service_name": record.service_name,
                "result": record.result,
                "duration_ms": record.duration_ms,
                "error_details": record.error_details
            }
            timeline.steps.append(step_info)
        
        elif record.event_type in ["EVENT_PUBLISHED", "EVENT_RECEIVED", "EVENT_PROCESSED", "EVENT_FAILED"]:
            event_info = {
                "event_type": record.event_type,
                "timestamp": record.timestamp.isoformat(),
                "service_name": record.service_name,
                "event_data": record.event_data,
                "result": record.result,
                "duration_ms": record.duration_ms
            }
            timeline.events.append(event_info)
        
        elif record.event_type in ["COMPENSATION_STARTED", "COMPENSATION_COMPLETED", "COMPENSATION_FAILED"]:
            compensation_info = {
                "step_name": record.step_name,
                "event_type": record.event_type,
                "timestamp": record.timestamp.isoformat(),
                "service_name": record.service_name,
                "result": record.result,
                "duration_ms": record.duration_ms,
                "error_details": record.error_details
            }
            timeline.compensations.append(compensation_info)
        
        # Update status and end time
        if record.event_type in ["SAGA_COMPLETED", "SAGA_FAILED", "SAGA_COMPENSATED"]:
            timeline.status = record.event_type.replace("SAGA_", "").lower()
            timeline.end_time = record.timestamp
            timeline.total_duration_ms = (timeline.end_time - timeline.start_time).total_seconds() * 1000
        
        # Update error summary
        if record.result == "FAILED" and record.error_details:
            if not timeline.error_summary:
                timeline.error_summary = {
                    "total_errors": 0,
                    "error_types": defaultdict(int),
                    "failed_steps": [],
                    "last_error": None
                }
            
            timeline.error_summary["total_errors"] += 1
            timeline.error_summary["error_types"][record.error_details.get("error_type", "Unknown")] += 1
            if record.step_name:
                timeline.error_summary["failed_steps"].append(record.step_name)
            timeline.error_summary["last_error"] = record.error_details
    
    def record_saga_start(self, saga_id: str, partner_id: str, correlation_id: str, service_name: str, event_data: Dict[str, Any]):
        """Registra el inicio de una Saga"""
        self._add_audit_record(
            saga_id=saga_id,
            partner_id=partner_id,
            event_type="SAGA_STARTED",
            service_name=service_name,
            correlation_id=correlation_id,
            causation_id=correlation_id,  # Same as correlation for start
            event_data=event_data,
            result="SUCCESS"
        )
    
    def record_step_start(self, saga_id: str, partner_id: str, step_name: str, correlation_id: str, service_name: str):
        """Registra el inicio de un paso"""
        self._add_audit_record(
            saga_id=saga_id,
            partner_id=partner_id,
            event_type="SAGA_STEP_STARTED",
            service_name=service_name,
            correlation_id=correlation_id,
            causation_id=correlation_id,
            event_data={"step_name": step_name},
            result="SUCCESS",
            step_name=step_name
        )
    
    def record_step_success(self, saga_id: str, partner_id: str, step_name: str, correlation_id: str, service_name: str, duration_ms: float = None):
        """Registra el éxito de un paso"""
        self._add_audit_record(
            saga_id=saga_id,
            partner_id=partner_id,
            event_type="SAGA_STEP_COMPLETED",
            service_name=service_name,
            correlation_id=correlation_id,
            causation_id=correlation_id,
            event_data={"step_name": step_name, "status": "completed"},
            result="SUCCESS",
            step_name=step_name,
            duration_ms=duration_ms
        )
    
    def record_step_failure(self, saga_id: str, partner_id: str, step_name: str, correlation_id: str, service_name: str, error: Exception, duration_ms: float = None):
        """Registra el fallo de un paso"""
        error_details = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": str(error.__traceback__) if hasattr(error, '__traceback__') else None
        }
        
        self._add_audit_record(
            saga_id=saga_id,
            partner_id=partner_id,
            event_type="SAGA_STEP_FAILED",
            service_name=service_name,
            correlation_id=correlation_id,
            causation_id=correlation_id,
            event_data={"step_name": step_name, "status": "failed"},
            result="FAILED",
            step_name=step_name,
            error_details=error_details,
            duration_ms=duration_ms
        )
    
    def record_step_compensation(self, saga_id: str, partner_id: str, step_name: str, correlation_id: str, service_name: str, duration_ms: float = None):
        """Registra la compensación de un paso"""
        self._add_audit_record(
            saga_id=saga_id,
            partner_id=partner_id,
            event_type="SAGA_STEP_COMPENSATED",
            service_name=service_name,
            correlation_id=correlation_id,
            causation_id=correlation_id,
            event_data={"step_name": step_name, "status": "compensated"},
            result="COMPENSATED",
            step_name=step_name,
            duration_ms=duration_ms
        )
    
    def record_event_published(self, saga_id: str, partner_id: str, event_name: str, correlation_id: str, service_name: str, event_data: Dict[str, Any]):
        """Registra la publicación de un evento"""
        self._add_audit_record(
            saga_id=saga_id,
            partner_id=partner_id,
            event_type="EVENT_PUBLISHED",
            service_name=service_name,
            correlation_id=correlation_id,
            causation_id=correlation_id,
            event_data={"event_name": event_name, "data": event_data},
            result="SUCCESS"
        )
    
    def record_event_received(self, saga_id: str, partner_id: str, event_name: str, correlation_id: str, service_name: str, event_data: Dict[str, Any]):
        """Registra la recepción de un evento"""
        self._add_audit_record(
            saga_id=saga_id,
            partner_id=partner_id,
            event_type="EVENT_RECEIVED",
            service_name=service_name,
            correlation_id=correlation_id,
            causation_id=correlation_id,
            event_data={"event_name": event_name, "data": event_data},
            result="SUCCESS"
        )
    
    def record_event_processed(self, saga_id: str, partner_id: str, event_name: str, correlation_id: str, service_name: str, duration_ms: float = None):
        """Registra el procesamiento exitoso de un evento"""
        self._add_audit_record(
            saga_id=saga_id,
            partner_id=partner_id,
            event_type="EVENT_PROCESSED",
            service_name=service_name,
            correlation_id=correlation_id,
            causation_id=correlation_id,
            event_data={"event_name": event_name, "status": "processed"},
            result="SUCCESS",
            duration_ms=duration_ms
        )
    
    def record_event_failure(self, saga_id: str, partner_id: str, event_name: str, correlation_id: str, service_name: str, error: Exception):
        """Registra el fallo en el procesamiento de un evento"""
        error_details = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": str(error.__traceback__) if hasattr(error, '__traceback__') else None
        }
        
        self._add_audit_record(
            saga_id=saga_id,
            partner_id=partner_id,
            event_type="EVENT_FAILED",
            service_name=service_name,
            correlation_id=correlation_id,
            causation_id=correlation_id,
            event_data={"event_name": event_name, "status": "failed"},
            result="FAILED",
            error_details=error_details
        )
    
    def record_saga_completion(self, saga_id: str, partner_id: str, correlation_id: str, service_name: str, status: str):
        """Registra la finalización de una Saga"""
        # Handle both string and dict status
        if isinstance(status, dict):
            status_str = status.get("status", "UNKNOWN")
        else:
            status_str = str(status)
            
        self._add_audit_record(
            saga_id=saga_id,
            partner_id=partner_id,
            event_type=f"SAGA_{status_str.upper()}",
            service_name=service_name,
            correlation_id=correlation_id,
            causation_id=correlation_id,
            event_data={"status": status_str},
            result=status_str.upper()
        )
    
    def record_saga_failure(self, saga_id: str, partner_id: str, correlation_id: str, service_name: str, error_details: Dict[str, Any]):
        """Registra el fallo de una Saga"""
        self._add_audit_record(
            saga_id=saga_id,
            partner_id=partner_id,
            event_type="SAGA_FAILED",
            service_name=service_name,
            correlation_id=correlation_id,
            causation_id=correlation_id,
            event_data=error_details,
            result="FAILED",
            error_details=error_details
        )
    
    def get_saga_timeline(self, saga_id: str) -> Optional[SagaTimeline]:
        """Obtiene la línea de tiempo de una Saga"""
        with self._lock:
            return self._saga_timelines.get(saga_id)
    
    def get_partner_timelines(self, partner_id: str) -> List[SagaTimeline]:
        """Obtiene todas las líneas de tiempo de un Partner"""
        with self._lock:
            return [timeline for timeline in self._saga_timelines.values() if timeline.partner_id == partner_id]
    
    def get_all_saga_timelines(self) -> List[SagaTimeline]:
        """Obtiene todas las líneas de tiempo de sagas"""
        with self._lock:
            return list(self._saga_timelines.values())
    
    def get_audit_records(self, 
                         saga_id: Optional[str] = None,
                         partner_id: Optional[str] = None,
                         event_type: Optional[str] = None,
                         result: Optional[str] = None,
                         service_name: Optional[str] = None,
                         start_time: Optional[datetime] = None,
                         end_time: Optional[datetime] = None) -> List[SagaAuditRecord]:
        """Busca registros de auditoría con filtros"""
        with self._lock:
            results = self._audit_records.copy()
            
            if saga_id:
                results = [record for record in results if record.saga_id == saga_id]
            if partner_id:
                results = [record for record in results if record.partner_id == partner_id]
            if event_type:
                results = [record for record in results if record.event_type == event_type]
            if result:
                results = [record for record in results if record.result == result]
            if service_name:
                results = [record for record in results if record.service_name == service_name]
            if start_time:
                results = [record for record in results if record.timestamp >= start_time]
            if end_time:
                results = [record for record in results if record.timestamp <= end_time]
            
            return results
    
    def get_failed_sagas(self) -> List[SagaTimeline]:
        """Obtiene todas las Sagas que han fallado"""
        with self._lock:
            return [timeline for timeline in self._saga_timelines.values() if timeline.status == "failed"]
    
    def get_compensated_sagas(self) -> List[SagaTimeline]:
        """Obtiene todas las Sagas que han sido compensadas"""
        with self._lock:
            return [timeline for timeline in self._saga_timelines.values() if timeline.status == "compensated"]
    
    def get_saga_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas generales de las Sagas"""
        with self._lock:
            total_sagas = len(self._saga_timelines)
            completed_sagas = len([t for t in self._saga_timelines.values() if t.status == "completed"])
            failed_sagas = len([t for t in self._saga_timelines.values() if t.status == "failed"])
            compensated_sagas = len([t for t in self._saga_timelines.values() if t.status == "compensated"])
            in_progress_sagas = len([t for t in self._saga_timelines.values() if t.status == "IN_PROGRESS"])
            
            total_audit_records = len(self._audit_records)
            
            return {
                "total_sagas": total_sagas,
                "completed_sagas": completed_sagas,
                "failed_sagas": failed_sagas,
                "compensated_sagas": compensated_sagas,
                "in_progress_sagas": in_progress_sagas,
                "total_audit_records": total_audit_records,
                "success_rate": (completed_sagas / total_sagas * 100) if total_sagas > 0 else 0,
                "failure_rate": (failed_sagas / total_sagas * 100) if total_sagas > 0 else 0,
                "compensation_rate": (compensated_sagas / total_sagas * 100) if total_sagas > 0 else 0
            }
    
    def export_audit_trail(self, file_path: str, saga_id: Optional[str] = None):
        """Exporta el trail de auditoría a un archivo"""
        if saga_id:
            records = self.get_audit_records(saga_id=saga_id)
            timeline = self.get_saga_timeline(saga_id)
            export_data = {
                "saga_id": saga_id,
                "timeline": timeline.to_dict() if timeline else None,
                "audit_records": [record.to_dict() for record in records]
            }
        else:
            export_data = {
                "statistics": self.get_saga_statistics(),
                "timelines": [timeline.to_dict() for timeline in self._saga_timelines.values()],
                "audit_records": [record.to_dict() for record in self._audit_records]
            }
        
        with open(file_path, 'w') as f:
            json.dump(export_data, f, indent=2)
    
    def get_health_status(self) -> Dict[str, Any]:
        """Obtiene el estado de salud del sistema de auditoría"""
        with self._lock:
            stats = self.get_saga_statistics()
            
            return {
                "status": "healthy",
                "total_sagas": stats["total_sagas"],
                "total_audit_records": stats["total_audit_records"],
                "success_rate": stats["success_rate"],
                "failure_rate": stats["failure_rate"],
                "compensation_rate": stats["compensation_rate"],
                "audit_file_path": self.audit_file_path,
                "max_records": self.max_records,
                "persistence_enabled": self.enable_persistence
            }

# Singleton instance
_saga_audit_trail_instance = None

def get_saga_audit_trail() -> SagaAuditTrail:
    """Obtiene la instancia singleton del SagaAuditTrail"""
    global _saga_audit_trail_instance
    if _saga_audit_trail_instance is None:
        _saga_audit_trail_instance = SagaAuditTrail()
    return _saga_audit_trail_instance
