# Gmail SMTP 이메일 발송 설정 가이드

## 📋 목차
1. [Gmail 앱 비밀번호 생성](#gmail-앱-비밀번호-생성)
2. [config.json 설정](#configjson-설정)
3. [테스트 이메일 발송](#테스트-이메일-발송)
4. [문제 해결](#문제-해결)

---

## 🔐 Gmail 앱 비밀번호 생성

### ⚠️ 중요사항
- **일반 Gmail 비밀번호를 사용하면 인증 실패합니다!**
- 반드시 **앱 비밀번호**를 생성해서 사용해야 합니다.
- 앱 비밀번호는 16자리 문자로 구성됩니다.

---

### 1단계: 2단계 인증 활성화

#### 1-1. Google 계정 설정 접속
```
https://myaccount.google.com/security
```

#### 1-2. "2단계 인증" 찾기
- 페이지에서 "2단계 인증" 섹션을 찾습니다
- "2단계 인증"이 **"사용 안함"** 상태라면 클릭하여 활성화합니다

#### 1-3. 2단계 인증 설정
```
1. "시작하기" 클릭
2. 비밀번호 입력하여 본인 확인
3. 전화번호 입력 (SMS 또는 음성 통화 선택)
4. 인증 코드 입력
5. "사용 설정" 클릭
```

✅ 2단계 인증이 활성화되면 **"사용"** 상태로 변경됩니다.

---

### 2단계: 앱 비밀번호 생성

#### 2-1. 앱 비밀번호 페이지 접속
```
https://myaccount.google.com/apppasswords
```

또는:
```
Google 계정 설정 > 보안 > 2단계 인증 > 앱 비밀번호
```

#### 2-2. 앱 비밀번호 생성

1. **앱 선택**
   ```
   드롭다운: "기타(맞춤 이름)"
   이름 입력: "Restaurant Survey System"
   ```

2. **"생성" 클릭**

3. **16자리 비밀번호 표시**
   ```
   예시: abcd efgh ijkl mnop
   ```

4. **⚠️ 중요: 이 비밀번호를 복사하세요!**
   - 이 비밀번호는 **다시 표시되지 않습니다**
   - 공백을 포함하거나 제거하고 사용 가능
   - `abcdefghijklmnop` 또는 `abcd efgh ijkl mnop` 둘 다 가능

---

## ⚙️ config.json 설정

### 파일 위치
```
config/config.json
```

### 설정 내용

```json
{
  "email_settings": {
    "sender_name": "맛집 추천 시스템",
    "sender_email": "your_email@gmail.com",           ← Gmail 주소
    "sender_password": "abcdefghijklmnop",            ← 앱 비밀번호 (16자리)
    "smtp_server": "smtp.gmail.com",                  ← Gmail SMTP 서버
    "smtp_port": 587,                                 ← SMTP 포트 (TLS)
    "subject_template": "[맛집 추천] 설문조사 참여 요청",
    "email_template": "templates/email_template.html",
    "recipients": [
      "user1@example.com",                            ← 수신자 목록
      "user2@example.com"
    ]
  }
}
```

### 설정 값 설명

| 필드 | 설명 | 예시 |
|------|------|------|
| `sender_email` | 발신자 Gmail 주소 | `your_email@gmail.com` |
| `sender_password` | **앱 비밀번호** (16자리) | `abcdefghijklmnop` |
| `smtp_server` | SMTP 서버 주소 | `smtp.gmail.com` |
| `smtp_port` | SMTP 포트 번호 | `587` (TLS) 또는 `465` (SSL) |
| `sender_name` | 발신자 표시 이름 | `맛집 추천 시스템` |
| `recipients` | 수신자 이메일 목록 | `["user1@example.com"]` |

---

## 🧪 테스트 이메일 발송

### 방법 1: Main 시스템 실행

```powershell
python src/advanced_restaurant_system.py
```

프로그램 실행 중 이메일 발송 확인 프롬프트가 나타나면:
```
이메일을 발송하시겠습니까? (y/n): y
```

### 방법 2: 테스트 스크립트 (추후 추가 예정)

```python
from src.advanced_restaurant_system import AdvancedRestaurantSystem

system = AdvancedRestaurantSystem()
system._send_email_smtp(
    recipient="test@example.com",
    subject="테스트 이메일",
    body="테스트 메시지입니다.",
    survey_link="https://forms.gle/test"
)
```

---

## 🔧 문제 해결

### ❌ 오류 1: "SMTP 인증 실패"

**오류 메시지:**
```
SMTPAuthenticationError: (535, b'5.7.8 Username and Password not accepted')
```

**원인:**
- 일반 Gmail 비밀번호를 사용했습니다
- 2단계 인증이 활성화되지 않았습니다
- 앱 비밀번호가 잘못 입력되었습니다

**해결:**
1. 2단계 인증 활성화 확인
2. 앱 비밀번호 재생성
3. config.json에 앱 비밀번호 정확히 입력 (공백 제거)

---

### ❌ 오류 2: "SMTP 설정이 없습니다"

**로그 메시지:**
```
⚠️  SMTP 설정이 없습니다.
⚠️  config.json의 email_settings에 다음 정보를 입력하세요
```

**원인:**
- `sender_email` 또는 `sender_password`가 비어있습니다

**해결:**
```json
"email_settings": {
  "sender_email": "your_email@gmail.com",     ← 입력 필요
  "sender_password": "abcdefghijklmnop"       ← 입력 필요
}
```

---

### ❌ 오류 3: "Connection timed out"

**오류 메시지:**
```
TimeoutError: [Errno 110] Connection timed out
```

**원인:**
- 방화벽이 SMTP 포트(587 또는 465)를 차단하고 있습니다
- 네트워크 연결 문제

**해결:**
1. 방화벽 설정 확인
2. 포트 587 (TLS) 또는 465 (SSL) 허용
3. 네트워크 연결 확인

---

### ❌ 오류 4: "Sender address rejected"

**오류 메시지:**
```
SMTPSenderRefused: (553, b'5.1.2 Invalid sender address')
```

**원인:**
- `sender_email`이 잘못된 형식입니다
- 존재하지 않는 이메일 주소입니다

**해결:**
- 올바른 Gmail 주소 입력 확인
- 형식: `username@gmail.com`

---

### ❌ 오류 5: "Daily sending quota exceeded"

**오류 메시지:**
```
SMTPDataError: (552, b'5.2.3 Your message exceeded Google's message size limits')
```

**원인:**
- Gmail 일일 발송 한도 초과
- 무료 Gmail: 하루 500통
- Google Workspace: 하루 2,000통

**해결:**
1. 발송량 줄이기
2. 여러 Gmail 계정 사용
3. Google Workspace 사용 고려

---

## 📊 Gmail SMTP 제한사항

| 항목 | 무료 Gmail | Google Workspace |
|------|------------|------------------|
| **일일 발송 한도** | 500통 | 2,000통 |
| **수신자 수/이메일** | 500명 | 2,000명 |
| **첨부파일 크기** | 25MB | 25MB |
| **발송 속도** | 제한 있음 | 제한 있음 |

---

## 💡 보안 권장사항

### ✅ 권장
- 앱 비밀번호 사용
- 2단계 인증 활성화
- `config.json`을 `.gitignore`에 포함 (이미 설정됨)
- 비밀번호 주기적 변경

### ❌ 비권장
- 일반 Gmail 비밀번호 사용
- 비밀번호를 코드에 하드코딩
- 비밀번호를 Git에 커밋
- 공개 저장소에 `config.json` 업로드

---

## 🔄 다른 이메일 서비스 사용

### Outlook/Hotmail

```json
{
  "smtp_server": "smtp-mail.outlook.com",
  "smtp_port": 587
}
```

### Naver

```json
{
  "smtp_server": "smtp.naver.com",
  "smtp_port": 587
}
```

### Daum

```json
{
  "smtp_server": "smtp.daum.net",
  "smtp_port": 465
}
```

**참고:** 각 서비스마다 별도의 앱 비밀번호 설정이 필요할 수 있습니다.

---

## 📚 추가 참고 자료

- **Gmail 앱 비밀번호:** https://support.google.com/accounts/answer/185833
- **Gmail SMTP 설정:** https://support.google.com/a/answer/176600
- **2단계 인증:** https://support.google.com/accounts/answer/185839
- **Python smtplib 문서:** https://docs.python.org/3/library/smtplib.html

---

## 🎯 빠른 체크리스트

설정 완료 전 확인사항:

- [ ] 2단계 인증 활성화 완료
- [ ] 앱 비밀번호 생성 완료 (16자리)
- [ ] config.json에 sender_email 입력
- [ ] config.json에 sender_password (앱 비밀번호) 입력
- [ ] config.json에 recipients 목록 입력
- [ ] 테스트 이메일 발송 성공

**모두 체크되었다면 실제 이메일 발송 준비 완료!** ✅

