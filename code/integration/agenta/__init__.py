"""
Agenta: Tiered Hierarchy Manager for Triumvirate Integration Layer

Agenta manages the hierarchical organization and business function mapping
of all system components, providing intelligent routing and coordination
across the organization structure.
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

from ..shared.base import TriumvirateComponent, ComponentType, TriumvirateMessage, MessagePriority
from ..shared.messaging import MessageRouter, MessageProtocol
from ..shared.discovery import ServiceDiscovery, ServiceInfo

class HierarchyLevel(Enum):
    BUSINESS_FUNCTION = "business_function"
    TEAM = "team"
    MICROAGENT = "microagent"
    KOSHA = "kosha"

class BusinessFunction(Enum):
    RESEARCH_DEVELOPMENT = "research_development"
    INTEGRATION_SPECIALISTS = "integration_specialists"
    RESPONSE_UNITS = "response_units"
    CROSS_TEAM_SUPPORT = "cross_team_support"
    SPECIALIZED_DEPTH = "specialized_depth"
    RESERVE_TEAMS = "reserve_teams"
    MARKETING = "marketing"
    SALES = "sales"
    FINANCE = "finance"
    OPERATIONS = "operations"

@dataclass
class HierarchyNode:
    """Node in the Agenta hierarchy"""
    node_id: str
    name: str
    node_type: HierarchyLevel
    parent_id: Optional[str] = None
    children_ids: Set[str] = None
    capabilities: Set[str] = None
    metadata: Dict[str, Any] = None
    load_factor: float = 0.0  # 0.0 to 1.0
    status: str = "active"
    registered_at: datetime = None
    
    def __post_init__(self):
        if self.children_ids is None:
            self.children_ids = set()
        if self.capabilities is None:
            self.capabilities = set()
        if self.metadata is None:
            self.metadata = {}
        if self.registered_at is None:
            self.registered_at = datetime.now()

class AgentaManager(TriumvirateComponent):
    """
    Agenta: Central hierarchy management component
    Manages business functions, teams, microagents, and koshas
    """
    
    def __init__(self, component_id: str = "primary"):
        super().__init__(ComponentType.AGENTA, component_id)
        
        # Hierarchy management
        self.hierarchy_nodes: Dict[str, HierarchyNode] = {}
        self.business_functions: Dict[str, BusinessFunction] = {}
        self.team_to_function_mapping: Dict[str, BusinessFunction] = {}
        
        # Routing intelligence
        self.capability_index: Dict[str, Set[str]] = {}  # capability -> node_ids
        self.load_balancing_enabled = True
        self.intelligent_routing = True
        
        # Performance tracking
        self.routing_stats = {
            "total_requests": 0,
            "successful_routes": 0,
            "failed_routes": 0,
            "average_response_time": 0.0
        }
        
        self.logger = logging.getLogger("AgentaManager")
        
    async def initialize(self) -> None:
        """Initialize Agenta hierarchy"""
        self.logger.info("Initializing Agenta hierarchy manager")
        
        # Register message handlers
        self.register_handler("hierarchy.register_node", self._handle_register_node)
        self.register_handler("hierarchy.find_path", self._handle_find_path)
        self.register_handler("hierarchy.get_children", self._handle_get_children)
        self.register_handler("hierarchy.update_load", self._handle_update_load)
        self.register_handler("routing.request", self._handle_routing_request)
        self.register_handler("business_function.create", self._handle_create_business_function)
        
        # Create initial business function hierarchy
        await self._initialize_business_hierarchy()
        
        self.logger.info("Agenta hierarchy manager initialized")
        
    async def shutdown(self) -> None:
        """Shutdown Agenta manager"""
        self.logger.info("Shutting down Agenta manager")
        
    async def _route_message(self, message: TriumvirateMessage) -> bool:
        """Route message to appropriate handler"""
        return await self.receive_message(message)
        
    async def register_business_function(self, function: BusinessFunction, 
                                       node_id: str, metadata: Dict[str, Any] = None) -> bool:
        """Register a business function in the hierarchy"""
        try:
            # Create business function node
            business_node = HierarchyNode(
                node_id=node_id,
                name=function.value.replace('_', ' ').title(),
                node_type=HierarchyLevel.BUSINESS_FUNCTION,
                capabilities=set(metadata.get("capabilities", [])) if metadata else set(),
                metadata=metadata or {}
            )
            
            self.hierarchy_nodes[node_id] = business_node
            self.business_functions[node_id] = function
            
            # Update capability index
            for capability in business_node.capabilities:
                if capability not in self.capability_index:
                    self.capability_index[capability] = set()
                self.capability_index[capability].add(node_id)
                
            self.logger.info(f"Registered business function: {function.value} -> {node_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register business function {function.value}: {e}")
            return False
            
    async def register_team(self, team_id: str, function_id: str, 
                          team_config: Dict[str, Any]) -> bool:
        """Register a team under a business function"""
        try:
            function = self.business_functions.get(function_id)
            if not function:
                self.logger.error(f"Business function {function_id} not found")
                return False
                
            # Create team node
            team_node = HierarchyNode(
                node_id=team_id,
                name=team_config.get("name", f"Team {team_id}"),
                node_type=HierarchyLevel.TEAM,
                parent_id=function_id,
                capabilities=set(team_config.get("capabilities", [])),
                metadata=team_config
            )
            
            self.hierarchy_nodes[team_id] = team_node
            
            # Update parent-child relationship
            if function_id in self.hierarchy_nodes:
                self.hierarchy_nodes[function_id].children_ids.add(team_id)
                
            self.team_to_function_mapping[team_id] = function
            
            # Update capability index
            for capability in team_node.capabilities:
                if capability not in self.capability_index:
                    self.capability_index[capability] = set()
                self.capability_index[capability].add(team_id)
                
            self.logger.info(f"Registered team: {team_id} under {function.value}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register team {team_id}: {e}")
            return False
            
    async def register_component(self, component_id: str, component_type: ComponentType,
                               team_id: Optional[str] = None, capabilities: List[str] = None) -> bool:
        """Register a microagent or kosha in the hierarchy"""
        try:
            # Create component node
            node_type = HierarchyLevel.MICROAGENT if component_type == ComponentType.MICROAGENT else HierarchyLevel.KOSHA
            
            component_node = HierarchyNode(
                node_id=component_id,
                name=f"{component_type.value.title()} {component_id}",
                node_type=node_type,
                parent_id=team_id,
                capabilities=set(capabilities or [])
            )
            
            self.hierarchy_nodes[component_id] = component_node
            
            # Update parent-child relationship
            if team_id and team_id in self.hierarchy_nodes:
                self.hierarchy_nodes[team_id].children_ids.add(component_id)
                
            # Update capability index
            for capability in component_node.capabilities:
                if capability not in self.capability_index:
                    self.capability_index[capability] = set()
                self.capability_index[capability].add(component_id)
                
            self.logger.info(f"Registered component: {component_id} ({component_type.value})")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register component {component_id}: {e}")
            return False
            
    async def intelligent_route(self, capability_required: str, 
                              preferred_function: Optional[BusinessFunction] = None) -> Optional[str]:
        """Intelligently route to the best component with required capability"""
        try:
            self.routing_stats["total_requests"] += 1
            start_time = datetime.now()
            
            # Find all components with the required capability
            candidate_nodes = self.capability_index.get(capability_required, set())
            if not candidate_nodes:
                self.logger.warning(f"No components found with capability: {capability_required}")
                self.routing_stats["failed_routes"] += 1
                return None
                
            # Filter by business function preference
            if preferred_function:
                function_nodes = {k for k, v in self.team_to_function_mapping.items() 
                                if v == preferred_function}
                candidate_nodes = candidate_nodes & function_nodes
                
            if not candidate_nodes:
                self.routing_stats["failed_routes"] += 1
                return None
                
            # Load balancing selection
            if self.load_balancing_enabled:
                best_node = self._select_optimal_node(candidate_nodes)
            else:
                best_node = next(iter(candidate_nodes))
                
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self._update_response_time(response_time)
            self.routing_stats["successful_routes"] += 1
            
            self.logger.info(f"Routed {capability_required} to {best_node} (response_time: {response_time:.2f}ms)")
            return best_node
            
        except Exception as e:
            self.logger.error(f"Intelligent routing failed for {capability_required}: {e}")
            self.routing_stats["failed_routes"] += 1
            return None
            
    def _select_optimal_node(self, candidate_nodes: Set[str]) -> str:
        """Select the optimal node based on load and capabilities"""
        def node_score(node_id: str) -> float:
            node = self.hierarchy_nodes.get(node_id)
            if not node:
                return 0.0
                
            # Lower load is better (inverted)
            load_score = 1.0 - node.load_factor
            
            # Additional capabilities bonus
            capability_bonus = len(node.capabilities) * 0.1
            
            return load_score + capability_bonus
            
        return max(candidate_nodes, key=node_score)
        
    def _update_response_time(self, response_time: float) -> None:
        """Update average response time"""
        current_avg = self.routing_stats["average_response_time"]
        total_requests = self.routing_stats["total_requests"]
        
        # Running average
        self.routing_stats["average_response_time"] = (
            (current_avg * (total_requests - 1) + response_time) / total_requests
        )
        
    async def update_component_load(self, component_id: str, load_factor: float) -> None:
        """Update load factor for a component"""
        if component_id in self.hierarchy_nodes:
            self.hierarchy_nodes[component_id].load_factor = max(0.0, min(1.0, load_factor))
            self.logger.debug(f"Updated load for {component_id}: {load_factor}")
            
    def get_hierarchy_tree(self, root_function: Optional[BusinessFunction] = None) -> Dict[str, Any]:
        """Get the complete hierarchy tree"""
        def build_tree(node_id: str) -> Dict[str, Any]:
            node = self.hierarchy_nodes.get(node_id)
            if not node:
                return {}
                
            tree_node = {
                "node_id": node.node_id,
                "name": node.name,
                "type": node.node_type.value,
                "status": node.status,
                "load_factor": node.load_factor,
                "capabilities": list(node.capabilities),
                "children": []
            }
            
            # Recursively build children
            for child_id in node.children_ids:
                if child_id in self.hierarchy_nodes:
                    child_tree = build_tree(child_id)
                    if child_tree:
                        tree_node["children"].append(child_tree)
                        
            return tree_node
            
        if root_function:
            # Build tree from specific business function
            function_nodes = [k for k, v in self.business_functions.items() if v == root_function]
            result = {"business_functions": []}
            for fnode_id in function_nodes:
                function_tree = build_tree(fnode_id)
                if function_tree:
                    result["business_functions"].append(function_tree)
            return result
        else:
            # Build full tree
            result = {"business_functions": []}
            for fnode_id in self.hierarchy_nodes:
                node = self.hierarchy_nodes[fnode_id]
                if node.node_type == HierarchyLevel.BUSINESS_FUNCTION:
                    function_tree = build_tree(fnode_id)
                    if function_tree:
                        result["business_functions"].append(function_tree)
            return result
            
    def get_routing_statistics(self) -> Dict[str, Any]:
        """Get routing performance statistics"""
        return {
            **self.routing_stats,
            "success_rate": (self.routing_stats["successful_routes"] / 
                           max(1, self.routing_stats["total_requests"])),
            "node_count": len(self.hierarchy_nodes),
            "business_function_count": len(self.business_functions),
            "team_count": len(self.team_to_function_mapping),
            "capability_coverage": len(self.capability_index)
        }
        
    async def _initialize_business_hierarchy(self) -> None:
        """Initialize the basic business function hierarchy"""
        business_functions = [
            BusinessFunction.RESEARCH_DEVELOPMENT,
            BusinessFunction.INTEGRATION_SPECIALISTS,
            BusinessFunction.RESPONSE_UNITS,
            BusinessFunction.CROSS_TEAM_SUPPORT,
            BusinessFunction.SPECIALIZED_DEPTH,
            BusinessFunction.RESERVE_TEAMS
        ]
        
        for i, func in enumerate(business_functions):
            function_id = f"BF_{i:03d}_{func.value.upper()}"
            await self.register_business_function(func, function_id, {
                "description": f"Primary {func.value.replace('_', ' ')} function",
                "priority": i,
                "specialization": func.value
            })
            
    # Message handlers
    async def _handle_register_node(self, message: TriumvirateMessage) -> Dict[str, Any]:
        """Handle hierarchy node registration message"""
        node_data = message.payload.get("node_data", {})
        node_type = node_data.get("node_type")
        
        if node_type == "business_function":
            function = BusinessFunction(node_data["function"])
            result = await self.register_business_function(
                function, node_data["node_id"], node_data.get("metadata")
            )
        elif node_type == "team":
            result = await self.register_team(
                node_data["node_id"], 
                node_data["function_id"], 
                node_data.get("config", {})
            )
        elif node_type in ["microagent", "kosha"]:
            component_type = ComponentType(node_type)
            result = await self.register_component(
                node_data["node_id"],
                component_type,
                node_data.get("team_id"),
                node_data.get("capabilities", [])
            )
        else:
            result = False
            
        return {"success": result, "node_id": node_data.get("node_id")}
        
    async def _handle_find_path(self, message: TriumvirateMessage) -> Dict[str, Any]:
        """Handle find path in hierarchy message"""
        start_node = message.payload.get("start_node")
        end_node = message.payload.get("end_node")
        
        # Simple path finding (could be enhanced with graph algorithms)
        path = []
        if start_node in self.hierarchy_nodes and end_node in self.hierarchy_nodes:
            start = self.hierarchy_nodes[start_node]
            end = self.hierarchy_nodes[end_node]
            
            # Find common ancestor
            current = start
            while current:
                path.append(current.node_id)
                if current.node_id == end_node:
                    break
                current = self.hierarchy_nodes.get(current.parent_id) if current.parent_id else None
                
        return {"path": path}
        
    async def _handle_get_children(self, message: TriumvirateMessage) -> Dict[str, Any]:
        """Handle get children message"""
        node_id = message.payload.get("node_id")
        if node_id in self.hierarchy_nodes:
            return {
                "children": list(self.hierarchy_nodes[node_id].children_ids),
                "node_type": self.hierarchy_nodes[node_id].node_type.value
            }
        return {"children": [], "node_type": None}
        
    async def _handle_update_load(self, message: TriumvirateMessage) -> Dict[str, Any]:
        """Handle load update message"""
        component_id = message.payload.get("component_id")
        load_factor = message.payload.get("load_factor")
        
        await self.update_component_load(component_id, load_factor)
        return {"success": True}
        
    async def _handle_routing_request(self, message: TriumvirateMessage) -> Dict[str, Any]:
        """Handle intelligent routing request"""
        capability = message.payload.get("capability")
        preferred_function = message.payload.get("preferred_function")
        
        if preferred_function:
            preferred_function = BusinessFunction(preferred_function)
            
        target_node = await self.intelligent_route(capability, preferred_function)
        return {"target_node": target_node, "capability": capability}
        
    async def _handle_create_business_function(self, message: TriumvirateMessage) -> Dict[str, Any]:
        """Handle business function creation message"""
        function_data = message.payload.get("function_data")
        function = BusinessFunction(function_data["function"])
        
        result = await self.register_business_function(
            function, 
            function_data["node_id"], 
            function_data.get("metadata")
        )
        return {"success": result}
