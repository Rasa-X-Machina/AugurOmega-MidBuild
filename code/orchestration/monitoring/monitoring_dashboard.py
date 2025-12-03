"""
Augur Omega: Real-time Monitoring Dashboard
Web-based monitoring interface with WebSocket support for real-time updates
"""
import os
import sys
import json
import logging
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
from dataclasses import dataclass, asdict

from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
from flask_cors import CORS

# Setup logging
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, 
            template_folder='../web_dashboard/templates',
            static_folder='../web_dashboard/static')
app.config['SECRET_KEY'] = 'augur-omega-dashboard-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Enable CORS
CORS(app)

class MonitoringDataStore:
    """Central data store for monitoring information"""
    
    def __init__(self):
        self.agent_data = {}
        self.team_data = {}
        self.system_metrics = {}
        self.audit_reports = {}
        self.orchestration_status = {}
        self.alerts = []
        self.performance_history = []
        self.last_update = datetime.now()
        
    def update_agent_data(self, agent_id: str, data: Dict[str, Any]):
        """Update agent monitoring data"""
        self.agent_data[agent_id] = {
            **data,
            "last_updated": datetime.now().isoformat()
        }
        self.last_update = datetime.now()
        
    def update_team_data(self, team_name: str, data: Dict[str, Any]):
        """Update team monitoring data"""
        self.team_data[team_name] = {
            **data,
            "last_updated": datetime.now().isoformat()
        }
        self.last_update = datetime.now()
        
    def update_system_metrics(self, metrics: Dict[str, Any]):
        """Update system metrics"""
        self.system_metrics = {
            **metrics,
            "timestamp": datetime.now().isoformat()
        }
        self.performance_history.append({
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics.copy()
        })
        
        # Keep only last 1000 data points
        if len(self.performance_history) > 1000:
            self.performance_history = self.performance_history[-1000:]
            
        self.last_update = datetime.now()
        
    def update_audit_report(self, report_id: str, report: Dict[str, Any]):
        """Update audit report"""
        self.audit_reports[report_id] = {
            **report,
            "timestamp": datetime.now().isoformat()
        }
        self.last_update = datetime.now()
        
    def update_orchestration_status(self, status: Dict[str, Any]):
        """Update orchestration status"""
        self.orchestration_status = {
            **status,
            "timestamp": datetime.now().isoformat()
        }
        self.last_update = datetime.now()
        
    def add_alert(self, alert: Dict[str, Any]):
        """Add new alert"""
        alert_data = {
            **alert,
            "id": f"alert_{int(time.time())}",
            "timestamp": datetime.now().isoformat(),
            "acknowledged": False
        }
        self.alerts.append(alert_data)
        
        # Keep only last 100 alerts
        if len(self.alerts) > 100:
            self.alerts = self.alerts[-100:]
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive dashboard data"""
        return {
            "agent_data": self.agent_data,
            "team_data": self.team_data,
            "system_metrics": self.system_metrics,
            "audit_reports": dict(list(self.audit_reports.items())[-20:]),  # Last 20 reports
            "orchestration_status": self.orchestration_status,
            "alerts": self.alerts[-10:],  # Last 10 alerts
            "performance_history": self.performance_history[-60:],  # Last 60 data points
            "last_update": self.last_update.isoformat()
        }

# Global data store
monitoring_store = MonitoringDataStore()

class MockDataGenerator:
    """Generates realistic mock data for demonstration"""
    
    def __init__(self):
        self.base_agent_count = 30
        self.base_team_count = 6
        
    def generate_agent_data(self) -> Dict[str, Any]:
        """Generate mock agent data"""
        agents = {}
        
        # Generate different types of agents
        agent_types = {
            'research': ['researcher_1', 'researcher_2', 'researcher_3'],
            'dev': ['dev_1', 'dev_2', 'dev_3', 'dev_4', 'dev_5'],
            'integration': ['integrator_1', 'integrator_2'],
            'response': ['responder_1', 'responder_2', 'responder_3'],
            'support': ['support_1', 'support_2'],
            'specialist': ['expert_1', 'expert_2', 'expert_3', 'expert_4'],
            'reserve': ['backup_1', 'backup_2']
        }
        
        import random
        
        for agent_type, agent_list in agent_types.items():
            for agent_name in agent_list:
                agent_id = f"{agent_type}_{agent_name.split('_')[1]}"
                
                # Generate realistic metrics
                cpu_usage = random.uniform(5, 45)
                memory_usage = random.uniform(10, 60)
                health_score = random.uniform(75, 95)
                
                # Determine status based on health score
                if health_score > 90:
                    status = 'running'
                elif health_score > 80:
                    status = 'idle'
                else:
                    status = 'maintenance'
                
                agents[agent_id] = {
                    'name': agent_name,
                    'status': status,
                    'type': agent_type,
                    'metrics': {
                        'cpu_usage': round(cpu_usage, 1),
                        'memory_usage': round(memory_usage, 1),
                        'health_score': round(health_score, 1),
                        'tasks_completed': random.randint(50, 200),
                        'tasks_failed': random.randint(0, 5),
                        'uptime_hours': random.randint(1, 168),
                        'restart_count': random.randint(0, 2)
                    },
                    'capabilities': random.sample([
                        'research', 'analysis', 'coding', 'testing', 
                        'integration', 'deployment', 'monitoring', 'support'
                    ], random.randint(2, 4)),
                    'last_activity': (datetime.now() - timedelta(minutes=random.randint(0, 30))).isoformat()
                }
        
        return agents
    
    def generate_team_data(self, agent_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate team data based on agent data"""
        teams = {}
        
        team_mapping = {
            'research': ['researcher_1', 'researcher_2', 'researcher_3'],
            'dev': ['dev_1', 'dev_2', 'dev_3', 'dev_4', 'dev_5'],
            'integration': ['integrator_1', 'integrator_2'],
            'response': ['responder_1', 'responder_2', 'responder_3'],
            'support': ['support_1', 'support_2'],
            'specialist': ['expert_1', 'expert_2', 'expert_3', 'expert_4']
        }
        
        import random
        
        for team_type, team_agents in team_mapping.items():
            team_agents_data = [agent_id for agent_id, data in agent_data.items() 
                              if data['name'] in [f"{team_type}_{agent.split('_')[1]}" for agent in team_agents]]
            
            if team_agents_data:
                # Calculate team metrics
                total_agents = len(team_agents_data)
                active_agents = len([aid for aid in team_agents_data 
                                   if agent_data[aid]['status'] == 'running'])
                
                avg_health = sum(agent_data[aid]['metrics']['health_score'] 
                               for aid in team_agents_data) / total_agents
                
                total_tasks = sum(agent_data[aid]['metrics']['tasks_completed'] 
                                for aid in team_agents_data)
                
                teams[team_type] = {
                    'total_agents': total_agents,
                    'active_agents': active_agents,
                    'avg_health_score': round(avg_health, 1),
                    'total_tasks': total_tasks,
                    'performance_score': round(random.uniform(80, 95), 1),
                    'efficiency': round(random.uniform(0.7, 0.9), 2),
                    'agents': team_agents_data
                }
        
        return teams
    
    def generate_system_metrics(self) -> Dict[str, Any]:
        """Generate system metrics"""
        import random
        
        return {
            'cpu_usage': round(random.uniform(25, 45), 1),
            'memory_usage': round(random.uniform(40, 65), 1),
            'disk_usage': round(random.uniform(30, 55), 1),
            'network_latency': round(random.uniform(10, 50), 1),
            'active_connections': random.randint(50, 150),
            'throughput': round(random.uniform(100, 500), 1),
            'error_rate': round(random.uniform(0.1, 2.5), 2),
            'uptime_hours': random.randint(100, 1000),
            'total_agents': len(self.generate_agent_data()),
            'active_teams': 6
        }

# Mock data generator
mock_generator = MockDataGenerator()

class DashboardWebSocket:
    """Handles WebSocket communication for real-time updates"""
    
    def __init__(self):
        self.clients = set()
        self.update_thread = None
        self.running = False
        
    def start_updates(self):
        """Start sending real-time updates to clients"""
        if self.running:
            return
        
        self.running = True
        self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self.update_thread.start()
        logger.info("Dashboard WebSocket updates started")
        
    def stop_updates(self):
        """Stop real-time updates"""
        self.running = False
        
        if self.update_thread:
            self.update_thread.join(timeout=5)
            
        logger.info("Dashboard WebSocket updates stopped")
    
    def _update_loop(self):
        """Main update loop"""
        while self.running:
            try:
                # Generate fresh mock data
                agent_data = mock_generator.generate_agent_data()
                team_data = mock_generator.generate_team_data(agent_data)
                system_metrics = mock_generator.generate_system_metrics()
                
                # Update data store
                for agent_id, data in agent_data.items():
                    monitoring_store.update_agent_data(agent_id, data)
                    
                for team_name, data in team_data.items():
                    monitoring_store.update_team_data(team_name, data)
                    
                monitoring_store.update_system_metrics(system_metrics)
                
                # Send updates to all connected clients
                dashboard_data = monitoring_store.get_dashboard_data()
                socketio.emit('dashboard_update', dashboard_data, broadcast=True)
                
                time.sleep(5)  # Update every 5 seconds
                
            except Exception as e:
                logger.error(f"Error in dashboard update loop: {str(e)}")
                time.sleep(10)
    
    def add_client(self):
        """Add a new WebSocket client"""
        self.clients.add(request.sid)
        
    def remove_client(self):
        """Remove a WebSocket client"""
        self.clients.discard(request.sid)

# Initialize WebSocket handler
dashboard_ws = DashboardWebSocket()

# Flask routes
@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/agents')
def get_agents():
    """Get all agent data"""
    return jsonify(monitoring_store.agent_data)

@app.route('/api/teams')
def get_teams():
    """Get all team data"""
    return jsonify(monitoring_store.team_data)

@app.route('/api/system')
def get_system_metrics():
    """Get system metrics"""
    return jsonify(monitoring_store.system_metrics)

@app.route('/api/audit-reports')
def get_audit_reports():
    """Get recent audit reports"""
    return jsonify(list(monitoring_store.audit_reports.values()))

@app.route('/api/orchestration')
def get_orchestration_status():
    """Get orchestration status"""
    return jsonify(monitoring_store.orchestration_status)

@app.route('/api/alerts')
def get_alerts():
    """Get alerts"""
    return jsonify(monitoring_store.alerts)

@app.route('/api/dashboard')
def get_dashboard_data():
    """Get comprehensive dashboard data"""
    return jsonify(monitoring_store.get_dashboard_data())

@app.route('/api/agent/<agent_id>')
def get_agent_details(agent_id):
    """Get detailed information for a specific agent"""
    if agent_id in monitoring_store.agent_data:
        return jsonify(monitoring_store.agent_data[agent_id])
    else:
        return jsonify({"error": "Agent not found"}), 404

@app.route('/api/team/<team_name>')
def get_team_details(team_name):
    """Get detailed information for a specific team"""
    if team_name in monitoring_store.team_data:
        return jsonify(monitoring_store.team_data[team_name])
    else:
        return jsonify({"error": "Team not found"}), 404

# WebSocket events
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    dashboard_ws.add_client()
    emit('connected', {'data': 'Connected to Augur Omega Dashboard'})
    
    # Send initial data
    dashboard_data = monitoring_store.get_dashboard_data()
    emit('dashboard_update', dashboard_data)
    
    logger.info(f"Client connected: {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    dashboard_ws.remove_client()
    logger.info(f"Client disconnected: {request.sid}")

@socketio.on('subscribe_agent')
def handle_agent_subscription(data):
    """Handle subscription to specific agent updates"""
    agent_id = data.get('agent_id')
    if agent_id and agent_id in monitoring_store.agent_data:
        emit('agent_update', monitoring_store.agent_data[agent_id])
        logger.info(f"Subscribed to agent {agent_id}")

@socketio.on('subscribe_team')
def handle_team_subscription(data):
    """Handle subscription to specific team updates"""
    team_name = data.get('team_name')
    if team_name and team_name in monitoring_store.team_data:
        emit('team_update', monitoring_store.team_data[team_name])
        logger.info(f"Subscribed to team {team_name}")

@socketio.on('acknowledge_alert')
def handle_alert_acknowledgment(data):
    """Handle alert acknowledgment"""
    alert_id = data.get('alert_id')
    if alert_id:
        for alert in monitoring_store.alerts:
            if alert.get('id') == alert_id:
                alert['acknowledged'] = True
                alert['acknowledged_at'] = datetime.now().isoformat()
                break
        
        # Broadcast acknowledgment to all clients
        emit('alert_acknowledged', {'alert_id': alert_id}, broadcast=True)
        logger.info(f"Alert {alert_id} acknowledged")

# Static file serving
@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    return send_from_directory(app.static_folder, filename)

def run_dashboard(host='0.0.0.0', port=5000, debug=False):
    """Run the monitoring dashboard"""
    logger.info(f"Starting Augur Omega Monitoring Dashboard on {host}:{port}")
    
    # Start WebSocket updates
    dashboard_ws.start_updates()
    
    # Run Flask-SocketIO app
    socketio.run(app, host=host, port=port, debug=debug)

if __name__ == '__main__':
    # Create template and static directories
    template_dir = Path(__file__).parent.parent / "web_dashboard" / "templates"
    static_dir = Path(__file__).parent.parent / "web_dashboard" / "static"
    
    template_dir.mkdir(parents=True, exist_ok=True)
    static_dir.mkdir(parents=True, exist_ok=True)
    
    # Run dashboard
    run_dashboard(debug=True)