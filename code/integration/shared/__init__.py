"""
Triumvirate Ecosystem Integration Layer
=======================================

Unified platform architecture supporting seamless component communication
between Agenta (Tiered Hierarchy), Pranava (Orchestration Signals), and 
Antakhara (Security & Policy Enforcement).

This integration layer provides:
- Unified communication protocols
- Cross-component intelligence routing
- Adaptive scaling and load balancing
- Real-time observability and monitoring
- Advanced security and governance enforcement
"""

__version__ = "1.0.0"
__author__ = "MiniMax Agent"

from .base import TriumvirateComponent
from .messaging import MessageRouter, MessageProtocol
from .discovery import ServiceDiscovery
from .monitoring import ObservabilityManager

__all__ = [
    "TriumvirateComponent",
    "MessageRouter", 
    "MessageProtocol",
    "ServiceDiscovery",
    "ObservabilityManager"
]
