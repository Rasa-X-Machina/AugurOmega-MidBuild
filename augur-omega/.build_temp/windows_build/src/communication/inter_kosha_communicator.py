"""
Augur Omega: Inter-Kosha Communication System
Manages communication between all koshas in the system
"""
import asyncio
import json
import uuid
from enum import Enum
from typing import Dict, List, Any, Optional, Callable, Awaitable
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import logging
import queue
import threading
from abc import ABC, abstractmethod


class MessageType(Enum):
    """Types of messages that can be sent between koshas"""
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    BROADCAST = "broadcast"
    ERROR = "error"
    HEARTBEAT = "heartbeat"
    SYNCHRONIZATION = "synchronization"


class MessagePriority(Enum):
    """Priority levels for messages"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class Message:
    """Represents a message between koshas"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source_id: str = ""
    target_id: str = ""  # Empty string for broadcast messages
    type: MessageType = MessageType.NOTIFICATION
    priority: MessagePriority = MessagePriority.NORMAL
    content: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    correlation_id: Optional[str] = None  # For request-response correlation
    timeout: Optional[int] = None  # Timeout in seconds
    retries: int = 0
    max_retries: int = 3


class KoshaStatus(Enum):
    """Status of a kosha in the system"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    BUSY = "busy"
    UNREACHABLE = "unreachable"
    ERROR = "error"


@dataclass
class KoshaInfo:
    """Information about a kosha in the system"""
    id: str
    type: str  # prime_kosha, domain_kosha, microagent
    status: KoshaStatus = KoshaStatus.ACTIVE
    capabilities: List[str] = field(default_factory=list)
    last_heartbeat: Optional[str] = None
    endpoint: Optional[str] = None
    response_time: float = 0.0
    load: float = 0.0  # 0.0 to 1.0


class MessageHandler(ABC):
    """Abstract base class for message handlers"""
    
    @abstractmethod
    async def handle_message(self, message: Message) -> Optional[Message]:
        """Handle an incoming message and optionally return a response"""
        pass


class DefaultMessageHandler(MessageHandler):
    """Default message handler for basic message types"""
    
    async def handle_message(self, message: Message) -> Optional[Message]:
        """Handle a message based on its type"""
        if message.type == MessageType.HEARTBEAT:
            # Return a heartbeat response
            response = Message(
                type=MessageType.RESPONSE,
                source_id=message.target_id,
                target_id=message.source_id,
                content={"status": "alive"},
                correlation_id=message.id
            )
            return response
        elif message.type == MessageType.SYNCHRONIZATION:
            # Process synchronization message
            response = Message(
                type=MessageType.RESPONSE,
                source_id=message.target_id,
                target_id=message.source_id,
                content={"synchronized": True},
                correlation_id=message.id
            )
            return response
        else:
            # For other message types, just acknowledge receipt
            response = Message(
                type=MessageType.RESPONSE,
                source_id=message.target_id,
                target_id=message.source_id,
                content={"acknowledged": True, "original_id": message.id},
                correlation_id=message.id
            )
            return response


class KoshaRegistry:
    """Registry to keep track of all koshas in the system"""
    
    def __init__(self):
        self._koshas: Dict[str, KoshaInfo] = {}
        self._lock = asyncio.Lock()
    
    async def register_kosha(self, kosha_info: KoshaInfo) -> bool:
        """Register a new kosha in the system"""
        async with self._lock:
            self._koshas[kosha_info.id] = kosha_info
            return True
    
    async def unregister_kosha(self, kosha_id: str) -> bool:
        """Unregister a kosha from the system"""
        async with self._lock:
            if kosha_id in self._koshas:
                del self._koshas[kosha_id]
                return True
            return False
    
    async def get_kosha(self, kosha_id: str) -> Optional[KoshaInfo]:
        """Get information about a specific kosha"""
        async with self._lock:
            return self._koshas.get(kosha_id)
    
    async def get_all_koshas(self) -> List[KoshaInfo]:
        """Get information about all registered koshas"""
        async with self._lock:
            return list(self._koshas.values())
    
    async def get_koshas_by_type(self, kosha_type: str) -> List[KoshaInfo]:
        """Get koshas of a specific type"""
        async with self._lock:
            return [k for k in self._koshas.values() if k.type == kosha_type]
    
    async def update_kosha_status(self, kosha_id: str, status: KoshaStatus) -> bool:
        """Update the status of a kosha"""
        async with self._lock:
            if kosha_id in self._koshas:
                self._koshas[kosha_id].status = status
                self._koshas[kosha_id].last_heartbeat = datetime.now().isoformat()
                return True
            return False
    
    async def update_kosha_load(self, kosha_id: str, load: float) -> bool:
        """Update the load of a kosha"""
        async with self._lock:
            if kosha_id in self._koshas:
                self._koshas[kosha_id].load = min(1.0, max(0.0, load))
                return True
            return False


class MessageQueue:
    """Thread-safe message queue for the communication system"""
    
    def __init__(self, maxsize: int = 0):
        self._queue = queue.Queue(maxsize=maxsize)
        self._lock = threading.Lock()
    
    def put(self, message: Message) -> bool:
        """Add a message to the queue"""
        try:
            self._queue.put(message, block=False)
            return True
        except queue.Full:
            return False
    
    def get(self) -> Optional[Message]:
        """Get a message from the queue"""
        try:
            return self._queue.get(block=False)
        except queue.Empty:
            return None
    
    def size(self) -> int:
        """Get the current size of the queue"""
        return self._queue.qsize()
    
    def is_empty(self) -> bool:
        """Check if the queue is empty"""
        return self._queue.empty()


class InterKoshaCommunicator:
    """Manages communication between all koshas in the system"""
    
    def __init__(self, max_message_retries: int = 3):
        self.registry = KoshaRegistry()
        self.message_queue = MessageQueue(maxsize=10000)
        self.handlers: Dict[str, MessageHandler] = {}
        self.message_callbacks: Dict[str, Callable[[Message], Awaitable[None]]] = {}
        self.pending_requests: Dict[str, asyncio.Future] = {}
        self.max_retries = max_message_retries
        
        # Start the message processing loop
        self._message_processing_task = None
        self._running = False
    
    async def start(self):
        """Start the communication system"""
        self._running = True
        self._message_processing_task = asyncio.create_task(self._process_messages())
        logging.info("Inter-Kosha Communication System started")
    
    async def stop(self):
        """Stop the communication system"""
        self._running = False
        if self._message_processing_task:
            self._message_processing_task.cancel()
            try:
                await self._message_processing_task
            except asyncio.CancelledError:
                pass
        
        # Cancel any pending requests
        for future in self.pending_requests.values():
            if not future.done():
                future.cancel()
        
        logging.info("Inter-Kosha Communication System stopped")
    
    async def register_kosha(self, kosha_id: str, kosha_type: str, capabilities: List[str] = None, endpoint: str = None):
        """Register a kosha in the communication system"""
        kosha_info = KoshaInfo(
            id=kosha_id,
            type=kosha_type,
            capabilities=capabilities or [],
            endpoint=endpoint
        )
        await self.registry.register_kosha(kosha_info)
        logging.info(f"Registered kosha: {kosha_id} (type: {kosha_type})")
    
    async def unregister_kosha(self, kosha_id: str):
        """Unregister a kosha from the communication system"""
        await self.registry.unregister_kosha(kosha_id)
        logging.info(f"Unregistered kosha: {kosha_id}")
    
    def register_handler(self, kosha_id: str, handler: MessageHandler):
        """Register a message handler for a specific kosha"""
        self.handlers[kosha_id] = handler
        logging.info(f"Registered message handler for kosha: {kosha_id}")
    
    def register_callback(self, message_type: str, callback: Callable[[Message], Awaitable[None]]):
        """Register a callback for a specific message type"""
        self.message_callbacks[message_type] = callback
        logging.info(f"Registered callback for message type: {message_type}")
    
    async def send_message(self, message: Message) -> Optional[Message]:
        """Send a message to another kosha"""
        if not message.target_id:  # Broadcast message
            await self._broadcast_message(message)
            return None
        
        # Check if target kosha exists
        target_kosha = await self.registry.get_kosha(message.target_id)
        if not target_kosha:
            logging.warning(f"Target kosha {message.target_id} not found")
            return None
        
        # Add to message queue
        if self.message_queue.put(message):
            logging.debug(f"Message queued: {message.id} from {message.source_id} to {message.target_id}")
            
            # If it's a request, create a future to wait for response
            if message.type == MessageType.REQUEST:
                future = asyncio.get_event_loop().create_future()
                self.pending_requests[message.id] = future
                
                # Wait for response with timeout
                try:
                    if message.timeout:
                        response = await asyncio.wait_for(future, timeout=message.timeout)
                    else:
                        response = await future
                    return response
                except asyncio.TimeoutError:
                    # Remove the future from pending requests
                    self.pending_requests.pop(message.id, None)
                    logging.warning(f"Request {message.id} timed out")
                    return None
        else:
            logging.warning(f"Message queue full, dropping message {message.id}")
            return None
    
    async def _broadcast_message(self, message: Message):
        """Broadcast a message to all registered koshas"""
        all_koshas = await self.registry.get_all_koshas()
        for kosha in all_koshas:
            if kosha.id != message.source_id:  # Don't send to self
                broadcast_msg = Message(
                    id=str(uuid.uuid4()),
                    source_id=message.source_id,
                    target_id=kosha.id,
                    type=message.type,
                    priority=message.priority,
                    content=message.content,
                    timestamp=message.timestamp,
                    correlation_id=message.correlation_id
                )
                if self.message_queue.put(broadcast_msg):
                    logging.debug(f"Broadcast message queued: {broadcast_msg.id}")
    
    async def _process_messages(self):
        """Process messages from the queue"""
        while self._running:
            message = self.message_queue.get()
            if message:
                await self._handle_message(message)
            else:
                # No messages, wait a bit before checking again
                await asyncio.sleep(0.01)
    
    async def _handle_message(self, message: Message):
        """Handle an incoming message"""
        logging.debug(f"Processing message {message.id} of type {message.type} for target {message.target_id}")
        
        # Check if this is a response to a pending request
        if message.type == MessageType.RESPONSE and message.correlation_id in self.pending_requests:
            future = self.pending_requests.pop(message.correlation_id, None)
            if future and not future.done():
                future.set_result(message)
            return
        
        # If target is specified, route to that kosha's handler
        if message.target_id and message.target_id in self.handlers:
            handler = self.handlers[message.target_id]
            try:
                response = await handler.handle_message(message)
                if response:
                    # Send response back if it's not a broadcast
                    if message.source_id:
                        response.target_id = message.source_id
                        response.source_id = message.target_id
                        self.message_queue.put(response)
            except Exception as e:
                logging.error(f"Error handling message {message.id}: {str(e)}")
                error_response = Message(
                    type=MessageType.ERROR,
                    source_id=message.target_id,
                    target_id=message.source_id,
                    content={"error": str(e), "original_id": message.id},
                    correlation_id=message.id
                )
                self.message_queue.put(error_response)
        else:
            # No specific target or handler, check for general callbacks
            if message.type.value in self.message_callbacks:
                callback = self.message_callbacks[message.type.value]
                try:
                    await callback(message)
                except Exception as e:
                    logging.error(f"Error in callback for message {message.id}: {str(e)}")
            else:
                # No handler or callback, use default handler
                default_handler = DefaultMessageHandler()
                try:
                    response = await default_handler.handle_message(message)
                    if response:
                        self.message_queue.put(response)
                except Exception as e:
                    logging.error(f"Error in default handler for message {message.id}: {str(e)}")
    
    async def send_request(self, source_id: str, target_id: str, content: Dict[str, Any], timeout: int = 30) -> Optional[Message]:
        """Send a request and wait for a response"""
        message = Message(
            source_id=source_id,
            target_id=target_id,
            type=MessageType.REQUEST,
            content=content,
            timeout=timeout
        )
        return await self.send_message(message)
    
    async def broadcast_notification(self, source_id: str, content: Dict[str, Any], message_type: MessageType = MessageType.NOTIFICATION):
        """Send a broadcast notification to all koshas"""
        message = Message(
            source_id=source_id,
            target_id="",  # Empty target for broadcast
            type=message_type,
            content=content
        )
        await self._broadcast_message(message)
    
    async def get_kosha_status(self, kosha_id: str) -> Optional[KoshaStatus]:
        """Get the status of a specific kosha"""
        kosha_info = await self.registry.get_kosha(kosha_id)
        return kosha_info.status if kosha_info else None
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        koshas = await self.registry.get_all_koshas()
        active_koshas = [k for k in koshas if k.status == KoshaStatus.ACTIVE]
        busy_koshas = [k for k in koshas if k.status == KoshaStatus.BUSY]
        inactive_koshas = [k for k in koshas if k.status == KoshaStatus.INACTIVE]
        
        return {
            "total_koshas": len(koshas),
            "active_koshas": len(active_koshas),
            "busy_koshas": len(busy_koshas),
            "inactive_koshas": len(inactive_koshas),
            "message_queue_size": self.message_queue.size(),
            "pending_requests": len(self.pending_requests)
        }
    
    async def heartbeat_kosha(self, kosha_id: str) -> bool:
        """Update the heartbeat for a kosha"""
        success = await self.registry.update_kosha_status(kosha_id, KoshaStatus.ACTIVE)
        if success:
            logging.debug(f"Heartbeat updated for kosha: {kosha_id}")
        else:
            logging.warning(f"Failed to update heartbeat for kosha: {kosha_id}")
        return success
    
    async def update_kosha_load(self, kosha_id: str, load: float) -> bool:
        """Update the load of a kosha"""
        success = await self.registry.update_kosha_load(kosha_id, load)
        if success:
            logging.debug(f"Load updated for kosha {kosha_id}: {load}")
        else:
            logging.warning(f"Failed to update load for kosha: {kosha_id}")
        return success
    
    async def find_koshas_with_capability(self, capability: str) -> List[KoshaInfo]:
        """Find all koshas that have a specific capability"""
        all_koshas = await self.registry.get_all_koshas()
        return [
            k for k in all_koshas 
            if capability in k.capabilities and k.status in [KoshaStatus.ACTIVE, KoshaStatus.BUSY]
        ]


def create_inter_kosha_demo():
    """Create a demo of the inter-kosha communication system"""
    import asyncio
    
    async def demo():
        print("=== Augur Omega: Inter-Kosha Communication System Demo ===\n")
        
        # Initialize the communication system
        communicator = InterKoshaCommunicator()
        await communicator.start()
        
        # Register some sample koshas
        await communicator.register_kosha("PRIME_001", "prime_kosha", ["strategic_planning", "system_coordination"])
        await communicator.register_kosha("DOMAIN_001", "domain_kosha", ["financial_analysis", "risk_assessment"])
        await communicator.register_kosha("MICRO_001", "microagent", ["data_processing", "calculation"])
        await communicator.register_kosha("DOMAIN_002", "domain_kosha", ["technical_integration", "api_management"])
        
        # Register handlers for the koshas
        class PrimeKoshaHandler(MessageHandler):
            async def handle_message(self, message: Message) -> Optional[Message]:
                print(f"PRIME_001 received {message.type.value} message: {message.content}")
                if message.type == MessageType.REQUEST:
                    return Message(
                        type=MessageType.RESPONSE,
                        source_id="PRIME_001",
                        target_id=message.source_id,
                        content={"decision": "approved", "strategy": "optimal_path"},
                        correlation_id=message.id
                    )
                return None
        
        class DomainKoshaHandler(MessageHandler):
            async def handle_message(self, message: Message) -> Optional[Message]:
                print(f"DOMAIN_001 received {message.type.value} message: {message.content}")
                if message.type == MessageType.REQUEST:
                    return Message(
                        type=MessageType.RESPONSE,
                        source_id="DOMAIN_001",
                        target_id=message.source_id,
                        content={"analysis": "completed", "risk_level": "medium"},
                        correlation_id=message.id
                    )
                return None
        
        class MicroAgentHandler(MessageHandler):
            async def handle_message(self, message: Message) -> Optional[Message]:
                print(f"MICRO_001 received {message.type.value} message: {message.content}")
                if message.type == MessageType.REQUEST:
                    return Message(
                        type=MessageType.RESPONSE,
                        source_id="MICRO_001",
                        target_id=message.source_id,
                        content={"processed": True, "result": "calculation_complete"},
                        correlation_id=message.id
                    )
                return None
        
        communicator.register_handler("PRIME_001", PrimeKoshaHandler())
        communicator.register_handler("DOMAIN_001", DomainKoshaHandler())
        communicator.register_handler("MICRO_001", MicroAgentHandler())
        
        print("Registered 4 koshas with handlers\n")
        
        # Test sending a request from PRIME_001 to DOMAIN_001
        print("1. Testing request-response between koshas:")
        response = await communicator.send_request(
            source_id="PRIME_001",
            target_id="DOMAIN_001",
            content={"request": "perform_risk_analysis", "data": {"investment": 1000000, "duration": 12}}
        )
        if response:
            print(f"   Response: {response.content}\n")
        
        # Test broadcasting a message
        print("2. Testing broadcast message:")
        await communicator.broadcast_notification(
            source_id="PRIME_001",
            content={"notification": "system_status_update", "status": "operational"}
        )
        await asyncio.sleep(0.1)  # Allow time for processing
        print("   Broadcast sent\n")
        
        # Test finding koshas with specific capabilities
        print("3. Testing capability-based discovery:")
        financial_koshas = await communicator.find_koshas_with_capability("financial_analysis")
        print(f"   Koshas with financial_analysis capability: {[k.id for k in financial_koshas]}\n")
        
        # Test system status
        print("4. Testing system status:")
        status = await communicator.get_system_status()
        print(f"   System Status: {status}\n")
        
        # Update kosha loads
        print("5. Testing load updates:")
        await communicator.update_kosha_load("PRIME_001", 0.7)
        await communicator.update_kosha_load("DOMAIN_001", 0.3)
        print("   Updated kosha loads\n")
        
        # Test heartbeat
        print("6. Testing heartbeat:")
        success = await communicator.heartbeat_kosha("MICRO_001")
        print(f"   Heartbeat success: {success}\n")
        
        # Stop the communication system
        await communicator.stop()
        print("Inter-Kosha Communication System demo completed!")
    
    # Run the demo
    asyncio.run(demo())


if __name__ == "__main__":
    create_inter_kosha_demo()