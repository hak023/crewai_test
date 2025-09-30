"""
고급 로깅 관리 모듈
실행별 로그 파일 생성 및 Task별 상세 로깅을 제공합니다.
"""

import os
import json
import logging
import sys
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path
import threading
from io import StringIO

class LoggingManager:
    """고급 로깅 관리 클래스"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)
        
        # 세션별 로그 파일 경로
        self.session_log_file = self.log_dir / f"session_{self.session_id}.log"
        self.task_log_file = self.log_dir / f"tasks_{self.session_id}.json"
        
        # 로깅 설정
        self.logging_config = config.get("logging", {})
        self.log_level = getattr(logging, self.logging_config.get("level", "INFO"))
        
        # 로거 설정
        self.logger = self._setup_logger()
        self.task_logs = []
        self._lock = threading.Lock()
        
    def _setup_logger(self) -> logging.Logger:
        """파일 로깅을 포함한 로거 설정"""
        logger = logging.getLogger(f"restaurant_system_{self.session_id}")
        logger.setLevel(self.log_level)
        
        # 기존 핸들러 제거
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        # 파일 핸들러 설정
        file_handler = logging.FileHandler(self.session_log_file, encoding='utf-8')
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        # 콘솔 핸들러 설정 (간소화 - print만 표시)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.CRITICAL)  # 콘솔은 중요한 것만
        console_handler.setFormatter(logging.Formatter('%(message)s'))
        logger.addHandler(console_handler)
        
        return logger
    
    def log_session_start(self, system_info: Dict[str, Any]):
        """세션 시작 로깅"""
        self.logger.info("=" * 80)
        self.logger.info(f"🚀 맛집 추천 시스템 세션 시작 - {self.session_id}")
        self.logger.info(f"📊 시스템 정보: {json.dumps(system_info, ensure_ascii=False, indent=2)}")
        self.logger.info("=" * 80)
    
    def log_session_end(self, results: Dict[str, Any]):
        """세션 종료 로깅"""
        self.logger.info("=" * 80)
        self.logger.info(f"🏁 맛집 추천 시스템 세션 종료 - {self.session_id}")
        self.logger.info(f"📈 세션 결과: {json.dumps(results, ensure_ascii=False, indent=2)}")
        self.logger.info("=" * 80)
        
        # Task 로그를 JSON 파일로 저장
        self._save_task_logs()
    
    def log_agent_creation(self, agent_name: str, agent_config: Dict[str, Any]):
        """에이전트 생성 로깅"""
        self.logger.info(f"🤖 에이전트 생성: {agent_name}")
        self.logger.debug(f"에이전트 설정: {json.dumps(agent_config, ensure_ascii=False, indent=2)}")
    
    def log_task_start(self, task_name: str, agent_name: str, input_data: Dict[str, Any]):
        """Task 시작 로깅"""
        task_id = f"{agent_name}_{task_name}_{datetime.now().strftime('%H%M%S')}"
        
        task_log = {
            "task_id": task_id,
            "task_name": task_name,
            "agent_name": agent_name,
            "start_time": datetime.now().isoformat(),
            "input_data": input_data,
            "status": "started"
        }
        
        with self._lock:
            self.task_logs.append(task_log)
        
        self.logger.info(f"📋 Task 시작: {task_name} (Agent: {agent_name})")
        self.logger.debug(f"Task 입력 데이터: {json.dumps(input_data, ensure_ascii=False, indent=2)}")
        
        return task_id
    
    def log_task_prompt(self, task_id: str, prompt: str, context: Dict[str, Any] = None):
        """Task 프롬프트 로깅 - session log에 상세 기록"""
        prompt_log = {
            "timestamp": datetime.now().isoformat(),
            "type": "prompt",
            "prompt": prompt,
            "context": context or {}
        }
        
        with self._lock:
            for task_log in self.task_logs:
                if task_log["task_id"] == task_id:
                    if "interactions" not in task_log:
                        task_log["interactions"] = []
                    task_log["interactions"].append(prompt_log)
                    break
        
        # Session log에 프롬프트 전체 로깅 (상세)
        self.logger.info("\n" + "▼" * 40 + " 프롬프트 " + "▼" * 40)
        self.logger.info(f"🆔 Task ID: {task_id}")
        self.logger.info(f"⏰ 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info("\n💬 프롬프트 내용:")
        self.logger.info("-" * 80)
        self.logger.info(prompt)
        self.logger.info("-" * 80)
        
        if context:
            self.logger.info("\n📋 컨텍스트 정보:")
            self.logger.info("-" * 80)
            for key, value in context.items():
                if isinstance(value, str):
                    if len(value) > 200:
                        self.logger.info(f"  {key}:")
                        self.logger.info(f"    {value[:200]}...")
                        self.logger.info(f"    ... (총 {len(value)}자)")
                    else:
                        self.logger.info(f"  {key}: {value}")
                elif isinstance(value, (list, dict)):
                    self.logger.info(f"  {key}:")
                    self.logger.info(f"    {json.dumps(value, ensure_ascii=False, indent=4)}")
                else:
                    self.logger.info(f"  {key}: {value}")
            self.logger.info("-" * 80)
        
        self.logger.info("▲" * 40 + " 프롬프트 끝 " + "▲" * 40 + "\n")
    
    def log_task_response(self, task_id: str, response: str, metadata: Dict[str, Any] = None):
        """Task 응답 로깅 - session log에 상세 기록"""
        response_log = {
            "timestamp": datetime.now().isoformat(),
            "type": "response",
            "response": response,
            "metadata": metadata or {}
        }
        
        with self._lock:
            for task_log in self.task_logs:
                if task_log["task_id"] == task_id:
                    if "interactions" not in task_log:
                        task_log["interactions"] = []
                    task_log["interactions"].append(response_log)
                    break
        
        # Session log에 응답 전체 로깅 (상세)
        self.logger.info("\n" + "▼" * 40 + " 응답 " + "▼" * 40)
        self.logger.info(f"🆔 Task ID: {task_id}")
        self.logger.info(f"⏰ 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info("\n📥 응답 내용:")
        self.logger.info("-" * 80)
        self.logger.info(response)
        self.logger.info("-" * 80)
        
        if metadata:
            self.logger.info("\n📊 메타데이터:")
            self.logger.info("-" * 80)
            for key, value in metadata.items():
                self.logger.info(f"  {key}: {value}")
            self.logger.info("-" * 80)
        
        self.logger.info("▲" * 40 + " 응답 끝 " + "▲" * 40 + "\n")
    
    def log_task_completion(self, task_id: str, result: Any, execution_time: float):
        """Task 완료 로깅"""
        with self._lock:
            for task_log in self.task_logs:
                if task_log["task_id"] == task_id:
                    task_log["end_time"] = datetime.now().isoformat()
                    task_log["execution_time"] = execution_time
                    task_log["result"] = str(result)[:1000]  # 결과는 1000자로 제한
                    task_log["status"] = "completed"
                    break
        
        self.logger.info(f"✅ Task 완료: {task_id} (실행시간: {execution_time:.2f}초)")
    
    def log_task_error(self, task_id: str, error: Exception, execution_time: float):
        """Task 오류 로깅"""
        with self._lock:
            for task_log in self.task_logs:
                if task_log["task_id"] == task_id:
                    task_log["end_time"] = datetime.now().isoformat()
                    task_log["execution_time"] = execution_time
                    task_log["error"] = str(error)
                    task_log["status"] = "error"
                    break
        
        self.logger.error(f"❌ Task 오류: {task_id} - {str(error)}")
    
    def log_crew_execution(self, crew_name: str, tasks: List[str], process_type: str):
        """크루 실행 로깅"""
        self.logger.info(f"👥 크루 실행: {crew_name}")
        self.logger.info(f"📋 실행할 Task들: {', '.join(tasks)}")
        self.logger.info(f"⚙️ 실행 방식: {process_type}")
    
    def log_api_call(self, api_name: str, endpoint: str, request_data: Dict[str, Any], response_data: Dict[str, Any]):
        """API 호출 로깅"""
        self.logger.info(f"🌐 API 호출: {api_name} - {endpoint}")
        self.logger.debug(f"요청 데이터: {json.dumps(request_data, ensure_ascii=False, indent=2)}")
        self.logger.debug(f"응답 데이터: {json.dumps(response_data, ensure_ascii=False, indent=2)}")
    
    def log_data_analysis(self, analysis_type: str, data_summary: Dict[str, Any], insights: List[str]):
        """데이터 분석 로깅"""
        self.logger.info(f"📊 데이터 분석: {analysis_type}")
        self.logger.info(f"📈 데이터 요약: {json.dumps(data_summary, ensure_ascii=False, indent=2)}")
        self.logger.info(f"💡 주요 인사이트: {insights}")
    
    def log_email_sending(self, recipient: str, subject: str, template_used: str, success: bool):
        """이메일 발송 로깅"""
        status = "성공" if success else "실패"
        self.logger.info(f"📧 이메일 발송 {status}: {recipient}")
        self.logger.info(f"📝 제목: {subject}")
        self.logger.info(f"📄 템플릿: {template_used}")
    
    def _save_task_logs(self):
        """Task 로그를 JSON 파일로 저장"""
        try:
            with open(self.task_log_file, 'w', encoding='utf-8') as f:
                json.dump(self.task_logs, f, ensure_ascii=False, indent=2)
            self.logger.info(f"📁 Task 로그 저장 완료: {self.task_log_file}")
        except Exception as e:
            self.logger.error(f"❌ Task 로그 저장 실패: {str(e)}")
    
    def get_session_summary(self) -> Dict[str, Any]:
        """세션 요약 정보 반환"""
        completed_tasks = len([t for t in self.task_logs if t.get("status") == "completed"])
        error_tasks = len([t for t in self.task_logs if t.get("status") == "error"])
        total_execution_time = sum([t.get("execution_time", 0) for t in self.task_logs])
        
        return {
            "session_id": self.session_id,
            "total_tasks": len(self.task_logs),
            "completed_tasks": completed_tasks,
            "error_tasks": error_tasks,
            "total_execution_time": total_execution_time,
            "log_files": {
                "session_log": str(self.session_log_file),
                "task_log": str(self.task_log_file)
            }
        }

# 전역 로깅 매니저 인스턴스
_logging_manager: Optional[LoggingManager] = None

def get_logging_manager(config: Dict[str, Any]) -> LoggingManager:
    """로깅 매니저 인스턴스 반환"""
    global _logging_manager
    if _logging_manager is None:
        _logging_manager = LoggingManager(config)
    return _logging_manager

def cleanup_logging_manager():
    """로깅 매니저 정리"""
    global _logging_manager
    if _logging_manager:
        _logging_manager._save_task_logs()
        _logging_manager = None
