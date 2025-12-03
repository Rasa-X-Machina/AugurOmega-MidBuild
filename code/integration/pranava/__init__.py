"""
Pranava: Orchestration Signal Router for Triumvirate Integration Layer

Pranava manages intelligent orchestration signals, routing, and coordination
across the triumvirate ecosystem, providing adaptive load balancing and
dynamic workflow management.
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Set, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import uuid

from ..shared.base import TriumvirateComponent, ComponentType, TriumvirateMessage, MessagePriority
from ..shared.messaging import MessageRouter
from ..shared.discovery import ServiceDiscovery

class SignalType(Enum):
    ROUTING = "routing"
    COORDINATION = "coordination"
    HEALTH_CHECK = "health_check"
    LOAD_BALANCE = "load_balance"
    WORKFLOW = "workflow"
    PRIORITY = "priority"
    SCALING = "scaling"
    ERROR_RECOVERY = "error_recovery"

class RoutingStrategy(Enum):
    ROUND_ROBIN = "round_robin"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_CONNECTIONS = "least_connections"
    LEAST_RESPONSE_TIME = "least_response_time"
    HASH_BASED = "hash_based"
    INTELLIGENT = "intelligent"

class WorkflowStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"

@dataclass
class OrchestrationSignal:
    """Orchestration signal structure"""
    signal_id: str
    signal_type: SignalType
    source: ComponentType
    target: ComponentType
    payload: Dict[str, Any]
    priority: MessagePriority
    timestamp: datetime
    correlation_id: Optional[str] = None
    routing_context: Dict[str, Any] = None
    ttl: Optional[int] = None

@dataclass
class WorkflowStep:
    """Step in an orchestration workflow"""
    step_id: str
    component_type: ComponentType
    operation: str
    parameters: Dict[str, Any]
    dependencies: List[str]  # step_ids that must complete first
    status: WorkflowStatus = WorkflowStatus.PENDING
    result: Any = None
    error: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

@dataclass
class Workflow:
    """Orchestration workflow definition"""
    workflow_id: str
    name: str
    steps: List[WorkflowStep]
    created_by: ComponentType
    created_at: datetime
    priority: MessagePriority = MessagePriority.NORMAL
    status: WorkflowStatus = WorkflowStatus.PENDING
    correlation_id: Optional[str] = None

class PranavaOrchestrator(TriumvirateComponent):
    """
    Pranava: Central orchestration and signal routing component
    Manages workflows, load balancing, and intelligent routing
    """
    
    def __init__(self, component_id: str = "primary"):
        super().__init__(ComponentType.PRANAVA, component_id)
        
        # Signal management
        self.active_signals: Dict[str, OrchestrationSignal] = {}
        self.signal_handlers: Dict[SignalType, Callable] = {}
        self.routing_table: Dict[str, List[str]] = {}  # capability -> component_ids
        
        # Workflow management
        self.active_workflows: Dict[str, Workflow] = {}
        self.workflow_templates: Dict[str, Dict[str, Any]] = {}
        self.workflow_state: Dict[str, Dict[str, Any]] = {}
        
        # Load balancing
        self.routing_strategies: Dict[str, RoutingStrategy] = {}
        self.component_load: Dict[str, float] = {}
        self.component_response_times: Dict[str, List[float]] = {}
        self.connection_counts: Dict[str, int] = {}
        
        # Performance tracking
        self.orchestration_stats = {
            "signals_processed": 0,
            "workflows_started": 0,
            "workflows_completed": 0,
            "routing_decisions": 0,
            "average_signal_latency": 0.0
        }
        
        # Health monitoring
        self.health_check_interval = 30  # seconds
        self.component_health: Dict[str, Dict[str, Any]] = {}
        
        self.logger = logging.getLogger("PranavaOrchestrator")
        
    async def initialize(self) -> None:
        """Initialize Pranava orchestrator"""
        self.logger.info("Initializing Pranava orchestrator")
        
        # Register signal handlers
        self.register_handler("signal.process", self._handle_signal_processing)
        self.register_handler("workflow.create", self._handle_workflow_creation)
        self.register_handler("workflow.execute", self._handle_workflow_execution)
        self.register_handler("routing.request", self._handle_routing_request)
        self.register_handler("load.update", self._handle_load_update)
        self.register_handler("health.check", self._handle_health_check)
        
        # Set up default routing strategies
        self.routing_strategies["default"] = RoutingStrategy.INTELLIGENT
        self.routing_strategies["realtime"] = RoutingStrategy.LEAST_RESPONSE_TIME
        self.routing_strategies["batch"] = RoutingStrategy.ROUND_ROBIN
        self.routing_strategies["compute_intensive"] = RoutingStrategy.WEIGHTED_ROUND_ROBIN
        
        # Start background tasks
        asyncio.create_task(self._health_monitor_loop())
        asyncio.create_task(self._signal_cleanup_loop())
        
        self.logger.info("Pranava orchestrator initialized")
        
    async def shutdown(self) -> None:
        """Shutdown Pranava orchestrator"""
        self.logger.info("Shutting down Pranava orchestrator")
        
    async def _route_message(self, message: TriumvirateMessage) -> bool:
        """Route message to appropriate handler"""
        return await self.receive_message(message)
        
    async def create_signal(self, signal_type: SignalType, source: ComponentType,
                          target: ComponentType, payload: Dict[str, Any],
                          priority: MessagePriority = MessagePriority.NORMAL,
                          routing_context: Dict[str, Any] = None) -> OrchestrationSignal:
        """Create a new orchestration signal"""
        signal = OrchestrationSignal(
            signal_id=str(uuid.uuid4()),
            signal_type=signal_type,
            source=source,
            target=target,
            payload=payload,
            priority=priority,
            timestamp=datetime.now(),
            routing_context=routing_context or {}
        )
        
        self.active_signals[signal.signal_id] = signal
        self.logger.debug(f"Created signal {signal.signal_id}: {signal_type.value}")
        
        return signal
        
    async def process_signal(self, signal: OrchestrationSignal) -> bool:
        """Process an orchestration signal"""
        try:
            start_time = datetime.now()
            
            # Update stats
            self.orchestration_stats["signals_processed"] += 1
            
            # Route signal based on type and routing context
            success = await self._route_signal(signal)
            
            # Update latency stats
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            self._update_signal_latency(processing_time)
            
            if success:
                self.logger.debug(f"Successfully processed signal {signal.signal_id}")
            else:
                self.logger.warning(f"Failed to process signal {signal.signal_id}")
                
            return success
            
        except Exception as e:
            self.logger.error(f"Error processing signal {signal.signal_id}: {e}")
            return False
            
    async def create_workflow(self, workflow_id: str, name: str, 
                            steps: List[WorkflowStep], created_by: ComponentType,
                            correlation_id: str = None) -> Workflow:
        """Create a new orchestration workflow"""
        workflow = Workflow(
            workflow_id=workflow_id,
            name=name,
            steps=steps,
            created_by=created_by,
            created_at=datetime.now(),
            correlation_id=correlation_id
        )
        
        self.active_workflows[workflow_id] = workflow
        self.workflow_state[workflow_id] = {
            "current_step": 0,
            "completed_steps": [],
            "failed_steps": [],
            "start_time": None,
            "end_time": None
        }
        
        self.logger.info(f"Created workflow: {workflow_id}")
        return workflow
        
    async def execute_workflow(self, workflow: Workflow) -> bool:
        """Execute an orchestration workflow"""
        try:
            self.orchestration_stats["workflows_started"] += 1
            workflow.status = WorkflowStatus.RUNNING
            workflow_state = self.workflow_state[workflow.workflow_id]
            workflow_state["start_time"] = datetime.now()
            
            self.logger.info(f"Starting workflow execution: {workflow.workflow_id}")
            
            # Execute steps according to dependencies
            await self._execute_workflow_steps(workflow)
            
            workflow.status = WorkflowStatus.COMPLETED
            workflow_state["end_time"] = datetime.now()
            self.orchestration_stats["workflows_completed"] += 1
            
            self.logger.info(f"Completed workflow execution: {workflow.workflow_id}")
            return True
            
        except Exception as e:
            workflow.status = WorkflowStatus.FAILED
            self.logger.error(f"Workflow execution failed: {workflow.workflow_id}: {e}")
            return False
            
    async def intelligent_route(self, capability_required: str, 
                              routing_hints: Dict[str, Any] = None) -> Optional[str]:
        """Intelligently route based on multiple factors"""
        try:
            self.orchestration_stats["routing_decisions"] += 1
            
            routing_context = routing_hints or {}
            strategy_name = routing_context.get("strategy", "default")
            strategy = self.routing_strategies.get(strategy_name, RoutingStrategy.INTELLIGENT)
            
            candidates = self._get_routing_candidates(capability_required)
            if not candidates:
                self.logger.warning(f"No candidates for capability: {capability_required}")
                return None
                
            selected_target = await self._apply_routing_strategy(candidates, strategy, routing_context)
            
            if selected_target:
                self.logger.debug(f"Intelligently routed {capability_required} to {selected_target}")
                return selected_target
            else:
                # Fallback to any available target
                return next(iter(candidates))
                
        except Exception as e:
            self.logger.error(f"Intelligent routing failed: {e}")
            return None
            
    def _get_routing_candidates(self, capability_required: str) -> Set[str]:
        """Get candidate components for routing"""
        candidates = set()
        
        # Check routing table
        if capability_required in self.routing_table:
            candidates.update(self.routing_table[capability_required])
            
        # Check component health
        healthy_candidates = set()
        for candidate in candidates:
            if self._is_component_healthy(candidate):
                healthy_candidates.add(candidate)
                
        return healthy_candidates
        
    def _is_component_healthy(self, component_id: str) -> bool:
        """Check if a component is healthy"""
        health_info = self.component_health.get(component_id, {})
        return health_info.get("status") == "healthy"
        
    async def _apply_routing_strategy(self, candidates: Set[str], 
                                    strategy: RoutingStrategy,
                                    context: Dict[str, Any]) -> Optional[str]:
        """Apply routing strategy to select target"""
        if not candidates:
            return None
            
        candidates_list = list(candidates)
        
        if strategy == RoutingStrategy.ROUND_ROBIN:
            # Simple round-robin based on hash
            hash_seed = context.get("hash_seed", "")
            selected = hash(hash_seed) % len(candidates_list)
            return candidates_list[selected]
            
        elif strategy == RoutingStrategy.WEIGHTED_ROUND_ROBIN:
            # Weight by inverse load
            weights = [(1.0 - self.component_load.get(c, 0.0)) for c in candidates_list]
            import random
            total_weight = sum(weights)
            if total_weight == 0:
                return candidates_list[0]
            r = random.uniform(0, total_weight)
            upto = 0
            for i, weight in enumerate(weights):
                upto += weight
                if r <= upto:
                    return candidates_list[i]
            return candidates_list[-1]
            
        elif strategy == RoutingStrategy.LEAST_CONNECTIONS:
            # Choose component with least connections
            connection_counts = [self.connection_counts.get(c, 0) for c in candidates_list]
            min_connections = min(connection_counts)
            min_index = connection_counts.index(min_connections)
            return candidates_list[min_index]
            
        elif strategy == RoutingStrategy.LEAST_RESPONSE_TIME:
            # Choose component with best response time
            response_times = []
            for candidate in candidates_list:
                times = self.component_response_times.get(candidate, [])
                avg_time = sum(times) / len(times) if times else 1000.0  # Default high time
                response_times.append(avg_time)
            min_time = min(response_times)
            min_index = response_times.index(min_time)
            return candidates_list[min_index]
            
        elif strategy == RoutingStrategy.HASH_BASED:
            # Hash-based routing for consistency
            hash_key = context.get("hash_key", "")
            if hash_key:
                hash_value = int(hashlib.md5(hash_key.encode()).hexdigest(), 16)
                selected = hash_value % len(candidates_list)
                return candidates_list[selected]
            else:
                return candidates_list[0]
                
        elif strategy == RoutingStrategy.INTELLIGENT:
            # Combine multiple factors
            scores = {}
            for candidate in candidates_list:
                score = 0.0
                
                # Load factor (lower is better)
                load = self.component_load.get(candidate, 0.5)
                score += (1.0 - load) * 40
                
                # Connection count (fewer is better)
                connections = self.connection_counts.get(candidate, 0)
                if connections > 0:
                    score += max(0, 20 - connections * 2)
                
                # Response time (lower is better)
                times = self.component_response_times.get(candidate, [])
                if times:
                    avg_time = sum(times[-10:]) / min(10, len(times))  # Recent avg
                    score += max(0, 30 - avg_time / 10)  # Normalize
                
                # Health status
                if self._is_component_healthy(candidate):
                    score += 10
                
                scores[candidate] = score
                
            # Return component with highest score
            return max(scores, key=scores.get)
            
        else:
            # Default fallback
            return candidates_list[0]
            
    def update_component_load(self, component_id: str, load_factor: float) -> None:
        """Update component load factor"""
        self.component_load[component_id] = max(0.0, min(1.0, load_factor))
        self.logger.debug(f"Updated load for {component_id}: {load_factor}")
        
    def update_component_response_time(self, component_id: str, response_time_ms: float) -> None:
        """Update component response time"""
        if component_id not in self.component_response_times:
            self.component_response_times[component_id] = []
            
        times = self.component_response_times[component_id]
        times.append(response_time_ms)
        
        # Keep only recent times
        if len(times) > 100:
            self.component_response_times[component_id] = times[-100:]
            
    def update_component_connections(self, component_id: str, count: int) -> None:
        """Update active connection count"""
        self.connection_counts[component_id] = max(0, count)
        
    async def _route_signal(self, signal: OrchestrationSignal) -> bool:
        """Route signal based on type and context"""
        if signal.signal_type == SignalType.ROUTING:
            return await self._route_routing_signal(signal)
        elif signal.signal_type == SignalType.COORDINATION:
            return await self._route_coordination_signal(signal)
        elif signal.signal_type == SignalType.HEALTH_CHECK:
            return await self._route_health_signal(signal)
        elif signal.signal_type == SignalType.LOAD_BALANCE:
            return await self._route_load_signal(signal)
        elif signal.signal_type == SignalType.WORKFLOW:
            return await self._route_workflow_signal(signal)
        else:
            self.logger.warning(f"Unknown signal type: {signal.signal_type}")
            return False
            
    async def _route_routing_signal(self, signal: OrchestrationSignal) -> bool:
        """Route routing signal"""
        capability = signal.payload.get("capability")
        routing_hints = signal.routing_context or {}
        
        target = await self.intelligent_route(capability, routing_hints)
        if target:
            # Send routing signal to target
            return True
        return False
        
    async def _route_coordination_signal(self, signal: OrchestrationSignal) -> bool:
        """Route coordination signal"""
        coordination_type = signal.payload.get("type")
        participants = signal.payload.get("participants", [])
        
        # Send coordination signal to all participants
        for participant in participants:
            # Implementation would send signal to participant
            pass
            
        return True
        
    async def _route_health_signal(self, signal: OrchestrationSignal) -> bool:
        """Route health check signal"""
        component_id = signal.payload.get("component_id")
        if component_id in self.component_health:
            # Update health status
            return True
        return False
        
    async def _route_load_signal(self, signal: OrchestrationSignal) -> bool:
        """Route load balancing signal"""
        component_id = signal.payload.get("component_id")
        load_factor = signal.payload.get("load_factor")
        
        self.update_component_load(component_id, load_factor)
        return True
        
    async def _route_workflow_signal(self, signal: OrchestrationSignal) -> bool:
        """Route workflow signal"""
        workflow_id = signal.payload.get("workflow_id")
        action = signal.payload.get("action")
        
        if workflow_id in self.active_workflows:
            if action == "pause":
                self.active_workflows[workflow_id].status = WorkflowStatus.PAUSED
            elif action == "resume":
                self.active_workflows[workflow_id].status = WorkflowStatus.RUNNING
            elif action == "cancel":
                self.active_workflows[workflow_id].status = WorkflowStatus.CANCELLED
                
        return True
        
    async def _execute_workflow_steps(self, workflow: Workflow) -> None:
        """Execute workflow steps according to dependencies"""
        workflow_state = self.workflow_state[workflow.workflow_id]
        completed_steps = set()
        failed_steps = set()
        
        while len(completed_steps) < len(workflow.steps):
            # Find ready steps (all dependencies completed)
            ready_steps = []
            for step in workflow.steps:
                if (step.step_id not in completed_steps and 
                    step.step_id not in failed_steps and
                    all(dep in completed_steps for dep in step.dependencies)):
                    ready_steps.append(step)
                    
            if not ready_steps:
                # No ready steps - deadlock or dependency error
                self.logger.error(f"Workflow {workflow.workflow_id} deadlock detected")
                break
                
            # Execute ready steps
            for step in ready_steps:
                await self._execute_workflow_step(step)
                if step.status == WorkflowStatus.COMPLETED:
                    completed_steps.add(step.step_id)
                else:
                    failed_steps.add(step.step_id)
                    
            # Update workflow state
            workflow_state["completed_steps"] = list(completed_steps)
            workflow_state["failed_steps"] = list(failed_steps)
            
    async def _execute_workflow_step(self, step: WorkflowStep) -> None:
        """Execute a single workflow step"""
        step.status = WorkflowStatus.RUNNING
        step.start_time = datetime.now()
        
        try:
            # Create signal for step execution
            signal = await self.create_signal(
                SignalType.COORDINATION,
                ComponentType.PRANAVA,
                step.component_type,
                {
                    "operation": step.operation,
                    "parameters": step.parameters,
                    "step_id": step.step_id
                }
            )
            
            await self.process_signal(signal)
            
            step.status = WorkflowStatus.COMPLETED
            step.end_time = datetime.now()
            self.logger.debug(f"Completed workflow step: {step.step_id}")
            
        except Exception as e:
            step.status = WorkflowStatus.FAILED
            step.error = str(e)
            step.end_time = datetime.now()
            self.logger.error(f"Workflow step failed: {step.step_id}: {e}")
            
    def _update_signal_latency(self, latency_ms: float) -> None:
        """Update average signal processing latency"""
        current_avg = self.orchestration_stats["average_signal_latency"]
        total_signals = self.orchestration_stats["signals_processed"]
        
        self.orchestration_stats["average_signal_latency"] = (
            (current_avg * (total_signals - 1) + latency_ms) / total_signals
        )
        
    async def _health_monitor_loop(self) -> None:
        """Background health monitoring loop"""
        while True:
            try:
                # Check health of registered components
                for component_id in set(self.component_health.keys()):
                    # In real implementation, would ping component
                    # For now, just update timestamp
                    if component_id in self.component_health:
                        self.component_health[component_id]["last_check"] = datetime.now()
                        
                await asyncio.sleep(self.health_check_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Health monitoring error: {e}")
                await asyncio.sleep(self.health_check_interval)
                
    async def _signal_cleanup_loop(self) -> None:
        """Background signal cleanup loop"""
        while True:
            try:
                current_time = datetime.now()
                
                # Clean up expired signals
                expired_signals = []
                for signal_id, signal in self.active_signals.items():
                    if signal.ttl:
                        age = (current_time - signal.timestamp).total_seconds()
                        if age > signal.ttl:
                            expired_signals.append(signal_id)
                            
                for signal_id in expired_signals:
                    del self.active_signals[signal_id]
                    
                if expired_signals:
                    self.logger.debug(f"Cleaned up {len(expired_signals)} expired signals")
                    
                await asyncio.sleep(60)  # Cleanup every minute
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Signal cleanup error: {e}")
                await asyncio.sleep(60)
                
    # Message handlers
    async def _handle_signal_processing(self, message: TriumvirateMessage) -> Dict[str, Any]:
        """Handle signal processing request"""
        signal_data = message.payload.get("signal_data")
        signal_type = SignalType(signal_data["signal_type"])
        
        signal = await self.create_signal(
            signal_type,
            ComponentType(signal_data["source"]),
            ComponentType(signal_data["target"]),
            signal_data.get("payload", {}),
            MessagePriority(signal_data.get("priority", 2)),
            signal_data.get("routing_context")
        )
        
        success = await self.process_signal(signal)
        return {"success": success, "signal_id": signal.signal_id}
        
    async def _handle_workflow_creation(self, message: TriumvirateMessage) -> Dict[str, Any]:
        """Handle workflow creation request"""
        workflow_data = message.payload.get("workflow_data")
        
        # Convert step data to WorkflowStep objects
        steps = []
        for step_data in workflow_data["steps"]:
            step = WorkflowStep(
                step_id=step_data["step_id"],
                component_type=ComponentType(step_data["component_type"]),
                operation=step_data["operation"],
                parameters=step_data.get("parameters", {}),
                dependencies=step_data.get("dependencies", [])
            )
            steps.append(step)
            
        workflow = await self.create_workflow(
            workflow_data["workflow_id"],
            workflow_data["name"],
            steps,
            ComponentType(message.sender.value)
        )
        
        return {"success": True, "workflow_id": workflow.workflow_id}
        
    async def _handle_workflow_execution(self, message: TriumvirateMessage) -> Dict[str, Any]:
        """Handle workflow execution request"""
        workflow_id = message.payload.get("workflow_id")
        
        if workflow_id in self.active_workflows:
            workflow = self.active_workflows[workflow_id]
            success = await self.execute_workflow(workflow)
            return {"success": success, "workflow_id": workflow_id}
        else:
            return {"success": False, "error": "Workflow not found"}
            
    async def _handle_routing_request(self, message: TriumvirateMessage) -> Dict[str, Any]:
        """Handle routing request"""
        capability = message.payload.get("capability")
        routing_hints = message.payload.get("routing_hints", {})
        
        target = await self.intelligent_route(capability, routing_hints)
        return {"target": target, "capability": capability}
        
    async def _handle_load_update(self, message: TriumvirateMessage) -> Dict[str, Any]:
        """Handle load update request"""
        component_id = message.payload.get("component_id")
        load_factor = message.payload.get("load_factor")
        
        self.update_component_load(component_id, load_factor)
        return {"success": True}
        
    async def _handle_health_check(self, message: TriumvirateMessage) -> Dict[str, Any]:
        """Handle health check request"""
        component_id = message.payload.get("component_id")
        health_status = message.payload.get("status")
        
        self.component_health[component_id] = {
            "status": health_status,
            "last_check": datetime.now(),
            "timestamp": datetime.now().isoformat()
        }
        
        return {"success": True, "component_id": component_id}
