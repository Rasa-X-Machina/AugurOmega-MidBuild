"""
Comprehensive observability and monitoring system for triumvirate components
"""

import asyncio
import time
import psutil
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from collections import defaultdict, deque
import logging
import json
import threading
from enum import Enum

from .base import ComponentType, TriumvirateMessage

class MetricType(Enum):
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"

class AlertSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class Metric:
    """Metric data structure"""
    name: str
    value: float
    metric_type: MetricType
    labels: Dict[str, str]
    timestamp: datetime
    component_id: Optional[str] = None

@dataclass
class Alert:
    """Alert data structure"""
    id: str
    severity: AlertSeverity
    title: str
    message: str
    component_id: str
    timestamp: datetime
    acknowledged: bool = False
    resolved: bool = False
    details: Dict[str, Any] = None

class ObservabilityManager:
    """Centralized observability and monitoring system"""
    
    def __init__(self, metrics_retention_hours: int = 24, max_alerts: int = 1000):
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self.alerts: List[Alert] = []
        self.metric_handlers: List[Callable] = []
        self.alert_handlers: List[Callable] = []
        self.component_metrics: Dict[str, Dict[str, Any]] = {}
        self.logger = logging.getLogger("ObservabilityManager")
        
        # System monitoring
        self.system_metrics_interval = 10  # seconds
        self.is_monitoring = False
        self.system_task = None
        
        # Performance tracking
        self.message_counts = defaultdict(int)
        self.message_times = defaultdict(list)
        self.component_health_history: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        
    async def start(self) -> None:
        """Start the observability system"""
        self.is_monitoring = True
        self.system_task = asyncio.create_task(self._system_monitor_loop())
        self.logger.info("Observability system started")
        
    async def stop(self) -> None:
        """Stop the observability system"""
        self.is_monitoring = False
        if self.system_task:
            self.system_task.cancel()
        self.logger.info("Observability system stopped")
        
    def record_metric(self, metric: Metric) -> None:
        """Record a metric"""
        metric_key = f"{metric.name}:{json.dumps(metric.labels, sort_keys=True)}"
        self.metrics[metric_key].append(metric)
        
        # Call registered handlers
        for handler in self.metric_handlers:
            try:
                handler(metric)
            except Exception as e:
                self.logger.error(f"Metric handler error: {e}")
                
    def increment_counter(self, name: str, component_id: str = None, 
                         value: float = 1, labels: Dict[str, str] = None) -> None:
        """Increment a counter metric"""
        metric = Metric(
            name=name,
            value=value,
            metric_type=MetricType.COUNTER,
            labels=labels or {},
            timestamp=datetime.now(),
            component_id=component_id
        )
        self.record_metric(metric)
        
    def set_gauge(self, name: str, value: float, component_id: str = None,
                 labels: Dict[str, str] = None) -> None:
        """Set a gauge metric"""
        metric = Metric(
            name=name,
            value=value,
            metric_type=MetricType.GAUGE,
            labels=labels or {},
            timestamp=datetime.now(),
            component_id=component_id
        )
        self.record_metric(metric)
        
    def record_timing(self, name: str, duration_ms: float, component_id: str = None,
                     labels: Dict[str, str] = None) -> None:
        """Record a timing metric"""
        metric = Metric(
            name=name,
            value=duration_ms,
            metric_type=MetricType.TIMER,
            labels=labels or {},
            timestamp=datetime.now(),
            component_id=component_id
        )
        self.record_metric(metric)
        
    def record_message_processing(self, message_type: str, duration_ms: float, 
                                component_id: str) -> None:
        """Record message processing metrics"""
        self.message_counts[message_type] += 1
        self.message_times[message_type].append(duration_ms)
        
        self.record_timing(f"message.processing_time", duration_ms, component_id)
        self.increment_counter(f"message.count", component_id, 
                              labels={"message_type": message_type})
                              
    def create_alert(self, severity: AlertSeverity, title: str, message: str,
                    component_id: str, details: Dict[str, Any] = None) -> Alert:
        """Create a new alert"""
        alert = Alert(
            id=f"alert_{int(time.time())}_{len(self.alerts)}",
            severity=severity,
            title=title,
            message=message,
            component_id=component_id,
            timestamp=datetime.now(),
            details=details or {}
        )
        
        self.alerts.append(alert)
        
        # Call alert handlers
        for handler in self.alert_handlers:
            try:
                handler(alert)
            except Exception as e:
                self.logger.error(f"Alert handler error: {e}")
                
        self.logger.warning(f"Alert created: {title} ({severity.value}) for {component_id}")
        return alert
        
    def get_component_metrics(self, component_id: str) -> Dict[str, Any]:
        """Get metrics for a specific component"""
        component_info = {
            "component_id": component_id,
            "metrics": {},
            "health_status": {},
            "performance_stats": {}
        }
        
        # Aggregate metrics for this component
        for metric_key, metric_deque in self.metrics.items():
            component_metrics = [m for m in metric_deque if m.component_id == component_id]
            if component_metrics:
                latest = component_metrics[-1]
                component_info["metrics"][metric_key] = {
                    "latest_value": latest.value,
                    "latest_timestamp": latest.timestamp.isoformat(),
                    "sample_count": len(component_metrics)
                }
                
        # Performance stats
        if component_id in self.component_health_history:
            history = self.component_health_history[component_id]
            if history:
                component_info["health_status"] = history[-1]
                
        # Message statistics
        msg_stats = {}
        for msg_type, times in self.message_times.items():
            msg_stats[msg_type] = {
                "count": self.message_counts[msg_type],
                "avg_duration_ms": sum(times) / len(times) if times else 0,
                "latest_duration_ms": times[-1] if times else 0
            }
        component_info["performance_stats"]["messages"] = msg_stats
        
        return component_info
        
    def get_system_overview(self) -> Dict[str, Any]:
        """Get system-wide metrics and overview"""
        return {
            "timestamp": datetime.now().isoformat(),
            "total_components_tracked": len(self.component_metrics),
            "total_alerts": len(self.alerts),
            "active_alerts": len([a for a in self.alerts if not a.resolved]),
            "critical_alerts": len([a for a in self.alerts if a.severity == AlertSeverity.CRITICAL]),
            "system_health": self._calculate_system_health(),
            "top_components_by_message_volume": self._get_top_components_by_volume(),
            "message_volume_trends": self._get_message_trends()
        }
        
    def _calculate_system_health(self) -> Dict[str, Any]:
        """Calculate overall system health score"""
        total_components = len(self.component_metrics)
        if total_components == 0:
            return {"status": "unknown", "score": 0}
            
        healthy_components = 0
        for component_id in self.component_metrics:
            if component_id in self.component_health_history:
                history = self.component_health_history[component_id]
                if history and history[-1].get("status") == "healthy":
                    healthy_components += 1
                    
        health_score = (healthy_components / total_components) * 100
        status = "healthy" if health_score >= 90 else "degraded" if health_score >= 70 else "unhealthy"
        
        return {"status": status, "score": health_score}
        
    def _get_top_components_by_volume(self) -> List[Dict[str, Any]]:
        """Get top components by message volume"""
        component_volumes = defaultdict(int)
        for component_id in self.component_metrics:
            for msg_type, count in self.message_counts.items():
                # This is a simplified version - in practice, you'd track per component
                component_volumes[component_id] += count
                
        sorted_components = sorted(component_volumes.items(), key=lambda x: x[1], reverse=True)
        return [{"component_id": cid, "message_volume": volume} 
                for cid, volume in sorted_components[:10]]
                
    def _get_message_trends(self) -> Dict[str, float]:
        """Get message processing time trends"""
        trends = {}
        for msg_type, times in self.message_times.items():
            if len(times) >= 10:
                recent_avg = sum(times[-10:]) / 10
                trends[msg_type] = recent_avg
        return trends
        
    async def _system_monitor_loop(self) -> None:
        """System monitoring loop for system metrics"""
        while self.is_monitoring:
            try:
                await self._collect_system_metrics()
                await asyncio.sleep(self.system_metrics_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"System monitoring error: {e}")
                await asyncio.sleep(self.system_metrics_interval)
                
    async def _collect_system_metrics(self) -> None:
        """Collect system-level metrics"""
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        self.set_gauge("system.cpu.usage_percent", cpu_percent, "system")
        
        # Memory usage
        memory = psutil.virtual_memory()
        self.set_gauge("system.memory.usage_percent", memory.percent, "system")
        self.set_gauge("system.memory.available_bytes", memory.available, "system")
        
        # Disk usage
        disk = psutil.disk_usage('/')
        self.set_gauge("system.disk.usage_percent", (disk.used / disk.total) * 100, "system")
        
    def add_metric_handler(self, handler: Callable) -> None:
        """Add a custom metric handler"""
        self.metric_handlers.append(handler)
        
    def add_alert_handler(self, handler: Callable) -> None:
        """Add a custom alert handler"""
        self.alert_handlers.append(handler)
        
    def update_component_health(self, component_id: str, status: str, 
                              details: Dict[str, Any] = None) -> None:
        """Update component health status"""
        health_record = {
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        }
        
        self.component_health_history[component_id].append(health_record)
        self.component_metrics[component_id] = health_record
        
        # Create alerts for degraded health
        if status in ["degraded", "unhealthy", "critical"]:
            severity = AlertSeverity.CRITICAL if status == "critical" else AlertSeverity.WARNING
            self.create_alert(
                severity,
                f"Component Health Issue",
                f"Component {component_id} status: {status}",
                component_id,
                details
            )
