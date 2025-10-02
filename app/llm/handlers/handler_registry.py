from typing import Dict, List, Optional
from .base_handler import BaseHandler
from .stock_handlers import StockOrderHandler, StockPriceHandler, StockAnalysisHandler, GeneralStockHandler
from .general_handler import GeneralAdviceHandler

class HandlerRegistry:
    """Handler 레지스트리 - 싱글톤 패턴"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._handlers: List[BaseHandler] = []
            self._handler_map: Dict[str, BaseHandler] = {}
            self._default_handler: Optional[BaseHandler] = None
            self._initialized = True
    
    def register_handler(self, handler: BaseHandler, is_default: bool = False):
        """Handler 등록"""
        self._handlers.append(handler)
        self._handler_map[handler.handler_name] = handler
        
        if is_default:
            self._default_handler = handler
    
    def get_handler(self, classification: Dict) -> Optional[BaseHandler]:
        """분류 결과에 따라 적절한 Handler 반환"""
        # 우선순위에 따라 Handler 선택
        priority_handlers = [
            handler for handler in self._handlers 
            if handler.handler_name != "general_advice"
        ]
        
        for handler in priority_handlers:
            if handler.can_handle(classification):
                return handler
        
        # 기본 Handler 반환
        return self._default_handler
    
    def get_handler_by_name(self, name: str) -> Optional[BaseHandler]:
        """이름으로 Handler 조회"""
        return self._handler_map.get(name)
    
    def list_handlers(self) -> List[str]:
        """등록된 Handler 목록"""
        return list(self._handler_map.keys())
    
    def clear_handlers(self):
        """모든 Handler 제거 (테스트용)"""
        self._handlers.clear()
        self._handler_map.clear()
        self._default_handler = None

# 전역 레지스트리 인스턴스
handler_registry = HandlerRegistry()

def initialize_handlers(model, structured_llm, json_parser):
    """Handler들 초기화 및 등록"""
    # 기존 Handler 정리
    handler_registry.clear_handlers()
    
    # Handler들 생성 및 등록
    handlers = [
        (StockOrderHandler(model, structured_llm), False),
        (StockPriceHandler(model), False),
        (StockAnalysisHandler(model, json_parser), False),
        (GeneralStockHandler(model, json_parser), False),
        (GeneralAdviceHandler(model, json_parser), True)  # 기본 Handler
    ]
    
    for handler, is_default in handlers:
        handler_registry.register_handler(handler, is_default)
    
    print(f"✅ {len(handlers)}개 Handler 초기화 완료: {handler_registry.list_handlers()}")
    
    return handler_registry