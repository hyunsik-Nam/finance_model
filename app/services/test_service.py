from ..llm.service.llm_service import LLMService

class TestService:
    def __init__(self):
        self.llm_service = LLMService()

    def get_test_data(self, question):
        yield from self.llm_service.advisor_stream(question)

