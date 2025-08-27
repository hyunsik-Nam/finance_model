import getpass
import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from app.utils.promptManager import YAMLPromptManager
import json

load_dotenv()

if not os.environ.get("GOOGLE_API_KEY"):
  os.environ["GOOGLE_API_KEY"] = getpass.getpass("Enter API key for Google Gemini: ")


model = init_chat_model("gemini-2.5-flash", model_provider="google_genai")
yaml_prompt_manager = YAMLPromptManager()

class TestService:
    def __init__(self):
        pass
    
    def get_test_data(self, question):
        question_type = self.question_classifier(question)

        print(f"Question Type: {question_type}")

        # 2. 분류에 따른 스트림 응답
        if "STOCK" in question_type:
            # 주식 관련 질문 - 스트림으로 처리
            context = question
            yield from self.advisor_stream(context, question, "stock_advisor")
        else:
            # 일반 질문 - 스트림으로 처리
            context = question
            yield from self.advisor_stream(context, question, "general_advisor")

    def question_classifier(self, question):
        """질문 분류기"""
        variables = {"question": question}
        prompt = yaml_prompt_manager.create_chat_prompt("stock_general_branch_prompt", **variables)

        chain = prompt | model
        response = chain.invoke({})

        return response.content
    
    def advisor_stream(self, context, question,prompts):
        """상담 스트림"""
        try:
            variables = {"context": context, "question": question}
            prompt = yaml_prompt_manager.create_chat_prompt(prompts, **variables)

            print(f"Using prompt: {prompt}")
            
            # Chain 생성
            chain = prompt | model
            
            # 먼저 분류 메시지 전송
            classification_data = {"content": f"{prompts} 상담을 시작합니다.\n\n"}
            yield f"data: {json.dumps(classification_data, ensure_ascii=False)}\n\n"
            
            # Chain으로 스트리밍
            for chunk in chain.stream({}):
                if hasattr(chunk, 'content') and chunk.content:
                    for char in chunk.content:
                        data = {"content": char}
                        yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
            
            yield "data: [DONE]\n\n"
            
        except Exception as e:
            error_data = {"content": f"오류가 발생했습니다: {str(e)}"}
            yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"
            yield "data: [DONE]\n\n"
    
    def stock_advisor(self, context):
        """주식 투자 상담"""
        prompt = yaml_prompt_manager.create_chat_prompt("stock_advisor")
        final_prompt = prompt.invoke({"context": context})

        response = model.invoke(final_prompt)
        return response.content
    
    def general_advisor(self, context):
        """일반 질문 상담"""
        prompt = yaml_prompt_manager.create_chat_prompt("general_advisor")
        final_prompt = prompt.invoke({"context": context})

        response = model.invoke(final_prompt)
        return response.content
