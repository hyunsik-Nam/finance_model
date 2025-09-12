# import getpass
# import os
# from typing import Any, Dict, List, TypedDict, Literal
import json

# from dotenv import load_dotenv
# from langchain.chat_models import init_chat_model
# from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
# from langchain_core.messages import HumanMessage, AIMessage
# from langchain_core.callbacks import BaseCallbackHandler
# from langchain_core.messages import BaseMessage
# from langchain_core.outputs import LLMResult
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.runnables import RunnableLambda
# from langchain.output_parsers.json import SimpleJsonOutputParser

# # LangGraph imports
from langgraph.graph import StateGraph, END, START
from langgraph.graph.message import add_messages

# # Your existing imports
# from ..utils.promptManager import YAMLPromptManager
# from ..utils.structured_outputs import StockStruct, FinalStockStruct, OrderClassifier
# from ..utils.llm_tools import *

from ..utils.route_function import *
from ..utils.node_function import *

# load_dotenv()

# if not os.environ.get("GOOGLE_API_KEY"):
#     os.environ["GOOGLE_API_KEY"] = getpass.getpass("Enter API key for Google Gemini: ")


# class LoggingHandler(BaseCallbackHandler):
#     def on_chat_model_start(
#         self, serialized: Dict[str, Any], messages: List[List[BaseMessage]], **kwargs
#     ) -> None:
#         print("Chat model started")

#     def on_llm_end(self, response: LLMResult, **kwargs) -> None:
#         print(f"Chat model ended, response: {response}")

#     def on_chain_start(
#         self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs
#     ) -> None:
#         print(f"Chain {serialized.get('name')} started")

#     def on_chain_end(self, outputs: Dict[str, Any], **kwargs) -> None:
#         print(f"Chain ended, outputs: {outputs}")


# State 정의
# class AdvisorState(TypedDict):
#     question: str
#     main_classification: dict
#     stock_classification: dict
#     route: str
#     final_result: Any
#     error: str


# callbacks = [LoggingHandler()]
# model = init_chat_model("gemini-2.5-flash", model_provider="google_genai")
# json_parser = SimpleJsonOutputParser()
# structured_llm = model.with_structured_output(FinalStockStruct)
# yaml_prompt_manager = YAMLPromptManager()


class LLMServiceGraph:
    def __init__(self):
        pass


    # def _format_stock_response(self, response):
    #     """주식 응답 포맷팅"""
    #     return {
    #         **response,
    #         "type": "stock_advice",
    #         "category": "investment"
    #     }
    
    # def _format_general_response(self, response):
    #     """일반 응답 포맷팅"""
    #     return {
    #         **response,
    #         "type": "general_advice",
    #         "category": "general"
    #     }
    
    # def _format_order_response(self, response):
    #     """주문 응답 포맷팅"""
    #     return {
    #         **response,
    #         "type": "order_confirmation",
    #         "category": "transaction"
    #     }
    
    def _create_langgraph_chain(self):
        """LangGraph 체인 생성"""
        
        # # 프롬프트 함수들
        # def stock_prompt(question: str):
        #     context = 'test입니다'
        #     prompt = yaml_prompt_manager.create_chat_prompt("stock_advisor", context=context, question=question)
        #     return prompt

        # def general_prompt(question: str):
        #     context = 'test입니다'
        #     prompt = yaml_prompt_manager.create_chat_prompt("general_advisor", context=context, question=question)
        #     return prompt

        # # 분류기들
        # classifier = yaml_prompt_manager.create_chat_prompt("stock_general_branch_prompt") | model
        # stock_classifier = yaml_prompt_manager.create_chat_prompt("stock_order_branch") | model.with_structured_output(OrderClassifier)

        # # 노드 함수들
        # def classify_main(state: AdvisorState) -> AdvisorState:
        #     """1차 분류: STOCK vs GENERAL"""
        #     try:
        #         question = state["question"]
        #         main_result = classifier.invoke({"question": question})
                
        #         is_stock = "STOCK" in main_result.content.upper()
        #         route = "STOCK" if is_stock else "GENERAL"
                
        #         return {
        #             **state,
        #             "main_classification": {"content": main_result.content, "is_stock": is_stock},
        #             "route": route
        #         }
        #     except Exception as e:
        #         return {**state, "error": str(e), "route": "ERROR"}

        # def classify_stock(state: AdvisorState) -> AdvisorState:
        #     """2차 분류: STOCK_ORDER vs STOCK_GENERAL"""
        #     try:
        #         question = state["question"]
        #         stock_result = stock_classifier.invoke({"question": question})
                
        #         stock_type = stock_result.get("type", "").upper()
                
        #         return {
        #             **state,
        #             "stock_classification": stock_result,
        #             "route": stock_type
        #         }
        #     except Exception as e:
        #         return {**state, "error": str(e), "route": "ERROR"}

        # def process_stock_order(state: AdvisorState) -> AdvisorState:
        #     """STOCK_ORDER 처리"""
        #     try:
        #         classification = state["stock_classification"]
        #         # parsed_data = parse_stock_info(classification)
        #         # result = (structured_llm | order_stock | RunnableLambda(self._format_order_response)).invoke(classification)
        #         result = (structured_llm).invoke(classification)
        #         print(f"result : {result}")
                
        #         return {**state, "final_result": result,"type":"order_confirmation"}
        #     except Exception as e:
        #         return {**state, "error": str(e)}

        # def process_stock_general(state: AdvisorState) -> AdvisorState:
        #     """STOCK_GENERAL 처리"""
        #     try:
        #         question = state["question"]
        #         result = (stock_prompt(question) | model | json_parser | RunnableLambda(self._format_stock_response)).invoke({"question": question})

        #         return {**state, "final_result": result,"type":"stock_advice"}
        #     except Exception as e:
        #         return {**state, "error": str(e)}

        # def process_general(state: AdvisorState) -> AdvisorState:
        #     """GENERAL 처리"""
        #     try:
        #         question = state["question"]
        #         result = (general_prompt(question) | model | json_parser | RunnableLambda(self._format_general_response)).invoke({"question": question})

        #         return {**state, "final_result": result,"type":"general_advice"}
        #     except Exception as e:
        #         return {**state, "error": str(e)}

        # def handle_error(state: AdvisorState) -> AdvisorState:
        #     """에러 처리"""
        #     error_result = {
        #         "content": f"오류가 발생했습니다: {state.get('error', '알 수 없는 오류')}",
        #         "type": "error"
        #     }
        #     return {**state, "final_result": error_result}

        # 라우팅 함수들
        # def route_after_main_classification(state: AdvisorState) -> Literal["classify_stock", "process_general", "handle_error"]:
        #     """메인 분류 후 라우팅"""
        #     route = state.get("route", "")
        #     if route == "ERROR":
        #         return "handle_error"
        #     elif route == "STOCK":
        #         return "classify_stock"
        #     else:
        #         return "process_general"

        # def route_after_stock_classification(state: AdvisorState) -> Literal["process_stock_order", "process_stock_general", "handle_error"]:
        #     """주식 분류 후 라우팅"""
        #     route = state.get("route", "")
        #     if route == "ERROR":
        #         return "handle_error"
        #     elif route == "STOCK_ORDER":
        #         return "process_stock_order"
        #     else:
        #         return "process_stock_general"

        # 그래프 생성
        workflow = StateGraph(AdvisorState)

        # 노드 추가
        workflow.add_node("classify_main", classify_main)
        workflow.add_node("classify_stock", classify_stock)
        workflow.add_node("process_stock_order", process_stock_order)
        workflow.add_node("process_stock_general", process_stock_general)
        workflow.add_node("process_general", process_general)
        workflow.add_node("handle_error", handle_error)

        # 엣지 추가
        workflow.add_edge(START, "classify_main")
        
        # 메인 분류 후 조건부 라우팅
        workflow.add_conditional_edges(
            "classify_main",
            route_after_main_classification,
            {
                "classify_stock": "classify_stock",
                "process_general": "process_general",
                "handle_error": "handle_error"
            }
        )

        # 주식 분류 후 조건부 라우팅
        workflow.add_conditional_edges(
            "classify_stock",
            route_after_stock_classification,
            {
                "process_stock_order": "process_stock_order",
                "process_stock_general": "process_stock_general",
                "handle_error": "handle_error"
            }
        )

        # 모든 처리 노드에서 END로
        workflow.add_edge("process_stock_order", END)
        workflow.add_edge("process_stock_general", END)
        workflow.add_edge("process_general", END)
        workflow.add_edge("handle_error", END)

        return workflow.compile()

    async def advisor_stream(self, question):
        """상담 스트림 (LangGraph 버전)"""
        try:
            # 먼저 분류 메시지 전송
            classification_data = {"content": f"상담을 시작합니다.\n\n"}
            yield f"data: {json.dumps(classification_data, ensure_ascii=False)}\n\n"

            # LangGraph 실행
            graph = self._create_langgraph_chain()
            
            # 스트리밍으로 실행
            async for chunk in graph.astream(
                {"question": question}
                # , 
                # config={"callbacks": callbacks}
            ):
                # 각 노드의 출력 처리
                for node_name, node_output in chunk.items():
                    print(f"Node {node_name} output: {node_output}")

                    if node_name == "classify_main":
                        route = node_output.get("route", "")
                        if route == "STOCK":
                            feedback = {"content": "📈 주식 관련 질문으로 분류되었습니다...\n\n"}
                            yield f"data: {json.dumps(feedback, ensure_ascii=False)}\n\n"
                        elif route == "GENERAL":
                            feedback = {"content": "💬 일반 상담으로 분류되었습니다...\n\n"}
                            yield f"data: {json.dumps(feedback, ensure_ascii=False)}\n\n"

                    if node_name in ["process_stock_order", "process_stock_general", "process_general", "handle_error"]:

                        # 최종 결과가 있는 경우만 스트리밍
                        final_result = node_output.get("final_result")
                        print(f"Final result: {final_result}")
                        if final_result:

                            # 타입별 이모지 추가
                            type_emojis = {
                                "stock_advice": "📊 ",
                                "general_advice": "💡 ",
                                "order_confirmation": "✅ ",
                                "error": "❌ "
                            }
                            prefix = type_emojis.get(final_result.get("type"), "")
                            for char in prefix:
                                yield f"data: {json.dumps({'content': char}, ensure_ascii=False)}\n\n"

                            # 결과를 적절히 스트리밍
                            if isinstance(final_result, dict):
                                content = final_result.get("content", "")
                                if isinstance(content, dict):
                                    content_str = json.dumps(content, ensure_ascii=False)
                                    for char in content_str:
                                        yield f"data: {json.dumps({'content': char}, ensure_ascii=False)}\n\n"
                                else:
                                    # 문자별로 스트리밍
                                    for char in str(content):
                                        yield f"data: {json.dumps({'content': char}, ensure_ascii=False)}\n\n"
                            else:
                                # 문자별로 스트리밍
                                for char in str(final_result):
                                    yield f"data: {json.dumps({'content': char}, ensure_ascii=False)}\n\n"
            
            yield "data: [DONE]\n\n"
            
        except Exception as e:
            error_data = {"content": f"오류가 발생했습니다: {str(e)}"}
            yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"
            yield "data: [DONE]\n\n"
