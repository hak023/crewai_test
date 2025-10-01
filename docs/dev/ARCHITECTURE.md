# 🏗️ 시스템 아키텍처 문서

**프로젝트**: "막내야. 회식 장소 알아봤니?" - AI 회식 장소 추천 시스템  
**문서 타입**: Technical Architecture Document  
**작성일**: 2025-10-01  
**버전**: 1.0  
**Architect**: Winston

---

## 📋 목차

1. [시스템 개요](#시스템-개요)
2. [아키텍처 원칙](#아키텍처-원칙)
3. [기술 스택](#기술-스택)
4. [시스템 아키텍처](#시스템-아키텍처)
5. [에이전트 아키텍처](#에이전트-아키텍처)
6. [데이터 흐름](#데이터-흐름)
7. [API 및 외부 통합](#api-및-외부-통합)
8. [보안 설계](#보안-설계)
9. [로깅 및 모니터링](#로깅-및-모니터링)
10. [배포 아키텍처](#배포-아키텍처)
11. [확장성 및 성능](#확장성-및-성능)
12. [향후 개선 사항](#향후-개선-사항)

---

## 🎯 시스템 개요

### 비즈니스 컨텍스트

"막내야. 회식 장소 알아봤니?" 시스템은 회사 팀의 막내 직원이 회식 장소를 빠르고 정확하게 추천받을 수 있도록 돕는 AI 기반 자동화 시스템입니다.

**핵심 가치 제안**:
- ⚡ 회식 장소 검색 시간 90% 단축 (30분 → 2분)
- 🎯 AI 기반 정확한 큐레이션
- 📊 팀 의견 수렴 자동화
- 📈 데이터 기반 의사결정 지원

### 시스템 목표

1. **자동화**: 맛집 검색부터 설문조사까지 전 과정 자동화
2. **정확성**: AI 기반 평가 기준으로 최적의 추천 제공
3. **협업**: 팀원 의견 수렴 및 데이터 분석 지원
4. **확장성**: 다양한 지역, 음식 종류, 예산 범위 지원

---

## 🎨 아키텍처 원칙

### 1. Multi-Agent Collaboration
- 6개의 전문 AI 에이전트가 협력하여 작업 수행
- 각 에이전트는 단일 책임 원칙(SRP) 준수
- Sequential Process로 단계별 명확한 작업 흐름

### 2. AI-First Design
- 모든 핵심 기능은 AI 에이전트가 수행
- 사람은 조건 입력과 최종 승인만 담당
- LLM(Gemini)을 활용한 자연어 처리

### 3. Event-Driven Logging
- 모든 에이전트 활동과 통신을 상세히 기록
- 구조화된 로그(JSON) + 가독성 높은 텍스트 로그
- 디버깅과 성능 분석을 위한 풍부한 메타데이터

### 4. Configuration-Driven
- 모든 설정은 `config.json`에서 중앙 관리
- API 키, 이메일 수신자, 평가 가중치 등 외부화
- 환경별 설정 분리 가능

### 5. Fail-Safe & Resilience
- API 오류 시 재시도 로직
- 부분 실패 시에도 결과 제공
- 명확한 에러 메시지와 로깅

---

## 💻 기술 스택

### Core Technologies

#### Programming Language
- **Python 3.11+**
  - 이유: AI/ML 생태계 지원, 풍부한 라이브러리
  - 주요 라이브러리: crewai, langchain, pandas, matplotlib

#### AI Framework
- **CrewAI 0.80.0+**
  - Multi-agent orchestration
  - Task management
  - Agent collaboration patterns

#### LLM (Large Language Model)
- **Google Gemini 2.0 Flash**
  - 이유: 빠른 응답 속도, 한글 지원 우수, 비용 효율적
  - 대안: OpenAI GPT-3.5/4 (호환 가능)

### External Services

#### Search & Information Retrieval
- **Serper API**
  - Google 검색 결과 수집
  - 맛집 정보, 평점, 리뷰 추출

#### Email Service
- **SendGrid API**
  - 설문조사 이메일 발송
  - 대안: SMTP (Gmail, Outlook 등)

#### Form Service
- **Google Forms** (선택)
  - 설문조사 생성
  - 대안: Typeform, SurveyMonkey

### Data & Analytics

#### Data Processing
- **Pandas 2.0+**
  - 설문 응답 데이터 분석
  - 통계 계산

#### Visualization
- **Matplotlib 3.7+**
  - 차트 및 그래프 생성
- **Seaborn 0.12+**
  - 고급 통계 시각화

### Development Tools

#### Configuration Management
- **JSON**
  - `config/config.json`: 설정 파일
  - 환경 변수 자동 설정

#### Logging
- **Python logging module**
  - 구조화된 로깅
  - 파일 및 콘솔 출력

#### Testing
- **pytest**
  - 단위 테스트
  - 통합 테스트

---

## 🏛️ 시스템 아키텍처

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        User Interface                        │
│                     (Command Line - CLI)                     │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              AdvancedRestaurantSystem (Main)                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │           Configuration Manager                       │   │
│  │  - config.json 로딩                                   │   │
│  │  - 환경 변수 설정                                      │   │
│  │  - API 키 관리                                        │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │           Logging Manager                             │   │
│  │  - 세션 로그                                          │   │
│  │  - Task 로그 (JSON)                                   │   │
│  │  - 에이전트 통신 로그                                  │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │         Multi-Agent Orchestration (CrewAI)            │   │
│  │                                                        │   │
│  │  [Researcher] → [Curator] → [Communicator]            │   │
│  │       ↓            ↓             ↓                     │   │
│  │  [Form Creator] → [Email Sender] → [Data Analyst]     │   │
│  │                                                        │   │
│  └──────────────────────────────────────────────────────┘   │
└───────────────────────┬─────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        ↓               ↓               ↓
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  Serper API  │ │  Gemini API  │ │ SendGrid API │
│  (Search)    │ │    (LLM)     │ │   (Email)    │
└──────────────┘ └──────────────┘ └──────────────┘
        ↓               ↓               ↓
┌──────────────────────────────────────────────────┐
│              External Data Sources                │
│  - 웹 검색 결과                                    │
│  - 맛집 정보 (네이버, 구글, 망고플레이트)            │
│  - 설문 응답 데이터                                │
└──────────────────────────────────────────────────┘
```

### Component Breakdown

#### 1. User Interface Layer
- **CLI (Command Line Interface)**
  - Python 표준 입력/출력
  - 사용자 요청 입력
  - 결과 출력 및 진행 상황 표시

#### 2. Application Layer
- **AdvancedRestaurantSystem**
  - 메인 오케스트레이터
  - 워크플로우 관리
  - 에이전트 조정

#### 3. Agent Layer (6개 에이전트)
- **Researcher**: 맛집 정보 수집
- **Curator**: 맛집 선별 및 평가
- **Communicator**: 결과 포맷팅
- **Form Creator**: 설문조사 생성
- **Email Sender**: 이메일 발송
- **Data Analyst**: 데이터 분석

#### 4. Integration Layer
- **External APIs**
  - Serper API (검색)
  - Gemini API (LLM)
  - SendGrid API (이메일)

#### 5. Data Layer
- **Configuration**: JSON 파일
- **Logs**: 파일 시스템
- **Analytics**: Pandas DataFrame

---

## 🤖 에이전트 아키텍처

### 1. Researcher Agent (맛집 정보 수집 전문가)

**역할**: 사용자 조건에 맞는 맛집 정보 수집

**도구**:
- SerperDevTool: 웹 검색

**입력**:
```python
{
  "user_request": "광화문 2만원 이하 한식"
}
```

**출력**:
```python
{
  "restaurants": [
    {
      "name": "깡장집 본점",
      "address": "서울 종로구 삼봉로 82",
      "phone": "02-1234-5678",
      "rating": 4.2,
      "price_range": "9,000원 ~ 10,000원",
      "menu": "강된장, 제육볶음",
      "hours": "11:00 - 21:00"
    },
    // ... 최소 5개
  ]
}
```

**구현**:
```python
researcher = Agent(
    role='맛집 정보 수집 전문가',
    goal='사용자의 요청에 따라 맛집 정보를 수집하고 분석합니다',
    tools=[self.search_tool],
    llm=self.llm,
    verbose=True,
    max_iter=3
)
```

---

### 2. Curator Agent (맛집 큐레이터)

**역할**: 수집된 맛집 평가 및 선별

**평가 기준**:
```python
weights = {
    "rating": 0.4,        # 평점 (40%)
    "price": 0.3,         # 가격 적정성 (30%)
    "distance": 0.2,      # 거리 및 접근성 (20%)
    "review_quality": 0.1 # 리뷰 품질 (10%)
}
```

**평가 로직**:
```python
def calculate_score(restaurant, weights):
    rating_score = normalize(restaurant.rating, 0, 5)
    price_score = calculate_price_score(restaurant.price, budget)
    distance_score = calculate_distance_score(restaurant.address, location)
    review_score = analyze_review_quality(restaurant.reviews)
    
    total_score = (
        rating_score * weights["rating"] +
        price_score * weights["price"] +
        distance_score * weights["distance"] +
        review_score * weights["review_quality"]
    )
    
    return total_score
```

**출력**:
```python
{
  "top_recommendations": [
    {
      "restaurant": {...},
      "score": 8.7,
      "reason": "40년 전통의 깊은 맛을 자랑하는 강된장 전문점..."
    },
    // 상위 2-3개
  ]
}
```

---

### 3. Communicator Agent (커뮤니케이터)

**역할**: 사용자 친화적 결과 생성

**템플릿**:
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

{separator}
"""
```

**출력**: 포맷팅된 추천 결과 (마크다운 형식)

---

### 4. Form Creator Agent (설문조사 생성 전문가)

**역할**: 설문조사 자동 생성

**설문 구조**:
```yaml
survey:
  title: "회식 장소 의견 조사"
  questions:
    - id: q1
      type: single_choice
      text: "가장 마음에 드는 맛집은?"
      options: ["깡장집 본점", "오빠닭 광화문점"]
      required: true
    
    - id: q2
      type: rating_scale
      text: "추천 만족도"
      scale: 1-5
      required: true
    
    - id: q3
      type: long_text
      text: "추가 의견"
      required: false
```

**출력**:
```python
{
  "survey_link": "https://forms.gle/xxxxx",
  "survey_items": [...],
  "expires_at": "2025-10-08"
}
```

---

### 5. Email Sender Agent (이메일 발송 전문가)

**역할**: 이메일 콘텐츠 작성 및 발송

**이메일 구조**:
```python
email = {
    "subject": "[팀명] 회식 장소 추천 - 설문조사 참여 요청",
    "to": ["teamlead@company.com", ...],
    "from": "maknae@company.com",
    "body": {
        "html": render_template("email_template.html", {
            "restaurants": top_recommendations,
            "survey_link": survey_link,
            "deadline": deadline
        }),
        "text": "..." # Plain text alternative
    }
}
```

**발송 로직**:
```python
def send_email(recipients, content):
    for recipient in recipients:
        try:
            sg = sendgrid.SendGridAPIClient(api_key)
            response = sg.send(email)
            log_email_sent(recipient, response.status_code)
        except Exception as e:
            log_email_error(recipient, str(e))
```

---

### 6. Data Analyst Agent (데이터 분석 전문가)

**역할**: 설문 응답 데이터 분석 및 시각화

**분석 프로세스**:
```python
def analyze_survey_data(responses):
    # 1. 기본 통계
    stats = {
        "total_responses": len(responses),
        "response_rate": len(responses) / total_sent,
        "average_satisfaction": mean(responses["satisfaction"])
    }
    
    # 2. 선호도 분석
    preferences = count_votes(responses["favorite"])
    
    # 3. 만족도 분석
    satisfaction_by_restaurant = group_by(
        responses, "restaurant", "satisfaction"
    ).mean()
    
    # 4. 키워드 추출
    keywords = extract_keywords(responses["comments"])
    
    return {
        "stats": stats,
        "preferences": preferences,
        "satisfaction": satisfaction_by_restaurant,
        "keywords": keywords
    }
```

**시각화**:
```python
def create_visualizations(analysis):
    # 선호도 막대 그래프
    plt.bar(preferences.keys(), preferences.values())
    plt.savefig("preference_chart.png")
    
    # 만족도 비교 차트
    plt.plot(satisfaction_by_restaurant)
    plt.savefig("satisfaction_chart.png")
    
    # 리포트 생성
    generate_html_report(analysis, charts)
```

---

## 🔄 데이터 흐름

### Complete Workflow

```
[사용자 입력]
    │
    ↓
[1. 맛집 추천 단계]
    │
    ├─→ Researcher Agent
    │   ├─ Serper API 호출 (맛집 검색)
    │   └─ 맛집 정보 5-10개 수집
    │
    ├─→ Curator Agent
    │   ├─ 평가 기준 적용
    │   ├─ 점수 계산
    │   └─ 상위 2-3개 선별
    │
    └─→ Communicator Agent
        ├─ 포맷팅
        └─ 추천 결과 생성
            │
            ↓
[2. 설문조사 생성 단계]
    │
    └─→ Form Creator Agent
        ├─ 설문 항목 생성
        ├─ Google Forms 생성
        └─ 설문 링크 반환
            │
            ↓
[3. 이메일 발송 단계]
    │
    └─→ Email Sender Agent
        ├─ 이메일 콘텐츠 작성
        ├─ SendGrid API 호출
        └─ 팀원들에게 발송
            │
            ↓
[4. 응답 수집 대기]
    │
    ↓
[5. 데이터 분석 단계]
    │
    └─→ Data Analyst Agent
        ├─ 응답 데이터 수집
        ├─ 통계 분석
        ├─ 시각화 생성
        └─ 리포트 작성
            │
            ↓
[최종 결과 제시]
```

### Agent Communication Flow

```
User → AdvancedRestaurantSystem
         │
         ├─→ Crew 1: Recommendation
         │   │
         │   ├─→ Researcher (Task 1)
         │   │   │ Input: user_request
         │   │   │ Output: raw_restaurants[]
         │   │   ↓
         │   ├─→ Curator (Task 2)
         │   │   │ Input: raw_restaurants[]
         │   │   │ Output: top_recommendations[]
         │   │   ↓
         │   └─→ Communicator (Task 3)
         │       │ Input: top_recommendations[]
         │       │ Output: formatted_result
         │       ↓
         │
         ├─→ Crew 2: Survey
         │   │
         │   └─→ Form Creator (Task 4)
         │       │ Input: formatted_result
         │       │ Output: survey_link
         │       ↓
         │
         ├─→ Crew 3: Email
         │   │
         │   └─→ Email Sender (Task 5)
         │       │ Input: formatted_result, survey_link
         │       │ Output: email_sent_status
         │       ↓
         │
         └─→ Crew 4: Analysis
             │
             └─→ Data Analyst (Task 6)
                 │ Input: survey_responses
                 │ Output: analysis_report
                 ↓
         
Result → User
```

### Data Models

#### Restaurant Model
```python
@dataclass
class Restaurant:
    name: str
    address: str
    phone: str
    rating: float
    price_range: str
    menu: Optional[str]
    hours: Optional[str]
    reviews: Optional[List[str]]
    
    def to_dict(self) -> dict:
        return asdict(self)
```

#### Recommendation Model
```python
@dataclass
class Recommendation:
    restaurant: Restaurant
    score: float
    reason: str
    rank: int
    
    def to_dict(self) -> dict:
        return {
            **self.restaurant.to_dict(),
            "score": self.score,
            "reason": self.reason,
            "rank": self.rank
        }
```

#### Survey Response Model
```python
@dataclass
class SurveyResponse:
    respondent_id: str
    favorite_restaurant: str
    satisfaction_scores: Dict[str, int]  # restaurant -> score (1-5)
    price_satisfaction: int  # 1-5
    comments: Optional[str]
    timestamp: datetime
```

---

## 🔌 API 및 외부 통합

### 1. Serper API

**목적**: 웹 검색을 통한 맛집 정보 수집

**엔드포인트**: `https://google.serper.dev/search`

**인증**: API Key (헤더)

**요청 예시**:
```python
headers = {
    "X-API-KEY": os.getenv("SERPER_API_KEY"),
    "Content-Type": "application/json"
}

payload = {
    "q": "광화문 2만원 이하 한식 맛집",
    "location": "Seoul, South Korea",
    "gl": "kr",
    "hl": "ko",
    "num": 10
}

response = requests.post(
    "https://google.serper.dev/search",
    headers=headers,
    json=payload
)
```

**응답 처리**:
```python
results = response.json()
for item in results.get("organic", []):
    restaurant = {
        "name": extract_name(item["title"]),
        "address": extract_address(item["snippet"]),
        "rating": extract_rating(item["snippet"]),
        "url": item["link"]
    }
```

**Rate Limiting**: 
- 1,000 requests/month (무료 티어)
- 재시도 로직 구현

---

### 2. Gemini API

**목적**: AI 에이전트의 LLM 백엔드

**모델**: `gemini-2.0-flash`

**설정**:
```python
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.7,
    max_output_tokens=2000,
    google_api_key=os.getenv("GEMINI_API_KEY")
)
```

**CrewAI 통합**:
```python
# LiteLLM 형식
self.llm = "gemini/gemini-2.0-flash"

# Agent에 적용
agent = Agent(
    role="...",
    goal="...",
    llm=self.llm
)
```

**비용 최적화**:
- 짧은 프롬프트 사용
- 응답 길이 제한 (max_tokens)
- 캐싱 활용 (동일 요청)

---

### 3. SendGrid API

**목적**: 설문조사 이메일 발송

**엔드포인트**: `https://api.sendgrid.com/v3/mail/send`

**인증**: API Key (헤더)

**요청 예시**:
```python
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content

sg = sendgrid.SendGridAPIClient(api_key=os.getenv("SENDGRID_API_KEY"))

message = Mail(
    from_email=Email("maknae@company.com", "막내야 시스템"),
    to_emails=[
        To("teamlead@company.com"),
        To("member1@company.com")
    ],
    subject="[팀명] 회식 장소 추천",
    html_content=Content("text/html", email_html)
)

response = sg.send(message)
```

**에러 처리**:
```python
try:
    response = sg.send(message)
    if response.status_code == 202:
        logger.info(f"Email sent successfully: {recipient}")
except Exception as e:
    logger.error(f"Email failed: {recipient} - {str(e)}")
```

---

### 4. Google Forms API (선택)

**목적**: 설문조사 생성

**대안**: 수동 생성 후 링크 제공

**현재 구현**: 템플릿 기반 설문 링크 생성

```python
def create_survey_link(recommendations, timestamp):
    # 간소화된 구현: 고정 링크 또는 시뮬레이션
    date_str = timestamp.strftime("%Y%m%d")
    return f"https://forms.gle/SURVEY-{date_str}"
```

**향후 개선**: Google Forms API 완전 통합

---

## 🔒 보안 설계

### 1. API 키 관리

**원칙**: 민감 정보 코드에서 분리

**구현**:
```python
# config.json (gitignore에 추가)
{
  "api_keys": {
    "gemini_api_key": "AIzaSy...",
    "serper_api_key": "0419c07...",
    "sendgrid_api_key": "SG.2GMM..."
  }
}

# 환경 변수로 자동 설정
os.environ["GEMINI_API_KEY"] = config["api_keys"]["gemini_api_key"]
```

**보안 체크리스트**:
- ✅ `config.json`을 `.gitignore`에 추가
- ✅ 예시 파일 제공 (`config_example.json`)
- ✅ API 키 검증 로직
- ✅ 키 회전(rotation) 가능한 구조

---

### 2. 이메일 보안

**개인정보 보호**:
```python
# 이메일 주소 로그 시 마스킹
def mask_email(email):
    name, domain = email.split("@")
    return f"{name[:2]}***@{domain}"

logger.info(f"Email sent to: {mask_email(recipient)}")
```

**스팸 방지**:
- 발송 빈도 제한
- Opt-out 링크 포함 (향후)
- SPF/DKIM 설정

---

### 3. 입력 검증

**SQL Injection 방지**: (현재 DB 없음, 향후 대비)

**XSS 방지**:
```python
from html import escape

def sanitize_input(user_input):
    return escape(user_input)
```

**Rate Limiting**:
```python
from functools import wraps
import time

def rate_limit(max_calls=5, period=60):
    calls = []
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            calls[:] = [c for c in calls if c > now - period]
            
            if len(calls) >= max_calls:
                raise Exception("Rate limit exceeded")
            
            calls.append(now)
            return func(*args, **kwargs)
        return wrapper
    return decorator
```

---

### 4. 데이터 보안

**로그 데이터**:
- 개인정보 마스킹
- 로그 파일 접근 제어
- 주기적 로그 정리

**설문 응답**:
- 익명화 옵션
- 데이터 암호화 (향후)
- GDPR 준수 (향후)

---

## 📊 로깅 및 모니터링

### 로깅 아키텍처

```
┌─────────────────────────────────────────┐
│      Application Components             │
│  ┌────────────────────────────────────┐ │
│  │  AdvancedRestaurantSystem          │ │
│  │  - Agents                          │ │
│  │  - Tasks                           │ │
│  │  - Crews                           │ │
│  └────────────────┬───────────────────┘ │
└────────────────────┼─────────────────────┘
                     │
                     ↓
        ┌────────────────────────┐
        │   Logging Manager      │
        │  - Session Logger      │
        │  - Task Logger         │
        │  - Agent Comm Logger   │
        └────────┬───────────────┘
                 │
         ┌───────┼───────┐
         ↓       ↓       ↓
    ┌─────┐ ┌─────┐ ┌──────────┐
    │ .log│ │.json│ │agent_comm│
    │(텍스트)│(구조화)│  .json   │
    └─────┘ └─────┘ └──────────┘
```

### 로그 타입

#### 1. Session Log (텍스트)
**파일**: `logs/session_YYYYMMDD_HHMMSS.log`

**내용**:
- 세션 시작/종료
- 시스템 정보
- 에이전트 생성
- Task 실행
- 프롬프트/응답
- 에러 및 경고

**형식**:
```
2025-10-01 09:48:47,505 - restaurant_system - INFO - 세션 시작
2025-10-01 09:48:47,509 - restaurant_system - INFO - 에이전트 생성: researcher
2025-10-01 09:49:13,710 - restaurant_system - INFO - Task 시작: research
2025-10-01 09:49:38,392 - restaurant_system - INFO - Task 완료: 24.68초
```

#### 2. Task Log (JSON)
**파일**: `logs/tasks_YYYYMMDD_HHMMSS.json`

**내용**:
- Task별 실행 정보
- 입력/출력 데이터
- 실행 시간
- 메타데이터

**구조**:
```json
[
  {
    "task_id": "crew_restaurant_recommendation_094913",
    "task_name": "restaurant_recommendation",
    "agent_name": "crew",
    "start_time": "2025-10-01T09:49:13.710820",
    "input_data": {
      "user_request": "광화문 2만원 이하 한식"
    },
    "status": "completed",
    "interactions": [
      {
        "timestamp": "2025-10-01T09:49:13.716071",
        "type": "prompt",
        "prompt": "맛집 추천 요청...",
        "context": {...}
      },
      {
        "timestamp": "2025-10-01T09:49:38.392025",
        "type": "response",
        "response": "추천 맛집 리스트...",
        "metadata": {
          "execution_time": 24.68
        }
      }
    ],
    "end_time": "2025-10-01T09:49:38.393026",
    "execution_time": 24.68,
    "result": "..."
  }
]
```

#### 3. Agent Communication Log (JSON)
**파일**: `logs/agent_communication_YYYYMMDD_HHMMSS.json`

**내용**:
- 에이전트 간 통신
- 데이터 전달
- 통신 타입

**구조**:
```json
{
  "session_info": {
    "timestamp": "20251001_095632",
    "total_communications": 3,
    "agents_involved": ["researcher", "curator", "communicator"]
  },
  "communications": [
    {
      "timestamp": "2025-10-01 09:56:35",
      "from_agent": "researcher",
      "to_agent": "curator",
      "data_type": "맛집 정보 데이터",
      "data_summary": "광화문 지역 한식당 5개 수집 완료",
      "data_content": "깡장집 본점, 오빠닭 광화문점..."
    }
  ]
}
```

### 로깅 레벨

```python
# 개발 환경
logging.DEBUG    # 상세한 디버깅 정보

# 프로덕션 환경
logging.INFO     # 일반 정보
logging.WARNING  # 경고 (API 응답 느림 등)
logging.ERROR    # 에러 (API 실패 등)
logging.CRITICAL # 치명적 에러 (시스템 중단)
```

### 성능 모니터링

**측정 지표**:
```python
metrics = {
    "total_execution_time": 45.2,  # 전체 실행 시간
    "task_times": {
        "research": 10.5,
        "curation": 8.3,
        "communication": 2.1,
        "survey_creation": 12.4,
        "email_sending": 5.2,
        "data_analysis": 6.7
    },
    "api_calls": {
        "serper": 3,
        "gemini": 15,
        "sendgrid": 5
    },
    "api_latencies": {
        "serper_avg": 1.2,
        "gemini_avg": 2.5,
        "sendgrid_avg": 0.8
    }
}
```

**알림 임계값**:
- ⚠️ Task 실행 시간 > 30초
- ⚠️ API 호출 실패율 > 10%
- 🚨 전체 실행 시간 > 2분

---

## 🚀 배포 아키텍처

### 현재 배포 방식: Standalone Desktop Application

```
┌─────────────────────────────────────────┐
│       사용자 PC (Windows/Mac/Linux)      │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │  Python 3.11+ Runtime              │ │
│  │                                    │ │
│  │  ┌──────────────────────────────┐ │ │
│  │  │ Advanced Restaurant System   │ │ │
│  │  │  - src/                      │ │ │
│  │  │  - config/                   │ │ │
│  │  │  - logs/                     │ │ │
│  │  └──────────────────────────────┘ │ │
│  └────────────────────────────────────┘ │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │  Dependencies (venv)               │ │
│  │  - crewai                          │ │
│  │  - langchain                       │ │
│  │  - pandas, matplotlib              │ │
│  └────────────────────────────────────┘ │
└─────────────────────────────────────────┘
         │
         ↓ (Internet)
┌─────────────────────────────────────────┐
│      External Services (Cloud)          │
│  - Serper API                           │
│  - Gemini API                           │
│  - SendGrid API                         │
└─────────────────────────────────────────┘
```

### 설치 및 실행

**설치**:
```bash
# 1. 저장소 클론
git clone <repository>
cd workspace_crewai_test

# 2. 가상 환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 의존성 설치
pip install -r requirements.txt

# 4. 설정 파일 생성
cp config/config_example.json config/config.json
# config.json 편집 (API 키 입력)
```

**실행**:
```bash
# PowerShell 스크립트 (Windows)
.\scripts\run_restaurant_system.ps1

# 또는 직접 Python 실행
python src/advanced_restaurant_system.py
```

### 향후 배포 옵션

#### 1. 웹 애플리케이션 (FastAPI + React)

```
┌─────────────────────────────────────────┐
│          Frontend (React SPA)            │
│  - 브라우저에서 실행                       │
│  - 조건 입력 UI                           │
│  - 결과 표시 대시보드                      │
└─────────────────┬───────────────────────┘
                  │ (HTTP/WebSocket)
                  ↓
┌─────────────────────────────────────────┐
│       Backend (FastAPI Server)          │
│  - REST API                             │
│  - WebSocket (실시간 진행 상황)           │
│  - Agent 오케스트레이션                   │
└─────────────────┬───────────────────────┘
                  │
                  ↓
┌─────────────────────────────────────────┐
│        Database (PostgreSQL)            │
│  - 사용자 정보                           │
│  - 추천 이력                             │
│  - 설문 응답                             │
└─────────────────────────────────────────┘
```

#### 2. 클라우드 배포 (AWS/GCP)

**컴포넌트**:
- **Compute**: AWS Lambda / Cloud Functions (서버리스)
- **Storage**: S3 / Cloud Storage (로그, 리포트)
- **Database**: RDS / Cloud SQL (데이터 저장)
- **Queue**: SQS / Pub/Sub (비동기 작업)
- **Cache**: Redis (응답 캐싱)

---

## ⚡ 확장성 및 성능

### 현재 성능

**처리 용량**:
- 동시 사용자: 1명 (CLI)
- 1회 실행 시간: 약 1-2분
- 일일 실행 가능 횟수: 제한 없음 (API 제한만)

**병목 지점**:
1. **외부 API 호출**: Serper, Gemini API 응답 시간
2. **LLM 처리**: 에이전트별 프롬프트 처리
3. **순차 실행**: Sequential Process (병렬 불가능)

### 확장 전략

#### 1. 캐싱 전략

```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=100)
def search_restaurants(location, price, cuisine):
    """동일 조건 검색 시 캐시된 결과 반환"""
    cache_key = hashlib.md5(
        f"{location}_{price}_{cuisine}".encode()
    ).hexdigest()
    
    # 캐시 확인
    if cached := get_from_cache(cache_key):
        return cached
    
    # API 호출
    result = serper_api.search(...)
    
    # 캐시 저장 (1시간)
    save_to_cache(cache_key, result, ttl=3600)
    
    return result
```

#### 2. 비동기 처리

```python
import asyncio

async def parallel_agent_execution():
    """독립적인 작업 병렬 실행"""
    tasks = [
        asyncio.create_task(researcher.execute()),
        asyncio.create_task(form_creator.prepare()),
    ]
    results = await asyncio.gather(*tasks)
    return results
```

#### 3. 데이터베이스 도입

**목적**:
- 추천 이력 저장
- 사용자 선호도 학습
- 설문 응답 저장

**스키마**:
```sql
-- 추천 이력
CREATE TABLE recommendations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    search_query TEXT,
    location VARCHAR(100),
    price_range VARCHAR(50),
    results JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 설문 응답
CREATE TABLE survey_responses (
    id SERIAL PRIMARY KEY,
    recommendation_id INTEGER REFERENCES recommendations(id),
    respondent_email VARCHAR(255),
    favorite_restaurant VARCHAR(255),
    satisfaction_scores JSONB,
    comments TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 인덱스
CREATE INDEX idx_recommendations_user ON recommendations(user_id);
CREATE INDEX idx_recommendations_created ON recommendations(created_at);
```

#### 4. Rate Limiting

```python
class APIRateLimiter:
    def __init__(self, max_calls_per_minute=10):
        self.max_calls = max_calls_per_minute
        self.calls = []
    
    def wait_if_needed(self):
        now = time.time()
        # 1분 이내 호출만 유지
        self.calls = [c for c in self.calls if c > now - 60]
        
        if len(self.calls) >= self.max_calls:
            sleep_time = 60 - (now - self.calls[0])
            time.sleep(sleep_time)
        
        self.calls.append(time.time())

# 사용
rate_limiter = APIRateLimiter(max_calls_per_minute=10)

def call_api():
    rate_limiter.wait_if_needed()
    return api.request()
```

### 모니터링 및 알림

```python
class PerformanceMonitor:
    def __init__(self):
        self.metrics = {
            "api_calls": defaultdict(int),
            "execution_times": defaultdict(list),
            "errors": defaultdict(int)
        }
    
    def record_api_call(self, api_name, duration):
        self.metrics["api_calls"][api_name] += 1
        self.metrics["execution_times"][api_name].append(duration)
    
    def record_error(self, component, error):
        self.metrics["errors"][component] += 1
        
        # 임계값 초과 시 알림
        if self.metrics["errors"][component] > 5:
            send_alert(f"High error rate in {component}")
    
    def get_summary(self):
        return {
            "total_api_calls": sum(self.metrics["api_calls"].values()),
            "avg_execution_times": {
                api: statistics.mean(times)
                for api, times in self.metrics["execution_times"].items()
            },
            "error_counts": dict(self.metrics["errors"])
        }
```

---

## 🔮 향후 개선 사항

### Phase 1: 사용자 경험 개선 (1-2개월)

**1.1 웹 UI 개발**
- React 기반 SPA
- 실시간 진행 상황 표시
- 지도 기반 맛집 표시

**1.2 모바일 앱**
- React Native
- 푸시 알림 (설문 참여 독려)
- 오프라인 모드

**1.3 음성 인터페이스**
- 음성 입력 (예: "광화문에서 2만원 이하 한식")
- 음성 출력 (추천 결과 읽어주기)

### Phase 2: 기능 확장 (3-4개월)

**2.1 실시간 예약 통합**
- 네이버 예약, 카카오 예약 API
- 자동 예약 기능

**2.2 팀 관리 기능**
- 팀원 정보 저장
- 식성/알레르기 정보 관리
- 과거 회식 이력 조회

**2.3 고급 분석**
- 팀 선호도 학습
- 예산 최적화 알고리즘
- 계절별 추천

### Phase 3: 엔터프라이즈 기능 (5-6개월)

**3.1 멀티 테넌시**
- 여러 조직 지원
- 조직별 설정 분리
- 권한 관리

**3.2 통합**
- Slack/Teams 봇
- 사내 시스템 연동
- SSO (Single Sign-On)

**3.3 고급 보고**
- 팀 회식 통계 대시보드
- 예산 트렌드 분석
- 만족도 추이

### Phase 4: AI 고도화 (장기)

**4.1 개인화 추천**
- 사용자별 선호도 학습
- 협업 필터링
- 하이브리드 추천

**4.2 대화형 AI**
- 자연어 대화로 조건 정제
- 맥락 이해 (예: "저번보다 저렴한 곳")
- 추천 이유 설명

**4.3 예측 분석**
- 팀원 만족도 예측
- 최적 예산 제안
- 혼잡도 예측

---

## 📚 기술 부채 및 개선 과제

### 현재 제한사항

1. **동기 실행**: 모든 에이전트가 순차 실행
   - **개선**: 독립적 작업 병렬화

2. **캐싱 없음**: 동일 조건 재검색
   - **개선**: Redis 캐시 도입

3. **오류 복구 제한적**: 부분 실패 시 전체 중단
   - **개선**: Circuit Breaker 패턴

4. **테스트 부족**: 단위 테스트 미흡
   - **개선**: 테스트 커버리지 80% 이상

5. **문서화 부족**: API 문서 없음
   - **개선**: OpenAPI 스펙 작성

### 리팩토링 계획

```python
# Before: 단일 파일
advanced_restaurant_system.py (1000+ lines)

# After: 모듈화
src/
├── core/
│   ├── agents/
│   │   ├── researcher.py
│   │   ├── curator.py
│   │   └── communicator.py
│   ├── workflows/
│   │   ├── recommendation.py
│   │   └── survey.py
│   └── orchestrator.py
├── services/
│   ├── search_service.py
│   ├── email_service.py
│   └── survey_service.py
├── models/
│   ├── restaurant.py
│   └── survey.py
└── utils/
    ├── config.py
    └── logging.py
```

---

## 📖 참고 문서

- [사용자 요구사항](./USER_REQUIREMENTS.md)
- [사용자 스토리](./USER_STORIES.md)
- [빠른 시작 가이드](../guides/QUICK_START.md)
- [설정 가이드](../guides/SETUP_GUIDE.md)

---

## 🤝 기여자

**Architect**: Winston  
**Product Owner**: Sarah  
**Development Team**: TBD

---

**문서 히스토리**:
- 2025-10-01: 초안 작성 (v1.0) - Winston

---

**Note**: 이 문서는 "막내야. 회식 장소 알아봤니?" 시스템의 기술 아키텍처를 정의합니다. 
실제 구현과 설계가 일치하지 않을 경우 이 문서를 업데이트하세요.

