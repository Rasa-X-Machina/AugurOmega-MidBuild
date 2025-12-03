"""
Augur Omega: Security Orchestration Layer
Integrates all security tools into a unified security framework
"""
import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
from pathlib import Path

# Import the security integrations
from ai_infra_guard_integration import AIIInfraGuardIntegration
from llm_security_integration import LLMTestingOrchestrator
from viper_integration import InfrastructureSecurityOrchestrator


class SecurityOrchestration:
    """
    Orchestrates all integrated security tools for comprehensive security assessment
    """
    
    def __init__(self, config_path: str = "security/config/security_orchestration_config.yaml"):
        self.logger = logging.getLogger(__name__)
        self.config = self._load_config(config_path)
        
        # Initialize all security tool integrations
        self._initialize_security_tools()
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load orchestration configuration"""
        config_file = Path(config_path)
        if config_file.exists():
            import yaml
            with open(config_file, 'r') as f:
                return yaml.safe_load(f)
        else:
            # Create default configuration
            default_config = {
                "orchestration": {
                    "parallel_execution": True,
                    "timeout_minutes": 60,
                    "retry_attempts": 3,
                    "failure_threshold": 0.8  # Fail if 80% of tools fail
                },
                "scheduling": {
                    "continuous_monitoring_interval_minutes": 60,
                    "compliance_scan_interval_days": 7,
                    "vulnerability_scan_interval_days": 1
                },
                "reporting": {
                    "format": "json",
                    "output_dir": "security/reports",
                    "retention_days": 90,
                    "notification_targets": ["security-team@example.com"]
                },
                "integration": {
                    "ai_infra_guard": {"enabled": True, "priority": 1},
                    "promptfoo_deepteam": {"enabled": True, "priority": 1},
                    "viper": {"enabled": True, "priority": 1},
                    "cervantes": {"enabled": True, "priority": 0},  # Not directly integrated yet
                    "red_team_osint": {"enabled": False, "priority": 0},  # Not implemented yet
                    "red_teaming_toolkit": {"enabled": False, "priority": 0}  # Not implemented yet
                }
            }
            
            # Create config directory if it doesn't exist
            config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(config_file, 'w') as f:
                import yaml
                yaml.dump(default_config, f)
            return default_config
    
    def _initialize_security_tools(self):
        """Initialize all security tool integrations"""
        self.tools = {}
        
        # Initialize AI-Infra-Guard for infrastructure security
        try:
            self.tools['ai_infra_guard'] = AIIInfraGuardIntegration()
            self.logger.info("AI-Infra-Guard integration initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize AI-Infra-Guard: {str(e)}")
            if self.config['integration']['ai_infra_guard']['enabled']:
                self.config['integration']['ai_infra_guard']['enabled'] = False
        
        # Initialize LLM security testing
        try:
            self.tools['llm_security'] = LLMTestingOrchestrator()
            self.logger.info("LLM Security testing integration initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize LLM Security: {str(e)}")
            if self.config['integration']['promptfoo_deepteam']['enabled']:
                self.config['integration']['promptfoo_deepteam']['enabled'] = False
        
        # Initialize Viper for infrastructure security
        try:
            self.tools['viper'] = InfrastructureSecurityOrchestrator()
            self.logger.info("Viper integration initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize Viper: {str(e)}")
            if self.config['integration']['viper']['enabled']:
                self.config['integration']['viper']['enabled'] = False
    
    async def run_comprehensive_security_assessment(self, assessment_targets: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run comprehensive security assessment using all available tools
        
        Args:
            assessment_targets: Dictionary containing targets for different security tools
                {
                    'infrastructure_targets': ['host1', 'host2'],
                    'llm_endpoints': ['endpoint1', 'endpoint2'], 
                    'ai_infrastructure_paths': ['/path/to/ai/infrastructure'],
                    'domain_for_osint': 'example.com'
                }
        
        Returns:
            Dictionary containing consolidated security assessment results
        """
        start_time = datetime.now()
        self.logger.info("Starting comprehensive security assessment")
        
        # Prepare tasks based on enabled tools
        tasks = []
        
        # AI Infrastructure Security Assessment (AI-Infra-Guard)
        if self.config['integration']['ai_infra_guard']['enabled']:
            infra_paths = assessment_targets.get('ai_infrastructure_paths', [])
            if infra_paths:
                tasks.extend([
                    asyncio.create_task(
                        self._run_ai_infra_guard_assessment(target, scan_type='full')
                    ) for target in infra_paths
                ])
        
        # LLM Security Assessment (Promptfoo & Deepteam)
        if self.config['integration']['promptfoo_deepteam']['enabled']:
            llm_endpoints = assessment_targets.get('llm_endpoints', [])
            if llm_endpoints:
                for endpoint in llm_endpoints:
                    # For demonstration, we'll use a mock model callback
                    async def mock_model_callback(prompt):
                        # This would be replaced with actual model calls
                        return f"Response to: {prompt[:50]}..."
                    
                    tasks.append(
                        asyncio.create_task(
                            self._run_llm_security_assessment(endpoint, mock_model_callback)
                        )
                    )
        
        # Infrastructure Security Assessment (Viper)
        if self.config['integration']['viper']['enabled']:
            infra_targets = assessment_targets.get('infrastructure_targets', [])
            if infra_targets:
                # Group targets for efficient scanning
                tasks.append(
                    asyncio.create_task(
                        self._run_viper_infrastructure_assessment(infra_targets)
                    )
                )
        
        # Execute all tasks in parallel
        task_results = []
        if tasks:
            try:
                task_results = await asyncio.gather(*tasks, return_exceptions=True)
            except Exception as e:
                self.logger.error(f"Error executing security assessment tasks: {str(e)}")
        
        # Consolidate results
        consolidated_results = self._consolidate_assessment_results(
            task_results, 
            assessment_targets, 
            start_time
        )
        
        # Generate comprehensive report
        report = self._generate_comprehensive_security_report(consolidated_results)
        
        # Save report
        self._save_comprehensive_report(report)
        
        # Handle notifications if needed
        self._handle_security_notifications(report)
        
        self.logger.info("Comprehensive security assessment completed")
        return report
    
    async def _run_ai_infra_guard_assessment(self, target: str, scan_type: str = 'full') -> Dict[str, Any]:
        """Run AI-Infra-Guard assessment"""
        try:
            if 'ai_infra_guard' in self.tools:
                results = self.tools['ai_infra_guard'].scan_infrastructure(target, scan_type)
                return {
                    'tool': 'ai_infra_guard',
                    'target': target,
                    'results': results,
                    'timestamp': self._get_current_timestamp()
                }
            else:
                return {
                    'tool': 'ai_infra_guard',
                    'target': target,
                    'error': 'Tool not available',
                    'timestamp': self._get_current_timestamp()
                }
        except Exception as e:
            self.logger.error(f"AI-Infra-Guard assessment failed for {target}: {str(e)}")
            return {
                'tool': 'ai_infra_guard',
                'target': target,
                'error': str(e),
                'timestamp': self._get_current_timestamp()
            }
    
    async def _run_llm_security_assessment(self, endpoint: str, model_callback) -> Dict[str, Any]:
        """Run LLM security assessment using Promptfoo and Deepteam"""
        try:
            if 'llm_security' in self.tools:
                results = await self.tools['llm_security'].run_comprehensive_llm_security_test(
                    endpoint, 
                    model_callback
                )
                return {
                    'tool': 'llm_security',
                    'target': endpoint,
                    'results': results,
                    'timestamp': self._get_current_timestamp()
                }
            else:
                return {
                    'tool': 'llm_security',
                    'target': endpoint,
                    'error': 'Tool not available',
                    'timestamp': self._get_current_timestamp()
                }
        except Exception as e:
            self.logger.error(f"LLM Security assessment failed for {endpoint}: {str(e)}")
            return {
                'tool': 'llm_security',
                'target': endpoint,
                'error': str(e),
                'timestamp': self._get_current_timestamp()
            }
    
    async def _run_viper_infrastructure_assessment(self, targets: List[str]) -> Dict[str, Any]:
        """Run infrastructure assessment using Viper"""
        try:
            if 'viper' in self.tools:
                results = self.tools['viper'].run_comprehensive_infrastructure_scan(targets)
                return {
                    'tool': 'viper',
                    'targets': targets,
                    'results': results,
                    'timestamp': self._get_current_timestamp()
                }
            else:
                return {
                    'tool': 'viper',
                    'targets': targets,
                    'error': 'Tool not available',
                    'timestamp': self._get_current_timestamp()
                }
        except Exception as e:
            self.logger.error(f"Viper assessment failed for {targets}: {str(e)}")
            return {
                'tool': 'viper',
                'targets': targets,
                'error': str(e),
                'timestamp': self._get_current_timestamp()
            }
    
    def _consolidate_assessment_results(self, task_results: List[Any], 
                                      assessment_targets: Dict[str, Any], 
                                      start_time: datetime) -> Dict[str, Any]:
        """Consolidate results from multiple security tools"""
        consolidated = {
            'assessment_targets': assessment_targets,
            'start_time': start_time.isoformat(),
            'completion_time': self._get_current_timestamp(),
            'total_duration_seconds': (datetime.now() - start_time).total_seconds(),
            'tool_results': {},
            'consolidated_metrics': {
                'total_findings': 0,
                'critical_vulnerabilities': 0,
                'high_vulnerabilities': 0,
                'medium_vulnerabilities': 0,
                'tools_executed': 0,
                'tools_failed': 0
            },
            'risk_assessment': {
                'overall_risk_score': 0.0,
                'overall_risk_level': 'unknown',
                'business_impact': 'unknown'
            },
            'priority_actions': []
        }
        
        for result in task_results:
            if isinstance(result, dict) and 'tool' in result:
                tool_name = result['tool']
                consolidated['tool_results'][tool_name] = result
                
                # Update metrics based on tool results
                self._update_consolidated_metrics(consolidated['consolidated_metrics'], result)
                
                # Update risk assessment
                self._update_risk_assessment(consolidated['risk_assessment'], result)
                
                # Add priority actions
                priority_actions = self._extract_priority_actions(result)
                consolidated['priority_actions'].extend(priority_actions)
            
            elif isinstance(result, Exception):
                self.logger.error(f"Task failed with exception: {str(result)}")
                consolidated['consolidated_metrics']['tools_failed'] += 1
            else:
                self.logger.warning(f"Unexpected result type: {type(result)}")
        
        # Calculate overall metrics
        consolidated['consolidated_metrics']['tools_executed'] = len(task_results) - consolidated['consolidated_metrics']['tools_failed']
        consolidated['risk_assessment']['overall_risk_level'] = self._calculate_overall_risk_level(consolidated['risk_assessment']['overall_risk_score'])
        
        return consolidated
    
    def _update_consolidated_metrics(self, metrics: Dict[str, int], result: Dict[str, Any]):
        """Update consolidated metrics based on individual tool results"""
        tool_name = result.get('tool', 'unknown')
        tool_results = result.get('results', {})
        
        if tool_name == 'ai_infra_guard':
            # Extract from AI-Infra-Guard results
            summary = tool_results.get('summary', {})
            severity_counts = summary.get('by_severity', {})
            
            metrics['critical_vulnerabilities'] += severity_counts.get('critical', 0)
            metrics['high_vulnerabilities'] += severity_counts.get('high', 0)
            metrics['medium_vulnerabilities'] += severity_counts.get('medium', 0)
            metrics['total_findings'] += sum(severity_counts.values())
        
        elif tool_name == 'llm_security':
            # Extract from LLM Security results
            pf_results = tool_results.get('promptfoo_results', {})
            dt_results = tool_results.get('deepteam_results', {})
            
            # Get metrics from Promptfoo
            pf_metrics = pf_results.get('security_metrics', {})
            metrics['total_findings'] += pf_metrics.get('total_vulnerabilities', 0)
            # Estimate critical/high from Promptfoo
            for vuln in pf_results.get('vulnerabilities', []):
                if vuln.get('severity') == 'critical':
                    metrics['critical_vulnerabilities'] += 1
                elif vuln.get('severity') == 'high':
                    metrics['high_vulnerabilities'] += 1
            
            # Get metrics from Deepteam (estimated from risk score)
            dt_risk = dt_results.get('overall_risk_score', 0)
            estimated_vulns = int(dt_risk * 50)
            metrics['total_findings'] += estimated_vulns
        
        elif tool_name == 'viper':
            # Extract from Viper results
            viper_metrics = tool_results.get('metrics', {})
            metrics['total_findings'] += viper_metrics.get('total_findings', 0)
            metrics['critical_vulnerabilities'] += viper_metrics.get('critical_vulnerabilities', 0)
            metrics['high_vulnerabilities'] += viper_metrics.get('high_vulnerabilities', 0)
    
    def _update_risk_assessment(self, risk_assessment: Dict[str, Any], result: Dict[str, Any]):
        """Update overall risk assessment based on tool results"""
        tool_results = result.get('results', {})
        
        if result.get('tool') == 'ai_infra_guard':
            tool_risk = tool_results.get('risk_assessment', {})
            risk_score = tool_risk.get('risk_score', 0.0)
            # Use weighted average for AI-Infra-Guard (weight 0.3)
            risk_assessment['overall_risk_score'] += risk_score * 0.3
        
        elif result.get('tool') == 'llm_security':
            tool_risk = tool_results.get('risk_assessment', {})
            risk_score = tool_risk.get('score', 0.0)
            # Use weighted average for LLM Security (weight 0.4)
            risk_assessment['overall_risk_score'] += risk_score * 0.4
        
        elif result.get('tool') == 'viper':
            tool_risk = tool_results.get('overall_assessment', {})
            risk_score = tool_risk.get('score', 0.0)
            # Use weighted average for Viper (weight 0.3)
            risk_assessment['overall_risk_score'] += risk_score * 0.3
        
        # Cap at 1.0
        risk_assessment['overall_risk_score'] = min(1.0, risk_assessment['overall_risk_score'])
    
    def _extract_priority_actions(self, result: Dict[str, Any]) -> List[str]:
        """Extract priority actions from tool results"""
        tool_name = result.get('tool', 'unknown')
        tool_results = result.get('results', {})
        
        actions = []
        
        if tool_name == 'ai_infra_guard':
            actions.extend(tool_results.get('summary', {}).get('recommended_actions', []))
        
        elif tool_name == 'llm_security':
            actions.extend(tool_results.get('remediation', {}).get('priority_actions', []))
        
        elif tool_name == 'viper':
            actions.extend(tool_results.get('priority_actions', []))
        
        return actions
    
    def _calculate_overall_risk_level(self, risk_score: float) -> str:
        """Calculate risk level from risk score"""
        if risk_score >= 0.8:
            return 'critical'
        elif risk_score >= 0.6:
            return 'high'
        elif risk_score >= 0.4:
            return 'medium'
        elif risk_score >= 0.2:
            return 'low'
        else:
            return 'none'
    
    def _generate_comprehensive_security_report(self, consolidated_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive security report from consolidated results"""
        return {
            'version': '1.0',
            'type': 'comprehensive_security_assessment_report',
            'metadata': {
                'created': self._get_current_timestamp(),
                'generator': 'Augur Omega Security Orchestration',
                'assessment_targets': consolidated_results['assessment_targets']
            },
            'executive_summary': {
                'overall_risk_level': consolidated_results['risk_assessment']['overall_risk_level'],
                'total_findings': consolidated_results['consolidated_metrics']['total_findings'],
                'critical_vulnerabilities': consolidated_results['consolidated_metrics']['critical_vulnerabilities'],
                'high_vulnerabilities': consolidated_results['consolidated_metrics']['high_vulnerabilities'],
                'assessment_summary': f"Comprehensive security assessment completed across AI infrastructure, LLM endpoints, and general infrastructure with {consolidated_results['consolidated_metrics']['tools_executed']} tools."
            },
            'consolidated_metrics': consolidated_results['consolidated_metrics'],
            'detailed_findings': {
                'ai_infrastructure': consolidated_results['tool_results'].get('ai_infra_guard', {}),
                'llm_security': consolidated_results['tool_results'].get('llm_security', {}),
                'infrastructure_security': consolidated_results['tool_results'].get('viper', {})
            },
            'risk_assessment': consolidated_results['risk_assessment'],
            'recommended_actions': {
                'immediate': [a for a in consolidated_results['priority_actions'] if 'CRITICAL' in a.upper() or 'IMMEDIATE' in a.upper()],
                'short_term': [a for a in consolidated_results['priority_actions'] if 'CRITICAL' not in a.upper() and 'IMMEDIATE' not in a.upper() and ('HIGH' in a.upper() or '30' in a.upper())],
                'medium_term': [a for a in consolidated_results['priority_actions'] if 'HIGH' not in a.upper() and '30' not in a.upper() and ('MEDIUM' in a.upper() or '90' in a.upper())],
                'ongoing': [a for a in consolidated_results['priority_actions'] if 'HIGH' not in a.upper() and 'MEDIUM' not in a.upper() and '30' not in a.upper() and '90' not in a.upper()]
            },
            'timeline': {
                'start_time': consolidated_results['start_time'],
                'completion_time': consolidated_results['completion_time'],
                'duration_seconds': consolidated_results['total_duration_seconds']
            }
        }
    
    def _save_comprehensive_report(self, report: Dict[str, Any]):
        """Save comprehensive security report to file"""
        output_dir = Path(self.config['reporting']['output_dir'])
        output_dir.mkdir(parents=True, exist_ok=True)
        
        filename = output_dir / f"comprehensive_security_report_{report['metadata']['created'].replace(':', '-')}.json"
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.logger.info(f"Comprehensive security report saved: {filename}")
    
    def _handle_security_notifications(self, report: Dict[str, Any]):
        """Handle security notifications based on report"""
        # Check if critical vulnerabilities were found
        if report['executive_summary']['critical_vulnerabilities'] > 0:
            self.logger.warning(f"CRITICAL VULNERABILITIES FOUND: {report['executive_summary']['critical_vulnerabilities']}")
            
            # In a real implementation, this would send notifications to configured targets
            # For now, we'll just log the notification
            for target in self.config['reporting']['notification_targets']:
                self.logger.info(f"Notification would be sent to: {target}")
        
        # Check if high vulnerabilities were found
        elif report['executive_summary']['high_vulnerabilities'] > 0:
            self.logger.warning(f"HIGH VULNERABILITIES FOUND: {report['executive_summary']['high_vulnerabilities']}")
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        return datetime.now().isoformat()
    
    def run_continuous_security_monitoring(self, assessment_targets: Dict[str, Any]):
        """Run continuous security monitoring"""
        import threading
        import time
        
        def monitoring_loop():
            while True:
                try:
                    # Run security assessment
                    assessment_task = self.run_comprehensive_security_assessment(assessment_targets)
                    # In a real implementation, this would be awaited
                    # For this sync wrapper, we'll use asyncio.run
                    import asyncio
                    if hasattr(asyncio, 'run'):
                        report = asyncio.run(assessment_task)
                    else:
                        # Fallback for older Python versions
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        try:
                            report = loop.run_until_complete(assessment_task)
                        finally:
                            loop.close()
                    
                    # Log assessment results
                    self.logger.info(f"Continuous monitoring assessment completed: {report['executive_summary']['overall_risk_level']} risk level")
                    
                    # Sleep for configured interval
                    interval = self.config['scheduling']['continuous_monitoring_interval_minutes'] * 60
                    time.sleep(interval)
                    
                except KeyboardInterrupt:
                    self.logger.info("Continuous monitoring stopped by user")
                    break
                except Exception as e:
                    self.logger.error(f"Error in continuous monitoring: {str(e)}")
                    # Continue monitoring even after errors
                    interval = self.config['scheduling']['continuous_monitoring_interval_minutes'] * 60
                    time.sleep(interval)
        
        # Run monitoring in a separate thread
        monitor_thread = threading.Thread(target=monitoring_loop, daemon=True)
        monitor_thread.start()
        
        return monitor_thread
    
    async def run_compliance_scan(self, compliance_framework: str = "OWASP") -> Dict[str, Any]:
        """Run compliance-focused security scan"""
        self.logger.info(f"Starting {compliance_framework} compliance scan")
        
        # This would execute specialized compliance tests
        # For now, we'll run a standard assessment with compliance focus
        targets = {
            'infrastructure_targets': ['localhost'],  # Default target for compliance
            'llm_endpoints': ['default_llm_endpoint'],
            'ai_infrastructure_paths': ['.']  # Current directory
        }
        
        assessment = await self.run_comprehensive_security_assessment(targets)
        
        # Add compliance-specific analysis
        compliance_results = self._add_compliance_analysis(assessment, compliance_framework)
        
        return compliance_results
    
    def _add_compliance_analysis(self, assessment: Dict[str, Any], framework: str) -> Dict[str, Any]:
        """Add compliance-specific analysis to assessment"""
        # Add compliance-specific mappings and analysis
        compliance_analysis = {
            'framework': framework,
            'requirements_mapped': [],
            'compliance_score': 0.0,
            'non_compliant_areas': [],
            'compliance_recommendations': []
        }
        
        # For OWASP, map findings to OWASP Top 10 categories
        if framework == "OWASP":
            # Map findings to OWASP categories
            owasp_mapping = {
                'prompt_injection': 'A01:2021-Broken Access Control',
                'pii_leakage': 'A04:2021-Insecure Design',
                'authentication_bypass': 'A01:2021-Broken Access Control',
                'injection': 'A03:2021-Injection',
                'vulnerable_components': 'A06:2021-Vulnerable and Outdated Components'
            }
            
            # Extract OWASP-relevant findings
            for tool_results in assessment['detailed_findings'].values():
                if 'vulnerabilities' in tool_results:
                    for finding in tool_results['vulnerabilities']:
                        finding_type = finding.get('type', 'unknown')
                        if finding_type in owasp_mapping:
                            compliance_analysis['requirements_mapped'].append({
                                'finding': finding,
                                'owasp_category': owasp_mapping[finding_type],
                                'severity': finding.get('severity', 'medium')
                            })
        
        assessment['compliance_analysis'] = compliance_analysis
        return assessment
    
    async def run_security_awareness_training(self) -> Dict[str, Any]:
        """Run security awareness training based on assessment findings"""
        # This would implement security awareness functionality
        # For now, return a mock training report
        return {
            'training_type': 'security_awareness',
            'recommendations': [
                'Review recent security vulnerabilities with development team',
                'Update secure coding practices documentation',
                'Schedule advanced security training for platform developers'
            ],
            'target_audience': ['developers', 'security_team'],
            'delivery_method': 'interactive_workshop',
            'estimated_duration_hours': 8
        }


# Example usage function
async def example_usage():
    """
    Example of how to use the Security Orchestration system
    """
    # Create security orchestration instance
    security_orchestrator = SecurityOrchestration()
    
    # Define assessment targets
    targets = {
        'infrastructure_targets': ['localhost', '127.0.0.1'],
        'llm_endpoints': ['mock_llm_endpoint'],
        'ai_infrastructure_paths': ['.'],  # Current directory
        'domain_for_osint': 'example.com'
    }
    
    # Run comprehensive security assessment
    assessment_report = await security_orchestrator.run_comprehensive_security_assessment(targets)
    
    print(f"Security assessment completed with {assessment_report['executive_summary']['overall_risk_level']} risk level")
    print(f"Total findings: {assessment_report['executive_summary']['total_findings']}")
    print(f"Critical vulnerabilities: {assessment_report['executive_summary']['critical_vulnerabilities']}")
    
    # Run compliance scan
    compliance_report = await security_orchestrator.run_compliance_scan("OWASP")
    print(f"Compliance analysis completed for {compliance_report['compliance_analysis']['framework']}")
    
    # Start continuous monitoring (in background)
    # monitor_thread = security_orchestrator.run_continuous_security_monitoring(targets)
    
    return assessment_report


# If this script is run directly, execute the example
if __name__ == "__main__":
    import asyncio
    asyncio.run(example_usage())