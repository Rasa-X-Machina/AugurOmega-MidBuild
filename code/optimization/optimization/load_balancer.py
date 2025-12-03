"""
Intelligent Load Balancer - Advanced load distribution and routing
Implements ML-based load balancing for optimal performance across distributed agents
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from collections import defaultdict, deque
import json
import numpy as np
import threading
from concurrent.futures import ThreadPoolExecutor

try:
    from sklearn.cluster import KMeans
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.preprocessing import StandardScaler
    HAS_ML = True
except ImportError:
    HAS_ML = False

@dataclass
class LoadMetrics:
    """Load metrics for an agent or service"""
    agent_id: str
    timestamp: datetime
    current_load: float  # 0-1
    response_time: float  # milliseconds
    throughput: float  # requests per second
    error_rate: float  # 0-1
    cpu_usage: float  # 0-1
    memory_usage: float  # 0-1
    queue_length: int
    active_connections: int
    
    def to_dict(self) -> Dict:
        return {
            'agent_id': self.agent_id,
            'timestamp': self.timestamp.isoformat(),
            'current_load': self.current_load,
            'response_time': self.response_time,
            'throughput': self.throughput,
            'error_rate': self.error_rate,
            'cpu_usage': self.cpu_usage,
            'memory_usage': self.memory_usage,
            'queue_length': self.queue_length,
            'active_connections': self.active_connections
        }

@dataclass
class RoutingRule:
    """Intelligent routing rule"""
    id: str
    name: str
    rule_type: str  # 'performance_based', 'location_based', 'capacity_based', 'ml_based'
    conditions: Dict[str, Any]
    target_agents: List[str]
    priority: int
    weight: float  # 0-1
    active: bool = True
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'name': self.name,
            'rule_type': self.rule_type,
            'conditions': self.conditions,
            'target_agents': self.target_agents,
            'priority': self.priority,
            'weight': self.weight,
            'active': self.active
        }

class IntelligentLoadBalancer:
    """
    Intelligent Load Balancer for Distributed Systems
    Features:
    - ML-based load prediction
    - Dynamic routing optimization
    - Multi-objective load balancing
    - Real-time performance monitoring
    - Automatic failover and recovery
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or self._default_config()
        self.logger = logging.getLogger(__name__)
        
        # Load tracking
        self.load_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.current_loads: Dict[str, LoadMetrics] = {}
        self.routing_rules: Dict[str, RoutingRule] = {}
        
        # ML models (if available)
        self.models: Dict[str, Any] = {}
        self.scalers: Dict[str, StandardScaler] = {}
        
        # Load balancing strategies
        self.strategies = {
            'round_robin': self._round_robin_balancing,
            'least_connections': self._least_connections_balancing,
            'weighted_round_robin': self._weighted_round_robin_balancing,
            'performance_based': self._performance_based_balancing,
            'ml_intelligent': self._ml_intelligent_balancing,
            'predictive': self._predictive_balancing
        }
        
        # Load balancing configuration
        self.balancing_config = {
            'max_load_threshold': 0.9,
            'optimal_load_range': (0.3, 0.7),
            'performance_weights': {
                'response_time': 0.4,
                'throughput': 0.3,
                'error_rate': 0.3
            },
            'rebalance_threshold': 0.15,  # 15% load difference triggers rebalancing
            'health_check_interval': 30  # seconds
        }
        
        # Load prediction
        self.prediction_models = {}
        self.load_predictions: Dict[str, Dict] = {}
        
        # Threading
        self.load_balancer_active = False
        self.balancer_thread: Optional[threading.Thread] = None
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Initialize ML models
        if HAS_ML:
            self._initialize_ml_models()
        
        # Load default routing rules
        self._load_default_routing_rules()
        
        self.logger.info("Intelligent Load Balancer initialized")
    
    def _default_config(self) -> Dict:
        """Default configuration for load balancer"""
        return {
            'balancing_strategy': 'ml_intelligent' if HAS_ML else 'performance_based',
            'enable_predictive_balancing': True,
            'enable_dynamic_routing': True,
            'enable_automatic_failover': True,
            'load_prediction_window': 300,  # 5 minutes
            'rebalancing_interval': 60,  # seconds
            'max_routing_rules': 20,
            'learning_rate': 0.01
        }
    
    def _initialize_ml_models(self):
        """Initialize machine learning models"""
        try:
            # Load prediction model
            self.models['load_predictor'] = RandomForestRegressor(
                n_estimators=100,
                random_state=42,
                max_depth=15
            )
            
            # Routing optimization model
            self.models['routing_optimizer'] = RandomForestRegressor(
                n_estimators=50,
                random_state=42
            )
            
            # Performance clustering model
            self.models['performance_cluster'] = KMeans(
                n_clusters=5,
                random_state=42,
                n_init=10
            )
            
            # Feature scaler
            self.scalers['feature_scaler'] = StandardScaler()
            
            self.logger.info("ML models initialized for load balancing")
            
        except Exception as e:
            self.logger.error(f"Error initializing ML models: {e}")
    
    def _load_default_routing_rules(self):
        """Load default routing rules"""
        
        # Performance-based routing
        performance_rule = RoutingRule(
            id="performance_based",
            name="Performance-Based Routing",
            rule_type="performance_based",
            conditions={
                "metric": "response_time",
                "operator": "<",
                "threshold": 100
            },
            target_agents=[],  # Will be populated dynamically
            priority=1,
            weight=0.8
        )
        
        # Capacity-based routing
        capacity_rule = RoutingRule(
            id="capacity_based",
            name="Capacity-Based Routing",
            rule_type="capacity_based",
            conditions={
                "metric": "available_capacity",
                "operator": ">",
                "threshold": 0.5
            },
            target_agents=[],
            priority=2,
            weight=0.6
        )
        
        # Geographic routing (if location data available)
        location_rule = RoutingRule(
            id="location_based",
            name="Location-Based Routing",
            rule_type="location_based",
            conditions={
                "metric": "distance",
                "operator": "<",
                "threshold": 100
            },
            target_agents=[],
            priority=3,
            weight=0.4
        )
        
        # ML-based intelligent routing
        ml_rule = RoutingRule(
            id="ml_intelligent",
            name="ML-Intelligent Routing",
            rule_type="ml_based",
            conditions={
                "use_ml_prediction": True,
                "confidence_threshold": 0.7
            },
            target_agents=[],
            priority=1,
            weight=1.0
        )
        
        self.routing_rules = {
            performance_rule.id: performance_rule,
            capacity_rule.id: capacity_rule,
            location_rule.id: location_rule,
            ml_rule.id: ml_rule
        }
        
        self.logger.info("Loaded default routing rules")
    
    def optimize(self, target_component: str, parameters: Dict[str, Any], context: Dict = None) -> Dict:
        """
        Optimize load balancing for target component
        
        Args:
            target_component: Component to optimize
            parameters: Optimization parameters
            context: Additional context
        
        Returns:
            Optimization result
        """
        try:
            strategy = self.config.get('balancing_strategy', 'performance_based')
            
            if strategy not in self.strategies:
                strategy = 'performance_based'
            
            # Get current load metrics
            available_agents = parameters.get('available_agents', [])
            current_loads = self._get_current_load_metrics(available_agents)
            
            # Execute balancing strategy
            result = self.strategies[strategy](target_component, current_loads, parameters, context)
            
            # Apply load balancing optimizations
            optimization_applied = self._apply_load_balancing(target_component, result['routing_plan'])
            
            # Record optimization
            self._record_load_balancing_optimization(target_component, result, optimization_applied)
            
            return {
                'success': optimization_applied,
                'improvement': result.get('expected_improvement', 0.0),
                'routing_plan': result.get('routing_plan', {}),
                'load_balance_score': result.get('load_balance_score', 0.0),
                'optimization_details': result
            }
            
        except Exception as e:
            self.logger.error(f"Error in load balancing optimization for {target_component}: {e}")
            return {
                'success': False,
                'improvement': 0.0,
                'error': str(e),
                'routing_plan': {}
            }
    
    def _round_robin_balancing(self, target_component: str, loads: Dict[str, LoadMetrics], 
                              parameters: Dict, context: Dict) -> Dict:
        """Round-robin load balancing"""
        available_agents = list(loads.keys())
        
        if not available_agents:
            return {
                'strategy': 'round_robin',
                'routing_plan': {},
                'expected_improvement': 0.0,
                'load_balance_score': 0.0
            }
        
        # Simple round-robin routing plan
        routing_plan = {}
        for i, agent_id in enumerate(available_agents):
            routing_plan[agent_id] = {
                'traffic_percentage': 100.0 / len(available_agents),
                'max_connections': parameters.get('max_connections_per_agent', 100),
                'routing_method': 'round_robin'
            }
        
        return {
            'strategy': 'round_robin',
            'routing_plan': routing_plan,
            'expected_improvement': 15.0,
            'load_balance_score': 0.6,
            'routing_method': 'Sequential distribution across all agents'
        }
    
    def _least_connections_balancing(self, target_component: str, loads: Dict[str, LoadMetrics],
                                    parameters: Dict, context: Dict) -> Dict:
        """Least connections load balancing"""
        
        # Calculate connection load for each agent
        connection_loads = {}
        for agent_id, load_metrics in loads.items():
            connection_loads[agent_id] = load_metrics.active_connections + load_metrics.queue_length
        
        # Sort by least connections
        sorted_agents = sorted(connection_loads.items(), key=lambda x: x[1])
        
        # Create routing plan based on connection load
        total_connections = sum(connection_loads.values())
        routing_plan = {}
        
        for agent_id, connections in sorted_agents:
            if total_connections > 0:
                traffic_percentage = (total_connections - connections) / total_connections * 100
            else:
                traffic_percentage = 100.0 / len(sorted_agents)
            
            routing_plan[agent_id] = {
                'traffic_percentage': traffic_percentage,
                'current_connections': connections,
                'max_connections': parameters.get('max_connections_per_agent', 100),
                'routing_method': 'least_connections'
            }
        
        return {
            'strategy': 'least_connections',
            'routing_plan': routing_plan,
            'expected_improvement': 25.0,
            'load_balance_score': 0.75,
            'routing_method': 'Routes to agents with fewer active connections'
        }
    
    def _weighted_round_robin_balancing(self, target_component: str, loads: Dict[str, LoadMetrics],
                                        parameters: Dict, context: Dict) -> Dict:
        """Weighted round-robin load balancing"""
        
        # Calculate weights based on agent capacity and performance
        agent_weights = {}
        for agent_id, load_metrics in loads.items():
            # Weight based on available capacity and performance
            capacity_factor = 1.0 - load_metrics.current_load
            performance_factor = 1.0 / (1.0 + load_metrics.response_time / 100)  # Lower response time = higher weight
            
            # Base weight (can be customized per agent)
            base_weight = parameters.get('agent_weights', {}).get(agent_id, 1.0)
            
            agent_weights[agent_id] = base_weight * capacity_factor * performance_factor
        
        # Normalize weights
        total_weight = sum(agent_weights.values())
        if total_weight == 0:
            total_weight = 1.0
        
        routing_plan = {}
        for agent_id, weight in agent_weights.items():
            traffic_percentage = (weight / total_weight) * 100
            
            routing_plan[agent_id] = {
                'traffic_percentage': traffic_percentage,
                'weight': weight,
                'max_connections': parameters.get('max_connections_per_agent', 100) * weight,
                'routing_method': 'weighted_round_robin'
            }
        
        return {
            'strategy': 'weighted_round_robin',
            'routing_plan': routing_plan,
            'expected_improvement': 35.0,
            'load_balance_score': 0.8,
            'routing_method': 'Weighted distribution based on capacity and performance'
        }
    
    def _performance_based_balancing(self, target_component: str, loads: Dict[str, LoadMetrics],
                                    parameters: Dict, context: Dict) -> Dict:
        """Performance-based intelligent load balancing"""
        
        # Calculate performance scores for each agent
        performance_scores = {}
        for agent_id, load_metrics in loads.items():
            # Calculate performance score (0-1, higher is better)
            response_time_score = max(0, 1.0 - load_metrics.response_time / 200)  # Normalize to 200ms
            throughput_score = min(1.0, load_metrics.throughput / 1000)  # Normalize to 1000 req/s
            error_rate_score = max(0, 1.0 - load_metrics.error_rate * 10)  # Penalize errors
            load_score = max(0, 1.0 - load_metrics.current_load)
            
            # Weighted performance score
            weights = self.balancing_config['performance_weights']
            performance_score = (
                weights['response_time'] * response_time_score +
                weights['throughput'] * throughput_score +
                weights['error_rate'] * error_rate_score
            ) * load_score
            
            performance_scores[agent_id] = performance_score
        
        # Create routing plan based on performance scores
        total_score = sum(performance_scores.values())
        routing_plan = {}
        
        if total_score > 0:
            for agent_id, score in performance_scores.items():
                traffic_percentage = (score / total_score) * 100
                
                routing_plan[agent_id] = {
                    'traffic_percentage': traffic_percentage,
                    'performance_score': score,
                    'max_connections': int(parameters.get('max_connections_per_agent', 100) * score),
                    'routing_method': 'performance_based'
                }
        else:
            # Fallback to equal distribution
            equal_percentage = 100.0 / len(loads)
            for agent_id in loads.keys():
                routing_plan[agent_id] = {
                    'traffic_percentage': equal_percentage,
                    'performance_score': 0,
                    'max_connections': parameters.get('max_connections_per_agent', 100),
                    'routing_method': 'performance_based_fallback'
                }
        
        return {
            'strategy': 'performance_based',
            'routing_plan': routing_plan,
            'expected_improvement': 45.0,
            'load_balance_score': 0.85,
            'performance_scores': performance_scores,
            'routing_method': 'Routes based on real-time performance metrics'
        }
    
    def _ml_intelligent_balancing(self, target_component: str, loads: Dict[str, LoadMetrics],
                                 parameters: Dict, context: Dict) -> Dict:
        """ML-based intelligent load balancing"""
        
        if not HAS_ML or 'load_predictor' not in self.models:
            # Fallback to performance-based
            return self._performance_based_balancing(target_component, loads, parameters, context)
        
        try:
            # Prepare training data from load history
            training_data = self._prepare_load_prediction_data()
            
            if len(training_data) < 20:
                # Not enough data for ML, fallback to performance-based
                return self._performance_based_balancing(target_component, loads, parameters, context)
            
            # Train ML models
            self._train_load_prediction_models(training_data)
            
            # Predict optimal load distribution
            predicted_loads = self._predict_optimal_loads(loads, parameters)
            
            # Create intelligent routing plan
            routing_plan = {}
            total_prediction = sum(predicted_loads.values())
            
            for agent_id, predicted_performance in predicted_loads.items():
                if total_prediction > 0:
                    traffic_percentage = (predicted_performance / total_prediction) * 100
                else:
                    traffic_percentage = 100.0 / len(predicted_loads)
                
                routing_plan[agent_id] = {
                    'traffic_percentage': traffic_percentage,
                    'predicted_performance': predicted_performance,
                    'max_connections': int(parameters.get('max_connections_per_agent', 100) * predicted_performance),
                    'routing_method': 'ml_intelligent',
                    'confidence': self._calculate_prediction_confidence(agent_id, training_data)
                }
            
            return {
                'strategy': 'ml_intelligent',
                'routing_plan': routing_plan,
                'expected_improvement': 60.0,
                'load_balance_score': 0.9,
                'predicted_loads': predicted_loads,
                'routing_method': 'ML-based prediction of optimal load distribution',
                'training_samples': len(training_data)
            }
            
        except Exception as e:
            self.logger.error(f"Error in ML intelligent balancing: {e}")
            return self._performance_based_balancing(target_component, loads, parameters, context)
    
    def _predictive_balancing(self, target_component: str, loads: Dict[str, LoadMetrics],
                             parameters: Dict, context: Dict) -> Dict:
        """Predictive load balancing with trend analysis"""
        
        # Analyze load trends
        load_trends = self._analyze_load_trends(loads)
        
        # Predict future loads
        future_loads = self._predict_future_loads(loads, load_trends)
        
        # Create predictive routing plan
        routing_plan = {}
        
        for agent_id, predicted_load in future_loads.items():
            # Calculate traffic allocation based on predicted capacity
            available_capacity = 1.0 - predicted_load
            
            routing_plan[agent_id] = {
                'traffic_percentage': available_capacity * 100,
                'predicted_load': predicted_load,
                'available_capacity': available_capacity,
                'max_connections': int(parameters.get('max_connections_per_agent', 100) * available_capacity),
                'routing_method': 'predictive',
                'trend_analysis': load_trends.get(agent_id, {})
            }
        
        return {
            'strategy': 'predictive',
            'routing_plan': routing_plan,
            'expected_improvement': 50.0,
            'load_balance_score': 0.88,
            'future_loads': future_loads,
            'routing_method': 'Predicts future loads and adapts routing proactively'
        }
    
    def _get_current_load_metrics(self, agent_ids: List[str]) -> Dict[str, LoadMetrics]:
        """Get current load metrics for agents"""
        load_metrics = {}
        
        for agent_id in agent_ids:
            # In real implementation, this would get actual metrics
            # For now, generate realistic load data
            
            import random
            
            load_metrics[agent_id] = LoadMetrics(
                agent_id=agent_id,
                timestamp=datetime.now(),
                current_load=random.uniform(0.1, 0.9),
                response_time=random.uniform(20, 200),
                throughput=random.uniform(100, 1000),
                error_rate=random.uniform(0.001, 0.02),
                cpu_usage=random.uniform(0.2, 0.9),
                memory_usage=random.uniform(0.3, 0.8),
                queue_length=random.randint(0, 50),
                active_connections=random.randint(10, 200)
            )
        
        return load_metrics
    
    def _analyze_load_trends(self, loads: Dict[str, LoadMetrics]) -> Dict[str, Dict]:
        """Analyze load trends for predictive balancing"""
        trends = {}
        
        for agent_id, current_load in loads.items():
            # Get historical data for trend analysis
            history = list(self.load_history[agent_id])
            
            if len(history) < 5:
                trends[agent_id] = {'trend': 'stable', 'confidence': 0.5}
                continue
            
            # Calculate trend
            recent_loads = [record.get('current_load', 0) for record in history[-10:]]
            
            if len(recent_loads) >= 2:
                # Simple linear trend
                import numpy as np
                x = np.arange(len(recent_loads))
                slope = np.polyfit(x, recent_loads, 1)[0]
                
                if slope > 0.05:
                    trend = 'increasing'
                elif slope < -0.05:
                    trend = 'decreasing'
                else:
                    trend = 'stable'
                
                confidence = min(1.0, len(recent_loads) / 20)
                
                trends[agent_id] = {
                    'trend': trend,
                    'slope': slope,
                    'confidence': confidence
                }
        
        return trends
    
    def _predict_future_loads(self, loads: Dict[str, LoadMetrics], trends: Dict[str, Dict]) -> Dict[str, float]:
        """Predict future loads based on trends"""
        future_loads = {}
        
        prediction_horizon = self.config.get('load_prediction_window', 300)  # 5 minutes
        
        for agent_id, current_load in loads.items():
            trend_info = trends.get(agent_id, {'trend': 'stable', 'confidence': 0.5})
            
            if trend_info['trend'] == 'increasing':
                # Predict load increase
                predicted_load = min(1.0, current_load.current_load + 0.1 * trend_info['confidence'])
            elif trend_info['trend'] == 'decreasing':
                # Predict load decrease
                predicted_load = max(0.0, current_load.current_load - 0.1 * trend_info['confidence'])
            else:
                # Stable trend
                predicted_load = current_load.current_load
            
            future_loads[agent_id] = predicted_load
        
        return future_loads
    
    def _prepare_load_prediction_data(self) -> List[Dict]:
        """Prepare training data for load prediction"""
        training_data = []
        
        for agent_id, history in self.load_history.items():
            for record in history:
                if isinstance(record, dict):
                    training_data.append(record)
        
        return training_data[-500:]  # Last 500 records
    
    def _train_load_prediction_models(self, training_data: List[Dict]):
        """Train ML models for load prediction"""
        if len(training_data) < 10:
            return
        
        try:
            # Prepare features and targets
            features = []
            targets = []
            
            for record in training_data:
                # Extract features
                feature_vector = [
                    record.get('current_load', 0),
                    record.get('response_time', 0),
                    record.get('throughput', 0),
                    record.get('cpu_usage', 0),
                    record.get('memory_usage', 0),
                    record.get('queue_length', 0)
                ]
                
                # Target (next load prediction)
                target = record.get('future_load', record.get('current_load', 0))
                
                features.append(feature_vector)
                targets.append(target)
            
            # Train model
            X = np.array(features)
            y = np.array(targets)
            
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            self.models['load_predictor'].fit(X_scaled, y)
            self.scalers['feature_scaler'] = scaler
            
            self.logger.info(f"Trained load prediction model with {len(training_data)} samples")
            
        except Exception as e:
            self.logger.error(f"Error training load prediction models: {e}")
    
    def _predict_optimal_loads(self, loads: Dict[str, LoadMetrics], parameters: Dict) -> Dict[str, float]:
        """Predict optimal load distribution using ML"""
        if 'load_predictor' not in self.models:
            return {agent_id: 0.5 for agent_id in loads.keys()}
        
        try:
            predictions = {}
            
            for agent_id, load_metrics in loads.items():
                # Prepare feature vector
                features = np.array([[
                    load_metrics.current_load,
                    load_metrics.response_time,
                    load_metrics.throughput,
                    load_metrics.cpu_usage,
                    load_metrics.memory_usage,
                    load_metrics.queue_length
                ]])
                
                # Scale features
                features_scaled = self.scalers['feature_scaler'].transform(features)
                
                # Predict optimal load
                predicted_load = self.models['load_predictor'].predict(features_scaled)[0]
                predictions[agent_id] = max(0.0, min(1.0, predicted_load))
            
            return predictions
            
        except Exception as e:
            self.logger.error(f"Error predicting optimal loads: {e}")
            return {agent_id: 0.5 for agent_id in loads.keys()}
    
    def _calculate_prediction_confidence(self, agent_id: str, training_data: List[Dict]) -> float:
        """Calculate confidence in ML prediction"""
        # Simple confidence calculation based on data availability
        agent_data = [record for record in training_data if record.get('agent_id') == agent_id]
        return min(1.0, len(agent_data) / 50)  # Higher confidence with more data
    
    def _apply_load_balancing(self, target_component: str, routing_plan: Dict) -> bool:
        """Apply load balancing optimization"""
        try:
            # Update routing rules based on optimization
            for agent_id, routing_config in routing_plan.items():
                # Create or update agent-specific routing rule
                rule_id = f"{target_component}_{agent_id}"
                
                rule = RoutingRule(
                    id=rule_id,
                    name=f"{target_component} - {agent_id} Routing",
                    rule_type="ml_based",
                    conditions={
                        "traffic_percentage": routing_config.get('traffic_percentage', 0),
                        "max_connections": routing_config.get('max_connections', 100)
                    },
                    target_agents=[agent_id],
                    priority=1,
                    weight=routing_config.get('traffic_percentage', 0) / 100.0
                )
                
                self.routing_rules[rule_id] = rule
            
            # Log optimization application
            self.logger.info(f"Applied load balancing to {target_component}: "
                           f"{len(routing_plan)} agents configured")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to apply load balancing to {target_component}: {e}")
            return False
    
    def _record_load_balancing_optimization(self, component_id: str, result: Dict, success: bool):
        """Record load balancing optimization"""
        record = {
            'timestamp': datetime.now(),
            'component_id': component_id,
            'strategy': result.get('strategy', 'unknown'),
            'routing_plan': result.get('routing_plan', {}),
            'expected_improvement': result.get('expected_improvement', 0.0),
            'load_balance_score': result.get('load_balance_score', 0.0),
            'success': success
        }
        
        # Add to component history
        self.load_history[f"{component_id}_optimization"].append(record)
        
        self.logger.info(f"Recorded load balancing optimization for {component_id}: "
                        f"{result.get('expected_improvement', 0):.1f}% improvement")
    
    def get_load_balancing_status(self) -> Dict:
        """Get current load balancing status"""
        active_agents = len(self.current_loads)
        active_rules = len([rule for rule in self.routing_rules.values() if rule.active])
        
        # Calculate load balance metrics
        if self.current_loads:
            loads = [load.current_load for load in self.current_loads.values()]
            avg_load = np.mean(loads)
            load_variance = np.var(loads)
            load_balance_score = max(0, 1.0 - load_variance / max(0.01, avg_load))
        else:
            avg_load = 0
            load_balance_score = 0
        
        # Get recent optimizations
        recent_cutoff = datetime.now() - timedelta(hours=24)
        recent_optimizations = []
        
        for history_key in self.load_history:
            if '_optimization' in history_key:
                for record in self.load_history[history_key]:
                    if record.get('timestamp', datetime.min) > recent_cutoff:
                        recent_optimizations.append(record)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "active_agents": active_agents,
            "active_routing_rules": active_rules,
            "average_load": round(avg_load, 3),
            "load_balance_score": round(load_balance_score, 3),
            "recent_optimizations": len(recent_optimizations),
            "load_distribution": {
                agent_id: round(load.current_load, 3)
                for agent_id, load in self.current_loads.items()
            },
            "routing_strategies": list(self.strategies.keys())
        }
    
    def export_load_balancing_results(self, output_path: str):
        """Export load balancing results"""
        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "status": self.get_load_balancing_status(),
            "current_loads": {aid: load.to_dict() for aid, load in self.current_loads.items()},
            "routing_rules": {rid: rule.to_dict() for rid, rule in self.routing_rules.items()},
            "load_history": {
                key: [record for record in history]
                for key, history in self.load_history.items()
            }
        }
        
        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        self.logger.info(f"Load balancing results exported to {output_path}")
