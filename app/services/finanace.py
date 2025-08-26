import openai
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import json
import time
from typing import Dict, List, Optional, Tuple
import requests
from abc import ABC, abstractmethod

class TradingAgent(ABC):
    """트레이딩 에이전트 베이스 클래스"""
    
    def __init__(self, name: str, llm_model: str = "gpt-4"):
        self.name = name
        self.llm_model = llm_model
        self.portfolio = {}
        self.cash = 100000  # 초기 현금
        self.trade_history = []
        
    @abstractmethod
    def analyze_market(self, symbol: str, data: pd.DataFrame) -> Dict:
        """시장 분석"""
        pass
    
    @abstractmethod
    def make_decision(self, analysis: Dict) -> Dict:
        """거래 결정"""
        pass

class LLMTradingAgent(TradingAgent):
    """LLM을 활용한 트레이딩 에이전트"""
    
    def __init__(self, name: str, api_key: str, llm_model: str = "gpt-4"):
        super().__init__(name, llm_model)
        openai.api_key = api_key
        self.client = openai.OpenAI(api_key=api_key)
        
    def get_news_sentiment(self, symbol: str) -> str:
        """뉴스 감성분석"""
        # 실제로는 뉴스 API를 사용
        prompt = f"""
        {symbol} 주식에 대한 최근 뉴스를 분석하여 시장 감성을 평가해주세요.
        긍정적(Positive), 중립적(Neutral), 부정적(Negative) 중 하나로 답변하고,
        간단한 이유를 제시해주세요.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.llm_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"뉴스 감성분석 오류: {e}")
            return "Neutral"
    
    def analyze_market(self, symbol: str, data: pd.DataFrame) -> Dict:
        """시장 분석 - LLM을 활용한 종합 분석"""
        
        # 기술적 지표 계산
        data['SMA_20'] = data['Close'].rolling(window=20).mean()
        data['SMA_50'] = data['Close'].rolling(window=50).mean()
        data['RSI'] = self.calculate_rsi(data['Close'])
        data['MACD'], data['MACD_signal'] = self.calculate_macd(data['Close'])
        
        current_price = data['Close'].iloc[-1]
        sma_20 = data['SMA_20'].iloc[-1]
        sma_50 = data['SMA_50'].iloc[-1]
        rsi = data['RSI'].iloc[-1]
        
        # 뉴스 감성 분석
        news_sentiment = self.get_news_sentiment(symbol)
        
        # LLM을 활용한 종합 분석
        analysis_prompt = f"""
        다음 주식 데이터를 분석하여 투자 의견을 제시해주세요:
        
        종목: {symbol}
        현재가: ${current_price:.2f}
        20일 이동평균: ${sma_20:.2f}
        50일 이동평균: ${sma_50:.2f}
        RSI: {rsi:.2f}
        뉴스 감성: {news_sentiment}
        
        다음 형식으로 JSON 응답해주세요:
        {{
            "recommendation": "BUY/SELL/HOLD",
            "confidence": 0-100,
            "reasoning": "분석 근거",
            "risk_level": "LOW/MEDIUM/HIGH",
            "target_allocation": 0-100
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.llm_model,
                messages=[{"role": "user", "content": analysis_prompt}],
                temperature=0.3
            )
            
            analysis_text = response.choices[0].message.content
            # JSON 파싱 시도
            try:
                analysis = json.loads(analysis_text)
            except:
                # JSON 파싱 실패시 기본값 반환
                analysis = {
                    "recommendation": "HOLD",
                    "confidence": 50,
                    "reasoning": "LLM 응답 파싱 실패",
                    "risk_level": "MEDIUM",
                    "target_allocation": 20
                }
                
        except Exception as e:
            print(f"LLM 분석 오류: {e}")
            analysis = {
                "recommendation": "HOLD",
                "confidence": 50,
                "reasoning": "LLM 분석 오류",
                "risk_level": "MEDIUM",
                "target_allocation": 20
            }
        
        # 기술적 지표 추가
        analysis.update({
            "current_price": current_price,
            "sma_20": sma_20,
            "sma_50": sma_50,
            "rsi": rsi,
            "news_sentiment": news_sentiment
        })
        
        return analysis
    
    def calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """RSI 계산"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    def calculate_macd(self, prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
        """MACD 계산"""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd = ema_fast - ema_slow
        macd_signal = macd.ewm(span=signal).mean()
        return macd, macd_signal
    
    def make_decision(self, analysis: Dict) -> Dict:
        """거래 결정 로직"""
        recommendation = analysis.get("recommendation", "HOLD")
        confidence = analysis.get("confidence", 50)
        risk_level = analysis.get("risk_level", "MEDIUM")
        target_allocation = analysis.get("target_allocation", 20)
        current_price = analysis.get("current_price", 0)
        
        # 리스크 관리
        max_position_size = self.get_max_position_size(risk_level)
        position_size = min(target_allocation, max_position_size)
        
        # 거래 결정
        decision = {
            "action": recommendation,
            "confidence": confidence,
            "position_size": position_size,
            "price": current_price,
            "reasoning": analysis.get("reasoning", ""),
            "timestamp": datetime.now()
        }
        
        return decision
    
    def get_max_position_size(self, risk_level: str) -> float:
        """리스크 레벨에 따른 최대 포지션 크기"""
        risk_limits = {
            "LOW": 30,
            "MEDIUM": 20,
            "HIGH": 10
        }
        return risk_limits.get(risk_level, 20)

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

class TradingOrchestrator:
    """트레이딩 오케스트레이터 - 전체 시스템 조율"""
    
    def __init__(self, agent: LLMTradingAgent, data_manager: MarketDataManager, 
                 risk_manager: RiskManager):
        self.agent = agent
        self.data_manager = data_manager
        self.risk_manager = risk_manager
        self.watchlist = ['AAPL', 'GOOGL', 'MSFT', 'TSLA']
        self.running = False
        
    def run_trading_cycle(self):
        """트레이딩 사이클 실행"""
        print(f"[{datetime.now()}] 트레이딩 사이클 시작")
        
        for symbol in self.watchlist:
            try:
                # 데이터 수집
                data = self.data_manager.get_stock_data(symbol)
                if data.empty:
                    continue
                
                # 시장 분석
                analysis = self.agent.analyze_market(symbol, data)
                print(f"{symbol} 분석 완료: {analysis['recommendation']} (신뢰도: {analysis['confidence']}%)")
                
                # 거래 결정
                decision = self.agent.make_decision(analysis)
                
                # 리스크 체크
                current_portfolio_value = self.calculate_portfolio_value()
                risk_status = self.risk_manager.check_risk_limits(
                    current_portfolio_value, 
                    self.agent.trade_history
                )
                
                if not risk_status['trading_allowed']:
                    print(f"⚠️ 리스크 한계 초과 - 거래 중단 ({symbol})")
                    continue
                
                # 거래 실행 (시뮬레이션)
                if decision['action'] in ['BUY', 'SELL'] and decision['confidence'] > 70:
                    self.execute_trade(symbol, decision)
                    
            except Exception as e:
                print(f"❌ {symbol} 처리 중 오류: {e}")
                
        print(f"[{datetime.now()}] 트레이딩 사이클 완료\n")
    
    def execute_trade(self, symbol: str, decision: Dict):
        """거래 실행 (시뮬레이션)"""
        action = decision['action']
        price = decision['price']
        position_size = decision['position_size']
        
        if action == 'BUY':
            max_shares = int((self.agent.cash * position_size / 100) / price)
            if max_shares > 0:
                self.agent.portfolio[symbol] = self.agent.portfolio.get(symbol, 0) + max_shares
                self.agent.cash -= max_shares * price
                
                trade_record = {
                    'timestamp': datetime.now(),
                    'symbol': symbol,
                    'action': action,
                    'shares': max_shares,
                    'price': price,
                    'total': max_shares * price,
                    'reasoning': decision['reasoning']
                }
                
                self.agent.trade_history.append(trade_record)
                print(f"✅ 매수 실행: {symbol} {max_shares}주 @ ${price:.2f}")
                
        elif action == 'SELL' and symbol in self.agent.portfolio:
            shares_to_sell = int(self.agent.portfolio[symbol] * position_size / 100)
            if shares_to_sell > 0:
                self.agent.portfolio[symbol] -= shares_to_sell
                self.agent.cash += shares_to_sell * price
                
                if self.agent.portfolio[symbol] <= 0:
                    del self.agent.portfolio[symbol]
                
                trade_record = {
                    'timestamp': datetime.now(),
                    'symbol': symbol,
                    'action': action,
                    'shares': shares_to_sell,
                    'price': price,
                    'total': shares_to_sell * price,
                    'reasoning': decision['reasoning']
                }
                
                self.agent.trade_history.append(trade_record)
                print(f"✅ 매도 실행: {symbol} {shares_to_sell}주 @ ${price:.2f}")
    
    def calculate_portfolio_value(self) -> float:
        """포트폴리오 총 가치 계산"""
        total_value = self.agent.cash
        
        for symbol, shares in self.agent.portfolio.items():
            current_price = self.data_manager.get_real_time_price(symbol)
            total_value += shares * current_price
            
        return total_value
    
    def start_automated_trading(self, interval_minutes: int = 60):
        """자동 트레이딩 시작"""
        self.running = True
        print(f"🚀 자동 트레이딩 시작 (주기: {interval_minutes}분)")
        
        while self.running:
            try:
                self.run_trading_cycle()
                self.print_portfolio_status()
                
                # 다음 사이클까지 대기
                time.sleep(interval_minutes * 60)
                
            except KeyboardInterrupt:
                print("❌ 사용자에 의해 중단됨")
                self.running = False
            except Exception as e:
                print(f"❌ 시스템 오류: {e}")
                time.sleep(300)  # 5분 대기 후 재시작
    
    def print_portfolio_status(self):
        """포트폴리오 현황 출력"""
        total_value = self.calculate_portfolio_value()
        print(f"\n=== 포트폴리오 현황 ===")
        print(f"현금: ${self.agent.cash:,.2f}")
        print(f"총 자산: ${total_value:,.2f}")
        print(f"보유 종목:")
        
        for symbol, shares in self.agent.portfolio.items():
            current_price = self.data_manager.get_real_time_price(symbol)
            value = shares * current_price
            print(f"  {symbol}: {shares}주 @ ${current_price:.2f} = ${value:,.2f}")
        
        if self.agent.trade_history:
            print(f"총 거래 횟수: {len(self.agent.trade_history)}")
        print("=" * 30)

# 사용 예시
def main():
    # OpenAI API 키 설정 (실제 키로 교체 필요)
    OPENAI_API_KEY = "your-openai-api-key"
    
    # 컴포넌트 초기화
    agent = LLMTradingAgent("SmartTrader", OPENAI_API_KEY)
    data_manager = MarketDataManager()
    risk_manager = RiskManager(max_drawdown=0.15, max_single_loss=0.05)
    
    # 오케스트레이터 생성
    orchestrator = TradingOrchestrator(agent, data_manager, risk_manager)
    
    # 백테스팅 모드
    print("백테스팅 모드로 한 번 실행...")
    orchestrator.run_trading_cycle()
    orchestrator.print_portfolio_status()
    
    # 실시간 트레이딩 (주석 해제하여 사용)
    # orchestrator.start_automated_trading(interval_minutes=60)

if __name__ == "__main__":
    main()