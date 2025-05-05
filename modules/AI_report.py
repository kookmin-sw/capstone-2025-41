import streamlit as st
from langchain_openai import ChatOpenAI
from modules.DB import SupabaseDB
from langchain_core.prompts import PromptTemplate
from modules.tools import get_economic_summary_text

def init_llm():
    if "openai" not in st.session_state:
        openai_api = st.secrets["openai"]["api_key"]
        openai = ChatOpenAI(
            model_name="gpt-4.1",
            temperature=0,
            api_key=openai_api
        )
        st.session_state["openai"] = openai

def generate_macroeconomic_content(llm, economic_summary):
    prompt = PromptTemplate.from_template("""
당신은 거시경제 지표 및 주가 지표 분석 전문가입니다.
일별 데이터의 경우 최근 1주일 간의 동향을, 월별 데이터의 경우 최근 1년 간의 동향을 위주로 분석해주세요.
경제 지표 테이블의 컬럼명에 대한 설명은 아래와 같습니다.
------------
[국내 경제지표]
unemp_rate: 국내 실업률
emp_rate: 국내 고용률
cpi: 국내 CPI
ppi: 국내 PPI
curr_account: 국내 경상수지
kr_bond_3y: 국내 3년물 국채 금리
kr_bond_10y: 국내 10년물 국채 금리
kr_base_rate: 국내 기준 금리
kospi: KOSPI
kosdaq: KOSDAQ
usd_krw: 원/달러 환율

[미국 경제지표]
us_unemp_rate: 미국 실업률
us_nfp: 미국 비농업고용자수
us_core_pce: 미국 Core PCE
us_pce: 미국 PCE
us_cpi: 미국 CPI
us_ppi: 미국 PPI
us_bond_2y: 미국 2년물 국채 금리
us_bond_10y: 미국 10년물 국채 금리
ffr: 미국 Federal funds rate
sp500: S&P500
nasdaq: NASDAQ
dji: 다우존스 지수
------------

아래는 최근의 국내/해외의 거시경제 지표 및 주가 지표입니다.
------------
{economic_summary}
------------

다음 섹션별로 분석 리포트를 제공해주세요.
1. 국내 거시경제 동향
- 고용 동향
- 물가 동향
- 수출입 동향
- 국채 금리 동향
- 주요 주가지표 동향 (KOSPI, KOSDAQ)
- 원/달러 환율 동향

2. 미국 거시경제 동향
- 고용 동향
- 물가 동향
- 국채 금리 동향
- 주요 주가지표 동향 (S&P500, NASDAQ, 다우존스)
""")

    formatted_prompt = prompt.format(
        economic_summary=economic_summary
    )

    response = llm.invoke(formatted_prompt).content

    return response


def chatbot_page3():
    st.title("📊 거시경제 동향 리포트")

    init_llm()
    supabase = SupabaseDB()

    # 데이터 수집
    economic_summary = get_economic_summary_text()

    # 캐시된 보고서가 없거나 재생성이 요청된 경우에만 새로 생성
    if "macro_report" not in st.session_state:
        with st.spinner("포트폴리오 분석 보고서를 생성하고 있습니다..."):
            macro_report = generate_macroeconomic_content(
                st.session_state["openai"],
                economic_summary
            )
            # 생성된 보고서 캐시
            st.session_state["macro_report"] = macro_report
    else:
        macro_report = st.session_state["macro_report"]

    st.markdown(macro_report)

