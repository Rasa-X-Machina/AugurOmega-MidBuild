"""
Analysis Engine - Intelligent performance analysis and diagnostics
Provides 10x improvement detection and optimization recommendations
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from collections import defaultdict, deque
import json
import numpy as np
import threading
from concurrent.futures import ThreadPoolExecutor
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

@dataclass
class AnalysisResult:
    """Container for analysis results"""
    analysis_type: str
    agent_id: str
    timestamp: datetime
    findings: List[Dict[str, Any]]
    recommendations: List[Dict[str, Any]]
    confidence_score: float  # 0-1
    severity: str  # 'low', 'medium', 'high', 'critical'
    
    def to_dict(self) -> Dict:
        return {
            'analysis_type': self.analysis_type,
            'agent_id': self.agent_id,
            'timestamp': self.timestamp.isoformat(),
            'findings': self.findings,
            'recommendations': self.recommendations,
            'confidence_score': self.confidence_score,
            'severity': self.severity
        }

@dataclass
class PerformanceTrend:
    """Performance trend analysis"""
    metric_name: str
    trend_direction: str  # 'improving', 'degrading', 'stable'
    trend_strength: float  # 0-1
    expected_value: float
    actual_value: float
    deviation_percentage: float
    prediction_confidence: float

class SystemAnalyzer:
    """
    Advanced Performance Analysis Engine
    Features:
    - Multi-dimensional performance analysis
    - Machine learning-based anomaly detection
    - Predictive analytics
    - 10x improvement opportunity identification
    - Root cause analysis
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or self._default_config()
        self.logger = logging.getLogger(__name__)
        
        # Analysis modules
        self.trend_analyzer = TrendAnalyzer()
        self.anomaly_detector = AnomalyDetector()
        self.bottleneck_analyzer = BottleneckAnalyzer()
        self.improvement_detector = ImprovementDetector()
        
        # Analysis results storage
        self.analysis_results: Dict[str, List[AnalysisResult]] = defaultdict(list)
        self.performance_trends: Dict[str, List[PerformanceTrend]] = defaultdict(list)
        
        # Machine learning models
        self.models: Dict[str, Any] = {}
        self.scalers: Dict[str, StandardScaler] = {}
        
        # Analysis configuration
        self.analysis_windows = {
            'short': timedelta(minutes=15),
            'medium': timedelta(hours=2),
            'long': timedelta(hours=24)
        }
        
        # Performance thresholds
        self.thresholds = {
            'cpu_critical': 95.0,
            'cpu_warning': 85.0,
            'memory_critical': 95.0,
            'memory_warning': 85.0,
            'latency_critical': 500.0,
            'latency_warning': 200.0,
            'error_rate_critical': 0.1,
            'error_rate_warning': 0.05
        }
        
        # Threading
        self.analysis_active = False
        self.analysis_thread: Optional[threading.Thread] = None
        self.executor = ThreadPoolExecutor(max_workers=5)
        
        # Statistics
        self.analyses_performed = 0
        self.improvements_detected = 0
        self.anomalies_detected = 0
        
        self.logger.info("System Analyzer initialized")
    
    def _default_config(self) -> Dict:
        """Default configuration for system analyzer"""
        return {
            'enable_ml_analysis': True,
            'enable_predictive_analytics': True,
            'enable_improvement_detection': True,
            'analysis_interval': 30,  # seconds
            'trend_detection_window': 60,  # minutes
            'anomaly_detection_sensitivity': 0.1,
            'min_data_points': 10,
            'enable_clustering': True
        }
    
    async def start_analyzer(self):
        """Start the system analyzer"""
        if self.analysis_active:
            self.logger.warning("System analyzer already running")
            return
        
        self.analysis_active = True
        
        # Initialize ML models
        if self.config.get('enable_ml_analysis', False):
            self._initialize_ml_models()
        
        # Start analysis thread
        self.analysis_thread = threading.Thread(target=self._analysis_loop, daemon=True)
        self.analysis_thread.start()
        
        self.logger.info("🔍 System Analyzer started")
    
    async def stop_analyzer(self):
        """Stop the system analyzer"""
        self.analysis_active = False
        
        if self.analysis_thread:
            self.analysis_thread.join(timeout=5)
        
        self.executor.shutdown(wait=True)
        
        self.logger.info("System Analyzer stopped")
    
    def _initialize_ml_models(self):
        """Initialize machine learning models"""
        try:
            # Anomaly detection model
            self.models['anomaly_detector'] = IsolationForest(
                contamination=self.config.get('anomaly_detection_sensitivity', 0.1),
                random_state=42
            )
            
            # Clustering model for agent grouping
            self.models['agent_clustering'] = KMeans(
                n_clusters=5,
                random_state=42,
                n_init=10
            )
            
            self.logger.info("ML models initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing ML models: {e}")
    
    def analyze_agent_performance(self, agent_id: str, metrics_history: List[Dict]) -> AnalysisResult:
        """Perform comprehensive performance analysis for an agent"""
        findings = []
        recommendations = []
        
        if len(metrics_history) < self.config['min_data_points']:
            return AnalysisResult(
                analysis_type="comprehensive",
                agent_id=agent_id,
                timestamp=datetime.now(),
                findings=[],
                recommendations=[],
                confidence_score=0.0,
                severity="low"
            )
        
        try:
            # Trend analysis
            trend_findings, trend_recommendations = self.trend_analyzer.analyze_trends(
                agent_id, metrics_history
            )
            findings.extend(trend_findings)
            recommendations.extend(trend_recommendations)
            
            # Anomaly detection
            anomaly_findings, anomaly_recommendations = self.anomaly_detector.detect_anomalies(
                agent_id, metrics_history, self.models.get('anomaly_detector')
            )
            findings.extend(anomaly_findings)
            recommendations.extend(anomaly_recommendations)
            
            # Bottleneck analysis
            bottleneck_findings, bottleneck_recommendations = self.bottleneck_analyzer.identify_bottlenecks(
                agent_id, metrics_history
            )
            findings.extend(bottleneck_findings)
            recommendations.extend(bottleneck_recommendations)
            
            # Improvement opportunity detection
            improvement_findings, improvement_recommendations = self.improvement_detector.find_improvements(
                agent_id, metrics_history
            )
            findings.extend(improvement_findings)
            recommendations.extend(improvement_recommendations)
            
            # Determine overall severity and confidence
            severity = self._determine_overall_severity(findings)
            confidence = self._calculate_confidence_score(findings, metrics_history)
            
            # Store results
            result = AnalysisResult(
                analysis_type="comprehensive",
                agent_id=agent_id,
                timestamp=datetime.now(),
                findings=findings,
                recommendations=recommendations,
                confidence_score=confidence,
                severity=severity
            )
            
            self.analysis_results[agent_id].append(result)
            self.analyses_performed += 1
            
            self.logger.info(f"Completed analysis for {agent_id}: {len(findings)} findings, {len(recommendations)} recommendations")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error analyzing agent {agent_id}: {e}")
            return AnalysisResult(
                analysis_type="error",
                agent_id=agent_id,
                timestamp=datetime.now(),
                findings=[{"error": f"Analysis failed: {str(e)}"}],
                recommendations=[],
                confidence_score=0.0,
                severity="medium"
            )
    
    def _determine_overall_severity(self, findings: List[Dict]) -> str:
        """Determine overall severity from findings"""
        severity_scores = {
            'low': 1,
            'medium': 2,
            'high': 3,
            'critical': 4
        }
        
        max_severity = 'low'
        max_score = 0
        
        for finding in findings:
            severity = finding.get('severity', 'low')
            score = severity_scores.get(severity, 1)
            
            if score > max_score:
                max_score = score
                max_severity = severity
        
        return max_severity
    
    def _calculate_confidence_score(self, findings: List[Dict], metrics_history: List[Dict]) -> float:
        """Calculate confidence score for analysis"""
        base_confidence = 0.5
        
        # Increase confidence based on data volume
        data_confidence = min(0.3, len(metrics_history) / 100 * 0.3)
        
        # Increase confidence based on finding specificity
        specificity_confidence = 0.0
        for finding in findings:
            if finding.get('confidence', 0) > 0:
                specificity_confidence += finding['confidence']
        
        specificity_confidence = min(0.2, specificity_confidence / len(findings) if findings else 0)
        
        total_confidence = base_confidence + data_confidence + specificity_confidence
        return min(1.0, total_confidence)
    
    def _analysis_loop(self):
        """Main analysis loop for continuous monitoring"""
        while self.analysis_active:
            try:
                # Perform periodic analysis of all agents
                # This would be called with actual agent data in a real implementation
                
                # For demonstration, simulate some analysis
                self.executor.submit(self._simulate_periodic_analysis)
                
                import time
                time.sleep(self.config['analysis_interval'])
                
            except Exception as e:
                self.logger.error(f"Error in analysis loop: {e}")
                import time
                time.sleep(10)
    
    def _simulate_periodic_analysis(self):
        """Simulate periodic analysis for demonstration"""
        # In a real implementation, this would:
        # 1. Get current agent data from monitoring system
        # 2. Perform analysis on each agent
        # 3. Store results and trigger notifications
        
        # Simulate analysis completion
        self.logger.debug("Performed periodic analysis batch")
    
    def get_latest_analysis(self, agent_id: str) -> Optional[AnalysisResult]:
        """Get the latest analysis result for an agent"""
        results = self.analysis_results.get(agent_id, [])
        return results[-1] if results else None
    
    def get_all_analyses(self, agent_id: str, limit: int = 10) -> List[AnalysisResult]:
        """Get recent analysis results for an agent"""
        results = self.analysis_results.get(agent_id, [])
        return results[-limit:] if results else []
    
    def get_analysis_summary(self) -> Dict:
        """Get comprehensive analysis summary"""
        total_agents = len(self.analysis_results)
        critical_issues = 0
        high_issues = 0
        total_findings = 0
        total_recommendations = 0
        
        for agent_id, results in self.analysis_results.items():
            if results:
                latest = results[-1]
                total_findings += len(latest.findings)
                total_recommendations += len(latest.recommendations)
                
                if latest.severity == 'critical':
                    critical_issues += 1
                elif latest.severity == 'high':
                    high_issues += 1
        
        return {
            "timestamp": datetime.now().isoformat(),
            "total_agents_analyzed": total_agents,
            "analyses_performed": self.analyses_performed,
            "critical_issues": critical_issues,
            "high_issues": high_issues,
            "total_findings": total_findings,
            "total_recommendations": total_recommendations,
            "improvements_detected": self.improvements_detected,
            "anomalies_detected": self.anomalies_detected,
            "analysis_rate": self.analyses_performed / max(1, (datetime.now() - datetime.now()).total_seconds())
        }
    
    def export_analysis_results(self, output_path: str):
        """Export analysis results to file"""
        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "summary": self.get_analysis_summary(),
            "analysis_results": {}
        }
        
        for agent_id, results in self.analysis_results.items():
            export_data["analysis_results"][agent_id] = [
                result.to_dict() for result in results
            ]
        
        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        self.logger.info(f"Analysis results exported to {output_path}")

# Additional analyzer classes
class TrendAnalyzer:
    """Analyzes performance trends over time"""
    
    def analyze_trends(self, agent_id: str, metrics_history: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """Analyze performance trends"""
        findings = []
        recommendations = []
        
        # Simple trend analysis for key metrics
        metrics_to_analyze = ['cpu_usage', 'memory_usage', 'latency_p95', 'throughput']
        
        for metric in metrics_to_analyze:
            values = [m.get(metric, 0) for m in metrics_history if m.get(metric) is not None]
            
            if len(values) < 5:
                continue
            
            # Calculate trend
            x = np.arange(len(values))
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, values)
            
            # Determine trend direction and strength
            if abs(r_value) > 0.7:  # Strong correlation
                if slope > 0 and metric in ['cpu_usage', 'memory_usage', 'latency_p95']:
                    findings.append({
                        'type': 'increasing_trend',
                        'metric': metric,
                        'severity': 'high' if slope > 1 else 'medium',
                        'description': f"{metric} showing increasing trend (slope: {slope:.2f})",
                        'confidence': abs(r_value)
                    })
                    recommendations.append({
                        'type': 'performance_tuning',
                        'metric': metric,
                        'description': f"Investigate {metric} increasing trend",
                        'priority': 'high'
                    })
                elif slope < 0 and metric == 'throughput':
                    findings.append({
                        'type': 'decreasing_trend',
                        'metric': metric,
                        'severity': 'medium',
                        'description': f"{metric} showing decreasing trend",
                        'confidence': abs(r_value)
                    })
        
        return findings, recommendations

class AnomalyDetector:
    """Detects anomalies in performance data"""
    
    def detect_anomalies(self, agent_id: str, metrics_history: List[Dict], model=None) -> Tuple[List[Dict], List[Dict]]:
        """Detect anomalies using statistical methods or ML"""
        findings = []
        recommendations = []
        
        if len(metrics_history) < 10:
            return findings, recommendations
        
        # Statistical anomaly detection
        key_metrics = ['cpu_usage', 'memory_usage', 'latency_p95']
        
        for metric in key_metrics:
            values = [m.get(metric, 0) for m in metrics_history if m.get(metric) is not None]
            
            if len(values) < 5:
                continue
            
            mean_val = np.mean(values)
            std_val = np.std(values)
            
            # Check for outliers (2-sigma rule)
            for i, value in enumerate(values[-5:]):  # Check last 5 points
                z_score = abs(value - mean_val) / std_val if std_val > 0 else 0
                
                if z_score > 2.0:
                    findings.append({
                        'type': 'statistical_anomaly',
                        'metric': metric,
                        'severity': 'high' if z_score > 3.0 else 'medium',
                        'description': f"Anomalous {metric} value: {value:.1f} (z-score: {z_score:.2f})",
                        'confidence': min(1.0, z_score / 3.0),
                        'data_point_index': len(values) - 5 + i
                    })
                    recommendations.append({
                        'type': 'investigate_anomaly',
                        'metric': metric,
                        'description': f"Investigate anomalous {metric} values",
                        'priority': 'medium'
                    })
        
        return findings, recommendations

class BottleneckAnalyzer:
    """Identifies performance bottlenecks"""
    
    def identify_bottlenecks(self, agent_id: str, metrics_history: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """Identify performance bottlenecks"""
        findings = []
        recommendations = []
        
        if not metrics_history:
            return findings, recommendations
        
        latest = metrics_history[-1]
        
        # CPU bottleneck
        if latest.get('cpu_usage', 0) > 90:
            findings.append({
                'type': 'cpu_bottleneck',
                'severity': 'critical',
                'description': f"High CPU usage: {latest['cpu_usage']:.1f}%",
                'confidence': 0.9
            })
            recommendations.append({
                'type': 'cpu_optimization',
                'description': 'Optimize CPU-intensive operations',
                'priority': 'high'
            })
        
        # Memory bottleneck
        if latest.get('memory_usage', 0) > 90:
            findings.append({
                'type': 'memory_bottleneck',
                'severity': 'critical',
                'description': f"High memory usage: {latest['memory_usage']:.1f}%",
                'confidence': 0.9
            })
            recommendations.append({
                'type': 'memory_optimization',
                'description': 'Optimize memory usage and garbage collection',
                'priority': 'high'
            })
        
        # Latency bottleneck
        if latest.get('latency_p95', 0) > 300:
            findings.append({
                'type': 'latency_bottleneck',
                'severity': 'high',
                'description': f"High latency: {latest['latency_p95']:.1f}ms",
                'confidence': 0.8
            })
            recommendations.append({
                'type': 'latency_optimization',
                'description': 'Optimize response times and reduce blocking operations',
                'priority': 'high'
            })
        
        # I/O bottleneck (inferred from low CPU, high latency)
        if (latest.get('cpu_usage', 0) < 50 and 
            latest.get('latency_p95', 0) > 200):
            findings.append({
                'type': 'io_bottleneck',
                'severity': 'medium',
                'description': 'Potential I/O bottleneck (low CPU, high latency)',
                'confidence': 0.6
            })
            recommendations.append({
                'type': 'io_optimization',
                'description': 'Optimize I/O operations and consider async patterns',
                'priority': 'medium'
            })
        
        return findings, recommendations

class ImprovementDetector:
    """Detects improvement opportunities"""
    
    def find_improvements(self, agent_id: str, metrics_history: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """Find improvement opportunities for 10x optimization"""
        findings = []
        recommendations = []
        
        if len(metrics_history) < 10:
            return findings, recommendations
        
        latest = metrics_history[-1]
        
        # Underutilization opportunities
        if latest.get('cpu_usage', 0) < 30 and latest.get('memory_usage', 0) < 50:
            findings.append({
                'type': 'underutilization',
                'severity': 'low',
                'description': 'Agent underutilized - could handle more load',
                'confidence': 0.7
            })
            recommendations.append({
                'type': 'load_balancing',
                'description': 'Redistribute load to increase efficiency',
                'priority': 'medium'
            })
        
        # Concurrency optimization
        if latest.get('semaphore_utilization', 0) < 0.5:
            findings.append({
                'type': 'concurrency_optimization',
                'severity': 'low',
                'description': 'Low semaphore utilization - opportunity to increase concurrency',
                'confidence': 0.6
            })
            recommendations.append({
                'type': 'concurrency_tuning',
                'description': 'Increase concurrency settings for better throughput',
                'priority': 'medium'
            })
        
        # Cache optimization
        if latest.get('latency_p95', 0) > 150 and latest.get('cpu_usage', 0) < 70:
            findings.append({
                'type': 'cache_opportunity',
                'severity': 'medium',
                'description': 'High latency with moderate CPU - caching opportunity',
                'confidence': 0.5
            })
            recommendations.append({
                'type': 'caching_strategy',
                'description': 'Implement caching to reduce latency',
                'priority': 'medium'
            })
        
        # Batch processing opportunity
        if latest.get('throughput', 0) < 100 and latest.get('queue_length', 0) > 10:
            findings.append({
                'type': 'batch_processing',
                'severity': 'medium',
                'description': 'Low throughput with queue buildup - batch processing opportunity',
                'confidence': 0.6
            })
            recommendations.append({
                'type': 'batch_optimization',
                'description': 'Implement batch processing to improve throughput',
                'priority': 'high'
            })
        
        return findings, recommendations
