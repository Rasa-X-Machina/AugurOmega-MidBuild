"""
Alert Manager - Intelligent alerting system for performance optimization
Provides real-time alerts with smart escalation and auto-resolution
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from collections import defaultdict, deque
import json
from enum import Enum
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import threading
from concurrent.futures import ThreadPoolExecutor

class AlertSeverity(Enum):
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"
    RESOLVED = "resolved"

class AlertStatus(Enum):
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"

@dataclass
class Alert:
    """Individual alert data structure"""
    id: str
    source: str  # agent_id or system
    alert_type: str
    message: str
    severity: AlertSeverity
    status: AlertStatus = AlertStatus.ACTIVE
    
    # Alert metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    
    # Context data
    context: Dict[str, Any] = field(default_factory=dict)
    metrics_snapshot: Dict[str, Any] = field(default_factory=dict)
    
    # Escalation tracking
    escalation_count: int = 0
    escalation_threshold: int = 3
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'source': self.source,
            'alert_type': self.alert_type,
            'message': self.message,
            'severity': self.severity.value,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'acknowledged_at': self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'context': self.context,
            'metrics_snapshot': self.metrics_snapshot,
            'escalation_count': self.escalation_count
        }

class AlertManager:
    """
    Intelligent Alert Manager for distributed performance monitoring
    Features:
    - Smart alert correlation
    - Auto-escalation
    - Alert fatigue prevention
    - Multi-channel notifications
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or self._default_config()
        self.logger = logging.getLogger(__name__)
        
        # Alert storage and indexing
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.alert_patterns: Dict[str, List[str]] = defaultdict(list)
        
        # Notification channels
        self.notification_channels: Dict[str, Callable] = {}
        self.escalation_policies: Dict[str, Dict] = {}
        
        # Alert suppression
        self.suppressed_alerts: Dict[str, datetime] = {}
        self.alert_cooldowns: Dict[str, datetime] = {}
        
        # Threading
        self.alert_processor_active = False
        self.processor_thread: Optional[threading.Thread] = None
        self.executor = ThreadPoolExecutor(max_workers=3)
        
        # Performance tracking
        self.alerts_sent = 0
        self.alerts_resolved = 0
        self.false_positives = 0
        
        self.logger.info("Alert Manager initialized")
    
    def _default_config(self) -> Dict:
        """Default configuration for alert manager"""
        return {
            'cooldown_periods': {
                'critical': 300,  # 5 minutes
                'warning': 600,   # 10 minutes
                'info': 1800      # 30 minutes
            },
            'escalation_intervals': {
                'critical': 900,  # 15 minutes
                'warning': 1800,  # 30 minutes
                'info': 3600      # 1 hour
            },
            'max_escalations': 5,
            'enable_auto_resolution': True,
            'enable_alert_correlation': True,
            'enable_smart_suppression': True,
            'channels': {
                'console': True,
                'email': False,
                'webhook': False
            }
        }
    
    async def start_manager(self):
        """Start the alert manager"""
        if self.alert_processor_active:
            self.logger.warning("Alert manager already running")
            return
        
        self.alert_processor_active = True
        
        # Start processing thread
        self.processor_thread = threading.Thread(target=self._alert_processing_loop, daemon=True)
        self.processor_thread.start()
        
        # Initialize notification channels
        self._initialize_notification_channels()
        
        self.logger.info("🚨 Alert Manager started")
    
    async def stop_manager(self):
        """Stop the alert manager"""
        self.alert_processor_active = False
        
        if self.processor_thread:
            self.processor_thread.join(timeout=5)
        
        self.executor.shutdown(wait=True)
        
        self.logger.info("Alert Manager stopped")
    
    def _initialize_notification_channels(self):
        """Initialize notification channels"""
        # Console notifications (always enabled)
        self.add_notification_channel('console', self._send_console_notification)
        
        # Email notifications (if configured)
        if self.config.get('channels', {}).get('email', False):
            self.add_notification_channel('email', self._send_email_notification)
        
        # Webhook notifications (if configured)
        if self.config.get('channels', {}).get('webhook', False):
            self.add_notification_channel('webhook', self._send_webhook_notification)
    
    def add_notification_channel(self, name: str, handler: Callable):
        """Add a notification channel"""
        self.notification_channels[name] = handler
        self.logger.info(f"Added notification channel: {name}")
    
    def send_alert(self, source: str, alert_type: str, message: str, 
                   severity: AlertSeverity = AlertSeverity.WARNING,
                   context: Dict = None, metrics_snapshot: Dict = None):
        """Send a new alert"""
        # Check for alert suppression
        alert_key = f"{source}:{alert_type}"
        if self._is_alert_suppressed(alert_key, severity):
            self.logger.debug(f"Alert suppressed: {alert_key}")
            return
        
        # Create alert
        alert_id = f"{alert_key}:{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        alert = Alert(
            id=alert_id,
            source=source,
            alert_type=alert_type,
            message=message,
            severity=severity,
            context=context or {},
            metrics_snapshot=metrics_snapshot or {}
        )
        
        # Store alert
        self.active_alerts[alert_id] = alert
        self.alert_history[alert_key].append(alert)
        
        # Update alert patterns for correlation
        self._update_alert_patterns(alert_key, message)
        
        # Send notifications
        self.executor.submit(self._send_notifications, alert)
        
        # Set cooldown
        self._set_alert_cooldown(alert_key, severity)
        
        self.alerts_sent += 1
        self.logger.info(f"🚨 Alert sent: [{severity.value.upper()}] {source} - {message}")
    
    def _is_alert_suppressed(self, alert_key: str, severity: AlertSeverity) -> bool:
        """Check if alert should be suppressed"""
        current_time = datetime.now()
        
        # Check global suppression
        if alert_key in self.suppressed_alerts:
            suppress_until = self.suppressed_alerts[alert_key]
            if current_time < suppress_until:
                return True
            else:
                del self.suppressed_alerts[alert_key]
        
        # Check cooldown
        if alert_key in self.alert_cooldowns:
            cooldown_until = self.alert_cooldowns[alert_key]
            if current_time < cooldown_until:
                return True
        
        # Smart suppression based on alert patterns
        if self.config.get('enable_smart_suppression', False):
            if self._should_suppress_based_on_patterns(alert_key):
                # Suppress for 5 minutes
                self.suppressed_alerts[alert_key] = current_time + timedelta(minutes=5)
                return True
        
        return False
    
    def _should_suppress_based_on_patterns(self, alert_key: str) -> bool:
        """Determine if alert should be suppressed based on patterns"""
        recent_cutoff = datetime.now() - timedelta(minutes=10)
        recent_alerts = [
            alert for alert in self.alert_history[alert_key]
            if alert.created_at > recent_cutoff
        ]
        
        # If we have too many similar alerts in a short time, suppress
        return len(recent_alerts) > 5
    
    def _set_alert_cooldown(self, alert_key: str, severity: AlertSeverity):
        """Set cooldown period for alert"""
        cooldown_seconds = self.config['cooldown_periods'][severity.value]
        self.alert_cooldowns[alert_key] = datetime.now() + timedelta(seconds=cooldown_seconds)
    
    def _update_alert_patterns(self, alert_key: str, message: str):
        """Update alert patterns for correlation analysis"""
        # Simple pattern extraction - look for common phrases
        words = message.lower().split()
        for word in words:
            if len(word) > 3:  # Only consider words longer than 3 characters
                self.alert_patterns[word].append(alert_key)
        
        # Clean up old patterns
        current_time = datetime.now()
        for pattern in list(self.alert_patterns.keys()):
            if current_time - datetime.now() > timedelta(hours=1):
                # Remove patterns older than 1 hour
                self.alert_patterns[pattern] = [
                    alert for alert in self.alert_patterns[pattern]
                    if datetime.now() - current_time < timedelta(hours=1)
                ]
    
    def _send_notifications(self, alert: Alert):
        """Send notifications through all configured channels"""
        for channel_name, handler in self.notification_channels.items():
            try:
                handler(alert)
            except Exception as e:
                self.logger.error(f"Failed to send notification via {channel_name}: {e}")
    
    def _send_console_notification(self, alert: Alert):
        """Send notification to console"""
        severity_icons = {
            AlertSeverity.CRITICAL: "🔥",
            AlertSeverity.WARNING: "⚠️",
            AlertSeverity.INFO: "ℹ️",
            AlertSeverity.RESOLVED: "✅"
        }
        
        icon = severity_icons.get(alert.severity, "📢")
        timestamp = alert.created_at.strftime("%Y-%m-%d %H:%M:%S")
        
        message = f"{icon} [{alert.severity.value.upper()}] {timestamp} | {alert.source} | {alert.alert_type} | {alert.message}"
        
        # Log based on severity
        if alert.severity == AlertSeverity.CRITICAL:
            self.logger.critical(message)
        elif alert.severity == AlertSeverity.WARNING:
            self.logger.warning(message)
        else:
            self.logger.info(message)
    
    def _send_email_notification(self, alert: Alert):
        """Send notification via email (placeholder implementation)"""
        # This would require SMTP configuration
        # For now, just log the intent
        self.logger.info(f"Email notification would be sent for alert: {alert.id}")
    
    def _send_webhook_notification(self, alert: Alert):
        """Send notification via webhook (placeholder implementation)"""
        # This would require webhook URL configuration
        # For now, just log the intent
        self.logger.info(f"Webhook notification would be sent for alert: {alert.id}")
    
    def _alert_processing_loop(self):
        """Main processing loop for alert management"""
        while self.alert_processor_active:
            try:
                current_time = datetime.now()
                
                # Check for escalation
                self._check_escalations(current_time)
                
                # Check for auto-resolution
                if self.config.get('enable_auto_resolution', False):
                    self._check_auto_resolution(current_time)
                
                # Clean up old alerts
                self._cleanup_old_alerts(current_time)
                
                # Process alert patterns
                self._analyze_alert_patterns()
                
                # Sleep for a short period
                import time
                time.sleep(30)  # Process every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Error in alert processing loop: {e}")
                import time
                time.sleep(10)
    
    def _check_escalations(self, current_time: datetime):
        """Check for alerts that need escalation"""
        escalation_interval = self.config['escalation_intervals']
        
        for alert_id, alert in list(self.active_alerts.items()):
            if alert.status != AlertStatus.ACTIVE:
                continue
            
            # Check if escalation is needed
            time_since_creation = current_time - alert.created_at
            escalation_interval_seconds = escalation_interval[alert.severity.value]
            
            if time_since_creation.total_seconds() > escalation_interval_seconds * (alert.escalation_count + 1):
                alert.escalation_count += 1
                alert.updated_at = current_time
                
                # Escalate alert
                escalation_message = f"ESCALATION #{alert.escalation_count}: {alert.message}"
                self.send_alert(
                    source=alert.source,
                    alert_type=f"{alert.alert_type}_escalated",
                    message=escalation_message,
                    severity=AlertSeverity.CRITICAL,
                    context=alert.context
                )
                
                self.logger.warning(f"Escalated alert {alert_id} (#{alert.escalation_count})")
    
    def _check_auto_resolution(self, current_time: datetime):
        """Check for alerts that can be automatically resolved"""
        resolution_threshold_minutes = {
            AlertSeverity.CRITICAL: 10,
            AlertSeverity.WARNING: 30,
            AlertSeverity.INFO: 60
        }
        
        for alert_id, alert in list(self.active_alerts.items()):
            if alert.status != AlertStatus.ACTIVE:
                continue
            
            # Check if enough time has passed for potential resolution
            time_since_creation = current_time - alert.created_at
            resolution_threshold = resolution_threshold_minutes[alert.severity.value]
            
            if time_since_creation.total_seconds() > resolution_threshold * 60:
                # Try to resolve the alert (in a real system, this would check actual metrics)
                self.resolve_alert(alert_id, auto_resolved=True)
    
    def resolve_alert(self, alert_id: str, auto_resolved: bool = False):
        """Resolve an active alert"""
        if alert_id not in self.active_alerts:
            self.logger.warning(f"Alert {alert_id} not found for resolution")
            return
        
        alert = self.active_alerts[alert_id]
        alert.status = AlertStatus.RESOLVED
        alert.resolved_at = datetime.now()
        alert.updated_at = datetime.now()
        
        self.alerts_resolved += 1
        
        resolution_type = "auto" if auto_resolved else "manual"
        self.logger.info(f"Alert {alert_id} resolved ({resolution_type})")
        
        # Send resolution notification
        self.send_alert(
            source=alert.source,
            alert_type=f"{alert.alert_type}_resolved",
            message=f"Alert resolved: {alert.message}",
            severity=AlertSeverity.RESOLVED,
            context={'original_alert_id': alert_id, 'auto_resolved': auto_resolved}
        )
    
    def _cleanup_old_alerts(self, current_time: datetime):
        """Clean up old resolved alerts"""
        retention_days = 7
        cutoff_time = current_time - timedelta(days=retention_days)
        
        # Clean up active alerts (should not normally be needed)
        for alert_id, alert in list(self.active_alerts.items()):
            if alert.created_at < cutoff_time:
                self.logger.warning(f"Removing old active alert: {alert_id}")
                del self.active_alerts[alert_id]
    
    def _analyze_alert_patterns(self):
        """Analyze alert patterns for insights"""
        if not self.config.get('enable_alert_correlation', False):
            return
        
        # Find frequently occurring alert patterns
        pattern_counts = {}
        for pattern, alerts in self.alert_patterns.items():
            if len(alerts) > 3:  # Only consider patterns with multiple occurrences
                pattern_counts[pattern] = len(set(alerts))  # Count unique alert types
        
        if pattern_counts:
            # Log top patterns
            top_patterns = sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            self.logger.info(f"Top alert patterns: {top_patterns}")
    
    def get_alert_summary(self) -> Dict:
        """Get comprehensive alert summary"""
        active_alerts = list(self.active_alerts.values())
        total_alerts = sum(len(deque_obj) for deque_obj in self.alert_history.values())
        
        # Categorize active alerts by severity
        severity_counts = defaultdict(int)
        for alert in active_alerts:
            severity_counts[alert.severity.value] += 1
        
        # Calculate alert metrics
        uptime = datetime.now() - datetime.now()  # Would need start time tracking
        
        return {
            "timestamp": datetime.now().isoformat(),
            "active_alerts": len(active_alerts),
            "total_alerts_sent": self.alerts_sent,
            "total_alerts_resolved": self.alerts_resolved,
            "resolution_rate": self.alerts_resolved / self.alerts_sent if self.alerts_sent > 0 else 0,
            "severity_breakdown": dict(severity_counts),
            "alert_patterns": len(self.alert_patterns),
            "suppressed_alerts": len(self.suppressed_alerts)
        }
    
    def export_alerts(self, output_path: str, limit: int = 1000):
        """Export alert history to file"""
        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "summary": self.get_alert_summary(),
            "active_alerts": {},
            "alert_history": {}
        }
        
        # Export active alerts
        for alert_id, alert in self.active_alerts.items():
            export_data["active_alerts"][alert_id] = alert.to_dict()
        
        # Export recent alert history
        for alert_key, alerts_deque in self.alert_history.items():
            recent_alerts = list(alerts_deque)[-limit:]
            export_data["alert_history"][alert_key] = [
                alert.to_dict() for alert in recent_alerts
            ]
        
        # Convert timestamps to ISO format
        for alert_id in export_data["active_alerts"]:
            alert = export_data["active_alerts"][alert_id]
            alert['created_at'] = alert['created_at']
            alert['updated_at'] = alert['updated_at']
        
        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        self.logger.info(f"Alerts exported to {output_path}")
