# Augur Omega Multi-Platform Build System

## Overview

The Augur Omega build system is designed to create executables and installation packages for multiple platforms from a single codebase. The system supports:

- **Windows**: EXE, MSI, ZIP distributions
- **macOS**: APP, DMG installers
- **Linux**: DEB, RPM, tar.gz packages
- **Android**: APK files
- **iOS**: IPA files
- **Desktop**: Tauri and Electron applications
- **TUI/CLI**: Terminal User Interface and Command Line Interface applications

## Build System Architecture

The build system consists of:

1. **Master Orchestrator** (`build_orchestrator.py`): Coordinates all builds
2. **Enhanced Builder** (`enhanced_build_system.py`): Main build logic
3. **Platform-Specific Scripts**: Individual build scripts for each platform
4. **Configuration File** (`build_config.toml`): Build settings and dependencies

## Prerequisites

Before running the build system, ensure you have:

- Python 3.9+
- Rust (for Tauri builds)
- Node.js and npm (for Electron builds)
- Xcode (for iOS builds on macOS)
- Android SDK/NDK (for Android builds)

## Usage

### Building All Platforms

```bash
python build_orchestrator.py
```

### Building Specific Platform

```bash
# Build for Windows only
python build_orchestrator.py --platform windows

# Build for Linux with specific target
python build_orchestrator.py --platform linux --target deb

# List all available platforms
python build_orchestrator.py --list
```

### Using the Enhanced Build System Directly

```bash
# Build all platforms
python enhanced_build_system.py

# Build specific platform
python enhanced_build_system.py --platform android

# Clean build directory and build
python enhanced_build_system.py --clean --platform tauri
```

## Platform-Specific Scripts

Each platform has its own build script in the `scripts/` directory:

- `scripts/build_windows.py` - Builds Windows executables and installers
- `scripts/build_macos.py` - Builds macOS applications and DMGs
- `scripts/build_linux.py` - Builds Linux packages
- `scripts/build_android.py` - Builds Android APKs
- `scripts/build_ios.py` - Builds iOS IPAs
- `scripts/build_desktop.py` - Builds Tauri and Electron apps
- `scripts/build_tui_cli.py` - Builds TUI and CLI applications

## Build Outputs

All build outputs are placed in the `builds/` directory:

```
builds/
├── windows/
│   ├── exe/      # Windows executables
│   ├── msi/      # Windows installers
│   └── zip/      # Windows ZIP distributions
├── macos/
│   ├── app/      # macOS applications
│   └── dmg/      # macOS disk images
├── linux/
│   ├── exe/      # Linux executables
│   ├── deb/      # Debian packages
│   ├── rpm/      # Red Hat packages
│   └── tar/      # Tar archives
├── android/
│   └── apk/      # Android packages
├── ios/
│   └── ipa/      # iOS packages
├── desktop/
│   ├── tauri/    # Tauri applications
│   └── electron/ # Electron applications
└── tui_cli/
    ├── cli/      # Command line interface
    ├── tui/      # Terminal user interface
    └── install_cli.sh # Installation script
```

## Configuration

The build system can be configured using `build_config.toml`:

```toml
[windows]
targets = ["exe", "msi", "zip"]
requirements = ["pyinstaller>=5.0", "cx_freeze", "nsis"]

[macos]
targets = ["app", "dmg"]
requirements = ["py2app", "pyinstaller>=5.0"]

[linux]
targets = ["deb", "rpm", "tar.gz"]
requirements = ["pyinstaller>=5.0", "fpm"]
```

## Troubleshooting

### Common Issues

1. **Missing Dependencies**: The build system will attempt to install required packages, but some system-level dependencies may need manual installation.

2. **Platform Restrictions**: iOS and macOS builds require macOS hosts. Android builds may require additional Android SDK setup.

3. **Permission Issues**: On Unix systems, ensure you have write permissions to the build directory.

### Verbose Output

For detailed build information, run with Python's verbose flag:

```bash
python -v build_orchestrator.py --platform linux
```

## Extending the Build System

To add support for new platforms or modify existing ones:

1. Create a new script in the `scripts/` directory following the existing pattern
2. Update the orchestrator to include the new platform
3. Add configuration options to `build_config.toml`
4. Update this documentation

## Build Reports

After each build, a detailed report is generated at `builds/build_report.json` containing:
- Timestamp of the build
- Platform and Python version
- List of completed and failed builds
- Build directory location