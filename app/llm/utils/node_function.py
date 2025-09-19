import getpass
import os
from typing import Any, Dict, List
from .advisor_types import AdvisorState
from ...services.finanace import MarketDataManager

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.messages import BaseMessage
from langchain_core.outputs import LLMResult
from langchain_core.runnables import RunnableLambda
from langchain.output_parsers.json import SimpleJsonOutputParser

# Your existing imports
from ..utils.promptManager import YAMLPromptManager
from ..utils.structured_outputs import FinalStockStruct, OrderClassifier
from ..utils.llm_tools import *

load_dotenv()

if not os.environ.get("GOOGLE_API_KEY"):
    os.environ["GOOGLE_API_KEY"] = getpass.getpass("Enter API key for Google Gemini: ")

class LoggingHandler(BaseCallbackHandler):
    def on_chat_model_start(
        self, serialized: Dict[str, Any], messages: List[List[BaseMessage]], **kwargs
    ) -> None:
        print("Chat model started")

    def on_llm_end(self, response: LLMResult, **kwargs) -> None:
        print(f"Chat model ended, response: {response}")

    def on_chain_start(
        self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs
    ) -> None:
        print(f"Chain {serialized.get('name')} started")

    def on_chain_end(self, outputs: Dict[str, Any], **kwargs) -> None:
        print(f"Chain ended, outputs: {outputs}")

callbacks = [LoggingHandler()]
model = init_chat_model("gemini-2.5-flash", model_provider="google_genai")
json_parser = SimpleJsonOutputParser()
structured_llm = model.with_structured_output(FinalStockStruct)
yaml_prompt_manager = YAMLPromptManager()

def format_stock_response(response):
    """주식 응답 포맷팅"""
    return {
        **response,
        "type": "stock_advice",
        "category": "investment"
    }

def format_general_response(response):
    """일반 응답 포맷팅"""
    return {
        **response,
        "type": "general_advice",
        "category": "general"
    }

def format_order_response(response):

    """주문 응답 포맷팅"""
    return {
        **response,
        "type": "order_confirmation",
        "category": "transaction"
    }

classifier = yaml_prompt_manager.create_chat_prompt("stock_general_branch_prompt") | model
stock_classifier = yaml_prompt_manager.create_chat_prompt("stock_order_branch") | model.with_structured_output(OrderClassifier)


# 프롬프트 함수들
def stock_prompt(question: str):
    context = 'test입니다'
    prompt = yaml_prompt_manager.create_chat_prompt("stock_advisor", context=context, question=question)
    return prompt

def general_prompt(question: str):
    context = 'test입니다'
    prompt = yaml_prompt_manager.create_chat_prompt("general_advisor", context=context, question=question)
    return prompt

# 분류기들

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
        return {**state, "error": str(e), "route": "ERROR"}

def classify_stock(state: AdvisorState) -> AdvisorState:
    """2차 분류: STOCK_ORDER vs STOCK_GENERAL"""
    try:
        question = state["question"]
        stock_result = stock_classifier.invoke({"question": question})
        
        stock_type = stock_result.get("type", "").upper()
        
        return {
            **state,
            "stock_classification": stock_result,
            "route": stock_type
        }
    except Exception as e:
        return {**state, "error": str(e), "route": "ERROR"}

def process_stock_order(state: AdvisorState) -> AdvisorState:
    """STOCK_ORDER 처리"""
    try:
        question = state["question"]
        classification = state["stock_classification"]

        def create_order_prompt(data):
            stock_info = f"주식: {data['stock']}, 액션: {data['action']}, 타입: {data['type']}"
            prompt = yaml_prompt_manager.create_chat_prompt(
                "stock_advisor",  # 기존 프롬프트 사용 또는 새로운 주문 프롬프트 생성
                context=f"주식 주문 정보: {stock_info}",
                question=f"{question} - 위 정보를 바탕으로 주문을 처리해주세요."
            )
            return prompt
        
        # parsed_data = parse_stock_info(classification)
        result = (RunnableLambda(create_order_prompt) | structured_llm | order_stock_handler | RunnableLambda(format_order_response)).invoke(classification)
        print(f"result : {result}")
        
        return {**state, "final_result": result,"type":"order_confirmation"}
    except Exception as e:
        return {**state, "error": str(e)}

def process_stock_general(state: AdvisorState) -> AdvisorState:
    """STOCK_GENERAL 처리"""
    try:
        question = state["question"]
        result = (stock_prompt(question) | model | json_parser | RunnableLambda(format_stock_response)).invoke({"question": question})

        return {**state, "final_result": result,"type":"stock_advice"}
    except Exception as e:
        return {**state, "error": str(e)}

def process_general(state: AdvisorState) -> AdvisorState:
    """GENERAL 처리"""
    try:
        question = state["question"]
        result = (general_prompt(question) | model | json_parser | RunnableLambda(format_general_response)).invoke({"question": question})

        return {**state, "final_result": result,"type":"general_advice"}
    except Exception as e:
        return {**state, "error": str(e)}

def handle_error(state: AdvisorState) -> AdvisorState:
    """에러 처리"""
    error_result = {
        "content": f"오류가 발생했습니다: {state.get('error', '알 수 없는 오류')}",
        "type": "error"
    }
    return {**state, "final_result": error_result}

# order_stock 함수 수정: FinalStockStruct를 받도록 변경
def order_stock_handler(structured_result: FinalStockStruct) -> dict:
    """structured_llm 결과에서 주문 처리"""
    data = structured_result['content']

    market_manager = MarketDataManager()
    symbol = market_manager.search_korean_stock_symbol(data.get('stock'))
    print(f"symbol : {symbol}")
    data1 = market_manager.get_stock_data(symbol)
    print(f"data1 : {data1}")

    return {
        "status": "success",
        "content": f"{data.get('stock')} {int(data.get('cnt'))} 주 {data.get('action')} 주문 완료",
        "structured_result": structured_result
    }