# import openai
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import json
import time
from typing import Dict, List, Optional, Tuple
import requests
from abc import ABC, abstractmethod
from PyQt5.QAxContainer import QAxWidget
from PyQt5.QtWidgets import QApplication
import sys
import pythoncom

class Kiwoom:
    def __init__(self):
        self.ocx = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
        self.ocx.OnEventConnect.connect(self.OnEventConnect)
        self.login = False

    def CommConnect(self):
        self.ocx.dynamicCall("CommConnect()")
        while self.login is False:
            pythoncom.PumpWaitingMessages()

    def OnEventConnect(self, code):
        self.login = True
        print("login is done", code)

class MarketDataManager:
    """시장 데이터 관리 클래스"""
    
    def __init__(self):
        self.data_cache = {}
        
    def get_stock_data(self, symbol: str, period: str = "3mo") -> pd.DataFrame:
        """주식 데이터 조회"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period)
            self.data_cache[symbol] = data
            return data
        except Exception as e:
            print(f"데이터 조회 오류 ({symbol}): {e}")
            return pd.DataFrame()
    
    def get_real_time_price(self, symbol: str) -> float:
        """실시간 가격 조회"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            return info.get('currentPrice', 0)
        except:
            return 0
        
    def search_korean_stock_symbol(stock_name: str) -> str:
        """한국투자증권 API나 다른 서비스로 검색"""
        # 예시: 한국투자증권 API (실제로는 인증 필요)
        try:
            # API 호출 예시 (실제 구현 시 API 키 필요)
            url = f"https://api.example.com/search?q={stock_name}"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                return data.get('symbol', f"{stock_name}.KS")
        except:
            pass

class RiskManager:
    """리스크 관리 클래스"""
    
    def __init__(self, max_drawdown: float = 0.15, max_single_loss: float = 0.05):
        self.max_drawdown = max_drawdown
        self.max_single_loss = max_single_loss
        self.peak_value = 0
        
    def check_risk_limits(self, current_value: float, trades: List[Dict]) -> Dict:
        """리스크 한계 점검"""
        if current_value > self.peak_value:
            self.peak_value = current_value
            
        drawdown = (self.peak_value - current_value) / self.peak_value if self.peak_value > 0 else 0
        
        # 최근 거래의 손실 체크
        recent_loss = 0
        if trades:
            latest_trade = trades[-1]
            if latest_trade.get('pnl', 0) < 0:
                recent_loss = abs(latest_trade['pnl']) / current_value
        
        risk_status = {
            "current_drawdown": drawdown,
            "max_drawdown_exceeded": drawdown > self.max_drawdown,
            "single_loss_exceeded": recent_loss > self.max_single_loss,
            "trading_allowed": drawdown <= self.max_drawdown and recent_loss <= self.max_single_loss
        }
        
        return risk_status
