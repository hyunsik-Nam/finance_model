from fastapi import APIRouter
from app.services.item_service import ItemService

router = APIRouter()
item_service = ItemService()

@router.get("/")
def get_all_items():
    """모든 상품 조회"""
    return item_service.get_all_items()

@router.get("/{item_id}")
def get_item(item_id: int):
    """특정 상품 조회"""
    return item_service.get_item_by_id(item_id)

@router.post("/")
def create_item(name: str, price: float, category: str):
    """상품 생성"""
    return item_service.create_item(name, price, category)

@router.put("/{item_id}")
def update_item(item_id: int, name: str, price: float):
    """상품 수정"""
    return item_service.update_item(item_id, name, price)
