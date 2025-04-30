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



def generate_section_content(llm, section_title, user_info, asset_summary, etf_summary, economic_summary, stock_summary):
    prompt = PromptTemplate.from_template("""
당신은 전문적인 포트폴리오 분석가입니다.
다음 정보를 바탕으로 {section_title} 섹션에 대한 상세한 분석을 제공해주세요.

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

분석 시 다음 사항을 고려해주세요:
1. 객관적인 데이터에 기반한 분석
2. 고객의 투자 성향과 목표 반영
3. 실행 가능한 구체적인 제안
4. 위험과 기회요인 모두 고려

응답은 한국어로 작성해주세요.
응답은 마크다운 형식으로 작성해주세요.
""")
    
    formatted_prompt = prompt.format(
        section_title=section_title,
        user_info=user_info,
        asset_summary=asset_summary,
        etf_summary=etf_summary,
        economic_summary=economic_summary,
        stock_summary=stock_summary
    )
    
    return llm.invoke(formatted_prompt).content

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
    
    report = {}
    progress_text = "보고서 생성 중..."
    progress_bar = st.progress(0)
    
    for i, (section_key, section_title) in enumerate(sections.items()):
        report[section_key] = {
            "title": section_title,
            "content": generate_section_content(
                llm,
                section_title,
                user_info,
                asset_summary,
                etf_summary,
                economic_summary,
                stock_summary
            )
        }
        progress_bar.progress((i + 1) / len(sections))
        
    progress_bar.empty()
    return report


def chatbot_page2():
    st.title("📊 투자 포트폴리오 분석 리포트")
    
    # 사이드바 추가
    with st.sidebar:
        st.title("🛠️ 보고서 설정")
        
        # 보고서 초기화 및 재생성 버튼
        if st.button("🔄 보고서 초기화 및 재생성"):
            # LLM 및 보고서 관련 모든 세션 상태 초기화
            for key in ["llm", "report_data"]:
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
    tab_basic, tab_investment, tab_risk = st.tabs(["📋 기본 정보", "💰 투자 분석", "⚠️ 리스크 관리"])
    
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

 