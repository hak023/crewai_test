# -*- coding: utf-8 -*-
"""
설문조사 응답 데이터 분석 스크립트

Google Forms에서 수집된 설문조사 응답을 분석하고 리포트를 생성합니다.
"""

import os
import json
import time
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
import pandas as pd

# 프로젝트 루트 경로 추가
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config_manager import load_config
from src.logging_manager import get_logging_manager
from src.advanced_restaurant_system import AdvancedRestaurantSystem

# Google Forms API
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class SurveyDataAnalyzer:
    """설문조사 데이터 분석기"""
    
    def __init__(self):
        """초기화"""
        self.config = load_config()
        self.logger = get_logging_manager()
        self.system = AdvancedRestaurantSystem()
        
        # 리포트 저장 경로
        self.reports_dir = PROJECT_ROOT / "reports"
        self.reports_dir.mkdir(exist_ok=True)
        
    def _authenticate_google_forms(self) -> Credentials:
        """Google Forms API 인증"""
        SCOPES = [
            'https://www.googleapis.com/auth/forms.body.readonly',
            'https://www.googleapis.com/auth/forms.responses.readonly'
        ]
        creds = None
        token_path = PROJECT_ROOT / "config" / "token.json"
        
        if token_path.exists():
            creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
            self.logger.logger.info("✅ 기존 token.json에서 인증 정보 로드")
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                self.logger.logger.info("🔄 토큰 갱신 중...")
                from google.auth.transport.requests import Request
                creds.refresh(Request())
                self.logger.logger.info("✅ 토큰 갱신 완료")
        
        return creds
    
    def get_form_responses(self, form_id: str) -> Dict[str, Any]:
        """Google Form의 응답 데이터를 가져옵니다."""
        try:
            credentials = self._authenticate_google_forms()
            if not credentials:
                self.logger.logger.error("❌ Google Forms API 인증 실패")
                return None
            
            service = build('forms', 'v1', credentials=credentials)
            
            # Form 정보 가져오기
            form = service.forms().get(formId=form_id).execute()
            form_title = form.get('info', {}).get('title', '설문조사')
            
            self.logger.logger.info(f"📋 설문조사: {form_title}")
            
            # 응답 가져오기
            responses = service.forms().responses().list(formId=form_id).execute()
            
            response_list = responses.get('responses', [])
            total_responses = len(response_list)
            
            self.logger.logger.info(f"📊 총 응답 수: {total_responses}개")
            
            return {
                'form_id': form_id,
                'form_title': form_title,
                'total_responses': total_responses,
                'responses': response_list,
                'questions': form.get('items', [])
            }
            
        except HttpError as e:
            self.logger.logger.error(f"❌ Google Forms API 오류: {e}")
            return None
        except Exception as e:
            self.logger.logger.error(f"❌ 응답 가져오기 실패: {e}")
            return None
    
    def parse_responses_to_dict(self, form_data: Dict[str, Any]) -> Dict[str, Any]:
        """Form 응답을 분석 가능한 형태로 파싱합니다."""
        if not form_data or not form_data.get('responses'):
            return {}
        
        parsed_data = {
            'total_responses': form_data['total_responses'],
            'restaurant_preferences': {},
            'feedback_comments': []
        }
        
        for response in form_data['responses']:
            answers = response.get('answers', {})
            
            for question_id, answer_data in answers.items():
                answer = answer_data.get('textAnswers', {}).get('answers', [])
                
                if answer:
                    answer_text = answer[0].get('value', '')
                    
                    # 맛집 선택 응답 집계
                    if '[' in answer_text and '위]' in answer_text:
                        # "[1위] 맛집 이름" 형식 파싱
                        if answer_text in parsed_data['restaurant_preferences']:
                            parsed_data['restaurant_preferences'][answer_text] += 1
                        else:
                            parsed_data['restaurant_preferences'][answer_text] = 1
                    # 피드백 응답 수집
                    elif len(answer_text) > 10:  # 자유 텍스트 응답으로 추정
                        parsed_data['feedback_comments'].append(answer_text)
        
        return parsed_data
    
    def generate_report(self, analysis_result: str, form_data: Dict[str, Any]) -> str:
        """분석 결과를 리포트 파일로 저장합니다."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"survey_report_{timestamp}.md"
        report_path = self.reports_dir / report_filename
        
        # 리포트 내용 생성
        report_content = f"""# 설문조사 분석 리포트

## 📋 기본 정보

- **설문조사 제목**: {form_data.get('form_title', 'N/A')}
- **분석 일시**: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M:%S')}
- **총 응답 수**: {form_data.get('total_responses', 0)}개

---

## 📊 응답 현황

"""
        
        # 맛집 선호도
        if form_data.get('restaurant_preferences'):
            report_content += "### 맛집 선호도\n\n"
            for restaurant, count in sorted(
                form_data['restaurant_preferences'].items(), 
                key=lambda x: x[1], 
                reverse=True
            ):
                percentage = (count / form_data['total_responses']) * 100
                report_content += f"- **{restaurant}**: {count}표 ({percentage:.1f}%)\n"
            report_content += "\n"
        
        # 피드백 코멘트
        if form_data.get('feedback_comments'):
            report_content += "### 💬 사용자 피드백\n\n"
            for idx, comment in enumerate(form_data['feedback_comments'][:10], 1):
                report_content += f"{idx}. \"{comment}\"\n"
            
            if len(form_data['feedback_comments']) > 10:
                report_content += f"\n... 외 {len(form_data['feedback_comments']) - 10}개 피드백\n"
            report_content += "\n"
        
        # AI 분석 결과
        report_content += f"""---

## 🤖 AI 분석 결과

{analysis_result}

---

## 📁 리포트 정보

- **리포트 파일**: `{report_filename}`
- **저장 위치**: `{self.reports_dir}`
- **생성 시간**: {datetime.now().isoformat()}

"""
        
        # 파일로 저장
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        self.logger.logger.info(f"✅ 리포트 저장 완료: {report_path}")
        
        return str(report_path)
    
    def send_report_email(self, report_path: str, recipients: List[str]):
        """분석 리포트를 이메일로 발송합니다."""
        try:
            # 리포트 파일 읽기
            with open(report_path, 'r', encoding='utf-8') as f:
                report_content = f.read()
            
            # 이메일 발송
            email_settings = self.config.get_email_settings()
            
            for recipient in recipients:
                success = self.system._send_email_smtp(
                    recipient=recipient,
                    subject=f"[맛집 추천] 설문조사 분석 리포트 - {datetime.now().strftime('%Y-%m-%d')}",
                    body=f"설문조사 분석 리포트가 생성되었습니다.\n\n{report_content[:500]}...\n\n전체 리포트는 첨부 파일을 확인하세요.",
                    survey_link=f"파일: {Path(report_path).name}"
                )
                
                if success:
                    self.logger.logger.info(f"✅ 리포트 이메일 발송: {recipient}")
                else:
                    self.logger.logger.warning(f"⚠️  리포트 이메일 발송 실패: {recipient}")
        
        except Exception as e:
            self.logger.logger.error(f"❌ 리포트 이메일 발송 오류: {e}")


def main():
    """메인 함수"""
    print("\n" + "=" * 80)
    print("📊 설문조사 데이터 분석 시스템")
    print("=" * 80)
    
    analyzer = SurveyDataAnalyzer()
    
    # Form ID 입력
    print("\n📋 Google Form ID를 입력하세요:")
    print("   (Form URL에서 '/d/' 다음의 문자열)")
    print("   예시: https://docs.google.com/forms/d/[FORM_ID]/viewform")
    
    form_id = input("\nForm ID: ").strip()
    
    if not form_id:
        print("❌ Form ID가 입력되지 않았습니다.")
        return
    
    print("\n" + "=" * 80)
    print("📥 설문조사 응답 가져오는 중...")
    print("=" * 80)
    
    # 응답 데이터 가져오기
    form_data = analyzer.get_form_responses(form_id)
    
    if not form_data:
        print("❌ 설문조사 응답을 가져올 수 없습니다.")
        return
    
    total_responses = form_data.get('total_responses', 0)
    
    print(f"\n✅ 응답 수집 완료!")
    print(f"   📊 현재까지 설문조사 완료된 개수: {total_responses}개")
    
    if total_responses == 0:
        print("\n⚠️  아직 응답이 없습니다.")
        print("   설문조사 링크를 공유하고 응답을 받은 후 다시 실행하세요.")
        return
    
    # 사용자 확인
    print("\n" + "=" * 80)
    print("📝 현재까지 결과로 리포트를 작성하시겠습니까?")
    print(f"   현재 응답 수: {total_responses}개")
    print("=" * 80)
    
    response = input("\n리포트 작성 (y/n): ").strip().lower()
    
    if response != 'y' and response != 'yes':
        print("\n⚠️  리포트 작성이 취소되었습니다.")
        return
    
    print("\n" + "=" * 80)
    print("🤖 AI 데이터 분석 시작...")
    print("=" * 80)
    
    # 응답 데이터 파싱
    parsed_data = analyzer.parse_responses_to_dict(form_data)
    
    # AI 분석 실행
    analysis_result = analyzer.system.analyze_survey_data(parsed_data)
    
    # 리포트 생성
    print("\n" + "=" * 80)
    print("📄 리포트 생성 중...")
    print("=" * 80)
    
    report_path = analyzer.generate_report(analysis_result, form_data)
    
    print(f"\n✅ 리포트 생성 완료!")
    print(f"   📁 저장 위치: {report_path}")
    
    # 이메일 발송 확인
    print("\n" + "=" * 80)
    print("📧 리포트를 이메일로 발송하시겠습니까?")
    print("=" * 80)
    
    email_response = input("\n이메일 발송 (y/n): ").strip().lower()
    
    if email_response == 'y' or email_response == 'yes':
        email_settings = analyzer.config.get_email_settings()
        recipients = email_settings.get('recipients', [])
        
        if recipients:
            print(f"\n📧 이메일 발송 중... (수신자: {len(recipients)}명)")
            analyzer.send_report_email(report_path, recipients)
            print("\n✅ 이메일 발송 완료!")
        else:
            print("\n⚠️  수신자가 설정되지 않았습니다.")
            print("   config.json의 email_settings.recipients를 확인하세요.")
    else:
        print("\n⚠️  이메일 발송이 취소되었습니다.")
    
    print("\n" + "=" * 80)
    print("✅ 분석 완료!")
    print("=" * 80)
    print(f"\n📁 리포트 파일: {report_path}")
    print("   파일을 열어서 상세 분석 결과를 확인하세요.\n")


if __name__ == "__main__":
    main()

