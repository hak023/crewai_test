"""
CrewAI를 활용한 맛집 추천 시스템
3개의 전문 에이전트가 협력하여 사용자에게 맞는 맛집을 추천합니다.
"""

import os
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool
# WebsiteSearchTool은 OpenAI를 내부적으로 사용하므로 Gemini 환경에서는 제외
from langchain_google_genai import ChatGoogleGenerativeAI
import json
from typing import List, Dict, Any

# 프로젝트 루트 경로 추가
from pathlib import Path
import sys
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config_manager import load_config

# 설정 로딩 (config_manager가 자동으로 환경 변수를 설정함)
config = load_config()
if not config:
    print("❌ 설정 파일을 로딩할 수 없습니다. config.json 파일을 확인하세요.")
    exit(1)

class RestaurantFinder:


    def __init__(self):
        # 도구 설정
        self.search_tool = SerperDevTool()
        # WebsiteSearchTool은 OpenAI를 사용하므로 제거 (Gemini 사용 시)
        # self.web_search_tool = WebsiteSearchTool()
        
        # 지연 초기화를 위한 플래그
        self._initialized = False
        
        # LLM 설정 (config에서 읽어옴)
        system_settings = config.get_system_settings()
        llm_provider = system_settings.get("llm_provider", "gemini")
        
        if llm_provider == "gemini":
            # Gemini 사용
            self.llm = f"gemini/{system_settings.get('llm_model', 'gemini-2.0-flash')}"
        else:
            # OpenAI 사용
            self.llm = system_settings.get("llm_model", "gpt-3.5-turbo")
    
    def setup_agents(self):
        """3개의 전문 에이전트를 설정합니다."""
        
        print("🔍 첫 번째 Agent 생성 시작...")
        # ① 리서처 에이전트 (The Researcher)
        self.researcher = Agent(
            role='맛집 정보 수집 전문가',
            goal='사용자의 요청에 따라 맛집 정보를 수집하고 분석합니다',
            backstory="""당신은 맛집 정보 수집의 전문가입니다. 
            웹 검색, 위치 정보, 맛집 API를 활용하여 사용자가 원하는 조건에 맞는 
            모든 관련 맛집 정보를 체계적으로 수집합니다.""",
            tools=[self.search_tool],  # SerperDevTool만 사용 (Gemini 호환)
            verbose=True,
            allow_delegation=False,
            llm=self.llm  # LLM 명시적 설정
        )
        print("✅ 첫 번째 Agent 생성 완료!")
        
        # ② 큐레이터 에이전트 (The Curator)
        self.curator = Agent(
            role='맛집 큐레이터',
            goal='수집된 맛집 정보를 분석하여 최고의 추천 리스트를 선별합니다',
            backstory="""당신은 맛집 큐레이터로서 수집된 방대한 정보 중에서 
            사용자의 조건에 가장 적합한 식당을 선별하는 전문가입니다. 
            평점, 가격, 거리, 리뷰 품질 등을 종합적으로 평가하여 최적의 추천을 제공합니다.""",
            tools=[],
            verbose=True,
            allow_delegation=False,
            llm=self.llm  # LLM 명시적 설정
        )
        
        # ③ 커뮤니케이터 에이전트 (The Communicator)
        self.communicator = Agent(
            role='맛집 추천 커뮤니케이터',
            goal='선별된 맛집 정보를 사용자에게 친절하고 명확하게 전달합니다',
            backstory="""당신은 맛집 추천 결과를 사용자에게 효과적으로 전달하는 
            커뮤니케이션 전문가입니다. 복잡한 정보를 간결하고 이해하기 쉽게 
            정리하여 사용자가 쉽게 결정할 수 있도록 도와줍니다.""",
            tools=[],
            verbose=True,
            allow_delegation=False,
            llm=self.llm  # LLM 명시적 설정
        )
    
    def setup_tasks(self):
        """각 에이전트의 작업을 정의합니다."""
        
        # 리서처 작업
        self.research_task = Task(
            description="""사용자 요청: {user_request}
            
            다음 정보를 수집하세요:
            1. 요청된 지역의 맛집 정보 (이름, 주소, 전화번호)
            2. 각 맛집의 평점 및 리뷰 정보
            3. 가격대 및 메뉴 정보
            4. 영업시간 및 특별 정보
            5. 최근 리뷰 트렌드
            
            수집된 정보를 JSON 형태로 정리하여 다음 에이전트에게 전달하세요.""",
            agent=self.researcher,
            expected_output="수집된 맛집 정보의 JSON 형태 데이터"
        )
        
        # 큐레이터 작업
        self.curation_task = Task(
            description="""리서처가 수집한 맛집 정보를 분석하여 최고의 추천 리스트를 선별하세요.
            
            평가 기준:
            1. 평점 (40% 가중치)
            2. 가격 적정성 (30% 가중치)
            3. 거리 (20% 가중치)
            4. 리뷰 품질 (10% 가중치)
            
            상위 3-5개의 맛집을 선별하고, 각각의 추천 이유를 명시하세요.""",
            agent=self.curator,
            expected_output="선별된 맛집 리스트와 추천 이유"
        )
        
        # 커뮤니케이터 작업
        self.communication_task = Task(
            description="""큐레이터가 선별한 맛집 리스트를 사용자에게 친절하고 명확하게 전달하세요.
            
            다음 형식으로 정리하세요:
            🍽️ 추천 맛집 리스트
            
            [순위] [맛집명]
            📍 주소: [주소]
            💰 가격대: [가격대]
            ⭐ 평점: [평점]
            🕒 영업시간: [영업시간]
            📞 전화번호: [전화번호]
            
            💡 추천 이유: [왜 이 맛집을 추천하는지 간단한 설명]
            
            각 맛집마다 위 형식으로 정리하여 최종 보고서를 작성하세요.""",
            agent=self.communicator,
            expected_output="사용자 친화적인 맛집 추천 보고서"
        )
    
    def setup_crew(self):
        """에이전트들을 팀으로 구성합니다."""
        self.crew = Crew(
            agents=[self.researcher, self.curator, self.communicator],
            tasks=[self.research_task, self.curation_task, self.communication_task],
            process=Process.sequential,  # 순차적으로 작업 수행
            verbose=True
        )
    
    def find_restaurants(self, user_request: str) -> str:
        """맛집을 찾아 추천합니다."""
        # 지연 초기화
        if not self._initialized:
            print("🔧 시스템 초기화 중...")
            self.setup_agents()
            self.setup_tasks()
            self.setup_crew()
            self._initialized = True
            print("✅ 시스템 초기화 완료!")
        
        print(f"🔍 사용자 요청: {user_request}")
        print("=" * 50)
        
        # CrewAI 실행
        result = self.crew.kickoff(inputs={"user_request": user_request})
        
        return result

def main():
    """메인 함수"""
    print("🍽️ CrewAI 맛집 추천 시스템")
    print("=" * 50)
    
    # 맛집 추천 시스템 초기화
    finder = RestaurantFinder()


    # 사용자 요청 예시
    user_requests = [
        "광화문 근처 3만원 이하의 한식 맛집을 찾아줘",
        "강남역 주변 2만원 이하의 일식 맛집 추천해줘",
        "홍대 근처 1만원 이하의 치킨집을 찾아줘"
    ]
    
    print("사용 가능한 예시 요청:")
    for i, request in enumerate(user_requests, 1):
        print(f"{i}. {request}")
    
    print("\n직접 요청을 입력하거나 위 번호를 선택하세요:")
    user_input = input("입력: ").strip()
    
    # 번호 선택 처리
    if user_input.isdigit() and 1 <= int(user_input) <= len(user_requests):
        selected_request = user_requests[int(user_input) - 1]
    else:
        selected_request = user_input
    
    if not selected_request:
        print("요청이 입력되지 않았습니다.")
        return
    
    try:
        # 맛집 추천 실행
        result = finder.find_restaurants(selected_request)
        print("\n" + "=" * 50)
        print("🎉 추천 결과:")
        print("=" * 50)
        print(result)
        
    except Exception as e:
        print(f"❌ 오류가 발생했습니다: {e}")
        print("API 키 설정을 확인해주세요.")

if __name__ == "__main__":
    main()
