"""
Legal Models for Jivaslokam

Data models for legal framework components including compliance standards,
regulatory frameworks, licensing agreements, and contractual obligations.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import json


class ComplianceLevel(Enum):
    """Compliance requirement levels"""
    MANDATORY = "mandatory"
    RECOMMENDED = "recommended"
    OPTIONAL = "optional"
    CONDITIONAL = "conditional"


@dataclass
class ComplianceStandard:
    """Compliance standard definition"""
    name: str
    description: str
    requirements: List[str]
    compliance_level: str
    version: str = "1.0"
    effective_date: str = "2024-01-01"
    categories: List[str] = field(default_factory=list)
    control_framework: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            'name': self.name,
            'description': self.description,
            'requirements': self.requirements,
            'compliance_level': self.compliance_level,
            'version': self.version,
            'effective_date': self.effective_date,
            'categories': self.categories,
            'control_framework': self.control_framework
        }


@dataclass
class LegalRequirement:
    """Individual legal requirement"""
    requirement_id: str
    title: str
    description: str
    compliance_standard: str
    requirement_type: str
    mandatory: bool = True
    evidence_required: bool = True
    validation_method: str = "automated"
    remediation_steps: List[str] = field(default_factory=list)
    penalties: List[str] = field(default_factory=list)
    exceptions: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            'requirement_id': self.requirement_id,
            'title': self.title,
            'description': self.description,
            'compliance_standard': self.compliance_standard,
            'requirement_type': self.requirement_type,
            'mandatory': self.mandatory,
            'evidence_required': self.evidence_required,
            'validation_method': self.validation_method,
            'remediation_steps': self.remediation_steps,
            'penalties': self.penalties,
            'exceptions': self.exceptions
        }


@dataclass
class RegulatoryFramework:
    """Regulatory framework definition"""
    name: str
    jurisdiction: str
    requirements: List[str]
    penalties: List[str]
    scope: str = "global"
    enforcement_date: str = "ongoing"
    reporting_frequency: str = "annual"
    key_authorities: List[str] = field(default_factory=list)
    guidance_documents: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            'name': self.name,
            'jurisdiction': self.jurisdiction,
            'requirements': self.requirements,
            'penalties': self.penalties,
            'scope': self.scope,
            'enforcement_date': self.enforcement_date,
            'reporting_frequency': self.reporting_frequency,
            'key_authorities': self.key_authorities,
            'guidance_documents': self.guidance_documents
        }


@dataclass
class LicensingAgreement:
    """Licensing agreement definition"""
    agreement_id: str
    license_type: str
    terms: Dict[str, Any]
    restrictions: List[str] = field(default_factory=list)
    usage_limits: Dict[str, Any] = field(default_factory=dict)
    geographic_scope: List[str] = field(default_factory=list)
    temporal_scope: str = "perpetual"
    renewal_requirements: List[str] = field(default_factory=list)
    termination_conditions: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            'agreement_id': self.agreement_id,
            'license_type': self.license_type,
            'terms': self.terms,
            'restrictions': self.restrictions,
            'usage_limits': self.usage_limits,
            'geographic_scope': self.geographic_scope,
            'temporal_scope': self.temporal_scope,
            'renewal_requirements': self.renewal_requirements,
            'termination_conditions': self.termination_conditions
        }


@dataclass
class IntellectualProperty:
    """Intellectual property definition"""
    ip_id: str
    ip_type: str
    description: str
    ownership: str
    protection_level: str
    restrictions: List[str] = field(default_factory=list)
    licensing_terms: Dict[str, Any] = field(default_factory=dict)
    confidentiality_requirements: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            'ip_id': self.ip_id,
            'ip_type': self.ip_type,
            'description': self.description,
            'ownership': self.ownership,
            'protection_level': self.protection_level,
            'restrictions': self.restrictions,
            'licensing_terms': self.licensing_terms,
            'confidentiality_requirements': self.confidentiality_requirements
        }


@dataclass
class ContractualObligation:
    """Contractual obligation definition"""
    obligation_id: str
    contract_type: str
    description: str
    party_responsible: str
    due_date: Optional[str] = None
    status: str = "active"
    compliance_requirements: List[str] = field(default_factory=list)
    reporting_requirements: List[str] = field(default_factory=list)
    audit_requirements: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            'obligation_id': self.obligation_id,
            'contract_type': self.contract_type,
            'description': self.description,
            'party_responsible': self.party_responsible,
            'due_date': self.due_date,
            'status': self.status,
            'compliance_requirements': self.compliance_requirements,
            'reporting_requirements': self.reporting_requirements,
            'audit_requirements': self.audit_requirements
        }
