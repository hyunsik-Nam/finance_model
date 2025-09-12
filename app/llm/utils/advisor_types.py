from typing import Any,TypedDict

class AdvisorState(TypedDict):
    question: str
    main_classification: dict
    stock_classification: dict
    route: str
    final_result: Any
    error: str