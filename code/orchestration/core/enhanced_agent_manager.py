"""
Augur Omega: Enhanced Agent Manager
Advanced real-time process management with dynamic teams and adaptive specialization
"""
import os
import sys
import json
import time
import asyncio
import logging
import threading
import subprocess
import configparser
import psutil
import signal
import traceback
import uuid
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import queue
import weakref
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import websocket
import hashlib

# Setup enhanced logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler('logs/enhanced_agent_manager.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class AgentStatus(Enum):
    """Agent status enumeration"""
    INITIALIZING = "initializing"
    RUNNING = "running"
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    STOPPING = "stopping"
    STOPPED = "stopped"
    FAILED = "failed"
    MAINTENANCE = "maintenance"

class AgentPriority(Enum):
    """Agent priority levels"""
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4
    BACKGROUND = 5

class TeamType(Enum):
    """Agent team types"""
    RESEARCH_AND_DEV = "research_and_dev"
    INTEGRATION_SPECIALISTS = "integration_specialists"
    RESPONSE_UNITS = "response_units"
    CROSS_TEAM_SUPPORT = "cross_team_support"
    SPECIALIST_DEPTH = "specialist_depth"
    RESERVE_TEAMS = "reserve_teams"

@dataclass
class AgentMetrics:
    """Agent performance metrics"""
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    tasks_completed: int = 0
    tasks_failed: int = 0
    uptime_seconds: float = 0.0
    last_activity: datetime = field(default_factory=datetime.now)
    health_score: float = 100.0
    error_rate: float = 0.0

@dataclass
class AgentCapability:
    """Agent capability definition"""
    name: str
    level: int  # 1-10 expertise level
    workload_capacity: int  # max concurrent tasks
    specialization_tags: List[str] = field(default_factory=list)

@dataclass
class AgentInfo:
    """Enhanced agent information"""
    agent_id: str
    name: str
    status: AgentStatus
    priority: AgentPriority
    team_type: TeamType
    capabilities: List[AgentCapability] = field(default_factory=list)
    process: Optional[subprocess.Popen] = None
    start_time: Optional[datetime] = None
    last_heartbeat: datetime = field(default_factory=datetime.now)
    restart_count: int = 0
    metrics: AgentMetrics = field(default_factory=AgentMetrics)
    specialization_level: int = 1
    adaptive_coefficient: float = 1.0
    workload: Dict[str, Any] = field(default_factory=dict)

class RealAgentProcess:
    """Real agent process management"""
    
    def __init__(self, agent_id: str, script_path: str, working_dir: str = None):
        self.agent_id = agent_id
        self.script_path = script_path
        self.working_dir = working_dir or os.getcwd()
        self.process = None
        self.status = AgentStatus.INITIALIZING
        self.start_time = None
        
    def start(self) -> bool:
        """Start the real agent process"""
        try:
            logger.info(f"Starting real agent process: {self.agent_id}")
            
            # Create working directory for agent
            agent_dir = Path(self.working_dir) / "agents" / self.agent_id
            agent_dir.mkdir(parents=True, exist_ok=True)
            
            # Start the actual process
            self.process = subprocess.Popen(
                [sys.executable, self.script_path],
                cwd=str(agent_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                preexec_fn=os.setsid if hasattr(os, 'setsid') else None
            )
            
            self.start_time = datetime.now()
            self.status = AgentStatus.RUNNING
            logger.info(f"Agent {self.agent_id} started with PID: {self.process.pid}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start agent {self.agent_id}: {str(e)}")
            self.status = AgentStatus.FAILED
            return False
    
    def poll(self) -> Optional[int]:
        """Check if process is running and return exit code if stopped"""
        if self.process is None:
            return None
        
        return self.process.poll()
    
    def terminate(self) -> bool:
        """Terminate the agent process gracefully"""
        try:
            if self.process is None:
                return True
                
            self.status = AgentStatus.STOPPING
            
            # Try graceful termination first
            if hasattr(os, 'kill'):
                try:
                    os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
                    time.sleep(2)  # Wait for graceful shutdown
                    
                    if self.process.poll() is None:
                        # Force kill if still running
                        os.killpg(os.getpgid(self.process.pid), signal.SIGKILL)
                except OSError:
                    pass  # Process may have already terminated
            
            self.process.wait(timeout=5)
            self.status = AgentStatus.STOPPED
            logger.info(f"Agent {self.agent_id} terminated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error terminating agent {self.agent_id}: {str(e)}")
            # Force kill as fallback
            try:
                if self.process:
                    self.process.kill()
            except:
                pass
            return False
    
    def is_running(self) -> bool:
        """Check if process is currently running"""
        return self.process is not None and self.poll() is None
    
    def get_performance_stats(self) -> Dict[str, float]:
        """Get process performance statistics"""
        stats = {"cpu": 0.0, "memory": 0.0, "open_files": 0}
        
        try:
            if self.process and self.is_running():
                process = psutil.Process(self.process.pid)
                stats["cpu"] = process.cpu_percent(interval=0.1)
                stats["memory"] = process.memory_percent()
                stats["open_files"] = len(process.open_files())
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
        
        return stats

class AdaptiveSpecializer:
    """System for adaptive agent specialization"""
    
    def __init__(self):
        self.specialization_history = {}
        self.performance_patterns = {}
        self.learning_models = {}
        
    def analyze_workload_pattern(self, agent_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze workload patterns to suggest specialization"""
        analysis = {
            "recommended_specialization": None,
            "expertise_boost": 0.0,
            "specialization_tags": [],
            "adaptive_coefficient": 1.0
        }
        
        # Analyze task complexity
        complexity_score = task_data.get("complexity_score", 1)
        if complexity_score > 8:
            analysis["recommended_specialization"] = "expert"
            analysis["expertise_boost"] = 0.2
            analysis["specialization_tags"].append("high_complexity")
        elif complexity_score < 3:
            analysis["recommended_specialization"] = "routine"
            analysis["expertise_boost"] = 0.1
            analysis["specialization_tags"].append("routine_processing")
        
        # Analyze domain patterns
        domain = task_data.get("domain", "")
        if domain in ["ai_ml", "data_science"]:
            analysis["specialization_tags"].append("ai_specialist")
            analysis["expertise_boost"] += 0.15
        elif domain in ["web_dev", "frontend"]:
            analysis["specialization_tags"].append("frontend_specialist")
            analysis["expertise_boost"] += 0.1
        
        # Calculate adaptive coefficient
        success_rate = task_data.get("success_rate", 1.0)
        analysis["adaptive_coefficient"] = 1.0 + (success_rate - 0.8) * 0.5
        
        return analysis
    
    def update_agent_capability(self, agent_id: str, task_outcome: Dict[str, Any]):
        """Update agent capabilities based on task outcomes"""
        # Store performance pattern
        if agent_id not in self.performance_patterns:
            self.performance_patterns[agent_id] = {}
        
        domain = task_outcome.get("domain", "general")
        if domain not in self.performance_patterns[agent_id]:
            self.performance_patterns[agent_id][domain] = {
                "tasks": 0,
                "success_rate": 1.0,
                "avg_performance": 1.0
            }
        
        pattern = self.performance_patterns[agent_id][domain]
        pattern["tasks"] += 1
        
        # Update success rate
        success = task_outcome.get("success", True)
        alpha = 0.1  # Learning rate
        pattern["success_rate"] = (1 - alpha) * pattern["success_rate"] + alpha * (1.0 if success else 0.0)
        
        # Update performance score
        performance = task_outcome.get("performance_score", 1.0)
        pattern["avg_performance"] = (1 - alpha) * pattern["avg_performance"] + alpha * performance

class EnhancedAgentManager:
    """Enhanced agent manager with real-time process management and dynamic teams"""
    
    def __init__(self, config_path: str = "config/enhanced_agents.cfg"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.agents: Dict[str, AgentInfo] = {}
        self.teams: Dict[str, List[str]] = {}
        self.monitoring_active = False
        self.monitor_thread = None
        self.monitor_lock = threading.Lock()
        self.adaptive_specializer = AdaptiveSpecializer()
        self.websocket_clients = weakref.WeakSet()
        self.process_executor = ProcessPoolExecutor(max_workers=8)
        
        # Performance tracking
        self.team_performance = {}
        self.system_metrics = AgentMetrics()
        
        # Create necessary directories
        Path("logs").mkdir(exist_ok=True)
        Path("config").mkdir(exist_ok=True)
        Path("agents").mkdir(exist_ok=True)
        
        # Initialize teams
        self._initialize_teams()
        
        logger.info("Enhanced Agent Manager initialized")
    
    def _load_config(self) -> configparser.ConfigParser:
        """Load enhanced agent configuration"""
        config = configparser.ConfigParser()
        
        if self.config_path.exists():
            config.read(self.config_path)
        else:
            self._create_default_config()
            config.read(self.config_path)
        
        return config
    
    def _create_default_config(self):
        """Create default enhanced agent configuration"""
        config = configparser.ConfigParser()
        
        # Enhanced settings
        config['enhanced_settings'] = {
            'real_process_mode': 'true',
            'adaptive_specialization': 'true',
            'team_formation': 'dynamic',
            'monitoring_interval': '5',
            'websocket_enabled': 'true'
        }
        
        # Dynamic team configuration
        config['dynamic_teams'] = {
            'research_and_dev': '5',
            'integration_specialists': '4', 
            'response_units': '6',
            'cross_team_support': '3',
            'specialist_depth': '8',
            'reserve_teams': '4'
        }
        
        # Adaptive specialization settings
        config['adaptive_specialization'] = {
            'learning_rate': '0.1',
            'performance_threshold': '0.8',
            'specialization_boost': 'true',
            'cross_training': 'true'
        }
        
        # Monitoring settings
        config['monitoring'] = {
            'enable_websocket': 'true',
            'websocket_port': '8765',
            'metrics_collection_interval': '3',
            'alert_thresholds': 'cpu:80,memory:85,error_rate:10'
        }
        
        # Agent specialization levels
        config['specialization_levels'] = {
            'junior': '1-3',
            'mid': '4-6',
            'senior': '7-8',
            'expert': '9-10'
        }
        
        # Create directory and write config
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            config.write(f)
        
        logger.info(f"Enhanced configuration created at {self.config_path}")
    
    def _initialize_teams(self):
        """Initialize dynamic team structure"""
        team_config = self.config.get('dynamic_teams', {})
        
        for team_type_str, count in team_config.items():
            try:
                team_type = TeamType(team_type_str)
                team_count = int(count)
                self.teams[team_type_str] = []
                
                # Create agents for each team
                for i in range(team_count):
                    agent_name = f"{team_type_str}_{i+1:03d}"
                    self._create_agent(agent_name, team_type)
                    
            except ValueError:
                logger.warning(f"Unknown team type: {team_type_str}")
                continue
    
    def _create_agent(self, name: str, team_type: TeamType, capabilities: List[AgentCapability] = None) -> str:
        """Create a new agent with given capabilities"""
        agent_id = str(uuid.uuid4())[:8]
        
        # Generate capabilities if not provided
        if capabilities is None:
            capabilities = self._generate_capabilities(name, team_type)
        
        agent_info = AgentInfo(
            agent_id=agent_id,
            name=name,
            status=AgentStatus.INITIALIZING,
            priority=AgentPriority.NORMAL,
            team_type=team_type,
            capabilities=capabilities,
            start_time=datetime.now()
        )
        
        self.agents[agent_id] = agent_info
        self.teams[team_type.value].append(agent_id)
        
        logger.info(f"Created agent {name} ({agent_id}) in team {team_type.value}")
        return agent_id
    
    def _generate_capabilities(self, name: str, team_type: TeamType) -> List[AgentCapability]:
        """Generate capabilities based on agent name and team type"""
        capabilities = []
        
        # Base capabilities by team type
        base_capabilities = {
            TeamType.RESEARCH_AND_DEV: ["research", "analysis", "development"],
            TeamType.INTEGRATION_SPECIALISTS: ["integration", "testing", "deployment"],
            TeamType.RESPONSE_UNITS: ["response", "incident", "support"],
            TeamType.CROSS_TEAM_SUPPORT: ["coordination", "communication", "support"],
            TeamType.SPECIALIST_DEPTH: ["expertise", "mentoring", "consultation"],
            TeamType.RESERVE_TEAMS: ["backup", "emergency", "scalability"]
        }
        
        base_skills = base_capabilities.get(team_type, ["general"])
        
        # Generate random specialization
        import random
        specialization_level = random.randint(1, 10)
        workload_capacity = random.randint(1, 5)
        
        for skill in base_skills:
            level = max(1, specialization_level + random.randint(-2, 2))
            capabilities.append(AgentCapability(
                name=skill,
                level=min(10, level),
                workload_capacity=workload_capacity,
                specialization_tags=[f"{skill}_specialist"]
            ))
        
        return capabilities
    
    def start_agent(self, agent_id: str) -> bool:
        """Start a specific agent with real process"""
        if agent_id not in self.agents:
            logger.error(f"Agent {agent_id} not found")
            return False
        
        agent = self.agents[agent_id]
        agent.status = AgentStatus.INITIALIZING
        
        try:
            # Create agent script
            script_path = self._create_agent_script(agent)
            if not script_path:
                agent.status = AgentStatus.FAILED
                return False
            
            # Start real process
            agent.process = RealAgentProcess(agent_id, script_path)
            if not agent.process.start():
                agent.status = AgentStatus.FAILED
                return False
            
            agent.start_time = datetime.now()
            agent.status = AgentStatus.RUNNING
            agent.last_heartbeat = datetime.now()
            
            logger.info(f"Agent {agent.name} ({agent_id}) started successfully")
            self._broadcast_update("agent_started", agent_id)
            return True
            
        except Exception as e:
            logger.error(f"Failed to start agent {agent_id}: {str(e)}")
            agent.status = AgentStatus.FAILED
            return False
    
    def _create_agent_script(self, agent: AgentInfo) -> Optional[str]:
        """Create an agent script based on its capabilities"""
        try:
            agent_dir = Path("agents") / agent.agent_id
            agent_dir.mkdir(parents=True, exist_ok=True)
            
            script_path = agent_dir / "agent.py"
            
            # Generate agent script based on capabilities
            script_content = self._generate_agent_script_content(agent)
            
            with open(script_path, 'w') as f:
                f.write(script_content)
            
            # Make script executable
            os.chmod(script_path, 0o755)
            
            return str(script_path)
            
        except Exception as e:
            logger.error(f"Failed to create agent script for {agent.agent_id}: {str(e)}")
            return None
    
    def _generate_agent_script_content(self, agent: AgentInfo) -> str:
        """Generate Python script content for the agent"""
        capabilities_text = ", ".join([f"{cap.name}: {cap.level}/10" for cap in agent.capabilities])
        
        script = f'''#!/usr/bin/env python3
"""
Agent: {agent.name} (ID: {agent.agent_id})
Team: {agent.team_type.value}
Capabilities: {capabilities_text}
"""

import time
import json
import sys
import random
from datetime import datetime
from typing import Dict, List, Any

class {agent.name.replace(" ", "").replace("-", "")}Agent:
    def __init__(self):
        self.agent_id = "{agent.agent_id}"
        self.name = "{agent.name}"
        self.status = "running"
        self.capabilities = {json.dumps([{"name": cap.name, "level": cap.level} for cap in agent.capabilities])}
        
    def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a task based on agent capabilities"""
        domain = task.get("domain", "general")
        complexity = task.get("complexity_score", 1)
        
        # Check if agent can handle the task
        best_capability = None
        best_score = 0
        
        for cap in self.capabilities:
            if domain.lower() in cap["name"].lower():
                score = cap["level"] / 10.0
                if score > best_score:
                    best_score = score
                    best_capability = cap["name"]
        
        # Simulate task processing
        processing_time = random.uniform(0.5, 3.0)
        time.sleep(processing_time)
        
        # Determine success based on capability level
        success_probability = best_score if best_capability else 0.5
        success = random.random() < success_probability
        
        result = {{
            "agent_id": self.agent_id,
            "task_id": task.get("task_id", "unknown"),
            "success": success,
            "processing_time": processing_time,
            "capability_used": best_capability,
            "performance_score": random.uniform(0.7, 1.0) if success else random.uniform(0.3, 0.7),
            "timestamp": datetime.now().isoformat()
        }}
        
        print(json.dumps(result))
        return result
    
    def run(self):
        """Main agent loop"""
        print(f"Agent {{self.name}} ({{self.agent_id}}) started")
        
        while True:
            try:
                # Simulate heartbeat
                heartbeat = {{
                    "agent_id": self.agent_id,
                    "status": "alive",
                    "timestamp": datetime.now().isoformat()
                }}
                print(f"HEARTBEAT: {{json.dumps(heartbeat)}}")
                
                # Simulate random task processing (10% chance per cycle)
                if random.random() < 0.1:
                    task = {{
                        "task_id": f"task_{{random.randint(1000, 9999)}}",
                        "domain": random.choice(["ai_ml", "web_dev", "data_science", "integration", "support"]),
                        "complexity_score": random.randint(1, 10)
                    }}
                    self.process_task(task)
                
                time.sleep(5)  # Main loop interval
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Agent error: {{e}}")
                time.sleep(1)

if __name__ == "__main__":
    agent = {agent.name.replace(" ", "").replace("-", "")}Agent()
    agent.run()
'''
        
        return script
    
    def start_monitoring(self):
        """Start real-time monitoring of all agents"""
        if self.monitoring_active:
            logger.warning("Monitoring already active")
            return
        
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("Enhanced monitoring started")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                current_time = datetime.now()
                
                # Monitor all agents
                for agent_id, agent in list(self.agents.items()):
                    # Update metrics
                    self._update_agent_metrics(agent)
                    
                    # Check heartbeat
                    if agent.last_heartbeat < current_time - timedelta(seconds=30):
                        logger.warning(f"Agent {agent.name} ({agent_id}) heartbeat timeout")
                        agent.status = AgentStatus.ERROR
                        
                        # Attempt restart if eligible
                        if agent.restart_count < 5:
                            agent.restart_count += 1
                            logger.info(f"Attempting to restart agent {agent.name} ({agent.restart_count}/5)")
                            self.restart_agent(agent_id)
                    
                    # Check process health
                    if agent.process:
                        stats = agent.process.get_performance_stats()
                        agent.metrics.cpu_usage = stats.get("cpu", 0.0)
                        agent.metrics.memory_usage = stats.get("memory", 0.0)
                
                # Update system metrics
                self._update_system_metrics()
                
                # Broadcast updates to WebSocket clients
                self._broadcast_monitoring_update()
                
                time.sleep(int(self.config.get('enhanced_settings', 'monitoring_interval', fallback=5)))
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {str(e)}")
                time.sleep(5)
    
    def _update_agent_metrics(self, agent: AgentInfo):
        """Update agent performance metrics"""
        try:
            if agent.process and agent.process.is_running():
                # Calculate uptime
                if agent.start_time:
                    agent.metrics.uptime_seconds = (datetime.now() - agent.start_time).total_seconds()
                
                # Update health score based on error rate and performance
                total_tasks = agent.metrics.tasks_completed + agent.metrics.tasks_failed
                if total_tasks > 0:
                    agent.metrics.error_rate = agent.metrics.tasks_failed / total_tasks
                    agent.metrics.health_score = max(0, 100 - (agent.metrics.error_rate * 100))
                
                agent.last_heartbeat = datetime.now()
                agent.status = AgentStatus.RUNNING if agent.status == AgentStatus.BUSY else agent.status
            else:
                if agent.process and agent.process.poll() is not None:
                    # Process has stopped
                    agent.status = AgentStatus.FAILED
                    logger.warning(f"Agent {agent.name} process stopped")
                    
        except Exception as e:
            logger.error(f"Error updating metrics for {agent.agent_id}: {str(e)}")
    
    def _update_system_metrics(self):
        """Update overall system metrics"""
        try:
            # Get system resource usage
            self.system_metrics.cpu_usage = psutil.cpu_percent(interval=0.1)
            self.system_metrics.memory_usage = psutil.virtual_memory().percent
            
            # Calculate team performance
            for team_name, agent_ids in self.teams.items():
                team_metrics = {
                    "total_agents": len(agent_ids),
                    "active_agents": 0,
                    "avg_health_score": 0.0,
                    "total_tasks": 0
                }
                
                total_health = 0
                total_tasks = 0
                
                for agent_id in agent_ids:
                    if agent_id in self.agents:
                        agent = self.agents[agent_id]
                        if agent.status in [AgentStatus.RUNNING, AgentStatus.BUSY]:
                            team_metrics["active_agents"] += 1
                        
                        total_health += agent.metrics.health_score
                        total_tasks += agent.metrics.tasks_completed + agent.metrics.tasks_failed
                
                if len(agent_ids) > 0:
                    team_metrics["avg_health_score"] = total_health / len(agent_ids)
                    team_metrics["total_tasks"] = total_tasks
                
                self.team_performance[team_name] = team_metrics
                
        except Exception as e:
            logger.error(f"Error updating system metrics: {str(e)}")
    
    def restart_agent(self, agent_id: str) -> bool:
        """Restart an agent"""
        if agent_id not in self.agents:
            return False
        
        agent = self.agents[agent_id]
        
        try:
            # Stop existing process
            if agent.process:
                agent.process.terminate()
            
            # Reset agent state
            agent.status = AgentStatus.INITIALIZING
            agent.last_heartbeat = datetime.now()
            
            # Start fresh
            return self.start_agent(agent_id)
            
        except Exception as e:
            logger.error(f"Failed to restart agent {agent_id}: {str(e)}")
            agent.status = AgentStatus.FAILED
            return False
    
    def assign_task(self, agent_id: str, task: Dict[str, Any]) -> bool:
        """Assign a task to an agent"""
        if agent_id not in self.agents:
            return False
        
        agent = self.agents[agent_id]
        
        if agent.status != AgentStatus.RUNNING:
            return False
        
        try:
            # Use adaptive specialization to optimize task assignment
            specialization_analysis = self.adaptive_specializer.analyze_workload_pattern(agent_id, task)
            
            # Update agent workload
            agent.workload["current_task"] = task
            agent.workload["specialization_boost"] = specialization_analysis.get("expertise_boost", 0.0)
            agent.workload["adaptive_coefficient"] = specialization_analysis.get("adaptive_coefficient", 1.0)
            
            agent.status = AgentStatus.BUSY
            self._broadcast_update("task_assigned", {"agent_id": agent_id, "task": task})
            
            logger.info(f"Task assigned to agent {agent.name} ({agent_id})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to assign task to agent {agent_id}: {str(e)}")
            return False
    
    def _broadcast_update(self, event_type: str, data: Any):
        """Broadcast update to WebSocket clients"""
        update = {
            "type": event_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        
        # This would be implemented to send to WebSocket clients
        # For now, we'll just log it
        logger.debug(f"Broadcasting {event_type}: {data}")
    
    def _broadcast_monitoring_update(self):
        """Broadcast comprehensive monitoring update"""
        monitoring_data = {
            "system_metrics": {
                "cpu_usage": self.system_metrics.cpu_usage,
                "memory_usage": self.system_metrics.memory_usage,
                "active_agents": len([a for a in self.agents.values() if a.status == AgentStatus.RUNNING]),
                "total_agents": len(self.agents)
            },
            "agents": {},
            "teams": self.team_performance,
            "timestamp": datetime.now().isoformat()
        }
        
        # Include agent details
        for agent_id, agent in self.agents.items():
            monitoring_data["agents"][agent_id] = {
                "name": agent.name,
                "status": agent.status.value,
                "team": agent.team_type.value,
                "metrics": {
                    "cpu_usage": agent.metrics.cpu_usage,
                    "memory_usage": agent.metrics.memory_usage,
                    "health_score": agent.metrics.health_score,
                    "tasks_completed": agent.metrics.tasks_completed,
                    "error_rate": agent.metrics.error_rate
                }
            }
        
        self._broadcast_update("monitoring_update", monitoring_data)
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive status of all agents and teams"""
        status = {
            "manager_running": self.monitoring_active,
            "total_agents": len(self.agents),
            "active_agents": len([a for a in self.agents.values() if a.status == AgentStatus.RUNNING]),
            "system_metrics": {
                "cpu_usage": self.system_metrics.cpu_usage,
                "memory_usage": self.system_metrics.memory_usage,
                "uptime": self.system_metrics.uptime_seconds
            },
            "teams": {},
            "agents": {}
        }
        
        # Team status
        for team_name, agent_ids in self.teams.items():
            team_status = {
                "total_agents": len(agent_ids),
                "active_agents": len([aid for aid in agent_ids if aid in self.agents and self.agents[aid].status == AgentStatus.RUNNING]),
                "agents": []
            }
            
            for agent_id in agent_ids:
                if agent_id in self.agents:
                    agent = self.agents[agent_id]
                    team_status["agents"].append({
                        "agent_id": agent_id,
                        "name": agent.name,
                        "status": agent.status.value,
                        "health_score": agent.metrics.health_score
                    })
            
            status["teams"][team_name] = team_status
        
        # Individual agent details
        for agent_id, agent in self.agents.items():
            status["agents"][agent_id] = {
                "name": agent.name,
                "status": agent.status.value,
                "team": agent.team_type.value,
                "priority": agent.priority.value,
                "capabilities": [{"name": cap.name, "level": cap.level} for cap in agent.capabilities],
                "metrics": {
                    "cpu_usage": agent.metrics.cpu_usage,
                    "memory_usage": agent.metrics.memory_usage,
                    "health_score": agent.metrics.health_score,
                    "tasks_completed": agent.metrics.tasks_completed,
                    "tasks_failed": agent.metrics.tasks_failed,
                    "uptime_seconds": agent.metrics.uptime_seconds,
                    "restart_count": agent.restart_count
                },
                "start_time": agent.start_time.isoformat() if agent.start_time else None,
                "last_heartbeat": agent.last_heartbeat.isoformat()
            }
        
        return status
    
    def start_all_agents(self):
        """Start all agents across all teams"""
        logger.info("Starting all enhanced agents...")
        
        started_count = 0
        for agent_id in self.agents:
            if self.start_agent(agent_id):
                started_count += 1
        
        logger.info(f"Started {started_count} agents out of {len(self.agents)} total")
        
        # Start monitoring
        self.start_monitoring()
    
    def stop_all_agents(self):
        """Stop all agents gracefully"""
        logger.info("Stopping all agents...")
        
        self.monitoring_active = False
        
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        
        # Stop all agent processes
        for agent_id, agent in self.agents.items():
            try:
                if agent.process:
                    agent.process.terminate()
                agent.status = AgentStatus.STOPPED
                logger.debug(f"Stopped agent {agent.name}")
            except Exception as e:
                logger.error(f"Error stopping agent {agent_id}: {str(e)}")
        
        # Clean up executor
        if hasattr(self, 'process_executor'):
            self.process_executor.shutdown(wait=True)
        
        logger.info("All agents stopped")
    
    def get_team_performance(self, team_name: str = None) -> Dict[str, Any]:
        """Get performance metrics for teams"""
        if team_name:
            return self.team_performance.get(team_name, {})
        return self.team_performance
    
    def optimize_team_composition(self):
        """Optimize team composition based on performance patterns"""
        logger.info("Optimizing team composition...")
        
        for team_name, team_data in self.team_performance.items():
            # Analyze team performance
            avg_health = team_data.get("avg_health_score", 0)
            total_tasks = team_data.get("total_tasks", 0)
            
            if avg_health < 70 and total_tasks > 100:
                # Team needs optimization
                agent_ids = self.teams.get(team_name, [])
                poor_performers = []
                
                for agent_id in agent_ids:
                    if agent_id in self.agents:
                        agent = self.agents[agent_id]
                        if agent.metrics.health_score < 60:
                            poor_performers.append(agent_id)
                
                # Suggest redistributing poor performers
                if poor_performers:
                    logger.warning(f"Team {team_name} has {len(poor_performers)} underperforming agents")
                    # Could implement automatic rebalancing here
                    
        logger.info("Team optimization analysis complete")

def main():
    """Main function"""
    manager = EnhancedAgentManager()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'start':
            print("Starting enhanced agent orchestration system...")
            manager.start_all_agents()
            print("Enhanced orchestration system active.")
            
        elif command == 'stop':
            print("Stopping enhanced orchestration system...")
            manager.stop_all_agents()
            print("System deactivated.")
            
        elif command == 'status':
            status = manager.get_status()
            print("Enhanced Agent Orchestration System Status:")
            print(f"  Monitoring Active: {status['manager_running']}")
            print(f"  Total Agents: {status['total_agents']}")
            print(f"  Active Agents: {status['active_agents']}")
            print(f"  System CPU: {status['system_metrics']['cpu_usage']:.1f}%")
            print(f"  System Memory: {status['system_metrics']['memory_usage']:.1f}%")
            
            if status['teams']:
                print("\\nTeam Performance:")
                for team_name, team_data in status['teams'].items():
                    print(f"  {team_name}: {team_data['active_agents']}/{team_data['total_agents']} active")
            
        elif command == 'optimize':
            print("Optimizing team composition...")
            manager.optimize_team_composition()
            print("Optimization complete.")
            
        else:
            print("Enhanced Agent Orchestration System")
            print("Usage: python enhanced_agent_manager.py [start|stop|status|optimize]")
            print("  start - Start all agents and monitoring")
            print("  stop - Stop all agents")
            print("  status - Get comprehensive system status")
            print("  optimize - Analyze and optimize team performance")
            
    else:
        print("Enhanced Agent Orchestration System")
        print("Usage: python enhanced_agent_manager.py [start|stop|status|optimize]")

if __name__ == "__main__":
    main()