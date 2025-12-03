#!/usr/bin/env python3
"""
Augur Omega: Windows Build Script
Builds Windows executables and installers
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import argparse


def build_windows_exe():
    """Build Windows EXE using PyInstaller"""
    print("Building Windows EXE...")
    
    project_root = Path(__file__).parent.parent
    builds_dir = project_root / "builds" / "windows" / "exe"
    builds_dir.mkdir(parents=True, exist_ok=True)
    
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
        print("Windows EXE built successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to build Windows EXE: {e}")
        return False


def build_windows_msi():
    """Build Windows MSI installer using cx_Freeze"""
    print("Building Windows MSI...")
    
    project_root = Path(__file__).parent.parent
    builds_dir = project_root / "builds" / "windows" / "msi"
    builds_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        import cx_Freeze
        
        # Create setup.py for cx_Freeze
        setup_py_content = f'''
import sys
from cx_Freeze import setup, Executable

build_exe_options = {{"packages": ["asyncio", "litestar", "pydantic", "sqlalchemy", "aiohttp"],
                     "excludes": ["tkinter"]}}

bdist_msi_options = {{
    "upgrade_code": "{{6D5E7857-412B-4C7D-8431-78CFF97A0A8B}}",
    "add_to_path": False,
    "initial_target_dir": r"[ProgramFilesFolder]\\\\AugurOmega",
}}

executables = [
    Executable("{project_root / "main.py"}", 
               base="Win32GUI",
               target_name="AugurOmega.exe")
]

setup(
    name="Augur Omega",
    version="1.0.0",
    description="AI Business Automation Platform",
    options={{"build_exe": build_exe_options, "bdist_msi": bdist_msi_options}},
    executables=executables
)
'''
        
        temp_dir = builds_dir / "temp"
        temp_dir.mkdir(exist_ok=True)
        
        setup_py_path = temp_dir / "setup.py"
        with open(setup_py_path, "w") as f:
            f.write(setup_py_content)
        
        # Build MSI
        subprocess.run([sys.executable, str(setup_py_path), "bdist_msi"], 
                      check=True, cwd=temp_dir)
        
        # Move MSI to output directory
        msi_files = list((temp_dir / "dist").glob("*.msi"))
        for msi_file in msi_files:
            shutil.move(str(msi_file), builds_dir / msi_file.name)
        
        print("Windows MSI built successfully")
        return True
    except ImportError:
        print("cx_Freeze not installed, skipping MSI build")
        return False
    except subprocess.CalledProcessError as e:
        print(f"Failed to build Windows MSI: {e}")
        return False


def build_windows_zip():
    """Create ZIP distribution"""
    print("Creating Windows ZIP distribution...")
    
    project_root = Path(__file__).parent.parent
    exe_dir = project_root / "builds" / "windows" / "exe"
    zip_dir = project_root / "builds" / "windows" / "zip"
    zip_dir.mkdir(parents=True, exist_ok=True)
    
    if not exe_dir.exists():
        print("EXE directory does not exist, building EXE first...")
        if not build_windows_exe():
            return False
    
    try:
        shutil.make_archive(
            str(zip_dir / "AugurOmega-Windows"),
            'zip',
            root_dir=exe_dir
        )
        print("Windows ZIP distribution created successfully")
        return True
    except Exception as e:
        print(f"Failed to create ZIP distribution: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='Build Augur Omega for Windows')
    parser.add_argument('--target', choices=['exe', 'msi', 'zip', 'all'], 
                       default='all', help='Build target')
    
    args = parser.parse_args()
    
    success = True
    
    if args.target in ['exe', 'all']:
        success &= build_windows_exe()
    
    if args.target in ['msi', 'all']:
        success &= build_windows_msi()
    
    if args.target in ['zip', 'all']:
        success &= build_windows_zip()
    
    if success:
        print("Windows build completed successfully!")
        return 0
    else:
        print("Windows build failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())