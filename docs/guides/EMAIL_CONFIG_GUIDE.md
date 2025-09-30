# 📧 이메일 수신자 설정 가이드

## 📋 개요

`advanced_restaurant_system.py`는 설문조사 이메일 발송 시 수신자 목록을 `config.json`에서 읽어옵니다.

## ⚙️ 설정 방법

### 1. config.json 편집

`config.json` 파일의 `email_settings` 섹션에서 `recipients` 배열을 수정합니다:

```json
{
  "email_settings": {
    "sender_name": "맛집 추천 시스템",
    "sender_email": "noreply@restaurant-system.com",
    "subject_template": "[맛집 추천] 설문조사 참여 요청",
    "email_template": "templates/email_template.html",
    "recipients": [
      "user1@example.com",
      "user2@example.com",
      "user3@example.com"
    ]
  }
}
```

### 2. 수신자 추가/제거

**수신자 추가:**
```json
"recipients": [
  "user1@example.com",
  "user2@example.com",
  "user3@example.com",
  "new.user@example.com"  // 새로운 수신자 추가
]
```

**수신자 제거:**
원하지 않는 이메일 주소를 삭제하거나 주석 처리합니다.

## ✅ 설정 검증

설정이 올바른지 확인하려면:

```python
from config_manager import load_config

config = load_config()
email_settings = config.get_email_settings()
recipients = email_settings.get("recipients", [])

print(f"수신자 {len(recipients)}명:")
for recipient in recipients:
    print(f"  - {recipient}")
```

## ⚠️ 주의사항

1. **유효한 이메일 주소 사용**
   - 올바른 이메일 형식 사용 (예: `user@domain.com`)
   - 공백이나 특수문자 주의

2. **개인정보 보호**
   - 실제 운영 시 수신자 이메일 주소 보안 관리
   - config.json을 버전 관리에 포함하지 않도록 주의

3. **발송 제한**
   - SendGrid API 제한 확인
   - 대량 발송 시 적절한 딜레이 추가 고려

## 🔧 고급 설정

### 동적 수신자 목록

코드에서 동적으로 수신자를 추가하려면:

```python
# config에서 기본 수신자 읽기
config = load_config()
email_settings = config.get_email_settings()
base_recipients = email_settings.get("recipients", [])

# 추가 수신자 병합
additional_recipients = ["extra@example.com"]
all_recipients = base_recipients + additional_recipients

# 워크플로우 실행
system.run_complete_workflow(user_request, all_recipients)
```

### 환경별 설정

개발/운영 환경별로 다른 수신자 사용:

**config.dev.json** (개발):
```json
"recipients": ["dev@example.com"]
```

**config.prod.json** (운영):
```json
"recipients": ["real.user1@company.com", "real.user2@company.com"]
```

실행 시:
```bash
# 개발 환경
python advanced_restaurant_system.py --config config.dev.json

# 운영 환경
python advanced_restaurant_system.py --config config.prod.json
```

## 📊 발송 통계 확인

로그 파일에서 이메일 발송 내역을 확인할 수 있습니다:

```bash
# 세션 로그에서 이메일 발송 확인
cat logs/session_YYYYMMDD_HHMMSS.log | grep "이메일 발송"
```

## 💡 예시

### 소규모 테스트
```json
"recipients": ["test@example.com"]
```

### 팀 내부 배포
```json
"recipients": [
  "team.lead@company.com",
  "member1@company.com",
  "member2@company.com"
]
```

### 고객 대상 배포
```json
"recipients": [
  "customer1@company.com",
  "customer2@company.com",
  "customer3@company.com",
  // ... 더 많은 고객
]
```

## 🔗 관련 문서

- [로깅 가이드](LOGGING_GUIDE.md) - 이메일 발송 로그 확인
- [설정 파일 예시](config_example.json) - 전체 설정 구조 참고
