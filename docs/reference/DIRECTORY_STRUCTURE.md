# 📁 프로젝트 디렉토리 구조

## 🎯 새로운 디렉토리 구조

```
workspace_crewai_test/
├── src/                          # 소스 코드
│   ├── __init__.py              # Python 패키지 초기화
│   ├── advanced_restaurant_system.py
│   ├── restaurant_finder.py
│   ├── config_manager.py
│   └── logging_manager.py
│
├── config/                       # 설정 파일
│   ├── config.json              # 실제 설정 (git ignore)
│   ├── config_example.json      # 설정 예시
│   ├── env_example.txt          # 환경 변수 예시
│   └── google_credentials.json  # Google API 인증 (git ignore)
│
├── docs/                         # 문서
│   ├── guides/                  # 사용 가이드
│   │   ├── SETUP_GUIDE.md
│   │   ├── QUICK_START.md
│   │   ├── GEMINI_SETUP.md
│   │   └── EMAIL_CONFIG_GUIDE.md
│   ├── reference/               # 참조 문서
│   │   ├── ADVANCED_README.md
│   │   ├── LOGGING_GUIDE.md
│   │   ├── LOGGING_IMPROVEMENTS.md
│   │   ├── TOOLS_CONFIGURATION.md
│   │   └── AGENT_FIX_GUIDE.md
│   └── DIRECTORY_STRUCTURE.md   # 이 파일
│
├── tests/                        # 테스트 파일
│   ├── __init__.py
│   ├── test_advanced_system.py
│   └── test_restaurant_finder.py
│
├── scripts/                      # 실행 스크립트
│   ├── run_restaurant_system.ps1
│   ├── run_simple.ps1
│   └── setup_config.py
│
├── templates/                    # 템플릿 파일
│   ├── email_template.html
│   └── report_template.html
│
├── logs/                         # 로그 파일 (자동 생성)
│   ├── session_*.log
│   └── tasks_*.json
│
├── __pycache__/                  # Python 캐시 (git ignore)
├── README.md                     # 프로젝트 메인 README
└── requirements.txt              # Python 패키지 의존성

```

## 📋 디렉토리 설명

### `/src/` - 소스 코드
- **목적**: 모든 Python 소스 코드를 한 곳에서 관리
- **파일**:
  - `advanced_restaurant_system.py`: 고급 맛집 추천 시스템
  - `restaurant_finder.py`: 기본 맛집 추천 시스템
  - `config_manager.py`: 설정 관리
  - `logging_manager.py`: 로깅 관리
  - `__init__.py`: 패키지 초기화

### `/config/` - 설정 파일
- **목적**: 모든 설정 파일을 중앙 집중 관리
- **파일**:
  - `config.json`: 실제 사용 설정 (개인 정보 포함, .gitignore)
  - `config_example.json`: 설정 예시 템플릿
  - `env_example.txt`: 환경 변수 설정 예시
  - `google_credentials.json`: Google API 인증 (개인 정보, .gitignore)

### `/docs/` - 문서
- **목적**: 모든 문서를 체계적으로 분류
- **하위 디렉토리**:
  - `guides/`: 사용자 가이드 및 설정 안내
  - `reference/`: 기술 참조 문서 및 개선 기록

### `/tests/` - 테스트 파일
- **목적**: 모든 테스트 코드를 별도 관리
- **파일**:
  - `test_advanced_system.py`: 고급 시스템 테스트
  - `test_restaurant_finder.py`: 기본 시스템 테스트

### `/scripts/` - 실행 스크립트
- **목적**: 실행 및 설정 스크립트 분리
- **파일**:
  - `run_restaurant_system.ps1`: 메인 실행 스크립트
  - `run_simple.ps1`: 간단 실행 스크립트
  - `setup_config.py`: 설정 초기화 스크립트

### `/templates/` - 템플릿 파일
- **목적**: HTML, 이메일 템플릿 관리
- **파일**:
  - `email_template.html`: 이메일 템플릿
  - `report_template.html`: 리포트 템플릿

### `/logs/` - 로그 파일
- **목적**: 실행 로그 자동 저장
- **파일**: 
  - `session_YYYYMMDD_HHMMSS.log`: 세션 로그
  - `tasks_YYYYMMDD_HHMMSS.json`: Task 상세 로그

---

## 🔄 마이그레이션 가이드

### Before (기존)
```
workspace_crewai_test/
├── advanced_restaurant_system.py
├── restaurant_finder.py
├── config_manager.py
├── logging_manager.py
├── config.json
├── ADVANCED_README.md
├── AGENT_FIX_GUIDE.md
├── ... (수많은 파일들)
```

### After (개선)
```
workspace_crewai_test/
├── src/              # 소스 코드
├── config/           # 설정
├── docs/             # 문서
├── tests/            # 테스트
├── scripts/          # 스크립트
├── templates/        # 템플릿
├── logs/             # 로그
├── README.md
└── requirements.txt
```

---

## 💡 Import 경로 변경

### Before (기존)
```python
from config_manager import load_config
from logging_manager import get_logging_manager
```

### After (개선)
```python
from src.config_manager import load_config
from src.logging_manager import get_logging_manager
```

또는 Python path 설정:
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config_manager import load_config
from src.logging_manager import get_logging_manager
```

---

## 📝 .gitignore 권장 사항

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python

# 환경
venv/
env/
ENV/

# 설정 파일 (개인 정보)
config/config.json
config/google_credentials.json

# 로그
logs/*.log
logs/*.json

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
```

---

## 🚀 실행 방법 변경

### Before (기존)
```powershell
.\run_restaurant_system.ps1
python advanced_restaurant_system.py
```

### After (개선)
```powershell
.\scripts\run_restaurant_system.ps1
python -m src.advanced_restaurant_system
```

또는 스크립트에서 자동으로 경로 처리

---

## ✅ 개선 효과

1. **가독성 향상** 📖
   - 파일 역할이 디렉토리로 명확히 구분됨
   
2. **유지보수 용이** 🔧
   - 관련 파일들이 그룹화되어 수정이 쉬움
   
3. **확장성** 📈
   - 새 기능 추가 시 적절한 디렉토리에 배치
   
4. **Git 관리** 🌿
   - .gitignore로 개인 정보 보호 용이
   
5. **협업** 👥
   - 프로젝트 구조가 명확하여 새로운 개발자 온보딩 쉬움

---

## 📞 다음 단계

1. ✅ 디렉토리 생성
2. ✅ 파일 이동
3. ✅ Import 경로 수정
4. ✅ 스크립트 경로 업데이트
5. ✅ .gitignore 생성
6. ✅ README 업데이트
7. ✅ 테스트 실행

---

생성일: 2025-09-30
