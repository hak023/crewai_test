"""
설정 파일 관리 모듈
JSON 설정 파일을 로딩하고 환경 변수를 설정합니다.
"""

import os
import sys
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path

# 프로젝트 루트를 Python path에 추가
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

class ConfigManager:
    """설정 파일을 관리하는 클래스"""
    
    def __init__(self, config_file: str = None):
        # config 디렉토리에서 설정 파일 찾기
        if config_file is None:
            self.config_file = str(PROJECT_ROOT / "config" / "config.json")
        else:
            self.config_file = config_file
        self.config = {}
        self.logger = self._setup_logger()
        
    def _setup_logger(self) -> logging.Logger:
        """로거 설정"""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def load_config(self) -> bool:
        """설정 파일을 로딩합니다."""
        try:
            if not os.path.exists(self.config_file):
                self.logger.warning(f"설정 파일이 없습니다: {self.config_file}")
                self.logger.info("config/config_example.json을 참고하여 config/config.json을 생성하세요.")
                return False
            
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            
            self.logger.info(f"설정 파일 로딩 완료: {self.config_file}")
            return True
            
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON 파싱 오류: {e}")
            return False
        except Exception as e:
            self.logger.error(f"설정 파일 로딩 오류: {e}")
            return False
    
    def setup_environment(self) -> bool:
        """환경 변수를 설정합니다."""
        try:
            if not self.config:
                self.logger.error("설정이 로딩되지 않았습니다.")
                return False
            
            # API 키 설정 (LLM provider에 따라)
            api_keys = self.config.get('api_keys', {})
            system_settings = self.config.get('system_settings', {})
            llm_provider = system_settings.get('llm_provider', 'gemini')
            
            for key, value in api_keys.items():
                # LLM provider에 따라 필요한 키만 설정
                should_set = True
                
                # OpenAI 키는 provider가 openai일 때만 설정
                if key == 'openai_api_key' and llm_provider != 'openai':
                    should_set = False
                    self.logger.info(f"OpenAI 사용 안 함 - OPENAI_API_KEY 환경 변수 설정 생략")
                
                if should_set and value and value != f"your-{key}-here":
                    os.environ[key.upper()] = value
                    self.logger.info(f"환경 변수 설정: {key.upper()}")
                    
                    # Gemini API 키를 GOOGLE_API_KEY로도 설정
                    if key == 'gemini_api_key':
                        os.environ['GOOGLE_API_KEY'] = value
                        self.logger.info("환경 변수 설정: GOOGLE_API_KEY")
                elif not value or value == f"your-{key}-here":
                    if should_set:
                        self.logger.warning(f"API 키가 설정되지 않았습니다: {key}")
            
            # Google 자격 증명 설정
            google_creds = self.config.get('google_credentials', {})
            if google_creds.get('credentials_file'):
                creds_file = google_creds['credentials_file']
                if os.path.exists(creds_file):
                    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = creds_file
                    self.logger.info(f"Google 자격 증명 설정: {creds_file}")
                else:
                    self.logger.warning(f"Google 자격 증명 파일을 찾을 수 없습니다: {creds_file}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"환경 변수 설정 오류: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """설정 값을 가져옵니다."""
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def get_api_key(self, service: str) -> Optional[str]:
        """특정 서비스의 API 키를 가져옵니다."""
        api_keys = self.config.get('api_keys', {})
        key_name = f"{service}_api_key"
        return api_keys.get(key_name)
    
    def get_system_settings(self) -> Dict[str, Any]:
        """시스템 설정을 가져옵니다."""
        return self.config.get('system_settings', {})
    
    def get_restaurant_settings(self) -> Dict[str, Any]:
        """맛집 추천 설정을 가져옵니다."""
        return self.config.get('restaurant_settings', {})
    
    def get_survey_settings(self) -> Dict[str, Any]:
        """설문조사 설정을 가져옵니다."""
        return self.config.get('survey_settings', {})
    
    def get_email_settings(self) -> Dict[str, Any]:
        """이메일 설정을 가져옵니다."""
        return self.config.get('email_settings', {})
    
    def get_data_analysis_settings(self) -> Dict[str, Any]:
        """데이터 분석 설정을 가져옵니다."""
        return self.config.get('data_analysis', {})
    
    def validate_config(self) -> bool:
        """설정 파일의 유효성을 검사합니다."""
        required_sections = ['api_keys', 'system_settings', 'restaurant_settings']
        
        for section in required_sections:
            if section not in self.config:
                self.logger.error(f"필수 설정 섹션이 없습니다: {section}")
                return False
        
        # API 키 검증 (Gemini 사용 시)
        api_keys = self.config.get('api_keys', {})
        system_settings = self.config.get('system_settings', {})
        llm_provider = system_settings.get('llm_provider', 'gemini')
        
        # LLM provider에 따라 필수 키 확인
        if llm_provider == 'gemini':
            if not api_keys.get('gemini_api_key') or api_keys.get('gemini_api_key') == 'your-gemini-api-key-here':
                self.logger.warning(f"필수 API 키가 설정되지 않았습니다: gemini_api_key")
        elif llm_provider == 'openai':
            if not api_keys.get('openai_api_key') or api_keys.get('openai_api_key') == 'your-openai-api-key-here':
                self.logger.warning(f"필수 API 키가 설정되지 않았습니다: openai_api_key")
        
        return True
    
    def create_example_config(self) -> bool:
        """예시 설정 파일을 생성합니다."""
        try:
            example_file = "config_example.json"
            if os.path.exists(example_file):
                with open(example_file, 'r', encoding='utf-8') as f:
                    example_config = json.load(f)
                
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    json.dump(example_config, f, indent=2, ensure_ascii=False)
                
                self.logger.info(f"예시 설정 파일 생성: {self.config_file}")
                return True
            else:
                self.logger.error(f"예시 설정 파일을 찾을 수 없습니다: {example_file}")
                return False
                
        except Exception as e:
            self.logger.error(f"예시 설정 파일 생성 오류: {e}")
            return False

def load_config(config_file: str = None) -> Optional[ConfigManager]:
    """설정을 로딩하고 환경을 설정합니다."""
    config_manager = ConfigManager(config_file)
    
    if config_manager.load_config():
        if config_manager.setup_environment():
            if config_manager.validate_config():
                return config_manager
            else:
                print("⚠️  설정 파일에 문제가 있습니다. config_example.json을 참고하여 수정하세요.")
                return config_manager
        else:
            print("❌ 환경 변수 설정에 실패했습니다.")
            return None
    else:
        print("❌ 설정 파일을 로딩할 수 없습니다.")
        return None

if __name__ == "__main__":
    # 설정 파일 테스트
    config = load_config()
    if config:
        print("✅ 설정 로딩 성공")
        print(f"OpenAI API 키: {config.get_api_key('openai')[:10]}..." if config.get_api_key('openai') else "❌ 설정되지 않음")
        print(f"시스템 설정: {config.get_system_settings()}")
    else:
        print("❌ 설정 로딩 실패")
