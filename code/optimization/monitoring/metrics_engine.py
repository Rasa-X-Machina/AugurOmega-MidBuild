"""
Real-time Metrics Engine - Advanced metrics collection and processing
Supports 3000+ agents with real-time aggregation and analytics
"""

import asyncio
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any, Union
from dataclasses import dataclass, field
from collections import defaultdict, deque
import json
import threading
from concurrent.futures import ThreadPoolExecutor
import weakref
import numpy as np
from enum import Enum

class MetricType(Enum):
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"
    RATE = "rate"

@dataclass
class MetricData:
    """Individual metric data point"""
    name: str
    value: Union[int, float]
    metric_type: MetricType
    labels: Dict[str, str] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    agent_id: str = "system"
    
    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'value': self.value,
            'type': self.metric_type.value,
            'labels': self.labels,
            'timestamp': self.timestamp.isoformat(),
            'agent_id': self.agent_id
        }

class MetricsEngine:
    """
    High-performance metrics engine supporting 3000+ agents
    Features:
    - Real-time aggregation
    - Time-series storage
    - Predictive analytics
    - Scalable design
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or self._default_config()
        self.logger = logging.getLogger(__name__)
        
        # Core storage
        self.metrics_store: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self.aggregated_metrics: Dict[str, Dict] = {}
        
        # Real-time processing
        self.processors: List[Callable] = []
        self.alert_conditions: Dict[str, Callable] = {}
        
        # Aggregation windows
        self.aggregation_windows = {
            '1s': 1,
            '10s': 10,
            '1m': 60,
            '5m': 300,
            '15m': 900,
            '1h': 3600
        }
        
        # Threading
        self.processing_active = False
        self.processor_thread: Optional[threading.Thread] = None
        self.executor = ThreadPoolExecutor(max_workers=5)
        
        # Performance tracking
        self.metrics_processed = 0
        self.processing_latency_avg = 0.0
        self.start_time = datetime.now()
        
        self.logger.info("Metrics Engine initialized")
    
    def _default_config(self) -> Dict:
        """Default configuration for metrics engine"""
        return {
            'aggregation_interval': 10,  # seconds
            'retention_days': 7,
            'enable_predictive': True,
            'enable_anomaly_detection': True,
            'max_processors': 10,
            'batch_size': 100
        }
    
    async def start_engine(self):
        """Start the metrics processing engine"""
        if self.processing_active:
            self.logger.warning("Metrics engine already running")
            return
        
        self.processing_active = True
        
        # Start processing thread
        self.processor_thread = threading.Thread(target=self._processing_loop, daemon=True)
        self.processor_thread.start()
        
        self.logger.info("📊 Metrics Engine started")
    
    async def stop_engine(self):
        """Stop the metrics processing engine"""
        self.processing_active = False
        
        if self.processor_thread:
            self.processor_thread.join(timeout=5)
        
        self.executor.shutdown(wait=True)
        
        self.logger.info("Metrics Engine stopped")
    
    def record_metric(self, metric_data: MetricData):
        """Record a new metric data point"""
        # Store in time-series
        metric_key = self._create_metric_key(metric_data)
        self.metrics_store[metric_key].append(metric_data)
        
        # Trigger immediate processing if needed
        if self.processing_active:
            self.executor.submit(self._process_metric_immediate, metric_data)
        
        self.metrics_processed += 1
    
    def _create_metric_key(self, metric_data: MetricData) -> str:
        """Create unique key for metric storage"""
        labels_str = json.dumps(metric_data.labels, sort_keys=True)
        return f"{metric_data.name}:{labels_str}:{metric_data.agent_id}"
    
    def _process_metric_immediate(self, metric_data: MetricData):
        """Process metric immediately for real-time analytics"""
        try:
            # Run custom processors
            for processor in self.processors:
                try:
                    processor(metric_data)
                except Exception as e:
                    self.logger.error(f"Error in metric processor: {e}")
            
            # Update aggregated metrics
            self._update_aggregated_metrics(metric_data)
            
        except Exception as e:
            self.logger.error(f"Error processing metric {metric_data.name}: {e}")
    
    def _update_aggregated_metrics(self, metric_data: MetricData):
        """Update aggregated metrics"""
        agg_key = f"{metric_data.name}:{metric_data.agent_id}"
        
        if agg_key not in self.aggregated_metrics:
            self.aggregated_metrics[agg_key] = {
                'count': 0,
                'sum': 0.0,
                'min': float('inf'),
                'max': float('-inf'),
                'last_value': 0.0,
                'last_update': datetime.now()
            }
        
        agg = self.aggregated_metrics[agg_key]
        agg['count'] += 1
        agg['sum'] += metric_data.value
        agg['min'] = min(agg['min'], metric_data.value)
        agg['max'] = max(agg['max'], metric_data.value)
        agg['last_value'] = metric_data.value
        agg['last_update'] = datetime.now()
    
    def _processing_loop(self):
        """Main processing loop for aggregated metrics"""
        while self.processing_active:
            try:
                # Perform windowed aggregations
                for window_name, window_seconds in self.aggregation_windows.items():
                    self._perform_windowed_aggregation(window_seconds)
                
                # Anomaly detection
                if self.config.get('enable_anomaly_detection', False):
                    self._detect_anomalies()
                
                # Predictive analytics
                if self.config.get('enable_predictive', False):
                    self._run_predictive_analysis()
                
                time.sleep(self.config['aggregation_interval'])
                
            except Exception as e:
                self.logger.error(f"Error in processing loop: {e}")
                time.sleep(5)
    
    def _perform_windowed_aggregation(self, window_seconds: int):
        """Perform aggregation over time window"""
        cutoff_time = datetime.now() - timedelta(seconds=window_seconds)
        
        for metric_key, metrics_deque in self.metrics_store.items():
            # Filter metrics in window
            window_metrics = [
                m for m in metrics_deque 
                if m.timestamp > cutoff_time
            ]
            
            if len(window_metrics) > 0:
                # Calculate window statistics
                values = [m.value for m in window_metrics]
                avg = np.mean(values)
                std = np.std(values)
                p95 = np.percentile(values, 95)
                p99 = np.percentile(values, 99)
                
                # Store aggregated result
                agg_key = f"{metric_key}:w{window_seconds}s"
                self.aggregated_metrics[agg_key] = {
                    'window_seconds': window_seconds,
                    'count': len(window_metrics),
                    'avg': avg,
                    'std': std,
                    'min': min(values),
                    'max': max(values),
                    'p95': p95,
                    'p99': p99,
                    'window_start': cutoff_time.isoformat(),
                    'window_end': datetime.now().isoformat()
                }
    
    def _detect_anomalies(self):
        """Detect anomalies in metric patterns"""
        for metric_key, agg_data in self.aggregated_metrics.items():
            if 'window_seconds' not in agg_data:
                continue
            
            # Simple anomaly detection using standard deviations
            mean = agg_data['avg']
            std = agg_data['std']
            current = agg_data.get('last_value', mean)
            
            if std > 0:
                z_score = abs(current - mean) / std
                if z_score > 3.0:  # 3-sigma rule
                    anomaly = {
                        'metric_key': metric_key,
                        'current_value': current,
                        'expected_mean': mean,
                        'z_score': z_score,
                        'timestamp': datetime.now().isoformat(),
                        'severity': 'high' if z_score > 4.0 else 'medium'
                    }
                    
                    self.logger.warning(f"Anomaly detected: {json.dumps(anomaly, indent=2)}")
    
    def _run_predictive_analysis(self):
        """Run predictive analytics on metrics"""
        # Get recent metrics for trend analysis
        recent_cutoff = datetime.now() - timedelta(minutes=15)
        
        for metric_key, metrics_deque in self.metrics_store.items():
            recent_metrics = [
                m for m in metrics_deque 
                if m.timestamp > recent_cutoff
            ]
            
            if len(recent_metrics) >= 5:  # Need at least 5 points
                values = [m.value for m in recent_metrics]
                times = [m.timestamp.timestamp() for m in recent_metrics]
                
                # Simple linear trend prediction
                try:
                    trend_coef = np.polyfit(times, values, 1)[0]  # slope
                    
                    if abs(trend_coef) > 0.01:  # Significant trend
                        prediction = {
                            'metric_key': metric_key,
                            'trend_slope': trend_coef,
                            'trend_direction': 'increasing' if trend_coef > 0 else 'decreasing',
                            'confidence': min(0.9, len(recent_metrics) / 20),  # Confidence based on data points
                            'prediction_window': '5m',
                            'timestamp': datetime.now().isoformat()
                        }
                        
                        self.logger.info(f"Predictive trend: {json.dumps(prediction, indent=2)}")
                        
                except Exception as e:
                    self.logger.debug(f"Prediction error for {metric_key}: {e}")
    
    def add_processor(self, processor_func: Callable[[MetricData], None]):
        """Add custom metric processor"""
        self.processors.append(processor_func)
        self.logger.info(f"Added metric processor: {processor_func.__name__}")
    
    def get_aggregated_metrics(self, metric_name: str = None, time_window: str = None) -> Dict:
        """Get aggregated metrics"""
        result = {}
        
        for key, data in self.aggregated_metrics.items():
            # Filter by metric name
            if metric_name and not key.startswith(metric_name):
                continue
            
            # Filter by time window
            if time_window:
                window_key = f":w{self.aggregation_windows[time_window]}s"
                if window_key not in key:
                    continue
            
            result[key] = data
        
        return result
    
    def get_metric_history(self, metric_name: str, agent_id: str = None, limit: int = 100) -> List[Dict]:
        """Get historical metrics for analysis"""
        result = []
        
        for key, metrics_deque in self.metrics_store.items():
            # Check if this metric matches
            if metric_name in key:
                if agent_id and agent_id not in key:
                    continue
                
                # Get recent metrics
                recent_metrics = list(metrics_deque)[-limit:]
                for metric in recent_metrics:
                    result.append(metric.to_dict())
        
        return sorted(result, key=lambda x: x['timestamp'])
    
    def get_performance_stats(self) -> Dict:
        """Get performance statistics of the metrics engine"""
        uptime = datetime.now() - self.start_time
        
        return {
            'uptime_seconds': uptime.total_seconds(),
            'metrics_processed': self.metrics_processed,
            'processing_rate': self.metrics_processed / uptime.total_seconds() if uptime.total_seconds() > 0 else 0,
            'storage_size': {
                'total_metrics': sum(len(deque_obj) for deque_obj in self.metrics_store.values()),
                'unique_metrics': len(self.metrics_store),
                'aggregated_metrics': len(self.aggregated_metrics)
            },
            'performance': {
                'avg_processing_latency_ms': self.processing_latency_avg * 1000,
                'processor_count': len(self.processors)
            }
        }

# Convenience functions for common metrics
def record_counter(name: str, value: int = 1, labels: Dict = None, agent_id: str = "system"):
    """Record a counter metric"""
    return MetricData(
        name=name,
        value=value,
        metric_type=MetricType.COUNTER,
        labels=labels or {},
        agent_id=agent_id
    )

def record_gauge(name: str, value: float, labels: Dict = None, agent_id: str = "system"):
    """Record a gauge metric"""
    return MetricData(
        name=name,
        value=value,
        metric_type=MetricType.GAUGE,
        labels=labels or {},
        agent_id=agent_id
    )

def record_timer(name: str, value: float, labels: Dict = None, agent_id: str = "system"):
    """Record a timer metric (in milliseconds)"""
    return MetricData(
        name=name,
        value=value,
        metric_type=MetricType.TIMER,
        labels=labels or {},
        agent_id=agent_id
    )

def record_rate(name: str, value: float, labels: Dict = None, agent_id: str = "system"):
    """Record a rate metric"""
    return MetricData(
        name=name,
        value=value,
        metric_type=MetricType.RATE,
        labels=labels or {},
        agent_id=agent_id
    )
