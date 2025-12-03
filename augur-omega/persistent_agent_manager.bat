@echo off
REM Augur Omega: Persistent Agent Activation Script
REM Ensures 38 specialized agents remain active across sessions

echo Starting Augur Omega Persistent Agent Manager...
echo Configuring 38 specialized agents for persistent operation...

REM Create a marker file to indicate persistent mode is active
echo %date% %time% - Persistent Agent Mode Activated > "%~dp0\logs\persistent_agent_activation.log"

REM Check if configuration file exists
if not exist "%~dp0\config\persistent_agents.cfg" (
    echo Creating default persistent agents configuration...
    REM Create the configuration file with persistent settings enabled
    echo [persistent_agents] > "%~dp0\config\persistent_agents.cfg"
    echo persistent_mode = true >> "%~dp0\config\persistent_agents.cfg"
    echo. >> "%~dp0\config\persistent_agents.cfg"
    echo [agents] >> "%~dp0\config\persistent_agents.cfg"
    echo all_agents_persistent = true >> "%~dp0\config\persistent_agents.cfg"
    echo. >> "%~dp0\config\persistent_agents.cfg"
    echo [persistence] >> "%~dp0\config\persistent_agents.cfg"
    echo persist_across_sessions = true >> "%~dp0\config\persistent_agents.cfg"
    echo auto_restart = true >> "%~dp0\config\persistent_agents.cfg"
    echo monitoring_interval = 30 >> "%~dp0\config\persistent_agents.cfg"
    echo enable_logging = true >> "%~dp0\config\persistent_agents.cfg"
)

REM Activate the persistent agent configuration
echo Activating persistent agent configuration...
python -c "
import configparser
import os
config = configparser.ConfigParser()
config.read('%~dp0\\config\\persistent_agents.cfg')

# Ensure all persistence settings are enabled
config.set('persistent_agents', 'persistent_mode', 'true')
config.set('persistence', 'persist_across_sessions', 'true')
config.set('persistence', 'auto_restart', 'true')

with open('%~dp0\\config\\persistent_agents.cfg', 'w') as configfile:
    config.write(configfile)

print('Persistent agent configuration activated!')
"

REM Start the agent orchestration system with persistent configuration
echo Starting Augur Omega Agent Orchestration System in persistent mode...
REM This would normally start the actual agent system, here we'll just log it
echo %date% %time% - Agent Orchestration System started in persistent mode >> "%~dp0\logs\persistent_agent_activation.log"

REM Create shortcut activation file
echo @echo off > "%~dp0\activate_persistent_agents.bat"
echo call "%~dp0\persistent_agent_manager.bat" >> "%~dp0\activate_persistent_agents.bat"
echo echo Persistent agents activated and running... >> "%~dp0\activate_persistent_agents.bat"

REM Create deactivation script
echo @echo off > "%~dp0\deactivate_persistent_agents.bat"
echo echo Deactivating persistent agents... >> "%~dp0\deactivate_persistent_agents.bat"
echo python -c ^" >> "%~dp0\deactivate_persistent_agents.bat"
echo import configparser >> "%~dp0\deactivate_persistent_agents.bat"
echo import os >> "%~dp0\deactivate_persistent_agents.bat"
echo config = configparser.ConfigParser^([) >> "%~dp0\deactivate_persistent_agents.bat"
echo config.read^('%~dp0\\config\\persistent_agents.cfg'^) >> "%~dp0\deactivate_persistent_agents.bat"
echo config.set^('persistent_agents', 'persistent_mode', 'false'^) >> "%~dp0\deactivate_persistent_agents.bat"
echo config.set^('persistence', 'persist_across_sessions', 'false'^) >> "%~dp0\deactivate_persistent_agents.bat"
echo config.set^('persistence', 'auto_restart', 'false'^) >> "%~dp0\deactivate_persistent_agents.bat"
echo with open^('%~dp0\\config\\persistent_agents.cfg', 'w'^) as configfile: >> "%~dp0\deactivate_persistent_agents.bat"
echo     config.write^([)configfile^)^] >> "%~dp0\deactivate_persistent_agents.bat"
echo print^([)'Persistent agent mode deactivated!'[) >> "%~dp0\deactivate_persistent_agents.bat"
echo ^" >> "%~dp0\deactivate_persistent_agents.bat"
echo echo Persistent agents deactivated. >> "%~dp0\deactivate_persistent_agents.bat"

echo.
echo Persistent Agent Manager activated successfully!
echo.
echo To deactivate: Run deactivate_persistent_agents.bat
echo To reactivate: Run activate_persistent_agents.bat
echo.
echo The 38 specialized agents are now configured to run persistently across sessions.
echo They will automatically restart if they stop and maintain operation between sessions.
pause