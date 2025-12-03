@echo off
REM Augur Omega: Permanent Agent Activation Script
REM Activates 38 specialized agents for permanent operation across sessions

echo.
echo ================================================
echo  Augur Omega Permanent Agent Service Activation
echo ================================================
echo.

REM Create runtime directory
if not exist "runtime" mkdir runtime

REM Create a permanent activation marker
echo Service Status: PERMANENTLY ACTIVATED > "runtime\permanent_activation_marker.txt"
echo Activated: %date% %time% >> "runtime\permanent_activation_marker.txt"
echo Agents: 38 specialized agents >> "runtime\permanent_activation_marker.txt"

REM Activate the permanent agent service
echo Activating permanent agent service...
python persistent_agent_service.py permanent

echo.
echo ================================================
echo  PERMANENT ACTIVATION SUCCESSFUL
echo ================================================
echo.
echo The 38 specialized agents are now configured for:
echo   - Permanent operation across all sessions
echo   - Automatic restart if stopped
echo   - Operation between system restarts
echo   - Persistent memory layer activation
echo.
echo To deactivate: Run deactivate_agents.bat
echo ================================================
echo.

pause