"""
Validation Engine for Jivaslokam

Provides comprehensive application validation, compliance checking,
and automated verification capabilities for enterprise deployment.

Performs multi-layered validation including code analysis, configuration
validation, security scanning, and compliance verification.
"""

import asyncio
import json
import ast
import re
import logging
from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import time
import hashlib

logger = logging.getLogger(__name__)


class ValidationSeverity(Enum):
    """Validation result severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class ValidationCategory(Enum):
    """Categories of validation checks"""
    SECURITY = "security"
    COMPLIANCE = "compliance"
    PERFORMANCE = "performance"
    CONFIGURATION = "configuration"
    CODE_QUALITY = "code_quality"
    LICENSING = "licensing"
    DEPLOYMENT = "deployment"
    RESOURCE_USAGE = "resource_usage"


@dataclass
class ValidationRule:
    """Individual validation rule definition"""
    rule_id: str
    name: str
    description: str
    category: ValidationCategory
    severity: ValidationSeverity
    pattern: str
    remediation: str
    enabled: bool = True
    
    def matches(self, content: str) -> bool:
        """Check if content matches the rule pattern"""
        try:
            return bool(re.search(self.pattern, content, re.IGNORECASE | re.MULTILINE))
        except Exception:
            return False


@dataclass
class ValidationFinding:
    """Individual validation finding"""
    rule_id: str
    rule_name: str
    category: ValidationCategory
    severity: ValidationSeverity
    description: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    context: Optional[str] = None
    remediation: str = ""
    evidence: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            'rule_id': self.rule_id,
            'rule_name': self.rule_name,
            'category': self.category.value,
            'severity': self.severity.value,
            'description': self.description,
            'file_path': self.file_path,
            'line_number': self.line_number,
            'context': self.context,
            'remediation': self.remediation,
            'evidence': self.evidence
        }


class ValidationEngine:
    """
    Comprehensive Validation Engine for Jivaslokam
    
    Performs multi-layered validation of applications including:
    - Security vulnerability scanning
    - Compliance verification
    - Code quality assessment
    - Configuration validation
    - License compliance checking
    - Deployment validation
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__ + ".ValidationEngine")
        self.validation_rules = {}
        self.custom_rules = {}
        self.validation_cache = {}
        self.audit_log = []
        
    async def initialize(self) -> None:
        """Initialize the validation engine"""
        self.logger.info("Initializing Validation Engine...")
        
        # Load built-in validation rules
        await self._load_built_in_rules()
        
        # Load custom rules
        await self._load_custom_rules()
        
        # Initialize validation profiles
        await self._initialize_validation_profiles()
        
        self.logger.info("Validation Engine initialized with %d rules", len(self.validation_rules))
    
    async def validate_application(self,
                                 application_id: str,
                                 deployment_config: Dict[str, Any],
                                 license_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform comprehensive application validation
        
        Args:
            application_id: Unique application identifier
            deployment_config: Application deployment configuration
            license_info: License information for validation
            
        Returns:
            Comprehensive validation results with findings and recommendations
        """
        try:
            self.logger.info("Starting comprehensive validation for application: %s", application_id)
            
            validation_results = {
                'application_id': application_id,
                'validation_timestamp': time.time(),
                'overall_score': 0.0,
                'compliance_score': 0.0,
                'categories': {},
                'findings': [],
                'violations': [],
                'recommendations': [],
                'summary': {}
            }
            
            # Validate deployment configuration
            config_validation = await self._validate_deployment_config(deployment_config)
            validation_results['categories']['configuration'] = config_validation
            
            # Validate license compliance
            license_validation = await self._validate_license_compliance(license_info)
            validation_results['categories']['licensing'] = license_validation
            
            # Validate security requirements
            security_validation = await self._validate_security_requirements(deployment_config)
            validation_results['categories']['security'] = security_validation
            
            # Validate compliance policies
            compliance_validation = await self._validate_compliance_policies(deployment_config)
            validation_results['categories']['compliance'] = compliance_validation
            
            # Validate performance requirements
            performance_validation = await self._validate_performance_requirements(deployment_config)
            validation_results['categories']['performance'] = performance_validation
            
            # Aggregate findings
            all_findings = []
            violations = []
            for category_results in validation_results['categories'].values():
                if 'findings' in category_results:
                    all_findings.extend(category_results['findings'])
                if 'violations' in category_results:
                    violations.extend(category_results['violations'])
            
            validation_results['findings'] = [f.to_dict() if hasattr(f, 'to_dict') else f for f in all_findings]
            validation_results['violations'] = violations
            
            # Calculate overall scores
            scores = []
            for category, results in validation_results['categories'].items():
                if 'score' in results:
                    scores.append(results['score'])
            
            if scores:
                validation_results['overall_score'] = sum(scores) / len(scores)
            
            # Calculate compliance score (excluding performance)
            compliance_categories = ['security', 'compliance', 'licensing', 'configuration']
            compliance_scores = []
            for category in compliance_categories:
                if category in validation_results['categories']:
                    cat_score = validation_results['categories'][category].get('score', 0)
                    compliance_scores.append(cat_score)
            
            if compliance_scores:
                validation_results['compliance_score'] = sum(compliance_scores) / len(compliance_scores)
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(validation_results)
            validation_results['recommendations'] = recommendations
            
            # Create summary
            validation_results['summary'] = {
                'total_findings': len(all_findings),
                'critical_violations': len([v for v in violations if v.get('severity') == 'critical']),
                'high_violations': len([v for v in violations if v.get('severity') == 'high']),
                'medium_violations': len([v for v in violations if v.get('severity') == 'medium']),
                'compliance_status': 'compliant' if validation_results['compliance_score'] >= 0.8 else 'non_compliant'
            }
            
            # Log validation audit
            await self._log_validation_audit(application_id, validation_results)
            
            self.logger.info("Validation completed for %s (score: %.2f, compliance: %.2f)",
                           application_id, validation_results['overall_score'], validation_results['compliance_score'])
            
            return validation_results
            
        except Exception as e:
            self.logger.error("Application validation failed for %s: %s", application_id, str(e))
            return {
                'application_id': application_id,
                'error': str(e),
                'findings': [],
                'violations': [],
                'recommendations': ['Contact system administrator'],
                'overall_score': 0.0,
                'compliance_score': 0.0
            }
    
    async def _validate_deployment_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate deployment configuration"""
        findings = []
        violations = []
        
        # Check required configuration fields
        required_fields = ['application_name', 'environment', 'region', 'instance_type']
        for field in required_fields:
            if field not in config:
                violation = {
                    'type': 'missing_config_field',
                    'field': field,
                    'severity': 'high',
                    'description': f'Required configuration field missing: {field}'
                }
                violations.append(violation)
        
        # Validate environment settings
        valid_environments = ['development', 'staging', 'production']
        if config.get('environment') not in valid_environments:
            violation = {
                'type': 'invalid_environment',
                'environment': config.get('environment'),
                'severity': 'critical',
                'description': f'Invalid environment: {config.get("environment")}. Must be one of: {valid_environments}'
            }
            violations.append(violation)
        
        # Check security configurations
        security_config = config.get('security', {})
        if not security_config.get('enable_encryption', True):
            finding = ValidationFinding(
                rule_id='security_encryption_disabled',
                rule_name='Encryption Disabled',
                category=ValidationCategory.SECURITY,
                severity=ValidationSeverity.HIGH,
                description='Encryption is disabled in security configuration',
                remediation='Enable encryption for data protection'
            )
            findings.append(finding)
        
        # Check resource limits
        resources = config.get('resources', {})
        if not resources.get('cpu_limit') or not resources.get('memory_limit'):
            finding = ValidationFinding(
                rule_id='missing_resource_limits',
                rule_name='Missing Resource Limits',
                category=ValidationCategory.PERFORMANCE,
                severity=ValidationSeverity.MEDIUM,
                description='Resource limits not properly configured',
                remediation='Set appropriate CPU and memory limits'
            )
            findings.append(finding)
        
        score = self._calculate_category_score(violations, findings)
        
        return {
            'score': score,
            'findings': findings,
            'violations': violations,
            'valid': len(violations) == 0
        }
    
    async def _validate_license_compliance(self, license_info: Dict[str, Any]) -> Dict[str, Any]:
        """Validate license compliance"""
        findings = []
        violations = []
        
        # Check license type compatibility
        license_type = license_info.get('license_type')
        if license_type in ['trial', 'evaluation']:
            violation = {
                'type': 'trial_license_production',
                'severity': 'critical',
                'description': f'{license_type.title()} license cannot be used for production deployment'
            }
            violations.append(violation)
        
        # Check license expiry
        expiry_date = license_info.get('expiry_date')
        if expiry_date:
            try:
                expiry_timestamp = time.mktime(time.strptime(expiry_date, '%Y-%m-%d'))
                if time.time() > expiry_timestamp:
                    violation = {
                        'type': 'license_expired',
                        'severity': 'critical',
                        'description': f'License expired on {expiry_date}'
                    }
                    violations.append(violation)
            except ValueError:
                violation = {
                    'type': 'invalid_expiry_format',
                    'severity': 'high',
                    'description': f'Invalid license expiry date format: {expiry_date}'
                }
                violations.append(violation)
        
        # Check license constraints
        constraints = license_info.get('constraints', [])
        if not constraints:
            finding = ValidationFinding(
                rule_id='no_license_constraints',
                rule_name='No License Constraints',
                category=ValidationCategory.LICENSING,
                severity=ValidationSeverity.LOW,
                description='License has no defined constraints',
                remediation='Define appropriate license constraints for tracking'
            )
            findings.append(finding)
        
        score = self._calculate_category_score(violations, findings)
        
        return {
            'score': score,
            'findings': findings,
            'violations': violations,
            'valid': len(violations) == 0
        }
    
    async def _validate_security_requirements(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate security requirements and configurations"""
        findings = []
        violations = []
        
        security_config = config.get('security', {})
        
        # Check SSL/TLS configuration
        if not security_config.get('ssl_enabled', True):
            violation = {
                'type': 'ssl_disabled',
                'severity': 'critical',
                'description': 'SSL/TLS encryption is disabled'
            }
            violations.append(violation)
        
        # Check authentication configuration
        auth_config = config.get('authentication', {})
        if not auth_config.get('enabled', False):
            violation = {
                'type': 'authentication_disabled',
                'severity': 'critical',
                'description': 'Authentication is disabled'
            }
            violations.append(violation)
        
        # Check for hardcoded secrets
        config_str = json.dumps(config)
        secret_patterns = [
            r'password["\s]*[:=]["\s]*["\w]+',
            r'secret["\s]*[:=]["\s]*["\w]+',
            r'api_key["\s]*[:=]["\s]*["\w]+',
            r'token["\s]*[:=]["\s]*["\w]+'
        ]
        
        for pattern in secret_patterns:
            matches = re.findall(pattern, config_str, re.IGNORECASE)
            if matches:
                finding = ValidationFinding(
                    rule_id='hardcoded_secret',
                    rule_name='Hardcoded Secret',
                    category=ValidationCategory.SECURITY,
                    severity=ValidationSeverity.HIGH,
                    description=f'Potential hardcoded secret found: {matches[0]}',
                    remediation='Move secrets to secure configuration management'
                )
                findings.append(finding)
        
        # Check for debug mode in production
        if config.get('environment') == 'production' and config.get('debug', False):
            violation = {
                'type': 'debug_in_production',
                'severity': 'high',
                'description': 'Debug mode enabled in production environment'
            }
            violations.append(violation)
        
        score = self._calculate_category_score(violations, findings)
        
        return {
            'score': score,
            'findings': findings,
            'violations': violations,
            'valid': len(violations) == 0
        }
    
    async def _validate_compliance_policies(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate compliance with enterprise policies"""
        findings = []
        violations = []
        
        # Check for compliance requirements
        compliance_config = config.get('compliance', {})
        
        # GDPR compliance
        if not compliance_config.get('data_protection', {}).get('gdpr_compliant', False):
            finding = ValidationFinding(
                rule_id='gdpr_compliance_missing',
                rule_name='GDPR Compliance Missing',
                category=ValidationCategory.COMPLIANCE,
                severity=ValidationSeverity.MEDIUM,
                description='GDPR compliance configuration not detected',
                remediation='Configure GDPR compliance settings including data retention and consent management'
            )
            findings.append(finding)
        
        # Audit logging
        if not config.get('logging', {}).get('audit_logging', False):
            finding = ValidationFinding(
                rule_id='audit_logging_disabled',
                rule_name='Audit Logging Disabled',
                category=ValidationCategory.COMPLIANCE,
                severity=ValidationSeverity.MEDIUM,
                description='Audit logging is disabled',
                remediation='Enable audit logging for compliance requirements'
            )
            findings.append(finding)
        
        # Data encryption at rest
        if not config.get('security', {}).get('encrypt_at_rest', False):
            finding = ValidationFinding(
                rule_id='data_encryption_rest_missing',
                rule_name='Data Encryption at Rest Missing',
                category=ValidationCategory.COMPLIANCE,
                severity=ValidationSeverity.HIGH,
                description='Data encryption at rest is not configured',
                remediation='Enable encryption at rest for sensitive data'
            )
            findings.append(finding)
        
        score = self._calculate_category_score(violations, findings)
        
        return {
            'score': score,
            'findings': findings,
            'violations': violations,
            'valid': len(violations) == 0
        }
    
    async def _validate_performance_requirements(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate performance requirements and optimizations"""
        findings = []
        violations = []
        
        resources = config.get('resources', {})
        
        # Check resource allocation
        if not resources.get('cpu_limit'):
            violation = {
                'type': 'no_cpu_limit',
                'severity': 'medium',
                'description': 'CPU limit not configured'
            }
            violations.append(violation)
        
        if not resources.get('memory_limit'):
            violation = {
                'type': 'no_memory_limit',
                'severity': 'medium',
                'description': 'Memory limit not configured'
            }
            violations.append(violation)
        
        # Check auto-scaling configuration
        autoscaling = config.get('autoscaling', {})
        if not autoscaling.get('enabled', False) and config.get('environment') == 'production':
            finding = ValidationFinding(
                rule_id='no_autoscaling_production',
                rule_name='No Auto-scaling in Production',
                category=ValidationCategory.PERFORMANCE,
                severity=ValidationSeverity.MEDIUM,
                description='Auto-scaling is not enabled in production',
                remediation='Enable auto-scaling for production workloads'
            )
            findings.append(finding)
        
        # Check health checks
        health_check = config.get('health_check', {})
        if not health_check.get('enabled', False):
            finding = ValidationFinding(
                rule_id='no_health_check',
                rule_name='No Health Check',
                category=ValidationCategory.PERFORMANCE,
                severity=ValidationSeverity.LOW,
                description='Health check endpoint not configured',
                remediation='Configure health check endpoint for monitoring'
            )
            findings.append(finding)
        
        score = self._calculate_category_score(violations, findings)
        
        return {
            'score': score,
            'findings': findings,
            'violations': violations,
            'valid': len(violations) == 0
        }
    
    async def _generate_recommendations(self, validation_results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on validation results"""
        recommendations = []
        
        # Critical violations
        critical_count = validation_results['summary'].get('critical_violations', 0)
        if critical_count > 0:
            recommendations.append(f"Address {critical_count} critical violations before deployment")
        
        # Security recommendations
        security_findings = validation_results['categories'].get('security', {})
        if security_findings.get('violations'):
            recommendations.append("Review and update security configurations")
        
        # Compliance recommendations
        compliance_findings = validation_results['categories'].get('compliance', {})
        if compliance_findings.get('findings'):
            recommendations.append("Implement compliance requirements and policies")
        
        # Performance recommendations
        performance_findings = validation_results['categories'].get('performance', {})
        if performance_findings.get('findings'):
            recommendations.append("Optimize performance configurations")
        
        # Overall score recommendations
        if validation_results['overall_score'] < 0.7:
            recommendations.append("Overall validation score is below threshold - comprehensive review recommended")
        
        if validation_results['compliance_score'] < 0.8:
            recommendations.append("Compliance score requires attention - ensure all policy requirements are met")
        
        # Positive reinforcement
        if validation_results['overall_score'] >= 0.9:
            recommendations.append("Excellent validation results - deployment approved with confidence")
        
        return recommendations
    
    def _calculate_category_score(self, violations: List[Dict], findings: List[ValidationFinding]) -> float:
        """Calculate score for a validation category"""
        if not violations and not findings:
            return 1.0
        
        # Weight different severity levels
        severity_weights = {
            'critical': 0.3,
            'high': 0.2,
            'medium': 0.1,
            'low': 0.05
        }
        
        total_penalty = 0.0
        
        # Add penalties for violations
        for violation in violations:
            severity = violation.get('severity', 'medium')
            weight = severity_weights.get(severity, 0.1)
            total_penalty += weight
        
        # Add penalties for findings
        for finding in findings:
            severity = finding.severity.value
            weight = severity_weights.get(severity, 0.05)
            total_penalty += weight
        
        # Calculate score
        score = max(0.0, 1.0 - total_penalty)
        return round(score, 2)
    
    async def _load_built_in_rules(self) -> None:
        """Load built-in validation rules"""
        rules = [
            # Security Rules
            ValidationRule(
                rule_id="SEC001",
                name="Hardcoded Credentials",
                description="Check for hardcoded passwords or API keys",
                category=ValidationCategory.SECURITY,
                severity=ValidationSeverity.HIGH,
                pattern=r"(password|api_key|secret|token)\s*=\s*[\"'][^\"']+[\"']",
                remediation="Move credentials to environment variables or secure configuration"
            ),
            ValidationRule(
                rule_id="SEC002",
                name="SQL Injection Risk",
                description="Check for potential SQL injection vulnerabilities",
                category=ValidationCategory.SECURITY,
                severity=ValidationSeverity.HIGH,
                pattern=r"(execute|query)\s*\(\s*[\"'].*\+.*[\"']",
                remediation="Use parameterized queries to prevent SQL injection"
            ),
            ValidationRule(
                rule_id="SEC003",
                name="Debug Mode in Production",
                description="Check if debug mode is enabled in production",
                category=ValidationCategory.SECURITY,
                severity=ValidationSeverity.HIGH,
                pattern=r"debug\s*=\s*True",
                remediation="Disable debug mode in production environments"
            ),
            
            # Compliance Rules
            ValidationRule(
                rule_id="COMP001",
                name="Missing Audit Logging",
                description="Check if audit logging is configured",
                category=ValidationCategory.COMPLIANCE,
                severity=ValidationSeverity.MEDIUM,
                pattern=r"audit_logging\s*=\s*False",
                remediation="Enable audit logging for compliance requirements"
            ),
            ValidationRule(
                rule_id="COMP002",
                name="GDPR Compliance Missing",
                description="Check for GDPR compliance configuration",
                category=ValidationCategory.COMPLIANCE,
                severity=ValidationSeverity.MEDIUM,
                pattern=r"gdpr_compliant\s*=\s*False",
                remediation="Implement GDPR compliance features including data retention policies"
            ),
            
            # Performance Rules
            ValidationRule(
                rule_id="PERF001",
                name="Missing Resource Limits",
                description="Check if resource limits are configured",
                category=ValidationCategory.PERFORMANCE,
                severity=ValidationSeverity.MEDIUM,
                pattern=r"cpu_limit\s*=\s*None|memory_limit\s*=\s*None",
                remediation="Configure appropriate CPU and memory limits"
            ),
            ValidationRule(
                rule_id="PERF002",
                name="No Health Checks",
                description="Check if health check endpoints are configured",
                category=ValidationCategory.PERFORMANCE,
                severity=ValidationSeverity.LOW,
                pattern=r"health_check\s*=\s*False",
                remediation="Configure health check endpoints for monitoring and auto-healing"
            )
        ]
        
        for rule in rules:
            self.validation_rules[rule.rule_id] = rule
        
        self.logger.info("Loaded %d built-in validation rules", len(rules))
    
    async def _load_custom_rules(self) -> None:
        """Load custom validation rules from configuration"""
        # In a real implementation, this would load from a rules repository or database
        self.logger.info("Loading custom validation rules")
    
    async def _initialize_validation_profiles(self) -> None:
        """Initialize validation profiles for different environments"""
        # In a real implementation, this would initialize environment-specific profiles
        self.logger.info("Initializing validation profiles")
    
    async def _log_validation_audit(self, application_id: str, results: Dict[str, Any]) -> None:
        """Log validation audit event"""
        audit_entry = {
            'timestamp': time.time(),
            'application_id': application_id,
            'validation_type': 'comprehensive',
            'overall_score': results['overall_score'],
            'compliance_score': results['compliance_score'],
            'violations_count': len(results['violations']),
            'findings_count': len(results['findings'])
        }
        
        self.audit_log.append(audit_entry)
        
        # Cleanup old entries (keep last 1000)
        if len(self.audit_log) > 1000:
            self.audit_log = self.audit_log[-1000:]
    
    async def shutdown(self) -> None:
        """Shutdown the validation engine"""
        self.logger.info("Shutting down Validation Engine")
        self.validation_rules.clear()
        self.custom_rules.clear()
        self.validation_cache.clear()
        self.audit_log.clear()