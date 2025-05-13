from .base import BaseLLM
from langchain_core.prompts import PromptTemplate

class PortfolioAlertLLM(BaseLLM):
    def __init__(self):
        super().__init__()
        
    def get_prompt_template(self):
        return PromptTemplate.from_template("""
        당신은 포트폴리오 관리 전문가입니다. 오늘({current_date}) 아침에 투자자에게 보낼 포트폴리오 알림 메일의 제목을 생성해주세요.
        
        규칙:
        1. 반드시 이모지를 포함하세요 (예: 💥, 🎯, 📈)
        2. 실제 수익/손실 데이터만 사용하세요
        3. 20자 이내로 간단명료하게 작성하세요
        4. 구체적인 수익률이나 손실률을 포함하세요
        5. 투자자의 목표 수익률과 현재 수익률을 비교하여 의미있는 알림을 생성하세요
        6. 투자자의 투자 목표에 부합하는 알림을 생성하세요
        7. 포트폴리오 보고서의 분석 내용을 참고하여 더 정확한 포트폴리오 상태를 알려주세요
        8. 반드시 하나의 제목만 생성하세요
        
        포트폴리오 데이터:
        {portfolio_data}
        
        개인 리포트 요약:
        {report_data}
        
        예시:
        💥 위험! 삼성전자 5.2% 손실, 리밸런싱 필요
        🎯 기회! 네이버 3.5% 수익 실현 타이밍
        
        알림:
        """) 