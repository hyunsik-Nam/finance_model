from typing import Optional

from pydantic import BaseModel, Field
from typing_extensions import Annotated, TypedDict

class Joke1(TypedDict):
    """Joke to tell user."""

    setup: Annotated[str, ..., "The setup of the joke"]

    # Alternatively, we could have specified setup as:

    # setup: str                    # no default, no description
    # setup: Annotated[str, ...]    # no default, no description
    # setup: Annotated[str, "foo"]  # default, no description

    punchline: Annotated[str, ..., "The punchline of the joke"]
    rating: Annotated[Optional[int], None, "How funny the joke is, from 1 to 10"]

class Joke(TypedDict):
    """test"""
    content: Joke1

class StockStruct(BaseModel):
    """ 주식정보를 담는 데이터 구조 """
    stock: str = Field(description="주식 설정 정보", example="삼성전자, 애플")
    current_price: float = Field(description="현재 주식 가격", example=1000.0)
    target_price: float = Field(description="목표 주식 가격", example=1200.0)
    stop_loss: Optional[float] = Field(description="손절가", example=900.0)
    take_profit: Optional[float] = Field(description="익절가", example=1100.0)

class FinalStockStruct(BaseModel):
    """ 최종 주식정보를 담는 데이터 구조 """
    content: StockStruct