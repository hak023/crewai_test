# CrewAI Advanced Restaurant Recommendation System Launcher
# PowerShell script to easily run the advanced restaurant recommendation system

param(
    [string]$Request = "",
    [switch]$Test = $false,
    [switch]$Help = $false
)

# 프로젝트 루트 디렉토리로 이동
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
Set-Location $ProjectRoot

Write-Host "📁 프로젝트 루트: $ProjectRoot" -ForegroundColor Cyan
Write-Host ""

# Color settings
$ErrorColor = "Red"
$SuccessColor = "Green"
$InfoColor = "Cyan"
$WarningColor = "Yellow"

function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

function Show-Help {
    Write-ColorOutput "CrewAI Advanced Restaurant Recommendation System Launcher" $InfoColor
    Write-ColorOutput ("=" * 60) $InfoColor
    Write-ColorOutput ""
    Write-ColorOutput "Usage:" $InfoColor
    Write-ColorOutput "  .\run_restaurant_system.ps1 [options]" $InfoColor
    Write-ColorOutput ""
    Write-ColorOutput "Options:" $InfoColor
    Write-ColorOutput "  -Request <string>         Restaurant recommendation request (optional)" $InfoColor
    Write-ColorOutput "  -Test                     Run in test mode" $InfoColor
    Write-ColorOutput "  -Help                     Show this help" $InfoColor
    Write-ColorOutput ""
    Write-ColorOutput "Examples:" $InfoColor
    Write-ColorOutput "  .\run_restaurant_system.ps1" $InfoColor
    Write-ColorOutput "  .\run_restaurant_system.ps1 -Test" $InfoColor
    Write-ColorOutput "  .\run_restaurant_system.ps1 -Help" $InfoColor
    Write-ColorOutput ""
    Write-ColorOutput "Features:" $InfoColor
    Write-ColorOutput "  - 6 AI Agents working together" $InfoColor
    Write-ColorOutput "  - Restaurant recommendation" $InfoColor
    Write-ColorOutput "  - Survey creation" $InfoColor
    Write-ColorOutput "  - Email sending" $InfoColor
    Write-ColorOutput "  - Data analysis" $InfoColor
    Write-ColorOutput "  - Detailed logging" $InfoColor
}

function Check-Environment {
    Write-ColorOutput "Checking environment..." $InfoColor
    
    # Check Python installation
    try {
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "Python installed: $pythonVersion" $SuccessColor
        } else {
            Write-ColorOutput "Python not installed" $ErrorColor
            return $false
        }
    } catch {
        Write-ColorOutput "Python not installed" $ErrorColor
        return $false
    }
    
    # Check pip installation
    try {
        $pipVersion = pip --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "pip installed: $pipVersion" $SuccessColor
        } else {
            Write-ColorOutput "pip not installed" $ErrorColor
            return $false
        }
    } catch {
        Write-ColorOutput "pip not installed" $ErrorColor
        return $false
    }
    
    return $true
}

function Install-Dependencies {
    Write-ColorOutput "Installing required packages..." $InfoColor
    
    try {
        pip install -r requirements.txt
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "Packages installed successfully" $SuccessColor
            return $true
        } else {
            Write-ColorOutput "Package installation failed" $ErrorColor
            return $false
        }
    } catch {
        Write-ColorOutput "Error during package installation" $ErrorColor
        return $false
    }
}

function Check-ConfigFile {
    param([string]$ConfigFile)
    
    if (Test-Path $ConfigFile) {
        Write-ColorOutput "✅ Config file found: $ConfigFile" $SuccessColor
        return $true
    } else {
        Write-ColorOutput "❌ Config file not found: $ConfigFile" $WarningColor
        Write-ColorOutput "💡 config/config_example.json을 복사하여 config/config.json을 생성하고 API 키를 설정하세요" $WarningColor
        Write-ColorOutput ""
        Write-ColorOutput "실행 방법:" $InfoColor
        Write-ColorOutput "  copy config\config_example.json config\config.json" $InfoColor
        Write-ColorOutput "  notepad config\config.json" $InfoColor
        return $false
    }
}

function Run-AdvancedSystem {
    param([string]$Request)
    
    Write-ColorOutput "" 
    Write-ColorOutput ("=" * 60) $InfoColor
    Write-ColorOutput "🚀 Advanced Restaurant Recommendation System" $InfoColor
    Write-ColorOutput ("=" * 60) $InfoColor
    Write-ColorOutput ""
    
    if ($Request) {
        Write-ColorOutput "📋 사용자 요청: $Request" $InfoColor
        Write-ColorOutput ""
    }
    
    # src/advanced_restaurant_system.py 실행 (모듈 방식)
    Write-ColorOutput "🔧 실행 중: python -m src.advanced_restaurant_system" $InfoColor
    Write-ColorOutput ""
    python -m src.advanced_restaurant_system
    
    if ($LASTEXITCODE -eq 0) {
        Write-ColorOutput ""
        Write-ColorOutput "✅ 시스템 실행 완료!" $SuccessColor
    } else {
        Write-ColorOutput ""
        Write-ColorOutput "❌ 시스템 실행 중 오류 발생" $ErrorColor
        Write-ColorOutput "💡 로그 파일을 확인하세요: logs\" $WarningColor
    }
}

function Run-Tests {
    Write-ColorOutput "" 
    Write-ColorOutput ("=" * 60) $InfoColor
    Write-ColorOutput "🧪 Advanced System Tests" $InfoColor
    Write-ColorOutput ("=" * 60) $InfoColor
    Write-ColorOutput ""
    
    # Test advanced system
    if (Test-Path "tests\test_advanced_system.py") {
        Write-ColorOutput "Testing advanced system..." $InfoColor
        Write-ColorOutput "🔧 실행 중: python -m tests.test_advanced_system" $InfoColor
        Write-ColorOutput ""
        python -m tests.test_advanced_system
        
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "✅ 테스트 완료!" $SuccessColor
        } else {
            Write-ColorOutput "❌ 테스트 실패" $ErrorColor
        }
    } else {
        Write-ColorOutput "⚠️  tests/test_advanced_system.py 파일을 찾을 수 없습니다" $WarningColor
    }
    
    Write-ColorOutput ""
    
    # Test restaurant finder
    if (Test-Path "tests\test_restaurant_finder.py") {
        Write-ColorOutput "Testing restaurant finder..." $InfoColor
        Write-ColorOutput "🔧 실행 중: python -m tests.test_restaurant_finder" $InfoColor
        Write-ColorOutput ""
        python -m tests.test_restaurant_finder
        
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "✅ 테스트 완료!" $SuccessColor
        } else {
            Write-ColorOutput "❌ 테스트 실패" $ErrorColor
        }
    }
}

# Main execution logic
if ($Help) {
    Show-Help
    exit 0
}

Write-ColorOutput ""
Write-ColorOutput ("=" * 60) $InfoColor
Write-ColorOutput "🍽️  CrewAI Advanced Restaurant System Launcher" $InfoColor
Write-ColorOutput ("=" * 60) $InfoColor
Write-ColorOutput ""

# Check environment
Write-ColorOutput "⚙️  환경 확인 중..." $InfoColor
if (-not (Check-Environment)) {
    Write-ColorOutput "❌ 환경 설정을 확인해주세요" $ErrorColor
    exit 1
}

# Install packages
Write-ColorOutput ""
if (-not (Install-Dependencies)) {
    Write-ColorOutput "❌ 패키지 설치 실패" $ErrorColor
    exit 1
}

# Check config file
Write-ColorOutput ""
if (-not (Check-ConfigFile "config\config.json")) {
    Write-ColorOutput "⚠️  config/config.json 파일을 먼저 설정해주세요" $WarningColor
    exit 1
}

# Test mode
if ($Test) {
    Run-Tests
    exit 0
}

# Run advanced system
Run-AdvancedSystem -Request $Request

Write-ColorOutput ""
Write-ColorOutput "📁 로그 파일 위치: logs\" $InfoColor
Write-ColorOutput "📚 문서 위치:" $InfoColor
Write-ColorOutput "   - 사용 가이드: docs\guides\" $InfoColor
Write-ColorOutput "   - 기술 참조: docs\reference\" $InfoColor
Write-ColorOutput ""