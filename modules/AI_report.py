import streamlit as st
from langchain_openai import ChatOpenAI
from modules.DB import SupabaseDB
from langchain_core.prompts import PromptTemplate
from modules.tools import get_economic_summary_text, get_real_estate_summary_text

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


def generate_real_estate_content(llm, real_estate_summary):
    prompt = PromptTemplate.from_template("""
당신은 국내 부동산 투자 전문가입니다.

당신은 최근 국내 부동산 지표를 분석하여 부동산 동향 리포트를 작성하고, 부동산 투자 관련 조언을 할 것입니다.

부동산 지표 테이블의 컬럼명에 대한 설명은 아래와 같습니다.
------------
부동산 지표의 컬럼명은 다음과 같은 조합으로 이루어져 있습니다.
(col1)_(col2)_(col3)

(col1)은 아래의 요소 중 하나로 구성되어 있습니다.
sale: 주택매매가격지수
jeon: 주택전세가격지수
month: 주택월세통합가격지수

(col2)은 아래의 요소 중 하나로 구성되어 있습니다.
apt: 아파트
row: 연립다세대
det: 단독주택

(col3)은 아래의 요소 중 하나로 구성되어 있습니다.
s: 서울
gg: 경기
ic: 인천
bs: 부산
dg: 대구
gj: 광주
dj: 대전
us: 울산
sj: 세종
gw: 강원
cb: 충북
cn: 충남
jb: 전북
jn: 전남
gb: 경북
gn: 경남
jj: 제주

예를 들어 sale_apt_s 컬럼명을 갖는 데이터는 서울 아파트 주택매매가격지수입니다.
------------

아래는 최근의 국내 부동산 지표입니다.
------------
{real_estate_summary}
------------

아래의 구조에 따라 **완성도 높은 부동산 동향 리포트**를 작성해주세요.
------------
1. 📌 **요약 개요 (3~5줄)**  
- 최근 한 달간 부동산 시장에서 가장 주목할 만한 변화와 특징을 요약해주세요.
- 예: "서울 아파트 매매지수는 1.3% 상승하며 회복세를 보였다. 지방은 전반적으로 약보합."

2. 🌏 **전국 시장 개요**  
- 전체 매매가격지수, 전세가격지수, 월세통합지수의 월간 및 전년동월 대비 변화율을 표와 함께 요약해주세요.

3. 🗺️ **지역별 시장 동향 분석**  
- 주요 광역시도별로 매매/전세/월세 지수의 변화율을 정리하고, 상승률 및 하락률 상위 3개 지역을 정리해주세요.
- 지역별 주요 이슈나 원인도 간략히 설명해주세요 (예: GTX, 공급확대, 투자심리 등).

4. 🏘️ **주택 유형별 동향 분석**  
- 아파트, 연립다세대, 단독주택별로 지역 간 비교를 통해 어떤 유형이 강세 또는 약세인지 정리해주세요.
- 월세와 매매지수를 활용해 **임대수익률 추정값**을 제시해줘도 좋습니다.

5. 💡 **투자 인사이트 요약 (3~5가지)**  
- 위 내용을 종합하여 다음과 같은 형태로 투자 인사이트를 작성해주세요:
    1. 수도권 아파트 매매는 회복세를 보이고 있으나, 강세 지역 편중 현상이 강함
    2. 지방의 월세 수익률이 상승 중이며 투자처로 검토 가능
    3. 전세 안정화로 전세 투자의 리스크는 다소 낮아진 상태
    4. 단기적 매매 차익보다는 월세 수익형 상품이 상대적으로 유리
    
⚠️ 주의사항:
- 숫자는 **간결하게**, 인사이트는 **구체적으로**
- 단순 요약이 아니라, **왜 그런 변화가 일어났는지**에 대한 원인과 해석 중심
- 지나치게 일반적인 조언은 피하고, **지역/유형별 차별화된 전략 제안** 포함
- 출력 시 마크다운의 취소선(`~~text~~`)은 절대 사용하지 마세요.
------------

""")

    formatted_prompt = prompt.format(
        real_estate_summary=real_estate_summary
    )

    response = llm.invoke(formatted_prompt).content

    return response


def chatbot_page3():
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


def chatbot_page4():
    init_llm()
    supabase = SupabaseDB()

    # 데이터 수집
    real_estate_summary = get_real_estate_summary_text()

    # 캐시된 보고서가 없거나 재생성이 요청된 경우에만 새로 생성
    if "real_estate_report" not in st.session_state:
        with st.spinner("부동산 동향 보고서를 생성하고 있습니다..."):
            real_estate_report = generate_real_estate_content(
                st.session_state["openai"],
                real_estate_summary
            )
            # 생성된 보고서 캐시
            st.session_state["real_estate_report"] = real_estate_report
    else:
        real_estate_report = st.session_state["real_estate_report"]

    st.markdown(real_estate_report)

