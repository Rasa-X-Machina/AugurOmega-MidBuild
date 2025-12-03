#!/usr/bin/env python3
"""
Augur Omega: Linux Build Script
Builds Linux packages (DEB, RPM, etc.)
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import platform
import argparse


def build_linux_exe():
    """Build Linux executable using PyInstaller"""
    print("Building Linux executable...")
    
    project_root = Path(__file__).parent.parent
    builds_dir = project_root / "builds" / "linux" / "exe"
    builds_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--onefile",
            "--name=augur-omega",
            f"--distpath={builds_dir}",
            str(project_root / "main.py")
        ]
        
        subprocess.run(cmd, check=True, cwd=project_root)
        print("Linux executable built successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to build Linux executable: {e}")
        return False


def build_linux_deb():
    """Build Linux DEB package"""
    print("Building Linux DEB package...")
    
    project_root = Path(__file__).parent.parent
    exe_dir = project_root / "builds" / "linux" / "exe"
    deb_dir = project_root / "builds" / "linux" / "deb"
    deb_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if executable exists, build if not
    if not any(exe_dir.glob("*")):
        print("Executable not found, building first...")
        if not build_linux_exe():
            return False
    
    # Create temporary build directory
    temp_dir = deb_dir / "temp"
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir(exist_ok=True)
    
    # Create DEBIAN package structure
    deb_pkg_dir = temp_dir / "augur-omega_1.0.0_amd64"
    app_dir = deb_pkg_dir / "usr" / "local" / "bin"
    app_dir.mkdir(parents=True)
    desktop_dir = deb_pkg_dir / "usr" / "share" / "applications"
    desktop_dir.mkdir(parents=True)
    icon_dir = deb_pkg_dir / "usr" / "share" / "icons" / "hicolor" / "256x256" / "apps"
    icon_dir.mkdir(parents=True)
    
    # Copy executable
    exe_files = list(exe_dir.glob("*"))
    if exe_files:
        exe_file = exe_files[0]
        shutil.copy2(exe_file, app_dir / "augur-omega")
    
    # Create desktop entry
    desktop_entry = """[Desktop Entry]
Version=1.0
Type=Application
Name=Augur Omega
Comment=AI Business Automation Platform
Exec=/usr/local/bin/augur-omega
Icon=augur-omega
Terminal=false
Categories=Utility;AI;
"""
    with open(desktop_dir / "augur-omega.desktop", "w") as f:
        f.write(desktop_entry)

    # Create DEBIAN control file
    control_dir = deb_pkg_dir / "DEBIAN"
    control_dir.mkdir(exist_ok=True)

    control_content = """Package: augur-omega
Version: 1.0.0
Section: utils
Priority: optional
Architecture: amd64
Depends: python3, python3-pip
Maintainer: Augur Omega AI <contact@augur-omega.ai>
Description: Advanced AI Business Automation Platform
 Advanced AI-powered business automation platform with consciousness integration and quantum optimization.
"""
    with open(control_dir / "control", "w") as f:
        f.write(control_content)

    # Build .deb package
    try:
        subprocess.run([
            "dpkg-deb", "--build", "--root-owner-group",
            str(deb_pkg_dir),
            str(deb_dir / "augur-omega_1.0.0_amd64.deb")
        ], check=True)
        
        print("Linux DEB package built successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to build Linux DEB package: {e}")
        return False
    except FileNotFoundError:
        print("dpkg-deb not found, skipping DEB build")
        return False


def build_linux_rpm():
    """Build Linux RPM package"""
    print("Building Linux RPM package...")
    
    project_root = Path(__file__).parent.parent
    exe_dir = project_root / "builds" / "linux" / "exe"
    rpm_dir = project_root / "builds" / "linux" / "rpm"
    rpm_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if executable exists, build if not
    if not any(exe_dir.glob("*")):
        print("Executable not found, building first...")
        if not build_linux_exe():
            return False
    
    try:
        # Check if fpm is available
        result = subprocess.run(["fpm", "--version"], capture_output=True)
        if result.returncode != 0:
            print("fpm not available, skipping RPM build")
            return False
        
        # Create temporary build directory
        temp_dir = rpm_dir / "temp"
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        temp_dir.mkdir(exist_ok=True)
        
        # Create package structure (similar to DEB)
        pkg_dir = temp_dir / "augur-omega"
        app_dir = pkg_dir / "usr" / "local" / "bin"
        app_dir.mkdir(parents=True)
        desktop_dir = pkg_dir / "usr" / "share" / "applications"
        desktop_dir.mkdir(parents=True)
        
        # Copy executable
        exe_files = list(exe_dir.glob("*"))
        if exe_files:
            exe_file = exe_files[0]
            shutil.copy2(exe_file, app_dir / "augur-omega")
        
        # Create desktop entry
        desktop_entry = """[Desktop Entry]
Version=1.0
Type=Application
Name=Augur Omega
Comment=AI Business Automation Platform
Exec=/usr/local/bin/augur-omega
Icon=augur-omega
Terminal=false
Categories=Utility;AI;
"""
        with open(desktop_dir / "augur-omega.desktop", "w") as f:
            f.write(desktop_entry)
        
        # Build RPM package using fpm
        subprocess.run([
            "fpm", "-s", "dir", "-t", "rpm",
            "-n", "augur-omega", "-v", "1.0.0",
            "-C", str(pkg_dir.parent),
            "--prefix", "/usr",
            "-p", str(rpm_dir / "augur-omega-1.0.0.x86_64.rpm")
        ], check=True)
        
        print("Linux RPM package built successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to build Linux RPM package: {e}")
        return False
    except FileNotFoundError:
        print("fpm not found, skipping RPM build")
        return False


def build_linux_tar():
    """Create Linux tar.gz archive"""
    print("Creating Linux tar.gz archive...")
    
    project_root = Path(__file__).parent.parent
    exe_dir = project_root / "builds" / "linux" / "exe"
    tar_dir = project_root / "builds" / "linux" / "tar"
    tar_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if executable exists, build if not
    if not any(exe_dir.glob("*")):
        print("Executable not found, building first...")
        if not build_linux_exe():
            return False
    
    try:
        shutil.make_archive(
            str(tar_dir / "augur-omega-linux"),
            'gztar',
            root_dir=exe_dir
        )
        print("Linux tar.gz archive created successfully")
        return True
    except Exception as e:
        print(f"Failed to create Linux tar.gz archive: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='Build Augur Omega for Linux')
    parser.add_argument('--target', choices=['exe', 'deb', 'rpm', 'tar', 'all'], 
                       default='all', help='Build target')
    
    args = parser.parse_args()
    
    success = True
    
    if args.target in ['exe', 'all']:
        success &= build_linux_exe()
    
    if args.target in ['deb', 'all']:
        success &= build_linux_deb()
    
    if args.target in ['rpm', 'all']:
        success &= build_linux_rpm()
    
    if args.target in ['tar', 'all']:
        success &= build_linux_tar()
    
    if success:
        print("Linux build completed successfully!")
        return 0
    else:
        print("Linux build failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())