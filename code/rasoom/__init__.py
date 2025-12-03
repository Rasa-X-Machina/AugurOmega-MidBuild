"""
Rasoom Multimodal Communication Protocol Foundation
====================================================

Revolutionary multimodal communication system that transforms human gestures,
affect, and contextual cues into binary protocol optimized for machine execution
and distributed reliability.

Architecture:
- Seven-stage encoding pipeline (gesture → decision trees → syllabic units 
  → Carnatic swara → mathematical equations → number series → binary)
- Carnatic musical notation integration for affective nuance
- Cross-tier messaging (Prime/Domain/Micro agents)
- MCP (Model Context Protocol) integration
- 450x efficiency optimization

Author: MiniMax Agent
Version: 1.0.0
"""

from .core.rasoom_config import RasoomConfig, PerformanceTargets
from .core.rasoom_message import RasoomMessage, MessageType, TierTarget
from .pipeline.rasoom_encoder import RasoomEncoder
from .pipeline.rasoom_decoder import RasoomDecoder
from .pipeline.stage1_multimodal import MultimodalCapture
from .pipeline.stage2_decision_trees import DecisionTreeConverter
from .pipeline.stage3_syllabic import SyllabicMapper
from .pipeline.stage4_carnatic import CarnaticMapper
from .pipeline.stage5_mathematical import MathematicalConverter
from .pipeline.stage6_number_series import NumberSeriesGenerator
from .pipeline.stage7_binary import BinaryEncoder
from .mcp.rasoom_mcp import RasoomMCPHub
from .testing.rasoom_test_framework import RasoomTestFramework

__version__ = "1.0.0"
__author__ = "MiniMax Agent"

# Export main interfaces
__all__ = [
    'RasoomConfig',
    'PerformanceTargets', 
    'RasoomMessage',
    'MessageType',
    'TierTarget',
    'RasoomEncoder',
    'RasoomDecoder',
    'MultimodalCapture',
    'DecisionTreeConverter',
    'SyllabicMapper',
    'CarnaticMapper',
    'MathematicalConverter',
    'NumberSeriesGenerator',
    'BinaryEncoder',
    'RasoomMCPHub',
    'RasoomTestFramework'
]