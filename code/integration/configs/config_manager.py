"""
Configuration management for Triumvirate Integration Layer
"""

import json
import yaml
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class IntegrationConfig:
    """Configuration for triumvirate integration"""
    
    # Component configurations
    agenta_config: Dict[str, Any]
    pranava_config: Dict[str, Any]
    antakhara_config: Dict[str, Any]
    shared_config: Dict[str, Any]
    
    # Service discovery settings
    service_discovery: Dict[str, Any]
    
    # Monitoring and observability
    monitoring: Dict[str, Any]
    
    # API configuration
    api_config: Dict[str, Any]
    
    # Security settings
    security: Dict[str, Any]
    
    # Logging configuration
    logging: Dict[str, Any]

class ConfigManager:
    """Configuration management system"""
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path or "configs/integration_config.yaml"
        self.config: Optional[IntegrationConfig] = None
        
    def load_config(self) -> IntegrationConfig:
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    if self.config_path.endswith('.yaml') or self.config_path.endswith('.yml'):
                        config_data = yaml.safe_load(f)
                    else:
                        config_data = json.load(f)
                        
                self.config = IntegrationConfig(**config_data)
                return self.config
            else:
                # Return default configuration
                self.config = self._create_default_config()
                return self.config
                
        except Exception as e:
            print(f"Error loading configuration: {e}")
            return self._create_default_config()
            
    def save_config(self, config: IntegrationConfig = None) -> bool:
        """Save configuration to file"""
        try:
            config_to_save = config or self.config
            if not config_to_save:
                return False
                
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            config_dict = asdict(config_to_save)
            
            with open(self.config_path, 'w') as f:
                if self.config_path.endswith('.yaml') or self.config_path.endswith('.yml'):
                    yaml.dump(config_dict, f, default_flow_style=False, indent=2)
                else:
                    json.dump(config_dict, f, indent=2)
                    
            return True
            
        except Exception as e:
            print(f"Error saving configuration: {e}")
            return False
            
    def _create_default_config(self) -> IntegrationConfig:
        """Create default configuration"""
        return IntegrationConfig(
            agenta_config={
                "component_id": "primary",
                "load_balancing_enabled": True,
                "intelligent_routing": True,
                "hierarchy_levels": ["business_function", "team", "microagent", "kosha"],
                "business_functions": [
                    "research_development",
                    "integration_specialists", 
                    "response_units",
                    "cross_team_support",
                    "specialized_depth",
                    "reserve_teams"
                ]
            },
            pranava_config={
                "component_id": "primary",
                "health_check_interval": 30,
                "signal_ttl": 300,
                "routing_strategies": {
                    "default": "intelligent",
                    "realtime": "least_response_time",
                    "batch": "round_robin",
                    "compute_intensive": "weighted_round_robin"
                }
            },
            antakhara_config={
                "component_id": "primary",
                "security_level": "medium",
                "compliance_frameworks": ["gdpr", "hipaa", "owasp", "iso27001"],
                "threat_detection": True,
                "audit_logging": True
            },
            shared_config={
                "message_queue_size": 10000,
                "health_check_timeout": 30,
                "max_restart_attempts": 3,
                "graceful_shutdown_timeout": 30
            },
            service_discovery={
                "health_check_interval": 30,
                "service_ttl": 300,
                "auto_discovery": True,
                "capability_matching": True
            },
            monitoring={
                "metrics_retention_hours": 24,
                "max_alerts": 1000,
                "system_metrics_interval": 10,
                "health_monitoring": True
            },
            api_config={
                "host": "0.0.0.0",
                "port": 8000,
                "cors_enabled": True,
                "rate_limiting": True,
                "request_timeout": 30
            },
            security={
                "api_key_required": True,
                "jwt_enabled": True,
                "https_only": False,
                "cors_origins": ["http://localhost:3000"],
                "rate_limit_per_minute": 1000
            },
            logging={
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "file_logging": True,
                "console_logging": True,
                "log_file": "logs/triumvirate.log"
            }
        )
        
    def update_config(self, section: str, key: str, value: Any) -> bool:
        """Update a specific configuration value"""
        try:
            config_dict = asdict(self.config)
            
            if section in config_dict:
                config_dict[section][key] = value
                self.config = IntegrationConfig(**config_dict)
                return True
                
            return False
            
        except Exception as e:
            print(f"Error updating configuration: {e}")
            return False
            
    def get_config_section(self, section: str) -> Optional[Dict[str, Any]]:
        """Get a specific configuration section"""
        if not self.config:
            return None
            
        config_dict = asdict(self.config)
        return config_dict.get(section)
