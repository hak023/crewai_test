# -*- coding: utf-8 -*-
"""
Google Forms API OAuth 2.0 인증 테스트 및 토큰 생성 스크립트

이 스크립트를 실행하면:
1. 웹 브라우저가 열립니다
2. Google 계정으로 로그인합니다
3. 권한을 승인합니다
4. config/token.json 파일이 자동 생성됩니다
5. 간단한 테스트 설문조사를 생성합니다

생성된 token.json은 계속 재사용됩니다.
"""

import os
import json
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# 프로젝트 루트 경로
PROJECT_ROOT = Path(__file__).parent

# Google Forms API 스코프
SCOPES = ['https://www.googleapis.com/auth/forms.body']

def authenticate_google_forms():
    """Google Forms API OAuth 2.0 인증"""
    creds = None
    token_path = PROJECT_ROOT / "config" / "token.json"
    
    # 기존 토큰 로드
    if token_path.exists():
        print(f"✅ 기존 token.json 발견: {token_path}")
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
        print("✅ 기존 인증 정보 로드 완료")
    
    # 토큰이 없거나 만료된 경우
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄 토큰이 만료되었습니다. 갱신 중...")
            creds.refresh(Request())
            print("✅ 토큰 갱신 완료")
        else:
            # OAuth 2.0 클라이언트 ID 파일 경로
            credentials_path = PROJECT_ROOT / "config" / "google_credentials.json"
            
            if not credentials_path.exists():
                print(f"❌ OAuth 2.0 클라이언트 ID 파일을 찾을 수 없습니다: {credentials_path}")
                print("\n📝 해결 방법:")
                print("1. Google Cloud Console에서 OAuth 2.0 클라이언트 ID를 생성하세요")
                print("2. '데스크톱 앱' 유형으로 생성하세요 (웹 앱 아님!)")
                print("3. 다운로드한 JSON 파일을 config/google_credentials.json에 저장하세요")
                print("\n📚 자세한 가이드: docs/guides/REAL_EMAIL_SURVEY_GUIDE.md")
                return None
            
            # 파일 내용 확인
            with open(credentials_path, 'r', encoding='utf-8') as f:
                creds_data = json.load(f)
            
            # Service Account인지 확인
            if creds_data.get("type") == "service_account":
                print("❌ 현재 파일은 Service Account 자격증명입니다.")
                print("❌ OAuth 2.0에는 '데스크톱 앱' 또는 '웹 애플리케이션' 클라이언트 ID가 필요합니다.\n")
                print("=" * 80)
                print("📝 OAuth 2.0 클라이언트 ID 생성 방법:")
                print("=" * 80)
                print("\n1️⃣  Google Cloud Console 접속:")
                print("   https://console.cloud.google.com/apis/credentials")
                print(f"\n2️⃣  프로젝트 선택: {creds_data.get('project_id', 'YOUR_PROJECT')}")
                print("\n3️⃣  '사용자 인증 정보 만들기' > 'OAuth 클라이언트 ID' 클릭")
                print("\n4️⃣  애플리케이션 유형: '데스크톱 앱' 선택 ⚠️ 중요!")
                print("   (이름: 'Restaurant System Desktop Client' 등)")
                print("\n5️⃣  '만들기' 클릭 후 JSON 다운로드")
                print("\n6️⃣  다운로드한 파일을 다음 경로에 저장:")
                print(f"   {credentials_path}")
                print("\n7️⃣  (선택) 기존 Service Account 파일 백업:")
                print(f"   config/google_credentials_service_account.json")
                print("\n8️⃣  이 스크립트를 다시 실행하세요")
                print("=" * 80)
                return None
            
            # OAuth 클라이언트 ID 확인
            if "installed" not in creds_data and "web" not in creds_data:
                print("❌ 올바른 OAuth 2.0 클라이언트 ID 형식이 아닙니다.")
                print(f"❌ 파일 내용: {creds_data.keys()}")
                return None
            
            print("\n" + "=" * 80)
            print("🔐 OAuth 2.0 인증 시작")
            print("=" * 80)
            print("\n⏳ 웹 브라우저가 열립니다...")
            print("📌 Google 계정으로 로그인하세요")
            print("📌 '이 앱은 Google에서 확인하지 않았습니다' 경고가 나오면:")
            print("   1. '고급' 클릭")
            print("   2. '프로젝트 이름(안전하지 않음)으로 이동' 클릭")
            print("📌 권한 승인 요청이 나오면 '허용' 클릭\n")
            
            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(credentials_path), SCOPES)
                creds = flow.run_local_server(port=0)
                print("\n✅ OAuth 2.0 인증 완료!")
            except Exception as auth_error:
                print(f"\n❌ OAuth 인증 실패: {auth_error}")
                return None
        
        # 토큰 저장
        try:
            token_path.parent.mkdir(parents=True, exist_ok=True)
            with open(str(token_path), 'w') as token:
                token.write(creds.to_json())
            print(f"✅ 인증 정보 저장 완료: {token_path}")
            print("   (다음부터는 이 파일을 사용하여 자동 인증됩니다)")
        except Exception as save_error:
            print(f"⚠️  token.json 저장 실패: {save_error}")
    
    return creds


def create_test_form(creds):
    """테스트용 간단한 설문조사 생성"""
    try:
        service = build('forms', 'v1', credentials=creds)
        
        print("\n" + "=" * 80)
        print("📝 테스트 설문조사 생성 중...")
        print("=" * 80)
        
        # 설문조사 생성
        form = {
            "info": {
                "title": "🍽️ 맛집 추천 테스트 설문조사",
                "documentTitle": "Restaurant Recommendation Test Survey"
            }
        }
        
        result = service.forms().create(body=form).execute()
        form_id = result['formId']
        form_url = result['responderUri']
        
        # 질문 추가
        update = {
            "requests": [
                {
                    "createItem": {
                        "item": {
                            "title": "추천된 맛집 중 가장 마음에 드는 곳은?",
                            "questionItem": {
                                "question": {
                                    "required": True,
                                    "choiceQuestion": {
                                        "type": "RADIO",
                                        "options": [
                                            {"value": "맛집 A"},
                                            {"value": "맛집 B"},
                                            {"value": "맛집 C"}
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
                            "title": "추천 만족도를 평가해주세요",
                            "questionItem": {
                                "question": {
                                    "required": False,
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
                },
                {
                    "createItem": {
                        "item": {
                            "title": "추가 의견이 있으시면 작성해주세요",
                            "questionItem": {
                                "question": {
                                    "required": False,
                                    "textQuestion": {
                                        "paragraph": True
                                    }
                                }
                            }
                        },
                        "location": {"index": 2}
                    }
                }
            ]
        }
        
        service.forms().batchUpdate(formId=form_id, body=update).execute()
        
        print("\n✅ 테스트 설문조사 생성 성공!")
        print("=" * 80)
        print(f"📋 Form ID: {form_id}")
        print(f"🔗 설문조사 링크: {form_url}")
        print("=" * 80)
        print("\n💡 웹 브라우저에서 위 링크를 열어 설문조사를 확인하세요!")
        print("💡 이제 main 시스템에서도 동일한 방식으로 설문조사를 생성할 수 있습니다.")
        
        return form_url
        
    except HttpError as e:
        print(f"\n❌ Google Form 생성 실패: {e}")
        return None
    except Exception as e:
        print(f"\n❌ 설문조사 생성 중 오류: {e}")
        return None


def main():
    print("\n" + "=" * 80)
    print("🔐 Google Forms API OAuth 2.0 인증 테스트")
    print("=" * 80)
    print("\n이 스크립트는:")
    print("1. OAuth 2.0 인증을 수행합니다")
    print("2. config/token.json 파일을 생성합니다")
    print("3. 테스트 설문조사를 생성합니다")
    print("\n" + "=" * 80 + "\n")
    
    # 인증
    creds = authenticate_google_forms()
    
    if creds:
        print("\n✅ 인증 성공!")
        print("✅ 이제 config/token.json 파일이 생성되었습니다.")
        print("✅ main 시스템에서 이 토큰을 자동으로 사용합니다.\n")
        
        # 테스트 설문조사 생성
        user_input = input("테스트 설문조사를 생성하시겠습니까? (y/n): ")
        if user_input.lower() == 'y':
            create_test_form(creds)
    else:
        print("\n❌ 인증 실패")
        print("📚 자세한 가이드: docs/guides/REAL_EMAIL_SURVEY_GUIDE.md")


if __name__ == "__main__":
    main()
