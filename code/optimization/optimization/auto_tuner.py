"""
Auto-Tuner - Intelligent parameter tuning for optimal performance
Implements machine learning-based auto-tuning for distributed systems
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import json
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import threading

# Import for ML capabilities (with fallback)
try:
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.model_selection import GridSearchCV
    from sklearn.preprocessing import StandardScaler
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False
    logging.warning("Scikit-learn not available. Auto-tuner will use heuristic methods.")

@dataclass
class TuningParameter:
    """Individual tuning parameter"""
    name: str
    current_value: Any
    optimal_value: Any
    range_min: Any
    range_max: Any
    parameter_type: str  # 'int', 'float', 'bool', 'choice'
    tuning_priority: str  # 'critical', 'high', 'medium', 'low'
    
    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'current_value': self.current_value,
            'optimal_value': self.optimal_value,
            'range_min': self.range_min,
            'range_max': self.range_max,
            'parameter_type': self.parameter_type,
            'tuning_priority': self.tuning_priority
        }

class AutoTuner:
    """
    Intelligent Auto-Tuner for Performance Optimization
    Features:
    - Machine learning-based parameter optimization
    - Multi-objective optimization
    - Adaptive learning from performance feedback
    - Risk-aware tuning decisions
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or self._default_config()
        self.logger = logging.getLogger(__name__)
        
        # Tuning parameters
        self.tuning_parameters: Dict[str, TuningParameter] = {}
        self.performance_history: List[Dict] = []
        self.tuning_results: Dict[str, Dict] = {}
        
        # ML models (if available)
        self.models: Dict[str, Any] = {}
        self.scalers: Dict[str, Any] = {}
        
        # Tuning strategies
        self.strategies = {
            'grid_search': self._grid_search_tuning,
            'bayesian': self._bayesian_tuning,
            'genetic': self._genetic_tuning,
            'heuristic': self._heuristic_tuning,
            'ml_guided': self._ml_guided_tuning
        }
        
        # Performance targets
        self.targets = {
            'latency': 50.0,  # milliseconds
            'throughput': 1000.0,  # ops/sec
            'cpu_efficiency': 0.8,
            'memory_efficiency': 0.8
        }
        
        # Threading
        self.tuning_active = False
        self.tuner_thread: Optional[threading.Thread] = None
        self.executor = ThreadPoolExecutor(max_workers=3)
        
        # Initialize ML models
        if HAS_SKLEARN:
            self._initialize_ml_models()
        
        self.logger.info("Auto-Tuner initialized")
    
    def _default_config(self) -> Dict:
        """Default configuration for auto-tuner"""
        return {
            'tuning_strategy': 'ml_guided' if HAS_SKLEARN else 'heuristic',
            'optimization_target': 'balanced',  # 'latency', 'throughput', 'balanced'
            'max_iterations': 50,
            'convergence_threshold': 0.02,
            'risk_tolerance': 0.1,
            'enable_adaptive_learning': True,
            'parameter_constraints': {
                'max_cpu_allocation': 0.9,
                'max_memory_allocation': 0.9,
                'min_thread_count': 1,
                'max_thread_count': 100
            }
        }
    
    def _initialize_ml_models(self):
        """Initialize machine learning models"""
        try:
            # Performance prediction model
            self.models['performance_predictor'] = RandomForestRegressor(
                n_estimators=100,
                random_state=42,
                max_depth=10
            )
            
            # Parameter optimization model
            self.models['parameter_optimizer'] = RandomForestRegressor(
                n_estimators=50,
                random_state=42
            )
            
            # Scaling model
            self.scalers['feature_scaler'] = StandardScaler()
            
            self.logger.info("ML models initialized for auto-tuning")
            
        except Exception as e:
            self.logger.error(f"Error initializing ML models: {e}")
    
    def register_tuning_parameter(self, param: TuningParameter):
        """Register a parameter for tuning"""
        self.tuning_parameters[param.name] = param
        self.logger.info(f"Registered tuning parameter: {param.name}")
    
    def optimize(self, target_component: str, parameters: Dict[str, Any], context: Dict = None) -> Dict:
        """
        Perform optimization on target component
        
        Args:
            target_component: Component to optimize
            parameters: Optimization parameters
            context: Additional context for optimization
        
        Returns:
            Optimization result dictionary
        """
        try:
            strategy = self.config.get('tuning_strategy', 'heuristic')
            
            if strategy not in self.strategies:
                strategy = 'heuristic'
                self.logger.warning(f"Unknown tuning strategy {strategy}, falling back to heuristic")
            
            # Execute tuning strategy
            result = self.strategies[strategy](target_component, parameters, context)
            
            # Apply optimization
            optimization_applied = self._apply_optimization(target_component, result['optimal_parameters'])
            
            # Record result
            self._record_tuning_result(target_component, result, optimization_applied)
            
            return {
                'success': optimization_applied,
                'improvement': result.get('expected_improvement', 0.0),
                'optimal_parameters': result.get('optimal_parameters', {}),
                'optimization_details': result
            }
            
        except Exception as e:
            self.logger.error(f"Error in auto-tuning for {target_component}: {e}")
            return {
                'success': False,
                'improvement': 0.0,
                'error': str(e),
                'optimal_parameters': {}
            }
    
    def _grid_search_tuning(self, target_component: str, parameters: Dict, context: Dict) -> Dict:
        """Grid search optimization"""
        # Define parameter grid
        param_grid = self._build_parameter_grid(target_component, parameters)
        
        best_score = float('-inf')
        best_params = {}
        
        # Evaluate parameter combinations
        for param_combination in self._generate_combinations(param_grid):
            score = self._evaluate_parameter_combination(target_component, param_combination)
            
            if score > best_score:
                best_score = score
                best_params = param_combination
        
        expected_improvement = self._estimate_improvement(best_params, best_score)
        
        return {
            'strategy': 'grid_search',
            'best_score': best_score,
            'optimal_parameters': best_params,
            'expected_improvement': expected_improvement,
            'iterations_evaluated': len(list(self._generate_combinations(param_grid)))
        }
    
    def _bayesian_tuning(self, target_component: str, parameters: Dict, context: Dict) -> Dict:
        """Bayesian optimization (simplified implementation)"""
        # Simplified Bayesian approach using acquisition functions
        max_iterations = self.config['max_iterations']
        
        # Initialize with random samples
        best_score = float('-inf')
        best_params = {}
        evaluated_params = []
        scores = []
        
        for iteration in range(max_iterations):
            # Generate candidate parameters
            if iteration < len(evaluated_params):
                # Use evaluated parameters
                candidate_params = evaluated_params[iteration % len(evaluated_params)]
            else:
                # Generate new candidate using Bayesian approach
                candidate_params = self._generate_bayesian_candidate(target_component, evaluated_params, scores)
            
            # Evaluate candidate
            score = self._evaluate_parameter_combination(target_component, candidate_params)
            
            # Update best
            if score > best_score:
                best_score = score
                best_params = candidate_params
            
            # Store evaluation
            evaluated_params.append(candidate_params)
            scores.append(score)
        
        expected_improvement = self._estimate_improvement(best_params, best_score)
        
        return {
            'strategy': 'bayesian',
            'best_score': best_score,
            'optimal_parameters': best_params,
            'expected_improvement': expected_improvement,
            'iterations_evaluated': max_iterations
        }
    
    def _genetic_tuning(self, target_component: str, parameters: Dict, context: Dict) -> Dict:
        """Genetic algorithm optimization"""
        population_size = 20
        generations = 10
        mutation_rate = 0.1
        crossover_rate = 0.8
        
        # Initialize population
        population = self._initialize_population(target_component, parameters, population_size)
        
        best_fitness = float('-inf')
        best_individual = None
        
        for generation in range(generations):
            # Evaluate fitness
            fitness_scores = []
            for individual in population:
                score = self._evaluate_fitness(target_component, individual)
                fitness_scores.append(score)
                
                if score > best_fitness:
                    best_fitness = score
                    best_individual = individual.copy()
            
            # Selection, crossover, mutation
            population = self._evolve_population(population, fitness_scores, mutation_rate, crossover_rate)
        
        expected_improvement = self._estimate_improvement(best_individual, best_fitness)
        
        return {
            'strategy': 'genetic',
            'best_fitness': best_fitness,
            'optimal_parameters': best_individual,
            'expected_improvement': expected_improvement,
            'generations': generations,
            'population_size': population_size
        }
    
    def _heuristic_tuning(self, target_component: str, parameters: Dict, context: Dict) -> Dict:
        """Heuristic-based tuning using domain knowledge"""
        optimal_params = {}
        total_improvement = 0.0
        
        # Get current metrics (would come from monitoring system)
        current_metrics = parameters.get('current_metrics', {})
        
        # CPU optimization
        if current_metrics.get('cpu_usage', 0) > 80:
            optimal_params['thread_pool_size'] = min(
                current_metrics.get('cpu_cores', 4) * 2,
                self.config['parameter_constraints']['max_thread_count']
            )
            optimal_params['batch_size'] = min(
                current_metrics.get('queue_length', 100) // 4,
                1000
            )
            total_improvement += 25.0
        
        # Memory optimization
        if current_metrics.get('memory_usage', 0) > 80:
            optimal_params['memory_pool_size'] = min(
                current_metrics.get('available_memory', 8) * 0.7,
                16
            )
            optimal_params['gc_threshold'] = 'adaptive'
            total_improvement += 20.0
        
        # Latency optimization
        if current_metrics.get('latency_p95', 0) > 100:
            optimal_params['connection_pool_size'] = min(
                current_metrics.get('expected_concurrent_users', 100),
                500
            )
            optimal_params['timeout_settings'] = 'aggressive'
            total_improvement += 30.0
        
        # Throughput optimization
        if current_metrics.get('throughput', 0) < 500:
            optimal_params['async_processing'] = True
            optimal_params['parallel_workers'] = min(
                current_metrics.get('cpu_cores', 4),
                8
            )
            total_improvement += 35.0
        
        # Set defaults for unspecified parameters
        for param_name, param in self.tuning_parameters.items():
            if param_name not in optimal_params:
                if param.parameter_type == 'int':
                    optimal_params[param_name] = int((param.range_max + param.range_min) / 2)
                elif param.parameter_type == 'float':
                    optimal_params[param_name] = (param.range_max + param.range_min) / 2
                elif param.parameter_type == 'bool':
                    optimal_params[param_name] = param.current_value
        
        return {
            'strategy': 'heuristic',
            'optimal_parameters': optimal_params,
            'expected_improvement': total_improvement,
            'applied_rules': ['cpu_optimization', 'memory_optimization', 'latency_optimization', 'throughput_optimization']
        }
    
    def _ml_guided_tuning(self, target_component: str, parameters: Dict, context: Dict) -> Dict:
        """ML-guided optimization using trained models"""
        if not HAS_SKLEARN or 'performance_predictor' not in self.models:
            return self._heuristic_tuning(target_component, parameters, context)
        
        try:
            # Get training data
            training_data = self._get_training_data(target_component)
            
            if len(training_data) < 10:
                # Not enough data for ML, fallback to heuristic
                return self._heuristic_tuning(target_component, parameters, context)
            
            # Prepare features and targets
            X = []
            y = []
            param_names = set()
            
            for data_point in training_data:
                features = []
                param_values = []
                
                for param_name, param_data in data_point['parameters'].items():
                    param_names.add(param_name)
                    features.extend([param_data.get('value', 0)])
                
                # Add performance metrics as features
                metrics = data_point['performance_metrics']
                features.extend([
                    metrics.get('cpu_usage', 0),
                    metrics.get('memory_usage', 0),
                    metrics.get('latency_p95', 0),
                    metrics.get('throughput', 0)
                ])
                
                X.append(features)
                y.append(data_point['overall_score'])
            
            # Train model
            X = np.array(X)
            y = np.array(y)
            
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            self.models['performance_predictor'].fit(X_scaled, y)
            
            # Optimize using trained model
            optimal_params, best_score = self._ml_optimize_parameters(target_component, param_names, scaler)
            
            expected_improvement = self._estimate_improvement(optimal_params, best_score)
            
            return {
                'strategy': 'ml_guided',
                'optimal_parameters': optimal_params,
                'expected_improvement': expected_improvement,
                'model_confidence': self._calculate_model_confidence(training_data),
                'training_samples': len(training_data)
            }
            
        except Exception as e:
            self.logger.error(f"Error in ML-guided tuning: {e}")
            return self._heuristic_tuning(target_component, parameters, context)
    
    def _build_parameter_grid(self, target_component: str, parameters: Dict) -> Dict:
        """Build parameter grid for optimization"""
        grid = {}
        
        # Get available parameters for this component
        component_params = [p for p in self.tuning_parameters.values() 
                          if target_component in p.name or not target_component]
        
        for param in component_params:
            if param.parameter_type == 'int':
                grid[param.name] = list(range(int(param.range_min), int(param.range_max) + 1, 
                                           max(1, (int(param.range_max) - int(param.range_min)) // 10)))
            elif param.parameter_type == 'float':
                grid[param.name] = np.linspace(param.range_min, param.range_max, 10).tolist()
            elif param.parameter_type == 'bool':
                grid[param.name] = [True, False]
            elif param.parameter_type == 'choice':
                grid[param.name] = param.range_min  # Assuming range_min contains choices
        
        return grid
    
    def _generate_combinations(self, param_grid: Dict):
        """Generate all parameter combinations"""
        import itertools
        
        param_names = list(param_grid.keys())
        param_ranges = [param_grid[name] for name in param_names]
        
        for combination in itertools.product(*param_ranges):
            yield dict(zip(param_names, combination))
    
    def _evaluate_parameter_combination(self, target_component: str, params: Dict) -> float:
        """Evaluate performance score for parameter combination"""
        # Simulate performance evaluation
        # In real implementation, this would test the parameter combination
        
        # Base score
        score = 100.0
        
        # Apply parameter effects
        if 'thread_pool_size' in params:
            thread_pool = params['thread_pool_size']
            if 4 <= thread_pool <= 16:
                score += 20  # Optimal range
            elif thread_pool > 16:
                score -= (thread_pool - 16) * 2  # Overhead penalty
        
        if 'batch_size' in params:
            batch_size = params['batch_size']
            if 10 <= batch_size <= 100:
                score += 15  # Optimal range
            elif batch_size > 100:
                score -= (batch_size - 100) * 0.1  # Memory pressure
        
        if 'memory_pool_size' in params:
            memory_pool = params['memory_pool_size']
            if 4 <= memory_pool <= 12:
                score += 10  # Optimal range
        
        return max(0.0, score)
    
    def _estimate_improvement(self, parameters: Dict, performance_score: float) -> float:
        """Estimate expected improvement percentage"""
        # Convert performance score to improvement percentage
        # Assuming baseline score of 100
        base_score = 100.0
        improvement = ((performance_score - base_score) / base_score) * 100
        
        return max(0.0, improvement)
    
    def _generate_bayesian_candidate(self, target_component: str, evaluated: List[Dict], scores: List[float]) -> Dict:
        """Generate candidate parameters using Bayesian approach"""
        if not evaluated:
            # First candidate - use current optimal values
            candidate = {}
            for param in self.tuning_parameters.values():
                if param.parameter_type == 'int':
                    candidate[param.name] = int((param.range_max + param.range_min) / 2)
                elif param.parameter_type == 'float':
                    candidate[param.name] = (param.range_max + param.range_min) / 2
                elif param.parameter_type == 'bool':
                    candidate[param.name] = param.current_value
            return candidate
        
        # Use acquisition function to generate candidate
        # Simplified: combine best performing parameters with exploration
        best_idx = np.argmax(scores)
        best_params = evaluated[best_idx]
        
        candidate = {}
        for param_name, param in self.tuning_parameters.items():
            if param_name in best_params:
                # Add some exploration
                range_size = param.range_max - param.range_min
                exploration = np.random.normal(0, range_size * 0.1)
                value = best_params[param_name] + exploration
                
                # Clamp to valid range
                value = max(param.range_min, min(param.range_max, value))
                candidate[param_name] = value
            else:
                # Use random value within range
                candidate[param_name] = np.random.uniform(param.range_min, param.range_max)
        
        return candidate
    
    def _initialize_population(self, target_component: str, parameters: Dict, size: int) -> List[Dict]:
        """Initialize population for genetic algorithm"""
        population = []
        
        for _ in range(size):
            individual = {}
            for param in self.tuning_parameters.values():
                if param.parameter_type == 'int':
                    individual[param.name] = np.random.randint(int(param.range_min), int(param.range_max) + 1)
                elif param.parameter_type == 'float':
                    individual[param.name] = np.random.uniform(param.range_min, param.range_max)
                elif param.parameter_type == 'bool':
                    individual[param.name] = np.random.choice([True, False])
            population.append(individual)
        
        return population
    
    def _evaluate_fitness(self, target_component: str, individual: Dict) -> float:
        """Evaluate fitness of individual in genetic algorithm"""
        return self._evaluate_parameter_combination(target_component, individual)
    
    def _evolve_population(self, population: List[Dict], fitness_scores: List[float], 
                          mutation_rate: float, crossover_rate: float) -> List[Dict]:
        """Evolve population using genetic operators"""
        new_population = []
        
        # Keep best individuals (elitism)
        sorted_indices = np.argsort(fitness_scores)[::-1]
        elite_count = len(population) // 4
        
        for i in range(elite_count):
            new_population.append(population[sorted_indices[i]].copy())
        
        # Generate rest through crossover and mutation
        while len(new_population) < len(population):
            # Selection
            parent1 = self._tournament_selection(population, fitness_scores)
            parent2 = self._tournament_selection(population, fitness_scores)
            
            # Crossover
            if np.random.random() < crossover_rate:
                child1, child2 = self._crossover(parent1, parent2)
            else:
                child1, child2 = parent1.copy(), parent2.copy()
            
            # Mutation
            if np.random.random() < mutation_rate:
                child1 = self._mutate(child1)
            if np.random.random() < mutation_rate:
                child2 = self._mutate(child2)
            
            new_population.extend([child1, child2])
        
        return new_population[:len(population)]
    
    def _tournament_selection(self, population: List[Dict], fitness_scores: List[float]) -> Dict:
        """Tournament selection"""
        tournament_size = 3
        tournament_indices = np.random.choice(len(population), tournament_size, replace=False)
        tournament_fitness = [fitness_scores[i] for i in tournament_indices]
        winner_idx = tournament_indices[np.argmax(tournament_fitness)]
        return population[winner_idx].copy()
    
    def _crossover(self, parent1: Dict, parent2: Dict) -> Tuple[Dict, Dict]:
        """Single-point crossover"""
        child1, child2 = parent1.copy(), parent2.copy()
        
        # Simple uniform crossover
        for key in parent1.keys():
            if np.random.random() < 0.5:
                child1[key], child2[key] = parent2[key], parent1[key]
        
        return child1, child2
    
    def _mutate(self, individual: Dict) -> Dict:
        """Mutate individual"""
        mutated = individual.copy()
        
        for param_name, value in mutated.items():
            if param_name in self.tuning_parameters:
                param = self.tuning_parameters[param_name]
                if param.parameter_type in ['int', 'float']:
                    # Gaussian mutation
                    range_size = param.range_max - param.range_min
                    mutation_strength = range_size * 0.1
                    mutated_value = value + np.random.normal(0, mutation_strength)
                    mutated_value = max(param.range_min, min(param.range_max, mutated_value))
                    mutated[param_name] = mutated_value
                elif param.parameter_type == 'bool':
                    mutated[param_name] = not value
        
        return mutated
    
    def _get_training_data(self, target_component: str) -> List[Dict]:
        """Get training data for ML models"""
        # Filter training data for target component
        component_data = [data for data in self.performance_history 
                         if data.get('component') == target_component]
        return component_data[-100:]  # Last 100 data points
    
    def _ml_optimize_parameters(self, target_component: str, param_names: set, scaler) -> Tuple[Dict, float]:
        """Optimize parameters using trained ML model"""
        # Generate candidate parameters
        candidates = []
        for _ in range(50):  # Test 50 candidates
            candidate = {}
            for param_name in param_names:
                if param_name in self.tuning_parameters:
                    param = self.tuning_parameters[param_name]
                    if param.parameter_type == 'int':
                        candidate[param_name] = np.random.randint(int(param.range_min), int(param.range_max) + 1)
                    elif param.parameter_type == 'float':
                        candidate[param_name] = np.random.uniform(param.range_min, param.range_max)
                    elif param.parameter_type == 'bool':
                        candidate[param_name] = np.random.choice([True, False])
            candidates.append(candidate)
        
        # Evaluate candidates
        best_score = float('-inf')
        best_candidate = {}
        
        for candidate in candidates:
            # Create feature vector (simplified)
            features = [candidate.get(name, 0) for name in param_names]
            features.extend([0, 0, 0, 0])  # Default metrics
            
            # Predict performance
            features_scaled = scaler.transform([features])
            score = self.models['performance_predictor'].predict(features_scaled)[0]
            
            if score > best_score:
                best_score = score
                best_candidate = candidate
        
        return best_candidate, best_score
    
    def _calculate_model_confidence(self, training_data: List[Dict]) -> float:
        """Calculate confidence in ML model"""
        # Simple confidence calculation based on data amount and variance
        if len(training_data) < 10:
            return 0.2
        elif len(training_data) < 50:
            return 0.5
        else:
            return 0.8
    
    def _apply_optimization(self, target_component: str, optimal_params: Dict) -> bool:
        """Apply optimization parameters to target component"""
        try:
            # In a real implementation, this would apply parameters to the actual system
            # For now, just log the application
            self.logger.info(f"Applying optimization to {target_component}: {optimal_params}")
            
            # Simulate application success
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to apply optimization to {target_component}: {e}")
            return False
    
    def _record_tuning_result(self, target_component: str, result: Dict, success: bool):
        """Record tuning result for learning"""
        record = {
            'timestamp': datetime.now(),
            'component': target_component,
            'strategy': result.get('strategy', 'unknown'),
            'optimal_parameters': result.get('optimal_parameters', {}),
            'expected_improvement': result.get('expected_improvement', 0.0),
            'success': success,
            'context': result
        }
        
        self.performance_history.append(record)
        
        # Keep only recent history
        if len(self.performance_history) > 1000:
            self.performance_history = self.performance_history[-1000:]
        
        self.tuning_results[f"{target_component}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"] = result
        
        self.logger.info(f"Recorded tuning result for {target_component}: {result.get('expected_improvement', 0):.1f}% expected improvement")
    
    def get_tuning_status(self) -> Dict:
        """Get current tuning status"""
        recent_results = [r for r in self.performance_history 
                         if r['timestamp'] > datetime.now() - timedelta(hours=24)]
        
        successful_tuning = sum(1 for r in recent_results if r['success'])
        total_tuning = len(recent_results)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "tuning_parameters_registered": len(self.tuning_parameters),
            "tuning_history_entries": len(self.performance_history),
            "recent_tuning_sessions": total_tuning,
            "successful_optimizations": successful_tuning,
            "success_rate": successful_tuning / total_tuning if total_tuning > 0 else 0,
            "average_expected_improvement": np.mean([r['expected_improvement'] for r in recent_results]) if recent_results else 0
        }
    
    def export_tuning_results(self, output_path: str):
        """Export tuning results"""
        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "status": self.get_tuning_status(),
            "tuning_parameters": {name: param.to_dict() for name, param in self.tuning_parameters.items()},
            "performance_history": self.performance_history,
            "tuning_results": self.tuning_results
        }
        
        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        self.logger.info(f"Tuning results exported to {output_path}")
