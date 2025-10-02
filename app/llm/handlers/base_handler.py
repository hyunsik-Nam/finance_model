from abc import ABC, abstractmethod
from typing import Dict, Any
from ..utils.advisor_types import AdvisorState

class BaseHandler(ABC):
    """Handler 기본 인터페이스"""
    
    @abstractmethod
    def can_handle(self, classification: Dict[str, Any]) -> bool:
        """이 핸들러가 처리할 수 있는지 판단"""
        pass
    
    @abstractmethod
    async def handle(self, state: AdvisorState) -> AdvisorState:
        """실제 처리 로직"""
        pass
    
    @property
    @abstractmethod
    def handler_name(self) -> str:
        """핸들러 이름"""
        pass
    
    def _format_response(self, content: Any, response_type: str, category: str) -> Dict[str, Any]:
        """응답 포맷팅 공통 메서드"""
        return {
            "content": content,
            "type": response_type,
            "category": category,
            "handler": self.handler_name
        }