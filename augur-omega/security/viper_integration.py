"""
Augur Omega: Viper Red Team Platform Integration
Integrates Viper's comprehensive red team platform for infrastructure security
"""
import requests
import json
import os
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
import time
from datetime import datetime


class ViperIntegration:
    """
    Integration with Viper red team platform for infrastructure security
    """
    
    def __init__(self, config_path: str = "security/config/viper_config.yaml"):
        self.config_path = config_path
        self.logger = logging.getLogger(__name__)
        self.config = self._load_config()
        
        # Initialize session with authentication
        self.session = requests.Session()
        self.api_key = self.config.get('api_key', os.getenv('VIPER_API_KEY', ''))
        if self.api_key:
            self.session.headers.update({'Authorization': f'Bearer {self.api_key}'})
        
        self.base_url = self.config.get('api_url', 'http://localhost:8080')
        self.timeout = self.config.get('timeout', 300)  # 5 minutes default
    
    def _load_config(self) -> Dict[str, Any]:
        """Load Viper integration configuration"""
        config_file = Path(self.config_path)
        if config_file.exists():
            import yaml
            with open(config_file, 'r') as f:
                return yaml.safe_load(f)
        else:
            # Create default configuration
            default_config = {
                "api_url": "http://localhost:8080",
                "api_key": "",  # Set in environment variable VIPER_API_KEY
                "timeout": 300,
                "default_modules": [
                    "port_scanner",
                    "service_enumeration",
                    "vulnerability_scanner",
                    "misconfiguration_detector",
                    "api_security_tester",
                    "authentication_bypass",
                    "authorization_checker",
                    "docker_security_scanner",
                    "kubernetes_security_assessment"
                ],
                "max_depth": 3,
                "ai_assistance": True,
                "reporting": {
                    "format": "json",
                    "output_dir": "security/reports",
                    "retention_days": 90
                }
            }
            # Create config directory if it doesn't exist
            config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(config_file, 'w') as f:
                import yaml
                yaml.dump(default_config, f)
            return default_config
    
    def run_infrastructure_security_scan(self, target_hosts: List[str], 
                                       custom_modules: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Run Viper's comprehensive infrastructure security scan
        
        Args:
            target_hosts: List of hosts/IPs to scan
            custom_modules: List of specific modules to run (uses defaults if None)
        
        Returns:
            Dictionary containing scan results
        """
        try:
            self.logger.info(f"Starting Viper security scan for targets: {target_hosts}")
            
            # Prepare scan request
            scan_request = {
                'targets': target_hosts,
                'modules': custom_modules or self.config['default_modules'],
                'options': {
                    'timeout': self.config['timeout'],
                    'max_depth': self.config['max_depth'],
                    'ai_assistance': self.config['ai_assistance']
                }
            }
            
            # Make API request to Viper
            response = self.session.post(
                f"{self.base_url}/api/v1/scan",
                json=scan_request,
                timeout=self.timeout + 30  # Add buffer to timeout
            )
            
            if response.status_code == 200:
                scan_response = response.json()
                
                # If scan initiated successfully, poll for results
                scan_id = scan_response.get('scan_id')
                if scan_id:
                    results = self._poll_scan_results(scan_id)
                    self.logger.info(f"Viper scan completed. Found {len(results.get('findings', []))} findings")
                    return self._process_scan_results(results, target_hosts)
                else:
                    self.logger.error(f"Viper scan failed to start: {scan_response}")
                    return {
                        "error": "Scan initiation failed",
                        "response": scan_response,
                        "targets": target_hosts
                    }
            else:
                self.logger.error(f"Viper API request failed: {response.status_code} - {response.text}")
                return {
                    "error": f"API request failed with status {response.status_code}",
                    "status_code": response.status_code,
                    "targets": target_hosts
                }
                
        except requests.exceptions.Timeout:
            self.logger.error(f"Viper scan timed out after {self.timeout} seconds")
            return {
                "error": "Scan timed out",
                "timeout": self.timeout,
                "targets": target_hosts
            }
        except Exception as e:
            self.logger.error(f"Error executing Viper scan: {str(e)}")
            return {
                "error": str(e),
                "targets": target_hosts
            }
    
    def _poll_scan_results(self, scan_id: str, max_attempts: int = 60, interval: int = 30) -> Dict[str, Any]:
        """Poll for scan results"""
        for attempt in range(max_attempts):
            try:
                response = self.session.get(
                    f"{self.base_url}/api/v1/scan/{scan_id}/results",
                    timeout=30
                )
                
                if response.status_code == 200:
                    results = response.json()
                    if results.get('status') == 'completed':
                        return results
                    elif results.get('status') == 'failed':
                        self.logger.error(f"Scan {scan_id} failed: {results.get('error', 'Unknown error')}")
                        return results
                elif response.status_code == 404:
                    self.logger.warning(f"Scan {scan_id} not found, might have expired")
                    return {"error": "Scan not found", "scan_id": scan_id}
                
            except Exception as e:
                self.logger.warning(f"Error polling scan results (attempt {attempt + 1}): {str(e)}")
            
            time.sleep(interval)
        
        # If we get here, the scan didn't complete in time
        self.logger.error(f"Scan {scan_id} did not complete within the expected time")
        return {
            "error": "Scan timeout",
            "scan_id": scan_id,
            "status": "timeout"
        }
    
    def _process_scan_results(self, results: Dict[str, Any], target_hosts: List[str]) -> Dict[str, Any]:
        """Process and enhance Viper scan results"""
        processed = {
            "raw_results": results,
            "summary": self._generate_summary(results),
            "threat_intel": self._enrich_with_threat_intel(results),
            "remediation_plan": self._generate_remediation_plan(results),
            "risk_assessment": self._assess_risk(results),
            "ai_recommendations": self._get_ai_recommendations(results),
            "targets": target_hosts,
            "timestamp": self._get_current_timestamp()
        }
        
        # Create security report
        self._create_security_report(processed)
        
        return processed
    
    def _generate_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary from Viper scan results"""
        findings = results.get('findings', [])
        
        summary = {
            "total_findings": len(findings),
            "by_severity": {
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0,
                "info": 0
            },
            "by_category": {},
            "affected_systems": set(),
            "executive_summary": []
        }
        
        for finding in findings:
            severity = finding.get('severity', 'info').lower()
            if severity in summary["by_severity"]:
                summary["by_severity"][severity] += 1
            
            category = finding.get('category', 'uncategorized')
            summary["by_category"][category] = summary["by_category"].get(category, 0) + 1
            
            # Extract affected systems
            if 'target' in finding:
                summary["affected_systems"].add(finding['target'])
        
        summary["affected_systems"] = list(summary["affected_systems"])
        
        # Generate executive summary based on critical findings
        critical_count = summary["by_severity"]["critical"]
        high_count = summary["by_severity"]["high"]
        
        if critical_count > 0:
            summary["executive_summary"].append(f"CRITICAL: {critical_count} critical vulnerabilities detected requiring immediate attention")
        if high_count > 0:
            summary["executive_summary"].append(f"HIGH: {high_count} high severity vulnerabilities detected")
        
        return summary
    
    def _enrich_with_threat_intel(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich results with threat intelligence"""
        # In a real implementation, this would integrate with threat intelligence feeds
        # For now, simulate threat intelligence enrichment
        enriched = {
            "indicators_of_compromise": [],
            "threat_actor_associations": [],
            "cve_correlations": [],
            "tactic_technique_mapping": {}  # MITRE ATT&CK mapping
        }
        
        # Extract CVEs from findings
        for finding in results.get('findings', []):
            if 'cve' in finding:
                enriched['cve_correlations'].append({
                    'cve_id': finding['cve'],
                    'finding': finding.get('title', ''),
                    'cvss_score': finding.get('cvss_score', 'N/A')
                })
        
        # Map findings to MITRE ATT&CK techniques
        for finding in results.get('findings', []):
            technique = self._map_to_mitre_technique(finding)
            if technique:
                enriched['tactic_technique_mapping'][finding.get('id', '')] = technique
        
        return enriched
    
    def _map_to_mitre_technique(self, finding: Dict[str, Any]) -> Dict[str, str]:
        """Map a finding to a MITRE ATT&CK technique"""
        finding_type = finding.get('type', '').lower()
        finding_description = finding.get('description', '').lower()
        
        # Map based on finding type and description
        if 'authentication' in finding_description or 'auth' in finding_description:
            return {'id': 'T1133', 'name': 'External Remote Services'}
        elif 'privilege' in finding_description or 'escalation' in finding_description:
            return {'id': 'T1068', 'name': 'Exploitation for Privilege Escalation'}
        elif 'persistence' in finding_description or 'backdoor' in finding_description:
            return {'id': 'T1505', 'name': 'Server Software Component'}
        elif 'execution' in finding_description or 'command' in finding_description:
            return {'id': 'T1106', 'name': 'Execution through API'}
        elif 'exfiltration' in finding_description or 'leak' in finding_description:
            return {'id': 'T1041', 'name': 'Exfiltration Over C2 Channel'}
        elif 'defense evasion' in finding_description or 'hide' in finding_description:
            return {'id': 'T1036', 'name': 'Masquerading'}
        elif 'discovery' in finding_description or 'enumerate' in finding_description:
            return {'id': 'T1082', 'name': 'System Information Discovery'}
        elif 'lateral' in finding_description or 'movement' in finding_description:
            return {'id': 'T1021', 'name': 'Remote Services'}
        else:
            return {}
    
    def _generate_remediation_plan(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate remediation recommendations"""
        findings = results.get('findings', [])
        remediation_plan = []
        
        for finding in findings:
            remediation = {
                "finding_id": finding.get('id', ''),
                "severity": finding.get('severity', 'info'),
                "title": finding.get('title', ''),
                "description": finding.get('description', ''),
                "remediation_steps": self._get_remediation_steps(finding),
                "priority": self._calculate_remediation_priority(finding),
                "estimated_time": self._estimate_remediation_time(finding),
                "resources_required": self._determine_resource_requirements(finding),
                "validation_steps": self._get_validation_steps(finding)
            }
            remediation_plan.append(remediation)
        
        return remediation_plan
    
    def _get_remediation_steps(self, finding: Dict[str, Any]) -> List[str]:
        """Get specific remediation steps for a finding"""
        finding_type = finding.get('type', 'generic').lower()
        
        # Standard remediation steps by finding type
        remediation_steps = {
            'port_exposure': [
                'Review firewall rules to restrict unnecessary port exposure',
                'Implement network segmentation to limit access',
                'Remove unnecessary services from exposed ports',
                'Apply access controls and authentication requirements'
            ],
            'service_vulnerability': [
                'Update affected service to patched version',
                'Apply vendor security patches',
                'Implement compensating controls if patch unavailable',
                'Review service configuration for security hardening'
            ],
            'authentication_bypass': [
                'Implement multi-factor authentication',
                'Review authentication mechanisms and controls',
                'Strengthen password policies',
                'Implement account lockout mechanisms'
            ],
            'misconfiguration': [
                'Review and correct configuration settings',
                'Implement configuration management and review processes',
                'Apply security best practices for the technology',
                'Regular configuration audits and monitoring'
            ],
            'api_insecurity': [
                'Implement proper authentication and authorization',
                'Apply rate limiting and request validation',
                'Use encryption for sensitive data transmission',
                'Document and review API security'
            ]
        }
        
        # Return standard steps for known types, generic for unknown types
        if finding_type in remediation_steps:
            return remediation_steps[finding_type]
        
        # Generic remediation steps for unknown finding types
        return [
            'Update to patched version if available',
            'Review vendor security advisories',
            'Implement additional security controls',
            'Monitor for exploitation attempts',
            'Validate fix in test environment before production'
        ]
    
    def _calculate_remediation_priority(self, finding: Dict[str, Any]) -> str:
        """Calculate remediation priority based on severity and impact"""
        severity = finding.get('severity', 'info').lower()
        cvss_score = finding.get('cvss_score', 0)
        
        # Priority based on severity and CVSS score
        if severity == 'critical' or cvss_score >= 9.0:
            return 'critical'
        elif severity == 'high' or cvss_score >= 7.0:
            return 'high'
        elif severity == 'medium' or cvss_score >= 4.0:
            return 'medium'
        else:
            return 'low'
    
    def _estimate_remediation_time(self, finding: Dict[str, Any]) -> str:
        """Estimate time required for remediation"""
        priority = self._calculate_remediation_priority(finding)
        
        time_estimates = {
            'critical': '1-3 days',
            'high': '3-7 days', 
            'medium': '1-2 weeks',
            'low': '2-4 weeks'
        }
        
        return time_estimates.get(priority, '2-4 weeks')
    
    def _determine_resource_requirements(self, finding: Dict[str, Any]) -> Dict[str, Any]:
        """Determine resources required for remediation"""
        priority = self._calculate_remediation_priority(finding)
        
        resource_requirements = {
            'critical': {
                'team_size': '3-5 engineers',
                'specialties': ['security', 'infrastructure', 'application'],
                'tools_needed': ['vulnerability_scanner', 'configuration_manager', 'ci_cd'],
                'reviewers': ['security_lead', 'architect'],
                'business_impact': 'Immediate service degradation possible'
            },
            'high': {
                'team_size': '2-3 engineers',
                'specialties': ['security', 'relevant_domain'],
                'tools_needed': ['vulnerability_scanner', 'configuration_manager'],
                'reviewers': ['tech_lead', 'security'],
                'business_impact': 'Potential service impact'
            },
            'medium': {
                'team_size': '1-2 engineers', 
                'specialties': ['relevant_domain'],
                'tools_needed': ['configuration_manager'],
                'reviewers': ['tech_lead'],
                'business_impact': 'Limited impact'
            },
            'low': {
                'team_size': '1 engineer',
                'specialties': ['general'],
                'tools_needed': [],
                'reviewers': ['peer_review'],
                'business_impact': 'Minimal impact'
            }
        }
        
        return resource_requirements.get(priority, resource_requirements['medium'])
    
    def _get_validation_steps(self, finding: Dict[str, Any]) -> List[str]:
        """Get steps to validate that remediation was successful"""
        return [
            'Re-scan affected system to verify vulnerability is fixed',
            'Test remediation in staging environment',
            'Monitor for any service impacts',
            'Document the remediation process for future reference'
        ]
    
    def _assess_risk(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall risk based on findings"""
        findings = results.get('findings', [])
        
        risk_metrics = {
            "risk_score": 0.0,
            "risk_level": "unknown",
            "business_impact": "unknown",
            "probability_of_exploit": 0.0,
            "exposure_surface": 0
        }
        
        if findings:
            # Calculate risk score based on finding count and severity
            severity_weights = {
                "critical": 10.0, 
                "high": 8.0, 
                "medium": 5.0, 
                "low": 2.0, 
                "info": 1.0
            }
            
            weighted_score = sum(
                severity_weights.get(f.get('severity', 'info').lower(), 1.0) 
                for f in findings
            )
            
            risk_metrics["risk_score"] = min(10.0, weighted_score / len(findings) if findings else 0)
            risk_metrics["exposure_surface"] = len(findings)
            
            # Determine risk level
            if risk_metrics["risk_score"] >= 8.0:
                risk_metrics["risk_level"] = "critical"
                risk_metrics["business_impact"] = "high"
                risk_metrics["probability_of_exploit"] = 0.9
            elif risk_metrics["risk_score"] >= 5.0:
                risk_metrics["risk_level"] = "high"
                risk_metrics["business_impact"] = "medium"
                risk_metrics["probability_of_exploit"] = 0.7
            elif risk_metrics["risk_score"] >= 3.0:
                risk_metrics["risk_level"] = "medium"
                risk_metrics["business_impact"] = "low_to_medium"
                risk_metrics["probability_of_exploit"] = 0.5
            else:
                risk_metrics["risk_level"] = "low"
                risk_metrics["business_impact"] = "low"
                risk_metrics["probability_of_exploit"] = 0.2
        
        return risk_metrics
    
    def _get_ai_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Get AI-powered security recommendations (simulated)"""
        # In a real implementation, this would interface with Viper's AI system
        # For now, generate recommendations based on findings
        
        recommendations = []
        
        # Check for specific critical patterns
        critical_findings = [f for f in results.get('findings', []) if f.get('severity') == 'critical']
        if critical_findings:
            recommendations.append("CRITICAL: Immediate remediation required for critical vulnerabilities.")
            recommendations.append("Implement compensating controls to reduce exposure until fixes are applied.")
        
        # Check for authentication issues
        auth_findings = [f for f in results.get('findings', []) if 'auth' in f.get('type', '').lower()]
        if auth_findings:
            recommendations.extend([
                "Implement multi-factor authentication where possible",
                "Review and strengthen authentication mechanisms",
                "Consider implementing Zero Trust principles"
            ])
        
        # General recommendations
        if results.get('summary', {}).get('by_severity', {}).get('high', 0) > 5:
            recommendations.append("Consider implementing a comprehensive vulnerability management program.")
        
        if not recommendations:
            recommendations.append("No critical issues found. Maintain regular security assessments.")
        
        recommendations.append("Schedule follow-up security scans to verify remediation effectiveness.")
        
        return recommendations
    
    def _create_security_report(self, processed_results: Dict[str, Any]):
        """Create security report from processed results"""
        output_dir = Path(self.config['reporting']['output_dir'])
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = processed_results['timestamp'].replace(':', '-')
        report_filename = output_dir / f"viper_security_report_{timestamp}.json"
        
        with open(report_filename, 'w') as f:
            json.dump(processed_results, f, indent=2)
        
        self.logger.info(f"Viper security report created: {report_filename}")
    
    def get_ai_security_recommendations(self, scan_results: Dict[str, Any]) -> Dict[str, Any]:
        """Get AI-powered security recommendations from Viper"""
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/ai-recommendations",
                json={'scan_results': scan_results},
                timeout=60  # Longer timeout for AI processing
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                self.logger.error(f"Viper AI recommendations failed: {response.status_code} - {response.text}")
                return {"error": f"API request failed with status {response.status_code}"}
                
        except Exception as e:
            self.logger.error(f"Error getting Viper AI recommendations: {str(e)}")
            return {"error": str(e)}
    
    def establish_secure_session(self, target_endpoint: str) -> str:
        """Establish secure session with Viper for ongoing security operations"""
        try:
            session_request = {
                'target': target_endpoint,
                'session_type': 'red_team',
                'duration': 'indefinite',
                'security_level': 'high',
                'ai_assistance': self.config['ai_assistance']
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/session",
                json=session_request,
                timeout=30
            )
            
            if response.status_code == 200:
                session_data = response.json()
                session_id = session_data.get('session_id', '')
                self.logger.info(f"Viper session established: {session_id}")
                return session_id
            else:
                self.logger.error(f"Failed to establish Viper session: {response.status_code}")
                return ''
                
        except Exception as e:
            self.logger.error(f"Error establishing Viper session: {str(e)}")
            return ''
    
    def monitor_threats_realtime(self, session_id: str) -> Dict[str, Any]:
        """Monitor threats in real-time using Viper's capabilities"""
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/session/{session_id}/threats",
                timeout=30
            )
            
            if response.status_code == 200:
                threats = response.json()
                self.logger.info(f"Real-time threat monitoring found {len(threats.get('active_threats', []))} active threats")
                return threats
            else:
                self.logger.error(f"Viper threat monitoring failed: {response.status_code}")
                return {"error": f"API request failed with status {response.status_code}"}
                
        except Exception as e:
            self.logger.error(f"Error monitoring threats with Viper: {str(e)}")
            return {"error": str(e)}
    
    def run_continuous_monitoring(self, target_hosts: List[str], 
                                interval_minutes: int = 60) -> None:
        """
        Perform continuous monitoring using Viper
        """
        import threading
        import time
        
        def monitoring_loop():
            session_id = self.establish_secure_session(target_hosts[0] if target_hosts else "default_target")
            if not session_id:
                self.logger.error("Failed to establish monitoring session")
                return
            
            try:
                while True:
                    threats = self.monitor_threats_realtime(session_id)
                    if 'error' not in threats:
                        active_threats = threats.get('active_threats', [])
                        if active_threats:
                            self.logger.warning(f"Active threats detected: {len(active_threats)}")
                            # Trigger alerting mechanism here
                        else:
                            self.logger.debug("No active threats detected")
                    else:
                        self.logger.error(f"Monitoring error: {threats['error']}")
                    
                    time.sleep(interval_minutes * 60)  # Convert minutes to seconds
            except KeyboardInterrupt:
                self.logger.info("Continuous monitoring stopped by user")
            except Exception as e:
                self.logger.error(f"Error in continuous monitoring: {str(e)}")
            finally:
                # Cleanup session
                try:
                    self.session.delete(f"{self.base_url}/api/v1/session/{session_id}")
                except:
                    pass  # Session cleanup is best effort
        
        # Run monitoring in a separate thread
        monitor_thread = threading.Thread(target=monitoring_loop, daemon=True)
        monitor_thread.start()
        
        return monitor_thread
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        return datetime.now().isoformat()


class InfrastructureSecurityOrchestrator:
    """
    Orchestrates infrastructure security testing using Viper and other tools
    """
    
    def __init__(self):
        self.viper = ViperIntegration()
        self.logger = logging.getLogger(__name__)
    
    def run_comprehensive_infrastructure_scan(self, target_hosts: List[str], 
                                            custom_modules: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Run comprehensive infrastructure security scan
        """
        self.logger.info(f"Starting comprehensive infrastructure scan for: {target_hosts}")
        
        # Run Viper scan
        viper_results = self.viper.run_infrastructure_security_scan(
            target_hosts, 
            custom_modules
        )
        
        # Process and consolidate results
        consolidated_results = self._consolidate_infrastructure_results(
            viper_results,
            target_hosts
        )
        
        # Generate comprehensive report
        report = self._generate_infrastructure_report(consolidated_results)
        
        # Save report
        self._save_infrastructure_report(report)
        
        self.logger.info(f"Comprehensive infrastructure scan completed for: {target_hosts}")
        return report
    
    def _consolidate_infrastructure_results(self, viper_results: Dict[str, Any], 
                                          target_hosts: List[str]) -> Dict[str, Any]:
        """Consolidate infrastructure scan results"""
        return {
            'target_hosts': target_hosts,
            'timestamp': self.viper._get_current_timestamp(),
            'viper_results': viper_results,
            'consolidated_metrics': self._calculate_infrastructure_metrics(viper_results),
            'overall_assessment': self._calculate_infrastructure_risk(viper_results),
            'priority_actions': self._determine_infrastructure_actions(viper_results)
        }
    
    def _calculate_infrastructure_metrics(self, viper_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate infrastructure security metrics"""
        metrics = {
            'total_findings': 0,
            'critical_vulnerabilities': 0,
            'high_vulnerabilities': 0,
            'exposed_services': 0,
            'configuration_issues': 0,
            'authentication_bypasses': 0
        }
        
        findings = viper_results.get('raw_results', {}).get('findings', [])
        
        for finding in findings:
            metrics['total_findings'] += 1
            severity = finding.get('severity', 'info')
            
            if severity == 'critical':
                metrics['critical_vulnerabilities'] += 1
            elif severity == 'high':
                metrics['high_vulnerabilities'] += 1
            
            # Count specific issue types
            finding_type = finding.get('type', 'unknown')
            if 'service' in finding_type:
                metrics['exposed_services'] += 1
            elif 'config' in finding_type or 'misconfig' in finding_type:
                metrics['configuration_issues'] += 1
            elif 'auth' in finding_type or 'bypass' in finding_type:
                metrics['authentication_bypasses'] += 1
        
        return metrics
    
    def _calculate_infrastructure_risk(self, viper_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall infrastructure risk"""
        risk_assessment = viper_results.get('risk_assessment', {})
        
        return {
            'score': risk_assessment.get('risk_score', 0.0),
            'level': risk_assessment.get('risk_level', 'unknown'),
            'business_impact': risk_assessment.get('business_impact', 'unknown'),
            'probability_of_exploit': risk_assessment.get('probability_of_exploit', 0.0),
            'exposure_surface': risk_assessment.get('exposure_surface', 0)
        }
    
    def _determine_infrastructure_actions(self, viper_results: Dict[str, Any]) -> List[str]:
        """Determine priority actions based on results"""
        actions = []
        
        # Get critical findings
        critical_findings = [
            f for f in viper_results.get('raw_results', {}).get('findings', []) 
            if f.get('severity') == 'critical'
        ]
        
        if critical_findings:
            actions.append(f"CRITICAL: Address {len(critical_findings)} critical vulnerabilities immediately")
        
        # Get high severity findings
        high_findings = [
            f for f in viper_results.get('raw_results', {}).get('findings', []) 
            if f.get('severity') == 'high'
        ]
        
        if high_findings:
            actions.append(f"HIGH: Address {len(high_findings)} high severity vulnerabilities")
        
        # Add specific recommendations
        recommendations = viper_results.get('ai_recommendations', [])
        actions.extend(recommendations[:3])  # Limit to top 3 recommendations
        
        if not actions:
            actions.append("No critical infrastructure vulnerabilities found. Continue regular monitoring.")
        
        actions.append("Schedule follow-up scan after implementing fixes.")
        
        return actions
    
    def _generate_infrastructure_report(self, consolidated_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive infrastructure security report"""
        return {
            'version': '1.0',
            'type': 'comprehensive_infrastructure_security_report',
            'metadata': {
                'timestamp': self.viper._get_current_timestamp(),
                'generator': 'Augur Omega Infrastructure Security Orchestrator',
                'targets': consolidated_results['target_hosts']
            },
            'executive_summary': {
                'overall_risk_level': consolidated_results['overall_assessment']['level'],
                'critical_vulnerabilities': consolidated_results['consolidated_metrics']['critical_vulnerabilities'],
                'high_vulnerabilities': consolidated_results['consolidated_metrics']['high_vulnerabilities'],
                'total_findings': consolidated_results['consolidated_metrics']['total_findings'],
                'infrastructure_summary': f"Scanned {len(consolidated_results['target_hosts'])} hosts. {consolidated_results['consolidated_metrics']['total_findings']} findings detected."
            },
            'detailed_findings': {
                'viper_findings': consolidated_results['viper_results']
            },
            'remediation': {
                'priority_actions': consolidated_results['priority_actions'],
                'recommended_timeline': 'Immediate for critical, 30 days for high, 90 days for medium'
            },
            'risk_assessment': consolidated_results['overall_assessment'],
            'metrics': consolidated_results['consolidated_metrics']
        }
    
    def _save_infrastructure_report(self, report: Dict[str, Any]):
        """Save infrastructure security report to file"""
        output_dir = Path("security/reports")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        filename = output_dir / f"infrastructure_security_report_{report['metadata']['timestamp'].replace(':', '-')}.json"
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.logger.info(f"Infrastructure security report saved: {filename}")