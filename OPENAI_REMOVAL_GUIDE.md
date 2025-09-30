# 🔧 OpenAI 제거 및 Gemini 전용 구성

**날짜**: 2025-09-30  
**작업**: WebsiteSearchTool의 OpenAI 의존성 제거

---

## 🚨 문제 발견

### 오류 메시지
```
Tool Usage Failed
Name: Search in a specific website
Error: Error code: 429 - {'error': {'message': 'You exceeded your current quota, 
please check your plan and billing details.', 'type': 'insufficient_quota', 
'param': None, 'code': 'insufficient_quota'}} in upsert.
```

### 원인 분석
- **WebsiteSearchTool**이 내부적으로 OpenAI API를 사용
- RAG (Retrieval Augmented Generation) 기능에서 임베딩과 LLM 필요
- 기본값으로 OpenAI를 사용하도록 설정되어 있음
- Gemini를 사용하도록 설정했지만, 일부 도구는 여전히 OpenAI 참조

---

## ✅ 해결 방법

### 1. WebsiteSearchTool 제거

#### src/advanced_restaurant_system.py
```python
# Before ❌
from crewai_tools import SerperDevTool, WebsiteSearchTool, CodeInterpreterTool
self.web_search_tool = WebsiteSearchTool()
tools=[self.search_tool, self.web_search_tool]

# After ✅
from crewai_tools import SerperDevTool, CodeInterpreterTool
# WebsiteSearchTool은 OpenAI를 내부적으로 사용하므로 Gemini 환경에서는 제외
# self.web_search_tool = WebsiteSearchTool()
tools=[self.search_tool]  # SerperDevTool만 사용 (Gemini 호환)
```

#### src/restaurant_finder.py
```python
# Before ❌
from crewai_tools import SerperDevTool, WebsiteSearchTool
self.web_search_tool = WebsiteSearchTool()

# After ✅
from crewai_tools import SerperDevTool
# WebsiteSearchTool은 OpenAI를 내부적으로 사용하므로 Gemini 환경에서는 제외
# self.web_search_tool = WebsiteSearchTool()
```

---

### 2. Agent Tools 재구성

#### Researcher Agent
```python
# Before
tools=[self.search_tool, self.web_search_tool]

# After
tools=[self.search_tool]  # SerperDevTool만 사용
```

#### Curator Agent
```python
# Before
tools=[self.web_search_tool]

# After
tools=[]  # 도구 없이 리서처의 정보만으로 분석
```

---

### 3. Task 설명 업데이트

#### research_task
```python
# Before
**사용 가능한 도구:**
- SerperDevTool: 웹 검색으로 맛집 정보, 리뷰, 평점 등을 검색
- WebsiteSearchTool: 맛집 웹사이트에서 메뉴, 가격, 영업시간 등 상세 정보 추출

**도구 사용 가이드:**
- 먼저 SerperDevTool로 맛집 목록을 검색하세요
- 각 맛집의 공식 웹사이트나 리뷰 사이트를 WebsiteSearchTool로 탐색하세요

# After
**사용 가능한 도구:**
- SerperDevTool: 웹 검색으로 맛집 정보, 리뷰, 평점, 메뉴, 가격, 영업시간 등을 검색

**도구 사용 가이드:**
- SerperDevTool로 맛집 목록, 리뷰, 평점, 메뉴, 가격 등을 종합적으로 검색하세요
- 다양한 검색어를 사용하여 더 많은 정보를 수집하세요 (예: "맛집명 리뷰", "맛집명 메뉴", "맛집명 가격")
```

#### curation_task
```python
# Before
**사용 가능한 도구:**
- WebsiteSearchTool: 의심스러운 정보가 있을 경우 웹사이트에서 직접 확인

**선별 프로세스:**
2. 의심스러운 정보는 WebsiteSearchTool로 직접 확인

# After
**선별 프로세스:**
1. 리서처의 데이터를 평가 기준에 따라 점수화
2. 상위 3-5개의 맛집을 선별
```

---

### 4. Config 검증 로직 수정

#### src/config_manager.py
```python
# Before
required_keys = ['openai_api_key']

for key in required_keys:
    if not api_keys.get(key):
        self.logger.warning(f"필수 API 키가 설정되지 않았습니다: {key}")

# After
llm_provider = system_settings.get('llm_provider', 'gemini')

if llm_provider == 'gemini':
    if not api_keys.get('gemini_api_key'):
        self.logger.warning(f"필수 API 키가 설정되지 않았습니다: gemini_api_key")
elif llm_provider == 'openai':
    if not api_keys.get('openai_api_key'):
        self.logger.warning(f"필수 API 키가 설정되지 않았습니다: openai_api_key")
```

---

## 📊 변경된 파일

1. ✅ `src/advanced_restaurant_system.py`
   - WebsiteSearchTool import 제거 및 주석 처리
   - Researcher: tools=[self.search_tool]
   - Curator: tools=[]
   - research_task 설명 수정
   - curation_task 설명 수정

2. ✅ `src/restaurant_finder.py`
   - WebsiteSearchTool import 제거 및 주석 처리
   - Researcher: tools=[self.search_tool]

3. ✅ `src/config_manager.py`
   - validate_config 수정 (LLM provider별 API 키 검증)

---

## 🎯 대체 전략

### WebsiteSearchTool의 기능을 SerperDevTool로 대체

#### 기존 (WebsiteSearchTool)
- 특정 웹사이트에서 정보 추출
- RAG 기반 정보 검색
- OpenAI 임베딩 사용

#### 대체 (SerperDevTool + 더 나은 검색 쿼리)
```python
# 예시: 더 구체적인 검색 쿼리 사용
"맛집명 + 메뉴"
"맛집명 + 가격"
"맛집명 + 영업시간"
"맛집명 + 리뷰"
```

### 장점
✅ OpenAI API 의존성 제거  
✅ 비용 절감 (Gemini만 사용)  
✅ 더 안정적인 실행 (할당량 초과 없음)  
✅ SerperDevTool의 강력한 검색 기능 활용

### 단점
⚠️ 특정 웹사이트의 세부 정보 추출 제한  
⚠️ 구조화된 데이터 추출이 약간 어려울 수 있음

---

## 🧪 테스트 계획

### 1. Agent 생성 테스트
```powershell
python -c "from src.advanced_restaurant_system import AdvancedRestaurantSystem; sys = AdvancedRestaurantSystem()"
```

### 2. 맛집 검색 테스트
```powershell
python -m src.restaurant_finder
```

### 3. 고급 시스템 실행 테스트
```powershell
.\scripts\run_restaurant_system.ps1
```

---

## 📝 향후 개선 사항

### 1. Gemini 호환 도구 탐색
- CrewAI Tools에서 Gemini를 지원하는 다른 RAG 도구 찾기
- 또는 직접 Gemini Embeddings를 사용하는 커스텀 도구 개발

### 2. SerperDevTool 최적화
- 더 효과적인 검색 쿼리 패턴 개발
- 검색 결과 파싱 로직 개선

### 3. 커스텀 도구 개발 (선택사항)
```python
from crewai_tools import tool
from langchain_google_genai import GoogleGenerativeAIEmbeddings

@tool("Website Content Extractor")
def extract_website_content(url: str) -> str:
    """웹사이트에서 내용을 추출 (Gemini 호환)"""
    # Gemini embeddings 사용
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    # ... 구현 ...
    pass
```

---

## ✅ 체크리스트

- [x] WebsiteSearchTool import 제거
- [x] WebsiteSearchTool 초기화 코드 주석 처리
- [x] Researcher Agent tools 수정
- [x] Curator Agent tools 수정
- [x] research_task 설명 업데이트
- [x] curation_task 설명 업데이트
- [x] config_manager validate_config 수정
- [x] 문서 작성 (OPENAI_REMOVAL_GUIDE.md)
- [ ] 테스트 실행 및 검증
- [ ] GitHub 커밋

---

## 🔍 관련 파일

- `src/advanced_restaurant_system.py` - Agent 및 Task 정의
- `src/restaurant_finder.py` - 기본 맛집 검색 시스템
- `src/config_manager.py` - 설정 및 검증
- `config/config.json` - API 키 및 시스템 설정

---

**완료 시각**: 2025-09-30  
**다음 단계**: 시스템 테스트 및 GitHub 업데이트
