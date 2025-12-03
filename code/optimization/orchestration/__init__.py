"""
Optimization Workflow Orchestrator - Coordinates the entire optimization ecosystem
Manages optimization workflows across monitoring, analysis, and optimization modules
"""

from .workflow_manager import WorkflowManager
from .integration_layer import OptimizationIntegrationLayer
from .api_interface import OptimizationAPI

__all__ = [
    'WorkflowManager',
    'OptimizationIntegrationLayer',
    'OptimizationAPI'
]

__version__ = "1.0.0"
__author__ = "MiniMax Agent"
