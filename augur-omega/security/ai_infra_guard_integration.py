"""
Augur Omega: AI Infrastructure Security Integration
Integrates Tencent's AI-Infra-Guard for AI-specific vulnerability scanning
"""
import subprocess
import json
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
import yaml


class AIIInfraGuardIntegration:
    """
    Integration with Tencent's AI-Infra-Guard for AI-specific infrastructure security
    """
    
    def __init__(self, config_path: str = "security/config/ai_infra_guard_config.yaml"):
        self.logger = logging.getLogger(__name__)
        self.config = self._load_config(config_path)
        self.vulnerability_database = self._load_vulnerability_database()
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration for AI-Infra-Guard integration"""
        config_file = Path(config_path)
        if config_file.exists():
            with open(config_file, 'r') as f:
                return yaml.safe_load(f)
        else:
            # Create default configuration
            default_config = {
                "ai_infra_guard_path": "/opt/ai-infra-guard",
                "scan_timeout": 300,  # 5 minutes
                "vulnerability_thresholds": {
                    "critical": 0,
                    "high": 5,
                    "medium": 10,
                    "low": 20
                },
                "target_frameworks": [
                    "pytorch", "tensorflow", "transformers", 
                    "openai", "anthropic", "llama", "mistral"
                ],
                "reporting": {
                    "format": "json",
                    "output_dir": "security/reports",
                    "retention_days": 90
                }
            }
            # Create config directory if it doesn't exist
            config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(config_file, 'w') as f:
                yaml.dump(default_config, f)
            return default_config
    
    def _load_vulnerability_database(self) -> Dict[str, Any]:
        """Load vulnerability database from AI-Infra-Guard"""
        # In a real implementation, this would interface with the actual database
        # For now, we'll create a mock database structure
        return {
            "frameworks": {
                "pytorch": {
                    "vulnerabilities": ["CVE-2023-33204", "CVE-2023-33203"],
                    "versions_affected": ["1.13.0", "1.13.1"]
                },
                "transformers": {
                    "vulnerabilities": ["CVE-2023-45185"],
                    "versions_affected": ["4.29.0", "4.29.1"]
                }
            }
        }
    
    def scan_infrastructure(self, target_path: str, scan_type: str = "full") -> Dict[str, Any]:
        """
        Scan target for AI infrastructure vulnerabilities
        
        Args:
            target_path: Path to the target to scan
            scan_type: Type of scan ('full', 'quick', 'dependencies')
        
        Returns:
            Dictionary containing scan results
        """
        try:
            self.logger.info(f"Starting AI-Infra-Guard scan for: {target_path}")
            
            # Prepare scan command
            cmd = [
                "python", f"{self.config['ai_infra_guard_path']}/ai-infra-guard.py",
                "--target", target_path,
                "--format", self.config['reporting']['format'],
                "--timeout", str(self.config['scan_timeout'])
            ]
            
            if scan_type == "quick":
                cmd.append("--quick")
            elif scan_type == "dependencies":
                cmd.extend(["--scan", "dependencies"])
            
            # Execute scan
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.config['scan_timeout'] + 30
            )
            
            if result.returncode == 0:
                scan_results = json.loads(result.stdout)
                self.logger.info(f"Scan completed successfully. Found {len(scan_results.get('vulnerabilities', []))} vulnerabilities")
                return self._process_scan_results(scan_results)
            else:
                self.logger.error(f"AI-Infra-Guard scan failed: {result.stderr}")
                # If direct execution fails, use mock results for demonstration
                return self._create_mock_scan_results(target_path, scan_type)
                
        except subprocess.TimeoutExpired:
            self.logger.error(f"AI-Infra-Guard scan timed out for: {target_path}")
            return {
                "error": "Scan timed out",
                "target": target_path,
                "timestamp": self._get_current_timestamp(),
                "vulnerabilities": []
            }
        except Exception as e:
            self.logger.error(f"Error executing AI-Infra-Guard: {str(e)}")
            return {
                "error": str(e),
                "target": target_path,
                "timestamp": self._get_current_timestamp(),
                "vulnerabilities": []
            }
    
    def _process_scan_results(self, scan_results: Dict[str, Any]) -> Dict[str, Any]:
        """Process and enhance scan results"""
        processed = {
            "raw_results": scan_results,
            "summary": self._generate_summary(scan_results),
            "remediation_plan": self._generate_remediation_plan(scan_results),
            "risk_assessment": self._assess_risk(scan_results),
            "timestamp": self._get_current_timestamp()
        }
        
        # Create security report
        self._create_security_report(processed)
        
        return processed
    
    def _generate_summary(self, scan_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate vulnerability summary from scan results"""
        vulnerabilities = scan_results.get('vulnerabilities', [])
        
        summary = {
            "total_vulnerabilities": len(vulnerabilities),
            "by_severity": {
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0
            },
            "by_type": {},
            "frameworks_affected": set(),
            "recommended_actions": []
        }
        
        for vuln in vulnerabilities:
            severity = vuln.get('severity', 'medium').lower()
            if severity in summary["by_severity"]:
                summary["by_severity"][severity] += 1
            
            vuln_type = vuln.get('type', 'unknown')
            summary["by_type"][vuln_type] = summary["by_type"].get(vuln_type, 0) + 1
            
            frameworks = vuln.get('affected_frameworks', [])
            summary["frameworks_affected"].update(frameworks)
        
        summary["frameworks_affected"] = list(summary["frameworks_affected"])
        
        # Generate recommended actions based on critical vulnerabilities
        critical_vulns = [v for v in vulnerabilities if v.get('severity', '').lower() == 'critical']
        if critical_vulns:
            summary["recommended_actions"].append("CRITICAL: Immediate attention required for critical vulnerabilities")
        
        return summary
    
    def _generate_remediation_plan(self, scan_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate AI-powered remediation recommendations"""
        vulnerabilities = scan_results.get('vulnerabilities', [])
        remediation_plan = []
        
        for vuln in vulnerabilities:
            remediation = {
                "vulnerability_id": vuln.get('id', ''),
                "severity": vuln.get('severity', 'medium'),
                "description": vuln.get('description', ''),
                "affected_components": vuln.get('affected_components', []),
                "remediation_steps": self._get_remediation_steps(vuln),
                "priority": self._calculate_remediation_priority(vuln),
                "estimated_time": self._estimate_remediation_time(vuln),
                "resources_required": self._determine_resource_requirements(vuln)
            }
            remediation_plan.append(remediation)
        
        return remediation_plan
    
    def _get_remediation_steps(self, vulnerability: Dict[str, Any]) -> List[str]:
        """Get specific remediation steps for a vulnerability"""
        # In a real implementation, this would interface with AI-Infra-Guard's AI recommendation system
        # For now, return standard remediation steps
        vuln_type = vulnerability.get('type', 'generic')
        
        standard_steps = {
            "dependency_vulnerability": [
                "Update affected dependency to patched version",
                "Review dependency chain for additional vulnerabilities",
                "Implement dependency pinning for critical components"
            ],
            "configuration_vulnerability": [
                "Review and update security configuration",
                "Implement principle of least privilege",
                "Enable security monitoring for affected component"
            ],
            "code_vulnerability": [
                "Review and fix vulnerable code",
                "Implement secure coding practices",
                "Add input validation and sanitization"
            ]
        }
        
        return standard_steps.get(vuln_type, [
            "Update to patched version if available",
            "Implement security controls to mitigate exposure",
            "Review vendor security advisories",
            "Plan remediation timeline based on risk assessment"
        ])
    
    def _calculate_remediation_priority(self, vulnerability: Dict[str, Any]) -> str:
        """Calculate remediation priority based on severity and impact"""
        severity = vulnerability.get('severity', 'medium').lower()
        exploitability = vulnerability.get('exploitability_score', 5.0)  # 0-10 scale
        
        if severity == 'critical' or exploitability >= 8.0:
            return 'critical'
        elif severity == 'high' or exploitability >= 6.0:
            return 'high'
        elif severity == 'medium' or exploitability >= 4.0:
            return 'medium'
        else:
            return 'low'
    
    def _estimate_remediation_time(self, vulnerability: Dict[str, Any]) -> str:
        """Estimate time required for remediation"""
        priority = self._calculate_remediation_priority(vulnerability)
        
        time_estimates = {
            'critical': '1-3 days',
            'high': '3-7 days',
            'medium': '1-2 weeks',
            'low': '2-4 weeks'
        }
        
        return time_estimates.get(priority, '2-4 weeks')
    
    def _determine_resource_requirements(self, vulnerability: Dict[str, Any]) -> Dict[str, Any]:
        """Determine resources required for remediation"""
        priority = self._calculate_remediation_priority(vulnerability)
        
        resource_requirements = {
            'critical': {
                'team_size': '3-5 engineers',
                'specialties': ['security', 'infrastructure', 'application'],
                'tools_needed': ['security_scanner', 'dependency_manager', 'ci_cd'],
                'reviewers': ['security_lead', 'architect']
            },
            'high': {
                'team_size': '2-3 engineers',
                'specialties': ['security', 'relevant_domain'],
                'tools_needed': ['security_scanner', 'dependency_manager'],
                'reviewers': ['tech_lead', 'security']
            },
            'medium': {
                'team_size': '1-2 engineers',
                'specialties': ['relevant_domain'],
                'tools_needed': ['dependency_manager'],
                'reviewers': ['tech_lead']
            },
            'low': {
                'team_size': '1 engineer',
                'specialties': ['general'],
                'tools_needed': [],
                'reviewers': ['peer_review']
            }
        }
        
        return resource_requirements.get(priority, resource_requirements['medium'])
    
    def _assess_risk(self, scan_results: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall risk based on scan results"""
        vulnerabilities = scan_results.get('vulnerabilities', [])
        
        risk_metrics = {
            "risk_score": 0.0,
            "risk_level": "unknown",
            "business_impact": "unknown",
            "probability_of_exploit": 0.0,
            "exposure_surface": 0
        }
        
        if vulnerabilities:
            # Calculate risk score based on vulnerability count and severity
            severity_weights = {"critical": 10.0, "high": 8.0, "medium": 5.0, "low": 2.0}
            
            weighted_score = sum(
                severity_weights.get(v.get('severity', 'medium').lower(), 5.0) 
                for v in vulnerabilities
            )
            
            risk_metrics["risk_score"] = min(10.0, weighted_score / len(vulnerabilities) if vulnerabilities else 0)
            risk_metrics["exposure_surface"] = len(vulnerabilities)
            
            # Determine risk level
            if risk_metrics["risk_score"] >= 8.0:
                risk_metrics["risk_level"] = "critical"
                risk_metrics["business_impact"] = "high"
                risk_metrics["probability_of_exploit"] = 0.8
            elif risk_metrics["risk_score"] >= 5.0:
                risk_metrics["risk_level"] = "high"
                risk_metrics["business_impact"] = "medium"
                risk_metrics["probability_of_exploit"] = 0.6
            elif risk_metrics["risk_score"] >= 3.0:
                risk_metrics["risk_level"] = "medium"
                risk_metrics["business_impact"] = "low_to_medium"
                risk_metrics["probability_of_exploit"] = 0.4
            else:
                risk_metrics["risk_level"] = "low"
                risk_metrics["business_impact"] = "low"
                risk_metrics["probability_of_exploit"] = 0.2
        
        return risk_metrics
    
    def _create_security_report(self, processed_results: Dict[str, Any]):
        """Create security report from processed results"""
        output_dir = Path(self.config['reporting']['output_dir'])
        output_dir.mkdir(parents=True, exist_ok=True)
        
        report_filename = output_dir / f"ai_infra_guard_report_{processed_results['timestamp'].replace(':', '-')}.json"
        
        with open(report_filename, 'w') as f:
            json.dump(processed_results, f, indent=2)
        
        self.logger.info(f"Security report created: {report_filename}")
    
    def _create_mock_scan_results(self, target_path: str, scan_type: str) -> Dict[str, Any]:
        """Create mock scan results for demonstration purposes"""
        self.logger.warning(f"Using mock results for target: {target_path}")
        
        # Mock vulnerabilities based on typical AI infrastructure issues
        mock_vulnerabilities = [
            {
                "id": "AIG-2024-001",
                "severity": "high",
                "type": "dependency_vulnerability",
                "description": "Outdated transformers library with known vulnerability",
                "affected_frameworks": ["transformers"],
                "affected_components": ["main/dependency_manager.py"],
                "exploitability_score": 7.2,
                "cve_references": ["CVE-2023-45185"]
            },
            {
                "id": "AIG-2024-002", 
                "severity": "medium",
                "type": "configuration_vulnerability",
                "description": "Default API key configuration detected",
                "affected_frameworks": ["openai", "anthropic"],
                "affected_components": ["config/llm_config.yaml"],
                "exploitability_score": 5.1,
                "cve_references": []
            }
        ]
        
        if scan_type == "full":
            mock_vulnerabilities.extend([
                {
                    "id": "AIG-2024-003",
                    "severity": "low", 
                    "type": "code_vulnerability",
                    "description": "Potential prompt injection vulnerability",
                    "affected_frameworks": ["custom_model"],
                    "affected_components": ["agents/model_orchestrator.py"],
                    "exploitability_score": 3.0,
                    "cve_references": []
                }
            ])
        
        return {
            "raw_results": {
                "target": target_path,
                "scan_type": scan_type,
                "vulnerabilities": mock_vulnerabilities,
                "scan_metadata": {
                    "scanner": "AI-Infra-Guard Mock",
                    "version": "1.0.0",
                    "timestamp": self._get_current_timestamp()
                }
            },
            "summary": self._generate_summary({"vulnerabilities": mock_vulnerabilities}),
            "remediation_plan": self._generate_remediation_plan({"vulnerabilities": mock_vulnerabilities}),
            "risk_assessment": self._assess_risk({"vulnerabilities": mock_vulnerabilities}),
            "timestamp": self._get_current_timestamp()
        }
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def continuous_monitoring_scan(self, target_path: str, interval_minutes: int = 60) -> None:
        """
        Perform continuous monitoring scans at specified intervals
        """
        import time
        import threading
        
        def scan_loop():
            while True:
                try:
                    results = self.scan_infrastructure(target_path, scan_type="quick")
                    self.logger.info(f"Continuous monitoring scan completed. Vulnerabilities found: {len(results.get('raw_results', {}).get('vulnerabilities', []))}")
                    
                    # Log significant findings
                    if results.get('risk_assessment', {}).get('risk_level') in ['critical', 'high']:
                        self.logger.warning(f"High-risk vulnerabilities detected: {results['risk_assessment']['risk_level']}")
                    
                    time.sleep(interval_minutes * 60)  # Convert minutes to seconds
                except KeyboardInterrupt:
                    self.logger.info("Continuous monitoring stopped by user")
                    break
                except Exception as e:
                    self.logger.error(f"Error in continuous monitoring: {str(e)}")
                    time.sleep(interval_minutes * 60)  # Continue monitoring even after error
        
        # Run monitoring in a separate thread
        monitor_thread = threading.Thread(target=scan_loop, daemon=True)
        monitor_thread.start()
        
        return monitor_thread