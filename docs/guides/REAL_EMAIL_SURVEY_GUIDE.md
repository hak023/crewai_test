# 실제 설문조사 및 이메일 발송 설정 가이드

## 📋 목차
1. [Google Forms API 설정](#google-forms-api-설정)
2. [이메일 SMTP 설정](#이메일-smtp-설정)
3. [테스트 실행](#테스트-실행)

---

## 🔧 Google Forms API 설정

### 1. Google Cloud Console 설정

1. **Google Cloud Console 접속**
   - https://console.cloud.google.com/ 에 접속합니다.

2. **새 프로젝트 생성**
   - 좌측 상단의 프로젝트 선택 > "새 프로젝트" 클릭
   - 프로젝트 이름: `restaurant-survey-system`

3. **Google Forms API 활성화**
   ```
   APIs & Services > Library > "Google Forms API" 검색 > 활성화
   ```

4. **서비스 계정 생성**
   ```
   APIs & Services > Credentials > Create Credentials > Service Account
   ```
   - 서비스 계정 이름: `restaurant-forms-service`
   - 역할: `Editor` 또는 `Owner`

5. **서비스 계정 키 생성**
   - 생성된 서비스 계정 클릭
   - Keys 탭 > Add Key > Create New Key
   - JSON 형식 선택 > 다운로드

6. **키 파일 저장**
   ```bash
   # 다운로드한 JSON 파일을 다음 경로로 복사
   cp ~/Downloads/restaurant-survey-system-*.json config/google_credentials.json
   ```

### 2. config.json 업데이트

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

