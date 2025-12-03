#!/usr/bin/env python3
"""
Augur Omega: macOS Build Script
Builds macOS applications and installers
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import platform
import argparse


def build_macos_app():
    """Build macOS APP using py2app or PyInstaller"""
    print("Building macOS APP...")
    
    if platform.system() != "Darwin":
        print("Error: macOS build requires macOS host")
        return False
    
    project_root = Path(__file__).parent.parent
    builds_dir = project_root / "builds" / "macos" / "app"
    builds_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Try py2app first
        import py2app
        
        setup_py_content = f'''
from setuptools import setup
import py2app

APP = ['{project_root / "main.py"}']
DATA_FILES = []
OPTIONS = {{
    'argv_emulation': True,
    'packages': ['litestar', 'pydantic', 'sqlalchemy', 'asyncio', 'aiohttp'],
    'includes': ['scipy', 'numpy'],
    'iconfile': '{project_root / "assets" / "icon.icns" if (project_root / "assets" / "icon.icns").exists() else ""}',
    'plist': {{
        'CFBundleName': 'Augur Omega',
        'CFBundleDisplayName': 'Augur Omega AI Platform',
        'CFBundleGetInfoString': 'Augur Omega AI Platform',
        'CFBundleIdentifier': 'com.augromega.platform',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSAppleScriptEnabled': True,
        'NSMainNibFile': 'MainMenu.nib',
        'NSPrincipalClass': 'NSApplication',
    }}
}}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={{'py2app': OPTIONS}},
    setup_requires=['py2app'],
)
'''
        
        temp_dir = builds_dir / "temp"
        temp_dir.mkdir(exist_ok=True)
        
        setup_py_path = temp_dir / "setup.py"
        with open(setup_py_path, "w") as f:
            f.write(setup_py_content)
        
        subprocess.run([sys.executable, str(setup_py_path), "py2app", "-A"], 
                      check=True, cwd=temp_dir)
        
        # Move built app to builds directory
        dist_dir = temp_dir / "dist"
        if dist_dir.exists():
            for app_file in dist_dir.glob("*.app"):
                dest_path = builds_dir / app_file.name
                if dest_path.exists():
                    shutil.rmtree(dest_path)
                shutil.move(str(app_file), str(dest_path))
        
        print("macOS APP built successfully with py2app")
        return True
        
    except ImportError:
        print("py2app not available, trying PyInstaller...")
        
        try:
            cmd = [
                sys.executable, "-m", "PyInstaller",
                "--onefile",
                "--windowed", 
                "--name=AugurOmega",
                f"--distpath={builds_dir}",
                str(project_root / "main.py")
            ]
            
            subprocess.run(cmd, check=True, cwd=project_root)
            
            # Convert to .app bundle format if executable was created
            app_files = list(builds_dir.glob("AugurOmega*"))
            for app_file in app_files:
                if app_file.is_file() and not app_file.suffix:
                    # Create .app bundle structure
                    app_bundle_dir = builds_dir / f"{app_file.name}.app" / "Contents" / "MacOS"
                    app_bundle_dir.mkdir(parents=True)
                    shutil.move(str(app_file), app_bundle_dir / app_file.name)
            
            print("macOS APP built successfully with PyInstaller")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Failed to build macOS APP: {e}")
            return False


def build_macos_dmg():
    """Build macOS DMG installer"""
    print("Building macOS DMG...")
    
    if platform.system() != "Darwin":
        print("Error: DMG creation requires macOS host")
        return False
    
    project_root = Path(__file__).parent.parent
    app_dir = project_root / "builds" / "macos" / "app"
    dmg_dir = project_root / "builds" / "macos" / "dmg"
    dmg_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if APP exists, build if not
    app_files = list(app_dir.rglob("*.app"))
    if not app_files:
        print("APP not found, building APP first...")
        if not build_macos_app():
            return False
        app_files = list(app_dir.rglob("*.app"))
    
    if not app_files:
        print("No APP found to package into DMG")
        return False
    
    app_path = app_files[0]
    
    try:
        dmg_name = dmg_dir / "AugurOmega-macOS.dmg"
        
        subprocess.run([
            "hdiutil", "create", "-volname", "AugurOmega", 
            "-srcfolder", str(app_path.parent), 
            "-ov", "-format", "UDZO", str(dmg_name)
        ], check=True)
        
        print("macOS DMG built successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to build macOS DMG: {e}")
        return False
    except FileNotFoundError:
        print("hdiutil not found, skipping DMG build")
        return False


def main():
    parser = argparse.ArgumentParser(description='Build Augur Omega for macOS')
    parser.add_argument('--target', choices=['app', 'dmg', 'all'], 
                       default='all', help='Build target')
    
    args = parser.parse_args()
    
    success = True
    
    if args.target in ['app', 'all']:
        success &= build_macos_app()
    
    if args.target in ['dmg', 'all']:
        success &= build_macos_dmg()
    
    if success:
        print("macOS build completed successfully!")
        return 0
    else:
        print("macOS build failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())