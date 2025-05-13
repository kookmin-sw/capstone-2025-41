from modules.tools import (
    get_asset_summary_text,
    get_etf_summary_text,
    get_economic_summary_text,
    get_owned_stock_summary_text
)
from modules.DB import SupabaseDB
import json

class DataProcessor:
    def __init__(self, user_id):
        self.user_id = user_id
        self.db = SupabaseDB()
        user = self.db.get_user(user_id)[0] if self.db.get_user(user_id) else {}
        personal_data = user.get("personal", {})
        if isinstance(personal_data, str):
            personal_data = json.loads(personal_data)
        self.user_info = personal_data
        
    def get_market_data(self):
        """시장 헤드라인 LLM에 필요한 데이터"""
        economic_summary = get_economic_summary_text()
        
        # 사용자 정보에서 투자 성향 데이터 추출
        investment_profile = self.user_info.get("investment_profile", {})
        investment_details = investment_profile.get("details", {})
        
        return {
            "market_data": f"""
            시장 동향: {economic_summary}
            투자 성향: {investment_profile.get('investment_style', '미입력')}
            투자 기간: {investment_details.get('investment_horizon', '미입력')}
            위험 감수도: {investment_details.get('risk_tolerance', '미입력')}
            """,
            "username": self.user_id
        }
    
    def get_portfolio_data(self):
        """포트폴리오 알림 LLM에 필요한 데이터"""
        asset_summary = get_asset_summary_text()
        stock_summary = get_owned_stock_summary_text()
        
        # 사용자 정보에서 투자 목표 데이터 추출
        financial = self.user_info.get("financial", {})
        investment_profile = self.user_info.get("investment_profile", {})
        investment_details = investment_profile.get("details", {})
        
        return {
            "portfolio_data": f"""
            자산 요약: {asset_summary}
            보유 종목: {stock_summary}
            투자 목표: {investment_details.get('investment_priority', '미입력')}
            목표 수익률: {investment_details.get('expected_return', '미입력')}%
            현재 수익률: {financial.get('current_return', '미입력')}%
            """,
            "username": self.user_id
        }
    
    def get_risk_data(self):
        """리스크 경고 LLM에 필요한 데이터"""
        stock_summary = get_owned_stock_summary_text()
        economic_summary = get_economic_summary_text()
        
        # 사용자 정보에서 리스크 관련 데이터 추출
        financial = self.user_info.get("financial", {})
        investment_profile = self.user_info.get("investment_profile", {})
        investment_details = investment_profile.get("details", {})
        
        return {
            "risk_data": f"""
            보유 종목: {stock_summary}
            시장 동향: {economic_summary}
            위험 감수도: {investment_details.get('risk_tolerance', '미입력')}
            투자 기간: {investment_details.get('investment_horizon', '미입력')}
            현재 변동성: {financial.get('current_volatility', '미입력')}%
            최대 손실 한도: {financial.get('max_loss_limit', '미입력')}%
            """,
            "username": self.user_id
        }
    
    def get_investment_data(self):
        """투자 액션 LLM에 필요한 데이터"""
        asset_summary = get_asset_summary_text()
        stock_summary = get_owned_stock_summary_text()
        economic_summary = get_economic_summary_text()
        
        # 사용자 정보에서 투자 목표와 성향 데이터 추출
        financial = self.user_info.get("financial", {})
        investment_profile = self.user_info.get("investment_profile", {})
        investment_details = investment_profile.get("details", {})
        
        return {
            "investment_data": f"""
            자산 요약: {asset_summary}
            보유 종목: {stock_summary}
            시장 동향: {economic_summary}
            투자 목표: {investment_details.get('investment_priority', '미입력')}
            목표 수익률: {investment_details.get('expected_return', '미입력')}%
            투자 성향: {investment_profile.get('investment_style', '미입력')}
            투자 기간: {investment_details.get('investment_horizon', '미입력')}
            위험 감수도: {investment_details.get('risk_tolerance', '미입력')}
            현재 수익률: {financial.get('current_return', '미입력')}%
            """,
            "username": self.user_id
        } 