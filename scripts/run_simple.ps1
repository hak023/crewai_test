# Simple Restaurant System Launcher
param(
    [string]$Mode = "basic",
    [string]$Request = "",
    [switch]$Test = $false,
    [switch]$Help = $false
)

if ($Help) {
    Write-Host "CrewAI Restaurant Recommendation System Launcher" -ForegroundColor Cyan
    Write-Host "=" * 50 -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage:" -ForegroundColor Yellow
    Write-Host "  .\run_simple.ps1 [options]" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Options:" -ForegroundColor Yellow
    Write-Host "  -Mode <basic|advanced>    System mode to run" -ForegroundColor Yellow
    Write-Host "  -Request <string>         Restaurant request" -ForegroundColor Yellow
    Write-Host "  -Test                     Run tests" -ForegroundColor Yellow
    Write-Host "  -Help                     Show this help" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Yellow
    Write-Host "  .\run_simple.ps1 -Mode basic" -ForegroundColor Green
    Write-Host "  .\run_simple.ps1 -Mode advanced -Test" -ForegroundColor Green
    exit 0
}

Write-Host "CrewAI Restaurant Recommendation System" -ForegroundColor Cyan
Write-Host "=" * 40 -ForegroundColor Cyan

# Check Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Python not found" -ForegroundColor Red
    exit 1
}

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

# Check config
if (Test-Path "config.json") {
    Write-Host "Config file found" -ForegroundColor Green
} else {
    Write-Host "Config file not found. Please run: python setup_config.py" -ForegroundColor Yellow
}

# Run system
if ($Test) {
    Write-Host "Running tests..." -ForegroundColor Yellow
    python test_restaurant_finder.py
    python test_advanced_system.py
} elseif ($Mode -eq "basic") {
    Write-Host "Running basic system..." -ForegroundColor Yellow
    python restaurant_finder.py
} elseif ($Mode -eq "advanced") {
    Write-Host "Running advanced system..." -ForegroundColor Yellow
    python advanced_restaurant_system.py
} else {
    Write-Host "Invalid mode. Use 'basic' or 'advanced'" -ForegroundColor Red
    exit 1
}

Write-Host "Done!" -ForegroundColor Green
