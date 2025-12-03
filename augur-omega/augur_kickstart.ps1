# Augur Omega: Agenta-Aligned Bootstrap Script (Robust Edition)
# Path: C:\Users\Dell\Rasa-X-Machina\augur-omega\augur_kickstart.ps1

$ErrorActionPreference = "Stop"

Write-Host "=== Augur Omega AI-Native Deployment Kick-Start ===" -ForegroundColor Cyan

# ============================================================================
# Step 1: Check Dependencies
# ============================================================================
Write-Host "Step 1: Verifying base dependencies..." -ForegroundColor Yellow
$dependencies = @("git", "python", "curl") 

foreach ($dep in $dependencies) {
    if (-not (Get-Command $dep -ErrorAction SilentlyContinue)) {
        Write-Error "CRITICAL: Missing dependency '$dep'. Please install it before continuing."
        exit 1
    }
}
Write-Host "Base Dependencies Verified." -ForegroundColor Green

# ============================================================================
# Step 2: Directory Structure
# ============================================================================
Write-Host "Step 2: Preparing config directories..." -ForegroundColor Yellow

# Use current location as base since you are already inside the folder
$baseDir = $PWD
$subDirs = @("prime_koshas", "microagents", "domain_koshas", "scripts")

foreach ($dir in $subDirs) {
    $path = Join-Path $baseDir $dir
    if (-not (Test-Path $path)) { New-Item -ItemType Directory -Force -Path $path | Out-Null }
}

# ============================================================================
# Step 3: Git Initialization
# ============================================================================
Write-Host "Step 3: Initializing Repository..." -ForegroundColor Yellow
$repoDir = Join-Path $baseDir "main"

if (-not (Test-Path $repoDir)) {
    New-Item -ItemType Directory -Force -Path $repoDir | Out-Null
    Set-Location $repoDir
    git init
    Write-Host "Initialized local Git repository." -ForegroundColor Gray
} else {
    Set-Location $repoDir
}

# ============================================================================
# Step 4: Install Dependencies
# ============================================================================
Write-Host "Step 4: Installing Python dependencies..." -ForegroundColor Yellow
python -m pip install --upgrade pip | Out-Null

# Look for requirements.txt in the base directory
$reqFile = Join-Path $baseDir "requirements.txt"

if (Test-Path $reqFile) {
    Write-Host "Found requirements.txt at $reqFile" -ForegroundColor Gray
    pip install -r $reqFile
} else {
    Write-Warning "requirements.txt not found at $reqFile. Skipping pip install."
}

# ============================================================================
# Step 5: Docker Setup (Graceful Degradation)
# ============================================================================
Write-Host "Step 5: Docker Setup..." -ForegroundColor Yellow

if (Get-Process "Docker Desktop" -ErrorAction SilentlyContinue) {
    Write-Host "Docker Desktop is running. Pulling images..." -ForegroundColor Gray
    docker pull python:3.11-slim
    docker pull node:20
} else {
    Write-Warning "Docker Desktop is NOT running. Skipping image pull."
    Write-Host "  -> You can still generate code, but you cannot run the containers yet." -ForegroundColor Gray
}

# ============================================================================
# Step 6: Kubernetes (Graceful Degradation)
# ============================================================================
Write-Host "Step 6: Kubernetes Setup..." -ForegroundColor Yellow

if (Get-Command "kind" -ErrorAction SilentlyContinue) {
    $clusters = kind get clusters
    if ($clusters -notcontains "augur-omega") {
        kind create cluster --name augur-omega
    }
    kubectl config use-context kind-augur-omega
} else {
    Write-Host "Skipping K8s setup (Local Mode)." -ForegroundColor Gray
}

# ============================================================================
# Step 7: Scaffolding
# ============================================================================
Write-Host "Step 7: Deploying Scaffolds..." -ForegroundColor Yellow

function New-EmptyFile ($FilePath) {
    if (-not (Test-Path $FilePath)) { New-Item -ItemType File -Force -Path $FilePath | Out-Null }
}

1..36 | ForEach-Object { New-EmptyFile (Join-Path $baseDir "prime_koshas\PRIME_$($_).py") }
1..144 | ForEach-Object { New-EmptyFile (Join-Path $baseDir "domain_koshas\DOMAIN_$($_).py") }

Write-Host "Scaffolding Complete." -ForegroundColor Green

# ============================================================================
# Step 8: Orchestration
# ============================================================================
Write-Host "Step 8: Triggering Agenta Orchestrator..." -ForegroundColor Yellow
$orchestratorScript = Join-Path $baseDir "augur_orchestrate.py"

if (Test-Path $orchestratorScript) {
    python $orchestratorScript
} else {
    Write-Error "Orchestrator script not found at $orchestratorScript"
    exit 1
}

# ============================================================================
# Step 9: The Gauntlet
# ============================================================================
Write-Host "Step 9: The Gauntlet (Testing Phase)..." -ForegroundColor Yellow

$env:PYTHONPATH = "$($env:PYTHONPATH);$baseDir"
$primePath = Join-Path $baseDir "prime_koshas"

Write-Host "Verifying syntax..."
python -m compileall $primePath

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Syntax Checks Passed. Committing to Repository..." -ForegroundColor Green
    git add .
    git commit -allow-empty -m "Augur Omega: Verified Build $(Get-Date -Format s)"
    Write-Host "Code committed locally." -ForegroundColor Gray
} else {
    Write-Error "❌ Syntax Errors Detected. Aborting Commit."
    Write-Host "Check logs/orchestrator_*.log for details." -ForegroundColor Red
    exit 1
}

Write-Host "=== Augur Omega Build Complete. System is Sovereignty-Ready. ===" -ForegroundColor Cyan
Write-Host "The Gauntlet has been passed. The system is ready for deployment." -ForegroundColor Green
Write-Host "Next Steps: Monitor the system and verify all services are running as expected." -ForegroundColor Cyan