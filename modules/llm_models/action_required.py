from .base import BaseLLM
from langchain_core.prompts import PromptTemplate

class ActionRequiredLLM(BaseLLM):
    def __init__(self):
        super().__init__()
        
    def get_prompt_template(self):
        return PromptTemplate.from_template("""
        당신은 투자 전문가입니다. 오늘({current_date}) 아침에 투자자에게 보낼 투자 액션 메일의 제목을 생성해주세요.
        
        규칙:
        1. 반드시 이모지를 포함하세요 (예: 💡, 📊, 🎯)
        2. 실제 시장 데이터만 사용하세요
        3. 20자 이내로 간단명료하게 작성하세요
        4. 구체적인 매수/매도 가격이나 목표가를 포함하세요
        5. "오늘의 투자 액션"이라는 문구를 포함하세요
        6. 투자자의 투자 스타일과 목표에 맞는 액션을 제안하세요
        7. 투자자의 위험 감수도와 투자 기간을 고려하여 액션을 제안하세요
        8. 현재 수익률과 목표 수익률을 비교하여 의미 있는 액션을 제안하세요
        9. 포트폴리오 보고서의 투자 전략과 액션 가이드를 참고하여 더 정확한 투자 액션을 제안하세요
        
        투자 데이터:
        {investment_data}
        
        예시:
        - "💡 오늘의 투자 액션: 삼성전자 68,000원 매수"
        - "📊 오늘의 투자 액션: 네이버 180,000원 매도"
        
        액션:
        """) 