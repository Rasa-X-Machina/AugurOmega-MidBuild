"""
Augur Omega: Main UI/UX Integration Module
Integrates all UI/UX components, agent formation, and settings management
"""
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional
import json
import logging
from datetime import datetime

# Import our modules
from agents.agent_formation_system import AgentFormationOptimizer, create_sample_agents, create_sample_tasks, Agent, Task
from settings.natural_language_to_json_converter import SettingsManager, NaturalLanguageToJSONConverter
from settings.configuration_modes import ConfigurationModeManager, ConfigurationMode
from settings.settings_kosha_integration import SettingsKoshaIntegration
from components.json_editor_app import JsonSettingsEditor  # Assuming this is available in JS context


class AugurOmegaUIUXSystem:
    """Main class to integrate all UI/UX components of the Augur Omega system"""
    
    def __init__(self, base_dir: str = "main/ui_ux_system"):
        self.base_dir = Path(base_dir)
        self.agent_optimizer = AgentFormationOptimizer()
        self.settings_manager = SettingsManager()
        self.config_mode_manager = ConfigurationModeManager()
        self.settings_integration = SettingsKoshaIntegration()
        
        # Setup logging
        self._setup_logging()
        
        # Initialize with sample data
        self._initialize_sample_data()
        
        logging.info("Augur Omega UI/UX System initialized successfully")
    
    def _setup_logging(self):
        """Setup logging for the system"""
        log_dir = self.base_dir / "logs"
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / f"ui_ux_system_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
    
    def _initialize_sample_data(self):
        """Initialize with sample agents and tasks"""
        agents = create_sample_agents()
        tasks = create_sample_tasks()
        
        for agent in agents:
            self.agent_optimizer.add_agent(agent)
        
        for task in tasks:
            self.agent_optimizer.add_task(task)
        
        logging.info(f"Initialized with {len(agents)} agents and {len(tasks)} tasks")
    
    def get_agent_optimization_results(self) -> Dict[str, Any]:
        """Get current agent formation optimization results"""
        # Form optimal teams
        assignments = self.agent_optimizer.form_optimal_teams()
        
        # Calculate efficiency metrics
        metrics = self.agent_optimizer.calculate_mathematical_efficiency_metrics(assignments)
        
        # Get cluster-based assignments as well
        cluster_assignments = self.agent_optimizer.optimize_by_expertise_cluster()
        cluster_metrics = self.agent_optimizer.calculate_mathematical_efficiency_metrics(cluster_assignments)
        
        return {
            "assignments": assignments,
            "metrics": metrics,
            "cluster_assignments": cluster_assignments,
            "cluster_metrics": cluster_metrics
        }
    
    def process_natural_language_settings(self, nl_input: str) -> Dict[str, Any]:
        """Process natural language input for settings changes"""
        result = self.settings_manager.update_settings_from_natural_language(nl_input)
        
        return {
            "success": result.success,
            "json_output": result.json_output,
            "confidence": result.confidence,
            "error_message": result.error_message
        }
    
    def get_current_config_mode(self) -> Dict[str, Any]:
        """Get information about the current configuration mode"""
        current_mode = self.config_mode_manager.get_current_mode()
        available_options = self.config_mode_manager.get_available_options()
        settings_for_mode = self.config_mode_manager.get_settings_for_current_mode()
        
        return {
            "current_mode": current_mode.value,
            "available_options_count": len(available_options),
            "settings_keys": list(settings_for_mode.keys()),
            "full_settings": settings_for_mode
        }
    
    def switch_config_mode(self, mode: ConfigurationMode) -> Dict[str, Any]:
        """Switch to a different configuration mode"""
        self.config_mode_manager.set_mode(mode)
        return self.get_current_config_mode()
    
    def update_kosha_setting(self, kosha_id: str, key: str, value: Any) -> bool:
        """Update a setting for a specific kosha"""
        return self.settings_integration.update_setting(kosha_id, key, value)
    
    def get_kosha_settings(self, kosha_id: str) -> Dict[str, Any]:
        """Get settings for a specific kosha"""
        return self.settings_integration.get_kosha_settings(kosha_id)
    
    def get_all_kosha_sync_status(self) -> Dict[str, Any]:
        """Get synchronization status for all koshas"""
        sync_status = self.settings_integration.get_sync_status()
        return {
            "sync_status": sync_status,
            "total_koshas": len(sync_status)
        }
    
    def run_optimization_cycle(self) -> Dict[str, Any]:
        """Run a complete optimization cycle"""
        # Get current optimization results
        optimization_results = self.get_agent_optimization_results()
        
        # Process any pending settings changes
        # In a real implementation, this would check for any configuration changes
        # that might affect the optimization
        
        # Return results with timestamp
        return {
            **optimization_results,
            "timestamp": datetime.now().isoformat(),
            "optimization_cycle": True
        }
    
    def export_system_state(self) -> Dict[str, Any]:
        """Export the current system state"""
        return {
            "timestamp": datetime.now().isoformat(),
            "agent_optimization": self.get_agent_optimization_results(),
            "current_config_mode": self.get_current_config_mode(),
            "settings_integration": self.get_all_kosha_sync_status(),
            "system_settings": self.settings_manager.get_all_settings()
        }
    
    def save_system_state(self, filename: str = None) -> str:
        """Save the current system state to a file"""
        if not filename:
            filename = self.base_dir / f"system_state_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        else:
            filename = self.base_dir / filename
        
        state = self.export_system_state()
        
        with open(filename, 'w') as f:
            json.dump(state, f, indent=2)
        
        logging.info(f"System state saved to {filename}")
        return str(filename)


def create_demo_interface():
    """Create a simple command-line interface for demonstration"""
    system = AugurOmegaUIUXSystem()
    
    print("=" * 60)
    print("AUGUR OMEGA: UI/UX INTEGRATION DEMO")
    print("=" * 60)
    
    while True:
        print("\nOptions:")
        print("1. Show Agent Optimization Results")
        print("2. Process Natural Language Settings")
        print("3. Switch Configuration Mode")
        print("4. Update Kosha Setting")
        print("5. Show Kosha Sync Status")
        print("6. Run Optimization Cycle")
        print("7. Export System State")
        print("8. Exit")
        
        choice = input("\nSelect an option (1-8): ").strip()
        
        if choice == "1":
            print("\n--- Agent Optimization Results ---")
            results = system.get_agent_optimization_results()
            print(f"Formation Efficiency: {results['metrics']['formation_efficiency']:.3f}")
            print(f"Resource Utilization: {results['metrics']['resource_utilization']:.3f}")
            print(f"Domain Coverage: {results['metrics']['domain_coverage']:.3f}")
            
        elif choice == "2":
            print("\n--- Natural Language Settings ---")
            nl_input = input("Enter a natural language description of settings: ")
            result = system.process_natural_language_settings(nl_input)
            print(f"Success: {result['success']}")
            print(f"Confidence: {result['confidence']:.2f}")
            if result['success'] and result['json_output']:
                print(f"JSON Output: {json.dumps(result['json_output'], indent=2)}")
            
        elif choice == "3":
            print("\n--- Switch Configuration Mode ---")
            print("Available modes: 1. Essence, 2. Smart, 3. Expert")
            mode_choice = input("Select mode (1-3): ").strip()
            mode_map = {"1": ConfigurationMode.ESSENCE, "2": ConfigurationMode.SMART, "3": ConfigurationMode.EXPERT}
            if mode_choice in mode_map:
                mode = mode_map[mode_choice]
                result = system.switch_config_mode(mode)
                print(f"Switched to {result['current_mode']} mode")
            else:
                print("Invalid choice")
            
        elif choice == "4":
            print("\n--- Update Kosha Setting ---")
            kosha_id = input("Enter Kosha ID: ").strip()
            key = input("Enter setting key (e.g., 'performance.level'): ").strip()
            value = input("Enter new value: ").strip()
            
            # Try to convert value to appropriate type
            try:
                value = json.loads(value)  # This handles bool, number, list, dict
            except json.JSONDecodeError:
                pass  # Keep as string if not valid JSON
            
            success = system.update_kosha_setting(kosha_id, key, value)
            print(f"Setting update {'successful' if success else 'failed'}")
            
        elif choice == "5":
            print("\n--- Kosha Sync Status ---")
            status = system.get_all_kosha_sync_status()
            print(f"Total Koshas: {status['total_koshas']}")
            for kosha_id, sync_status in status['sync_status'].items():
                print(f"  {kosha_id}: {sync_status.value}")
            
        elif choice == "6":
            print("\n--- Running Optimization Cycle ---")
            result = system.run_optimization_cycle()
            print(f"Optimization completed at {result['timestamp']}")
            print(f"Efficiency: {result['metrics']['formation_efficiency']:.3f}")
            
        elif choice == "7":
            print("\n--- Export System State ---")
            filename = system.save_system_state()
            print(f"System state exported to: {filename}")
            
        elif choice == "8":
            print("\nExiting Augur Omega UI/UX Demo...")
            break
            
        else:
            print("\nInvalid option, please try again")


if __name__ == "__main__":
    create_demo_interface()