# 🚀 CrewAI 맛집 추천 시스템 설정 가이드

이 가이드는 CrewAI 맛집 추천 시스템을 쉽게 설정하고 실행하는 방법을 설명합니다.

## 📋 목차
1. [빠른 시작](#빠른-시작)
2. [설정 파일 구성](#설정-파일-구성)
3. [실행 방법](#실행-방법)
4. [문제 해결](#문제-해결)

## 🚀 빠른 시작

### 1단계: 설정 파일 생성
```bash
python setup_config.py
```
- 메뉴에서 "1. 설정 파일 생성" 선택
- `config.json` 파일이 생성됩니다

### 2단계: API 키 설정
```bash
python setup_config.py
```
- 메뉴에서 "2. API 키 설정" 선택
- OpenAI API 키 입력 (필수)
- 다른 API 키들 입력 (선택사항)

### 3단계: 시스템 실행
```powershell
# PowerShell 사용
.\run_simple.ps1 -Mode basic

# 또는 직접 실행
python restaurant_finder.py
```

## ⚙️ 설정 파일 구성

### config.json 구조
```json
{
  "api_keys": {
    "openai_api_key": "your-openai-api-key-here",
    "serper_api_key": "your-serper-api-key-here",
    "sendgrid_api_key": "your-sendgrid-api-key-here"
  },
  "system_settings": {
    "llm_model": "gpt-3.5-turbo",
    "temperature": 0.7
  },
  "restaurant_settings": {
    "max_recommendations": 5,
    "evaluation_weights": {
      "rating": 0.4,
      "price": 0.3,
      "distance": 0.2,
      "review_quality": 0.1
    }
  }
}
```

### 필수 설정
- **openai_api_key**: OpenAI API 키 (필수)
- **llm_model**: 사용할 LLM 모델 (기본값: gpt-3.5-turbo)
- **temperature**: 모델의 창의성 수준 (0.0-1.0)

### 선택적 설정
- **serper_api_key**: 웹 검색용 (선택사항)
- **sendgrid_api_key**: 이메일 발송용 (고급 시스템)
- **google_credentials**: 구글 폼/스프레드시트용 (고급 시스템)

## 🎮 실행 방법

### PowerShell 스크립트 사용 (권장)
```powershell
# 도움말 보기
.\run_simple.ps1 -Help

# 기본 시스템 실행
.\run_simple.ps1 -Mode basic

# 고급 시스템 실행
.\run_simple.ps1 -Mode advanced

# 테스트 실행
.\run_simple.ps1 -Test
```

### 직접 Python 실행
```bash
# 기본 시스템
python restaurant_finder.py

# 고급 시스템
python advanced_restaurant_system.py

# 테스트
python test_restaurant_finder.py
python test_advanced_system.py
```

### 설정 도구 사용
```bash
# 설정 도구 실행
python setup_config.py

# 설정 검증
python config_manager.py
```

## 📁 파일 구조

```
workspace_crewai_test/
├── run_simple.ps1              # PowerShell 실행 스크립트
├── setup_config.py             # 설정 도구
├── config_manager.py            # 설정 관리 모듈
├── config.json                 # 설정 파일 (생성 필요)
├── config_example.json         # 설정 예시 파일
├── restaurant_finder.py        # 기본 맛집 추천 시스템
├── advanced_restaurant_system.py # 고급 시스템
├── test_restaurant_finder.py   # 기본 시스템 테스트
├── test_advanced_system.py     # 고급 시스템 테스트
├── requirements.txt            # 필요한 패키지 목록
└── README.md                   # 기본 설명서
```

## 🔧 시스템 모드

### 기본 시스템 (restaurant_finder.py)
- **에이전트**: 리서처, 큐레이터, 커뮤니케이터 (3개)
- **기능**: 맛집 추천만 수행
- **사용법**: `python restaurant_finder.py`

### 고급 시스템 (advanced_restaurant_system.py)
- **에이전트**: 6개 (기본 3개 + 폼 생성, 이메일 발송, 데이터 분석)
- **기능**: 맛집 추천 + 설문조사 + 데이터 분석
- **사용법**: `python advanced_restaurant_system.py`

## 🔍 문제 해결

### 일반적인 문제들

#### 1. Python이 설치되지 않음
```bash
# Python 설치 확인
python --version

# Python 설치: https://python.org/downloads/
```

#### 2. 패키지 설치 실패
```bash
# pip 업그레이드
python -m pip install --upgrade pip

# 패키지 재설치
pip install -r requirements.txt --force-reinstall
```

#### 3. API 키 오류
```bash
# 설정 검증
python setup_config.py
# 메뉴에서 "4. 설정 검증" 선택
```

#### 4. 설정 파일 없음
```bash
# 설정 파일 생성
python setup_config.py
# 메뉴에서 "1. 설정 파일 생성" 선택
```

#### 5. PowerShell 실행 정책 오류
```powershell
# 실행 정책 변경
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 또는 우회 실행
powershell -ExecutionPolicy Bypass -File run_simple.ps1
```

### 로그 확인
```bash
# 시스템 로그 확인 (있는 경우)
cat logs/system.log

# Python 오류 확인
python -c "import crewai; print('CrewAI 설치 확인')"
```

## 📞 지원

### 자주 묻는 질문

**Q: OpenAI API 키는 어디서 구하나요?**
A: https://platform.openai.com/api-keys 에서 생성할 수 있습니다.

**Q: 시스템이 실행되지 않아요**
A: `python setup_config.py`로 설정을 확인하고, `python test_restaurant_finder.py`로 테스트해보세요.

**Q: 고급 시스템을 사용하려면?**
A: Google API와 SendGrid API 키가 필요합니다. `config.json`에서 설정하세요.

**Q: PowerShell 스크립트가 실행되지 않아요**
A: `powershell -ExecutionPolicy Bypass -File run_simple.ps1`로 실행하세요.

### 추가 도움말
- [CrewAI 공식 문서](https://docs.crewai.com/)
- [OpenAI API 문서](https://platform.openai.com/docs)
- [PowerShell 실행 정책](https://docs.microsoft.com/powershell/module/microsoft.powershell.core/about/about_execution_policies)

## 🎉 완료!

설정이 완료되면 다음과 같이 실행할 수 있습니다:

```powershell
# 기본 시스템
.\run_simple.ps1 -Mode basic

# 고급 시스템
.\run_simple.ps1 -Mode advanced

# 테스트
.\run_simple.ps1 -Test
```

즐거운 맛집 탐험 되세요! 🍽️✨
