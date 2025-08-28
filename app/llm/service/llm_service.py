    
import getpass
import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from ..utils.promptManager import YAMLPromptManager
from langchain_core.runnables import RunnableBranch, RunnablePassthrough
from langchain.output_parsers.json import SimpleJsonOutputParser
from ..utils.structured_outputs import StockStruct,FinalStockStruct,Joke
import json

load_dotenv()

if not os.environ.get("GOOGLE_API_KEY"):
  os.environ["GOOGLE_API_KEY"] = getpass.getpass("Enter API key for Google Gemini: ")


model = init_chat_model("gemini-2.5-flash", model_provider="google_genai")
json_parser = SimpleJsonOutputParser()
structured_llm = model.with_structured_output(Joke)
yaml_prompt_manager = YAMLPromptManager()

class LLMService:
    def __init__(self):
        pass
    
    def _create_routing_chain(self):
        """라우팅 체인 생성"""
        
        # 각 어드바이저 프롬프트
        def stock_prompt(question: str) : 
            context = 'test입니다'
            prompt = yaml_prompt_manager.create_chat_prompt("stock_advisor", context=context, question=question)
            return prompt


        # general_prompt = yaml_prompt_manager.create_chat_prompt("general_advisor")

        def general_prompt(question: str) :
            context = 'test입니다'
            prompt = yaml_prompt_manager.create_chat_prompt("general_advisor", context=context, question=question)
            return prompt

        # 분류기
        classifier_prompt =  yaml_prompt_manager.create_chat_prompt("stock_general_branch_prompt")

        classifier = classifier_prompt | model
        

        # 🎯 RunnableBranch로 분기처리
        routing_chain = RunnableBranch(
            # 조건1: STOCK이 포함된 경우
            (lambda x: "STOCK" in classifier.invoke({"question": x["question"]}).content.upper(),
             lambda x : stock_prompt(x["question"]) | structured_llm
            ),      # 조건2: 기본값 (GENERAL)
            lambda x : general_prompt(x["question"]) | model | json_parser
        )
        
        return routing_chain
    

    def advisor_stream(self, question):
        """상담 스트림"""
        try:
            # 먼저 분류 메시지 전송
            classification_data = {"content": f"상담을 시작합니다.\n\n"}
            yield f"data: {json.dumps(classification_data, ensure_ascii=False)}\n\n"
            
            response = self._create_routing_chain().invoke({"question": question})
            print(f"결과값:{response}")

            # Chain으로 스트리밍
            for chunk in self._create_routing_chain().stream({"question": question}):
                # content가 있으면 한 번에 처리
                content = chunk.get("content", "") if isinstance(chunk, dict) else ""
                for char in content:
                    yield f"data: {json.dumps({'content': char}, ensure_ascii=False)}\n\n"
            
            yield "data: [DONE]\n\n"
            
        except Exception as e:
            error_data = {"content": f"오류가 발생했습니다: {str(e)}"}
            yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"
            yield "data: [DONE]\n\n"
    
