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

class TestService:
    def __init__(self):
        pass
    
    def get_test_data(self, msg):
        yaml_prompt_manager = YAMLPromptManager()
        prompt_test = yaml_prompt_manager.create_chat_prompt("test_prompt")
        final_prompt = prompt_test.invoke({"question": msg})
        

        for chunk in model.stream(final_prompt):
            # 한글자씩 보내기
            for char in chunk.content:
                data = {"content": char}
                yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
        
        # 스트림 종료 신호
        yield "data: [DONE]\n\n"