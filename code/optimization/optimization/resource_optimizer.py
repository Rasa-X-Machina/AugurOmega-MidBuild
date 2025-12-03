"""
Resource Optimizer - Intelligent resource allocation and management
Optimizes CPU, memory, network, and storage resources for maximum efficiency
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from collections import defaultdict, deque
import json
import numpy as np
import threading
from concurrent.futures import ThreadPoolExecutor
import psutil

@dataclass
class ResourceMetrics:
    """Resource usage metrics"""
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_io: Dict[str, float]
    gpu_usage: Optional[float] = None
    thread_count: int = 0
    file_descriptors: int = 0
    
    def to_dict(self) -> Dict:
        return {
            'timestamp': self.timestamp.isoformat(),
            'cpu_usage': self.cpu_usage,
            'memory_usage': self.memory_usage,
            'disk_usage': self.disk_usage,
            'network_io': self.network_io,
            'gpu_usage': self.gpu_usage,
            'thread_count': self.thread_count,
            'file_descriptors': self.file_descriptors
        }

@dataclass
class ResourceAllocation:
    """Resource allocation configuration"""
    component_id: str
    cpu_cores: float
    memory_gb: float
    disk_gb: float
    network_bandwidth_mbps: float
    priority: str  # 'critical', 'high', 'medium', 'low'
    
    def to_dict(self) -> Dict:
        return {
            'component_id': self.component_id,
            'cpu_cores': self.cpu_cores,
            'memory_gb': self.memory_gb,
            'disk_gb': self.disk_gb,
            'network_bandwidth_mbps': self.network_bandwidth_mbps,
            'priority': self.priority
        }

class ResourceOptimizer:
    """
    Intelligent Resource Optimizer
    Features:
    - Dynamic resource allocation
    - Resource usage prediction
    - Load balancing across components
    - Resource contention detection
    - Automated resource scaling
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or self._default_config()
        self.logger = logging.getLogger(__name__)
        
        # Resource tracking
        self.resource_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.current_allocations: Dict[str, ResourceAllocation] = {}
        self.resource_contention: Dict[str, float] = defaultdict(float)
        
        # System resources
        self.system_resources = self._get_system_resources()
        self.available_resources = {
            'cpu_cores': self.system_resources['cpu_cores'],
            'memory_gb': self.system_resources['memory_gb'],
            'disk_gb': self.system_resources['disk_gb'],
            'network_bandwidth_mbps': self.system_resources.get('network_bandwidth', 1000)
        }
        
        # Optimization strategies
        self.strategies = {
            'balanced': self._balanced_optimization,
            'performance_first': self._performance_first_optimization,
            'efficiency_first': self._efficiency_first_optimization,
            'cost_optimized': self._cost_optimized_optimization
        }
        
        # Optimization settings
        self.optimization_targets = {
            'cpu_utilization': 0.75,  # Target 75% CPU utilization
            'memory_utilization': 0.80,  # Target 80% memory utilization
            'load_balance_threshold': 0.2,  # 20% difference between components
            'contention_threshold': 0.15  # 15% contention threshold
        }
        
        # Threading
        self.optimizer_active = False
        self.optimizer_thread: Optional[threading.Thread] = None
        self.executor = ThreadPoolExecutor(max_workers=3)
        
        self.logger.info("Resource Optimizer initialized")
    
    def _default_config(self) -> Dict:
        """Default configuration for resource optimizer"""
        return {
            'optimization_strategy': 'balanced',
            'optimization_interval': 120,  # seconds
            'enable_predictive_scaling': True,
            'enable_resource_contention_detection': True,
            'enable_automated_scaling': True,
            'scaling_cooldown': 300,  # 5 minutes
            'resource_reservation': 0.1,  # Reserve 10% for system
            'max_over_allocation': 1.2  # Allow 20% over-allocation
        }
    
    def _get_system_resources(self) -> Dict:
        """Get current system resource capabilities"""
        try:
            return {
                'cpu_cores': psutil.cpu_count(),
                'memory_gb': psutil.virtual_memory().total / (1024**3),
                'disk_gb': psutil.disk_usage('/').total / (1024**3),
                'network_bandwidth': 1000,  # Mbps (would be measured in real implementation)
                'available_cpu_cores': psutil.cpu_count(logical=True),
                'available_memory_gb': psutil.virtual_memory().available / (1024**3)
            }
        except Exception as e:
            self.logger.error(f"Error getting system resources: {e}")
            return {
                'cpu_cores': 4,
                'memory_gb': 8,
                'disk_gb': 100,
                'network_bandwidth': 1000,
                'available_cpu_cores': 4,
                'available_memory_gb': 6
            }
    
    def optimize(self, target_component: str, parameters: Dict[str, Any], context: Dict = None) -> Dict:
        """
        Optimize resources for target component
        
        Args:
            target_component: Component to optimize
            parameters: Optimization parameters
            context: Additional context
        
        Returns:
            Optimization result
        """
        try:
            strategy = self.config.get('optimization_strategy', 'balanced')
            
            if strategy not in self.strategies:
                strategy = 'balanced'
            
            # Get current resource usage
            current_usage = self._get_current_resource_usage(target_component)
            
            # Execute optimization strategy
            result = self.strategies[strategy](target_component, current_usage, parameters, context)
            
            # Apply resource optimizations
            optimization_applied = self._apply_resource_optimization(target_component, result['optimal_allocations'])
            
            # Record optimization
            self._record_resource_optimization(target_component, result, optimization_applied)
            
            return {
                'success': optimization_applied,
                'improvement': result.get('expected_improvement', 0.0),
                'optimal_allocations': result.get('optimal_allocations', {}),
                'resource_efficiency': result.get('resource_efficiency', 0.0),
                'optimization_details': result
            }
            
        except Exception as e:
            self.logger.error(f"Error in resource optimization for {target_component}: {e}")
            return {
                'success': False,
                'improvement': 0.0,
                'error': str(e),
                'optimal_allocations': {}
            }
    
    def _balanced_optimization(self, target_component: str, current_usage: ResourceMetrics, 
                              parameters: Dict, context: Dict) -> Dict:
        """Balanced optimization approach"""
        
        # Get component requirements
        component_requirements = parameters.get('requirements', {})
        
        # Calculate optimal allocations based on current usage patterns
        optimal_allocations = {}
        
        # CPU optimization
        cpu_usage = current_usage.cpu_usage
        if cpu_usage > 0.9:
            # High CPU usage - allocate more cores
            optimal_allocations['cpu_cores'] = min(
                self.available_resources['cpu_cores'] * 0.8,
                component_requirements.get('cpu_cores', 4) * 1.5
            )
        elif cpu_usage < 0.3:
            # Low CPU usage - reduce allocation
            optimal_allocations['cpu_cores'] = max(
                1.0,
                component_requirements.get('cpu_cores', 2) * 0.7
            )
        else:
            # Moderate usage - maintain current with slight optimization
            optimal_allocations['cpu_cores'] = component_requirements.get('cpu_cores', 2) * 1.1
        
        # Memory optimization
        memory_usage = current_usage.memory_usage
        if memory_usage > 0.85:
            # High memory usage - increase allocation
            optimal_allocations['memory_gb'] = min(
                self.available_resources['memory_gb'] * 0.7,
                component_requirements.get('memory_gb', 4) * 1.3
            )
        elif memory_usage < 0.4:
            # Low memory usage - reduce allocation
            optimal_allocations['memory_gb'] = max(
                1.0,
                component_requirements.get('memory_gb', 2) * 0.8
            )
        else:
            # Moderate usage - maintain with optimization
            optimal_allocations['memory_gb'] = component_requirements.get('memory_gb', 2) * 1.05
        
        # Disk optimization
        disk_usage = current_usage.disk_usage
        optimal_allocations['disk_gb'] = component_requirements.get('disk_gb', 10) * 1.1
        
        # Network optimization
        optimal_allocations['network_bandwidth_mbps'] = component_requirements.get('network_bandwidth', 100)
        
        # Calculate expected improvements
        cpu_improvement = self._calculate_cpu_improvement(current_usage, optimal_allocations)
        memory_improvement = self._calculate_memory_improvement(current_usage, optimal_allocations)
        total_improvement = (cpu_improvement + memory_improvement) / 2
        
        # Calculate resource efficiency
        resource_efficiency = self._calculate_resource_efficiency(optimal_allocations, current_usage)
        
        return {
            'strategy': 'balanced',
            'optimal_allocations': optimal_allocations,
            'expected_improvement': total_improvement,
            'resource_efficiency': resource_efficiency,
            'reasoning': {
                'cpu_optimization': 'Balanced based on current usage patterns',
                'memory_optimization': 'Adjusted for memory pressure and availability'
            }
        }
    
    def _performance_first_optimization(self, target_component: str, current_usage: ResourceMetrics,
                                       parameters: Dict, context: Dict) -> Dict:
        """Performance-focused optimization"""
        
        component_requirements = parameters.get('requirements', {})
        
        # Maximize resources for performance
        optimal_allocations = {
            'cpu_cores': min(
                self.available_resources['cpu_cores'] * 0.8,
                component_requirements.get('cpu_cores', 8) * 1.5
            ),
            'memory_gb': min(
                self.available_resources['memory_gb'] * 0.7,
                component_requirements.get('memory_gb', 8) * 1.4
            ),
            'disk_gb': component_requirements.get('disk_gb', 20) * 1.2,
            'network_bandwidth_mbps': component_requirements.get('network_bandwidth', 200) * 1.5
        }
        
        total_improvement = 45.0  # High improvement expected for performance focus
        resource_efficiency = 0.65  # Lower efficiency but higher performance
        
        return {
            'strategy': 'performance_first',
            'optimal_allocations': optimal_allocations,
            'expected_improvement': total_improvement,
            'resource_efficiency': resource_efficiency,
            'trade_offs': ['Higher resource usage', 'Better performance', 'Lower efficiency']
        }
    
    def _efficiency_first_optimization(self, target_component: str, current_usage: ResourceMetrics,
                                      parameters: Dict, context: Dict) -> Dict:
        """Efficiency-focused optimization"""
        
        component_requirements = parameters.get('requirements', {})
        
        # Optimize for resource efficiency
        optimal_allocations = {
            'cpu_cores': component_requirements.get('cpu_cores', 2) * 0.9,
            'memory_gb': component_requirements.get('memory_gb', 2) * 0.85,
            'disk_gb': component_requirements.get('disk_gb', 10) * 0.9,
            'network_bandwidth_mbps': component_requirements.get('network_bandwidth', 100) * 0.8
        }
        
        total_improvement = 25.0  # Moderate improvement
        resource_efficiency = 0.85  # High efficiency
        
        return {
            'strategy': 'efficiency_first',
            'optimal_allocations': optimal_allocations,
            'expected_improvement': total_improvement,
            'resource_efficiency': resource_efficiency,
            'benefits': ['Reduced resource usage', 'Higher efficiency', 'Lower costs']
        }
    
    def _cost_optimized_optimization(self, target_component: str, current_usage: ResourceMetrics,
                                    parameters: Dict, context: Dict) -> Dict:
        """Cost-optimized resource allocation"""
        
        component_requirements = parameters.get('requirements', {})
        cost_budget = parameters.get('cost_budget', 100)  # Budget in cost units
        
        # Calculate cost-efficient allocation
        # CPU cost per core: 10 units, Memory cost per GB: 5 units
        
        available_budget = cost_budget * (1 - self.config['resource_reservation'])
        
        # Allocate based on cost efficiency
        cpu_cost_per_core = 10
        memory_cost_per_gb = 5
        disk_cost_per_gb = 2
        network_cost_per_mbps = 1
        
        # Optimal allocation within budget
        cpu_cores = min(
            component_requirements.get('cpu_cores', 4),
            available_budget / cpu_cost_per_core
        )
        
        remaining_budget = available_budget - (cpu_cores * cpu_cost_per_core)
        
        memory_gb = min(
            component_requirements.get('memory_gb', 4),
            remaining_budget / memory_cost_per_gb
        )
        
        remaining_budget -= (memory_gb * memory_cost_per_gb)
        
        optimal_allocations = {
            'cpu_cores': cpu_cores,
            'memory_gb': memory_gb,
            'disk_gb': component_requirements.get('disk_gb', 10) * 0.8,
            'network_bandwidth_mbps': min(
                component_requirements.get('network_bandwidth', 100),
                remaining_budget / network_cost_per_mbps
            )
        }
        
        total_improvement = 20.0  # Conservative improvement for cost efficiency
        resource_efficiency = 0.9  # Very high efficiency
        
        return {
            'strategy': 'cost_optimized',
            'optimal_allocations': optimal_allocations,
            'expected_improvement': total_improvement,
            'resource_efficiency': resource_efficiency,
            'cost_budget_used': available_budget - remaining_budget,
            'efficiency_gains': 'Maximum resource utilization within budget constraints'
        }
    
    def _get_current_resource_usage(self, component_id: str) -> ResourceMetrics:
        """Get current resource usage for component"""
        # In a real implementation, this would get actual resource usage
        # For now, generate realistic metrics
        
        import random
        
        return ResourceMetrics(
            timestamp=datetime.now(),
            cpu_usage=random.uniform(0.2, 0.9),
            memory_usage=random.uniform(0.3, 0.85),
            disk_usage=random.uniform(0.1, 0.6),
            network_io={
                'bytes_sent': random.randint(1000, 10000),
                'bytes_recv': random.randint(5000, 50000)
            },
            thread_count=random.randint(5, 50),
            file_descriptors=random.randint(50, 500)
        )
    
    def _calculate_cpu_improvement(self, current: ResourceMetrics, allocations: Dict) -> float:
        """Calculate expected CPU improvement"""
        current_cpu = current.cpu_usage
        target_utilization = self.optimization_targets['cpu_utilization']
        
        if current_cpu > target_utilization:
            # High CPU usage - expect improvement from better allocation
            return min(30.0, (current_cpu - target_utilization) * 100)
        elif current_cpu < target_utilization * 0.5:
            # Low CPU usage - expect efficiency improvement
            return 10.0
        else:
            return 15.0  # Moderate improvement
    
    def _calculate_memory_improvement(self, current: ResourceMetrics, allocations: Dict) -> float:
        """Calculate expected memory improvement"""
        current_memory = current.memory_usage
        target_utilization = self.optimization_targets['memory_utilization']
        
        if current_memory > target_utilization:
            # High memory usage - expect improvement
            return min(25.0, (current_memory - target_utilization) * 100)
        elif current_memory < target_utilization * 0.4:
            # Low memory usage - efficiency improvement
            return 8.0
        else:
            return 12.0  # Moderate improvement
    
    def _calculate_resource_efficiency(self, allocations: Dict, current: ResourceMetrics) -> float:
        """Calculate resource efficiency score"""
        # Calculate how efficiently resources are allocated
        
        cpu_efficiency = 1.0 - abs(current.cpu_usage - self.optimization_targets['cpu_utilization'])
        memory_efficiency = 1.0 - abs(current.memory_usage - self.optimization_targets['memory_utilization'])
        
        # Check for over-allocation
        total_cpu_allocated = sum(alloc.get('cpu_cores', 0) for alloc in allocations.values())
        total_memory_allocated = sum(alloc.get('memory_gb', 0) for alloc in allocations.values())
        
        over_allocation_penalty = 0
        if total_cpu_allocated > self.available_resources['cpu_cores']:
            over_allocation_penalty += 0.1
        if total_memory_allocated > self.available_resources['memory_gb']:
            over_allocation_penalty += 0.1
        
        efficiency = (cpu_efficiency + memory_efficiency) / 2 - over_allocation_penalty
        return max(0.0, min(1.0, efficiency))
    
    def _apply_resource_optimization(self, component_id: str, optimal_allocations: Dict) -> bool:
        """Apply resource optimizations"""
        try:
            # Create or update allocation
            allocation = ResourceAllocation(
                component_id=component_id,
                cpu_cores=optimal_allocations.get('cpu_cores', 2),
                memory_gb=optimal_allocations.get('memory_gb', 2),
                disk_gb=optimal_allocations.get('disk_gb', 10),
                network_bandwidth_mbps=optimal_allocations.get('network_bandwidth_mbps', 100),
                priority='medium'
            )
            
            self.current_allocations[component_id] = allocation
            
            # Log optimization application
            self.logger.info(f"Applied resource optimization to {component_id}: "
                           f"CPU={allocation.cpu_cores:.1f}, Memory={allocation.memory_gb:.1f}GB")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to apply resource optimization to {component_id}: {e}")
            return False
    
    def _record_resource_optimization(self, component_id: str, result: Dict, success: bool):
        """Record resource optimization for tracking"""
        record = {
            'timestamp': datetime.now(),
            'component_id': component_id,
            'strategy': result.get('strategy', 'unknown'),
            'optimal_allocations': result.get('optimal_allocations', {}),
            'expected_improvement': result.get('expected_improvement', 0.0),
            'resource_efficiency': result.get('resource_efficiency', 0.0),
            'success': success
        }
        
        # Add to component history
        self.resource_history[component_id].append(record)
        
        # Update system-wide metrics
        self._update_system_resource_metrics()
        
        self.logger.info(f"Recorded resource optimization for {component_id}: "
                        f"{result.get('expected_improvement', 0):.1f}% improvement")
    
    def _update_system_resource_metrics(self):
        """Update system-wide resource metrics"""
        total_cpu_allocated = sum(alloc.cpu_cores for alloc in self.current_allocations.values())
        total_memory_allocated = sum(alloc.memory_gb for alloc in self.current_allocations.values())
        
        self.available_resources = {
            'cpu_cores': self.system_resources['cpu_cores'],
            'memory_gb': self.system_resources['memory_gb'],
            'disk_gb': self.system_resources['disk_gb'],
            'network_bandwidth_mbps': self.system_resources.get('network_bandwidth', 1000),
            'allocated_cpu_cores': total_cpu_allocated,
            'allocated_memory_gb': total_memory_allocated
        }
    
    def detect_resource_contention(self) -> Dict[str, float]:
        """Detect resource contention across components"""
        contention_analysis = {}
        
        if len(self.current_allocations) < 2:
            return contention_analysis
        
        # Check for CPU contention
        cpu_allocations = [alloc.cpu_cores for alloc in self.current_allocations.values()]
        cpu_variance = np.var(cpu_allocations)
        cpu_contention = min(1.0, cpu_variance / np.mean(cpu_allocations)) if np.mean(cpu_allocations) > 0 else 0
        
        # Check for memory contention
        memory_allocations = [alloc.memory_gb for alloc in self.current_allocations.values()]
        memory_variance = np.var(memory_allocations)
        memory_contention = min(1.0, memory_variance / np.mean(memory_allocations)) if np.mean(memory_allocations) > 0 else 0
        
        # Overall contention
        overall_contention = (cpu_contention + memory_contention) / 2
        
        contention_analysis = {
            'cpu_contention': cpu_contention,
            'memory_contention': memory_contention,
            'overall_contention': overall_contention,
            'contention_level': 'high' if overall_contention > 0.5 else 'medium' if overall_contention > 0.2 else 'low'
        }
        
        self.resource_contention.update(contention_analysis)
        
        return contention_analysis
    
    def get_resource_optimization_status(self) -> Dict:
        """Get current resource optimization status"""
        active_allocations = len(self.current_allocations)
        
        # Calculate resource utilization
        total_cpu_used = sum(alloc.cpu_cores for alloc in self.current_allocations.values())
        total_memory_used = sum(alloc.memory_gb for alloc in self.current_allocations.values())
        
        cpu_utilization = total_cpu_used / self.system_resources['cpu_cores'] if self.system_resources['cpu_cores'] > 0 else 0
        memory_utilization = total_memory_used / self.system_resources['memory_gb'] if self.system_resources['memory_gb'] > 0 else 0
        
        # Get recent optimizations
        recent_cutoff = datetime.now() - timedelta(hours=24)
        recent_optimizations = []
        
        for component_history in self.resource_history.values():
            for record in component_history:
                if record['timestamp'] > recent_cutoff:
                    recent_optimizations.append(record)
        
        successful_optimizations = sum(1 for opt in recent_optimizations if opt.get('success', False))
        
        return {
            "timestamp": datetime.now().isoformat(),
            "active_allocations": active_allocations,
            "total_cpu_allocated": total_cpu_used,
            "total_memory_allocated": total_memory_used,
            "cpu_utilization": round(cpu_utilization * 100, 1),
            "memory_utilization": round(memory_utilization * 100, 1),
            "recent_optimizations": len(recent_optimizations),
            "successful_optimizations": successful_optimizations,
            "optimization_success_rate": successful_optimizations / len(recent_optimizations) if recent_optimizations else 0,
            "resource_contention": self.resource_contention.get('overall_contention', 0.0),
            "available_resources": {
                "cpu_cores": self.system_resources['cpu_cores'],
                "memory_gb": round(self.system_resources['memory_gb'], 1),
                "disk_gb": round(self.system_resources['disk_gb'], 1)
            }
        }
    
    def export_resource_optimization_results(self, output_path: str):
        """Export resource optimization results"""
        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "status": self.get_resource_optimization_status(),
            "current_allocations": {cid: alloc.to_dict() for cid, alloc in self.current_allocations.items()},
            "resource_history": {
                cid: [record for record in history]
                for cid, history in self.resource_history.items()
            },
            "resource_contention": dict(self.resource_contention),
            "system_resources": self.system_resources
        }
        
        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        self.logger.info(f"Resource optimization results exported to {output_path}")
