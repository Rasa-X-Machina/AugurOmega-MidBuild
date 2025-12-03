"""
Augur Omega: Inter-Kosha Communication System
Manages communication between all koshas in the system.
Includes specialized handlers for LLM Gateways (Minimax) and Recursive Builders.
"""
import asyncio
import json
import uuid
import os
import logging
import queue
import threading
from enum import Enum
from typing import Dict, List, Any, Optional, Callable, Awaitable
from dataclasses import dataclass, field
from datetime import datetime
from abc import ABC, abstractmethod

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- IMPORT THE SANITIZER ---
try:
    # Assuming message_utils.py is in the same directory
    from .message_utils import sanitize_message_history
except ImportError:
    # Fallback/Mock for standalone testing if file is missing
    logging.warning("message_utils.py not found. Using identity function for sanitization.")
    def sanitize_message_history(msgs: List[Dict[str, Any]]) -> List[Dict[str, Any]]: return msgs

# --- CORE DEFINITIONS ---

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
    type: str  # prime_kosha, domain_kosha, microagent, gateway, builder
    status: KoshaStatus = KoshaStatus.ACTIVE
    capabilities: List[str] = field(default_factory=list)
    last_heartbeat: Optional[str] = None
    endpoint: Optional[str] = None
    response_time: float = 0.0
    load: float = 0.0  # 0.0 to 1.0

# --- HANDLER ABSTRACTIONS ---

class MessageHandler(ABC):
    """Abstract base class for message handlers"""
    @abstractmethod
    async def handle_message(self, message: Message) -> Optional[Message]:
        """Handle an incoming message and optionally return a response"""
        pass

class DefaultMessageHandler(MessageHandler):
    """Default message handler for basic message types"""
    async def handle_message(self, message: Message) -> Optional[Message]:
        if message.type == MessageType.HEARTBEAT:
            return Message(
                type=MessageType.RESPONSE,
                source_id=message.target_id,
                target_id=message.source_id,
                content={"status": "alive"},
                correlation_id=message.id
            )
        elif message.type == MessageType.SYNCHRONIZATION:
            return Message(
                type=MessageType.RESPONSE,
                source_id=message.target_id,
                target_id=message.source_id,
                content={"synchronized": True},
                correlation_id=message.id
            )
        else:
            return Message(
                type=MessageType.RESPONSE,
                source_id=message.target_id,
                target_id=message.source_id,
                content={"acknowledged": True, "original_id": message.id},
                correlation_id=message.id
            )

# --- SPECIALIZED HANDLERS ---

class MinimaxGatewayHandler(MessageHandler):
    """
    Acts as a proxy to the Minimax API.
    Handles history tracking and sanitization (Fix for Error 2013).
    """
    def __init__(self, api_client, model_name="abab6.5s-chat"):
        self.client = api_client
        self.model_name = model_name
        self.conversation_history = [] 

    async def handle_message(self, message: Message) -> Optional[Message]:
        if message.type != MessageType.REQUEST:
            return None

        user_prompt = message.content.get("prompt")
        tools_def = message.content.get("tools", [])
        
        # Update internal history
        self.conversation_history.append({"role": "user", "content": user_prompt})

        try:
            # SANITIZATION STEP
            clean_messages = sanitize_message_history(self.conversation_history)
            
            logging.info(f"Gateway: Sending {len(clean_messages)} messages to Minimax...")

            # Execute API call in a separate thread to avoid blocking asyncio loop
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.model_name,
                messages=clean_messages,
                tools=tools_def if tools_def else None
            )

            response_text = response.choices[0].message.content
            self.conversation_history.append({"role": "assistant", "content": response_text})

            return Message(
                type=MessageType.RESPONSE,
                source_id=message.target_id,
                target_id=message.source_id,
                content={"llm_response": response_text},
                correlation_id=message.id
            )
        except Exception as e:
            logging.error(f"Minimax API Error: {str(e)}")
            return Message(
                type=MessageType.ERROR,
                source_id=message.target_id,
                target_id=message.source_id,
                content={"error": str(e)},
                correlation_id=message.id
            )

class RecursiveBuilderKosha(MessageHandler):
    """
    A Supervisor Agent that generates a list of files sequentially.
    Fixes the 'stops after one file' issue by maintaining an internal queue.
    """
    def __init__(self, communicator, target_llm_id, output_dir="."):
        self.communicator = communicator
        self.target_llm_id = target_llm_id
        self.output_dir = output_dir
        self.build_queue = []
        self.is_building = False

    async def queue_build(self, file_manifest: List[str]):
        """Accepts a list of filenames/descriptions to build."""
        self.build_queue.extend(file_manifest)
        logging.info(f"Builder: Queued {len(file_manifest)} files.")
        if not self.is_building:
            asyncio.create_task(self._process_next())

    async def _process_next(self):
        """The internal loop that keeps the builder moving."""
        if not self.build_queue:
            self.is_building = False
            logging.info("Builder: ✅ All files generated.")
            return

        self.is_building = True
        current_file = self.build_queue.pop(0)
        logging.info(f"Builder: 🔨 processing {current_file}...")

        # Request code generation from LLM Gateway
        response = await self.communicator.send_request(
            source_id="BUILDER_SYS",
            target_id=self.target_llm_id,
            content={
                "prompt": f"Generate the full Python code for the file: {current_file}. Return ONLY code inside markdown blocks.",
            },
            timeout=120 
        )

        if response and "llm_response" in response.content:
            self._write_to_disk(current_file, response.content["llm_response"])
            # Recursion delay to yield control
            await asyncio.sleep(0.5) 
            await self._process_next() 
        else:
            logging.error(f"Builder: ❌ FAILED {current_file}. Retrying in 5s...")
            self.build_queue.insert(0, current_file) # Re-queue
            await asyncio.sleep(5)
            await self._process_next()

    def _write_to_disk(self, filename, content):
        # Strip markdown code blocks
        clean_content = content.replace("```python", "").replace("```", "").strip()
        
        # Ensure directory exists
        path = os.path.join(self.output_dir, filename)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        with open(path, "w", encoding="utf-8") as f:
            f.write(clean_content)
        logging.info(f"Builder: 💾 SAVED {path}")

    async def handle_message(self, message: Message) -> Optional[Message]:
        # Listen for build commands
        if message.type == MessageType.REQUEST and "build_manifest" in message.content:
            await self.queue_build(message.content["build_manifest"])
            return Message(
                type=MessageType.RESPONSE, 
                source_id=message.target_id,
                target_id=message.source_id,
                content={"status": "Build Started", "queue_length": len(self.build_queue)},
                correlation_id=message.id
            )
        return None

# --- CORE REGISTRY & COMMUNICATOR ---

class KoshaRegistry:
    """Registry to keep track of all koshas in the system"""
    def __init__(self):
        self._koshas: Dict[str, KoshaInfo] = {}
        self._lock = asyncio.Lock()
    
    async def register_kosha(self, kosha_info: KoshaInfo) -> bool:
        async with self._lock:
            self._koshas[kosha_info.id] = kosha_info
            return True
    
    async def unregister_kosha(self, kosha_id: str) -> bool:
        async with self._lock:
            if kosha_id in self._koshas:
                del self._koshas[kosha_id]
                return True
            return False
    
    async def get_kosha(self, kosha_id: str) -> Optional[KoshaInfo]:
        async with self._lock:
            return self._koshas.get(kosha_id)
    
    async def get_all_koshas(self) -> List[KoshaInfo]:
        async with self._lock:
            return list(self._koshas.values())

    async def update_kosha_status(self, kosha_id: str, status: KoshaStatus) -> bool:
        async with self._lock:
            if kosha_id in self._koshas:
                self._koshas[kosha_id].status = status
                self._koshas[kosha_id].last_heartbeat = datetime.now().isoformat()
                return True
            return False

class MessageQueue:
    """Thread-safe message queue"""
    def __init__(self, maxsize: int = 0):
        self._queue = queue.Queue(maxsize=maxsize)
    def put(self, message: Message) -> bool:
        try:
            self._queue.put(message, block=False)
            return True
        except queue.Full:
            return False
    def get(self) -> Optional[Message]:
        try:
            return self._queue.get(block=False)
        except queue.Empty:
            return None
    def size(self) -> int:
        return self._queue.qsize()

class InterKoshaCommunicator:
    """Manages communication between all koshas in the system"""
    def __init__(self):
        self.registry = KoshaRegistry()
        self.message_queue = MessageQueue(maxsize=10000)
        self.handlers: Dict[str, MessageHandler] = {}
        self.pending_requests: Dict[str, asyncio.Future] = {}
        self._running = False
        self._message_processing_task = None

    async def start(self):
        self._running = True
        self._message_processing_task = asyncio.create_task(self._process_messages())
        logging.info("Inter-Kosha Communication System started")

    async def stop(self):
        self._running = False
        if self._message_processing_task:
            self._message_processing_task.cancel()
        # Cancel pending
        for future in self.pending_requests.values():
            if not future.done(): future.cancel()
        logging.info("Inter-Kosha Communication System stopped")

    def register_handler(self, kosha_id: str, handler: MessageHandler):
        self.handlers[kosha_id] = handler

    async def register_kosha(self, kosha_id: str, kosha_type: str, capabilities: List[str] = None):
        await self.registry.register_kosha(KoshaInfo(id=kosha_id, type=kosha_type, capabilities=capabilities if capabilities is not None else []))

    async def send_message(self, message: Message) -> Optional[Message]:
        if not message.target_id: return None # Broadcast logic simplified for brevity
        
        if self.message_queue.put(message):
            if message.type == MessageType.REQUEST:
                future = asyncio.get_event_loop().create_future()
                self.pending_requests[message.id] = future
                try:
                    if message.timeout:
                        return await asyncio.wait_for(future, timeout=message.timeout)
                    else:
                        return await future
                except asyncio.TimeoutError:
                    self.pending_requests.pop(message.id, None)
                    return None
        return None

    async def send_request(self, source_id: str, target_id: str, content: Dict[str, Any], timeout: int = 30) -> Optional[Message]:
        message = Message(
            source_id=source_id, target_id=target_id, type=MessageType.REQUEST,
            content=content, timeout=timeout
        )
        return await self.send_message(message)

    async def get_system_status(self) -> Dict[str, Any]:
        koshas = await self.registry.get_all_koshas()
        return {
            "total_koshas": len(koshas),
            "queue_size": self.message_queue.size(),
            "pending_requests": len(self.pending_requests)
        }

    async def _process_messages(self):
        while self._running:
            message = self.message_queue.get()
            if message:
                await self._handle_message(message)
            else:
                await asyncio.sleep(0.01)

    async def _handle_message(self, message: Message):
        # 1. Handle Response correlation
        if message.type == MessageType.RESPONSE and message.correlation_id in self.pending_requests:
            future = self.pending_requests.pop(message.correlation_id, None)
            if future and not future.done():
                future.set_result(message)
            return
        
        # 2. Route to Handler
        if message.target_id in self.handlers:
            handler = self.handlers[message.target_id]
            try:
                response = await handler.handle_message(message)
                if response:
                    # Route response back to source
                    response.target_id = message.source_id
                    response.source_id = message.target_id
                    self.message_queue.put(response)
            except Exception as e:
                logging.error(f"Error handling message {message.id}: {str(e)}")

# --- MAIN EXECUTION: PERSISTENT SERVER ---

async def run_persistent_server():
    """
    Starts the Augur-Omega system and keeps it running indefinitely.
    Replaces the 'Demo' mode.
    """
    print("\n=== Augur Omega: Inter-Kosha System (Persistent Mode) ===")
    
    # 1. Initialize
    communicator = InterKoshaCommunicator()
    await communicator.start()

    # 2. Setup Mock or Real Client (Replace with your actual Minimax/OpenAI Client init)
    # EXAMPLE: client = openai.OpenAI(api_key="...", base_url="https://api.minimax.chat/v1")
    class MockClient: 
        class choices:
            class message: content = "def generated_code():\n    pass"
            def __getitem__(self, i): return self
        class chat:
            class completions:
                def create(*args, **kwargs): return MockClient()
    
    # 3. Register System Agents
    # Gateway Agent (Talks to LLM)
    await communicator.register_kosha("MINIMAX_GATEWAY", "gateway", ["llm_access"])
    communicator.register_handler("MINIMAX_GATEWAY", MinimaxGatewayHandler(api_client=MockClient()))
    
    # Builder Agent (Orchestrates Files)
    await communicator.register_kosha("OMEGA_BUILDER", "builder", ["file_generation"])
    # Pass 'MINIMAX_GATEWAY' as the target for the builder to use
    communicator.register_handler("OMEGA_BUILDER", RecursiveBuilderKosha(communicator, "MINIMAX_GATEWAY"))

    print("✅ System Initialized. Active Koshas: MINIMAX_GATEWAY, OMEGA_BUILDER")

    # 4. (Optional) Trigger an immediate build of a manifest
    # Uncomment below to start a build on launch:
    '''
    initial_manifest = ["utils.py", "models.py", "config.py"]
    await communicator.send_request(
        source_id="USER_CLI", 
        target_id="OMEGA_BUILDER", 
        content={"build_manifest": initial_manifest}
    )
    '''

    # 5. Keep-Alive Loop
    try:
        while True:
            await asyncio.sleep(60)
            status = await communicator.get_system_status()
            logging.info(f"System Heartbeat: {status}")
    except KeyboardInterrupt:
        print("\nShutting down Augur Omega...")
    finally:
        await communicator.stop()

if __name__ == "__main__":
    try:
        asyncio.run(run_persistent_server())
    except KeyboardInterrupt:
        pass