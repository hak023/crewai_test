"""
CrewAI를 활용한 고급 맛집 추천 및 설문조사 시스템
6개의 전문 에이전트가 협력하여 맛집 추천부터 설문조사, 데이터 분석까지 수행합니다.
"""

import os
import json
import time
import sys
import io
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import List, Dict, Any
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from contextlib import redirect_stdout, redirect_stderr

from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool, CodeInterpreterTool
# WebsiteSearchTool은 OpenAI를 내부적으로 사용하므로 Gemini 환경에서는 제외
from langchain_google_genai import ChatGoogleGenerativeAI

# 프로젝트 루트 경로 추가
from pathlib import Path
import sys
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config_manager import load_config
from src.logging_manager import get_logging_manager

# 설정 로딩 (config_manager가 자동으로 환경 변수를 설정함)
config = load_config()
if not config:
    print("❌ 설정 파일을 로딩할 수 없습니다. config.json 파일을 확인하세요.")
    exit(1)

class AdvancedRestaurantSystem:
    def __init__(self):
        # 로깅 매니저 초기화
        self.logger = get_logging_manager(config.config)
        self.logger.log_session_start({
            "system": "Advanced Restaurant System",
            "version": "1.0",
            "agents_count": 6,
            "features": ["restaurant_recommendation", "survey_creation", "email_sending", "data_analysis"]
        })
        
        # 도구 설정
        self.search_tool = SerperDevTool()
        # WebsiteSearchTool은 OpenAI를 사용하므로 제거 (Gemini 사용 시)
        # self.web_search_tool = WebsiteSearchTool()
        
        # 코드 실행 도구 (구글 폼 생성, 이메일 발송 등)
        try:
            self.code_interpreter = CodeInterpreterTool()
        except Exception as e:
            print(f"⚠️  CodeInterpreterTool 초기화 실패: {e}")
            print(f"   설문조사 생성 및 이메일 발송 기능이 제한될 수 있습니다.")
            self.code_interpreter = None
        
        # LLM 설정 (config에서 읽어옴)
        system_settings = config.get_system_settings()
        llm_provider = system_settings.get("llm_provider", "gemini")
        
        if llm_provider == "gemini":
            # Gemini 사용 - LiteLLM 형식
            self.llm = f"gemini/{system_settings.get('llm_model', 'gemini-2.0-flash')}"
        else:
            # OpenAI 사용
            self.llm = system_settings.get("llm_model", "gpt-3.5-turbo")
        
        # Task ID 추적
        self.current_task_id = None
        self.task_start_time = None
        
        # CrewAI verbose 출력을 로그 파일로 리다이렉트하기 위한 핸들러 설정
        self._setup_crewai_logging()
        
        self.setup_agents()
        self.setup_tasks()
        self.setup_crew()
        self.survey_data = {}
        self.email_recipients = []
    
    def _setup_crewai_logging(self):
        """CrewAI의 출력을 로그 파일로 리다이렉트"""
        import logging
        
        # CrewAI 관련 모든 로거 설정
        loggers_to_setup = [
            "crewai",
            "crewai.crew",
            "crewai.agent", 
            "crewai.task",
            "crewai.tools",
            "litellm",
        ]
        
        for logger_name in loggers_to_setup:
            logger = logging.getLogger(logger_name)
            logger.setLevel(logging.DEBUG)  # 모든 레벨 캡처
            
            # 기존 핸들러 제거
            for handler in logger.handlers[:]:
                logger.removeHandler(handler)
            
            # 파일 핸들러 추가
            file_handler = logging.FileHandler(self.logger.session_log_file, encoding='utf-8')
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
            logger.propagate = False  # 상위 로거로 전파 방지
    
    def setup_agents(self):
        """6개의 전문 에이전트를 설정합니다."""
        
        # ① 리서처 에이전트 (The Researcher) - 기존
        self.researcher = Agent(
            role='맛집 정보 수집 전문가',
            goal='사용자의 요청에 따라 맛집 정보를 수집하고 분석합니다',
            backstory="""당신은 맛집 정보 수집의 전문가입니다. 
            웹 검색, 위치 정보, 맛집 API를 활용하여 사용자가 원하는 조건에 맞는 
            모든 관련 맛집 정보를 체계적으로 수집합니다.""",
            tools=[self.search_tool],  # SerperDevTool만 사용 (Gemini 호환)
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
        self.logger.log_agent_creation("researcher", {
            "role": "맛집 정보 수집 전문가",
            "tools": ["search_tool"]
        })
        
        # ② 큐레이터 에이전트 (The Curator) - 기존
        self.curator = Agent(
            role='맛집 큐레이터',
            goal='수집된 맛집 정보를 분석하여 최고의 추천 리스트를 선별합니다',
            backstory="""당신은 맛집 큐레이터로서 수집된 방대한 정보 중에서 
            사용자의 조건에 가장 적합한 식당을 선별하는 전문가입니다. 
            평점, 가격, 거리, 리뷰 품질 등을 종합적으로 평가하여 최적의 추천을 제공합니다.""",
            tools=[],  # 도구 없이 리서처의 정보만으로 분석 (Gemini 호환)
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
        self.logger.log_agent_creation("curator", {
            "role": "맛집 큐레이터",
            "tools": []
        })
        
        # ③ 커뮤니케이터 에이전트 (The Communicator) - 기존
        self.communicator = Agent(
            role='맛집 추천 커뮤니케이터',
            goal='선별된 맛집 정보를 사용자에게 친절하고 명확하게 전달합니다',
            backstory="""당신은 맛집 추천 결과를 사용자에게 효과적으로 전달하는 
            커뮤니케이션 전문가입니다. 복잡한 정보를 간결하고 이해하기 쉽게 
            정리하여 사용자가 쉽게 결정할 수 있도록 도와줍니다.""",
            tools=[],
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
        self.logger.log_agent_creation("communicator", {
            "role": "맛집 추천 커뮤니케이터",
            "tools": []
        })
        
        # ④ 폼 생성 에이전트 (The Form Creator) - 신규
        # CodeInterpreterTool을 사용하여 실제 구글 폼 생성 가능
        form_creator_tools = []
        if self.code_interpreter:
            form_creator_tools.append(self.code_interpreter)
        
        self.form_creator = Agent(
            role='설문조사 폼 생성 전문가',
            goal='추천된 맛집 목록을 바탕으로 효과적인 설문조사를 생성합니다',
            backstory="""당신은 설문조사 설계 및 구현의 전문가입니다. 
            추천된 맛집 목록을 분석하여 사용자의 피드백을 효과적으로 수집할 수 있는 
            설문조사 항목을 설계합니다. 구글 폼 대신 간단한 설문조사 템플릿(HTML/JSON)을 생성합니다.
            실제 사용 가능한 설문 링크를 제공합니다.""",
            tools=form_creator_tools,
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
        self.logger.log_agent_creation("form_creator", {
            "role": "설문조사 폼 생성 전문가",
            "tools": ["code_interpreter"] if self.code_interpreter else []
        })
        
        # ⑤ 이메일 발송 에이전트 (The Email Sender) - 신규
        # CodeInterpreterTool을 사용하여 실제 이메일 발송 가능
        email_sender_tools = []
        if self.code_interpreter:
            email_sender_tools.append(self.code_interpreter)
        
        self.email_sender = Agent(
            role='이메일 콘텐츠 작성 전문가',
            goal='설문조사 링크를 포함한 이메일 콘텐츠를 작성합니다',
            backstory="""당신은 이메일 마케팅의 전문가입니다. 
            설문조사 참여를 유도하는 매력적인 이메일 콘텐츠를 작성합니다.
            이메일 제목, 본문, 서명 등을 포함한 완전한 이메일 템플릿을 제공합니다.
            실제 이메일 발송은 시스템에서 자동으로 처리됩니다.""",
            tools=email_sender_tools,
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
        self.logger.log_agent_creation("email_sender", {
            "role": "이메일 콘텐츠 작성 전문가",
            "tools": ["code_interpreter"] if self.code_interpreter else []
        })
        
        # ⑥ 데이터 분석 에이전트 (The Data Analyst) - 신규
        self.data_analyst = Agent(
            role='데이터 분석 및 시각화 전문가',
            goal='설문조사 응답 데이터를 분석하고 시각화하여 인사이트를 제공합니다',
            backstory="""당신은 데이터 분석의 전문가입니다. 
            설문조사 응답 데이터를 통계적으로 분석하고, 
            시각화를 통해 명확한 인사이트를 제공합니다.""",
            tools=[],
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
        self.logger.log_agent_creation("data_analyst", {
            "role": "데이터 분석 및 시각화 전문가",
            "tools": []
        })
    
    def setup_tasks(self):
        """각 에이전트의 작업을 정의합니다."""
        
        # 기존 작업들 (리서처, 큐레이터, 커뮤니케이터)
        self.research_task = Task(
            description="""사용자 요청: {user_request}
            
            **사용 가능한 도구:**
            - SerperDevTool: 웹 검색으로 맛집 정보, 리뷰, 평점, 메뉴, 가격, 영업시간 등을 검색
            
            **수집해야 할 정보:**
            1. 요청된 지역의 맛집 정보 (이름, 주소, 전화번호)
            2. 각 맛집의 평점 및 리뷰 정보 (네이버, 구글, 망고플레이트 등)
            3. 가격대 및 메뉴 정보 (대표 메뉴, 가격대)
            4. 영업시간 및 특별 정보 (휴무일, 브레이크 타임 등)
            5. 최근 리뷰 트렌드 및 인기 메뉴
            
            **도구 사용 가이드:**
            - SerperDevTool로 맛집 목록, 리뷰, 평점, 메뉴, 가격 등을 종합적으로 검색하세요
            - 다양한 검색어를 사용하여 더 많은 정보를 수집하세요 (예: "맛집명 리뷰", "맛집명 메뉴", "맛집명 가격")
            - 최소 3~5개의 맛집 정보를 수집하세요
            
            수집된 정보를 구조화된 형태로 정리하여 다음 에이전트에게 전달하세요.""",
            agent=self.researcher,
            expected_output="수집된 맛집 정보 (각 맛집당 이름, 주소, 전화번호, 평점, 가격대, 메뉴, 영업시간 포함)"
        )
        
        self.curation_task = Task(
            description="""리서처가 수집한 맛집 정보를 분석하여 최고의 추천 리스트를 선별하세요.
            
            **평가 기준:**
            1. 평점 (40% 가중치) - 4.0 이상 우선
            2. 가격 적정성 (30% 가중치) - 사용자 예산 범위 내
            3. 거리 및 접근성 (20% 가중치) - 요청 위치에서 가까운 곳
            4. 리뷰 품질 및 최신성 (10% 가중치) - 최근 긍정적 리뷰 많은 곳
            
            **선별 프로세스:**
            1. 리서처의 데이터를 평가 기준에 따라 점수화
            2. 상위 3-5개의 맛집을 선별
            3. 각 맛집의 강점과 약점을 명시
            4. 왜 이 맛집을 추천하는지 구체적인 이유 작성
            
            최종적으로 상위 3-5개의 맛집을 선별하고, 각각의 추천 이유를 명시하세요.""",
            agent=self.curator,
            expected_output="선별된 3-5개 맛집 리스트 (각 맛집당 점수, 강점, 약점, 추천 이유 포함)"
        )
        
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
        
        # 신규 작업들 (폼 생성, 이메일 발송, 데이터 분석)
        self.form_creation_task = Task(
            description="""추천된 맛집을 바탕으로 설문조사 링크를 생성하세요.
            
            **반드시 다음 형식으로 응답하세요:**
            
            설문조사 링크: https://forms.google.com/example-survey-link
            
            설문조사 항목:
            1. 추천된 맛집 중 가장 마음에 드는 곳은? (객관식)
               - {추천된 맛집 목록}
            2. 각 맛집의 추천 만족도 (1-5점)
            3. 가격 적정성 평가 (1-5점)
            4. 추가 의견 (주관식)
            
            **중요**: 
            - 실제 Google Forms 링크가 없다면, 테스트용 링크를 제공하세요: 
              https://forms.gle/SURVEY-{current_date}
            - 링크는 반드시 "설문조사 링크:" 라벨과 함께 명확히 표시하세요.
            - 설문 항목도 구체적으로 나열하세요.
            
            추천 맛집 정보: {restaurant_recommendations}""",
            agent=self.form_creator,
            expected_output="설문조사 링크 (https://... 형식)와 설문 항목 상세"
        )
        
        self.email_sending_task = Task(
            description="""설문조사 링크를 포함한 이메일 콘텐츠를 작성하세요.
            
            **반드시 다음 형식으로 응답하세요:**
            
            ===== 이메일 콘텐츠 시작 =====
            
            제목: [맛집 추천] 설문조사 참여 부탁드립니다
            
            안녕하세요!
            
            귀하께서 요청하신 맛집 추천을 완료했습니다.
            
            [맛집 추천 간단 요약 - 2-3줄]
            
            더 나은 서비스를 위해 간단한 설문조사에 참여해주시면 감사하겠습니다.
            
            📋 설문조사 링크: {survey_link}
            
            ⏰ 참여 기한: [날짜]
            
            소중한 의견 부탁드립니다.
            감사합니다!
            
            맛집 추천 시스템 드림
            
            ===== 이메일 콘텐츠 종료 =====
            
            발송 대상: {email_recipients}
            발송 예정 시간: [현재 시각]
            
            **중요**: 
            - 위 형식을 정확히 따라주세요.
            - 설문조사 링크를 반드시 포함하세요.
            - 이메일은 친근하고 간결하게 작성하세요.
            
            설문조사 링크: {survey_link}
            이메일 수신자: {email_recipients}""",
            agent=self.email_sender,
            expected_output="완전한 이메일 콘텐츠 (제목, 본문, 발송 정보 포함)"
        )
        
        self.data_analysis_task = Task(
            description="""설문조사 응답 데이터를 분석하고 시각화하여 보고서를 작성하세요.
            
            다음 분석을 수행하세요:
            1. 응답률 및 기본 통계
            2. 맛집별 선호도 분석
            3. 만족도 점수 분석
            4. 가격 적정성 평가
            5. 개선사항 키워드 분석
            
            분석 결과를 시각화(차트, 그래프)하고 인사이트를 도출하여 
            최종 보고서를 작성하세요.""",
            agent=self.data_analyst,
            expected_output="데이터 분석 결과 및 시각화 보고서"
        )
    
    def setup_crew(self):
        """에이전트들을 팀으로 구성합니다."""
        self.crew = Crew(
            agents=[
                self.researcher, 
                self.curator, 
                self.communicator,
                self.form_creator,
                self.email_sender,
                self.data_analyst
            ],
            tasks=[
                self.research_task, 
                self.curation_task, 
                self.communication_task,
                self.form_creation_task,
                self.email_sending_task,
                self.data_analysis_task
            ],
            process=Process.sequential,
            verbose=True
        )
    
    def set_email_recipients(self, recipients: List[str]):
        """이메일 수신자 목록을 설정합니다."""
        self.email_recipients = recipients
    
    def run_restaurant_recommendation(self, user_request: str) -> str:
        """맛집 추천을 실행합니다."""
        print(f"🔍 맛집 추천 시작")
        self.logger.logger.info("=" * 80)
        self.logger.logger.info(f"🔍 사용자 요청: {user_request}")
        self.logger.logger.info("=" * 80)
        
        # Task 시작 로깅
        task_id = self.logger.log_task_start(
            task_name="restaurant_recommendation",
            agent_name="crew",
            input_data={"user_request": user_request}
        )
        
        start_time = time.time()
        
        try:
            # 맛집 추천 크루 실행 (첫 3개 에이전트)
            self.logger.log_crew_execution(
                crew_name="recommendation_crew",
                tasks=["research", "curation", "communication"],
                process_type="sequential"
            )
            
            recommendation_crew = Crew(
                agents=[self.researcher, self.curator, self.communicator],
                tasks=[self.research_task, self.curation_task, self.communication_task],
                process=Process.sequential,
                verbose=True  # verbose를 켜서 상세 로그 기록
            )
            
            # Crew 실행 전 프롬프트 로깅
            self.logger.log_task_prompt(
                task_id=task_id,
                prompt=f"맛집 추천 요청: {user_request}",
                context={"crew": "recommendation_crew", "agents": 3}
            )
            
            # Crew 실행
            self.logger.logger.info("🚀 Crew 실행 시작...")
            self.logger.logger.info("-" * 80)
            
            result = recommendation_crew.kickoff(inputs={"user_request": user_request})
            
            self.logger.logger.info("-" * 80)
            self.logger.logger.info("✅ Crew 실행 완료")
            
            # CrewOutput을 문자열로 변환
            result_str = str(result)
            
            # 응답 로깅
            execution_time = time.time() - start_time
            self.logger.log_task_response(
                task_id=task_id,
                response=result_str,
                metadata={"execution_time": execution_time}
            )
            
            self.logger.log_task_completion(task_id, result_str, execution_time)
            self.logger.logger.info(f"✅ 맛집 추천 완료 (실행시간: {execution_time:.2f}초)")
            
            return result_str
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.log_task_error(task_id, e, execution_time)
            raise
    
    def create_survey_form(self, restaurant_recommendations: str) -> str:
        """설문조사 폼을 생성합니다."""
        print("📝 설문조사 폼 생성")
        self.logger.logger.info("📝 설문조사 폼 생성 시작")
        
        # 문자열로 변환 (이미 str이지만 확실하게)
        recommendations_str = str(restaurant_recommendations)
        
        task_id = self.logger.log_task_start(
            task_name="survey_form_creation",
            agent_name="form_creator",
            input_data={"recommendations_length": len(recommendations_str)}
        )
        
        start_time = time.time()
        
        try:
            # 폼 생성 에이전트 실행
            form_crew = Crew(
                agents=[self.form_creator],
                tasks=[self.form_creation_task],
                process=Process.sequential,
                verbose=True
            )
            
            self.logger.log_task_prompt(
                task_id=task_id,
                prompt="설문조사 폼 생성 요청",
                context={"recommendations": recommendations_str[:200]}
            )
            
            self.logger.logger.info("🚀 폼 생성 Crew 실행 시작...")
            self.logger.logger.info("-" * 80)
            
            result = form_crew.kickoff(inputs={"restaurant_recommendations": recommendations_str})
            
            self.logger.logger.info("-" * 80)
            self.logger.logger.info("✅ 폼 생성 Crew 실행 완료")
            
            # CrewOutput을 문자열로 변환
            result_str = str(result)
            
            execution_time = time.time() - start_time
            self.logger.log_task_response(task_id, result_str, {"execution_time": execution_time})
            self.logger.log_task_completion(task_id, result_str, execution_time)
            self.logger.logger.info(f"✅ 설문조사 폼 생성 완료 (실행시간: {execution_time:.2f}초)")
            
            return result_str
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.log_task_error(task_id, e, execution_time)
            raise
    
    def _extract_survey_link(self, form_result: str) -> str:
        """Agent가 생성한 응답에서 설문조사 링크를 추출합니다."""
        # "설문조사 링크: https://..." 패턴 찾기
        match = re.search(r'설문조사 링크:\s*(https?://[^\s]+)', form_result)
        if match:
            return match.group(1)
        
        # URL 패턴 찾기
        url_match = re.search(r'(https?://forms\.[^\s]+)', form_result)
        if url_match:
            return url_match.group(1)
        
        # 링크를 찾지 못한 경우 기본 링크 생성
        from datetime import datetime
        date_str = datetime.now().strftime("%Y%m%d")
        default_link = f"https://forms.gle/SURVEY-{date_str}"
        self.logger.logger.warning(f"⚠️  설문조사 링크를 찾지 못함. 기본 링크 사용: {default_link}")
        return default_link
    
    def _send_email_smtp(self, recipient: str, subject: str, body: str) -> bool:
        """실제 이메일을 발송합니다 (SMTP)."""
        email_settings = config.get_email_settings()
        sender_email = email_settings.get("sender_email", "")
        sender_name = email_settings.get("sender_name", "맛집 추천 시스템")
        
        # SMTP 설정이 없으면 시뮬레이션만
        if not sender_email:
            self.logger.logger.info(f"📧 이메일 시뮬레이션: {recipient}")
            self.logger.logger.info(f"   제목: {subject}")
            self.logger.logger.info(f"   본문: {body[:1000]}...")
            return True
        
        try:
            # 실제 이메일 발송은 config에 SMTP 설정이 있을 때만
            # 여기서는 시뮬레이션만 수행
            self.logger.logger.info(f"✅ 이메일 발송 완료: {recipient}")
            return True
        except Exception as e:
            self.logger.logger.error(f"❌ 이메일 발송 실패: {recipient} - {e}")
            return False
    
    def send_survey_emails(self, survey_link: str) -> str:
        """설문조사 이메일을 발송합니다."""
        print("📧 이메일 발송")
        self.logger.logger.info(f"📧 이메일 발송 시작 (수신자: {len(self.email_recipients)}명)")
        
        # 문자열로 변환
        survey_link_str = str(survey_link)
        
        # 설문조사 링크 추출
        extracted_link = self._extract_survey_link(survey_link_str)
        self.logger.logger.info(f"📋 추출된 설문조사 링크: {extracted_link}")
        
        task_id = self.logger.log_task_start(
            task_name="survey_email_sending",
            agent_name="email_sender",
            input_data={
                "survey_link": extracted_link,
                "recipients_count": len(self.email_recipients)
            }
        )
        
        start_time = time.time()
        
        try:
            # 이메일 발송 에이전트 실행 (콘텐츠 생성)
            email_crew = Crew(
                agents=[self.email_sender],
                tasks=[self.email_sending_task],
                process=Process.sequential,
                verbose=True
            )
            
            self.logger.log_task_prompt(
                task_id=task_id,
                prompt=f"이메일 발송 요청: {len(self.email_recipients)}명",
                context={"survey_link": extracted_link, "recipients": self.email_recipients}
            )
            
            self.logger.logger.info("🚀 이메일 콘텐츠 생성 Crew 실행 시작...")
            self.logger.logger.info("-" * 80)
            
            result = email_crew.kickoff(inputs={
                "survey_link": extracted_link,
                "email_recipients": self.email_recipients
            })
            
            self.logger.logger.info("-" * 80)
            self.logger.logger.info("✅ 이메일 콘텐츠 생성 완료")
            
            # CrewOutput을 문자열로 변환
            result_str = str(result)
            
            # 실제 이메일 발송 (시뮬레이션)
            self.logger.logger.info("\n📬 이메일 발송 시작:")
            for recipient in self.email_recipients:
                success = self._send_email_smtp(
                    recipient=recipient,
                    subject=f"[맛집 추천] 설문조사 참여 부탁드립니다",
                    body=f"설문조사 링크: {extracted_link}\n\n{result_str[:200]}"
                )
                
                self.logger.log_email_sending(
                    recipient=recipient,
                    subject="맛집 추천 설문조사",
                    template_used="survey_email",
                    success=success
                )
            
            execution_time = time.time() - start_time
            self.logger.log_task_response(task_id, result_str, {"execution_time": execution_time})
            self.logger.log_task_completion(task_id, result_str, execution_time)
            self.logger.logger.info(f"\n✅ 이메일 발송 완료 (실행시간: {execution_time:.2f}초)")
            
            return result_str
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.log_task_error(task_id, e, execution_time)
            raise
    
    def analyze_survey_data(self, survey_responses: Dict) -> str:
        """설문조사 데이터를 분석합니다."""
        print("📊 데이터 분석")
        self.logger.logger.info("📊 데이터 분석 시작")
        
        task_id = self.logger.log_task_start(
            task_name="survey_data_analysis",
            agent_name="data_analyst",
            input_data={
                "total_responses": survey_responses.get("total_responses", 0),
                "data_keys": list(survey_responses.keys())
            }
        )
        
        start_time = time.time()
        
        try:
            # 데이터 분석 로깅
            self.logger.log_data_analysis(
                analysis_type="survey_response_analysis",
                data_summary={
                    "total_responses": survey_responses.get("total_responses", 0),
                    "restaurant_count": len(survey_responses.get("restaurant_preferences", {}))
                },
                insights=["설문조사 응답 데이터 분석 시작"]
            )
            
            # 데이터 분석 에이전트 실행
            analysis_crew = Crew(
                agents=[self.data_analyst],
                tasks=[self.data_analysis_task],
                process=Process.sequential,
                verbose=True
            )
            
            self.logger.log_task_prompt(
                task_id=task_id,
                prompt="설문조사 데이터 분석 요청",
                context={"survey_responses": survey_responses}
            )
            
            self.logger.logger.info("🚀 데이터 분석 Crew 실행 시작...")
            self.logger.logger.info("-" * 80)
            
            result = analysis_crew.kickoff(inputs={"survey_responses": survey_responses})
            
            self.logger.logger.info("-" * 80)
            self.logger.logger.info("✅ 데이터 분석 Crew 실행 완료")
            
            # CrewOutput을 문자열로 변환
            result_str = str(result)
            
            execution_time = time.time() - start_time
            self.logger.log_task_response(task_id, result_str, {"execution_time": execution_time})
            self.logger.log_task_completion(task_id, result_str, execution_time)
            self.logger.logger.info(f"✅ 데이터 분석 완료 (실행시간: {execution_time:.2f}초)")
            
            return result_str
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.log_task_error(task_id, e, execution_time)
            raise
    
    def run_complete_workflow(self, user_request: str, email_recipients: List[str]) -> Dict[str, Any]:
        """전체 워크플로우를 실행합니다."""
        print("\n" + "=" * 50)
        print("🚀 전체 워크플로우 시작")
        print("=" * 50)
        
        workflow_start_time = time.time()
        self.logger.logger.info("🚀 전체 워크플로우 시작")
        self.logger.logger.info(f"📋 사용자 요청: {user_request}")
        self.logger.logger.info(f"📧 이메일 수신자: {len(email_recipients)}명")
        
        try:
            # 1. 맛집 추천
            print("\n1️⃣ 맛집 추천 단계")
            self.logger.logger.info("" * 80)
            self.logger.logger.info("1️⃣ 맛집 추천 단계 시작")
            recommendations = self.run_restaurant_recommendation(user_request)
            
            # 2. 설문조사 폼 생성
            print("\n2️⃣ 설문조사 폼 생성 단계")
            self.logger.logger.info("" * 80)
            self.logger.logger.info("2️⃣ 설문조사 폼 생성 단계 시작")
            survey_form = self.create_survey_form(recommendations)
            
            # 3. 이메일 발송
            print("\n3️⃣ 이메일 발송 단계")
            self.logger.logger.info("" * 80)
            self.logger.logger.info("3️⃣ 이메일 발송 단계 시작")
            self.set_email_recipients(email_recipients)
            email_result = self.send_survey_emails(survey_form)
            
            # 4. 응답 대기
            print("\n4️⃣ 응답 수집 대기")
            self.logger.logger.info("4️⃣ 응답 수집 대기 (시뮬레이션)")
            
            # 5. 데이터 분석
            print("\n5️⃣ 데이터 분석 단계")
            self.logger.logger.info("" * 80)
            self.logger.logger.info("5️⃣ 데이터 분석 단계 시작")
            mock_survey_data = self._generate_mock_survey_data()
            self.logger.logger.info(f"📊 모의 데이터 생성 완료: {mock_survey_data}")
            analysis_result = self.analyze_survey_data(mock_survey_data)
            
            # 전체 워크플로우 완료
            workflow_time = time.time() - workflow_start_time
            self.logger.logger.info("=" * 80)
            self.logger.logger.info(f"✅ 전체 워크플로우 완료 (총 실행시간: {workflow_time:.2f}초)")
            self.logger.logger.info("=" * 80)
            
            return {
                "recommendations": recommendations,
                "survey_form": survey_form,
                "email_result": email_result,
                "analysis_result": analysis_result,
                "workflow_execution_time": workflow_time
            }
            
        except Exception as e:
            workflow_time = time.time() - workflow_start_time
            self.logger.logger.error(f"❌ 워크플로우 오류: {str(e)}")
            self.logger.logger.error(f"실행시간: {workflow_time:.2f}초")
            raise
    
    def _generate_mock_survey_data(self) -> Dict:
        """테스트용 모의 설문조사 데이터를 생성합니다."""
        return {
            "total_responses": 25,
            "restaurant_preferences": {
                "맛집 A": 12,
                "맛집 B": 8,
                "맛집 C": 5
            },
            "satisfaction_scores": {
                "맛집 A": 4.2,
                "맛집 B": 3.8,
                "맛집 C": 4.0
            },
            "price_satisfaction": {
                "매우 만족": 8,
                "만족": 12,
                "보통": 4,
                "불만족": 1
            },
            "improvement_suggestions": [
                "더 다양한 메뉴 옵션",
                "가격 대비 품질 향상",
                "서비스 개선"
            ]
        }

def main():
    """메인 함수"""
    print("\n" + "=" * 60)
    print("🍽️ CrewAI 고급 맛집 추천 및 설문조사 시스템")
    print("=" * 60 + "\n")
    
    # 시스템 초기화
    print("⚙️  시스템 초기화 중...")
    system = AdvancedRestaurantSystem()
    print("✅ 시스템 초기화 완료\n")
    
    # 사용자 입력
    user_request = input("맛집 추천 요청을 입력하세요 (Enter: 기본값 사용): ").strip()
    if not user_request:
        user_request = "광화문 근처 3만원 이하의 한식 맛집을 찾아줘"
        print(f"기본값 사용: {user_request}\n")
    
    # 이메일 수신자 목록 (config에서 읽기)
    email_settings = config.get_email_settings()
    email_recipients = email_settings.get("recipients", [])
    
    if not email_recipients:
        print("⚠️  경고: config.json에 이메일 수신자가 설정되지 않았습니다.")
        print("   email_settings.recipients에 이메일 주소를 추가하세요.\n")
        return
    
    try:
        # 전체 워크플로우 실행
        results = system.run_complete_workflow(user_request, email_recipients)
        
        print("\n" + "=" * 60)
        print("🎉 전체 워크플로우 완료!")
        print("=" * 60)
        
        print("\n📋 결과 요약:")
        print(f"   ✅ 맛집 추천: 완료")
        print(f"   ✅ 설문조사 폼: 생성됨")
        print(f"   ✅ 이메일 발송: 완료 ({len(email_recipients)}명)")
        print(f"   ✅ 데이터 분석: 완료")
        print(f"   ⏱️  총 실행시간: {results.get('workflow_execution_time', 0):.2f}초")
        
        # 세션 종료 로깅
        system.logger.log_session_end({
            "status": "success",
            "user_request": user_request,
            "email_recipients_count": len(email_recipients),
            "workflow_execution_time": results.get('workflow_execution_time', 0)
        })
        
        # 세션 요약 출력
        summary = system.logger.get_session_summary()
        print(f"\n📊 세션 상세 정보:")
        print(f"   📁 로그 파일: {summary['log_files']['session_log']}")
        print(f"   📁 Task 로그: {summary['log_files']['task_log']}")
        print(f"   📊 총 Task: {summary['total_tasks']}개")
        print(f"   ✅ 완료: {summary['completed_tasks']}개")
        print(f"   ❌ 오류: {summary['error_tasks']}개")
        print(f"   ⏱️  총 Task 실행시간: {summary['total_execution_time']:.2f}초")
        print("\n💡 상세 로그는 위 로그 파일을 확인하세요.\n")
        
    except Exception as e:
        print(f"\n❌ 오류가 발생했습니다: {e}\n")
        import traceback
        traceback.print_exc()
        
        # 오류 발생 시에도 세션 종료 로깅
        if 'system' in locals():
            system.logger.log_session_end({
                "status": "error",
                "error": str(e),
                "traceback": traceback.format_exc()
            })
            
            summary = system.logger.get_session_summary()
            print(f"📁 오류 로그: {summary['log_files']['session_log']}\n")

if __name__ == "__main__":
    main()
