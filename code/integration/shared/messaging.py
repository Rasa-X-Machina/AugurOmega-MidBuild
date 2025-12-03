"""
Unified messaging system for triumvirate component communication
"""

import asyncio
import json
import uuid
from typing import Dict, Any, Optional, List, Callable
from dataclasses import asdict
from datetime import datetime
from collections import defaultdict
import threading

from .base import TriumvirateMessage, ComponentType, MessagePriority

class MessageRouter:
    """Central message routing and distribution system"""
    
    def __init__(self):
        self.routes: Dict[str, List[Callable]] = defaultdict(list)
        self.component_registry: Dict[str, Dict[str, Any]] = {}
        self.message_queue = asyncio.Queue()
        self.running = False
        self.router_thread = None
        
    def register_component(self, component_type: ComponentType, component_id: str, 
                         endpoint: str, capabilities: List[str] = None) -> None:
        """Register a component in the routing system"""
        self.component_registry[f"{component_type.value}.{component_id}"] = {
            "type": component_type.value,
            "id": component_id,
            "endpoint": endpoint,
            "capabilities": capabilities or [],
            "status": "online",
            "registered_at": datetime.now().isoformat()
        }
        self.logger.info(f"Registered component: {component_type.value}.{component_id}")
        
    def add_route(self, message_type: str, handler: Callable) -> None:
        """Add a message route"""
        self.routes[message_type].append(handler)
        
    async def start(self) -> None:
        """Start the message router"""
        self.running = True
        self.router_thread = threading.Thread(target=self._process_routes)
        self.router_thread.start()
        self.logger.info("Message router started")
        
    async def stop(self) -> None:
        """Stop the message router"""
        self.running = False
        if self.router_thread:
            self.router_thread.join()
        self.logger.info("Message router stopped")
        
    def create_message(self, sender: ComponentType, recipient: ComponentType,
                      message_type: str, payload: Dict[str, Any],
                      priority: MessagePriority = MessagePriority.NORMAL) -> TriumvirateMessage:
        """Create a new triumvirate message"""
        return TriumvirateMessage(
            id=str(uuid.uuid4()),
            sender=sender,
            recipient=recipient,
            priority=priority,
            message_type=message_type,
            payload=payload,
            timestamp=datetime.now()
        )
        
    async def route_message(self, message: TriumvirateMessage) -> bool:
        """Route a message to appropriate handlers"""
        try:
            handlers = self.routes.get(message.message_type, [])
            if not handlers:
                self.logger.warning(f"No handlers for message type: {message.message_type}")
                return False
                
            # Execute handlers concurrently
            tasks = [handler(message) for handler in handlers]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Log results
            successful = sum(1 for r in results if r is True or r is None)
            self.logger.info(f"Message {message.id} processed by {successful}/{len(handlers)} handlers")
            
            return successful > 0
            
        except Exception as e:
            self.logger.error(f"Failed to route message {message.id}: {e}")
            return False
            
    def _process_routes(self) -> None:
        """Process message routes in a separate thread"""
        asyncio.run(self._router_loop())
        
    async def _router_loop(self) -> None:
        """Main router processing loop"""
        while self.running:
            try:
                # Process queued messages
                if not self.message_queue.empty():
                    message = await self.message_queue.get()
                    await self.route_message(message)
                    
                await asyncio.sleep(0.01)  # Small delay to prevent busy waiting
                
            except Exception as e:
                self.logger.error(f"Router loop error: {e}")
                await asyncio.sleep(1)

class MessageProtocol:
    """Message protocol definitions and validation"""
    
    # Protocol version for compatibility
    PROTOCOL_VERSION = "1.0.0"
    
    @staticmethod
    def serialize_message(message: TriumvirateMessage) -> str:
        """Serialize message to JSON string"""
        data = asdict(message)
        # Convert datetime to ISO format
        data['timestamp'] = message.timestamp.isoformat()
        data['sender'] = message.sender.value
        data['recipient'] = message.recipient.value
        data['priority'] = message.priority.value
        return json.dumps(data)
        
    @staticmethod
    def deserialize_message(data: str) -> TriumvirateMessage:
        """Deserialize JSON string to message"""
        raw_data = json.loads(data)
        return TriumvirateMessage(
            id=raw_data['id'],
            sender=ComponentType(raw_data['sender']),
            recipient=ComponentType(raw_data['recipient']),
            priority=MessagePriority(raw_data['priority']),
            message_type=raw_data['message_type'],
            payload=raw_data['payload'],
            timestamp=datetime.fromisoformat(raw_data['timestamp']),
            correlation_id=raw_data.get('correlation_id'),
            ttl=raw_data.get('ttl')
        )
        
    @staticmethod
    def validate_message(message: TriumvirateMessage) -> bool:
        """Validate message structure and content"""
        required_fields = ['id', 'sender', 'recipient', 'message_type', 'payload']
        
        # Check required fields
        if not all(hasattr(message, field) for field in required_fields):
            return False
            
        # Validate enum values
        if not isinstance(message.sender, ComponentType):
            return False
        if not isinstance(message.recipient, ComponentType):
            return False
        if not isinstance(message.priority, MessagePriority):
            return False
            
        # Check message ID format
        if not isinstance(message.id, str) or len(message.id) == 0:
            return False
            
        return True
