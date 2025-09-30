# 🍽️ CrewAI 맛집 추천 및 설문조사 시스템

CrewAI를 활용한 지능형 맛집 추천 및 설문조사 자동화 시스템입니다.

## 📁 프로젝트 구조

```
workspace_crewai_test/
├── src/                      # 소스 코드
│   ├── advanced_restaurant_system.py   # 고급 맛집 추천 시스템
│   ├── restaurant_finder.py            # 기본 맛집 추천 시스템
│   ├── config_manager.py               # 설정 관리
│   └── logging_manager.py              # 로깅 관리
│
├── config/                   # 설정 파일
│   ├── config.json          # 실제 설정 (git ignore)
│   ├── config_example.json  # 설정 예시
│   └── env_example.txt      # 환경 변수 예시
│
├── docs/                     # 문서
│   ├── guides/              # 사용 가이드
│   └── reference/           # 기술 참조
│
├── tests/                    # 테스트 파일
├── scripts/                  # 실행 스크립트
├── templates/                # 템플릿 (이메일, 리포트)
└── logs/                     # 로그 파일 (자동 생성)
```

상세한 디렉토리 구조는 [DIRECTORY_STRUCTURE.md](docs/reference/DIRECTORY_STRUCTURE.md)를 참조하세요.

## 🎯 주요 기능

### 1. **기본 시스템** (`restaurant_finder.py`)
- 3개 Agent 협업: Researcher, Curator, Communicator
- 웹 검색 기반 맛집 정보 수집
- AI 기반 맛집 큐레이션 및 추천

### 2. **고급 시스템** (`advanced_restaurant_system.py`)
- 6개 Agent 협업 워크플로우
- 맛집 추천 → 설문조사 생성 → 이메일 발송 → 데이터 분석
- 상세 로깅 및 분석 리포트 생성

## 🚀 빠른 시작

### 1. 환경 설정

```bash
# 의존성 설치
pip install -r requirements.txt

# 설정 파일 생성
copy config\config_example.json config\config.json

# config/config.json 파일을 편집하여 API 키 설정
```

### 2. 실행

```powershell
# 고급 시스템 실행
python -m src.advanced_restaurant_system

# 기본 시스템 실행  
python -m src.restaurant_finder
```

## 📚 문서

- **설정 가이드**: [docs/guides/SETUP_GUIDE.md](docs/guides/SETUP_GUIDE.md)
- **빠른 시작**: [docs/guides/QUICK_START.md](docs/guides/QUICK_START.md)
- **Gemini 설정**: [docs/guides/GEMINI_SETUP.md](docs/guides/GEMINI_SETUP.md)
- **로깅 가이드**: [docs/reference/LOGGING_GUIDE.md](docs/reference/LOGGING_GUIDE.md)
- **도구 설정**: [docs/reference/TOOLS_CONFIGURATION.md](docs/reference/TOOLS_CONFIGURATION.md)

## 🔧 설정

### API 키 설정 (`config/config.json`)

```json
{
  "api_keys": {
    "serper_api_key": "your-serper-key",
    "google_api_key": "your-gemini-key"
  },
  "system_settings": {
    "llm_provider": "gemini",
    "llm_model": "gemini-2.0-flash"
  },
  "email_settings": {
    "recipients": ["email@example.com"]
  }
}
```

## 🤖 Agent 구성

### 기본 시스템 (3 Agents)
1. **Researcher**: 맛집 정보 수집
2. **Curator**: 맛집 선별 및 큐레이션
3. **Communicator**: 사용자 친화적 포맷팅

### 고급 시스템 (6 Agents)
1. **Researcher**: 맛집 정보 수집
2. **Curator**: 맛집 선별 및 큐레이션
3. **Communicator**: 추천 결과 정리
4. **Form Creator**: 설문조사 생성
5. **Email Sender**: 이메일 콘텐츠 작성
6. **Data Analyst**: 설문 데이터 분석

## 📊 로깅

모든 실행은 자동으로 로그가 기록됩니다:

- **세션 로그**: `logs/session_YYYYMMDD_HHMMSS.log`
  - 전체 실행 과정
  - Agent 간 통신
  - 프롬프트/응답 상세 내역

- **Task 로그**: `logs/tasks_YYYYMMDD_HHMMSS.json`
  - Task별 실행 정보 (JSON)
  - 실행 시간, 입출력 데이터

## 🧪 테스트

```powershell
# 고급 시스템 테스트
python -m tests.test_advanced_system

# 기본 시스템 테스트
python -m tests.test_restaurant_finder
```

## 📝 라이센스

이 프로젝트는 MIT 라이센스 하에 배포됩니다.

## 🤝 기여

기여를 환영합니다! Pull Request를 제출해 주세요.

## 📞 문의

문제가 발생하면 Issue를 등록해 주세요.

---

**생성일**: 2025-09-30
**최근 업데이트**: 2025-09-30