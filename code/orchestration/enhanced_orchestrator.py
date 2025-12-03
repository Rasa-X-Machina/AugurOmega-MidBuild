"""
Augur Omega: Enhanced Orchestration System
Main orchestrator that integrates all enhanced components
"""
import os
import sys
import json
import time
import logging
import threading
import asyncio
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import signal

# Add core modules to path
sys.path.append(str(Path(__file__).parent))

from core.enhanced_agent_manager import EnhancedAgentManager
from teams.dynamic_team_orchestrator import DynamicTeamOrchestrator, WorkloadRequest, WorkloadType, SpecializationDomain
from auditor.executable_auditor import ExecutableAuditor
from monitoring.monitoring_dashboard import monitoring_store, run_dashboard

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler('logs/enhanced_orchestrator.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class OrchestrationMetrics:
    """System-wide orchestration metrics"""
    uptime_seconds: float = 0.0
    total_workloads_processed: int = 0
    successful_workloads: int = 0
    failed_workloads: int = 0
    avg_workload_completion_time: float = 0.0
    total_audits_completed: int = 0
    audit_pass_rate: float = 1.0
    system_health_score: float = 100.0
    last_heartbeat: datetime = field(default_factory=datetime.now)

class SystemIntegrator:
    """Integrates all enhanced orchestration components"""
    
    def __init__(self, config_path: str = "config/enhanced_orchestrator.cfg"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        
        # Initialize components
        self.agent_manager = EnhancedAgentManager()
        self.team_orchestrator = DynamicTeamOrchestrator(self.agent_manager)
        self.executable_auditor = ExecutableAuditor()
        
        # Integration state
        self.orchestrator_running = False
        self.integration_thread = None
        self.metrics = OrchestrationMetrics()
        self.system_lock = threading.Lock()
        
        # Performance tracking
        self.workload_history = []
        self.audit_history = []
        self.system_events = []
        
        # Create necessary directories
        Path("logs").mkdir(exist_ok=True)
        Path("config").mkdir(exist_ok=True)
        
        logger.info("Enhanced Orchestration System initialized")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load orchestration configuration"""
        config_file = self.config_path
        
        if config_file.exists():
            with open(config_file, 'r') as f:
                return json.load(f)
        else:
            # Create default configuration
            default_config = {
                "orchestration": {
                    "start_agent_manager": True,
                    "start_team_orchestrator": True,
                    "start_executable_auditor": True,
                    "start_monitoring_dashboard": True,
                    "dashboard_host": "0.0.0.0",
                    "dashboard_port": 5000
                },
                "integration": {
                    "sync_interval_seconds": 10,
                    "metrics_collection_interval": 30,
                    "health_check_interval": 15,
                    "alert_thresholds": {
                        "cpu_usage": 80,
                        "memory_usage": 85,
                        "error_rate": 5,
                        "health_score": 70
                    }
                },
                "workload_management": {
                    "auto_workload_generation": True,
                    "workload_generation_interval": 60,
                    "workload_types": ["research_project", "development_sprint", "emergency_response"]
                }
            }
            
            # Create config directory and file
            config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            
            return default_config
    
    def start_orchestration_system(self):
        """Start the entire enhanced orchestration system"""
        if self.orchestrator_running:
            logger.warning("Orchestration system already running")
            return
        
        logger.info("Starting Enhanced Orchestration System...")
        
        try:
            # Start core components
            if self.config.get("orchestration", {}).get("start_agent_manager", True):
                logger.info("Starting Enhanced Agent Manager...")
                self.agent_manager.start_all_agents()
                time.sleep(2)  # Give agents time to start
            
            if self.config.get("orchestration", {}).get("start_team_orchestrator", True):
                logger.info("Starting Dynamic Team Orchestrator...")
                self.team_orchestrator.start_orchestration()
                time.sleep(1)
            
            if self.config.get("orchestration", {}).get("start_executable_auditor", True):
                logger.info("Starting Executable Auditor...")
                self.executable_auditor.start_auditor()
                time.sleep(1)
            
            # Start monitoring dashboard
            if self.config.get("orchestration", {}).get("start_monitoring_dashboard", True):
                logger.info("Starting Monitoring Dashboard...")
                dashboard_host = self.config.get("orchestration", {}).get("dashboard_host", "0.0.0.0")
                dashboard_port = self.config.get("orchestration", {}).get("dashboard_port", 5000)
                
                # Start dashboard in separate thread
                dashboard_thread = threading.Thread(
                    target=run_dashboard,
                    args=(dashboard_host, dashboard_port, False),
                    daemon=True
                )
                dashboard_thread.start()
                time.sleep(1)
            
            # Start integration loop
            self.orchestrator_running = True
            self.integration_thread = threading.Thread(target=self._integration_loop, daemon=True)
            self.integration_thread.start()
            
            logger.info("Enhanced Orchestration System started successfully!")
            logger.info(f"Monitoring Dashboard available at http://localhost:{dashboard_port}")
            
        except Exception as e:
            logger.error(f"Failed to start orchestration system: {str(e)}")
            self.stop_orchestration_system()
            raise
    
    def stop_orchestration_system(self):
        """Stop the entire orchestration system"""
        if not self.orchestrator_running:
            logger.warning("Orchestration system not running")
            return
        
        logger.info("Stopping Enhanced Orchestration System...")
        
        self.orchestrator_running = False
        
        # Stop integration thread
        if self.integration_thread:
            self.integration_thread.join(timeout=5)
        
        # Stop components in reverse order
        try:
            if hasattr(self, 'team_orchestrator'):
                self.team_orchestrator.stop_orchestration()
                logger.info("Dynamic Team Orchestrator stopped")
        except Exception as e:
            logger.error(f"Error stopping team orchestrator: {str(e)}")
        
        try:
            if hasattr(self, 'executable_auditor'):
                self.executable_auditor.stop_auditor()
                logger.info("Executable Auditor stopped")
        except Exception as e:
            logger.error(f"Error stopping executable auditor: {str(e)}")
        
        try:
            if hasattr(self, 'agent_manager'):
                self.agent_manager.stop_all_agents()
                logger.info("Enhanced Agent Manager stopped")
        except Exception as e:
            logger.error(f"Error stopping agent manager: {str(e)}")
        
        logger.info("Enhanced Orchestration System stopped")
    
    def _integration_loop(self):
        """Main integration loop that coordinates all components"""
        sync_interval = self.config.get("integration", {}).get("sync_interval_seconds", 10)
        metrics_interval = self.config.get("integration", {}).get("metrics_collection_interval", 30)
        health_interval = self.config.get("integration", {}).get("health_check_interval", 15)
        
        last_metrics_time = time.time()
        last_health_time = time.time()
        
        while self.orchestrator_running:
            try:
                current_time = time.time()
                
                # Update system metrics
                if current_time - last_metrics_time >= metrics_interval:
                    self._update_system_metrics()
                    last_metrics_time = current_time
                
                # Perform health checks
                if current_time - last_health_time >= health_interval:
                    self._perform_health_checks()
                    last_health_time = current_time
                
                # Synchronize data between components
                self._synchronize_component_data()
                
                # Generate demo workloads if enabled
                if self.config.get("workload_management", {}).get("auto_workload_generation", False):
                    self._generate_demo_workloads()
                
                # Update monitoring store
                self._update_monitoring_data()
                
                time.sleep(sync_interval)
                
            except Exception as e:
                logger.error(f"Error in integration loop: {str(e)}")
                time.sleep(5)
    
    def _update_system_metrics(self):
        """Update system-wide metrics"""
        try:
            # Update orchestrator metrics
            self.metrics.uptime_seconds = (datetime.now() - self.metrics.last_heartbeat).total_seconds()
            
            # Get component metrics
            agent_status = self.agent_manager.get_status()
            orchestration_status = self.team_orchestrator.get_orchestration_status()
            audit_status = self.executable_auditor.get_audit_status()
            
            # Calculate overall system health
            health_components = []
            
            if agent_status:
                active_ratio = agent_status.get("active_agents", 0) / max(1, agent_status.get("total_agents", 1))
                health_components.append(active_ratio * 100)
            
            if orchestration_status:
                success_rate = orchestration_status.get("metrics", {}).get("success_rate", 1.0)
                health_components.append(success_rate * 100)
            
            if audit_status:
                audit_success_rate = audit_status.get("audit_statistics", {}).get("success_rate", 100.0)
                health_components.append(audit_success_rate)
            
            if health_components:
                self.metrics.system_health_score = sum(health_components) / len(health_components)
            
            self.metrics.last_heartbeat = datetime.now()
            
        except Exception as e:
            logger.error(f"Error updating system metrics: {str(e)}")
    
    def _perform_health_checks(self):
        """Perform comprehensive health checks on all components"""
        alerts = []
        
        try:
            # Check agent manager health
            agent_status = self.agent_manager.get_status()
            if agent_status:
                system_metrics = agent_status.get("system_metrics", {})
                cpu_usage = system_metrics.get("cpu_usage", 0)
                memory_usage = system_metrics.get("memory_usage", 0)
                
                thresholds = self.config.get("integration", {}).get("alert_thresholds", {})
                
                if cpu_usage > thresholds.get("cpu_usage", 80):
                    alerts.append({
                        "type": "HIGH_CPU_USAGE",
                        "message": f"CPU usage at {cpu_usage:.1f}%",
                        "severity": "medium"
                    })
                
                if memory_usage > thresholds.get("memory_usage", 85):
                    alerts.append({
                        "type": "HIGH_MEMORY_USAGE", 
                        "message": f"Memory usage at {memory_usage:.1f}%",
                        "severity": "medium"
                    })
            
            # Check orchestrator health
            orchestration_status = self.team_orchestrator.get_orchestration_status()
            if orchestration_status:
                pending_workloads = orchestration_status.get("pending_workloads", 0)
                if pending_workloads > 20:
                    alerts.append({
                        "type": "HIGH_WORKLOAD_QUEUE",
                        "message": f"High workload queue: {pending_workloads} pending",
                        "severity": "medium"
                    })
            
            # Check audit health
            audit_status = self.executable_auditor.get_audit_status()
            if audit_status:
                error_rate = 100 - audit_status.get("audit_statistics", {}).get("success_rate", 100.0)
                if error_rate > 5:
                    alerts.append({
                        "type": "HIGH_AUDIT_ERROR_RATE",
                        "message": f"Audit error rate at {error_rate:.1f}%",
                        "severity": "high"
                    })
            
            # Send alerts
            for alert in alerts:
                self._send_alert(alert)
                self.system_events.append({
                    "timestamp": datetime.now().isoformat(),
                    "event_type": "health_check_alert",
                    "data": alert
                })
                
        except Exception as e:
            logger.error(f"Error performing health checks: {str(e)}")
    
    def _synchronize_component_data(self):
        """Synchronize data between all components"""
        try:
            # Get latest data from all components
            agent_status = self.agent_manager.get_status()
            orchestration_status = self.team_orchestrator.get_orchestration_status()
            audit_status = self.executable_auditor.get_audit_status()
            
            # Update monitoring store with latest data
            if agent_status:
                for agent_id, agent_data in agent_status.get("agents", {}).items():
                    monitoring_store.update_agent_data(agent_id, {
                        "name": agent_data.get("name", agent_id),
                        "status": agent_data.get("status", "unknown"),
                        "metrics": agent_data.get("metrics", {}),
                        "team": agent_data.get("team", "unknown")
                    })
            
            if orchestration_status:
                for team_name, team_data in orchestration_status.get("active_team_details", {}).items():
                    monitoring_store.update_team_data(team_name, team_data)
            
            if audit_status:
                recent_reports = self.executable_auditor.get_recent_reports(10)
                for report in recent_reports:
                    monitoring_store.update_audit_report(
                        report.report_id,
                        asdict(report)
                    )
                
                monitoring_store.update_orchestration_status({
                    "orchestrator_running": orchestration_status.get("orchestrator_running", False),
                    "active_teams": orchestration_status.get("active_teams", 0),
                    "pending_workloads": orchestration_status.get("pending_workloads", 0)
                })
                
        except Exception as e:
            logger.error(f"Error synchronizing component data: {str(e)}")
    
    def _generate_demo_workloads(self):
        """Generate demonstration workloads for testing"""
        try:
            import random
            
            workload_interval = self.config.get("workload_management", {}).get("workload_generation_interval", 60)
            
            # Generate workload every interval
            if random.random() < 0.1:  # 10% chance per cycle
                workload_types = [
                    WorkloadType.RESEARCH_PROJECT,
                    WorkloadType.DEVELOPMENT_SPRINT,
                    WorkloadType.EMERGENCY_RESPONSE
                ]
                
                domains = [
                    SpecializationDomain.AI_MACHINE_LEARNING,
                    SpecializationDomain.WEB_DEVELOPMENT,
                    SpecializationDomain.DATA_SCIENCE
                ]
                
                workload_type = random.choice(workload_types)
                domain = random.choice(domains)
                
                if workload_type == WorkloadType.RESEARCH_PROJECT:
                    self.team_orchestrator.submit_research_workload(
                        f"Research task {int(time.time())}",
                        domain,
                        random.randint(3, 7),
                        random.uniform(4, 16)
                    )
                elif workload_type == WorkloadType.DEVELOPMENT_SPRINT:
                    requirements = ["coding", "testing", "deployment"]
                    self.team_orchestrator.submit_development_workload(
                        f"Development task {int(time.time())}",
                        domain,
                        requirements,
                        random.randint(2, 5),
                        random.uniform(8, 24)
                    )
                elif workload_type == WorkloadType.EMERGENCY_RESPONSE:
                    self.team_orchestrator.submit_emergency_workload(
                        f"Emergency incident {int(time.time())}",
                        "critical_system_failure",
                        1,
                        random.uniform(2, 8)
                    )
                    
        except Exception as e:
            logger.error(f"Error generating demo workloads: {str(e)}")
    
    def _update_monitoring_data(self):
        """Update monitoring store with system data"""
        try:
            # Update system metrics
            monitoring_store.update_system_metrics({
                "cpu_usage": self.agent_manager.system_metrics.cpu_usage,
                "memory_usage": self.agent_manager.system_metrics.memory_usage,
                "total_agents": len(self.agent_manager.agents),
                "active_agents": len([a for a in self.agent_manager.agents.values() if a.status.value == "running"]),
                "active_teams": len(self.team_orchestrator.workload_scheduler.active_teams),
                "pending_workloads": len(self.team_orchestrator.workload_scheduler.pending_workloads),
                "audit_statistics": self.executable_auditor.audit_stats,
                "system_health_score": self.metrics.system_health_score,
                "uptime_hours": self.metrics.uptime_seconds / 3600
            })
            
        except Exception as e:
            logger.error(f"Error updating monitoring data: {str(e)}")
    
    def _send_alert(self, alert: Dict[str, Any]):
        """Send alert to monitoring system"""
        try:
            alert["timestamp"] = datetime.now().isoformat()
            alert["system"] = "enhanced_orchestrator"
            
            monitoring_store.add_alert(alert)
            
            # Log alert
            logger.warning(f"ALERT: {alert['type']} - {alert['message']}")
            
        except Exception as e:
            logger.error(f"Error sending alert: {str(e)}")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        try:
            agent_status = self.agent_manager.get_status()
            orchestration_status = self.team_orchestrator.get_orchestration_status()
            audit_status = self.executable_auditor.get_audit_status()
            
            return {
                "orchestrator_running": self.orchestrator_running,
                "uptime_hours": self.metrics.uptime_seconds / 3600,
                "system_health_score": self.metrics.system_health_score,
                "components": {
                    "agent_manager": {
                        "running": self.agent_manager.monitoring_active,
                        "total_agents": len(self.agent_manager.agents),
                        "active_agents": len([a for a in self.agent_manager.agents.values() 
                                            if a.status.value == "running"])
                    },
                    "team_orchestrator": {
                        "running": orchestration_status.get("orchestrator_running", False),
                        "active_teams": orchestration_status.get("active_teams", 0),
                        "pending_workloads": orchestration_status.get("pending_workloads", 0)
                    },
                    "executable_auditor": {
                        "running": audit_status.get("auditor_running", False),
                        "total_audits": audit_status.get("total_audits", 0),
                        "success_rate": audit_status.get("audit_statistics", {}).get("success_rate", 0)
                    }
                },
                "metrics": {
                    "total_workloads": self.metrics.total_workloads_processed,
                    "workload_success_rate": (
                        self.metrics.successful_workloads / max(1, self.metrics.total_workloads_processed)
                    ) * 100,
                    "avg_completion_time": self.metrics.avg_workload_completion_time,
                    "system_events": len(self.system_events)
                },
                "dashboard_url": f"http://localhost:{self.config.get('orchestration', {}).get('dashboard_port', 5000)}"
            }
            
        except Exception as e:
            logger.error(f"Error getting system status: {str(e)}")
            return {
                "orchestrator_running": self.orchestrator_running,
                "error": str(e)
            }
    
    def submit_workload(self, workload_type: str, description: str, domain: str = "general", 
                       priority: int = 5, estimated_hours: float = 8.0) -> str:
        """Submit a workload to the system"""
        try:
            workload_type_enum = WorkloadType(workload_type)
            domain_enum = SpecializationDomain(domain)
            
            if workload_type_enum == WorkloadType.RESEARCH_PROJECT:
                return self.team_orchestrator.submit_research_workload(
                    description, domain_enum, priority, estimated_hours
                )
            elif workload_type_enum == WorkloadType.DEVELOPMENT_SPRINT:
                return self.team_orchestrator.submit_development_workload(
                    description, domain_enum, ["coding", "testing", "deployment"], 
                    priority, estimated_hours
                )
            elif workload_type == "emergency_response":
                return self.team_orchestrator.submit_emergency_workload(
                    description, "system_emergency", priority, estimated_hours
                )
            else:
                raise ValueError(f"Unknown workload type: {workload_type}")
                
        except Exception as e:
            logger.error(f"Error submitting workload: {str(e)}")
            raise
    
    def perform_system_audit(self, build_id: str = None, platform: str = "auto") -> str:
        """Perform a system audit"""
        try:
            # For demo purposes, create mock audit artifacts
            import tempfile
            import os
            
            # Create temporary build artifacts
            artifacts = []
            
            if platform == "auto" or platform == "windows":
                exe_path = os.path.join(tempfile.gettempdir(), f"{build_id or 'demo'}.exe")
                with open(exe_path, 'w') as f:
                    f.write("Mock Windows executable")
                artifacts.append(exe_path)
            
            if platform == "auto" or platform == "linux":
                deb_path = os.path.join(tempfile.gettempdir(), f"{build_id or 'demo'}.deb")
                with open(deb_path, 'w') as f:
                    f.write("Mock Debian package")
                artifacts.append(deb_path)
            
            # Determine platform enum
            from auditor.executable_auditor import Platform
            platform_enum = Platform(platform) if platform != "auto" else Platform.WINDOWS
            
            # Perform audit
            return self.executable_auditor.audit_build_artifact(
                build_id or f"audit_{int(time.time())}",
                platform_enum,
                artifacts
            )
            
        except Exception as e:
            logger.error(f"Error performing system audit: {str(e)}")
            raise

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Augur Omega Enhanced Orchestration System")
    parser.add_argument("command", choices=["start", "stop", "status", "demo", "workload", "audit"], 
                       help="Command to execute")
    parser.add_argument("--config", default="config/enhanced_orchestrator.cfg", 
                       help="Configuration file path")
    parser.add_argument("--workload-type", choices=["research_project", "development_sprint", "emergency_response"],
                       help="Workload type for 'workload' command")
    parser.add_argument("--description", help="Workload description")
    parser.add_argument("--priority", type=int, default=5, help="Workload priority (1-10)")
    parser.add_argument("--platform", default="auto", help="Platform for 'audit' command")
    
    args = parser.parse_args()
    
    orchestrator = SystemIntegrator(args.config)
    
    try:
        if args.command == "start":
            print("Starting Enhanced Orchestration System...")
            orchestrator.start_orchestration_system()
            print(f"System started successfully!")
            print(f"Monitoring Dashboard: {orchestrator.get_system_status()['dashboard_url']}")
            
            # Keep running
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\\nStopping system...")
                
        elif args.command == "stop":
            print("Stopping Enhanced Orchestration System...")
            orchestrator.stop_orchestration_system()
            print("System stopped successfully!")
            
        elif args.command == "status":
            status = orchestrator.get_system_status()
            print("Enhanced Orchestration System Status:")
            print(f"  Running: {status['orchestrator_running']}")
            print(f"  Uptime: {status['uptime_hours']:.1f} hours")
            print(f"  System Health: {status['system_health_score']:.1f}%")
            
            if 'components' in status:
                print("\\nComponents:")
                for component, info in status['components'].items():
                    print(f"  {component}: {'✓' if info['running'] else '✗'}")
                    if 'total_agents' in info:
                        print(f"    Agents: {info['active_agents']}/{info['total_agents']} active")
                    if 'active_teams' in info:
                        print(f"    Teams: {info['active_teams']} active")
            
            if 'dashboard_url' in status:
                print(f"\\nDashboard: {status['dashboard_url']}")
            
        elif args.command == "demo":
            print("Running Enhanced Orchestration System Demo...")
            orchestrator.start_orchestration_system()
            
            # Generate some demo workloads
            time.sleep(5)
            
            print("\\nGenerating demo workloads...")
            orchestrator.submit_workload(
                "research_project", 
                "AI research for customer sentiment analysis",
                "ai_ml",
                priority=3,
                estimated_hours=12.0
            )
            
            orchestrator.submit_workload(
                "development_sprint",
                "Web application frontend development",
                "web_dev",
                requirements=["frontend", "react", "testing"],
                priority=4,
                estimated_hours=20.0
            )
            
            # Run for demo period
            print("\\nDemo running... (Press Ctrl+C to stop)")
            try:
                time.sleep(30)
            except KeyboardInterrupt:
                pass
                
            orchestrator.stop_orchestration_system()
            print("Demo completed!")
            
        elif args.command == "workload":
            if not args.description:
                print("Error: --description required for workload command")
                return
            
            if not args.workload_type:
                print("Error: --workload-type required for workload command")
                return
            
            print(f"Submitting workload: {args.description}")
            workload_id = orchestrator.submit_workload(
                args.workload_type,
                args.description,
                priority=args.priority
            )
            print(f"Workload submitted: {workload_id}")
            
        elif args.command == "audit":
            print(f"Performing system audit for platform: {args.platform}")
            audit_id = orchestrator.perform_system_audit(platform=args.platform)
            print(f"Audit initiated: {audit_id}")
            
    except KeyboardInterrupt:
        print("\\nStopping system...")
        orchestrator.stop_orchestration_system()
    except Exception as e:
        print(f"Error: {str(e)}")
        if orchestrator.orchestrator_running:
            orchestrator.stop_orchestration_system()

if __name__ == "__main__":
    main()