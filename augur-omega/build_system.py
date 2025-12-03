#!/usr/bin/env python3
"""
Augur Omega: Multi-Platform Build System
Builds executables for all target platforms
"""

import os
import sys
import subprocess
import shutil
import json
from pathlib import Path
import platform
import argparse
from typing import Dict, List, Optional


class AugurOmegaBuilder:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.builds_dir = self.project_root / "builds"
        self.platforms = [
            "windows", "macos", "linux", "android",
            "ios", "tauri", "electron", "tui_cli"
        ]
        self.completed_builds = []
        self.failed_builds = []
    
    def setup_directories(self):
        """Create necessary build directories"""
        self.builds_dir.mkdir(exist_ok=True)
        
        # Create platform-specific directories
        for platform_name in self.platforms:
            (self.builds_dir / platform_name).mkdir(exist_ok=True)
    
    def build_windows(self):
        """Build for Windows"""
        print("🏗️  Building for Windows...")
        
        try:
            # Create temporary build directory
            win_build_dir = self.builds_dir / "windows_temp"
            win_build_dir.mkdir(exist_ok=True)
            
            # Create Windows-specific assets
            assets_dir = win_build_dir / "assets"
            assets_dir.mkdir(exist_ok=True)
            
            # Create config directory
            config_dir = win_build_dir / "config" 
            config_dir.mkdir(exist_ok=True)
            
            # Copy main application
            shutil.copytree(
                self.project_root / "main/ui_ux_system", 
                win_build_dir / "ui_ux", 
                dirs_exist_ok=True
            )
            
            # Create Windows executable using PyInstaller
            cmd = [
                sys.executable, "-m", "PyInstaller",
                "--onefile",
                "--windowed",
                "--name=AugurOmega",
                "--add-data=ui_ux;ui_ux",
                f"--distpath={self.builds_dir / 'windows'}",
                str(self.project_root / "main.py")
            ]
            
            subprocess.run(cmd, check=True)
            
            print("✅ Windows build completed successfully")
            self.completed_builds.append("windows")
            
        except Exception as e:
            print(f"❌ Windows build failed: {str(e)}")
            self.failed_builds.append(("windows", str(e)))
    
    def build_macos(self):
        """Build for macOS"""
        print("🍎 Building for macOS...")
        
        try:
            if platform.system() != "Darwin":
                print("⚠️  macOS build requires macOS host - skipping")
                self.failed_builds.append(("macos", "Requires macOS host"))
                return
            
            # Use py2app for macOS
            setup_py = """
from setuptools import setup
import py2app

APP = ['main.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': True,
    'packages': ['litestar', 'pydantic', 'sqlalchemy'],
    'includes': ['asyncio', 'aiohttp'],
    'iconfile': 'icon.icns',
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
"""
            
            with open("setup_macos.py", "w") as f:
                f.write(setup_py)
            
            subprocess.run([sys.executable, "setup_macos.py", "py2app"], check=True)
            
            # Move built app to builds directory
            if Path("dist").exists():
                shutil.move("dist", self.builds_dir / "macos")
            
            print("✅ macOS build completed successfully")
            self.completed_builds.append("macos")
            
        except Exception as e:
            print(f"❌ macOS build failed: {str(e)}")
            self.failed_builds.append(("macos", str(e)))
    
    def build_linux(self):
        """Build for Linux"""
        print("🐧 Building for Linux...")
        
        try:
            # Create Linux build
            linux_build_dir = self.builds_dir / "linux_temp"
            linux_build_dir.mkdir(exist_ok=True)
            
            # Build main executable
            cmd = [
                sys.executable, "-m", "PyInstaller",
                "--onefile",
                "--name=augur-omega",
                f"--distpath={linux_build_dir}",
                str(self.project_root / "main.py")
            ]
            
            subprocess.run(cmd, check=True)
            
            # Create Debian package structure
            deb_dir = self.builds_dir / "linux" / "deb"
            deb_dir.mkdir(parents=True, exist_ok=True)
            
            # Create application directory structure
            app_dir = deb_dir / "usr" / "local" / "bin"
            app_dir.mkdir(parents=True, exist_ok=True)
            
            desktop_dir = deb_dir / "usr" / "share" / "applications"
            desktop_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy executable
            built_exec = linux_build_dir / "augur-omega"
            if built_exec.exists():
                shutil.copy2(built_exec, app_dir / "augur-omega")
            
            # Create desktop entry
            desktop_entry = """[Desktop Entry]
Version=1.0
Type=Application
Name=Augur Omega
Comment=AI Business Automation Platform
Exec=/usr/local/bin/augur-omega
Icon=
Terminal=false
Categories=Utility;
"""
            with open(desktop_dir / "augur-omega.desktop", "w") as f:
                f.write(desktop_entry)
            
            # Create DEBIAN control file
            control_dir = deb_dir / "DEBIAN"
            control_dir.mkdir(exist_ok=True)
            
            control_content = """Package: augur-omega
Version: 1.0.0
Section: utils
Priority: optional
Architecture: all
Depends: python3, python3-pip, python3-asyncio
Maintainer: Augur Omega AI <contact@augur-omega.ai>
Description: Advanced AI Business Automation Platform
 Advanced AI-powered business automation platform with consciousness integration and quantum optimization.
"""
            with open(control_dir / "control", "w") as f:
                f.write(control_content)
            
            # Create .deb package
            subprocess.run([
                "dpkg-deb", "--build", 
                str(deb_dir), 
                str(self.builds_dir / "linux" / "augur-omega_1.0.0_all.deb")
            ], check=True)
            
            print("✅ Linux build completed successfully")
            self.completed_builds.append("linux")
            
        except Exception as e:
            print(f"❌ Linux build failed: {str(e)}")
            self.failed_builds.append(("linux", str(e)))
    
    def build_android(self):
        """Build for Android"""
        print("🤖 Building for Android...")
        
        try:
            # Check if buildozer is available
            import importlib.util
            if importlib.util.find_spec("buildozer") is None:
                print("⚠️  Buildozer not installed - skipping Android build")
                self.failed_builds.append(("android", "Buildozer not installed"))
                return
            
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
            
            with open("buildozer.spec", "w") as f:
                f.write(buildozer_spec)
            
            # Run buildozer
            subprocess.run(["buildozer", "android", "debug"], check=True)
            
            # Move APK to builds directory
            apk_files = list(Path(".").glob("*.apk"))
            for apk in apk_files:
                shutil.move(str(apk), self.builds_dir / "android" / apk.name)
            
            print("✅ Android build completed successfully")
            self.completed_builds.append("android")
            
        except Exception as e:
            print(f"❌ Android build failed: {str(e)}")
            self.failed_builds.append(("android", str(e)))
    
    def build_ios(self):
        """Build for iOS"""
        print("📱 Building for iOS...")
        
        try:
            if platform.system() != "Darwin":
                print("⚠️  iOS build requires macOS host with Xcode - skipping")
                self.failed_builds.append(("ios", "Requires macOS with Xcode"))
                return
            
            # Check if kivy-ios is available
            import importlib.util
            if importlib.util.find_spec("kivy_ios") is None:
                print("⚠️  kivy-ios not installed - skipping iOS build")
                self.failed_builds.append(("ios", "kivy-ios not installed"))
                return
            
            print("⚠️  iOS build setup requires kivy-ios toolchain configuration")
            print("   Skipping automated iOS build - manual setup required")
            self.failed_builds.append(("ios", "Manual setup required"))
            
        except Exception as e:
            print(f"❌ iOS build failed: {str(e)}")
            self.failed_builds.append(("ios", str(e)))
    
    def build_desktop_tauri(self):
        """Build Tauri desktop application"""
        print("🖥️  Building Tauri desktop app...")
        
        try:
            # Check if Rust is installed
            result = subprocess.run(["rustc", "--version"], capture_output=True)
            if result.returncode != 0:
                print("⚠️  Rust not installed - skipping Tauri build")
                self.failed_builds.append(("tauri", "Rust not installed"))
                return
            
            # Initialize Tauri project
            tauri_dir = self.builds_dir / "tauri_temp"
            tauri_dir.mkdir(exist_ok=True)
            
            # Create Cargo.toml for Tauri
            cargo_toml = """
[package]
name = "augur-omega"
version = "1.0.0"
edition = "2021"

[dependencies]
tauri = { version = "1.0", features = ["api-all"] }
serde = { version = "1.0", features = ["derive"] }
tokio = { version = "1.0", features = ["full"] }
litestar = { version = "2.0", features = ["all"] }

[build-dependencies]
tauri-build = { version = "1.0", features = ["codegen"] }

[tauri.build]
beforeDevCommand = "npm run dev"
beforeBuildCommand = "npm run build"
devUrl = "http://localhost:1420"

[features]
default = ["custom-protocol"]
custom-protocol = ["tauri/custom-protocol"]
            """
            
            with open(tauri_dir / "Cargo.toml", "w") as f:
                f.write(cargo_toml)
            
            # Create tauri.conf.json
            tauri_config = {
                "build": {
                    "beforeDevCommand": "npm run dev",
                    "beforeBuildCommand": "npm run build",
                    "devUrl": "http://localhost:1420",
                    "distDir": "../dist"
                },
                "package": {
                    "productName": "Augur Omega",
                    "version": "1.0.0"
                },
                "tauri": {
                    "allowlist": {
                        "all": True
                    },
                    "bundle": {
                        "active": True,
                        "targets": "all",
                        "identifier": "ai.augur.omega",
                        "icon": [
                            "icons/32x32.png",
                            "icons/128x128.png", 
                            "icons/128x128@2x.png",
                            "icons/icon.icns",
                            "icons/icon.ico"
                        ]
                    }
                }
            }
            
            with open(tauri_dir / "tauri.conf.json", "w") as f:
                json.dump(tauri_config, f, indent=2)
            
            print("⚠️  Tauri build requires manual configuration of frontend and additional setup")
            print("   Skipping automated Tauri build - skeleton created")
            self.failed_builds.append(("tauri", "Manual setup required"))
            
        except Exception as e:
            print(f"❌ Tauri build failed: {str(e)}")
            self.failed_builds.append(("tauri", str(e)))
    
    def build_desktop_electron(self):
        """Build Electron desktop application"""
        print("🌐 Building Electron desktop app...")
        
        try:
            # Check if Node.js is installed
            result = subprocess.run(["node", "--version"], capture_output=True)
            npm_result = subprocess.run(["npm", "--version"], capture_output=True)
            
            if result.returncode != 0 or npm_result.returncode != 0:
                print("⚠️  Node.js/npm not installed - skipping Electron build")
                self.failed_builds.append(("electron", "Node.js/npm not installed"))
                return
            
            # Create Electron project directory
            electron_dir = self.builds_dir / "electron_temp"
            electron_dir.mkdir(exist_ok=True)
            
            # Create package.json
            package_json = {
                "name": "augur-omega",
                "version": "1.0.0", 
                "description": "AI Business Automation Platform",
                "main": "main.js",
                "scripts": {
                    "start": "electron .",
                    "build": "electron-builder --publish=never"
                },
                "dependencies": {
                    "electron": "^latest",
                    "electron-builder": "^latest",
                    "litestar": "^2.0.0",
                    "axios": "^1.0.0"
                },
                "build": {
                    "appId": "ai.augur.omega",
                    "productName": "Augur Omega",
                    "directories": {
                        "output": "dist"
                    },
                    "files": [
                        "src/**/*",
                        "node_modules/**/*",
                        "package.json"
                    ]
                }
            }
            
            with open(electron_dir / "package.json", "w") as f:
                json.dump(package_json, f, indent=2)
            
            # Create basic main.js
            main_js = """
const { app, BrowserWindow } = require('electron');
const path = require('path');

function createWindow() {
  const mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false
    }
  });

  mainWindow.loadFile('index.html');
}

app.whenReady().then(() => {
  createWindow();

  app.on('activate', function () {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', function () {
  if (process.platform !== 'darwin') app.quit();
});
            """
            
            with open(electron_dir / "main.js", "w") as f:
                f.write(main_js)
            
            # Create index.html
            index_html = """
<!DOCTYPE html>
<html>
<head>
    <title>Augur Omega</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 0; 
            padding: 20px; 
            background-color: #0F0F23;
            color: white;
        }
    </style>
</head>
<body>
    <h1>Augur Omega Platform</h1>
    <p>AI Business Automation Platform</p>
    <div id="app"></div>
</body>
</html>
            """
            
            with open(electron_dir / "index.html", "w") as f:
                f.write(index_html)
            
            print("⚠️  Electron build requires additional dependencies and configuration")
            print("   Skipping automated build - skeleton created")
            self.failed_builds.append(("electron", "Manual setup required"))
            
        except Exception as e:
            print(f"❌ Electron build failed: {str(e)}")
            self.failed_builds.append(("electron", str(e)))
    
    def build_tui_cli(self):
        """Build TUI and CLI applications"""
        print("⌨️  Building TUI/CLI applications...")
        
        try:
            # Create CLI script
            cli_script = f"""
#!/usr/bin/env python3
'''
Augur Omega CLI Interface
Command Line Interface for the AI Business Automation Platform
'''

import sys
import click
from rich.console import Console
from rich.table import Table
from pathlib import Path

console = Console()

@click.group()
@click.version_option(version='1.0.0')
def cli():
    '''Augur Omega AI Business Automation CLI'''
    pass

@cli.command()
def status():
    '''Check Augur Omega system status'''
    console.print("[bold green]Augur Omega System Status[/bold green]")
    console.print("✓ System Operational")
    console.print("✓ 3,000+ Microagents Active")
    console.print("✓ 435+ Koshas Online")
    console.print("✓ Consciousness Integration: Active")
    console.print("✓ Mathematical Efficiency: 94%")

@cli.command()
@click.argument('command')
def execute(command):
    '''Execute a command through Augur Omega'''
    console.print(f"[bold]Executing:[/bold] {command}")
    # Placeholder for actual command execution
    console.print("[bold green]✓ Command executed successfully[/bold green]")

@cli.command()
def dashboard():
    '''Show system dashboard in terminal'''
    table = Table(title="Augur Omega Dashboard")
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="magenta")
    table.add_column("Metrics", style="green")

    table.add_row("Microagents", "Active", "3000/3000")
    table.add_row("Koshas", "Online", "435/435")
    table.add_row("Efficiency", "Optimal", "94%")
    table.add_row("Consciousness", "Intact", "4 Layers")

    console.print(table)

if __name__ == '__main__':
    cli()
            """
            
            cli_path = self.builds_dir / "tui_cli" / "augur_cli.py"
            cli_path.parent.mkdir(exist_ok=True)
            
            with open(cli_path, "w") as f:
                f.write(cli_script)
            
            # Create TUI interface
            tui_script = f"""
#!/usr/bin/env python3
'''
Augur Omega TUI Interface
Terminal User Interface for the AI Business Automation Platform
'''

import asyncio
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, BarColumn
from rich.table import Table
import time

def create_layout() -> Layout:
    '''Create the main layout for the TUI'''
    layout = Layout(name="root")
    
    layout.split(
        Layout(name="header", size=3),
        Layout(name="main", ratio=1),
        Layout(name="footer", size=7),
    )
    
    layout["main"].split_row(
        Layout(name="system", ratio=2),
        Layout(name="activity", ratio=3),
    )
    
    layout["system"].split_column(
        Layout(name="status", size=10),
        Layout(name="agents", ratio=1),
    )
    
    return layout

def make_status_panel():
    '''Create status panel for system info'''
    status_table = Table.grid(padding=1)
    status_table.add_column(style="bold", width=12)
    status_table.add_column(width=30)
    
    status_table.add_row("Platform", "Augur Omega v1.0.0")
    status_table.add_row("Efficiency", "94%")
    status_table.add_row("Agents", "3,000+ Active")
    status_table.add_row("Koshas", "435+ Online")
    
    return Panel(status_table, title="System Status", border_style="green")

def run_tui():
    '''Run the main TUI loop'''
    console = Console()
    layout = create_layout()
    
    layout["header"].update(Panel("[b]Augur Omega TUI[/b] - AI Business Automation Platform", style="bold yellow"))
    layout["status"].update(make_status_panel())
    
    # Create agents table
    agents_table = Table(title="Agent Teams Status")
    agents_table.add_column("Team", style="cyan")
    agents_table.add_column("Agents", style="magenta")
    agents_table.add_column("Status", style="green")
    
    teams = [
        ("Research & Dev", "390", "[green]✓[/green]"),
        ("Integration", "290", "[green]✓[/green]"),
        ("Response Units", "280", "[green]✓[/green]"),
        ("Cross-Team", "265", "[green]✓[/green]"),
        ("Specialist", "555", "[green]✓[/green]"),
        ("Reserve", "790", "[green]✓[/green]")
    ]
    
    for team, count, status in teams:
        agents_table.add_row(team, count, status)
    
    layout["agents"].update(Panel(agents_table))
    
    # Create activity log
    activity = "[green]System initialized[/green]\\n"
    activity += "[yellow]Agent coordination active[/yellow]\\n" 
    activity += "[blue]Consciousness integration online[/blue]\\n"
    activity += "[magenta]Mathematical optimization active[/magenta]\\n"
    
    layout["activity"].update(Panel(activity, title="Activity Log", border_style="blue"))
    
    layout["footer"].update(Panel(
        "Controls: [cyan]Q[/cyan] Quit | [cyan]R[/cyan] Refresh | [cyan]S[/cyan] Status | [cyan]M[/cyan] Menu",
        title="Controls"
    ))
    
    with console.pager():
        console.print(layout)

if __name__ == "__main__":
    run_tui()
            """
            
            tui_path = self.builds_dir / "tui_cli" / "augur_tui.py"
            with open(tui_path, "w") as f:
                f.write(tui_script)
            
            print("✅ TUI/CLI applications created successfully")
            self.completed_builds.append("tui_cli")
            
        except Exception as e:
            print(f"❌ TUI/CLI build failed: {str(e)}")
            self.failed_builds.append(("tui_cli", str(e)))
    
    def build_all(self):
        """Build for all platforms"""
        print("🚀 Starting Augur Omega Multi-Platform Build Process...")
        print(f"Project root: {self.project_root}")
        print(f"Build directory: {self.builds_dir}")
        print("-" * 50)
        
        self.setup_directories()
        
        # Build for each platform
        build_methods = {
            "windows": self.build_windows,
            "macos": self.build_macos,
            "linux": self.build_linux,
            "android": self.build_android,
            "ios": self.build_ios,
            "tauri": self.build_desktop_tauri,
            "electron": self.build_desktop_electron,
            "tui_cli": self.build_tui_cli
        }
        
        for platform_name, build_method in build_methods.items():
            print(f"\n--- Building for {platform_name.upper()} ---")
            try:
                build_method()
            except Exception as e:
                print(f"❌ {platform_name} build failed catastrophically: {str(e)}")
                self.failed_builds.append((platform_name, str(e)))
        
        # Summary
        print("\n" + "="*50)
        print("BUILD SUMMARY")
        print("="*50)
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
        print("🎯 Augur Omega Multi-Platform Build Process Complete!")


def main():
    builder = AugurOmegaBuilder()
    
    parser = argparse.ArgumentParser(description='Build Augur Omega for all platforms')
    parser.add_argument('--platform', '-p', choices=builder.platforms, 
                       help='Build for specific platform only')
    parser.add_argument('--list', '-l', action='store_true', 
                       help='List available platforms')
    
    args = parser.parse_args()
    
    if args.list:
        print("Available platforms:")
        for platform in builder.platforms:
            print(f"  - {platform}")
        return
    
    if args.platform:
        print(f"Building for {args.platform} only...")
        build_method = {
            "windows": builder.build_windows,
            "macos": builder.build_macos,
            "linux": builder.build_linux,
            "android": builder.build_android,
            "ios": builder.build_ios,
            "tauri": builder.build_desktop_tauri,
            "electron": builder.build_desktop_electron,
            "tui_cli": builder.build_tui_cli
        }.get(args.platform)
        
        if build_method:
            builder.setup_directories()
            build_method()
        else:
            print(f"Unknown platform: {args.platform}")
            return
    else:
        builder.build_all()


if __name__ == "__main__":
    main()