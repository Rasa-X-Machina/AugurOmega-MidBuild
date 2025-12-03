# Triumvirate Integration Layer API Documentation

## Overview

The Triumvirate Integration Layer provides comprehensive APIs for managing the integration of Agenta (Tiered Hierarchy), Pranava (Orchestration Signals), and Antakhara (Security & Policy Enforcement) components.

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

All API endpoints require authentication using API keys or JWT tokens.

### Headers
```
Authorization: Bearer <api_key>
Content-Type: application/json
```

## Core Endpoints

### Hierarchy Management

#### Register Hierarchy Node
```http
POST /hierarchy/register
```

**Request Body:**
```json
{
  "node_data": {
    "node_type": "business_function",
    "function": "research_development",
    "node_id": "BF_000_RESEARCH_DEVELOPMENT",
    "metadata": {
      "description": "Primary research and development function",
      "priority": 0,
      "specialization": "research_development"
    }
  }
}
```

**Response:**
```json
{
  "success": true,
  "node_id": "BF_000_RESEARCH_DEVELOPMENT"
}
```

#### Get Hierarchy Tree
```http
GET /hierarchy/tree?root_function=research_development
```

**Response:**
```json
{
  "hierarchy_tree": {
    "business_functions": [
      {
        "node_id": "BF_000_RESEARCH_DEVELOPMENT",
        "name": "Research Development",
        "type": "business_function",
        "status": "active",
        "load_factor": 0.0,
        "capabilities": ["reasoning", "analysis"],
        "children": [
          {
            "node_id": "TEAM_RD_001",
            "name": "AI Research Team",
            "type": "team",
            "children": [...]
          }
        ]
      }
    ]
  }
}
```

### Orchestration

#### Intelligent Routing Request
```http
POST /orchestration/route
```

**Request Body:**
```json
{
  "capability": "reasoning",
  "preferred_function": "research_development",
  "routing_hints": {
    "strategy": "intelligent",
    "priority": "high"
  }
}
```

**Response:**
```json
{
  "target_node": "MA_001_AI_REASONER",
  "capability": "reasoning"
}
```

#### Create Workflow
```http
POST /orchestration/workflow/create
```

**Request Body:**
```json
{
  "workflow_data": {
    "workflow_id": "workflow_001",
    "name": "Research Analysis Workflow",
    "steps": [
      {
        "step_id": "step_001",
        "component_type": "microagent",
        "operation": "analyze_data",
        "parameters": {
          "dataset": "research_data",
          "analysis_type": "pattern_recognition"
        },
        "dependencies": []
      },
      {
        "step_id": "step_002",
        "component_type": "microagent",
        "operation": "generate_insights",
        "parameters": {
          "input_step": "step_001"
        },
        "dependencies": ["step_001"]
      }
    ]
  }
}
```

**Response:**
```json
{
  "success": true,
  "workflow_id": "workflow_001"
}
```

#### Execute Workflow
```http
POST /orchestration/workflow/execute
```

**Request Body:**
```json
{
  "workflow_id": "workflow_001"
}
```

**Response:**
```json
{
  "success": true,
  "workflow_id": "workflow_001"
}
```

### Security & Policy Enforcement

#### Create Security Policy
```http
POST /security/policy/create
```

**Request Body:**
```json
{
  "policy_data": {
    "policy_id": "policy_access_control_custom",
    "name": "Custom Access Control",
    "policy_type": "access_control",
    "description": "Custom access control policy for specific resources",
    "rules": {
      "require_authentication": true,
      "allowed_operations": {
        "agenta": ["read", "write", "admin"],
        "pranava": ["read", "write", "execute"],
        "antakhara": ["read", "write", "execute", "admin"]
      }
    },
    "security_level": 3
  }
}
```

**Response:**
```json
{
  "success": true,
  "policy_id": "policy_access_control_custom"
}
```

#### Check Access
```http
POST /security/access/check
```

**Request Body:**
```json
{
  "resource": "hierarchy",
  "action": "write",
  "component": "agenta",
  "component_id": "primary"
}
```

**Response:**
```json
{
  "allowed": true,
  "reason": "Access granted by policies"
}
```

#### Log Security Event
```http
POST /security/event/log
```

**Request Body:**
```json
{
  "event_data": {
    "event_id": "event_001",
    "event_type": "unauthorized_access_attempt",
    "severity": 2,
    "source_component": "unknown_component",
    "target_component": "hierarchy",
    "description": "Attempted unauthorized access to hierarchy resources",
    "details": {
      "ip_address": "192.168.1.100",
      "access_attempted": "hierarchy.write"
    }
  }
}
```

**Response:**
```json
{
  "success": true
}
```

### Monitoring & Observability

#### Get System Metrics
```http
GET /monitoring/metrics?component_id=agenta
```

**Response:**
```json
{
  "component_id": "agenta",
  "metrics": {
    "agenta.routing_performance:{}": {
      "latest_value": 45.2,
      "latest_timestamp": "2024-01-15T10:30:00",
      "sample_count": 150
    }
  },
  "health_status": {
    "status": "healthy",
    "timestamp": "2024-01-15T10:30:00"
  },
  "performance_stats": {
    "messages": {
      "routing_request": {
        "count": 1250,
        "avg_duration_ms": 12.5,
        "latest_duration_ms": 15.2
      }
    }
  }
}
```

#### Get Health Status
```http
GET /monitoring/health
```

**Response:**
```json
{
  "components": {
    "agenta": {
      "component_id": "primary",
      "component_type": "agenta",
      "status": "healthy",
      "is_running": true,
      "dependencies": [],
      "timestamp": "2024-01-15T10:30:00"
    },
    "pranava": {
      "component_id": "primary",
      "component_type": "pranava",
      "status": "healthy",
      "is_running": true,
      "dependencies": [],
      "timestamp": "2024-01-15T10:30:00"
    },
    "antakhara": {
      "component_id": "primary",
      "component_type": "antakhara",
      "status": "healthy",
      "is_running": true,
      "dependencies": [],
      "timestamp": "2024-01-15T10:30:00"
    }
  }
}
```

#### Get System Alerts
```http
GET /monitoring/alerts
```

**Response:**
```json
{
  "alerts": [
    {
      "id": "alert_001",
      "severity": "warning",
      "title": "Component Health Issue",
      "message": "Component test_component status: degraded",
      "component_id": "test_component",
      "timestamp": "2024-01-15T10:30:00",
      "acknowledged": false,
      "resolved": false
    }
  ],
  "active_alerts": 1,
  "critical_alerts": 0
}
```

### Service Discovery

#### Get Services
```http
GET /discovery/services
```

**Response:**
```json
{
  "total_services": 7,
  "service_types": 4,
  "healthy_services": 7,
  "unhealthy_services": 0,
  "service_types_summary": {
    "agenta": {
      "total": 1,
      "online": 1,
      "offline": 0
    },
    "pranava": {
      "total": 1,
      "online": 1,
      "offline": 0
    },
    "antakhara": {
      "total": 1,
      "online": 1,
      "offline": 0
    },
    "intelligent_coordinator": {
      "total": 1,
      "online": 1,
      "offline": 0
    }
  },
  "services": {
    "agenta_primary": {
      "service_type": "agenta",
      "endpoint": "agenta://primary",
      "status": "online",
      "capabilities": ["hierarchy_management", "intelligent_routing"],
      "last_seen": "2024-01-15T10:30:00"
    }
  }
}
```

### System Overview

#### Get System Overview
```http
GET /system/overview
```

**Response:**
```json
{
  "timestamp": "2024-01-15T10:30:00",
  "system_stats": {
    "agenta_stats": {
      "total_requests": 1250,
      "successful_routes": 1200,
      "failed_routes": 50,
      "average_response_time": 12.5,
      "success_rate": 0.96
    },
    "pranava_stats": {
      "signals_processed": 980,
      "workflows_started": 15,
      "workflows_completed": 14,
      "routing_decisions": 2500,
      "average_signal_latency": 8.2
    },
    "antakhara_stats": {
      "policies_evaluated": 5000,
      "access_granted": 4800,
      "access_denied": 200,
      "threats_detected": 2,
      "compliance_checks": 45
    }
  },
  "observability": {
    "timestamp": "2024-01-15T10:30:00",
    "total_components_tracked": 3,
    "total_alerts": 1,
    "active_alerts": 1,
    "critical_alerts": 0,
    "system_health": {
      "status": "healthy",
      "score": 95.5
    }
  },
  "service_mesh": {
    "total_services": 7,
    "healthy_services": 7,
    "service_types": 4
  }
}
```

## WebSocket API

### Real-time Monitoring

Connect to WebSocket for real-time updates:
```
ws://localhost:8000/ws/monitor
```

#### Subscribe to Component Updates
```json
{
  "type": "subscribe",
  "channel": "component_updates",
  "component": "agenta"
}
```

#### Subscribe to Alerts
```json
{
  "type": "subscribe",
  "channel": "alerts",
  "severity": ["warning", "critical"]
}
```

#### Receive Updates
```json
{
  "type": "component_update",
  "component": "agenta",
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00",
  "metrics": {
    "routing_performance": 45.2,
    "active_connections": 15
  }
}
```

## Error Responses

All endpoints return standard HTTP status codes and error responses:

```json
{
  "error": "Error description",
  "status": 404,
  "timestamp": "2024-01-15T10:30:00"
}
```

### Common Error Codes

- `400`: Bad Request - Invalid request format
- `401`: Unauthorized - Missing or invalid authentication
- `403`: Forbidden - Insufficient permissions
- `404`: Not Found - Resource not found
- `500`: Internal Server Error - Server-side error

## Rate Limiting

- Standard endpoints: 1000 requests per minute per API key
- Monitoring endpoints: 100 requests per minute per API key
- System overview: 10 requests per minute per API key

## SDKs and Libraries

### Python SDK

```python
from triumvirate_integration import TriumvirateClient

client = TriumvirateClient(api_key="your_api_key", base_url="http://localhost:8000")

# Register a hierarchy node
result = await client.hierarchy.register_node({
    "node_type": "business_function",
    "function": "research_development",
    "node_id": "BF_001",
    "metadata": {"priority": 1}
})

# Request intelligent routing
route = await client.orchestration.request_routing({
    "capability": "reasoning",
    "preferred_function": "research_development"
})

# Check access
access = await client.security.check_access({
    "resource": "hierarchy",
    "action": "write",
    "component": "agenta"
})
```

### JavaScript SDK

```javascript
import { TriumvirateClient } from '@triumvirate/js-sdk';

const client = new TriumvirateClient({
    apiKey: 'your_api_key',
    baseUrl: 'http://localhost:8000'
});

// Register hierarchy node
const result = await client.hierarchy.registerNode({
    nodeType: 'business_function',
    function: 'research_development',
    nodeId: 'BF_001',
    metadata: { priority: 1 }
});

// Request routing
const route = await client.orchestration.requestRouting({
    capability: 'reasoning',
    preferredFunction: 'research_development'
});

// Check access
const access = await client.security.checkAccess({
    resource: 'hierarchy',
    action: 'write',
    component: 'agenta'
});
```

## Examples

### Complete Integration Example

```python
import asyncio
from triumvirate_integration import TriumvirateIntegrationManager

async def main():
    # Initialize the integration system
    manager = TriumvirateIntegrationManager()
    await manager.initialize()
    
    # Start the system
    await manager.start()
    
    try:
        # Get system status
        status = manager.get_status()
        print(f"System status: {status}")
        
        # Create a business function
        api_client = manager.api_server
        
        # Register research and development function
        result = await api_client.handle_api_request(
            "POST", "/hierarchy/register",
            {
                "node_data": {
                    "node_type": "business_function",
                    "function": "research_development",
                    "node_id": "BF_RESEARCH_DEV",
                    "metadata": {
                        "description": "Primary R&D function",
                        "priority": 1
                    }
                }
            }
        )
        print(f"Function registration: {result}")
        
        # Create a workflow
        workflow_result = await api_client.handle_api_request(
            "POST", "/orchestration/workflow/create",
            {
                "workflow_data": {
                    "workflow_id": "research_workflow",
                    "name": "AI Research Analysis",
                    "steps": [
                        {
                            "step_id": "data_collection",
                            "component_type": "microagent",
                            "operation": "collect_data",
                            "parameters": {"source": "research_db"}
                        },
                        {
                            "step_id": "analysis",
                            "component_type": "microagent", 
                            "operation": "analyze_patterns",
                            "parameters": {"input_step": "data_collection"},
                            "dependencies": ["data_collection"]
                        }
                    ]
                }
            }
        )
        print(f"Workflow creation: {workflow_result}")
        
        # Check security access
        access_result = await api_client.handle_api_request(
            "POST", "/security/access/check",
            {
                "resource": "hierarchy",
                "action": "read",
                "component": "agenta"
            }
        )
        print(f"Access check: {access_result}")
        
        # Get system overview
        overview = await api_client.handle_api_request("GET", "/system/overview")
        print(f"System overview: {overview}")
        
    finally:
        # Shutdown gracefully
        await manager.stop()

if __name__ == "__main__":
    asyncio.run(main())
```

This comprehensive API documentation provides all the necessary information to integrate with and manage the Triumvirate Integration Layer effectively.
