@echo off
REM Augur Omega: Quick Agent Activation
REM This file can be copied to Windows PATH to run from anywhere

REM First, find the Augur Omega installation directory
for /f "delims=" %%i in ('cd') do set CURRENT_DIR=%%i

REM If we're in the augur-omega directory, run directly
if exist "persistent_agent_service.py" (
    python persistent_agent_service.py permanent
    goto :eof
)

REM Otherwise, look for the augur-omega directory
REM This assumes the standard path, but could be made more flexible
if exist "C:\Users\Dell\Rasa-X-Machina\augur-omega\persistent_agent_service.py" (
    cd /d "C:\Users\Dell\Rasa-X-Machina\augur-omega"
    python persistent_agent_service.py permanent
    cd /d "%CURRENT_DIR%"
) else (
    echo Augur Omega installation not found. Please run from the augur-omega directory.
)