#!/usr/bin/env python3
"""
Augur Omega: Master Build Orchestrator
Coordinates all platform builds and manages dependencies
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import platform
import argparse
import json
from typing import Dict, List, Optional


# Try to import toml, install if not available
try:
    import toml
except ImportError:
    print("toml package not found, installing...")
    subprocess.run([sys.executable, "-m", "pip", "install", "toml"], check=True)
    import toml


class BuildOrchestrator:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.builds_dir = self.project_root / "builds"
        self.config = self._load_config()
        self.platform_builders = {
            "windows": str(self.project_root / "scripts" / "build_windows.py"),
            "macos": str(self.project_root / "scripts" / "build_macos.py"),
            "linux": str(self.project_root / "scripts" / "build_linux.py"),
            "android": str(self.project_root / "scripts" / "build_android.py"),
            "ios": str(self.project_root / "scripts" / "build_ios.py"),
            "desktop": str(self.project_root / "scripts" / "build_desktop.py"),
            "tui_cli": str(self.project_root / "scripts" / "build_tui_cli.py")
        }
        self.completed_builds = []
        self.failed_builds = []

    def _load_config(self) -> dict:
        """Load build configuration from TOML file"""
        config_path = self.project_root / "build_config.toml"
        if config_path.exists():
            with open(config_path, 'r') as f:
                return toml.load(f)
        else:
            # Default configuration
            return {}

    def setup_build_environment(self):
        """Set up the build environment with necessary dependencies"""
        print("Setting up build environment...")
        
        # Install core dependencies
        core_deps = self.config.get("build_dependencies", {}).get("core_deps", [
            "litestar", "pydantic", "sqlalchemy", "asyncpg", "redis", 
            "aiohttp", "scipy", "numpy", "pydantic", "fastapi", "uvicorn", 
            "websockets", "click", "rich", "inquirer", "aiofiles"
        ])
        
        try:
            for dep in core_deps:
                subprocess.run([sys.executable, "-m", "pip", "install", dep], 
                             check=True, capture_output=True)
            print("Core dependencies installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"Warning: Could not install all core dependencies: {e}")

    def check_platform_compatibility(self, platform_name: str) -> bool:
        """Check if the current system can build for the specified platform"""
        if platform_name in ["macos", "ios"] and platform.system() != "Darwin":
            print(f"⚠️  {platform_name} build requires macOS host")
            return False
        return True

    def run_platform_build(self, platform_name: str, target: str = "all") -> bool:
        """Run the build script for a specific platform"""
        if not self.check_platform_compatibility(platform_name):
            self.failed_builds.append((platform_name, "Platform requirements not met"))
            return False

        build_script = self.platform_builders.get(platform_name)
        if not build_script or not Path(build_script).exists():
            print(f"❌ Build script not found for {platform_name}")
            self.failed_builds.append((platform_name, "Build script not found"))
            return False

        print(f"🚀 Building {platform_name}...")
        
        try:
            result = subprocess.run([
                sys.executable, build_script, "--target", target
            ], check=True, capture_output=True, text=True)
            
            print(f"✅ {platform_name} build completed successfully")
            self.completed_builds.append(platform_name)
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ {platform_name} build failed:")
            print(f"   stdout: {e.stdout}")
            print(f"   stderr: {e.stderr}")
            self.failed_builds.append((platform_name, str(e)))
            return False

    def build_all_platforms(self):
        """Build for all platforms"""
        print("🚀 Starting Augur Omega Master Build Process...")
        print(f"Project root: {self.project_root}")
        print(f"Build directory: {self.builds_dir}")
        print("-" * 70)

        # Set up build environment
        self.setup_build_environment()

        # Create builds directory
        self.builds_dir.mkdir(exist_ok=True)

        # Build for each platform
        platforms_to_build = list(self.platform_builders.keys())
        for platform_name in platforms_to_build:
            self.run_platform_build(platform_name, "all")

        # Summary
        print("\n" + "="*70)
        print("BUILD SUMMARY")
        print("="*70)
        print(f"✅ Successful builds: {len(self.completed_builds)}")
        for platform in self.completed_builds:
            print(f"   - {platform}")

        if self.failed_builds:
            print(f"❌ Failed builds: {len(self.failed_builds)}")
            for platform, error in self.failed_builds:
                print(f"   - {platform}: {error}")
        else:
            print("✅ All builds completed successfully!")

        print(f"\n📁 Build outputs located in: {self.builds_dir}")
        print("🎯 Augur Omega Master Build Process Complete!")

        # Create build report
        self.create_build_report()

    def create_build_report(self):
        """Create a detailed build report"""
        report = {
            "build_timestamp": __import__('datetime').datetime.now().isoformat(),
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "completed_builds": self.completed_builds,
            "failed_builds": self.failed_builds,
            "build_directory": str(self.builds_dir),
            "project_root": str(self.project_root)
        }

        report_path = self.builds_dir / "build_report.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"📄 Build report saved to: {report_path}")

    def build_specific_platform(self, platform_name: str, target: str = "all"):
        """Build for a specific platform"""
        if platform_name not in self.platform_builders:
            print(f"❌ Unknown platform: {platform_name}")
            return False

        self.setup_build_environment()
        return self.run_platform_build(platform_name, target)


def main():
    orchestrator = BuildOrchestrator()

    parser = argparse.ArgumentParser(description='Orchestrate Augur Omega builds')
    parser.add_argument('--platform', '-p', 
                       choices=list(orchestrator.platform_builders.keys()),
                       help='Build for specific platform only')
    parser.add_argument('--target', '-t', default='all',
                       help='Build target (varies by platform)')
    parser.add_argument('--list', '-l', action='store_true',
                       help='List available platforms')
    parser.add_argument('--clean', '-c', action='store_true',
                       help='Clean build directory before building')

    args = parser.parse_args()

    if args.list:
        print("Available platforms:")
        for platform_name in orchestrator.platform_builders.keys():
            print(f"  - {platform_name}")
        return

    if args.clean:
        print("Cleaning build directory...")
        if orchestrator.builds_dir.exists():
            shutil.rmtree(orchestrator.builds_dir)

    if args.platform:
        print(f"Building for {args.platform} only...")
        success = orchestrator.build_specific_platform(args.platform, args.target)
        if success:
            print(f"✅ {args.platform} build completed successfully!")
        else:
            print(f"❌ {args.platform} build failed!")
    else:
        orchestrator.build_all_platforms()


if __name__ == "__main__":
    main()