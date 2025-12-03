# Augur Omega: Persistent Agent Activation Shortcut
# PowerShell script to manage persistent agent activation

param(
    [Parameter(Position=0)]
    [ValidateSet("Activate", "Deactivate", "Status", "Setup", IgnoreCase = $true)]
    [string]$Command = "Status"
)

# Define paths
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$configDir = Join-Path $scriptDir "config"
$logDir = Join-Path $scriptDir "logs"

# Create directories if they don't exist
if (!(Test-Path $configDir)) {
    New-Item -ItemType Directory -Path $configDir -Force
}

if (!(Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir -Force
}

Write-Host "Augur Omega Persistent Agent Manager" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan

switch ($Command.ToLower()) {
    "activate" {
        Write-Host "Activating persistent agents..." -ForegroundColor Green
        $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
        if ($pythonCmd) {
            & python persistent_agent_manager.py activate
        } else {
            Write-Host "Python not found. Please ensure Python is installed and in PATH." -ForegroundColor Red
        }
    }
    
    "deactivate" {
        Write-Host "Deactivating persistent agents..." -ForegroundColor Yellow
        $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
        if ($pythonCmd) {
            & python persistent_agent_manager.py deactivate
        } else {
            Write-Host "Python not found. Please ensure Python is installed and in PATH." -ForegroundColor Red
        }
    }
    
    "status" {
        Write-Host "Checking persistent agent status..." -ForegroundColor Blue
        $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
        if ($pythonCmd) {
            & python persistent_agent_manager.py status
        } else {
            Write-Host "Python not found. Please ensure Python is installed and in PATH." -ForegroundColor Red
        }
    }
    
    "setup" {
        Write-Host "Setting up persistent agent configuration..." -ForegroundColor Magenta
        $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
        if ($pythonCmd) {
            & python persistent_agent_manager.py setup
        } else {
            Write-Host "Python not found. Please ensure Python is installed and in PATH." -ForegroundColor Red
        }
    }
    
    default {
        Write-Host "Usage: $MyInvocation.MyCommand.Name [Activate|Deactivate|Status|Setup]" -ForegroundColor White
        Write-Host "  Activate   - Start all persistent agents" -ForegroundColor White
        Write-Host "  Deactivate - Stop all persistent agents" -ForegroundColor White
        Write-Host "  Status     - Check status of persistent agents" -ForegroundColor White
        Write-Host "  Setup      - Create configuration and shortcuts" -ForegroundColor White
    }
}

Write-Host "`nOperation completed." -ForegroundColor Green