@echo off
REM Augur Omega: Boot Service Activation Script
REM This script ensures the permanent agent service starts on system boot

echo Setting up Augur Omega Permanent Agent Service for automatic startup...

REM Get the current directory (where this script is located)
set SCRIPT_DIR=%~dp0

REM Register the service to start on boot using schtasks
schtasks /create /tn "AugurOmega_PermanentAgentService" /tr "python %SCRIPT_DIR%persistent_agent_service.py permanent" /sc onstart /ru "SYSTEM" /rl HIGHEST /f

if %errorlevel% equ 0 (
    echo Successfully created boot startup task for Augur Omega Permanent Agent Service
    echo The 38 specialized agents will start automatically on system boot
) else (
    echo Failed to create boot startup task
    echo Manual startup will be required
)

REM Also create a user login task as backup
schtasks /create /tn "AugurOmega_PermanentAgentService_User" /tr "python %SCRIPT_DIR%persistent_agent_service.py permanent" /sc onlogon /ru %USERNAME% /f

if %errorlevel% equ 0 (
    echo Created secondary login startup task as backup
) else (
    echo Failed to create login startup task (this is a backup, not critical)
)

echo.
echo Permanent agent service is configured to start automatically.
echo All 38 specialized agents will run persistently across sessions until explicitly deactivated.
echo.
echo To verify: Run 'schtasks /query /tn "AugurOmega_PermanentAgentService"'
echo To deactivate: Run 'deactivate_agents_permanent.bat'

pause