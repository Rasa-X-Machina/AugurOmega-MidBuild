#!/usr/bin/env python3
"""
Augur Omega: iOS Build Script
Builds iOS IPA
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import platform
import argparse


def build_ios_ipa():
    """Build iOS IPA using kivy-ios"""
    print("Building iOS IPA...")
    
    if platform.system() != "Darwin":
        print("Error: iOS build requires macOS host with Xcode")
        return False
    
    project_root = Path(__file__).parent.parent
    builds_dir = project_root / "builds" / "ios" / "ipa"
    builds_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Check if kivy-ios is available
        import importlib.util
        if importlib.util.find_spec("kivy_ios") is None:
            print("kivy-ios not installed, skipping iOS build")
            return False

        # Create iOS build directory
        ios_build_dir = builds_dir / "temp"
        if ios_build_dir.exists():
            shutil.rmtree(ios_build_dir)
        ios_build_dir.mkdir(exist_ok=True)
        
        # Initialize kivy-ios project
        main_py_path = str(project_root / "main.py")
        
        # Run kivy-ios tool to create project
        subprocess.run([
            sys.executable, "-m", "kivy_ios", "create", "AugurOmega", main_py_path
        ], check=True, cwd=ios_build_dir)
        
        # Build the project using xcodebuild
        app_dir = ios_build_dir / "AugurOmega"
        if app_dir.exists():
            subprocess.run([
                "xcodebuild", "-project", "AugurOmega.xcodeproj",
                "-target", "AugurOmega", "-configuration", "Release",
                "ARCHS=arm64", "ONLY_ACTIVE_ARCH=NO",
                f"-destination generic/platform=iOS"
            ], check=True, cwd=app_dir)
        
        print("iOS IPA built successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to build iOS IPA: {e}")
        return False
    except ImportError:
        print("kivy-ios not available, skipping iOS build")
        return False
    except Exception as e:
        print(f"Unexpected error during iOS build: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='Build Augur Omega for iOS')
    parser.add_argument('--target', choices=['ipa', 'all'], 
                       default='all', help='Build target (only IPA available)')
    
    args = parser.parse_args()
    
    success = build_ios_ipa()
    
    if success:
        print("iOS build completed successfully!")
        return 0
    else:
        print("iOS build failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())