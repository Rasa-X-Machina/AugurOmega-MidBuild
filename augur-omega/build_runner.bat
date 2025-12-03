@echo off
REM Augur Omega: Cross-Platform Build Runner
REM Builds executables for all platforms with single command

echo.
echo ================================================
echo  Augur Omega: Multi-Platform Build System
echo ================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.9+ and ensure it's in your PATH
    pause
    exit /b 1
)

REM Navigate to project directory
cd /d "%~dp0"

REM Run the enhanced build system
echo Building Augur Omega for all platforms...
python enhanced_build_system.py %*

echo.
echo Build process completed. Check the 'builds' directory for outputs.
echo.
pause