"""
설정 파일 설정 도구
사용자가 쉽게 config.json 파일을 생성하고 설정할 수 있도록 도와줍니다.
"""

import os
import json
import shutil
from pathlib import Path

def create_config_file():
    """config.json 파일을 생성합니다."""
    example_file = "config_example.json"
    config_file = "config.json"
    
    if not os.path.exists(example_file):
        print("❌ config_example.json 파일을 찾을 수 없습니다.")
        return False
    
    if os.path.exists(config_file):
        response = input(f"⚠️  {config_file} 파일이 이미 존재합니다. 덮어쓰시겠습니까? (y/N): ")
        if response.lower() != 'y':
            print("설정 파일 생성을 취소했습니다.")
            return False
    
    try:
        shutil.copy2(example_file, config_file)
        print(f"✅ {config_file} 파일이 생성되었습니다.")
        return True
    except Exception as e:
        print(f"❌ 설정 파일 생성 실패: {e}")
        return False

def setup_api_keys():
    """API 키를 설정합니다."""
    config_file = "config.json"
    
    if not os.path.exists(config_file):
        print("❌ config.json 파일이 없습니다. 먼저 설정 파일을 생성하세요.")
        return False
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print("🔑 API 키 설정")
        print("=" * 30)
        
        # OpenAI API 키
        openai_key = input("OpenAI API 키를 입력하세요 (필수): ").strip()
        if openai_key:
            config['api_keys']['openai_api_key'] = openai_key
            print("✅ OpenAI API 키가 설정되었습니다.")
        else:
            print("⚠️  OpenAI API 키가 설정되지 않았습니다.")
        
        # Serper API 키
        serper_key = input("Serper API 키를 입력하세요 (선택사항): ").strip()
        if serper_key:
            config['api_keys']['serper_api_key'] = serper_key
            print("✅ Serper API 키가 설정되었습니다.")
        
        # SendGrid API 키
        sendgrid_key = input("SendGrid API 키를 입력하세요 (선택사항): ").strip()
        if sendgrid_key:
            config['api_keys']['sendgrid_api_key'] = sendgrid_key
            print("✅ SendGrid API 키가 설정되었습니다.")
        
        # 설정 저장
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print("✅ 설정이 저장되었습니다.")
        return True
        
    except Exception as e:
        print(f"❌ 설정 저장 실패: {e}")
        return False

def setup_google_credentials():
    """Google 자격 증명을 설정합니다."""
    config_file = "config.json"
    
    if not os.path.exists(config_file):
        print("❌ config.json 파일이 없습니다. 먼저 설정 파일을 생성하세요.")
        return False
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print("🔑 Google 자격 증명 설정")
        print("=" * 30)
        print("Google Cloud Console에서 서비스 계정 키를 다운로드하고")
        print("JSON 파일의 경로를 입력하세요.")
        
        creds_path = input("Google 자격 증명 파일 경로: ").strip()
        if creds_path and os.path.exists(creds_path):
            config['google_credentials']['credentials_file'] = creds_path
            print("✅ Google 자격 증명이 설정되었습니다.")
        else:
            print("⚠️  Google 자격 증명 파일을 찾을 수 없습니다.")
        
        # 설정 저장
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print("✅ 설정이 저장되었습니다.")
        return True
        
    except Exception as e:
        print(f"❌ 설정 저장 실패: {e}")
        return False

def validate_config():
    """설정 파일을 검증합니다."""
    config_file = "config.json"
    
    if not os.path.exists(config_file):
        print("❌ config.json 파일이 없습니다.")
        return False
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print("🔍 설정 파일 검증")
        print("=" * 30)
        
        # API 키 검증
        api_keys = config.get('api_keys', {})
        required_keys = ['openai_api_key']
        
        for key in required_keys:
            value = api_keys.get(key, '')
            if value and value != f"your-{key}-here":
                print(f"✅ {key}: 설정됨")
            else:
                print(f"❌ {key}: 설정되지 않음")
        
        # Google 자격 증명 검증
        google_creds = config.get('google_credentials', {})
        creds_file = google_creds.get('credentials_file', '')
        if creds_file and os.path.exists(creds_file):
            print("✅ Google 자격 증명: 설정됨")
        else:
            print("⚠️  Google 자격 증명: 설정되지 않음")
        
        return True
        
    except Exception as e:
        print(f"❌ 설정 파일 검증 실패: {e}")
        return False

def main():
    """메인 함수"""
    print("🔧 CrewAI 맛집 추천 시스템 설정 도구")
    print("=" * 50)
    
    while True:
        print("\n선택하세요:")
        print("1. 설정 파일 생성")
        print("2. API 키 설정")
        print("3. Google 자격 증명 설정")
        print("4. 설정 검증")
        print("5. 종료")
        
        choice = input("\n선택 (1-5): ").strip()
        
        if choice == '1':
            create_config_file()
        elif choice == '2':
            setup_api_keys()
        elif choice == '3':
            setup_google_credentials()
        elif choice == '4':
            validate_config()
        elif choice == '5':
            print("👋 설정 도구를 종료합니다.")
            break
        else:
            print("❌ 잘못된 선택입니다. 1-5 중에서 선택하세요.")

if __name__ == "__main__":
    main()
