from langchain_core.tools import tool
from typing import Generator

def parse_stock_info(data):
    """주식 정보를 파싱하는 함수입니다"""
    print("Parsing stock info...")
    print(f"Original data: {data}")
    
    result = {**data, 'stock': '바위'}
    print(f"Modified data: {result}")
    return result

@tool
def order_stock(content:dict) -> dict:
    """ 주식을 주문하는 함수입니다"""
    print("Order data:", content)

    return {
        "content": {
            "status": "success",
            "message": f"{content['stock']} 주문 완료"
        }
    }

async def test():
    print("hi")