from .advisor_types import AdvisorState
from typing import Literal

def route_after_main_classification(state: AdvisorState) -> Literal["classify_stock", "process_general", "handle_error"]:
    """메인 분류 후 라우팅"""
    route = state.get("route", "")
    if route == "ERROR":
        return "handle_error"
    elif route == "STOCK":
        return "classify_stock"
    else:
        return "process_general"

def route_after_stock_classification(state: AdvisorState) -> Literal["process_stock_order", "process_stock_general", "handle_error"]:
    """주식 분류 후 라우팅"""
    route = state.get("route", "")
    if route == "ERROR":
        return "handle_error"
    elif route == "STOCK_ORDER":
        return "process_stock_order"
    else:
        return "process_stock_general"