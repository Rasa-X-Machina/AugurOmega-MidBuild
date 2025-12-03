# Augur Omega: Permanent Agent Service
# PowerShell script to run the agent service in the background

param(
    [Parameter(Position=0)]
    [ValidateSet("Start", "Stop", "Status", "Activate", "Deactivate", IgnoreCase = $true)]
    [string]$Command = "Status"
)

# Define paths
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$runtimeDir = Join-Path $scriptDir "runtime"
$logDir = Join-Path $scriptDir "logs"

# Create directories if they don't exist
if (!(Test-Path $runtimeDir)) {
    New-Item -ItemType Directory -Path $runtimeDir -Force
}

if (!(Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir -Force
}

Write-Host "Augur Omega Permanent Agent Service" -ForegroundColor Cyan
Write-Host "===================================" -ForegroundColor Cyan

switch ($Command.ToLower()) {
    "activate" {
        Write-Host "Activating permanent agent service..." -ForegroundColor Green
        $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
        if ($pythonCmd) {
            Start-Process -FilePath python -ArgumentList "persistent_agent_service.py", "permanent" -WorkingDirectory $scriptDir
            Write-Host "Permanent agent service activated in background." -ForegroundColor Green
        } else {
            Write-Host "Python not found. Please ensure Python is installed and in PATH." -ForegroundColor Red
        }
    }
    
    "deactivate" {
        Write-Host "Deactivating permanent agent service..." -ForegroundColor Yellow
        $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
        if ($pythonCmd) {
            & python persistent_agent_service.py deactivate
        } else {
            Write-Host "Python not found. Please ensure Python is installed and in PATH." -ForegroundColor Red
        }
    }
    
    "start" {
        Write-Host "Starting agent service..." -ForegroundColor Green
        $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
        if ($pythonCmd) {
            & python persistent_agent_service.py activate
        } else {
            Write-Host "Python not found. Please ensure Python is installed and in PATH." -ForegroundColor Red
        }
    }
    
    "stop" {
        Write-Host "Stopping agent service..." -ForegroundColor Yellow
        $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
        if ($pythonCmd) {
            & python persistent_agent_service.py deactivate
        } else {
            Write-Host "Python not found. Please ensure Python is installed and in PATH." -ForegroundColor Red
        }
    }
    
    "status" {
        Write-Host "Checking agent service status..." -ForegroundColor Blue
        $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
        if ($pythonCmd) {
            & python persistent_agent_service.py status
        } else {
            Write-Host "Python not found. Please ensure Python is installed and in PATH." -ForegroundColor Red
        }
    }
    
    default {
        Write-Host "Usage: $MyInvocation.MyCommand.Name [Activate|Deactivate|Start|Stop|Status]" -ForegroundColor White
        Write-Host "  Activate   - Start all 38+ agents permanently (until deactivated)" -ForegroundColor White
        Write-Host "  Deactivate - Stop all agents permanently" -ForegroundColor White
        Write-Host "  Start      - Alias for activate" -ForegroundColor White
        Write-Host "  Stop       - Alias for deactivate" -ForegroundColor White
        Write-Host "  Status     - Check current agent service status" -ForegroundColor White
    }
}

Write-Host "`nOperation completed." -ForegroundColor Green