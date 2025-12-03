#!/usr/bin/env python3
"""
Augur Omega: Desktop Build Script
Builds Tauri and Electron desktop applications
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import argparse


def build_tauri_app():
    """Build Tauri desktop application"""
    print("Building Tauri desktop app...")
    
    project_root = Path(__file__).parent.parent
    builds_dir = project_root / "builds" / "desktop" / "tauri"
    builds_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Check if Rust is installed
        result = subprocess.run(["rustc", "--version"], capture_output=True)
        if result.returncode != 0:
            print("Rust not installed, skipping Tauri build")
            return False

        # Install Tauri CLI if not already installed
        subprocess.run(["cargo", "install", "tauri-cli"], check=True)

        # Create Tauri project directory
        tauri_dir = builds_dir / "temp"
        if tauri_dir.exists():
            shutil.rmtree(tauri_dir)
        tauri_dir.mkdir(exist_ok=True)

        # Initialize a new Rust project
        os.chdir(tauri_dir)
        subprocess.run(["cargo", "init"], check=True)
        
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

[build-dependencies]
tauri-build = { version = "1.0", features = ["codegen"] }

[features]
default = ["custom-protocol"]
custom-protocol = ["tauri/custom-protocol"]
        """

        with open("Cargo.toml", "w") as f:
            f.write(cargo_toml)

        # Create tauri.conf.json
        tauri_config = {
            "build": {
                "beforeDevCommand": "",
                "beforeBuildCommand": "",
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
                    ],
                    "resources": [],
                    "externalBin": [],
                    "copyright": "",
                    "category": "DeveloperTool",
                    "shortDescription": "",
                    "longDescription": ""
                }
            }
        }

        with open("tauri.conf.json", "w") as f:
            import json
            json.dump(tauri_config, f, indent=2)

        # Build Tauri app
        subprocess.run(["cargo", "tauri", "build"], check=True)

        # Move built app to output directory
        target_dir = tauri_dir / "target"
        if target_dir.exists():
            release_dir = target_dir / "release"
            if release_dir.exists():
                for build_file in release_dir.rglob("*"):
                    if build_file.is_file() and build_file.suffix in [".exe", ".app", ".deb", ".rpm"]:
                        shutil.copy2(build_file, builds_dir / build_file.name)

        print("Tauri desktop app built successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to build Tauri app: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error during Tauri build: {e}")
        return False
    finally:
        os.chdir(project_root)


def build_electron_app():
    """Build Electron desktop application"""
    print("Building Electron desktop app...")
    
    project_root = Path(__file__).parent.parent
    builds_dir = project_root / "builds" / "desktop" / "electron"
    builds_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Check if Node.js is installed
        result = subprocess.run(["node", "--version"], capture_output=True)
        npm_result = subprocess.run(["npm", "--version"], capture_output=True)

        if result.returncode != 0 or npm_result.returncode != 0:
            print("Node.js/npm not installed, skipping Electron build")
            return False

        # Create Electron project directory
        electron_dir = builds_dir / "temp"
        if electron_dir.exists():
            shutil.rmtree(electron_dir)
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
                "electron-builder": "^latest"
            },
            "devDependencies": {
                "electron": "^latest",
                "electron-builder": "^latest"
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
                ],
                "mac": {
                    "target": ["dmg", "zip"]
                },
                "win": {
                    "target": ["nsis", "zip"]
                },
                "linux": {
                    "target": ["AppImage", "deb", "rpm"]
                }
            }
        }

        with open(electron_dir / "package.json", "w") as f:
            import json
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

  // Load the Augur Omega UI if available
  // For now, we'll create a basic interface
  mainWindow.loadFile('index.html');
  
  // Open DevTools for debugging
  // mainWindow.webContents.openDevTools();
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
            background: linear-gradient(135deg, #0F0F23 0%, #1a1a2e 100%);
            color: white;
            min-height: 100vh;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        header {
            text-align: center;
            padding: 20px 0;
            border-bottom: 1px solid #444;
        }
        h1 {
            margin: 0;
            font-size: 2.5em;
            background: linear-gradient(to right, #00c9ff, #92fe9d);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .status-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }
        .status-card {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            padding: 20px;
            text-align: center;
        }
        .status-card h3 {
            margin-top: 0;
            color: #00c9ff;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Augur Omega Platform</h1>
            <p>AI Business Automation Platform</p>
        </header>
        
        <div class="status-grid">
            <div class="status-card">
                <h3>System Status</h3>
                <p>Operational</p>
            </div>
            <div class="status-card">
                <h3>Microagents</h3>
                <p>3,000+ Active</p>
            </div>
            <div class="status-card">
                <h3>Koshas</h3>
                <p>435+ Online</p>
            </div>
            <div class="status-card">
                <h3>Efficiency</h3>
                <p>94%</p>
            </div>
        </div>
        
        <div id="app"></div>
    </div>
    
    <script>
        // In a real implementation, this would connect to the Augur Omega backend
        console.log('Augur Omega Electron App Loaded');
    </script>
</body>
</html>
        """

        with open(electron_dir / "index.html", "w") as f:
            f.write(index_html)

        # Change to electron directory and install dependencies
        os.chdir(electron_dir)
        subprocess.run(["npm", "install"], check=True)
        subprocess.run(["npm", "run", "build"], check=True)

        # Move built app to output directory
        dist_dir = electron_dir / "dist"
        if dist_dir.exists():
            for build_file in dist_dir.rglob("*"):
                if build_file.is_file() and build_file.suffix in [".exe", ".app", ".deb", ".rpm", ".AppImage"]:
                    shutil.copy2(build_file, builds_dir / build_file.name)

        print("Electron desktop app built successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to build Electron app: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error during Electron build: {e}")
        return False
    finally:
        os.chdir(project_root)


def main():
    parser = argparse.ArgumentParser(description='Build Augur Omega desktop applications')
    parser.add_argument('--target', choices=['tauri', 'electron', 'all'], 
                       default='all', help='Build target')
    
    args = parser.parse_args()
    
    success = True
    
    if args.target in ['tauri', 'all']:
        success &= build_tauri_app()
    
    if args.target in ['electron', 'all']:
        success &= build_electron_app()
    
    if success:
        print("Desktop build completed successfully!")
        return 0
    else:
        print("Desktop build failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())