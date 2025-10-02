from .base_handler import BaseHandler
from ..utils.advisor_types import AdvisorState
from ..utils.promptManager import YAMLPromptManager
from typing import Dict, Any

class GeneralAdviceHandler(BaseHandler):
    """일반 상담 Handler"""
    
    def __init__(self, model, json_parser):
        self.model = model
        self.json_parser = json_parser
        self.yaml_prompt_manager = YAMLPromptManager()
    
    def can_handle(self, classification: Dict[str, Any]) -> bool:
        return True  # 기본 핸들러로 모든 요청 처리 가능
    
    async def handle(self, state: AdvisorState) -> AdvisorState:
        try:
            question = state["question"]
            prompt = self.yaml_prompt_manager.create_chat_prompt(
                "general_advisor", 
                context="일반적인 상담", 
                question=question
            )
            
            result = (prompt | self.model | self.json_parser).invoke({"question": question})
            formatted_result = self._format_response(result, "general_advice", "general")
            
            return {
                **state, 
                "final_result": formatted_result,
                "handler_name": self.handler_name
            }
        except Exception as e:
            return {**state, "error": f"{self.handler_name}: {str(e)}"}
    
    @property
    def handler_name(self) -> str:
        return "general_advice"