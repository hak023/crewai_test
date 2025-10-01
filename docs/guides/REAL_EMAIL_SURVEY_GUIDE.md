# 실제 설문조사 및 이메일 발송 설정 가이드

## 📋 목차
1. [Google Forms API 설정](#google-forms-api-설정)
2. [이메일 SMTP 설정](#이메일-smtp-설정)
3. [테스트 실행](#테스트-실행)

---

## 🔧 Google Forms API 설정

### ⚠️ 중요: Service Account vs OAuth 2.0 클라이언트 ID

현재 `config/google_credentials.json`이 **Service Account**인 경우, OAuth 2.0에는 사용할 수 없습니다.

**확인 방법:**
```bash
# google_credentials.json 파일을 열어서 확인
# "type": "service_account" 라면 → 변경 필요 ❌
# "installed" 또는 "web" 키가 있다면 → 정상 ✅
```

---

### 1. Google Cloud Console에서 OAuth 2.0 클라이언트 ID 생성

#### 1-1. Google Cloud Console 접속
https://console.cloud.google.com/apis/credentials

#### 1-2. 프로젝트 선택
- 기존 프로젝트가 있다면 선택
- 없다면 "새 프로젝트" 생성 (`restaurant-survey-system`)

#### 1-3. Google Forms API 활성화
```
좌측 메뉴: APIs & Services > Library
검색: "Google Forms API"
→ "사용 설정" 클릭
```

#### 1-4. OAuth 동의 화면 구성 (최초 1회)
```
APIs & Services > OAuth consent screen
1. User Type: External 선택 → 만들기
2. 앱 정보:
   - 앱 이름: Restaurant Survey System
   - 사용자 지원 이메일: (본인 이메일)
   - 개발자 연락처 정보: (본인 이메일)
3. 범위(Scopes): 기본값 그대로 (나중에 런타임에서 요청됨)
4. 테스트 사용자: (선택사항) 본인 이메일 추가
5. 저장 후 계속
```

#### 1-5. OAuth 2.0 클라이언트 ID 생성 ⭐ 핵심
```
APIs & Services > Credentials > + CREATE CREDENTIALS > OAuth client ID

⚠️ 매우 중요: 애플리케이션 유형 선택
┌─────────────────────────────────────┐
│ Application type:                   │
│ ○ Web application                   │
│ ● Desktop app          ← 이것 선택! │
│ ○ Android                           │
│ ○ Chrome app                        │
│ ○ iOS                               │
│ ○ Universal Windows Platform (UWP) │
└─────────────────────────────────────┘

이름: Restaurant System Desktop Client
→ "만들기" 클릭
```

#### 1-6. 클라이언트 시크릿 다운로드
```
✅ "OAuth 클라이언트가 생성되었습니다" 팝업이 나타남
→ "JSON 다운로드" 클릭
→ client_secret_XXXXX.apps.googleusercontent.com.json 파일 저장
```

#### 1-7. 다운로드한 파일을 프로젝트로 복사

**Windows (PowerShell):**
```powershell
# 기존 Service Account 파일 백업 (선택사항)
Move-Item config\google_credentials.json config\google_credentials_service_account.json

# 새로 다운로드한 OAuth 클라이언트 ID 파일 복사
Copy-Item "$env:USERPROFILE\Downloads\client_secret_*.json" config\google_credentials.json
```

**Linux/Mac:**
```bash
# 기존 Service Account 파일 백업 (선택사항)
mv config/google_credentials.json config/google_credentials_service_account.json

# 새로 다운로드한 OAuth 클라이언트 ID 파일 복사
cp ~/Downloads/client_secret_*.json config/google_credentials.json
```

---

### 2. 미리 토큰 생성하기 (추천 ⭐)

OAuth 2.0 인증은 첫 실행 시 웹 브라우저를 통해 Google 로그인이 필요합니다.
**미리 토큰을 생성해두면** main 시스템 실행 시 자동으로 인증됩니다.

#### 2-1. 토큰 생성 스크립트 실행

```powershell
# 테스트 스크립트 실행
python test_google_forms_oauth.py
```

#### 2-2. 웹 브라우저에서 인증

스크립트 실행 시 자동으로 웹 브라우저가 열립니다:

```
1. Google 계정 선택 및 로그인
2. "이 앱은 Google에서 확인하지 않았습니다" 경고 화면이 나타날 수 있음
   → "고급" 클릭
   → "Restaurant System(안전하지 않음)으로 이동" 클릭
3. 권한 요청 화면:
   "Google Forms를 보고, 수정하고, 만들고, 삭제"
   → "허용" 클릭
4. 인증 완료 메시지 확인
```

#### 2-3. 토큰 생성 확인

```powershell
# token.json 파일이 생성되었는지 확인
dir config\token.json
```

**성공 시 출력:**
```
✅ OAuth 2.0 인증 완료!
✅ 인증 정보 저장 완료: config\token.json
   (다음부터는 이 파일을 사용하여 자동 인증됩니다)
```

---

### 3. OAuth 2.0 인증 동작 방식

#### 첫 실행 (token.json 없음):
```
1. 웹 브라우저 자동 실행
2. Google 로그인
3. 권한 승인
4. token.json 자동 생성 ✅
```

#### 이후 실행 (token.json 있음):
```
1. token.json에서 자동 인증 ✅
2. 브라우저 열리지 않음
3. 바로 Forms API 사용 가능
```

#### 토큰 만료 시:
```
1. refresh_token으로 자동 갱신 ✅
2. 갱신된 토큰을 token.json에 저장
3. 사용자 개입 불필요
```

---

### 5. config.json 업데이트

`config/config.json` 파일에 Google credentials 경로를 추가합니다:

```json
{
  "system_settings": {
    "llm_provider": "gemini",
    "llm_model": "gemini-2.0-flash",
    "google_credentials_path": "config/google_credentials.json"
  },
  ...
}
```

---

## 📧 이메일 SMTP 설정

### 1. Gmail SMTP 사용 (추천)

#### Gmail 앱 비밀번호 생성

1. **Google 계정 관리** 접속
   - https://myaccount.google.com/

2. **2단계 인증 활성화** (필수)
   - 보안 > 2단계 인증 > 시작하기

3. **앱 비밀번호 생성**
   - 보안 > 앱 비밀번호
   - 앱 선택: `메일`
   - 기기 선택: `기타` (맛집 추천 시스템)
   - 생성된 16자리 비밀번호 복사

### 2. config.json 업데이트

`config/config.json` 파일에 이메일 설정을 추가합니다:

```json
{
  "email_settings": {
    "sender_email": "your-email@gmail.com",
    "sender_password": "앱 비밀번호 16자리",
    "sender_name": "맛집 추천 시스템",
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587
  }
}
```

### 3. 전체 config.json 예시

```json
{
  "api_keys": {
    "google_api_key": "your-gemini-api-key",
    "serper_api_key": "your-serper-api-key"
  },
  "system_settings": {
    "llm_provider": "gemini",
    "llm_model": "gemini-2.0-flash",
    "temperature": 0.7,
    "google_credentials_path": "config/google_credentials.json"
  },
  "email_settings": {
    "sender_email": "your-email@gmail.com",
    "sender_password": "your-app-password",
    "sender_name": "맛집 추천 시스템",
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587
  },
  "agents_config": {
    "researcher": {
      "max_iterations": 3,
      "timeout": 60
    }
  }
}
```

---

## 🧪 테스트 실행

### 1. 패키지 설치

```bash
pip install -r requirements.txt
```

### 2. 시스템 실행

```powershell
.\scripts\run_simple.ps1
```

또는

```bash
python src/advanced_restaurant_system.py
```

### 3. 실행 과정

1. **맛집 추천**: AI 에이전트가 맛집을 검색하고 추천합니다.

2. **설문조사 생성**:
   - Google Forms API를 사용하여 **실제 설문조사**가 생성됩니다.
   - 생성 실패 시 시뮬레이션 모드로 전환됩니다.

3. **이메일 발송 확인**:
   ```
   ================================================================================
   📧 이메일 발송 확인
      수신자: recipient@example.com
      제목: [맛집 추천] 설문조사 참여 부탁드립니다
      설문조사 링크: https://docs.google.com/forms/...
   ================================================================================
   
   이메일을 발송하시겠습니까? (y/n): 
   ```
   
4. **이메일 발송**:
   - `y` 입력: 실제 이메일이 발송됩니다.
   - `n` 입력: 이메일 발송이 취소됩니다.

---

## ⚠️ 주의사항

### Google Forms API

1. **서비스 계정 권한**
   - 생성된 Google Form은 서비스 계정이 소유합니다.
   - 본인 계정에서 보려면 서비스 계정 이메일을 Google Form에 공유해야 합니다.

2. **API 할당량**
   - Google Forms API는 무료로 사용 가능하지만 할당량이 있습니다.
   - 프로젝트당 하루 1,000개 폼 생성 제한

### 이메일 발송

1. **Gmail 보안**
   - 반드시 **앱 비밀번호**를 사용하세요 (실제 Gmail 비밀번호 X)
   - 2단계 인증이 필수입니다.

2. **발송 제한**
   - Gmail은 하루 500개 이메일 발송 제한이 있습니다.
   - 대량 발송 시 Gmail 비즈니스 계정을 사용하세요.

3. **스팸 방지**
   - 발송 빈도가 너무 높으면 스팸으로 분류될 수 있습니다.
   - 적절한 간격을 두고 발송하세요.

---

## 🔍 문제 해결

### Google Forms API 오류

**문제**: `google_credentials.json` 파일을 찾을 수 없습니다.

**해결**:
```bash
# 파일 경로 확인
ls config/google_credentials.json

# 없다면 다시 다운로드하여 저장
```

**문제**: `HttpError 403: Permission denied`

**해결**:
- Google Cloud Console에서 Google Forms API가 활성화되었는지 확인
- 서비스 계정 권한이 `Editor` 이상인지 확인

### 이메일 발송 오류

**문제**: `SMTPAuthenticationError`

**해결**:
1. Gmail 앱 비밀번호를 정확히 입력했는지 확인 (공백 없이)
2. 2단계 인증이 활성화되었는지 확인
3. `config.json`의 이메일 주소가 정확한지 확인

**문제**: 이메일이 스팸함에 들어갑니다.

**해결**:
- 첫 발송 시 수신자가 "스팸 아님"으로 표시
- 발송 빈도를 낮춤
- SPF, DKIM 레코드 설정 (고급)

---

## 📚 참고 자료

- [Google Forms API 문서](https://developers.google.com/forms/api)
- [Gmail SMTP 설정](https://support.google.com/mail/answer/7126229)
- [Python smtplib 문서](https://docs.python.org/3/library/smtplib.html)

---

## ✅ 완료!

이제 시스템이 실제로:
- ✅ Google Forms를 생성하고
- ✅ 사용자 확인을 받아
- ✅ 실제 이메일을 발송합니다!

**즐거운 코딩 되세요!** 🚀

