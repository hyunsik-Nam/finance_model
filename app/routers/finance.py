from fastapi import APIRouter, Depends, HTTPException
from supabase import Client
from typing import List
from app.database.supabase import get_supabase_client
from app.services.finance_service import FinanceService
from app.models.schemas import FinancialDataCreate, FinancialDataResponse

router = APIRouter()

def get_finance_service(supabase: Client = Depends(get_supabase_client)) -> FinanceService:
    return FinanceService(supabase)

@router.get("/stocks/", response_model=List[FinancialDataResponse])
def get_all_stocks(
    limit: int = 100,
    service: FinanceService = Depends(get_finance_service)
):
    """모든 주식 조회"""
    return service.get_all_stocks(limit)

@router.get("/stocks/{symbol}", response_model=FinancialDataResponse)
def get_stock(
    symbol: str,
    service: FinanceService = Depends(get_finance_service)
):
    """특정 주식 조회"""
    stock = service.get_stock_by_symbol(symbol.upper())
    if not stock:
        raise HTTPException(status_code=404, detail="주식을 찾을 수 없습니다")
    return stock

@router.post("/stocks/", response_model=FinancialDataResponse)
def create_stock(
    data: FinancialDataCreate,
    service: FinanceService = Depends(get_finance_service)
):
    """새 주식 데이터 생성"""
    return service.create_stock_data(data)

@router.put("/stocks/{symbol}/price")
def update_stock_price(
    symbol: str,
    new_price: float,
    service: FinanceService = Depends(get_finance_service)
):
    """주식 가격 업데이트"""
    result = service.update_stock_price(symbol.upper(), new_price)
    if not result:
        raise HTTPException(status_code=404, detail="주식을 찾을 수 없습니다")
    return result

@router.get("/stocks/search/")
def search_stocks(
    q: str,
    service: FinanceService = Depends(get_finance_service)
):
    """주식 검색"""
    return service.search_stocks(q)