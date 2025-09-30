# 🛠️ Agent 도구 설정 가이드

## 📋 개요

[CrewAI 공식 문서](https://docs.crewai.com/en/concepts/tools)를 참조하여 각 Agent에게 역할에 맞는 도구를 설정했습니다.

## 🎯 Agent별 도구 설정

### 1. **Researcher (맛집 정보 수집 전문가)** 🔍

#### 할당된 도구
- ✅ **SerperDevTool**: 웹 검색 (맛집 정보, 리뷰, 평점)
- ✅ **WebsiteSearchTool**: 웹사이트 탐색 (메뉴, 가격, 영업시간)

#### 도구 사용 목적
```python
tools=[self.search_tool, self.web_search_tool]
```

**사용 시나리오:**
1. SerperDevTool로 "광화문 중화요리 맛집" 검색
2. 검색 결과에서 맛집 목록 추출
3. WebsiteSearchTool로 각 맛집의 공식 웹사이트 탐색
4. 메뉴, 가격, 영업시간 등 상세 정보 수집

**수집하는 정보:**
- 맛집 이름, 주소, 전화번호
- 평점 및 리뷰 (네이버, 구글, 망고플레이트)
- 가격대 및 메뉴
- 영업시간, 휴무일
- 최근 리뷰 트렌드

---

### 2. **Curator (맛집 큐레이터)** 📊

#### 할당된 도구
- ✅ **WebsiteSearchTool**: 정보 검증용

#### 도구 사용 목적
```python
tools=[self.web_search_tool]
```

**사용 시나리오:**
1. Researcher가 수집한 데이터 분석
2. 의심스러운 정보 발견 시 WebsiteSearchTool로 직접 확인
3. 평점, 가격, 리뷰 등을 검증
4. 최종 3-5개 맛집 선별

**평가 기준:**
- 평점 (40% 가중치) - 4.0 이상 우선
- 가격 적정성 (30%) - 사용자 예산 범위 내
- 거리 및 접근성 (20%) - 요청 위치에서 가까운 곳
- 리뷰 품질 (10%) - 최근 긍정적 리뷰 많은 곳

---

### 3. **Communicator (맛집 추천 커뮤니케이터)** 💬

#### 할당된 도구
- ❌ 없음 (텍스트 정리 및 포맷팅만 수행)

#### 역할
```python
tools=[]  # 도구 불필요
```

**수행 작업:**
- Curator가 선별한 맛집 리스트를 사용자 친화적으로 포맷팅
- 이모지와 구조화된 형식으로 정리
- 추천 이유를 명확하게 전달

---

### 4. **Form Creator (설문조사 폼 생성 전문가)** 📝

#### 할당된 도구
- ❌ 없음 (LLM 기반 설문 설계)

#### 역할
```python
tools=[]  # 도구 불필요
```

**수행 작업:**
- 추천된 맛집을 바탕으로 설문 문항 설계
- 객관식, 척도, 주관식 문항 구성
- 구글 폼 API 연동 (코드로 처리)

---

### 5. **Email Sender (이메일 마케팅 전문가)** 📧

#### 할당된 도구
- ❌ 없음 (이메일 템플릿 작성만)

#### 역할
```python
tools=[]  # 도구 불필요
```

**수행 작업:**
- 설문조사 참여 유도 이메일 작성
- 친근하고 매력적인 문구 구성
- 이메일 API 연동 (코드로 처리)

---

### 6. **Data Analyst (데이터 분석 및 시각화 전문가)** 📈

#### 할당된 도구
- ❌ 없음 (LLM 기반 데이터 분석)

#### 역할
```python
tools=[]  # 도구 불필요
```

**수행 작업:**
- 설문 응답 데이터 통계 분석
- 트렌드 및 패턴 파악
- 인사이트 도출 및 보고서 작성

---

## 📊 도구 활용 전략

### CrewAI 도구의 주요 특징

[공식 문서](https://docs.crewai.com/en/concepts/tools)에 따르면:

✅ **Error Handling**: 모든 도구는 오류 처리 기능 내장
✅ **Caching**: 이전 결과 재사용으로 성능 최적화
✅ **Asynchronous Support**: 비동기 작업 지원

### 도구 선택 기준

| Agent | 도구 필요 여부 | 이유 |
|-------|---------------|------|
| **Researcher** | ✅ 필수 | 외부 정보 수집 필요 |
| **Curator** | ⚠️ 선택 | 정보 검증 시 유용 |
| **Communicator** | ❌ 불필요 | 텍스트 처리만 |
| **Form Creator** | ❌ 불필요 | LLM으로 충분 |
| **Email Sender** | ❌ 불필요 | LLM으로 충분 |
| **Data Analyst** | ❌ 불필요 | LLM으로 충분 |

---

## 🔧 Task 설명 개선

### Before ❌

```python
description="""사용자 요청: {user_request}
다음 정보를 수집하세요:
1. 맛집 정보
2. 평점 정보
..."""
```

### After ✅

```python
description="""사용자 요청: {user_request}

**사용 가능한 도구:**
- SerperDevTool: 웹 검색으로 맛집 정보 검색
- WebsiteSearchTool: 웹사이트에서 상세 정보 추출

**도구 사용 가이드:**
- 먼저 SerperDevTool로 맛집 목록을 검색하세요
- 각 맛집을 WebsiteSearchTool로 탐색하세요
..."""
```

---

## 🚀 개선 효과

### 1. **Researcher 강화** 🔍
- ✅ SerperDevTool로 광범위한 검색
- ✅ WebsiteSearchTool로 상세 정보 추출
- ✅ 5~10개 맛집 정보 수집 가능

### 2. **Curator 검증 기능 추가** 📊
- ✅ WebsiteSearchTool로 정보 검증
- ✅ 의심스러운 데이터 직접 확인
- ✅ 더 정확한 추천 가능

### 3. **명확한 Task 가이드** 📝
- ✅ 도구 사용법 명시
- ✅ 기대 결과 구체화
- ✅ Agent의 도구 활용도 증가

---

## 💡 실행 예시

### Researcher의 도구 사용

```
1. SerperDevTool 호출
   입력: "광화문 중화요리 26000원 30000원"
   결과: [맛집A, 맛집B, 맛집C, ...]

2. WebsiteSearchTool 호출 (각 맛집마다)
   입력: "맛집A 공식 웹사이트"
   결과: 메뉴, 가격, 영업시간 등

3. 수집된 정보 구조화
   - 맛집A: {이름, 주소, 전화, 평점, ...}
   - 맛집B: {이름, 주소, 전화, 평점, ...}
   ...
```

### Curator의 도구 사용

```
1. Researcher 데이터 분석
   - 평점 4.5 -> 높음
   - 가격 28000원 -> 예산 범위 내
   - 거리 500m -> 가까움

2. 의심스러운 정보 발견 시
   WebsiteSearchTool 호출
   입력: "맛집A 최신 메뉴 가격"
   결과: 실제 가격 확인

3. 최종 선별
   - 맛집A: 점수 9.2/10
   - 맛집B: 점수 8.8/10
   - 맛집C: 점수 8.5/10
```

---

## 📚 참고 자료

### CrewAI 공식 문서
- [Tools Overview](https://docs.crewai.com/en/concepts/tools)
- [Available CrewAI Tools](https://docs.crewai.com/en/concepts/tools#available-crewai-tools)
- [Creating Custom Tools](https://docs.crewai.com/en/concepts/tools#creating-your-own-tools)

### 사용 가능한 도구
- **SerperDevTool**: 웹 검색 전문 도구
- **WebsiteSearchTool**: 웹사이트 RAG 검색 도구
- **FileReadTool**: 파일 읽기
- **DirectoryReadTool**: 디렉토리 탐색
- 그 외 20+ 도구 사용 가능

---

## ✅ 체크리스트

### Agent 도구 설정
- [x] Researcher: SerperDevTool + WebsiteSearchTool
- [x] Curator: WebsiteSearchTool
- [x] Communicator: 도구 없음
- [x] Form Creator: 도구 없음
- [x] Email Sender: 도구 없음
- [x] Data Analyst: 도구 없음

### Task 설명 개선
- [x] Research Task: 도구 사용 가이드 추가
- [x] Curation Task: 도구 활용 명시
- [x] Communication Task: 포맷팅 가이드
- [x] Form Creation Task: 설문 설계 가이드
- [x] Email Sending Task: 이메일 작성 가이드
- [x] Data Analysis Task: 분석 기준 명시

### 로깅
- [x] 도구 사용 내역 로그에 기록
- [x] 도구 호출 결과 추적
- [x] 에러 핸들링 및 재시도 로직

---

## 🎉 결론

이제 Agent들은:
- ✅ 역할에 맞는 도구로 **실제 정보 수집** 가능
- ✅ 명확한 Task 가이드로 **도구 활용도 증가**
- ✅ CrewAI의 강력한 도구 생태계 활용
- ✅ 더 정확하고 실용적인 결과 생성

Agent들이 이제 제대로 동작할 것입니다! 🚀
