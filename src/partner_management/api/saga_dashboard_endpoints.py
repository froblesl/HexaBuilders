"""
Endpoints para el Dashboard de Sagas
Proporciona APIs REST para acceder a logs, métricas y estado de las Sagas.
"""

from flask import Blueprint, request, jsonify
import logging
from datetime import datetime, timezone, timedelta

from src.partner_management.seedwork.infraestructura.saga_log import get_saga_log, SagaLogLevel, SagaEventType
from src.partner_management.seedwork.infraestructura.saga_audit_trail import get_saga_audit_trail
from src.partner_management.seedwork.infraestructura.saga_metrics import get_saga_metrics
from src.partner_management.seedwork.infraestructura.saga_dashboard import get_saga_dashboard

dashboard_bp = Blueprint('saga_dashboard', __name__)
logger = logging.getLogger(__name__)

# Initialize components
saga_log = get_saga_log()
audit_trail = get_saga_audit_trail()
saga_metrics = get_saga_metrics()
saga_dashboard = get_saga_dashboard()

@dashboard_bp.route('/dashboard')
def dashboard():
    """Página principal del dashboard"""
    return saga_dashboard.blueprint.dashboard()

@dashboard_bp.route('/system-status')
def system_status():
    """Estado del sistema de Sagas"""
    try:
        system_metrics = saga_metrics.get_current_system_metrics()
        
        return jsonify({
            "status": "healthy",
            "total_sagas": system_metrics.total_sagas,
            "active_sagas": system_metrics.active_sagas,
            "completed_sagas": system_metrics.completed_sagas,
            "failed_sagas": system_metrics.failed_sagas,
            "compensated_sagas": system_metrics.compensated_sagas,
            "success_rate": system_metrics.success_rate_percent,
            "error_rate": system_metrics.error_rate_percent,
            "compensation_rate": system_metrics.compensation_rate_percent,
            "events_per_second": system_metrics.events_per_second,
            "average_duration_ms": system_metrics.average_saga_duration_ms
        })
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        return jsonify({"error": str(e)}), 500

@dashboard_bp.route('/performance')
def performance():
    """Métricas de performance del sistema"""
    try:
        system_metrics = saga_metrics.get_system_metrics()
        if not system_metrics:
            return jsonify({"error": "No performance metrics available"}), 503
        
        return jsonify({
            "events_per_second": system_metrics.events_per_second,
            "average_duration_ms": system_metrics.average_saga_duration_ms,
            "memory_usage_mb": system_metrics.memory_usage_mb,
            "cpu_usage_percent": system_metrics.cpu_usage_percent,
            "total_events_processed": system_metrics.total_events_processed,
            "system_uptime_hours": system_metrics.system_uptime_hours
        })
    except Exception as e:
        logger.error(f"Error getting performance metrics: {e}")
        return jsonify({"error": str(e)}), 500

@dashboard_bp.route('/alerts')
def alerts():
    """Alertas activas del sistema"""
    try:
        active_alerts = saga_metrics.get_active_alerts()
        return jsonify([{
            "id": alert.id,
            "timestamp": alert.timestamp.isoformat(),
            "saga_id": alert.saga_id,
            "partner_id": alert.partner_id,
            "metric_name": alert.metric_name,
            "current_value": alert.current_value,
            "threshold_value": alert.threshold_value,
            "severity": alert.severity,
            "message": alert.message,
            "resolved": alert.resolved,
            "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None
        } for alert in active_alerts])
    except Exception as e:
        logger.error(f"Error getting alerts: {e}")
        return jsonify({"error": str(e)}), 500

@dashboard_bp.route('/logs')
def logs():
    """Logs del sistema con filtros"""
    try:
        # Get query parameters
        saga_id = request.args.get('saga_id')
        partner_id = request.args.get('partner_id')
        level = request.args.get('level')
        event_type = request.args.get('event_type')
        service_name = request.args.get('service_name')
        step_name = request.args.get('step_name')
        limit = int(request.args.get('limit', 100))
        hours = int(request.args.get('hours', 24))
        
        # Build filters
        filters = {}
        if saga_id:
            filters['saga_id'] = saga_id
        if partner_id:
            filters['partner_id'] = partner_id
        if level:
            try:
                filters['level'] = SagaLogLevel(level)
            except ValueError:
                return jsonify({"error": f"Invalid log level: {level}"}), 400
        if event_type:
            try:
                filters['event_type'] = SagaEventType(event_type)
            except ValueError:
                return jsonify({"error": f"Invalid event type: {event_type}"}), 400
        if service_name:
            filters['service_name'] = service_name
        if step_name:
            filters['step_name'] = step_name
        
        # Add time filter
        if hours > 0:
            start_time = datetime.now(timezone.utc) - timedelta(hours=hours)
            filters['start_time'] = start_time
        
        # Get logs
        logs = saga_log.search_logs(**filters)
        recent_logs = logs[-limit:] if logs else []
        
        return jsonify([{
            "id": log.id,
            "timestamp": log.timestamp.isoformat(),
            "level": log.level.value,
            "event_type": log.event_type.value,
            "saga_id": log.saga_id,
            "partner_id": log.partner_id,
            "step_name": log.step_name,
            "message": log.message,
            "correlation_id": log.correlation_id,
            "causation_id": log.causation_id,
            "service_name": log.service_name,
            "duration_ms": log.duration_ms,
            "error_details": log.error_details,
            "metadata": log.metadata
        } for log in recent_logs])
    except Exception as e:
        logger.error(f"Error getting logs: {e}")
        return jsonify({"error": str(e)}), 500

@dashboard_bp.route('/sagas')
def sagas():
    """Lista de todas las Sagas con métricas"""
    try:
        # Usar el audit trail para obtener las sagas
        all_timelines = audit_trail.get_all_saga_timelines()
        sagas = []
        
        for timeline in all_timelines:
            sagas.append({
                "saga_id": timeline.saga_id,
                "partner_id": timeline.partner_id,
                "total_duration_ms": timeline.total_duration_ms,
                "status": timeline.status,
                "start_time": timeline.start_time.isoformat(),
                "end_time": timeline.end_time.isoformat() if timeline.end_time else None,
                "total_steps": len(timeline.steps),
                "successful_steps": len([s for s in timeline.steps if s.get("result") == "SUCCESS"]),
                "failed_steps": len([s for s in timeline.steps if s.get("result") == "FAILED"]),
                "compensations": len(timeline.compensations),
                "error_summary": timeline.error_summary
            })
        
        return jsonify(sagas)
    except Exception as e:
        logger.error(f"Error getting sagas: {e}")
        return jsonify({"error": str(e)}), 500

@dashboard_bp.route('/sagas/<saga_id>')
def get_saga(saga_id):
    """Detalles de una Saga específica"""
    try:
        # Get saga metrics
        performance = saga_metrics.get_saga_performance(saga_id)
        if not performance:
            return jsonify({"error": "Saga not found"}), 404
        
        # Get saga logs
        logs = saga_log.get_saga_logs(saga_id)
        
        # Get saga timeline
        timeline = audit_trail.get_saga_timeline(saga_id)
        
        return jsonify({
            "saga_id": saga_id,
            "performance": {
                "total_duration_ms": performance.total_duration_ms,
                "average_step_duration_ms": performance.average_step_duration_ms,
                "slowest_step": performance.slowest_step,
                "slowest_step_duration_ms": performance.slowest_step_duration_ms,
                "fastest_step": performance.fastest_step,
                "fastest_step_duration_ms": performance.fastest_step_duration_ms,
                "error_count": performance.error_count,
                "compensation_count": performance.compensation_count,
                "throughput_events_per_second": performance.throughput_events_per_second
            },
            "timeline": {
                "saga_id": timeline.saga_id if timeline else None,
                "partner_id": timeline.partner_id if timeline else None,
                "start_time": timeline.start_time.isoformat() if timeline else None,
                "end_time": timeline.end_time.isoformat() if timeline else None,
                "total_duration_ms": timeline.total_duration_ms if timeline else None,
                "status": timeline.status if timeline else None,
                "steps": timeline.steps if timeline else [],
                "events": timeline.events if timeline else [],
                "compensations": timeline.compensations if timeline else [],
                "error_summary": timeline.error_summary if timeline else None
            },
            "logs": [{
                "id": log.id,
                "timestamp": log.timestamp.isoformat(),
                "level": log.level.value,
                "event_type": log.event_type.value,
                "step_name": log.step_name,
                "message": log.message,
                "service_name": log.service_name,
                "duration_ms": log.duration_ms,
                "error_details": log.error_details
            } for log in logs[-50:]]  # Last 50 logs
        })
    except Exception as e:
        logger.error(f"Error getting saga details: {e}")
        return jsonify({"error": str(e)}), 500

@dashboard_bp.route('/timeline/<saga_id>')
def timeline(saga_id):
    """Línea de tiempo de una Saga específica"""
    try:
        timeline = audit_trail.get_saga_timeline(saga_id)
        if not timeline:
            return jsonify({"error": "Saga not found"}), 404
        
        return jsonify({
            "saga_id": timeline.saga_id,
            "partner_id": timeline.partner_id,
            "start_time": timeline.start_time.isoformat(),
            "end_time": timeline.end_time.isoformat() if timeline.end_time else None,
            "total_duration_ms": timeline.total_duration_ms,
            "status": timeline.status,
            "steps": timeline.steps,
            "events": timeline.events,
            "compensations": timeline.compensations,
            "error_summary": timeline.error_summary
        })
    except Exception as e:
        logger.error(f"Error getting saga timeline: {e}")
        return jsonify({"error": str(e)}), 500

@dashboard_bp.route('/trends')
def trends():
    """Tendencias de performance del sistema"""
    try:
        hours = int(request.args.get('hours', 24))
        trends_data = saga_metrics.get_performance_trends(hours=hours)
        
        # Get system metrics history
        history = saga_metrics.get_system_metrics_history(hours=hours)
        
        # Generate chart data
        labels = []
        success_rates = []
        error_rates = []
        events_per_second = []
        compensation_rates = []
        
        for i, metrics in enumerate(history):
            hour = datetime.now(timezone.utc) - timedelta(hours=len(history)-1-i)
            labels.append(hour.strftime('%H:%M'))
            success_rates.append(metrics.success_rate_percent)
            error_rates.append(metrics.error_rate_percent)
            events_per_second.append(metrics.events_per_second)
            compensation_rates.append(metrics.compensation_rate_percent)
        
        return jsonify({
            "labels": labels,
            "success_rates": success_rates,
            "error_rates": error_rates,
            "events_per_second": events_per_second,
            "compensation_rates": compensation_rates,
            "trends": trends_data
        })
    except Exception as e:
        logger.error(f"Error getting trends: {e}")
        return jsonify({"error": str(e)}), 500

@dashboard_bp.route('/recommendations/<saga_id>')
def recommendations(saga_id):
    """Recomendaciones de optimización para una Saga"""
    try:
        recommendations = saga_metrics.get_performance_recommendations(saga_id)
        return jsonify({
            "saga_id": saga_id,
            "recommendations": recommendations
        })
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        return jsonify({"error": str(e)}), 500

@dashboard_bp.route('/export/<saga_id>')
def export_saga(saga_id):
    """Exporta todos los datos de una Saga"""
    try:
        # Get all data
        performance = saga_metrics.get_saga_performance(saga_id)
        logs = saga_log.get_saga_logs(saga_id)
        timeline = audit_trail.get_saga_timeline(saga_id)
        
        export_data = {
            "saga_id": saga_id,
            "export_timestamp": datetime.now(timezone.utc).isoformat(),
            "performance": performance.__dict__ if performance else None,
            "timeline": timeline.__dict__ if timeline else None,
            "logs": [log.to_dict() for log in logs]
        }
        
        return jsonify(export_data)
    except Exception as e:
        logger.error(f"Error exporting saga: {e}")
        return jsonify({"error": str(e)}), 500

@dashboard_bp.route('/health')
def health():
    """Estado de salud del sistema de logging y monitoreo"""
    try:
        log_health = saga_log.get_health_status()
        audit_health = audit_trail.get_health_status()
        metrics_health = saga_metrics.get_health_status()
        
        return jsonify({
            "status": "healthy",
            "components": {
                "saga_log": log_health,
                "audit_trail": audit_health,
                "metrics": metrics_health
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    except Exception as e:
        logger.error(f"Error getting health status: {e}")
        return jsonify({"error": str(e)}), 500

@dashboard_bp.route('/clear-logs')
def clear_logs():
    """Limpia logs antiguos (solo para administración)"""
    try:
        days = int(request.args.get('days', 30))
        saga_log.clear_logs(older_than_days=days)
        
        return jsonify({
            "message": f"Logs older than {days} days have been cleared",
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    except Exception as e:
        logger.error(f"Error clearing logs: {e}")
        return jsonify({"error": str(e)}), 500

@dashboard_bp.route('/resolve-alert/<alert_id>')
def resolve_alert(alert_id):
    """Resuelve una alerta específica"""
    try:
        saga_metrics.resolve_alert(alert_id)
        return jsonify({
            "message": f"Alert {alert_id} resolved",
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    except Exception as e:
        logger.error(f"Error resolving alert: {e}")
        return jsonify({"error": str(e)}), 500
