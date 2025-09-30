# Gemini API 설정 가이드

## 1. Gemini API 키 발급

1. **Google AI Studio** 방문: https://aistudio.google.com/
2. **Get API Key** 클릭
3. **Create API Key** 선택
4. API 키를 복사하여 저장

## 2. API 키 설정

### 방법 1: config.json 파일 수정
```json
{
  "api_keys": {
    "gemini_api_key": "여기에_발급받은_API_키_입력"
  }
}
```

### 방법 2: 환경 변수 설정
```bash
# Windows PowerShell
$env:GEMINI_API_KEY="여기에_발급받은_API_키_입력"

# Windows CMD
set GEMINI_API_KEY=여기에_발급받은_API_키_입력
```

## 3. 테스트 실행

```bash
python -c "
from advanced_restaurant_system import AdvancedRestaurantSystem
system = AdvancedRestaurantSystem()
print('Gemini API 설정 완료!')
"
```

## 4. 주의사항

- Gemini API는 무료 할당량이 있습니다 (월 15회 요청)
- API 키는 안전하게 보관하세요
- 프로덕션 환경에서는 환경 변수 사용을 권장합니다

## 5. 문제 해결

### API 키 오류
- API 키가 올바르게 설정되었는지 확인
- Google AI Studio에서 API 키가 활성화되어 있는지 확인

### 네트워크 오류
- 인터넷 연결 상태 확인
- 방화벽 설정 확인

### 모델 오류
- 지원되는 모델명 확인: `gemini-1.5-flash`, `gemini-1.5-pro`
