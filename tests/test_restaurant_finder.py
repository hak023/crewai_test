"""
CrewAI 맛집 추천 시스템 테스트
API 키 없이도 기본 구조를 테스트할 수 있는 간단한 테스트
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
        print("✅ 모든 필요한 모듈이 정상적으로 import되었습니다.")
        return True
    except ImportError as e:
        print(f"❌ 모듈 import 실패: {e}")
        return False

def test_agent_creation():
    """에이전트 생성 테스트"""
    try:
        from crewai import Agent
        
        # 간단한 테스트 에이전트 생성
        test_agent = Agent(
            role='테스트 에이전트',
            goal='테스트 목적',
            backstory='테스트용 에이전트입니다.',
            verbose=False
        )
        
        print("✅ 에이전트 생성이 정상적으로 작동합니다.")
        return True
    except Exception as e:
        print(f"❌ 에이전트 생성 실패: {e}")
        return False

def test_task_creation():
    """작업(Task) 생성 테스트"""
    try:
        from crewai import Agent, Task
        
        # 테스트 에이전트 생성
        test_agent = Agent(
            role='테스트 에이전트',
            goal='테스트 목적',
            backstory='테스트용 에이전트입니다.',
            verbose=False
        )
        
        # 테스트 작업 생성
        test_task = Task(
            description="테스트 작업입니다.",
            agent=test_agent,
            expected_output="테스트 결과"
        )
        
        print("✅ 작업(Task) 생성이 정상적으로 작동합니다.")
        return True
    except Exception as e:
        print(f"❌ 작업 생성 실패: {e}")
        return False

def test_crew_creation():
    """크루(Crew) 생성 테스트"""
    try:
        from crewai import Agent, Task, Crew, Process
        
        # 테스트 에이전트들 생성
        agent1 = Agent(
            role='테스트 에이전트 1',
            goal='테스트 목적 1',
            backstory='테스트용 에이전트 1입니다.',
            verbose=False
        )
        
        agent2 = Agent(
            role='테스트 에이전트 2',
            goal='테스트 목적 2',
            backstory='테스트용 에이전트 2입니다.',
            verbose=False
        )
        
        # 테스트 작업들 생성
        task1 = Task(
            description="첫 번째 테스트 작업입니다.",
            agent=agent1,
            expected_output="첫 번째 결과"
        )
        
        task2 = Task(
            description="두 번째 테스트 작업입니다.",
            agent=agent2,
            expected_output="두 번째 결과"
        )
        
        # 테스트 크루 생성
        test_crew = Crew(
            agents=[agent1, agent2],
            tasks=[task1, task2],
            process=Process.sequential,
            verbose=False
        )
        
        print("✅ 크루(Crew) 생성이 정상적으로 작동합니다.")
        return True
    except Exception as e:
        print(f"❌ 크루 생성 실패: {e}")
        return False

def test_restaurant_finder_structure():
    """맛집 추천 시스템 구조 테스트"""
    try:
        # restaurant_finder.py 모듈 import 테스트
        sys.path.append('.')
        from restaurant_finder import RestaurantFinder
        
        print("✅ 맛집 추천 시스템 모듈이 정상적으로 import되었습니다.")
        return True
    except Exception as e:
        print(f"❌ 맛집 추천 시스템 모듈 import 실패: {e}")
        return False

def main():
    """메인 테스트 함수"""
    print("🧪 CrewAI 맛집 추천 시스템 테스트 시작")
    print("=" * 50)
    
    tests = [
        ("모듈 Import 테스트", test_imports),
        ("에이전트 생성 테스트", test_agent_creation),
        ("작업 생성 테스트", test_task_creation),
        ("크루 생성 테스트", test_crew_creation),
        ("맛집 추천 시스템 구조 테스트", test_restaurant_finder_structure)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 {test_name} 실행 중...")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} 실패")
    
    print("\n" + "=" * 50)
    print(f"📊 테스트 결과: {passed}/{total} 통과")
    
    if passed == total:
        print("🎉 모든 테스트가 통과했습니다!")
        print("\n💡 다음 단계:")
        print("1. OpenAI API 키를 설정하세요")
        print("2. python restaurant_finder.py를 실행하세요")
    else:
        print("⚠️  일부 테스트가 실패했습니다. 오류를 확인해주세요.")

if __name__ == "__main__":
    main()
