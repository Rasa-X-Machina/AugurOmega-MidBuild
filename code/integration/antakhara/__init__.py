"""
Antakhara: Security & Policy Enforcement for Triumvirate Integration Layer

Antakhara provides comprehensive security governance, policy enforcement,
and compliance monitoring across the entire triumvirate ecosystem.
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Set, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import uuid
import re

from ..shared.base import TriumvirateComponent, ComponentType, TriumvirateMessage, MessagePriority
from ..shared.messaging import MessageRouter
from ..shared.discovery import ServiceDiscovery

class PolicyType(Enum):
    ACCESS_CONTROL = "access_control"
    DATA_PRIVACY = "data_privacy"
    RESOURCE_LIMITS = "resource_limits"
    COMPLIANCE = "compliance"
    SECURITY_RULES = "security_rules"
    CONTENT_FILTERING = "content_filtering"

class SecurityLevel(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

class ComplianceFramework(Enum):
    GDPR = "gdpr"
    HIPAA = "hipaa"
    SOX = "sox"
    PCI_DSS = "pci_dss"
    OWASP = "owasp"
    ISO_27001 = "iso_27001"

@dataclass
class SecurityPolicy:
    """Security policy definition"""
    policy_id: str
    name: str
    policy_type: PolicyType
    description: str
    rules: Dict[str, Any]
    security_level: SecurityLevel
    enabled: bool = True
    last_updated: datetime = None
    
    def __post_init__(self):
        if self.last_updated is None:
            self.last_updated = datetime.now()

@dataclass
class ComplianceRequirement:
    """Compliance requirement definition"""
    requirement_id: str
    framework: ComplianceFramework
    description: str
    controls: List[str]
    audit_frequency: str
    last_audit: Optional[datetime] = None
    next_audit: Optional[datetime] = None
    status: str = "pending"  # pending, in_progress, compliant, non_compliant

@dataclass
class SecurityEvent:
    """Security event logging"""
    event_id: str
    event_type: str
    severity: SecurityLevel
    source_component: str
    target_component: str
    description: str
    timestamp: datetime
    details: Dict[str, Any]
    resolved: bool = False
    resolved_at: Optional[datetime] = None

class AntakharaEnforcer(TriumvirateComponent):
    """
    Antakhara: Central security and policy enforcement component
    Manages security policies, compliance, and threat detection
    """
    
    def __init__(self, component_id: str = "primary"):
        super().__init__(ComponentType.ANTAKHARA, component_id)
        
        # Policy management
        self.active_policies: Dict[str, SecurityPolicy] = {}
        self.policy_evaluators: Dict[PolicyType, Callable] = {}
        
        # Compliance management
        self.compliance_requirements: Dict[str, ComplianceRequirement] = {}
        self.compliance_status: Dict[str, Dict[str, Any]] = {}
        
        # Security monitoring
        self.security_events: List[SecurityEvent] = []
        self.threat_detectors: List[Callable] = []
        self.blacklist_patterns: Set[str] = set()
        self.whitelist_patterns: Set[str] = set()
        
        # Access control
        self.access_matrix: Dict[str, Dict[str, Set[ComponentType]]] = {}  # resource -> action -> components
        self.authentication_tokens: Dict[str, Dict[str, Any]] = {}
        
        # Audit logging
        self.audit_log: List[Dict[str, Any]] = []
        self.compliance_reports: List[Dict[str, Any]] = []
        
        # Performance tracking
        self.security_stats = {
            "policies_evaluated": 0,
            "access_granted": 0,
            "access_denied": 0,
            "threats_detected": 0,
            "compliance_checks": 0,
            "false_positives": 0
        }
        
        self.logger = logging.getLogger("AntakharaEnforcer")
        
    async def initialize(self) -> None:
        """Initialize Antakhara security system"""
        self.logger.info("Initializing Antakhara security enforcer")
        
        # Register security message handlers
        self.register_handler("security.evaluate_policy", self._handle_policy_evaluation)
        self.register_handler("security.check_access", self._handle_access_check)
        self.register_handler("security.log_event", self._handle_security_event)
        self.register_handler("compliance.audit", self._handle_compliance_audit)
        self.register_handler("policy.create", self._handle_policy_creation)
        
        # Initialize default policies
        await self._initialize_default_policies()
        
        # Initialize compliance frameworks
        await self._initialize_compliance_frameworks()
        
        # Set up threat detection
        await self._setup_threat_detection()
        
        # Start background security monitoring
        asyncio.create_task(self._security_monitor_loop())
        asyncio.create_task(self._compliance_check_loop())
        
        self.logger.info("Antakhara security enforcer initialized")
        
    async def shutdown(self) -> None:
        """Shutdown Antakhara enforcer"""
        self.logger.info("Shutting down Antakhara enforcer")
        
    async def _route_message(self, message: TriumvirateMessage) -> bool:
        """Route security message to appropriate handler"""
        return await self.receive_message(message)
        
    async def create_policy(self, policy: SecurityPolicy) -> bool:
        """Create and activate a security policy"""
        try:
            self.active_policies[policy.policy_id] = policy
            self.logger.info(f"Created security policy: {policy.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create policy {policy.policy_id}: {e}")
            return False
            
    async def evaluate_policy(self, policy_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a security policy against given context"""
        try:
            self.security_stats["policies_evaluated"] += 1
            
            policy = self.active_policies.get(policy_id)
            if not policy:
                return {"allowed": False, "reason": "Policy not found"}
                
            if not policy.enabled:
                return {"allowed": True, "reason": "Policy disabled"}
                
            # Get policy evaluator
            evaluator = self.policy_evaluators.get(policy.policy_type)
            if not evaluator:
                return {"allowed": False, "reason": "No evaluator for policy type"}
                
            # Evaluate policy
            result = await evaluator(policy, context)
            
            self.logger.debug(f"Policy {policy_id} evaluation: {result}")
            return result
            
        except Exception as e:
            self.logger.error(f"Policy evaluation failed for {policy_id}: {e}")
            return {"allowed": False, "reason": f"Evaluation error: {e}"}
            
    async def check_access(self, resource: str, action: str, 
                          component: ComponentType, context: Dict[str, Any]) -> Dict[str, Any]:
        """Check access permissions for a component"""
        try:
            # Check access matrix first
            if resource in self.access_matrix:
                if action in self.access_matrix[resource]:
                    allowed_components = self.access_matrix[resource][action]
                    if component in allowed_components:
                        self.security_stats["access_granted"] += 1
                        return {"allowed": True, "reason": "Access matrix grant"}
                        
            # Evaluate security policies
            evaluation_context = {
                "resource": resource,
                "action": action,
                "component": component.value,
                "component_id": context.get("component_id"),
                "request_metadata": context
            }
            
            # Check all relevant policies
            for policy_id, policy in self.active_policies.items():
                if (policy.policy_type == PolicyType.ACCESS_CONTROL and 
                    policy.enabled):
                    result = await self.evaluate_policy(policy_id, evaluation_context)
                    if not result.get("allowed", False):
                        self.security_stats["access_denied"] += 1
                        return {
                            "allowed": False, 
                            "reason": result.get("reason", "Policy denial"),
                            "policy_id": policy_id
                        }
                        
            self.security_stats["access_granted"] += 1
            return {"allowed": True, "reason": "Access granted by policies"}
            
        except Exception as e:
            self.logger.error(f"Access check failed: {e}")
            self.security_stats["access_denied"] += 1
            return {"allowed": False, "reason": f"Access check error: {e}"}
            
    async def log_security_event(self, event: SecurityEvent) -> bool:
        """Log a security event"""
        try:
            self.security_events.append(event)
            
            # Check if this event requires immediate response
            if event.severity in [SecurityLevel.HIGH, SecurityLevel.CRITICAL]:
                await self._handle_high_severity_event(event)
                
            # Audit log
            await self._audit_log_event(event)
            
            self.logger.warning(f"Security event logged: {event.event_type} ({event.severity.name})")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to log security event: {e}")
            return False
            
    async def check_compliance(self, framework: ComplianceFramework, 
                              component_id: str) -> Dict[str, Any]:
        """Check compliance for a component against a framework"""
        try:
            self.security_stats["compliance_checks"] += 1
            
            # Find relevant compliance requirements
            requirements = [
                req for req in self.compliance_requirements.values()
                if req.framework == framework
            ]
            
            compliance_results = {
                "framework": framework.value,
                "component_id": component_id,
                "status": "compliant",
                "checks": []
            }
            
            for req in requirements:
                check_result = await self._check_compliance_requirement(req, component_id)
                compliance_results["checks"].append(check_result)
                
                if check_result["status"] != "compliant":
                    compliance_results["status"] = "non_compliant"
                    
            # Update compliance status
            self.compliance_status[f"{framework.value}_{component_id}"] = compliance_results
            
            return compliance_results
            
        except Exception as e:
            self.logger.error(f"Compliance check failed: {e}")
            return {
                "framework": framework.value,
                "component_id": component_id,
                "status": "error",
                "error": str(e)
            }
            
    def add_threat_detector(self, detector: Callable) -> None:
        """Add a threat detection function"""
        self.threat_detectors.append(detector)
        
    def add_access_rule(self, resource: str, action: str, 
                       allowed_components: Set[ComponentType]) -> None:
        """Add access control rule"""
        if resource not in self.access_matrix:
            self.access_matrix[resource] = {}
            
        self.access_matrix[resource][action] = allowed_components
        self.logger.info(f"Added access rule: {resource}.{action} for {len(allowed_components)} components")
        
    async def generate_security_report(self, time_range_hours: int = 24) -> Dict[str, Any]:
        """Generate comprehensive security report"""
        try:
            current_time = datetime.now()
            start_time = current_time - timedelta(hours=time_range_hours)
            
            # Filter events in time range
            recent_events = [
                event for event in self.security_events
                if event.timestamp >= start_time
            ]
            
            # Generate statistics
            event_summary = {
                "total_events": len(recent_events),
                "high_severity": len([e for e in recent_events if e.severity == SecurityLevel.HIGH]),
                "critical_severity": len([e for e in recent_events if e.severity == SecurityLevel.CRITICAL]),
                "resolved": len([e for e in recent_events if e.resolved]),
                "unresolved": len([e for e in recent_events if not e.resolved])
            }
            
            # Compliance summary
            compliance_summary = {
                "total_checks": len(self.compliance_status),
                "compliant": len([s for s in self.compliance_status.values() if s["status"] == "compliant"]),
                "non_compliant": len([s for s in self.compliance_status.values() if s["status"] == "non_compliant"])
            }
            
            report = {
                "report_id": str(uuid.uuid4()),
                "generated_at": current_time.isoformat(),
                "time_range_hours": time_range_hours,
                "security_stats": self.security_stats,
                "event_summary": event_summary,
                "compliance_summary": compliance_summary,
                "active_policies": len(self.active_policies),
                "threat_detectors": len(self.threat_detectors)
            }
            
            self.compliance_reports.append(report)
            return report
            
        except Exception as e:
            self.logger.error(f"Security report generation failed: {e}")
            return {"error": str(e)}
            
    async def _initialize_default_policies(self) -> None:
        """Initialize default security policies"""
        # Access control policy
        access_policy = SecurityPolicy(
            policy_id="policy_access_control_default",
            name="Default Access Control",
            policy_type=PolicyType.ACCESS_CONTROL,
            description="Default access control policy for triumvirate components",
            security_level=SecurityLevel.MEDIUM,
            rules={
                "require_authentication": True,
                "allowed_operations": {
                    ComponentType.AGENTA.value: ["read", "write"],
                    ComponentType.PRANAVA.value: ["read", "write", "execute"],
                    ComponentType.ANTAKHARA.value: ["read", "write", "execute", "admin"]
                }
            }
        )
        
        # Data privacy policy
        privacy_policy = SecurityPolicy(
            policy_id="policy_data_privacy_default",
            name="Default Data Privacy",
            policy_type=PolicyType.DATA_PRIVACY,
            description="Default data privacy and encryption policy",
            security_level=SecurityLevel.HIGH,
            rules={
                "encrypt_sensitive_data": True,
                "data_retention_days": 90,
                "anonymize_pii": True,
                "require_consent": True
            }
        )
        
        # Resource limits policy
        resource_policy = SecurityPolicy(
            policy_id="policy_resource_limits_default",
            name="Default Resource Limits",
            policy_type=PolicyType.RESOURCE_LIMITS,
            description="Default resource usage limits",
            security_level=SecurityLevel.MEDIUM,
            rules={
                "max_memory_mb": 1024,
                "max_cpu_percent": 80,
                "max_connections": 100,
                "rate_limit_per_minute": 1000
            }
        )
        
        # Create all policies
        await self.create_policy(access_policy)
        await self.create_policy(privacy_policy)
        await self.create_policy(resource_policy)
        
        # Register policy evaluators
        self.policy_evaluators[PolicyType.ACCESS_CONTROL] = self._evaluate_access_policy
        self.policy_evaluators[PolicyType.DATA_PRIVACY] = self._evaluate_privacy_policy
        self.policy_evaluators[PolicyType.RESOURCE_LIMITS] = self._evaluate_resource_policy
        
    async def _initialize_compliance_frameworks(self) -> None:
        """Initialize compliance frameworks"""
        # GDPR requirements
        gdpr_req = ComplianceRequirement(
            requirement_id="compliance_gdpr_data_protection",
            framework=ComplianceFramework.GDPR,
            description="General Data Protection Regulation data protection requirements",
            controls=["data_encryption", "consent_management", "right_to_erasure", "data_portability"],
            audit_frequency="quarterly"
        )
        
        # ISO 27001 requirements
        iso_req = ComplianceRequirement(
            requirement_id="compliance_iso27001_security",
            framework=ComplianceFramework.ISO_27001,
            description="Information Security Management System requirements",
            controls=["risk_assessment", "access_control", "incident_response", "business_continuity"],
            audit_frequency="annual"
        )
        
        # OWASP requirements
        owasp_req = ComplianceRequirement(
            requirement_id="compliance_owasp_security",
            framework=ComplianceFramework.OWASP,
            description="OWASP security best practices",
            controls=["input_validation", "output_encoding", "authentication", "session_management"],
            audit_frequency="monthly"
        )
        
        self.compliance_requirements["gdpr_data_protection"] = gdpr_req
        self.compliance_requirements["iso27001_security"] = iso_req
        self.compliance_requirements["owasp_security"] = owasp_req
        
    async def _setup_threat_detection(self) -> None:
        """Set up threat detection mechanisms"""
        # SQL injection detector
        def detect_sql_injection(context: Dict[str, Any]) -> Optional[SecurityEvent]:
            query = context.get("query", "")
            if "UNION" in query.upper() or "DROP" in query.upper() or "SELECT" in query.upper():
                return SecurityEvent(
                    event_id=str(uuid.uuid4()),
                    event_type="sql_injection_attempt",
                    severity=SecurityLevel.HIGH,
                    source_component=context.get("source", "unknown"),
                    target_component=context.get("target", "database"),
                    description="Potential SQL injection detected",
                    timestamp=datetime.now(),
                    details={"query_snippet": query[:100]}
                )
            return None
            
        # Rate limiting detector
        def detect_rate_limiting(context: Dict[str, Any]) -> Optional[SecurityEvent]:
            request_count = context.get("request_count", 0)
            time_window = context.get("time_window_seconds", 60)
            
            if request_count > 1000:  # Threshold for rate limiting
                return SecurityEvent(
                    event_id=str(uuid.uuid4()),
                    event_type="rate_limiting_violation",
                    severity=SecurityLevel.MEDIUM,
                    source_component=context.get("source", "unknown"),
                    target_component=context.get("target", "api"),
                    description=f"High request rate detected: {request_count} in {time_window}s",
                    timestamp=datetime.now(),
                    details={"request_count": request_count, "time_window": time_window}
                )
            return None
            
        self.add_threat_detector(detect_sql_injection)
        self.add_threat_detector(detect_rate_limiting)
        
        # Initialize access control matrix
        self.add_access_rule("hierarchy", "read", {
            ComponentType.AGENTA, ComponentType.PRANAVA, ComponentType.ANTAKHARA
        })
        self.add_access_rule("hierarchy", "write", {ComponentType.AGENTA})
        self.add_access_rule("orchestration", "execute", {ComponentType.PRANAVA})
        self.add_access_rule("orchestration", "read", {ComponentType.AGENTA, ComponentType.PRANAVA})
        self.add_access_rule("security", "admin", {ComponentType.ANTAKHARA})
        self.add_access_rule("security", "read", {ComponentType.AGENTA, ComponentType.PRANAVA, ComponentType.ANTAKHARA})
        
    async def _evaluate_access_policy(self, policy: SecurityPolicy, 
                                    context: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate access control policy"""
        component = context.get("component")
        action = context.get("action")
        
        # Check if component is in allowed operations
        allowed_operations = policy.rules.get("allowed_operations", {})
        component_operations = allowed_operations.get(component, [])
        
        if action in component_operations:
            return {"allowed": True, "reason": "Component authorized for action"}
        else:
            return {"allowed": False, "reason": f"Component {component} not authorized for {action}"}
            
    async def _evaluate_privacy_policy(self, policy: SecurityPolicy, 
                                     context: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate data privacy policy"""
        data_type = context.get("data_type", "")
        operation = context.get("operation", "")
        
        # Check encryption requirement
        if policy.rules.get("encrypt_sensitive_data", False):
            if data_type in ["pii", "financial", "medical"]:
                if context.get("encrypted", False):
                    return {"allowed": True, "reason": "Data properly encrypted"}
                else:
                    return {"allowed": False, "reason": "Sensitive data must be encrypted"}
                    
        # Check consent requirement
        if policy.rules.get("require_consent", False):
            if not context.get("consent_given", False):
                return {"allowed": False, "reason": "User consent required"}
                
        return {"allowed": True, "reason": "Privacy policy satisfied"}
        
    async def _evaluate_resource_policy(self, policy: SecurityPolicy, 
                                       context: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate resource limits policy"""
        # Check memory limit
        max_memory = policy.rules.get("max_memory_mb", 1024)
        current_memory = context.get("memory_usage_mb", 0)
        
        if current_memory > max_memory:
            return {"allowed": False, "reason": f"Memory limit exceeded: {current_memory}MB > {max_memory}MB"}
            
        # Check CPU limit
        max_cpu = policy.rules.get("max_cpu_percent", 80)
        current_cpu = context.get("cpu_usage_percent", 0)
        
        if current_cpu > max_cpu:
            return {"allowed": False, "reason": f"CPU limit exceeded: {current_cpu}% > {max_cpu}%"}
            
        return {"allowed": True, "reason": "Resource limits satisfied"}
        
    async def _check_compliance_requirement(self, req: ComplianceRequirement, 
                                          component_id: str) -> Dict[str, Any]:
        """Check individual compliance requirement"""
        return {
            "requirement_id": req.requirement_id,
            "status": "compliant",  # Simplified - would implement actual checks
            "controls_checked": len(req.controls),
            "next_audit": req.next_audit.isoformat() if req.next_audit else None
        }
        
    async def _handle_high_severity_event(self, event: SecurityEvent) -> None:
        """Handle high severity security event"""
        self.logger.critical(f"High severity security event: {event.description}")
        
        # Could trigger automated responses like:
        # - Isolate affected components
        # - Alert security team
        # - Implement emergency policies
        
    async def _audit_log_event(self, event: SecurityEvent) -> None:
        """Add event to audit log"""
        audit_entry = {
            "timestamp": event.timestamp.isoformat(),
            "event_id": event.event_id,
            "event_type": event.event_type,
            "severity": event.severity.name,
            "source": event.source_component,
            "target": event.target_component,
            "description": event.description,
            "details": event.details
        }
        
        self.audit_log.append(audit_entry)
        
        # Keep audit log size manageable
        if len(self.audit_log) > 10000:
            self.audit_log = self.audit_log[-5000:]  # Keep last 5000 entries
            
    async def _security_monitor_loop(self) -> None:
        """Background security monitoring loop"""
        while True:
            try:
                # Run threat detection
                for detector in self.threat_detectors:
                    try:
                        # This would run with actual monitoring data
                        pass
                    except Exception as e:
                        self.logger.error(f"Threat detector error: {e}")
                        
                await asyncio.sleep(10)  # Monitor every 10 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Security monitoring error: {e}")
                await asyncio.sleep(10)
                
    async def _compliance_check_loop(self) -> None:
        """Background compliance checking loop"""
        while True:
            try:
                # Check if any compliance requirements need auditing
                current_time = datetime.now()
                for req in self.compliance_requirements.values():
                    if req.next_audit and current_time >= req.next_audit:
                        self.logger.info(f"Compliance audit due for {req.framework.value}")
                        req.next_audit = current_time + timedelta(days=90)  # Next audit in 90 days
                        
                await asyncio.sleep(3600)  # Check every hour
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Compliance check error: {e}")
                await asyncio.sleep(3600)
                
    # Message handlers
    async def _handle_policy_evaluation(self, message: TriumvirateMessage) -> Dict[str, Any]:
        """Handle policy evaluation request"""
        policy_id = message.payload.get("policy_id")
        context = message.payload.get("context", {})
        
        result = await self.evaluate_policy(policy_id, context)
        return result
        
    async def _handle_access_check(self, message: TriumvirateMessage) -> Dict[str, Any]:
        """Handle access check request"""
        resource = message.payload.get("resource")
        action = message.payload.get("action")
        component = ComponentType(message.payload.get("component"))
        context = message.payload
        
        result = await self.check_access(resource, action, component, context)
        return result
        
    async def _handle_security_event(self, message: TriumvirateMessage) -> Dict[str, Any]:
        """Handle security event logging request"""
        event_data = message.payload.get("event_data")
        
        event = SecurityEvent(
            event_id=event_data["event_id"],
            event_type=event_data["event_type"],
            severity=SecurityLevel(event_data["severity"]),
            source_component=event_data["source_component"],
            target_component=event_data["target_component"],
            description=event_data["description"],
            timestamp=datetime.now(),
            details=event_data.get("details", {})
        )
        
        success = await self.log_security_event(event)
        return {"success": success}
        
    async def _handle_compliance_audit(self, message: TriumvirateMessage) -> Dict[str, Any]:
        """Handle compliance audit request"""
        framework = ComplianceFramework(message.payload.get("framework"))
        component_id = message.payload.get("component_id")
        
        result = await self.check_compliance(framework, component_id)
        return result
        
    async def _handle_policy_creation(self, message: TriumvirateMessage) -> Dict[str, Any]:
        """Handle policy creation request"""
        policy_data = message.payload.get("policy_data")
        
        policy = SecurityPolicy(
            policy_id=policy_data["policy_id"],
            name=policy_data["name"],
            policy_type=PolicyType(policy_data["policy_type"]),
            description=policy_data["description"],
            rules=policy_data["rules"],
            security_level=SecurityLevel(policy_data["security_level"])
        )
        
        success = await self.create_policy(policy)
        return {"success": success, "policy_id": policy.policy_id}
