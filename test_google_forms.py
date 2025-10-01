"""
Google Forms API 테스트 스크립트
"""

import os
import sys
from pathlib import Path

# 프로젝트 루트를 Python path에 추가
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def test_google_forms_api():
    """Google Forms API 연결을 테스트합니다."""
    
    print("="*80)
    print("🔧 Google Forms API 테스트")
    print("="*80)
    
    # 1. credentials 파일 확인
    credentials_path = PROJECT_ROOT / "config" / "google_credentials.json"
    print(f"\n1️⃣ Credentials 파일 확인")
    print(f"   경로: {credentials_path}")
    
    if not credentials_path.exists():
        print(f"   ❌ 파일을 찾을 수 없습니다!")
        print(f"   📝 다음 경로에 google_credentials.json을 저장하세요:")
        print(f"      {credentials_path}")
        return False
    
    print(f"   ✅ 파일 존재 확인")
    
    # 2. 인증 테스트
    print(f"\n2️⃣ Google 서비스 계정 인증")
    try:
        credentials = service_account.Credentials.from_service_account_file(
            str(credentials_path),
            scopes=[
                'https://www.googleapis.com/auth/forms.body',
                'https://www.googleapis.com/auth/forms.responses.readonly',
                'https://www.googleapis.com/auth/drive',
                'https://www.googleapis.com/auth/drive.file'
            ]
        )
        print(f"   ✅ 인증 성공")
        print(f"   📧 서비스 계정: {credentials.service_account_email}")
    except Exception as e:
        print(f"   ❌ 인증 실패: {e}")
        return False
    
    # 3. Forms API 서비스 생성
    print(f"\n3️⃣ Google Forms API 서비스 생성")
    try:
        service = build('forms', 'v1', credentials=credentials)
        print(f"   ✅ 서비스 생성 성공")
    except Exception as e:
        print(f"   ❌ 서비스 생성 실패: {e}")
        return False
    
    # 4. 테스트 폼 생성
    print(f"\n4️⃣ 테스트 Google Form 생성")
    try:
        form = {
            "info": {
                "title": "테스트 설문조사",
                "documentTitle": "Test Survey",
            }
        }
        
        result = service.forms().create(body=form).execute()
        form_id = result['formId']
        
        print(f"   ✅ 폼 생성 성공!")
        print(f"   📝 Form ID: {form_id}")
        print(f"   🔗 편집 링크: https://docs.google.com/forms/d/{form_id}/edit")
        print(f"   📋 응답 링크: https://docs.google.com/forms/d/e/{form_id}/viewform")
        
        # 5. 테스트 질문 추가
        print(f"\n5️⃣ 테스트 질문 추가")
        questions = [
            {
                "createItem": {
                    "item": {
                        "title": "테스트 질문: 가장 좋아하는 음식은?",
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
            }
        ]
        
        update = {"requests": questions}
        service.forms().batchUpdate(formId=form_id, body=update).execute()
        
        print(f"   ✅ 질문 추가 성공!")
        
        print(f"\n" + "="*80)
        print(f"✅ 모든 테스트 통과!")
        print(f"="*80)
        print(f"\n📋 생성된 테스트 설문조사:")
        print(f"   편집: https://docs.google.com/forms/d/{form_id}/edit")
        print(f"   응답: https://docs.google.com/forms/d/e/{form_id}/viewform")
        print(f"\n💡 이 링크로 접속하여 설문조사를 확인하세요!")
        print(f"   (서비스 계정으로 생성되었으므로 공유 설정이 필요할 수 있습니다)")
        
        return True
        
    except HttpError as e:
        print(f"   ❌ 폼 생성 실패 (HTTP Error): {e}")
        print(f"\n💡 문제 해결 방법:")
        print(f"   1. Google Cloud Console에서 Forms API가 활성화되었는지 확인")
        print(f"   2. 서비스 계정에 적절한 권한이 있는지 확인")
        print(f"   3. API 할당량을 확인")
        return False
    except Exception as e:
        print(f"   ❌ 폼 생성 실패: {e}")
        return False

if __name__ == "__main__":
    success = test_google_forms_api()
    
    if success:
        print(f"\n🎉 Google Forms API가 정상적으로 작동합니다!")
        sys.exit(0)
    else:
        print(f"\n❌ Google Forms API 테스트 실패")
        print(f"   docs/guides/REAL_EMAIL_SURVEY_GUIDE.md를 참고하여 설정하세요.")
        sys.exit(1)

