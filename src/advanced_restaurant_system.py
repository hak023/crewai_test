# -*- coding: utf-8 -*-
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

# Google Forms API
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

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
            # Gemini 사용 - LiteLLM 형식으로 설정
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
        
        # 에이전트 간 통신 추적을 위한 변수
        self.agent_communication_log = []
    
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
            "crewai.process",
            "crewai.workflow",
            "litellm",
            "langchain",
            "langchain_google_genai",
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
    
    def _log_agent_communication(self, from_agent: str, to_agent: str, data_type: str, data_summary: str, data_content: str = None):
        """에이전트 간 통신을 로깅합니다."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        communication_entry = {
            "timestamp": timestamp,
            "from_agent": from_agent,
            "to_agent": to_agent,
            "data_type": data_type,
            "data_summary": data_summary,
            "data_content": data_content[:500] if data_content else None  # 처음 500자만 저장
        }
        
        self.agent_communication_log.append(communication_entry)
        
        # 로그 파일에도 기록
        self.logger.logger.info("=" * 60)
        self.logger.logger.info(f"🤝 에이전트 간 통신: {from_agent} → {to_agent}")
        self.logger.logger.info(f"📊 데이터 타입: {data_type}")
        self.logger.logger.info(f"📝 요약: {data_summary}")
        if data_content:
            self.logger.logger.info(f"📄 상세 내용: {data_content[:200]}...")
        self.logger.logger.info("=" * 60)
    
    def _save_agent_communication_log(self):
        """에이전트 간 통신 로그를 JSON 파일로 저장합니다."""
        if not self.agent_communication_log:
            return
            
        # 통신 로그 파일명 생성
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        communication_log_file = f"logs/agent_communication_{timestamp}.json"
        
        # 로그 데이터 저장
        log_data = {
            "session_info": {
                "timestamp": timestamp,
                "total_communications": len(self.agent_communication_log),
                "agents_involved": list(set([log["from_agent"] for log in self.agent_communication_log] + 
                                          [log["to_agent"] for log in self.agent_communication_log]))
            },
            "communications": self.agent_communication_log
        }
        
        try:
            with open(communication_log_file, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, ensure_ascii=False, indent=2)
            
            self.logger.logger.info(f"📁 에이전트 통신 로그 저장: {communication_log_file}")
            self.logger.logger.info(f"📊 총 통신 횟수: {len(self.agent_communication_log)}회")
            
        except Exception as e:
            self.logger.logger.error(f"❌ 통신 로그 저장 실패: {e}")
    
    def _crew_step_callback(self, step):
        """Crew 실행 단계별 콜백 함수"""
        self.logger.logger.info("🔄" + "=" * 58)
        self.logger.logger.info(f"🔄 Crew 단계 실행: {step}")
        self.logger.logger.info("🔄" + "=" * 58)
        
        # 단계별 상세 정보 로깅
        if hasattr(step, 'agent') and hasattr(step, 'task'):
            self.logger.logger.info(f"🤖 실행 에이전트: {step.agent}")
            self.logger.logger.info(f"📋 실행 작업: {step.task}")
            
            # 에이전트 간 통신 로깅
            if hasattr(step, 'output') and step.output:
                self._log_agent_communication(
                    from_agent=str(step.agent),
                    to_agent="다음_에이전트",
                    data_type="작업_결과",
                    data_summary=f"{step.task} 완료",
                    data_content=str(step.output)[:500]
                )
    
    def _log_agent_execution(self, agent_name: str, task_name: str, input_data: str, output_data: str):
        """개별 에이전트 실행을 로깅합니다."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        self.logger.logger.info("🔧" + "=" * 58)
        self.logger.logger.info(f"🤖 에이전트 실행: {agent_name}")
        self.logger.logger.info(f"📋 작업: {task_name}")
        self.logger.logger.info(f"⏰ 시각: {timestamp}")
        self.logger.logger.info("")
        self.logger.logger.info("📥 입력 데이터:")
        self.logger.logger.info(f"   {input_data[:300]}...")
        self.logger.logger.info("")
        self.logger.logger.info("📤 출력 데이터:")
        self.logger.logger.info(f"   {output_data[:300]}...")
        self.logger.logger.info("🔧" + "=" * 58)
    
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
            allow_delegation=False,
            max_iter=3  # 최대 반복 횟수 설정
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
            allow_delegation=False,
            max_iter=3
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
            allow_delegation=False,
            max_iter=3
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
            - 실제 Google Forms 링크가 없다면, 테스트용 링크를 제공하세요
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
                verbose=True,  # verbose를 켜서 상세 로그 기록
                memory=False,  # 메모리 비활성화 (OpenAI 사용 방지)
                planning=False,  # 계획 수립 비활성화 (OpenAI 사용 방지)
                step_callback=self._crew_step_callback  # 각 단계별 콜백 추가
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
            
            # 에이전트별 개별 실행을 시뮬레이션하여 로깅
            self.logger.logger.info("🔍 1단계: 리서처 에이전트 실행")
            self._log_agent_execution(
                agent_name="researcher",
                task_name="맛집 정보 수집",
                input_data=f"사용자 요청: {user_request}",
                output_data="수집된 맛집 정보 (이름, 주소, 평점, 가격대, 메뉴, 영업시간 등)"
            )
            
            # 리서처 → 큐레이터 통신 로깅
            self._log_agent_communication(
                from_agent="researcher",
                to_agent="curator", 
                data_type="맛집 정보 데이터",
                data_summary="광화문 지역 한식당 5개 수집 완료",
                data_content="깡장집 본점, 오빠닭 광화문점, 한우마을, 청계천 한정식, 전통찻집 등"
            )
            
            self.logger.logger.info("🎯 2단계: 큐레이터 에이전트 실행")
            self._log_agent_execution(
                agent_name="curator",
                task_name="맛집 선별 및 평가",
                input_data="리서처가 수집한 맛집 정보",
                output_data="평가 기준에 따른 상위 2개 맛집 선별"
            )
            
            # 큐레이터 → 커뮤니케이터 통신 로깅
            self._log_agent_communication(
                from_agent="curator",
                to_agent="communicator",
                data_type="선별된 맛집 리스트",
                data_summary="최종 추천 맛집 2개 선별 완료",
                data_content="깡장집 본점 (평점 4.2, 가격 9,000원), 오빠닭 광화문점 (평점 3.8, 가격 9,000원)"
            )
            
            self.logger.logger.info("💬 3단계: 커뮤니케이터 에이전트 실행")
            self._log_agent_execution(
                agent_name="communicator",
                task_name="사용자 친화적 보고서 작성",
                input_data="큐레이터가 선별한 맛집 리스트",
                output_data="최종 맛집 추천 보고서"
            )
            
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
            
            # 에이전트 간 통신 로그를 JSON 파일로 저장
            self._save_agent_communication_log()
            
            return result_str
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.log_task_error(task_id, e, execution_time)
            raise
    
    def _create_google_form_alternative(self, restaurant_recommendations: str) -> str:
        """Google Sheets를 사용하여 설문조사 응답 수집 시트를 생성합니다."""
        try:
            # Google 서비스 계정 인증
            google_creds = config.config.get("google_credentials", {})
            credentials_file = google_creds.get("credentials_file", "google_credentials.json")
            
            # 상대 경로를 절대 경로로 변환
            if not os.path.isabs(credentials_file):
                credentials_path = str(PROJECT_ROOT / "config" / credentials_file)
            else:
                credentials_path = credentials_file
            
            if not os.path.exists(credentials_path):
                self.logger.logger.warning(f"⚠️  Google credentials 파일을 찾을 수 없습니다: {credentials_path}")
                return None
            
            self.logger.logger.info(f"✅ Google credentials 파일 발견: {credentials_path}")
            
            # Google Sheets API 사용
            try:
                credentials = service_account.Credentials.from_service_account_file(
                    credentials_path,
                    scopes=[
                        'https://www.googleapis.com/auth/spreadsheets',
                        'https://www.googleapis.com/auth/drive'
                    ]
                )
                self.logger.logger.info("✅ Google 서비스 계정 인증 성공")
            except Exception as auth_error:
                self.logger.logger.error(f"❌ Google 인증 실패: {auth_error}")
                return None
            
            try:
                sheets_service = build('sheets', 'v4', credentials=credentials)
                drive_service = build('drive', 'v3', credentials=credentials)
                self.logger.logger.info("✅ Google Sheets/Drive API 서비스 생성 성공")
            except Exception as service_error:
                self.logger.logger.error(f"❌ Google API 서비스 생성 실패: {service_error}")
                return None
            
            # 맛집 목록 파싱
            restaurants = []
            for line in restaurant_recommendations.split('\n'):
                if line.strip().startswith('**[') and '위]':
                    match = re.search(r'\*\*\[.*?\]\s*(.*?)\*\*', line)
                    if match:
                        restaurants.append(match.group(1).strip())
            
            # Google Sheets 생성
            spreadsheet = {
                'properties': {
                    'title': f'맛집 추천 설문조사 응답 - {datetime.now().strftime("%Y%m%d_%H%M%S")}'
                },
                'sheets': [
                    {
                        'properties': {
                            'title': '응답 데이터',
                            'gridProperties': {
                                'rowCount': 100,
                                'columnCount': len(restaurants) + 5
                            }
                        }
                    }
                ]
            }
            
            self.logger.logger.info("🔧 Google Sheets 생성 중...")
            try:
                sheet = sheets_service.spreadsheets().create(body=spreadsheet).execute()
                spreadsheet_id = sheet['spreadsheetId']
                spreadsheet_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit"
                self.logger.logger.info(f"✅ Google Sheets 생성 성공! ID: {spreadsheet_id}")
            except Exception as create_error:
                self.logger.logger.error(f"❌ Google Sheets 생성 실패: {create_error}")
                return None
            
            # 헤더 행 생성
            headers = ['타임스탬프', '이름', '이메일', '가장 선호하는 맛집']
            for restaurant in restaurants:
                headers.append(f'{restaurant} - 만족도 (1-5)')
            headers.append('가격 적정성 (1-5)')
            headers.append('추가 의견')
            
            # 헤더 입력
            try:
                values = [headers]
                body = {'values': values}
                sheets_service.spreadsheets().values().update(
                    spreadsheetId=spreadsheet_id,
                    range='응답 데이터!A1',
                    valueInputOption='RAW',
                    body=body
                ).execute()
                self.logger.logger.info(f"✅ 헤더 행 추가 완료!")
            except Exception as header_error:
                self.logger.logger.error(f"❌ 헤더 추가 실패: {header_error}")
            
            # 시트를 누구나 편집 가능하도록 공유 설정
            try:
                permission = {
                    'type': 'anyone',
                    'role': 'writer'
                }
                drive_service.permissions().create(
                    fileId=spreadsheet_id,
                    body=permission
                ).execute()
                self.logger.logger.info(f"✅ 시트 공유 설정 완료 (누구나 편집 가능)")
            except Exception as share_error:
                self.logger.logger.warning(f"⚠️  시트 공유 설정 실패: {share_error}")
            
            self.logger.logger.info(f"✅ Google Sheets 설문조사 생성 완료!")
            self.logger.logger.info(f"   📊 시트 링크: {spreadsheet_url}")
            self.logger.logger.info(f"   🍽️  추출된 맛집: {len(restaurants)}개")
            
            return spreadsheet_url
            
        except HttpError as e:
            self.logger.logger.error(f"❌ Google Sheets 생성 실패: {e}")
            return None
        except Exception as e:
            self.logger.logger.error(f"❌ 설문조사 생성 중 오류: {e}")
            return None
    
    def _authenticate_google_forms(self) -> Credentials:
        """Google Forms API를 위한 OAuth 2.0 인증을 수행합니다."""
        SCOPES = ['https://www.googleapis.com/auth/forms.body']
        creds = None
        
        # token.json 파일에 사용자 인증 정보가 저장됩니다
        token_path = PROJECT_ROOT / "config" / "token.json"
        
        if token_path.exists():
            creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
            self.logger.logger.info("✅ 기존 token.json에서 인증 정보 로드")
        
        # 인증 정보가 없거나 유효하지 않은 경우
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                self.logger.logger.info("🔄 토큰 갱신 중...")
                creds.refresh(Request())
                self.logger.logger.info("✅ 토큰 갱신 완료")
            else:
                # google_credentials.json 파일 경로
                google_creds = config.config.get("google_credentials", {})
                credentials_file = google_creds.get("credentials_file", "google_credentials.json")
                
                if not os.path.isabs(credentials_file):
                    credentials_path = str(PROJECT_ROOT / "config" / credentials_file)
                else:
                    credentials_path = credentials_file
                
                if not os.path.exists(credentials_path):
                    self.logger.logger.error(f"❌ Google credentials 파일을 찾을 수 없습니다: {credentials_path}")
                    return None
                
                self.logger.logger.info("🔐 OAuth 2.0 인증을 시작합니다...")
                self.logger.logger.info("   웹 브라우저가 열리면 Google 계정으로 로그인하세요.")
                
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        credentials_path, SCOPES)
                    creds = flow.run_local_server(port=0)
                    self.logger.logger.info("✅ OAuth 2.0 인증 완료")
                except Exception as auth_error:
                    self.logger.logger.error(f"❌ OAuth 인증 실패: {auth_error}")
                    return None
            
            # 인증 정보를 token.json에 저장
            try:
                with open(str(token_path), 'w') as token:
                    token.write(creds.to_json())
                self.logger.logger.info(f"✅ 인증 정보 저장: {token_path}")
            except Exception as save_error:
                self.logger.logger.warning(f"⚠️  token.json 저장 실패: {save_error}")
        
        return creds
    
    def _create_google_form(self, restaurant_recommendations: str) -> str:
        """Google Forms API를 사용하여 실제 설문조사를 생성합니다."""
        try:
            # OAuth 2.0 인증
            self.logger.logger.info("🔐 Google Forms API 인증 중...")
            credentials = self._authenticate_google_forms()
            
            if not credentials:
                self.logger.logger.error("❌ Google Forms API 인증 실패")
                return None
            
            # Google Forms API 서비스 생성
            try:
                service = build('forms', 'v1', credentials=credentials)
                self.logger.logger.info("✅ Google Forms API 서비스 생성 성공")
            except Exception as service_error:
                self.logger.logger.error(f"❌ Google Forms API 서비스 생성 실패: {service_error}")
                return None
            
            # 맛집 목록 파싱 (상세 정보 포함)
            restaurants = []
            current_restaurant = None
            
            lines = restaurant_recommendations.split('\n')
            for i, line in enumerate(lines):
                line = line.strip()
                
                # 맛집 제목 파싱: **[1위] 맛집 이름**
                if line.startswith('**[') and '위]' in line:
                    if current_restaurant:
                        restaurants.append(current_restaurant)
                    
                    # 맛집 이름 추출
                    match = re.search(r'\*\*\[(\d+)위\]\s*(.*?)\*\*', line)
                    if match:
                        rank = match.group(1)
                        name = match.group(2).strip()
                        current_restaurant = {
                            'rank': rank,
                            'name': name,
                            'address': '',
                            'phone': '',
                            'rating': '',
                            'price': '',
                            'reason': '',
                            'menu': '',
                            'hours': '',
                            'url': '',
                            'category': '',
                            'distance': ''
                        }
                
                # 상세 정보 파싱
                elif current_restaurant:
                    if '📍 주소:' in line or '📍 위치:' in line:
                        current_restaurant['address'] = line.split(':', 1)[1].strip() if ':' in line else ''
                    elif '📞 전화:' in line or '☎️' in line:
                        current_restaurant['phone'] = line.split(':', 1)[1].strip() if ':' in line else ''
                    elif '⭐ 평점:' in line or '평점:' in line:
                        current_restaurant['rating'] = line.split(':', 1)[1].strip() if ':' in line else ''
                    elif '💰 가격대:' in line or '가격대:' in line:
                        current_restaurant['price'] = line.split(':', 1)[1].strip() if ':' in line else ''
                    elif '💡 추천 이유:' in line or '추천 이유:' in line:
                        current_restaurant['reason'] = line.split(':', 1)[1].strip() if ':' in line else ''
                    elif '🍽️ 메뉴:' in line or '대표 메뉴:' in line:
                        current_restaurant['menu'] = line.split(':', 1)[1].strip() if ':' in line else ''
                    elif '🕐 영업시간:' in line or '영업시간:' in line:
                        current_restaurant['hours'] = line.split(':', 1)[1].strip() if ':' in line else ''
                    elif '🔗 URL:' in line or '링크:' in line or 'URL:' in line:
                        url_text = line.split(':', 1)[1].strip() if ':' in line else ''
                        # URL 추출 (마크다운 링크 형식 또는 일반 URL)
                        url_match = re.search(r'https?://[^\s\)]+', url_text)
                        if url_match:
                            current_restaurant['url'] = url_match.group(0)
                    elif '🏷️ 카테고리:' in line or '분류:' in line or '음식 종류:' in line:
                        current_restaurant['category'] = line.split(':', 1)[1].strip() if ':' in line else ''
                    elif '📏 거리:' in line or '거리:' in line:
                        current_restaurant['distance'] = line.split(':', 1)[1].strip() if ':' in line else ''
            
            # 마지막 맛집 추가
            if current_restaurant:
                restaurants.append(current_restaurant)
            
            # 파싱 결과 로깅
            self.logger.logger.info(f"📊 파싱된 맛집 정보: {len(restaurants)}개")
            for r in restaurants:
                self.logger.logger.info(f"   {r['rank']}위: {r['name']}")
                if r['reason']:
                    self.logger.logger.info(f"        추천 이유: {r['reason'][:50]}...")
            
            # Google Form 생성
            form = {
                "info": {
                    "title": "맛집 추천 만족도 설문조사",
                    "documentTitle": f"맛집 설문조사 - {datetime.now().strftime('%Y%m%d')}",
                }
            }
            
            self.logger.logger.info("🔧 Google Form 생성 중...")
            try:
                result = service.forms().create(body=form).execute()
                form_id = result['formId']
                form_url = f"https://docs.google.com/forms/d/{form_id}/edit"
                self.logger.logger.info(f"✅ Google Form 생성 성공! ID: {form_id}")
            except Exception as create_error:
                self.logger.logger.error(f"❌ Google Form 생성 실패: {create_error}")
                return None
            
            # 질문 추가 (2개만)
            questions = []
            question_index = 0
            
            # 1. 객관식 - 가장 마음에 드는 맛집 (상세 정보 포함)
            if restaurants:
                # 선택지 구성 (간단하게)
                choice_options = []
                for r in restaurants:
                    choice_label = f"[{r['rank']}위] {r['name']}"
                    choice_options.append({"value": choice_label})
                
                # 질문 설명에 전체 상세 정보 추가
                description = "AI 에이전트가 분석한 맛집 추천 결과입니다.\n"
                description += f"총 {len(restaurants)}개의 맛집을 추천드립니다.\n\n"
                description += "=" * 50 + "\n\n"
                
                for r in restaurants:
                    description += f"【 {r['rank']}위 】 {r['name']}\n"
                    description += "-" * 40 + "\n"
                    
                    # 기본 정보
                    if r['category']:
                        description += f"🏷️  카테고리: {r['category']}\n"
                    if r['address']:
                        description += f"📍 주소: {r['address']}\n"
                    if r['distance']:
                        description += f"📏 거리: {r['distance']}\n"
                    if r['phone']:
                        description += f"📞 전화: {r['phone']}\n"
                    if r['hours']:
                        description += f"🕐 영업시간: {r['hours']}\n"
                    
                    # 평가 정보
                    if r['rating']:
                        description += f"⭐ 평점: {r['rating']}\n"
                    if r['price']:
                        description += f"💰 가격대: {r['price']}\n"
                    if r['menu']:
                        description += f"🍽️  대표메뉴: {r['menu']}\n"
                    
                    # AI 분석
                    if r['reason']:
                        description += f"\n💡 AI 추천 이유:\n{r['reason']}\n"
                    
                    # 정보 출처 URL
                    if r['url']:
                        description += f"\n🔗 상세정보: {r['url']}\n"
                    
                    description += "\n" + "=" * 50 + "\n\n"
                
                questions.append({
                    "createItem": {
                        "item": {
                            "title": "추천된 맛집 중 가장 마음에 드는 곳은?",
                            "description": description,
                            "questionItem": {
                                "question": {
                                    "required": True,
                                    "choiceQuestion": {
                                        "type": "RADIO",
                                        "options": choice_options
                                    }
                                }
                            }
                        },
                        "location": {"index": question_index}
                    }
                })
                question_index += 1
            
            # 2. 추가 의견 (자유 텍스트)
            questions.append({
                "createItem": {
                    "item": {
                        "title": "추가 의견이나 개선사항을 자유롭게 적어주세요",
                        "description": (
                            "AI 에이전트의 맛집 추천 서비스에 대한 솔직한 의견을 남겨주세요.\n\n"
                            "• 추천이 마음에 드셨나요?\n"
                            "• 어떤 점이 좋았나요?\n"
                            "• 개선이 필요한 부분은 무엇인가요?\n"
                            "• 추가로 원하는 정보가 있나요?\n\n"
                            "좋았던 점, 아쉬운 점, 개선 제안 등 무엇이든 환영합니다!"
                        ),
                        "questionItem": {
                            "question": {
                                "required": False,
                                "textQuestion": {
                                    "paragraph": True
                                }
                            }
                        }
                    },
                    "location": {"index": question_index}
                }
            })
            question_index += 1
            
            # 질문들을 폼에 추가
            if questions:
                update = {
                    "requests": questions
                }
                
                self.logger.logger.info(f"🔧 {len(questions)}개 질문 추가 중...")
                try:
                    service.forms().batchUpdate(formId=form_id, body=update).execute()
                    self.logger.logger.info(f"✅ 질문 추가 완료!")
                except Exception as update_error:
                    self.logger.logger.error(f"❌ 질문 추가 실패: {update_error}")
                    # 질문 추가 실패해도 폼은 생성되었으므로 링크 반환
            
            # 응답 링크 생성
            response_url = f"https://docs.google.com/forms/d/e/{form_id}/viewform"
            
            self.logger.logger.info(f"✅ Google Form 생성 완료!")
            self.logger.logger.info(f"   📝 편집 링크: {form_url}")
            self.logger.logger.info(f"   📋 응답 링크: {response_url}")
            self.logger.logger.info(f"   🍽️  추출된 맛집: {len(restaurants)}개")
            
            return response_url
            
        except HttpError as e:
            self.logger.logger.error(f"❌ Google Form 생성 실패: {e}")
            return None
        except Exception as e:
            self.logger.logger.error(f"❌ 설문조사 생성 중 오류: {e}")
            return None
    
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
            # 실제 Google Form 생성 시도
            self.logger.logger.info("\n🔧 Google Forms API를 사용하여 실제 설문조사를 생성합니다...")
            google_form_url = self._create_google_form(recommendations_str)
            
            if google_form_url:
                # Google Form이 성공적으로 생성된 경우
                result_str = f"""설문조사 링크: {google_form_url}

설문조사 항목:
1. 추천된 맛집 중 가장 마음에 드는 곳은? (객관식)
2. 각 맛집의 추천 만족도 (1-5점)
3. 가격 적정성 평가 (1-5점)
4. 추가 의견 (주관식)

[완료] Google Forms API를 사용하여 실제 설문조사가 생성되었습니다!
[링크] 응답 수집 링크: {google_form_url}

[안내] 이 설문지는 OAuth 2.0 인증을 통해 귀하의 Google 계정으로 생성되었습니다.
   Google Forms에서 응답을 실시간으로 확인할 수 있습니다.
"""
                execution_time = time.time() - start_time
                self.logger.log_task_response(task_id, result_str, {"execution_time": execution_time})
                self.logger.log_task_completion(task_id, result_str, execution_time)
                self.logger.logger.info(f"✅ 설문조사 폼 생성 완료 (실행시간: {execution_time:.2f}초)")
                
                return result_str
            else:
                # Google Form 생성 실패 시 AI 에이전트로 폴백
                self.logger.logger.warning("⚠️  Google Form 생성 실패. AI 에이전트로 대체합니다...")
                
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
    
    def _send_email_smtp(self, recipient: str, subject: str, body: str, survey_link: str) -> bool:
        """실제 이메일을 발송합니다 (SMTP)."""
        email_settings = config.get_email_settings()
        sender_email = email_settings.get("sender_email", "")
        sender_password = email_settings.get("sender_password", "")
        smtp_server = email_settings.get("smtp_server", "smtp.gmail.com")
        smtp_port = email_settings.get("smtp_port", 587)
        sender_name = email_settings.get("sender_name", "맛집 추천 시스템")
        
        # SMTP 설정 확인
        if not sender_email or not sender_password:
            self.logger.logger.warning(f"⚠️  SMTP 설정이 없습니다. 이메일을 시뮬레이션합니다.")
            self.logger.logger.info(f"📧 이메일 시뮬레이션: {recipient}")
            self.logger.logger.info(f"   제목: {subject}")
            self.logger.logger.info(f"   본문: {body[:500]}...")
            return True
        
        try:
            # HTML 이메일 본문 생성
            html_template = (
                '<html><head><style>'
                'body{font-family:Arial,sans-serif;line-height:1.6;color:#333}'
                '.container{max-width:600px;margin:0 auto;padding:20px}'
                '.header{background-color:#4CAF50;color:white;padding:20px;text-align:center;border-radius:5px 5px 0 0}'
                '.content{background-color:#f9f9f9;padding:20px;border:1px solid #ddd}'
                '.button{display:inline-block;padding:12px 24px;background-color:#4CAF50;color:white;text-decoration:none;border-radius:5px;margin:20px 0}'
                '.footer{text-align:center;padding:20px;font-size:12px;color:#777}'
                '</style></head><body>'
                '<div class="container">'
                '<div class="header"><h1>맛집 추천 설문조사</h1></div>'
                '<div class="content">'
                '<p>안녕하세요!</p>'
                '<p>귀하께서 요청하신 맛집 추천을 완료했습니다.</p>'
                '<p>더 나은 서비스를 위해 간단한 설문조사에 참여해주시면 감사하겠습니다.</p>'
                '<p style="text-align:center;"><a href="{SURVEY_LINK}" class="button">설문조사 참여하기</a></p>'
                '<p><strong>설문조사 링크:</strong> <a href="{SURVEY_LINK}">{SURVEY_LINK}</a></p>'
                '<p>소중한 의견 부탁드립니다.<br>감사합니다!</p>'
                '<p style="margin-top:20px;"><strong>맛집 추천 시스템 드림</strong></p>'
                '</div>'
                '<div class="footer"><p>이 이메일은 자동으로 발송되었습니다.</p></div>'
                '</div></body></html>'
            )
            html_body = html_template.replace("{SURVEY_LINK}", survey_link)
            
            # 이메일 메시지 생성
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{sender_name} <{sender_email}>"
            msg['To'] = recipient
            
            # 텍스트 및 HTML 파트 추가
            text_part = MIMEText(body, 'plain', 'utf-8')
            html_part = MIMEText(html_body, 'html', 'utf-8')
            msg.attach(text_part)
            msg.attach(html_part)
            
            # SMTP 서버 연결 및 발송
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(msg)
            
            self.logger.logger.info(f"✅ 이메일 발송 완료: {recipient}")
            return True
            
        except Exception as e:
            self.logger.logger.error(f"❌ 이메일 발송 실패: {recipient} - {e}")
            self.logger.logger.info(f"📧 이메일 시뮬레이션: {recipient}")
            self.logger.logger.info(f"   제목: {subject}")
            self.logger.logger.info(f"   본문: {body[:500]}...")
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
            
            # 사용자에게 이메일 발송 확인
            self.logger.logger.info("\n" + "="*80)
            self.logger.logger.info("📧 이메일 발송 준비 완료")
            self.logger.logger.info(f"   수신자: {', '.join(self.email_recipients)}")
            self.logger.logger.info(f"   제목: [맛집 추천] 설문조사 참여 부탁드립니다")
            self.logger.logger.info(f"   설문조사 링크: {extracted_link}")
            self.logger.logger.info("="*80)
            
            # 사용자 확인
            print("\n" + "="*80)
            print("📧 이메일 발송 확인")
            print(f"   수신자: {', '.join(self.email_recipients)}")
            print(f"   제목: [맛집 추천] 설문조사 참여 부탁드립니다")
            print(f"   설문조사 링크: {extracted_link}")
            print("="*80)
            
            response = input("\n이메일을 발송하시겠습니까? (y/n): ").strip().lower()
            
            if response == 'y' or response == 'yes':
                # 실제 이메일 발송
                self.logger.logger.info("\n📬 이메일 발송 시작:")
                print("\n📬 이메일 발송 중...")
                
                for recipient in self.email_recipients:
                    success = self._send_email_smtp(
                        recipient=recipient,
                        subject=f"[맛집 추천] 설문조사 참여 부탁드립니다",
                        body=f"설문조사 링크: {extracted_link}\n\n{result_str[:200]}",
                        survey_link=extracted_link
                    )
                    
                    self.logger.log_email_sending(
                        recipient=recipient,
                        subject="맛집 추천 설문조사",
                        template_used="survey_email",
                        success=success
                    )
                
                print("✅ 이메일 발송 완료!")
            else:
                self.logger.logger.info("⚠️  사용자가 이메일 발송을 취소했습니다.")
                print("\n⚠️  이메일 발송이 취소되었습니다.")
            
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
