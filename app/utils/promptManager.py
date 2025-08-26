import yaml
import os
from pathlib import Path

class YAMLPromptManager:
    """YAML 프롬프트 파일 관리 클래스"""
    
    def __init__(self, prompts_file="prompts/prompts_list.yaml"):
        self.prompts_file = prompts_file
        self.prompts = self.load_prompts()
    
    def load_prompts(self):
        """YAML 프롬프트 파일 로드"""
        try:
            with open(self.prompts_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"⚠️ 프롬프트 파일을 찾을 수 없습니다: {self.prompts_file}")
            return {}
        except yaml.YAMLError as e:
            print(f"⚠️ YAML 파일 파싱 오류: {e}")
            return {}
    
    def get_prompt(self, prompt_name):
        """특정 프롬프트 가져오기"""
        if prompt_name in self.prompts:
            return self.prompts[prompt_name]
        else:
            print(f"⚠️ '{prompt_name}' 프롬프트를 찾을 수 없습니다.")
            return None
    
    def list_prompts(self):
        """사용 가능한 프롬프트 목록"""
        print("📋 사용 가능한 프롬프트들:")
        for name, details in self.prompts.items():
            print(f"   - {name}: {details.get('description', 'No description')}")
            print(f"     카테고리: {details.get('category', 'Unknown')}")
            print(f"     변수: {details.get('variables', [])}")
            print()
    
    def create_chat_prompt(self, prompt_name, **kwargs):
        """LangChain ChatPromptTemplate 생성"""
        prompt_data = self.get_prompt(prompt_name)
        if not prompt_data:
            return None
        
        from langchain_core.prompts import ChatPromptTemplate
        
        # 프롬프트 텍스트에 변수 값 삽입
        prompt_text = prompt_data["prompt"]
        
        # kwargs로 전달된 변수들 적용
        for key, value in kwargs.items():
            prompt_text = prompt_text.replace(f"{{{key}}}", str(value))
        
        return ChatPromptTemplate.from_messages([
            ("system", prompt_text),
            ("user", "{question}")
        ])

# YAML 프롬프트 매니저 초기화