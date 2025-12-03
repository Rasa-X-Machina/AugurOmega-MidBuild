"""
Main entry point for Triumvirate Integration Layer

This script provides a command-line interface for managing the triumvirate
integration system, including initialization, startup, shutdown, and monitoring.
"""

import asyncio
import argparse
import sys
import signal
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from triumvirate_manager import TriumvirateIntegrationManager, setup_signal_handlers
from configs.config_manager import ConfigManager

async def main():
    """Main entry point for the triumvirate integration system"""
    parser = argparse.ArgumentParser(description="Triumvirate Integration Layer")
    parser.add_argument(
        "--config", 
        default="configs/integration_config.yaml",
        help="Configuration file path (default: configs/integration_config.yaml)"
    )
    parser.add_argument(
        "--action",
        choices=["start", "stop", "restart", "status", "health"],
        default="start",
        help="Action to perform (default: start)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="API server port (default: 8000)"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="API server host (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Run as daemon process"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    parser.add_argument(
        "--log-file",
        default="logs/triumvirate.log",
        help="Log file path (default: logs/triumvirate.log)"
    )
    
    args = parser.parse_args()
    
    # Create necessary directories
    Path("logs").mkdir(exist_ok=True)
    Path("data").mkdir(exist_ok=True)
    
    try:
        # Create and configure the integration manager
        manager = TriumvirateIntegrationManager(args.config)
        
        # Update API configuration if provided
        config_manager = ConfigManager(args.config)
        config = config_manager.load_config()
        config.api_config["host"] = args.host
        config.api_config["port"] = args.port
        config_manager.save_config(config)
        
        # Setup logging
        if args.debug:
            import logging
            logging.basicConfig(
                level=logging.DEBUG,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                handlers=[
                    logging.FileHandler(args.log_file),
                    logging.StreamHandler(sys.stdout)
                ]
            )
        
        # Setup signal handlers for graceful shutdown
        setup_signal_handlers(manager)
        
        # Perform the requested action
        if args.action == "start":
            await start_system(manager, args)
        elif args.action == "stop":
            await stop_system(manager)
        elif args.action == "restart":
            await restart_system(manager, args)
        elif args.action == "status":
            await show_status(manager)
        elif args.action == "health":
            await show_health(manager)
        
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

async def start_system(manager, args):
    """Start the triumvirate integration system"""
    print("🚀 Starting Triumvirate Integration Layer...")
    
    # Initialize the system
    print("📦 Initializing system components...")
    if not await manager.initialize():
        print("❌ Failed to initialize system")
        sys.exit(1)
    
    # Start the system
    print("⚡ Starting all components...")
    if not await manager.start():
        print("❌ Failed to start system")
        sys.exit(1)
    
    # Show system status
    status = manager.get_status()
    print("\n✅ Triumvirtate Integration Layer started successfully!")
    print(f"🌐 API Server: http://{args.host}:{args.port}")
    print(f"📊 System Status: {status['system_status'].title()}")
    
    if not args.daemon:
        print("\n📈 Component Status:")
        for comp_name, comp_info in status["components"].items():
            status_icon = "🟢" if comp_info["running"] else "🔴"
            print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
        
        print(f"\n🔗 API Endpoints:")
        print(f"  • Health: http://{args.host}:{args.port}/api/v1/monitoring/health")
        print(f"  • Metrics: http://{args.host}:{args.port}/api/v1/monitoring/metrics")
        print(f"  • System Overview: http://{args.host}:{args.port}/api/v1/system/overview")
        
        print(f"\n📝 Logs: {args.log_file}")
        print("\nPress Ctrl+C to stop the system")
        
        # Keep running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutdown requested...")
    else:
        print("🔄 Running as daemon...")

async def stop_system(manager):
    """Stop the triumvirate integration system"""
    print("🛑 Stopping Triumvirate Integration Layer...")
    
    if not await manager.stop():
        print("❌ Failed to stop system properly")
        sys.exit(1)
    
    print("✅ System stopped successfully")

async def restart_system(manager, args):
    """Restart the triumvirate integration system"""
    print("🔄 Restarting Triumvirate Integration Layer...")
    
    if not await manager.restart():
        print("❌ Failed to restart system")
        sys.exit(1)
    
    print("✅ System restarted successfully")
    print(f"🌐 Available at: http://{args.host}:{args.port}")

async def show_status(manager):
    """Show system status"""
    status = manager.get_status()
    
    print("📊 Triumvirate Integration Layer Status")
    print("=" * 50)
    print(f"System Status: {status['system_status'].title()}")
    
    if status['startup_time']:
        from datetime import datetime
        startup_time = datetime.fromisoformat(status['startup_time'])
        uptime_seconds = (datetime.now() - startup_time).total_seconds()
        uptime_hours = int(uptime_seconds // 3600)
        uptime_minutes = int((uptime_seconds % 3600) // 60)
        print(f"Uptime: {uptime_hours}h {uptime_minutes}m")
    
    print("\n🔧 Components:")
    for comp_name, comp_info in status["components"].items():
        status_icon = "🟢" if comp_info["running"] else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
    
    print("\n🌐 Shared Infrastructure:")
    for infra_name, infra_status in status["shared_infrastructure"].items():
        status_icon = "🟢" if infra_status else "🔴"
        print(f"  {status_icon} {infra_name.replace('_', ' ').title()}: {'Running' if infra_status else 'Stopped'}")
    
    print("\n🚀 Revolutionary Capabilities:")
    for cap_name, cap_status in status["revolutionary_capabilities"].items():
        status_icon = "🟢" if cap_status else "🔴"
        print(f"  {status_icon} {cap_name.replace('_', ' ').title()}: {'Active' if cap_status else 'Inactive'}")

async def show_health(manager):
    """Show detailed health information"""
    print("🏥 Triumvirate Integration Layer Health Check")
    print("=" * 50)
    
    # Get system overview
    overview = manager.observability.get_system_overview()
    
    print(f"System Health: {overview['system_health']['status'].title()}")
    print(f"Health Score: {overview['system_health']['score']:.1f}%")
    
    print(f"\n📊 Metrics:")
    print(f"  • Total Components: {overview['total_components_tracked']}")
    print(f"  • Active Alerts: {overview['active_alerts']}")
    print(f"  • Critical Alerts: {overview['critical_alerts']}")
    
    print(f"\n🔍 Component Health:")
    for comp_name in ["agenta", "pranava", "antakhara"]:
        health = await getattr(manager, comp_name).get_health_status()
        status_icon = "🟢" if health["status"] == "healthy" else "🟡" if health["status"] == "degraded" else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {health['status']}")
    
    # Check integration health
    integration_status = manager.get_status()
    if integration_status['system_status'] == 'running':
        print(f"\n✅ Integration Status: HEALTHY")
    else:
        print(f"\n❌ Integration Status: UNHEALTHY")

if __name__ == "__main__":
    # Ensure we can handle KeyboardInterrupt properly
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
Triumvirate Integration Manager

Central orchestrator that manages the integration of Agenta, Pranava, and Antakhara
components into a unified platform with seamless communication and revolutionary
capabilities.
"""
Main entry point for Triumvirate Integration Layer

This script provides a command-line interface for managing the triumvirate
integration system, including initialization, startup, shutdown, and monitoring.
"""

import asyncio
import argparse
import sys
import signal
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from triumvirate_manager import TriumvirateIntegrationManager, setup_signal_handlers
from configs.config_manager import ConfigManager

async def main():
    """Main entry point for the triumvirate integration system"""
    parser = argparse.ArgumentParser(description="Triumvirate Integration Layer")
    parser.add_argument(
        "--config", 
        default="configs/integration_config.yaml",
        help="Configuration file path (default: configs/integration_config.yaml)"
    )
    parser.add_argument(
        "--action",
        choices=["start", "stop", "restart", "status", "health"],
        default="start",
        help="Action to perform (default: start)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="API server port (default: 8000)"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="API server host (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Run as daemon process"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    parser.add_argument(
        "--log-file",
        default="logs/triumvirate.log",
        help="Log file path (default: logs/triumvirate.log)"
    )
    
    args = parser.parse_args()
    
    # Create necessary directories
    Path("logs").mkdir(exist_ok=True)
    Path("data").mkdir(exist_ok=True)
    
    try:
        # Create and configure the integration manager
        manager = TriumvirateIntegrationManager(args.config)
        
        # Update API configuration if provided
        config_manager = ConfigManager(args.config)
        config = config_manager.load_config()
        config.api_config["host"] = args.host
        config.api_config["port"] = args.port
        config_manager.save_config(config)
        
        # Setup logging
        if args.debug:
            import logging
            logging.basicConfig(
                level=logging.DEBUG,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                handlers=[
                    logging.FileHandler(args.log_file),
                    logging.StreamHandler(sys.stdout)
                ]
            )
        
        # Setup signal handlers for graceful shutdown
        setup_signal_handlers(manager)
        
        # Perform the requested action
        if args.action == "start":
            await start_system(manager, args)
        elif args.action == "stop":
            await stop_system(manager)
        elif args.action == "restart":
            await restart_system(manager, args)
        elif args.action == "status":
            await show_status(manager)
        elif args.action == "health":
            await show_health(manager)
        
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

async def start_system(manager, args):
    """Start the triumvirate integration system"""
    print("🚀 Starting Triumvirate Integration Layer...")
    
    # Initialize the system
    print("📦 Initializing system components...")
    if not await manager.initialize():
        print("❌ Failed to initialize system")
        sys.exit(1)
    
    # Start the system
    print("⚡ Starting all components...")
    if not await manager.start():
        print("❌ Failed to start system")
        sys.exit(1)
    
    # Show system status
    status = manager.get_status()
    print("\n✅ Triumvirtate Integration Layer started successfully!")
    print(f"🌐 API Server: http://{args.host}:{args.port}")
    print(f"📊 System Status: {status['system_status'].title()}")
    
    if not args.daemon:
        print("\n📈 Component Status:")
        for comp_name, comp_info in status["components"].items():
            status_icon = "🟢" if comp_info["running"] else "🔴"
            print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
        
        print(f"\n🔗 API Endpoints:")
        print(f"  • Health: http://{args.host}:{args.port}/api/v1/monitoring/health")
        print(f"  • Metrics: http://{args.host}:{args.port}/api/v1/monitoring/metrics")
        print(f"  • System Overview: http://{args.host}:{args.port}/api/v1/system/overview")
        
        print(f"\n📝 Logs: {args.log_file}")
        print("\nPress Ctrl+C to stop the system")
        
        # Keep running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutdown requested...")
    else:
        print("🔄 Running as daemon...")

async def stop_system(manager):
    """Stop the triumvirate integration system"""
    print("🛑 Stopping Triumvirate Integration Layer...")
    
    if not await manager.stop():
        print("❌ Failed to stop system properly")
        sys.exit(1)
    
    print("✅ System stopped successfully")

async def restart_system(manager, args):
    """Restart the triumvirate integration system"""
    print("🔄 Restarting Triumvirate Integration Layer...")
    
    if not await manager.restart():
        print("❌ Failed to restart system")
        sys.exit(1)
    
    print("✅ System restarted successfully")
    print(f"🌐 Available at: http://{args.host}:{args.port}")

async def show_status(manager):
    """Show system status"""
    status = manager.get_status()
    
    print("📊 Triumvirate Integration Layer Status")
    print("=" * 50)
    print(f"System Status: {status['system_status'].title()}")
    
    if status['startup_time']:
        from datetime import datetime
        startup_time = datetime.fromisoformat(status['startup_time'])
        uptime_seconds = (datetime.now() - startup_time).total_seconds()
        uptime_hours = int(uptime_seconds // 3600)
        uptime_minutes = int((uptime_seconds % 3600) // 60)
        print(f"Uptime: {uptime_hours}h {uptime_minutes}m")
    
    print("\n🔧 Components:")
    for comp_name, comp_info in status["components"].items():
        status_icon = "🟢" if comp_info["running"] else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
    
    print("\n🌐 Shared Infrastructure:")
    for infra_name, infra_status in status["shared_infrastructure"].items():
        status_icon = "🟢" if infra_status else "🔴"
        print(f"  {status_icon} {infra_name.replace('_', ' ').title()}: {'Running' if infra_status else 'Stopped'}")
    
    print("\n🚀 Revolutionary Capabilities:")
    for cap_name, cap_status in status["revolutionary_capabilities"].items():
        status_icon = "🟢" if cap_status else "🔴"
        print(f"  {status_icon} {cap_name.replace('_', ' ').title()}: {'Active' if cap_status else 'Inactive'}")

async def show_health(manager):
    """Show detailed health information"""
    print("🏥 Triumvirate Integration Layer Health Check")
    print("=" * 50)
    
    # Get system overview
    overview = manager.observability.get_system_overview()
    
    print(f"System Health: {overview['system_health']['status'].title()}")
    print(f"Health Score: {overview['system_health']['score']:.1f}%")
    
    print(f"\n📊 Metrics:")
    print(f"  • Total Components: {overview['total_components_tracked']}")
    print(f"  • Active Alerts: {overview['active_alerts']}")
    print(f"  • Critical Alerts: {overview['critical_alerts']}")
    
    print(f"\n🔍 Component Health:")
    for comp_name in ["agenta", "pranava", "antakhara"]:
        health = await getattr(manager, comp_name).get_health_status()
        status_icon = "🟢" if health["status"] == "healthy" else "🟡" if health["status"] == "degraded" else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {health['status']}")
    
    # Check integration health
    integration_status = manager.get_status()
    if integration_status['system_status'] == 'running':
        print(f"\n✅ Integration Status: HEALTHY")
    else:
        print(f"\n❌ Integration Status: UNHEALTHY")

if __name__ == "__main__":
    # Ensure we can handle KeyboardInterrupt properly
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)

import asyncio
import logging
import signal
import sys
from typing import Dict, List, Any, Optional
from datetime import datetime
import threading

from .shared.base import TriumvirateComponent, ComponentType, TriumvirateMessage
from .shared.messaging import MessageRouter, MessageProtocol
from .shared.discovery import ServiceDiscovery
from .shared.monitoring import ObservabilityManager

from .agenta.manager import AgentaManager
from .pranava.orchestrator import PranavaOrchestrator
from .antakhara.enforcer import AntakharaEnforcer

from .api import TriumvirateAPI
from .configs.config_manager import ConfigManager

class TriumvirateIntegrationManager:
    """
Main entry point for Triumvirate Integration Layer

This script provides a command-line interface for managing the triumvirate
integration system, including initialization, startup, shutdown, and monitoring.
"""

import asyncio
import argparse
import sys
import signal
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from triumvirate_manager import TriumvirateIntegrationManager, setup_signal_handlers
from configs.config_manager import ConfigManager

async def main():
    """Main entry point for the triumvirate integration system"""
    parser = argparse.ArgumentParser(description="Triumvirate Integration Layer")
    parser.add_argument(
        "--config", 
        default="configs/integration_config.yaml",
        help="Configuration file path (default: configs/integration_config.yaml)"
    )
    parser.add_argument(
        "--action",
        choices=["start", "stop", "restart", "status", "health"],
        default="start",
        help="Action to perform (default: start)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="API server port (default: 8000)"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="API server host (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Run as daemon process"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    parser.add_argument(
        "--log-file",
        default="logs/triumvirate.log",
        help="Log file path (default: logs/triumvirate.log)"
    )
    
    args = parser.parse_args()
    
    # Create necessary directories
    Path("logs").mkdir(exist_ok=True)
    Path("data").mkdir(exist_ok=True)
    
    try:
        # Create and configure the integration manager
        manager = TriumvirateIntegrationManager(args.config)
        
        # Update API configuration if provided
        config_manager = ConfigManager(args.config)
        config = config_manager.load_config()
        config.api_config["host"] = args.host
        config.api_config["port"] = args.port
        config_manager.save_config(config)
        
        # Setup logging
        if args.debug:
            import logging
            logging.basicConfig(
                level=logging.DEBUG,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                handlers=[
                    logging.FileHandler(args.log_file),
                    logging.StreamHandler(sys.stdout)
                ]
            )
        
        # Setup signal handlers for graceful shutdown
        setup_signal_handlers(manager)
        
        # Perform the requested action
        if args.action == "start":
            await start_system(manager, args)
        elif args.action == "stop":
            await stop_system(manager)
        elif args.action == "restart":
            await restart_system(manager, args)
        elif args.action == "status":
            await show_status(manager)
        elif args.action == "health":
            await show_health(manager)
        
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

async def start_system(manager, args):
    """Start the triumvirate integration system"""
    print("🚀 Starting Triumvirate Integration Layer...")
    
    # Initialize the system
    print("📦 Initializing system components...")
    if not await manager.initialize():
        print("❌ Failed to initialize system")
        sys.exit(1)
    
    # Start the system
    print("⚡ Starting all components...")
    if not await manager.start():
        print("❌ Failed to start system")
        sys.exit(1)
    
    # Show system status
    status = manager.get_status()
    print("\n✅ Triumvirtate Integration Layer started successfully!")
    print(f"🌐 API Server: http://{args.host}:{args.port}")
    print(f"📊 System Status: {status['system_status'].title()}")
    
    if not args.daemon:
        print("\n📈 Component Status:")
        for comp_name, comp_info in status["components"].items():
            status_icon = "🟢" if comp_info["running"] else "🔴"
            print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
        
        print(f"\n🔗 API Endpoints:")
        print(f"  • Health: http://{args.host}:{args.port}/api/v1/monitoring/health")
        print(f"  • Metrics: http://{args.host}:{args.port}/api/v1/monitoring/metrics")
        print(f"  • System Overview: http://{args.host}:{args.port}/api/v1/system/overview")
        
        print(f"\n📝 Logs: {args.log_file}")
        print("\nPress Ctrl+C to stop the system")
        
        # Keep running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutdown requested...")
    else:
        print("🔄 Running as daemon...")

async def stop_system(manager):
    """Stop the triumvirate integration system"""
    print("🛑 Stopping Triumvirate Integration Layer...")
    
    if not await manager.stop():
        print("❌ Failed to stop system properly")
        sys.exit(1)
    
    print("✅ System stopped successfully")

async def restart_system(manager, args):
    """Restart the triumvirate integration system"""
    print("🔄 Restarting Triumvirate Integration Layer...")
    
    if not await manager.restart():
        print("❌ Failed to restart system")
        sys.exit(1)
    
    print("✅ System restarted successfully")
    print(f"🌐 Available at: http://{args.host}:{args.port}")

async def show_status(manager):
    """Show system status"""
    status = manager.get_status()
    
    print("📊 Triumvirate Integration Layer Status")
    print("=" * 50)
    print(f"System Status: {status['system_status'].title()}")
    
    if status['startup_time']:
        from datetime import datetime
        startup_time = datetime.fromisoformat(status['startup_time'])
        uptime_seconds = (datetime.now() - startup_time).total_seconds()
        uptime_hours = int(uptime_seconds // 3600)
        uptime_minutes = int((uptime_seconds % 3600) // 60)
        print(f"Uptime: {uptime_hours}h {uptime_minutes}m")
    
    print("\n🔧 Components:")
    for comp_name, comp_info in status["components"].items():
        status_icon = "🟢" if comp_info["running"] else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
    
    print("\n🌐 Shared Infrastructure:")
    for infra_name, infra_status in status["shared_infrastructure"].items():
        status_icon = "🟢" if infra_status else "🔴"
        print(f"  {status_icon} {infra_name.replace('_', ' ').title()}: {'Running' if infra_status else 'Stopped'}")
    
    print("\n🚀 Revolutionary Capabilities:")
    for cap_name, cap_status in status["revolutionary_capabilities"].items():
        status_icon = "🟢" if cap_status else "🔴"
        print(f"  {status_icon} {cap_name.replace('_', ' ').title()}: {'Active' if cap_status else 'Inactive'}")

async def show_health(manager):
    """Show detailed health information"""
    print("🏥 Triumvirate Integration Layer Health Check")
    print("=" * 50)
    
    # Get system overview
    overview = manager.observability.get_system_overview()
    
    print(f"System Health: {overview['system_health']['status'].title()}")
    print(f"Health Score: {overview['system_health']['score']:.1f}%")
    
    print(f"\n📊 Metrics:")
    print(f"  • Total Components: {overview['total_components_tracked']}")
    print(f"  • Active Alerts: {overview['active_alerts']}")
    print(f"  • Critical Alerts: {overview['critical_alerts']}")
    
    print(f"\n🔍 Component Health:")
    for comp_name in ["agenta", "pranava", "antakhara"]:
        health = await getattr(manager, comp_name).get_health_status()
        status_icon = "🟢" if health["status"] == "healthy" else "🟡" if health["status"] == "degraded" else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {health['status']}")
    
    # Check integration health
    integration_status = manager.get_status()
    if integration_status['system_status'] == 'running':
        print(f"\n✅ Integration Status: HEALTHY")
    else:
        print(f"\n❌ Integration Status: UNHEALTHY")

if __name__ == "__main__":
    # Ensure we can handle KeyboardInterrupt properly
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
    Central manager for triumvirate ecosystem integration
    
    Orchestrates Agenta (hierarchy), Pranava (orchestration), and Antakhara (security)
    into a unified platform with revolutionary capabilities:
    - Intelligent cross-component routing and optimization
    - Adaptive scaling and load balancing
    - Real-time security monitoring and policy enforcement
    - Unified observability and performance analytics
    - Self-healing and resilience mechanisms
    """
Main entry point for Triumvirate Integration Layer

This script provides a command-line interface for managing the triumvirate
integration system, including initialization, startup, shutdown, and monitoring.
"""

import asyncio
import argparse
import sys
import signal
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from triumvirate_manager import TriumvirateIntegrationManager, setup_signal_handlers
from configs.config_manager import ConfigManager

async def main():
    """Main entry point for the triumvirate integration system"""
    parser = argparse.ArgumentParser(description="Triumvirate Integration Layer")
    parser.add_argument(
        "--config", 
        default="configs/integration_config.yaml",
        help="Configuration file path (default: configs/integration_config.yaml)"
    )
    parser.add_argument(
        "--action",
        choices=["start", "stop", "restart", "status", "health"],
        default="start",
        help="Action to perform (default: start)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="API server port (default: 8000)"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="API server host (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Run as daemon process"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    parser.add_argument(
        "--log-file",
        default="logs/triumvirate.log",
        help="Log file path (default: logs/triumvirate.log)"
    )
    
    args = parser.parse_args()
    
    # Create necessary directories
    Path("logs").mkdir(exist_ok=True)
    Path("data").mkdir(exist_ok=True)
    
    try:
        # Create and configure the integration manager
        manager = TriumvirateIntegrationManager(args.config)
        
        # Update API configuration if provided
        config_manager = ConfigManager(args.config)
        config = config_manager.load_config()
        config.api_config["host"] = args.host
        config.api_config["port"] = args.port
        config_manager.save_config(config)
        
        # Setup logging
        if args.debug:
            import logging
            logging.basicConfig(
                level=logging.DEBUG,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                handlers=[
                    logging.FileHandler(args.log_file),
                    logging.StreamHandler(sys.stdout)
                ]
            )
        
        # Setup signal handlers for graceful shutdown
        setup_signal_handlers(manager)
        
        # Perform the requested action
        if args.action == "start":
            await start_system(manager, args)
        elif args.action == "stop":
            await stop_system(manager)
        elif args.action == "restart":
            await restart_system(manager, args)
        elif args.action == "status":
            await show_status(manager)
        elif args.action == "health":
            await show_health(manager)
        
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

async def start_system(manager, args):
    """Start the triumvirate integration system"""
    print("🚀 Starting Triumvirate Integration Layer...")
    
    # Initialize the system
    print("📦 Initializing system components...")
    if not await manager.initialize():
        print("❌ Failed to initialize system")
        sys.exit(1)
    
    # Start the system
    print("⚡ Starting all components...")
    if not await manager.start():
        print("❌ Failed to start system")
        sys.exit(1)
    
    # Show system status
    status = manager.get_status()
    print("\n✅ Triumvirtate Integration Layer started successfully!")
    print(f"🌐 API Server: http://{args.host}:{args.port}")
    print(f"📊 System Status: {status['system_status'].title()}")
    
    if not args.daemon:
        print("\n📈 Component Status:")
        for comp_name, comp_info in status["components"].items():
            status_icon = "🟢" if comp_info["running"] else "🔴"
            print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
        
        print(f"\n🔗 API Endpoints:")
        print(f"  • Health: http://{args.host}:{args.port}/api/v1/monitoring/health")
        print(f"  • Metrics: http://{args.host}:{args.port}/api/v1/monitoring/metrics")
        print(f"  • System Overview: http://{args.host}:{args.port}/api/v1/system/overview")
        
        print(f"\n📝 Logs: {args.log_file}")
        print("\nPress Ctrl+C to stop the system")
        
        # Keep running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutdown requested...")
    else:
        print("🔄 Running as daemon...")

async def stop_system(manager):
    """Stop the triumvirate integration system"""
    print("🛑 Stopping Triumvirate Integration Layer...")
    
    if not await manager.stop():
        print("❌ Failed to stop system properly")
        sys.exit(1)
    
    print("✅ System stopped successfully")

async def restart_system(manager, args):
    """Restart the triumvirate integration system"""
    print("🔄 Restarting Triumvirate Integration Layer...")
    
    if not await manager.restart():
        print("❌ Failed to restart system")
        sys.exit(1)
    
    print("✅ System restarted successfully")
    print(f"🌐 Available at: http://{args.host}:{args.port}")

async def show_status(manager):
    """Show system status"""
    status = manager.get_status()
    
    print("📊 Triumvirate Integration Layer Status")
    print("=" * 50)
    print(f"System Status: {status['system_status'].title()}")
    
    if status['startup_time']:
        from datetime import datetime
        startup_time = datetime.fromisoformat(status['startup_time'])
        uptime_seconds = (datetime.now() - startup_time).total_seconds()
        uptime_hours = int(uptime_seconds // 3600)
        uptime_minutes = int((uptime_seconds % 3600) // 60)
        print(f"Uptime: {uptime_hours}h {uptime_minutes}m")
    
    print("\n🔧 Components:")
    for comp_name, comp_info in status["components"].items():
        status_icon = "🟢" if comp_info["running"] else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
    
    print("\n🌐 Shared Infrastructure:")
    for infra_name, infra_status in status["shared_infrastructure"].items():
        status_icon = "🟢" if infra_status else "🔴"
        print(f"  {status_icon} {infra_name.replace('_', ' ').title()}: {'Running' if infra_status else 'Stopped'}")
    
    print("\n🚀 Revolutionary Capabilities:")
    for cap_name, cap_status in status["revolutionary_capabilities"].items():
        status_icon = "🟢" if cap_status else "🔴"
        print(f"  {status_icon} {cap_name.replace('_', ' ').title()}: {'Active' if cap_status else 'Inactive'}")

async def show_health(manager):
    """Show detailed health information"""
    print("🏥 Triumvirate Integration Layer Health Check")
    print("=" * 50)
    
    # Get system overview
    overview = manager.observability.get_system_overview()
    
    print(f"System Health: {overview['system_health']['status'].title()}")
    print(f"Health Score: {overview['system_health']['score']:.1f}%")
    
    print(f"\n📊 Metrics:")
    print(f"  • Total Components: {overview['total_components_tracked']}")
    print(f"  • Active Alerts: {overview['active_alerts']}")
    print(f"  • Critical Alerts: {overview['critical_alerts']}")
    
    print(f"\n🔍 Component Health:")
    for comp_name in ["agenta", "pranava", "antakhara"]:
        health = await getattr(manager, comp_name).get_health_status()
        status_icon = "🟢" if health["status"] == "healthy" else "🟡" if health["status"] == "degraded" else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {health['status']}")
    
    # Check integration health
    integration_status = manager.get_status()
    if integration_status['system_status'] == 'running':
        print(f"\n✅ Integration Status: HEALTHY")
    else:
        print(f"\n❌ Integration Status: UNHEALTHY")

if __name__ == "__main__":
    # Ensure we can handle KeyboardInterrupt properly
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
    
    def __init__(self, config_path: str = None):
        # Configuration
        self.config_manager = ConfigManager(config_path)
        self.config = self.config_manager.load_config()
        
        # Core components
        self.agenta: Optional[AgentaManager] = None
        self.pranava: Optional[PranavaOrchestrator] = None
        self.antakhara: Optional[AntakharaEnforcer] = None
        
        # Shared infrastructure
        self.message_router: Optional[MessageRouter] = None
        self.service_discovery: Optional[ServiceDiscovery] = None
        self.observability: Optional[ObservabilityManager] = None
        self.api_server: Optional[TriumvirateAPI] = None
        
        # Integration state
        self.is_running = False
        self.startup_time = None
        self.component_health: Dict[str, Dict[str, Any]] = {}
        
        # Revolutionary capabilities
        self.intelligent_coordinator = None
        self.adaptive_optimizer = None
        self.self_healer = None
        self.performance_optimizer = None
        
        # Logging
        self.logger = logging.getLogger("TriumvirateManager")
        
    async def initialize(self) -> bool:
        """
Main entry point for Triumvirate Integration Layer

This script provides a command-line interface for managing the triumvirate
integration system, including initialization, startup, shutdown, and monitoring.
"""

import asyncio
import argparse
import sys
import signal
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from triumvirate_manager import TriumvirateIntegrationManager, setup_signal_handlers
from configs.config_manager import ConfigManager

async def main():
    """Main entry point for the triumvirate integration system"""
    parser = argparse.ArgumentParser(description="Triumvirate Integration Layer")
    parser.add_argument(
        "--config", 
        default="configs/integration_config.yaml",
        help="Configuration file path (default: configs/integration_config.yaml)"
    )
    parser.add_argument(
        "--action",
        choices=["start", "stop", "restart", "status", "health"],
        default="start",
        help="Action to perform (default: start)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="API server port (default: 8000)"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="API server host (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Run as daemon process"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    parser.add_argument(
        "--log-file",
        default="logs/triumvirate.log",
        help="Log file path (default: logs/triumvirate.log)"
    )
    
    args = parser.parse_args()
    
    # Create necessary directories
    Path("logs").mkdir(exist_ok=True)
    Path("data").mkdir(exist_ok=True)
    
    try:
        # Create and configure the integration manager
        manager = TriumvirateIntegrationManager(args.config)
        
        # Update API configuration if provided
        config_manager = ConfigManager(args.config)
        config = config_manager.load_config()
        config.api_config["host"] = args.host
        config.api_config["port"] = args.port
        config_manager.save_config(config)
        
        # Setup logging
        if args.debug:
            import logging
            logging.basicConfig(
                level=logging.DEBUG,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                handlers=[
                    logging.FileHandler(args.log_file),
                    logging.StreamHandler(sys.stdout)
                ]
            )
        
        # Setup signal handlers for graceful shutdown
        setup_signal_handlers(manager)
        
        # Perform the requested action
        if args.action == "start":
            await start_system(manager, args)
        elif args.action == "stop":
            await stop_system(manager)
        elif args.action == "restart":
            await restart_system(manager, args)
        elif args.action == "status":
            await show_status(manager)
        elif args.action == "health":
            await show_health(manager)
        
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

async def start_system(manager, args):
    """Start the triumvirate integration system"""
    print("🚀 Starting Triumvirate Integration Layer...")
    
    # Initialize the system
    print("📦 Initializing system components...")
    if not await manager.initialize():
        print("❌ Failed to initialize system")
        sys.exit(1)
    
    # Start the system
    print("⚡ Starting all components...")
    if not await manager.start():
        print("❌ Failed to start system")
        sys.exit(1)
    
    # Show system status
    status = manager.get_status()
    print("\n✅ Triumvirtate Integration Layer started successfully!")
    print(f"🌐 API Server: http://{args.host}:{args.port}")
    print(f"📊 System Status: {status['system_status'].title()}")
    
    if not args.daemon:
        print("\n📈 Component Status:")
        for comp_name, comp_info in status["components"].items():
            status_icon = "🟢" if comp_info["running"] else "🔴"
            print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
        
        print(f"\n🔗 API Endpoints:")
        print(f"  • Health: http://{args.host}:{args.port}/api/v1/monitoring/health")
        print(f"  • Metrics: http://{args.host}:{args.port}/api/v1/monitoring/metrics")
        print(f"  • System Overview: http://{args.host}:{args.port}/api/v1/system/overview")
        
        print(f"\n📝 Logs: {args.log_file}")
        print("\nPress Ctrl+C to stop the system")
        
        # Keep running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutdown requested...")
    else:
        print("🔄 Running as daemon...")

async def stop_system(manager):
    """Stop the triumvirate integration system"""
    print("🛑 Stopping Triumvirate Integration Layer...")
    
    if not await manager.stop():
        print("❌ Failed to stop system properly")
        sys.exit(1)
    
    print("✅ System stopped successfully")

async def restart_system(manager, args):
    """Restart the triumvirate integration system"""
    print("🔄 Restarting Triumvirate Integration Layer...")
    
    if not await manager.restart():
        print("❌ Failed to restart system")
        sys.exit(1)
    
    print("✅ System restarted successfully")
    print(f"🌐 Available at: http://{args.host}:{args.port}")

async def show_status(manager):
    """Show system status"""
    status = manager.get_status()
    
    print("📊 Triumvirate Integration Layer Status")
    print("=" * 50)
    print(f"System Status: {status['system_status'].title()}")
    
    if status['startup_time']:
        from datetime import datetime
        startup_time = datetime.fromisoformat(status['startup_time'])
        uptime_seconds = (datetime.now() - startup_time).total_seconds()
        uptime_hours = int(uptime_seconds // 3600)
        uptime_minutes = int((uptime_seconds % 3600) // 60)
        print(f"Uptime: {uptime_hours}h {uptime_minutes}m")
    
    print("\n🔧 Components:")
    for comp_name, comp_info in status["components"].items():
        status_icon = "🟢" if comp_info["running"] else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
    
    print("\n🌐 Shared Infrastructure:")
    for infra_name, infra_status in status["shared_infrastructure"].items():
        status_icon = "🟢" if infra_status else "🔴"
        print(f"  {status_icon} {infra_name.replace('_', ' ').title()}: {'Running' if infra_status else 'Stopped'}")
    
    print("\n🚀 Revolutionary Capabilities:")
    for cap_name, cap_status in status["revolutionary_capabilities"].items():
        status_icon = "🟢" if cap_status else "🔴"
        print(f"  {status_icon} {cap_name.replace('_', ' ').title()}: {'Active' if cap_status else 'Inactive'}")

async def show_health(manager):
    """Show detailed health information"""
    print("🏥 Triumvirate Integration Layer Health Check")
    print("=" * 50)
    
    # Get system overview
    overview = manager.observability.get_system_overview()
    
    print(f"System Health: {overview['system_health']['status'].title()}")
    print(f"Health Score: {overview['system_health']['score']:.1f}%")
    
    print(f"\n📊 Metrics:")
    print(f"  • Total Components: {overview['total_components_tracked']}")
    print(f"  • Active Alerts: {overview['active_alerts']}")
    print(f"  • Critical Alerts: {overview['critical_alerts']}")
    
    print(f"\n🔍 Component Health:")
    for comp_name in ["agenta", "pranava", "antakhara"]:
        health = await getattr(manager, comp_name).get_health_status()
        status_icon = "🟢" if health["status"] == "healthy" else "🟡" if health["status"] == "degraded" else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {health['status']}")
    
    # Check integration health
    integration_status = manager.get_status()
    if integration_status['system_status'] == 'running':
        print(f"\n✅ Integration Status: HEALTHY")
    else:
        print(f"\n❌ Integration Status: UNHEALTHY")

if __name__ == "__main__":
    # Ensure we can handle KeyboardInterrupt properly
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)Initialize the triumvirate integration system"""
Main entry point for Triumvirate Integration Layer

This script provides a command-line interface for managing the triumvirate
integration system, including initialization, startup, shutdown, and monitoring.
"""

import asyncio
import argparse
import sys
import signal
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from triumvirate_manager import TriumvirateIntegrationManager, setup_signal_handlers
from configs.config_manager import ConfigManager

async def main():
    """Main entry point for the triumvirate integration system"""
    parser = argparse.ArgumentParser(description="Triumvirate Integration Layer")
    parser.add_argument(
        "--config", 
        default="configs/integration_config.yaml",
        help="Configuration file path (default: configs/integration_config.yaml)"
    )
    parser.add_argument(
        "--action",
        choices=["start", "stop", "restart", "status", "health"],
        default="start",
        help="Action to perform (default: start)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="API server port (default: 8000)"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="API server host (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Run as daemon process"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    parser.add_argument(
        "--log-file",
        default="logs/triumvirate.log",
        help="Log file path (default: logs/triumvirate.log)"
    )
    
    args = parser.parse_args()
    
    # Create necessary directories
    Path("logs").mkdir(exist_ok=True)
    Path("data").mkdir(exist_ok=True)
    
    try:
        # Create and configure the integration manager
        manager = TriumvirateIntegrationManager(args.config)
        
        # Update API configuration if provided
        config_manager = ConfigManager(args.config)
        config = config_manager.load_config()
        config.api_config["host"] = args.host
        config.api_config["port"] = args.port
        config_manager.save_config(config)
        
        # Setup logging
        if args.debug:
            import logging
            logging.basicConfig(
                level=logging.DEBUG,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                handlers=[
                    logging.FileHandler(args.log_file),
                    logging.StreamHandler(sys.stdout)
                ]
            )
        
        # Setup signal handlers for graceful shutdown
        setup_signal_handlers(manager)
        
        # Perform the requested action
        if args.action == "start":
            await start_system(manager, args)
        elif args.action == "stop":
            await stop_system(manager)
        elif args.action == "restart":
            await restart_system(manager, args)
        elif args.action == "status":
            await show_status(manager)
        elif args.action == "health":
            await show_health(manager)
        
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

async def start_system(manager, args):
    """Start the triumvirate integration system"""
    print("🚀 Starting Triumvirate Integration Layer...")
    
    # Initialize the system
    print("📦 Initializing system components...")
    if not await manager.initialize():
        print("❌ Failed to initialize system")
        sys.exit(1)
    
    # Start the system
    print("⚡ Starting all components...")
    if not await manager.start():
        print("❌ Failed to start system")
        sys.exit(1)
    
    # Show system status
    status = manager.get_status()
    print("\n✅ Triumvirtate Integration Layer started successfully!")
    print(f"🌐 API Server: http://{args.host}:{args.port}")
    print(f"📊 System Status: {status['system_status'].title()}")
    
    if not args.daemon:
        print("\n📈 Component Status:")
        for comp_name, comp_info in status["components"].items():
            status_icon = "🟢" if comp_info["running"] else "🔴"
            print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
        
        print(f"\n🔗 API Endpoints:")
        print(f"  • Health: http://{args.host}:{args.port}/api/v1/monitoring/health")
        print(f"  • Metrics: http://{args.host}:{args.port}/api/v1/monitoring/metrics")
        print(f"  • System Overview: http://{args.host}:{args.port}/api/v1/system/overview")
        
        print(f"\n📝 Logs: {args.log_file}")
        print("\nPress Ctrl+C to stop the system")
        
        # Keep running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutdown requested...")
    else:
        print("🔄 Running as daemon...")

async def stop_system(manager):
    """Stop the triumvirate integration system"""
    print("🛑 Stopping Triumvirate Integration Layer...")
    
    if not await manager.stop():
        print("❌ Failed to stop system properly")
        sys.exit(1)
    
    print("✅ System stopped successfully")

async def restart_system(manager, args):
    """Restart the triumvirate integration system"""
    print("🔄 Restarting Triumvirate Integration Layer...")
    
    if not await manager.restart():
        print("❌ Failed to restart system")
        sys.exit(1)
    
    print("✅ System restarted successfully")
    print(f"🌐 Available at: http://{args.host}:{args.port}")

async def show_status(manager):
    """Show system status"""
    status = manager.get_status()
    
    print("📊 Triumvirate Integration Layer Status")
    print("=" * 50)
    print(f"System Status: {status['system_status'].title()}")
    
    if status['startup_time']:
        from datetime import datetime
        startup_time = datetime.fromisoformat(status['startup_time'])
        uptime_seconds = (datetime.now() - startup_time).total_seconds()
        uptime_hours = int(uptime_seconds // 3600)
        uptime_minutes = int((uptime_seconds % 3600) // 60)
        print(f"Uptime: {uptime_hours}h {uptime_minutes}m")
    
    print("\n🔧 Components:")
    for comp_name, comp_info in status["components"].items():
        status_icon = "🟢" if comp_info["running"] else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
    
    print("\n🌐 Shared Infrastructure:")
    for infra_name, infra_status in status["shared_infrastructure"].items():
        status_icon = "🟢" if infra_status else "🔴"
        print(f"  {status_icon} {infra_name.replace('_', ' ').title()}: {'Running' if infra_status else 'Stopped'}")
    
    print("\n🚀 Revolutionary Capabilities:")
    for cap_name, cap_status in status["revolutionary_capabilities"].items():
        status_icon = "🟢" if cap_status else "🔴"
        print(f"  {status_icon} {cap_name.replace('_', ' ').title()}: {'Active' if cap_status else 'Inactive'}")

async def show_health(manager):
    """Show detailed health information"""
    print("🏥 Triumvirate Integration Layer Health Check")
    print("=" * 50)
    
    # Get system overview
    overview = manager.observability.get_system_overview()
    
    print(f"System Health: {overview['system_health']['status'].title()}")
    print(f"Health Score: {overview['system_health']['score']:.1f}%")
    
    print(f"\n📊 Metrics:")
    print(f"  • Total Components: {overview['total_components_tracked']}")
    print(f"  • Active Alerts: {overview['active_alerts']}")
    print(f"  • Critical Alerts: {overview['critical_alerts']}")
    
    print(f"\n🔍 Component Health:")
    for comp_name in ["agenta", "pranava", "antakhara"]:
        health = await getattr(manager, comp_name).get_health_status()
        status_icon = "🟢" if health["status"] == "healthy" else "🟡" if health["status"] == "degraded" else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {health['status']}")
    
    # Check integration health
    integration_status = manager.get_status()
    if integration_status['system_status'] == 'running':
        print(f"\n✅ Integration Status: HEALTHY")
    else:
        print(f"\n❌ Integration Status: UNHEALTHY")

if __name__ == "__main__":
    # Ensure we can handle KeyboardInterrupt properly
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
        try:
            self.logger.info("Initializing Triumvirate Integration Manager")
            
            # Setup logging
            self._setup_logging()
            
            # Initialize shared infrastructure
            await self._initialize_shared_infrastructure()
            
            # Initialize core triumvirate components
            await self._initialize_triumvirate_components()
            
            # Initialize revolutionary capabilities
            await self._initialize_revolutionary_capabilities()
            
            # Setup inter-component communication
            await self._setup_inter_component_communication()
            
            # Initialize API layer
            await self._initialize_api_layer()
            
            # Setup monitoring and health checks
            await self._setup_health_monitoring()
            
            # Register services
            await self._register_services()
            
            self.logger.info("Triumvirate Integration Manager initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Triumvirate Integration Manager: {e}")
            return False
            
    async def start(self) -> bool:
        """
Main entry point for Triumvirate Integration Layer

This script provides a command-line interface for managing the triumvirate
integration system, including initialization, startup, shutdown, and monitoring.
"""

import asyncio
import argparse
import sys
import signal
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from triumvirate_manager import TriumvirateIntegrationManager, setup_signal_handlers
from configs.config_manager import ConfigManager

async def main():
    """Main entry point for the triumvirate integration system"""
    parser = argparse.ArgumentParser(description="Triumvirate Integration Layer")
    parser.add_argument(
        "--config", 
        default="configs/integration_config.yaml",
        help="Configuration file path (default: configs/integration_config.yaml)"
    )
    parser.add_argument(
        "--action",
        choices=["start", "stop", "restart", "status", "health"],
        default="start",
        help="Action to perform (default: start)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="API server port (default: 8000)"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="API server host (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Run as daemon process"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    parser.add_argument(
        "--log-file",
        default="logs/triumvirate.log",
        help="Log file path (default: logs/triumvirate.log)"
    )
    
    args = parser.parse_args()
    
    # Create necessary directories
    Path("logs").mkdir(exist_ok=True)
    Path("data").mkdir(exist_ok=True)
    
    try:
        # Create and configure the integration manager
        manager = TriumvirateIntegrationManager(args.config)
        
        # Update API configuration if provided
        config_manager = ConfigManager(args.config)
        config = config_manager.load_config()
        config.api_config["host"] = args.host
        config.api_config["port"] = args.port
        config_manager.save_config(config)
        
        # Setup logging
        if args.debug:
            import logging
            logging.basicConfig(
                level=logging.DEBUG,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                handlers=[
                    logging.FileHandler(args.log_file),
                    logging.StreamHandler(sys.stdout)
                ]
            )
        
        # Setup signal handlers for graceful shutdown
        setup_signal_handlers(manager)
        
        # Perform the requested action
        if args.action == "start":
            await start_system(manager, args)
        elif args.action == "stop":
            await stop_system(manager)
        elif args.action == "restart":
            await restart_system(manager, args)
        elif args.action == "status":
            await show_status(manager)
        elif args.action == "health":
            await show_health(manager)
        
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

async def start_system(manager, args):
    """Start the triumvirate integration system"""
    print("🚀 Starting Triumvirate Integration Layer...")
    
    # Initialize the system
    print("📦 Initializing system components...")
    if not await manager.initialize():
        print("❌ Failed to initialize system")
        sys.exit(1)
    
    # Start the system
    print("⚡ Starting all components...")
    if not await manager.start():
        print("❌ Failed to start system")
        sys.exit(1)
    
    # Show system status
    status = manager.get_status()
    print("\n✅ Triumvirtate Integration Layer started successfully!")
    print(f"🌐 API Server: http://{args.host}:{args.port}")
    print(f"📊 System Status: {status['system_status'].title()}")
    
    if not args.daemon:
        print("\n📈 Component Status:")
        for comp_name, comp_info in status["components"].items():
            status_icon = "🟢" if comp_info["running"] else "🔴"
            print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
        
        print(f"\n🔗 API Endpoints:")
        print(f"  • Health: http://{args.host}:{args.port}/api/v1/monitoring/health")
        print(f"  • Metrics: http://{args.host}:{args.port}/api/v1/monitoring/metrics")
        print(f"  • System Overview: http://{args.host}:{args.port}/api/v1/system/overview")
        
        print(f"\n📝 Logs: {args.log_file}")
        print("\nPress Ctrl+C to stop the system")
        
        # Keep running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutdown requested...")
    else:
        print("🔄 Running as daemon...")

async def stop_system(manager):
    """Stop the triumvirate integration system"""
    print("🛑 Stopping Triumvirate Integration Layer...")
    
    if not await manager.stop():
        print("❌ Failed to stop system properly")
        sys.exit(1)
    
    print("✅ System stopped successfully")

async def restart_system(manager, args):
    """Restart the triumvirate integration system"""
    print("🔄 Restarting Triumvirate Integration Layer...")
    
    if not await manager.restart():
        print("❌ Failed to restart system")
        sys.exit(1)
    
    print("✅ System restarted successfully")
    print(f"🌐 Available at: http://{args.host}:{args.port}")

async def show_status(manager):
    """Show system status"""
    status = manager.get_status()
    
    print("📊 Triumvirate Integration Layer Status")
    print("=" * 50)
    print(f"System Status: {status['system_status'].title()}")
    
    if status['startup_time']:
        from datetime import datetime
        startup_time = datetime.fromisoformat(status['startup_time'])
        uptime_seconds = (datetime.now() - startup_time).total_seconds()
        uptime_hours = int(uptime_seconds // 3600)
        uptime_minutes = int((uptime_seconds % 3600) // 60)
        print(f"Uptime: {uptime_hours}h {uptime_minutes}m")
    
    print("\n🔧 Components:")
    for comp_name, comp_info in status["components"].items():
        status_icon = "🟢" if comp_info["running"] else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
    
    print("\n🌐 Shared Infrastructure:")
    for infra_name, infra_status in status["shared_infrastructure"].items():
        status_icon = "🟢" if infra_status else "🔴"
        print(f"  {status_icon} {infra_name.replace('_', ' ').title()}: {'Running' if infra_status else 'Stopped'}")
    
    print("\n🚀 Revolutionary Capabilities:")
    for cap_name, cap_status in status["revolutionary_capabilities"].items():
        status_icon = "🟢" if cap_status else "🔴"
        print(f"  {status_icon} {cap_name.replace('_', ' ').title()}: {'Active' if cap_status else 'Inactive'}")

async def show_health(manager):
    """Show detailed health information"""
    print("🏥 Triumvirate Integration Layer Health Check")
    print("=" * 50)
    
    # Get system overview
    overview = manager.observability.get_system_overview()
    
    print(f"System Health: {overview['system_health']['status'].title()}")
    print(f"Health Score: {overview['system_health']['score']:.1f}%")
    
    print(f"\n📊 Metrics:")
    print(f"  • Total Components: {overview['total_components_tracked']}")
    print(f"  • Active Alerts: {overview['active_alerts']}")
    print(f"  • Critical Alerts: {overview['critical_alerts']}")
    
    print(f"\n🔍 Component Health:")
    for comp_name in ["agenta", "pranava", "antakhara"]:
        health = await getattr(manager, comp_name).get_health_status()
        status_icon = "🟢" if health["status"] == "healthy" else "🟡" if health["status"] == "degraded" else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {health['status']}")
    
    # Check integration health
    integration_status = manager.get_status()
    if integration_status['system_status'] == 'running':
        print(f"\n✅ Integration Status: HEALTHY")
    else:
        print(f"\n❌ Integration Status: UNHEALTHY")

if __name__ == "__main__":
    # Ensure we can handle KeyboardInterrupt properly
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)Start the triumvirate integration system"""
Main entry point for Triumvirate Integration Layer

This script provides a command-line interface for managing the triumvirate
integration system, including initialization, startup, shutdown, and monitoring.
"""

import asyncio
import argparse
import sys
import signal
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from triumvirate_manager import TriumvirateIntegrationManager, setup_signal_handlers
from configs.config_manager import ConfigManager

async def main():
    """Main entry point for the triumvirate integration system"""
    parser = argparse.ArgumentParser(description="Triumvirate Integration Layer")
    parser.add_argument(
        "--config", 
        default="configs/integration_config.yaml",
        help="Configuration file path (default: configs/integration_config.yaml)"
    )
    parser.add_argument(
        "--action",
        choices=["start", "stop", "restart", "status", "health"],
        default="start",
        help="Action to perform (default: start)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="API server port (default: 8000)"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="API server host (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Run as daemon process"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    parser.add_argument(
        "--log-file",
        default="logs/triumvirate.log",
        help="Log file path (default: logs/triumvirate.log)"
    )
    
    args = parser.parse_args()
    
    # Create necessary directories
    Path("logs").mkdir(exist_ok=True)
    Path("data").mkdir(exist_ok=True)
    
    try:
        # Create and configure the integration manager
        manager = TriumvirateIntegrationManager(args.config)
        
        # Update API configuration if provided
        config_manager = ConfigManager(args.config)
        config = config_manager.load_config()
        config.api_config["host"] = args.host
        config.api_config["port"] = args.port
        config_manager.save_config(config)
        
        # Setup logging
        if args.debug:
            import logging
            logging.basicConfig(
                level=logging.DEBUG,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                handlers=[
                    logging.FileHandler(args.log_file),
                    logging.StreamHandler(sys.stdout)
                ]
            )
        
        # Setup signal handlers for graceful shutdown
        setup_signal_handlers(manager)
        
        # Perform the requested action
        if args.action == "start":
            await start_system(manager, args)
        elif args.action == "stop":
            await stop_system(manager)
        elif args.action == "restart":
            await restart_system(manager, args)
        elif args.action == "status":
            await show_status(manager)
        elif args.action == "health":
            await show_health(manager)
        
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

async def start_system(manager, args):
    """Start the triumvirate integration system"""
    print("🚀 Starting Triumvirate Integration Layer...")
    
    # Initialize the system
    print("📦 Initializing system components...")
    if not await manager.initialize():
        print("❌ Failed to initialize system")
        sys.exit(1)
    
    # Start the system
    print("⚡ Starting all components...")
    if not await manager.start():
        print("❌ Failed to start system")
        sys.exit(1)
    
    # Show system status
    status = manager.get_status()
    print("\n✅ Triumvirtate Integration Layer started successfully!")
    print(f"🌐 API Server: http://{args.host}:{args.port}")
    print(f"📊 System Status: {status['system_status'].title()}")
    
    if not args.daemon:
        print("\n📈 Component Status:")
        for comp_name, comp_info in status["components"].items():
            status_icon = "🟢" if comp_info["running"] else "🔴"
            print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
        
        print(f"\n🔗 API Endpoints:")
        print(f"  • Health: http://{args.host}:{args.port}/api/v1/monitoring/health")
        print(f"  • Metrics: http://{args.host}:{args.port}/api/v1/monitoring/metrics")
        print(f"  • System Overview: http://{args.host}:{args.port}/api/v1/system/overview")
        
        print(f"\n📝 Logs: {args.log_file}")
        print("\nPress Ctrl+C to stop the system")
        
        # Keep running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutdown requested...")
    else:
        print("🔄 Running as daemon...")

async def stop_system(manager):
    """Stop the triumvirate integration system"""
    print("🛑 Stopping Triumvirate Integration Layer...")
    
    if not await manager.stop():
        print("❌ Failed to stop system properly")
        sys.exit(1)
    
    print("✅ System stopped successfully")

async def restart_system(manager, args):
    """Restart the triumvirate integration system"""
    print("🔄 Restarting Triumvirate Integration Layer...")
    
    if not await manager.restart():
        print("❌ Failed to restart system")
        sys.exit(1)
    
    print("✅ System restarted successfully")
    print(f"🌐 Available at: http://{args.host}:{args.port}")

async def show_status(manager):
    """Show system status"""
    status = manager.get_status()
    
    print("📊 Triumvirate Integration Layer Status")
    print("=" * 50)
    print(f"System Status: {status['system_status'].title()}")
    
    if status['startup_time']:
        from datetime import datetime
        startup_time = datetime.fromisoformat(status['startup_time'])
        uptime_seconds = (datetime.now() - startup_time).total_seconds()
        uptime_hours = int(uptime_seconds // 3600)
        uptime_minutes = int((uptime_seconds % 3600) // 60)
        print(f"Uptime: {uptime_hours}h {uptime_minutes}m")
    
    print("\n🔧 Components:")
    for comp_name, comp_info in status["components"].items():
        status_icon = "🟢" if comp_info["running"] else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
    
    print("\n🌐 Shared Infrastructure:")
    for infra_name, infra_status in status["shared_infrastructure"].items():
        status_icon = "🟢" if infra_status else "🔴"
        print(f"  {status_icon} {infra_name.replace('_', ' ').title()}: {'Running' if infra_status else 'Stopped'}")
    
    print("\n🚀 Revolutionary Capabilities:")
    for cap_name, cap_status in status["revolutionary_capabilities"].items():
        status_icon = "🟢" if cap_status else "🔴"
        print(f"  {status_icon} {cap_name.replace('_', ' ').title()}: {'Active' if cap_status else 'Inactive'}")

async def show_health(manager):
    """Show detailed health information"""
    print("🏥 Triumvirate Integration Layer Health Check")
    print("=" * 50)
    
    # Get system overview
    overview = manager.observability.get_system_overview()
    
    print(f"System Health: {overview['system_health']['status'].title()}")
    print(f"Health Score: {overview['system_health']['score']:.1f}%")
    
    print(f"\n📊 Metrics:")
    print(f"  • Total Components: {overview['total_components_tracked']}")
    print(f"  • Active Alerts: {overview['active_alerts']}")
    print(f"  • Critical Alerts: {overview['critical_alerts']}")
    
    print(f"\n🔍 Component Health:")
    for comp_name in ["agenta", "pranava", "antakhara"]:
        health = await getattr(manager, comp_name).get_health_status()
        status_icon = "🟢" if health["status"] == "healthy" else "🟡" if health["status"] == "degraded" else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {health['status']}")
    
    # Check integration health
    integration_status = manager.get_status()
    if integration_status['system_status'] == 'running':
        print(f"\n✅ Integration Status: HEALTHY")
    else:
        print(f"\n❌ Integration Status: UNHEALTHY")

if __name__ == "__main__":
    # Ensure we can handle KeyboardInterrupt properly
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
        try:
            if self.is_running:
                self.logger.warning("System already running")
                return True
                
            self.logger.info("Starting Triumvirate Integration System")
            
            # Start all components
            await self.agenta.start()
            await self.pranava.start()
            await self.antakhara.start()
            
            # Start shared infrastructure
            await self.message_router.start()
            await self.service_discovery.start_health_monitoring()
            await self.observability.start()
            
            # Start revolutionary capabilities
            if self.intelligent_coordinator:
                await self.intelligent_coordinator.start()
            if self.adaptive_optimizer:
                await self.adaptive_optimizer.start()
            if self.self_healer:
                await self.self_healer.start()
            if self.performance_optimizer:
                await self.performance_optimizer.start()
            
            self.is_running = True
            self.startup_time = datetime.now()
            
            self.logger.info("Triumvirate Integration System started successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start Triumvirate Integration System: {e}")
            await self._emergency_shutdown()
            return False
            
    async def stop(self) -> bool:
        """
Main entry point for Triumvirate Integration Layer

This script provides a command-line interface for managing the triumvirate
integration system, including initialization, startup, shutdown, and monitoring.
"""

import asyncio
import argparse
import sys
import signal
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from triumvirate_manager import TriumvirateIntegrationManager, setup_signal_handlers
from configs.config_manager import ConfigManager

async def main():
    """Main entry point for the triumvirate integration system"""
    parser = argparse.ArgumentParser(description="Triumvirate Integration Layer")
    parser.add_argument(
        "--config", 
        default="configs/integration_config.yaml",
        help="Configuration file path (default: configs/integration_config.yaml)"
    )
    parser.add_argument(
        "--action",
        choices=["start", "stop", "restart", "status", "health"],
        default="start",
        help="Action to perform (default: start)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="API server port (default: 8000)"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="API server host (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Run as daemon process"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    parser.add_argument(
        "--log-file",
        default="logs/triumvirate.log",
        help="Log file path (default: logs/triumvirate.log)"
    )
    
    args = parser.parse_args()
    
    # Create necessary directories
    Path("logs").mkdir(exist_ok=True)
    Path("data").mkdir(exist_ok=True)
    
    try:
        # Create and configure the integration manager
        manager = TriumvirateIntegrationManager(args.config)
        
        # Update API configuration if provided
        config_manager = ConfigManager(args.config)
        config = config_manager.load_config()
        config.api_config["host"] = args.host
        config.api_config["port"] = args.port
        config_manager.save_config(config)
        
        # Setup logging
        if args.debug:
            import logging
            logging.basicConfig(
                level=logging.DEBUG,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                handlers=[
                    logging.FileHandler(args.log_file),
                    logging.StreamHandler(sys.stdout)
                ]
            )
        
        # Setup signal handlers for graceful shutdown
        setup_signal_handlers(manager)
        
        # Perform the requested action
        if args.action == "start":
            await start_system(manager, args)
        elif args.action == "stop":
            await stop_system(manager)
        elif args.action == "restart":
            await restart_system(manager, args)
        elif args.action == "status":
            await show_status(manager)
        elif args.action == "health":
            await show_health(manager)
        
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

async def start_system(manager, args):
    """Start the triumvirate integration system"""
    print("🚀 Starting Triumvirate Integration Layer...")
    
    # Initialize the system
    print("📦 Initializing system components...")
    if not await manager.initialize():
        print("❌ Failed to initialize system")
        sys.exit(1)
    
    # Start the system
    print("⚡ Starting all components...")
    if not await manager.start():
        print("❌ Failed to start system")
        sys.exit(1)
    
    # Show system status
    status = manager.get_status()
    print("\n✅ Triumvirtate Integration Layer started successfully!")
    print(f"🌐 API Server: http://{args.host}:{args.port}")
    print(f"📊 System Status: {status['system_status'].title()}")
    
    if not args.daemon:
        print("\n📈 Component Status:")
        for comp_name, comp_info in status["components"].items():
            status_icon = "🟢" if comp_info["running"] else "🔴"
            print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
        
        print(f"\n🔗 API Endpoints:")
        print(f"  • Health: http://{args.host}:{args.port}/api/v1/monitoring/health")
        print(f"  • Metrics: http://{args.host}:{args.port}/api/v1/monitoring/metrics")
        print(f"  • System Overview: http://{args.host}:{args.port}/api/v1/system/overview")
        
        print(f"\n📝 Logs: {args.log_file}")
        print("\nPress Ctrl+C to stop the system")
        
        # Keep running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutdown requested...")
    else:
        print("🔄 Running as daemon...")

async def stop_system(manager):
    """Stop the triumvirate integration system"""
    print("🛑 Stopping Triumvirate Integration Layer...")
    
    if not await manager.stop():
        print("❌ Failed to stop system properly")
        sys.exit(1)
    
    print("✅ System stopped successfully")

async def restart_system(manager, args):
    """Restart the triumvirate integration system"""
    print("🔄 Restarting Triumvirate Integration Layer...")
    
    if not await manager.restart():
        print("❌ Failed to restart system")
        sys.exit(1)
    
    print("✅ System restarted successfully")
    print(f"🌐 Available at: http://{args.host}:{args.port}")

async def show_status(manager):
    """Show system status"""
    status = manager.get_status()
    
    print("📊 Triumvirate Integration Layer Status")
    print("=" * 50)
    print(f"System Status: {status['system_status'].title()}")
    
    if status['startup_time']:
        from datetime import datetime
        startup_time = datetime.fromisoformat(status['startup_time'])
        uptime_seconds = (datetime.now() - startup_time).total_seconds()
        uptime_hours = int(uptime_seconds // 3600)
        uptime_minutes = int((uptime_seconds % 3600) // 60)
        print(f"Uptime: {uptime_hours}h {uptime_minutes}m")
    
    print("\n🔧 Components:")
    for comp_name, comp_info in status["components"].items():
        status_icon = "🟢" if comp_info["running"] else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
    
    print("\n🌐 Shared Infrastructure:")
    for infra_name, infra_status in status["shared_infrastructure"].items():
        status_icon = "🟢" if infra_status else "🔴"
        print(f"  {status_icon} {infra_name.replace('_', ' ').title()}: {'Running' if infra_status else 'Stopped'}")
    
    print("\n🚀 Revolutionary Capabilities:")
    for cap_name, cap_status in status["revolutionary_capabilities"].items():
        status_icon = "🟢" if cap_status else "🔴"
        print(f"  {status_icon} {cap_name.replace('_', ' ').title()}: {'Active' if cap_status else 'Inactive'}")

async def show_health(manager):
    """Show detailed health information"""
    print("🏥 Triumvirate Integration Layer Health Check")
    print("=" * 50)
    
    # Get system overview
    overview = manager.observability.get_system_overview()
    
    print(f"System Health: {overview['system_health']['status'].title()}")
    print(f"Health Score: {overview['system_health']['score']:.1f}%")
    
    print(f"\n📊 Metrics:")
    print(f"  • Total Components: {overview['total_components_tracked']}")
    print(f"  • Active Alerts: {overview['active_alerts']}")
    print(f"  • Critical Alerts: {overview['critical_alerts']}")
    
    print(f"\n🔍 Component Health:")
    for comp_name in ["agenta", "pranava", "antakhara"]:
        health = await getattr(manager, comp_name).get_health_status()
        status_icon = "🟢" if health["status"] == "healthy" else "🟡" if health["status"] == "degraded" else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {health['status']}")
    
    # Check integration health
    integration_status = manager.get_status()
    if integration_status['system_status'] == 'running':
        print(f"\n✅ Integration Status: HEALTHY")
    else:
        print(f"\n❌ Integration Status: UNHEALTHY")

if __name__ == "__main__":
    # Ensure we can handle KeyboardInterrupt properly
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)Stop the triumvirate integration system"""
Main entry point for Triumvirate Integration Layer

This script provides a command-line interface for managing the triumvirate
integration system, including initialization, startup, shutdown, and monitoring.
"""

import asyncio
import argparse
import sys
import signal
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from triumvirate_manager import TriumvirateIntegrationManager, setup_signal_handlers
from configs.config_manager import ConfigManager

async def main():
    """Main entry point for the triumvirate integration system"""
    parser = argparse.ArgumentParser(description="Triumvirate Integration Layer")
    parser.add_argument(
        "--config", 
        default="configs/integration_config.yaml",
        help="Configuration file path (default: configs/integration_config.yaml)"
    )
    parser.add_argument(
        "--action",
        choices=["start", "stop", "restart", "status", "health"],
        default="start",
        help="Action to perform (default: start)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="API server port (default: 8000)"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="API server host (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Run as daemon process"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    parser.add_argument(
        "--log-file",
        default="logs/triumvirate.log",
        help="Log file path (default: logs/triumvirate.log)"
    )
    
    args = parser.parse_args()
    
    # Create necessary directories
    Path("logs").mkdir(exist_ok=True)
    Path("data").mkdir(exist_ok=True)
    
    try:
        # Create and configure the integration manager
        manager = TriumvirateIntegrationManager(args.config)
        
        # Update API configuration if provided
        config_manager = ConfigManager(args.config)
        config = config_manager.load_config()
        config.api_config["host"] = args.host
        config.api_config["port"] = args.port
        config_manager.save_config(config)
        
        # Setup logging
        if args.debug:
            import logging
            logging.basicConfig(
                level=logging.DEBUG,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                handlers=[
                    logging.FileHandler(args.log_file),
                    logging.StreamHandler(sys.stdout)
                ]
            )
        
        # Setup signal handlers for graceful shutdown
        setup_signal_handlers(manager)
        
        # Perform the requested action
        if args.action == "start":
            await start_system(manager, args)
        elif args.action == "stop":
            await stop_system(manager)
        elif args.action == "restart":
            await restart_system(manager, args)
        elif args.action == "status":
            await show_status(manager)
        elif args.action == "health":
            await show_health(manager)
        
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

async def start_system(manager, args):
    """Start the triumvirate integration system"""
    print("🚀 Starting Triumvirate Integration Layer...")
    
    # Initialize the system
    print("📦 Initializing system components...")
    if not await manager.initialize():
        print("❌ Failed to initialize system")
        sys.exit(1)
    
    # Start the system
    print("⚡ Starting all components...")
    if not await manager.start():
        print("❌ Failed to start system")
        sys.exit(1)
    
    # Show system status
    status = manager.get_status()
    print("\n✅ Triumvirtate Integration Layer started successfully!")
    print(f"🌐 API Server: http://{args.host}:{args.port}")
    print(f"📊 System Status: {status['system_status'].title()}")
    
    if not args.daemon:
        print("\n📈 Component Status:")
        for comp_name, comp_info in status["components"].items():
            status_icon = "🟢" if comp_info["running"] else "🔴"
            print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
        
        print(f"\n🔗 API Endpoints:")
        print(f"  • Health: http://{args.host}:{args.port}/api/v1/monitoring/health")
        print(f"  • Metrics: http://{args.host}:{args.port}/api/v1/monitoring/metrics")
        print(f"  • System Overview: http://{args.host}:{args.port}/api/v1/system/overview")
        
        print(f"\n📝 Logs: {args.log_file}")
        print("\nPress Ctrl+C to stop the system")
        
        # Keep running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutdown requested...")
    else:
        print("🔄 Running as daemon...")

async def stop_system(manager):
    """Stop the triumvirate integration system"""
    print("🛑 Stopping Triumvirate Integration Layer...")
    
    if not await manager.stop():
        print("❌ Failed to stop system properly")
        sys.exit(1)
    
    print("✅ System stopped successfully")

async def restart_system(manager, args):
    """Restart the triumvirate integration system"""
    print("🔄 Restarting Triumvirate Integration Layer...")
    
    if not await manager.restart():
        print("❌ Failed to restart system")
        sys.exit(1)
    
    print("✅ System restarted successfully")
    print(f"🌐 Available at: http://{args.host}:{args.port}")

async def show_status(manager):
    """Show system status"""
    status = manager.get_status()
    
    print("📊 Triumvirate Integration Layer Status")
    print("=" * 50)
    print(f"System Status: {status['system_status'].title()}")
    
    if status['startup_time']:
        from datetime import datetime
        startup_time = datetime.fromisoformat(status['startup_time'])
        uptime_seconds = (datetime.now() - startup_time).total_seconds()
        uptime_hours = int(uptime_seconds // 3600)
        uptime_minutes = int((uptime_seconds % 3600) // 60)
        print(f"Uptime: {uptime_hours}h {uptime_minutes}m")
    
    print("\n🔧 Components:")
    for comp_name, comp_info in status["components"].items():
        status_icon = "🟢" if comp_info["running"] else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
    
    print("\n🌐 Shared Infrastructure:")
    for infra_name, infra_status in status["shared_infrastructure"].items():
        status_icon = "🟢" if infra_status else "🔴"
        print(f"  {status_icon} {infra_name.replace('_', ' ').title()}: {'Running' if infra_status else 'Stopped'}")
    
    print("\n🚀 Revolutionary Capabilities:")
    for cap_name, cap_status in status["revolutionary_capabilities"].items():
        status_icon = "🟢" if cap_status else "🔴"
        print(f"  {status_icon} {cap_name.replace('_', ' ').title()}: {'Active' if cap_status else 'Inactive'}")

async def show_health(manager):
    """Show detailed health information"""
    print("🏥 Triumvirate Integration Layer Health Check")
    print("=" * 50)
    
    # Get system overview
    overview = manager.observability.get_system_overview()
    
    print(f"System Health: {overview['system_health']['status'].title()}")
    print(f"Health Score: {overview['system_health']['score']:.1f}%")
    
    print(f"\n📊 Metrics:")
    print(f"  • Total Components: {overview['total_components_tracked']}")
    print(f"  • Active Alerts: {overview['active_alerts']}")
    print(f"  • Critical Alerts: {overview['critical_alerts']}")
    
    print(f"\n🔍 Component Health:")
    for comp_name in ["agenta", "pranava", "antakhara"]:
        health = await getattr(manager, comp_name).get_health_status()
        status_icon = "🟢" if health["status"] == "healthy" else "🟡" if health["status"] == "degraded" else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {health['status']}")
    
    # Check integration health
    integration_status = manager.get_status()
    if integration_status['system_status'] == 'running':
        print(f"\n✅ Integration Status: HEALTHY")
    else:
        print(f"\n❌ Integration Status: UNHEALTHY")

if __name__ == "__main__":
    # Ensure we can handle KeyboardInterrupt properly
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
        try:
            if not self.is_running:
                self.logger.warning("System not running")
                return True
                
            self.logger.info("Stopping Triumvirate Integration System")
            
            # Stop revolutionary capabilities
            if self.self_healer:
                await self.self_healer.stop()
            if self.performance_optimizer:
                await self.performance_optimizer.stop()
            if self.adaptive_optimizer:
                await self.adaptive_optimizer.stop()
            if self.intelligent_coordinator:
                await self.intelligent_coordinator.stop()
            
            # Stop core components
            await self.agenta.stop()
            await self.pranava.stop()
            await self.antakhara.stop()
            
            # Stop shared infrastructure
            await self.message_router.stop()
            await self.service_discovery.stop_health_monitoring()
            await self.observability.stop()
            
            self.is_running = False
            self.logger.info("Triumvirate Integration System stopped")
            return True
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
            return False
            
    async def restart(self) -> bool:
        """
Main entry point for Triumvirate Integration Layer

This script provides a command-line interface for managing the triumvirate
integration system, including initialization, startup, shutdown, and monitoring.
"""

import asyncio
import argparse
import sys
import signal
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from triumvirate_manager import TriumvirateIntegrationManager, setup_signal_handlers
from configs.config_manager import ConfigManager

async def main():
    """Main entry point for the triumvirate integration system"""
    parser = argparse.ArgumentParser(description="Triumvirate Integration Layer")
    parser.add_argument(
        "--config", 
        default="configs/integration_config.yaml",
        help="Configuration file path (default: configs/integration_config.yaml)"
    )
    parser.add_argument(
        "--action",
        choices=["start", "stop", "restart", "status", "health"],
        default="start",
        help="Action to perform (default: start)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="API server port (default: 8000)"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="API server host (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Run as daemon process"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    parser.add_argument(
        "--log-file",
        default="logs/triumvirate.log",
        help="Log file path (default: logs/triumvirate.log)"
    )
    
    args = parser.parse_args()
    
    # Create necessary directories
    Path("logs").mkdir(exist_ok=True)
    Path("data").mkdir(exist_ok=True)
    
    try:
        # Create and configure the integration manager
        manager = TriumvirateIntegrationManager(args.config)
        
        # Update API configuration if provided
        config_manager = ConfigManager(args.config)
        config = config_manager.load_config()
        config.api_config["host"] = args.host
        config.api_config["port"] = args.port
        config_manager.save_config(config)
        
        # Setup logging
        if args.debug:
            import logging
            logging.basicConfig(
                level=logging.DEBUG,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                handlers=[
                    logging.FileHandler(args.log_file),
                    logging.StreamHandler(sys.stdout)
                ]
            )
        
        # Setup signal handlers for graceful shutdown
        setup_signal_handlers(manager)
        
        # Perform the requested action
        if args.action == "start":
            await start_system(manager, args)
        elif args.action == "stop":
            await stop_system(manager)
        elif args.action == "restart":
            await restart_system(manager, args)
        elif args.action == "status":
            await show_status(manager)
        elif args.action == "health":
            await show_health(manager)
        
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

async def start_system(manager, args):
    """Start the triumvirate integration system"""
    print("🚀 Starting Triumvirate Integration Layer...")
    
    # Initialize the system
    print("📦 Initializing system components...")
    if not await manager.initialize():
        print("❌ Failed to initialize system")
        sys.exit(1)
    
    # Start the system
    print("⚡ Starting all components...")
    if not await manager.start():
        print("❌ Failed to start system")
        sys.exit(1)
    
    # Show system status
    status = manager.get_status()
    print("\n✅ Triumvirtate Integration Layer started successfully!")
    print(f"🌐 API Server: http://{args.host}:{args.port}")
    print(f"📊 System Status: {status['system_status'].title()}")
    
    if not args.daemon:
        print("\n📈 Component Status:")
        for comp_name, comp_info in status["components"].items():
            status_icon = "🟢" if comp_info["running"] else "🔴"
            print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
        
        print(f"\n🔗 API Endpoints:")
        print(f"  • Health: http://{args.host}:{args.port}/api/v1/monitoring/health")
        print(f"  • Metrics: http://{args.host}:{args.port}/api/v1/monitoring/metrics")
        print(f"  • System Overview: http://{args.host}:{args.port}/api/v1/system/overview")
        
        print(f"\n📝 Logs: {args.log_file}")
        print("\nPress Ctrl+C to stop the system")
        
        # Keep running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutdown requested...")
    else:
        print("🔄 Running as daemon...")

async def stop_system(manager):
    """Stop the triumvirate integration system"""
    print("🛑 Stopping Triumvirate Integration Layer...")
    
    if not await manager.stop():
        print("❌ Failed to stop system properly")
        sys.exit(1)
    
    print("✅ System stopped successfully")

async def restart_system(manager, args):
    """Restart the triumvirate integration system"""
    print("🔄 Restarting Triumvirate Integration Layer...")
    
    if not await manager.restart():
        print("❌ Failed to restart system")
        sys.exit(1)
    
    print("✅ System restarted successfully")
    print(f"🌐 Available at: http://{args.host}:{args.port}")

async def show_status(manager):
    """Show system status"""
    status = manager.get_status()
    
    print("📊 Triumvirate Integration Layer Status")
    print("=" * 50)
    print(f"System Status: {status['system_status'].title()}")
    
    if status['startup_time']:
        from datetime import datetime
        startup_time = datetime.fromisoformat(status['startup_time'])
        uptime_seconds = (datetime.now() - startup_time).total_seconds()
        uptime_hours = int(uptime_seconds // 3600)
        uptime_minutes = int((uptime_seconds % 3600) // 60)
        print(f"Uptime: {uptime_hours}h {uptime_minutes}m")
    
    print("\n🔧 Components:")
    for comp_name, comp_info in status["components"].items():
        status_icon = "🟢" if comp_info["running"] else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
    
    print("\n🌐 Shared Infrastructure:")
    for infra_name, infra_status in status["shared_infrastructure"].items():
        status_icon = "🟢" if infra_status else "🔴"
        print(f"  {status_icon} {infra_name.replace('_', ' ').title()}: {'Running' if infra_status else 'Stopped'}")
    
    print("\n🚀 Revolutionary Capabilities:")
    for cap_name, cap_status in status["revolutionary_capabilities"].items():
        status_icon = "🟢" if cap_status else "🔴"
        print(f"  {status_icon} {cap_name.replace('_', ' ').title()}: {'Active' if cap_status else 'Inactive'}")

async def show_health(manager):
    """Show detailed health information"""
    print("🏥 Triumvirate Integration Layer Health Check")
    print("=" * 50)
    
    # Get system overview
    overview = manager.observability.get_system_overview()
    
    print(f"System Health: {overview['system_health']['status'].title()}")
    print(f"Health Score: {overview['system_health']['score']:.1f}%")
    
    print(f"\n📊 Metrics:")
    print(f"  • Total Components: {overview['total_components_tracked']}")
    print(f"  • Active Alerts: {overview['active_alerts']}")
    print(f"  • Critical Alerts: {overview['critical_alerts']}")
    
    print(f"\n🔍 Component Health:")
    for comp_name in ["agenta", "pranava", "antakhara"]:
        health = await getattr(manager, comp_name).get_health_status()
        status_icon = "🟢" if health["status"] == "healthy" else "🟡" if health["status"] == "degraded" else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {health['status']}")
    
    # Check integration health
    integration_status = manager.get_status()
    if integration_status['system_status'] == 'running':
        print(f"\n✅ Integration Status: HEALTHY")
    else:
        print(f"\n❌ Integration Status: UNHEALTHY")

if __name__ == "__main__":
    # Ensure we can handle KeyboardInterrupt properly
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)Restart the triumvirate integration system"""
Main entry point for Triumvirate Integration Layer

This script provides a command-line interface for managing the triumvirate
integration system, including initialization, startup, shutdown, and monitoring.
"""

import asyncio
import argparse
import sys
import signal
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from triumvirate_manager import TriumvirateIntegrationManager, setup_signal_handlers
from configs.config_manager import ConfigManager

async def main():
    """Main entry point for the triumvirate integration system"""
    parser = argparse.ArgumentParser(description="Triumvirate Integration Layer")
    parser.add_argument(
        "--config", 
        default="configs/integration_config.yaml",
        help="Configuration file path (default: configs/integration_config.yaml)"
    )
    parser.add_argument(
        "--action",
        choices=["start", "stop", "restart", "status", "health"],
        default="start",
        help="Action to perform (default: start)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="API server port (default: 8000)"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="API server host (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Run as daemon process"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    parser.add_argument(
        "--log-file",
        default="logs/triumvirate.log",
        help="Log file path (default: logs/triumvirate.log)"
    )
    
    args = parser.parse_args()
    
    # Create necessary directories
    Path("logs").mkdir(exist_ok=True)
    Path("data").mkdir(exist_ok=True)
    
    try:
        # Create and configure the integration manager
        manager = TriumvirateIntegrationManager(args.config)
        
        # Update API configuration if provided
        config_manager = ConfigManager(args.config)
        config = config_manager.load_config()
        config.api_config["host"] = args.host
        config.api_config["port"] = args.port
        config_manager.save_config(config)
        
        # Setup logging
        if args.debug:
            import logging
            logging.basicConfig(
                level=logging.DEBUG,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                handlers=[
                    logging.FileHandler(args.log_file),
                    logging.StreamHandler(sys.stdout)
                ]
            )
        
        # Setup signal handlers for graceful shutdown
        setup_signal_handlers(manager)
        
        # Perform the requested action
        if args.action == "start":
            await start_system(manager, args)
        elif args.action == "stop":
            await stop_system(manager)
        elif args.action == "restart":
            await restart_system(manager, args)
        elif args.action == "status":
            await show_status(manager)
        elif args.action == "health":
            await show_health(manager)
        
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

async def start_system(manager, args):
    """Start the triumvirate integration system"""
    print("🚀 Starting Triumvirate Integration Layer...")
    
    # Initialize the system
    print("📦 Initializing system components...")
    if not await manager.initialize():
        print("❌ Failed to initialize system")
        sys.exit(1)
    
    # Start the system
    print("⚡ Starting all components...")
    if not await manager.start():
        print("❌ Failed to start system")
        sys.exit(1)
    
    # Show system status
    status = manager.get_status()
    print("\n✅ Triumvirtate Integration Layer started successfully!")
    print(f"🌐 API Server: http://{args.host}:{args.port}")
    print(f"📊 System Status: {status['system_status'].title()}")
    
    if not args.daemon:
        print("\n📈 Component Status:")
        for comp_name, comp_info in status["components"].items():
            status_icon = "🟢" if comp_info["running"] else "🔴"
            print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
        
        print(f"\n🔗 API Endpoints:")
        print(f"  • Health: http://{args.host}:{args.port}/api/v1/monitoring/health")
        print(f"  • Metrics: http://{args.host}:{args.port}/api/v1/monitoring/metrics")
        print(f"  • System Overview: http://{args.host}:{args.port}/api/v1/system/overview")
        
        print(f"\n📝 Logs: {args.log_file}")
        print("\nPress Ctrl+C to stop the system")
        
        # Keep running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutdown requested...")
    else:
        print("🔄 Running as daemon...")

async def stop_system(manager):
    """Stop the triumvirate integration system"""
    print("🛑 Stopping Triumvirate Integration Layer...")
    
    if not await manager.stop():
        print("❌ Failed to stop system properly")
        sys.exit(1)
    
    print("✅ System stopped successfully")

async def restart_system(manager, args):
    """Restart the triumvirate integration system"""
    print("🔄 Restarting Triumvirate Integration Layer...")
    
    if not await manager.restart():
        print("❌ Failed to restart system")
        sys.exit(1)
    
    print("✅ System restarted successfully")
    print(f"🌐 Available at: http://{args.host}:{args.port}")

async def show_status(manager):
    """Show system status"""
    status = manager.get_status()
    
    print("📊 Triumvirate Integration Layer Status")
    print("=" * 50)
    print(f"System Status: {status['system_status'].title()}")
    
    if status['startup_time']:
        from datetime import datetime
        startup_time = datetime.fromisoformat(status['startup_time'])
        uptime_seconds = (datetime.now() - startup_time).total_seconds()
        uptime_hours = int(uptime_seconds // 3600)
        uptime_minutes = int((uptime_seconds % 3600) // 60)
        print(f"Uptime: {uptime_hours}h {uptime_minutes}m")
    
    print("\n🔧 Components:")
    for comp_name, comp_info in status["components"].items():
        status_icon = "🟢" if comp_info["running"] else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
    
    print("\n🌐 Shared Infrastructure:")
    for infra_name, infra_status in status["shared_infrastructure"].items():
        status_icon = "🟢" if infra_status else "🔴"
        print(f"  {status_icon} {infra_name.replace('_', ' ').title()}: {'Running' if infra_status else 'Stopped'}")
    
    print("\n🚀 Revolutionary Capabilities:")
    for cap_name, cap_status in status["revolutionary_capabilities"].items():
        status_icon = "🟢" if cap_status else "🔴"
        print(f"  {status_icon} {cap_name.replace('_', ' ').title()}: {'Active' if cap_status else 'Inactive'}")

async def show_health(manager):
    """Show detailed health information"""
    print("🏥 Triumvirate Integration Layer Health Check")
    print("=" * 50)
    
    # Get system overview
    overview = manager.observability.get_system_overview()
    
    print(f"System Health: {overview['system_health']['status'].title()}")
    print(f"Health Score: {overview['system_health']['score']:.1f}%")
    
    print(f"\n📊 Metrics:")
    print(f"  • Total Components: {overview['total_components_tracked']}")
    print(f"  • Active Alerts: {overview['active_alerts']}")
    print(f"  • Critical Alerts: {overview['critical_alerts']}")
    
    print(f"\n🔍 Component Health:")
    for comp_name in ["agenta", "pranava", "antakhara"]:
        health = await getattr(manager, comp_name).get_health_status()
        status_icon = "🟢" if health["status"] == "healthy" else "🟡" if health["status"] == "degraded" else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {health['status']}")
    
    # Check integration health
    integration_status = manager.get_status()
    if integration_status['system_status'] == 'running':
        print(f"\n✅ Integration Status: HEALTHY")
    else:
        print(f"\n❌ Integration Status: UNHEALTHY")

if __name__ == "__main__":
    # Ensure we can handle KeyboardInterrupt properly
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
        self.logger.info("Restarting Triumvirate Integration System")
        await self.stop()
        await asyncio.sleep(2)  # Brief pause
        return await self.start()
        
    def get_status(self) -> Dict[str, Any]:
        """
Main entry point for Triumvirate Integration Layer

This script provides a command-line interface for managing the triumvirate
integration system, including initialization, startup, shutdown, and monitoring.
"""

import asyncio
import argparse
import sys
import signal
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from triumvirate_manager import TriumvirateIntegrationManager, setup_signal_handlers
from configs.config_manager import ConfigManager

async def main():
    """Main entry point for the triumvirate integration system"""
    parser = argparse.ArgumentParser(description="Triumvirate Integration Layer")
    parser.add_argument(
        "--config", 
        default="configs/integration_config.yaml",
        help="Configuration file path (default: configs/integration_config.yaml)"
    )
    parser.add_argument(
        "--action",
        choices=["start", "stop", "restart", "status", "health"],
        default="start",
        help="Action to perform (default: start)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="API server port (default: 8000)"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="API server host (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Run as daemon process"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    parser.add_argument(
        "--log-file",
        default="logs/triumvirate.log",
        help="Log file path (default: logs/triumvirate.log)"
    )
    
    args = parser.parse_args()
    
    # Create necessary directories
    Path("logs").mkdir(exist_ok=True)
    Path("data").mkdir(exist_ok=True)
    
    try:
        # Create and configure the integration manager
        manager = TriumvirateIntegrationManager(args.config)
        
        # Update API configuration if provided
        config_manager = ConfigManager(args.config)
        config = config_manager.load_config()
        config.api_config["host"] = args.host
        config.api_config["port"] = args.port
        config_manager.save_config(config)
        
        # Setup logging
        if args.debug:
            import logging
            logging.basicConfig(
                level=logging.DEBUG,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                handlers=[
                    logging.FileHandler(args.log_file),
                    logging.StreamHandler(sys.stdout)
                ]
            )
        
        # Setup signal handlers for graceful shutdown
        setup_signal_handlers(manager)
        
        # Perform the requested action
        if args.action == "start":
            await start_system(manager, args)
        elif args.action == "stop":
            await stop_system(manager)
        elif args.action == "restart":
            await restart_system(manager, args)
        elif args.action == "status":
            await show_status(manager)
        elif args.action == "health":
            await show_health(manager)
        
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

async def start_system(manager, args):
    """Start the triumvirate integration system"""
    print("🚀 Starting Triumvirate Integration Layer...")
    
    # Initialize the system
    print("📦 Initializing system components...")
    if not await manager.initialize():
        print("❌ Failed to initialize system")
        sys.exit(1)
    
    # Start the system
    print("⚡ Starting all components...")
    if not await manager.start():
        print("❌ Failed to start system")
        sys.exit(1)
    
    # Show system status
    status = manager.get_status()
    print("\n✅ Triumvirtate Integration Layer started successfully!")
    print(f"🌐 API Server: http://{args.host}:{args.port}")
    print(f"📊 System Status: {status['system_status'].title()}")
    
    if not args.daemon:
        print("\n📈 Component Status:")
        for comp_name, comp_info in status["components"].items():
            status_icon = "🟢" if comp_info["running"] else "🔴"
            print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
        
        print(f"\n🔗 API Endpoints:")
        print(f"  • Health: http://{args.host}:{args.port}/api/v1/monitoring/health")
        print(f"  • Metrics: http://{args.host}:{args.port}/api/v1/monitoring/metrics")
        print(f"  • System Overview: http://{args.host}:{args.port}/api/v1/system/overview")
        
        print(f"\n📝 Logs: {args.log_file}")
        print("\nPress Ctrl+C to stop the system")
        
        # Keep running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutdown requested...")
    else:
        print("🔄 Running as daemon...")

async def stop_system(manager):
    """Stop the triumvirate integration system"""
    print("🛑 Stopping Triumvirate Integration Layer...")
    
    if not await manager.stop():
        print("❌ Failed to stop system properly")
        sys.exit(1)
    
    print("✅ System stopped successfully")

async def restart_system(manager, args):
    """Restart the triumvirate integration system"""
    print("🔄 Restarting Triumvirate Integration Layer...")
    
    if not await manager.restart():
        print("❌ Failed to restart system")
        sys.exit(1)
    
    print("✅ System restarted successfully")
    print(f"🌐 Available at: http://{args.host}:{args.port}")

async def show_status(manager):
    """Show system status"""
    status = manager.get_status()
    
    print("📊 Triumvirate Integration Layer Status")
    print("=" * 50)
    print(f"System Status: {status['system_status'].title()}")
    
    if status['startup_time']:
        from datetime import datetime
        startup_time = datetime.fromisoformat(status['startup_time'])
        uptime_seconds = (datetime.now() - startup_time).total_seconds()
        uptime_hours = int(uptime_seconds // 3600)
        uptime_minutes = int((uptime_seconds % 3600) // 60)
        print(f"Uptime: {uptime_hours}h {uptime_minutes}m")
    
    print("\n🔧 Components:")
    for comp_name, comp_info in status["components"].items():
        status_icon = "🟢" if comp_info["running"] else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
    
    print("\n🌐 Shared Infrastructure:")
    for infra_name, infra_status in status["shared_infrastructure"].items():
        status_icon = "🟢" if infra_status else "🔴"
        print(f"  {status_icon} {infra_name.replace('_', ' ').title()}: {'Running' if infra_status else 'Stopped'}")
    
    print("\n🚀 Revolutionary Capabilities:")
    for cap_name, cap_status in status["revolutionary_capabilities"].items():
        status_icon = "🟢" if cap_status else "🔴"
        print(f"  {status_icon} {cap_name.replace('_', ' ').title()}: {'Active' if cap_status else 'Inactive'}")

async def show_health(manager):
    """Show detailed health information"""
    print("🏥 Triumvirate Integration Layer Health Check")
    print("=" * 50)
    
    # Get system overview
    overview = manager.observability.get_system_overview()
    
    print(f"System Health: {overview['system_health']['status'].title()}")
    print(f"Health Score: {overview['system_health']['score']:.1f}%")
    
    print(f"\n📊 Metrics:")
    print(f"  • Total Components: {overview['total_components_tracked']}")
    print(f"  • Active Alerts: {overview['active_alerts']}")
    print(f"  • Critical Alerts: {overview['critical_alerts']}")
    
    print(f"\n🔍 Component Health:")
    for comp_name in ["agenta", "pranava", "antakhara"]:
        health = await getattr(manager, comp_name).get_health_status()
        status_icon = "🟢" if health["status"] == "healthy" else "🟡" if health["status"] == "degraded" else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {health['status']}")
    
    # Check integration health
    integration_status = manager.get_status()
    if integration_status['system_status'] == 'running':
        print(f"\n✅ Integration Status: HEALTHY")
    else:
        print(f"\n❌ Integration Status: UNHEALTHY")

if __name__ == "__main__":
    # Ensure we can handle KeyboardInterrupt properly
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)Get comprehensive system status"""
Main entry point for Triumvirate Integration Layer

This script provides a command-line interface for managing the triumvirate
integration system, including initialization, startup, shutdown, and monitoring.
"""

import asyncio
import argparse
import sys
import signal
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from triumvirate_manager import TriumvirateIntegrationManager, setup_signal_handlers
from configs.config_manager import ConfigManager

async def main():
    """Main entry point for the triumvirate integration system"""
    parser = argparse.ArgumentParser(description="Triumvirate Integration Layer")
    parser.add_argument(
        "--config", 
        default="configs/integration_config.yaml",
        help="Configuration file path (default: configs/integration_config.yaml)"
    )
    parser.add_argument(
        "--action",
        choices=["start", "stop", "restart", "status", "health"],
        default="start",
        help="Action to perform (default: start)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="API server port (default: 8000)"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="API server host (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Run as daemon process"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    parser.add_argument(
        "--log-file",
        default="logs/triumvirate.log",
        help="Log file path (default: logs/triumvirate.log)"
    )
    
    args = parser.parse_args()
    
    # Create necessary directories
    Path("logs").mkdir(exist_ok=True)
    Path("data").mkdir(exist_ok=True)
    
    try:
        # Create and configure the integration manager
        manager = TriumvirateIntegrationManager(args.config)
        
        # Update API configuration if provided
        config_manager = ConfigManager(args.config)
        config = config_manager.load_config()
        config.api_config["host"] = args.host
        config.api_config["port"] = args.port
        config_manager.save_config(config)
        
        # Setup logging
        if args.debug:
            import logging
            logging.basicConfig(
                level=logging.DEBUG,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                handlers=[
                    logging.FileHandler(args.log_file),
                    logging.StreamHandler(sys.stdout)
                ]
            )
        
        # Setup signal handlers for graceful shutdown
        setup_signal_handlers(manager)
        
        # Perform the requested action
        if args.action == "start":
            await start_system(manager, args)
        elif args.action == "stop":
            await stop_system(manager)
        elif args.action == "restart":
            await restart_system(manager, args)
        elif args.action == "status":
            await show_status(manager)
        elif args.action == "health":
            await show_health(manager)
        
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

async def start_system(manager, args):
    """Start the triumvirate integration system"""
    print("🚀 Starting Triumvirate Integration Layer...")
    
    # Initialize the system
    print("📦 Initializing system components...")
    if not await manager.initialize():
        print("❌ Failed to initialize system")
        sys.exit(1)
    
    # Start the system
    print("⚡ Starting all components...")
    if not await manager.start():
        print("❌ Failed to start system")
        sys.exit(1)
    
    # Show system status
    status = manager.get_status()
    print("\n✅ Triumvirtate Integration Layer started successfully!")
    print(f"🌐 API Server: http://{args.host}:{args.port}")
    print(f"📊 System Status: {status['system_status'].title()}")
    
    if not args.daemon:
        print("\n📈 Component Status:")
        for comp_name, comp_info in status["components"].items():
            status_icon = "🟢" if comp_info["running"] else "🔴"
            print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
        
        print(f"\n🔗 API Endpoints:")
        print(f"  • Health: http://{args.host}:{args.port}/api/v1/monitoring/health")
        print(f"  • Metrics: http://{args.host}:{args.port}/api/v1/monitoring/metrics")
        print(f"  • System Overview: http://{args.host}:{args.port}/api/v1/system/overview")
        
        print(f"\n📝 Logs: {args.log_file}")
        print("\nPress Ctrl+C to stop the system")
        
        # Keep running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutdown requested...")
    else:
        print("🔄 Running as daemon...")

async def stop_system(manager):
    """Stop the triumvirate integration system"""
    print("🛑 Stopping Triumvirate Integration Layer...")
    
    if not await manager.stop():
        print("❌ Failed to stop system properly")
        sys.exit(1)
    
    print("✅ System stopped successfully")

async def restart_system(manager, args):
    """Restart the triumvirate integration system"""
    print("🔄 Restarting Triumvirate Integration Layer...")
    
    if not await manager.restart():
        print("❌ Failed to restart system")
        sys.exit(1)
    
    print("✅ System restarted successfully")
    print(f"🌐 Available at: http://{args.host}:{args.port}")

async def show_status(manager):
    """Show system status"""
    status = manager.get_status()
    
    print("📊 Triumvirate Integration Layer Status")
    print("=" * 50)
    print(f"System Status: {status['system_status'].title()}")
    
    if status['startup_time']:
        from datetime import datetime
        startup_time = datetime.fromisoformat(status['startup_time'])
        uptime_seconds = (datetime.now() - startup_time).total_seconds()
        uptime_hours = int(uptime_seconds // 3600)
        uptime_minutes = int((uptime_seconds % 3600) // 60)
        print(f"Uptime: {uptime_hours}h {uptime_minutes}m")
    
    print("\n🔧 Components:")
    for comp_name, comp_info in status["components"].items():
        status_icon = "🟢" if comp_info["running"] else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
    
    print("\n🌐 Shared Infrastructure:")
    for infra_name, infra_status in status["shared_infrastructure"].items():
        status_icon = "🟢" if infra_status else "🔴"
        print(f"  {status_icon} {infra_name.replace('_', ' ').title()}: {'Running' if infra_status else 'Stopped'}")
    
    print("\n🚀 Revolutionary Capabilities:")
    for cap_name, cap_status in status["revolutionary_capabilities"].items():
        status_icon = "🟢" if cap_status else "🔴"
        print(f"  {status_icon} {cap_name.replace('_', ' ').title()}: {'Active' if cap_status else 'Inactive'}")

async def show_health(manager):
    """Show detailed health information"""
    print("🏥 Triumvirate Integration Layer Health Check")
    print("=" * 50)
    
    # Get system overview
    overview = manager.observability.get_system_overview()
    
    print(f"System Health: {overview['system_health']['status'].title()}")
    print(f"Health Score: {overview['system_health']['score']:.1f}%")
    
    print(f"\n📊 Metrics:")
    print(f"  • Total Components: {overview['total_components_tracked']}")
    print(f"  • Active Alerts: {overview['active_alerts']}")
    print(f"  • Critical Alerts: {overview['critical_alerts']}")
    
    print(f"\n🔍 Component Health:")
    for comp_name in ["agenta", "pranava", "antakhara"]:
        health = await getattr(manager, comp_name).get_health_status()
        status_icon = "🟢" if health["status"] == "healthy" else "🟡" if health["status"] == "degraded" else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {health['status']}")
    
    # Check integration health
    integration_status = manager.get_status()
    if integration_status['system_status'] == 'running':
        print(f"\n✅ Integration Status: HEALTHY")
    else:
        print(f"\n❌ Integration Status: UNHEALTHY")

if __name__ == "__main__":
    # Ensure we can handle KeyboardInterrupt properly
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
        uptime_seconds = 0
        if self.startup_time:
            uptime_seconds = (datetime.now() - self.startup_time).total_seconds()
            
        return {
            "system_status": "running" if self.is_running else "stopped",
            "startup_time": self.startup_time.isoformat() if self.startup_time else None,
            "uptime_seconds": uptime_seconds,
            "components": {
                "agenta": {
                    "running": self.agenta.is_running if self.agenta else False,
                    "status": self.component_health.get("agenta", {}).get("status", "unknown")
                },
                "pranava": {
                    "running": self.pranava.is_running if self.pranava else False,
                    "status": self.component_health.get("pranava", {}).get("status", "unknown")
                },
                "antakhara": {
                    "running": self.antakhara.is_running if self.antakhara else False,
                    "status": self.component_health.get("antakhara", {}).get("status", "unknown")
                }
            },
            "shared_infrastructure": {
                "message_router": self.message_router.running if self.message_router else False,
                "service_discovery": self.service_discovery.is_monitoring if self.service_discovery else False,
                "observability": self.observability.is_monitoring if self.observability else False
            },
            "revolutionary_capabilities": {
                "intelligent_coordinator": self.intelligent_coordinator.is_running if self.intelligent_coordinator else False,
                "adaptive_optimizer": self.adaptive_optimizer.is_running if self.adaptive_optimizer else False,
                "self_healer": self.self_healer.is_running if self.self_healer else False,
                "performance_optimizer": self.performance_optimizer.is_running if self.performance_optimizer else False
            }
        }
        
    async def _initialize_shared_infrastructure(self) -> None:
        """
Main entry point for Triumvirate Integration Layer

This script provides a command-line interface for managing the triumvirate
integration system, including initialization, startup, shutdown, and monitoring.
"""

import asyncio
import argparse
import sys
import signal
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from triumvirate_manager import TriumvirateIntegrationManager, setup_signal_handlers
from configs.config_manager import ConfigManager

async def main():
    """Main entry point for the triumvirate integration system"""
    parser = argparse.ArgumentParser(description="Triumvirate Integration Layer")
    parser.add_argument(
        "--config", 
        default="configs/integration_config.yaml",
        help="Configuration file path (default: configs/integration_config.yaml)"
    )
    parser.add_argument(
        "--action",
        choices=["start", "stop", "restart", "status", "health"],
        default="start",
        help="Action to perform (default: start)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="API server port (default: 8000)"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="API server host (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Run as daemon process"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    parser.add_argument(
        "--log-file",
        default="logs/triumvirate.log",
        help="Log file path (default: logs/triumvirate.log)"
    )
    
    args = parser.parse_args()
    
    # Create necessary directories
    Path("logs").mkdir(exist_ok=True)
    Path("data").mkdir(exist_ok=True)
    
    try:
        # Create and configure the integration manager
        manager = TriumvirateIntegrationManager(args.config)
        
        # Update API configuration if provided
        config_manager = ConfigManager(args.config)
        config = config_manager.load_config()
        config.api_config["host"] = args.host
        config.api_config["port"] = args.port
        config_manager.save_config(config)
        
        # Setup logging
        if args.debug:
            import logging
            logging.basicConfig(
                level=logging.DEBUG,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                handlers=[
                    logging.FileHandler(args.log_file),
                    logging.StreamHandler(sys.stdout)
                ]
            )
        
        # Setup signal handlers for graceful shutdown
        setup_signal_handlers(manager)
        
        # Perform the requested action
        if args.action == "start":
            await start_system(manager, args)
        elif args.action == "stop":
            await stop_system(manager)
        elif args.action == "restart":
            await restart_system(manager, args)
        elif args.action == "status":
            await show_status(manager)
        elif args.action == "health":
            await show_health(manager)
        
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

async def start_system(manager, args):
    """Start the triumvirate integration system"""
    print("🚀 Starting Triumvirate Integration Layer...")
    
    # Initialize the system
    print("📦 Initializing system components...")
    if not await manager.initialize():
        print("❌ Failed to initialize system")
        sys.exit(1)
    
    # Start the system
    print("⚡ Starting all components...")
    if not await manager.start():
        print("❌ Failed to start system")
        sys.exit(1)
    
    # Show system status
    status = manager.get_status()
    print("\n✅ Triumvirtate Integration Layer started successfully!")
    print(f"🌐 API Server: http://{args.host}:{args.port}")
    print(f"📊 System Status: {status['system_status'].title()}")
    
    if not args.daemon:
        print("\n📈 Component Status:")
        for comp_name, comp_info in status["components"].items():
            status_icon = "🟢" if comp_info["running"] else "🔴"
            print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
        
        print(f"\n🔗 API Endpoints:")
        print(f"  • Health: http://{args.host}:{args.port}/api/v1/monitoring/health")
        print(f"  • Metrics: http://{args.host}:{args.port}/api/v1/monitoring/metrics")
        print(f"  • System Overview: http://{args.host}:{args.port}/api/v1/system/overview")
        
        print(f"\n📝 Logs: {args.log_file}")
        print("\nPress Ctrl+C to stop the system")
        
        # Keep running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutdown requested...")
    else:
        print("🔄 Running as daemon...")

async def stop_system(manager):
    """Stop the triumvirate integration system"""
    print("🛑 Stopping Triumvirate Integration Layer...")
    
    if not await manager.stop():
        print("❌ Failed to stop system properly")
        sys.exit(1)
    
    print("✅ System stopped successfully")

async def restart_system(manager, args):
    """Restart the triumvirate integration system"""
    print("🔄 Restarting Triumvirate Integration Layer...")
    
    if not await manager.restart():
        print("❌ Failed to restart system")
        sys.exit(1)
    
    print("✅ System restarted successfully")
    print(f"🌐 Available at: http://{args.host}:{args.port}")

async def show_status(manager):
    """Show system status"""
    status = manager.get_status()
    
    print("📊 Triumvirate Integration Layer Status")
    print("=" * 50)
    print(f"System Status: {status['system_status'].title()}")
    
    if status['startup_time']:
        from datetime import datetime
        startup_time = datetime.fromisoformat(status['startup_time'])
        uptime_seconds = (datetime.now() - startup_time).total_seconds()
        uptime_hours = int(uptime_seconds // 3600)
        uptime_minutes = int((uptime_seconds % 3600) // 60)
        print(f"Uptime: {uptime_hours}h {uptime_minutes}m")
    
    print("\n🔧 Components:")
    for comp_name, comp_info in status["components"].items():
        status_icon = "🟢" if comp_info["running"] else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
    
    print("\n🌐 Shared Infrastructure:")
    for infra_name, infra_status in status["shared_infrastructure"].items():
        status_icon = "🟢" if infra_status else "🔴"
        print(f"  {status_icon} {infra_name.replace('_', ' ').title()}: {'Running' if infra_status else 'Stopped'}")
    
    print("\n🚀 Revolutionary Capabilities:")
    for cap_name, cap_status in status["revolutionary_capabilities"].items():
        status_icon = "🟢" if cap_status else "🔴"
        print(f"  {status_icon} {cap_name.replace('_', ' ').title()}: {'Active' if cap_status else 'Inactive'}")

async def show_health(manager):
    """Show detailed health information"""
    print("🏥 Triumvirate Integration Layer Health Check")
    print("=" * 50)
    
    # Get system overview
    overview = manager.observability.get_system_overview()
    
    print(f"System Health: {overview['system_health']['status'].title()}")
    print(f"Health Score: {overview['system_health']['score']:.1f}%")
    
    print(f"\n📊 Metrics:")
    print(f"  • Total Components: {overview['total_components_tracked']}")
    print(f"  • Active Alerts: {overview['active_alerts']}")
    print(f"  • Critical Alerts: {overview['critical_alerts']}")
    
    print(f"\n🔍 Component Health:")
    for comp_name in ["agenta", "pranava", "antakhara"]:
        health = await getattr(manager, comp_name).get_health_status()
        status_icon = "🟢" if health["status"] == "healthy" else "🟡" if health["status"] == "degraded" else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {health['status']}")
    
    # Check integration health
    integration_status = manager.get_status()
    if integration_status['system_status'] == 'running':
        print(f"\n✅ Integration Status: HEALTHY")
    else:
        print(f"\n❌ Integration Status: UNHEALTHY")

if __name__ == "__main__":
    # Ensure we can handle KeyboardInterrupt properly
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)Initialize shared infrastructure components"""
Main entry point for Triumvirate Integration Layer

This script provides a command-line interface for managing the triumvirate
integration system, including initialization, startup, shutdown, and monitoring.
"""

import asyncio
import argparse
import sys
import signal
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from triumvirate_manager import TriumvirateIntegrationManager, setup_signal_handlers
from configs.config_manager import ConfigManager

async def main():
    """Main entry point for the triumvirate integration system"""
    parser = argparse.ArgumentParser(description="Triumvirate Integration Layer")
    parser.add_argument(
        "--config", 
        default="configs/integration_config.yaml",
        help="Configuration file path (default: configs/integration_config.yaml)"
    )
    parser.add_argument(
        "--action",
        choices=["start", "stop", "restart", "status", "health"],
        default="start",
        help="Action to perform (default: start)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="API server port (default: 8000)"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="API server host (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Run as daemon process"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    parser.add_argument(
        "--log-file",
        default="logs/triumvirate.log",
        help="Log file path (default: logs/triumvirate.log)"
    )
    
    args = parser.parse_args()
    
    # Create necessary directories
    Path("logs").mkdir(exist_ok=True)
    Path("data").mkdir(exist_ok=True)
    
    try:
        # Create and configure the integration manager
        manager = TriumvirateIntegrationManager(args.config)
        
        # Update API configuration if provided
        config_manager = ConfigManager(args.config)
        config = config_manager.load_config()
        config.api_config["host"] = args.host
        config.api_config["port"] = args.port
        config_manager.save_config(config)
        
        # Setup logging
        if args.debug:
            import logging
            logging.basicConfig(
                level=logging.DEBUG,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                handlers=[
                    logging.FileHandler(args.log_file),
                    logging.StreamHandler(sys.stdout)
                ]
            )
        
        # Setup signal handlers for graceful shutdown
        setup_signal_handlers(manager)
        
        # Perform the requested action
        if args.action == "start":
            await start_system(manager, args)
        elif args.action == "stop":
            await stop_system(manager)
        elif args.action == "restart":
            await restart_system(manager, args)
        elif args.action == "status":
            await show_status(manager)
        elif args.action == "health":
            await show_health(manager)
        
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

async def start_system(manager, args):
    """Start the triumvirate integration system"""
    print("🚀 Starting Triumvirate Integration Layer...")
    
    # Initialize the system
    print("📦 Initializing system components...")
    if not await manager.initialize():
        print("❌ Failed to initialize system")
        sys.exit(1)
    
    # Start the system
    print("⚡ Starting all components...")
    if not await manager.start():
        print("❌ Failed to start system")
        sys.exit(1)
    
    # Show system status
    status = manager.get_status()
    print("\n✅ Triumvirtate Integration Layer started successfully!")
    print(f"🌐 API Server: http://{args.host}:{args.port}")
    print(f"📊 System Status: {status['system_status'].title()}")
    
    if not args.daemon:
        print("\n📈 Component Status:")
        for comp_name, comp_info in status["components"].items():
            status_icon = "🟢" if comp_info["running"] else "🔴"
            print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
        
        print(f"\n🔗 API Endpoints:")
        print(f"  • Health: http://{args.host}:{args.port}/api/v1/monitoring/health")
        print(f"  • Metrics: http://{args.host}:{args.port}/api/v1/monitoring/metrics")
        print(f"  • System Overview: http://{args.host}:{args.port}/api/v1/system/overview")
        
        print(f"\n📝 Logs: {args.log_file}")
        print("\nPress Ctrl+C to stop the system")
        
        # Keep running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutdown requested...")
    else:
        print("🔄 Running as daemon...")

async def stop_system(manager):
    """Stop the triumvirate integration system"""
    print("🛑 Stopping Triumvirate Integration Layer...")
    
    if not await manager.stop():
        print("❌ Failed to stop system properly")
        sys.exit(1)
    
    print("✅ System stopped successfully")

async def restart_system(manager, args):
    """Restart the triumvirate integration system"""
    print("🔄 Restarting Triumvirate Integration Layer...")
    
    if not await manager.restart():
        print("❌ Failed to restart system")
        sys.exit(1)
    
    print("✅ System restarted successfully")
    print(f"🌐 Available at: http://{args.host}:{args.port}")

async def show_status(manager):
    """Show system status"""
    status = manager.get_status()
    
    print("📊 Triumvirate Integration Layer Status")
    print("=" * 50)
    print(f"System Status: {status['system_status'].title()}")
    
    if status['startup_time']:
        from datetime import datetime
        startup_time = datetime.fromisoformat(status['startup_time'])
        uptime_seconds = (datetime.now() - startup_time).total_seconds()
        uptime_hours = int(uptime_seconds // 3600)
        uptime_minutes = int((uptime_seconds % 3600) // 60)
        print(f"Uptime: {uptime_hours}h {uptime_minutes}m")
    
    print("\n🔧 Components:")
    for comp_name, comp_info in status["components"].items():
        status_icon = "🟢" if comp_info["running"] else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
    
    print("\n🌐 Shared Infrastructure:")
    for infra_name, infra_status in status["shared_infrastructure"].items():
        status_icon = "🟢" if infra_status else "🔴"
        print(f"  {status_icon} {infra_name.replace('_', ' ').title()}: {'Running' if infra_status else 'Stopped'}")
    
    print("\n🚀 Revolutionary Capabilities:")
    for cap_name, cap_status in status["revolutionary_capabilities"].items():
        status_icon = "🟢" if cap_status else "🔴"
        print(f"  {status_icon} {cap_name.replace('_', ' ').title()}: {'Active' if cap_status else 'Inactive'}")

async def show_health(manager):
    """Show detailed health information"""
    print("🏥 Triumvirate Integration Layer Health Check")
    print("=" * 50)
    
    # Get system overview
    overview = manager.observability.get_system_overview()
    
    print(f"System Health: {overview['system_health']['status'].title()}")
    print(f"Health Score: {overview['system_health']['score']:.1f}%")
    
    print(f"\n📊 Metrics:")
    print(f"  • Total Components: {overview['total_components_tracked']}")
    print(f"  • Active Alerts: {overview['active_alerts']}")
    print(f"  • Critical Alerts: {overview['critical_alerts']}")
    
    print(f"\n🔍 Component Health:")
    for comp_name in ["agenta", "pranava", "antakhara"]:
        health = await getattr(manager, comp_name).get_health_status()
        status_icon = "🟢" if health["status"] == "healthy" else "🟡" if health["status"] == "degraded" else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {health['status']}")
    
    # Check integration health
    integration_status = manager.get_status()
    if integration_status['system_status'] == 'running':
        print(f"\n✅ Integration Status: HEALTHY")
    else:
        print(f"\n❌ Integration Status: UNHEALTHY")

if __name__ == "__main__":
    # Ensure we can handle KeyboardInterrupt properly
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
        self.logger.info("Initializing shared infrastructure")
        
        # Message router
        self.message_router = MessageRouter()
        
        # Service discovery
        health_interval = self.config.shared_config.get("health_check_interval", 30)
        self.service_discovery = ServiceDiscovery(health_interval)
        
        # Observability
        retention_hours = self.config.monitoring.get("metrics_retention_hours", 24)
        max_alerts = self.config.monitoring.get("max_alerts", 1000)
        self.observability = ObservabilityManager(retention_hours, max_alerts)
        
    async def _initialize_triumvirate_components(self) -> None:
        """
Main entry point for Triumvirate Integration Layer

This script provides a command-line interface for managing the triumvirate
integration system, including initialization, startup, shutdown, and monitoring.
"""

import asyncio
import argparse
import sys
import signal
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from triumvirate_manager import TriumvirateIntegrationManager, setup_signal_handlers
from configs.config_manager import ConfigManager

async def main():
    """Main entry point for the triumvirate integration system"""
    parser = argparse.ArgumentParser(description="Triumvirate Integration Layer")
    parser.add_argument(
        "--config", 
        default="configs/integration_config.yaml",
        help="Configuration file path (default: configs/integration_config.yaml)"
    )
    parser.add_argument(
        "--action",
        choices=["start", "stop", "restart", "status", "health"],
        default="start",
        help="Action to perform (default: start)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="API server port (default: 8000)"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="API server host (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Run as daemon process"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    parser.add_argument(
        "--log-file",
        default="logs/triumvirate.log",
        help="Log file path (default: logs/triumvirate.log)"
    )
    
    args = parser.parse_args()
    
    # Create necessary directories
    Path("logs").mkdir(exist_ok=True)
    Path("data").mkdir(exist_ok=True)
    
    try:
        # Create and configure the integration manager
        manager = TriumvirateIntegrationManager(args.config)
        
        # Update API configuration if provided
        config_manager = ConfigManager(args.config)
        config = config_manager.load_config()
        config.api_config["host"] = args.host
        config.api_config["port"] = args.port
        config_manager.save_config(config)
        
        # Setup logging
        if args.debug:
            import logging
            logging.basicConfig(
                level=logging.DEBUG,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                handlers=[
                    logging.FileHandler(args.log_file),
                    logging.StreamHandler(sys.stdout)
                ]
            )
        
        # Setup signal handlers for graceful shutdown
        setup_signal_handlers(manager)
        
        # Perform the requested action
        if args.action == "start":
            await start_system(manager, args)
        elif args.action == "stop":
            await stop_system(manager)
        elif args.action == "restart":
            await restart_system(manager, args)
        elif args.action == "status":
            await show_status(manager)
        elif args.action == "health":
            await show_health(manager)
        
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

async def start_system(manager, args):
    """Start the triumvirate integration system"""
    print("🚀 Starting Triumvirate Integration Layer...")
    
    # Initialize the system
    print("📦 Initializing system components...")
    if not await manager.initialize():
        print("❌ Failed to initialize system")
        sys.exit(1)
    
    # Start the system
    print("⚡ Starting all components...")
    if not await manager.start():
        print("❌ Failed to start system")
        sys.exit(1)
    
    # Show system status
    status = manager.get_status()
    print("\n✅ Triumvirtate Integration Layer started successfully!")
    print(f"🌐 API Server: http://{args.host}:{args.port}")
    print(f"📊 System Status: {status['system_status'].title()}")
    
    if not args.daemon:
        print("\n📈 Component Status:")
        for comp_name, comp_info in status["components"].items():
            status_icon = "🟢" if comp_info["running"] else "🔴"
            print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
        
        print(f"\n🔗 API Endpoints:")
        print(f"  • Health: http://{args.host}:{args.port}/api/v1/monitoring/health")
        print(f"  • Metrics: http://{args.host}:{args.port}/api/v1/monitoring/metrics")
        print(f"  • System Overview: http://{args.host}:{args.port}/api/v1/system/overview")
        
        print(f"\n📝 Logs: {args.log_file}")
        print("\nPress Ctrl+C to stop the system")
        
        # Keep running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutdown requested...")
    else:
        print("🔄 Running as daemon...")

async def stop_system(manager):
    """Stop the triumvirate integration system"""
    print("🛑 Stopping Triumvirate Integration Layer...")
    
    if not await manager.stop():
        print("❌ Failed to stop system properly")
        sys.exit(1)
    
    print("✅ System stopped successfully")

async def restart_system(manager, args):
    """Restart the triumvirate integration system"""
    print("🔄 Restarting Triumvirate Integration Layer...")
    
    if not await manager.restart():
        print("❌ Failed to restart system")
        sys.exit(1)
    
    print("✅ System restarted successfully")
    print(f"🌐 Available at: http://{args.host}:{args.port}")

async def show_status(manager):
    """Show system status"""
    status = manager.get_status()
    
    print("📊 Triumvirate Integration Layer Status")
    print("=" * 50)
    print(f"System Status: {status['system_status'].title()}")
    
    if status['startup_time']:
        from datetime import datetime
        startup_time = datetime.fromisoformat(status['startup_time'])
        uptime_seconds = (datetime.now() - startup_time).total_seconds()
        uptime_hours = int(uptime_seconds // 3600)
        uptime_minutes = int((uptime_seconds % 3600) // 60)
        print(f"Uptime: {uptime_hours}h {uptime_minutes}m")
    
    print("\n🔧 Components:")
    for comp_name, comp_info in status["components"].items():
        status_icon = "🟢" if comp_info["running"] else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
    
    print("\n🌐 Shared Infrastructure:")
    for infra_name, infra_status in status["shared_infrastructure"].items():
        status_icon = "🟢" if infra_status else "🔴"
        print(f"  {status_icon} {infra_name.replace('_', ' ').title()}: {'Running' if infra_status else 'Stopped'}")
    
    print("\n🚀 Revolutionary Capabilities:")
    for cap_name, cap_status in status["revolutionary_capabilities"].items():
        status_icon = "🟢" if cap_status else "🔴"
        print(f"  {status_icon} {cap_name.replace('_', ' ').title()}: {'Active' if cap_status else 'Inactive'}")

async def show_health(manager):
    """Show detailed health information"""
    print("🏥 Triumvirate Integration Layer Health Check")
    print("=" * 50)
    
    # Get system overview
    overview = manager.observability.get_system_overview()
    
    print(f"System Health: {overview['system_health']['status'].title()}")
    print(f"Health Score: {overview['system_health']['score']:.1f}%")
    
    print(f"\n📊 Metrics:")
    print(f"  • Total Components: {overview['total_components_tracked']}")
    print(f"  • Active Alerts: {overview['active_alerts']}")
    print(f"  • Critical Alerts: {overview['critical_alerts']}")
    
    print(f"\n🔍 Component Health:")
    for comp_name in ["agenta", "pranava", "antakhara"]:
        health = await getattr(manager, comp_name).get_health_status()
        status_icon = "🟢" if health["status"] == "healthy" else "🟡" if health["status"] == "degraded" else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {health['status']}")
    
    # Check integration health
    integration_status = manager.get_status()
    if integration_status['system_status'] == 'running':
        print(f"\n✅ Integration Status: HEALTHY")
    else:
        print(f"\n❌ Integration Status: UNHEALTHY")

if __name__ == "__main__":
    # Ensure we can handle KeyboardInterrupt properly
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)Initialize the three core triumvirate components"""
Main entry point for Triumvirate Integration Layer

This script provides a command-line interface for managing the triumvirate
integration system, including initialization, startup, shutdown, and monitoring.
"""

import asyncio
import argparse
import sys
import signal
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from triumvirate_manager import TriumvirateIntegrationManager, setup_signal_handlers
from configs.config_manager import ConfigManager

async def main():
    """Main entry point for the triumvirate integration system"""
    parser = argparse.ArgumentParser(description="Triumvirate Integration Layer")
    parser.add_argument(
        "--config", 
        default="configs/integration_config.yaml",
        help="Configuration file path (default: configs/integration_config.yaml)"
    )
    parser.add_argument(
        "--action",
        choices=["start", "stop", "restart", "status", "health"],
        default="start",
        help="Action to perform (default: start)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="API server port (default: 8000)"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="API server host (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Run as daemon process"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    parser.add_argument(
        "--log-file",
        default="logs/triumvirate.log",
        help="Log file path (default: logs/triumvirate.log)"
    )
    
    args = parser.parse_args()
    
    # Create necessary directories
    Path("logs").mkdir(exist_ok=True)
    Path("data").mkdir(exist_ok=True)
    
    try:
        # Create and configure the integration manager
        manager = TriumvirateIntegrationManager(args.config)
        
        # Update API configuration if provided
        config_manager = ConfigManager(args.config)
        config = config_manager.load_config()
        config.api_config["host"] = args.host
        config.api_config["port"] = args.port
        config_manager.save_config(config)
        
        # Setup logging
        if args.debug:
            import logging
            logging.basicConfig(
                level=logging.DEBUG,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                handlers=[
                    logging.FileHandler(args.log_file),
                    logging.StreamHandler(sys.stdout)
                ]
            )
        
        # Setup signal handlers for graceful shutdown
        setup_signal_handlers(manager)
        
        # Perform the requested action
        if args.action == "start":
            await start_system(manager, args)
        elif args.action == "stop":
            await stop_system(manager)
        elif args.action == "restart":
            await restart_system(manager, args)
        elif args.action == "status":
            await show_status(manager)
        elif args.action == "health":
            await show_health(manager)
        
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

async def start_system(manager, args):
    """Start the triumvirate integration system"""
    print("🚀 Starting Triumvirate Integration Layer...")
    
    # Initialize the system
    print("📦 Initializing system components...")
    if not await manager.initialize():
        print("❌ Failed to initialize system")
        sys.exit(1)
    
    # Start the system
    print("⚡ Starting all components...")
    if not await manager.start():
        print("❌ Failed to start system")
        sys.exit(1)
    
    # Show system status
    status = manager.get_status()
    print("\n✅ Triumvirtate Integration Layer started successfully!")
    print(f"🌐 API Server: http://{args.host}:{args.port}")
    print(f"📊 System Status: {status['system_status'].title()}")
    
    if not args.daemon:
        print("\n📈 Component Status:")
        for comp_name, comp_info in status["components"].items():
            status_icon = "🟢" if comp_info["running"] else "🔴"
            print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
        
        print(f"\n🔗 API Endpoints:")
        print(f"  • Health: http://{args.host}:{args.port}/api/v1/monitoring/health")
        print(f"  • Metrics: http://{args.host}:{args.port}/api/v1/monitoring/metrics")
        print(f"  • System Overview: http://{args.host}:{args.port}/api/v1/system/overview")
        
        print(f"\n📝 Logs: {args.log_file}")
        print("\nPress Ctrl+C to stop the system")
        
        # Keep running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutdown requested...")
    else:
        print("🔄 Running as daemon...")

async def stop_system(manager):
    """Stop the triumvirate integration system"""
    print("🛑 Stopping Triumvirate Integration Layer...")
    
    if not await manager.stop():
        print("❌ Failed to stop system properly")
        sys.exit(1)
    
    print("✅ System stopped successfully")

async def restart_system(manager, args):
    """Restart the triumvirate integration system"""
    print("🔄 Restarting Triumvirate Integration Layer...")
    
    if not await manager.restart():
        print("❌ Failed to restart system")
        sys.exit(1)
    
    print("✅ System restarted successfully")
    print(f"🌐 Available at: http://{args.host}:{args.port}")

async def show_status(manager):
    """Show system status"""
    status = manager.get_status()
    
    print("📊 Triumvirate Integration Layer Status")
    print("=" * 50)
    print(f"System Status: {status['system_status'].title()}")
    
    if status['startup_time']:
        from datetime import datetime
        startup_time = datetime.fromisoformat(status['startup_time'])
        uptime_seconds = (datetime.now() - startup_time).total_seconds()
        uptime_hours = int(uptime_seconds // 3600)
        uptime_minutes = int((uptime_seconds % 3600) // 60)
        print(f"Uptime: {uptime_hours}h {uptime_minutes}m")
    
    print("\n🔧 Components:")
    for comp_name, comp_info in status["components"].items():
        status_icon = "🟢" if comp_info["running"] else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
    
    print("\n🌐 Shared Infrastructure:")
    for infra_name, infra_status in status["shared_infrastructure"].items():
        status_icon = "🟢" if infra_status else "🔴"
        print(f"  {status_icon} {infra_name.replace('_', ' ').title()}: {'Running' if infra_status else 'Stopped'}")
    
    print("\n🚀 Revolutionary Capabilities:")
    for cap_name, cap_status in status["revolutionary_capabilities"].items():
        status_icon = "🟢" if cap_status else "🔴"
        print(f"  {status_icon} {cap_name.replace('_', ' ').title()}: {'Active' if cap_status else 'Inactive'}")

async def show_health(manager):
    """Show detailed health information"""
    print("🏥 Triumvirate Integration Layer Health Check")
    print("=" * 50)
    
    # Get system overview
    overview = manager.observability.get_system_overview()
    
    print(f"System Health: {overview['system_health']['status'].title()}")
    print(f"Health Score: {overview['system_health']['score']:.1f}%")
    
    print(f"\n📊 Metrics:")
    print(f"  • Total Components: {overview['total_components_tracked']}")
    print(f"  • Active Alerts: {overview['active_alerts']}")
    print(f"  • Critical Alerts: {overview['critical_alerts']}")
    
    print(f"\n🔍 Component Health:")
    for comp_name in ["agenta", "pranava", "antakhara"]:
        health = await getattr(manager, comp_name).get_health_status()
        status_icon = "🟢" if health["status"] == "healthy" else "🟡" if health["status"] == "degraded" else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {health['status']}")
    
    # Check integration health
    integration_status = manager.get_status()
    if integration_status['system_status'] == 'running':
        print(f"\n✅ Integration Status: HEALTHY")
    else:
        print(f"\n❌ Integration Status: UNHEALTHY")

if __name__ == "__main__":
    # Ensure we can handle KeyboardInterrupt properly
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
        self.logger.info("Initializing triumvirate components")
        
        # Agenta (Hierarchy Manager)
        agenta_config = self.config.agenta_config
        self.agenta = AgentaManager(agenta_config["component_id"])
        self.agenta.load_balancing_enabled = agenta_config["load_balancing_enabled"]
        self.agenta.intelligent_routing = agenta_config["intelligent_routing"]
        await self.agenta.initialize()
        
        # Pranava (Orchestration Router)
        pranava_config = self.config.pranava_config
        self.pranava = PranavaOrchestrator(pranava_config["component_id"])
        self.pranava.health_check_interval = pranava_config["health_check_interval"]
        await self.pranava.initialize()
        
        # Antakhara (Security Enforcer)
        antakhara_config = self.config.antakhara_config
        self.antakhara = AntakharaEnforcer(antakhara_config["component_id"])
        await self.antakhara.initialize()
        
    async def _initialize_revolutionary_capabilities(self) -> None:
        """
Main entry point for Triumvirate Integration Layer

This script provides a command-line interface for managing the triumvirate
integration system, including initialization, startup, shutdown, and monitoring.
"""

import asyncio
import argparse
import sys
import signal
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from triumvirate_manager import TriumvirateIntegrationManager, setup_signal_handlers
from configs.config_manager import ConfigManager

async def main():
    """Main entry point for the triumvirate integration system"""
    parser = argparse.ArgumentParser(description="Triumvirate Integration Layer")
    parser.add_argument(
        "--config", 
        default="configs/integration_config.yaml",
        help="Configuration file path (default: configs/integration_config.yaml)"
    )
    parser.add_argument(
        "--action",
        choices=["start", "stop", "restart", "status", "health"],
        default="start",
        help="Action to perform (default: start)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="API server port (default: 8000)"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="API server host (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Run as daemon process"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    parser.add_argument(
        "--log-file",
        default="logs/triumvirate.log",
        help="Log file path (default: logs/triumvirate.log)"
    )
    
    args = parser.parse_args()
    
    # Create necessary directories
    Path("logs").mkdir(exist_ok=True)
    Path("data").mkdir(exist_ok=True)
    
    try:
        # Create and configure the integration manager
        manager = TriumvirateIntegrationManager(args.config)
        
        # Update API configuration if provided
        config_manager = ConfigManager(args.config)
        config = config_manager.load_config()
        config.api_config["host"] = args.host
        config.api_config["port"] = args.port
        config_manager.save_config(config)
        
        # Setup logging
        if args.debug:
            import logging
            logging.basicConfig(
                level=logging.DEBUG,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                handlers=[
                    logging.FileHandler(args.log_file),
                    logging.StreamHandler(sys.stdout)
                ]
            )
        
        # Setup signal handlers for graceful shutdown
        setup_signal_handlers(manager)
        
        # Perform the requested action
        if args.action == "start":
            await start_system(manager, args)
        elif args.action == "stop":
            await stop_system(manager)
        elif args.action == "restart":
            await restart_system(manager, args)
        elif args.action == "status":
            await show_status(manager)
        elif args.action == "health":
            await show_health(manager)
        
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

async def start_system(manager, args):
    """Start the triumvirate integration system"""
    print("🚀 Starting Triumvirate Integration Layer...")
    
    # Initialize the system
    print("📦 Initializing system components...")
    if not await manager.initialize():
        print("❌ Failed to initialize system")
        sys.exit(1)
    
    # Start the system
    print("⚡ Starting all components...")
    if not await manager.start():
        print("❌ Failed to start system")
        sys.exit(1)
    
    # Show system status
    status = manager.get_status()
    print("\n✅ Triumvirtate Integration Layer started successfully!")
    print(f"🌐 API Server: http://{args.host}:{args.port}")
    print(f"📊 System Status: {status['system_status'].title()}")
    
    if not args.daemon:
        print("\n📈 Component Status:")
        for comp_name, comp_info in status["components"].items():
            status_icon = "🟢" if comp_info["running"] else "🔴"
            print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
        
        print(f"\n🔗 API Endpoints:")
        print(f"  • Health: http://{args.host}:{args.port}/api/v1/monitoring/health")
        print(f"  • Metrics: http://{args.host}:{args.port}/api/v1/monitoring/metrics")
        print(f"  • System Overview: http://{args.host}:{args.port}/api/v1/system/overview")
        
        print(f"\n📝 Logs: {args.log_file}")
        print("\nPress Ctrl+C to stop the system")
        
        # Keep running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutdown requested...")
    else:
        print("🔄 Running as daemon...")

async def stop_system(manager):
    """Stop the triumvirate integration system"""
    print("🛑 Stopping Triumvirate Integration Layer...")
    
    if not await manager.stop():
        print("❌ Failed to stop system properly")
        sys.exit(1)
    
    print("✅ System stopped successfully")

async def restart_system(manager, args):
    """Restart the triumvirate integration system"""
    print("🔄 Restarting Triumvirate Integration Layer...")
    
    if not await manager.restart():
        print("❌ Failed to restart system")
        sys.exit(1)
    
    print("✅ System restarted successfully")
    print(f"🌐 Available at: http://{args.host}:{args.port}")

async def show_status(manager):
    """Show system status"""
    status = manager.get_status()
    
    print("📊 Triumvirate Integration Layer Status")
    print("=" * 50)
    print(f"System Status: {status['system_status'].title()}")
    
    if status['startup_time']:
        from datetime import datetime
        startup_time = datetime.fromisoformat(status['startup_time'])
        uptime_seconds = (datetime.now() - startup_time).total_seconds()
        uptime_hours = int(uptime_seconds // 3600)
        uptime_minutes = int((uptime_seconds % 3600) // 60)
        print(f"Uptime: {uptime_hours}h {uptime_minutes}m")
    
    print("\n🔧 Components:")
    for comp_name, comp_info in status["components"].items():
        status_icon = "🟢" if comp_info["running"] else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
    
    print("\n🌐 Shared Infrastructure:")
    for infra_name, infra_status in status["shared_infrastructure"].items():
        status_icon = "🟢" if infra_status else "🔴"
        print(f"  {status_icon} {infra_name.replace('_', ' ').title()}: {'Running' if infra_status else 'Stopped'}")
    
    print("\n🚀 Revolutionary Capabilities:")
    for cap_name, cap_status in status["revolutionary_capabilities"].items():
        status_icon = "🟢" if cap_status else "🔴"
        print(f"  {status_icon} {cap_name.replace('_', ' ').title()}: {'Active' if cap_status else 'Inactive'}")

async def show_health(manager):
    """Show detailed health information"""
    print("🏥 Triumvirate Integration Layer Health Check")
    print("=" * 50)
    
    # Get system overview
    overview = manager.observability.get_system_overview()
    
    print(f"System Health: {overview['system_health']['status'].title()}")
    print(f"Health Score: {overview['system_health']['score']:.1f}%")
    
    print(f"\n📊 Metrics:")
    print(f"  • Total Components: {overview['total_components_tracked']}")
    print(f"  • Active Alerts: {overview['active_alerts']}")
    print(f"  • Critical Alerts: {overview['critical_alerts']}")
    
    print(f"\n🔍 Component Health:")
    for comp_name in ["agenta", "pranava", "antakhara"]:
        health = await getattr(manager, comp_name).get_health_status()
        status_icon = "🟢" if health["status"] == "healthy" else "🟡" if health["status"] == "degraded" else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {health['status']}")
    
    # Check integration health
    integration_status = manager.get_status()
    if integration_status['system_status'] == 'running':
        print(f"\n✅ Integration Status: HEALTHY")
    else:
        print(f"\n❌ Integration Status: UNHEALTHY")

if __name__ == "__main__":
    # Ensure we can handle KeyboardInterrupt properly
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)Initialize revolutionary integration capabilities"""
Main entry point for Triumvirate Integration Layer

This script provides a command-line interface for managing the triumvirate
integration system, including initialization, startup, shutdown, and monitoring.
"""

import asyncio
import argparse
import sys
import signal
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from triumvirate_manager import TriumvirateIntegrationManager, setup_signal_handlers
from configs.config_manager import ConfigManager

async def main():
    """Main entry point for the triumvirate integration system"""
    parser = argparse.ArgumentParser(description="Triumvirate Integration Layer")
    parser.add_argument(
        "--config", 
        default="configs/integration_config.yaml",
        help="Configuration file path (default: configs/integration_config.yaml)"
    )
    parser.add_argument(
        "--action",
        choices=["start", "stop", "restart", "status", "health"],
        default="start",
        help="Action to perform (default: start)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="API server port (default: 8000)"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="API server host (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Run as daemon process"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    parser.add_argument(
        "--log-file",
        default="logs/triumvirate.log",
        help="Log file path (default: logs/triumvirate.log)"
    )
    
    args = parser.parse_args()
    
    # Create necessary directories
    Path("logs").mkdir(exist_ok=True)
    Path("data").mkdir(exist_ok=True)
    
    try:
        # Create and configure the integration manager
        manager = TriumvirateIntegrationManager(args.config)
        
        # Update API configuration if provided
        config_manager = ConfigManager(args.config)
        config = config_manager.load_config()
        config.api_config["host"] = args.host
        config.api_config["port"] = args.port
        config_manager.save_config(config)
        
        # Setup logging
        if args.debug:
            import logging
            logging.basicConfig(
                level=logging.DEBUG,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                handlers=[
                    logging.FileHandler(args.log_file),
                    logging.StreamHandler(sys.stdout)
                ]
            )
        
        # Setup signal handlers for graceful shutdown
        setup_signal_handlers(manager)
        
        # Perform the requested action
        if args.action == "start":
            await start_system(manager, args)
        elif args.action == "stop":
            await stop_system(manager)
        elif args.action == "restart":
            await restart_system(manager, args)
        elif args.action == "status":
            await show_status(manager)
        elif args.action == "health":
            await show_health(manager)
        
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

async def start_system(manager, args):
    """Start the triumvirate integration system"""
    print("🚀 Starting Triumvirate Integration Layer...")
    
    # Initialize the system
    print("📦 Initializing system components...")
    if not await manager.initialize():
        print("❌ Failed to initialize system")
        sys.exit(1)
    
    # Start the system
    print("⚡ Starting all components...")
    if not await manager.start():
        print("❌ Failed to start system")
        sys.exit(1)
    
    # Show system status
    status = manager.get_status()
    print("\n✅ Triumvirtate Integration Layer started successfully!")
    print(f"🌐 API Server: http://{args.host}:{args.port}")
    print(f"📊 System Status: {status['system_status'].title()}")
    
    if not args.daemon:
        print("\n📈 Component Status:")
        for comp_name, comp_info in status["components"].items():
            status_icon = "🟢" if comp_info["running"] else "🔴"
            print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
        
        print(f"\n🔗 API Endpoints:")
        print(f"  • Health: http://{args.host}:{args.port}/api/v1/monitoring/health")
        print(f"  • Metrics: http://{args.host}:{args.port}/api/v1/monitoring/metrics")
        print(f"  • System Overview: http://{args.host}:{args.port}/api/v1/system/overview")
        
        print(f"\n📝 Logs: {args.log_file}")
        print("\nPress Ctrl+C to stop the system")
        
        # Keep running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutdown requested...")
    else:
        print("🔄 Running as daemon...")

async def stop_system(manager):
    """Stop the triumvirate integration system"""
    print("🛑 Stopping Triumvirate Integration Layer...")
    
    if not await manager.stop():
        print("❌ Failed to stop system properly")
        sys.exit(1)
    
    print("✅ System stopped successfully")

async def restart_system(manager, args):
    """Restart the triumvirate integration system"""
    print("🔄 Restarting Triumvirate Integration Layer...")
    
    if not await manager.restart():
        print("❌ Failed to restart system")
        sys.exit(1)
    
    print("✅ System restarted successfully")
    print(f"🌐 Available at: http://{args.host}:{args.port}")

async def show_status(manager):
    """Show system status"""
    status = manager.get_status()
    
    print("📊 Triumvirate Integration Layer Status")
    print("=" * 50)
    print(f"System Status: {status['system_status'].title()}")
    
    if status['startup_time']:
        from datetime import datetime
        startup_time = datetime.fromisoformat(status['startup_time'])
        uptime_seconds = (datetime.now() - startup_time).total_seconds()
        uptime_hours = int(uptime_seconds // 3600)
        uptime_minutes = int((uptime_seconds % 3600) // 60)
        print(f"Uptime: {uptime_hours}h {uptime_minutes}m")
    
    print("\n🔧 Components:")
    for comp_name, comp_info in status["components"].items():
        status_icon = "🟢" if comp_info["running"] else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
    
    print("\n🌐 Shared Infrastructure:")
    for infra_name, infra_status in status["shared_infrastructure"].items():
        status_icon = "🟢" if infra_status else "🔴"
        print(f"  {status_icon} {infra_name.replace('_', ' ').title()}: {'Running' if infra_status else 'Stopped'}")
    
    print("\n🚀 Revolutionary Capabilities:")
    for cap_name, cap_status in status["revolutionary_capabilities"].items():
        status_icon = "🟢" if cap_status else "🔴"
        print(f"  {status_icon} {cap_name.replace('_', ' ').title()}: {'Active' if cap_status else 'Inactive'}")

async def show_health(manager):
    """Show detailed health information"""
    print("🏥 Triumvirate Integration Layer Health Check")
    print("=" * 50)
    
    # Get system overview
    overview = manager.observability.get_system_overview()
    
    print(f"System Health: {overview['system_health']['status'].title()}")
    print(f"Health Score: {overview['system_health']['score']:.1f}%")
    
    print(f"\n📊 Metrics:")
    print(f"  • Total Components: {overview['total_components_tracked']}")
    print(f"  • Active Alerts: {overview['active_alerts']}")
    print(f"  • Critical Alerts: {overview['critical_alerts']}")
    
    print(f"\n🔍 Component Health:")
    for comp_name in ["agenta", "pranava", "antakhara"]:
        health = await getattr(manager, comp_name).get_health_status()
        status_icon = "🟢" if health["status"] == "healthy" else "🟡" if health["status"] == "degraded" else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {health['status']}")
    
    # Check integration health
    integration_status = manager.get_status()
    if integration_status['system_status'] == 'running':
        print(f"\n✅ Integration Status: HEALTHY")
    else:
        print(f"\n❌ Integration Status: UNHEALTHY")

if __name__ == "__main__":
    # Ensure we can handle KeyboardInterrupt properly
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
        self.logger.info("Initializing revolutionary capabilities")
        
        # Intelligent Cross-Component Coordinator
        from .revolutionary.intelligent_coordinator import IntelligentCoordinator
        self.intelligent_coordinator = IntelligentCoordinator(self.agenta, self.pranava, self.antakhara)
        await self.intelligent_coordinator.initialize()
        
        # Adaptive Scaling and Load Balancer
        from .revolutionary.adaptive_optimizer import AdaptiveOptimizer
        self.adaptive_optimizer = AdaptiveOptimizer(self.service_discovery, self.observability)
        await self.adaptive_optimizer.initialize()
        
        # Self-Healing and Resilience System
        from .revolutionary.self_healer import SelfHealer
        self.self_healer = SelfHealer(self, self.service_discovery, self.observability)
        await self.self_healer.initialize()
        
        # Performance Optimization Engine
        from .revolutionary.performance_optimizer import PerformanceOptimizer
        self.performance_optimizer = PerformanceOptimizer(self.observability, self.service_discovery)
        await self.performance_optimizer.initialize()
        
    async def _setup_inter_component_communication(self) -> None:
        """
Main entry point for Triumvirate Integration Layer

This script provides a command-line interface for managing the triumvirate
integration system, including initialization, startup, shutdown, and monitoring.
"""

import asyncio
import argparse
import sys
import signal
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from triumvirate_manager import TriumvirateIntegrationManager, setup_signal_handlers
from configs.config_manager import ConfigManager

async def main():
    """Main entry point for the triumvirate integration system"""
    parser = argparse.ArgumentParser(description="Triumvirate Integration Layer")
    parser.add_argument(
        "--config", 
        default="configs/integration_config.yaml",
        help="Configuration file path (default: configs/integration_config.yaml)"
    )
    parser.add_argument(
        "--action",
        choices=["start", "stop", "restart", "status", "health"],
        default="start",
        help="Action to perform (default: start)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="API server port (default: 8000)"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="API server host (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Run as daemon process"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    parser.add_argument(
        "--log-file",
        default="logs/triumvirate.log",
        help="Log file path (default: logs/triumvirate.log)"
    )
    
    args = parser.parse_args()
    
    # Create necessary directories
    Path("logs").mkdir(exist_ok=True)
    Path("data").mkdir(exist_ok=True)
    
    try:
        # Create and configure the integration manager
        manager = TriumvirateIntegrationManager(args.config)
        
        # Update API configuration if provided
        config_manager = ConfigManager(args.config)
        config = config_manager.load_config()
        config.api_config["host"] = args.host
        config.api_config["port"] = args.port
        config_manager.save_config(config)
        
        # Setup logging
        if args.debug:
            import logging
            logging.basicConfig(
                level=logging.DEBUG,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                handlers=[
                    logging.FileHandler(args.log_file),
                    logging.StreamHandler(sys.stdout)
                ]
            )
        
        # Setup signal handlers for graceful shutdown
        setup_signal_handlers(manager)
        
        # Perform the requested action
        if args.action == "start":
            await start_system(manager, args)
        elif args.action == "stop":
            await stop_system(manager)
        elif args.action == "restart":
            await restart_system(manager, args)
        elif args.action == "status":
            await show_status(manager)
        elif args.action == "health":
            await show_health(manager)
        
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

async def start_system(manager, args):
    """Start the triumvirate integration system"""
    print("🚀 Starting Triumvirate Integration Layer...")
    
    # Initialize the system
    print("📦 Initializing system components...")
    if not await manager.initialize():
        print("❌ Failed to initialize system")
        sys.exit(1)
    
    # Start the system
    print("⚡ Starting all components...")
    if not await manager.start():
        print("❌ Failed to start system")
        sys.exit(1)
    
    # Show system status
    status = manager.get_status()
    print("\n✅ Triumvirtate Integration Layer started successfully!")
    print(f"🌐 API Server: http://{args.host}:{args.port}")
    print(f"📊 System Status: {status['system_status'].title()}")
    
    if not args.daemon:
        print("\n📈 Component Status:")
        for comp_name, comp_info in status["components"].items():
            status_icon = "🟢" if comp_info["running"] else "🔴"
            print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
        
        print(f"\n🔗 API Endpoints:")
        print(f"  • Health: http://{args.host}:{args.port}/api/v1/monitoring/health")
        print(f"  • Metrics: http://{args.host}:{args.port}/api/v1/monitoring/metrics")
        print(f"  • System Overview: http://{args.host}:{args.port}/api/v1/system/overview")
        
        print(f"\n📝 Logs: {args.log_file}")
        print("\nPress Ctrl+C to stop the system")
        
        # Keep running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutdown requested...")
    else:
        print("🔄 Running as daemon...")

async def stop_system(manager):
    """Stop the triumvirate integration system"""
    print("🛑 Stopping Triumvirate Integration Layer...")
    
    if not await manager.stop():
        print("❌ Failed to stop system properly")
        sys.exit(1)
    
    print("✅ System stopped successfully")

async def restart_system(manager, args):
    """Restart the triumvirate integration system"""
    print("🔄 Restarting Triumvirate Integration Layer...")
    
    if not await manager.restart():
        print("❌ Failed to restart system")
        sys.exit(1)
    
    print("✅ System restarted successfully")
    print(f"🌐 Available at: http://{args.host}:{args.port}")

async def show_status(manager):
    """Show system status"""
    status = manager.get_status()
    
    print("📊 Triumvirate Integration Layer Status")
    print("=" * 50)
    print(f"System Status: {status['system_status'].title()}")
    
    if status['startup_time']:
        from datetime import datetime
        startup_time = datetime.fromisoformat(status['startup_time'])
        uptime_seconds = (datetime.now() - startup_time).total_seconds()
        uptime_hours = int(uptime_seconds // 3600)
        uptime_minutes = int((uptime_seconds % 3600) // 60)
        print(f"Uptime: {uptime_hours}h {uptime_minutes}m")
    
    print("\n🔧 Components:")
    for comp_name, comp_info in status["components"].items():
        status_icon = "🟢" if comp_info["running"] else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
    
    print("\n🌐 Shared Infrastructure:")
    for infra_name, infra_status in status["shared_infrastructure"].items():
        status_icon = "🟢" if infra_status else "🔴"
        print(f"  {status_icon} {infra_name.replace('_', ' ').title()}: {'Running' if infra_status else 'Stopped'}")
    
    print("\n🚀 Revolutionary Capabilities:")
    for cap_name, cap_status in status["revolutionary_capabilities"].items():
        status_icon = "🟢" if cap_status else "🔴"
        print(f"  {status_icon} {cap_name.replace('_', ' ').title()}: {'Active' if cap_status else 'Inactive'}")

async def show_health(manager):
    """Show detailed health information"""
    print("🏥 Triumvirate Integration Layer Health Check")
    print("=" * 50)
    
    # Get system overview
    overview = manager.observability.get_system_overview()
    
    print(f"System Health: {overview['system_health']['status'].title()}")
    print(f"Health Score: {overview['system_health']['score']:.1f}%")
    
    print(f"\n📊 Metrics:")
    print(f"  • Total Components: {overview['total_components_tracked']}")
    print(f"  • Active Alerts: {overview['active_alerts']}")
    print(f"  • Critical Alerts: {overview['critical_alerts']}")
    
    print(f"\n🔍 Component Health:")
    for comp_name in ["agenta", "pranava", "antakhara"]:
        health = await getattr(manager, comp_name).get_health_status()
        status_icon = "🟢" if health["status"] == "healthy" else "🟡" if health["status"] == "degraded" else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {health['status']}")
    
    # Check integration health
    integration_status = manager.get_status()
    if integration_status['system_status'] == 'running':
        print(f"\n✅ Integration Status: HEALTHY")
    else:
        print(f"\n❌ Integration Status: UNHEALTHY")

if __name__ == "__main__":
    # Ensure we can handle KeyboardInterrupt properly
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)Setup communication between all components"""
Main entry point for Triumvirate Integration Layer

This script provides a command-line interface for managing the triumvirate
integration system, including initialization, startup, shutdown, and monitoring.
"""

import asyncio
import argparse
import sys
import signal
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from triumvirate_manager import TriumvirateIntegrationManager, setup_signal_handlers
from configs.config_manager import ConfigManager

async def main():
    """Main entry point for the triumvirate integration system"""
    parser = argparse.ArgumentParser(description="Triumvirate Integration Layer")
    parser.add_argument(
        "--config", 
        default="configs/integration_config.yaml",
        help="Configuration file path (default: configs/integration_config.yaml)"
    )
    parser.add_argument(
        "--action",
        choices=["start", "stop", "restart", "status", "health"],
        default="start",
        help="Action to perform (default: start)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="API server port (default: 8000)"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="API server host (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Run as daemon process"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    parser.add_argument(
        "--log-file",
        default="logs/triumvirate.log",
        help="Log file path (default: logs/triumvirate.log)"
    )
    
    args = parser.parse_args()
    
    # Create necessary directories
    Path("logs").mkdir(exist_ok=True)
    Path("data").mkdir(exist_ok=True)
    
    try:
        # Create and configure the integration manager
        manager = TriumvirateIntegrationManager(args.config)
        
        # Update API configuration if provided
        config_manager = ConfigManager(args.config)
        config = config_manager.load_config()
        config.api_config["host"] = args.host
        config.api_config["port"] = args.port
        config_manager.save_config(config)
        
        # Setup logging
        if args.debug:
            import logging
            logging.basicConfig(
                level=logging.DEBUG,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                handlers=[
                    logging.FileHandler(args.log_file),
                    logging.StreamHandler(sys.stdout)
                ]
            )
        
        # Setup signal handlers for graceful shutdown
        setup_signal_handlers(manager)
        
        # Perform the requested action
        if args.action == "start":
            await start_system(manager, args)
        elif args.action == "stop":
            await stop_system(manager)
        elif args.action == "restart":
            await restart_system(manager, args)
        elif args.action == "status":
            await show_status(manager)
        elif args.action == "health":
            await show_health(manager)
        
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

async def start_system(manager, args):
    """Start the triumvirate integration system"""
    print("🚀 Starting Triumvirate Integration Layer...")
    
    # Initialize the system
    print("📦 Initializing system components...")
    if not await manager.initialize():
        print("❌ Failed to initialize system")
        sys.exit(1)
    
    # Start the system
    print("⚡ Starting all components...")
    if not await manager.start():
        print("❌ Failed to start system")
        sys.exit(1)
    
    # Show system status
    status = manager.get_status()
    print("\n✅ Triumvirtate Integration Layer started successfully!")
    print(f"🌐 API Server: http://{args.host}:{args.port}")
    print(f"📊 System Status: {status['system_status'].title()}")
    
    if not args.daemon:
        print("\n📈 Component Status:")
        for comp_name, comp_info in status["components"].items():
            status_icon = "🟢" if comp_info["running"] else "🔴"
            print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
        
        print(f"\n🔗 API Endpoints:")
        print(f"  • Health: http://{args.host}:{args.port}/api/v1/monitoring/health")
        print(f"  • Metrics: http://{args.host}:{args.port}/api/v1/monitoring/metrics")
        print(f"  • System Overview: http://{args.host}:{args.port}/api/v1/system/overview")
        
        print(f"\n📝 Logs: {args.log_file}")
        print("\nPress Ctrl+C to stop the system")
        
        # Keep running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutdown requested...")
    else:
        print("🔄 Running as daemon...")

async def stop_system(manager):
    """Stop the triumvirate integration system"""
    print("🛑 Stopping Triumvirate Integration Layer...")
    
    if not await manager.stop():
        print("❌ Failed to stop system properly")
        sys.exit(1)
    
    print("✅ System stopped successfully")

async def restart_system(manager, args):
    """Restart the triumvirate integration system"""
    print("🔄 Restarting Triumvirate Integration Layer...")
    
    if not await manager.restart():
        print("❌ Failed to restart system")
        sys.exit(1)
    
    print("✅ System restarted successfully")
    print(f"🌐 Available at: http://{args.host}:{args.port}")

async def show_status(manager):
    """Show system status"""
    status = manager.get_status()
    
    print("📊 Triumvirate Integration Layer Status")
    print("=" * 50)
    print(f"System Status: {status['system_status'].title()}")
    
    if status['startup_time']:
        from datetime import datetime
        startup_time = datetime.fromisoformat(status['startup_time'])
        uptime_seconds = (datetime.now() - startup_time).total_seconds()
        uptime_hours = int(uptime_seconds // 3600)
        uptime_minutes = int((uptime_seconds % 3600) // 60)
        print(f"Uptime: {uptime_hours}h {uptime_minutes}m")
    
    print("\n🔧 Components:")
    for comp_name, comp_info in status["components"].items():
        status_icon = "🟢" if comp_info["running"] else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
    
    print("\n🌐 Shared Infrastructure:")
    for infra_name, infra_status in status["shared_infrastructure"].items():
        status_icon = "🟢" if infra_status else "🔴"
        print(f"  {status_icon} {infra_name.replace('_', ' ').title()}: {'Running' if infra_status else 'Stopped'}")
    
    print("\n🚀 Revolutionary Capabilities:")
    for cap_name, cap_status in status["revolutionary_capabilities"].items():
        status_icon = "🟢" if cap_status else "🔴"
        print(f"  {status_icon} {cap_name.replace('_', ' ').title()}: {'Active' if cap_status else 'Inactive'}")

async def show_health(manager):
    """Show detailed health information"""
    print("🏥 Triumvirate Integration Layer Health Check")
    print("=" * 50)
    
    # Get system overview
    overview = manager.observability.get_system_overview()
    
    print(f"System Health: {overview['system_health']['status'].title()}")
    print(f"Health Score: {overview['system_health']['score']:.1f}%")
    
    print(f"\n📊 Metrics:")
    print(f"  • Total Components: {overview['total_components_tracked']}")
    print(f"  • Active Alerts: {overview['active_alerts']}")
    print(f"  • Critical Alerts: {overview['critical_alerts']}")
    
    print(f"\n🔍 Component Health:")
    for comp_name in ["agenta", "pranava", "antakhara"]:
        health = await getattr(manager, comp_name).get_health_status()
        status_icon = "🟢" if health["status"] == "healthy" else "🟡" if health["status"] == "degraded" else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {health['status']}")
    
    # Check integration health
    integration_status = manager.get_status()
    if integration_status['system_status'] == 'running':
        print(f"\n✅ Integration Status: HEALTHY")
    else:
        print(f"\n❌ Integration Status: UNHEALTHY")

if __name__ == "__main__":
    # Ensure we can handle KeyboardInterrupt properly
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
        self.logger.info("Setting up inter-component communication")
        
        # Register components in message router
        self.message_router.register_component(
            ComponentType.AGENTA, 
            self.agenta.component_id, 
            f"agenta://{self.agenta.component_id}",
            ["hierarchy_management", "intelligent_routing"]
        )
        
        self.message_router.register_component(
            ComponentType.PRANAVA,
            self.pranava.component_id,
            f"pranava://{self.pranava.component_id}",
            ["orchestration", "workflow_management", "load_balancing"]
        )
        
        self.message_router.register_component(
            ComponentType.ANTAKHARA,
            self.antakhara.component_id,
            f"antakhara://{self.antakhara.component_id}",
            ["security", "policy_enforcement", "compliance"]
        )
        
        # Setup cross-component message routes
        self.message_router.add_route("hierarchy.routing_request", self.agenta.receive_message)
        self.message_router.add_route("orchestration.workflow_request", self.pranava.receive_message)
        self.message_router.add_route("security.policy_request", self.antakhara.receive_message)
        
        # Add metric handlers
        self.observability.add_metric_handler(self._handle_metric)
        self.observability.add_alert_handler(self._handle_alert)
        
    async def _initialize_api_layer(self) -> None:
        """
Main entry point for Triumvirate Integration Layer

This script provides a command-line interface for managing the triumvirate
integration system, including initialization, startup, shutdown, and monitoring.
"""

import asyncio
import argparse
import sys
import signal
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from triumvirate_manager import TriumvirateIntegrationManager, setup_signal_handlers
from configs.config_manager import ConfigManager

async def main():
    """Main entry point for the triumvirate integration system"""
    parser = argparse.ArgumentParser(description="Triumvirate Integration Layer")
    parser.add_argument(
        "--config", 
        default="configs/integration_config.yaml",
        help="Configuration file path (default: configs/integration_config.yaml)"
    )
    parser.add_argument(
        "--action",
        choices=["start", "stop", "restart", "status", "health"],
        default="start",
        help="Action to perform (default: start)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="API server port (default: 8000)"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="API server host (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Run as daemon process"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    parser.add_argument(
        "--log-file",
        default="logs/triumvirate.log",
        help="Log file path (default: logs/triumvirate.log)"
    )
    
    args = parser.parse_args()
    
    # Create necessary directories
    Path("logs").mkdir(exist_ok=True)
    Path("data").mkdir(exist_ok=True)
    
    try:
        # Create and configure the integration manager
        manager = TriumvirateIntegrationManager(args.config)
        
        # Update API configuration if provided
        config_manager = ConfigManager(args.config)
        config = config_manager.load_config()
        config.api_config["host"] = args.host
        config.api_config["port"] = args.port
        config_manager.save_config(config)
        
        # Setup logging
        if args.debug:
            import logging
            logging.basicConfig(
                level=logging.DEBUG,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                handlers=[
                    logging.FileHandler(args.log_file),
                    logging.StreamHandler(sys.stdout)
                ]
            )
        
        # Setup signal handlers for graceful shutdown
        setup_signal_handlers(manager)
        
        # Perform the requested action
        if args.action == "start":
            await start_system(manager, args)
        elif args.action == "stop":
            await stop_system(manager)
        elif args.action == "restart":
            await restart_system(manager, args)
        elif args.action == "status":
            await show_status(manager)
        elif args.action == "health":
            await show_health(manager)
        
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

async def start_system(manager, args):
    """Start the triumvirate integration system"""
    print("🚀 Starting Triumvirate Integration Layer...")
    
    # Initialize the system
    print("📦 Initializing system components...")
    if not await manager.initialize():
        print("❌ Failed to initialize system")
        sys.exit(1)
    
    # Start the system
    print("⚡ Starting all components...")
    if not await manager.start():
        print("❌ Failed to start system")
        sys.exit(1)
    
    # Show system status
    status = manager.get_status()
    print("\n✅ Triumvirtate Integration Layer started successfully!")
    print(f"🌐 API Server: http://{args.host}:{args.port}")
    print(f"📊 System Status: {status['system_status'].title()}")
    
    if not args.daemon:
        print("\n📈 Component Status:")
        for comp_name, comp_info in status["components"].items():
            status_icon = "🟢" if comp_info["running"] else "🔴"
            print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
        
        print(f"\n🔗 API Endpoints:")
        print(f"  • Health: http://{args.host}:{args.port}/api/v1/monitoring/health")
        print(f"  • Metrics: http://{args.host}:{args.port}/api/v1/monitoring/metrics")
        print(f"  • System Overview: http://{args.host}:{args.port}/api/v1/system/overview")
        
        print(f"\n📝 Logs: {args.log_file}")
        print("\nPress Ctrl+C to stop the system")
        
        # Keep running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutdown requested...")
    else:
        print("🔄 Running as daemon...")

async def stop_system(manager):
    """Stop the triumvirate integration system"""
    print("🛑 Stopping Triumvirate Integration Layer...")
    
    if not await manager.stop():
        print("❌ Failed to stop system properly")
        sys.exit(1)
    
    print("✅ System stopped successfully")

async def restart_system(manager, args):
    """Restart the triumvirate integration system"""
    print("🔄 Restarting Triumvirate Integration Layer...")
    
    if not await manager.restart():
        print("❌ Failed to restart system")
        sys.exit(1)
    
    print("✅ System restarted successfully")
    print(f"🌐 Available at: http://{args.host}:{args.port}")

async def show_status(manager):
    """Show system status"""
    status = manager.get_status()
    
    print("📊 Triumvirate Integration Layer Status")
    print("=" * 50)
    print(f"System Status: {status['system_status'].title()}")
    
    if status['startup_time']:
        from datetime import datetime
        startup_time = datetime.fromisoformat(status['startup_time'])
        uptime_seconds = (datetime.now() - startup_time).total_seconds()
        uptime_hours = int(uptime_seconds // 3600)
        uptime_minutes = int((uptime_seconds % 3600) // 60)
        print(f"Uptime: {uptime_hours}h {uptime_minutes}m")
    
    print("\n🔧 Components:")
    for comp_name, comp_info in status["components"].items():
        status_icon = "🟢" if comp_info["running"] else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
    
    print("\n🌐 Shared Infrastructure:")
    for infra_name, infra_status in status["shared_infrastructure"].items():
        status_icon = "🟢" if infra_status else "🔴"
        print(f"  {status_icon} {infra_name.replace('_', ' ').title()}: {'Running' if infra_status else 'Stopped'}")
    
    print("\n🚀 Revolutionary Capabilities:")
    for cap_name, cap_status in status["revolutionary_capabilities"].items():
        status_icon = "🟢" if cap_status else "🔴"
        print(f"  {status_icon} {cap_name.replace('_', ' ').title()}: {'Active' if cap_status else 'Inactive'}")

async def show_health(manager):
    """Show detailed health information"""
    print("🏥 Triumvirate Integration Layer Health Check")
    print("=" * 50)
    
    # Get system overview
    overview = manager.observability.get_system_overview()
    
    print(f"System Health: {overview['system_health']['status'].title()}")
    print(f"Health Score: {overview['system_health']['score']:.1f}%")
    
    print(f"\n📊 Metrics:")
    print(f"  • Total Components: {overview['total_components_tracked']}")
    print(f"  • Active Alerts: {overview['active_alerts']}")
    print(f"  • Critical Alerts: {overview['critical_alerts']}")
    
    print(f"\n🔍 Component Health:")
    for comp_name in ["agenta", "pranava", "antakhara"]:
        health = await getattr(manager, comp_name).get_health_status()
        status_icon = "🟢" if health["status"] == "healthy" else "🟡" if health["status"] == "degraded" else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {health['status']}")
    
    # Check integration health
    integration_status = manager.get_status()
    if integration_status['system_status'] == 'running':
        print(f"\n✅ Integration Status: HEALTHY")
    else:
        print(f"\n❌ Integration Status: UNHEALTHY")

if __name__ == "__main__":
    # Ensure we can handle KeyboardInterrupt properly
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)Initialize API layer"""
Main entry point for Triumvirate Integration Layer

This script provides a command-line interface for managing the triumvirate
integration system, including initialization, startup, shutdown, and monitoring.
"""

import asyncio
import argparse
import sys
import signal
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from triumvirate_manager import TriumvirateIntegrationManager, setup_signal_handlers
from configs.config_manager import ConfigManager

async def main():
    """Main entry point for the triumvirate integration system"""
    parser = argparse.ArgumentParser(description="Triumvirate Integration Layer")
    parser.add_argument(
        "--config", 
        default="configs/integration_config.yaml",
        help="Configuration file path (default: configs/integration_config.yaml)"
    )
    parser.add_argument(
        "--action",
        choices=["start", "stop", "restart", "status", "health"],
        default="start",
        help="Action to perform (default: start)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="API server port (default: 8000)"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="API server host (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Run as daemon process"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    parser.add_argument(
        "--log-file",
        default="logs/triumvirate.log",
        help="Log file path (default: logs/triumvirate.log)"
    )
    
    args = parser.parse_args()
    
    # Create necessary directories
    Path("logs").mkdir(exist_ok=True)
    Path("data").mkdir(exist_ok=True)
    
    try:
        # Create and configure the integration manager
        manager = TriumvirateIntegrationManager(args.config)
        
        # Update API configuration if provided
        config_manager = ConfigManager(args.config)
        config = config_manager.load_config()
        config.api_config["host"] = args.host
        config.api_config["port"] = args.port
        config_manager.save_config(config)
        
        # Setup logging
        if args.debug:
            import logging
            logging.basicConfig(
                level=logging.DEBUG,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                handlers=[
                    logging.FileHandler(args.log_file),
                    logging.StreamHandler(sys.stdout)
                ]
            )
        
        # Setup signal handlers for graceful shutdown
        setup_signal_handlers(manager)
        
        # Perform the requested action
        if args.action == "start":
            await start_system(manager, args)
        elif args.action == "stop":
            await stop_system(manager)
        elif args.action == "restart":
            await restart_system(manager, args)
        elif args.action == "status":
            await show_status(manager)
        elif args.action == "health":
            await show_health(manager)
        
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

async def start_system(manager, args):
    """Start the triumvirate integration system"""
    print("🚀 Starting Triumvirate Integration Layer...")
    
    # Initialize the system
    print("📦 Initializing system components...")
    if not await manager.initialize():
        print("❌ Failed to initialize system")
        sys.exit(1)
    
    # Start the system
    print("⚡ Starting all components...")
    if not await manager.start():
        print("❌ Failed to start system")
        sys.exit(1)
    
    # Show system status
    status = manager.get_status()
    print("\n✅ Triumvirtate Integration Layer started successfully!")
    print(f"🌐 API Server: http://{args.host}:{args.port}")
    print(f"📊 System Status: {status['system_status'].title()}")
    
    if not args.daemon:
        print("\n📈 Component Status:")
        for comp_name, comp_info in status["components"].items():
            status_icon = "🟢" if comp_info["running"] else "🔴"
            print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
        
        print(f"\n🔗 API Endpoints:")
        print(f"  • Health: http://{args.host}:{args.port}/api/v1/monitoring/health")
        print(f"  • Metrics: http://{args.host}:{args.port}/api/v1/monitoring/metrics")
        print(f"  • System Overview: http://{args.host}:{args.port}/api/v1/system/overview")
        
        print(f"\n📝 Logs: {args.log_file}")
        print("\nPress Ctrl+C to stop the system")
        
        # Keep running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutdown requested...")
    else:
        print("🔄 Running as daemon...")

async def stop_system(manager):
    """Stop the triumvirate integration system"""
    print("🛑 Stopping Triumvirate Integration Layer...")
    
    if not await manager.stop():
        print("❌ Failed to stop system properly")
        sys.exit(1)
    
    print("✅ System stopped successfully")

async def restart_system(manager, args):
    """Restart the triumvirate integration system"""
    print("🔄 Restarting Triumvirate Integration Layer...")
    
    if not await manager.restart():
        print("❌ Failed to restart system")
        sys.exit(1)
    
    print("✅ System restarted successfully")
    print(f"🌐 Available at: http://{args.host}:{args.port}")

async def show_status(manager):
    """Show system status"""
    status = manager.get_status()
    
    print("📊 Triumvirate Integration Layer Status")
    print("=" * 50)
    print(f"System Status: {status['system_status'].title()}")
    
    if status['startup_time']:
        from datetime import datetime
        startup_time = datetime.fromisoformat(status['startup_time'])
        uptime_seconds = (datetime.now() - startup_time).total_seconds()
        uptime_hours = int(uptime_seconds // 3600)
        uptime_minutes = int((uptime_seconds % 3600) // 60)
        print(f"Uptime: {uptime_hours}h {uptime_minutes}m")
    
    print("\n🔧 Components:")
    for comp_name, comp_info in status["components"].items():
        status_icon = "🟢" if comp_info["running"] else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
    
    print("\n🌐 Shared Infrastructure:")
    for infra_name, infra_status in status["shared_infrastructure"].items():
        status_icon = "🟢" if infra_status else "🔴"
        print(f"  {status_icon} {infra_name.replace('_', ' ').title()}: {'Running' if infra_status else 'Stopped'}")
    
    print("\n🚀 Revolutionary Capabilities:")
    for cap_name, cap_status in status["revolutionary_capabilities"].items():
        status_icon = "🟢" if cap_status else "🔴"
        print(f"  {status_icon} {cap_name.replace('_', ' ').title()}: {'Active' if cap_status else 'Inactive'}")

async def show_health(manager):
    """Show detailed health information"""
    print("🏥 Triumvirate Integration Layer Health Check")
    print("=" * 50)
    
    # Get system overview
    overview = manager.observability.get_system_overview()
    
    print(f"System Health: {overview['system_health']['status'].title()}")
    print(f"Health Score: {overview['system_health']['score']:.1f}%")
    
    print(f"\n📊 Metrics:")
    print(f"  • Total Components: {overview['total_components_tracked']}")
    print(f"  • Active Alerts: {overview['active_alerts']}")
    print(f"  • Critical Alerts: {overview['critical_alerts']}")
    
    print(f"\n🔍 Component Health:")
    for comp_name in ["agenta", "pranava", "antakhara"]:
        health = await getattr(manager, comp_name).get_health_status()
        status_icon = "🟢" if health["status"] == "healthy" else "🟡" if health["status"] == "degraded" else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {health['status']}")
    
    # Check integration health
    integration_status = manager.get_status()
    if integration_status['system_status'] == 'running':
        print(f"\n✅ Integration Status: HEALTHY")
    else:
        print(f"\n❌ Integration Status: UNHEALTHY")

if __name__ == "__main__":
    # Ensure we can handle KeyboardInterrupt properly
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
        self.logger.info("Initializing API layer")
        
        self.api_server = TriumvirateAPI(
            self.agenta, self.pranava, self.antakhara,
            self.service_discovery, self.observability
        )
        
    async def _setup_health_monitoring(self) -> None:
        """
Main entry point for Triumvirate Integration Layer

This script provides a command-line interface for managing the triumvirate
integration system, including initialization, startup, shutdown, and monitoring.
"""

import asyncio
import argparse
import sys
import signal
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from triumvirate_manager import TriumvirateIntegrationManager, setup_signal_handlers
from configs.config_manager import ConfigManager

async def main():
    """Main entry point for the triumvirate integration system"""
    parser = argparse.ArgumentParser(description="Triumvirate Integration Layer")
    parser.add_argument(
        "--config", 
        default="configs/integration_config.yaml",
        help="Configuration file path (default: configs/integration_config.yaml)"
    )
    parser.add_argument(
        "--action",
        choices=["start", "stop", "restart", "status", "health"],
        default="start",
        help="Action to perform (default: start)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="API server port (default: 8000)"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="API server host (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Run as daemon process"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    parser.add_argument(
        "--log-file",
        default="logs/triumvirate.log",
        help="Log file path (default: logs/triumvirate.log)"
    )
    
    args = parser.parse_args()
    
    # Create necessary directories
    Path("logs").mkdir(exist_ok=True)
    Path("data").mkdir(exist_ok=True)
    
    try:
        # Create and configure the integration manager
        manager = TriumvirateIntegrationManager(args.config)
        
        # Update API configuration if provided
        config_manager = ConfigManager(args.config)
        config = config_manager.load_config()
        config.api_config["host"] = args.host
        config.api_config["port"] = args.port
        config_manager.save_config(config)
        
        # Setup logging
        if args.debug:
            import logging
            logging.basicConfig(
                level=logging.DEBUG,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                handlers=[
                    logging.FileHandler(args.log_file),
                    logging.StreamHandler(sys.stdout)
                ]
            )
        
        # Setup signal handlers for graceful shutdown
        setup_signal_handlers(manager)
        
        # Perform the requested action
        if args.action == "start":
            await start_system(manager, args)
        elif args.action == "stop":
            await stop_system(manager)
        elif args.action == "restart":
            await restart_system(manager, args)
        elif args.action == "status":
            await show_status(manager)
        elif args.action == "health":
            await show_health(manager)
        
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

async def start_system(manager, args):
    """Start the triumvirate integration system"""
    print("🚀 Starting Triumvirate Integration Layer...")
    
    # Initialize the system
    print("📦 Initializing system components...")
    if not await manager.initialize():
        print("❌ Failed to initialize system")
        sys.exit(1)
    
    # Start the system
    print("⚡ Starting all components...")
    if not await manager.start():
        print("❌ Failed to start system")
        sys.exit(1)
    
    # Show system status
    status = manager.get_status()
    print("\n✅ Triumvirtate Integration Layer started successfully!")
    print(f"🌐 API Server: http://{args.host}:{args.port}")
    print(f"📊 System Status: {status['system_status'].title()}")
    
    if not args.daemon:
        print("\n📈 Component Status:")
        for comp_name, comp_info in status["components"].items():
            status_icon = "🟢" if comp_info["running"] else "🔴"
            print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
        
        print(f"\n🔗 API Endpoints:")
        print(f"  • Health: http://{args.host}:{args.port}/api/v1/monitoring/health")
        print(f"  • Metrics: http://{args.host}:{args.port}/api/v1/monitoring/metrics")
        print(f"  • System Overview: http://{args.host}:{args.port}/api/v1/system/overview")
        
        print(f"\n📝 Logs: {args.log_file}")
        print("\nPress Ctrl+C to stop the system")
        
        # Keep running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutdown requested...")
    else:
        print("🔄 Running as daemon...")

async def stop_system(manager):
    """Stop the triumvirate integration system"""
    print("🛑 Stopping Triumvirate Integration Layer...")
    
    if not await manager.stop():
        print("❌ Failed to stop system properly")
        sys.exit(1)
    
    print("✅ System stopped successfully")

async def restart_system(manager, args):
    """Restart the triumvirate integration system"""
    print("🔄 Restarting Triumvirate Integration Layer...")
    
    if not await manager.restart():
        print("❌ Failed to restart system")
        sys.exit(1)
    
    print("✅ System restarted successfully")
    print(f"🌐 Available at: http://{args.host}:{args.port}")

async def show_status(manager):
    """Show system status"""
    status = manager.get_status()
    
    print("📊 Triumvirate Integration Layer Status")
    print("=" * 50)
    print(f"System Status: {status['system_status'].title()}")
    
    if status['startup_time']:
        from datetime import datetime
        startup_time = datetime.fromisoformat(status['startup_time'])
        uptime_seconds = (datetime.now() - startup_time).total_seconds()
        uptime_hours = int(uptime_seconds // 3600)
        uptime_minutes = int((uptime_seconds % 3600) // 60)
        print(f"Uptime: {uptime_hours}h {uptime_minutes}m")
    
    print("\n🔧 Components:")
    for comp_name, comp_info in status["components"].items():
        status_icon = "🟢" if comp_info["running"] else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
    
    print("\n🌐 Shared Infrastructure:")
    for infra_name, infra_status in status["shared_infrastructure"].items():
        status_icon = "🟢" if infra_status else "🔴"
        print(f"  {status_icon} {infra_name.replace('_', ' ').title()}: {'Running' if infra_status else 'Stopped'}")
    
    print("\n🚀 Revolutionary Capabilities:")
    for cap_name, cap_status in status["revolutionary_capabilities"].items():
        status_icon = "🟢" if cap_status else "🔴"
        print(f"  {status_icon} {cap_name.replace('_', ' ').title()}: {'Active' if cap_status else 'Inactive'}")

async def show_health(manager):
    """Show detailed health information"""
    print("🏥 Triumvirate Integration Layer Health Check")
    print("=" * 50)
    
    # Get system overview
    overview = manager.observability.get_system_overview()
    
    print(f"System Health: {overview['system_health']['status'].title()}")
    print(f"Health Score: {overview['system_health']['score']:.1f}%")
    
    print(f"\n📊 Metrics:")
    print(f"  • Total Components: {overview['total_components_tracked']}")
    print(f"  • Active Alerts: {overview['active_alerts']}")
    print(f"  • Critical Alerts: {overview['critical_alerts']}")
    
    print(f"\n🔍 Component Health:")
    for comp_name in ["agenta", "pranava", "antakhara"]:
        health = await getattr(manager, comp_name).get_health_status()
        status_icon = "🟢" if health["status"] == "healthy" else "🟡" if health["status"] == "degraded" else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {health['status']}")
    
    # Check integration health
    integration_status = manager.get_status()
    if integration_status['system_status'] == 'running':
        print(f"\n✅ Integration Status: HEALTHY")
    else:
        print(f"\n❌ Integration Status: UNHEALTHY")

if __name__ == "__main__":
    # Ensure we can handle KeyboardInterrupt properly
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)Setup health monitoring for all components"""
Main entry point for Triumvirate Integration Layer

This script provides a command-line interface for managing the triumvirate
integration system, including initialization, startup, shutdown, and monitoring.
"""

import asyncio
import argparse
import sys
import signal
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from triumvirate_manager import TriumvirateIntegrationManager, setup_signal_handlers
from configs.config_manager import ConfigManager

async def main():
    """Main entry point for the triumvirate integration system"""
    parser = argparse.ArgumentParser(description="Triumvirate Integration Layer")
    parser.add_argument(
        "--config", 
        default="configs/integration_config.yaml",
        help="Configuration file path (default: configs/integration_config.yaml)"
    )
    parser.add_argument(
        "--action",
        choices=["start", "stop", "restart", "status", "health"],
        default="start",
        help="Action to perform (default: start)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="API server port (default: 8000)"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="API server host (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Run as daemon process"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    parser.add_argument(
        "--log-file",
        default="logs/triumvirate.log",
        help="Log file path (default: logs/triumvirate.log)"
    )
    
    args = parser.parse_args()
    
    # Create necessary directories
    Path("logs").mkdir(exist_ok=True)
    Path("data").mkdir(exist_ok=True)
    
    try:
        # Create and configure the integration manager
        manager = TriumvirateIntegrationManager(args.config)
        
        # Update API configuration if provided
        config_manager = ConfigManager(args.config)
        config = config_manager.load_config()
        config.api_config["host"] = args.host
        config.api_config["port"] = args.port
        config_manager.save_config(config)
        
        # Setup logging
        if args.debug:
            import logging
            logging.basicConfig(
                level=logging.DEBUG,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                handlers=[
                    logging.FileHandler(args.log_file),
                    logging.StreamHandler(sys.stdout)
                ]
            )
        
        # Setup signal handlers for graceful shutdown
        setup_signal_handlers(manager)
        
        # Perform the requested action
        if args.action == "start":
            await start_system(manager, args)
        elif args.action == "stop":
            await stop_system(manager)
        elif args.action == "restart":
            await restart_system(manager, args)
        elif args.action == "status":
            await show_status(manager)
        elif args.action == "health":
            await show_health(manager)
        
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

async def start_system(manager, args):
    """Start the triumvirate integration system"""
    print("🚀 Starting Triumvirate Integration Layer...")
    
    # Initialize the system
    print("📦 Initializing system components...")
    if not await manager.initialize():
        print("❌ Failed to initialize system")
        sys.exit(1)
    
    # Start the system
    print("⚡ Starting all components...")
    if not await manager.start():
        print("❌ Failed to start system")
        sys.exit(1)
    
    # Show system status
    status = manager.get_status()
    print("\n✅ Triumvirtate Integration Layer started successfully!")
    print(f"🌐 API Server: http://{args.host}:{args.port}")
    print(f"📊 System Status: {status['system_status'].title()}")
    
    if not args.daemon:
        print("\n📈 Component Status:")
        for comp_name, comp_info in status["components"].items():
            status_icon = "🟢" if comp_info["running"] else "🔴"
            print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
        
        print(f"\n🔗 API Endpoints:")
        print(f"  • Health: http://{args.host}:{args.port}/api/v1/monitoring/health")
        print(f"  • Metrics: http://{args.host}:{args.port}/api/v1/monitoring/metrics")
        print(f"  • System Overview: http://{args.host}:{args.port}/api/v1/system/overview")
        
        print(f"\n📝 Logs: {args.log_file}")
        print("\nPress Ctrl+C to stop the system")
        
        # Keep running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutdown requested...")
    else:
        print("🔄 Running as daemon...")

async def stop_system(manager):
    """Stop the triumvirate integration system"""
    print("🛑 Stopping Triumvirate Integration Layer...")
    
    if not await manager.stop():
        print("❌ Failed to stop system properly")
        sys.exit(1)
    
    print("✅ System stopped successfully")

async def restart_system(manager, args):
    """Restart the triumvirate integration system"""
    print("🔄 Restarting Triumvirate Integration Layer...")
    
    if not await manager.restart():
        print("❌ Failed to restart system")
        sys.exit(1)
    
    print("✅ System restarted successfully")
    print(f"🌐 Available at: http://{args.host}:{args.port}")

async def show_status(manager):
    """Show system status"""
    status = manager.get_status()
    
    print("📊 Triumvirate Integration Layer Status")
    print("=" * 50)
    print(f"System Status: {status['system_status'].title()}")
    
    if status['startup_time']:
        from datetime import datetime
        startup_time = datetime.fromisoformat(status['startup_time'])
        uptime_seconds = (datetime.now() - startup_time).total_seconds()
        uptime_hours = int(uptime_seconds // 3600)
        uptime_minutes = int((uptime_seconds % 3600) // 60)
        print(f"Uptime: {uptime_hours}h {uptime_minutes}m")
    
    print("\n🔧 Components:")
    for comp_name, comp_info in status["components"].items():
        status_icon = "🟢" if comp_info["running"] else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
    
    print("\n🌐 Shared Infrastructure:")
    for infra_name, infra_status in status["shared_infrastructure"].items():
        status_icon = "🟢" if infra_status else "🔴"
        print(f"  {status_icon} {infra_name.replace('_', ' ').title()}: {'Running' if infra_status else 'Stopped'}")
    
    print("\n🚀 Revolutionary Capabilities:")
    for cap_name, cap_status in status["revolutionary_capabilities"].items():
        status_icon = "🟢" if cap_status else "🔴"
        print(f"  {status_icon} {cap_name.replace('_', ' ').title()}: {'Active' if cap_status else 'Inactive'}")

async def show_health(manager):
    """Show detailed health information"""
    print("🏥 Triumvirate Integration Layer Health Check")
    print("=" * 50)
    
    # Get system overview
    overview = manager.observability.get_system_overview()
    
    print(f"System Health: {overview['system_health']['status'].title()}")
    print(f"Health Score: {overview['system_health']['score']:.1f}%")
    
    print(f"\n📊 Metrics:")
    print(f"  • Total Components: {overview['total_components_tracked']}")
    print(f"  • Active Alerts: {overview['active_alerts']}")
    print(f"  • Critical Alerts: {overview['critical_alerts']}")
    
    print(f"\n🔍 Component Health:")
    for comp_name in ["agenta", "pranava", "antakhara"]:
        health = await getattr(manager, comp_name).get_health_status()
        status_icon = "🟢" if health["status"] == "healthy" else "🟡" if health["status"] == "degraded" else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {health['status']}")
    
    # Check integration health
    integration_status = manager.get_status()
    if integration_status['system_status'] == 'running':
        print(f"\n✅ Integration Status: HEALTHY")
    else:
        print(f"\n❌ Integration Status: UNHEALTHY")

if __name__ == "__main__":
    # Ensure we can handle KeyboardInterrupt properly
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
        self.logger.info("Setting up health monitoring")
        
        # Create health check tasks
        asyncio.create_task(self._health_monitor_loop())
        asyncio.create_task(self._integration_health_loop())
        
    async def _register_services(self) -> None:
        """
Main entry point for Triumvirate Integration Layer

This script provides a command-line interface for managing the triumvirate
integration system, including initialization, startup, shutdown, and monitoring.
"""

import asyncio
import argparse
import sys
import signal
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from triumvirate_manager import TriumvirateIntegrationManager, setup_signal_handlers
from configs.config_manager import ConfigManager

async def main():
    """Main entry point for the triumvirate integration system"""
    parser = argparse.ArgumentParser(description="Triumvirate Integration Layer")
    parser.add_argument(
        "--config", 
        default="configs/integration_config.yaml",
        help="Configuration file path (default: configs/integration_config.yaml)"
    )
    parser.add_argument(
        "--action",
        choices=["start", "stop", "restart", "status", "health"],
        default="start",
        help="Action to perform (default: start)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="API server port (default: 8000)"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="API server host (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Run as daemon process"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    parser.add_argument(
        "--log-file",
        default="logs/triumvirate.log",
        help="Log file path (default: logs/triumvirate.log)"
    )
    
    args = parser.parse_args()
    
    # Create necessary directories
    Path("logs").mkdir(exist_ok=True)
    Path("data").mkdir(exist_ok=True)
    
    try:
        # Create and configure the integration manager
        manager = TriumvirateIntegrationManager(args.config)
        
        # Update API configuration if provided
        config_manager = ConfigManager(args.config)
        config = config_manager.load_config()
        config.api_config["host"] = args.host
        config.api_config["port"] = args.port
        config_manager.save_config(config)
        
        # Setup logging
        if args.debug:
            import logging
            logging.basicConfig(
                level=logging.DEBUG,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                handlers=[
                    logging.FileHandler(args.log_file),
                    logging.StreamHandler(sys.stdout)
                ]
            )
        
        # Setup signal handlers for graceful shutdown
        setup_signal_handlers(manager)
        
        # Perform the requested action
        if args.action == "start":
            await start_system(manager, args)
        elif args.action == "stop":
            await stop_system(manager)
        elif args.action == "restart":
            await restart_system(manager, args)
        elif args.action == "status":
            await show_status(manager)
        elif args.action == "health":
            await show_health(manager)
        
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

async def start_system(manager, args):
    """Start the triumvirate integration system"""
    print("🚀 Starting Triumvirate Integration Layer...")
    
    # Initialize the system
    print("📦 Initializing system components...")
    if not await manager.initialize():
        print("❌ Failed to initialize system")
        sys.exit(1)
    
    # Start the system
    print("⚡ Starting all components...")
    if not await manager.start():
        print("❌ Failed to start system")
        sys.exit(1)
    
    # Show system status
    status = manager.get_status()
    print("\n✅ Triumvirtate Integration Layer started successfully!")
    print(f"🌐 API Server: http://{args.host}:{args.port}")
    print(f"📊 System Status: {status['system_status'].title()}")
    
    if not args.daemon:
        print("\n📈 Component Status:")
        for comp_name, comp_info in status["components"].items():
            status_icon = "🟢" if comp_info["running"] else "🔴"
            print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
        
        print(f"\n🔗 API Endpoints:")
        print(f"  • Health: http://{args.host}:{args.port}/api/v1/monitoring/health")
        print(f"  • Metrics: http://{args.host}:{args.port}/api/v1/monitoring/metrics")
        print(f"  • System Overview: http://{args.host}:{args.port}/api/v1/system/overview")
        
        print(f"\n📝 Logs: {args.log_file}")
        print("\nPress Ctrl+C to stop the system")
        
        # Keep running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutdown requested...")
    else:
        print("🔄 Running as daemon...")

async def stop_system(manager):
    """Stop the triumvirate integration system"""
    print("🛑 Stopping Triumvirate Integration Layer...")
    
    if not await manager.stop():
        print("❌ Failed to stop system properly")
        sys.exit(1)
    
    print("✅ System stopped successfully")

async def restart_system(manager, args):
    """Restart the triumvirate integration system"""
    print("🔄 Restarting Triumvirate Integration Layer...")
    
    if not await manager.restart():
        print("❌ Failed to restart system")
        sys.exit(1)
    
    print("✅ System restarted successfully")
    print(f"🌐 Available at: http://{args.host}:{args.port}")

async def show_status(manager):
    """Show system status"""
    status = manager.get_status()
    
    print("📊 Triumvirate Integration Layer Status")
    print("=" * 50)
    print(f"System Status: {status['system_status'].title()}")
    
    if status['startup_time']:
        from datetime import datetime
        startup_time = datetime.fromisoformat(status['startup_time'])
        uptime_seconds = (datetime.now() - startup_time).total_seconds()
        uptime_hours = int(uptime_seconds // 3600)
        uptime_minutes = int((uptime_seconds % 3600) // 60)
        print(f"Uptime: {uptime_hours}h {uptime_minutes}m")
    
    print("\n🔧 Components:")
    for comp_name, comp_info in status["components"].items():
        status_icon = "🟢" if comp_info["running"] else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
    
    print("\n🌐 Shared Infrastructure:")
    for infra_name, infra_status in status["shared_infrastructure"].items():
        status_icon = "🟢" if infra_status else "🔴"
        print(f"  {status_icon} {infra_name.replace('_', ' ').title()}: {'Running' if infra_status else 'Stopped'}")
    
    print("\n🚀 Revolutionary Capabilities:")
    for cap_name, cap_status in status["revolutionary_capabilities"].items():
        status_icon = "🟢" if cap_status else "🔴"
        print(f"  {status_icon} {cap_name.replace('_', ' ').title()}: {'Active' if cap_status else 'Inactive'}")

async def show_health(manager):
    """Show detailed health information"""
    print("🏥 Triumvirate Integration Layer Health Check")
    print("=" * 50)
    
    # Get system overview
    overview = manager.observability.get_system_overview()
    
    print(f"System Health: {overview['system_health']['status'].title()}")
    print(f"Health Score: {overview['system_health']['score']:.1f}%")
    
    print(f"\n📊 Metrics:")
    print(f"  • Total Components: {overview['total_components_tracked']}")
    print(f"  • Active Alerts: {overview['active_alerts']}")
    print(f"  • Critical Alerts: {overview['critical_alerts']}")
    
    print(f"\n🔍 Component Health:")
    for comp_name in ["agenta", "pranava", "antakhara"]:
        health = await getattr(manager, comp_name).get_health_status()
        status_icon = "🟢" if health["status"] == "healthy" else "🟡" if health["status"] == "degraded" else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {health['status']}")
    
    # Check integration health
    integration_status = manager.get_status()
    if integration_status['system_status'] == 'running':
        print(f"\n✅ Integration Status: HEALTHY")
    else:
        print(f"\n❌ Integration Status: UNHEALTHY")

if __name__ == "__main__":
    # Ensure we can handle KeyboardInterrupt properly
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)Register all services in discovery system"""
Main entry point for Triumvirate Integration Layer

This script provides a command-line interface for managing the triumvirate
integration system, including initialization, startup, shutdown, and monitoring.
"""

import asyncio
import argparse
import sys
import signal
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from triumvirate_manager import TriumvirateIntegrationManager, setup_signal_handlers
from configs.config_manager import ConfigManager

async def main():
    """Main entry point for the triumvirate integration system"""
    parser = argparse.ArgumentParser(description="Triumvirate Integration Layer")
    parser.add_argument(
        "--config", 
        default="configs/integration_config.yaml",
        help="Configuration file path (default: configs/integration_config.yaml)"
    )
    parser.add_argument(
        "--action",
        choices=["start", "stop", "restart", "status", "health"],
        default="start",
        help="Action to perform (default: start)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="API server port (default: 8000)"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="API server host (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Run as daemon process"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    parser.add_argument(
        "--log-file",
        default="logs/triumvirate.log",
        help="Log file path (default: logs/triumvirate.log)"
    )
    
    args = parser.parse_args()
    
    # Create necessary directories
    Path("logs").mkdir(exist_ok=True)
    Path("data").mkdir(exist_ok=True)
    
    try:
        # Create and configure the integration manager
        manager = TriumvirateIntegrationManager(args.config)
        
        # Update API configuration if provided
        config_manager = ConfigManager(args.config)
        config = config_manager.load_config()
        config.api_config["host"] = args.host
        config.api_config["port"] = args.port
        config_manager.save_config(config)
        
        # Setup logging
        if args.debug:
            import logging
            logging.basicConfig(
                level=logging.DEBUG,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                handlers=[
                    logging.FileHandler(args.log_file),
                    logging.StreamHandler(sys.stdout)
                ]
            )
        
        # Setup signal handlers for graceful shutdown
        setup_signal_handlers(manager)
        
        # Perform the requested action
        if args.action == "start":
            await start_system(manager, args)
        elif args.action == "stop":
            await stop_system(manager)
        elif args.action == "restart":
            await restart_system(manager, args)
        elif args.action == "status":
            await show_status(manager)
        elif args.action == "health":
            await show_health(manager)
        
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

async def start_system(manager, args):
    """Start the triumvirate integration system"""
    print("🚀 Starting Triumvirate Integration Layer...")
    
    # Initialize the system
    print("📦 Initializing system components...")
    if not await manager.initialize():
        print("❌ Failed to initialize system")
        sys.exit(1)
    
    # Start the system
    print("⚡ Starting all components...")
    if not await manager.start():
        print("❌ Failed to start system")
        sys.exit(1)
    
    # Show system status
    status = manager.get_status()
    print("\n✅ Triumvirtate Integration Layer started successfully!")
    print(f"🌐 API Server: http://{args.host}:{args.port}")
    print(f"📊 System Status: {status['system_status'].title()}")
    
    if not args.daemon:
        print("\n📈 Component Status:")
        for comp_name, comp_info in status["components"].items():
            status_icon = "🟢" if comp_info["running"] else "🔴"
            print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
        
        print(f"\n🔗 API Endpoints:")
        print(f"  • Health: http://{args.host}:{args.port}/api/v1/monitoring/health")
        print(f"  • Metrics: http://{args.host}:{args.port}/api/v1/monitoring/metrics")
        print(f"  • System Overview: http://{args.host}:{args.port}/api/v1/system/overview")
        
        print(f"\n📝 Logs: {args.log_file}")
        print("\nPress Ctrl+C to stop the system")
        
        # Keep running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutdown requested...")
    else:
        print("🔄 Running as daemon...")

async def stop_system(manager):
    """Stop the triumvirate integration system"""
    print("🛑 Stopping Triumvirate Integration Layer...")
    
    if not await manager.stop():
        print("❌ Failed to stop system properly")
        sys.exit(1)
    
    print("✅ System stopped successfully")

async def restart_system(manager, args):
    """Restart the triumvirate integration system"""
    print("🔄 Restarting Triumvirate Integration Layer...")
    
    if not await manager.restart():
        print("❌ Failed to restart system")
        sys.exit(1)
    
    print("✅ System restarted successfully")
    print(f"🌐 Available at: http://{args.host}:{args.port}")

async def show_status(manager):
    """Show system status"""
    status = manager.get_status()
    
    print("📊 Triumvirate Integration Layer Status")
    print("=" * 50)
    print(f"System Status: {status['system_status'].title()}")
    
    if status['startup_time']:
        from datetime import datetime
        startup_time = datetime.fromisoformat(status['startup_time'])
        uptime_seconds = (datetime.now() - startup_time).total_seconds()
        uptime_hours = int(uptime_seconds // 3600)
        uptime_minutes = int((uptime_seconds % 3600) // 60)
        print(f"Uptime: {uptime_hours}h {uptime_minutes}m")
    
    print("\n🔧 Components:")
    for comp_name, comp_info in status["components"].items():
        status_icon = "🟢" if comp_info["running"] else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
    
    print("\n🌐 Shared Infrastructure:")
    for infra_name, infra_status in status["shared_infrastructure"].items():
        status_icon = "🟢" if infra_status else "🔴"
        print(f"  {status_icon} {infra_name.replace('_', ' ').title()}: {'Running' if infra_status else 'Stopped'}")
    
    print("\n🚀 Revolutionary Capabilities:")
    for cap_name, cap_status in status["revolutionary_capabilities"].items():
        status_icon = "🟢" if cap_status else "🔴"
        print(f"  {status_icon} {cap_name.replace('_', ' ').title()}: {'Active' if cap_status else 'Inactive'}")

async def show_health(manager):
    """Show detailed health information"""
    print("🏥 Triumvirate Integration Layer Health Check")
    print("=" * 50)
    
    # Get system overview
    overview = manager.observability.get_system_overview()
    
    print(f"System Health: {overview['system_health']['status'].title()}")
    print(f"Health Score: {overview['system_health']['score']:.1f}%")
    
    print(f"\n📊 Metrics:")
    print(f"  • Total Components: {overview['total_components_tracked']}")
    print(f"  • Active Alerts: {overview['active_alerts']}")
    print(f"  • Critical Alerts: {overview['critical_alerts']}")
    
    print(f"\n🔍 Component Health:")
    for comp_name in ["agenta", "pranava", "antakhara"]:
        health = await getattr(manager, comp_name).get_health_status()
        status_icon = "🟢" if health["status"] == "healthy" else "🟡" if health["status"] == "degraded" else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {health['status']}")
    
    # Check integration health
    integration_status = manager.get_status()
    if integration_status['system_status'] == 'running':
        print(f"\n✅ Integration Status: HEALTHY")
    else:
        print(f"\n❌ Integration Status: UNHEALTHY")

if __name__ == "__main__":
    # Ensure we can handle KeyboardInterrupt properly
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
        self.logger.info("Registering services")
        
        # Register core components
        await self.service_discovery.register_service(
            self._create_service_info("agenta", ComponentType.AGENTA, self.agenta.component_id)
        )
        
        await self.service_discovery.register_service(
            self._create_service_info("pranava", ComponentType.PRANAVA, self.pranava.component_id)
        )
        
        await self.service_discovery.register_service(
            self._create_service_info("antakhara", ComponentType.ANTAKHARA, self.antakhara.component_id)
        )
        
        # Register revolutionary capabilities
        if self.intelligent_coordinator:
            await self.service_discovery.register_service(
                self._create_service_info("intelligent_coordinator", ComponentType.MICROAGENT, "intelligent_coordinator")
            )
            
        if self.adaptive_optimizer:
            await self.service_discovery.register_service(
                self._create_service_info("adaptive_optimizer", ComponentType.MICROAGENT, "adaptive_optimizer")
            )
            
        if self.self_healer:
            await self.service_discovery.register_service(
                self._create_service_info("self_healer", ComponentType.MICROAGENT, "self_healer")
            )
            
        if self.performance_optimizer:
            await self.service_discovery.register_service(
                self._create_service_info("performance_optimizer", ComponentType.MICROAGENT, "performance_optimizer")
            )
            
    def _create_service_info(self, service_type: str, component_type: ComponentType, 
                           component_id: str) -> ServiceInfo:
        """
Main entry point for Triumvirate Integration Layer

This script provides a command-line interface for managing the triumvirate
integration system, including initialization, startup, shutdown, and monitoring.
"""

import asyncio
import argparse
import sys
import signal
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from triumvirate_manager import TriumvirateIntegrationManager, setup_signal_handlers
from configs.config_manager import ConfigManager

async def main():
    """Main entry point for the triumvirate integration system"""
    parser = argparse.ArgumentParser(description="Triumvirate Integration Layer")
    parser.add_argument(
        "--config", 
        default="configs/integration_config.yaml",
        help="Configuration file path (default: configs/integration_config.yaml)"
    )
    parser.add_argument(
        "--action",
        choices=["start", "stop", "restart", "status", "health"],
        default="start",
        help="Action to perform (default: start)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="API server port (default: 8000)"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="API server host (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Run as daemon process"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    parser.add_argument(
        "--log-file",
        default="logs/triumvirate.log",
        help="Log file path (default: logs/triumvirate.log)"
    )
    
    args = parser.parse_args()
    
    # Create necessary directories
    Path("logs").mkdir(exist_ok=True)
    Path("data").mkdir(exist_ok=True)
    
    try:
        # Create and configure the integration manager
        manager = TriumvirateIntegrationManager(args.config)
        
        # Update API configuration if provided
        config_manager = ConfigManager(args.config)
        config = config_manager.load_config()
        config.api_config["host"] = args.host
        config.api_config["port"] = args.port
        config_manager.save_config(config)
        
        # Setup logging
        if args.debug:
            import logging
            logging.basicConfig(
                level=logging.DEBUG,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                handlers=[
                    logging.FileHandler(args.log_file),
                    logging.StreamHandler(sys.stdout)
                ]
            )
        
        # Setup signal handlers for graceful shutdown
        setup_signal_handlers(manager)
        
        # Perform the requested action
        if args.action == "start":
            await start_system(manager, args)
        elif args.action == "stop":
            await stop_system(manager)
        elif args.action == "restart":
            await restart_system(manager, args)
        elif args.action == "status":
            await show_status(manager)
        elif args.action == "health":
            await show_health(manager)
        
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

async def start_system(manager, args):
    """Start the triumvirate integration system"""
    print("🚀 Starting Triumvirate Integration Layer...")
    
    # Initialize the system
    print("📦 Initializing system components...")
    if not await manager.initialize():
        print("❌ Failed to initialize system")
        sys.exit(1)
    
    # Start the system
    print("⚡ Starting all components...")
    if not await manager.start():
        print("❌ Failed to start system")
        sys.exit(1)
    
    # Show system status
    status = manager.get_status()
    print("\n✅ Triumvirtate Integration Layer started successfully!")
    print(f"🌐 API Server: http://{args.host}:{args.port}")
    print(f"📊 System Status: {status['system_status'].title()}")
    
    if not args.daemon:
        print("\n📈 Component Status:")
        for comp_name, comp_info in status["components"].items():
            status_icon = "🟢" if comp_info["running"] else "🔴"
            print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
        
        print(f"\n🔗 API Endpoints:")
        print(f"  • Health: http://{args.host}:{args.port}/api/v1/monitoring/health")
        print(f"  • Metrics: http://{args.host}:{args.port}/api/v1/monitoring/metrics")
        print(f"  • System Overview: http://{args.host}:{args.port}/api/v1/system/overview")
        
        print(f"\n📝 Logs: {args.log_file}")
        print("\nPress Ctrl+C to stop the system")
        
        # Keep running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutdown requested...")
    else:
        print("🔄 Running as daemon...")

async def stop_system(manager):
    """Stop the triumvirate integration system"""
    print("🛑 Stopping Triumvirate Integration Layer...")
    
    if not await manager.stop():
        print("❌ Failed to stop system properly")
        sys.exit(1)
    
    print("✅ System stopped successfully")

async def restart_system(manager, args):
    """Restart the triumvirate integration system"""
    print("🔄 Restarting Triumvirate Integration Layer...")
    
    if not await manager.restart():
        print("❌ Failed to restart system")
        sys.exit(1)
    
    print("✅ System restarted successfully")
    print(f"🌐 Available at: http://{args.host}:{args.port}")

async def show_status(manager):
    """Show system status"""
    status = manager.get_status()
    
    print("📊 Triumvirate Integration Layer Status")
    print("=" * 50)
    print(f"System Status: {status['system_status'].title()}")
    
    if status['startup_time']:
        from datetime import datetime
        startup_time = datetime.fromisoformat(status['startup_time'])
        uptime_seconds = (datetime.now() - startup_time).total_seconds()
        uptime_hours = int(uptime_seconds // 3600)
        uptime_minutes = int((uptime_seconds % 3600) // 60)
        print(f"Uptime: {uptime_hours}h {uptime_minutes}m")
    
    print("\n🔧 Components:")
    for comp_name, comp_info in status["components"].items():
        status_icon = "🟢" if comp_info["running"] else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
    
    print("\n🌐 Shared Infrastructure:")
    for infra_name, infra_status in status["shared_infrastructure"].items():
        status_icon = "🟢" if infra_status else "🔴"
        print(f"  {status_icon} {infra_name.replace('_', ' ').title()}: {'Running' if infra_status else 'Stopped'}")
    
    print("\n🚀 Revolutionary Capabilities:")
    for cap_name, cap_status in status["revolutionary_capabilities"].items():
        status_icon = "🟢" if cap_status else "🔴"
        print(f"  {status_icon} {cap_name.replace('_', ' ').title()}: {'Active' if cap_status else 'Inactive'}")

async def show_health(manager):
    """Show detailed health information"""
    print("🏥 Triumvirate Integration Layer Health Check")
    print("=" * 50)
    
    # Get system overview
    overview = manager.observability.get_system_overview()
    
    print(f"System Health: {overview['system_health']['status'].title()}")
    print(f"Health Score: {overview['system_health']['score']:.1f}%")
    
    print(f"\n📊 Metrics:")
    print(f"  • Total Components: {overview['total_components_tracked']}")
    print(f"  • Active Alerts: {overview['active_alerts']}")
    print(f"  • Critical Alerts: {overview['critical_alerts']}")
    
    print(f"\n🔍 Component Health:")
    for comp_name in ["agenta", "pranava", "antakhara"]:
        health = await getattr(manager, comp_name).get_health_status()
        status_icon = "🟢" if health["status"] == "healthy" else "🟡" if health["status"] == "degraded" else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {health['status']}")
    
    # Check integration health
    integration_status = manager.get_status()
    if integration_status['system_status'] == 'running':
        print(f"\n✅ Integration Status: HEALTHY")
    else:
        print(f"\n❌ Integration Status: UNHEALTHY")

if __name__ == "__main__":
    # Ensure we can handle KeyboardInterrupt properly
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)Create service info for registration"""
Main entry point for Triumvirate Integration Layer

This script provides a command-line interface for managing the triumvirate
integration system, including initialization, startup, shutdown, and monitoring.
"""

import asyncio
import argparse
import sys
import signal
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from triumvirate_manager import TriumvirateIntegrationManager, setup_signal_handlers
from configs.config_manager import ConfigManager

async def main():
    """Main entry point for the triumvirate integration system"""
    parser = argparse.ArgumentParser(description="Triumvirate Integration Layer")
    parser.add_argument(
        "--config", 
        default="configs/integration_config.yaml",
        help="Configuration file path (default: configs/integration_config.yaml)"
    )
    parser.add_argument(
        "--action",
        choices=["start", "stop", "restart", "status", "health"],
        default="start",
        help="Action to perform (default: start)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="API server port (default: 8000)"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="API server host (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Run as daemon process"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    parser.add_argument(
        "--log-file",
        default="logs/triumvirate.log",
        help="Log file path (default: logs/triumvirate.log)"
    )
    
    args = parser.parse_args()
    
    # Create necessary directories
    Path("logs").mkdir(exist_ok=True)
    Path("data").mkdir(exist_ok=True)
    
    try:
        # Create and configure the integration manager
        manager = TriumvirateIntegrationManager(args.config)
        
        # Update API configuration if provided
        config_manager = ConfigManager(args.config)
        config = config_manager.load_config()
        config.api_config["host"] = args.host
        config.api_config["port"] = args.port
        config_manager.save_config(config)
        
        # Setup logging
        if args.debug:
            import logging
            logging.basicConfig(
                level=logging.DEBUG,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                handlers=[
                    logging.FileHandler(args.log_file),
                    logging.StreamHandler(sys.stdout)
                ]
            )
        
        # Setup signal handlers for graceful shutdown
        setup_signal_handlers(manager)
        
        # Perform the requested action
        if args.action == "start":
            await start_system(manager, args)
        elif args.action == "stop":
            await stop_system(manager)
        elif args.action == "restart":
            await restart_system(manager, args)
        elif args.action == "status":
            await show_status(manager)
        elif args.action == "health":
            await show_health(manager)
        
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

async def start_system(manager, args):
    """Start the triumvirate integration system"""
    print("🚀 Starting Triumvirate Integration Layer...")
    
    # Initialize the system
    print("📦 Initializing system components...")
    if not await manager.initialize():
        print("❌ Failed to initialize system")
        sys.exit(1)
    
    # Start the system
    print("⚡ Starting all components...")
    if not await manager.start():
        print("❌ Failed to start system")
        sys.exit(1)
    
    # Show system status
    status = manager.get_status()
    print("\n✅ Triumvirtate Integration Layer started successfully!")
    print(f"🌐 API Server: http://{args.host}:{args.port}")
    print(f"📊 System Status: {status['system_status'].title()}")
    
    if not args.daemon:
        print("\n📈 Component Status:")
        for comp_name, comp_info in status["components"].items():
            status_icon = "🟢" if comp_info["running"] else "🔴"
            print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
        
        print(f"\n🔗 API Endpoints:")
        print(f"  • Health: http://{args.host}:{args.port}/api/v1/monitoring/health")
        print(f"  • Metrics: http://{args.host}:{args.port}/api/v1/monitoring/metrics")
        print(f"  • System Overview: http://{args.host}:{args.port}/api/v1/system/overview")
        
        print(f"\n📝 Logs: {args.log_file}")
        print("\nPress Ctrl+C to stop the system")
        
        # Keep running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutdown requested...")
    else:
        print("🔄 Running as daemon...")

async def stop_system(manager):
    """Stop the triumvirate integration system"""
    print("🛑 Stopping Triumvirate Integration Layer...")
    
    if not await manager.stop():
        print("❌ Failed to stop system properly")
        sys.exit(1)
    
    print("✅ System stopped successfully")

async def restart_system(manager, args):
    """Restart the triumvirate integration system"""
    print("🔄 Restarting Triumvirate Integration Layer...")
    
    if not await manager.restart():
        print("❌ Failed to restart system")
        sys.exit(1)
    
    print("✅ System restarted successfully")
    print(f"🌐 Available at: http://{args.host}:{args.port}")

async def show_status(manager):
    """Show system status"""
    status = manager.get_status()
    
    print("📊 Triumvirate Integration Layer Status")
    print("=" * 50)
    print(f"System Status: {status['system_status'].title()}")
    
    if status['startup_time']:
        from datetime import datetime
        startup_time = datetime.fromisoformat(status['startup_time'])
        uptime_seconds = (datetime.now() - startup_time).total_seconds()
        uptime_hours = int(uptime_seconds // 3600)
        uptime_minutes = int((uptime_seconds % 3600) // 60)
        print(f"Uptime: {uptime_hours}h {uptime_minutes}m")
    
    print("\n🔧 Components:")
    for comp_name, comp_info in status["components"].items():
        status_icon = "🟢" if comp_info["running"] else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
    
    print("\n🌐 Shared Infrastructure:")
    for infra_name, infra_status in status["shared_infrastructure"].items():
        status_icon = "🟢" if infra_status else "🔴"
        print(f"  {status_icon} {infra_name.replace('_', ' ').title()}: {'Running' if infra_status else 'Stopped'}")
    
    print("\n🚀 Revolutionary Capabilities:")
    for cap_name, cap_status in status["revolutionary_capabilities"].items():
        status_icon = "🟢" if cap_status else "🔴"
        print(f"  {status_icon} {cap_name.replace('_', ' ').title()}: {'Active' if cap_status else 'Inactive'}")

async def show_health(manager):
    """Show detailed health information"""
    print("🏥 Triumvirate Integration Layer Health Check")
    print("=" * 50)
    
    # Get system overview
    overview = manager.observability.get_system_overview()
    
    print(f"System Health: {overview['system_health']['status'].title()}")
    print(f"Health Score: {overview['system_health']['score']:.1f}%")
    
    print(f"\n📊 Metrics:")
    print(f"  • Total Components: {overview['total_components_tracked']}")
    print(f"  • Active Alerts: {overview['active_alerts']}")
    print(f"  • Critical Alerts: {overview['critical_alerts']}")
    
    print(f"\n🔍 Component Health:")
    for comp_name in ["agenta", "pranava", "antakhara"]:
        health = await getattr(manager, comp_name).get_health_status()
        status_icon = "🟢" if health["status"] == "healthy" else "🟡" if health["status"] == "degraded" else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {health['status']}")
    
    # Check integration health
    integration_status = manager.get_status()
    if integration_status['system_status'] == 'running':
        print(f"\n✅ Integration Status: HEALTHY")
    else:
        print(f"\n❌ Integration Status: UNHEALTHY")

if __name__ == "__main__":
    # Ensure we can handle KeyboardInterrupt properly
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
        return ServiceInfo(
            service_id=f"{service_type}_{component_id}",
            service_type=service_type,
            endpoint=f"{service_type}://{component_id}",
            capabilities=self._get_service_capabilities(service_type),
            metadata={
                "component_type": component_type.value,
                "integration_version": "1.0.0",
                "registered_at": datetime.now().isoformat()
            }
        )
        
    def _get_service_capabilities(self, service_type: str) -> List[str]:
        """
Main entry point for Triumvirate Integration Layer

This script provides a command-line interface for managing the triumvirate
integration system, including initialization, startup, shutdown, and monitoring.
"""

import asyncio
import argparse
import sys
import signal
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from triumvirate_manager import TriumvirateIntegrationManager, setup_signal_handlers
from configs.config_manager import ConfigManager

async def main():
    """Main entry point for the triumvirate integration system"""
    parser = argparse.ArgumentParser(description="Triumvirate Integration Layer")
    parser.add_argument(
        "--config", 
        default="configs/integration_config.yaml",
        help="Configuration file path (default: configs/integration_config.yaml)"
    )
    parser.add_argument(
        "--action",
        choices=["start", "stop", "restart", "status", "health"],
        default="start",
        help="Action to perform (default: start)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="API server port (default: 8000)"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="API server host (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Run as daemon process"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    parser.add_argument(
        "--log-file",
        default="logs/triumvirate.log",
        help="Log file path (default: logs/triumvirate.log)"
    )
    
    args = parser.parse_args()
    
    # Create necessary directories
    Path("logs").mkdir(exist_ok=True)
    Path("data").mkdir(exist_ok=True)
    
    try:
        # Create and configure the integration manager
        manager = TriumvirateIntegrationManager(args.config)
        
        # Update API configuration if provided
        config_manager = ConfigManager(args.config)
        config = config_manager.load_config()
        config.api_config["host"] = args.host
        config.api_config["port"] = args.port
        config_manager.save_config(config)
        
        # Setup logging
        if args.debug:
            import logging
            logging.basicConfig(
                level=logging.DEBUG,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                handlers=[
                    logging.FileHandler(args.log_file),
                    logging.StreamHandler(sys.stdout)
                ]
            )
        
        # Setup signal handlers for graceful shutdown
        setup_signal_handlers(manager)
        
        # Perform the requested action
        if args.action == "start":
            await start_system(manager, args)
        elif args.action == "stop":
            await stop_system(manager)
        elif args.action == "restart":
            await restart_system(manager, args)
        elif args.action == "status":
            await show_status(manager)
        elif args.action == "health":
            await show_health(manager)
        
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

async def start_system(manager, args):
    """Start the triumvirate integration system"""
    print("🚀 Starting Triumvirate Integration Layer...")
    
    # Initialize the system
    print("📦 Initializing system components...")
    if not await manager.initialize():
        print("❌ Failed to initialize system")
        sys.exit(1)
    
    # Start the system
    print("⚡ Starting all components...")
    if not await manager.start():
        print("❌ Failed to start system")
        sys.exit(1)
    
    # Show system status
    status = manager.get_status()
    print("\n✅ Triumvirtate Integration Layer started successfully!")
    print(f"🌐 API Server: http://{args.host}:{args.port}")
    print(f"📊 System Status: {status['system_status'].title()}")
    
    if not args.daemon:
        print("\n📈 Component Status:")
        for comp_name, comp_info in status["components"].items():
            status_icon = "🟢" if comp_info["running"] else "🔴"
            print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
        
        print(f"\n🔗 API Endpoints:")
        print(f"  • Health: http://{args.host}:{args.port}/api/v1/monitoring/health")
        print(f"  • Metrics: http://{args.host}:{args.port}/api/v1/monitoring/metrics")
        print(f"  • System Overview: http://{args.host}:{args.port}/api/v1/system/overview")
        
        print(f"\n📝 Logs: {args.log_file}")
        print("\nPress Ctrl+C to stop the system")
        
        # Keep running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutdown requested...")
    else:
        print("🔄 Running as daemon...")

async def stop_system(manager):
    """Stop the triumvirate integration system"""
    print("🛑 Stopping Triumvirate Integration Layer...")
    
    if not await manager.stop():
        print("❌ Failed to stop system properly")
        sys.exit(1)
    
    print("✅ System stopped successfully")

async def restart_system(manager, args):
    """Restart the triumvirate integration system"""
    print("🔄 Restarting Triumvirate Integration Layer...")
    
    if not await manager.restart():
        print("❌ Failed to restart system")
        sys.exit(1)
    
    print("✅ System restarted successfully")
    print(f"🌐 Available at: http://{args.host}:{args.port}")

async def show_status(manager):
    """Show system status"""
    status = manager.get_status()
    
    print("📊 Triumvirate Integration Layer Status")
    print("=" * 50)
    print(f"System Status: {status['system_status'].title()}")
    
    if status['startup_time']:
        from datetime import datetime
        startup_time = datetime.fromisoformat(status['startup_time'])
        uptime_seconds = (datetime.now() - startup_time).total_seconds()
        uptime_hours = int(uptime_seconds // 3600)
        uptime_minutes = int((uptime_seconds % 3600) // 60)
        print(f"Uptime: {uptime_hours}h {uptime_minutes}m")
    
    print("\n🔧 Components:")
    for comp_name, comp_info in status["components"].items():
        status_icon = "🟢" if comp_info["running"] else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
    
    print("\n🌐 Shared Infrastructure:")
    for infra_name, infra_status in status["shared_infrastructure"].items():
        status_icon = "🟢" if infra_status else "🔴"
        print(f"  {status_icon} {infra_name.replace('_', ' ').title()}: {'Running' if infra_status else 'Stopped'}")
    
    print("\n🚀 Revolutionary Capabilities:")
    for cap_name, cap_status in status["revolutionary_capabilities"].items():
        status_icon = "🟢" if cap_status else "🔴"
        print(f"  {status_icon} {cap_name.replace('_', ' ').title()}: {'Active' if cap_status else 'Inactive'}")

async def show_health(manager):
    """Show detailed health information"""
    print("🏥 Triumvirate Integration Layer Health Check")
    print("=" * 50)
    
    # Get system overview
    overview = manager.observability.get_system_overview()
    
    print(f"System Health: {overview['system_health']['status'].title()}")
    print(f"Health Score: {overview['system_health']['score']:.1f}%")
    
    print(f"\n📊 Metrics:")
    print(f"  • Total Components: {overview['total_components_tracked']}")
    print(f"  • Active Alerts: {overview['active_alerts']}")
    print(f"  • Critical Alerts: {overview['critical_alerts']}")
    
    print(f"\n🔍 Component Health:")
    for comp_name in ["agenta", "pranava", "antakhara"]:
        health = await getattr(manager, comp_name).get_health_status()
        status_icon = "🟢" if health["status"] == "healthy" else "🟡" if health["status"] == "degraded" else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {health['status']}")
    
    # Check integration health
    integration_status = manager.get_status()
    if integration_status['system_status'] == 'running':
        print(f"\n✅ Integration Status: HEALTHY")
    else:
        print(f"\n❌ Integration Status: UNHEALTHY")

if __name__ == "__main__":
    # Ensure we can handle KeyboardInterrupt properly
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)Get capabilities for a service type"""
Main entry point for Triumvirate Integration Layer

This script provides a command-line interface for managing the triumvirate
integration system, including initialization, startup, shutdown, and monitoring.
"""

import asyncio
import argparse
import sys
import signal
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from triumvirate_manager import TriumvirateIntegrationManager, setup_signal_handlers
from configs.config_manager import ConfigManager

async def main():
    """Main entry point for the triumvirate integration system"""
    parser = argparse.ArgumentParser(description="Triumvirate Integration Layer")
    parser.add_argument(
        "--config", 
        default="configs/integration_config.yaml",
        help="Configuration file path (default: configs/integration_config.yaml)"
    )
    parser.add_argument(
        "--action",
        choices=["start", "stop", "restart", "status", "health"],
        default="start",
        help="Action to perform (default: start)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="API server port (default: 8000)"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="API server host (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Run as daemon process"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    parser.add_argument(
        "--log-file",
        default="logs/triumvirate.log",
        help="Log file path (default: logs/triumvirate.log)"
    )
    
    args = parser.parse_args()
    
    # Create necessary directories
    Path("logs").mkdir(exist_ok=True)
    Path("data").mkdir(exist_ok=True)
    
    try:
        # Create and configure the integration manager
        manager = TriumvirateIntegrationManager(args.config)
        
        # Update API configuration if provided
        config_manager = ConfigManager(args.config)
        config = config_manager.load_config()
        config.api_config["host"] = args.host
        config.api_config["port"] = args.port
        config_manager.save_config(config)
        
        # Setup logging
        if args.debug:
            import logging
            logging.basicConfig(
                level=logging.DEBUG,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                handlers=[
                    logging.FileHandler(args.log_file),
                    logging.StreamHandler(sys.stdout)
                ]
            )
        
        # Setup signal handlers for graceful shutdown
        setup_signal_handlers(manager)
        
        # Perform the requested action
        if args.action == "start":
            await start_system(manager, args)
        elif args.action == "stop":
            await stop_system(manager)
        elif args.action == "restart":
            await restart_system(manager, args)
        elif args.action == "status":
            await show_status(manager)
        elif args.action == "health":
            await show_health(manager)
        
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

async def start_system(manager, args):
    """Start the triumvirate integration system"""
    print("🚀 Starting Triumvirate Integration Layer...")
    
    # Initialize the system
    print("📦 Initializing system components...")
    if not await manager.initialize():
        print("❌ Failed to initialize system")
        sys.exit(1)
    
    # Start the system
    print("⚡ Starting all components...")
    if not await manager.start():
        print("❌ Failed to start system")
        sys.exit(1)
    
    # Show system status
    status = manager.get_status()
    print("\n✅ Triumvirtate Integration Layer started successfully!")
    print(f"🌐 API Server: http://{args.host}:{args.port}")
    print(f"📊 System Status: {status['system_status'].title()}")
    
    if not args.daemon:
        print("\n📈 Component Status:")
        for comp_name, comp_info in status["components"].items():
            status_icon = "🟢" if comp_info["running"] else "🔴"
            print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
        
        print(f"\n🔗 API Endpoints:")
        print(f"  • Health: http://{args.host}:{args.port}/api/v1/monitoring/health")
        print(f"  • Metrics: http://{args.host}:{args.port}/api/v1/monitoring/metrics")
        print(f"  • System Overview: http://{args.host}:{args.port}/api/v1/system/overview")
        
        print(f"\n📝 Logs: {args.log_file}")
        print("\nPress Ctrl+C to stop the system")
        
        # Keep running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutdown requested...")
    else:
        print("🔄 Running as daemon...")

async def stop_system(manager):
    """Stop the triumvirate integration system"""
    print("🛑 Stopping Triumvirate Integration Layer...")
    
    if not await manager.stop():
        print("❌ Failed to stop system properly")
        sys.exit(1)
    
    print("✅ System stopped successfully")

async def restart_system(manager, args):
    """Restart the triumvirate integration system"""
    print("🔄 Restarting Triumvirate Integration Layer...")
    
    if not await manager.restart():
        print("❌ Failed to restart system")
        sys.exit(1)
    
    print("✅ System restarted successfully")
    print(f"🌐 Available at: http://{args.host}:{args.port}")

async def show_status(manager):
    """Show system status"""
    status = manager.get_status()
    
    print("📊 Triumvirate Integration Layer Status")
    print("=" * 50)
    print(f"System Status: {status['system_status'].title()}")
    
    if status['startup_time']:
        from datetime import datetime
        startup_time = datetime.fromisoformat(status['startup_time'])
        uptime_seconds = (datetime.now() - startup_time).total_seconds()
        uptime_hours = int(uptime_seconds // 3600)
        uptime_minutes = int((uptime_seconds % 3600) // 60)
        print(f"Uptime: {uptime_hours}h {uptime_minutes}m")
    
    print("\n🔧 Components:")
    for comp_name, comp_info in status["components"].items():
        status_icon = "🟢" if comp_info["running"] else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
    
    print("\n🌐 Shared Infrastructure:")
    for infra_name, infra_status in status["shared_infrastructure"].items():
        status_icon = "🟢" if infra_status else "🔴"
        print(f"  {status_icon} {infra_name.replace('_', ' ').title()}: {'Running' if infra_status else 'Stopped'}")
    
    print("\n🚀 Revolutionary Capabilities:")
    for cap_name, cap_status in status["revolutionary_capabilities"].items():
        status_icon = "🟢" if cap_status else "🔴"
        print(f"  {status_icon} {cap_name.replace('_', ' ').title()}: {'Active' if cap_status else 'Inactive'}")

async def show_health(manager):
    """Show detailed health information"""
    print("🏥 Triumvirate Integration Layer Health Check")
    print("=" * 50)
    
    # Get system overview
    overview = manager.observability.get_system_overview()
    
    print(f"System Health: {overview['system_health']['status'].title()}")
    print(f"Health Score: {overview['system_health']['score']:.1f}%")
    
    print(f"\n📊 Metrics:")
    print(f"  • Total Components: {overview['total_components_tracked']}")
    print(f"  • Active Alerts: {overview['active_alerts']}")
    print(f"  • Critical Alerts: {overview['critical_alerts']}")
    
    print(f"\n🔍 Component Health:")
    for comp_name in ["agenta", "pranava", "antakhara"]:
        health = await getattr(manager, comp_name).get_health_status()
        status_icon = "🟢" if health["status"] == "healthy" else "🟡" if health["status"] == "degraded" else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {health['status']}")
    
    # Check integration health
    integration_status = manager.get_status()
    if integration_status['system_status'] == 'running':
        print(f"\n✅ Integration Status: HEALTHY")
    else:
        print(f"\n❌ Integration Status: UNHEALTHY")

if __name__ == "__main__":
    # Ensure we can handle KeyboardInterrupt properly
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
        capabilities_map = {
            "agenta": ["hierarchy_management", "intelligent_routing", "load_balancing"],
            "pranava": ["orchestration", "workflow_management", "load_balancing"],
            "antakhara": ["security", "policy_enforcement", "compliance"],
            "intelligent_coordinator": ["cross_component_coordination", "intelligence_routing"],
            "adaptive_optimizer": ["adaptive_scaling", "performance_optimization"],
            "self_healer": ["self_healing", "resilience"],
            "performance_optimizer": ["performance_optimization", "analytics"]
        }
        return capabilities_map.get(service_type, [])
        
    def _setup_logging(self) -> None:
        """
Main entry point for Triumvirate Integration Layer

This script provides a command-line interface for managing the triumvirate
integration system, including initialization, startup, shutdown, and monitoring.
"""

import asyncio
import argparse
import sys
import signal
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from triumvirate_manager import TriumvirateIntegrationManager, setup_signal_handlers
from configs.config_manager import ConfigManager

async def main():
    """Main entry point for the triumvirate integration system"""
    parser = argparse.ArgumentParser(description="Triumvirate Integration Layer")
    parser.add_argument(
        "--config", 
        default="configs/integration_config.yaml",
        help="Configuration file path (default: configs/integration_config.yaml)"
    )
    parser.add_argument(
        "--action",
        choices=["start", "stop", "restart", "status", "health"],
        default="start",
        help="Action to perform (default: start)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="API server port (default: 8000)"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="API server host (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Run as daemon process"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    parser.add_argument(
        "--log-file",
        default="logs/triumvirate.log",
        help="Log file path (default: logs/triumvirate.log)"
    )
    
    args = parser.parse_args()
    
    # Create necessary directories
    Path("logs").mkdir(exist_ok=True)
    Path("data").mkdir(exist_ok=True)
    
    try:
        # Create and configure the integration manager
        manager = TriumvirateIntegrationManager(args.config)
        
        # Update API configuration if provided
        config_manager = ConfigManager(args.config)
        config = config_manager.load_config()
        config.api_config["host"] = args.host
        config.api_config["port"] = args.port
        config_manager.save_config(config)
        
        # Setup logging
        if args.debug:
            import logging
            logging.basicConfig(
                level=logging.DEBUG,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                handlers=[
                    logging.FileHandler(args.log_file),
                    logging.StreamHandler(sys.stdout)
                ]
            )
        
        # Setup signal handlers for graceful shutdown
        setup_signal_handlers(manager)
        
        # Perform the requested action
        if args.action == "start":
            await start_system(manager, args)
        elif args.action == "stop":
            await stop_system(manager)
        elif args.action == "restart":
            await restart_system(manager, args)
        elif args.action == "status":
            await show_status(manager)
        elif args.action == "health":
            await show_health(manager)
        
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

async def start_system(manager, args):
    """Start the triumvirate integration system"""
    print("🚀 Starting Triumvirate Integration Layer...")
    
    # Initialize the system
    print("📦 Initializing system components...")
    if not await manager.initialize():
        print("❌ Failed to initialize system")
        sys.exit(1)
    
    # Start the system
    print("⚡ Starting all components...")
    if not await manager.start():
        print("❌ Failed to start system")
        sys.exit(1)
    
    # Show system status
    status = manager.get_status()
    print("\n✅ Triumvirtate Integration Layer started successfully!")
    print(f"🌐 API Server: http://{args.host}:{args.port}")
    print(f"📊 System Status: {status['system_status'].title()}")
    
    if not args.daemon:
        print("\n📈 Component Status:")
        for comp_name, comp_info in status["components"].items():
            status_icon = "🟢" if comp_info["running"] else "🔴"
            print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
        
        print(f"\n🔗 API Endpoints:")
        print(f"  • Health: http://{args.host}:{args.port}/api/v1/monitoring/health")
        print(f"  • Metrics: http://{args.host}:{args.port}/api/v1/monitoring/metrics")
        print(f"  • System Overview: http://{args.host}:{args.port}/api/v1/system/overview")
        
        print(f"\n📝 Logs: {args.log_file}")
        print("\nPress Ctrl+C to stop the system")
        
        # Keep running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutdown requested...")
    else:
        print("🔄 Running as daemon...")

async def stop_system(manager):
    """Stop the triumvirate integration system"""
    print("🛑 Stopping Triumvirate Integration Layer...")
    
    if not await manager.stop():
        print("❌ Failed to stop system properly")
        sys.exit(1)
    
    print("✅ System stopped successfully")

async def restart_system(manager, args):
    """Restart the triumvirate integration system"""
    print("🔄 Restarting Triumvirate Integration Layer...")
    
    if not await manager.restart():
        print("❌ Failed to restart system")
        sys.exit(1)
    
    print("✅ System restarted successfully")
    print(f"🌐 Available at: http://{args.host}:{args.port}")

async def show_status(manager):
    """Show system status"""
    status = manager.get_status()
    
    print("📊 Triumvirate Integration Layer Status")
    print("=" * 50)
    print(f"System Status: {status['system_status'].title()}")
    
    if status['startup_time']:
        from datetime import datetime
        startup_time = datetime.fromisoformat(status['startup_time'])
        uptime_seconds = (datetime.now() - startup_time).total_seconds()
        uptime_hours = int(uptime_seconds // 3600)
        uptime_minutes = int((uptime_seconds % 3600) // 60)
        print(f"Uptime: {uptime_hours}h {uptime_minutes}m")
    
    print("\n🔧 Components:")
    for comp_name, comp_info in status["components"].items():
        status_icon = "🟢" if comp_info["running"] else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
    
    print("\n🌐 Shared Infrastructure:")
    for infra_name, infra_status in status["shared_infrastructure"].items():
        status_icon = "🟢" if infra_status else "🔴"
        print(f"  {status_icon} {infra_name.replace('_', ' ').title()}: {'Running' if infra_status else 'Stopped'}")
    
    print("\n🚀 Revolutionary Capabilities:")
    for cap_name, cap_status in status["revolutionary_capabilities"].items():
        status_icon = "🟢" if cap_status else "🔴"
        print(f"  {status_icon} {cap_name.replace('_', ' ').title()}: {'Active' if cap_status else 'Inactive'}")

async def show_health(manager):
    """Show detailed health information"""
    print("🏥 Triumvirate Integration Layer Health Check")
    print("=" * 50)
    
    # Get system overview
    overview = manager.observability.get_system_overview()
    
    print(f"System Health: {overview['system_health']['status'].title()}")
    print(f"Health Score: {overview['system_health']['score']:.1f}%")
    
    print(f"\n📊 Metrics:")
    print(f"  • Total Components: {overview['total_components_tracked']}")
    print(f"  • Active Alerts: {overview['active_alerts']}")
    print(f"  • Critical Alerts: {overview['critical_alerts']}")
    
    print(f"\n🔍 Component Health:")
    for comp_name in ["agenta", "pranava", "antakhara"]:
        health = await getattr(manager, comp_name).get_health_status()
        status_icon = "🟢" if health["status"] == "healthy" else "🟡" if health["status"] == "degraded" else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {health['status']}")
    
    # Check integration health
    integration_status = manager.get_status()
    if integration_status['system_status'] == 'running':
        print(f"\n✅ Integration Status: HEALTHY")
    else:
        print(f"\n❌ Integration Status: UNHEALTHY")

if __name__ == "__main__":
    # Ensure we can handle KeyboardInterrupt properly
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)Setup logging configuration"""
Main entry point for Triumvirate Integration Layer

This script provides a command-line interface for managing the triumvirate
integration system, including initialization, startup, shutdown, and monitoring.
"""

import asyncio
import argparse
import sys
import signal
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from triumvirate_manager import TriumvirateIntegrationManager, setup_signal_handlers
from configs.config_manager import ConfigManager

async def main():
    """Main entry point for the triumvirate integration system"""
    parser = argparse.ArgumentParser(description="Triumvirate Integration Layer")
    parser.add_argument(
        "--config", 
        default="configs/integration_config.yaml",
        help="Configuration file path (default: configs/integration_config.yaml)"
    )
    parser.add_argument(
        "--action",
        choices=["start", "stop", "restart", "status", "health"],
        default="start",
        help="Action to perform (default: start)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="API server port (default: 8000)"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="API server host (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Run as daemon process"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    parser.add_argument(
        "--log-file",
        default="logs/triumvirate.log",
        help="Log file path (default: logs/triumvirate.log)"
    )
    
    args = parser.parse_args()
    
    # Create necessary directories
    Path("logs").mkdir(exist_ok=True)
    Path("data").mkdir(exist_ok=True)
    
    try:
        # Create and configure the integration manager
        manager = TriumvirateIntegrationManager(args.config)
        
        # Update API configuration if provided
        config_manager = ConfigManager(args.config)
        config = config_manager.load_config()
        config.api_config["host"] = args.host
        config.api_config["port"] = args.port
        config_manager.save_config(config)
        
        # Setup logging
        if args.debug:
            import logging
            logging.basicConfig(
                level=logging.DEBUG,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                handlers=[
                    logging.FileHandler(args.log_file),
                    logging.StreamHandler(sys.stdout)
                ]
            )
        
        # Setup signal handlers for graceful shutdown
        setup_signal_handlers(manager)
        
        # Perform the requested action
        if args.action == "start":
            await start_system(manager, args)
        elif args.action == "stop":
            await stop_system(manager)
        elif args.action == "restart":
            await restart_system(manager, args)
        elif args.action == "status":
            await show_status(manager)
        elif args.action == "health":
            await show_health(manager)
        
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

async def start_system(manager, args):
    """Start the triumvirate integration system"""
    print("🚀 Starting Triumvirate Integration Layer...")
    
    # Initialize the system
    print("📦 Initializing system components...")
    if not await manager.initialize():
        print("❌ Failed to initialize system")
        sys.exit(1)
    
    # Start the system
    print("⚡ Starting all components...")
    if not await manager.start():
        print("❌ Failed to start system")
        sys.exit(1)
    
    # Show system status
    status = manager.get_status()
    print("\n✅ Triumvirtate Integration Layer started successfully!")
    print(f"🌐 API Server: http://{args.host}:{args.port}")
    print(f"📊 System Status: {status['system_status'].title()}")
    
    if not args.daemon:
        print("\n📈 Component Status:")
        for comp_name, comp_info in status["components"].items():
            status_icon = "🟢" if comp_info["running"] else "🔴"
            print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
        
        print(f"\n🔗 API Endpoints:")
        print(f"  • Health: http://{args.host}:{args.port}/api/v1/monitoring/health")
        print(f"  • Metrics: http://{args.host}:{args.port}/api/v1/monitoring/metrics")
        print(f"  • System Overview: http://{args.host}:{args.port}/api/v1/system/overview")
        
        print(f"\n📝 Logs: {args.log_file}")
        print("\nPress Ctrl+C to stop the system")
        
        # Keep running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutdown requested...")
    else:
        print("🔄 Running as daemon...")

async def stop_system(manager):
    """Stop the triumvirate integration system"""
    print("🛑 Stopping Triumvirate Integration Layer...")
    
    if not await manager.stop():
        print("❌ Failed to stop system properly")
        sys.exit(1)
    
    print("✅ System stopped successfully")

async def restart_system(manager, args):
    """Restart the triumvirate integration system"""
    print("🔄 Restarting Triumvirate Integration Layer...")
    
    if not await manager.restart():
        print("❌ Failed to restart system")
        sys.exit(1)
    
    print("✅ System restarted successfully")
    print(f"🌐 Available at: http://{args.host}:{args.port}")

async def show_status(manager):
    """Show system status"""
    status = manager.get_status()
    
    print("📊 Triumvirate Integration Layer Status")
    print("=" * 50)
    print(f"System Status: {status['system_status'].title()}")
    
    if status['startup_time']:
        from datetime import datetime
        startup_time = datetime.fromisoformat(status['startup_time'])
        uptime_seconds = (datetime.now() - startup_time).total_seconds()
        uptime_hours = int(uptime_seconds // 3600)
        uptime_minutes = int((uptime_seconds % 3600) // 60)
        print(f"Uptime: {uptime_hours}h {uptime_minutes}m")
    
    print("\n🔧 Components:")
    for comp_name, comp_info in status["components"].items():
        status_icon = "🟢" if comp_info["running"] else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
    
    print("\n🌐 Shared Infrastructure:")
    for infra_name, infra_status in status["shared_infrastructure"].items():
        status_icon = "🟢" if infra_status else "🔴"
        print(f"  {status_icon} {infra_name.replace('_', ' ').title()}: {'Running' if infra_status else 'Stopped'}")
    
    print("\n🚀 Revolutionary Capabilities:")
    for cap_name, cap_status in status["revolutionary_capabilities"].items():
        status_icon = "🟢" if cap_status else "🔴"
        print(f"  {status_icon} {cap_name.replace('_', ' ').title()}: {'Active' if cap_status else 'Inactive'}")

async def show_health(manager):
    """Show detailed health information"""
    print("🏥 Triumvirate Integration Layer Health Check")
    print("=" * 50)
    
    # Get system overview
    overview = manager.observability.get_system_overview()
    
    print(f"System Health: {overview['system_health']['status'].title()}")
    print(f"Health Score: {overview['system_health']['score']:.1f}%")
    
    print(f"\n📊 Metrics:")
    print(f"  • Total Components: {overview['total_components_tracked']}")
    print(f"  • Active Alerts: {overview['active_alerts']}")
    print(f"  • Critical Alerts: {overview['critical_alerts']}")
    
    print(f"\n🔍 Component Health:")
    for comp_name in ["agenta", "pranava", "antakhara"]:
        health = await getattr(manager, comp_name).get_health_status()
        status_icon = "🟢" if health["status"] == "healthy" else "🟡" if health["status"] == "degraded" else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {health['status']}")
    
    # Check integration health
    integration_status = manager.get_status()
    if integration_status['system_status'] == 'running':
        print(f"\n✅ Integration Status: HEALTHY")
    else:
        print(f"\n❌ Integration Status: UNHEALTHY")

if __name__ == "__main__":
    # Ensure we can handle KeyboardInterrupt properly
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
        logging_config = self.config.logging
        
        # Configure logging
        logging.basicConfig(
            level=getattr(logging, logging_config.get("level", "INFO")),
            format=logging_config.get("format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"),
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler(logging_config.get("log_file", "logs/triumvirate.log"))
            ] if logging_config.get("file_logging", True) else [logging.StreamHandler(sys.stdout)]
        )
        
    async def _health_monitor_loop(self) -> None:
        """
Main entry point for Triumvirate Integration Layer

This script provides a command-line interface for managing the triumvirate
integration system, including initialization, startup, shutdown, and monitoring.
"""

import asyncio
import argparse
import sys
import signal
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from triumvirate_manager import TriumvirateIntegrationManager, setup_signal_handlers
from configs.config_manager import ConfigManager

async def main():
    """Main entry point for the triumvirate integration system"""
    parser = argparse.ArgumentParser(description="Triumvirate Integration Layer")
    parser.add_argument(
        "--config", 
        default="configs/integration_config.yaml",
        help="Configuration file path (default: configs/integration_config.yaml)"
    )
    parser.add_argument(
        "--action",
        choices=["start", "stop", "restart", "status", "health"],
        default="start",
        help="Action to perform (default: start)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="API server port (default: 8000)"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="API server host (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Run as daemon process"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    parser.add_argument(
        "--log-file",
        default="logs/triumvirate.log",
        help="Log file path (default: logs/triumvirate.log)"
    )
    
    args = parser.parse_args()
    
    # Create necessary directories
    Path("logs").mkdir(exist_ok=True)
    Path("data").mkdir(exist_ok=True)
    
    try:
        # Create and configure the integration manager
        manager = TriumvirateIntegrationManager(args.config)
        
        # Update API configuration if provided
        config_manager = ConfigManager(args.config)
        config = config_manager.load_config()
        config.api_config["host"] = args.host
        config.api_config["port"] = args.port
        config_manager.save_config(config)
        
        # Setup logging
        if args.debug:
            import logging
            logging.basicConfig(
                level=logging.DEBUG,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                handlers=[
                    logging.FileHandler(args.log_file),
                    logging.StreamHandler(sys.stdout)
                ]
            )
        
        # Setup signal handlers for graceful shutdown
        setup_signal_handlers(manager)
        
        # Perform the requested action
        if args.action == "start":
            await start_system(manager, args)
        elif args.action == "stop":
            await stop_system(manager)
        elif args.action == "restart":
            await restart_system(manager, args)
        elif args.action == "status":
            await show_status(manager)
        elif args.action == "health":
            await show_health(manager)
        
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

async def start_system(manager, args):
    """Start the triumvirate integration system"""
    print("🚀 Starting Triumvirate Integration Layer...")
    
    # Initialize the system
    print("📦 Initializing system components...")
    if not await manager.initialize():
        print("❌ Failed to initialize system")
        sys.exit(1)
    
    # Start the system
    print("⚡ Starting all components...")
    if not await manager.start():
        print("❌ Failed to start system")
        sys.exit(1)
    
    # Show system status
    status = manager.get_status()
    print("\n✅ Triumvirtate Integration Layer started successfully!")
    print(f"🌐 API Server: http://{args.host}:{args.port}")
    print(f"📊 System Status: {status['system_status'].title()}")
    
    if not args.daemon:
        print("\n📈 Component Status:")
        for comp_name, comp_info in status["components"].items():
            status_icon = "🟢" if comp_info["running"] else "🔴"
            print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
        
        print(f"\n🔗 API Endpoints:")
        print(f"  • Health: http://{args.host}:{args.port}/api/v1/monitoring/health")
        print(f"  • Metrics: http://{args.host}:{args.port}/api/v1/monitoring/metrics")
        print(f"  • System Overview: http://{args.host}:{args.port}/api/v1/system/overview")
        
        print(f"\n📝 Logs: {args.log_file}")
        print("\nPress Ctrl+C to stop the system")
        
        # Keep running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutdown requested...")
    else:
        print("🔄 Running as daemon...")

async def stop_system(manager):
    """Stop the triumvirate integration system"""
    print("🛑 Stopping Triumvirate Integration Layer...")
    
    if not await manager.stop():
        print("❌ Failed to stop system properly")
        sys.exit(1)
    
    print("✅ System stopped successfully")

async def restart_system(manager, args):
    """Restart the triumvirate integration system"""
    print("🔄 Restarting Triumvirate Integration Layer...")
    
    if not await manager.restart():
        print("❌ Failed to restart system")
        sys.exit(1)
    
    print("✅ System restarted successfully")
    print(f"🌐 Available at: http://{args.host}:{args.port}")

async def show_status(manager):
    """Show system status"""
    status = manager.get_status()
    
    print("📊 Triumvirate Integration Layer Status")
    print("=" * 50)
    print(f"System Status: {status['system_status'].title()}")
    
    if status['startup_time']:
        from datetime import datetime
        startup_time = datetime.fromisoformat(status['startup_time'])
        uptime_seconds = (datetime.now() - startup_time).total_seconds()
        uptime_hours = int(uptime_seconds // 3600)
        uptime_minutes = int((uptime_seconds % 3600) // 60)
        print(f"Uptime: {uptime_hours}h {uptime_minutes}m")
    
    print("\n🔧 Components:")
    for comp_name, comp_info in status["components"].items():
        status_icon = "🟢" if comp_info["running"] else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
    
    print("\n🌐 Shared Infrastructure:")
    for infra_name, infra_status in status["shared_infrastructure"].items():
        status_icon = "🟢" if infra_status else "🔴"
        print(f"  {status_icon} {infra_name.replace('_', ' ').title()}: {'Running' if infra_status else 'Stopped'}")
    
    print("\n🚀 Revolutionary Capabilities:")
    for cap_name, cap_status in status["revolutionary_capabilities"].items():
        status_icon = "🟢" if cap_status else "🔴"
        print(f"  {status_icon} {cap_name.replace('_', ' ').title()}: {'Active' if cap_status else 'Inactive'}")

async def show_health(manager):
    """Show detailed health information"""
    print("🏥 Triumvirate Integration Layer Health Check")
    print("=" * 50)
    
    # Get system overview
    overview = manager.observability.get_system_overview()
    
    print(f"System Health: {overview['system_health']['status'].title()}")
    print(f"Health Score: {overview['system_health']['score']:.1f}%")
    
    print(f"\n📊 Metrics:")
    print(f"  • Total Components: {overview['total_components_tracked']}")
    print(f"  • Active Alerts: {overview['active_alerts']}")
    print(f"  • Critical Alerts: {overview['critical_alerts']}")
    
    print(f"\n🔍 Component Health:")
    for comp_name in ["agenta", "pranava", "antakhara"]:
        health = await getattr(manager, comp_name).get_health_status()
        status_icon = "🟢" if health["status"] == "healthy" else "🟡" if health["status"] == "degraded" else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {health['status']}")
    
    # Check integration health
    integration_status = manager.get_status()
    if integration_status['system_status'] == 'running':
        print(f"\n✅ Integration Status: HEALTHY")
    else:
        print(f"\n❌ Integration Status: UNHEALTHY")

if __name__ == "__main__":
    # Ensure we can handle KeyboardInterrupt properly
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)Monitor health of all components"""
Main entry point for Triumvirate Integration Layer

This script provides a command-line interface for managing the triumvirate
integration system, including initialization, startup, shutdown, and monitoring.
"""

import asyncio
import argparse
import sys
import signal
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from triumvirate_manager import TriumvirateIntegrationManager, setup_signal_handlers
from configs.config_manager import ConfigManager

async def main():
    """Main entry point for the triumvirate integration system"""
    parser = argparse.ArgumentParser(description="Triumvirate Integration Layer")
    parser.add_argument(
        "--config", 
        default="configs/integration_config.yaml",
        help="Configuration file path (default: configs/integration_config.yaml)"
    )
    parser.add_argument(
        "--action",
        choices=["start", "stop", "restart", "status", "health"],
        default="start",
        help="Action to perform (default: start)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="API server port (default: 8000)"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="API server host (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Run as daemon process"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    parser.add_argument(
        "--log-file",
        default="logs/triumvirate.log",
        help="Log file path (default: logs/triumvirate.log)"
    )
    
    args = parser.parse_args()
    
    # Create necessary directories
    Path("logs").mkdir(exist_ok=True)
    Path("data").mkdir(exist_ok=True)
    
    try:
        # Create and configure the integration manager
        manager = TriumvirateIntegrationManager(args.config)
        
        # Update API configuration if provided
        config_manager = ConfigManager(args.config)
        config = config_manager.load_config()
        config.api_config["host"] = args.host
        config.api_config["port"] = args.port
        config_manager.save_config(config)
        
        # Setup logging
        if args.debug:
            import logging
            logging.basicConfig(
                level=logging.DEBUG,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                handlers=[
                    logging.FileHandler(args.log_file),
                    logging.StreamHandler(sys.stdout)
                ]
            )
        
        # Setup signal handlers for graceful shutdown
        setup_signal_handlers(manager)
        
        # Perform the requested action
        if args.action == "start":
            await start_system(manager, args)
        elif args.action == "stop":
            await stop_system(manager)
        elif args.action == "restart":
            await restart_system(manager, args)
        elif args.action == "status":
            await show_status(manager)
        elif args.action == "health":
            await show_health(manager)
        
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

async def start_system(manager, args):
    """Start the triumvirate integration system"""
    print("🚀 Starting Triumvirate Integration Layer...")
    
    # Initialize the system
    print("📦 Initializing system components...")
    if not await manager.initialize():
        print("❌ Failed to initialize system")
        sys.exit(1)
    
    # Start the system
    print("⚡ Starting all components...")
    if not await manager.start():
        print("❌ Failed to start system")
        sys.exit(1)
    
    # Show system status
    status = manager.get_status()
    print("\n✅ Triumvirtate Integration Layer started successfully!")
    print(f"🌐 API Server: http://{args.host}:{args.port}")
    print(f"📊 System Status: {status['system_status'].title()}")
    
    if not args.daemon:
        print("\n📈 Component Status:")
        for comp_name, comp_info in status["components"].items():
            status_icon = "🟢" if comp_info["running"] else "🔴"
            print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
        
        print(f"\n🔗 API Endpoints:")
        print(f"  • Health: http://{args.host}:{args.port}/api/v1/monitoring/health")
        print(f"  • Metrics: http://{args.host}:{args.port}/api/v1/monitoring/metrics")
        print(f"  • System Overview: http://{args.host}:{args.port}/api/v1/system/overview")
        
        print(f"\n📝 Logs: {args.log_file}")
        print("\nPress Ctrl+C to stop the system")
        
        # Keep running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutdown requested...")
    else:
        print("🔄 Running as daemon...")

async def stop_system(manager):
    """Stop the triumvirate integration system"""
    print("🛑 Stopping Triumvirate Integration Layer...")
    
    if not await manager.stop():
        print("❌ Failed to stop system properly")
        sys.exit(1)
    
    print("✅ System stopped successfully")

async def restart_system(manager, args):
    """Restart the triumvirate integration system"""
    print("🔄 Restarting Triumvirate Integration Layer...")
    
    if not await manager.restart():
        print("❌ Failed to restart system")
        sys.exit(1)
    
    print("✅ System restarted successfully")
    print(f"🌐 Available at: http://{args.host}:{args.port}")

async def show_status(manager):
    """Show system status"""
    status = manager.get_status()
    
    print("📊 Triumvirate Integration Layer Status")
    print("=" * 50)
    print(f"System Status: {status['system_status'].title()}")
    
    if status['startup_time']:
        from datetime import datetime
        startup_time = datetime.fromisoformat(status['startup_time'])
        uptime_seconds = (datetime.now() - startup_time).total_seconds()
        uptime_hours = int(uptime_seconds // 3600)
        uptime_minutes = int((uptime_seconds % 3600) // 60)
        print(f"Uptime: {uptime_hours}h {uptime_minutes}m")
    
    print("\n🔧 Components:")
    for comp_name, comp_info in status["components"].items():
        status_icon = "🟢" if comp_info["running"] else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
    
    print("\n🌐 Shared Infrastructure:")
    for infra_name, infra_status in status["shared_infrastructure"].items():
        status_icon = "🟢" if infra_status else "🔴"
        print(f"  {status_icon} {infra_name.replace('_', ' ').title()}: {'Running' if infra_status else 'Stopped'}")
    
    print("\n🚀 Revolutionary Capabilities:")
    for cap_name, cap_status in status["revolutionary_capabilities"].items():
        status_icon = "🟢" if cap_status else "🔴"
        print(f"  {status_icon} {cap_name.replace('_', ' ').title()}: {'Active' if cap_status else 'Inactive'}")

async def show_health(manager):
    """Show detailed health information"""
    print("🏥 Triumvirate Integration Layer Health Check")
    print("=" * 50)
    
    # Get system overview
    overview = manager.observability.get_system_overview()
    
    print(f"System Health: {overview['system_health']['status'].title()}")
    print(f"Health Score: {overview['system_health']['score']:.1f}%")
    
    print(f"\n📊 Metrics:")
    print(f"  • Total Components: {overview['total_components_tracked']}")
    print(f"  • Active Alerts: {overview['active_alerts']}")
    print(f"  • Critical Alerts: {overview['critical_alerts']}")
    
    print(f"\n🔍 Component Health:")
    for comp_name in ["agenta", "pranava", "antakhara"]:
        health = await getattr(manager, comp_name).get_health_status()
        status_icon = "🟢" if health["status"] == "healthy" else "🟡" if health["status"] == "degraded" else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {health['status']}")
    
    # Check integration health
    integration_status = manager.get_status()
    if integration_status['system_status'] == 'running':
        print(f"\n✅ Integration Status: HEALTHY")
    else:
        print(f"\n❌ Integration Status: UNHEALTHY")

if __name__ == "__main__":
    # Ensure we can handle KeyboardInterrupt properly
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
        while True:
            try:
                # Check component health
                if self.agenta:
                    health = await self.agenta.get_health_status()
                    self.component_health["agenta"] = health
                    self.observability.update_component_health("agenta", health["status"], health)
                    
                if self.pranava:
                    health = await self.pranava.get_health_status()
                    self.component_health["pranava"] = health
                    self.observability.update_component_health("pranava", health["status"], health)
                    
                if self.antakhara:
                    health = await self.antakhara.get_health_status()
                    self.component_health["antakhara"] = health
                    self.observability.update_component_health("antakhara", health["status"], health)
                    
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Health monitoring error: {e}")
                await asyncio.sleep(30)
                
    async def _integration_health_loop(self) -> None:
        """
Main entry point for Triumvirate Integration Layer

This script provides a command-line interface for managing the triumvirate
integration system, including initialization, startup, shutdown, and monitoring.
"""

import asyncio
import argparse
import sys
import signal
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from triumvirate_manager import TriumvirateIntegrationManager, setup_signal_handlers
from configs.config_manager import ConfigManager

async def main():
    """Main entry point for the triumvirate integration system"""
    parser = argparse.ArgumentParser(description="Triumvirate Integration Layer")
    parser.add_argument(
        "--config", 
        default="configs/integration_config.yaml",
        help="Configuration file path (default: configs/integration_config.yaml)"
    )
    parser.add_argument(
        "--action",
        choices=["start", "stop", "restart", "status", "health"],
        default="start",
        help="Action to perform (default: start)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="API server port (default: 8000)"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="API server host (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Run as daemon process"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    parser.add_argument(
        "--log-file",
        default="logs/triumvirate.log",
        help="Log file path (default: logs/triumvirate.log)"
    )
    
    args = parser.parse_args()
    
    # Create necessary directories
    Path("logs").mkdir(exist_ok=True)
    Path("data").mkdir(exist_ok=True)
    
    try:
        # Create and configure the integration manager
        manager = TriumvirateIntegrationManager(args.config)
        
        # Update API configuration if provided
        config_manager = ConfigManager(args.config)
        config = config_manager.load_config()
        config.api_config["host"] = args.host
        config.api_config["port"] = args.port
        config_manager.save_config(config)
        
        # Setup logging
        if args.debug:
            import logging
            logging.basicConfig(
                level=logging.DEBUG,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                handlers=[
                    logging.FileHandler(args.log_file),
                    logging.StreamHandler(sys.stdout)
                ]
            )
        
        # Setup signal handlers for graceful shutdown
        setup_signal_handlers(manager)
        
        # Perform the requested action
        if args.action == "start":
            await start_system(manager, args)
        elif args.action == "stop":
            await stop_system(manager)
        elif args.action == "restart":
            await restart_system(manager, args)
        elif args.action == "status":
            await show_status(manager)
        elif args.action == "health":
            await show_health(manager)
        
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

async def start_system(manager, args):
    """Start the triumvirate integration system"""
    print("🚀 Starting Triumvirate Integration Layer...")
    
    # Initialize the system
    print("📦 Initializing system components...")
    if not await manager.initialize():
        print("❌ Failed to initialize system")
        sys.exit(1)
    
    # Start the system
    print("⚡ Starting all components...")
    if not await manager.start():
        print("❌ Failed to start system")
        sys.exit(1)
    
    # Show system status
    status = manager.get_status()
    print("\n✅ Triumvirtate Integration Layer started successfully!")
    print(f"🌐 API Server: http://{args.host}:{args.port}")
    print(f"📊 System Status: {status['system_status'].title()}")
    
    if not args.daemon:
        print("\n📈 Component Status:")
        for comp_name, comp_info in status["components"].items():
            status_icon = "🟢" if comp_info["running"] else "🔴"
            print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
        
        print(f"\n🔗 API Endpoints:")
        print(f"  • Health: http://{args.host}:{args.port}/api/v1/monitoring/health")
        print(f"  • Metrics: http://{args.host}:{args.port}/api/v1/monitoring/metrics")
        print(f"  • System Overview: http://{args.host}:{args.port}/api/v1/system/overview")
        
        print(f"\n📝 Logs: {args.log_file}")
        print("\nPress Ctrl+C to stop the system")
        
        # Keep running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutdown requested...")
    else:
        print("🔄 Running as daemon...")

async def stop_system(manager):
    """Stop the triumvirate integration system"""
    print("🛑 Stopping Triumvirate Integration Layer...")
    
    if not await manager.stop():
        print("❌ Failed to stop system properly")
        sys.exit(1)
    
    print("✅ System stopped successfully")

async def restart_system(manager, args):
    """Restart the triumvirate integration system"""
    print("🔄 Restarting Triumvirate Integration Layer...")
    
    if not await manager.restart():
        print("❌ Failed to restart system")
        sys.exit(1)
    
    print("✅ System restarted successfully")
    print(f"🌐 Available at: http://{args.host}:{args.port}")

async def show_status(manager):
    """Show system status"""
    status = manager.get_status()
    
    print("📊 Triumvirate Integration Layer Status")
    print("=" * 50)
    print(f"System Status: {status['system_status'].title()}")
    
    if status['startup_time']:
        from datetime import datetime
        startup_time = datetime.fromisoformat(status['startup_time'])
        uptime_seconds = (datetime.now() - startup_time).total_seconds()
        uptime_hours = int(uptime_seconds // 3600)
        uptime_minutes = int((uptime_seconds % 3600) // 60)
        print(f"Uptime: {uptime_hours}h {uptime_minutes}m")
    
    print("\n🔧 Components:")
    for comp_name, comp_info in status["components"].items():
        status_icon = "🟢" if comp_info["running"] else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
    
    print("\n🌐 Shared Infrastructure:")
    for infra_name, infra_status in status["shared_infrastructure"].items():
        status_icon = "🟢" if infra_status else "🔴"
        print(f"  {status_icon} {infra_name.replace('_', ' ').title()}: {'Running' if infra_status else 'Stopped'}")
    
    print("\n🚀 Revolutionary Capabilities:")
    for cap_name, cap_status in status["revolutionary_capabilities"].items():
        status_icon = "🟢" if cap_status else "🔴"
        print(f"  {status_icon} {cap_name.replace('_', ' ').title()}: {'Active' if cap_status else 'Inactive'}")

async def show_health(manager):
    """Show detailed health information"""
    print("🏥 Triumvirate Integration Layer Health Check")
    print("=" * 50)
    
    # Get system overview
    overview = manager.observability.get_system_overview()
    
    print(f"System Health: {overview['system_health']['status'].title()}")
    print(f"Health Score: {overview['system_health']['score']:.1f}%")
    
    print(f"\n📊 Metrics:")
    print(f"  • Total Components: {overview['total_components_tracked']}")
    print(f"  • Active Alerts: {overview['active_alerts']}")
    print(f"  • Critical Alerts: {overview['critical_alerts']}")
    
    print(f"\n🔍 Component Health:")
    for comp_name in ["agenta", "pranava", "antakhara"]:
        health = await getattr(manager, comp_name).get_health_status()
        status_icon = "🟢" if health["status"] == "healthy" else "🟡" if health["status"] == "degraded" else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {health['status']}")
    
    # Check integration health
    integration_status = manager.get_status()
    if integration_status['system_status'] == 'running':
        print(f"\n✅ Integration Status: HEALTHY")
    else:
        print(f"\n❌ Integration Status: UNHEALTHY")

if __name__ == "__main__":
    # Ensure we can handle KeyboardInterrupt properly
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)Monitor integration health and perform diagnostics"""
Main entry point for Triumvirate Integration Layer

This script provides a command-line interface for managing the triumvirate
integration system, including initialization, startup, shutdown, and monitoring.
"""

import asyncio
import argparse
import sys
import signal
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from triumvirate_manager import TriumvirateIntegrationManager, setup_signal_handlers
from configs.config_manager import ConfigManager

async def main():
    """Main entry point for the triumvirate integration system"""
    parser = argparse.ArgumentParser(description="Triumvirate Integration Layer")
    parser.add_argument(
        "--config", 
        default="configs/integration_config.yaml",
        help="Configuration file path (default: configs/integration_config.yaml)"
    )
    parser.add_argument(
        "--action",
        choices=["start", "stop", "restart", "status", "health"],
        default="start",
        help="Action to perform (default: start)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="API server port (default: 8000)"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="API server host (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Run as daemon process"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    parser.add_argument(
        "--log-file",
        default="logs/triumvirate.log",
        help="Log file path (default: logs/triumvirate.log)"
    )
    
    args = parser.parse_args()
    
    # Create necessary directories
    Path("logs").mkdir(exist_ok=True)
    Path("data").mkdir(exist_ok=True)
    
    try:
        # Create and configure the integration manager
        manager = TriumvirateIntegrationManager(args.config)
        
        # Update API configuration if provided
        config_manager = ConfigManager(args.config)
        config = config_manager.load_config()
        config.api_config["host"] = args.host
        config.api_config["port"] = args.port
        config_manager.save_config(config)
        
        # Setup logging
        if args.debug:
            import logging
            logging.basicConfig(
                level=logging.DEBUG,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                handlers=[
                    logging.FileHandler(args.log_file),
                    logging.StreamHandler(sys.stdout)
                ]
            )
        
        # Setup signal handlers for graceful shutdown
        setup_signal_handlers(manager)
        
        # Perform the requested action
        if args.action == "start":
            await start_system(manager, args)
        elif args.action == "stop":
            await stop_system(manager)
        elif args.action == "restart":
            await restart_system(manager, args)
        elif args.action == "status":
            await show_status(manager)
        elif args.action == "health":
            await show_health(manager)
        
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

async def start_system(manager, args):
    """Start the triumvirate integration system"""
    print("🚀 Starting Triumvirate Integration Layer...")
    
    # Initialize the system
    print("📦 Initializing system components...")
    if not await manager.initialize():
        print("❌ Failed to initialize system")
        sys.exit(1)
    
    # Start the system
    print("⚡ Starting all components...")
    if not await manager.start():
        print("❌ Failed to start system")
        sys.exit(1)
    
    # Show system status
    status = manager.get_status()
    print("\n✅ Triumvirtate Integration Layer started successfully!")
    print(f"🌐 API Server: http://{args.host}:{args.port}")
    print(f"📊 System Status: {status['system_status'].title()}")
    
    if not args.daemon:
        print("\n📈 Component Status:")
        for comp_name, comp_info in status["components"].items():
            status_icon = "🟢" if comp_info["running"] else "🔴"
            print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
        
        print(f"\n🔗 API Endpoints:")
        print(f"  • Health: http://{args.host}:{args.port}/api/v1/monitoring/health")
        print(f"  • Metrics: http://{args.host}:{args.port}/api/v1/monitoring/metrics")
        print(f"  • System Overview: http://{args.host}:{args.port}/api/v1/system/overview")
        
        print(f"\n📝 Logs: {args.log_file}")
        print("\nPress Ctrl+C to stop the system")
        
        # Keep running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutdown requested...")
    else:
        print("🔄 Running as daemon...")

async def stop_system(manager):
    """Stop the triumvirate integration system"""
    print("🛑 Stopping Triumvirate Integration Layer...")
    
    if not await manager.stop():
        print("❌ Failed to stop system properly")
        sys.exit(1)
    
    print("✅ System stopped successfully")

async def restart_system(manager, args):
    """Restart the triumvirate integration system"""
    print("🔄 Restarting Triumvirate Integration Layer...")
    
    if not await manager.restart():
        print("❌ Failed to restart system")
        sys.exit(1)
    
    print("✅ System restarted successfully")
    print(f"🌐 Available at: http://{args.host}:{args.port}")

async def show_status(manager):
    """Show system status"""
    status = manager.get_status()
    
    print("📊 Triumvirate Integration Layer Status")
    print("=" * 50)
    print(f"System Status: {status['system_status'].title()}")
    
    if status['startup_time']:
        from datetime import datetime
        startup_time = datetime.fromisoformat(status['startup_time'])
        uptime_seconds = (datetime.now() - startup_time).total_seconds()
        uptime_hours = int(uptime_seconds // 3600)
        uptime_minutes = int((uptime_seconds % 3600) // 60)
        print(f"Uptime: {uptime_hours}h {uptime_minutes}m")
    
    print("\n🔧 Components:")
    for comp_name, comp_info in status["components"].items():
        status_icon = "🟢" if comp_info["running"] else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
    
    print("\n🌐 Shared Infrastructure:")
    for infra_name, infra_status in status["shared_infrastructure"].items():
        status_icon = "🟢" if infra_status else "🔴"
        print(f"  {status_icon} {infra_name.replace('_', ' ').title()}: {'Running' if infra_status else 'Stopped'}")
    
    print("\n🚀 Revolutionary Capabilities:")
    for cap_name, cap_status in status["revolutionary_capabilities"].items():
        status_icon = "🟢" if cap_status else "🔴"
        print(f"  {status_icon} {cap_name.replace('_', ' ').title()}: {'Active' if cap_status else 'Inactive'}")

async def show_health(manager):
    """Show detailed health information"""
    print("🏥 Triumvirate Integration Layer Health Check")
    print("=" * 50)
    
    # Get system overview
    overview = manager.observability.get_system_overview()
    
    print(f"System Health: {overview['system_health']['status'].title()}")
    print(f"Health Score: {overview['system_health']['score']:.1f}%")
    
    print(f"\n📊 Metrics:")
    print(f"  • Total Components: {overview['total_components_tracked']}")
    print(f"  • Active Alerts: {overview['active_alerts']}")
    print(f"  • Critical Alerts: {overview['critical_alerts']}")
    
    print(f"\n🔍 Component Health:")
    for comp_name in ["agenta", "pranava", "antakhara"]:
        health = await getattr(manager, comp_name).get_health_status()
        status_icon = "🟢" if health["status"] == "healthy" else "🟡" if health["status"] == "degraded" else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {health['status']}")
    
    # Check integration health
    integration_status = manager.get_status()
    if integration_status['system_status'] == 'running':
        print(f"\n✅ Integration Status: HEALTHY")
    else:
        print(f"\n❌ Integration Status: UNHEALTHY")

if __name__ == "__main__":
    # Ensure we can handle KeyboardInterrupt properly
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
        while True:
            try:
                # Check integration health
                status = self.get_status()
                
                # Report integration health
                self.observability.set_gauge("integration.health_score", self._calculate_health_score(status), "integration")
                
                # Check for integration issues
                integration_issues = self._detect_integration_issues(status)
                if integration_issues:
                    self.logger.warning(f"Integration issues detected: {integration_issues}")
                    
                await asyncio.sleep(60)  # Check every minute
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Integration health monitoring error: {e}")
                await asyncio.sleep(60)
                
    def _calculate_health_score(self, status: Dict[str, Any]) -> float:
        """
Main entry point for Triumvirate Integration Layer

This script provides a command-line interface for managing the triumvirate
integration system, including initialization, startup, shutdown, and monitoring.
"""

import asyncio
import argparse
import sys
import signal
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from triumvirate_manager import TriumvirateIntegrationManager, setup_signal_handlers
from configs.config_manager import ConfigManager

async def main():
    """Main entry point for the triumvirate integration system"""
    parser = argparse.ArgumentParser(description="Triumvirate Integration Layer")
    parser.add_argument(
        "--config", 
        default="configs/integration_config.yaml",
        help="Configuration file path (default: configs/integration_config.yaml)"
    )
    parser.add_argument(
        "--action",
        choices=["start", "stop", "restart", "status", "health"],
        default="start",
        help="Action to perform (default: start)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="API server port (default: 8000)"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="API server host (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Run as daemon process"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    parser.add_argument(
        "--log-file",
        default="logs/triumvirate.log",
        help="Log file path (default: logs/triumvirate.log)"
    )
    
    args = parser.parse_args()
    
    # Create necessary directories
    Path("logs").mkdir(exist_ok=True)
    Path("data").mkdir(exist_ok=True)
    
    try:
        # Create and configure the integration manager
        manager = TriumvirateIntegrationManager(args.config)
        
        # Update API configuration if provided
        config_manager = ConfigManager(args.config)
        config = config_manager.load_config()
        config.api_config["host"] = args.host
        config.api_config["port"] = args.port
        config_manager.save_config(config)
        
        # Setup logging
        if args.debug:
            import logging
            logging.basicConfig(
                level=logging.DEBUG,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                handlers=[
                    logging.FileHandler(args.log_file),
                    logging.StreamHandler(sys.stdout)
                ]
            )
        
        # Setup signal handlers for graceful shutdown
        setup_signal_handlers(manager)
        
        # Perform the requested action
        if args.action == "start":
            await start_system(manager, args)
        elif args.action == "stop":
            await stop_system(manager)
        elif args.action == "restart":
            await restart_system(manager, args)
        elif args.action == "status":
            await show_status(manager)
        elif args.action == "health":
            await show_health(manager)
        
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

async def start_system(manager, args):
    """Start the triumvirate integration system"""
    print("🚀 Starting Triumvirate Integration Layer...")
    
    # Initialize the system
    print("📦 Initializing system components...")
    if not await manager.initialize():
        print("❌ Failed to initialize system")
        sys.exit(1)
    
    # Start the system
    print("⚡ Starting all components...")
    if not await manager.start():
        print("❌ Failed to start system")
        sys.exit(1)
    
    # Show system status
    status = manager.get_status()
    print("\n✅ Triumvirtate Integration Layer started successfully!")
    print(f"🌐 API Server: http://{args.host}:{args.port}")
    print(f"📊 System Status: {status['system_status'].title()}")
    
    if not args.daemon:
        print("\n📈 Component Status:")
        for comp_name, comp_info in status["components"].items():
            status_icon = "🟢" if comp_info["running"] else "🔴"
            print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
        
        print(f"\n🔗 API Endpoints:")
        print(f"  • Health: http://{args.host}:{args.port}/api/v1/monitoring/health")
        print(f"  • Metrics: http://{args.host}:{args.port}/api/v1/monitoring/metrics")
        print(f"  • System Overview: http://{args.host}:{args.port}/api/v1/system/overview")
        
        print(f"\n📝 Logs: {args.log_file}")
        print("\nPress Ctrl+C to stop the system")
        
        # Keep running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutdown requested...")
    else:
        print("🔄 Running as daemon...")

async def stop_system(manager):
    """Stop the triumvirate integration system"""
    print("🛑 Stopping Triumvirate Integration Layer...")
    
    if not await manager.stop():
        print("❌ Failed to stop system properly")
        sys.exit(1)
    
    print("✅ System stopped successfully")

async def restart_system(manager, args):
    """Restart the triumvirate integration system"""
    print("🔄 Restarting Triumvirate Integration Layer...")
    
    if not await manager.restart():
        print("❌ Failed to restart system")
        sys.exit(1)
    
    print("✅ System restarted successfully")
    print(f"🌐 Available at: http://{args.host}:{args.port}")

async def show_status(manager):
    """Show system status"""
    status = manager.get_status()
    
    print("📊 Triumvirate Integration Layer Status")
    print("=" * 50)
    print(f"System Status: {status['system_status'].title()}")
    
    if status['startup_time']:
        from datetime import datetime
        startup_time = datetime.fromisoformat(status['startup_time'])
        uptime_seconds = (datetime.now() - startup_time).total_seconds()
        uptime_hours = int(uptime_seconds // 3600)
        uptime_minutes = int((uptime_seconds % 3600) // 60)
        print(f"Uptime: {uptime_hours}h {uptime_minutes}m")
    
    print("\n🔧 Components:")
    for comp_name, comp_info in status["components"].items():
        status_icon = "🟢" if comp_info["running"] else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
    
    print("\n🌐 Shared Infrastructure:")
    for infra_name, infra_status in status["shared_infrastructure"].items():
        status_icon = "🟢" if infra_status else "🔴"
        print(f"  {status_icon} {infra_name.replace('_', ' ').title()}: {'Running' if infra_status else 'Stopped'}")
    
    print("\n🚀 Revolutionary Capabilities:")
    for cap_name, cap_status in status["revolutionary_capabilities"].items():
        status_icon = "🟢" if cap_status else "🔴"
        print(f"  {status_icon} {cap_name.replace('_', ' ').title()}: {'Active' if cap_status else 'Inactive'}")

async def show_health(manager):
    """Show detailed health information"""
    print("🏥 Triumvirate Integration Layer Health Check")
    print("=" * 50)
    
    # Get system overview
    overview = manager.observability.get_system_overview()
    
    print(f"System Health: {overview['system_health']['status'].title()}")
    print(f"Health Score: {overview['system_health']['score']:.1f}%")
    
    print(f"\n📊 Metrics:")
    print(f"  • Total Components: {overview['total_components_tracked']}")
    print(f"  • Active Alerts: {overview['active_alerts']}")
    print(f"  • Critical Alerts: {overview['critical_alerts']}")
    
    print(f"\n🔍 Component Health:")
    for comp_name in ["agenta", "pranava", "antakhara"]:
        health = await getattr(manager, comp_name).get_health_status()
        status_icon = "🟢" if health["status"] == "healthy" else "🟡" if health["status"] == "degraded" else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {health['status']}")
    
    # Check integration health
    integration_status = manager.get_status()
    if integration_status['system_status'] == 'running':
        print(f"\n✅ Integration Status: HEALTHY")
    else:
        print(f"\n❌ Integration Status: UNHEALTHY")

if __name__ == "__main__":
    # Ensure we can handle KeyboardInterrupt properly
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)Calculate overall system health score"""
Main entry point for Triumvirate Integration Layer

This script provides a command-line interface for managing the triumvirate
integration system, including initialization, startup, shutdown, and monitoring.
"""

import asyncio
import argparse
import sys
import signal
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from triumvirate_manager import TriumvirateIntegrationManager, setup_signal_handlers
from configs.config_manager import ConfigManager

async def main():
    """Main entry point for the triumvirate integration system"""
    parser = argparse.ArgumentParser(description="Triumvirate Integration Layer")
    parser.add_argument(
        "--config", 
        default="configs/integration_config.yaml",
        help="Configuration file path (default: configs/integration_config.yaml)"
    )
    parser.add_argument(
        "--action",
        choices=["start", "stop", "restart", "status", "health"],
        default="start",
        help="Action to perform (default: start)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="API server port (default: 8000)"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="API server host (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Run as daemon process"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    parser.add_argument(
        "--log-file",
        default="logs/triumvirate.log",
        help="Log file path (default: logs/triumvirate.log)"
    )
    
    args = parser.parse_args()
    
    # Create necessary directories
    Path("logs").mkdir(exist_ok=True)
    Path("data").mkdir(exist_ok=True)
    
    try:
        # Create and configure the integration manager
        manager = TriumvirateIntegrationManager(args.config)
        
        # Update API configuration if provided
        config_manager = ConfigManager(args.config)
        config = config_manager.load_config()
        config.api_config["host"] = args.host
        config.api_config["port"] = args.port
        config_manager.save_config(config)
        
        # Setup logging
        if args.debug:
            import logging
            logging.basicConfig(
                level=logging.DEBUG,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                handlers=[
                    logging.FileHandler(args.log_file),
                    logging.StreamHandler(sys.stdout)
                ]
            )
        
        # Setup signal handlers for graceful shutdown
        setup_signal_handlers(manager)
        
        # Perform the requested action
        if args.action == "start":
            await start_system(manager, args)
        elif args.action == "stop":
            await stop_system(manager)
        elif args.action == "restart":
            await restart_system(manager, args)
        elif args.action == "status":
            await show_status(manager)
        elif args.action == "health":
            await show_health(manager)
        
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

async def start_system(manager, args):
    """Start the triumvirate integration system"""
    print("🚀 Starting Triumvirate Integration Layer...")
    
    # Initialize the system
    print("📦 Initializing system components...")
    if not await manager.initialize():
        print("❌ Failed to initialize system")
        sys.exit(1)
    
    # Start the system
    print("⚡ Starting all components...")
    if not await manager.start():
        print("❌ Failed to start system")
        sys.exit(1)
    
    # Show system status
    status = manager.get_status()
    print("\n✅ Triumvirtate Integration Layer started successfully!")
    print(f"🌐 API Server: http://{args.host}:{args.port}")
    print(f"📊 System Status: {status['system_status'].title()}")
    
    if not args.daemon:
        print("\n📈 Component Status:")
        for comp_name, comp_info in status["components"].items():
            status_icon = "🟢" if comp_info["running"] else "🔴"
            print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
        
        print(f"\n🔗 API Endpoints:")
        print(f"  • Health: http://{args.host}:{args.port}/api/v1/monitoring/health")
        print(f"  • Metrics: http://{args.host}:{args.port}/api/v1/monitoring/metrics")
        print(f"  • System Overview: http://{args.host}:{args.port}/api/v1/system/overview")
        
        print(f"\n📝 Logs: {args.log_file}")
        print("\nPress Ctrl+C to stop the system")
        
        # Keep running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutdown requested...")
    else:
        print("🔄 Running as daemon...")

async def stop_system(manager):
    """Stop the triumvirate integration system"""
    print("🛑 Stopping Triumvirate Integration Layer...")
    
    if not await manager.stop():
        print("❌ Failed to stop system properly")
        sys.exit(1)
    
    print("✅ System stopped successfully")

async def restart_system(manager, args):
    """Restart the triumvirate integration system"""
    print("🔄 Restarting Triumvirate Integration Layer...")
    
    if not await manager.restart():
        print("❌ Failed to restart system")
        sys.exit(1)
    
    print("✅ System restarted successfully")
    print(f"🌐 Available at: http://{args.host}:{args.port}")

async def show_status(manager):
    """Show system status"""
    status = manager.get_status()
    
    print("📊 Triumvirate Integration Layer Status")
    print("=" * 50)
    print(f"System Status: {status['system_status'].title()}")
    
    if status['startup_time']:
        from datetime import datetime
        startup_time = datetime.fromisoformat(status['startup_time'])
        uptime_seconds = (datetime.now() - startup_time).total_seconds()
        uptime_hours = int(uptime_seconds // 3600)
        uptime_minutes = int((uptime_seconds % 3600) // 60)
        print(f"Uptime: {uptime_hours}h {uptime_minutes}m")
    
    print("\n🔧 Components:")
    for comp_name, comp_info in status["components"].items():
        status_icon = "🟢" if comp_info["running"] else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
    
    print("\n🌐 Shared Infrastructure:")
    for infra_name, infra_status in status["shared_infrastructure"].items():
        status_icon = "🟢" if infra_status else "🔴"
        print(f"  {status_icon} {infra_name.replace('_', ' ').title()}: {'Running' if infra_status else 'Stopped'}")
    
    print("\n🚀 Revolutionary Capabilities:")
    for cap_name, cap_status in status["revolutionary_capabilities"].items():
        status_icon = "🟢" if cap_status else "🔴"
        print(f"  {status_icon} {cap_name.replace('_', ' ').title()}: {'Active' if cap_status else 'Inactive'}")

async def show_health(manager):
    """Show detailed health information"""
    print("🏥 Triumvirate Integration Layer Health Check")
    print("=" * 50)
    
    # Get system overview
    overview = manager.observability.get_system_overview()
    
    print(f"System Health: {overview['system_health']['status'].title()}")
    print(f"Health Score: {overview['system_health']['score']:.1f}%")
    
    print(f"\n📊 Metrics:")
    print(f"  • Total Components: {overview['total_components_tracked']}")
    print(f"  • Active Alerts: {overview['active_alerts']}")
    print(f"  • Critical Alerts: {overview['critical_alerts']}")
    
    print(f"\n🔍 Component Health:")
    for comp_name in ["agenta", "pranava", "antakhara"]:
        health = await getattr(manager, comp_name).get_health_status()
        status_icon = "🟢" if health["status"] == "healthy" else "🟡" if health["status"] == "degraded" else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {health['status']}")
    
    # Check integration health
    integration_status = manager.get_status()
    if integration_status['system_status'] == 'running':
        print(f"\n✅ Integration Status: HEALTHY")
    else:
        print(f"\n❌ Integration Status: UNHEALTHY")

if __name__ == "__main__":
    # Ensure we can handle KeyboardInterrupt properly
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
        score = 0.0
        
        # Component health (70% of score)
        components_score = 0.0
        component_count = 0
        for comp_name, comp_status in status["components"].items():
            if comp_status["running"]:
                if comp_status["status"] == "healthy":
                    components_score += 1.0
                elif comp_status["status"] == "degraded":
                    components_score += 0.5
            component_count += 1
            
        if component_count > 0:
            components_score = (components_score / component_count) * 0.7
            
        # Infrastructure health (20% of score)
        infrastructure_score = 0.0
        infrastructure_count = 0
        for infra_name, infra_status in status["shared_infrastructure"].items():
            if infra_status:
                infrastructure_score += 1.0
            infrastructure_count += 1
            
        if infrastructure_count > 0:
            infrastructure_score = (infrastructure_score / infrastructure_count) * 0.2
            
        # Revolutionary capabilities (10% of score)
        revolutionary_score = 0.0
        revolutionary_count = 0
        for cap_name, cap_status in status["revolutionary_capabilities"].items():
            if cap_status:
                revolutionary_score += 1.0
            revolutionary_count += 1
            
        if revolutionary_count > 0:
            revolutionary_score = (revolutionary_score / revolutionary_count) * 0.1
            
        return components_score + infrastructure_score + revolutionary_score
        
    def _detect_integration_issues(self, status: Dict[str, Any]) -> List[str]:
        """
Main entry point for Triumvirate Integration Layer

This script provides a command-line interface for managing the triumvirate
integration system, including initialization, startup, shutdown, and monitoring.
"""

import asyncio
import argparse
import sys
import signal
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from triumvirate_manager import TriumvirateIntegrationManager, setup_signal_handlers
from configs.config_manager import ConfigManager

async def main():
    """Main entry point for the triumvirate integration system"""
    parser = argparse.ArgumentParser(description="Triumvirate Integration Layer")
    parser.add_argument(
        "--config", 
        default="configs/integration_config.yaml",
        help="Configuration file path (default: configs/integration_config.yaml)"
    )
    parser.add_argument(
        "--action",
        choices=["start", "stop", "restart", "status", "health"],
        default="start",
        help="Action to perform (default: start)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="API server port (default: 8000)"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="API server host (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Run as daemon process"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    parser.add_argument(
        "--log-file",
        default="logs/triumvirate.log",
        help="Log file path (default: logs/triumvirate.log)"
    )
    
    args = parser.parse_args()
    
    # Create necessary directories
    Path("logs").mkdir(exist_ok=True)
    Path("data").mkdir(exist_ok=True)
    
    try:
        # Create and configure the integration manager
        manager = TriumvirateIntegrationManager(args.config)
        
        # Update API configuration if provided
        config_manager = ConfigManager(args.config)
        config = config_manager.load_config()
        config.api_config["host"] = args.host
        config.api_config["port"] = args.port
        config_manager.save_config(config)
        
        # Setup logging
        if args.debug:
            import logging
            logging.basicConfig(
                level=logging.DEBUG,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                handlers=[
                    logging.FileHandler(args.log_file),
                    logging.StreamHandler(sys.stdout)
                ]
            )
        
        # Setup signal handlers for graceful shutdown
        setup_signal_handlers(manager)
        
        # Perform the requested action
        if args.action == "start":
            await start_system(manager, args)
        elif args.action == "stop":
            await stop_system(manager)
        elif args.action == "restart":
            await restart_system(manager, args)
        elif args.action == "status":
            await show_status(manager)
        elif args.action == "health":
            await show_health(manager)
        
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

async def start_system(manager, args):
    """Start the triumvirate integration system"""
    print("🚀 Starting Triumvirate Integration Layer...")
    
    # Initialize the system
    print("📦 Initializing system components...")
    if not await manager.initialize():
        print("❌ Failed to initialize system")
        sys.exit(1)
    
    # Start the system
    print("⚡ Starting all components...")
    if not await manager.start():
        print("❌ Failed to start system")
        sys.exit(1)
    
    # Show system status
    status = manager.get_status()
    print("\n✅ Triumvirtate Integration Layer started successfully!")
    print(f"🌐 API Server: http://{args.host}:{args.port}")
    print(f"📊 System Status: {status['system_status'].title()}")
    
    if not args.daemon:
        print("\n📈 Component Status:")
        for comp_name, comp_info in status["components"].items():
            status_icon = "🟢" if comp_info["running"] else "🔴"
            print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
        
        print(f"\n🔗 API Endpoints:")
        print(f"  • Health: http://{args.host}:{args.port}/api/v1/monitoring/health")
        print(f"  • Metrics: http://{args.host}:{args.port}/api/v1/monitoring/metrics")
        print(f"  • System Overview: http://{args.host}:{args.port}/api/v1/system/overview")
        
        print(f"\n📝 Logs: {args.log_file}")
        print("\nPress Ctrl+C to stop the system")
        
        # Keep running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutdown requested...")
    else:
        print("🔄 Running as daemon...")

async def stop_system(manager):
    """Stop the triumvirate integration system"""
    print("🛑 Stopping Triumvirate Integration Layer...")
    
    if not await manager.stop():
        print("❌ Failed to stop system properly")
        sys.exit(1)
    
    print("✅ System stopped successfully")

async def restart_system(manager, args):
    """Restart the triumvirate integration system"""
    print("🔄 Restarting Triumvirate Integration Layer...")
    
    if not await manager.restart():
        print("❌ Failed to restart system")
        sys.exit(1)
    
    print("✅ System restarted successfully")
    print(f"🌐 Available at: http://{args.host}:{args.port}")

async def show_status(manager):
    """Show system status"""
    status = manager.get_status()
    
    print("📊 Triumvirate Integration Layer Status")
    print("=" * 50)
    print(f"System Status: {status['system_status'].title()}")
    
    if status['startup_time']:
        from datetime import datetime
        startup_time = datetime.fromisoformat(status['startup_time'])
        uptime_seconds = (datetime.now() - startup_time).total_seconds()
        uptime_hours = int(uptime_seconds // 3600)
        uptime_minutes = int((uptime_seconds % 3600) // 60)
        print(f"Uptime: {uptime_hours}h {uptime_minutes}m")
    
    print("\n🔧 Components:")
    for comp_name, comp_info in status["components"].items():
        status_icon = "🟢" if comp_info["running"] else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
    
    print("\n🌐 Shared Infrastructure:")
    for infra_name, infra_status in status["shared_infrastructure"].items():
        status_icon = "🟢" if infra_status else "🔴"
        print(f"  {status_icon} {infra_name.replace('_', ' ').title()}: {'Running' if infra_status else 'Stopped'}")
    
    print("\n🚀 Revolutionary Capabilities:")
    for cap_name, cap_status in status["revolutionary_capabilities"].items():
        status_icon = "🟢" if cap_status else "🔴"
        print(f"  {status_icon} {cap_name.replace('_', ' ').title()}: {'Active' if cap_status else 'Inactive'}")

async def show_health(manager):
    """Show detailed health information"""
    print("🏥 Triumvirate Integration Layer Health Check")
    print("=" * 50)
    
    # Get system overview
    overview = manager.observability.get_system_overview()
    
    print(f"System Health: {overview['system_health']['status'].title()}")
    print(f"Health Score: {overview['system_health']['score']:.1f}%")
    
    print(f"\n📊 Metrics:")
    print(f"  • Total Components: {overview['total_components_tracked']}")
    print(f"  • Active Alerts: {overview['active_alerts']}")
    print(f"  • Critical Alerts: {overview['critical_alerts']}")
    
    print(f"\n🔍 Component Health:")
    for comp_name in ["agenta", "pranava", "antakhara"]:
        health = await getattr(manager, comp_name).get_health_status()
        status_icon = "🟢" if health["status"] == "healthy" else "🟡" if health["status"] == "degraded" else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {health['status']}")
    
    # Check integration health
    integration_status = manager.get_status()
    if integration_status['system_status'] == 'running':
        print(f"\n✅ Integration Status: HEALTHY")
    else:
        print(f"\n❌ Integration Status: UNHEALTHY")

if __name__ == "__main__":
    # Ensure we can handle KeyboardInterrupt properly
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)Detect potential integration issues"""
Main entry point for Triumvirate Integration Layer

This script provides a command-line interface for managing the triumvirate
integration system, including initialization, startup, shutdown, and monitoring.
"""

import asyncio
import argparse
import sys
import signal
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from triumvirate_manager import TriumvirateIntegrationManager, setup_signal_handlers
from configs.config_manager import ConfigManager

async def main():
    """Main entry point for the triumvirate integration system"""
    parser = argparse.ArgumentParser(description="Triumvirate Integration Layer")
    parser.add_argument(
        "--config", 
        default="configs/integration_config.yaml",
        help="Configuration file path (default: configs/integration_config.yaml)"
    )
    parser.add_argument(
        "--action",
        choices=["start", "stop", "restart", "status", "health"],
        default="start",
        help="Action to perform (default: start)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="API server port (default: 8000)"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="API server host (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Run as daemon process"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    parser.add_argument(
        "--log-file",
        default="logs/triumvirate.log",
        help="Log file path (default: logs/triumvirate.log)"
    )
    
    args = parser.parse_args()
    
    # Create necessary directories
    Path("logs").mkdir(exist_ok=True)
    Path("data").mkdir(exist_ok=True)
    
    try:
        # Create and configure the integration manager
        manager = TriumvirateIntegrationManager(args.config)
        
        # Update API configuration if provided
        config_manager = ConfigManager(args.config)
        config = config_manager.load_config()
        config.api_config["host"] = args.host
        config.api_config["port"] = args.port
        config_manager.save_config(config)
        
        # Setup logging
        if args.debug:
            import logging
            logging.basicConfig(
                level=logging.DEBUG,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                handlers=[
                    logging.FileHandler(args.log_file),
                    logging.StreamHandler(sys.stdout)
                ]
            )
        
        # Setup signal handlers for graceful shutdown
        setup_signal_handlers(manager)
        
        # Perform the requested action
        if args.action == "start":
            await start_system(manager, args)
        elif args.action == "stop":
            await stop_system(manager)
        elif args.action == "restart":
            await restart_system(manager, args)
        elif args.action == "status":
            await show_status(manager)
        elif args.action == "health":
            await show_health(manager)
        
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

async def start_system(manager, args):
    """Start the triumvirate integration system"""
    print("🚀 Starting Triumvirate Integration Layer...")
    
    # Initialize the system
    print("📦 Initializing system components...")
    if not await manager.initialize():
        print("❌ Failed to initialize system")
        sys.exit(1)
    
    # Start the system
    print("⚡ Starting all components...")
    if not await manager.start():
        print("❌ Failed to start system")
        sys.exit(1)
    
    # Show system status
    status = manager.get_status()
    print("\n✅ Triumvirtate Integration Layer started successfully!")
    print(f"🌐 API Server: http://{args.host}:{args.port}")
    print(f"📊 System Status: {status['system_status'].title()}")
    
    if not args.daemon:
        print("\n📈 Component Status:")
        for comp_name, comp_info in status["components"].items():
            status_icon = "🟢" if comp_info["running"] else "🔴"
            print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
        
        print(f"\n🔗 API Endpoints:")
        print(f"  • Health: http://{args.host}:{args.port}/api/v1/monitoring/health")
        print(f"  • Metrics: http://{args.host}:{args.port}/api/v1/monitoring/metrics")
        print(f"  • System Overview: http://{args.host}:{args.port}/api/v1/system/overview")
        
        print(f"\n📝 Logs: {args.log_file}")
        print("\nPress Ctrl+C to stop the system")
        
        # Keep running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutdown requested...")
    else:
        print("🔄 Running as daemon...")

async def stop_system(manager):
    """Stop the triumvirate integration system"""
    print("🛑 Stopping Triumvirate Integration Layer...")
    
    if not await manager.stop():
        print("❌ Failed to stop system properly")
        sys.exit(1)
    
    print("✅ System stopped successfully")

async def restart_system(manager, args):
    """Restart the triumvirate integration system"""
    print("🔄 Restarting Triumvirate Integration Layer...")
    
    if not await manager.restart():
        print("❌ Failed to restart system")
        sys.exit(1)
    
    print("✅ System restarted successfully")
    print(f"🌐 Available at: http://{args.host}:{args.port}")

async def show_status(manager):
    """Show system status"""
    status = manager.get_status()
    
    print("📊 Triumvirate Integration Layer Status")
    print("=" * 50)
    print(f"System Status: {status['system_status'].title()}")
    
    if status['startup_time']:
        from datetime import datetime
        startup_time = datetime.fromisoformat(status['startup_time'])
        uptime_seconds = (datetime.now() - startup_time).total_seconds()
        uptime_hours = int(uptime_seconds // 3600)
        uptime_minutes = int((uptime_seconds % 3600) // 60)
        print(f"Uptime: {uptime_hours}h {uptime_minutes}m")
    
    print("\n🔧 Components:")
    for comp_name, comp_info in status["components"].items():
        status_icon = "🟢" if comp_info["running"] else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
    
    print("\n🌐 Shared Infrastructure:")
    for infra_name, infra_status in status["shared_infrastructure"].items():
        status_icon = "🟢" if infra_status else "🔴"
        print(f"  {status_icon} {infra_name.replace('_', ' ').title()}: {'Running' if infra_status else 'Stopped'}")
    
    print("\n🚀 Revolutionary Capabilities:")
    for cap_name, cap_status in status["revolutionary_capabilities"].items():
        status_icon = "🟢" if cap_status else "🔴"
        print(f"  {status_icon} {cap_name.replace('_', ' ').title()}: {'Active' if cap_status else 'Inactive'}")

async def show_health(manager):
    """Show detailed health information"""
    print("🏥 Triumvirate Integration Layer Health Check")
    print("=" * 50)
    
    # Get system overview
    overview = manager.observability.get_system_overview()
    
    print(f"System Health: {overview['system_health']['status'].title()}")
    print(f"Health Score: {overview['system_health']['score']:.1f}%")
    
    print(f"\n📊 Metrics:")
    print(f"  • Total Components: {overview['total_components_tracked']}")
    print(f"  • Active Alerts: {overview['active_alerts']}")
    print(f"  • Critical Alerts: {overview['critical_alerts']}")
    
    print(f"\n🔍 Component Health:")
    for comp_name in ["agenta", "pranava", "antakhara"]:
        health = await getattr(manager, comp_name).get_health_status()
        status_icon = "🟢" if health["status"] == "healthy" else "🟡" if health["status"] == "degraded" else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {health['status']}")
    
    # Check integration health
    integration_status = manager.get_status()
    if integration_status['system_status'] == 'running':
        print(f"\n✅ Integration Status: HEALTHY")
    else:
        print(f"\n❌ Integration Status: UNHEALTHY")

if __name__ == "__main__":
    # Ensure we can handle KeyboardInterrupt properly
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
        issues = []
        
        # Check if any components are not running
        for comp_name, comp_status in status["components"].items():
            if not comp_status["running"]:
                issues.append(f"{comp_name} is not running")
                
        # Check infrastructure
        for infra_name, infra_status in status["shared_infrastructure"].items():
            if not infra_status:
                issues.append(f"{infra_name} is not operational")
                
        return issues
        
    async def _handle_metric(self, metric) -> None:
        """
Main entry point for Triumvirate Integration Layer

This script provides a command-line interface for managing the triumvirate
integration system, including initialization, startup, shutdown, and monitoring.
"""

import asyncio
import argparse
import sys
import signal
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from triumvirate_manager import TriumvirateIntegrationManager, setup_signal_handlers
from configs.config_manager import ConfigManager

async def main():
    """Main entry point for the triumvirate integration system"""
    parser = argparse.ArgumentParser(description="Triumvirate Integration Layer")
    parser.add_argument(
        "--config", 
        default="configs/integration_config.yaml",
        help="Configuration file path (default: configs/integration_config.yaml)"
    )
    parser.add_argument(
        "--action",
        choices=["start", "stop", "restart", "status", "health"],
        default="start",
        help="Action to perform (default: start)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="API server port (default: 8000)"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="API server host (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Run as daemon process"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    parser.add_argument(
        "--log-file",
        default="logs/triumvirate.log",
        help="Log file path (default: logs/triumvirate.log)"
    )
    
    args = parser.parse_args()
    
    # Create necessary directories
    Path("logs").mkdir(exist_ok=True)
    Path("data").mkdir(exist_ok=True)
    
    try:
        # Create and configure the integration manager
        manager = TriumvirateIntegrationManager(args.config)
        
        # Update API configuration if provided
        config_manager = ConfigManager(args.config)
        config = config_manager.load_config()
        config.api_config["host"] = args.host
        config.api_config["port"] = args.port
        config_manager.save_config(config)
        
        # Setup logging
        if args.debug:
            import logging
            logging.basicConfig(
                level=logging.DEBUG,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                handlers=[
                    logging.FileHandler(args.log_file),
                    logging.StreamHandler(sys.stdout)
                ]
            )
        
        # Setup signal handlers for graceful shutdown
        setup_signal_handlers(manager)
        
        # Perform the requested action
        if args.action == "start":
            await start_system(manager, args)
        elif args.action == "stop":
            await stop_system(manager)
        elif args.action == "restart":
            await restart_system(manager, args)
        elif args.action == "status":
            await show_status(manager)
        elif args.action == "health":
            await show_health(manager)
        
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

async def start_system(manager, args):
    """Start the triumvirate integration system"""
    print("🚀 Starting Triumvirate Integration Layer...")
    
    # Initialize the system
    print("📦 Initializing system components...")
    if not await manager.initialize():
        print("❌ Failed to initialize system")
        sys.exit(1)
    
    # Start the system
    print("⚡ Starting all components...")
    if not await manager.start():
        print("❌ Failed to start system")
        sys.exit(1)
    
    # Show system status
    status = manager.get_status()
    print("\n✅ Triumvirtate Integration Layer started successfully!")
    print(f"🌐 API Server: http://{args.host}:{args.port}")
    print(f"📊 System Status: {status['system_status'].title()}")
    
    if not args.daemon:
        print("\n📈 Component Status:")
        for comp_name, comp_info in status["components"].items():
            status_icon = "🟢" if comp_info["running"] else "🔴"
            print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
        
        print(f"\n🔗 API Endpoints:")
        print(f"  • Health: http://{args.host}:{args.port}/api/v1/monitoring/health")
        print(f"  • Metrics: http://{args.host}:{args.port}/api/v1/monitoring/metrics")
        print(f"  • System Overview: http://{args.host}:{args.port}/api/v1/system/overview")
        
        print(f"\n📝 Logs: {args.log_file}")
        print("\nPress Ctrl+C to stop the system")
        
        # Keep running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutdown requested...")
    else:
        print("🔄 Running as daemon...")

async def stop_system(manager):
    """Stop the triumvirate integration system"""
    print("🛑 Stopping Triumvirate Integration Layer...")
    
    if not await manager.stop():
        print("❌ Failed to stop system properly")
        sys.exit(1)
    
    print("✅ System stopped successfully")

async def restart_system(manager, args):
    """Restart the triumvirate integration system"""
    print("🔄 Restarting Triumvirate Integration Layer...")
    
    if not await manager.restart():
        print("❌ Failed to restart system")
        sys.exit(1)
    
    print("✅ System restarted successfully")
    print(f"🌐 Available at: http://{args.host}:{args.port}")

async def show_status(manager):
    """Show system status"""
    status = manager.get_status()
    
    print("📊 Triumvirate Integration Layer Status")
    print("=" * 50)
    print(f"System Status: {status['system_status'].title()}")
    
    if status['startup_time']:
        from datetime import datetime
        startup_time = datetime.fromisoformat(status['startup_time'])
        uptime_seconds = (datetime.now() - startup_time).total_seconds()
        uptime_hours = int(uptime_seconds // 3600)
        uptime_minutes = int((uptime_seconds % 3600) // 60)
        print(f"Uptime: {uptime_hours}h {uptime_minutes}m")
    
    print("\n🔧 Components:")
    for comp_name, comp_info in status["components"].items():
        status_icon = "🟢" if comp_info["running"] else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
    
    print("\n🌐 Shared Infrastructure:")
    for infra_name, infra_status in status["shared_infrastructure"].items():
        status_icon = "🟢" if infra_status else "🔴"
        print(f"  {status_icon} {infra_name.replace('_', ' ').title()}: {'Running' if infra_status else 'Stopped'}")
    
    print("\n🚀 Revolutionary Capabilities:")
    for cap_name, cap_status in status["revolutionary_capabilities"].items():
        status_icon = "🟢" if cap_status else "🔴"
        print(f"  {status_icon} {cap_name.replace('_', ' ').title()}: {'Active' if cap_status else 'Inactive'}")

async def show_health(manager):
    """Show detailed health information"""
    print("🏥 Triumvirate Integration Layer Health Check")
    print("=" * 50)
    
    # Get system overview
    overview = manager.observability.get_system_overview()
    
    print(f"System Health: {overview['system_health']['status'].title()}")
    print(f"Health Score: {overview['system_health']['score']:.1f}%")
    
    print(f"\n📊 Metrics:")
    print(f"  • Total Components: {overview['total_components_tracked']}")
    print(f"  • Active Alerts: {overview['active_alerts']}")
    print(f"  • Critical Alerts: {overview['critical_alerts']}")
    
    print(f"\n🔍 Component Health:")
    for comp_name in ["agenta", "pranava", "antakhara"]:
        health = await getattr(manager, comp_name).get_health_status()
        status_icon = "🟢" if health["status"] == "healthy" else "🟡" if health["status"] == "degraded" else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {health['status']}")
    
    # Check integration health
    integration_status = manager.get_status()
    if integration_status['system_status'] == 'running':
        print(f"\n✅ Integration Status: HEALTHY")
    else:
        print(f"\n❌ Integration Status: UNHEALTHY")

if __name__ == "__main__":
    # Ensure we can handle KeyboardInterrupt properly
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)Handle metrics from observability system"""
Main entry point for Triumvirate Integration Layer

This script provides a command-line interface for managing the triumvirate
integration system, including initialization, startup, shutdown, and monitoring.
"""

import asyncio
import argparse
import sys
import signal
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from triumvirate_manager import TriumvirateIntegrationManager, setup_signal_handlers
from configs.config_manager import ConfigManager

async def main():
    """Main entry point for the triumvirate integration system"""
    parser = argparse.ArgumentParser(description="Triumvirate Integration Layer")
    parser.add_argument(
        "--config", 
        default="configs/integration_config.yaml",
        help="Configuration file path (default: configs/integration_config.yaml)"
    )
    parser.add_argument(
        "--action",
        choices=["start", "stop", "restart", "status", "health"],
        default="start",
        help="Action to perform (default: start)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="API server port (default: 8000)"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="API server host (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Run as daemon process"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    parser.add_argument(
        "--log-file",
        default="logs/triumvirate.log",
        help="Log file path (default: logs/triumvirate.log)"
    )
    
    args = parser.parse_args()
    
    # Create necessary directories
    Path("logs").mkdir(exist_ok=True)
    Path("data").mkdir(exist_ok=True)
    
    try:
        # Create and configure the integration manager
        manager = TriumvirateIntegrationManager(args.config)
        
        # Update API configuration if provided
        config_manager = ConfigManager(args.config)
        config = config_manager.load_config()
        config.api_config["host"] = args.host
        config.api_config["port"] = args.port
        config_manager.save_config(config)
        
        # Setup logging
        if args.debug:
            import logging
            logging.basicConfig(
                level=logging.DEBUG,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                handlers=[
                    logging.FileHandler(args.log_file),
                    logging.StreamHandler(sys.stdout)
                ]
            )
        
        # Setup signal handlers for graceful shutdown
        setup_signal_handlers(manager)
        
        # Perform the requested action
        if args.action == "start":
            await start_system(manager, args)
        elif args.action == "stop":
            await stop_system(manager)
        elif args.action == "restart":
            await restart_system(manager, args)
        elif args.action == "status":
            await show_status(manager)
        elif args.action == "health":
            await show_health(manager)
        
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

async def start_system(manager, args):
    """Start the triumvirate integration system"""
    print("🚀 Starting Triumvirate Integration Layer...")
    
    # Initialize the system
    print("📦 Initializing system components...")
    if not await manager.initialize():
        print("❌ Failed to initialize system")
        sys.exit(1)
    
    # Start the system
    print("⚡ Starting all components...")
    if not await manager.start():
        print("❌ Failed to start system")
        sys.exit(1)
    
    # Show system status
    status = manager.get_status()
    print("\n✅ Triumvirtate Integration Layer started successfully!")
    print(f"🌐 API Server: http://{args.host}:{args.port}")
    print(f"📊 System Status: {status['system_status'].title()}")
    
    if not args.daemon:
        print("\n📈 Component Status:")
        for comp_name, comp_info in status["components"].items():
            status_icon = "🟢" if comp_info["running"] else "🔴"
            print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
        
        print(f"\n🔗 API Endpoints:")
        print(f"  • Health: http://{args.host}:{args.port}/api/v1/monitoring/health")
        print(f"  • Metrics: http://{args.host}:{args.port}/api/v1/monitoring/metrics")
        print(f"  • System Overview: http://{args.host}:{args.port}/api/v1/system/overview")
        
        print(f"\n📝 Logs: {args.log_file}")
        print("\nPress Ctrl+C to stop the system")
        
        # Keep running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutdown requested...")
    else:
        print("🔄 Running as daemon...")

async def stop_system(manager):
    """Stop the triumvirate integration system"""
    print("🛑 Stopping Triumvirate Integration Layer...")
    
    if not await manager.stop():
        print("❌ Failed to stop system properly")
        sys.exit(1)
    
    print("✅ System stopped successfully")

async def restart_system(manager, args):
    """Restart the triumvirate integration system"""
    print("🔄 Restarting Triumvirate Integration Layer...")
    
    if not await manager.restart():
        print("❌ Failed to restart system")
        sys.exit(1)
    
    print("✅ System restarted successfully")
    print(f"🌐 Available at: http://{args.host}:{args.port}")

async def show_status(manager):
    """Show system status"""
    status = manager.get_status()
    
    print("📊 Triumvirate Integration Layer Status")
    print("=" * 50)
    print(f"System Status: {status['system_status'].title()}")
    
    if status['startup_time']:
        from datetime import datetime
        startup_time = datetime.fromisoformat(status['startup_time'])
        uptime_seconds = (datetime.now() - startup_time).total_seconds()
        uptime_hours = int(uptime_seconds // 3600)
        uptime_minutes = int((uptime_seconds % 3600) // 60)
        print(f"Uptime: {uptime_hours}h {uptime_minutes}m")
    
    print("\n🔧 Components:")
    for comp_name, comp_info in status["components"].items():
        status_icon = "🟢" if comp_info["running"] else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
    
    print("\n🌐 Shared Infrastructure:")
    for infra_name, infra_status in status["shared_infrastructure"].items():
        status_icon = "🟢" if infra_status else "🔴"
        print(f"  {status_icon} {infra_name.replace('_', ' ').title()}: {'Running' if infra_status else 'Stopped'}")
    
    print("\n🚀 Revolutionary Capabilities:")
    for cap_name, cap_status in status["revolutionary_capabilities"].items():
        status_icon = "🟢" if cap_status else "🔴"
        print(f"  {status_icon} {cap_name.replace('_', ' ').title()}: {'Active' if cap_status else 'Inactive'}")

async def show_health(manager):
    """Show detailed health information"""
    print("🏥 Triumvirate Integration Layer Health Check")
    print("=" * 50)
    
    # Get system overview
    overview = manager.observability.get_system_overview()
    
    print(f"System Health: {overview['system_health']['status'].title()}")
    print(f"Health Score: {overview['system_health']['score']:.1f}%")
    
    print(f"\n📊 Metrics:")
    print(f"  • Total Components: {overview['total_components_tracked']}")
    print(f"  • Active Alerts: {overview['active_alerts']}")
    print(f"  • Critical Alerts: {overview['critical_alerts']}")
    
    print(f"\n🔍 Component Health:")
    for comp_name in ["agenta", "pranava", "antakhara"]:
        health = await getattr(manager, comp_name).get_health_status()
        status_icon = "🟢" if health["status"] == "healthy" else "🟡" if health["status"] == "degraded" else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {health['status']}")
    
    # Check integration health
    integration_status = manager.get_status()
    if integration_status['system_status'] == 'running':
        print(f"\n✅ Integration Status: HEALTHY")
    else:
        print(f"\n❌ Integration Status: UNHEALTHY")

if __name__ == "__main__":
    # Ensure we can handle KeyboardInterrupt properly
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
        # Update component performance metrics
        if metric.component_id:
            if metric.component_id == "agenta":
                self.observability.set_gauge("agenta.routing_performance", metric.value, "agenta")
            elif metric.component_id == "pranava":
                self.observability.set_gauge("pranava.orchestration_performance", metric.value, "pranava")
            elif metric.component_id == "antakhara":
                self.observability.set_gauge("antakhara.security_performance", metric.value, "antakhara")
                
    async def _handle_alert(self, alert) -> None:
        """
Main entry point for Triumvirate Integration Layer

This script provides a command-line interface for managing the triumvirate
integration system, including initialization, startup, shutdown, and monitoring.
"""

import asyncio
import argparse
import sys
import signal
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from triumvirate_manager import TriumvirateIntegrationManager, setup_signal_handlers
from configs.config_manager import ConfigManager

async def main():
    """Main entry point for the triumvirate integration system"""
    parser = argparse.ArgumentParser(description="Triumvirate Integration Layer")
    parser.add_argument(
        "--config", 
        default="configs/integration_config.yaml",
        help="Configuration file path (default: configs/integration_config.yaml)"
    )
    parser.add_argument(
        "--action",
        choices=["start", "stop", "restart", "status", "health"],
        default="start",
        help="Action to perform (default: start)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="API server port (default: 8000)"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="API server host (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Run as daemon process"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    parser.add_argument(
        "--log-file",
        default="logs/triumvirate.log",
        help="Log file path (default: logs/triumvirate.log)"
    )
    
    args = parser.parse_args()
    
    # Create necessary directories
    Path("logs").mkdir(exist_ok=True)
    Path("data").mkdir(exist_ok=True)
    
    try:
        # Create and configure the integration manager
        manager = TriumvirateIntegrationManager(args.config)
        
        # Update API configuration if provided
        config_manager = ConfigManager(args.config)
        config = config_manager.load_config()
        config.api_config["host"] = args.host
        config.api_config["port"] = args.port
        config_manager.save_config(config)
        
        # Setup logging
        if args.debug:
            import logging
            logging.basicConfig(
                level=logging.DEBUG,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                handlers=[
                    logging.FileHandler(args.log_file),
                    logging.StreamHandler(sys.stdout)
                ]
            )
        
        # Setup signal handlers for graceful shutdown
        setup_signal_handlers(manager)
        
        # Perform the requested action
        if args.action == "start":
            await start_system(manager, args)
        elif args.action == "stop":
            await stop_system(manager)
        elif args.action == "restart":
            await restart_system(manager, args)
        elif args.action == "status":
            await show_status(manager)
        elif args.action == "health":
            await show_health(manager)
        
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

async def start_system(manager, args):
    """Start the triumvirate integration system"""
    print("🚀 Starting Triumvirate Integration Layer...")
    
    # Initialize the system
    print("📦 Initializing system components...")
    if not await manager.initialize():
        print("❌ Failed to initialize system")
        sys.exit(1)
    
    # Start the system
    print("⚡ Starting all components...")
    if not await manager.start():
        print("❌ Failed to start system")
        sys.exit(1)
    
    # Show system status
    status = manager.get_status()
    print("\n✅ Triumvirtate Integration Layer started successfully!")
    print(f"🌐 API Server: http://{args.host}:{args.port}")
    print(f"📊 System Status: {status['system_status'].title()}")
    
    if not args.daemon:
        print("\n📈 Component Status:")
        for comp_name, comp_info in status["components"].items():
            status_icon = "🟢" if comp_info["running"] else "🔴"
            print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
        
        print(f"\n🔗 API Endpoints:")
        print(f"  • Health: http://{args.host}:{args.port}/api/v1/monitoring/health")
        print(f"  • Metrics: http://{args.host}:{args.port}/api/v1/monitoring/metrics")
        print(f"  • System Overview: http://{args.host}:{args.port}/api/v1/system/overview")
        
        print(f"\n📝 Logs: {args.log_file}")
        print("\nPress Ctrl+C to stop the system")
        
        # Keep running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutdown requested...")
    else:
        print("🔄 Running as daemon...")

async def stop_system(manager):
    """Stop the triumvirate integration system"""
    print("🛑 Stopping Triumvirate Integration Layer...")
    
    if not await manager.stop():
        print("❌ Failed to stop system properly")
        sys.exit(1)
    
    print("✅ System stopped successfully")

async def restart_system(manager, args):
    """Restart the triumvirate integration system"""
    print("🔄 Restarting Triumvirate Integration Layer...")
    
    if not await manager.restart():
        print("❌ Failed to restart system")
        sys.exit(1)
    
    print("✅ System restarted successfully")
    print(f"🌐 Available at: http://{args.host}:{args.port}")

async def show_status(manager):
    """Show system status"""
    status = manager.get_status()
    
    print("📊 Triumvirate Integration Layer Status")
    print("=" * 50)
    print(f"System Status: {status['system_status'].title()}")
    
    if status['startup_time']:
        from datetime import datetime
        startup_time = datetime.fromisoformat(status['startup_time'])
        uptime_seconds = (datetime.now() - startup_time).total_seconds()
        uptime_hours = int(uptime_seconds // 3600)
        uptime_minutes = int((uptime_seconds % 3600) // 60)
        print(f"Uptime: {uptime_hours}h {uptime_minutes}m")
    
    print("\n🔧 Components:")
    for comp_name, comp_info in status["components"].items():
        status_icon = "🟢" if comp_info["running"] else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
    
    print("\n🌐 Shared Infrastructure:")
    for infra_name, infra_status in status["shared_infrastructure"].items():
        status_icon = "🟢" if infra_status else "🔴"
        print(f"  {status_icon} {infra_name.replace('_', ' ').title()}: {'Running' if infra_status else 'Stopped'}")
    
    print("\n🚀 Revolutionary Capabilities:")
    for cap_name, cap_status in status["revolutionary_capabilities"].items():
        status_icon = "🟢" if cap_status else "🔴"
        print(f"  {status_icon} {cap_name.replace('_', ' ').title()}: {'Active' if cap_status else 'Inactive'}")

async def show_health(manager):
    """Show detailed health information"""
    print("🏥 Triumvirate Integration Layer Health Check")
    print("=" * 50)
    
    # Get system overview
    overview = manager.observability.get_system_overview()
    
    print(f"System Health: {overview['system_health']['status'].title()}")
    print(f"Health Score: {overview['system_health']['score']:.1f}%")
    
    print(f"\n📊 Metrics:")
    print(f"  • Total Components: {overview['total_components_tracked']}")
    print(f"  • Active Alerts: {overview['active_alerts']}")
    print(f"  • Critical Alerts: {overview['critical_alerts']}")
    
    print(f"\n🔍 Component Health:")
    for comp_name in ["agenta", "pranava", "antakhara"]:
        health = await getattr(manager, comp_name).get_health_status()
        status_icon = "🟢" if health["status"] == "healthy" else "🟡" if health["status"] == "degraded" else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {health['status']}")
    
    # Check integration health
    integration_status = manager.get_status()
    if integration_status['system_status'] == 'running':
        print(f"\n✅ Integration Status: HEALTHY")
    else:
        print(f"\n❌ Integration Status: UNHEALTHY")

if __name__ == "__main__":
    # Ensure we can handle KeyboardInterrupt properly
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)Handle alerts from observability system"""
Main entry point for Triumvirate Integration Layer

This script provides a command-line interface for managing the triumvirate
integration system, including initialization, startup, shutdown, and monitoring.
"""

import asyncio
import argparse
import sys
import signal
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from triumvirate_manager import TriumvirateIntegrationManager, setup_signal_handlers
from configs.config_manager import ConfigManager

async def main():
    """Main entry point for the triumvirate integration system"""
    parser = argparse.ArgumentParser(description="Triumvirate Integration Layer")
    parser.add_argument(
        "--config", 
        default="configs/integration_config.yaml",
        help="Configuration file path (default: configs/integration_config.yaml)"
    )
    parser.add_argument(
        "--action",
        choices=["start", "stop", "restart", "status", "health"],
        default="start",
        help="Action to perform (default: start)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="API server port (default: 8000)"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="API server host (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Run as daemon process"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    parser.add_argument(
        "--log-file",
        default="logs/triumvirate.log",
        help="Log file path (default: logs/triumvirate.log)"
    )
    
    args = parser.parse_args()
    
    # Create necessary directories
    Path("logs").mkdir(exist_ok=True)
    Path("data").mkdir(exist_ok=True)
    
    try:
        # Create and configure the integration manager
        manager = TriumvirateIntegrationManager(args.config)
        
        # Update API configuration if provided
        config_manager = ConfigManager(args.config)
        config = config_manager.load_config()
        config.api_config["host"] = args.host
        config.api_config["port"] = args.port
        config_manager.save_config(config)
        
        # Setup logging
        if args.debug:
            import logging
            logging.basicConfig(
                level=logging.DEBUG,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                handlers=[
                    logging.FileHandler(args.log_file),
                    logging.StreamHandler(sys.stdout)
                ]
            )
        
        # Setup signal handlers for graceful shutdown
        setup_signal_handlers(manager)
        
        # Perform the requested action
        if args.action == "start":
            await start_system(manager, args)
        elif args.action == "stop":
            await stop_system(manager)
        elif args.action == "restart":
            await restart_system(manager, args)
        elif args.action == "status":
            await show_status(manager)
        elif args.action == "health":
            await show_health(manager)
        
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

async def start_system(manager, args):
    """Start the triumvirate integration system"""
    print("🚀 Starting Triumvirate Integration Layer...")
    
    # Initialize the system
    print("📦 Initializing system components...")
    if not await manager.initialize():
        print("❌ Failed to initialize system")
        sys.exit(1)
    
    # Start the system
    print("⚡ Starting all components...")
    if not await manager.start():
        print("❌ Failed to start system")
        sys.exit(1)
    
    # Show system status
    status = manager.get_status()
    print("\n✅ Triumvirtate Integration Layer started successfully!")
    print(f"🌐 API Server: http://{args.host}:{args.port}")
    print(f"📊 System Status: {status['system_status'].title()}")
    
    if not args.daemon:
        print("\n📈 Component Status:")
        for comp_name, comp_info in status["components"].items():
            status_icon = "🟢" if comp_info["running"] else "🔴"
            print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
        
        print(f"\n🔗 API Endpoints:")
        print(f"  • Health: http://{args.host}:{args.port}/api/v1/monitoring/health")
        print(f"  • Metrics: http://{args.host}:{args.port}/api/v1/monitoring/metrics")
        print(f"  • System Overview: http://{args.host}:{args.port}/api/v1/system/overview")
        
        print(f"\n📝 Logs: {args.log_file}")
        print("\nPress Ctrl+C to stop the system")
        
        # Keep running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutdown requested...")
    else:
        print("🔄 Running as daemon...")

async def stop_system(manager):
    """Stop the triumvirate integration system"""
    print("🛑 Stopping Triumvirate Integration Layer...")
    
    if not await manager.stop():
        print("❌ Failed to stop system properly")
        sys.exit(1)
    
    print("✅ System stopped successfully")

async def restart_system(manager, args):
    """Restart the triumvirate integration system"""
    print("🔄 Restarting Triumvirate Integration Layer...")
    
    if not await manager.restart():
        print("❌ Failed to restart system")
        sys.exit(1)
    
    print("✅ System restarted successfully")
    print(f"🌐 Available at: http://{args.host}:{args.port}")

async def show_status(manager):
    """Show system status"""
    status = manager.get_status()
    
    print("📊 Triumvirate Integration Layer Status")
    print("=" * 50)
    print(f"System Status: {status['system_status'].title()}")
    
    if status['startup_time']:
        from datetime import datetime
        startup_time = datetime.fromisoformat(status['startup_time'])
        uptime_seconds = (datetime.now() - startup_time).total_seconds()
        uptime_hours = int(uptime_seconds // 3600)
        uptime_minutes = int((uptime_seconds % 3600) // 60)
        print(f"Uptime: {uptime_hours}h {uptime_minutes}m")
    
    print("\n🔧 Components:")
    for comp_name, comp_info in status["components"].items():
        status_icon = "🟢" if comp_info["running"] else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
    
    print("\n🌐 Shared Infrastructure:")
    for infra_name, infra_status in status["shared_infrastructure"].items():
        status_icon = "🟢" if infra_status else "🔴"
        print(f"  {status_icon} {infra_name.replace('_', ' ').title()}: {'Running' if infra_status else 'Stopped'}")
    
    print("\n🚀 Revolutionary Capabilities:")
    for cap_name, cap_status in status["revolutionary_capabilities"].items():
        status_icon = "🟢" if cap_status else "🔴"
        print(f"  {status_icon} {cap_name.replace('_', ' ').title()}: {'Active' if cap_status else 'Inactive'}")

async def show_health(manager):
    """Show detailed health information"""
    print("🏥 Triumvirate Integration Layer Health Check")
    print("=" * 50)
    
    # Get system overview
    overview = manager.observability.get_system_overview()
    
    print(f"System Health: {overview['system_health']['status'].title()}")
    print(f"Health Score: {overview['system_health']['score']:.1f}%")
    
    print(f"\n📊 Metrics:")
    print(f"  • Total Components: {overview['total_components_tracked']}")
    print(f"  • Active Alerts: {overview['active_alerts']}")
    print(f"  • Critical Alerts: {overview['critical_alerts']}")
    
    print(f"\n🔍 Component Health:")
    for comp_name in ["agenta", "pranava", "antakhara"]:
        health = await getattr(manager, comp_name).get_health_status()
        status_icon = "🟢" if health["status"] == "healthy" else "🟡" if health["status"] == "degraded" else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {health['status']}")
    
    # Check integration health
    integration_status = manager.get_status()
    if integration_status['system_status'] == 'running':
        print(f"\n✅ Integration Status: HEALTHY")
    else:
        print(f"\n❌ Integration Status: UNHEALTHY")

if __name__ == "__main__":
    # Ensure we can handle KeyboardInterrupt properly
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
        # Log alert
        self.logger.warning(f"Alert: {alert.title} - {alert.message}")
        
        # If critical, trigger self-healing
        if alert.severity.value == "critical":
            if self.self_healer:
                await self.self_healer.handle_critical_alert(alert)
                
    async def _emergency_shutdown(self) -> None:
        """
Main entry point for Triumvirate Integration Layer

This script provides a command-line interface for managing the triumvirate
integration system, including initialization, startup, shutdown, and monitoring.
"""

import asyncio
import argparse
import sys
import signal
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from triumvirate_manager import TriumvirateIntegrationManager, setup_signal_handlers
from configs.config_manager import ConfigManager

async def main():
    """Main entry point for the triumvirate integration system"""
    parser = argparse.ArgumentParser(description="Triumvirate Integration Layer")
    parser.add_argument(
        "--config", 
        default="configs/integration_config.yaml",
        help="Configuration file path (default: configs/integration_config.yaml)"
    )
    parser.add_argument(
        "--action",
        choices=["start", "stop", "restart", "status", "health"],
        default="start",
        help="Action to perform (default: start)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="API server port (default: 8000)"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="API server host (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Run as daemon process"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    parser.add_argument(
        "--log-file",
        default="logs/triumvirate.log",
        help="Log file path (default: logs/triumvirate.log)"
    )
    
    args = parser.parse_args()
    
    # Create necessary directories
    Path("logs").mkdir(exist_ok=True)
    Path("data").mkdir(exist_ok=True)
    
    try:
        # Create and configure the integration manager
        manager = TriumvirateIntegrationManager(args.config)
        
        # Update API configuration if provided
        config_manager = ConfigManager(args.config)
        config = config_manager.load_config()
        config.api_config["host"] = args.host
        config.api_config["port"] = args.port
        config_manager.save_config(config)
        
        # Setup logging
        if args.debug:
            import logging
            logging.basicConfig(
                level=logging.DEBUG,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                handlers=[
                    logging.FileHandler(args.log_file),
                    logging.StreamHandler(sys.stdout)
                ]
            )
        
        # Setup signal handlers for graceful shutdown
        setup_signal_handlers(manager)
        
        # Perform the requested action
        if args.action == "start":
            await start_system(manager, args)
        elif args.action == "stop":
            await stop_system(manager)
        elif args.action == "restart":
            await restart_system(manager, args)
        elif args.action == "status":
            await show_status(manager)
        elif args.action == "health":
            await show_health(manager)
        
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

async def start_system(manager, args):
    """Start the triumvirate integration system"""
    print("🚀 Starting Triumvirate Integration Layer...")
    
    # Initialize the system
    print("📦 Initializing system components...")
    if not await manager.initialize():
        print("❌ Failed to initialize system")
        sys.exit(1)
    
    # Start the system
    print("⚡ Starting all components...")
    if not await manager.start():
        print("❌ Failed to start system")
        sys.exit(1)
    
    # Show system status
    status = manager.get_status()
    print("\n✅ Triumvirtate Integration Layer started successfully!")
    print(f"🌐 API Server: http://{args.host}:{args.port}")
    print(f"📊 System Status: {status['system_status'].title()}")
    
    if not args.daemon:
        print("\n📈 Component Status:")
        for comp_name, comp_info in status["components"].items():
            status_icon = "🟢" if comp_info["running"] else "🔴"
            print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
        
        print(f"\n🔗 API Endpoints:")
        print(f"  • Health: http://{args.host}:{args.port}/api/v1/monitoring/health")
        print(f"  • Metrics: http://{args.host}:{args.port}/api/v1/monitoring/metrics")
        print(f"  • System Overview: http://{args.host}:{args.port}/api/v1/system/overview")
        
        print(f"\n📝 Logs: {args.log_file}")
        print("\nPress Ctrl+C to stop the system")
        
        # Keep running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutdown requested...")
    else:
        print("🔄 Running as daemon...")

async def stop_system(manager):
    """Stop the triumvirate integration system"""
    print("🛑 Stopping Triumvirate Integration Layer...")
    
    if not await manager.stop():
        print("❌ Failed to stop system properly")
        sys.exit(1)
    
    print("✅ System stopped successfully")

async def restart_system(manager, args):
    """Restart the triumvirate integration system"""
    print("🔄 Restarting Triumvirate Integration Layer...")
    
    if not await manager.restart():
        print("❌ Failed to restart system")
        sys.exit(1)
    
    print("✅ System restarted successfully")
    print(f"🌐 Available at: http://{args.host}:{args.port}")

async def show_status(manager):
    """Show system status"""
    status = manager.get_status()
    
    print("📊 Triumvirate Integration Layer Status")
    print("=" * 50)
    print(f"System Status: {status['system_status'].title()}")
    
    if status['startup_time']:
        from datetime import datetime
        startup_time = datetime.fromisoformat(status['startup_time'])
        uptime_seconds = (datetime.now() - startup_time).total_seconds()
        uptime_hours = int(uptime_seconds // 3600)
        uptime_minutes = int((uptime_seconds % 3600) // 60)
        print(f"Uptime: {uptime_hours}h {uptime_minutes}m")
    
    print("\n🔧 Components:")
    for comp_name, comp_info in status["components"].items():
        status_icon = "🟢" if comp_info["running"] else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
    
    print("\n🌐 Shared Infrastructure:")
    for infra_name, infra_status in status["shared_infrastructure"].items():
        status_icon = "🟢" if infra_status else "🔴"
        print(f"  {status_icon} {infra_name.replace('_', ' ').title()}: {'Running' if infra_status else 'Stopped'}")
    
    print("\n🚀 Revolutionary Capabilities:")
    for cap_name, cap_status in status["revolutionary_capabilities"].items():
        status_icon = "🟢" if cap_status else "🔴"
        print(f"  {status_icon} {cap_name.replace('_', ' ').title()}: {'Active' if cap_status else 'Inactive'}")

async def show_health(manager):
    """Show detailed health information"""
    print("🏥 Triumvirate Integration Layer Health Check")
    print("=" * 50)
    
    # Get system overview
    overview = manager.observability.get_system_overview()
    
    print(f"System Health: {overview['system_health']['status'].title()}")
    print(f"Health Score: {overview['system_health']['score']:.1f}%")
    
    print(f"\n📊 Metrics:")
    print(f"  • Total Components: {overview['total_components_tracked']}")
    print(f"  • Active Alerts: {overview['active_alerts']}")
    print(f"  • Critical Alerts: {overview['critical_alerts']}")
    
    print(f"\n🔍 Component Health:")
    for comp_name in ["agenta", "pranava", "antakhara"]:
        health = await getattr(manager, comp_name).get_health_status()
        status_icon = "🟢" if health["status"] == "healthy" else "🟡" if health["status"] == "degraded" else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {health['status']}")
    
    # Check integration health
    integration_status = manager.get_status()
    if integration_status['system_status'] == 'running':
        print(f"\n✅ Integration Status: HEALTHY")
    else:
        print(f"\n❌ Integration Status: UNHEALTHY")

if __name__ == "__main__":
    # Ensure we can handle KeyboardInterrupt properly
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)Emergency shutdown procedure"""
Main entry point for Triumvirate Integration Layer

This script provides a command-line interface for managing the triumvirate
integration system, including initialization, startup, shutdown, and monitoring.
"""

import asyncio
import argparse
import sys
import signal
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from triumvirate_manager import TriumvirateIntegrationManager, setup_signal_handlers
from configs.config_manager import ConfigManager

async def main():
    """Main entry point for the triumvirate integration system"""
    parser = argparse.ArgumentParser(description="Triumvirate Integration Layer")
    parser.add_argument(
        "--config", 
        default="configs/integration_config.yaml",
        help="Configuration file path (default: configs/integration_config.yaml)"
    )
    parser.add_argument(
        "--action",
        choices=["start", "stop", "restart", "status", "health"],
        default="start",
        help="Action to perform (default: start)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="API server port (default: 8000)"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="API server host (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Run as daemon process"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    parser.add_argument(
        "--log-file",
        default="logs/triumvirate.log",
        help="Log file path (default: logs/triumvirate.log)"
    )
    
    args = parser.parse_args()
    
    # Create necessary directories
    Path("logs").mkdir(exist_ok=True)
    Path("data").mkdir(exist_ok=True)
    
    try:
        # Create and configure the integration manager
        manager = TriumvirateIntegrationManager(args.config)
        
        # Update API configuration if provided
        config_manager = ConfigManager(args.config)
        config = config_manager.load_config()
        config.api_config["host"] = args.host
        config.api_config["port"] = args.port
        config_manager.save_config(config)
        
        # Setup logging
        if args.debug:
            import logging
            logging.basicConfig(
                level=logging.DEBUG,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                handlers=[
                    logging.FileHandler(args.log_file),
                    logging.StreamHandler(sys.stdout)
                ]
            )
        
        # Setup signal handlers for graceful shutdown
        setup_signal_handlers(manager)
        
        # Perform the requested action
        if args.action == "start":
            await start_system(manager, args)
        elif args.action == "stop":
            await stop_system(manager)
        elif args.action == "restart":
            await restart_system(manager, args)
        elif args.action == "status":
            await show_status(manager)
        elif args.action == "health":
            await show_health(manager)
        
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

async def start_system(manager, args):
    """Start the triumvirate integration system"""
    print("🚀 Starting Triumvirate Integration Layer...")
    
    # Initialize the system
    print("📦 Initializing system components...")
    if not await manager.initialize():
        print("❌ Failed to initialize system")
        sys.exit(1)
    
    # Start the system
    print("⚡ Starting all components...")
    if not await manager.start():
        print("❌ Failed to start system")
        sys.exit(1)
    
    # Show system status
    status = manager.get_status()
    print("\n✅ Triumvirtate Integration Layer started successfully!")
    print(f"🌐 API Server: http://{args.host}:{args.port}")
    print(f"📊 System Status: {status['system_status'].title()}")
    
    if not args.daemon:
        print("\n📈 Component Status:")
        for comp_name, comp_info in status["components"].items():
            status_icon = "🟢" if comp_info["running"] else "🔴"
            print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
        
        print(f"\n🔗 API Endpoints:")
        print(f"  • Health: http://{args.host}:{args.port}/api/v1/monitoring/health")
        print(f"  • Metrics: http://{args.host}:{args.port}/api/v1/monitoring/metrics")
        print(f"  • System Overview: http://{args.host}:{args.port}/api/v1/system/overview")
        
        print(f"\n📝 Logs: {args.log_file}")
        print("\nPress Ctrl+C to stop the system")
        
        # Keep running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutdown requested...")
    else:
        print("🔄 Running as daemon...")

async def stop_system(manager):
    """Stop the triumvirate integration system"""
    print("🛑 Stopping Triumvirate Integration Layer...")
    
    if not await manager.stop():
        print("❌ Failed to stop system properly")
        sys.exit(1)
    
    print("✅ System stopped successfully")

async def restart_system(manager, args):
    """Restart the triumvirate integration system"""
    print("🔄 Restarting Triumvirate Integration Layer...")
    
    if not await manager.restart():
        print("❌ Failed to restart system")
        sys.exit(1)
    
    print("✅ System restarted successfully")
    print(f"🌐 Available at: http://{args.host}:{args.port}")

async def show_status(manager):
    """Show system status"""
    status = manager.get_status()
    
    print("📊 Triumvirate Integration Layer Status")
    print("=" * 50)
    print(f"System Status: {status['system_status'].title()}")
    
    if status['startup_time']:
        from datetime import datetime
        startup_time = datetime.fromisoformat(status['startup_time'])
        uptime_seconds = (datetime.now() - startup_time).total_seconds()
        uptime_hours = int(uptime_seconds // 3600)
        uptime_minutes = int((uptime_seconds % 3600) // 60)
        print(f"Uptime: {uptime_hours}h {uptime_minutes}m")
    
    print("\n🔧 Components:")
    for comp_name, comp_info in status["components"].items():
        status_icon = "🟢" if comp_info["running"] else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
    
    print("\n🌐 Shared Infrastructure:")
    for infra_name, infra_status in status["shared_infrastructure"].items():
        status_icon = "🟢" if infra_status else "🔴"
        print(f"  {status_icon} {infra_name.replace('_', ' ').title()}: {'Running' if infra_status else 'Stopped'}")
    
    print("\n🚀 Revolutionary Capabilities:")
    for cap_name, cap_status in status["revolutionary_capabilities"].items():
        status_icon = "🟢" if cap_status else "🔴"
        print(f"  {status_icon} {cap_name.replace('_', ' ').title()}: {'Active' if cap_status else 'Inactive'}")

async def show_health(manager):
    """Show detailed health information"""
    print("🏥 Triumvirate Integration Layer Health Check")
    print("=" * 50)
    
    # Get system overview
    overview = manager.observability.get_system_overview()
    
    print(f"System Health: {overview['system_health']['status'].title()}")
    print(f"Health Score: {overview['system_health']['score']:.1f}%")
    
    print(f"\n📊 Metrics:")
    print(f"  • Total Components: {overview['total_components_tracked']}")
    print(f"  • Active Alerts: {overview['active_alerts']}")
    print(f"  • Critical Alerts: {overview['critical_alerts']}")
    
    print(f"\n🔍 Component Health:")
    for comp_name in ["agenta", "pranava", "antakhara"]:
        health = await getattr(manager, comp_name).get_health_status()
        status_icon = "🟢" if health["status"] == "healthy" else "🟡" if health["status"] == "degraded" else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {health['status']}")
    
    # Check integration health
    integration_status = manager.get_status()
    if integration_status['system_status'] == 'running':
        print(f"\n✅ Integration Status: HEALTHY")
    else:
        print(f"\n❌ Integration Status: UNHEALTHY")

if __name__ == "__main__":
    # Ensure we can handle KeyboardInterrupt properly
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
        self.logger.critical("Initiating emergency shutdown")
        
        try:
            # Stop all components immediately
            tasks = [
                self.agenta.stop() if self.agenta else None,
                self.pranava.stop() if self.pranava else None,
                self.antakhara.stop() if self.antakhara else None,
                self.message_router.stop() if self.message_router else None,
                self.service_discovery.stop_health_monitoring() if self.service_discovery else None,
                self.observability.stop() if self.observability else None
            ]
            
            await asyncio.gather(*[t for t in tasks if t is not None], return_exceptions=True)
            
        except Exception as e:
            self.logger.error(f"Emergency shutdown error: {e}")
            
        self.is_running = False

# Signal handling for graceful shutdown
def setup_signal_handlers(manager: TriumvirateIntegrationManager):
    """
Main entry point for Triumvirate Integration Layer

This script provides a command-line interface for managing the triumvirate
integration system, including initialization, startup, shutdown, and monitoring.
"""

import asyncio
import argparse
import sys
import signal
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from triumvirate_manager import TriumvirateIntegrationManager, setup_signal_handlers
from configs.config_manager import ConfigManager

async def main():
    """Main entry point for the triumvirate integration system"""
    parser = argparse.ArgumentParser(description="Triumvirate Integration Layer")
    parser.add_argument(
        "--config", 
        default="configs/integration_config.yaml",
        help="Configuration file path (default: configs/integration_config.yaml)"
    )
    parser.add_argument(
        "--action",
        choices=["start", "stop", "restart", "status", "health"],
        default="start",
        help="Action to perform (default: start)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="API server port (default: 8000)"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="API server host (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Run as daemon process"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    parser.add_argument(
        "--log-file",
        default="logs/triumvirate.log",
        help="Log file path (default: logs/triumvirate.log)"
    )
    
    args = parser.parse_args()
    
    # Create necessary directories
    Path("logs").mkdir(exist_ok=True)
    Path("data").mkdir(exist_ok=True)
    
    try:
        # Create and configure the integration manager
        manager = TriumvirateIntegrationManager(args.config)
        
        # Update API configuration if provided
        config_manager = ConfigManager(args.config)
        config = config_manager.load_config()
        config.api_config["host"] = args.host
        config.api_config["port"] = args.port
        config_manager.save_config(config)
        
        # Setup logging
        if args.debug:
            import logging
            logging.basicConfig(
                level=logging.DEBUG,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                handlers=[
                    logging.FileHandler(args.log_file),
                    logging.StreamHandler(sys.stdout)
                ]
            )
        
        # Setup signal handlers for graceful shutdown
        setup_signal_handlers(manager)
        
        # Perform the requested action
        if args.action == "start":
            await start_system(manager, args)
        elif args.action == "stop":
            await stop_system(manager)
        elif args.action == "restart":
            await restart_system(manager, args)
        elif args.action == "status":
            await show_status(manager)
        elif args.action == "health":
            await show_health(manager)
        
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

async def start_system(manager, args):
    """Start the triumvirate integration system"""
    print("🚀 Starting Triumvirate Integration Layer...")
    
    # Initialize the system
    print("📦 Initializing system components...")
    if not await manager.initialize():
        print("❌ Failed to initialize system")
        sys.exit(1)
    
    # Start the system
    print("⚡ Starting all components...")
    if not await manager.start():
        print("❌ Failed to start system")
        sys.exit(1)
    
    # Show system status
    status = manager.get_status()
    print("\n✅ Triumvirtate Integration Layer started successfully!")
    print(f"🌐 API Server: http://{args.host}:{args.port}")
    print(f"📊 System Status: {status['system_status'].title()}")
    
    if not args.daemon:
        print("\n📈 Component Status:")
        for comp_name, comp_info in status["components"].items():
            status_icon = "🟢" if comp_info["running"] else "🔴"
            print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
        
        print(f"\n🔗 API Endpoints:")
        print(f"  • Health: http://{args.host}:{args.port}/api/v1/monitoring/health")
        print(f"  • Metrics: http://{args.host}:{args.port}/api/v1/monitoring/metrics")
        print(f"  • System Overview: http://{args.host}:{args.port}/api/v1/system/overview")
        
        print(f"\n📝 Logs: {args.log_file}")
        print("\nPress Ctrl+C to stop the system")
        
        # Keep running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutdown requested...")
    else:
        print("🔄 Running as daemon...")

async def stop_system(manager):
    """Stop the triumvirate integration system"""
    print("🛑 Stopping Triumvirate Integration Layer...")
    
    if not await manager.stop():
        print("❌ Failed to stop system properly")
        sys.exit(1)
    
    print("✅ System stopped successfully")

async def restart_system(manager, args):
    """Restart the triumvirate integration system"""
    print("🔄 Restarting Triumvirate Integration Layer...")
    
    if not await manager.restart():
        print("❌ Failed to restart system")
        sys.exit(1)
    
    print("✅ System restarted successfully")
    print(f"🌐 Available at: http://{args.host}:{args.port}")

async def show_status(manager):
    """Show system status"""
    status = manager.get_status()
    
    print("📊 Triumvirate Integration Layer Status")
    print("=" * 50)
    print(f"System Status: {status['system_status'].title()}")
    
    if status['startup_time']:
        from datetime import datetime
        startup_time = datetime.fromisoformat(status['startup_time'])
        uptime_seconds = (datetime.now() - startup_time).total_seconds()
        uptime_hours = int(uptime_seconds // 3600)
        uptime_minutes = int((uptime_seconds % 3600) // 60)
        print(f"Uptime: {uptime_hours}h {uptime_minutes}m")
    
    print("\n🔧 Components:")
    for comp_name, comp_info in status["components"].items():
        status_icon = "🟢" if comp_info["running"] else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
    
    print("\n🌐 Shared Infrastructure:")
    for infra_name, infra_status in status["shared_infrastructure"].items():
        status_icon = "🟢" if infra_status else "🔴"
        print(f"  {status_icon} {infra_name.replace('_', ' ').title()}: {'Running' if infra_status else 'Stopped'}")
    
    print("\n🚀 Revolutionary Capabilities:")
    for cap_name, cap_status in status["revolutionary_capabilities"].items():
        status_icon = "🟢" if cap_status else "🔴"
        print(f"  {status_icon} {cap_name.replace('_', ' ').title()}: {'Active' if cap_status else 'Inactive'}")

async def show_health(manager):
    """Show detailed health information"""
    print("🏥 Triumvirate Integration Layer Health Check")
    print("=" * 50)
    
    # Get system overview
    overview = manager.observability.get_system_overview()
    
    print(f"System Health: {overview['system_health']['status'].title()}")
    print(f"Health Score: {overview['system_health']['score']:.1f}%")
    
    print(f"\n📊 Metrics:")
    print(f"  • Total Components: {overview['total_components_tracked']}")
    print(f"  • Active Alerts: {overview['active_alerts']}")
    print(f"  • Critical Alerts: {overview['critical_alerts']}")
    
    print(f"\n🔍 Component Health:")
    for comp_name in ["agenta", "pranava", "antakhara"]:
        health = await getattr(manager, comp_name).get_health_status()
        status_icon = "🟢" if health["status"] == "healthy" else "🟡" if health["status"] == "degraded" else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {health['status']}")
    
    # Check integration health
    integration_status = manager.get_status()
    if integration_status['system_status'] == 'running':
        print(f"\n✅ Integration Status: HEALTHY")
    else:
        print(f"\n❌ Integration Status: UNHEALTHY")

if __name__ == "__main__":
    # Ensure we can handle KeyboardInterrupt properly
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)Setup signal handlers for graceful shutdown"""
Main entry point for Triumvirate Integration Layer

This script provides a command-line interface for managing the triumvirate
integration system, including initialization, startup, shutdown, and monitoring.
"""

import asyncio
import argparse
import sys
import signal
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from triumvirate_manager import TriumvirateIntegrationManager, setup_signal_handlers
from configs.config_manager import ConfigManager

async def main():
    """Main entry point for the triumvirate integration system"""
    parser = argparse.ArgumentParser(description="Triumvirate Integration Layer")
    parser.add_argument(
        "--config", 
        default="configs/integration_config.yaml",
        help="Configuration file path (default: configs/integration_config.yaml)"
    )
    parser.add_argument(
        "--action",
        choices=["start", "stop", "restart", "status", "health"],
        default="start",
        help="Action to perform (default: start)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="API server port (default: 8000)"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="API server host (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Run as daemon process"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    parser.add_argument(
        "--log-file",
        default="logs/triumvirate.log",
        help="Log file path (default: logs/triumvirate.log)"
    )
    
    args = parser.parse_args()
    
    # Create necessary directories
    Path("logs").mkdir(exist_ok=True)
    Path("data").mkdir(exist_ok=True)
    
    try:
        # Create and configure the integration manager
        manager = TriumvirateIntegrationManager(args.config)
        
        # Update API configuration if provided
        config_manager = ConfigManager(args.config)
        config = config_manager.load_config()
        config.api_config["host"] = args.host
        config.api_config["port"] = args.port
        config_manager.save_config(config)
        
        # Setup logging
        if args.debug:
            import logging
            logging.basicConfig(
                level=logging.DEBUG,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                handlers=[
                    logging.FileHandler(args.log_file),
                    logging.StreamHandler(sys.stdout)
                ]
            )
        
        # Setup signal handlers for graceful shutdown
        setup_signal_handlers(manager)
        
        # Perform the requested action
        if args.action == "start":
            await start_system(manager, args)
        elif args.action == "stop":
            await stop_system(manager)
        elif args.action == "restart":
            await restart_system(manager, args)
        elif args.action == "status":
            await show_status(manager)
        elif args.action == "health":
            await show_health(manager)
        
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

async def start_system(manager, args):
    """Start the triumvirate integration system"""
    print("🚀 Starting Triumvirate Integration Layer...")
    
    # Initialize the system
    print("📦 Initializing system components...")
    if not await manager.initialize():
        print("❌ Failed to initialize system")
        sys.exit(1)
    
    # Start the system
    print("⚡ Starting all components...")
    if not await manager.start():
        print("❌ Failed to start system")
        sys.exit(1)
    
    # Show system status
    status = manager.get_status()
    print("\n✅ Triumvirtate Integration Layer started successfully!")
    print(f"🌐 API Server: http://{args.host}:{args.port}")
    print(f"📊 System Status: {status['system_status'].title()}")
    
    if not args.daemon:
        print("\n📈 Component Status:")
        for comp_name, comp_info in status["components"].items():
            status_icon = "🟢" if comp_info["running"] else "🔴"
            print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
        
        print(f"\n🔗 API Endpoints:")
        print(f"  • Health: http://{args.host}:{args.port}/api/v1/monitoring/health")
        print(f"  • Metrics: http://{args.host}:{args.port}/api/v1/monitoring/metrics")
        print(f"  • System Overview: http://{args.host}:{args.port}/api/v1/system/overview")
        
        print(f"\n📝 Logs: {args.log_file}")
        print("\nPress Ctrl+C to stop the system")
        
        # Keep running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutdown requested...")
    else:
        print("🔄 Running as daemon...")

async def stop_system(manager):
    """Stop the triumvirate integration system"""
    print("🛑 Stopping Triumvirate Integration Layer...")
    
    if not await manager.stop():
        print("❌ Failed to stop system properly")
        sys.exit(1)
    
    print("✅ System stopped successfully")

async def restart_system(manager, args):
    """Restart the triumvirate integration system"""
    print("🔄 Restarting Triumvirate Integration Layer...")
    
    if not await manager.restart():
        print("❌ Failed to restart system")
        sys.exit(1)
    
    print("✅ System restarted successfully")
    print(f"🌐 Available at: http://{args.host}:{args.port}")

async def show_status(manager):
    """Show system status"""
    status = manager.get_status()
    
    print("📊 Triumvirate Integration Layer Status")
    print("=" * 50)
    print(f"System Status: {status['system_status'].title()}")
    
    if status['startup_time']:
        from datetime import datetime
        startup_time = datetime.fromisoformat(status['startup_time'])
        uptime_seconds = (datetime.now() - startup_time).total_seconds()
        uptime_hours = int(uptime_seconds // 3600)
        uptime_minutes = int((uptime_seconds % 3600) // 60)
        print(f"Uptime: {uptime_hours}h {uptime_minutes}m")
    
    print("\n🔧 Components:")
    for comp_name, comp_info in status["components"].items():
        status_icon = "🟢" if comp_info["running"] else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {comp_info['status']}")
    
    print("\n🌐 Shared Infrastructure:")
    for infra_name, infra_status in status["shared_infrastructure"].items():
        status_icon = "🟢" if infra_status else "🔴"
        print(f"  {status_icon} {infra_name.replace('_', ' ').title()}: {'Running' if infra_status else 'Stopped'}")
    
    print("\n🚀 Revolutionary Capabilities:")
    for cap_name, cap_status in status["revolutionary_capabilities"].items():
        status_icon = "🟢" if cap_status else "🔴"
        print(f"  {status_icon} {cap_name.replace('_', ' ').title()}: {'Active' if cap_status else 'Inactive'}")

async def show_health(manager):
    """Show detailed health information"""
    print("🏥 Triumvirate Integration Layer Health Check")
    print("=" * 50)
    
    # Get system overview
    overview = manager.observability.get_system_overview()
    
    print(f"System Health: {overview['system_health']['status'].title()}")
    print(f"Health Score: {overview['system_health']['score']:.1f}%")
    
    print(f"\n📊 Metrics:")
    print(f"  • Total Components: {overview['total_components_tracked']}")
    print(f"  • Active Alerts: {overview['active_alerts']}")
    print(f"  • Critical Alerts: {overview['critical_alerts']}")
    
    print(f"\n🔍 Component Health:")
    for comp_name in ["agenta", "pranava", "antakhara"]:
        health = await getattr(manager, comp_name).get_health_status()
        status_icon = "🟢" if health["status"] == "healthy" else "🟡" if health["status"] == "degraded" else "🔴"
        print(f"  {status_icon} {comp_name.title()}: {health['status']}")
    
    # Check integration health
    integration_status = manager.get_status()
    if integration_status['system_status'] == 'running':
        print(f"\n✅ Integration Status: HEALTHY")
    else:
        print(f"\n❌ Integration Status: UNHEALTHY")

if __name__ == "__main__":
    # Ensure we can handle KeyboardInterrupt properly
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
    def signal_handler(signum, frame):
        print(f"Received signal {signum}, initiating graceful shutdown...")
        asyncio.create_task(manager.stop())
        sys.exit(0)
        
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
