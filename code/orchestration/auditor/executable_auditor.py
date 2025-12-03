"""
Augur Omega: Executable Auditor Integration
Real-time build validation, health monitoring, and audit trail management
"""
import json
import os
import sys
import time
import logging
import threading
import subprocess
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import xml.etree.ElementTree as ET
import re
import configparser
from collections import defaultdict, deque

# Setup logging
logger = logging.getLogger(__name__)

class AuditStatus(Enum):
    """Audit status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    WARNING = "warning"
    FAILED = "failed"
    ERROR = "error"

class Platform(Enum):
    """Supported platforms for audit"""
    WINDOWS = "windows"
    MACOS = "macos"
    LINUX = "linux"
    ANDROID = "android"
    IOS = "ios"
    TAURI = "tauri"
    ELECTRON = "electron"
    CLI_TUI = "cli_tui"

class AuditSeverity(Enum):
    """Audit issue severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

@dataclass
class AuditCheck:
    """Individual audit check definition"""
    check_id: str
    name: str
    description: str
    severity: AuditSeverity
    platform: Platform
    check_function: str
    enabled: bool = True
    timeout_seconds: int = 30

@dataclass
class AuditResult:
    """Audit check result"""
    check_id: str
    status: AuditStatus
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    execution_time: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class AuditReport:
    """Complete audit report"""
    report_id: str
    build_id: str
    platform: Platform
    status: AuditStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    results: List[AuditResult] = field(default_factory=list)
    overall_score: float = 0.0
    artifacts_validated: List[str] = field(default_factory=list)
    security_scan_results: Dict[str, Any] = field(default_factory=dict)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)

class BuildArtifactAnalyzer:
    """Analyzes build artifacts for validation"""
    
    def __init__(self):
        self.artifact_validators = self._initialize_validators()
        
    def _initialize_validators(self) -> Dict[Platform, Dict[str, callable]]:
        """Initialize validators for each platform"""
        validators = {}
        
        # Windows validators
        validators[Platform.WINDOWS] = {
            "executable": self._validate_windows_executable,
            "installer": self._validate_windows_installer,
            "manifest": self._validate_windows_manifest
        }
        
        # macOS validators
        validators[Platform.MACOS] = {
            "app_bundle": self._validate_macos_app_bundle,
            "info_plist": self._validate_macos_info_plist,
            "signature": self._validate_macos_signature
        }
        
        # Linux validators
        validators[Platform.LINUX] = {
            "package": self._validate_linux_package,
            "desktop_entry": self._validate_linux_desktop_entry,
            "permissions": self._validate_linux_permissions
        }
        
        # Android validators
        validators[Platform.ANDROID] = {
            "manifest": self._validate_android_manifest,
            "gradle": self._validate_android_gradle,
            "apk_structure": self._validate_android_apk_structure
        }
        
        # iOS validators
        validators[Platform.IOS] = {
            "info_plist": self._validate_ios_info_plist,
            "swift_sources": self._validate_ios_swift_sources,
            "bundle_structure": self._validate_ios_bundle
        }
        
        # Tauri validators
        validators[Platform.TAURI] = {
            "cargo_toml": self._validate_tauri_cargo_toml,
            "tauri_config": self._validate_tauri_config,
            "rust_sources": self._validate_tauri_rust
        }
        
        # Electron validators
        validators[Platform.ELECTRON] = {
            "package_json": self._validate_electron_package_json,
            "main_js": self._validate_electron_main_js,
            "electron_structure": self._validate_electron_structure
        }
        
        # CLI/TUI validators
        validators[Platform.CLI_TUI] = {
            "python_scripts": self._validate_python_cli,
            "requirements": self._validate_python_requirements
        }
        
        return validators
    
    def validate_artifact(self, artifact_path: str, platform: Platform, artifact_type: str) -> AuditResult:
        """Validate a specific artifact"""
        start_time = time.time()
        
        try:
            validator = self.artifact_validators.get(platform, {}).get(artifact_type)
            
            if not validator:
                return AuditResult(
                    check_id=f"{platform.value}_{artifact_type}",
                    status=AuditStatus.ERROR,
                    message=f"No validator found for {platform.value} {artifact_type}"
                )
            
            result = validator(artifact_path)
            execution_time = time.time() - start_time
            
            result.execution_time = execution_time
            return result
            
        except Exception as e:
            logger.error(f"Error validating {artifact_type} for {platform.value}: {str(e)}")
            return AuditResult(
                check_id=f"{platform.value}_{artifact_type}",
                status=AuditStatus.ERROR,
                message=f"Validation error: {str(e)}"
            )
    
    def _validate_windows_executable(self, exe_path: str) -> AuditResult:
        """Validate Windows executable"""
        exe_path = Path(exe_path)
        
        if not exe_path.exists():
            return AuditResult(
                check_id="windows_executable",
                status=AuditStatus.FAILED,
                message="Executable file not found",
                details={"path": exe_path}
            )
        
        # Check file size
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        if size_mb > 500:  # Very large executable
            return AuditResult(
                check_id="windows_executable",
                status=AuditStatus.WARNING,
                message=f"Large executable size: {size_mb:.1f}MB",
                details={"size_mb": size_mb}
            )
        
        # Check for basic PE structure (simplified)
        try:
            with open(exe_path, 'rb') as f:
                header = f.read(64)
                if not header.startswith(b'MZ'):
                    return AuditResult(
                        check_id="windows_executable",
                        status=AuditStatus.FAILED,
                        message="Invalid PE executable format"
                    )
        except Exception as e:
            return AuditResult(
                check_id="windows_executable",
                status=AuditStatus.ERROR,
                message=f"Error reading executable: {str(e)}"
            )
        
        return AuditResult(
            check_id="windows_executable",
            status=AuditStatus.PASSED,
            message="Windows executable validation passed"
        )
    
    def _validate_windows_installer(self, installer_path: str) -> AuditResult:
        """Validate Windows installer"""
        installer_path = Path(installer_path)
        
        if not installer_path.exists():
            return AuditResult(
                check_id="windows_installer",
                status=AuditStatus.FAILED,
                message="Installer file not found"
            )
        
        # Check for NSIS script structure
        try:
            with open(installer_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            # Check for basic NSIS elements
            nsis_keywords = ['!define', 'Section', 'InstallDir', 'OutFile']
            found_keywords = [kw for kw in nsis_keywords if kw in content]
            
            if len(found_keywords) < 2:
                return AuditResult(
                    check_id="windows_installer",
                    status=AuditStatus.WARNING,
                    message="Installer may be incomplete - missing NSIS keywords",
                    details={"found_keywords": found_keywords}
                )
                
        except Exception as e:
            return AuditResult(
                check_id="windows_installer",
                status=AuditStatus.ERROR,
                message=f"Error reading installer: {str(e)}"
            )
        
        return AuditResult(
            check_id="windows_installer",
            status=AuditStatus.PASSED,
            message="Windows installer validation passed"
        )
    
    def _validate_windows_manifest(self, manifest_path: str) -> AuditResult:
        """Validate Windows manifest"""
        manifest_path = Path(manifest_path)
        
        if not manifest_path.exists():
            return AuditResult(
                check_id="windows_manifest",
                status=AuditStatus.WARNING,
                message="Manifest file not found"
            )
        
        try:
            tree = ET.parse(manifest_path)
            root = tree.getroot()
            
            # Check for required elements
            required_elements = [
                "{urn:schemas-microsoft-com:asm.v1}assemblyIdentity",
                "{urn:schemas-microsoft-com:asm.v1}application"
            ]
            
            missing_elements = []
            for elem in required_elements:
                if root.find(elem) is None:
                    missing_elements.append(elem)
            
            if missing_elements:
                return AuditResult(
                    check_id="windows_manifest",
                    status=AuditStatus.WARNING,
                    message="Manifest missing required elements",
                    details={"missing_elements": missing_elements}
                )
                
        except ET.ParseError as e:
            return AuditResult(
                check_id="windows_manifest",
                status=AuditStatus.FAILED,
                message=f"Invalid XML in manifest: {str(e)}"
            )
        except Exception as e:
            return AuditResult(
                check_id="windows_manifest",
                status=AuditStatus.ERROR,
                message=f"Error parsing manifest: {str(e)}"
            )
        
        return AuditResult(
            check_id="windows_manifest",
            status=AuditStatus.PASSED,
            message="Windows manifest validation passed"
        )
    
    def _validate_macos_app_bundle(self, app_path: str) -> AuditResult:
        """Validate macOS application bundle"""
        app_path = Path(app_path)
        
        if not app_path.exists():
            return AuditResult(
                check_id="macos_app_bundle",
                status=AuditStatus.FAILED,
                message="App bundle not found"
            )
        
        # Check bundle structure
        required_structure = [
            "Contents/Info.plist",
            "Contents/MacOS",
            "Contents/Resources"
        ]
        
        missing_structure = []
        for part in required_structure:
            if not (app_path / part).exists():
                missing_structure.append(part)
        
        if missing_structure:
            return AuditResult(
                check_id="macos_app_bundle",
                status=AuditStatus.FAILED,
                message="App bundle structure incomplete",
                details={"missing_structure": missing_structure}
            )
        
        return AuditResult(
            check_id="macos_app_bundle",
            status=AuditStatus.PASSED,
            message="macOS app bundle structure valid"
        )
    
    def _validate_macos_info_plist(self, plist_path: str) -> AuditResult:
        """Validate macOS Info.plist"""
        plist_path = Path(plist_path)
        
        if not plist_path.exists():
            return AuditResult(
                check_id="macos_info_plist",
                status=AuditStatus.FAILED,
                message="Info.plist not found"
            )
        
        try:
            # Read and check basic Plist structure
            with open(plist_path, 'rb') as f:
                content = f.read()
            
            # Check for required keys
            required_keys = [
                b'CFBundleIdentifier',
                b'CFBundleName',
                b'CFBundleVersion'
            ]
            
            missing_keys = []
            for key in required_keys:
                if key not in content:
                    missing_keys.append(key.decode('utf-8', errors='ignore'))
            
            if missing_keys:
                return AuditResult(
                    check_id="macos_info_plist",
                    status=AuditStatus.WARNING,
                    message="Info.plist missing required keys",
                    details={"missing_keys": missing_keys}
                )
                
        except Exception as e:
            return AuditResult(
                check_id="macos_info_plist",
                status=AuditStatus.ERROR,
                message=f"Error reading Info.plist: {str(e)}"
            )
        
        return AuditResult(
            check_id="macos_info_plist",
            status=AuditStatus.PASSED,
            message="macOS Info.plist validation passed"
        )
    
    def _validate_macos_signature(self, app_path: str) -> AuditResult:
        """Validate macOS code signature (simplified)"""
        app_path = Path(app_path)
        
        # Check for _CodeSignature directory
        signature_dir = app_path / "Contents" / "_CodeSignature"
        if not signature_dir.exists():
            return AuditResult(
                check_id="macos_signature",
                status=AuditStatus.WARNING,
                message="Application not signed"
            )
        
        return AuditResult(
            check_id="macos_signature",
            status=AuditStatus.PASSED,
            message="Code signature present"
        )
    
    def _validate_linux_package(self, package_path: str) -> AuditResult:
        """Validate Linux package"""
        package_path = Path(package_path)
        
        if not package_path.exists():
            return AuditResult(
                check_id="linux_package",
                status=AuditStatus.FAILED,
                message="Package file not found"
            )
        
        # Check package type
        if package_path.suffix == '.deb':
            return self._validate_deb_package(package_path)
        elif package_path.suffix == '.rpm':
            return self._validate_rpm_package(package_path)
        else:
            return AuditResult(
                check_id="linux_package",
                status=AuditStatus.WARNING,
                message="Unknown package format"
            )
    
    def _validate_deb_package(self, deb_path: Path) -> AuditResult:
        """Validate Debian package"""
        try:
            # Use dpkg-deb to inspect package
            result = subprocess.run(
                ['dpkg-deb', '-I', str(deb_path)],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                return AuditResult(
                    check_id="debian_package",
                    status=AuditStatus.FAILED,
                    message="Invalid Debian package",
                    details={"error": result.stderr}
                )
            
            # Check for required control files
            control_output = result.stdout
            required_fields = ['Package:', 'Version:', 'Description:']
            
            missing_fields = []
            for field in required_fields:
                if field not in control_output:
                    missing_fields.append(field)
            
            if missing_fields:
                return AuditResult(
                    check_id="debian_package",
                    status=AuditStatus.WARNING,
                    message="Package missing required fields",
                    details={"missing_fields": missing_fields}
                )
                
        except Exception as e:
            return AuditResult(
                check_id="debian_package",
                status=AuditStatus.ERROR,
                message=f"Error validating Debian package: {str(e)}"
            )
        
        return AuditResult(
            check_id="debian_package",
            status=AuditStatus.PASSED,
            message="Debian package validation passed"
        )
    
    def _validate_rpm_package(self, rpm_path: Path) -> AuditResult:
        """Validate RPM package"""
        try:
            # Use rpm to inspect package
            result = subprocess.run(
                ['rpm', '-qp', '--queryformat', '%{NAME} %{VERSION}', str(rpm_path)],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                return AuditResult(
                    check_id="rpm_package",
                    status=AuditStatus.FAILED,
                    message="Invalid RPM package"
                )
            
            # Basic validation passed
            package_info = result.stdout.strip()
            if not package_info:
                return AuditResult(
                    check_id="rpm_package",
                    status=AuditStatus.WARNING,
                    message="Package information incomplete"
                )
                
        except Exception as e:
            return AuditResult(
                check_id="rpm_package",
                status=AuditStatus.ERROR,
                message=f"Error validating RPM package: {str(e)}"
            )
        
        return AuditResult(
            check_id="rpm_package",
            status=AuditStatus.PASSED,
            message="RPM package validation passed"
        )
    
    def _validate_linux_desktop_entry(self, desktop_path: str) -> AuditResult:
        """Validate Linux .desktop file"""
        desktop_path = Path(desktop_path)
        
        if not desktop_path.exists():
            return AuditResult(
                check_id="linux_desktop_entry",
                status=AuditStatus.WARNING,
                message="Desktop entry file not found"
            )
        
        try:
            config = configparser.ConfigParser()
            config.read(desktop_path)
            
            # Check for Desktop Entry section
            if not config.has_section('Desktop Entry'):
                return AuditResult(
                    check_id="linux_desktop_entry",
                    status=AuditStatus.FAILED,
                    message="Missing Desktop Entry section"
                )
            
            # Check for required keys
            required_keys = ['Name', 'Exec', 'Type']
            missing_keys = []
            
            for key in required_keys:
                if not config.has_option('Desktop Entry', key):
                    missing_keys.append(key)
            
            if missing_keys:
                return AuditResult(
                    check_id="linux_desktop_entry",
                    status=AuditStatus.WARNING,
                    message="Desktop entry missing required keys",
                    details={"missing_keys": missing_keys}
                )
                
        except Exception as e:
            return AuditResult(
                check_id="linux_desktop_entry",
                status=AuditStatus.ERROR,
                message=f"Error parsing desktop entry: {str(e)}"
            )
        
        return AuditResult(
            check_id="linux_desktop_entry",
            status=AuditStatus.PASSED,
            message="Linux desktop entry validation passed"
        )
    
    def _validate_linux_permissions(self, artifact_path: str) -> AuditResult:
        """Validate Linux file permissions"""
        artifact_path = Path(artifact_path)
        
        if not artifact_path.exists():
            return AuditResult(
                check_id="linux_permissions",
                status=AuditStatus.FAILED,
                message="Artifact not found"
            )
        
        try:
            stat_info = artifact_path.stat()
            permissions = oct(stat_info.st_mode)[-3:]
            
            # Check if executable has appropriate permissions
            if artifact_path.is_file():
                if not any(p in permissions for p in ['5', '7']):  # r-x or rwx
                    return AuditResult(
                        check_id="linux_permissions",
                        status=AuditStatus.WARNING,
                        message="File may not have execute permissions",
                        details={"permissions": permissions}
                    )
            
        except Exception as e:
            return AuditResult(
                check_id="linux_permissions",
                status=AuditStatus.ERROR,
                message=f"Error checking permissions: {str(e)}"
            )
        
        return AuditResult(
            check_id="linux_permissions",
            status=AuditStatus.PASSED,
            message="Linux permissions validation passed"
        )
    
    def _validate_android_manifest(self, manifest_path: str) -> AuditResult:
        """Validate Android manifest"""
        manifest_path = Path(manifest_path)
        
        if not manifest_path.exists():
            return AuditResult(
                check_id="android_manifest",
                status=AuditStatus.FAILED,
                message="AndroidManifest.xml not found"
            )
        
        try:
            tree = ET.parse(manifest_path)
            root = tree.getroot()
            
            # Check for required elements
            required_elements = ['application', 'activity']
            
            missing_elements = []
            for elem in required_elements:
                if root.find(elem) is None:
                    missing_elements.append(elem)
            
            # Check for permissions
            permissions = root.findall('.//uses-permission')
            if not permissions:
                logger.warning("No permissions declared in Android manifest")
            
            if missing_elements:
                return AuditResult(
                    check_id="android_manifest",
                    status=AuditStatus.WARNING,
                    message="Android manifest missing elements",
                    details={"missing_elements": missing_elements}
                )
                
        except ET.ParseError as e:
            return AuditResult(
                check_id="android_manifest",
                status=AuditStatus.FAILED,
                message=f"Invalid XML in Android manifest: {str(e)}"
            )
        except Exception as e:
            return AuditResult(
                check_id="android_manifest",
                status=AuditStatus.ERROR,
                message=f"Error parsing Android manifest: {str(e)}"
            )
        
        return AuditResult(
            check_id="android_manifest",
            status=AuditStatus.PASSED,
            message="Android manifest validation passed"
        )
    
    def _validate_android_gradle(self, gradle_path: str) -> AuditResult:
        """Validate Android Gradle configuration"""
        gradle_path = Path(gradle_path)
        
        if not gradle_path.exists():
            return AuditResult(
                check_id="android_gradle",
                status=AuditStatus.WARNING,
                message="Gradle configuration not found"
            )
        
        try:
            with open(gradle_path, 'r') as f:
                content = f.read()
            
            # Check for basic Gradle structure
            android_keywords = ['android', 'dependencies', 'compileSdk']
            found_keywords = [kw for kw in android_keywords if kw in content]
            
            if len(found_keywords) < 2:
                return AuditResult(
                    check_id="android_gradle",
                    status=AuditStatus.WARNING,
                    message="Gradle configuration may be incomplete"
                )
                
        except Exception as e:
            return AuditResult(
                check_id="android_gradle",
                status=AuditStatus.ERROR,
                message=f"Error reading Gradle file: {str(e)}"
            )
        
        return AuditResult(
            check_id="android_gradle",
            status=AuditStatus.PASSED,
            message="Android Gradle validation passed"
        )
    
    def _validate_android_apk_structure(self, apk_path: str) -> AuditResult:
        """Validate APK structure (simplified)"""
        apk_path = Path(apk_path)
        
        if not apk_path.exists():
            return AuditResult(
                check_id="android_apk_structure",
                status=AuditStatus.FAILED,
                message="APK file not found"
            )
        
        # Check APK file size
        size_mb = apk_path.stat().st_size / (1024 * 1024)
        if size_mb > 100:  # Very large APK
            return AuditResult(
                check_id="android_apk_structure",
                status=AuditStatus.WARNING,
                message=f"Large APK size: {size_mb:.1f}MB"
            )
        
        return AuditResult(
            check_id="android_apk_structure",
            status=AuditStatus.PASSED,
            message="Android APK structure valid"
        )
    
    def _validate_ios_info_plist(self, plist_path: str) -> AuditResult:
        """Validate iOS Info.plist"""
        # Similar to macOS Info.plist validation
        return self._validate_macos_info_plist(plist_path)
    
    def _validate_ios_swift_sources(self, source_path: str) -> AuditResult:
        """Validate iOS Swift sources"""
        source_path = Path(source_path)
        
        if not source_path.exists():
            return AuditResult(
                check_id="ios_swift_sources",
                status=AuditStatus.WARNING,
                message="Swift source directory not found"
            )
        
        # Check for .swift files
        swift_files = list(source_path.glob("*.swift"))
        if not swift_files:
            return AuditResult(
                check_id="ios_swift_sources",
                status=AuditStatus.WARNING,
                message="No Swift source files found"
            )
        
        return AuditResult(
            check_id="ios_swift_sources",
            status=AuditStatus.PASSED,
            message=f"Found {len(swift_files)} Swift source files"
        )
    
    def _validate_ios_bundle(self, bundle_path: str) -> AuditResult:
        """Validate iOS bundle structure"""
        bundle_path = Path(bundle_path)
        
        # Check bundle structure similar to macOS
        required_structure = [
            "Info.plist",
            "SwiftApp.app"
        ]
        
        for part in required_structure:
            if not (bundle_path / part).exists():
                return AuditResult(
                    check_id="ios_bundle_structure",
                    status=AuditStatus.WARNING,
                    message=f"Missing iOS bundle component: {part}"
                )
        
        return AuditResult(
            check_id="ios_bundle_structure",
            status=AuditStatus.PASSED,
            message="iOS bundle structure valid"
        )
    
    def _validate_tauri_cargo_toml(self, cargo_path: str) -> AuditResult:
        """Validate Tauri Cargo.toml"""
        cargo_path = Path(cargo_path)
        
        if not cargo_path.exists():
            return AuditResult(
                check_id="tauri_cargo_toml",
                status=AuditStatus.FAILED,
                message="Cargo.toml not found"
            )
        
        try:
            config = configparser.ConfigParser()
            config.read(cargo_path)
            
            # Check for required sections
            required_sections = ['package', 'dependencies']
            missing_sections = []
            
            for section in required_sections:
                if not config.has_section(section):
                    missing_sections.append(section)
            
            if missing_sections:
                return AuditResult(
                    check_id="tauri_cargo_toml",
                    status=AuditStatus.WARNING,
                    message="Cargo.toml missing sections",
                    details={"missing_sections": missing_sections}
                )
                
        except Exception as e:
            return AuditResult(
                check_id="tauri_cargo_toml",
                status=AuditStatus.ERROR,
                message=f"Error parsing Cargo.toml: {str(e)}"
            )
        
        return AuditResult(
            check_id="tauri_cargo_toml",
            status=AuditStatus.PASSED,
            message="Tauri Cargo.toml validation passed"
        )
    
    def _validate_tauri_config(self, config_path: str) -> AuditResult:
        """Validate Tauri configuration"""
        config_path = Path(config_path)
        
        if not config_path.exists():
            return AuditResult(
                check_id="tauri_config",
                status=AuditStatus.FAILED,
                message="tauri.conf.json not found"
            )
        
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Check for required fields
            required_fields = ['build', 'tauri']
            missing_fields = []
            
            for field in required_fields:
                if field not in config:
                    missing_fields.append(field)
            
            if missing_fields:
                return AuditResult(
                    check_id="tauri_config",
                    status=AuditStatus.WARNING,
                    message="Tauri config missing fields",
                    details={"missing_fields": missing_fields}
                )
                
        except json.JSONDecodeError as e:
            return AuditResult(
                check_id="tauri_config",
                status=AuditStatus.FAILED,
                message=f"Invalid JSON in tauri.conf.json: {str(e)}"
            )
        except Exception as e:
            return AuditResult(
                check_id="tauri_config",
                status=AuditStatus.ERROR,
                message=f"Error reading Tauri config: {str(e)}"
            )
        
        return AuditResult(
            check_id="tauri_config",
            status=AuditStatus.PASSED,
            message="Tauri configuration validation passed"
        )
    
    def _validate_tauri_rust(self, rust_path: str) -> AuditResult:
        """Validate Tauri Rust sources"""
        rust_path = Path(rust_path)
        
        if not rust_path.exists():
            return AuditResult(
                check_id="tauri_rust_sources",
                status=AuditStatus.FAILED,
                message="Rust source directory not found"
            )
        
        # Check for main.rs
        main_rs = rust_path / "main.rs"
        if not main_rs.exists():
            return AuditResult(
                check_id="tauri_rust_sources",
                status=AuditStatus.WARNING,
                message="main.rs not found"
            )
        
        # Check for Tauri imports
        try:
            with open(main_rs, 'r') as f:
                content = f.read()
            
            tauri_imports = ['tauri::generate_handler', '#[tauri::command]']
            found_imports = [imp for imp in tauri_imports if imp in content]
            
            if not found_imports:
                return AuditResult(
                    check_id="tauri_rust_sources",
                    status=AuditStatus.WARNING,
                    message="No Tauri-specific imports found"
                )
                
        except Exception as e:
            return AuditResult(
                check_id="tauri_rust_sources",
                status=AuditStatus.ERROR,
                message=f"Error reading main.rs: {str(e)}"
            )
        
        return AuditResult(
            check_id="tauri_rust_sources",
            status=AuditStatus.PASSED,
            message="Tauri Rust sources validation passed"
        )
    
    def _validate_electron_package_json(self, package_path: str) -> AuditResult:
        """Validate Electron package.json"""
        package_path = Path(package_path)
        
        if not package_path.exists():
            return AuditResult(
                check_id="electron_package_json",
                status=AuditStatus.FAILED,
                message="package.json not found"
            )
        
        try:
            with open(package_path, 'r') as f:
                package_data = json.load(f)
            
            # Check for required fields
            required_fields = ['name', 'version', 'main', 'scripts']
            missing_fields = []
            
            for field in required_fields:
                if field not in package_data:
                    missing_fields.append(field)
            
            # Check for Electron-specific scripts
            electron_scripts = ['start', 'build', 'dist']
            found_scripts = [script for script in electron_scripts if script in package_data.get('scripts', {})]
            
            if len(found_scripts) < 2:
                return AuditResult(
                    check_id="electron_package_json",
                    status=AuditStatus.WARNING,
                    message="Missing Electron-specific scripts",
                    details={"found_scripts": found_scripts}
                )
            
            if missing_fields:
                return AuditResult(
                    check_id="electron_package_json",
                    status=AuditStatus.WARNING,
                    message="package.json missing required fields",
                    details={"missing_fields": missing_fields}
                )
                
        except json.JSONDecodeError as e:
            return AuditResult(
                check_id="electron_package_json",
                status=AuditStatus.FAILED,
                message=f"Invalid JSON in package.json: {str(e)}"
            )
        except Exception as e:
            return AuditResult(
                check_id="electron_package_json",
                status=AuditStatus.ERROR,
                message=f"Error reading package.json: {str(e)}"
            )
        
        return AuditResult(
            check_id="electron_package_json",
            status=AuditStatus.PASSED,
            message="Electron package.json validation passed"
        )
    
    def _validate_electron_main_js(self, main_js_path: str) -> AuditResult:
        """Validate Electron main.js"""
        main_js_path = Path(main_js_path)
        
        if not main_js_path.exists():
            return AuditResult(
                check_id="electron_main_js",
                status=AuditStatus.FAILED,
                message="main.js not found"
            )
        
        try:
            with open(main_js_path, 'r') as f:
                content = f.read()
            
            # Check for Electron-specific patterns
            electron_patterns = [
                'electron',
                'app.on',
                'BrowserWindow',
                'mainWindow'
            ]
            
            found_patterns = [pattern for pattern in electron_patterns if pattern in content]
            
            if len(found_patterns) < 2:
                return AuditResult(
                    check_id="electron_main_js",
                    status=AuditStatus.WARNING,
                    message="main.js may not contain Electron-specific code",
                    details={"found_patterns": found_patterns}
                )
                
        except Exception as e:
            return AuditResult(
                check_id="electron_main_js",
                status=AuditStatus.ERROR,
                message=f"Error reading main.js: {str(e)}"
            )
        
        return AuditResult(
            check_id="electron_main_js",
            status=AuditStatus.PASSED,
            message="Electron main.js validation passed"
        )
    
    def _validate_electron_structure(self, electron_path: str) -> AuditResult:
        """Validate Electron app structure"""
        electron_path = Path(electron_path)
        
        required_structure = [
            "package.json",
            "main.js",
            "index.html",
            "renderer.js"
        ]
        
        missing_files = []
        for file_name in required_structure:
            if not (electron_path / file_name).exists():
                missing_files.append(file_name)
        
        if missing_files:
            return AuditResult(
                check_id="electron_structure",
                status=AuditStatus.WARNING,
                message="Electron app structure incomplete",
                details={"missing_files": missing_files}
            )
        
        return AuditResult(
            check_id="electron_structure",
            status=AuditStatus.PASSED,
            message="Electron app structure valid"
        )
    
    def _validate_python_cli(self, script_path: str) -> AuditResult:
        """Validate Python CLI script"""
        script_path = Path(script_path)
        
        if not script_path.exists():
            return AuditResult(
                check_id="python_cli_script",
                status=AuditStatus.FAILED,
                message="CLI script not found"
            )
        
        try:
            with open(script_path, 'r') as f:
                content = f.read()
            
            # Check for Python shebang
            if not content.startswith('#!/usr/bin/env python'):
                return AuditResult(
                    check_id="python_cli_script",
                    status=AuditStatus.WARNING,
                    message="Missing Python shebang"
                )
            
            # Check for Click or argparse patterns
            click_patterns = ['import click', '@click.command']
            argparse_patterns = ['import argparse', 'argparse.ArgumentParser']
            
            has_click = any(pattern in content for pattern in click_patterns)
            has_argparse = any(pattern in content for pattern in argparse_patterns)
            
            if not (has_click or has_argparse):
                return AuditResult(
                    check_id="python_cli_script",
                    status=AuditStatus.WARNING,
                    message="No CLI framework detected (Click/argparse)"
                )
                
        except Exception as e:
            return AuditResult(
                check_id="python_cli_script",
                status=AuditStatus.ERROR,
                message=f"Error reading CLI script: {str(e)}"
            )
        
        return AuditResult(
            check_id="python_cli_script",
            status=AuditStatus.PASSED,
            message="Python CLI script validation passed"
        )
    
    def _validate_python_requirements(self, req_path: str) -> AuditResult:
        """Validate Python requirements.txt"""
        req_path = Path(req_path)
        
        if not req_path.exists():
            return AuditResult(
                check_id="python_requirements",
                status=AuditStatus.WARNING,
                message="requirements.txt not found"
            )
        
        try:
            with open(req_path, 'r') as f:
                requirements = f.read().strip().split('\\n')
            
            # Check for empty requirements
            if not requirements or requirements == ['']:
                return AuditResult(
                    check_id="python_requirements",
                    status=AuditStatus.WARNING,
                    message="requirements.txt is empty"
                )
            
            # Basic format validation
            valid_reqs = 0
            for req in requirements:
                req = req.strip()
                if req and not req.startswith('#'):
                    # Check for package name
                    if re.match(r'^[a-zA-Z0-9_-]+', req):
                        valid_reqs += 1
                    else:
                        logger.warning(f"Invalid requirement format: {req}")
            
            if valid_reqs == 0:
                return AuditResult(
                    check_id="python_requirements",
                    status=AuditStatus.FAILED,
                    message="No valid requirements found"
                )
                
        except Exception as e:
            return AuditResult(
                check_id="python_requirements",
                status=AuditStatus.ERROR,
                message=f"Error reading requirements.txt: {str(e)}"
            )
        
        return AuditResult(
            check_id="python_requirements",
            status=AuditStatus.PASSED,
            message=f"Python requirements validation passed ({valid_reqs} packages)"
        )

class ExecutableAuditor:
    """Main Executable Auditor class"""
    
    def __init__(self, config_path: str = "config/auditor.cfg"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.analyzer = BuildArtifactAnalyzer()
        self.audit_reports = {}
        self.audit_thread = None
        self.auditor_running = False
        self.audit_queue = deque(maxlen=10000)  # Last 10000 audits
        
        # Audit statistics
        self.audit_stats = {
            "total_audits": 0,
            "passed_audits": 0,
            "failed_audits": 0,
            "warning_audits": 0,
            "avg_audit_time": 0.0
        }
        
        logger.info("Executable Auditor initialized")
    
    def _load_config(self) -> configparser.ConfigParser:
        """Load auditor configuration"""
        config = configparser.ConfigParser()
        
        if self.config_path.exists():
            config.read(self.config_path)
        else:
            self._create_default_config()
            config.read(self.config_path)
        
        return config
    
    def _create_default_config(self):
        """Create default auditor configuration"""
        config = configparser.ConfigParser()
        
        # Audit settings
        config['audit_settings'] = {
            'enable_real_time_monitoring': 'true',
            'audit_interval_seconds': '30',
            'max_concurrent_audits': '5',
            'timeout_seconds': '300'
        }
        
        # Platform settings
        config['platforms'] = {
            'windows_enabled': 'true',
            'macos_enabled': 'true',
            'linux_enabled': 'true',
            'android_enabled': 'true',
            'ios_enabled': 'true',
            'tauri_enabled': 'true',
            'electron_enabled': 'true',
            'cli_tui_enabled': 'true'
        }
        
        # Security settings
        config['security'] = {
            'scan_for_vulnerabilities': 'true',
            'check_code_signing': 'true',
            'validate_permissions': 'true',
            'threat_detection': 'true'
        }
        
        # Alert settings
        config['alerts'] = {
            'alert_on_failure': 'true',
            'alert_on_critical_issues': 'true',
            'alert_email': '',
            'webhook_url': ''
        }
        
        # Create directory and write config
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            config.write(f)
        
        logger.info(f"Auditor configuration created at {self.config_path}")
    
    def start_auditor(self):
        """Start the real-time auditor"""
        if self.auditor_running:
            logger.warning("Auditor already running")
            return
        
        self.auditor_running = True
        self.audit_thread = threading.Thread(target=self._audit_loop, daemon=True)
        self.audit_thread.start()
        logger.info("Executable Auditor started")
    
    def stop_auditor(self):
        """Stop the auditor"""
        self.auditor_running = False
        
        if self.audit_thread:
            self.audit_thread.join(timeout=5)
        
        logger.info("Executable Auditor stopped")
    
    def _audit_loop(self):
        """Main audit loop for continuous monitoring"""
        last_audit_time = datetime.now() - timedelta(seconds=60)  # Audit immediately on start
        
        while self.auditor_running:
            try:
                current_time = datetime.now()
                audit_interval = int(self.config.get('audit_settings', 'audit_interval_seconds', fallback=30))
                
                # Check if it's time for the next audit cycle
                if (current_time - last_audit_time).total_seconds() >= audit_interval:
                    self._perform_continuous_audit()
                    last_audit_time = current_time
                
                time.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                logger.error(f"Error in audit loop: {str(e)}")
                time.sleep(10)
    
    def _perform_continuous_audit(self):
        """Perform continuous audit of system state"""
        try:
            # Scan for new build artifacts
            artifacts = self._scan_build_artifacts()
            
            if artifacts:
                logger.info(f"Found {len(artifacts)} artifacts for audit")
                
                # Audit each artifact
                for artifact in artifacts:
                    self.audit_build_artifact(
                        artifact['build_id'],
                        artifact['platform'],
                        artifact['artifacts']
                    )
            
        except Exception as e:
            logger.error(f"Error in continuous audit: {str(e)}")
    
    def _scan_build_artifacts(self) -> List[Dict[str, Any]]:
        """Scan for new build artifacts to audit"""
        artifacts = []
        
        # Common build artifact locations
        build_locations = [
            "builds/windows",
            "builds/macos", 
            "builds/linux",
            "builds/android",
            "builds/ios",
            "builds/tauri",
            "builds/electron",
            "builds/cli"
        ]
        
        platform_map = {
            "builds/windows": Platform.WINDOWS,
            "builds/macos": Platform.MACOS,
            "builds/linux": Platform.LINUX,
            "builds/android": Platform.ANDROID,
            "builds/ios": Platform.IOS,
            "builds/tauri": Platform.TAURI,
            "builds/electron": Platform.ELECTRON,
            "builds/cli": Platform.CLI_TUI
        }
        
        for location in build_locations:
            build_path = Path(location)
            if build_path.exists():
                # Check for build artifacts
                for item in build_path.iterdir():
                    if item.is_file() and item.suffix in ['.exe', '.app', '.deb', '.rpm', '.apk', '.ipa']:
                        # This is a new build artifact
                        artifacts.append({
                            'build_id': item.stem,
                            'platform': platform_map[location],
                            'artifacts': [str(item)]
                        })
        
        return artifacts
    
    def audit_build_artifact(self, build_id: str, platform: Platform, 
                           artifact_paths: List[str]) -> str:
        """Audit a build artifact and return audit report ID"""
        report_id = f"audit_{int(time.time())}_{build_id}"
        
        try:
            report = AuditReport(
                report_id=report_id,
                build_id=build_id,
                platform=platform,
                status=AuditStatus.RUNNING,
                started_at=datetime.now()
            )
            
            # Perform audit checks
            audit_results = []
            
            for artifact_path in artifact_paths:
                artifact_type = self._determine_artifact_type(artifact_path)
                
                if self.config.getboolean('platforms', f"{platform.value}_enabled", fallback=True):
                    result = self.analyzer.validate_artifact(artifact_path, platform, artifact_type)
                    audit_results.append(result)
                    report.artifacts_validated.append(f"{artifact_type}:{artifact_path}")
            
            report.results = audit_results
            
            # Calculate overall status and score
            passed_results = [r for r in audit_results if r.status == AuditStatus.PASSED]
            failed_results = [r for r in audit_results if r.status == AuditStatus.FAILED]
            warning_results = [r for r in audit_results if r.status == AuditStatus.WARNING]
            
            total_results = len(audit_results)
            if total_results > 0:
                score = (len(passed_results) / total_results) * 100
                report.overall_score = score
                
                if failed_results:
                    report.status = AuditStatus.FAILED
                elif warning_results:
                    report.status = AuditStatus.WARNING
                else:
                    report.status = AuditStatus.PASSED
            
            report.completed_at = datetime.now()
            
            # Store report
            self.audit_reports[report_id] = report
            self.audit_queue.append(report)
            
            # Update statistics
            self.audit_stats["total_audits"] += 1
            if report.status == AuditStatus.PASSED:
                self.audit_stats["passed_audits"] += 1
            elif report.status == AuditStatus.FAILED:
                self.audit_stats["failed_audits"] += 1
            elif report.status == AuditStatus.WARNING:
                self.audit_stats["warning_audits"] += 1
            
            # Calculate average audit time
            total_time = sum(r.execution_time for r in audit_results)
            self.audit_stats["avg_audit_time"] = (
                (self.audit_stats["avg_audit_time"] * (self.audit_stats["total_audits"] - 1) + total_time) 
                / self.audit_stats["total_audits"]
            )
            
            logger.info(f"Audit {report_id} completed - Status: {report.status.value}, Score: {report.overall_score:.1f}")
            
            # Send alerts if configured
            if self.config.getboolean('alerts', 'alert_on_failure', fallback=False) and report.status == AuditStatus.FAILED:
                self._send_alert("AUDIT_FAILED", f"Audit failed for build {build_id}", report)
            
            if self.config.getboolean('alerts', 'alert_on_critical_issues', fallback=False):
                critical_results = [r for r in audit_results if r.severity == AuditSeverity.CRITICAL]
                if critical_results:
                    self._send_alert("CRITICAL_ISSUE", f"Critical issues found in build {build_id}", report)
            
            return report_id
            
        except Exception as e:
            logger.error(f"Error auditing artifact {artifact_path}: {str(e)}")
            
            # Create error report
            error_report = AuditReport(
                report_id=report_id,
                build_id=build_id,
                platform=platform,
                status=AuditStatus.ERROR,
                started_at=datetime.now(),
                completed_at=datetime.now()
            )
            
            self.audit_reports[report_id] = error_report
            return report_id
    
    def _determine_artifact_type(self, artifact_path: str) -> str:
        """Determine artifact type from file path"""
        path = Path(artifact_path)
        suffix = path.suffix.lower()
        
        type_map = {
            '.exe': 'executable',
            '.app': 'app_bundle',
            '.deb': 'package',
            '.rpm': 'package',
            '.apk': 'apk_structure',
            '.ipa': 'bundle_structure',
            '.toml': 'cargo_toml',
            '.json': 'config',
            '.js': 'main_js',
            '.html': 'index',
            '.py': 'python_scripts',
            '.plist': 'info_plist',
            '.gradle': 'gradle',
            '.rs': 'rust_sources'
        }
        
        # Check filename patterns
        if 'info.plist' in path.name:
            return 'info_plist'
        elif 'tauri.conf.json' in path.name:
            return 'tauri_config'
        elif path.name == 'package.json':
            return 'package_json'
        elif path.name == 'main.js':
            return 'main_js'
        elif path.name.endswith('.desktop'):
            return 'desktop_entry'
        elif 'AndroidManifest.xml' in path.name:
            return 'manifest'
        elif 'Cargo.toml' in path.name:
            return 'cargo_toml'
        elif path.name == 'requirements.txt':
            return 'requirements'
        
        return type_map.get(suffix, 'generic')
    
    def _send_alert(self, alert_type: str, message: str, report: AuditReport):
        """Send alert for audit issues"""
        alert_data = {
            "type": alert_type,
            "message": message,
            "report_id": report.report_id,
            "build_id": report.build_id,
            "platform": report.platform.value,
            "timestamp": datetime.now().isoformat(),
            "severity": "high" if report.status == AuditStatus.FAILED else "medium"
        }
        
        # Log alert
        logger.warning(f"ALERT {alert_type}: {message}")
        
        # In a real implementation, this would send email, webhook, etc.
        # For now, just store in audit queue
        self.audit_queue.append({
            "alert_type": alert_type,
            "alert_data": alert_data
        })
    
    def get_audit_report(self, report_id: str) -> Optional[AuditReport]:
        """Get audit report by ID"""
        return self.audit_reports.get(report_id)
    
    def get_audit_status(self) -> Dict[str, Any]:
        """Get current audit status and statistics"""
        # Calculate recent audit performance
        recent_audits = [report for report in list(self.audit_queue) if isinstance(report, AuditReport)]
        recent_24h = [report for report in recent_audits 
                     if (datetime.now() - report.started_at).total_seconds() < 86400]  # 24 hours
        
        if recent_24h:
            success_rate_24h = len([r for r in recent_24h if r.status == AuditStatus.PASSED]) / len(recent_24h)
            avg_score_24h = sum(r.overall_score for r in recent_24h) / len(recent_24h)
        else:
            success_rate_24h = 0.0
            avg_score_24h = 0.0
        
        return {
            "auditor_running": self.auditor_running,
            "total_audits": self.audit_stats["total_audits"],
            "audit_statistics": {
                "passed": self.audit_stats["passed_audits"],
                "failed": self.audit_stats["failed_audits"],
                "warnings": self.audit_stats["warning_audits"],
                "success_rate": (self.audit_stats["passed_audits"] / max(1, self.audit_stats["total_audits"])) * 100,
                "avg_audit_time": self.audit_stats["avg_audit_time"]
            },
            "recent_performance": {
                "audits_last_24h": len(recent_24h),
                "success_rate_24h": success_rate_24h * 100,
                "avg_score_24h": avg_score_24h
            },
            "active_audits": len([r for r in recent_audits if r.status == AuditStatus.RUNNING]),
            "platform_coverage": {
                platform.value: self.config.getboolean('platforms', f"{platform.value}_enabled", fallback=True)
                for platform in Platform
            }
        }
    
    def get_recent_reports(self, count: int = 10) -> List[AuditReport]:
        """Get recent audit reports"""
        recent_reports = [report for report in list(self.audit_queue) if isinstance(report, AuditReport)]
        return sorted(recent_reports, key=lambda x: x.started_at, reverse=True)[:count]

def main():
    """Main function"""
    auditor = ExecutableAuditor()
    
    print("Executable Auditor")
    print("Usage: python executable_auditor.py [start|status|stop]")
    print("  start - Start real-time auditing")
    print("  status - Get current audit status")
    print("  stop - Stop auditing")

if __name__ == "__main__":
    main()