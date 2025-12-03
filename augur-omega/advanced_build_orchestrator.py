#!/usr/bin/env python3
"""
Augur Omega: Advanced Build Orchestrator
Optimizes build processes with mathematical efficiency >94% and task completion rate >91%
Coordinates all platform builds and manages dependencies with parallel execution
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import platform
import argparse
import json
import asyncio
import time
from typing import Dict, List, Optional, Tuple, Callable
from dataclasses import dataclass
import math
from concurrent.futures import ThreadPoolExecutor
import statistics


@dataclass
class BuildMetrics:
    """Track build performance metrics"""
    start_time: float
    end_time: float = 0
    success_count: int = 0
    failure_count: int = 0
    total_tasks: int = 0
    completed_tasks: int = 0
    efficiency: float = 0.0
    task_completion_rate: float = 0.0
    build_times: List[float] = None

    def __post_init__(self):
        if self.build_times is None:
            self.build_times = []


class BuildOrchestrator:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.builds_dir = self.project_root / "builds"
        self.platform_builders = {
            "windows": str(self.project_root / "scripts" / "build_windows.py"),
            "macos": str(self.project_root / "scripts" / "build_macos.py"),
            "linux": str(self.project_root / "scripts" / "build_linux.py"),
            "android": str(self.project_root / "scripts" / "build_android.py"),
            "ios": str(self.project_root / "scripts" / "build_ios.py"),
            "tauri": str(self.project_root / "scripts" / "build_desktop.py"),
            "electron": str(self.project_root / "scripts" / "build_desktop.py"),
            "tui_cli": str(self.project_root / "scripts" / "build_tui_cli.py"),
            "web": str(self.project_root / "scripts" / "build_web.py")
        }
        self.completed_builds = []
        self.failed_builds = []
        self.metrics = BuildMetrics(start_time=time.time())
        self.executor = ThreadPoolExecutor(max_workers=8)  # Optimize for parallel builds
        self.build_results = {}

    def setup_build_environment(self):
        """Set up the build environment with necessary dependencies"""
        print("Setting up build environment...")

        # Install core dependencies
        core_deps = [
            "litestar", "pydantic", "sqlalchemy", "asyncpg", "redis",
            "aiohttp", "scipy", "numpy", "pydantic", "fastapi", "uvicorn",
            "websockets", "click", "rich", "inquirer", "aiofiles", "toml"
        ]

        try:
            for dep in core_deps:
                subprocess.run([sys.executable, "-m", "pip", "install", dep],
                             check=True, capture_output=True, timeout=300)
            print("Core dependencies installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"Warning: Could not install all core dependencies: {e}")
        except subprocess.TimeoutExpired:
            print("Warning: Dependency installation timed out")

    def check_platform_compatibility(self, platform_name: str) -> bool:
        """Check if the current system can build for the specified platform"""
        if platform_name in ["macos", "ios"] and platform.system() != "Darwin":
            print(f"⚠️  {platform_name} build requires macOS host")
            return False
        return True

    def calculate_build_efficiency(self, build_time: float, expected_time: float) -> float:
        """Calculate mathematical efficiency of the build"""
        # Efficiency = (expected_time / actual_time) * 100
        # If actual time is less than expected, efficiency can exceed 100%
        efficiency = (expected_time / build_time) * 100
        return min(efficiency, 100)  # Cap at 100% for practical purposes

    def run_platform_build(self, platform_name: str, target: str = "all") -> Tuple[bool, float]:
        """Run the build script for a specific platform with timing"""
        start_time = time.time()
        
        if not self.check_platform_compatibility(platform_name):
            self.failed_builds.append((platform_name, "Platform requirements not met"))
            return False, time.time() - start_time

        build_script = self.platform_builders.get(platform_name)
        if not build_script or not Path(build_script).exists():
            print(f"❌ Build script not found for {platform_name}")
            self.failed_builds.append((platform_name, "Build script not found"))
            return False, time.time() - start_time

        print(f"🚀 Building {platform_name}...")

        try:
            # Determine expected build time based on platform complexity
            expected_times = {
                "windows": 180,  # 3 minutes
                "macos": 240,    # 4 minutes
                "linux": 150,    # 2.5 minutes
                "android": 600,  # 10 minutes (complex)
                "ios": 600,      # 10 minutes (requires Xcode)
                "tauri": 420,    # 7 minutes (Rust compilation)
                "electron": 300, # 5 minutes (Node.js build)
                "tui_cli": 60,   # 1 minute (simple Python)
                "web": 30        # 30 seconds (static files)
            }
            expected_time = expected_times.get(platform_name, 180)

            result = subprocess.run([
                sys.executable, build_script, "--target", target
            ], check=True, capture_output=True, text=True, timeout=1200)  # 20 minute timeout

            build_duration = time.time() - start_time
            efficiency = self.calculate_build_efficiency(build_duration, expected_time)
            
            print(f"✅ {platform_name} build completed in {build_duration:.2f}s (Efficiency: {efficiency:.1f}%)")
            self.completed_builds.append((platform_name, build_duration, efficiency))
            return True, build_duration
        except subprocess.CalledProcessError as e:
            build_duration = time.time() - start_time
            print(f"❌ {platform_name} build failed after {build_duration:.2f}s:")
            print(f"   stdout: {e.stdout}")
            print(f"   stderr: {e.stderr}")
            self.failed_builds.append((platform_name, str(e)))
            return False, build_duration
        except subprocess.TimeoutExpired:
            build_duration = time.time() - start_time
            print(f"❌ {platform_name} build timed out after {build_duration:.2f}s")
            self.failed_builds.append((platform_name, "Build timed out"))
            return False, build_duration

    async def run_parallel_builds(self, platforms: List[str], target: str = "all"):
        """Run multiple builds in parallel with optimized resource allocation"""
        print(f"🚀 Starting parallel build for {len(platforms)} platforms...")
        
        # Calculate optimal parallelism based on system resources
        cpu_count = os.cpu_count() or 4
        optimal_parallelism = min(len(platforms), max(2, cpu_count - 2))  # Leave some resources for system
        
        print(f"Using {optimal_parallelism} parallel build processes")
        
        # Split platforms into batches for optimal resource usage
        batches = [platforms[i:i + optimal_parallelism] for i in range(0, len(platforms), optimal_parallelism)]
        
        for batch_num, batch in enumerate(batches, 1):
            print(f"📦 Processing batch {batch_num}/{len(batches)}: {', '.join(batch)}")
            
            # Run builds in current batch in parallel
            tasks = []
            for platform_name in batch:
                task = asyncio.get_event_loop().run_in_executor(
                    self.executor, 
                    self.run_platform_build, 
                    platform_name, 
                    target
                )
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for i, result in enumerate(results):
                platform_name = batch[i]
                if isinstance(result, tuple):
                    success, duration = result
                    if success:
                        self.metrics.success_count += 1
                    else:
                        self.metrics.failure_count += 1
                    self.metrics.build_times.append(duration)
                    self.metrics.completed_tasks += 1
                else:
                    # Handle exception case
                    print(f"❌ Exception during {platform_name} build: {result}")
                    self.failed_builds.append((platform_name, str(result)))
                    self.metrics.failure_count += 1
                    self.metrics.completed_tasks += 1

    def build_all_platforms(self):
        """Build for all platforms with mathematical optimization"""
        print("🚀 Starting Augur Omega Master Build Process...")
        print(f"Project root: {self.project_root}")
        print(f"Build directory: {self.builds_dir}")
        print(f"System: {platform.system()} ({os.cpu_count()} CPU cores)")
        print("-" * 70)

        # Set up build environment
        self.setup_build_environment()

        # Create builds directory
        self.builds_dir.mkdir(exist_ok=True)

        # Determine which platforms to build based on compatibility
        all_platforms = list(self.platform_builders.keys())
        compatible_platforms = [p for p in all_platforms if self.check_platform_compatibility(p)]
        
        print(f"Available platforms: {len(all_platforms)}")
        print(f"Compatible platforms: {len(compatible_platforms)}")
        print(f"Building: {', '.join(compatible_platforms)}")

        # Update metrics
        self.metrics.total_tasks = len(compatible_platforms)

        # Run builds in parallel
        asyncio.run(self.run_parallel_builds(compatible_platforms, "all"))

        # Calculate final metrics
        total_build_time = time.time() - self.metrics.start_time
        self.metrics.end_time = time.time()
        
        if self.metrics.completed_tasks > 0:
            self.metrics.task_completion_rate = (self.metrics.success_count / self.metrics.completed_tasks) * 100
        else:
            self.metrics.task_completion_rate = 0
            
        if self.metrics.build_times:
            avg_build_time = statistics.mean(self.metrics.build_times)
            # Efficiency is based on how quickly we completed compared to sequential execution
            estimated_sequential_time = sum(self.metrics.build_times)
            self.metrics.efficiency = (estimated_sequential_time / total_build_time) * 100
        else:
            self.metrics.efficiency = 0

        # Summary
        print("\n" + "="*70)
        print("BUILD SUMMARY")
        print("="*70)
        print(f"📊 Total tasks: {self.metrics.total_tasks}")
        print(f"✅ Successful builds: {self.metrics.success_count}")
        print(f"❌ Failed builds: {self.metrics.failure_count}")
        print(f"📈 Task completion rate: {self.metrics.task_completion_rate:.1f}%")
        print(f"⚡ Mathematical efficiency: {self.metrics.efficiency:.1f}%")
        print(f"⏱️  Total build time: {total_build_time:.2f}s")
        
        if self.metrics.build_times:
            print(f"📊 Avg build time: {statistics.mean(self.metrics.build_times):.2f}s")
            print(f"📊 Min build time: {min(self.metrics.build_times):.2f}s")
            print(f"📊 Max build time: {max(self.metrics.build_times):.2f}s")

        for platform, duration, efficiency in self.completed_builds:
            print(f"   - {platform}: {duration:.2f}s (eff: {efficiency:.1f}%)")

        if self.failed_builds:
            print("\n❌ Failed builds:")
            for platform, error in self.failed_builds:
                print(f"   - {platform}: {error}")
        else:
            print("\n✅ All builds completed successfully!")

        print(f"\n📁 Build outputs located in: {self.builds_dir}")
        
        # Check if we met the requirements
        efficiency_met = self.metrics.efficiency > 94
        completion_rate_met = self.metrics.task_completion_rate > 91
        
        print(f"🎯 Requirements check:")
        print(f"   - Mathematical efficiency >94%: {'✅' if efficiency_met else '❌'} ({self.metrics.efficiency:.1f}%)")
        print(f"   - Task completion rate >91%: {'✅' if completion_rate_met else '❌'} ({self.metrics.task_completion_rate:.1f}%)")
        
        if efficiency_met and completion_rate_met:
            print("\n🎉 All requirements met! Augur Omega build system optimized successfully!")
        else:
            print("\n⚠️  Some requirements not met. Consider optimizing build configurations.")

        # Create build report
        self.create_build_report()

    def create_build_report(self):
        """Create a detailed build report"""
        report = {
            "build_timestamp": __import__('datetime').datetime.now().isoformat(),
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "completed_builds": [{"platform": name, "duration": duration, "efficiency": eff} 
                                for name, duration, eff in self.completed_builds],
            "failed_builds": [{"platform": platform, "error": error} 
                             for platform, error in self.failed_builds],
            "build_directory": str(self.builds_dir),
            "project_root": str(self.project_root),
            "metrics": {
                "total_tasks": self.metrics.total_tasks,
                "success_count": self.metrics.success_count,
                "failure_count": self.metrics.failure_count,
                "completed_tasks": self.metrics.completed_tasks,
                "efficiency": self.metrics.efficiency,
                "task_completion_rate": self.metrics.task_completion_rate,
                "total_build_time": time.time() - self.metrics.start_time,
                "build_times": self.metrics.build_times
            }
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
        success, duration = self.run_platform_build(platform_name, target)
        
        if success:
            print(f"✅ {platform_name} build completed successfully in {duration:.2f}s!")
            return True
        else:
            print(f"❌ {platform_name} build failed!")
            return False


def main():
    orchestrator = BuildOrchestrator()

    parser = argparse.ArgumentParser(description='Orchestrate Augur Omega builds with mathematical optimization')
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