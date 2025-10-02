import getpass
import os
from typing import Any, Dict, List
from .advisor_types import AdvisorState

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.messages import BaseMessage
from langchain_core.outputs import LLMResult
from langchain.output_parsers.json import SimpleJsonOutputParser

from ..utils.promptManager import YAMLPromptManager
from ..utils.structured_outputs import FinalStockStruct, OrderClassifier
from ..handlers.handler_registry import handler_registry, initialize_handlers

if not os.environ.get("GOOGLE_API_KEY"):
    os.environ["GOOGLE_API_KEY"] = getpass.getpass("Enter API key for Google Gemini: ")

class LoggingHandler(BaseCallbackHandler):
    def on_chat_model_start(self, serialized: Dict[str, Any], messages: List[List[BaseMessage]], **kwargs) -> None:
        print("🤖 Chat model started")

    def on_llm_end(self, response: LLMResult, **kwargs) -> None:
        print("✅ Chat model ended")

    def on_chain_start(self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs) -> None:
        print(f"🔗 Chain '{serialized.get('name')}' started")

    def on_chain_end(self, outputs: Dict[str, Any], **kwargs) -> None:
        print("🏁 Chain ended")

# 전역 변수 초기화
model = init_chat_model("gemini-2.5-flash", model_provider="google_genai")
json_parser = SimpleJsonOutputParser()
structured_llm = model.with_structured_output(FinalStockStruct)
yaml_prompt_manager = YAMLPromptManager()

# 분류기들
classifier = yaml_prompt_manager.create_chat_prompt("stock_general_branch_prompt") | model
stock_classifier = yaml_prompt_manager.create_chat_prompt("stock_order_branch") | model.with_structured_output(OrderClassifier)

# Handler들 초기화
initialize_handlers(model, structured_llm, json_parser)

def classify_main(state: AdvisorState) -> AdvisorState:
    """1차 분류: STOCK vs GENERAL"""
    try:
        question = state["question"]
        main_result = classifier.invoke({"question": question})
        
        is_stock = "STOCK" in main_result.content.upper()
        route = "STOCK" if is_stock else "GENERAL"
        
        return {
            **state,
            "main_classification": {"content": main_result.content, "is_stock": is_stock},
            "route": route
        }
    except Exception as e:
        print(f"❌ Main classification error: {e}")
        return {**state, "error": str(e), "route": "ERROR"}

def classify_stock(state: AdvisorState) -> AdvisorState:
    """2차 분류: 세부 주식 기능 분류"""
    try:
        question = state["question"]
        stock_result = stock_classifier.invoke({"question": question})
        
        return {
            **state,
            "stock_classification": stock_result,
            "route": "STOCK_HANDLER"
        }
    except Exception as e:
        print(f"❌ Stock classification error: {e}")
        return {**state, "error": str(e), "route": "ERROR"}

async def process_stock_with_handlers(state: AdvisorState) -> AdvisorState:
    """Handler 패턴을 사용하는 동적 주식 처리 노드"""
    try:
        classification = state.get("stock_classification", {})
        
        # 적절한 Handler 선택
        handler = handler_registry.get_handler(classification)
        
        if handler:
            print(f"🎯 선택된 Handler: {handler.handler_name}")
            return await handler.handle(state)
        else:
            raise Exception("적절한 Handler를 찾을 수 없습니다")
            
    except Exception as e:
        print(f"❌ Handler processing error: {e}")
        return {**state, "error": str(e)}

def process_general(state: AdvisorState) -> AdvisorState:
    """일반 상담 처리"""
    try:
        # 일반 상담도 Handler를 통해 처리
        handler = handler_registry.get_handler_by_name("general_advice")
        
        if handler:
            # 동기 처리를 위해 asyncio 사용
            import asyncio
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(handler.handle(state))
        else:
            raise Exception("General advice handler를 찾을 수 없습니다")
            
    except Exception as e:
        print(f"❌ General processing error: {e}")
        return {**state, "error": str(e)}

def handle_error(state: AdvisorState) -> AdvisorState:
    """에러 처리"""
    error_message = state.get('error', '알 수 없는 오류')
    error_result = {
        "content": f"오류가 발생했습니다: {error_message}",
        "type": "error",
        "category": "system_error",
        "handler": "error_handler"
    }
    return {**state, "final_result": error_result}