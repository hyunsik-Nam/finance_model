from fastapi import APIRouter
from app.services.user_service import UserService

router = APIRouter()
user_service = UserService()

@router.get("/")
def get_all_users():
    """모든 사용자 조회"""
    return user_service.get_all_users()

@router.get("/{user_id}")
def get_user(user_id: int):
    """특정 사용자 조회"""
    return user_service.get_user_by_id(user_id)

@router.post("/")
def create_user(name: str, email: str):
    """사용자 생성"""
    return user_service.create_user(name, email)

@router.put("/{user_id}")  
def update_user(user_id: int, name: str, email: str):
    """사용자 수정"""
    return user_service.update_user(user_id, name, email)

@router.delete("/{user_id}")
def delete_user(user_id: int):
    """사용자 삭제"""
    return user_service.delete_user(user_id)
