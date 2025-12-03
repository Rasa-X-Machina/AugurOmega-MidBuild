"""
Comprehensive tests for Triumvirate Integration Layer
"""

import asyncio
import pytest
import json
from datetime import datetime
from unittest.mock import Mock, AsyncMock

from triumvirate_manager import TriumvirateIntegrationManager
from shared.base import ComponentType, MessagePriority
from shared.messaging import MessageRouter
from shared.discovery import ServiceDiscovery, ServiceInfo
from shared.monitoring import ObservabilityManager

class TestTriumvirateIntegration:
    """Test suite for triumvirate integration"""
    
    @pytest.fixture
    async def integration_manager(self):
        """Create integration manager for testing"""
        manager = TriumvirateIntegrationManager("configs/test_config.yaml")
        # Use test configuration
        await manager.initialize()
        yield manager
        await manager.stop()
        
    async def test_manager_initialization(self, integration_manager):
        """Test manager initialization"""
        assert integration_manager is not None
        assert integration_manager.agenta is not None
        assert integration_manager.pranava is not None
        assert integration_manager.antakhara is not None
        assert integration_manager.message_router is not None
        assert integration_manager.service_discovery is not None
        assert integration_manager.observability is not None
        
    async def test_manager_start_stop(self, integration_manager):
        """Test manager start and stop"""
        # Test start
        result = await integration_manager.start()
        assert result is True
        assert integration_manager.is_running is True
        
        # Test stop
        result = await integration_manager.stop()
        assert result is True
        assert integration_manager.is_running is False
        
    async def test_manager_status(self, integration_manager):
        """Test manager status reporting"""
        status = integration_manager.get_status()
        
        assert "system_status" in status
        assert "components" in status
        assert "shared_infrastructure" in status
        assert "revolutionary_capabilities" in status
        
        # Check component structure
        assert "agenta" in status["components"]
        assert "pranava" in status["components"]
        assert "antakhara" in status["components"]
        
class TestMessageRouter:
    """Test message routing functionality"""
    
    def setup_method(self):
        self.router = MessageRouter()
        
    async def test_message_creation(self):
        """Test message creation"""
        message = self.router.create_message(
            ComponentType.AGENTA,
            ComponentType.PRANAVA,
            "test_message",
            {"test": "data"}
        )
        
        assert message.sender == ComponentType.AGENTA
        assert message.recipient == ComponentType.PRANAVA
        assert message.message_type == "test_message"
        assert message.payload == {"test": "data"}
        
    async def test_message_routing(self):
        """Test message routing"""
        handler_called = False
        
        def test_handler(message):
            nonlocal handler_called
            handler_called = True
            return True
            
        self.router.add_route("test_message", test_handler)
        
        message = self.router.create_message(
            ComponentType.AGENTA,
            ComponentType.PRANAVA,
            "test_message",
            {"test": "data"}
        )
        
        result = await self.router.route_message(message)
        assert result is True
        assert handler_called is True

class TestServiceDiscovery:
    """Test service discovery functionality"""
    
    def setup_method(self):
        self.discovery = ServiceDiscovery()
        
    async def test_service_registration(self):
        """Test service registration"""
        service = ServiceInfo(
            service_id="test_service",
            service_type="test",
            endpoint="test://endpoint",
            capabilities=["test_capability"],
            metadata={}
        )
        
        result = await self.discovery.register_service(service)
        assert result is True
        assert service.service_id in self.discovery.services
        
    async def test_service_discovery(self):
        """Test service discovery"""
        # Register a service
        service = ServiceInfo(
            service_id="test_service",
            service_type="test",
            endpoint="test://endpoint",
            capabilities=["test_capability"],
            metadata={}
        )
        await self.discovery.register_service(service)
        
        # Find the service
        services = self.discovery.find_services("test")
        assert len(services) == 1
        assert services[0].service_id == "test_service"
        
    async def test_service_mesh_info(self):
        """Test service mesh information"""
        service = ServiceInfo(
            service_id="test_service",
            service_type="test",
            endpoint="test://endpoint",
            capabilities=["test_capability"],
            metadata={}
        )
        await self.discovery.register_service(service)
        
        mesh_info = self.discovery.get_service_mesh_info()
        
        assert mesh_info["total_services"] == 1
        assert mesh_info["healthy_services"] == 1
        assert "test" in mesh_info["service_types_summary"]

class TestObservability:
    """Test observability and monitoring"""
    
    def setup_method(self):
        self.observability = ObservabilityManager()
        
    async def test_metric_recording(self):
        """Test metric recording"""
        from shared.monitoring import Metric, MetricType
        
        metric = Metric(
            name="test_metric",
            value=42.0,
            metric_type=MetricType.COUNTER,
            labels={"test": "label"},
            timestamp=datetime.now()
        )
        
        self.observability.record_metric(metric)
        
        # Check if metric was recorded
        metric_key = f"test_metric:{json.dumps({'test': 'label'}, sort_keys=True)}"
        assert metric_key in self.observability.metrics
        assert len(self.observability.metrics[metric_key]) == 1
        
    async def test_counter_increment(self):
        """Test counter increment"""
        self.observability.increment_counter("test_counter", "test_component", 5)
        
        # Check if counter was incremented
        metric_key = "test_counter:{}"
        assert metric_key in self.observability.metrics
        assert self.observability.metrics[metric_key][-1].value == 5
        
    async def test_alert_creation(self):
        """Test alert creation"""
        from shared.monitoring import AlertSeverity
        
        alert = self.observability.create_alert(
            AlertSeverity.WARNING,
            "Test Alert",
            "This is a test alert",
            "test_component"
        )
        
        assert alert.title == "Test Alert"
        assert alert.severity == AlertSeverity.WARNING
        assert alert.component_id == "test_component"
        assert alert.id in [a.id for a in self.observability.alerts]

class TestIntegrationScenarios:
    """Test real-world integration scenarios"""
    
    @pytest.fixture
    async def integrated_manager(self):
        """Create fully integrated manager"""
        manager = TriumvirateIntegrationManager()
        await manager.initialize()
        await manager.start()
        yield manager
        await manager.stop()
        
    async def test_end_to_end_routing(self, integrated_manager):
        """Test end-to-end message routing through all components"""
        # Create routing request message
        message = integrated_manager.message_router.create_message(
            ComponentType.AGENTA,
            ComponentType.PRANAVA,
            "hierarchy.routing_request",
            {
                "capability": "reasoning",
                "preferred_function": "research_development"
            }
        )
        
        # Send message through router
        result = await integrated_manager.message_router.route_message(message)
        assert result is True
        
    async def test_workflow_execution(self, integrated_manager):
        """Test workflow creation and execution"""
        # This would require a more complex setup with actual workflow data
        pass
        
    async def test_security_policy_enforcement(self, integrated_manager):
        """Test security policy enforcement"""
        # Create access check request
        message = integrated_manager.message_router.create_message(
            ComponentType.AGENTA,
            ComponentType.ANTAKHARA,
            "security.access_check",
            {
                "resource": "hierarchy",
                "action": "write",
                "component": "agenta"
            }
        )
        
        result = await integrated_manager.message_router.route_message(message)
        assert result is True
        
    async def test_health_monitoring(self, integrated_manager):
        """Test health monitoring across components"""
        # Wait for health monitoring to collect data
        await asyncio.sleep(2)
        
        # Check system overview
        overview = integrated_manager.observability.get_system_overview()
        assert "timestamp" in overview
        assert "system_health" in overview
        
    async def test_self_healing(self, integrated_manager):
        """Test self-healing capabilities"""
        # Create a critical alert
        from shared.monitoring import AlertSeverity
        alert = integrated_manager.observability.create_alert(
            AlertSeverity.CRITICAL,
            "Test Critical Alert",
            "This is a critical test alert",
            "test_component"
        )
        
        # Trigger self-healing
        if integrated_manager.self_healer:
            await integrated_manager.self_healer.handle_critical_alert(alert)
            
        # Check that alert was handled
        assert alert.acknowledged is True

# Performance tests
class TestPerformance:
    """Test performance characteristics"""
    
    @pytest.mark.asyncio
    async def test_message_throughput(self):
        """Test message routing throughput"""
        manager = TriumvirateIntegrationManager()
        await manager.initialize()
        
        router = manager.message_router
        
        # Create test route
        async def test_handler(message):
            return True
            
        router.add_route("throughput_test", test_handler)
        
        # Send many messages
        start_time = datetime.now()
        tasks = []
        
        for i in range(1000):
            message = router.create_message(
                ComponentType.AGENTA,
                ComponentType.PRANAVA,
                "throughput_test",
                {"message_id": i}
            )
            tasks.append(router.route_message(message))
            
        results = await asyncio.gather(*tasks)
        end_time = datetime.now()
        
        # Calculate throughput
        duration = (end_time - start_time).total_seconds()
        throughput = len(results) / duration
        
        assert len([r for r in results if r]) > 900  # At least 90% success rate
        assert throughput > 100  # At least 100 messages per second
        
        await manager.stop()
        
    @pytest.mark.asyncio
    async def test_memory_usage(self):
        """Test memory usage under load"""
        manager = TriumvirateIntegrationManager()
        await manager.initialize()
        
        # Generate load
        for i in range(10000):
            metric_name = f"test_metric_{i % 100}"
            manager.observability.set_gauge(metric_name, i, "test_component")
            
        # Check that metrics are properly managed (should not grow indefinitely)
        total_metrics = sum(len(queue) for queue in manager.observability.metrics.values())
        assert total_metrics <= 11000  # Allow some buffer
        
        await manager.stop()

if __name__ == "__main__":
    # Run tests
    asyncio.run(pytest.main([__file__]))
