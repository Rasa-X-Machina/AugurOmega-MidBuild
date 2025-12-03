"""
Compliance Monitoring for Jivaslokam

Provides real-time compliance monitoring and alerting capabilities
for enterprise deployment scenarios.

Monitors compliance posture, tracks violations, and provides
real-time visibility into compliance status.
"""

import asyncio
import json
import logging
import time
from typing import Dict, Any, List, Optional, Set, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class MonitorStatus(Enum):
    """Monitoring status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PAUSED = "paused"
    ERROR = "error"


class AlertSeverity(Enum):
    """Alert severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class ComplianceMetric:
    """Compliance metric definition"""
    metric_id: str
    name: str
    description: str
    metric_type: str  # counter, gauge, histogram
    compliance_framework: str
    measurement_unit: str
    normal_range: Optional[tuple] = None
    critical_threshold: Optional[float] = None
    warning_threshold: Optional[float] = None
    
    def evaluate_status(self, value: float) -> str:
        """Evaluate metric status based on thresholds"""
        if self.critical_threshold and value >= self.critical_threshold:
            return "critical"
        elif self.warning_threshold and value >= self.warning_threshold:
            return "warning"
        elif self.normal_range:
            min_val, max_val = self.normal_range
            if min_val <= value <= max_val:
                return "normal"
            else:
                return "warning"
        else:
            return "unknown"


@dataclass
class ComplianceAlert:
    """Compliance alert"""
    alert_id: str
    timestamp: str
    severity: AlertSeverity
    title: str
    description: str
    metric_id: Optional[str] = None
    application_id: Optional[str] = None
    current_value: Optional[float] = None
    threshold_value: Optional[float] = None
    resolved: bool = False
    resolved_at: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            'alert_id': self.alert_id,
            'timestamp': self.timestamp,
            'severity': self.severity.value,
            'title': self.title,
            'description': self.description,
            'metric_id': self.metric_id,
            'application_id': self.application_id,
            'current_value': self.current_value,
            'threshold_value': self.threshold_value,
            'resolved': self.resolved,
            'resolved_at': self.resolved_at
        }


@dataclass
class ComplianceDashboard:
    """Compliance dashboard data"""
    timestamp: str
    overall_score: float
    total_applications: int
    compliant_applications: int
    violations_count: int
    active_alerts: int
    frameworks_status: Dict[str, Dict[str, Any]]
    top_violations: List[Dict[str, Any]]
    recent_alerts: List[ComplianceAlert]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            'timestamp': self.timestamp,
            'overall_score': self.overall_score,
            'total_applications': self.total_applications,
            'compliant_applications': self.compliant_applications,
            'violations_count': self.violations_count,
            'active_alerts': self.active_alerts,
            'frameworks_status': self.frameworks_status,
            'top_violations': self.top_violations,
            'recent_alerts': [alert.to_dict() for alert in self.recent_alerts]
        }


class ComplianceMonitor:
    """
    Real-time Compliance Monitor for Jivaslokam
    
    Provides continuous monitoring of compliance posture including:
    - Real-time compliance metrics tracking
    - Automated alerting for compliance violations
    - Compliance dashboard and reporting
    - Historical compliance trend analysis
    - Integration with external monitoring systems
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__ + ".ComplianceMonitor")
        self.compliance_metrics = {}
        self.active_monitors = {}
        self.alert_handlers = {}
        self.compliance_data = {}
        self.alert_history = []
        self.dashboard_cache = {}
        self.monitoring_active = False
        
    async def initialize(self) -> None:
        """Initialize the compliance monitor"""
        self.logger.info("Initializing Compliance Monitor...")
        
        # Load compliance metrics
        await self._load_compliance_metrics()
        
        # Initialize alert handlers
        await self._initialize_alert_handlers()
        
        # Start monitoring
        await self._start_monitoring()
        
        self.logger.info("Compliance Monitor initialized successfully")
    
    async def start_monitoring(self, application_id: str, monitoring_config: Dict[str, Any]) -> bool:
        """
        Start compliance monitoring for an application
        
        Args:
            application_id: Unique application identifier
            monitoring_config: Monitoring configuration
            
        Returns:
            Success status of monitoring start
        """
        try:
            self.logger.info("Starting compliance monitoring for: %s", application_id)
            
            monitor_id = f"monitor_{application_id}_{int(time.time())}"
            
            # Create monitor
            self.active_monitors[monitor_id] = {
                'application_id': application_id,
                'start_time': time.time(),
                'status': MonitorStatus.ACTIVE,
                'config': monitoring_config,
                'metrics': [],
                'alerts': []
            }
            
            # Initialize compliance data storage
            if application_id not in self.compliance_data:
                self.compliance_data[application_id] = {
                    'compliance_score': 1.0,
                    'violations': [],
                    'metrics': {},
                    'last_update': time.time()
                }
            
            # Start metric collection
            asyncio.create_task(self._collect_metrics(monitor_id, application_id))
            
            self.logger.info("Compliance monitoring started for %s", application_id)
            return True
            
        except Exception as e:
            self.logger.error("Failed to start monitoring for %s: %s", application_id, str(e))
            return False
    
    async def stop_monitoring(self, application_id: str) -> bool:
        """Stop compliance monitoring for an application"""
        try:
            # Find active monitor for application
            monitor_ids = [
                mid for mid, data in self.active_monitors.items()
                if data['application_id'] == application_id
            ]
            
            for monitor_id in monitor_ids:
                self.active_monitors[monitor_id]['status'] = MonitorStatus.INACTIVE
                del self.active_monitors[monitor_id]
            
            self.logger.info("Stopped compliance monitoring for %s", application_id)
            return True
            
        except Exception as e:
            self.logger.error("Failed to stop monitoring for %s: %s", application_id, str(e))
            return False
    
    async def get_compliance_dashboard(self, timeframe: str = "1h") -> ComplianceDashboard:
        """
        Get compliance dashboard data
        
        Args:
            timeframe: Data timeframe (5m, 1h, 1d, 1w)
            
        Returns:
            Compliance dashboard with current status
        """
        try:
            dashboard_cache_key = f"dashboard_{timeframe}"
            current_time = time.time()
            
            # Check cache freshness
            if dashboard_cache_key in self.dashboard_cache:
                cached_data = self.dashboard_cache[dashboard_cache_key]
                if current_time - cached_data['timestamp'] < 300:  # 5 minutes cache
                    return cached_data['dashboard']
            
            # Calculate dashboard metrics
            dashboard_data = await self._calculate_dashboard_data(timeframe)
            
            # Cache result
            self.dashboard_cache[dashboard_cache_key] = {
                'dashboard': dashboard_data,
                'timestamp': current_time
            }
            
            return dashboard_data
            
        except Exception as e:
            self.logger.error("Failed to generate compliance dashboard: %s", str(e))
            return ComplianceDashboard(
                timestamp=str(time.time()),
                overall_score=0.0,
                total_applications=0,
                compliant_applications=0,
                violations_count=0,
                active_alerts=0,
                frameworks_status={},
                top_violations=[],
                recent_alerts=[]
            )
    
    async def get_application_status(self, application_id: str) -> Dict[str, Any]:
        """Get current compliance status for an application"""
        try:
            if application_id not in self.compliance_data:
                return {
                    'application_id': application_id,
                    'status': 'not_monitored',
                    'compliance_score': 0.0,
                    'violations_count': 0,
                    'last_update': None
                }
            
            app_data = self.compliance_data[application_id]
            
            # Get active alerts for application
            active_alerts = [
                alert for alert in self.alert_history
                if alert.application_id == application_id and not alert.resolved
            ]
            
            return {
                'application_id': application_id,
                'status': 'monitored',
                'compliance_score': app_data['compliance_score'],
                'violations_count': len(app_data['violations']),
                'active_alerts': len(active_alerts),
                'last_update': app_data['last_update'],
                'frameworks': app_data.get('frameworks', {}),
                'recent_violations': app_data['violations'][-10:]  # Last 10 violations
            }
            
        except Exception as e:
            self.logger.error("Failed to get application status for %s: %s", application_id, str(e))
            return {
                'application_id': application_id,
                'status': 'error',
                'error': str(e)
            }
    
    async def update_compliance_metric(self,
                                     application_id: str,
                                     metric_id: str,
                                     value: float,
                                     metadata: Optional[Dict[str, Any]] = None) -> None:
        """Update a compliance metric for an application"""
        try:
            if application_id not in self.compliance_data:
                self.compliance_data[application_id] = {
                    'compliance_score': 1.0,
                    'violations': [],
                    'metrics': {},
                    'last_update': time.time(),
                    'frameworks': {}
                }
            
            # Update metric
            self.compliance_data[application_id]['metrics'][metric_id] = {
                'value': value,
                'timestamp': time.time(),
                'metadata': metadata or {}
            }
            
            # Check for alerts
            await self._check_metric_alerts(application_id, metric_id, value)
            
            # Update compliance score
            await self._update_compliance_score(application_id)
            
            self.compliance_data[application_id]['last_update'] = time.time()
            
        except Exception as e:
            self.logger.error(f"Failed to update metric {metric_id} for {application_id}: {str(e)}")
    
    async def _collect_metrics(self, monitor_id: str, application_id: str) -> None:
        """Background task to collect compliance metrics"""
        try:
            monitor_config = self.active_monitors[monitor_id]['config']
            collection_interval = monitor_config.get('collection_interval', 300)  # 5 minutes
            
            while True:
                try:
                    # Collect metrics based on configuration
                    metrics_to_collect = monitor_config.get('metrics', [])
                    
                    for metric_id in metrics_to_collect:
                        if metric_id in self.compliance_metrics:
                            metric = self.compliance_metrics[metric_id]
                            value = await self._collect_metric_value(application_id, metric)
                            
                            await self.update_compliance_metric(application_id, metric_id, value)
                    
                    await asyncio.sleep(collection_interval)
                    
                except Exception as e:
                    self.logger.error(f"Metric collection error for {monitor_id}: {str(e)}")
                    await asyncio.sleep(collection_interval)
                    
        except Exception as e:
            self.logger.error(f"Metric collection failed for monitor {monitor_id}: {str(e)}")
    
    async def _collect_metric_value(self, application_id: str, metric: ComplianceMetric) -> float:
        """Collect value for a specific metric"""
        # In production, this would integrate with actual monitoring systems
        # For now, return simulated values based on metric type
        
        import random
        
        if metric.metric_type == "counter":
            return random.uniform(0, 100)
        elif metric.metric_type == "gauge":
            return random.uniform(0, 1)
        elif metric.metric_type == "histogram":
            return random.uniform(0, 100)
        else:
            return random.uniform(0, 100)
    
    async def _check_metric_alerts(self, application_id: str, metric_id: str, value: float) -> None:
        """Check if metric value triggers alerts"""
        try:
            if metric_id not in self.compliance_metrics:
                return
            
            metric = self.compliance_metrics[metric_id]
            
            # Evaluate metric status
            status = metric.evaluate_status(value)
            
            # Create alert if status is critical or warning
            if status in ['critical', 'warning']:
                alert = ComplianceAlert(
                    alert_id=f"alert_{metric_id}_{application_id}_{int(time.time())}",
                    timestamp=str(time.time()),
                    severity=AlertSeverity.CRITICAL if status == 'critical' else AlertSeverity.HIGH,
                    title=f"{metric.name} Alert",
                    description=f"{metric.name} is {status}: {value} (threshold: {getattr(metric, f'{status}_threshold', 'N/A')})",
                    metric_id=metric_id,
                    application_id=application_id,
                    current_value=value,
                    threshold_value=getattr(metric, f'{status}_threshold', None)
                )
                
                # Add to history
                self.alert_history.append(alert)
                
                # Process alert through handlers
                await self._process_alert(alert)
                
        except Exception as e:
            self.logger.error(f"Failed to check metric alerts: {str(e)}")
    
    async def _process_alert(self, alert: ComplianceAlert) -> None:
        """Process compliance alert"""
        try:
            # Check if alert already exists (avoid duplicates)
            existing_alert = next(
                (a for a in self.alert_history 
                 if a.alert_id == alert.alert_id and a.timestamp == alert.timestamp),
                None
            )
            
            if existing_alert:
                return  # Skip duplicate
            
            # Call alert handlers
            for handler_name, handler_func in self.alert_handlers.items():
                try:
                    await handler_func(alert)
                except Exception as e:
                    self.logger.error(f"Alert handler {handler_name} failed: {str(e)}")
            
            # Log alert
            self.logger.warning(f"Compliance alert: {alert.title} - {alert.description}")
            
        except Exception as e:
            self.logger.error(f"Failed to process alert: {str(e)}")
    
    async def _update_compliance_score(self, application_id: str) -> None:
        """Update compliance score for an application"""
        try:
            app_data = self.compliance_data[application_id]
            
            # Get violations count
            violations_count = len(app_data['violations'])
            
            # Calculate score based on violations and active alerts
            active_alerts = [
                alert for alert in self.alert_history
                if alert.application_id == application_id and not alert.resolved
            ]
            
            # Base score calculation
            base_score = 1.0
            violation_penalty = violations_count * 0.1
            alert_penalty = len(active_alerts) * 0.05
            
            final_score = max(0.0, base_score - violation_penalty - alert_penalty)
            
            # Update application data
            app_data['compliance_score'] = final_score
            
            # Update frameworks status
            frameworks = {}
            for framework in ['GDPR', 'SOX', 'HIPAA', 'PCI_DSS', 'GENERAL']:
                framework_violations = [
                    v for v in app_data['violations'] 
                    if framework in v.get('frameworks', [])
                ]
                frameworks[framework] = {
                    'compliance_score': max(0.0, 1.0 - len(framework_violations) * 0.2),
                    'violations_count': len(framework_violations),
                    'status': 'compliant' if len(framework_violations) == 0 else 'non_compliant'
                }
            
            app_data['frameworks'] = frameworks
            
        except Exception as e:
            self.logger.error(f"Failed to update compliance score for {application_id}: {str(e)}")
    
    async def _calculate_dashboard_data(self, timeframe: str) -> ComplianceDashboard:
        """Calculate dashboard data for specified timeframe"""
        try:
            current_time = time.time()
            
            # Calculate timeframe
            timeframe_seconds = {
                '5m': 300,
                '1h': 3600,
                '1d': 86400,
                '1w': 604800
            }.get(timeframe, 3600)
            
            cutoff_time = current_time - timeframe_seconds
            
            # Filter data by timeframe
            filtered_alerts = [
                alert for alert in self.alert_history
                if float(alert.timestamp) >= cutoff_time
            ]
            
            # Calculate overall metrics
            total_applications = len(self.compliance_data)
            compliant_applications = len([
                app_id for app_id, data in self.compliance_data.items()
                if data['compliance_score'] >= 0.8
            ])
            
            violations_count = len([
                violation for app_data in self.compliance_data.values()
                for violation in app_data['violations']
            ])
            
            active_alerts = len([alert for alert in filtered_alerts if not alert.resolved])
            
            # Calculate overall score
            if total_applications > 0:
                overall_score = sum(
                    data['compliance_score'] for data in self.compliance_data.values()
                ) / total_applications
            else:
                overall_score = 1.0
            
            # Get frameworks status
            frameworks_status = {}
            for framework in ['GDPR', 'SOX', 'HIPAA', 'PCI_DSS', 'GENERAL']:
                framework_apps = [
                    (app_id, data) for app_id, data in self.compliance_data.items()
                    if framework in data.get('frameworks', {})
                ]
                
                if framework_apps:
                    framework_score = sum(
                        data['frameworks'][framework]['compliance_score']
                        for _, data in framework_apps
                    ) / len(framework_apps)
                else:
                    framework_score = 1.0
                
                frameworks_status[framework] = {
                    'compliance_score': framework_score,
                    'applications_count': len(framework_apps),
                    'status': 'compliant' if framework_score >= 0.8 else 'non_compliant'
                }
            
            # Get top violations
            top_violations = []
            for app_id, app_data in self.compliance_data.items():
                for violation in app_data['violations'][-5:]:  # Last 5 violations
                    top_violations.append({
                        'application_id': app_id,
                        'violation': violation,
                        'timestamp': violation.get('timestamp', 'unknown')
                    })
            
            # Sort by timestamp and limit
            top_violations.sort(key=lambda x: x['timestamp'], reverse=True)
            top_violations = top_violations[:10]
            
            # Get recent alerts
            recent_alerts = sorted(
                filtered_alerts,
                key=lambda x: float(x.timestamp),
                reverse=True
            )[:5]
            
            return ComplianceDashboard(
                timestamp=str(current_time),
                overall_score=overall_score,
                total_applications=total_applications,
                compliant_applications=compliant_applications,
                violations_count=violations_count,
                active_alerts=active_alerts,
                frameworks_status=frameworks_status,
                top_violations=top_violations,
                recent_alerts=recent_alerts
            )
            
        except Exception as e:
            self.logger.error(f"Failed to calculate dashboard data: {str(e)}")
            raise
    
    async def _start_monitoring(self) -> None:
        """Start background monitoring tasks"""
        if not self.monitoring_active:
            self.monitoring_active = True
            
            # Start dashboard updater
            asyncio.create_task(self._dashboard_updater())
            
            # Start alert cleanup
            asyncio.create_task(self._alert_cleanup())
            
            self.logger.info("Background monitoring tasks started")
    
    async def _dashboard_updater(self) -> None:
        """Background task to update dashboard cache"""
        while self.monitoring_active:
            try:
                # Update dashboard for each timeframe
                for timeframe in ['5m', '1h', '1d', '1w']:
                    await self.get_compliance_dashboard(timeframe)
                
                await asyncio.sleep(300)  # Update every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Dashboard updater error: {str(e)}")
                await asyncio.sleep(300)
    
    async def _alert_cleanup(self) -> None:
        """Background task to cleanup old alerts"""
        while self.monitoring_active:
            try:
                current_time = time.time()
                retention_period = 7 * 24 * 3600  # 7 days
                
                # Remove old alerts
                self.alert_history = [
                    alert for alert in self.alert_history
                    if current_time - float(alert.timestamp) <= retention_period
                ]
                
                await asyncio.sleep(3600)  # Cleanup every hour
                
            except Exception as e:
                self.logger.error(f"Alert cleanup error: {str(e)}")
                await asyncio.sleep(3600)
    
    async def _load_compliance_metrics(self) -> None:
        """Load compliance metrics definitions"""
        metrics = [
            ComplianceMetric(
                metric_id="compliance_score",
                name="Overall Compliance Score",
                description="Overall compliance score for application",
                metric_type="gauge",
                compliance_framework="GENERAL",
                measurement_unit="score",
                normal_range=(0.8, 1.0),
                critical_threshold=0.5,
                warning_threshold=0.7
            ),
            ComplianceMetric(
                metric_id="gdpr_violations",
                name="GDPR Violations Count",
                description="Number of GDPR compliance violations",
                metric_type="counter",
                compliance_framework="GDPR",
                measurement_unit="count",
                warning_threshold=1.0,
                critical_threshold=3.0
            ),
            ComplianceMetric(
                metric_id="sox_violations",
                name="SOX Violations Count",
                description="Number of SOX compliance violations",
                metric_type="counter",
                compliance_framework="SOX",
                measurement_unit="count",
                warning_threshold=1.0,
                critical_threshold=2.0
            ),
            ComplianceMetric(
                metric_id="security_violations",
                name="Security Violations Count",
                description="Number of security-related violations",
                metric_type="counter",
                compliance_framework="GENERAL",
                measurement_unit="count",
                warning_threshold=2.0,
                critical_threshold=5.0
            ),
            ComplianceMetric(
                metric_id="active_alerts",
                name="Active Compliance Alerts",
                description="Number of active compliance alerts",
                metric_type="counter",
                compliance_framework="GENERAL",
                measurement_unit="count",
                warning_threshold=1.0,
                critical_threshold=3.0
            )
        ]
        
        for metric in metrics:
            self.compliance_metrics[metric.metric_id] = metric
        
        self.logger.info("Loaded %d compliance metrics", len(metrics))
    
    async def _initialize_alert_handlers(self) -> None:
        """Initialize alert handlers"""
        # Add default alert handlers
        self.alert_handlers['email'] = self._send_email_alert
        self.alert_handlers['webhook'] = self._send_webhook_alert
        self.alert_handlers['log'] = self._log_alert
        
        self.logger.info("Initialized %d alert handlers", len(self.alert_handlers))
    
    async def _send_email_alert(self, alert: ComplianceAlert) -> None:
        """Send email alert"""
        try:
            # In production, this would integrate with email system
            self.logger.info(f"Email alert sent: {alert.title}")
        except Exception as e:
            self.logger.error(f"Failed to send email alert: {str(e)}")
    
    async def _send_webhook_alert(self, alert: ComplianceAlert) -> None:
        """Send webhook alert"""
        try:
            # In production, this would send HTTP webhook
            self.logger.info(f"Webhook alert sent: {alert.title}")
        except Exception as e:
            self.logger.error(f"Failed to send webhook alert: {str(e)}")
    
    async def _log_alert(self, alert: ComplianceAlert) -> None:
        """Log alert to system logs"""
        try:
            log_level = {
                AlertSeverity.CRITICAL: "CRITICAL",
                AlertSeverity.HIGH: "WARNING",
                AlertSeverity.MEDIUM: "INFO",
                AlertSeverity.LOW: "INFO"
            }.get(alert.severity, "INFO")
            
            log_message = f"[{log_level}] Compliance Alert: {alert.title} - {alert.description}"
            
            if alert.severity == AlertSeverity.CRITICAL:
                self.logger.critical(log_message)
            elif alert.severity == AlertSeverity.HIGH:
                self.logger.warning(log_message)
            else:
                self.logger.info(log_message)
                
        except Exception as e:
            self.logger.error(f"Failed to log alert: {str(e)}")
    
    async def shutdown(self) -> None:
        """Shutdown the compliance monitor"""
        self.logger.info("Shutting down Compliance Monitor")
        
        # Stop monitoring
        self.monitoring_active = False
        
        # Deactivate all monitors
        for monitor_id in self.active_monitors:
            self.active_monitors[monitor_id]['status'] = MonitorStatus.INACTIVE
        self.active_monitors.clear()
        
        # Clear caches
        self.dashboard_cache.clear()
        self.compliance_data.clear()
        self.alert_history.clear()