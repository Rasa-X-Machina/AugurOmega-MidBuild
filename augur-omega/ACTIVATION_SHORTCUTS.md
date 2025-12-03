# Augur Omega: Agent Activation Shortcuts

This document describes all available shortcuts to activate the permanent agent service for Augur Omega.

## Desktop Shortcuts

Two shortcuts have been created for easy access:

1. **Desktop Shortcut**: `Activate_Augur_Omega_Agents.lnk`
   - Located on your desktop for one-click activation
   - Runs the permanent agent activation silently in the background
   - Starts all 38+ specialized agents in permanent mode

2. **Start Menu Shortcut**: `Activate_Augur_Omega_Agents.lnk`
   - Available in your Windows Start Menu
   - Same functionality as desktop shortcut
   - Can be accessed by searching "Activate Augur"

## Batch Scripts

Multiple batch scripts are available in the augur-omega directory:

### Primary Activation Scripts
- `activate_agents_permanent.bat` - Main activation script
- `deactivate_agents_permanent.bat` - Main deactivation script
- `universal_activate_agents.bat` - Works from any location
- `quick_activate_agents.bat` - Quick activation from project directory

### Management Scripts
- `agent_status.bat` - Check current agent status
- `deactivate_agents.bat` - Standard deactivation

### Service Management
- `permanent_agent_service.ps1` - PowerShell management script
- `setup_autostart_permanent_agents.bat` - Configure auto-start on boot

## How to Use

### Desktop/Start Menu Method (Easiest)
1. Double-click the desktop shortcut or search "Activate Augur" in Start Menu
2. The service will activate automatically without needing to navigate to the directory

### Batch Scripts Method
1. Navigate to the augur-omega directory: `cd C:\Users\Dell\Rasa-X-Machina\augur-omega`
2. Run the activation script: `activate_agents_permanent.bat`

### Universal Method
1. Run from anywhere: `universal_activate_agents.bat` (if in PATH)

## Permanent Agent Status

Once activated, the 38+ specialized agents will:
- Run continuously in the background
- Restart automatically if they stop
- Maintain operation between system sessions
- Operate until explicitly deactivated

## To Deactivate

To stop the permanent agent service:
- Run `deactivate_agents_permanent.bat` from the augur-omega directory
- Or run the deactivation script from the desktop/start menu if created
- Or use the PowerShell script with the deactivate command

## Verification

To verify the service status:
- Run `agent_status.bat` from the augur-omega directory
- Or run `python persistent_agent_service.py status`

## Auto-Startup Configuration

Run `setup_autostart_permanent_agents.bat` to configure the service to start automatically on system boot.