from .base import BaseLLM
from langchain_core.prompts import PromptTemplate

class RiskWarningLLM(BaseLLM):
    def __init__(self):
        super().__init__()
        
    def get_prompt_template(self):
        return PromptTemplate.from_template("""
        당신은 리스크 관리 전문가입니다. 오늘({current_date}) 아침에 투자자에게 보낼 리스크 경고 메일의 제목을 생성해주세요.
        
        규칙:
        1. 반드시 이모지를 포함하세요 (예: ⚠️, ❗, 🚨)
        2. 실제 변동성 데이터만 사용하세요
        3. 20자 이내로 간단명료하게 작성하세요
        4. 구체적인 변동폭이나 위험 수준을 포함하세요
        5. "오늘의 리스크"라는 문구를 포함하세요
        6. 투자자의 위험 감수도와 최대 손실 한도를 고려하여 경고를 생성하세요
        7. 투자자의 투자 기간에 맞는 리스크 관점을 제시하세요
        
        리스크 데이터:
        {risk_data}
        
        예시:
        - "⚠️ 오늘의 리스크: 삼성전자 변동폭 3.2% 예상"
        - "❗ 오늘의 리스크: 네이버 5일 연속 하락 중"
        
        경고:
        """) 