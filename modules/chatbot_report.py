import streamlit as st
import json
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from modules.DB import SupabaseDB
from langchain_core.prompts import PromptTemplate
from fpdf import FPDF
import tempfile
from modules.tools import (
    get_asset_summary_text,
    get_etf_summary_text,
    get_economic_summary_text,
    get_owned_stock_summary_text
)

def get_user_id():
    return st.session_state.get("id")

def init_llm():
    if "llm" not in st.session_state:
        api_key = st.secrets["gemini"]["api_key"]
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0,
            google_api_key=api_key
        )
        st.session_state["llm"] = llm

    if "openai" not in st.session_state:
        openai_api = st.secrets["openai"]["api_key"]
        openai = ChatOpenAI(
            model_name="gpt-4.1",
            temperature=0,
            api_key = openai_api
        )
        st.session_state["openai"] = openai


def generate_section_content(llm, user_info, asset_summary, etf_summary, economic_summary, stock_summary):
    prompt = PromptTemplate.from_template("""
당신은 전문적인 포트폴리오 분석가입니다.
다음 정보를 바탕으로 투자 포트폴리오에 대한 종합적인 분석 보고서를 작성해주세요.

고객 정보:
{user_info}

자산 요약:
{asset_summary}

ETF 정보:
{etf_summary}

경제 지표:
{economic_summary}

보유 주식 정보:
{stock_summary}

다음 섹션별로 분석을 제공해주세요. 각 섹션은 [섹션명]으로 시작하고 [섹션 끝]으로 끝나야 합니다:

1. [고객 기본 정보 요약] - 고객의 기본 정보와 투자 프로필 요약
2. [투자 성향 분석] - 고객의 투자 성향과 위험 선호도 분석
3. [자산 구성 현황] - 현재 자산 포트폴리오 구성 분석
4. [수익률 및 성과 분석] - 투자 성과와 수익률 분석
5. [리스크 분석] - 포트폴리오의 위험 요소 분석
6. [현금 흐름 분석] - 현금 흐름과 유동성 분석
7. [세제 및 절세 전략] - 세금 최적화 전략
8. [투자 전략 제안] - 향후 투자 방향 제안
9. [위험 시나리오 대응 전략] - 시장 위험에 대한 대응 전략
10. [개인화된 목표 추적 및 다음 단계] - 투자 목표 달성 현황과 향후 계획

분석 시 다음 사항을 고려해주세요:
1. 객관적인 데이터에 기반한 분석
2. 고객의 투자 성향과 목표 반영
3. 실행 가능한 구체적인 제안
4. 위험과 기회요인 모두 고려

응답은 한국어로 작성해주세요.
""")
    
    formatted_prompt = prompt.format(
        user_info=user_info,
        asset_summary=asset_summary,
        etf_summary=etf_summary,
        economic_summary=economic_summary,
        stock_summary=stock_summary
    )
    
    response = llm.invoke(formatted_prompt).content
    
    # 응답을 섹션별로 파싱
    sections = {
        "basic_info": "고객 기본 정보 요약",
        "investment_style": "투자 성향 분석",
        "asset_composition": "자산 구성 현황",
        "performance": "수익률 및 성과 분석",
        "risk_analysis": "리스크 분석",
        "cash_flow": "현금 흐름 분석",
        "tax_strategy": "세제 및 절세 전략",
        "investment_strategy": "투자 전략 제안",
        "risk_scenario": "위험 시나리오 대응 전략",
        "goals_tracking": "개인화된 목표 추적 및 다음 단계"
    }
    
    parsed_sections = {}
    for section_key, section_title in sections.items():
        start = response.find(f"[{section_title}]")
        if start != -1:
            end = response.find("[섹션 끝]", start)
            if end != -1:
                content = response[start + len(section_title) + 2:end].strip()
                parsed_sections[section_key] = content
            else:
                # 다음 섹션의 시작을 찾아서 자르기
                next_section_start = float('inf')
                for next_title in sections.values():
                    next_start = response.find(f"[{next_title}]", start + len(section_title))
                    if next_start != -1 and next_start < next_section_start:
                        next_section_start = next_start
                if next_section_start != float('inf'):
                    content = response[start + len(section_title) + 2:next_section_start].strip()
                else:
                    content = response[start + len(section_title) + 2:].strip()
                parsed_sections[section_key] = content
    
    return parsed_sections

def generate_portfolio_report(llm, user_info, asset_summary, etf_summary, economic_summary, stock_summary):
    sections = {
        "basic_info": "고객 기본 정보 요약",
        "investment_style": "투자 성향 분석",
        "asset_composition": "자산 구성 현황",
        "performance": "수익률 및 성과 분석",
        "risk_analysis": "리스크 분석",
        "cash_flow": "현금 흐름 분석",
        "tax_strategy": "세제 및 절세 전략",
        "investment_strategy": "투자 전략 제안",
        "risk_scenario": "위험 시나리오 대응 전략",
        "goals_tracking": "개인화된 목표 추적 및 다음 단계"
    }
    
    progress_text = "보고서 생성 중..."
    progress_bar = st.progress(0)
    
    # 한 번의 API 호출로 모든 섹션 생성
    section_contents = generate_section_content(
        llm,
        user_info,
        asset_summary,
        etf_summary,
        economic_summary,
        stock_summary
    )
    
    # 결과 포맷팅
    report = {}
    for i, (section_key, section_title) in enumerate(sections.items()):
        report[section_key] = {
            "title": section_title,
            "content": section_contents.get(section_key, "섹션 내용을 찾을 수 없습니다.")
        }
        progress_bar.progress((i + 1) / len(sections))
    
    progress_bar.empty()
    return report


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


def chatbot_page2():
    st.title("📊 투자 포트폴리오 분석 리포트")
    
    # 사이드바 추가
    with st.sidebar:
        st.title("🛠️ 보고서 설정")
        
        # 보고서 초기화 및 재생성 버튼
        if st.button("🔄 보고서 초기화 및 재생성"):
            # LLM 및 보고서 관련 모든 세션 상태 초기화
            for key in ["llm", "report_data", "openai", "macro_report"]:
                if key in st.session_state:
                    del st.session_state[key]

            st.rerun()
    
    init_llm()
    
    username = get_user_id()
    supabase = SupabaseDB()
    user_info = supabase.get_user(username)

    if not user_info or "id" not in user_info[0]:
        st.error("❌ Supabase에서 해당 사용자를 찾을 수 없습니다.")
        st.stop()

    # 데이터 수집
    asset_summary = get_asset_summary_text()
    etf_summary = get_etf_summary_text()
    economic_summary = get_economic_summary_text()
    stock_summary = get_owned_stock_summary_text()

    # personal summary 준비
    personal = user_info[0].get("personal", {})
    if isinstance(personal, str):
        try:
            personal = json.loads(personal)
        except json.JSONDecodeError:
            personal = {}

    personal_summary = "\n".join([f"{k}: {v}" for k, v in personal.items()])

    # 캐시된 보고서가 없거나 재생성이 요청된 경우에만 새로 생성
    if "report_data" not in st.session_state:
        # 보고서 생성 시작
        with st.spinner("포트폴리오 분석 보고서를 생성하고 있습니다..."):
            report = generate_portfolio_report(
                st.session_state["llm"],
                personal_summary,
                asset_summary,
                etf_summary,
                economic_summary,
                stock_summary
            )
            # 생성된 보고서 캐시
            st.session_state["report_data"] = report
    else:
        report = st.session_state["report_data"]
    
    # 보고서를 탭으로 구성
    tab_basic, tab_investment, tab_risk, macro = st.tabs(["📋 기본 정보", "💰 투자 분석", "⚠️ 리스크 관리", "거시경제 동향"])
    
    with tab_basic:
        # 기본 정보 관련 섹션
        st.subheader("🧑 고객 정보")
        with st.expander("고객 기본 정보 요약", expanded=False):
            st.markdown(report["basic_info"]["content"])
            
        st.subheader("📈 자산 현황")
        with st.expander("자산 구성 현황", expanded=False):
            st.markdown(report["asset_composition"]["content"])
            
        with st.expander("투자 성향 분석", expanded=False):
            st.markdown(report["investment_style"]["content"])
    
    with tab_investment:
        # 투자 분석 관련 섹션
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 성과 분석")
            with st.expander("수익률 및 성과 분석", expanded=False):
                st.markdown(report["performance"]["content"])
                
            with st.expander("현금 흐름 분석", expanded=False):
                st.markdown(report["cash_flow"]["content"])
        
        with col2:
            st.subheader("📝 전략")
            with st.expander("투자 전략 제안", expanded=False):
                st.markdown(report["investment_strategy"]["content"])
                
            with st.expander("세제 및 절세 전략", expanded=False):
                st.markdown(report["tax_strategy"]["content"])
    
    with tab_risk:
        # 리스크 관련 섹션
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🎯 리스크 분석")
            with st.expander("리스크 분석", expanded=False):
                st.markdown(report["risk_analysis"]["content"])
        
        with col2:
            st.subheader("🛡️ 대응 전략")
            with st.expander("위험 시나리오 대응 전략", expanded=False):
                st.markdown(report["risk_scenario"]["content"])
        
        st.subheader("🎆 목표 관리")
        with st.expander("개인화된 목표 추적 및 다음 단계", expanded=False):
            st.markdown(report["goals_tracking"]["content"])

    with macro:
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

 