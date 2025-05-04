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
당신은 25년 경력의 자산관리 전문가이자 포트폴리오 매니저입니다.
당신의 주요 역할은 고객의 재무 상태를 종합적으로 분석하고, 맞춤형 자산관리 전략을 제시하는 것입니다.

[입력 데이터]
1. 고객 기본 정보:
{user_info}

2. 자산 포트폴리오:
{asset_summary}

3. 경제 환경 분석:
{economic_summary}

4. 투자 현황:
{stock_summary}

[작성 가이드라인]
1. 전문성: 모든 분석과 제안은 객관적 데이터와 전문적 지표에 기반해야 합니다.
2. 실행가능성: 제시하는 모든 전략은 구체적이고 실현 가능해야 합니다.
3. 맞춤화: 고객의 상황과 성향을 고려한 개인화된 제안이어야 합니다.
4. 위험관리: 잠재적 위험요소를 명확히 식별하고 대응 방안을 제시해야 합니다.
5. 이해용이성: 전문 용어는 반드시 쉬운 설명을 덧붙여야 합니다.

[필수 포함 요소]
각 섹션은 반드시 [섹션명]으로 시작하며, 다음 내용을 포함해야 합니다:

1. [요약 섹션]
   - 고객 프로필 요약 (연령, 직업, 자산규모)
   - 투자 성향 분석
   - 핵심 제안사항 (3가지 이내)

2. [마이데이터 분석]
   - 자산 구성 분석 (항목별 비중)
   - 현금흐름 분석 (월간 수입/지출)
   - 부채 현황 (총액, 이자율, 상환계획)
   - 투자자산 성과 분석

3. [재무 건전성 평가]
   - 핵심 재무비율 분석 (부채비율, 유동성비율 등)
   - 위험 지표 평가 (변동성, 집중도 등)
   - 수익성 지표 분석 (ROI, 샤프비율 등)

4. [투자 성향 진단]
   - 위험 감수성향 평가
   - 투자 스타일 분석
   - 투자 목표 정합성 검토

5. [포트폴리오 전략]
   - 현재 자산배분 평가
   - 목표 포트폴리오 제시
   - 리밸런싱 계획 (단계별 조정안)

6. [위험관리 전략]
   - 주요 위험요소 식별
   - 시나리오별 대응 전략
   - 위험 모니터링 계획

7. [실행 로드맵]
   - 단기 과제 (3개월 이내)
   - 중기 과제 (3개월~1년)
   - 장기 과제 (1년 이상)

8. [부록]
   - 용어 설명
   - 데이터 출처
   - 참고 지표 설명

[예시 분석]
[요약 섹션]
고객명 홍길동(35세)은 IT 기업 재직 중인 전문직으로, 총 자산 5억 원 규모를 보유하고 있습니다. 
투자 성향은 '적극투자형'으로 분석되며, 현재 주식과 펀드 위주의 포트폴리오를 구성하고 있습니다.

핵심 제안:
1. 주식 비중 축소 (현재 80% → 목표 60%)
2. 채권형 자산 편입 (목표 20%)
3. 정기적 리밸런싱 체계 수립

[작성 시 유의사항]
1. 모든 수치는 구체적으로 제시할 것
2. 각 제안에 대한 근거를 명시할 것
3. 실행 우선순위를 명확히 할 것
4. 잠재적 위험요소를 반드시 언급할 것
5. 전문용어는 풀어서 설명할 것

응답은 반드시 한국어로 작성해주세요.
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

 