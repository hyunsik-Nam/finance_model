from ..llm.service.llm_service import LLMService
from ..llm.service.llm_service_langgraph import LLMServiceGraph

class TestService:
    def __init__(self):
        self.llm_service = LLMServiceGraph()

    async def get_test_data(self, question):
        async for chunk in self.llm_service.advisor_stream(question):
            yield chunk

