#!/bin/bash
# Augur Omega Build System Runner (Linux/macOS)
# Provides a simple interface to run different build configurations

# Function to print header
print_header() {
    clear
    echo "==============================================="
    echo "    Augur Omega Multi-Platform Build System"
    echo "==============================================="
    echo
}

# Function to show menu
show_menu() {
    echo
    echo "Select build option:"
    echo
    echo "[1] Build All Platforms"
    echo "[2] Build Windows (EXE/MSI)"
    echo "[3] Build macOS (APP/DMG) "
    echo "[4] Build Linux (DEB/RPM)"
    echo "[5] Build Android (APK)"
    echo "[6] Build Desktop Apps (Tauri/Electron)"
    echo "[7] Build TUI/CLI"
    echo "[8] Clean Build Directory"
    echo "[0] Exit"
    echo
}

# Main loop
while true; do
    print_header
    show_menu
    
    read -p "Enter your choice (0-8): " choice
    
    case $choice in
        1)
            echo
            echo "Building all platforms..."
            python3 build_orchestrator.py
            read -p "Press Enter to continue..."
            ;;
        2)
            echo
            echo "Building Windows (EXE/MSI)..."
            python3 build_orchestrator.py --platform windows
            read -p "Press Enter to continue..."
            ;;
        3)
            echo
            echo "Building macOS (APP/DMG)..."
            echo "Note: This requires macOS host"
            python3 build_orchestrator.py --platform macos
            read -p "Press Enter to continue..."
            ;;
        4)
            echo
            echo "Building Linux (DEB/RPM)..."
            python3 build_orchestrator.py --platform linux
            read -p "Press Enter to continue..."
            ;;
        5)
            echo
            echo "Building Android (APK)..."
            python3 build_orchestrator.py --platform android
            read -p "Press Enter to continue..."
            ;;
        6)
            echo
            echo "Building Desktop Apps (Tauri/Electron)..."
            python3 build_orchestrator.py --platform desktop
            read -p "Press Enter to continue..."
            ;;
        7)
            echo
            echo "Building TUI/CLI..."
            python3 build_orchestrator.py --platform tui_cli
            read -p "Press Enter to continue..."
            ;;
        8)
            echo
            echo "Cleaning build directory..."
            python3 build_orchestrator.py --clean
            read -p "Press Enter to continue..."
            ;;
        0)
            echo
            echo "Thank you for using Augur Omega Build System!"
            exit 0
            ;;
        *)
            echo "Invalid choice. Please select 0-8."
            read -p "Press Enter to continue..."
            ;;
    esac
done