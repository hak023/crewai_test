# 📝 로깅 개선 사항

## 🎯 개선 목표
- CrewAI의 상세한 실행 과정을 로그 파일에 기록
- 프롬프트와 응답의 전체 내용 기록
- Agent 간 통신 및 Tool 사용 내역 캡처

## ✅ 적용된 개선사항

### 1. **프롬프트/응답 전체 로깅**

#### 변경 전
```python
self.logger.debug(f"💬 Task 프롬프트: {prompt[:200]}...")  # 200자만
self.logger.debug(f"📝 Task 응답: {response[:200]}...")      # 200자만
```

#### 변경 후
```python
# 프롬프트 전체 로깅
self.logger.info(f"💬 프롬프트 전송 ({task_id}):")
self.logger.info(f"📤 {prompt}")  # 전체 내용
self.logger.info(f"📋 컨텍스트: {json.dumps(context, ...)}")

# 응답 전체 로깅
self.logger.info(f"📥 응답 수신 ({task_id}):")
self.logger.info(f"📄 {response}")  # 전체 내용
self.logger.info(f"📊 메타데이터: {json.dumps(metadata, ...)}")
```

### 2. **CrewAI 상세 로깅 강화**

#### 추가된 로거
```python
loggers_to_setup = [
    "crewai",          # CrewAI 메인
    "crewai.crew",     # Crew 실행
    "crewai.agent",    # Agent 동작
    "crewai.task",     # Task 실행
    "crewai.tools",    # Tool 사용
    "litellm",         # LLM 호출
]
```

모든 CrewAI 내부 동작이 DEBUG 레벨로 로그 파일에 기록됩니다.

### 3. **Crew 실행 구간 명확화**

```python
self.logger.logger.info("🚀 Crew 실행 시작...")
self.logger.logger.info("-" * 80)

result = crew.kickoff(...)  # CrewAI verbose 출력이 여기에 기록됨

self.logger.logger.info("-" * 80)
self.logger.logger.info("✅ Crew 실행 완료")
```

### 4. **콘솔 출력 간소화**

```python
# 콘솔 핸들러는 CRITICAL 레벨만 표시
console_handler.setLevel(logging.CRITICAL)
```

- 콘솔: print문만 표시 (깔끔)
- 로그 파일: 모든 상세 정보 기록

## 📊 로그 파일에 기록되는 내용

### session_*.log
```
================================================================================
🚀 맛집 추천 시스템 세션 시작 - 20250930_180000
📊 시스템 정보: {...}
================================================================================

🤖 에이전트 생성: researcher
🤖 에이전트 생성: curator
... (6개 Agent)

🚀 전체 워크플로우 시작
📋 사용자 요청: 광화문 근처 맛집 추천
📧 이메일 수신자: 1명

================================================================================
🔍 사용자 요청: 광화문 근처 맛집 추천
================================================================================

📋 Task 시작: restaurant_recommendation (Agent: crew)
👥 크루 실행: recommendation_crew
📋 실행할 Task들: research, curation, communication
⚙️ 실행 방식: sequential

💬 프롬프트 전송 (crew_restaurant_recommendation_180059):
📤 맛집 추천 요청: 광화문 근처 맛집 추천
📋 컨텍스트: {
  "crew": "recommendation_crew",
  "agents": 3
}

🚀 Crew 실행 시작...
--------------------------------------------------------------------------------
[CrewAI 상세 실행 로그]
- Agent 간 통신
- Tool 사용 내역
- LLM 프롬프트/응답
- 중간 처리 과정
--------------------------------------------------------------------------------
✅ Crew 실행 완료

📥 응답 수신 (crew_restaurant_recommendation_180059):
📄 🍽️ 추천 맛집 리스트
[1] 맛집 이름
📍 주소: ...
💰 가격대: ...
⭐ 평점: ...
...

📊 메타데이터: {
  "execution_time": 20.5
}

✅ Task 완료: crew_restaurant_recommendation_180059 (실행시간: 20.50초)
✅ 맛집 추천 완료 (실행시간: 20.50초)
```

### tasks_*.json
```json
[
  {
    "task_id": "crew_restaurant_recommendation_180059",
    "task_name": "restaurant_recommendation",
    "agent_name": "crew",
    "start_time": "2025-09-30T18:00:59.794143",
    "input_data": {
      "user_request": "광화문 근처 맛집 추천"
    },
    "status": "completed",
    "interactions": [
      {
        "timestamp": "2025-09-30T18:00:59.798122",
        "type": "prompt",
        "prompt": "맛집 추천 요청: ...",
        "context": {...}
      },
      {
        "timestamp": "2025-09-30T18:01:20.652434",
        "type": "response",
        "response": "🍽️ 추천 맛집 리스트\n...",
        "metadata": {
          "execution_time": 20.858
        }
      }
    ],
    "end_time": "2025-09-30T18:01:20.652434",
    "execution_time": 20.858,
    "result": "🍽️ 추천 맛집 리스트\n..."
  }
]
```

## 🎯 주요 개선 효과

### Before ❌
- 프롬프트/응답이 200자로 잘림
- CrewAI 내부 동작 볼 수 없음
- Agent 간 통신 과정 미기록
- 중간 처리 과정 불명확

### After ✅
- ✅ 프롬프트/응답 **전체 내용** 기록
- ✅ CrewAI **모든 내부 동작** 기록
- ✅ Agent 간 **통신 과정** 상세 기록
- ✅ Tool 사용, LLM 호출 등 **모든 과정** 추적 가능

## 📖 사용 방법

### 실행 후 로그 확인
```bash
# 전체 로그 확인
cat logs/session_YYYYMMDD_HHMMSS.log

# 특정 부분만 확인
grep "프롬프트" logs/session_*.log
grep "응답" logs/session_*.log
grep "Crew 실행" logs/session_*.log
```

### 실시간 모니터링
```powershell
# PowerShell
Get-Content logs\session_*.log -Wait

# Git Bash / Linux
tail -f logs/session_*.log
```

## 💡 디버깅 활용

### Agent 동작 추적
```bash
grep "Agent" logs/session_*.log
```

### Tool 사용 확인
```bash
grep "Tool" logs/session_*.log
grep "crewai.tools" logs/session_*.log
```

### LLM 호출 확인
```bash
grep "litellm" logs/session_*.log
```

### 실행 시간 분석
```bash
grep "실행시간" logs/session_*.log
```

## 🔧 추가 팁

### 로그 레벨 조정
`config.json`에서:
```json
{
  "logging": {
    "level": "DEBUG"  // INFO, DEBUG, WARNING, ERROR
  }
}
```

### 로그 크기 관리
- 각 세션마다 새 로그 파일 생성
- 타임스탬프로 구분 가능
- 오래된 로그는 주기적으로 정리

## 📞 문제 해결

### 로그가 너무 많아요
→ `config.json`에서 `level`을 `INFO`로 변경

### 로그가 너무 적어요
→ `config.json`에서 `level`을 `DEBUG`로 변경

### 콘솔이 너무 지저분해요
→ 이미 최소화됨. print문만 표시됩니다.

## 🎉 결론

이제 로그 파일에서:
- ✅ 전체 실행 과정 추적 가능
- ✅ 문제 발생 시 정확한 원인 파악 가능
- ✅ Agent/Tool/LLM 동작 상세 확인 가능
- ✅ 성능 분석 및 최적화 가능
