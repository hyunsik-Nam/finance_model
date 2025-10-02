from typing import TypedDict, Any, Dict, Optional

class AdvisorState(TypedDict):
    question: str
    main_classification: Optional[Dict[str, Any]]
    stock_classification: Optional[Dict[str, Any]]
    route: str
    final_result: Optional[Any]
    error: Optional[str]
    handler_name: Optional[str]