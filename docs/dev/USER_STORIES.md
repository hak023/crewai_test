# 📖 사용자 스토리 (User Stories)

**프로젝트**: "막내야. 회식 장소 알아봤니?" - AI 회식 장소 추천 시스템  
**작성일**: 2025-10-01  
**버전**: 1.0  
**Product Owner**: Sarah

---

## 🎯 Epic: 팀 회식 장소 추천 자동화

**Epic 설명**: 팀 막내가 회식 장소를 빠르고 정확하게 찾아 추천하고, 팀원들의 의견을 수렴하여 최종 결정을 지원하는 AI 기반 시스템

**비즈니스 가치**: 회식 장소 선정 시간 90% 단축, 팀원 만족도 향상, 막내 직원의 업무 스트레스 감소

---

## 📋 사용자 스토리 목록

### Sprint 1: 핵심 추천 기능 (MVP)

#### Story 1.1: 맛집 정보 수집
#### Story 1.2: AI 기반 맛집 큐레이션
#### Story 1.3: 사용자 친화적 결과 표시

### Sprint 2: 팀 의견 수렴 기능

#### Story 2.1: 설문조사 자동 생성
#### Story 2.2: 이메일 자동 발송

### Sprint 3: 데이터 분석 및 개선

#### Story 3.1: 설문 데이터 분석
#### Story 3.2: 시각화 및 리포트 생성

---

# Sprint 1: 핵심 추천 기능 (MVP)

## Story 1.1: 맛집 정보 수집

### 📌 Story Card

**Story ID**: US-001  
**Title**: 조건에 맞는 맛집 정보 자동 수집  
**Priority**: P0 (필수)  
**Story Points**: 5  
**Sprint**: Sprint 1

### 👤 User Story

```
AS a 팀 막내 직원
I WANT 위치, 예산, 음식 종류를 입력하면 자동으로 맛집 정보를 수집하는 기능
SO THAT 여러 웹사이트를 돌아다니지 않고 빠르게 여러 옵션을 찾을 수 있다
```

### 📋 Acceptance Criteria

```gherkin
GIVEN 사용자가 "광화문 2만원 이하 한식" 조건을 입력했을 때
WHEN 시스템이 맛집 검색을 실행하면
THEN 조건에 맞는 맛집을 최소 5개 이상 수집한다
AND 각 맛집은 다음 정보를 포함한다:
  - 음식점 이름 (필수)
  - 주소 (필수)
  - 전화번호 (필수)
  - 평점 (필수)
  - 가격대 (필수)
  - 메뉴 (선택)
  - 영업시간 (선택)
AND 검색 시간은 30초를 초과하지 않는다
```

### 🔧 Technical Details

**구현 요소**:
- SerperDevTool을 활용한 웹 검색
- 네이버, 구글, 망고플레이트 등 주요 플랫폼 정보 통합
- Researcher Agent 활용

**API 요구사항**:
- Serper API 키 필요
- Gemini API 키 필요

**데이터 구조**:
```python
{
  "name": str,
  "address": str,
  "phone": str,
  "rating": float,
  "price_range": str,
  "menu": str (optional),
  "hours": str (optional)
}
```

### ✅ Definition of Done

- [ ] 조건에 맞는 맛집을 5개 이상 수집
- [ ] 모든 필수 정보 포함 확인
- [ ] 30초 이내 검색 완료 성능 테스트 통과
- [ ] 에러 처리 및 로깅 구현
- [ ] 단위 테스트 작성 및 통과
- [ ] 코드 리뷰 완료

### 🧪 Test Scenarios

**Test Case 1: 정상 검색**
```
Input: "광화문 2만원 이하 한식"
Expected: 5개 이상의 맛집 정보, 모든 필수 필드 포함
```

**Test Case 2: 결과 없음**
```
Input: "북극 1원 이하 프랑스 요리"
Expected: 적절한 에러 메시지 또는 대안 제시
```

**Test Case 3: 성능 테스트**
```
Input: 다양한 조건
Expected: 모든 케이스 30초 이내 완료
```

---

## Story 1.2: AI 기반 맛집 큐레이션

### 📌 Story Card

**Story ID**: US-002  
**Title**: 수집된 맛집을 평가하여 최적의 추천 리스트 선별  
**Priority**: P0 (필수)  
**Story Points**: 8  
**Sprint**: Sprint 1  
**Dependencies**: US-001

### 👤 User Story

```
AS a 팀 막내 직원
I WANT 수집된 여러 맛집 중에서 AI가 평점, 가격, 거리를 고려하여 최적의 옵션을 선별해주는 기능
SO THAT 내가 일일이 비교하지 않아도 자신 있게 추천할 수 있다
```

### 📋 Acceptance Criteria

```gherkin
GIVEN 5개 이상의 맛집 정보가 수집되었을 때
WHEN Curator Agent가 평가를 실행하면
THEN 다음 기준으로 점수를 계산한다:
  - 평점 (40% 가중치): 4.0 이상 우선
  - 가격 적정성 (30% 가중치): 사용자 예산 범위 내
  - 거리 및 접근성 (20% 가중치): 도보 10분 이내
  - 리뷰 품질 (10% 가중치): 최근 긍정적 리뷰
AND 상위 2-3개 맛집을 최종 추천으로 선별한다
AND 각 맛집별로 구체적인 추천 이유를 제시한다
```

### 🔧 Technical Details

**구현 요소**:
- Curator Agent 구현
- 가중치 기반 평가 알고리즘
- 추천 이유 생성 로직

**평가 로직**:
```python
score = (rating * 0.4) + (price_score * 0.3) + 
        (distance_score * 0.2) + (review_score * 0.1)
```

**설정 가능 항목**:
```json
{
  "evaluation_weights": {
    "rating": 0.4,
    "price": 0.3,
    "distance": 0.2,
    "review_quality": 0.1
  }
}
```

### ✅ Definition of Done

- [ ] 평가 기준에 따른 정확한 점수 계산
- [ ] 상위 2-3개 맛집 선별
- [ ] 추천 이유 구체적으로 생성
- [ ] 가중치 설정 가능 (config.json)
- [ ] 단위 테스트 및 통합 테스트 통과
- [ ] 코드 리뷰 완료

### 🧪 Test Scenarios

**Test Case 1: 정상 큐레이션**
```
Input: 5개 맛집 데이터
Expected: 상위 2-3개 선별, 각각 추천 이유 포함
```

**Test Case 2: 동점 처리**
```
Input: 점수가 동일한 맛집들
Expected: 추가 기준(리뷰 수, 최신성)으로 정렬
```

**Test Case 3: 가중치 변경**
```
Input: 가중치 설정 변경 (가격 50%, 평점 30%)
Expected: 변경된 가중치로 정확히 계산
```

---

## Story 1.3: 사용자 친화적 결과 표시

### 📌 Story Card

**Story ID**: US-003  
**Title**: 추천 결과를 읽기 쉬운 형식으로 표시  
**Priority**: P0 (필수)  
**Story Points**: 3  
**Sprint**: Sprint 1  
**Dependencies**: US-002

### 👤 User Story

```
AS a 팀 막내 직원
I WANT 추천 결과가 이모지와 명확한 구조로 정리되어 표시되는 기능
SO THAT 팀장님이나 선배들에게 쉽게 공유하고 설명할 수 있다
```

### 📋 Acceptance Criteria

```gherkin
GIVEN 2-3개의 추천 맛집이 선별되었을 때
WHEN Communicator Agent가 결과를 생성하면
THEN 다음 형식으로 출력된다:
  🍽️ 추천 맛집 리스트
  
  [순위] [맛집명]
  📍 주소: [주소]
  💰 가격대: [가격대]
  ⭐ 평점: [평점]
  🕒 영업시간: [영업시간]
  📞 전화번호: [전화번호]
  
  💡 추천 이유: [구체적인 설명]
AND 모든 필수 정보가 빠짐없이 포함된다
AND 일관된 포맷으로 표시된다
```

### 🔧 Technical Details

**구현 요소**:
- Communicator Agent 구현
- 템플릿 기반 출력 포맷팅
- 이모지 매핑

**출력 템플릿**:
```python
template = """
🍽️ 추천 맛집 리스트

[{rank}] {name}
📍 주소: {address}
💰 가격대: {price_range}
⭐ 평점: {rating}/5
🕒 영업시간: {hours}
📞 전화번호: {phone}

💡 추천 이유: {reason}
"""
```

### ✅ Definition of Done

- [ ] 일관된 포맷으로 출력
- [ ] 모든 필수 정보 포함
- [ ] 이모지 정상 표시 (Windows/Mac/Linux)
- [ ] 한글 인코딩 문제 없음
- [ ] 테스트 통과
- [ ] 코드 리뷰 완료

### 🧪 Test Scenarios

**Test Case 1: 정상 출력**
```
Input: 2개 추천 맛집
Expected: 지정된 형식으로 정확히 출력
```

**Test Case 2: 특수문자 처리**
```
Input: 맛집명에 특수문자 포함
Expected: 특수문자 정상 표시
```

**Test Case 3: 긴 텍스트 처리**
```
Input: 매우 긴 추천 이유
Expected: 적절히 포맷팅 또는 줄바꿈
```

---

# Sprint 2: 팀 의견 수렴 기능

## Story 2.1: 설문조사 자동 생성

### 📌 Story Card

**Story ID**: US-004  
**Title**: 추천 맛집 기반 설문조사 자동 생성  
**Priority**: P1 (중요)  
**Story Points**: 5  
**Sprint**: Sprint 2  
**Dependencies**: US-003

### 👤 User Story

```
AS a 팀 막내 직원
I WANT 추천된 맛집 목록을 바탕으로 자동으로 설문조사가 생성되는 기능
SO THAT 수동으로 설문을 만들지 않고도 팀원들의 의견을 빠르게 수렴할 수 있다
```

### 📋 Acceptance Criteria

```gherkin
GIVEN 2-3개의 추천 맛집이 있을 때
WHEN Form Creator Agent가 설문조사를 생성하면
THEN 다음 항목을 포함한 설문조사가 생성된다:
  1. 추천된 맛집 중 가장 마음에 드는 곳은? (객관식)
  2. 각 맛집의 추천 만족도 (1-5점 척도)
  3. 가격 적정성 평가 (1-5점 척도)
  4. 추가 의견 (주관식)
AND 설문조사 링크가 생성된다
AND 링크는 접근 가능하고 모바일 친화적이다
```

### 🔧 Technical Details

**구현 요소**:
- Form Creator Agent 구현
- 설문 템플릿 생성
- Google Forms 또는 동등한 도구 활용

**설문 구조**:
```yaml
survey:
  title: "[팀명] 회식 장소 의견 조사"
  questions:
    - type: single_choice
      text: "가장 마음에 드는 맛집은?"
      options: [맛집1, 맛집2, 맛집3]
    - type: rating_scale
      text: "각 맛집 만족도 (1-5점)"
      scale: 1-5
    - type: rating_scale
      text: "가격 적정성 (1-5점)"
      scale: 1-5
    - type: long_text
      text: "추가 의견"
```

### ✅ Definition of Done

- [ ] 설문조사 자동 생성 기능 구현
- [ ] 접근 가능한 설문 링크 제공
- [ ] 모바일 반응형 확인
- [ ] 설문 항목 정확성 검증
- [ ] 테스트 통과
- [ ] 코드 리뷰 완료

### 🧪 Test Scenarios

**Test Case 1: 설문 생성**
```
Input: 3개 추천 맛집
Expected: 모든 맛집 포함된 설문 생성, 링크 제공
```

**Test Case 2: 링크 접근성**
```
Action: 생성된 링크 클릭
Expected: 설문 페이지 정상 표시
```

**Test Case 3: 모바일 테스트**
```
Device: 스마트폰 (iOS/Android)
Expected: 모바일에서 정상 작동
```

---

## Story 2.2: 이메일 자동 발송

### 📌 Story Card

**Story ID**: US-005  
**Title**: 추천 결과 및 설문조사 이메일 자동 발송  
**Priority**: P1 (중요)  
**Story Points**: 5  
**Sprint**: Sprint 2  
**Dependencies**: US-004

### 👤 User Story

```
AS a 팀 막내 직원
I WANT 추천 맛집과 설문조사 링크가 자동으로 팀원들에게 이메일로 발송되는 기능
SO THAT 일일이 복사 붙여넣기하지 않고 한 번에 모든 팀원에게 정보를 전달할 수 있다
```

### 📋 Acceptance Criteria

```gherkin
GIVEN 추천 맛집과 설문조사 링크가 준비되었을 때
WHEN Email Sender Agent가 이메일을 발송하면
THEN 다음 내용을 포함한 이메일이 발송된다:
  - 추천 맛집 요약 (2-3줄)
  - 설문조사 링크
  - 참여 기한
  - 문의 연락처
AND config.json에 설정된 모든 수신자에게 발송된다
AND 발송 성공 여부가 로그에 기록된다
```

### 🔧 Technical Details

**구현 요소**:
- Email Sender Agent 구현
- 이메일 템플릿 시스템
- SendGrid API 또는 SMTP 활용

**이메일 템플릿**:
```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
</head>
<body>
  <h2>🍽️ [팀명] 회식 장소 추천</h2>
  
  <p>안녕하세요!</p>
  
  <p>귀하께서 요청하신 회식 장소 추천을 완료했습니다.</p>
  
  <h3>추천 맛집 요약</h3>
  <ul>
    <li>{restaurant1}</li>
    <li>{restaurant2}</li>
    <li>{restaurant3}</li>
  </ul>
  
  <p>더 나은 결정을 위해 간단한 설문조사에 참여해주세요:</p>
  <p><a href="{survey_link}">📋 설문조사 참여하기</a></p>
  
  <p>⏰ 참여 기한: {deadline}</p>
  
  <p>감사합니다!<br>
  막내 올림</p>
</body>
</html>
```

**설정**:
```json
{
  "email_settings": {
    "sender_name": "막내야 시스템",
    "sender_email": "maknae@company.com",
    "recipients": [
      "teamlead@company.com",
      "member1@company.com",
      "member2@company.com"
    ]
  }
}
```

### ✅ Definition of Done

- [ ] 이메일 자동 발송 기능 구현
- [ ] 이메일 템플릿 적용
- [ ] config.json에서 수신자 관리
- [ ] 발송 성공/실패 로깅
- [ ] 테스트 이메일 발송 확인
- [ ] 코드 리뷰 완료

### 🧪 Test Scenarios

**Test Case 1: 정상 발송**
```
Input: 3명의 수신자
Expected: 3명 모두에게 이메일 발송, 로그 기록
```

**Test Case 2: 발송 실패 처리**
```
Input: 잘못된 이메일 주소 포함
Expected: 에러 로깅, 나머지 수신자는 정상 발송
```

**Test Case 3: 이메일 내용 검증**
```
Action: 수신된 이메일 확인
Expected: 모든 필수 내용 포함, 링크 정상 작동
```

---

# Sprint 3: 데이터 분석 및 개선

## Story 3.1: 설문 데이터 분석

### 📌 Story Card

**Story ID**: US-006  
**Title**: 설문조사 응답 데이터 수집 및 분석  
**Priority**: P2 (선택)  
**Story Points**: 5  
**Sprint**: Sprint 3  
**Dependencies**: US-005

### 👤 User Story

```
AS a 팀 막내 직원
I WANT 설문조사 응답 데이터가 자동으로 분석되는 기능
SO THAT 팀원들이 어떤 맛집을 선호하는지 한눈에 파악하고 자신 있게 최종 결정을 내릴 수 있다
```

### 📋 Acceptance Criteria

```gherkin
GIVEN 설문조사 응답이 5개 이상 수집되었을 때
WHEN Data Analyst Agent가 분석을 실행하면
THEN 다음 분석 결과를 제공한다:
  - 응답률 (총 발송 대비 응답 수)
  - 맛집별 선호도 (1위, 2위, 3위)
  - 평균 만족도 점수
  - 가격 적정성 평가
  - 주요 의견 키워드 추출
AND 분석 결과는 구조화된 형식으로 저장된다
```

### 🔧 Technical Details

**구현 요소**:
- Data Analyst Agent 구현
- Pandas를 활용한 데이터 분석
- 통계 분석 로직

**분석 로직**:
```python
analysis = {
    "total_responses": count,
    "response_rate": rate,
    "restaurant_preferences": {
        "restaurant_a": votes,
        "restaurant_b": votes,
        "restaurant_c": votes
    },
    "satisfaction_scores": {
        "restaurant_a": avg_score,
        "restaurant_b": avg_score,
        "restaurant_c": avg_score
    },
    "price_satisfaction": distribution,
    "keywords": extracted_keywords
}
```

### ✅ Definition of Done

- [ ] 설문 응답 데이터 정확히 수집
- [ ] 통계 분석 정확성 검증
- [ ] 키워드 추출 기능 구현
- [ ] 분석 결과 JSON 저장
- [ ] 단위 테스트 통과
- [ ] 코드 리뷰 완료

### 🧪 Test Scenarios

**Test Case 1: 정상 분석**
```
Input: 10개 설문 응답
Expected: 모든 분석 항목 정확히 계산
```

**Test Case 2: 적은 응답**
```
Input: 3개 설문 응답
Expected: 적은 샘플 경고와 함께 분석 제공
```

**Test Case 3: 키워드 추출**
```
Input: 주관식 의견 10개
Expected: 상위 5개 키워드 추출
```

---

## Story 3.2: 시각화 및 리포트 생성

### 📌 Story Card

**Story ID**: US-007  
**Title**: 분석 결과 시각화 및 리포트 생성  
**Priority**: P2 (선택)  
**Story Points**: 5  
**Sprint**: Sprint 3  
**Dependencies**: US-006

### 👤 User Story

```
AS a 팀 막내 직원
I WANT 설문 분석 결과가 차트와 그래프로 시각화된 리포트로 제공되는 기능
SO THAT 팀장님에게 보고할 때 전문적이고 설득력 있게 보일 수 있다
```

### 📋 Acceptance Criteria

```gherkin
GIVEN 설문 분석이 완료되었을 때
WHEN Data Analyst Agent가 시각화를 생성하면
THEN 다음 차트가 포함된 리포트가 생성된다:
  - 맛집별 선호도 막대 그래프
  - 만족도 점수 비교 차트
  - 가격 적정성 분포 파이 차트
AND 리포트는 HTML 또는 PDF 형식으로 저장된다
AND 모든 차트는 한글이 정상 표시된다
```

### 🔧 Technical Details

**구현 요소**:
- Matplotlib/Seaborn 활용 시각화
- HTML/PDF 리포트 생성
- 한글 폰트 설정

**시각화 종류**:
```python
charts = {
    "preference_bar": "맛집별 선호도 막대 그래프",
    "satisfaction_comparison": "만족도 점수 비교 차트",
    "price_pie": "가격 적정성 파이 차트",
    "response_trend": "응답 시간 추이"
}
```

**리포트 템플릿**:
```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>회식 장소 설문조사 분석 리포트</title>
</head>
<body>
  <h1>📊 회식 장소 설문조사 분석 리포트</h1>
  
  <h2>응답 현황</h2>
  <p>총 응답: {total} / 발송: {sent} (응답률: {rate}%)</p>
  
  <h2>맛집 선호도</h2>
  <img src="{preference_chart}">
  
  <h2>만족도 분석</h2>
  <img src="{satisfaction_chart}">
  
  <h2>최종 추천</h2>
  <p>{recommendation}</p>
</body>
</html>
```

### ✅ Definition of Done

- [ ] 모든 차트 정상 생성
- [ ] 한글 폰트 정상 표시
- [ ] HTML/PDF 리포트 생성
- [ ] 리포트 품질 검증
- [ ] 테스트 통과
- [ ] 코드 리뷰 완료

### 🧪 Test Scenarios

**Test Case 1: 리포트 생성**
```
Input: 분석 데이터
Expected: 모든 차트 포함된 HTML 리포트 생성
```

**Test Case 2: 한글 표시**
```
Check: 모든 차트의 라벨, 제목
Expected: 한글 깨짐 없이 정상 표시
```

**Test Case 3: PDF 변환**
```
Action: HTML → PDF 변환
Expected: PDF에서도 차트 정상 표시
```

---

## 📊 Sprint 계획 요약

### Sprint 1: 핵심 추천 기능 (MVP)
- **Story Points**: 16
- **Duration**: 2주
- **Goal**: 사용자가 조건을 입력하면 AI가 맛집을 추천하는 핵심 기능 완성
- **Stories**: US-001, US-002, US-003

### Sprint 2: 팀 의견 수렴 기능
- **Story Points**: 10
- **Duration**: 2주
- **Goal**: 설문조사 자동 생성 및 이메일 발송으로 팀 협업 지원
- **Stories**: US-004, US-005

### Sprint 3: 데이터 분석 및 개선
- **Story Points**: 10
- **Duration**: 2주
- **Goal**: 설문 데이터 분석 및 시각화로 의사결정 지원
- **Stories**: US-006, US-007

**Total Story Points**: 36  
**Total Duration**: 6주

---

## 🎯 Release 계획

### Release 1.0 (MVP)
- Sprint 1 완료 후 배포
- 기본 맛집 추천 기능 제공
- 타겟 사용자: 파일럿 팀 (5-10명)

### Release 2.0
- Sprint 2 완료 후 배포
- 팀 의견 수렴 기능 추가
- 타겟 사용자: 전체 조직 (50-100명)

### Release 3.0
- Sprint 3 완료 후 배포
- 데이터 분석 및 리포트 기능 추가
- 타겟 사용자: 전사 확대

---

## 📝 Notes

**Product Owner 승인**: ✅ Sarah  
**Stakeholder 검토**: Pending  
**Technical Lead 검토**: Pending

**참고 문서**:
- [사용자 요구사항](./USER_REQUIREMENTS.md)
- [기술 명세서](./TECHNICAL_SPECIFICATION.md)
- [빠른 시작 가이드](../guides/QUICK_START.md)

---

**문서 히스토리**:
- 2025-10-01: 초안 작성 (v1.0)

