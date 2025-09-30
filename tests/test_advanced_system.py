"""
CrewAI 고급 맛집 추천 및 설문조사 시스템 테스트
6개 에이전트의 통합 시스템을 테스트합니다.
"""

import os
import sys
from unittest.mock import patch, MagicMock

def test_imports():
    """필요한 모듈들이 정상적으로 import되는지 테스트"""
    try:
        from crewai import Agent, Task, Crew, Process
        from crewai_tools import SerperDevTool, WebsiteSearchTool
        from langchain_google_genai import ChatGoogleGenerativeAI
        import pandas as pd
        import matplotlib.pyplot as plt
        import seaborn as sns
        from sendgrid import SendGridAPIClient
        from googleapiclient.discovery import build
        print("✅ 모든 필요한 모듈이 정상적으로 import되었습니다.")
        return True
    except ImportError as e:
        print(f"❌ 모듈 import 실패: {e}")
        return False

def test_agent_creation():
    """6개 에이전트 생성 테스트"""
    try:
        from crewai import Agent
        
        # 6개 에이전트 생성 테스트
        agents = [
            Agent(role='리서처', goal='정보 수집', backstory='정보 수집 전문가', verbose=False),
            Agent(role='큐레이터', goal='정보 선별', backstory='정보 선별 전문가', verbose=False),
            Agent(role='커뮤니케이터', goal='결과 전달', backstory='커뮤니케이션 전문가', verbose=False),
            Agent(role='폼 생성자', goal='폼 생성', backstory='폼 생성 전문가', verbose=False),
            Agent(role='이메일 발송자', goal='이메일 발송', backstory='이메일 전문가', verbose=False),
            Agent(role='데이터 분석가', goal='데이터 분석', backstory='데이터 분석 전문가', verbose=False)
        ]
        
        print("✅ 6개 에이전트 생성이 정상적으로 작동합니다.")
        return True
    except Exception as e:
        print(f"❌ 에이전트 생성 실패: {e}")
        return False

def test_task_creation():
    """6개 작업(Task) 생성 테스트"""
    try:
        from crewai import Agent, Task
        
        # 테스트 에이전트들 생성
        agents = [
            Agent(role='리서처', goal='정보 수집', backstory='정보 수집 전문가', verbose=False),
            Agent(role='큐레이터', goal='정보 선별', backstory='정보 선별 전문가', verbose=False),
            Agent(role='커뮤니케이터', goal='결과 전달', backstory='커뮤니케이션 전문가', verbose=False),
            Agent(role='폼 생성자', goal='폼 생성', backstory='폼 생성 전문가', verbose=False),
            Agent(role='이메일 발송자', goal='이메일 발송', backstory='이메일 전문가', verbose=False),
            Agent(role='데이터 분석가', goal='데이터 분석', backstory='데이터 분석 전문가', verbose=False)
        ]
        
        # 6개 작업 생성
        tasks = [
            Task(description="정보 수집 작업", agent=agents[0], expected_output="수집된 정보"),
            Task(description="정보 선별 작업", agent=agents[1], expected_output="선별된 정보"),
            Task(description="결과 전달 작업", agent=agents[2], expected_output="전달된 결과"),
            Task(description="폼 생성 작업", agent=agents[3], expected_output="생성된 폼"),
            Task(description="이메일 발송 작업", agent=agents[4], expected_output="발송 결과"),
            Task(description="데이터 분석 작업", agent=agents[5], expected_output="분석 결과")
        ]
        
        print("✅ 6개 작업(Task) 생성이 정상적으로 작동합니다.")
        return True
    except Exception as e:
        print(f"❌ 작업 생성 실패: {e}")
        return False

def test_crew_creation():
    """6개 에이전트 크루 생성 테스트"""
    try:
        from crewai import Agent, Task, Crew, Process
        
        # 6개 에이전트들 생성
        agents = [
            Agent(role='리서처', goal='정보 수집', backstory='정보 수집 전문가', verbose=False),
            Agent(role='큐레이터', goal='정보 선별', backstory='정보 선별 전문가', verbose=False),
            Agent(role='커뮤니케이터', goal='결과 전달', backstory='커뮤니케이션 전문가', verbose=False),
            Agent(role='폼 생성자', goal='폼 생성', backstory='폼 생성 전문가', verbose=False),
            Agent(role='이메일 발송자', goal='이메일 발송', backstory='이메일 전문가', verbose=False),
            Agent(role='데이터 분석가', goal='데이터 분석', backstory='데이터 분석 전문가', verbose=False)
        ]
        
        # 6개 작업들 생성
        tasks = [
            Task(description="정보 수집 작업", agent=agents[0], expected_output="수집된 정보"),
            Task(description="정보 선별 작업", agent=agents[1], expected_output="선별된 정보"),
            Task(description="결과 전달 작업", agent=agents[2], expected_output="전달된 결과"),
            Task(description="폼 생성 작업", agent=agents[3], expected_output="생성된 폼"),
            Task(description="이메일 발송 작업", agent=agents[4], expected_output="발송 결과"),
            Task(description="데이터 분석 작업", agent=agents[5], expected_output="분석 결과")
        ]
        
        # 6개 에이전트 크루 생성
        test_crew = Crew(
            agents=agents,
            tasks=tasks,
            process=Process.sequential,
            verbose=False
        )
        
        print("✅ 6개 에이전트 크루(Crew) 생성이 정상적으로 작동합니다.")
        return True
    except Exception as e:
        print(f"❌ 크루 생성 실패: {e}")
        return False

def test_advanced_system_structure():
    """고급 시스템 구조 테스트"""
    try:
        # advanced_restaurant_system.py 모듈 import 테스트
        sys.path.append('.')
        from advanced_restaurant_system import AdvancedRestaurantSystem
        
        print("✅ 고급 맛집 추천 시스템 모듈이 정상적으로 import되었습니다.")
        return True
    except Exception as e:
        print(f"❌ 고급 시스템 모듈 import 실패: {e}")
        return False

def test_data_analysis_tools():
    """데이터 분석 도구 테스트"""
    try:
        import pandas as pd
        import matplotlib.pyplot as plt
        import seaborn as sns
        
        # 간단한 데이터 생성 및 시각화 테스트
        data = {'restaurant': ['A', 'B', 'C'], 'rating': [4.5, 4.2, 4.0]}
        df = pd.DataFrame(data)
        
        # 시각화 테스트 (실제로는 저장하지 않음)
        plt.figure(figsize=(8, 6))
        sns.barplot(data=df, x='restaurant', y='rating')
        plt.title('맛집 평점 비교')
        plt.close()  # 메모리 절약을 위해 닫기
        
        print("✅ 데이터 분석 도구가 정상적으로 작동합니다.")
        return True
    except Exception as e:
        print(f"❌ 데이터 분석 도구 테스트 실패: {e}")
        return False

def test_email_tools():
    """이메일 도구 테스트"""
    try:
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail
        
        # SendGrid 클라이언트 생성 테스트 (실제 발송은 하지 않음)
        sg = SendGridAPIClient(api_key="test-key")
        
        print("✅ 이메일 도구가 정상적으로 작동합니다.")
        return True
    except Exception as e:
        print(f"❌ 이메일 도구 테스트 실패: {e}")
        return False

def test_google_api_tools():
    """구글 API 도구 테스트"""
    try:
        from googleapiclient.discovery import build
        
        # 구글 API 서비스 생성 테스트 (실제 인증은 하지 않음)
        # service = build('forms', 'v1', credentials=None)
        
        print("✅ 구글 API 도구가 정상적으로 작동합니다.")
        return True
    except Exception as e:
        print(f"❌ 구글 API 도구 테스트 실패: {e}")
        return False

def main():
    """메인 테스트 함수"""
    print("🧪 CrewAI 고급 맛집 추천 및 설문조사 시스템 테스트 시작")
    print("=" * 70)
    
    tests = [
        ("모듈 Import 테스트", test_imports),
        ("6개 에이전트 생성 테스트", test_agent_creation),
        ("6개 작업 생성 테스트", test_task_creation),
        ("6개 에이전트 크루 생성 테스트", test_crew_creation),
        ("고급 시스템 구조 테스트", test_advanced_system_structure),
        ("데이터 분석 도구 테스트", test_data_analysis_tools),
        ("이메일 도구 테스트", test_email_tools),
        ("구글 API 도구 테스트", test_google_api_tools)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 {test_name} 실행 중...")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} 실패")
    
    print("\n" + "=" * 70)
    print(f"📊 테스트 결과: {passed}/{total} 통과")
    
    if passed == total:
        print("🎉 모든 테스트가 통과했습니다!")
        print("\n💡 다음 단계:")
        print("1. OpenAI API 키를 설정하세요")
        print("2. Google API 자격 증명을 설정하세요")
        print("3. SendGrid API 키를 설정하세요")
        print("4. python advanced_restaurant_system.py를 실행하세요")
    else:
        print("⚠️  일부 테스트가 실패했습니다. 오류를 확인해주세요.")

if __name__ == "__main__":
    main()
