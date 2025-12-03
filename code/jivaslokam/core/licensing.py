"""
License Manager for Jivaslokam

Provides comprehensive license validation, compliance checking,
and enforcement capabilities for enterprise deployment.

Supports various license models including SaaS, perpetual, usage-based,
and hybrid licensing structures with automated compliance validation.
"""

import asyncio
import json
import time
import logging
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import hashlib
import secrets

logger = logging.getLogger(__name__)


class LicenseType(Enum):
    """Supported license types"""
    PERPETUAL = "perpetual"
    SUBSCRIPTION = "subscription"
    USAGE_BASED = "usage_based"
    TRIAL = "trial"
    EVALUATION = "evaluation"
    NODE_LOCKED = "node_locked"
    FLOATING = "floating"
    ENTERPRISE = "enterprise"


class LicenseStatus(Enum):
    """License status types"""
    VALID = "valid"
    EXPIRED = "expired"
    REVOKED = "revoked"
    SUSPENDED = "suspended"
    OVERUSE = "overuse"
    INVALID = "invalid"
    PENDING_ACTIVATION = "pending_activation"


@dataclass
class LicenseConstraint:
    """License constraint definition"""
    constraint_type: str  # max_users, max_instances, max_apis, geographic_limit, etc.
    value: Any
    description: str
    enforcement_level: str  # hard, soft, warning
    
    def validate(self, usage_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate usage against constraint"""
        current_value = usage_data.get(self.constraint_type, 0)
        max_allowed = self.value
        
        if self.constraint_type == "max_users":
            status = "compliant" if current_value <= max_allowed else "violation"
        elif self.constraint_type == "max_instances":
            status = "compliant" if current_value <= max_allowed else "violation"
        elif self.constraint_type == "expiry_date":
            status = "compliant" if time.time() <= max_allowed else "expired"
        else:
            status = "unknown"
        
        return {
            "constraint": self.constraint_type,
            "status": status,
            "current_value": current_value,
            "max_allowed": max_allowed,
            "enforcement_level": self.enforcement_level
        }


@dataclass
class LicenseMetadata:
    """License metadata and information"""
    license_id: str
    license_type: LicenseType
    issued_to: str
    issued_by: str
    issue_date: str
    expiry_date: Optional[str]
    version: str
    product_name: str
    product_version: str
    constraints: List[LicenseConstraint] = field(default_factory=list)
    custom_fields: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            'license_id': self.license_id,
            'license_type': self.license_type.value,
            'issued_to': self.issued_to,
            'issued_by': self.issued_by,
            'issue_date': self.issue_date,
            'expiry_date': self.expiry_date,
            'version': self.version,
            'product_name': self.product_name,
            'product_version': self.product_version,
            'constraints': [
                {
                    'constraint_type': c.constraint_type,
                    'value': c.value,
                    'description': c.description,
                    'enforcement_level': c.enforcement_level
                } for c in self.constraints
            ],
            'custom_fields': self.custom_fields
        }


class LicenseValidator:
    """Validates license authenticity and compliance"""
    
    def __init__(self, public_key: Optional[str] = None):
        self.logger = logging.getLogger(__name__ + ".LicenseValidator")
        self.public_key = public_key or self._generate_demo_public_key()
    
    def _generate_demo_public_key(self) -> str:
        """Generate a demo public key for testing"""
        return "JIVASLOKAM_DEMO_PUBLIC_KEY_2024"
    
    async def validate_license_signature(self, license_data: Dict[str, Any], signature: str) -> bool:
        """Validate license signature (simplified for demo)"""
        # In production, this would use proper cryptographic signature validation
        expected_hash = hashlib.sha256(
            json.dumps(license_data, sort_keys=True).encode()
        ).hexdigest()
        
        # Simple signature validation (replace with cryptographic validation in production)
        return len(signature) > 20 and signature.startswith("SIGN_")
    
    async def validate_license_format(self, license_info: Dict[str, Any]) -> Dict[str, Any]:
        """Validate license format and required fields"""
        required_fields = [
            'license_id', 'license_type', 'issued_to', 'issued_by', 
            'issue_date', 'version', 'product_name'
        ]
        
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        for field in required_fields:
            if field not in license_info:
                validation_result['errors'].append(f"Missing required field: {field}")
                validation_result['valid'] = False
        
        # Validate license type
        if 'license_type' in license_info:
            try:
                LicenseType(license_info['license_type'])
            except ValueError:
                validation_result['errors'].append(f"Invalid license type: {license_info['license_type']}")
                validation_result['valid'] = False
        
        # Validate date formats
        date_fields = ['issue_date', 'expiry_date']
        for field in date_fields:
            if field in license_info and license_info[field]:
                try:
                    time.strptime(license_info[field], '%Y-%m-%d')
                except ValueError:
                    validation_result['errors'].append(f"Invalid date format for {field}: {license_info[field]}")
        
        return validation_result


class LicenseManager:
    """
    Comprehensive License Manager for Jivaslokam
    
    Provides license validation, compliance checking, and enforcement
    for enterprise deployment scenarios.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__ + ".LicenseManager")
        self.validator = LicenseValidator()
        self.license_cache = {}
        self.active_sessions = {}
        self.usage_tracking = {}
        self.audit_log = []
        
    async def initialize(self) -> None:
        """Initialize the license manager"""
        self.logger.info("Initializing License Manager...")
        
        # Initialize usage tracking
        await self._initialize_usage_tracking()
        
        # Load license validation rules
        await self._load_license_rules()
        
        self.logger.info("License Manager initialized successfully")
    
    async def validate_license(self, license_info: Dict[str, Any]) -> bool:
        """
        Validate a license against enterprise requirements
        
        Args:
            license_info: License information to validate
            
        Returns:
            Boolean indicating if license is valid and compliant
        """
        try:
            self.logger.info("Validating license: %s", license_info.get('license_id', 'unknown'))
            
            # Format validation
            format_validation = await self.validator.validate_license_format(license_info)
            if not format_validation['valid']:
                self.logger.error("License format validation failed: %s", format_validation['errors'])
                return False
            
            # Signature validation
            signature = license_info.get('signature', '')
            if signature:
                signature_valid = await self.validator.validate_license_signature(
                    license_info, signature
                )
                if not signature_valid:
                    self.logger.error("License signature validation failed")
                    return False
            
            # Create license metadata
            metadata = LicenseMetadata(
                license_id=license_info['license_id'],
                license_type=LicenseType(license_info['license_type']),
                issued_to=license_info['issued_to'],
                issued_by=license_info['issued_by'],
                issue_date=license_info['issue_date'],
                expiry_date=license_info.get('expiry_date'),
                version=license_info['version'],
                product_name=license_info['product_name'],
                product_version=license_info['product_version']
            )
            
            # Add constraints if present
            if 'constraints' in license_info:
                for constraint_data in license_info['constraints']:
                    constraint = LicenseConstraint(
                        constraint_type=constraint_data['constraint_type'],
                        value=constraint_data['value'],
                        description=constraint_data['description'],
                        enforcement_level=constraint_data['enforcement_level']
                    )
                    metadata.constraints.append(constraint)
            
            # Validate constraints
            constraint_valid = await self._validate_constraints(metadata, {})
            if not constraint_valid['overall_valid']:
                self.logger.error("License constraint validation failed: %s", constraint_valid['violations'])
                return False
            
            # Cache the license
            self.license_cache[metadata.license_id] = {
                'metadata': metadata,
                'validated_at': time.time(),
                'usage_data': {}
            }
            
            self.logger.info("License %s validated successfully", metadata.license_id)
            return True
            
        except Exception as e:
            self.logger.error("License validation failed: %s", str(e))
            return False
    
    async def check_usage_compliance(self, 
                                   license_id: str, 
                                   usage_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check usage against license constraints
        
        Args:
            license_id: License identifier
            usage_data: Current usage metrics
            
        Returns:
            Compliance report with constraint status
        """
        try:
            if license_id not in self.license_cache:
                return {
                    'compliant': False,
                    'error': 'License not found in cache',
                    'constraints': []
                }
            
            license_data = self.license_cache[license_id]
            metadata = license_data['metadata']
            
            constraint_results = []
            violations = []
            
            for constraint in metadata.constraints:
                result = constraint.validate(usage_data)
                constraint_results.append(result)
                
                if result['status'] == 'violation' and constraint.enforcement_level == 'hard':
                    violations.append({
                        'constraint': constraint.constraint_type,
                        'current_value': result['current_value'],
                        'max_allowed': result['max_allowed'],
                        'description': constraint.description
                    })
            
            # Update usage tracking
            self.usage_tracking[license_id] = {
                'last_check': time.time(),
                'usage_data': usage_data,
                'constraint_results': constraint_results
            }
            
            compliance_report = {
                'license_id': license_id,
                'compliant': len(violations) == 0,
                'violations': violations,
                'constraints': constraint_results,
                'usage_score': self._calculate_usage_score(usage_data, metadata),
                'recommendations': self._generate_usage_recommendations(violations)
            }
            
            return compliance_report
            
        except Exception as e:
            self.logger.error("Usage compliance check failed: %s", str(e))
            return {
                'compliant': False,
                'error': str(e),
                'violations': [],
                'constraints': []
            }
    
    async def validate_deployment_license(self, 
                                        deployment_config: Dict[str, Any],
                                        license_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate deployment configuration against license requirements
        
        Args:
            deployment_config: Deployment configuration to validate
            license_info: License information for validation
            
        Returns:
            Deployment validation result
        """
        try:
            self.logger.info("Validating deployment license compliance")
            
            validation_result = {
                'valid': True,
                'compliance_score': 1.0,
                'violations': [],
                'warnings': [],
                'recommendations': []
            }
            
            # Check if license allows deployment
            license_type = license_info.get('license_type')
            if license_type == 'trial' or license_type == 'evaluation':
                if deployment_config.get('production_deployment', False):
                    validation_result['valid'] = False
                    validation_result['violations'].append({
                        'type': 'trial_deployment_restriction',
                        'description': 'Trial/Evaluation licenses cannot be used for production deployment',
                        'severity': 'critical'
                    })
            
            # Check license type compatibility
            required_license_types = deployment_config.get('required_license_types', [])
            if required_license_types and license_type not in required_license_types:
                validation_result['valid'] = False
                validation_result['violations'].append({
                    'type': 'license_type_mismatch',
                    'description': f'License type {license_type} not in required types: {required_license_types}',
                    'severity': 'high'
                })
            
            # Check geographic restrictions
            deployment_region = deployment_config.get('deployment_region')
            license_regions = license_info.get('allowed_regions', [])
            if license_regions and deployment_region not in license_regions:
                validation_result['valid'] = False
                validation_result['violations'].append({
                    'type': 'geographic_restriction',
                    'description': f'Deployment region {deployment_region} not allowed by license',
                    'severity': 'high'
                })
            
            # Check capacity limits
            max_instances = self._get_license_constraint(license_info, 'max_instances')
            planned_instances = deployment_config.get('planned_instances', 1)
            if max_instances and planned_instances > max_instances:
                validation_result['valid'] = False
                validation_result['violations'].append({
                    'type': 'capacity_exceeded',
                    'description': f'Planned instances ({planned_instances}) exceed license limit ({max_instances})',
                    'severity': 'critical'
                })
            
            # Calculate compliance score
            violations_count = len(validation_result['violations'])
            if violations_count > 0:
                validation_result['compliance_score'] = max(0.0, 1.0 - (violations_count * 0.2))
            
            # Generate recommendations
            if validation_result['violations']:
                validation_result['recommendations'].extend([
                    'Review and update license configuration',
                    'Contact licensing department for assistance',
                    'Consider upgrading to appropriate license tier'
                ])
            
            return validation_result
            
        except Exception as e:
            self.logger.error("Deployment license validation failed: %s", str(e))
            return {
                'valid': False,
                'compliance_score': 0.0,
                'violations': [{
                    'type': 'validation_error',
                    'description': f'Validation system error: {str(e)}',
                    'severity': 'critical'
                }],
                'warnings': [],
                'recommendations': ['Contact system administrator']
            }
    
    async def generate_license_report(self, license_id: str) -> Dict[str, Any]:
        """Generate comprehensive license usage report"""
        try:
            if license_id not in self.license_cache:
                return {'error': 'License not found'}
            
            license_data = self.license_cache[license_id]
            metadata = license_data['metadata']
            usage_data = self.usage_tracking.get(license_id, {})
            
            report = {
                'license_id': license_id,
                'license_info': metadata.to_dict(),
                'usage_metrics': usage_data,
                'compliance_status': 'compliant',
                'expiry_status': 'active',
                'recommendations': [],
                'generated_at': time.time()
            }
            
            # Check expiry status
            if metadata.expiry_date:
                expiry_timestamp = time.mktime(time.strptime(metadata.expiry_date, '%Y-%m-%d'))
                if time.time() > expiry_timestamp:
                    report['expiry_status'] = 'expired'
                    report['compliance_status'] = 'non_compliant'
                    report['recommendations'].append('License has expired - renewal required')
            
            # Check constraint violations
            if usage_data.get('constraint_results'):
                violations = [
                    r for r in usage_data['constraint_results'] 
                    if r['status'] == 'violation'
                ]
                if violations:
                    report['compliance_status'] = 'non_compliant'
                    report['recommendations'].append('License constraints exceeded - usage reduction required')
            
            return report
            
        except Exception as e:
            self.logger.error("License report generation failed: %s", str(e))
            return {'error': str(e)}
    
    async def _validate_constraints(self, metadata: LicenseMetadata, usage_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate all license constraints"""
        violations = []
        for constraint in metadata.constraints:
            validation = constraint.validate(usage_data)
            if validation['status'] == 'violation':
                violations.append(validation)
        
        return {
            'overall_valid': len(violations) == 0,
            'violations': violations
        }
    
    def _get_license_constraint(self, license_info: Dict[str, Any], constraint_type: str) -> Optional[Any]:
        """Get constraint value from license info"""
        for constraint in license_info.get('constraints', []):
            if constraint.get('constraint_type') == constraint_type:
                return constraint.get('value')
        return None
    
    def _calculate_usage_score(self, usage_data: Dict[str, Any], metadata: LicenseMetadata) -> float:
        """Calculate usage score based on constraints and actual usage"""
        total_constraints = len(metadata.constraints)
        if total_constraints == 0:
            return 1.0
        
        compliant_constraints = 0
        for constraint in metadata.constraints:
            validation = constraint.validate(usage_data)
            if validation['status'] == 'compliant':
                compliant_constraints += 1
        
        return compliant_constraints / total_constraints
    
    def _generate_usage_recommendations(self, violations: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on usage violations"""
        recommendations = []
        
        for violation in violations:
            constraint = violation.get('constraint', 'unknown')
            if constraint == 'max_users':
                recommendations.append('Consider upgrading license tier for additional users')
            elif constraint == 'max_instances':
                recommendations.append('Optimize instance usage or upgrade license capacity')
            elif constraint == 'expiry_date':
                recommendations.append('Renew license before expiry date')
        
        if not recommendations:
            recommendations.append('Usage within license constraints')
        
        return recommendations
    
    async def _initialize_usage_tracking(self) -> None:
        """Initialize usage tracking infrastructure"""
        self.logger.info("Initializing usage tracking")
        # Initialize usage metrics collection
    
    async def _load_license_rules(self) -> None:
        """Load license validation rules and policies"""
        self.logger.info("Loading license validation rules")
        # Load enterprise license policies and rules
    
    async def shutdown(self) -> None:
        """Shutdown the license manager"""
        self.logger.info("Shutting down License Manager")
        self.license_cache.clear()
        self.usage_tracking.clear()
        self.active_sessions.clear()
