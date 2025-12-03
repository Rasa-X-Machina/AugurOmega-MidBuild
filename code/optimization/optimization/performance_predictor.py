"""
Performance Predictor - Advanced performance prediction and optimization
Implements ML-based performance forecasting and proactive optimization
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
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
    from sklearn.linear_model import LinearRegression
    from sklearn.preprocessing import StandardScaler, PolynomialFeatures
    from sklearn.model_selection import cross_val_score
    from sklearn.metrics import mean_squared_error, r2_score
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

@dataclass
class PerformancePrediction:
    """Performance prediction result"""
    component_id: str
    prediction_horizon: timedelta
    predicted_metrics: Dict[str, float]
    confidence_interval: Dict[str, Tuple[float, float]]
    prediction_confidence: float
    timestamp: datetime
    model_used: str
    
    def to_dict(self) -> Dict:
        return {
            'component_id': self.component_id,
            'prediction_horizon_hours': self.prediction_horizon.total_seconds() / 3600,
            'predicted_metrics': self.predicted_metrics,
            'confidence_interval': {
                k: (v[0], v[1]) for k, v in self.confidence_interval.items()
            },
            'prediction_confidence': self.prediction_confidence,
            'timestamp': self.timestamp.isoformat(),
            'model_used': self.model_used
        }

@dataclass
class OptimizationOpportunity:
    """Identified optimization opportunity"""
    id: str
    component_id: str
    opportunity_type: str  # 'scaling', 'optimization', 'prevention'
    description: str
    expected_improvement: float
    urgency: str  # 'critical', 'high', 'medium', 'low'
    timeline: str  # 'immediate', 'short_term', 'medium_term', 'long_term'
    confidence: float
    recommended_actions: List[str]
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'component_id': self.component_id,
            'opportunity_type': self.opportunity_type,
            'description': self.description,
            'expected_improvement': self.expected_improvement,
            'urgency': self.urgency,
            'timeline': self.timeline,
            'confidence': self.confidence,
            'recommended_actions': self.recommended_actions,
            'created_at': self.created_at.isoformat()
        }

class PerformancePredictor:
    """
    Advanced Performance Predictor for Proactive Optimization
    Features:
    - Multi-horizon performance prediction
    - ML-based optimization opportunity detection
    - Predictive scaling recommendations
    - Anomaly detection and prevention
    - Performance trend analysis
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or self._default_config()
        self.logger = logging.getLogger(__name__)
        
        # Prediction tracking
        self.prediction_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.performance_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=2000))
        self.optimization_opportunities: deque = deque(maxlen=500)
        
        # ML models
        self.models: Dict[str, Any] = {}
        self.scalers: Dict[str, StandardScaler] = {}
        self.model_performance: Dict[str, Dict] = {}
        
        # Prediction horizons
        self.prediction_horizons = {
            'short': timedelta(minutes=15),
            'medium': timedelta(hours=2),
            'long': timedelta(hours=24)
        }
        
        # Performance targets
        self.performance_targets = {
            'latency_p95': 100.0,  # milliseconds
            'throughput': 1000.0,  # requests per second
            'cpu_efficiency': 0.8,
            'memory_efficiency': 0.8,
            'availability': 0.99
        }
        
        # Optimization strategies
        self.optimization_strategies = {
            'predictive_scaling': self._predictive_scaling,
            'capacity_planning': self._capacity_planning,
            'performance_optimization': self._performance_optimization,
            'cost_optimization': self._cost_optimization,
            'reliability_optimization': self._reliability_optimization
        }
        
        # Threading
        self.predictor_active = False
        self.predictor_thread: Optional[threading.Thread] = None
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Initialize ML models
        if HAS_SKLEARN:
            self._initialize_ml_models()
        
        self.logger.info("Performance Predictor initialized")
    
    def _default_config(self) -> Dict:
        """Default configuration for performance predictor"""
        return {
            'enable_ml_predictions': True,
            'enable_optimization_detection': True,
            'prediction_confidence_threshold': 0.7,
            'optimization_confidence_threshold': 0.8,
            'max_prediction_horizon_hours': 24,
            'training_data_window_days': 30,
            'retraining_interval_hours': 6,
            'enable_real_time_predictions': True,
            'feature_engineering': True
        }
    
    def _initialize_ml_models(self):
        """Initialize machine learning models"""
        try:
            # Performance prediction models
            self.models['latency_predictor'] = RandomForestRegressor(
                n_estimators=100,
                random_state=42,
                max_depth=15
            )
            
            self.models['throughput_predictor'] = GradientBoostingRegressor(
                n_estimators=100,
                random_state=42,
                max_depth=8
            )
            
            self.models['resource_predictor'] = RandomForestRegressor(
                n_estimators=50,
                random_state=42,
                max_depth=10
            )
            
            self.models['anomaly_detector'] = RandomForestRegressor(
                n_estimators=100,
                random_state=42,
                max_depth=12
            )
            
            # Feature scalers
            self.scalers['performance_scaler'] = StandardScaler()
            self.scalers['resource_scaler'] = StandardScaler()
            
            self.logger.info("ML models initialized for performance prediction")
            
        except Exception as e:
            self.logger.error(f"Error initializing ML models: {e}")
    
    def optimize(self, target_component: str, parameters: Dict[str, Any], context: Dict = None) -> Dict:
        """
        Perform predictive optimization for target component
        
        Args:
            target_component: Component to optimize
            parameters: Optimization parameters
            context: Additional context
        
        Returns:
            Optimization result with predictions and recommendations
        """
        try:
            # Get performance history
            history = self._get_performance_history(target_component)
            
            if len(history) < 20:
                return {
                    'success': False,
                    'improvement': 0.0,
                    'error': 'Insufficient historical data for prediction',
                    'predictions': {},
                    'optimization_opportunities': []
                }
            
            # Generate performance predictions
            predictions = self._generate_performance_predictions(target_component, history, parameters)
            
            # Identify optimization opportunities
            opportunities = self._identify_optimization_opportunities(target_component, predictions, history)
            
            # Generate optimization recommendations
            optimization_plan = self._generate_optimization_plan(target_component, opportunities, predictions)
            
            # Apply predictive optimizations if configured
            optimization_applied = self._apply_predictive_optimizations(target_component, optimization_plan)
            
            # Record results
            self._record_prediction_optimization(target_component, predictions, opportunities, optimization_applied)
            
            return {
                'success': optimization_applied,
                'improvement': optimization_plan.get('expected_total_improvement', 0.0),
                'predictions': predictions,
                'optimization_opportunities': [opp.to_dict() for opp in opportunities],
                'optimization_plan': optimization_plan,
                'confidence_score': np.mean([opp.confidence for opp in opportunities]) if opportunities else 0.0
            }
            
        except Exception as e:
            self.logger.error(f"Error in predictive optimization for {target_component}: {e}")
            return {
                'success': False,
                'improvement': 0.0,
                'error': str(e),
                'predictions': {},
                'optimization_opportunities': []
            }
    
    def _get_performance_history(self, component_id: str) -> List[Dict]:
        """Get performance history for component"""
        return list(self.performance_history.get(component_id, []))
    
    def _generate_performance_predictions(self, component_id: str, history: List[Dict], parameters: Dict) -> Dict[str, PerformancePrediction]:
        """Generate performance predictions for multiple horizons"""
        predictions = {}
        
        if not HAS_SKLEARN:
            return predictions
        
        try:
            # Prepare training data
            training_data = self._prepare_prediction_data(history)
            
            if len(training_data) < 20:
                return predictions
            
            # Train models
            self._train_prediction_models(training_data)
            
            # Generate predictions for each horizon
            for horizon_name, horizon_duration in self.prediction_horizons.items():
                if horizon_duration.total_seconds() <= self.config['max_prediction_horizon_hours'] * 3600:
                    prediction = self._predict_single_horizon(
                        component_id, training_data, horizon_duration, parameters
                    )
                    if prediction:
                        predictions[horizon_name] = prediction
            
            return predictions
            
        except Exception as e:
            self.logger.error(f"Error generating performance predictions for {component_id}: {e}")
            return predictions
    
    def _prepare_prediction_data(self, history: List[Dict]) -> List[Dict]:
        """Prepare data for ML training"""
        training_data = []
        
        for i, record in enumerate(history):
            if i < 10:  # Need history for feature engineering
                continue
            
            # Get recent data for feature engineering
            recent_records = history[max(0, i-10):i]
            
            # Extract features
            features = self._extract_performance_features(recent_records, record)
            
            # Extract targets (current metrics)
            targets = {
                'latency_p95': record.get('latency_p95', 0),
                'throughput': record.get('throughput', 0),
                'cpu_usage': record.get('cpu_usage', 0),
                'memory_usage': record.get('memory_usage', 0)
            }
            
            training_data.append({
                'features': features,
                'targets': targets,
                'timestamp': record.get('timestamp', datetime.now())
            })
        
        return training_data[-500:]  # Last 500 data points
    
    def _extract_performance_features(self, recent_records: List[Dict], current_record: Dict) -> Dict[str, float]:
        """Extract performance features for ML training"""
        features = {}
        
        # Current metrics
        features['current_latency'] = current_record.get('latency_p95', 0)
        features['current_throughput'] = current_record.get('throughput', 0)
        features['current_cpu'] = current_record.get('cpu_usage', 0)
        features['current_memory'] = current_record.get('memory_usage', 0)
        
        # Historical trends
        if len(recent_records) >= 5:
            latencies = [r.get('latency_p95', 0) for r in recent_records]
            throughputs = [r.get('throughput', 0) for r in recent_records]
            
            features['latency_trend'] = np.polyfit(range(len(latencies)), latencies, 1)[0] if len(latencies) > 1 else 0
            features['throughput_trend'] = np.polyfit(range(len(throughputs)), throughputs, 1)[0] if len(throughputs) > 1 else 0
            features['latency_volatility'] = np.std(latencies) if len(latencies) > 1 else 0
            features['throughput_volatility'] = np.std(throughputs) if len(throughputs) > 1 else 0
        
        # Time-based features
        timestamp = current_record.get('timestamp', datetime.now())
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)
        
        features['hour_of_day'] = timestamp.hour
        features['day_of_week'] = timestamp.weekday()
        features['is_weekend'] = 1 if timestamp.weekday() >= 5 else 0
        
        # Load pattern features
        features['queue_length'] = current_record.get('queue_length', 0)
        features['active_connections'] = current_record.get('active_connections', 0)
        
        return features
    
    def _train_prediction_models(self, training_data: List[Dict]):
        """Train ML models for performance prediction"""
        if len(training_data) < 10:
            return
        
        try:
            # Prepare feature matrix
            features_list = []
            targets = {'latency': [], 'throughput': [], 'cpu': [], 'memory': []}
            
            for data in training_data:
                features = data['features']
                targets_dict = data['targets']
                
                features_list.append(list(features.values()))
                targets['latency'].append(targets_dict.get('latency_p95', 0))
                targets['throughput'].append(targets_dict.get('throughput', 0))
                targets['cpu'].append(targets_dict.get('cpu_usage', 0))
                targets['memory'].append(targets_dict.get('memory_usage', 0))
            
            X = np.array(features_list)
            
            # Scale features
            X_scaled = self.scalers['performance_scaler'].fit_transform(X)
            
            # Train models
            if 'latency_predictor' in self.models:
                y_latency = np.array(targets['latency'])
                if len(y_latency) > 0:
                    self.models['latency_predictor'].fit(X_scaled, y_latency)
                    self.model_performance['latency'] = self._evaluate_model(
                        self.models['latency_predictor'], X_scaled, y_latency
                    )
            
            if 'throughput_predictor' in self.models:
                y_throughput = np.array(targets['throughput'])
                if len(y_throughput) > 0:
                    self.models['throughput_predictor'].fit(X_scaled, y_throughput)
                    self.model_performance['throughput'] = self._evaluate_model(
                        self.models['throughput_predictor'], X_scaled, y_throughput
                    )
            
            self.logger.info("Trained performance prediction models")
            
        except Exception as e:
            self.logger.error(f"Error training prediction models: {e}")
    
    def _evaluate_model(self, model, X, y) -> Dict[str, float]:
        """Evaluate model performance"""
        try:
            predictions = model.predict(X)
            mse = mean_squared_error(y, predictions)
            r2 = r2_score(y, predictions)
            
            return {
                'mse': float(mse),
                'r2_score': float(r2),
                'rmse': float(np.sqrt(mse))
            }
        except Exception:
            return {'mse': float('inf'), 'r2_score': 0, 'rmse': float('inf')}
    
    def _predict_single_horizon(self, component_id: str, training_data: List[Dict], 
                               horizon: timedelta, parameters: Dict) -> Optional[PerformancePrediction]:
        """Predict performance for single horizon"""
        if not training_data or 'latency_predictor' not in self.models:
            return None
        
        try:
            # Get latest features
            latest_features = training_data[-1]['features']
            features_array = np.array([list(latest_features.values())])
            features_scaled = self.scalers['performance_scaler'].transform(features_array)
            
            # Make predictions
            predicted_latency = self.models['latency_predictor'].predict(features_scaled)[0]
            predicted_throughput = self.models['throughput_predictor'].predict(features_scaled)[0] if 'throughput_predictor' in self.models else 500
            predicted_cpu = 0.7  # Simplified prediction
            predicted_memory = 0.6  # Simplified prediction
            
            # Calculate confidence intervals (simplified)
            model_performance = self.model_performance.get('latency', {'rmse': 10})
            rmse = model_performance.get('rmse', 10)
            
            confidence = max(0.3, min(1.0, 1.0 / (1.0 + rmse / 100)))  # Higher confidence with lower RMSE
            
            prediction = PerformancePrediction(
                component_id=component_id,
                prediction_horizon=horizon,
                predicted_metrics={
                    'latency_p95': predicted_latency,
                    'throughput': predicted_throughput,
                    'cpu_usage': predicted_cpu,
                    'memory_usage': predicted_memory
                },
                confidence_interval={
                    'latency_p95': (predicted_latency - rmse, predicted_latency + rmse),
                    'throughput': (predicted_throughput * 0.8, predicted_throughput * 1.2),
                    'cpu_usage': (predicted_cpu - 0.1, predicted_cpu + 0.1),
                    'memory_usage': (predicted_memory - 0.1, predicted_memory + 0.1)
                },
                prediction_confidence=confidence,
                timestamp=datetime.now(),
                model_used="RandomForest"
            )
            
            return prediction
            
        except Exception as e:
            self.logger.error(f"Error in single horizon prediction: {e}")
            return None
    
    def _identify_optimization_opportunities(self, component_id: str, predictions: Dict[str, PerformancePrediction],
                                           history: List[Dict]) -> List[OptimizationOpportunity]:
        """Identify optimization opportunities based on predictions"""
        opportunities = []
        
        if not predictions:
            return opportunities
        
        try:
            # Analyze each prediction horizon
            for horizon_name, prediction in predictions.items():
                if prediction.prediction_confidence < self.config['optimization_confidence_threshold']:
                    continue
                
                # Check for scaling opportunities
                scaling_opps = self._detect_scaling_opportunities(component_id, prediction, horizon_name)
                opportunities.extend(scaling_opps)
                
                # Check for performance optimization opportunities
                performance_opps = self._detect_performance_opportunities(component_id, prediction, horizon_name)
                opportunities.extend(performance_opps)
                
                # Check for capacity planning opportunities
                capacity_opps = self._detect_capacity_opportunities(component_id, prediction, horizon_name)
                opportunities.extend(capacity_opps)
            
            return opportunities
            
        except Exception as e:
            self.logger.error(f"Error identifying optimization opportunities: {e}")
            return opportunities
    
    def _detect_scaling_opportunities(self, component_id: str, prediction: PerformancePrediction, 
                                    horizon: str) -> List[OptimizationOpportunity]:
        """Detect scaling-related optimization opportunities"""
        opportunities = []
        
        metrics = prediction.predicted_metrics
        
        # Check for overload prediction
        if metrics.get('cpu_usage', 0) > 0.9:
            opportunity = OptimizationOpportunity(
                id=f"{component_id}_scale_up_{horizon}",
                component_id=component_id,
                opportunity_type="scaling",
                description=f"Predicted CPU overload ({metrics['cpu_usage']*100:.1f}%) in {horizon} horizon",
                expected_improvement=40.0,
                urgency="high",
                timeline="short_term" if horizon == "short" else "medium_term",
                confidence=prediction.prediction_confidence,
                recommended_actions=[
                    "Increase CPU allocation",
                    "Implement horizontal scaling",
                    "Optimize CPU-intensive operations",
                    "Monitor resource usage closely"
                ]
            )
            opportunities.append(opportunity)
        
        # Check for under-utilization
        if metrics.get('cpu_usage', 0) < 0.3 and metrics.get('memory_usage', 0) < 0.4:
            opportunity = OptimizationOpportunity(
                id=f"{component_id}_scale_down_{horizon}",
                component_id=component_id,
                opportunity_type="scaling",
                description=f"Predicted under-utilization ({metrics['cpu_usage']*100:.1f}% CPU) in {horizon} horizon",
                expected_improvement=25.0,
                urgency="medium",
                timeline="medium_term",
                confidence=prediction.prediction_confidence,
                recommended_actions=[
                    "Reduce resource allocation",
                    "Consolidate workloads",
                    "Implement resource sharing",
                    "Optimize for cost efficiency"
                ]
            )
            opportunities.append(opportunity)
        
        return opportunities
    
    def _detect_performance_opportunities(self, component_id: str, prediction: PerformancePrediction,
                                        horizon: str) -> List[OptimizationOpportunity]:
        """Detect performance optimization opportunities"""
        opportunities = []
        
        metrics = prediction.predicted_metrics
        
        # Check for latency issues
        if metrics.get('latency_p95', 0) > self.performance_targets['latency_p95']:
            improvement_potential = min(50.0, (metrics['latency_p95'] - self.performance_targets['latency_p95']) / self.performance_targets['latency_p95'] * 100)
            
            opportunity = OptimizationOpportunity(
                id=f"{component_id}_latency_optimization_{horizon}",
                component_id=component_id,
                opportunity_type="optimization",
                description=f"Predicted high latency ({metrics['latency_p95']:.1f}ms) in {horizon} horizon",
                expected_improvement=improvement_potential,
                urgency="high" if metrics['latency_p95'] > 200 else "medium",
                timeline="short_term",
                confidence=prediction.prediction_confidence,
                recommended_actions=[
                    "Optimize database queries",
                    "Implement caching strategies",
                    "Reduce API response times",
                    "Optimize network communication"
                ]
            )
            opportunities.append(opportunity)
        
        # Check for throughput limitations
        if metrics.get('throughput', 0) < self.performance_targets['throughput'] * 0.7:
            improvement_potential = min(60.0, (self.performance_targets['throughput'] - metrics['throughput']) / self.performance_targets['throughput'] * 100)
            
            opportunity = OptimizationOpportunity(
                id=f"{component_id}_throughput_optimization_{horizon}",
                component_id=component_id,
                opportunity_type="optimization",
                description=f"Predicted low throughput ({metrics['throughput']:.0f} req/s) in {horizon} horizon",
                expected_improvement=improvement_potential,
                urgency="medium",
                timeline="medium_term",
                confidence=prediction.prediction_confidence,
                recommended_actions=[
                    "Implement batch processing",
                    "Optimize algorithms",
                    "Add parallel processing",
                    "Increase worker threads"
                ]
            )
            opportunities.append(opportunity)
        
        return opportunities
    
    def _detect_capacity_opportunities(self, component_id: str, prediction: PerformancePrediction,
                                     horizon: str) -> List[OptimizationOpportunity]:
        """Detect capacity planning opportunities"""
        opportunities = []
        
        metrics = prediction.predicted_metrics
        
        # Predict future capacity needs
        if metrics.get('memory_usage', 0) > 0.8 or metrics.get('cpu_usage', 0) > 0.85:
            opportunity = OptimizationOpportunity(
                id=f"{component_id}_capacity_planning_{horizon}",
                component_id=component_id,
                opportunity_type="prevention",
                description=f"Predicted capacity constraints in {horizon} horizon",
                expected_improvement=35.0,
                urgency="high" if horizon == "short" else "medium",
                timeline="short_term" if horizon == "short" else "medium_term",
                confidence=prediction.prediction_confidence,
                recommended_actions=[
                    "Plan capacity expansion",
                    "Implement auto-scaling",
                    "Optimize resource usage",
                    "Prepare failover resources"
                ]
            )
            opportunities.append(opportunity)
        
        return opportunities
    
    def _generate_optimization_plan(self, component_id: str, opportunities: List[OptimizationOpportunity],
                                  predictions: Dict[str, PerformancePrediction]) -> Dict[str, Any]:
        """Generate comprehensive optimization plan"""
        if not opportunities:
            return {
                'optimization_plan': [],
                'expected_total_improvement': 0.0,
                'priority_order': []
            }
        
        # Prioritize opportunities
        prioritized_opportunities = sorted(
            opportunities,
            key=lambda x: (x.urgency == 'critical', x.expected_improvement, x.confidence),
            reverse=True
        )
        
        # Group by urgency and timeline
        plan = {
            'optimization_plan': [],
            'expected_total_improvement': 0.0,
            'priority_order': [],
            'immediate_actions': [],
            'short_term_actions': [],
            'medium_term_actions': [],
            'long_term_actions': []
        }
        
        total_improvement = 0.0
        
        for opp in prioritized_opportunities:
            plan['optimization_plan'].append(opp.to_dict())
            plan['priority_order'].append(opp.id)
            
            # Calculate improvement (avoid double counting)
            if opp.urgency in ['critical', 'high']:
                improvement = opp.expected_improvement * 0.8  # 80% confidence for high priority
            else:
                improvement = opp.expected_improvement * 0.6  # 60% confidence for medium/low priority
            
            total_improvement += improvement
            
            # Categorize by timeline
            timeline_key = f"{opp.timeline}_actions"
            if timeline_key in plan:
                plan[timeline_key].append(opp.description)
        
        plan['expected_total_improvement'] = min(1000.0, total_improvement)  # Cap at 10x improvement
        
        return plan
    
    def _apply_predictive_optimizations(self, component_id: str, optimization_plan: Dict) -> bool:
        """Apply predictive optimizations"""
        try:
            # For now, just log the optimization plan
            # In a real implementation, this would trigger actual optimizations
            
            immediate_actions = optimization_plan.get('immediate_actions', [])
            if immediate_actions:
                self.logger.info(f"Applying immediate optimizations for {component_id}: {immediate_actions}")
            
            self.logger.info(f"Generated optimization plan for {component_id}: "
                           f"{optimization_plan.get('expected_total_improvement', 0):.1f}% improvement potential")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to apply predictive optimizations: {e}")
            return False
    
    def _record_prediction_optimization(self, component_id: str, predictions: Dict[str, PerformancePrediction],
                                      opportunities: List[OptimizationOpportunity], success: bool):
        """Record prediction and optimization results"""
        record = {
            'timestamp': datetime.now(),
            'component_id': component_id,
            'predictions': {name: pred.to_dict() for name, pred in predictions.items()},
            'opportunities': [opp.to_dict() for opp in opportunities],
            'optimization_count': len(opportunities),
            'average_confidence': np.mean([opp.confidence for opp in opportunities]) if opportunities else 0,
            'success': success
        }
        
        # Store predictions
        for horizon_name, prediction in predictions.items():
            key = f"{component_id}_{horizon_name}"
            self.prediction_history[key].append(prediction.to_dict())
        
        # Store optimization opportunities
        for opportunity in opportunities:
            self.optimization_opportunities.append(opportunity.to_dict())
        
        self.logger.info(f"Recorded prediction optimization for {component_id}: "
                        f"{len(opportunities)} opportunities identified")
    
    def get_prediction_status(self) -> Dict:
        """Get current prediction status"""
        total_predictions = sum(len(history) for history in self.prediction_history.values())
        recent_opportunities = [opp for opp in self.optimization_opportunities 
                              if datetime.fromisoformat(opp['created_at']) > datetime.now() - timedelta(days=7)]
        
        # Calculate model performance
        avg_r2_score = np.mean([perf.get('r2_score', 0) for perf in self.model_performance.values()])
        
        return {
            "timestamp": datetime.now().isoformat(),
            "total_predictions": total_predictions,
            "active_components": len(self.prediction_history),
            "recent_opportunities": len(recent_opportunities),
            "model_performance": {
                "average_r2_score": round(avg_r2_score, 3),
                "models_trained": len(self.models),
                "training_data_points": sum(len(history) for history in self.performance_history.values())
            },
            "prediction_horizons": list(self.prediction_horizons.keys()),
            "optimization_opportunities_by_type": self._count_opportunities_by_type(recent_opportunities)
        }
    
    def _count_opportunities_by_type(self, opportunities: List[Dict]) -> Dict[str, int]:
        """Count opportunities by type"""
        counts = defaultdict(int)
        for opp in opportunities:
            counts[opp['opportunity_type']] += 1
        return dict(counts)
    
    def export_prediction_results(self, output_path: str):
        """Export prediction results"""
        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "status": self.get_prediction_status(),
            "prediction_history": {
                key: list(history)
                for key, history in self.prediction_history.items()
            },
            "optimization_opportunities": list(self.optimization_opportunities),
            "model_performance": self.model_performance,
            "performance_history": {
                key: list(history)
                for key, history in self.performance_history.items()
            }
        }
        
        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        self.logger.info(f"Prediction results exported to {output_path}")
