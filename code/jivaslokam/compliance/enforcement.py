"""
Compliance Enforcer for Jivaslokam

Provides real-time compliance enforcement and automated remediation
for enterprise deployment scenarios.

Enforces compliance policies through automated blocking, alerting,
and remediation actions based on violation severity and compliance frameworks.
"""

import asyncio
import json
import logging
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum

from .validator import ComplianceValidator, ComplianceViolation, ValidationMode

logger = logging.getLogger(__name__)


class EnforcementAction(Enum):
    """Types of enforcement actions"""
    BLOCK_DEPLOYMENT = "block_deployment"
    ALERT_ADMIN = "alert_admin"
    LOG_VIOLATION = "log_violation"
    QUARANTINE = "quarantine"
    REMEDIATE_AUTOMATICALLY = "remediate_automatically"
    ESCALATE = "escalate"
    APPROVE = "approve"


class EnforcementLevel(Enum):
    """Enforcement levels"""
    HARD = "hard"  # Block execution
    SOFT = "soft"  # Warn but allow
    MONITOR = "monitor"  # Log only
    EXEMPT = "exempt"  # No enforcement


@dataclass
class EnforcementPolicy:
    """Compliance enforcement policy"""
    policy_id: str
    name: str
    compliance_framework: str
    violation_types: List[str]
    enforcement_action: EnforcementAction
    enforcement_level: EnforcementLevel
    severity_thresholds: Dict[str, str]  # severity -> enforcement level
    auto_remediation: bool = False
    notification_settings: Dict[str, Any] = field(default_factory=dict)
    escalation_rules: List[Dict[str, Any]] = field(default_factory=list)
    
    def should_enforce(self, violation: ComplianceViolation) -> bool:
        """Check if policy should enforce for given violation"""
        return (
            violation.rule_id in self.violation_types or
            violation.rule_name in self.violation_types or
            violation.category.value in self.violation_types
        )
    
    def get_enforcement_level(self, violation: ComplianceViolation) -> EnforcementLevel:
        """Get enforcement level for violation"""
        return self.severity_thresholds.get(violation.severity, EnforcementLevel.MONITOR)


@dataclass
class EnforcementResult:
    """Result of enforcement action"""
    enforcement_id: str
    timestamp: str
    policy_id: str
    violation_id: str
    action_taken: EnforcementAction
    enforcement_level: EnforcementLevel
    success: bool
    details: str
    auto_remediation_attempted: bool = False
    remediation_result: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            'enforcement_id': self.enforcement_id,
            'timestamp': self.timestamp,
            'policy_id': self.policy_id,
            'violation_id': self.violation_id,
            'action_taken': self.action_taken.value,
            'enforcement_level': self.enforcement_level.value,
            'success': self.success,
            'details': self.details,
            'auto_remediation_attempted': self.auto_remediation_attempted,
            'remediation_result': self.remediation_result
        }


class ComplianceEnforcer:
    """
    Real-time Compliance Enforcer for Jivaslokam
    
    Provides automated enforcement of compliance policies including:
    - Real-time violation detection and enforcement
    - Automated remediation actions
    - Administrative alerting and escalation
    - Compliance policy management
    - Audit trail maintenance
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__ + ".ComplianceEnforcer")
        self.compliance_validator = ComplianceValidator()
        self.enforcement_policies = {}
        self.active_enforcements = {}
        self.compliance_cache = {}
        self.audit_log = []
        self.notification_queue = []
        
        # Notification settings
        self.smtp_config = {
            'server': 'localhost',
            'port': 587,
            'username': None,
            'password': None,
            'from_address': 'compliance@jivaslokam.com'
        }
        
    async def initialize(self) -> None:
        """Initialize the compliance enforcer"""
        self.logger.info("Initializing Compliance Enforcer...")
        
        # Initialize compliance validator
        await self.compliance_validator.initialize()
        
        # Load enforcement policies
        await self._load_enforcement_policies()
        
        # Initialize notification system
        await self._initialize_notification_system()
        
        # Start background processes
        asyncio.create_task(self._notification_processor())
        asyncio.create_task(self._enforcement_monitor())
        
        self.logger.info("Compliance Enforcer initialized successfully")
    
    async def enforce_compliance(self,
                               application_id: str,
                               deployment_config: Dict[str, Any],
                               license_info: Dict[str, Any],
                               validation_mode: ValidationMode = ValidationMode.STRICT) -> Dict[str, Any]:
        """
        Enforce compliance for deployment
        
        Args:
            application_id: Unique application identifier
            deployment_config: Application deployment configuration
            license_info: License information
            validation_mode: Level of validation strictness
            
        Returns:
            Enforcement results with actions taken and compliance status
        """
        try:
            self.logger.info("Starting compliance enforcement for: %s", application_id)
            
            # Perform compliance validation
            compliance_report = await self.compliance_validator.validate_compliance(
                application_id, deployment_config, license_info, validation_mode
            )
            
            # Apply enforcement policies
            enforcement_results = await self._apply_enforcement_policies(
                application_id, compliance_report.violations, deployment_config
            )
            
            # Determine overall compliance status
            deployment_allowed = self._determine_deployment_status(enforcement_results)
            
            # Handle automatic remediation
            if deployment_allowed:
                remediation_results = await self._attempt_automatic_remediation(
                    application_id, compliance_report.violations, deployment_config
                )
                enforcement_results.extend(remediation_results)
            
            # Generate enforcement report
            enforcement_report = {
                'application_id': application_id,
                'deployment_allowed': deployment_allowed,
                'compliance_score': compliance_report.compliance_score,
                'enforcement_results': [r.to_dict() for r in enforcement_results],
                'total_violations': len(compliance_report.violations),
                'enforced_violations': len([r for r in enforcement_results if r.success]),
                'remediated_violations': len([r for r in enforcement_results if r.auto_remediation_attempted]),
                'timestamp': time.time(),
                'recommendations': self._generate_enforcement_recommendations(enforcement_results)
            }
            
            # Log enforcement audit
            await self._log_enforcement_audit('compliance_enforcement', {
                'application_id': application_id,
                'deployment_allowed': deployment_allowed,
                'total_enforcements': len(enforcement_results),
                'success_rate': len([r for r in enforcement_results if r.success]) / len(enforcement_results) if enforcement_results else 1.0
            })
            
            # Process notifications
            await self._process_enforcement_notifications(enforcement_report)
            
            self.logger.info("Compliance enforcement completed for %s (deployment: %s)",
                           application_id, "allowed" if deployment_allowed else "blocked")
            
            return enforcement_report
            
        except Exception as e:
            self.logger.error("Compliance enforcement failed for %s: %s", application_id, str(e))
            return {
                'application_id': application_id,
                'deployment_allowed': False,
                'error': str(e),
                'enforcement_results': [],
                'recommendations': ['Contact system administrator immediately']
            }
    
    async def _apply_enforcement_policies(self,
                                        application_id: str,
                                        violations: List[ComplianceViolation],
                                        deployment_config: Dict[str, Any]) -> List[EnforcementResult]:
        """Apply enforcement policies to violations"""
        enforcement_results = []
        
        for violation in violations:
            # Find applicable policies
            applicable_policies = [
                policy for policy in self.enforcement_policies.values()
                if policy.should_enforce(violation)
            ]
            
            if not applicable_policies:
                # Create default enforcement result
                result = EnforcementResult(
                    enforcement_id=f"enforce_{violation.rule_id}_{int(time.time())}",
                    timestamp=str(time.time()),
                    policy_id="default_policy",
                    violation_id=violation.rule_id,
                    action_taken=EnforcementAction.LOG_VIOLATION,
                    enforcement_level=EnforcementLevel.MONITOR,
                    success=True,
                    details=f"No enforcement policy found for violation {violation.rule_id}"
                )
                enforcement_results.append(result)
                continue
            
            # Apply each applicable policy
            for policy in applicable_policies:
                result = await self._apply_policy(violation, policy, application_id, deployment_config)
                enforcement_results.append(result)
        
        return enforcement_results
    
    async def _apply_policy(self,
                          violation: ComplianceViolation,
                          policy: EnforcementPolicy,
                          application_id: str,
                          deployment_config: Dict[str, Any]) -> EnforcementResult:
        """Apply a specific enforcement policy"""
        
        enforcement_id = f"{policy.policy_id}_{violation.rule_id}_{int(time.time())}"
        enforcement_level = policy.get_enforcement_level(violation)
        
        # Track active enforcement
        self.active_enforcements[enforcement_id] = {
            'policy_id': policy.policy_id,
            'violation_id': violation.rule_id,
            'application_id': application_id,
            'start_time': time.time(),
            'status': 'active'
        }
        
        try:
            if policy.enforcement_action == EnforcementAction.BLOCK_DEPLOYMENT:
                success = await self._block_deployment(application_id, violation)
                details = "Deployment blocked due to compliance violation"
                
            elif policy.enforcement_action == EnforcementAction.ALERT_ADMIN:
                success = await self._alert_administrator(violation, policy.notification_settings)
                details = "Administrator alert sent"
                
            elif policy.enforcement_action == EnforcementAction.LOG_VIOLATION:
                success = await self._log_violation(violation, application_id)
                details = "Violation logged to audit trail"
                
            elif policy.enforcement_action == EnforcementAction.QUARANTINE:
                success = await self._quarantine_application(application_id, violation)
                details = "Application quarantined for compliance review"
                
            elif policy.enforcement_action == EnforcementAction.ESCALATE:
                success = await self._escalate_violation(violation, policy.escalation_rules)
                details = "Violation escalated according to escalation rules"
                
            else:
                success = True
                details = "Policy action completed successfully"
            
            result = EnforcementResult(
                enforcement_id=enforcement_id,
                timestamp=str(time.time()),
                policy_id=policy.policy_id,
                violation_id=violation.rule_id,
                action_taken=policy.enforcement_action,
                enforcement_level=enforcement_level,
                success=success,
                details=details
            )
            
            # Update active enforcement status
            self.active_enforcements[enforcement_id]['status'] = 'completed' if success else 'failed'
            self.active_enforcements[enforcement_id]['end_time'] = time.time()
            
            return result
            
        except Exception as e:
            self.logger.error("Policy enforcement failed: %s", str(e))
            return EnforcementResult(
                enforcement_id=enforcement_id,
                timestamp=str(time.time()),
                policy_id=policy.policy_id,
                violation_id=violation.rule_id,
                action_taken=policy.enforcement_action,
                enforcement_level=enforcement_level,
                success=False,
                details=f"Enforcement failed: {str(e)}"
            )
    
    async def _attempt_automatic_remediation(self,
                                           application_id: str,
                                           violations: List[ComplianceViolation],
                                           deployment_config: Dict[str, Any]) -> List[EnforcementResult]:
        """Attempt automatic remediation for violations"""
        remediation_results = []
        
        for violation in violations:
            # Check if automatic remediation is available
            if not self._can_auto_remediate(violation):
                continue
            
            remediation_id = f"remediate_{violation.rule_id}_{int(time.time())}"
            
            try:
                # Attempt remediation based on violation type
                remediation_success = await self._perform_auto_remediation(
                    violation, deployment_config
                )
                
                if remediation_success:
                    result = EnforcementResult(
                        enforcement_id=remediation_id,
                        timestamp=str(time.time()),
                        policy_id="auto_remediation",
                        violation_id=violation.rule_id,
                        action_taken=EnforcementAction.REMEDIATE_AUTOMATICALLY,
                        enforcement_level=EnforcementLevel.SOFT,
                        success=True,
                        details=f"Automatic remediation successful for {violation.rule_id}",
                        auto_remediation_attempted=True,
                        remediation_result="success"
                    )
                else:
                    result = EnforcementResult(
                        enforcement_id=remediation_id,
                        timestamp=str(time.time()),
                        policy_id="auto_remediation",
                        violation_id=violation.rule_id,
                        action_taken=EnforcementAction.REMEDIATE_AUTOMATICALLY,
                        enforcement_level=EnforcementLevel.SOFT,
                        success=False,
                        details=f"Automatic remediation failed for {violation.rule_id}",
                        auto_remediation_attempted=True,
                        remediation_result="failed"
                    )
                
                remediation_results.append(result)
                
            except Exception as e:
                self.logger.error(f"Auto remediation failed for {violation.rule_id}: {str(e)}")
        
        return remediation_results
    
    def _determine_deployment_status(self, enforcement_results: List[EnforcementResult]) -> bool:
        """Determine if deployment should be allowed based on enforcement results"""
        # Check for hard blocks
        hard_blocks = [
            r for r in enforcement_results
            if r.enforcement_level == EnforcementLevel.HARD and r.success
        ]
        
        if hard_blocks:
            return False
        
        # Check for quarantine
        quarantines = [
            r for r in enforcement_results
            if r.action_taken == EnforcementAction.QUARANTINE and r.success
        ]
        
        if quarantines:
            return False
        
        # Allow deployment if no hard blocks or quarantines
        return True
    
    def _can_auto_remediate(self, violation: ComplianceViolation) -> bool:
        """Check if violation can be automatically remediated"""
        # Define rules that can be automatically remediated
        auto_remediable = [
            'SSL/TLS',
            'encryption',
            'audit_logging',
            'access_controls',
            'password_policy'
        ]
        
        return any(keyword in violation.rule_name.lower() for keyword in auto_remediable)
    
    async def _perform_auto_remediation(self,
                                      violation: ComplianceViolation,
                                      deployment_config: Dict[str, Any]) -> bool:
        """Perform automatic remediation for a violation"""
        try:
            rule_name = violation.rule_name.lower()
            
            if 'ssl' in rule_name or 'tls' in rule_name:
                # Enable SSL/TLS
                if 'security' not in deployment_config:
                    deployment_config['security'] = {}
                deployment_config['security']['ssl_enabled'] = True
                deployment_config['security']['tls_version'] = '1.2'
                return True
            
            elif 'encryption' in rule_name:
                # Enable encryption
                if 'security' not in deployment_config:
                    deployment_config['security'] = {}
                deployment_config['security']['encrypt_at_rest'] = True
                deployment_config['security']['encrypt_in_transit'] = True
                return True
            
            elif 'audit' in rule_name:
                # Enable audit logging
                if 'logging' not in deployment_config:
                    deployment_config['logging'] = {}
                deployment_config['logging']['audit_logging'] = True
                deployment_config['logging']['log_level'] = 'DEBUG'
                return True
            
            elif 'access' in rule_name:
                # Enable access controls
                if 'authentication' not in deployment_config:
                    deployment_config['authentication'] = {}
                deployment_config['authentication']['access_controls'] = True
                deployment_config['authentication']['rbac_enabled'] = True
                return True
            
            elif 'password' in rule_name:
                # Enable password policies
                if 'security' not in deployment_config:
                    deployment_config['security'] = {}
                deployment_config['security']['password_policy'] = {
                    'min_length': 12,
                    'require_uppercase': True,
                    'require_lowercase': True,
                    'require_numbers': True,
                    'require_symbols': True
                }
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Auto remediation failed: {str(e)}")
            return False
    
    async def _block_deployment(self, application_id: str, violation: ComplianceViolation) -> bool:
        """Block deployment due to compliance violation"""
        self.logger.warning("Blocking deployment of %s due to violation: %s",
                          application_id, violation.rule_id)
        
        # In a real implementation, this would integrate with deployment systems
        # to actually block the deployment
        
        return True
    
    async def _alert_administrator(self, violation: ComplianceViolation, notification_config: Dict[str, Any]) -> bool:
        """Send administrator alert for violation"""
        try:
            alert_message = f"""
            Compliance Violation Alert
            
            Violation ID: {violation.rule_id}
            Rule Name: {violation.rule_name}
            Severity: {violation.severity}
            Description: {violation.description}
            Framework: {violation.framework}
            
            Immediate attention required.
            """
            
            # Add to notification queue
            self.notification_queue.append({
                'type': 'compliance_alert',
                'message': alert_message,
                'priority': violation.severity,
                'timestamp': time.time()
            })
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send administrator alert: {str(e)}")
            return False
    
    async def _log_violation(self, violation: ComplianceViolation, application_id: str) -> bool:
        """Log violation to audit trail"""
        try:
            audit_entry = {
                'timestamp': time.time(),
                'event_type': 'compliance_violation',
                'application_id': application_id,
                'violation': violation.to_dict(),
                'action': 'logged'
            }
            self.audit_log.append(audit_entry)
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to log violation: {str(e)}")
            return False
    
    async def _quarantine_application(self, application_id: str, violation: ComplianceViolation) -> bool:
        """Quarantine application for compliance review"""
        self.logger.warning("Quarantining application %s for compliance review", application_id)
        # In a real implementation, this would integrate with application management systems
        return True
    
    async def _escalate_violation(self, violation: ComplianceViolation, escalation_rules: List[Dict[str, Any]]) -> bool:
        """Escalate violation according to escalation rules"""
        try:
            for rule in escalation_rules:
                if rule.get('severity') == violation.severity:
                    # Process escalation rule
                    escalation_type = rule.get('escalation_type', 'notification')
                    recipients = rule.get('recipients', [])
                    
                    if escalation_type == 'notification':
                        # Add to notification queue
                        self.notification_queue.append({
                            'type': 'escalation',
                            'severity': violation.severity,
                            'recipients': recipients,
                            'violation': violation.rule_id,
                            'timestamp': time.time()
                        })
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to escalate violation: {str(e)}")
            return False
    
    def _generate_enforcement_recommendations(self, enforcement_results: List[EnforcementResult]) -> List[str]:
        """Generate recommendations based on enforcement results"""
        recommendations = []
        
        # Analyze success rate
        if enforcement_results:
            success_rate = len([r for r in enforcement_results if r.success]) / len(enforcement_results)
            if success_rate < 0.7:
                recommendations.append("Review enforcement policies - low success rate detected")
        
        # Check for patterns in failures
        failed_enforcements = [r for r in enforcement_results if not r.success]
        if failed_enforcements:
            recommendations.append(f"{len(failed_enforcements)} enforcement actions failed - investigate system issues")
        
        # Check for auto remediation
        auto_remediated = [r for r in enforcement_results if r.auto_remediation_attempted]
        if auto_remediated:
            successful_remediations = [r for r in auto_remediated if r.remediation_result == 'success']
            recommendations.append(f"Auto-remediated {len(successful_remediations)}/{len(auto_remediated)} violations")
        
        return recommendations
    
    async def _process_enforcement_notifications(self, enforcement_report: Dict[str, Any]) -> None:
        """Process notifications from enforcement report"""
        # Check if deployment was blocked
        if not enforcement_report['deployment_allowed']:
            self.notification_queue.append({
                'type': 'deployment_blocked',
                'application_id': enforcement_report['application_id'],
                'total_violations': enforcement_report['total_violations'],
                'timestamp': time.time()
            })
        
        # Add critical alerts
        if enforcement_report['total_violations'] > 10:
            self.notification_queue.append({
                'type': 'high_violation_count',
                'application_id': enforcement_report['application_id'],
                'violation_count': enforcement_report['total_violations'],
                'timestamp': time.time()
            })
    
    async def _notification_processor(self) -> None:
        """Background task to process notifications"""
        while True:
            try:
                if self.notification_queue:
                    notification = self.notification_queue.pop(0)
                    await self._send_notification(notification)
                
                await asyncio.sleep(1)  # Check every second
                
            except Exception as e:
                self.logger.error(f"Notification processor error: {str(e)}")
                await asyncio.sleep(5)
    
    async def _enforcement_monitor(self) -> None:
        """Background task to monitor active enforcements"""
        while True:
            try:
                # Clean up completed enforcements
                current_time = time.time()
                timeout_threshold = 3600  # 1 hour
                
                completed_enforcements = [
                    enforcement_id for enforcement_id, data in self.active_enforcements.items()
                    if data.get('status') == 'completed' and 
                    current_time - data.get('end_time', current_time) > timeout_threshold
                ]
                
                for enforcement_id in completed_enforcements:
                    del self.active_enforcements[enforcement_id]
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                self.logger.error(f"Enforcement monitor error: {str(e)}")
                await asyncio.sleep(60)
    
    async def _send_notification(self, notification: Dict[str, Any]) -> bool:
        """Send notification using configured notification system"""
        try:
            notification_type = notification.get('type')
            
            if notification_type in ['compliance_alert', 'escalation', 'deployment_blocked']:
                return await self._send_email_notification(notification)
            elif notification_type == 'slack':
                return await self._send_slack_notification(notification)
            else:
                self.logger.info(f"Notification queued: {notification_type}")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to send notification: {str(e)}")
            return False
    
    async def _send_email_notification(self, notification: Dict[str, Any]) -> bool:
        """Send email notification"""
        try:
            # In production, this would integrate with actual email system
            self.logger.info(f"Email notification sent: {notification.get('type')}")
            return True
            
        except Exception as e:
            self.logger.error(f"Email notification failed: {str(e)}")
            return False
    
    async def _send_slack_notification(self, notification: Dict[str, Any]) -> bool:
        """Send Slack notification"""
        try:
            # In production, this would integrate with Slack API
            self.logger.info(f"Slack notification sent: {notification.get('type')}")
            return True
            
        except Exception as e:
            self.logger.error(f"Slack notification failed: {str(e)}")
            return False
    
    async def _initialize_notification_system(self) -> None:
        """Initialize notification system"""
        self.logger.info("Initializing notification system")
        # In production, this would load notification configuration
    
    async def _load_enforcement_policies(self) -> None:
        """Load enforcement policies"""
        policies = [
            # GDPR Enforcement Policy
            EnforcementPolicy(
                policy_id="GDPR_ENFORCEMENT",
                name="GDPR Compliance Enforcement",
                compliance_framework="GDPR",
                violation_types=["GDPR", "data_protection", "privacy"],
                enforcement_action=EnforcementAction.BLOCK_DEPLOYMENT,
                enforcement_level=EnforcementLevel.HARD,
                severity_thresholds={
                    "critical": EnforcementLevel.HARD,
                    "high": EnforcementLevel.SOFT,
                    "medium": EnforcementLevel.MONITOR,
                    "low": EnforcementLevel.EXEMPT
                },
                auto_remediation=True
            ),
            
            # SOX Enforcement Policy
            EnforcementPolicy(
                policy_id="SOX_ENFORCEMENT",
                name="SOX Compliance Enforcement",
                compliance_framework="SOX",
                violation_types=["SOX", "financial", "audit"],
                enforcement_action=EnforcementAction.ESCALATE,
                enforcement_level=EnforcementLevel.HARD,
                severity_thresholds={
                    "critical": EnforcementLevel.HARD,
                    "high": EnforcementLevel.SOFT,
                    "medium": EnforcementLevel.MONITOR
                },
                auto_remediation=True
            ),
            
            # General Security Enforcement Policy
            EnforcementPolicy(
                policy_id="SECURITY_ENFORCEMENT",
                name="General Security Enforcement",
                compliance_framework="GENERAL",
                violation_types=["SEC", "security", "encryption"],
                enforcement_action=EnforcementAction.BLOCK_DEPLOYMENT,
                enforcement_level=EnforcementLevel.HARD,
                severity_thresholds={
                    "critical": EnforcementLevel.HARD,
                    "high": EnforcementLevel.SOFT,
                    "medium": EnforcementLevel.MONITOR
                },
                auto_remediation=True
            ),
            
            # Monitoring Policy for Low Severity
            EnforcementPolicy(
                policy_id="MONITORING_POLICY",
                name="Compliance Monitoring",
                compliance_framework="GENERAL",
                violation_types=["*"],
                enforcement_action=EnforcementAction.LOG_VIOLATION,
                enforcement_level=EnforcementLevel.MONITOR,
                severity_thresholds={
                    "low": EnforcementLevel.MONITOR
                }
            )
        ]
        
        for policy in policies:
            self.enforcement_policies[policy.policy_id] = policy
        
        self.logger.info("Loaded %d enforcement policies", len(policies))
    
    async def _log_enforcement_audit(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """Log enforcement audit event"""
        audit_entry = {
            'timestamp': time.time(),
            'event_type': event_type,
            'event_data': event_data
        }
        self.audit_log.append(audit_entry)
        
        # Cleanup old entries (keep last 500)
        if len(self.audit_log) > 500:
            self.audit_log = self.audit_log[-500:]
    
    async def shutdown(self) -> None:
        """Shutdown the compliance enforcer"""
        self.logger.info("Shutting down Compliance Enforcer")
        
        # Clear active enforcements
        self.active_enforcements.clear()
        
        # Clear queues
        self.notification_queue.clear()
        
        # Shutdown compliance validator
        if hasattr(self.compliance_validator, 'shutdown'):
            await self.compliance_validator.shutdown()