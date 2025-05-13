from .base import BaseLLM
from langchain_core.prompts import PromptTemplate

class MarketHeadlineLLM(BaseLLM):
    def __init__(self):
        super().__init__()
        
    def get_prompt_template(self):
        return PromptTemplate.from_template("""
        당신은 금융 시장 전문가입니다. 오늘({current_date}) 아침에 투자자들에게 보낼 시장 동향 메일의 제목을 생성해주세요.
        
        규칙:
        1. 반드시 이모지를 포함하세요 (예: 🚨, ⚡, 💥)
        2. 실제 데이터에 근거한 내용만 작성하세요
        3. 20자 이내로 간단명료하게 작성하세요
        4. 구체적인 수치나 변화율을 포함하세요
        5. "오늘의 시장 동향"이라는 문구를 포함하세요
        6. 투자자의 투자 성향과 기간을 고려하여 관련성 높은 시장 동향을 선택하세요
        7. 포트폴리오 보고서의 분석 내용을 참고하여 더 정확한 시장 동향을 제시하세요
        8. 반드시 하나의 제목만 생성하세요
        
        시장 데이터:
        {market_data}
        
        개인 리포트 요약:
        {report_data}
        
        예시:
        🚨 오늘의 시장 동향: KOSPI 2.5% 하락 예상
        ⚡ 오늘의 시장 동향: 달러/원 환율 1,350원 돌파
        
        헤드라인:
        """) 