from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class FinancialDataCreate(BaseModel):
    symbol: str
    name: Optional[str] = None
    price: float
    volume: Optional[int] = 0
    market_cap: Optional[int] = None
    pe_ratio: Optional[float] = None
    sector: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class FinancialDataResponse(BaseModel):
    id: int
    symbol: str
    name: Optional[str]
    price: float
    volume: Optional[int]
    market_cap: Optional[int]
    pe_ratio: Optional[float]
    sector: Optional[str]
    metadata: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: Optional[datetime]