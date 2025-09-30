# Simple Restaurant System Launcher
param(
    [string]$Mode = "basic",
    [string]$Request = "",
    [switch]$Test = $false,
    [switch]$Help = $false
)

# 프로젝트 루트 디렉토리로 이동
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
Set-Location $ProjectRoot

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
if (Test-Path "config\config.json") {
    Write-Host "✅ Config file found: config\config.json" -ForegroundColor Green
} else {
    Write-Host "⚠️  Config file not found: config\config.json" -ForegroundColor Yellow
    Write-Host "💡 실행 방법:" -ForegroundColor Cyan
    Write-Host "   copy config\config_example.json config\config.json" -ForegroundColor White
    Write-Host "   notepad config\config.json" -ForegroundColor White
}

# Run system
if ($Test) {
    Write-Host "🧪 Running tests..." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "📋 Test 1: Restaurant Finder" -ForegroundColor Cyan
    python -m tests.test_restaurant_finder
    Write-Host ""
    Write-Host "📋 Test 2: Advanced System" -ForegroundColor Cyan
    python -m tests.test_advanced_system
} elseif ($Mode -eq "basic") {
    Write-Host "🚀 Running basic system..." -ForegroundColor Yellow
    Write-Host "🔧 Command: python -m src.restaurant_finder" -ForegroundColor Cyan
    Write-Host ""
    python -m src.restaurant_finder
} elseif ($Mode -eq "advanced") {
    Write-Host "🚀 Running advanced system..." -ForegroundColor Yellow
    Write-Host "🔧 Command: python -m src.advanced_restaurant_system" -ForegroundColor Cyan
    Write-Host ""
    python -m src.advanced_restaurant_system
} else {
    Write-Host "❌ Invalid mode. Use 'basic' or 'advanced'" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "✅ Done!" -ForegroundColor Green
Write-Host "📁 로그 위치: logs\" -ForegroundColor Cyan
Write-Host "📚 문서 위치: docs\" -ForegroundColor Cyan
