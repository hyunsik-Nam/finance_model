from fastapi import APIRouter
from app.services.order_service import OrderService

router = APIRouter()
order_service = OrderService()

@router.get("/")
def get_all_orders():
    """모든 주문 조회"""
    return order_service.get_all_orders()

@router.get("/{order_id}")
def get_order(order_id: int):
    """특정 주문 조회"""
    return order_service.get_order_by_id(order_id)

@router.post("/")
def create_order(user_id: int, item_id: int, quantity: int):
    """주문 생성"""
    return order_service.create_order(user_id, item_id, quantity)
