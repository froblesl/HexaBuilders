"""
SagaDashboard - Dashboard de Visualización y Monitoreo para Sagas
Proporciona una interfaz web para visualizar logs, métricas y estado de las Sagas.
"""

import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from flask import Blueprint, render_template_string, jsonify, request
import threading

from .saga_log import SagaLog, get_saga_log, SagaLogLevel, SagaEventType
from .saga_audit_trail import SagaAuditTrail, get_saga_audit_trail
from .saga_metrics import SagaMetrics, get_saga_metrics

# HTML Template for the Dashboard
DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HexaBuilders - Saga Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
        .header h1 { margin: 0; font-size: 2em; }
        .header p { margin: 5px 0 0 0; opacity: 0.9; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 20px; }
        .card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .card h3 { margin-top: 0; color: #333; border-bottom: 2px solid #667eea; padding-bottom: 10px; }
        .metric { display: flex; justify-content: space-between; margin: 10px 0; }
        .metric-value { font-weight: bold; color: #667eea; }
        .status-badge { padding: 5px 10px; border-radius: 15px; color: white; font-size: 0.8em; }
        .status-healthy { background-color: #28a745; }
        .status-warning { background-color: #ffc107; color: #333; }
        .status-critical { background-color: #dc3545; }
        .status-degraded { background-color: #fd7e14; }
        .log-entry { background: #f8f9fa; padding: 10px; margin: 5px 0; border-radius: 5px; border-left: 4px solid #667eea; }
        .log-error { border-left-color: #dc3545; }
        .log-warning { border-left-color: #ffc107; }
        .log-info { border-left-color: #17a2b8; }
        .log-debug { border-left-color: #6c757d; }
        .timeline { position: relative; padding-left: 30px; }
        .timeline::before { content: ''; position: absolute; left: 15px; top: 0; bottom: 0; width: 2px; background: #667eea; }
        .timeline-item { position: relative; margin-bottom: 20px; }
        .timeline-item::before { content: ''; position: absolute; left: -23px; top: 5px; width: 12px; height: 12px; border-radius: 50%; background: #667eea; }
        .timeline-item.error::before { background: #dc3545; }
        .timeline-item.warning::before { background: #ffc107; }
        .timeline-item.success::before { background: #28a745; }
        .timeline-content { background: white; padding: 15px; border-radius: 5px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        .timeline-time { font-size: 0.8em; color: #666; }
        .timeline-title { font-weight: bold; margin: 5px 0; }
        .timeline-details { font-size: 0.9em; color: #555; }
        .chart-container { position: relative; height: 300px; margin: 20px 0; }
        .alert { padding: 15px; margin: 10px 0; border-radius: 5px; }
        .alert-critical { background-color: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; }
        .alert-high { background-color: #fff3cd; border: 1px solid #ffeaa7; color: #856404; }
        .alert-medium { background-color: #d1ecf1; border: 1px solid #bee5eb; color: #0c5460; }
        .alert-low { background-color: #d4edda; border: 1px solid #c3e6cb; color: #155724; }
        .refresh-btn { background: #667eea; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; margin: 10px 0; }
        .refresh-btn:hover { background: #5a6fd8; }
        .filter-section { background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
        .filter-group { display: inline-block; margin: 0 10px 10px 0; }
        .filter-group label { display: block; margin-bottom: 5px; font-weight: bold; }
        .filter-group select, .filter-group input { padding: 5px; border: 1px solid #ddd; border-radius: 3px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 HexaBuilders Saga Dashboard</h1>
            <p>Monitoreo en tiempo real de transacciones distribuidas</p>
        </div>

        <div class="filter-section">
            <h3>Filtros</h3>
            <div class="filter-group">
                <label for="saga-filter">Saga ID:</label>
                <input type="text" id="saga-filter" placeholder="Filtrar por Saga ID">
            </div>
            <div class="filter-group">
                <label for="partner-filter">Partner ID:</label>
                <input type="text" id="partner-filter" placeholder="Filtrar por Partner ID">
            </div>
            <div class="filter-group">
                <label for="level-filter">Nivel de Log:</label>
                <select id="level-filter">
                    <option value="">Todos</option>
                    <option value="DEBUG">DEBUG</option>
                    <option value="INFO">INFO</option>
                    <option value="WARNING">WARNING</option>
                    <option value="ERROR">ERROR</option>
                    <option value="CRITICAL">CRITICAL</option>
                </select>
            </div>
            <div class="filter-group">
                <label for="service-filter">Servicio:</label>
                <select id="service-filter">
                    <option value="">Todos</option>
                    <option value="partner-management">Partner Management</option>
                    <option value="onboarding">Onboarding</option>
                    <option value="campaign-management">Campaign Management</option>
                    <option value="recruitment">Recruitment</option>
                    <option value="notifications">Notifications</option>
                </select>
            </div>
            <button class="refresh-btn" onclick="refreshDashboard()">🔄 Actualizar</button>
        </div>

        <div class="grid">
            <div class="card">
                <h3>📊 Estado del Sistema</h3>
                <div id="system-status">
                    <div class="metric">
                        <span>Estado General:</span>
                        <span id="overall-status" class="status-badge">Cargando...</span>
                    </div>
                    <div class="metric">
                        <span>Total de Sagas:</span>
                        <span id="total-sagas" class="metric-value">-</span>
                    </div>
                    <div class="metric">
                        <span>Sagas Activas:</span>
                        <span id="active-sagas" class="metric-value">-</span>
                    </div>
                    <div class="metric">
                        <span>Tasa de Éxito:</span>
                        <span id="success-rate" class="metric-value">-</span>
                    </div>
                    <div class="metric">
                        <span>Tasa de Error:</span>
                        <span id="error-rate" class="metric-value">-</span>
                    </div>
                </div>
            </div>

            <div class="card">
                <h3>⚡ Performance</h3>
                <div id="performance-metrics">
                    <div class="metric">
                        <span>Eventos/segundo:</span>
                        <span id="events-per-second" class="metric-value">-</span>
                    </div>
                    <div class="metric">
                        <span>Duración Promedio:</span>
                        <span id="avg-duration" class="metric-value">-</span>
                    </div>
                    <div class="metric">
                        <span>Memoria Usada:</span>
                        <span id="memory-usage" class="metric-value">-</span>
                    </div>
                    <div class="metric">
                        <span>CPU Usage:</span>
                        <span id="cpu-usage" class="metric-value">-</span>
                    </div>
                </div>
            </div>

            <div class="card">
                <h3>🚨 Alertas Activas</h3>
                <div id="active-alerts">
                    <p>Cargando alertas...</p>
                </div>
            </div>

            <div class="card">
                <h3>📈 Tendencias</h3>
                <div class="chart-container">
                    <canvas id="trends-chart"></canvas>
                </div>
            </div>
        </div>

        <div class="grid">
            <div class="card">
                <h3>📋 Logs Recientes</h3>
                <div id="recent-logs">
                    <p>Cargando logs...</p>
                </div>
            </div>

            <div class="card">
                <h3>🕒 Línea de Tiempo de Saga</h3>
                <div id="saga-timeline">
                    <p>Selecciona una Saga para ver su línea de tiempo</p>
                </div>
            </div>
        </div>
    </div>

    <script>
        let trendsChart = null;
        let currentFilters = {};

        function refreshDashboard() {
            // Get current filters
            currentFilters = {
                saga_id: document.getElementById('saga-filter').value,
                partner_id: document.getElementById('partner-filter').value,
                level: document.getElementById('level-filter').value,
                service_name: document.getElementById('service-filter').value
            };

            // Refresh all sections
            loadSystemStatus();
            loadPerformanceMetrics();
            loadActiveAlerts();
            loadRecentLogs();
            loadTrendsChart();
        }

        function loadSystemStatus() {
            fetch('/api/v1/saga-dashboard/system-status')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('overall-status').textContent = data.status.toUpperCase();
                    document.getElementById('overall-status').className = `status-badge status-${data.status}`;
                    document.getElementById('total-sagas').textContent = data.total_sagas || 0;
                    document.getElementById('active-sagas').textContent = data.active_sagas || 0;
                    document.getElementById('success-rate').textContent = `${(data.success_rate || 0).toFixed(1)}%`;
                    document.getElementById('error-rate').textContent = `${(data.error_rate || 0).toFixed(1)}%`;
                })
                .catch(error => console.error('Error loading system status:', error));
        }

        function loadPerformanceMetrics() {
            fetch('/api/v1/saga-dashboard/performance')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('events-per-second').textContent = `${(data.events_per_second || 0).toFixed(2)}/s`;
                    document.getElementById('avg-duration').textContent = `${(data.average_duration_ms || 0).toFixed(0)}ms`;
                    document.getElementById('memory-usage').textContent = `${(data.memory_usage_mb || 0).toFixed(1)}MB`;
                    document.getElementById('cpu-usage').textContent = `${(data.cpu_usage_percent || 0).toFixed(1)}%`;
                })
                .catch(error => console.error('Error loading performance metrics:', error));
        }

        function loadActiveAlerts() {
            fetch('/api/v1/saga-dashboard/alerts')
                .then(response => response.json())
                .then(data => {
                    const alertsContainer = document.getElementById('active-alerts');
                    if (data.length === 0) {
                        alertsContainer.innerHTML = '<p>✅ No hay alertas activas</p>';
                        return;
                    }

                    let alertsHtml = '';
                    data.forEach(alert => {
                        const alertClass = `alert-${alert.severity.toLowerCase()}`;
                        alertsHtml += `
                            <div class="alert ${alertClass}">
                                <strong>${alert.severity}:</strong> ${alert.message}<br>
                                <small>Métrica: ${alert.metric_name} (${alert.current_value} vs ${alert.threshold_value})</small>
                            </div>
                        `;
                    });
                    alertsContainer.innerHTML = alertsHtml;
                })
                .catch(error => console.error('Error loading alerts:', error));
        }

        function loadRecentLogs() {
            const params = new URLSearchParams(currentFilters);
            fetch(`/api/v1/saga-dashboard/logs?${params}`)
                .then(response => response.json())
                .then(data => {
                    const logsContainer = document.getElementById('recent-logs');
                    if (data.length === 0) {
                        logsContainer.innerHTML = '<p>No hay logs disponibles</p>';
                        return;
                    }

                    let logsHtml = '';
                    data.forEach(log => {
                        const logClass = `log-${log.level.toLowerCase()}`;
                        logsHtml += `
                            <div class="log-entry ${logClass}">
                                <div style="display: flex; justify-content: space-between;">
                                    <strong>${log.event_type}</strong>
                                    <span style="font-size: 0.8em; color: #666;">${new Date(log.timestamp).toLocaleString()}</span>
                                </div>
                                <div>Saga: ${log.saga_id} | Partner: ${log.partner_id}</div>
                                <div>${log.message}</div>
                                ${log.step_name ? `<div><small>Paso: ${log.step_name}</small></div>` : ''}
                            </div>
                        `;
                    });
                    logsContainer.innerHTML = logsHtml;
                })
                .catch(error => console.error('Error loading logs:', error));
        }

        function loadTrendsChart() {
            fetch('/api/v1/saga-dashboard/trends')
                .then(response => response.json())
                .then(data => {
                    const ctx = document.getElementById('trends-chart').getContext('2d');
                    
                    if (trendsChart) {
                        trendsChart.destroy();
                    }

                    trendsChart = new Chart(ctx, {
                        type: 'line',
                        data: {
                            labels: data.labels || [],
                            datasets: [
                                {
                                    label: 'Tasa de Éxito (%)',
                                    data: data.success_rates || [],
                                    borderColor: '#28a745',
                                    backgroundColor: 'rgba(40, 167, 69, 0.1)',
                                    tension: 0.1
                                },
                                {
                                    label: 'Tasa de Error (%)',
                                    data: data.error_rates || [],
                                    borderColor: '#dc3545',
                                    backgroundColor: 'rgba(220, 53, 69, 0.1)',
                                    tension: 0.1
                                },
                                {
                                    label: 'Eventos/segundo',
                                    data: data.events_per_second || [],
                                    borderColor: '#667eea',
                                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                                    tension: 0.1
                                }
                            ]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            scales: {
                                y: {
                                    beginAtZero: true
                                }
                            }
                        }
                    });
                })
                .catch(error => console.error('Error loading trends chart:', error));
        }

        function loadSagaTimeline(sagaId) {
            fetch(`/api/v1/saga-dashboard/timeline/${sagaId}`)
                .then(response => response.json())
                .then(data => {
                    const timelineContainer = document.getElementById('saga-timeline');
                    if (!data) {
                        timelineContainer.innerHTML = '<p>Saga no encontrada</p>';
                        return;
                    }

                    let timelineHtml = `
                        <h4>Saga: ${data.saga_id}</h4>
                        <p><strong>Partner:</strong> ${data.partner_id} | <strong>Estado:</strong> ${data.status}</p>
                        <p><strong>Duración:</strong> ${(data.total_duration_ms || 0).toFixed(0)}ms</p>
                        <div class="timeline">
                    `;

                    data.steps.forEach(step => {
                        const stepClass = step.result === 'FAILED' ? 'error' : 
                                        step.result === 'COMPENSATED' ? 'warning' : 'success';
                        timelineHtml += `
                            <div class="timeline-item ${stepClass}">
                                <div class="timeline-content">
                                    <div class="timeline-time">${new Date(step.timestamp).toLocaleString()}</div>
                                    <div class="timeline-title">${step.step_name || step.event_type}</div>
                                    <div class="timeline-details">
                                        ${step.result} | ${step.service_name}
                                        ${step.duration_ms ? ` | ${step.duration_ms.toFixed(0)}ms` : ''}
                                    </div>
                                </div>
                            </div>
                        `;
                    });

                    timelineHtml += '</div>';
                    timelineContainer.innerHTML = timelineHtml;
                })
                .catch(error => console.error('Error loading saga timeline:', error));
        }

        // Auto-refresh every 30 seconds
        setInterval(refreshDashboard, 30000);

        // Initial load
        refreshDashboard();
    </script>
</body>
</html>
"""

class SagaDashboard:
    """Dashboard de visualización y monitoreo para Sagas"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Dependencies
        self.saga_log = get_saga_log()
        self.audit_trail = get_saga_audit_trail()
        self.saga_metrics = get_saga_metrics()
        
        # Create Flask blueprint
        self.blueprint = Blueprint('saga_dashboard', __name__, url_prefix='/api/v1/saga-dashboard')
        self._register_routes()
    
    def _register_routes(self):
        """Registra las rutas del dashboard"""
        
        @self.blueprint.route('/')
        def dashboard():
            """Página principal del dashboard"""
            return render_template_string(DASHBOARD_TEMPLATE)
        
        @self.blueprint.route('/system-status')
        def system_status():
            """Estado del sistema"""
            try:
                # Get system metrics
                system_metrics = self.saga_metrics.get_system_metrics()
                if not system_metrics:
                    return jsonify({"error": "No system metrics available"})
                
                return jsonify({
                    "status": "healthy",
                    "total_sagas": system_metrics.total_sagas,
                    "active_sagas": system_metrics.active_sagas,
                    "success_rate": system_metrics.success_rate_percent,
                    "error_rate": system_metrics.error_rate_percent,
                    "compensation_rate": system_metrics.compensation_rate_percent
                })
            except Exception as e:
                self.logger.error(f"Error getting system status: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.blueprint.route('/performance')
        def performance():
            """Métricas de performance"""
            try:
                system_metrics = self.saga_metrics.get_system_metrics()
                if not system_metrics:
                    return jsonify({"error": "No performance metrics available"})
                
                return jsonify({
                    "events_per_second": system_metrics.events_per_second,
                    "average_duration_ms": system_metrics.average_saga_duration_ms,
                    "memory_usage_mb": system_metrics.memory_usage_mb,
                    "cpu_usage_percent": system_metrics.cpu_usage_percent
                })
            except Exception as e:
                self.logger.error(f"Error getting performance metrics: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.blueprint.route('/alerts')
        def alerts():
            """Alertas activas"""
            try:
                active_alerts = self.saga_metrics.get_active_alerts()
                return jsonify([{
                    "id": alert.id,
                    "timestamp": alert.timestamp.isoformat(),
                    "saga_id": alert.saga_id,
                    "partner_id": alert.partner_id,
                    "metric_name": alert.metric_name,
                    "current_value": alert.current_value,
                    "threshold_value": alert.threshold_value,
                    "severity": alert.severity,
                    "message": alert.message
                } for alert in active_alerts])
            except Exception as e:
                self.logger.error(f"Error getting alerts: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.blueprint.route('/logs')
        def logs():
            """Logs recientes con filtros"""
            try:
                # Get query parameters
                saga_id = request.args.get('saga_id')
                partner_id = request.args.get('partner_id')
                level = request.args.get('level')
                service_name = request.args.get('service_name')
                limit = int(request.args.get('limit', 50))
                
                # Build filters
                filters = {}
                if saga_id:
                    filters['saga_id'] = saga_id
                if partner_id:
                    filters['partner_id'] = partner_id
                if level:
                    filters['level'] = SagaLogLevel(level)
                if service_name:
                    filters['service_name'] = service_name
                
                # Get logs
                logs = self.saga_log.search_logs(**filters)
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
                    "service_name": log.service_name,
                    "duration_ms": log.duration_ms
                } for log in recent_logs])
            except Exception as e:
                self.logger.error(f"Error getting logs: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.blueprint.route('/trends')
        def trends():
            """Tendencias de performance"""
            try:
                trends_data = self.saga_metrics.get_performance_trends(hours=24)
                
                # Generate sample data for chart (in real implementation, this would come from historical data)
                labels = []
                success_rates = []
                error_rates = []
                events_per_second = []
                
                # Generate last 24 hours of data
                for i in range(24):
                    hour = datetime.now(timezone.utc) - timedelta(hours=23-i)
                    labels.append(hour.strftime('%H:%M'))
                    success_rates.append(85 + (i % 10) - 5)  # Sample data
                    error_rates.append(5 + (i % 5))  # Sample data
                    events_per_second.append(10 + (i % 20))  # Sample data
                
                return jsonify({
                    "labels": labels,
                    "success_rates": success_rates,
                    "error_rates": error_rates,
                    "events_per_second": events_per_second,
                    "trends": trends_data
                })
            except Exception as e:
                self.logger.error(f"Error getting trends: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.blueprint.route('/timeline/<saga_id>')
        def timeline(saga_id):
            """Línea de tiempo de una Saga específica"""
            try:
                timeline = self.audit_trail.get_saga_timeline(saga_id)
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
                self.logger.error(f"Error getting saga timeline: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.blueprint.route('/sagas')
        def sagas():
            """Lista de todas las Sagas"""
            try:
                all_metrics = self.saga_metrics.get_all_performance_metrics()
                sagas = []
                
                for saga_id, metrics in all_metrics.items():
                    sagas.append({
                        "saga_id": saga_id,
                        "partner_id": metrics.partner_id,
                        "total_duration_ms": metrics.total_duration_ms,
                        "status": metrics.status,
                        "completed_steps": metrics.completed_steps,
                        "failed_steps": metrics.failed_steps,
                        "error_count": metrics.error_count
                    })
                
                return jsonify(sagas)
            except Exception as e:
                self.logger.error(f"Error getting sagas: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.blueprint.route('/health')
        def health():
            """Estado de salud del dashboard"""
            try:
                log_health = self.saga_log.get_health_status()
                audit_health = self.audit_trail.get_health_status()
                metrics_health = self.saga_metrics.get_health_status()
                
                return jsonify({
                    "status": "healthy",
                    "components": {
                        "saga_log": log_health,
                        "audit_trail": audit_health,
                        "metrics": metrics_health
                    }
                })
            except Exception as e:
                self.logger.error(f"Error getting dashboard health: {e}")
                return jsonify({"error": str(e)}), 500

# Singleton instance
_saga_dashboard_instance = None

def get_saga_dashboard() -> SagaDashboard:
    """Obtiene la instancia singleton del SagaDashboard"""
    global _saga_dashboard_instance
    if _saga_dashboard_instance is None:
        _saga_dashboard_instance = SagaDashboard()
    return _saga_dashboard_instance
