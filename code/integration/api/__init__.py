"""
API Layer for Triumvirate Integration Layer

Provides REST API endpoints and WebSocket interfaces for triumvirate component
management, monitoring, and orchestration.
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import asdict

from ..shared.base import ComponentType, MessagePriority
from ..shared.messaging import MessageRouter, MessageProtocol
from ..shared.discovery import ServiceDiscovery, ServiceInfo
from ..shared.monitoring import ObservabilityManager, AlertSeverity

class TriumvirateAPI:
    """API layer for triumvirate integration management"""
    
    def __init__(self, agenta_manager, pranava_orchestrator, antakhara_enforcer,
                 service_discovery, observability_manager):
        self.agenta = agenta_manager
        self.pranava = pranava_orchestrator  
        self.antakhara = antakhara_enforcer
        self.discovery = service_discovery
        self.observability = observability_manager
        self.logger = logging.getLogger("TriumvirateAPI")
        
    async def handle_api_request(self, method: str, endpoint: str, 
                               data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle API requests"""
        try:
            if endpoint == "/hierarchy/register":
                return await self._register_hierarchy_node(data)
            elif endpoint == "/hierarchy/tree":
                return await self._get_hierarchy_tree(data)
            elif endpoint == "/orchestration/route":
                return await self._handle_routing_request(data)
            elif endpoint == "/orchestration/workflow/create":
                return await self._create_workflow(data)
            elif endpoint == "/orchestration/workflow/execute":
                return await self._execute_workflow(data)
            elif endpoint == "/security/policy/create":
                return await self._create_policy(data)
            elif endpoint == "/security/access/check":
                return await self._check_access(data)
            elif endpoint == "/security/event/log":
                return await self._log_security_event(data)
            elif endpoint == "/monitoring/metrics":
                return await self._get_metrics(data)
            elif endpoint == "/monitoring/health":
                return await self._get_health_status(data)
            elif endpoint == "/monitoring/alerts":
                return await self._get_alerts(data)
            elif endpoint == "/discovery/services":
                return await self._get_services(data)
            elif endpoint == "/system/overview":
                return await self._get_system_overview()
            else:
                return {"error": "Unknown endpoint", "status": 404}
                
        except Exception as e:
            self.logger.error(f"API request failed: {e}")
            return {"error": str(e), "status": 500}
            
    async def _register_hierarchy_node(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Register a hierarchy node via API"""
        node_data = data.get("node_data")
        node_type = node_data.get("node_type")
        
        if node_type == "business_function":
            from agenta.manager import BusinessFunction
            function = BusinessFunction(node_data["function"])
            result = await self.agenta.register_business_function(
                function, node_data["node_id"], node_data.get("metadata")
            )
        elif node_type == "team":
            result = await self.agenta.register_team(
                node_data["node_id"],
                node_data["function_id"], 
                node_data.get("config", {})
            )
        elif node_type in ["microagent", "kosha"]:
            component_type = ComponentType(node_type)
            result = await self.agenta.register_component(
                node_data["node_id"],
                component_type,
                node_data.get("team_id"),
                node_data.get("capabilities", [])
            )
        else:
            result = False
            
        return {"success": result, "node_id": node_data.get("node_id")}
        
    async def _get_hierarchy_tree(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get hierarchy tree via API"""
        root_function = data.get("root_function")
        if root_function:
            from agenta.manager import BusinessFunction
            root_function = BusinessFunction(root_function)
            
        tree = self.agenta.get_hierarchy_tree(root_function)
        return {"hierarchy_tree": tree}
        
    async def _handle_routing_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle routing request via API"""
        capability = data.get("capability")
        preferred_function = data.get("preferred_function")
        
        if preferred_function:
            from agenta.manager import BusinessFunction
            preferred_function = BusinessFunction(preferred_function)
            
        target = await self.agenta.intelligent_route(capability, preferred_function)
        return {"target_node": target, "capability": capability}
        
    async def _create_workflow(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create workflow via API"""
        workflow_data = data.get("workflow_data")
        
        # Convert step data
        steps = []
        for step_data in workflow_data["steps"]:
            from pranava.orchestrator import WorkflowStep
            step = WorkflowStep(
                step_id=step_data["step_id"],
                component_type=ComponentType(step_data["component_type"]),
                operation=step_data["operation"],
                parameters=step_data.get("parameters", {}),
                dependencies=step_data.get("dependencies", [])
            )
            steps.append(step)
            
        workflow = await self.pranava.create_workflow(
            workflow_data["workflow_id"],
            workflow_data["name"],
            steps,
            ComponentType.AGENTA  # API caller
        )
        
        return {"success": True, "workflow_id": workflow.workflow_id}
        
    async def _execute_workflow(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute workflow via API"""
        workflow_id = data.get("workflow_id")
        
        if workflow_id in self.pranava.active_workflows:
            workflow = self.pranava.active_workflows[workflow_id]
            success = await self.pranava.execute_workflow(workflow)
            return {"success": success, "workflow_id": workflow_id}
        else:
            return {"success": False, "error": "Workflow not found"}
            
    async def _create_policy(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create security policy via API"""
        policy_data = data.get("policy_data")
        
        from antakhara.enforcer import SecurityPolicy, PolicyType, SecurityLevel
        policy = SecurityPolicy(
            policy_id=policy_data["policy_id"],
            name=policy_data["name"],
            policy_type=PolicyType(policy_data["policy_type"]),
            description=policy_data["description"],
            rules=policy_data["rules"],
            security_level=SecurityLevel(policy_data["security_level"])
        )
        
        success = await self.antakhara.create_policy(policy)
        return {"success": success, "policy_id": policy.policy_id}
        
    async def _check_access(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Check access permissions via API"""
        resource = data.get("resource")
        action = data.get("action")
        component = ComponentType(data.get("component"))
        
        result = await self.antakhara.check_access(resource, action, component, data)
        return result
        
    async def _log_security_event(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Log security event via API"""
        event_data = data.get("event_data")
        
        from antakhara.enforcer import SecurityEvent, SecurityLevel
        event = SecurityEvent(
            event_id=event_data["event_id"],
            event_type=event_data["event_type"],
            severity=SecurityLevel(event_data["severity"]),
            source_component=event_data["source_component"],
            target_component=event_data["target_component"],
            description=event_data["description"],
            timestamp=datetime.now(),
            details=event_data.get("details", {})
        )
        
        success = await self.antakhara.log_security_event(event)
        return {"success": success}
        
    async def _get_metrics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get system metrics via API"""
        component_id = data.get("component_id")
        
        if component_id:
            return self.observability.get_component_metrics(component_id)
        else:
            return self.observability.get_system_overview()
            
    async def _get_health_status(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get component health status via API"""
        component_id = data.get("component_id")
        
        if component_id:
            return await self.agenta.get_health_status()
        else:
            # Return health status for all components
            health_info = {
                "agenta": await self.agenta.get_health_status(),
                "pranava": await self.pranava.get_health_status(),
                "antakhara": await self.antakhara.get_health_status()
            }
            return {"components": health_info}
            
    async def _get_alerts(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get system alerts via API"""
        return {
            "alerts": self.observability.alerts,
            "active_alerts": len([a for a in self.observability.alerts if not a.resolved]),
            "critical_alerts": len([a for a in self.observability.alerts if a.severity == AlertSeverity.CRITICAL])
        }
        
    async def _get_services(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get service discovery info via API"""
        return self.discovery.get_service_mesh_info()
        
    async def _get_system_overview(self) -> Dict[str, Any]:
        """Get comprehensive system overview"""
        overview = {
            "timestamp": datetime.now().isoformat(),
            "system_stats": {
                "agenta_stats": self.agenta.get_routing_statistics(),
                "pranava_stats": self.pranava.orchestration_stats,
                "antakhara_stats": self.antakhara.security_stats
            },
            "observability": self.observability.get_system_overview(),
            "service_mesh": self.discovery.get_service_mesh_info()
        }
        
        return overview
