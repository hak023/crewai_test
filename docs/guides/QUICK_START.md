# 🚀 빠른 시작 가이드

## 📋 사전 준비

1. **Python 3.11 이상** 설치
2. **config.json** 설정 완료
   - API 키 설정 (Gemini, Serper 등)
   - 이메일 수신자 설정

## ⚡ 실행 방법

### Windows (PowerShell)

```powershell
# 1. 기본 실행 (가장 간단)
.\run_restaurant_system.ps1

# 2. 테스트 모드
.\run_restaurant_system.ps1 -Test

# 3. 도움말
.\run_restaurant_system.ps1 -Help
```

### 직접 Python 실행

```bash
python advanced_restaurant_system.py
```

## 📝 실행 과정

PowerShell 스크립트 (`run_restaurant_system.ps1`)는 다음을 자동으로 수행합니다:

1. ✅ **환경 확인**: Python, pip 설치 확인
2. 📦 **패키지 설치**: requirements.txt 기반 자동 설치
3. ⚙️ **설정 확인**: config.json 파일 검증
4. 🚀 **시스템 실행**: advanced_restaurant_system.py 실행

## 🎯 실행 흐름

```
실행 시작
  ↓
환경 확인 (Python, pip)
  ↓
패키지 자동 설치
  ↓
config.json 확인
  ↓
시스템 초기화 (6개 Agent 생성)
  ↓
사용자 입력 대기
  ↓
워크플로우 실행
  ├─ 맛집 추천
  ├─ 설문조사 생성
  ├─ 이메일 발송
  └─ 데이터 분석
  ↓
로그 저장 (logs/ 디렉토리)
  ↓
완료!
```

## 📁 출력 파일

실행 완료 후 `logs/` 디렉토리에서 확인:

```
logs/
├── session_YYYYMMDD_HHMMSS.log    # 상세 실행 로그
└── tasks_YYYYMMDD_HHMMSS.json     # Task별 구조화된 데이터
```

## ⚙️ config.json 필수 설정

```json
{
  "api_keys": {
    "gemini_api_key": "your-api-key",
    "serper_api_key": "your-api-key",
    "sendgrid_api_key": "your-api-key"
  },
  "email_settings": {
    "sender_email": "your-email@gmail.com",
    "recipients": [
      "recipient1@example.com",
      "recipient2@example.com"
    ]
  }
}
```

## 🔧 문제 해결

### Python을 찾을 수 없음
```powershell
# Python 설치 확인
python --version

# PATH 환경 변수 확인
```

### 패키지 설치 오류
```powershell
# 수동 설치
pip install -r requirements.txt
```

### config.json 오류
```powershell
# config_example.json을 복사하여 수정
Copy-Item config_example.json config.json
# 이후 API 키 등 설정
```

## 💡 유용한 팁

### 1. 실행 전 설정 확인
```powershell
# config.json 테스트
python -c "from config_manager import load_config; config = load_config(); print('OK' if config else 'ERROR')"
```

### 2. 로그 실시간 확인
```powershell
# 다른 터미널에서
Get-Content logs\session_*.log -Wait
```

### 3. 빠른 테스트
```powershell
# 전체 시스템 테스트
.\run_restaurant_system.ps1 -Test
```

## 📚 추가 문서

- [로깅 가이드](LOGGING_GUIDE.md) - 로그 파일 확인 방법
- [이메일 설정 가이드](EMAIL_CONFIG_GUIDE.md) - 이메일 수신자 관리
- [고급 사용법](ADVANCED_README.md) - 상세 기능 설명

## 🎉 첫 실행 예시

```powershell
PS C:\work\workspace_crewai_test> .\run_restaurant_system.ps1

============================================================
🍽️  CrewAI Advanced Restaurant System Launcher
============================================================

⚙️  환경 확인 중...
Python installed: Python 3.11.9
pip installed: pip 25.2
✅ 환경 확인 완료

📦 패키지 설치...
✅ 패키지 설치 완료

⚙️  시스템 초기화 중...
✅ 시스템 초기화 완료

맛집 추천 요청을 입력하세요 (Enter: 기본값 사용): 
기본값 사용: 광화문 근처 3만원 이하의 한식 맛집을 찾아줘

[시스템 실행...]

✅ 시스템 실행 완료!

📁 로그 파일 위치: logs\
```

## ❓ 자주 묻는 질문

**Q: 실행 시간이 얼마나 걸리나요?**
A: 전체 워크플로우는 약 30초~2분 정도 소요됩니다. (API 응답 속도에 따라 다름)

**Q: 이메일이 실제로 발송되나요?**
A: SendGrid API 키가 설정되어 있으면 실제로 발송됩니다. 테스트 시 주의하세요.

**Q: 로그 파일이 너무 많아지면?**
A: `logs/` 디렉토리를 주기적으로 정리하거나 백업하세요.

**Q: 오류가 발생하면?**
A: 로그 파일(`logs/session_*.log`)을 확인하여 상세 오류 내용을 파악하세요.
