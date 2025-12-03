"""
Performance Dashboard - Real-time visualization and monitoring interface
Provides comprehensive views of performance metrics and system health
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import json
from collections import defaultdict, deque
import threading
from concurrent.futures import ThreadPoolExecutor

try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib.animation import FuncAnimation
    import seaborn as sns
    import pandas as pd
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("Warning: matplotlib not available. Dashboard will use text-based display.")

@dataclass
class DashboardConfig:
    """Configuration for performance dashboard"""
    refresh_interval: float = 2.0  # seconds
    max_data_points: int = 200
    enable_real_time_plots: bool = True
    save_snapshots: bool = True
    snapshot_interval: int = 300  # 5 minutes
    
    # Display settings
    show_system_overview: bool = True
    show_agent_details: bool = True
    show_alerts: bool = True
    show_optimization_suggestions: bool = True

class PerformanceDashboard:
    """
    Real-time Performance Dashboard for Augur Omega
    Features:
    - Real-time performance visualization
    - Interactive charts and graphs
    - System health overview
    - Alert monitoring
    - Optimization recommendations
    """
    
    def __init__(self, config: Optional[DashboardConfig] = None):
        self.config = config or DashboardConfig()
        self.logger = logging.getLogger(__name__)
        
        # Data storage
        self.monitoring_data: Dict[str, deque] = defaultdict(lambda: deque(maxlen=self.config.max_data_points))
        self.system_metrics: Dict[str, Any] = {}
        self.alert_data: List[Dict] = []
        self.optimization_suggestions: List[Dict] = []
        
        # Dashboard state
        self.dashboard_active = False
        self.last_update = datetime.now()
        
        # Threading
        self.dashboard_thread: Optional[threading.Thread] = None
        self.executor = ThreadPoolExecutor(max_workers=2)
        
        # Visualization
        self.charts: Dict[str, Any] = {}
        if HAS_MATPLOTLIB:
            self._setup_matplotlib()
        
        self.logger.info("Performance Dashboard initialized")
    
    def _setup_matplotlib(self):
        """Setup matplotlib configuration"""
        plt.style.use('seaborn-v0_8' if 'seaborn-v0_8' in plt.style.available else 'seaborn')
        plt.rcParams['figure.figsize'] = (15, 10)
        plt.rcParams['font.size'] = 10
        plt.rcParams['axes.labelsize'] = 10
        plt.rcParams['axes.titlesize'] = 14
    
    async def start(self):
        """Start the performance dashboard"""
        if self.dashboard_active:
            self.logger.warning("Dashboard already running")
            return
        
        self.dashboard_active = True
        
        # Start dashboard thread
        self.dashboard_thread = threading.Thread(target=self._dashboard_loop, daemon=True)
        self.dashboard_thread.start()
        
        # Start real-time plotting if enabled
        if self.config.enable_real_time_plots and HAS_MATPLOTLIB:
            self._start_real_time_plotting()
        
        self.logger.info("📊 Performance Dashboard started")
    
    async def stop(self):
        """Stop the performance dashboard"""
        self.dashboard_active = False
        
        if self.dashboard_thread:
            self.dashboard_thread.join(timeout=5)
        
        self.logger.info("Performance Dashboard stopped")
    
    def update_metrics(self, agent_id: str, metrics_data: Dict):
        """Update metrics for display"""
        timestamp = datetime.now()
        
        # Store raw data
        for metric_name, value in metrics_data.items():
            data_point = {
                'timestamp': timestamp,
                'agent_id': agent_id,
                'value': value
            }
            self.monitoring_data[f"{agent_id}:{metric_name}"].append(data_point)
        
        # Update system overview
        self._update_system_overview(agent_id, metrics_data)
    
    def _update_system_overview(self, agent_id: str, metrics_data: Dict):
        """Update system-wide overview metrics"""
        if 'system_overview' not in self.system_metrics:
            self.system_metrics['system_overview'] = {
                'total_agents': 0,
                'healthy_agents': 0,
                'avg_cpu': 0,
                'avg_memory': 0,
                'avg_latency': 0,
                'total_throughput': 0,
                'active_alerts': 0
            }
        
        overview = self.system_metrics['system_overview']
        overview['total_agents'] += 1
        
        # Calculate running averages
        cpu = metrics_data.get('cpu_usage', 0)
        memory = metrics_data.get('memory_usage', 0)
        latency = metrics_data.get('latency_p95', 0)
        throughput = metrics_data.get('throughput', 0)
        
        # Update cumulative averages
        n = overview['total_agents']
        overview['avg_cpu'] = (overview['avg_cpu'] * (n-1) + cpu) / n
        overview['avg_memory'] = (overview['avg_memory'] * (n-1) + memory) / n
        overview['avg_latency'] = (overview['avg_latency'] * (n-1) + latency) / n
        overview['total_throughput'] += throughput
        
        # Update health count
        health_score = self._calculate_health_score(metrics_data)
        if health_score > 70:
            overview['healthy_agents'] += 1
    
    def _calculate_health_score(self, metrics: Dict) -> float:
        """Calculate agent health score"""
        score = 100.0
        
        if metrics.get('cpu_usage', 0) > 90:
            score -= 20
        elif metrics.get('cpu_usage', 0) > 80:
            score -= 10
        
        if metrics.get('memory_usage', 0) > 90:
            score -= 20
        
        if metrics.get('latency_p95', 0) > 150:
            score -= 20
        
        if metrics.get('error_rate', 0) > 0.05:
            score -= 25
        
        return max(0.0, score)
    
    def update_alerts(self, alert_data: Dict):
        """Update alert data for display"""
        self.alert_data.append({
            'timestamp': datetime.now(),
            'data': alert_data
        })
        
        # Keep only recent alerts (last 100)
        if len(self.alert_data) > 100:
            self.alert_data = self.alert_data[-100:]
    
    def add_optimization_suggestion(self, suggestion: Dict):
        """Add optimization suggestion"""
        self.optimization_suggestions.append({
            'timestamp': datetime.now(),
            'suggestion': suggestion
        })
        
        # Keep only recent suggestions
        if len(self.optimization_suggestions) > 50:
            self.optimization_suggestions = self.optimization_suggestions[-50:]
    
    def _dashboard_loop(self):
        """Main dashboard update loop"""
        while self.dashboard_active:
            try:
                # Update dashboard data
                self._update_dashboard_display()
                
                # Save snapshots if enabled
                if self.config.save_snapshots:
                    self._save_snapshot()
                
                import time
                time.sleep(self.config.refresh_interval)
                
            except Exception as e:
                self.logger.error(f"Error in dashboard loop: {e}")
                import time
                time.sleep(5)
    
    def _update_dashboard_display(self):
        """Update the dashboard display"""
        if not HAS_MATPLOTLIB:
            self._display_text_dashboard()
        else:
            self._display_graphical_dashboard()
    
    def _display_text_dashboard(self):
        """Text-based dashboard display"""
        print("\n" + "="*80)
        print("🚀 AUGUR OMEGA PERFORMANCE DASHBOARD")
        print("="*80)
        
        # System overview
        if 'system_overview' in self.system_metrics:
            overview = self.system_metrics['system_overview']
            health_percentage = (overview['healthy_agents'] / overview['total_agents'] * 100) if overview['total_agents'] > 0 else 0
            
            print(f"📊 SYSTEM OVERVIEW:")
            print(f"  Total Agents: {overview['total_agents']}")
            print(f"  Healthy Agents: {overview['healthy_agents']} ({health_percentage:.1f}%)")
            print(f"  Average CPU: {overview['avg_cpu']:.1f}%")
            print(f"  Average Memory: {overview['avg_memory']:.1f}%")
            print(f"  Average Latency: {overview['avg_latency']:.1f}ms")
            print(f"  Total Throughput: {overview['total_throughput']:.0f} ops/sec")
        
        # Recent alerts
        if self.alert_data:
            print(f"\n🚨 RECENT ALERTS ({len(self.alert_data)}):")
            for alert in self.alert_data[-5:]:  # Show last 5
                alert_info = alert['data']
                print(f"  [{alert_info.get('severity', 'unknown').upper()}] {alert_info.get('message', 'No message')}")
        
        # Optimization suggestions
        if self.optimization_suggestions:
            print(f"\n💡 OPTIMIZATION SUGGESTIONS ({len(self.optimization_suggestions)}):")
            for suggestion in self.optimization_suggestions[-3:]:  # Show last 3
                sugg_info = suggestion['suggestion']
                print(f"  {sugg_info.get('type', 'unknown')}: {sugg_info.get('description', 'No description')}")
        
        print(f"Last Update: {datetime.now().strftime('%H:%M:%S')}")
        print("="*80)
    
    def _display_graphical_dashboard(self):
        """Graphical dashboard display"""
        try:
            # Create figure with subplots
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
            fig.suptitle('🚀 Augur Omega Performance Dashboard', fontsize=16, fontweight='bold')
            
            # System Overview Chart
            if 'system_overview' in self.system_metrics:
                self._plot_system_overview(ax1)
            
            # CPU Usage Over Time
            self._plot_metric_trend(ax2, 'cpu_usage', 'CPU Usage (%)', 'red')
            
            # Latency Trends
            self._plot_metric_trend(ax3, 'latency_p95', 'Latency P95 (ms)', 'orange')
            
            # Health Score Distribution
            self._plot_health_distribution(ax4)
            
            plt.tight_layout()
            plt.show(block=False)
            plt.pause(0.1)
            
        except Exception as e:
            self.logger.error(f"Error in graphical display: {e}")
            self._display_text_dashboard()
    
    def _plot_system_overview(self, ax):
        """Plot system overview metrics"""
        overview = self.system_metrics['system_overview']
        
        # Create overview chart
        metrics = ['CPU', 'Memory', 'Latency', 'Health %']
        values = [
            overview['avg_cpu'],
            overview['avg_memory'],
            min(overview['avg_latency'] / 2, 100),  # Scale latency to 0-100
            (overview['healthy_agents'] / overview['total_agents'] * 100) if overview['total_agents'] > 0 else 0
        ]
        
        colors = ['red' if v > 80 else 'orange' if v > 60 else 'green' for v in values]
        
        bars = ax.bar(metrics, values, color=colors, alpha=0.7)
        ax.set_title('System Overview', fontweight='bold')
        ax.set_ylabel('Percentage')
        ax.set_ylim(0, 100)
        
        # Add value labels on bars
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                   f'{value:.1f}', ha='center', va='bottom')
    
    def _plot_metric_trend(self, ax, metric_name: str, title: str, color: str):
        """Plot metric trend over time"""
        # Aggregate data from all agents for this metric
        timestamps = []
        values = []
        
        for agent_metric, data_points in self.monitoring_data.items():
            if metric_name in agent_metric:
                for dp in list(data_points)[-50:]:  # Last 50 points
                    timestamps.append(dp['timestamp'])
                    values.append(dp['value'])
        
        if timestamps and values:
            # Sort by timestamp
            combined = list(zip(timestamps, values))
            combined.sort(key=lambda x: x[0])
            timestamps, values = zip(*combined)
            
            # Plot trend
            ax.plot(timestamps, values, color=color, alpha=0.7, linewidth=2)
            ax.fill_between(timestamps, values, alpha=0.3, color=color)
            
            # Formatting
            ax.set_title(title, fontweight='bold')
            ax.set_ylabel('Value')
            
            # Format x-axis
            if len(timestamps) > 1:
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
                ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=5))
                plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        else:
            ax.text(0.5, 0.5, f'No {metric_name} data available', 
                   ha='center', va='center', transform=ax.transAxes)
            ax.set_title(title, fontweight='bold')
    
    def _plot_health_distribution(self, ax):
        """Plot health score distribution"""
        health_scores = []
        
        # Extract health scores from recent metrics
        for agent_metric, data_points in self.monitoring_data.items():
            if 'health_score' in agent_metric:
                for dp in list(data_points)[-10:]:  # Last 10 points per agent
                    health_scores.append(dp['value'])
        
        if health_scores:
            # Create histogram
            ax.hist(health_scores, bins=20, alpha=0.7, color='green', edgecolor='black')
            ax.axvline(x=70, color='red', linestyle='--', label='Healthy Threshold')
            ax.set_title('Health Score Distribution', fontweight='bold')
            ax.set_xlabel('Health Score')
            ax.set_ylabel('Number of Agents')
            ax.legend()
            ax.set_xlim(0, 100)
        else:
            ax.text(0.5, 0.5, 'No health data available', 
                   ha='center', va='center', transform=ax.transAxes)
            ax.set_title('Health Score Distribution', fontweight='bold')
    
    def _start_real_time_plotting(self):
        """Start real-time plotting animation"""
        try:
            self.anim = FuncAnimation(plt.gcf(), self._update_plots, interval=2000, blit=False)
        except Exception as e:
            self.logger.error(f"Error starting real-time plotting: {e}")
    
    def _update_plots(self, frame):
        """Update plots for animation"""
        if HAS_MATPLOTLIB:
            # This would be called by FuncAnimation
            # For now, just return empty list
            pass
    
    def _save_snapshot(self):
        """Save dashboard snapshot"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            snapshot_path = f"code/optimization/docs/dashboard_snapshot_{timestamp}.json"
            
            snapshot_data = {
                "timestamp": datetime.now().isoformat(),
                "system_metrics": self.system_metrics,
                "alert_count": len(self.alert_data),
                "optimization_count": len(self.optimization_suggestions),
                "monitoring_data_summary": {
                    agent_metric: len(data_points) 
                    for agent_metric, data_points in self.monitoring_data.items()
                }
            }
            
            with open(snapshot_path, 'w') as f:
                json.dump(snapshot_data, f, indent=2, default=str)
                
        except Exception as e:
            self.logger.error(f"Error saving snapshot: {e}")
    
    def get_dashboard_summary(self) -> Dict:
        """Get dashboard summary for API"""
        return {
            "timestamp": datetime.now().isoformat(),
            "system_metrics": self.system_metrics,
            "recent_alerts": len(self.alert_data),
            "optimization_suggestions": len(self.optimization_suggestions),
            "active_agents": len(set(dp['agent_id'] for data_points in self.monitoring_data.values() for dp in data_points)),
            "total_data_points": sum(len(data_points) for data_points in self.monitoring_data.values())
        }
    
    def export_dashboard_data(self, output_path: str):
        """Export all dashboard data"""
        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "dashboard_config": {
                "refresh_interval": self.config.refresh_interval,
                "max_data_points": self.config.max_data_points,
                "enable_real_time_plots": self.config.enable_real_time_plots
            },
            "system_metrics": self.system_metrics,
            "alert_data": self.alert_data,
            "optimization_suggestions": self.optimization_suggestions,
            "monitoring_data": {}
        }
        
        # Convert monitoring data
        for agent_metric, data_points in self.monitoring_data.items():
            export_data["monitoring_data"][agent_metric] = [
                {
                    'timestamp': dp['timestamp'].isoformat(),
                    'agent_id': dp['agent_id'],
                    'value': dp['value']
                }
                for dp in data_points
            ]
        
        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        self.logger.info(f"Dashboard data exported to {output_path}")
