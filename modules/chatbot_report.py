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

다음 섹션별로 분석을 제공해주세요. 각 섹션은 [섹션명]으로 시작해야 합니다:

1. [요약 섹션]
   - 고객 기본 정보 (나이, 직업, 자산 수준 요약)
   - 투자 성향 요약
   - 핵심 리포트 요약 (자산 진단 + 전략 요약)

2. [마이데이터 분석]
   - 총자산 개요: 예금, 투자, 부동산, 연금, 보험 등 항목별 총액
   - 부채 구조: 대출 금액, 이자율, 상환 계획
   - 소득/지출 분석: 월간/분기별 현금흐름, 소비 패턴
   - 투자 내역 분석: 종목별 수익률, 리스크 지표

3. [재무 상태 평가]
   - 자산 대비 부채 비율 (LTV, DTI 등)
   - 유동성 지수 (비상금 대비 지출 비율)
   - 투자 효율성 분석 (수익률 vs. 변동성, 샤프지수 등)

4. [투자 성향 진단]
   - 위험 감수 성향 (설문/행동 기반)
   - 투자 스타일 (공격형 / 중립형 / 안정형)
   - 선호 자산군 (주식, 채권, 현금 등)

5. [맞춤형 포트폴리오 제안]
   - 현재 자산 배분 분석: 실제 vs. 권장 비중
   - 권장 포트폴리오 제시: 투자 성향 기반 최적 배분안
   - 리밸런싱 전략: 현재 비중에서 필요한 조정안

6. [시나리오 기반 전략]
   - 경제 환경 변화 대응 전략 (침체, 금리 상승 등)
   - 자산 증감 시나리오별 리스크 관리 방안

7. [세부 실행 가이드]
   - 단기 전략 (3~6개월): 소비 구조 개선, 투자 구조 조정
   - 중기 전략 (1~3년): 투자 확대, 보험/연금 최적화
   - 장기 전략 (3년 이상): 은퇴 준비, 자산 승계 전략

8. [부록]
   - 데이터 수집 출처 및 기준
   - 용어 해설 (샤프지수, 베타 등 어려운 경제 용어)
   - 금융상품 비교표 (수수료, 수익률, 리스크 등)

아래 자산 데이터를 바탕으로 고객의 자산 상태를 분석하고, 투자 성향과 목표를 반영한 실행 가능한 맞춤형 포트폴리오 전략을 제안해주세요.

분석 시 다음 사항을 반드시 고려하세요:

1. 객관적인 수치와 데이터 기반 분석

2. 고객의 위험 성향과 재무 목표 반영

3. 실행 가능한 구체적이고 현실적인 제안 포함

4. 주요 위험 요인과 기회 요인 모두 명시

5. 투자 성향과 현재 상태의 괴리 조정

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
        "summary": "요약 섹션",
        "mydata": "마이데이터 분석",
        "financial_status": "재무 상태 평가",
        "investment_style": "투자 성향 진단",
        "portfolio": "맞춤형 포트폴리오 제안",
        "scenario": "시나리오 기반 전략",
        "action_guide": "세부 실행 가이드",
        "appendix": "부록"
    }
    
    parsed_sections = {}
    current_section = None
    current_content = []
    
    # 응답을 줄 단위로 분석
    lines = response.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # 새로운 섹션의 시작인지 확인
        for section_key, section_title in sections.items():
            if f"[{section_title}]" in line:
                # 이전 섹션의 내용을 저장
                if current_section and current_content:
                    parsed_sections[current_section] = '\n'.join(current_content)
                # 새로운 섹션 시작
                current_section = section_key
                current_content = []
                break
        else:
            # 현재 섹션이 있다면 내용 추가
            if current_section:
                current_content.append(line)
    
    # 마지막 섹션의 내용 저장
    if current_section and current_content:
        parsed_sections[current_section] = '\n'.join(current_content)
    
    # 누락된 섹션에 대한 기본값 설정
    for section_key in sections.keys():
        if section_key not in parsed_sections:
            parsed_sections[section_key] = "이 섹션의 내용을 생성하는 중 문제가 발생했습니다. 보고서를 다시 생성해주세요."
    
    return parsed_sections

def generate_portfolio_report(llm, user_info, asset_summary, etf_summary, economic_summary, stock_summary):
    sections = {
        "summary": "요약 섹션",
        "mydata": "마이데이터 분석",
        "financial_status": "재무 상태 평가",
        "investment_style": "투자 성향 진단",
        "portfolio": "맞춤형 포트폴리오 제안",
        "scenario": "시나리오 기반 전략",
        "action_guide": "세부 실행 가이드",
        "appendix": "부록"
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

def chatbot_page2():
    st.title("📊 투자 포트폴리오 분석 리포트")
    
    # 사이드바 추가
    with st.sidebar:
        st.title("🛠️ 보고서 설정")
        
        # 보고서 초기화 및 재생성 버튼
        if st.button("🔄 보고서 초기화 및 재생성"):
            # LLM 및 보고서 관련 모든 세션 상태 초기화
            for key in ["llm", "report_data"]:
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
    tab_summary, tab_analysis, tab_strategy = st.tabs(["📋 요약", "💰 분석", "⚠️ 전략"])
    
    with tab_summary:
        # 요약 섹션
        st.subheader("📊 요약")
        with st.expander("요약 섹션", expanded=True):
            st.markdown(report["summary"]["content"])
            
        st.subheader("📈 마이데이터 분석")
        with st.expander("마이데이터 분석", expanded=False):
            st.markdown(report["mydata"]["content"])
    
    with tab_analysis:
        # 분석 관련 섹션
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 재무 상태")
            with st.expander("재무 상태 평가", expanded=False):
                st.markdown(report["financial_status"]["content"])
                
            with st.expander("투자 성향 진단", expanded=False):
                st.markdown(report["investment_style"]["content"])
        
        with col2:
            st.subheader("📝 포트폴리오")
            with st.expander("맞춤형 포트폴리오 제안", expanded=False):
                st.markdown(report["portfolio"]["content"])
    
    with tab_strategy:
        # 전략 관련 섹션
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🎯 시나리오 전략")
            with st.expander("시나리오 기반 전략", expanded=False):
                st.markdown(report["scenario"]["content"])
        
        with col2:
            st.subheader("🛡️ 실행 가이드")
            with st.expander("세부 실행 가이드", expanded=False):
                st.markdown(report["action_guide"]["content"])
        
        st.subheader("📚 부록")
        with st.expander("부록", expanded=False):
            st.markdown(report["appendix"]["content"])

 