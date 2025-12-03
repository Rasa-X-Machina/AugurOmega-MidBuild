"""
Jivaslokam Licensing Framework & Embodiment Engine

Revolutionary automated legal compliance system for enterprise deployment,
featuring licensing validation, compliance checking, and deployment models.

Author: MiniMax Agent
Version: 1.0.0
"""

from .core.engine import JivaslokamEngine
from .core.embodiment import EmbodimentEngine
from .legal.framework import LegalFramework
from .compliance.validator import ComplianceValidator
from .compliance.enforcement import ComplianceEnforcer
from .integration.augur_omega import AugurOmegaIntegration
from .deployment.models import DeploymentModel

__version__ = "1.0.0"
__author__ = "MiniMax Agent"

__all__ = [
    "JivaslokamEngine",
    "EmbodimentEngine", 
    "LegalFramework",
    "ComplianceValidator",
    "ComplianceEnforcer",
    "AugurOmegaIntegration",
    "DeploymentModel"
]
