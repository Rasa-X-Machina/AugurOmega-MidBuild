#!/usr/bin/env python3
"""
Augur Omega: Android Build Script
Builds Android APK
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import argparse


def build_android_apk():
    """Build Android APK using Buildozer"""
    print("Building Android APK...")
    
    project_root = Path(__file__).parent.parent
    builds_dir = project_root / "builds" / "android" / "apk"
    builds_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Check if buildozer is available
        import importlib.util
        if importlib.util.find_spec("buildozer") is None:
            print("Buildozer not installed, skipping Android build")
            return False

        # Create buildozer.spec file
        buildozer_spec = f"""
[app]
title = Augur Omega
package.name = auguromega
package.domain = ai.augur.omega

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,wav,mp3,m4a,ttf,otf,txt,json,yaml,yml,cfg,ini,xml,html,css,js

version = 1.0.0
requirements = python3,kivy,litestar,pydantic,sqlalchemy,aiohttp,numpy,scipy,asyncio

orientation = all
fullscreen = 0

[buildozer]
log_level = 2

android.permissions = INTERNET,ACCESS_NETWORK_STATE,CAMERA,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE
        """

        # Write buildozer.spec to project root
        spec_path = project_root / "buildozer.spec"
        with open(spec_path, "w") as f:
            f.write(buildozer_spec)

        # Run buildozer for APK
        result = subprocess.run(
            ["buildozer", "android", "debug"], 
            check=True, 
            cwd=project_root,
            capture_output=True,
            text=True
        )
        
        # Move APK to builds directory
        apk_files = list(project_root.glob("*.apk"))
        for apk in apk_files:
            shutil.move(str(apk), builds_dir / apk.name)

        print("Android APK built successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to build Android APK: {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        return False
    except ImportError:
        print("Buildozer not available, skipping Android build")
        return False
    except Exception as e:
        print(f"Unexpected error during Android build: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='Build Augur Omega for Android')
    parser.add_argument('--target', choices=['apk', 'all'], 
                       default='all', help='Build target (only APK available)')
    
    args = parser.parse_args()
    
    success = build_android_apk()
    
    if success:
        print("Android build completed successfully!")
        return 0
    else:
        print("Android build failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())