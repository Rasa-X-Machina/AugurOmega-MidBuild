"""
Shared base components for the Triumvirate Integration Layer
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
import json
from datetime import datetime

class ComponentType(Enum):
    AGENTA = "agenta"
    PRANAVA = "pranava"  
    ANTAKHARA = "antakhara"
    MICROAGENT = "microagent"
    KOSHA = "kosha"

class MessagePriority(Enum):
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class TriumvirateMessage:
    """Unified message format for triumvirate communication"""
    id: str
    sender: ComponentType
    recipient: ComponentType
    priority: MessagePriority
    message_type: str
    payload: Dict[str, Any]
    timestamp: datetime
    correlation_id: Optional[str] = None
    ttl: Optional[int] = None  # Time to live in seconds

class TriumvirateComponent(ABC):
    """Abstract base class for all triumvirate components"""
    
    def __init__(self, component_type: ComponentType, component_id: str):
        self.component_type = component_type
        self.component_id = component_id
        self.logger = logging.getLogger(f"{component_type.value}.{component_id}")
        self.is_running = False
        self.message_handlers: Dict[str, callable] = {}
        self.dependencies: List[str] = []
        self.health_status = "unknown"
        
    async def start(self) -> None:
        """Start the component"""
        self.logger.info(f"Starting {self.component_type.value} component {self.component_id}")
        self.is_running = True
        await self.initialize()
        
    async def stop(self) -> None:
        """Stop the component"""
        self.logger.info(f"Stopping {self.component_type.value} component {self.component_id}")
        self.is_running = False
        await self.shutdown()
        
    async def send_message(self, message: TriumvirateMessage) -> bool:
        """Send a message to another component"""
        try:
            return await self._route_message(message)
        except Exception as e:
            self.logger.error(f"Failed to send message: {e}")
            return False
            
    async def receive_message(self, message: TriumvirateMessage) -> Optional[Dict[str, Any]]:
        """Receive and process a message"""
        try:
            handler = self.message_handlers.get(message.message_type)
            if handler:
                return await handler(message)
            else:
                self.logger.warning(f"No handler for message type: {message.message_type}")
                return None
        except Exception as e:
            self.logger.error(f"Failed to process message: {e}")
            raise
            
    def register_handler(self, message_type: str, handler: callable) -> None:
        """Register a message handler"""
        self.message_handlers[message_type] = handler
        
    def add_dependency(self, dependency: str) -> None:
        """Add a component dependency"""
        if dependency not in self.dependencies:
            self.dependencies.append(dependency)
            
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the component"""
        pass
        
    @abstractmethod
    async def shutdown(self) -> None:
        """Shutdown the component"""
        pass
        
    @abstractmethod
    async def _route_message(self, message: TriumvirateMessage) -> bool:
        """Route a message to the appropriate destination"""
        pass
        
    async def get_health_status(self) -> Dict[str, Any]:
        """Get component health status"""
        return {
            "component_id": self.component_id,
            "component_type": self.component_type.value,
            "status": self.health_status,
            "is_running": self.is_running,
            "dependencies": self.dependencies,
            "timestamp": datetime.now().isoformat()
        }
