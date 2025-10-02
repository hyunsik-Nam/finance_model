from typing import Literal
from .advisor_types import AdvisorState

def route_after_main_classification(state: AdvisorState) -> Literal["classify_stock", "process_general", "handle_error"]:
    """메인 분류 후 라우팅"""
    route = state.get("route", "")
    print(f"🔀 Main classification route: {route}")
    
    if route == "ERROR":
        return "handle_error"
    elif route == "STOCK":
        return "classify_stock"
    else:
        return "process_general"

def route_after_stock_classification(state: AdvisorState) -> Literal["process_stock_with_handlers", "handle_error"]:
    """주식 분류 후 라우팅"""
    route = state.get("route", "")
    print(f"🔀 Stock classification route: {route}")
    
    if route == "ERROR":
        return "handle_error"
    else:
        return "process_stock_with_handlers"