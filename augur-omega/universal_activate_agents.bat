@echo off
REM Augur Omega: Universal Agent Activation Script
REM Can be run from any location to activate permanent agents

SET AUGUR_OMEGA_ROOT=C:\Users\Dell\Rasa-X-Machina\augur-omega

echo Activating Augur Omega Permanent Agent Service...
echo Location: %AUGUR_OMEGA_ROOT%

REM Check if the directory exists
if not exist "%AUGUR_OMEGA_ROOT%" (
    echo Error: Augur Omega directory not found at %AUGUR_OMEGA_ROOT%
    echo Please verify the installation path.
    pause
    exit /b 1
)

REM Change to the agent directory and activate permanent service
cd /d "%AUGUR_OMEGA_ROOT%"
call activate_agents_permanent.bat

echo.
echo Augur Omega Permanent Agent Service activated successfully!
echo The 38+ specialized agents are now running persistently.
echo.
pause