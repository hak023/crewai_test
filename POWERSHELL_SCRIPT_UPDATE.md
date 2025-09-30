# 🔧 PowerShell 스크립트 업데이트

**날짜**: 2025-09-30  
**작업**: 디렉토리 구조 변경에 따른 스크립트 수정

---

## 📋 수정된 파일

1. ✅ `scripts/run_restaurant_system.ps1`
2. ✅ `scripts/run_simple.ps1`

---

## 🔄 주요 변경사항

### 1. 프로젝트 루트 자동 이동

#### 추가된 코드
```powershell
# 프로젝트 루트 디렉토리로 이동
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
Set-Location $ProjectRoot
```

**효과**:
- 스크립트를 `scripts/` 디렉토리에서 실행해도 자동으로 프로젝트 루트로 이동
- 상대 경로 문제 해결

---

### 2. Python 실행 경로 수정

#### Before ❌
```powershell
python advanced_restaurant_system.py
python restaurant_finder.py
python test_advanced_system.py
```

#### After ✅
```powershell
python -m src.advanced_restaurant_system
python -m src.restaurant_finder
python -m tests.test_advanced_system
python -m tests.test_restaurant_finder
```

**효과**:
- 모듈 방식으로 실행하여 import 경로 문제 해결
- 새로운 디렉토리 구조에 맞게 조정

---

### 3. Config 파일 경로 수정

#### Before ❌
```powershell
Check-ConfigFile "config.json"
```

#### After ✅
```powershell
Check-ConfigFile "config\config.json"
```

**효과**:
- `config/` 디렉토리 내 설정 파일 확인
- 더 명확한 오류 메시지 제공

---

### 4. 사용자 안내 개선

#### Before ❌
```powershell
Write-Host "Config file not found"
```

#### After ✅
```powershell
Write-Host "❌ Config file not found: config\config.json"
Write-Host "💡 실행 방법:"
Write-Host "   copy config\config_example.json config\config.json"
Write-Host "   notepad config\config.json"
```

**효과**:
- 문제 해결 방법을 바로 제시
- 사용자 경험 개선

---

### 5. 테스트 기능 강화

#### run_restaurant_system.ps1
```powershell
function Run-Tests {
    # Test advanced system
    if (Test-Path "tests\test_advanced_system.py") {
        python -m tests.test_advanced_system
    }
    
    # Test restaurant finder  
    if (Test-Path "tests\test_restaurant_finder.py") {
        python -m tests.test_restaurant_finder
    }
}
```

**효과**:
- 모든 테스트를 자동으로 실행
- 각 테스트 결과를 명확히 표시

---

### 6. 로그 및 문서 위치 안내 추가

```powershell
Write-Host "📁 로그 파일 위치: logs\"
Write-Host "📚 문서 위치:"
Write-Host "   - 사용 가이드: docs\guides\"
Write-Host "   - 기술 참조: docs\reference\"
```

**효과**:
- 실행 후 참고할 위치 안내
- 문서 접근성 향상

---

## 🚀 실행 방법 변경

### Before (디렉토리 구조 변경 전)

```powershell
# 프로젝트 루트에서만 실행 가능
.\run_restaurant_system.ps1
.\run_simple.ps1
```

### After (디렉토리 구조 변경 후)

```powershell
# 어디서든 실행 가능
.\scripts\run_restaurant_system.ps1
.\scripts\run_simple.ps1

# 또는 scripts 디렉토리에서
cd scripts
.\run_restaurant_system.ps1
.\run_simple.ps1
```

**효과**: 스크립트가 자동으로 프로젝트 루트로 이동하므로 어디서든 실행 가능

---

## 📝 사용 예시

### run_restaurant_system.ps1

```powershell
# 도움말
.\scripts\run_restaurant_system.ps1 -Help

# 고급 시스템 실행
.\scripts\run_restaurant_system.ps1

# 테스트 모드
.\scripts\run_restaurant_system.ps1 -Test
```

### run_simple.ps1

```powershell
# 기본 시스템 실행
.\scripts\run_simple.ps1 -Mode basic

# 고급 시스템 실행
.\scripts\run_simple.ps1 -Mode advanced

# 테스트 실행
.\scripts\run_simple.ps1 -Test
```

---

## 🎯 개선 효과

### 1. 유연성 향상
- ✅ 스크립트 위치에 상관없이 실행 가능
- ✅ 자동으로 프로젝트 루트 탐지

### 2. 오류 메시지 개선
- ✅ 문제 발생 시 해결 방법 제시
- ✅ 명확한 파일 경로 표시

### 3. 사용성 향상
- ✅ 실행 후 참고할 위치 안내
- ✅ 진행 상황 명확히 표시

### 4. 테스트 자동화
- ✅ 모든 테스트를 한 번에 실행
- ✅ 개별 테스트 결과 확인 가능

---

## 🧪 테스트 결과

### 실행 테스트
```powershell
# 1. 프로젝트 루트에서
PS C:\work\workspace_crewai_test> .\scripts\run_restaurant_system.ps1 -Help
✅ 정상 동작

# 2. scripts 디렉토리에서
PS C:\work\workspace_crewai_test\scripts> .\run_restaurant_system.ps1 -Help
✅ 정상 동작 (자동으로 프로젝트 루트로 이동)
```

---

## 📂 파일 구조 (최종)

```
workspace_crewai_test/
├── scripts/
│   ├── run_restaurant_system.ps1  ✅ 수정됨
│   ├── run_simple.ps1              ✅ 수정됨
│   └── setup_config.py
├── src/
│   ├── advanced_restaurant_system.py
│   └── restaurant_finder.py
├── config/
│   ├── config.json
│   └── config_example.json
├── tests/
│   ├── test_advanced_system.py
│   └── test_restaurant_finder.py
└── ...
```

---

## 🔧 추가 개선 사항

### 1. setup_config.py도 업데이트 필요

현재 `scripts/setup_config.py`도 경로 수정이 필요할 수 있습니다.

### 2. 배치 파일 추가 (선택사항)

Windows 사용자를 위한 `.bat` 파일:
```batch
@echo off
powershell -ExecutionPolicy Bypass -File "%~dp0run_restaurant_system.ps1" %*
```

---

## ✅ 체크리스트

- [x] 프로젝트 루트 자동 이동 기능 추가
- [x] Python 모듈 실행 경로 수정
- [x] Config 파일 경로 수정 (`config/config.json`)
- [x] 테스트 파일 경로 수정 (`tests/`)
- [x] 사용자 안내 메시지 개선
- [x] 테스트 기능 강화
- [x] 로그 및 문서 위치 안내 추가

---

**완료 시각**: 2025-09-30  
**다음 단계**: GitHub에 커밋
