# OAuth 2.0 인증 문제 해결 가이드

## ❌ 일반적인 오류 및 해결 방법

### 1. "Client secrets must be for a web or installed app"

**원인:**
- `config/google_credentials.json`이 Service Account 자격증명입니다
- OAuth 2.0에는 "Desktop app" 또는 "Web application" 클라이언트 ID가 필요합니다

**해결:**
```powershell
# 1. 현재 파일 확인
type config\google_credentials.json

# "type": "service_account" 가 보이면 변경 필요
```

**단계별 해결:**

1. **Google Cloud Console 접속**
   - https://console.cloud.google.com/apis/credentials

2. **OAuth 2.0 클라이언트 ID 생성**
   - `+ CREATE CREDENTIALS` > `OAuth client ID`
   - Application type: **Desktop app** ⚠️ 중요!
   - 이름: `Restaurant System Desktop Client`

3. **JSON 다운로드**
   - 생성 후 다운로드 버튼 클릭
   - `client_secret_XXX.json` 파일 저장

4. **파일 교체**
   ```powershell
   # 기존 파일 백업
   Move-Item config\google_credentials.json config\google_credentials_service_account.json
   
   # 새 파일 복사
   Copy-Item "$env:USERPROFILE\Downloads\client_secret_*.json" config\google_credentials.json
   ```

5. **토큰 생성**
   ```powershell
   python test_google_forms_oauth.py
   ```

---

### 2. "This app isn't verified" (앱이 확인되지 않음)

**원인:**
- Google에서 아직 앱을 검토하지 않았습니다
- 개발 중인 앱이므로 정상입니다

**해결:**
1. "고급" 클릭
2. "Restaurant System(안전하지 않음)으로 이동" 클릭
3. 권한 승인

**설명:** 
- 본인이 만든 앱이므로 안전합니다
- 프로덕션 배포 시에만 Google 검토가 필요합니다

---

### 3. "Access blocked: This app's request is invalid"

**원인:**
- OAuth 동의 화면이 구성되지 않았습니다

**해결:**
```
Google Cloud Console > APIs & Services > OAuth consent screen
1. User Type: External 선택
2. 앱 정보 입력:
   - 앱 이름: Restaurant Survey System
   - 사용자 지원 이메일: (본인 이메일)
   - 개발자 연락처: (본인 이메일)
3. 저장 후 계속
4. Scopes: 기본값 유지 (건너뛰기 가능)
5. 테스트 사용자: (선택사항) 본인 이메일 추가
```

---

### 4. "The project does not have Forms API enabled"

**원인:**
- Google Forms API가 활성화되지 않았습니다

**해결:**
```
Google Cloud Console > APIs & Services > Library
→ "Google Forms API" 검색
→ "사용 설정" 클릭
```

---

### 5. Token refresh 실패

**원인:**
- `token.json`이 손상되었거나 만료되었습니다

**해결:**
```powershell
# token.json 삭제 후 재생성
Remove-Item config\token.json
python test_google_forms_oauth.py
```

---

### 6. "Redirect URI mismatch"

**원인:**
- Redirect URI가 설정되지 않았거나 일치하지 않습니다
- Desktop app에서는 자동으로 `http://localhost` 사용

**해결:**
1. Google Cloud Console > Credentials > OAuth 2.0 클라이언트 ID 편집
2. "승인된 리디렉션 URI"에 다음 추가:
   ```
   http://localhost
   http://localhost:8080
   http://localhost:8000
   ```
3. 저장

---

## ✅ 정상 작동 확인 방법

### 1. OAuth 2.0 클라이언트 ID 파일 확인

**올바른 형식:**
```json
{
  "installed": {
    "client_id": "XXX.apps.googleusercontent.com",
    "project_id": "your-project-id",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_secret": "XXX",
    "redirect_uris": ["http://localhost", "urn:ietf:wg:oauth:2.0:oob"]
  }
}
```

**또는 (Web application):**
```json
{
  "web": {
    "client_id": "XXX.apps.googleusercontent.com",
    ...
  }
}
```

**잘못된 형식 (Service Account):**
```json
{
  "type": "service_account",   ← 이것이 보이면 안됨!
  "project_id": "...",
  ...
}
```

---

### 2. 토큰 생성 테스트

```powershell
# 테스트 스크립트 실행
python test_google_forms_oauth.py
```

**성공 시 출력:**
```
✅ OAuth 2.0 인증 완료!
✅ 인증 정보 저장 완료: config\token.json
✅ 테스트 설문조사 생성 성공!
🔗 설문조사 링크: https://docs.google.com/forms/d/XXX/viewform
```

---

### 3. Main 시스템 테스트

```powershell
python src/advanced_restaurant_system.py
```

**성공 시 로그:**
```
✅ 기존 token.json에서 인증 정보 로드
✅ Google Form 생성 완료
📋 Form ID: XXX
🔗 응답 링크: https://docs.google.com/forms/d/XXX/viewform
```

---

## 🔄 완전한 재설정 방법

모든 설정을 처음부터 다시 하려면:

```powershell
# 1. 기존 파일 백업
Move-Item config\google_credentials.json config\google_credentials_backup.json
Remove-Item config\token.json

# 2. Google Cloud Console에서 새 OAuth 클라이언트 ID 생성
#    (위의 "1. Client secrets must be for a web or installed app" 섹션 참조)

# 3. 다운로드한 파일 복사
Copy-Item "$env:USERPROFILE\Downloads\client_secret_*.json" config\google_credentials.json

# 4. 토큰 생성
python test_google_forms_oauth.py

# 5. Main 시스템 실행
python src/advanced_restaurant_system.py
```

---

## 📚 추가 참고 자료

- **전체 설정 가이드:** `docs/guides/REAL_EMAIL_SURVEY_GUIDE.md`
- **Google Forms API 문서:** https://developers.google.com/forms/api
- **OAuth 2.0 가이드:** https://developers.google.com/identity/protocols/oauth2
- **Python Quickstart:** https://developers.google.com/forms/api/quickstart/python

---

## 💡 자주 묻는 질문

**Q: Service Account를 사용할 수 없나요?**
A: Google Forms API는 Service Account로 제한적으로만 지원됩니다. OAuth 2.0 사용을 권장합니다.

**Q: 매번 로그인해야 하나요?**
A: 아니요. `token.json`이 생성되면 이후 자동 인증됩니다. 토큰은 자동으로 갱신됩니다.

**Q: token.json을 Git에 올려도 되나요?**
A: 절대 안됩니다! `.gitignore`에 이미 추가되어 있습니다. 개인 인증 정보이므로 공유하지 마세요.

**Q: 다른 사람도 사용하려면?**
A: 각자 자신의 Google 계정으로 `test_google_forms_oauth.py`를 실행하여 개인 `token.json`을 생성해야 합니다.

**Q: 프로덕션 환경에서는?**
A: 서버 환경에서는 Service Account 또는 다른 인증 방식을 고려해야 합니다. 현재 구현은 로컬 개발 환경용입니다.

