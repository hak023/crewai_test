# 🔍 고급 로깅 시스템 가이드

## 📋 개요

`advanced_restaurant_system.py`는 실행 시 상세한 로그를 자동으로 기록합니다.

## 📂 로그 파일 위치

실행할 때마다 `logs/` 디렉토리에 두 개의 파일이 생성됩니다:

```
logs/
├── session_YYYYMMDD_HHMMSS.log    # 상세 실행 로그
└── tasks_YYYYMMDD_HHMMSS.json     # Task별 구조화된 로그
```

## 📝 로그 내용

### 1. session_*.log (세션 로그)
실행 중 발생하는 모든 이벤트를 시간순으로 기록합니다:

✅ **기록되는 내용:**
- 시스템 시작/종료
- Agent 생성 정보
- Task 시작/완료/오류
- 사용자 요청 및 입력 데이터
- 프롬프트 (LLM에 전달되는 요청)
- 응답 (LLM으로부터 받은 결과)
- 실행 시간
- 이메일 발송 내역
- 데이터 분석 결과
- Crew 실행 상세 내역
- API 호출 정보
- 오류 및 예외

### 2. tasks_*.json (Task 로그)
각 Task의 구조화된 정보를 JSON 형식으로 저장합니다:

```json
[
  {
    "task_id": "crew_restaurant_recommendation_170823",
    "task_name": "restaurant_recommendation",
    "agent_name": "crew",
    "start_time": "2025-09-30T17:08:23.123456",
    "input_data": {
      "user_request": "광화문 근처 맛집"
    },
    "status": "completed",
    "interactions": [
      {
        "timestamp": "2025-09-30T17:08:23.234567",
        "type": "prompt",
        "prompt": "맛집 추천 요청: 광화문 근처 맛집",
        "context": {...}
      },
      {
        "timestamp": "2025-09-30T17:08:45.345678",
        "type": "response",
        "response": "추천 맛집 리스트...",
        "metadata": {
          "execution_time": 22.1
        }
      }
    ],
    "end_time": "2025-09-30T17:08:45.456789",
    "execution_time": 22.3,
    "result": "추천 결과..."
  }
]
```

## 🎯 주요 특징

### 1. 자동 로깅
- 시스템 실행 시 자동으로 로그 파일 생성
- 별도 설정 없이 모든 작업 기록

### 2. 상세한 내용 기록
- **입력 프롬프트**: Agent에게 전달되는 모든 지시사항
- **응답 내용**: Agent가 생성한 결과
- **실행 시간**: 각 Task의 정확한 수행 시간
- **메타데이터**: 추가 컨텍스트 정보

### 3. 구조화된 데이터
- JSON 형식으로 Task 정보 저장
- 프로그램으로 쉽게 분석 가능
- 타임스탬프로 모든 이벤트 추적

### 4. 간소한 콘솔 출력
- print문은 최소화하여 핵심 정보만 표시
- 상세 내용은 로그 파일에만 기록
- 실행 중 화면이 깔끔함

## 📖 사용 예시

### 시스템 실행
```bash
python advanced_restaurant_system.py
```

### 로그 확인
실행 완료 후 출력되는 로그 파일 경로를 확인:
```
💡 생성된 로그 파일을 확인하세요:
   - logs\session_20250930_171638.log
   - logs\tasks_20250930_171638.json
```

### 로그 분석
```python
import json

# Task 로그 읽기
with open('logs/tasks_20250930_171638.json', 'r', encoding='utf-8') as f:
    tasks = json.load(f)

# Task 실행 시간 분석
for task in tasks:
    print(f"{task['task_name']}: {task['execution_time']:.2f}초")
```

## 🔧 로깅 레벨 설정

`config.json`에서 로깅 레벨 조정:
```json
{
  "logging": {
    "level": "INFO",
    "enable_file_logging": true,
    "enable_console_logging": true
  }
}
```

레벨 옵션:
- `DEBUG`: 모든 상세 정보
- `INFO`: 일반 정보 (기본값)
- `WARNING`: 경고 이상
- `ERROR`: 오류만

## 📊 로그 활용

### 1. 성능 분석
- 각 Task의 실행 시간 확인
- 병목 지점 파악
- 최적화 포인트 발견

### 2. 디버깅
- 오류 발생 시점 추적
- 입력/출력 데이터 확인
- 실행 흐름 분석

### 3. 감사 추적
- 모든 작업 기록 보존
- 사용자 요청 이력 관리
- 시스템 사용 통계

### 4. 품질 관리
- LLM 응답 품질 검토
- 프롬프트 효과 분석
- 결과 일관성 확인

## 💡 팁

1. **로그 정기적 백업**: 중요한 실행 기록은 별도 보관
2. **로그 분석 자동화**: JSON 로그를 활용한 자동 리포트 생성
3. **디스크 공간 관리**: 오래된 로그는 주기적으로 정리
4. **프롬프트 개선**: 로그를 통해 프롬프트 최적화

## 🚀 고급 기능

### CrewAI Verbose 출력
- CrewAI의 모든 verbose 출력이 자동으로 로그 파일에 기록됨
- 콘솔에는 핵심 진행 상황만 표시
- Agent 간 통신, Tool 사용 등 모든 내부 동작 추적 가능

### 실시간 모니터링
```bash
# PowerShell에서 실시간 로그 확인
Get-Content logs\session_YYYYMMDD_HHMMSS.log -Wait

# 또는
tail -f logs/session_YYYYMMDD_HHMMSS.log  # Git Bash/Linux
```

## 📞 문의

로깅 관련 문제가 있다면 `logging_manager.py` 파일을 확인하거나
설정을 조정해보세요.
