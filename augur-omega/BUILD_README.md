# Augur Omega: Multi-Platform Build System

This directory contains the complete build infrastructure for Augur Omega across all target platforms.

## 🎯 Supported Platforms

### Desktop Platforms
- **Windows**: EXE, MSI installer, ZIP archives
- **macOS**: APP bundle, PKG installer, DMG disk image  
- **Linux**: DEB (Debian/Ubuntu), RPM (Fedora/RHEL), TAR.GZ archives, SNAP, Flatpak

### Mobile Platforms  
- **Android**: APK, AAB (Android App Bundle) with Kotlin
- **iOS**: IPA with Swift

### Web & PWA
- **Progressive Web App**: Modern web application with offline capabilities
- **SPA/MPA**: Single/Multi-page application architecture

### Desktop Frameworks
- **Tauri**: Rust-based desktop applications with smaller footprints
- **Electron**: Cross-platform desktop applications with web technologies

### Terminal Interfaces
- **TUI (Terminal User Interface)**: Rich terminal interface with visual elements
- **CLI (Command Line Interface)**: Command-line interface for scripting and automation

## 🛠️ Build System Architecture

```
build_system/
├── build_config.toml          # Build configurations for all platforms
├── build_system.py            # Main build orchestration system
├── build.py                   # Build entry point
├── main.py                    # Application entry point
├── requirements.txt           # Complete dependency list
├── Dockerfile.build           # Linux distribution build
├── scripts/                   # Platform-specific build scripts
│   ├── build_windows.py
│   ├── build_macos.py  
│   ├── build_linux.py
│   ├── build_android.py
│   ├── build_ios.py
│   ├── build_desktop.py
│   └── build_tui_cli.py
├── builds/                    # Build output directory (created during build)
│   ├── windows/
│   ├── macos/
│   ├── linux/
│   ├── android/
│   ├── ios/
│   ├── tauri/
│   ├── electron/
│   └── tui_cli/
└── README.md                  # This file
```

## 🔧 Build Prerequisites

### Universal Requirements
- Python 3.9+ with pip
- Git for version control
- 4GB+ free disk space for builds

### Platform-Specific Requirements

#### Windows
- MSVC Build Tools or Visual Studio Build Tools
- NSIS for installer generation (optional)

#### macOS
- Xcode Command Line Tools (`xcode-select --install`)
- Xcode IDE for iOS builds (optional)

#### Linux
- GCC compiler toolchain
- Development headers for Python, SSL, cryptographic libraries
- dpkg-deb for Debian packaging (usually pre-installed)

#### Android
- Android SDK
- Buildozer and python-for-android
- Java JDK 8+

#### iOS
- Xcode with iOS SDK
- Apple Developer Account
- kivy-ios toolchain

#### Tauri
- Rust programming language
- Cargo package manager

#### Electron
- Node.js and npm
- Electron and electron-builder

## 🚀 Building Augur Omega

### Build All Platforms
```bash
python build.py
```

### Build Specific Platform
```bash
python build.py --platform windows
python build.py --platform linux
python build.py --platform android
# etc.
```

### List Available Platforms
```bash
python build.py --list
```

## ⚙️ Build Configuration

The build system uses `build_config.toml` for configuration:

```toml
[build_system]
name = "augur-omega-builder"
version = "1.0.0"

[windows]
build_script = "scripts/build_windows.py"
output_dir = "builds/windows"
targets = ["exe", "msi", "zip"]
requirements = ["pyinstaller>=5.0", "cx_freeze", "nsis"]

[macos]
build_script = "scripts/build_macos.py"
output_dir = "builds/macos"
targets = ["app", "pkg", "dmg"]
requirements = ["py2app", "pyinstaller>=5.0"]
# ... and so on for each platform
```

## 📁 Output Structure

After building, the `builds/` directory will contain:

```
builds/
├── windows/          # Windows executables and installers
│   ├── AugurOmega.exe
│   └── installer.exe
├── macos/            # macOS applications and installers  
│   ├── AugurOmega.app/
│   └── AugurOmega.pkg
├── linux/            # Linux packages and archives
│   ├── augur-omega_1.0.0_amd64.deb
│   ├── augur-omega-1.0.0.x86_64.rpm
│   └── augur-omega.tar.gz
├── android/          # Android APKs and AABs
│   └── augur-omega-1.0.0.apk
├── ios/              # iOS IPA files
│   └── AugurOmega.ipa
├── tauri/            # Tauri desktop applications
│   └── augur-omega/
├── electron/         # Electron desktop applications
│   └── dist/
└── tui_cli/          # Terminal interface scripts
    ├── augur_cli.py
    └── augur_tui.py
```

## 🚢 Deployment

### Desktop Platforms
- Windows: Distribute installer or portable EXE
- macOS: Distribute APP bundle or PKG installer
- Linux: Distribute DEB/RPM packages or portable TAR/GZ archive

### Mobile Platforms
- Android: Upload AAB to Google Play Console, APK for direct distribution
- iOS: Upload IPA to Apple App Store through Transporter

### Web/PWA
- Host the generated static files on a web server
- Ensure proper CORS and security headers

### Tauri/Electron
- Distribute the generated application bundles
- Tauri produces smaller executables than Electron

## 🧪 Testing Built Applications

Each platform build includes basic functionality tests:

```bash
# Test Windows build
./builds/windows/AugurOmega.exe --test

# Test Linux build  
./builds/linux/augur-omega --status

# Test Android app
adb install builds/android/augur-omega-1.0.0.apk

# Test TUI/CLI
python builds/tui_cli/augur_cli.py status
```

## 🔄 Continuous Integration

The build system is designed for CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
name: Build & Release
on: [push, pull_request]

jobs:
  build-windows:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build for Windows
        run: python build.py --platform windows
      - name: Upload Windows artifacts
        uses: actions/upload-artifact@v3
        with:
          name: windows-build
          path: builds/windows/

  build-linux:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build for Linux
        run: python build.py --platform linux
      - name: Upload Linux artifacts
        uses: actions/upload-artifact@v3
        with:
          name: linux-build
          path: builds/linux/
```

## 📋 Supported Features Matrix

| Platform | TUI | CLI | GUI | Web | Mobile | AI Integration | Security |
|----------|-----|-----|-----|-----|--------|----------------|----------|
| Windows  | ✅  | ✅  | ✅  | ✅  | ❌     | ✅             | ✅       |
| macOS    | ✅  | ✅  | ✅  | ✅  | ❌     | ✅             | ✅       |
| Linux    | ✅  | ✅  | ✅  | ✅  | ❌     | ✅             | ✅       |
| Android  | ❌  | ❌  | ✅  | ❌  | ✅     | ✅             | ✅       |
| iOS      | ❌  | ❌  | ✅  | ❌  | ✅     | ✅             | ✅       |
| Tauri    | ❌  | ❌  | ✅  | ❌  | ❌     | ✅             | ✅       |
| Electron | ❌  | ❌  | ✅  | ❌  | ❌     | ✅             | ✅       |
| Web/PWA  | ❌  | ❌  | ✅  | ✅  | ❌     | ✅             | ✅       |

## 📞 Support & Troubleshooting

If you encounter build issues:

1. Ensure all prerequisites are installed
2. Check Python version (3.9+ required)
3. Verify sufficient disk space
4. Check platform-specific requirements
5. Review the build logs in the respective platform directories

For support, create an issue in the repository with:
- Your operating system and version
- Python version (`python --version`)
- Build command used
- Complete error message
- Relevant portions of the build log

## 📄 License

This build system is part of the Augur Omega platform and is licensed under the same terms as the main project.