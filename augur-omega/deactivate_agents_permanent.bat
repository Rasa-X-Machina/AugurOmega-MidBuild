@echo off
REM Augur Omega: Permanent Agent Deactivation Script
REM Deactivates 38 specialized agents from permanent operation

echo.
echo ================================================
echo  Augur Omega Permanent Agent Service Deactivation
echo ================================================
echo.

REM Remove permanent activation marker
if exist "runtime\permanent_activation_marker.txt" (
    del "runtime\permanent_activation_marker.txt"
    echo Removed permanent activation marker.
) else (
    echo No permanent activation marker found.
)

REM Deactivate the permanent agent service
echo Deactivating permanent agent service...
python persistent_agent_service.py deactivate

echo.
echo ================================================
echo  PERMANENT DEACTIVATION SUCCESSFUL
echo ================================================
echo.
echo The 38 specialized agents are now:  
echo   - Removed from permanent operation
echo   - Will not automatically restart
echo   - Disabled for persistent memory layer
echo.
echo To reactivate: Run activate_agents_permanent.bat
echo ================================================
echo.

pause