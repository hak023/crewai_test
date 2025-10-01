"""
Google Forms API OAuth 2.0 테스트 스크립트
"""

import os
import sys
from pathlib import Path

# 프로젝트 루트를 Python path에 추가
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def test_google_forms_oauth():
    """Google Forms API OAuth 2.0 연결을 테스트합니다."""
    
    print("="*80)
    print("🔧 Google Forms API OAuth 2.0 테스트")
    print("="*80)
    
    SCOPES = ['https://www.googleapis.com/auth/forms.body']
    creds = None
    
    # 1. credentials 파일 확인
    credentials_path = PROJECT_ROOT / "config" / "google_credentials.json"
    token_path = PROJECT_ROOT / "config" / "token.json"
    
    print(f"\n1️⃣ Credentials 파일 확인")
    print(f"   OAuth 2.0 클라이언트: {credentials_path}")
    
    if not credentials_path.exists():
        print(f"   ❌ 파일을 찾을 수 없습니다!")
        print(f"   📝 다음 단계를 따라주세요:")
        print(f"      1. Google Cloud Console > APIs & Services > Credentials")
        print(f"      2. OAuth 2.0 클라이언트 ID 생성 (Desktop app)")
        print(f"      3. JSON 다운로드 후 {credentials_path}로 저장")
        return False
    
    print(f"   ✅ 파일 존재 확인")
    
    # 2. 토큰 확인
    print(f"\n2️⃣ 인증 토큰 확인")
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
        print(f"   ✅ 기존 token.json 발견")
    
    # 3. 인증
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print(f"   🔄 토큰 갱신 중...")
            try:
                creds.refresh(Request())
                print(f"   ✅ 토큰 갱신 완료")
            except Exception as e:
                print(f"   ❌ 토큰 갱신 실패: {e}")
                creds = None
        
        if not creds:
            print(f"\n3️⃣ OAuth 2.0 인증 시작")
            print(f"   🌐 웹 브라우저가 열립니다...")
            print(f"   📌 Google 계정으로 로그인하고 권한을 승인하세요.")
            
            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(credentials_path), SCOPES)
                creds = flow.run_local_server(port=0)
                print(f"   ✅ OAuth 2.0 인증 완료!")
            except Exception as e:
                print(f"   ❌ OAuth 인증 실패: {e}")
                return False
            
            # 토큰 저장
            try:
                with open(str(token_path), 'w') as token:
                    token.write(creds.to_json())
                print(f"   ✅ 인증 정보 저장: {token_path}")
            except Exception as e:
                print(f"   ⚠️  토큰 저장 실패: {e}")
    else:
        print(f"   ✅ 유효한 인증 토큰 확인")
    
    # 4. Forms API 서비스 생성
    print(f"\n4️⃣ Google Forms API 서비스 생성")
    try:
        service = build('forms', 'v1', credentials=creds)
        print(f"   ✅ 서비스 생성 성공")
    except Exception as e:
        print(f"   ❌ 서비스 생성 실패: {e}")
        return False
    
    # 5. 테스트 폼 생성
    print(f"\n5️⃣ 테스트 Google Form 생성")
    try:
        new_form = {
            'info': {
                'title': 'OAuth 2.0 테스트 설문조사',
                'documentTitle': 'OAuth Test Form'
            }
        }
        
        result = service.forms().create(body=new_form).execute()
        form_id = result['formId']
        
        print(f"   ✅ 폼 생성 성공!")
        print(f"   📝 Form ID: {form_id}")
        
        # 응답 URL 생성
        response_url = f"https://docs.google.com/forms/d/e/{form_id}/viewform"
        edit_url = f"https://docs.google.com/forms/d/{form_id}/edit"
        
        print(f"   🔗 편집 링크: {edit_url}")
        print(f"   📋 응답 링크: {response_url}")
        
        # 6. 테스트 질문 추가
        print(f"\n6️⃣ 테스트 질문 추가")
        questions = [
            {
                "createItem": {
                    "item": {
                        "title": "가장 좋아하는 음식은?",
                        "questionItem": {
                            "question": {
                                "required": True,
                                "choiceQuestion": {
                                    "type": "RADIO",
                                    "options": [
                                        {"value": "한식"},
                                        {"value": "중식"},
                                        {"value": "일식"},
                                        {"value": "양식"}
                                    ]
                                }
                            }
                        }
                    },
                    "location": {"index": 0}
                }
            },
            {
                "createItem": {
                    "item": {
                        "title": "만족도를 평가해주세요 (1-5점)",
                        "questionItem": {
                            "question": {
                                "required": True,
                                "scaleQuestion": {
                                    "low": 1,
                                    "high": 5,
                                    "lowLabel": "매우 불만족",
                                    "highLabel": "매우 만족"
                                }
                            }
                        }
                    },
                    "location": {"index": 1}
                }
            }
        ]
        
        update = {"requests": questions}
        service.forms().batchUpdate(formId=form_id, body=update).execute()
        
        print(f"   ✅ 질문 추가 완료!")
        
        print(f"\n" + "="*80)
        print(f"✅ 모든 테스트 통과!")
        print(f"="*80)
        print(f"\n📋 생성된 테스트 설문조사:")
        print(f"   편집: {edit_url}")
        print(f"   응답: {response_url}")
        print(f"\n💡 위 링크로 접속하여 설문조사를 확인하세요!")
        print(f"   OAuth 2.0으로 생성되었으므로 귀하의 Google 계정에서 소유합니다.")
        
        return True
        
    except HttpError as e:
        print(f"   ❌ 폼 생성 실패 (HTTP Error): {e}")
        print(f"\n💡 문제 해결 방법:")
        print(f"   1. Google Cloud Console에서 Forms API가 활성화되었는지 확인")
        print(f"   2. OAuth 2.0 클라이언트 ID가 올바르게 설정되었는지 확인")
        print(f"   3. 웹 브라우저에서 권한 승인이 완료되었는지 확인")
        return False
    except Exception as e:
        print(f"   ❌ 폼 생성 실패: {e}")
        return False

if __name__ == "__main__":
    success = test_google_forms_oauth()
    
    if success:
        print(f"\n🎉 Google Forms API OAuth 2.0이 정상적으로 작동합니다!")
        sys.exit(0)
    else:
        print(f"\n❌ Google Forms API OAuth 2.0 테스트 실패")
        print(f"   docs/guides/REAL_EMAIL_SURVEY_GUIDE.md를 참고하여 설정하세요.")
        sys.exit(1)

